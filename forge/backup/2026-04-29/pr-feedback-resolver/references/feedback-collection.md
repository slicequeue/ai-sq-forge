# PR 피드백 수집 절차 상세

---

## gh API 명령어

### PR 본문·메타

```bash
gh pr view --json number,title,body,url
```

### 이슈 코멘트 (일반 대화)

```bash
# owner/repo 확인
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
PR_NUM=$(gh pr view --json number -q .number)

# 이슈 코멘트 수집
gh api "repos/${REPO}/issues/${PR_NUM}/comments"
```

### 라인별 리뷰 코멘트

```bash
gh api "repos/${REPO}/pulls/${PR_NUM}/comments" --paginate
```

### 리뷰 상태 확인

```bash
gh api "repos/${REPO}/pulls/${PR_NUM}/reviews"
```

---

## CodeRabbit 코멘트 식별

### 식별 기준

`user.login` 필드가 아래 중 하나:
- `coderabbitai[bot]`
- `coderabbit`
- `CodeRabbit[bot]`

### 처리 원칙

- CodeRabbit 코멘트는 **우선 반영 권장** → 높음 우선순위
- CodeRabbit이 제안한 코드 변경은 대부분 자동 수정 가능
- CodeRabbit의 "Actionable" 제안과 "Informational" 코멘트를 구분

---

## 코멘트 분류 기준

| 분류 | 식별 | 우선순위 | 대응 |
|------|------|---------|------|
| CodeRabbit 제안 | `user.login` = `coderabbitai[bot]` | **높음** | 즉시 수정 |
| 리뷰어 수정 요청 | `CHANGES_REQUESTED` 또는 인라인 수정 요청 | **높음** | 즉시 수정 |
| 리뷰어 제안 | `COMMENTED`, 개선 제안 | **중간** | 가능하면 반영 |
| 질문/논의 | 이슈 코멘트, 질문 | **낮음** | 답변만 (코드 변경 불필요) |

---

## 답글 작성

### 필수 순서

```
1. 코드 수정
2. /git-commit 스킬로 커밋
3. git push (원격 반영)
4. 답글 작성
```

**push 전 답글 금지** — CodeRabbit이 변경사항을 확인해야 resolved 처리 가능.

### 답글 API

```bash
# 리뷰 코멘트에 답글
gh api "repos/${REPO}/pulls/${PR_NUM}/comments/{comment_id}/replies" \
  -f body="수정 완료했습니다. {간단 설명}"

# 이슈 코멘트에 답글
gh api "repos/${REPO}/issues/${PR_NUM}/comments" \
  -f body="{답변 내용}"
```

### 답글 형식

```
수정 완료했습니다.
- {변경 요약 1}
- {변경 요약 2}
```

간결하게. 변경 내용을 1~3줄로 요약.
