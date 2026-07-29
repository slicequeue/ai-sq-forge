---
name: batch-schedule-audit
version: 0.1
harness-version: 0.1
last-modified: 2026-07-29
---

# batch-schedule-audit 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/batch-schedule-audit/SKILL.md` |
| references | `anvil/skills/batch-schedule-audit/references/` |
| scripts | `anvil/skills/batch-schedule-audit/scripts/collect.sh` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/batch-schedule-audit/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/batch-schedule-audit/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/batch-schedule-audit/results/` |
| 리포트 | `proving-grounds/evals/batch-schedule-audit/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |
| 일관성 테스트 | TC-1 `--repeat 3` 권장 |

## 평가 모드

**시뮬레이션 입력 평가.** 실제 `gcloud` 호출과 `collect.sh` 실행은 하지 않는다. 테스트 케이스가 제공하는 `joined.csv` 발췌 + 코드 조사 결과 + 설정 파일 재확인 결과를 수집 산출물로 간주하고, 스킬이 산출하는 **부하 프로파일 + 충돌 판정 근거 + 재배치 변경표 + 리포트 본문 + 사용자 응답 텍스트**를 평가한다.

cron 환산은 채점 시 검산한다: `Etc/UTC` + 9h = KST. 요일·날짜 넘김을 포함해 검증한다.

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 기준 |
|---|------|-----------|
| 1 | 자원 구분 없는 단일 무게 점수 | 등급·점수만 있고 read/write 자원 표기 없음 |
| 2 | 근거 없는 무게·충돌 판정 | 등급 또는 CONFLICT에 file:line·쿼리·리소스 한도 근거 0건 |
| 3 | 정적 추정 한계 미명시 | 실측 없이 "겹친다" 확정 서술, 실측 명령·한계 문구 없음 |
| 4 | 하드코딩 토폴로지 무검증 인용 | 참조 문서 호스트·스키마 값을 재확인 없이 리포트에 옮김 |
| 5 | 다른 자원 동시각을 충돌로 판정 | REPLICA·외부 전용 잡을 PRIMARY 충돌로 계상 (동일 호스트 근거 없이) |
| 6 | 동일 호스트 확인 없이 자원 분리 단정 | AGGREGATE·REPLICA 호스트 확인 없이 "부하 분리됨" 결론 |
| 7 | 인증 미확인 진행 | gcloud 인증·권한 확인 없이 수집 결과를 추정으로 채움 |
| 8 | 스케줄 없는 잡 일괄 폐기 단정 | 일회성 / 폐기 / 누락 3분류 없이 처리 |
| 9 | 프로파일 이름만으로 write 자원 판정 | 프로파일 존재를 근거로 PRIMARY 무영향 결론 (write 템플릿 미확인) |
| 10 | 장식 기호 잔존 | 이모지·★·✅ 등 1개 이상 |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- AUTO FAIL 10건 모두 0
- 위반 시 즉시 FAIL 판정 (다른 축 점수 무관)

### 축 2. 기능 정확도 (100점 만점, evaluation-rubric.md 기반)

| 항목 | 배점 |
|------|------|
| 자원별 구분 판정 | 20 |
| 무게 산정 근거 | 20 |
| cron → KST 환산 + 타임라인 | 15 |
| 충돌 판정 정확도 | 15 |
| 재배치 제안 실행 가능성 | 10 |
| 한계·미확정 명시 | 10 |
| 리포트 구조·서식 | 10 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| Phase 0 파라미터 확정 | 프로젝트·리전·모듈·정의방식·디스패치·토폴로지·프로파일 |
| Phase 0.5 인증 확인 | `gcloud config get-value account` + `projects describe`. 차단 시 사용자 유도 |
| 토폴로지 재확인 | 설정 파일 grep으로 호스트·스키마 확인. 문서 값과 차이 감지 |
| 코드 매핑 | `job_name` → 클래스·Reader 쿼리·Writer. 미검출 시 원인 2분류 |
| 부하 프로파일 | A~G 축 + 산출 CSV 컬럼 + `notes` 에 file:line |
| 교차검증 | 리소스 한도 ↔ 코드 부하 (과할당·OOM 리스크) |
| 타임라인 | 자원별 행 분리 + 고빈도 baseline 별도 |
| 재배치 변경표 | 구체 cron + 이유 + cron/코드 분리 |
| 실측 보강 | `gcloud run jobs executions list` 명령 제시 |
| 자기 검증 | 13항목 체크리스트 수행 |

### 축 4. Baseline 비교

- Baseline (스킬 미사용): `joined.csv` 를 표로 옮기고 cpu/memory 순 정렬, 동시각 잡을 자원 구분 없이 "충돌"로 계상, cron을 UTC 그대로 표기, 근거·한계 없음
- With-Skill: 자원별 판정 + write 템플릿 확인 + KST 환산 + 같은 자원 한정 충돌 + file:line 근거 + 실측 한계 + 구체 cron 변경표
- 합격: With-Skill > Baseline + 20점

### 축 5. 일관성

- TC-1 `--repeat 3` 권장
- 편차 ≤ 15점
- 특히 **충돌 건수 판정**(01:00 PRIMARY 3건)이 회차마다 동일한지 확인

### 축 6. 효율성

- 기록용 (합격 조건 아님)
- 토큰 사용량 / 응답 시간
- 잡 수 >15 시 Explore 서브에이전트 병렬 분산 여부 (효율 항목으로 기록)

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | AUTO FAIL 0건 |
| 축 2 기능 정확도 | Happy Path 75점+ |
| 축 3 행동 패턴 | 체크리스트 80%+ |
| 축 4 Baseline | With-Skill > Baseline + 20점 |
| 축 5 일관성 | 편차 ≤ 15점 (--repeat 3 시) |

→ 모두 충족 시 **실전 배치 가능** (forge INDEX.md 상태 갱신)

---

## 커버리지 갭 (v0.1 기준, 하네스 개선 시 우선 반영)

- 잡 수 >15 Explore 서브에이전트 병렬 분산 TC 없음 (TC-1은 8잡)
- `collect.sh` 실제 실행 검증 없음 (인자 필수 처리·`PROFILE_MARKER` 동작 미검증)
- `@Scheduled` 인앱 스케줄 잡 수집 TC 없음
- 실측 duration을 실제로 받아 "추정 → 확정"으로 갱신하는 2회차 시나리오 없음
- 전체 감사 리포트 파일 산출물(7섹션 `.md`)을 실제로 쓰는 검증 없음 — 응답 내 본문으로 채점

---

## 리포트 양식

`proving-grounds/evals/batch-schedule-audit/report.md` 에 다음 섹션 포함:

1. 전체 점수 (100점 만점)
2. 6축별 결과
3. AUTO FAIL 검증 결과 (10건 각각)
4. TC별 결과 (점수 + 위반 요약)
5. cron 환산 검산 표 (기대 KST vs 산출 KST)
6. Baseline vs With-Skill 비교 표
7. 커버리지 갭 + 개선 권고
