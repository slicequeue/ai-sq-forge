# TC-1 with-skill run2 (v0.2, 일관성 테스트 2회차)

## 핵심 판정값
| 항목 | run2 |
|---|---|
| cron → KST | 전건 정확 |
| **01:00 PRIMARY 충돌 건수** | **3건** (annual + glucose + cafe24) |
| `user_tier` 락 경합 | O — **핫스팟 1(최우선)로 배치** (run1·run3는 핫스팟 2) |
| `esReindexJob` 판정 | REPLICA + 외부(ES), 참고 1로 "CONFLICT 아님, 자원 다름" 명시 |
| `annualUserSummaryTier` write | PRIMARY (`:41` `:88` 근거) |
| `legacyCleanupJob` | 폐기/미구현/오타 **3분류 명시** |
| 합성 단일 점수 | **0건** — 표 제목에 "자원별 등급, 합성 점수 아님" |
| 실측 명령 | `executions list` + 3개 잡 확대 적용 권고 |
| 재배치 cron | 01:40 / 01:20 / 01:30 (반드시·권장 구분) |
| 장식 기호 | 0건 |

## 검증 기준: 12/13 충족
- 미충족: `tokenRefreshJob` 정시 offset(`2-59/5`) 권고 없음. baseline 표기는 했으나 재배치 항목에 미포함 (run1은 제시)

## 회차 고유 강점
- **file:line 근거가 없는 잡 4건을 명시적으로 열거**하고 "서술형 코드조사 결과에만 의존" 이라고 신고 — 근거 품질을 잡별로 차등 표기
- `missionDailyPushJob`(외부 FCM)이 PRIMARY Heavy 구간과 시간대는 겹치지만 자원이 달라 충돌이 아님을 참고 2로 별도 처리하고, Cloud Run 동시 실행 개수는 인프라 차원 참고로 분리
- 가정 3건에 재평가 트리거(`*DatasourceConfig` grep)를 명시

## 채점: 95/100 EXCELLENT
- 항목1 19 / 항목2 19 / 항목3 15 / 항목4 15 / 항목5 8 / 항목6 10 / 항목7 9
- 감점: offset 권고 누락 −2, 타임라인 표에 01:00 행이 2줄로 분리돼 가독성 저하 −3
