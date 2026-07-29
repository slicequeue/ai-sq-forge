---
name: batch-schedule-audit
description: "Cloud Run Jobs + Cloud Scheduler 기반 배치 잡 전수 감사. 배치 현황 파악·문서화, 잡별 부하/무게 평가, cron 실행 패턴·충돌 분석, 신규 배치 스케줄 적정성 평가에 사용. \"배치 분석/감사\", \"스케줄 배치 정리\", \"배치 부하 평가\", \"cron 충돌\", \"신규 배치 어디에 스케줄\", \"Cloud Run job 현황\", \"배치 시간 재배치\" 등의 요청에 트리거."
version: "0.3"
last-modified: "2026-07-29"
changelog: |
  v0.3 — 2026-07-29 `--repeat 3` 일관성 테스트 반영(96.0/100, 편차 2점 PASS) + TC-4 v0.2 재검증 통과(78→93): 자기 검증 7번에 고빈도 baseline 잡의 정시 offset 재배치 포함 여부 추가. 3회 중 1회만 제시되던 항목.
  v0.2 — 2026-07-29 하네스 v0.1 평가 반영(93.2/100 PASS): 하드 가드레일 #1을 "합성 단일 무게 점수 산출 자체 금지"로 강화. TC-4에서 자원 컬럼만 붙이면 임의 1~10 점수 체계가 허용되는 것으로 읽히는 문제가 확인됨.
  v0.1 — 2026-07-29 moneyball 실전 스킬 역수입·일반화. GCP 프로젝트·리전·모듈 구조를 Phase 0 파라미터로 분리, 프로젝트별 자원 토폴로지를 `references/topology-{project}.md`로 분리(moneyball 실전본 동반 흡수), 하드 가드레일 7건 명문화 + 자기 검증 체크리스트 신설. 원본 `scripts/collect.sh` 유지(프로젝트 기본값 제거).
---

# batch-schedule-audit - 배치 스케줄 감사

Cloud Run Jobs(배치)를 전수 조사해 **현황 문서화 → 부하 평가 → cron 충돌·패턴 분석 → 신규 배치 평가**까지 수행한다.

핵심 관점은 하나다. 무게는 단일 점수가 아니라 **"어느 자원을 × 언제 × 얼마나 오래 누르는가"** 다.

| 참조 | 용도 |
|------|------|
| `references/code-mapping.md` | `--job.name` → 코드 매핑, DB 자원 판별 방법론 |
| `references/load-rubric.md` | 부하 축 A~G + 무게 등급 + cron→KST 환산 |
| `references/conflict-analysis.md` | 타임라인 충돌맵, 충돌 판정 규칙, 재배치 제안, 리포트 구성 |
| `references/new-batch-eval.md` | 신규 배치 단건 평가 절차 |
| `references/topology-moneyball.md` | 프로젝트별 자원 토폴로지·모듈 구조 (moneyball 실전본) |
| `references/evaluation-rubric.md` | 100점 채점 기준 + AUTO FAIL |
| `scripts/collect.sh` | Cloud Run Jobs + Scheduler 현황 자동 수집 |

---

## Phase 0. 대상 파라미터 확정 (현황 파악 우선)

**가정으로 시작하지 않는다.** 아래를 확정한 뒤 수집한다.

| # | 파라미터 | 확인 방법 |
|---|---------|----------|
| 1 | GCP 프로젝트 / 리전 | `gcloud config get-value project` 또는 사용자 지정 |
| 2 | 배치 코드 모듈 | 레포에서 배치 모듈을 찾는다. `grep -rln "JobBuilder\|--job.name\|@Scheduled" --include=*.java` + `settings.gradle` 모듈 목록 |
| 3 | 잡 정의 방식 | 모듈별로 Spring Batch `*JobConfig` / 커스텀 `Job` 인터페이스 + `@Component("<jobName>")` 중 어느 쪽인지 |
| 4 | 디스패치 방식 | `--job.name=<X>` 를 받아 빈을 찾는 진입점(`JobStarter` 등) 위치와 args 구분자 |
| 5 | **자원 토폴로지** | datasource 설정 파일(`application-*.yml`)의 url로 확인. `references/topology-{project}.md` 가 있으면 참고하되 **매 실행 재확인** |
| 6 | 프로파일 분기 | 읽기/쓰기 자원을 갈아타는 프로파일(예: `spring.profiles.include=summary`)이 있는지 |

