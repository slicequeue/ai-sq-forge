# 프로젝트별 자원 토폴로지 — moneyball (prd-pasta)

> 프로젝트별 토폴로지 파일 규약: `references/topology-{project}.md`.
> **이 문서의 값은 스냅샷이다.** 호스트·스키마는 변경될 수 있으므로 매 실행 설정 파일에서 재확인한다 (하드 가드레일 #4).
> 최종 확인: 2026-06-26 (moneyball 실전 운영본 역수입)

## 대상

| 항목 | 값 |
|------|-----|
| GCP 프로젝트 | `prd-pasta` |
| 리전 | `asia-northeast3` |

---

## 배치 코드 모듈 (2개 병존)

| 모듈 | 성격 | 잡 정의 방식 |
|---|---|---|
| `batch/` | 레거시 | 커스텀 `Job` 인터페이스 + `@Component("<jobName>")`. 로직은 주입된 `service/` |
| `batch-app/` | 신규 | Spring Batch `*JobConfig.java` (`new JobBuilder("<jobName>", ...)`). 잡 빈명이 `--job.name` |

- 디스패치: `batch/.../service/JobStarter.java` 가 `--job.name` 으로 `@Component` 빈을 찾아 실행.
- args 예: `--job.name=mealDailyReviewPushJob;locale=ko_KR;fetchSize=500;processChunkSize=100` → `;` 구분.
- **실재하는 파라미터 오타**: `chinkSize`(chunkSize 오타), `zoenId`(zoneId 오타). 오타 파라미터는 무시되어 기본값으로 동작하므로 부하 추정이 틀어진다. 코드에서 읽는 키와 대조 필수.

---

## 자원 토폴로지 (prod, 2026-06-26 확인값)

| 자원 | 위치 | 설정 출처 |
|---|---|---|
| DB-PRIMARY | `10.60.23.208 / pasta` | `batch/.../application-prod.yml`, `batch-app/.../application-prod.yml` (`spring.datasource.url`) |
| DB-REPLICA | `10.60.23.12 / pasta` | `application-summary.yml` (`pasta.summary.datasource.replica`) |
| DB-AGGREGATE | `10.60.23.208 / pasta_aggregate` | `application-summary.yml` (`pasta.summary.datasource.summary`) |

> **AGGREGATE가 PRIMARY와 동일 호스트(`.208`)다.** 논리 스키마만 분리돼 있고 물리 디스크·IO·CPU는 공유한다. 따라서 summary 잡의 **쓰기 부하는 PRIMARY 호스트 부하에 합산**된다. 호스트가 여전히 같은지 매번 확인하고 리포트에 명시한다.

---

## 프로파일 분기 (summary)

Cloud Run 잡 env에 `spring.profiles.include=summary` 가 있으면 적용. `collect.sh` 의 `summary_profile` 컬럼으로 확인.

라우팅 정본: `batch/.../configuration/SummaryDatasourceConfig.java`

| 빈 | 자원 |
|---|---|
| `replicaDataSource()` (`@Primary`) | 기본 읽기 = **REPLICA** (읽기 전용) |
| `summaryDataSource()` / `summaryJdbcTemplate()` | 쓰기 = **AGGREGATE** (`pasta_aggregate`) |

코드에서 `pastaReplicaJdbcTemplate`(읽기) vs `summaryJdbcTemplate` / `pastaMainJdbcTemplate`(쓰기) 사용처를 grep으로 확인한다.

> **주의**: summary 프로파일이 붙어 있어도 **일부 잡은 REPLICA 읽기 + PRIMARY 직접 쓰기**다. 예: `annualUserSummaryTier` 는 `pastaMainJdbcTemplate` 로 운영 DB에 write. 프로파일 이름만 보고 "PRIMARY를 안 건드린다"고 판정하면 오판이다. **반드시 write 템플릿을 확인한다.**

---

## 외부 시스템 타격 잡

DB 외에 외부 I/O가 주 병목인 잡:

| 분류 | 대상 |
|---|---|
| 파트너·기기 연동 | Cafe24, NovoNordisk, i-SENS, Inbody |
| 분석 | Amplitude |
| 검색 색인 | Elasticsearch |
| 푸시 | FCM |
| 파일·알림 | Slack, GCS |

잡의 client·service에서 외부 호출 패턴(건수·배치 여부·rate limit)을 확인해 `external_io` 에 기록한다.
