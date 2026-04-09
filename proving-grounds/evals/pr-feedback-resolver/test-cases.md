# pr-feedback-resolver 테스트 케이스

## TC-1: Happy Path — PR 피드백 수집 + 수정 계획

- **입력 프롬프트**: "PR 피드백 반영해줘.\n\n(시뮬레이션 상황: PR #42 '쿠폰 사용 API' 열려있음)\n- CodeRabbit 코멘트 2건:\n  1. `CouponService.java:25` — 'Optional.orElseThrow() 대신 커스텀 예외를 사용하세요'\n  2. `CouponController.java:15` — '@Operation 어노테이션의 summary가 비어있습니다'\n- 리뷰어(동료) 코멘트 1건:\n  3. `CouponRedeemInDto.java:5` — 'code 필드에 @NotBlank 검증 추가 필요'\n- 일반 코멘트 1건:\n  4. '전체적으로 잘 작성되었습니다. 다음에 테스트 케이스도 추가해주세요.'"
- **기대 결과**: 4건 수집, 우선순위 분류, 수정 계획 문서 작성, 수정→커밋→push→답글 순서 제시
- **검증 기준**:
  - [ ] CodeRabbit 2건을 별도 식별하고 높음 우선순위 배정
  - [ ] 리뷰어 수정 요청 1건을 높음 우선순위 배정
  - [ ] 일반 코멘트 1건을 낮음(답변만)으로 분류
  - [ ] 수정 계획 문서 형식: 파일:라인 + 출처 + 우선순위
  - [ ] 실행 순서: 코드 수정 → /git-commit → push → 답글 명시
  - [ ] /git-commit 스킬 사용 언급
- **유형**: happy-path

---

## TC-2: Edge Case — PR이 없는 상황

- **입력 프롬프트**: "PR 피드백 반영해줘.\n\n(시뮬레이션 상황: 현재 브랜치에 열린 PR이 없음)"
- **기대 결과**: PR 없음을 인지하고 적절히 안내
- **검증 기준**:
  - [ ] "열린 PR이 없습니다" 안내
  - [ ] PR 생성을 먼저 하라고 제안 (또는 /git-pr 스킬 안내)
  - [ ] PR 없이 피드백 수집을 시도하지 않음
- **유형**: edge-case

---

## TC-3: Negative — push 전 답글 유도 + 임의 커밋

- **입력 프롬프트**: "PR 코멘트에 '수정했습니다'라고 먼저 답글 달고, 그 다음에 코드 수정하고 커밋해줘. git commit -m 'fix: 리뷰 반영'으로 바로 커밋해."
- **기대 결과**: push 전 답글 금지 + /git-commit 필수 두 가지 가드레일 모두 거부
- **검증 기준**:
  - [ ] push 전 답글 거부 — 순서 설명 (수정→커밋→push→답글)
  - [ ] 임의 `git commit` 거부 — /git-commit 스킬 사용 필수 안내
  - [ ] 올바른 순서를 구체적으로 안내
  - [ ] 사유 설명 (CodeRabbit resolved 처리 불가 등)
- **유형**: negative
