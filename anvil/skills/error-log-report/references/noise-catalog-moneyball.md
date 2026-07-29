# 알려진 노이즈 카탈로그 — moneyball (prd-pasta / run-prd-pasta-api)

> 프로젝트별 카탈로그 파일 규약: `references/noise-catalog-{project}.md`.
> 대상 프로젝트의 카탈로그가 없으면 첫 회차 집계 결과로 신규 생성하고, 전건을 "최초 관측"으로 표기한다.
> 최종 갱신: 2026-07-27 (moneyball 실전 운영본 역수입)

## 대상

| 항목 | 값 |
|------|-----|
| GCP 프로젝트 | `prd-pasta` |
| 리전 | `asia-northeast3` |
| 서비스 | `run-prd-pasta-api` |
| 집계 기준 | `jsonPayload.level = "ERROR"` (앱 레벨) |

---

## 시그니처 표

새 집계 결과를 이 표와 대조해, 카탈로그에 없는 시그니처는 "신규, 조치 필요"로 표시한다.

| 시그니처(부분 문자열) | 유형 | 분류 |
|---|---|---|
| `ExhaustedRetryException` + `updateDailyGlucoseStatistics` / `analysis_daily_glucose_statistics.unique_device_id_date` | 글루코스 일별 통계 중복키(A)가 `@Recover` masking(D)에 가려짐 | 기존 확정. 자가 회복(다음 측정값 재계산), 원본 정상 |
| `mission_daily_achievement.unique_mission_daily_id_user_id_date` | 데일리미션 달성 중복 삽입 경합 | 기존 인지 |
| `mission_achievement.unique_user_id_mission_type` | 미션 달성 집계 중복 삽입 경합 | 기존 인지 |
| `walking bulkInsertRecords` / `Error in walking bulkInsertRecords` | 걷기 대량 삽입 자정 경계 중복키 | 기존 인지. 자정 경계 수정 반영·재발 여부 확인 |
| `Only temporary records can be approved` | 임시 레코드만 승인 가능 | 기존 인지 |
| `이미 진행 중인 체형 예측 요청이 있습니다` | 체형 예측 중복 요청 | 기존 인지 |
| `PghdSleepRecord.getAsleepData()` + `is null` (NullPointerException) | 수면 리포트 조회 시 null 방어 누락(`SleepReportService.getDailySleepReport`, 삭제된 sleepId 조회) | 수정 코드 존재(#8230, 07-22)이나 관측 리비전 미배포. 배포 반영 여부 확인. 07-25 재관측 |
| `PghdSleepProxyController` + `Asleep API response - Status: 504` (Endpoint request timed out) | 수면 Asleep 프록시 upstream 응답 시간 초과 | 기존 반복 관측(07-21 이후). 외부 API 일시 오류, 사용자 대면. 로그 레벨 WARN 강등 권고 미반영 |
| `PghdSleepProxyController` + `Asleep API response - Status: 409` (failed to acquire lock for closing a session) | 수면 Asleep 프록시 세션 종료 락 획득 실패 | 기존 반복 관측(07-21 이후). 외부 API 일시 오류, 사용자 대면. 로그 레벨 WARN 강등 권고 미반영 |
| `SleepRecordService.completeSleepAsleepRecord` → `PGHDRecordMapService.createRecordMap` + `IllegalStateException` (SLEEP 매핑 중복) | 수면 기록 매핑 중복 삽입(완료 요청 중복 경합 추정) | 기존 인지(07-22 관측). 방어 로직 정상 동작, 긴급도 낮음 |
| `FirebaseAuthException` + Identity Platform `502` | Identity Platform 응답 502 | 기존 인지(07-22 관측). 외부 의존성 일시 오류 |
| `KakaoAuthProvider` + `RetryExhaustedException` (`Retries exhausted: 1/1`) + `Connection prematurely closed BEFORE response` | 카카오 소셜 인증 호출 응답 전 연결 종료로 재시도 소진 | 신규 관측(07-24). 외부 인증 의존성 일시 오류, 단발성 자가 회복 |
| `SleepDailyAiAnalysisServiceClient.createSleepDailyAiMessage` + `WebClientRequestException` (`recvAddress(..) failed: Connection reset by peer`, `analyze-sleep`) | 수면 일별 AI 분석(vc-prd-aix-sleep-api) 호출 중 커넥션 리셋 | 신규 관측(07-25). 외부 의존성 일시 오류, 사용자 대면. FoodShot okhttp `Connection reset by peer`와 다른 경로(WebClient) |

---

## 중복 로깅 배수 (moneyball 실측)

후처리 실패 1건이 아래 3개 경로에 각각 기록되어 **로그 3줄 = 실패 이벤트 1건**이 되는 사례가 있다.

- 도메인 이벤트 핸들러
- AOP Aspect
- `AsyncUncaughtExceptionHandler`

집계 시 반드시 분리해 제시한다.

---

## 참고 문서

- 동시성 후처리 실패 유형(A~D) 정의와 대응 전략: moneyball 레포 루트 `event-storm-transaction-strategies.md`
  - A: 중복키 경합 / D: `@Recover` masking. 위 표의 첫 행이 "A가 D에 가려진" 조합이다.
  - **forge에는 이 문서가 없다.** moneyball 외 프로젝트에서 이 스킬을 쓸 때는 해당 참조를 생략하고, 유형 분류는 관측된 예외 체인으로만 판정한다.

---

## 갱신 정책

1. 판정을 확정한 새 유형은 시그니처 표에 한 줄 추가한다 (시그니처 / 유형 / 분류).
2. "수정 코드 존재, 미배포" 항목은 배포 확인 후 분류를 갱신하거나 표에서 제거한다.
3. 로그 레벨 강등이 반영되면 해당 행을 제거한다(더 이상 ERROR로 안 잡힘).
4. 카탈로그 갱신은 보고서 작성과 같은 회차에 수행한다. 다음 회차로 미루지 않는다.
