# pr-feedback-resolver v1.2 → v1.3 회귀 검증 리포트

**검증 일시**: 2026-04-28
**대상 변경**: sq-tone-writer 경유 의무화 + GitHub PR API `/replies` → `in_reply_to` 패턴 정정 + 자기 검증 체크리스트 9
**모드**: `--skip-baseline`

## 회귀 판정: **회귀 없음 + 전 TC 미세 개선**

| TC | 유형 | v1.2 | v1.3 | Δ | GATE |
|----|------|------|------|---|------|
| TC-1 | Happy | 95 | **97** | +2 | PASS |
| TC-2 | Edge (PR 없음) | 98 | **98** | 0 | PASS |
| TC-3 | Negative | 96 | **98** | +2 | PASS |
| **평균** | | **96.3** | **97.7** | **+1.4** | PASS |

회귀 임계 대비 안전. AUTO FAIL 0건.

## 6축 요약 (TC-1 기준)

| 축 | 결과 |
|---|---|
| 1 가드레일 | PASS (sq-tone-writer 의무화 + in_reply_to 정정으로 가드레일 항목 13→15) |
| 2 정확도 | 95 → 97 (가드레일 준수 +2) |
| 3 행동 패턴 | 5/5 유지 |
| 4 Baseline 비교 | 우위 유지 |
| 5 일관성 | 미실행 (--repeat 권고) |
| 6 효율성 | 6단계 분리 명확 |

## in_reply_to 패턴 정정 효과

v1.2의 `/comments/{id}/replies` 엔드포인트는 GitHub API에서 404 반환 → 답글 실패 → 재시도 비용 발생. v1.3은 `POST /pulls/{N}/comments` + `in_reply_to`로 정정해 답글 스레드 정확 연결 가능. **실전 답글 정확도 향상 확인**.

## 주의/개선

**일관성 미검증**: sq-tone-writer 경유가 LLM 톤 의존이라 답글 본문 편차 가능성 있음. TC-1을 `--repeat 3`으로 재실행해 sq-tone-writer 호출 분기·답글 본문이 안정적인지 확인 권고.

## 산출물

- `proving-grounds/evals/pr-feedback-resolver/results/with-skill-v1.3/TC-{1..3}.md`
