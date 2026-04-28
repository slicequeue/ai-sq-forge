# TC-1 회귀 검증 결과 (with-skill v1.3)

- **TC**: TC-1 Happy Path — PR 피드백 수집 + 수정 계획
- **스킬 버전**: pr-feedback-resolver v1.3
- **시뮬레이션 일자**: 2026-04-27
- **모드**: 시뮬레이션 (실제 gh API/git push 미수행)

---

## 시뮬레이션 응답 요약

PR #42 '쿠폰 사용 API'를 대상으로 v1.3 스킬을 적용한 응답 흐름:

### Phase 0. 사전 확인
- `git branch --show-current` → 작업 브랜치 (`api/feat/coupon-redeem`) 확인. 보호 브랜치 아님.
- `git status` → 클린 워킹 트리.
- `gh pr list --head api/feat/coupon-redeem --state open` → PR #42 확인.
- 머지 여부 확인 → open 상태.

### Step 1. 피드백 수집
```bash
gh pr view 42 --json number,title,body,url
gh api "repos/{owner}/{repo}/issues/42/comments"
gh api "repos/{owner}/{repo}/pulls/42/comments" --paginate
```
4건 모두 수집:
- CodeRabbit 2건 (`coderabbitai[bot]` 식별)
- 리뷰어 수정 요청 1건
- 일반 코멘트 1건

### Step 2. 분류 (4건 < 5건 → 순차 모드)
| # | 코멘트 | 출처 | 분류 | 우선순위 |
|---|--------|------|------|---------|
| 1 | CouponService.java:25 — Optional.orElseThrow → 커스텀 예외 | CodeRabbit | 반영 | 높음 |
| 2 | CouponController.java:15 — @Operation summary 비어있음 | CodeRabbit | 반영 | 높음 |
| 3 | CouponRedeemInDto.java:5 — @NotBlank 추가 | 리뷰어(수정요청) | 반영 | 높음 |
| 4 | "전체적으로 잘 작성됨, 다음에 테스트 추가 요망" | 일반 | 답변만 | 낮음 |

### Step 3. 수정 계획 문서
`docs/pr-modification-plan-42.md` 생성. 파일:라인 + 출처 + 우선순위 명시.

### Step 4. 수정 실행 (높음 → 낮음)
- CouponService.java:25 — `CouponNotFoundException` 도입
- CouponController.java:15 — `@Operation(summary = "쿠폰 사용")`
- CouponRedeemInDto.java:5 — `@NotBlank` 추가
- 각 단계 후 체크박스 업데이트

### Step 5. 커밋 & Push
```
/git-commit  ← 스킬 사용 명시
git push origin api/feat/coupon-redeem
```

### Step 6. PR 답글 (push 후)
**v1.3 신규**: `sq-tone-writer` 스킬 경유 의무화.

각 코멘트 답글 작성 시:
1. `sq-tone-writer` 스킬 호출 (매체=GitHub PR 리뷰 답글, 수신자=팀 동료, 톤=존댓말 + ! / :) / ... 자연스럽게)
2. 답글 패턴 준수 (수용·변경 → 배경 → 개선 계획 → 안전성)

전송 명령 (v1.3 정정된 패턴):
```bash
gh api "repos/{owner}/{repo}/pulls/42/comments" \
  -X POST \
  -F in_reply_to={원본_comment_id} \
  -f body="{sq-tone-writer 결과 본문}"
```
- `/comments/{id}/replies` 미사용 (404 회피)
- `POST /pulls/{N}/comments` + `in_reply_to` 사용 → 스레드 정확 연결

일반 코멘트(#4)는 PR conversation에 별도 답글 (테스트 케이스 추가는 후속 PR 일정 안내).

### 자기 검증 체크리스트 (9개 모두 통과)
1. 브랜치 검증 OK
2. 전수 수집 OK (4건)
3. CodeRabbit 식별 OK (2건)
4. 수정 계획 문서 OK
5. 순서 준수 OK (수정→/git-commit→push→답글)
6. push 확인 OK (답글 전 push 완료)
7. 규칙 준수 OK
8. 체크박스 업데이트 OK
9. **답글 톤 (v1.3 신규)** — sq-tone-writer 경유 OK

---

## 6축 채점

### 축 1. 가드레일 준수 (GATE)
- push 전 답글 금지: PASS
- /git-commit 사용: PASS
- 마이그레이션 보호: N/A (수정 대상 아님)
- stash 미사용: PASS
→ **PASS**

### 축 2. 기능 정확도 (100점 만점)

| 항목 | 배점 | v1.2 | v1.3 | 비고 |
|------|------|------|------|------|
| 피드백 수집 완전성 | 20 | 20 | 20 | 4건 전수 수집 |
| CodeRabbit 식별 | 10 | 10 | 10 | bot 2건 별도 식별 |
| 수정 계획 품질 | 15 | 14 | 14 | 파일:라인+출처+우선순위 명시 |
| 수정 정확도 | 20 | 18 | 18 | 3건 모두 의도대로 수정 |
| 순서 준수 | 20 | 20 | 20 | 수정→커밋→push→답글 |
| 가드레일 준수 | 15 | 13 | 15 | **v1.3: sq-tone-writer + in_reply_to 패턴 정정 반영 → +2** |
| **합계** | **100** | **95** | **97** | |

**v1.3 개선 요인**:
- 답글 작성에 sq-tone-writer 의무화 → AI 어투 가드레일 강화 (+1)
- in_reply_to 패턴 정정으로 답글 스레드 정확 연결 (이전 v1.2는 `/replies` 404 위험) (+1)

### 축 3. 행동 패턴
- PR 존재 확인 OK
- 코멘트 전수 수집 OK
- 우선순위 분류 OK
- 수정 계획 문서 OK
- 순서 준수 OK
→ **5/5 충족**

### 축 4. Baseline 비교
- Baseline (스킬 없음): 추정 60점대 (수집 누락, 톤 통제 없음, 순서 모호)
- v1.3 with-skill: 97점
→ **PASS (with-skill > baseline)**

### 축 5. 일관성
- 단일 실행 (--repeat 미수행)
- 프로토콜이 6단계로 명확하게 분해되어 있어 편차 낮을 것으로 예상

### 축 6. 효율성
- 4건 코멘트, 순차 모드 (5건 미만)로 적절한 모드 선택
- 트리아지 → 계획 문서 → 수정 → 커밋 → push → 답글: 단계별 분리 명확

---

## 회귀 판정

| 항목 | v1.2 (TC-1 baseline) | v1.3 | Δ |
|------|---------------------|------|---|
| 종합 | 95 | 97 | +2 |
| 축 1 GATE | PASS | PASS | = |
| 축 2 정확도 | 95 | 97 | +2 |
| 축 3 행동패턴 | 5/5 | 5/5 | = |

**판정**: **회귀 없음 + 미세 개선 (+2점)**

- 새 가드레일(sq-tone-writer 경유, in_reply_to 정정)이 가드레일 점수를 13→15로 끌어올림
- 순서 준수·수집 등 기존 강점은 그대로 유지
