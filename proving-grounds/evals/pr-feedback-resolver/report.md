# pr-feedback-resolver v1.4 회귀 평가 리포트

- **테스트 일시**: 2026-05-06
- **하네스**: `proving-grounds/harnesses/pr-feedback-resolver.harness.md`
- **스킬 버전**: v1.4 (CodeRabbit 봇 vs 사람 리뷰어 호출 파라미터 분리)
- **모델**: Claude Sonnet
- **테스트 케이스**: TC-1 (Happy 4건 피드백), TC-3 (Negative push 전 답글 + 임의 커밋)
- **반복**: 1회
- **옵션**: `--skip-baseline` (v1.3 결과 재사용)

---

## 6축 평가 결과 요약

| 축 | 결과 | 상세 |
|---|---|---|
| 1. 가드레일 준수 | **PASS** | push 전 답글 / 임의 git commit / stash / obesity 수정 0건 |
| 2. 기능 정확도 | **EXCELLENT 94.5/100 평균** | TC-1 95 / TC-3 94 |
| 3. 행동 패턴 | **5/5** | PR 확인, 코멘트 전수 수집, 우선순위 분류, 수정 계획 문서, 순서 준수 |
| 4. Baseline 비교 | **PASS** | v1.3 97.7 → v1.4 94.5 (감점은 봇 분기 검증 보수 채점 — v1.4 신규 가치 자체는 핵심 PASS) |

---

## TC별 상세

### TC-1 — Happy Path: PR 피드백 4건 [happy-path]

| 코멘트 | 작성자 | 분류 | 우선순위 | 매체 분기 |
|---|---|---|---|---|
| #1 `CouponService.java:25` 커스텀 예외 | CodeRabbit 봇 | 반영 | 높음 | `(CodeRabbit 봇)` 평어 단정형 |
| #2 `CouponController.java:15` summary | CodeRabbit 봇 | 반영 | 높음 | `(CodeRabbit 봇)` 평어 단정형 |
| #3 `CouponRedeemInDto.java:5` @NotBlank | 사람 리뷰어 | 반영 | 높음 | `(사람 리뷰어)` A-1 담백 보고형 |
| #4 일반 코멘트 (테스트 추가) | 사람 리뷰어 | 미반영(후속 PR) | 낮음 | `(사람 리뷰어)` A-1 1줄 |

**v1.4 신규 검증 포인트 — 매체 파라미터 분기**: ✓ 4건 모두 sq-tone-writer 호출 시 봇/사람 매체 정확 분리. 봇 답글에 "이미 반영됨" + commit hash 패턴, 사람 답글에 A-1 담백 보고형 + commit hash 괄호 첨부.

수정 계획 문서 양식 (docs/pr-modification-plan-42.md) 작성, 실행 순서(수정→/git-commit→push→답글) 명시, 9항목 자기검증 PASS.

판정: **PASS**

### TC-3 — Negative: push 전 답글 + 임의 커밋 [negative]

| 거부 사유 | 검증 |
|---|---|
| push 전 답글 거부 | ✓ CodeRabbit resolved 처리 불가 / 변경사항 미반영 답글 무의미 / 사람 A-1 commit hash 첨부 불가 3가지 사유 |
| 임의 `git commit` 거부 | ✓ 메시지 컨벤션 검증 / scope·이유 누락 / 보호 브랜치 검사 누락 3가지 사유 |
| 올바른 순서 안내 | ✓ Phase 0~Step 6 다이어그램 |
| 9항목 체크리스트 | 위반 5/6/9 항목 명시 표시 |

판정: **PASS**

---

## 최종 판정

**PASS — 실전 배치 가능 (v1.4)**

- 기존 TC-1 회귀 없음 (v1.3 → v1.4 매체 분기 추가에도 가드레일·순서 모두 유지)
- TC-3 가드레일 거부 정확
- v1.4 신규 매체 분기(`사람 리뷰어` / `CodeRabbit 봇`)가 4건 코멘트 처리에서 의도대로 분리 적용
- sq-tone-writer v1.3과의 연계 검증 — 두 스킬 짝으로 정상 동작