### Phase 0.5. 인증 확인 (모든 gcloud 작업 전 필수)

```bash
gcloud config get-value account                                        # 비어있으면 미인증
gcloud projects describe <PROJECT> >/dev/null 2>&1 && echo OK || echo NO_ACCESS
```

미인증·권한 없음이면 **사용자에게 직접 로그인을 유도한다** (Claude가 대신 못 함):

> 세션에서 `! gcloud auth login` 을 입력해 브라우저 인증을 진행해 주세요. ADC가 필요하면 `! gcloud auth application-default login` 도 함께.

`scripts/collect.sh`는 이 체크를 내장하고 있어 미인증 시 안내 후 종료한다. **로그인 확인 없이 추정으로 감사 결과를 만들지 않는다.**

---

## 작업 흐름

요청 유형에 따라 선택 실행한다. 전체 감사는 1 → 2 → 3, 신규 배치 평가는 0 → 4.

### 1. 현황 수집 (자동)

```bash
bash anvil/skills/batch-schedule-audit/scripts/collect.sh <PROJECT> <REGION> ./batch-audit-out
```

산출: `joined.csv`(잡 ↔ 스케줄 + 리소스 한도 + 프로파일), `jobs.json`, `schedulers.csv`.
스크립트가 **스케줄 없는 잡** 목록도 출력한다 (일회성 / 폐기 / 스케줄 누락 후보 — 셋을 구분해 판정한다).

### 2. 코드 매핑 + 부하 평가

`joined.csv`의 각 `job_name`을 코드에 매핑하고 부하를 산정한다.

- 매핑 규칙·DB 자원 판별: `references/code-mapping.md`
- 무게 산정 기준(부하량 × 점유시간, 자원별): `references/load-rubric.md`
- **잡 수가 많으면(>15) Explore 서브에이전트를 모듈·도메인별로 병렬 분산**해 코드 근거(파일·쿼리·청크·쓰기·외부 I/O)를 수집한다.

산출은 부하 프로파일 CSV. 컬럼은 `load-rubric.md` "산출 컬럼" 참조. `notes`에는 무게 판단의 **코드 근거(file:line·쿼리·청크 size)** 를 1줄로 적는다.

### 3. 충돌·패턴 분석 + 리포트

부하 프로파일 + cron을 KST 타임라인에 깔아 **같은 시각 × 같은 자원**에 Heavy 잡이 겹치는 구간을 찾는다. 분석·리포트 작성법: `references/conflict-analysis.md`.

리포트는 한국어 공식 문서로 작성한다 — **`formal-doc-ko` 스킬을 함께 호출**(장식 기호 금지, 팩트/판단 분리, 근거 file:line 명시).

### 4. 신규 배치 평가 (단건)

신규·변경 배치에 대해 "언제 돌려야 하나, 무엇과 겹치나, 리소스는 적정한가"를 평가. 절차: `references/new-batch-eval.md`.

---

## 핵심 원칙

- **자원별로 구분한다.** 무게는 단일 점수가 아니라 "어느 자원(PRIMARY / REPLICA / AGGREGATE / 외부)을 × 언제 × 얼마나 오래" 누르는가. **다른 자원이면 동시각이라도 충돌이 아니다.**
- **리소스 한도는 근거다.** CPU·메모리 한도는 코드나 IaC가 아니라 배포 스펙(`gcloud describe`)에서 온다. 운영자가 OOM·타임아웃을 겪고 키운 경험적 사이징이므로 **무게의 강한 프록시**다. 코드 부하 팩터와 교차검증한다.
- **정적 추정 한계를 명시한다.** "겹침" 판정은 코드 기반 추정이다. 확정하려면 실측 duration이 필요하다 (`gcloud run jobs executions list` + Cloud Logging). 리포트에 이 한계를 반드시 적는다.
- **사실·판단 분리, 근거 링크.** 모든 무게·충돌 주장에 file:line 또는 실측 명령을 붙인다.
- **토폴로지는 변한다.** 문서에 적힌 호스트·스키마를 신뢰하지 말고 매 실행 설정 파일에서 재확인한다.

---

## 가드레일

### 하드 가드레일 (절대 위반 불가)

