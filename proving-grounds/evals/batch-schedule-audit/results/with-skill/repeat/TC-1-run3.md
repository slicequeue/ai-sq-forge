# TC-1 with-skill run3 (v0.2, 일관성 테스트 3회차)

## 핵심 판정값
| 항목 | run3 |
|---|---|
| cron → KST | `0 16`=01:00 / `10 16`=01:10 / `0 17`=02:00 / `50 7-21`=16:50~06:50 15회 / `*/5`=288회 — 전건 정확 |
| **01:00 PRIMARY 충돌 건수** | **3건** (annual + glucose + cafe24) |
| `user_tier` 락 경합 | O (01:00 vs 01:10, 둘 다 chunk 없음 → LONG 추정) |
| `esReindexJob` 판정 | REPLICA+ES 별도 자원, CONFLICT 아님 |
| `annualUserSummaryTier` write | PRIMARY (`:88` 근거) |
| `legacyCleanupJob` | 폐기/오타 미구분, 콘솔·IaC + git 이력 확인 2항목 제시 |
| 합성 단일 점수 | **0건** — "무게는 자원별 Heavy/Medium/Light 3단으로만 표기한다(합성 점수 미산출)" 명시 |
| 실측 명령 | `executions list` 제시 |
| 재배치 cron | `0 18 * * *`(cafe24 03:00), `40 16 * * *`(userTierRecalc 01:40) 구체값 |
| 장식 기호 | 0건 |

## 검증 기준: 13/13 충족

## 회차 고유 강점
- **무게를 read/write 2개 컬럼으로 분리** — 같은 잡의 읽기 Heavy / 쓰기 Medium을 따로 표기 (run1은 단일 weight 컬럼). v0.2 가드레일 취지에 더 정합
- `glucoseDailyStatisticsJob`의 PRIMARY 판정을 "`summary_profile=-` 기반 규칙 추정"으로 명시하고, **추정이 틀려도 물리 호스트 겹침 결론은 유지될 가능성**까지 2단 논증
- 핫스팟 4-3에서 근거 불충분을 이유로 **판정 자체를 보류** (가드레일 준수 명시)
- `cafe24SyncJob`의 부하 근거가 얕음을 스스로 신고하고 과할당 판단을 보류
- 재배치 대안으로 cron 분리보다 **완료 트리거 체이닝**을 제시

## 채점: 96/100 EXCELLENT
- 항목1 자원구분 20 / 항목2 무게근거 19 / 항목3 cron환산 15 / 항목4 충돌판정 15
- 항목5 재배치 9 / 항목6 한계명시 10 / 항목7 구조 8
- 감점: 타임라인을 ASCII 다이어그램으로 표현해 가독성이 표보다 낮음 −2, `userTierRecalcJob` read 자원 미상 −2

## AUTO FAIL: 0건
