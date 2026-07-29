# TC-1 with-skill run1 (v0.2, 일관성 테스트 1회차)

## 핵심 판정값
| 항목 | run1 |
|---|---|
| cron → KST | 전건 정확 (01:00 / 01:10 / 02:00 / 16:50~06:50 / 5분) |
| **01:00 PRIMARY 충돌 건수** | **3건** (annual + glucose + cafe24) + tokenRefresh baseline 겹침 |
| `user_tier` 락 경합 | O (핫스팟 2, "겹침 가능"으로 한정) |
| `esReindexJob` 판정 | REPLICA 읽기 + 외부(ES), PRIMARY 미접촉 |
| `annualUserSummaryTier` write | PRIMARY (`:88` `pastaMainJdbcTemplate` 근거) |
| `legacyCleanupJob` | 폐기/오타 미확정, 일괄 폐기 단정 거부 |
| 합성 단일 점수 | **0건** — §5 제목에 "자원별, 합성 점수 없음" 명시 |
| 실측 명령 | `executions list` + "annualUserSummaryTier duration이 핫스팟 2·3 확정을 좌우" |
| 재배치 cron | `40 16`, `25 16`, `30 16`, **`2-59/5`(정시 회피 offset)** 구체값 |
| 장식 기호 | 0건 |

## 검증 기준: 13/13 충족

## 회차 고유 강점
- **`tokenRefreshJob` 정시 offset `2-59/5` 권고** — 3회차 중 이 회차만 제시. `load-rubric.md`의 offset 기법을 실제 적용
- **AGGREGATE 규칙 비적용 사례임을 명시** — summary 프로파일 2건 모두 쓰기가 PRIMARY이거나 DB 쓰기 없음 → "이번 데이터셋에서는 AGGREGATE 동일 호스트 규칙이 직접 적용되는 사례가 없다"고 정확히 한정
- 핫스팟 1에서 **테이블 단위 락 경합과 인스턴스 자원 경합을 구분** (다른 테이블이므로 락은 아니나 CPU·IO 동시 점유)
- `glucoseDailyStatisticsJob` write 자원 재확인 필요를 운영 점검 2번으로 올리며 **테이블명이 분석 스키마를 연상시킨다는 반대 정황**까지 제시
- 운영 점검 5항목 (run3는 3항목)

## 채점: 97/100 EXCELLENT
- 항목1 20 / 항목2 20 / 항목3 15 / 항목4 15 / 항목5 10 / 항목6 10 / 항목7 7
- 감점: `missionDailyPushJob`·`cafe24SyncJob` read 자원 미상 −3