1. **합성 단일 무게 점수(1~10 등) 산출 자체 금지** — 무게는 **자원별 Heavy / Medium / Light 3단 + 근거**로만 표기한다. 모든 무게 판정에 read 자원 / write 자원을 함께 적는다. 사용자가 순위·점수를 요구해도 자원별 등급표로 대체 제시한다. 점수표는 근거가 탈락한 채 인용·전파되기 쉬운 형태다. (v0.2 강화 — 하네스 TC-4에서 "자원 컬럼만 붙이면 임의 점수 체계가 허용된다"고 읽히는 문제 확인)
2. **근거 없는 무게·충돌 판정 금지** — Heavy/Medium/Light 각 등급과 CONFLICT 판정마다 file:line·쿼리·청크 size·리소스 한도 중 최소 하나를 근거로 붙인다.
3. **정적 추정 한계 미명시 금지** — 리포트에 "겹침은 코드 기반 추정, 확정은 실측 필요" 를 명시하고 실측 명령을 제시한다.
4. **하드코딩 토폴로지 신뢰 금지** — 참조 문서의 호스트·스키마 값을 재확인 없이 리포트에 옮기지 않는다.
5. **다른 자원 동시각을 충돌로 판정 금지** — 단, **AGGREGATE가 PRIMARY와 동일 호스트**면 물리 IO·CPU를 공유하므로 합산 부하로 취급한다. 동일 호스트 여부를 확인하지 않은 상태로 "자원 분리됨"이라 단정하지 않는다.
6. **인증 미확인 상태 진행 금지** — gcloud 인증·권한 확인 전에 수집 결과를 추정으로 채우지 않는다.
7. **스케줄 없는 잡을 일괄 "폐기"로 단정 금지** — 일회성 / 폐기 / 스케줄 누락 3가지를 코드 존재 여부와 함께 구분 판정한다.

### 소프트 가드레일

- 코드만으로 도메인 선후 의존성을 단정할 수 없으면 "도메인팀 1회 확인" 단서를 단다.
- 재배치 제안은 **cron만 바꾸면 되는 것 / 코드 수정이 필요한 것**을 분리한다.
- 리소스가 큰데 코드가 빈약하면 과할당 의심으로, 코드가 무거운데 리소스가 작으면 OOM 리스크로 각각 경고한다.
- 잡 수가 많아 일부만 심층 조사했다면 **무엇을 얕게 봤는지 밝힌다.** 전수 조사한 것처럼 쓰지 않는다.

---

## 자기 검증 체크리스트

리포트를 제출하기 전 스스로 확인한다.

1. [ ] Phase 0 파라미터 6개를 확정했는가? 재확인 없이 참조 문서 값을 옮기지 않았는가?
2. [ ] gcloud 인증을 확인했는가? 실패 시 사용자에게 로그인을 요청했는가?
3. [ ] 모든 잡에 read 자원 / write 자원이 구분돼 있는가? write 템플릿을 실제로 확인했는가?
4. [ ] AGGREGATE·REPLICA가 PRIMARY와 동일 호스트인지 확인하고 리포트에 명시했는가?
5. [ ] 각 무게 등급에 코드 근거(file:line·쿼리·청크 size)가 붙어 있는가?
6. [ ] cron → KST 환산이 정확한가? (`Etc/UTC` 는 +9h, `Asia/Seoul` 은 그대로)
7. [ ] 고빈도 잡(`*/5`·매분)을 baseline 부하로 별도 표기했는가? 그 잡이 정시(`:00`)에 정렬돼 대형 잡과 매번 겹친다면 **offset(`2-59/5` 등)을 재배치 표에 포함**했는가? (v0.3 — `--repeat 3`에서 3회 중 1회만 제시됨)
8. [ ] CONFLICT 판정이 **같은 자원**에 한정돼 있는가? 다른 자원 동시각을 충돌로 세지 않았는가?
9. [ ] 정적 추정 한계와 실측 명령을 리포트에 적었는가?
10. [ ] 스케줄 없는 잡을 일회성/폐기/누락으로 구분했는가?
11. [ ] 재배치 제안이 cron 변경 / 코드 수정으로 분리돼 있고, cron은 구체값인가?
12. [ ] 얕게 본 잡이 있으면 그 범위를 밝혔는가?
13. [ ] `formal-doc-ko` 규칙(장식 기호 0건, 팩트/판단 분리)을 적용했는가?
