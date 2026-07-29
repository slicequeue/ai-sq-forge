# 코드 매핑 + DB 자원 판별

`--job.name=<X>` 값을 코드에 매핑하고, 각 잡이 어느 DB·시스템을 타격하는지 판별하는 방법론.

프로젝트별 실제 모듈 구조·호스트 값은 `topology-{project}.md` 참조. **그 값도 매 실행 재확인한다.**

---

## 1. job.name → 코드

먼저 잡 정의 방식을 판별한다. 한 레포에 두 방식이 섞여 있는 경우가 흔하다(레거시 + 신규 마이그레이션 중).

| 정의 방식 | 특징 | 찾는 법 |
|---|---|---|
| 커스텀 `Job` 인터페이스 (레거시형) | `@Component("<jobName>")` 가 자체 `Job` 인터페이스 구현, 로직은 주입된 `*Service` | `grep -rln '"<jobName>"' <module>/src/main/java` → 해당 클래스의 `run()` 이 호출하는 Service 추적 |
| Spring Batch (표준형) | `*JobConfig.java` 에서 `new JobBuilder("<jobName>", ...)`, 또는 빈명이 곧 잡명 | `grep -rln '<jobName>' <module>/src/main/java` → JobConfig의 Reader 쿼리 / Processor / Writer |
| `@Scheduled` 인앱 스케줄 | Cloud Scheduler가 아니라 앱 내부 스케줄 | `grep -rn '@Scheduled' --include=*.java` — **Cloud Run Jobs 목록에 안 나오므로 별도 수집** |

### 디스패치 진입점

`--job.name` 을 받아 빈을 찾는 진입점(`JobStarter` 등)을 찾아 args 규약을 확인한다.

- 구분자 확인: `--job.name=mealDailyReviewPushJob;locale=ko_KR;fetchSize=500;processChunkSize=100` → `;` 구분 파라미터.
- 파라미터 이름을 그대로 신뢰하지 않는다. **오타가 실재한다** (예: `chinkSize`, `zoenId`). 코드에서 실제로 읽는 키와 대조한다 — 오타 파라미터는 무시되어 기본값으로 동작하므로 **부하 추정이 틀어진다**.

### 매핑 실패 시

`--job.name` 이 코드에 없으면 두 가능성을 **모두** 확인한다.

1. 코드 없음 — 폐기된 잡이거나 미구현 Cloud Run Job (리소스만 할당돼 있음)
2. 오타 — 잡 정의 쪽 또는 args 쪽 철자 불일치

어느 쪽인지 확정해 리포트의 "운영 점검 필요" 섹션에 올린다. 일괄 "폐기"로 단정하지 않는다.

---

## 2. DB 자원 판별 (자원별 평가의 핵심)

기본값은 운영 **PRIMARY**다. 예외는 읽기/쓰기 자원을 갈아타는 프로파일이다.

### 절차

1. **프로파일 분기 확인** — Cloud Run 잡 env에 자원 전환 프로파일(예: `spring.profiles.include=summary`)이 있는지. `collect.sh` 의 `summary_profile` 컬럼으로 확인.
2. **DataSource 설정 클래스 추적** — 해당 프로파일의 `*DatasourceConfig.java` 에서
   - `@Primary` 가 붙은 DataSource = 기본 읽기 경로
   - 별도 이름의 DataSource·JdbcTemplate = 쓰기 경로
3. **코드에서 실제 사용 템플릿 grep** — 읽기 템플릿 vs 쓰기 템플릿 사용처를 확인한다.

> **가장 자주 틀리는 지점**: 프로파일이 붙어 있어도 **일부 잡은 REPLICA 읽기 + PRIMARY 직접 쓰기**다. 프로파일 이름만 보고 "이 잡은 PRIMARY를 안 건드린다"고 판정하면 오판이다. **반드시 write 템플릿을 확인한다.**

### 동일 호스트 여부 확인 (필수)

논리 스키마가 분리돼 있어도 **물리 호스트가 같으면** 디스크·IO·CPU를 공유한다. 이 경우 쓰기 부하는 PRIMARY 호스트 부하에 합산된다.

```bash
grep -rn "jdbc:mysql\|jdbc:postgresql" --include=application-*.yml <module>/src/main/resources
```

호스트가 같은지 매번 확인하고 리포트에 명시한다. 확인 없이 "자원 분리됨"이라 쓰지 않는다.

---

## 3. 외부 시스템 타격 잡

DB 외에 외부 I/O가 주 병목인 잡을 별도 분류한다. 잡의 client·service에서 외부 호출 패턴(건수·배치 여부·rate limit)을 확인해 `external_io` 에 기록한다.

| 유형 | 예시 |
|------|------|
| 파트너·기기 연동 API | 커머스 플랫폼, 의료기기 벤더 API |
| 분석·마케팅 | 이벤트 전송 SDK/S2S |
| 검색 색인 | Elasticsearch bulk |
| 푸시 | FCM 멀티캐스트 |
| 파일·알림 | GCS 업로드, Slack webhook |

같은 외부 시스템을 치는 잡들이 동일 시간대에 몰리면 **DB와 무관하게 충돌**이다 (rate limit·상대 서버 부하).
