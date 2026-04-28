# java-spring-coder v1.3 → v1.4 회귀 검증 리포트

**검증 일시**: 2026-04-28
**대상 변경**: OAuth2 Client 격리, Non-bean `@Transactional` 금지, SecurityContext save/restore, env yml 4곳, 자기 검증 체크리스트 14·15·16
**모드**: `--skip-baseline` (with-skill 단독 채점)

## 회귀 판정: **PASS (회귀 없음)**

| TC | 유형 | v1.3 | v1.4 | Δ |
|----|------|------|------|---|
| TC-1 | Happy Path | 100/100 | **100/100** | 0 |
| TC-2 | Edge Case | 85/85 | **85/85** | 0 |
| TC-3 | Negative | PASS (3건 거부) | **PASS** (+ admin 13~16 추가 안내) | 미세 향상 |

회귀 임계 (-10점) 미해당. AUTO FAIL 0건.

## 6축 요약

| 축 | 결과 |
|---|---|
| 1 가드레일 | PASS |
| 2 정확도 | PASS (TC-1·TC-2 100%) |
| 3 행동 패턴 | 6/6 모두 충족 |
| 4 Baseline 비교 | 동률 PASS (회귀 임계 미해당) |
| 5 일관성 | N/A (--repeat 미지정) |
| 6 효율성 | 토큰 +1~4% (체크리스트 추가분) |

## 신규 가드레일 적용 효과

TC-1~3은 OAuth2/Non-bean Tx 시나리오를 **직접 트리거하지 않아 N/A로 안전 격리**. 자기 검증 14·15·16번이 추가됐지만 무관 항목 N/A 처리로 본문 길이 안전(323줄, 400줄 한도 내). 음의 영향 0건.

## 주의/개선

현 하네스 TC 3개는 v1.4 신규 가드레일을 **실측하지 못함**. 다음 라운드 권고:
- TC-4 (Edge): OAuth2 Client 커스터마이징 + admin 모듈 + 외부 API 추가 시나리오
- TC-5 (Negative): Non-bean에 `@Transactional` 유도

현재로서는 회귀 안전성만 확인됐고, 신규 가드레일의 효과 측정은 미수행 상태.

## 산출물

- `proving-grounds/evals/java-spring-coder/results/with-skill-v1.4/TC-{1..3}.md`
