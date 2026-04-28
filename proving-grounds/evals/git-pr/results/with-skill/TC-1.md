# TC-1 With-Skill (git-pr 적용)

## 시뮬레이션 응답

변경사항 분석을 진행한다.

```bash
git status                                          # working tree clean
git branch --show-current                           # api/fix/null-check-coupon
git log dev..HEAD --oneline                         # fix: 쿠폰 조회 시 null 처리 누락 수정
git diff dev..HEAD --stat                           # CouponService.java | 6 +++++-
gh pr list --head api/fix/null-check-coupon --state open  # (열린 PR 없음)
```

- base: `dev` (일반 변경, hotfix 아님)
- 원격 push 완료 → 추가 push 불필요
- 동일 head 브랜치에 열린 PR 없음 → 신규 생성

## PR 본문 (작성)

**제목**: `fix: 쿠폰 조회 시 null 처리 누락 수정`

```markdown
## Why need this PR❓

쿠폰 조회 API에서 존재하지 않는 쿠폰 ID로 요청이 들어올 때 **NullPointerException**이 발생해 500 에러로 응답되던 문제.

**원인**: `CouponService.getCoupon()`에서 repository 조회 결과의 null 처리가 누락되어, 이후 DTO 변환 시점에 NPE 발생.

## Changes ✌️

**파일 1개, +5 / -1 lines**

| 파일 | 변경 |
|---|---|
| `pghd/coupon/application/CouponService.java` | 쿠폰 조회 결과가 비어 있을 때 null 반환 처리. 컨트롤러 단에서 404로 매핑되도록 정리 |

---

📘 **상세 분석/측정 결과/근거 문서는 Notion으로 별도 공유 예정**

## Test list 📝

- [x] `./gradlew :pghd:test` 통과 (회귀 없음)
- [x] 로컬에서 존재하지 않는 쿠폰 ID 요청 → 404 응답 확인
```

## 자기 검증 체크리스트

- [x] 분량: 약 25줄 (단순 fix는 빈약하지 않은 범위 내 짧게)
- [x] Why: 현상 1줄 + 원인 1줄
- [x] Changes: 표 1줄
- [x] 측정/배포/후속 섹션 생략 (해당 없음)
- [x] Test list 포함
- [x] 한국어 본문, AI 표기 없음, docs/ 링크 없음
- [x] target `dev`

## 실행 명령

```bash
gh pr create \
  --base dev \
  --head api/fix/null-check-coupon \
  --title "fix: 쿠폰 조회 시 null 처리 누락 수정" \
  --body "$(cat <<'EOF'
## Why need this PR❓
...(위 본문)...
EOF
)"
```

## 출력

신규 생성: https://github.com/{org}/{repo}/pull/{N}
