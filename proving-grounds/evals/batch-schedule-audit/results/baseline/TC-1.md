# TC-1 baseline (happy-path: 전체 감사)

## 검증 기준 대조 — 10/13 충족 (baseline 중 최고)
- [x] cron → KST 환산 정확 (`0 16` = 01:00, `50 7-21` = 16:50~익일 06:50, 15회/일)
- [x] `annualUserSummaryTier` write PRIMARY 판정 (프로파일에 속지 않음)
- [x] 01:00 PRIMARY 충돌 3건 식별
- [x] `user_tier` 락 경합 + **기능 중복 의심**까지 지적 (무청크 duration 근거)
- [~] `esReindexJob` — REPLICA 읽기·DB 쓰기 없음 정확 판정. 단 그룹 D에서 "01:00 REPLICA 풀스캔과 동시 진행"을 충돌로 계상 → **REPLICA 내 충돌**이므로 규칙상 정당. PRIMARY 충돌로 오판은 없음
- [x] `tokenRefreshJob` 상시 배경 부하로 별도 표기 (그룹 E). 단 **정시 offset(`2-59/5`) 권고 없음**
- [x] `legacyCleanupJob` orphan config 판정 + 설정 제거 권고. 단 일회성/누락 3분류 명시는 없음
- [~] 무게 등급 file:line 근거 — 코드 사실은 인용하나 **file:line 표기 0건**, Heavy/Medium/Light 등급 자체를 안 매김
- [ ] 리소스↔코드 교차검증 — 16Gi 언급은 있으나 과할당·OOM 리스크 판정 없음
- [x] 재배치 변경표 O. 단 cron 표현식 대신 KST 시각 서술
- [x] cron 변경 / 코드 수정(청크 도입·체이닝) 분리
- [x] 정적 추정 한계 + duration 실측 필요 명시. 단 `gcloud run jobs executions list` 명령 미제시
- [x] 장식 기호 0건
- 추가 강점: AGGREGATE=PRIMARY 동일 호스트 인지 + "다른 DB니까 안전이라는 착시" 경고 / 확인된 사실 vs 가정 표 분리 / Cloud Run 쿼터 변수 지적

## 채점: 78/100 PASS
- 항목1 자원구분 17 / 항목2 무게근거 11 / 항목3 cron환산 13 / 항목4 충돌판정 14
- 항목5 재배치 7 / 항목6 한계명시 8 / 항목7 구조 8

## AUTO FAIL: 0건
## 특기
이 도메인에서 baseline(sonnet)이 예상보다 강함. 스킬의 격차는 happy-path보다 **negative TC(TC-4)에서 결정적으로 벌어짐**. 하네스 축4 합격선(+20점)을 happy-path 단독으로는 못 넘을 가능성 → 리포트에서 TC 유형별 분리 비교 필요.
