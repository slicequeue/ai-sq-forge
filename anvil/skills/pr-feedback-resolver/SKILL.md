---
name: pr-feedback-resolver
description: "PR 리뷰 코멘트(CodeRabbit 포함)를 수집하여 수정 계획을 세우고 코드를 수정하는 스킬. PR 피드백 반영, CodeRabbit 대응, 리뷰 수정, PR 코멘트 처리 요청 시 사용. Use proactively when the user asks to handle PR feedback, CodeRabbit comments, or review modifications."
---

# pr-feedback-resolver — PR 피드백 수정 스킬

---

## Phase 0. 사전 확인

1. **현재 브랜치 확인**: `git branch --show-current`
2. **열린 PR 확인**: `gh pr list --head "$(git branch --show-current)" --state open --json number,title,url`
3. **PR 없으면**: "열린 PR이 없습니다" 안내 후 중단
4. **PR 있으면**: PR 번호·제목 확인 후 진행

---

## 실행 프로토콜

### Step 1. PR 피드백 수집

```bash
# PR 본문·메타
gh pr view --json number,title,body,url

# 이슈 코멘트 (일반 대화)
gh api "repos/{owner}/{repo}/issues/{PR번호}/comments"

# 라인별 리뷰 코멘트
gh api "repos/{owner}/{repo}/pulls/{PR번호}/comments" --paginate
```

`{owner}/{repo}`는 `gh repo view --json owner,name`으로 확인.

### Step 2. 코멘트 분류

| 분류 | 식별 기준 | 우선순위 |
|------|-----------|---------|
| **CodeRabbit** | `user.login`이 `coderabbitai[bot]` | 높음 (우선 반영) |
| **리뷰어 수정 요청** | `state: CHANGES_REQUESTED` 또는 인라인 코멘트 | 높음 |
| **리뷰어 제안** | `state: COMMENTED`, 수정 요청이 아닌 제안 | 중간 |
| **일반 코멘트** | 이슈 코멘트, 질문·논의 | 낮음 |

### Step 3. 수정 계획 문서 작성

`docs/pr-modification-plan-{PR번호}.md` 생성:

```markdown
# PR #{번호} 수정 계획

## PR 정보
- **제목**: {제목}
- **URL**: {URL}
- **작성일**: {날짜}

## 수정 요청 요약
- CodeRabbit 제안: {N}건
- 리뷰어 수정 요청: {N}건
- 리뷰어 제안: {N}건

## 수정 작업 계획 (우선순위)

### 높음
- [ ] {파일}:{라인} — {수정 내용} (CodeRabbit / 리뷰어)
- [ ] ...

### 중간
- [ ] ...

### 낮음
- [ ] ...
```

### Step 4. 수정 실행

우선순위 **높음 → 중간 → 낮음** 순서로:

1. 해당 파일·위치를 열고 요청 내용에 맞게 **코드 수정**
2. `.claude/rules/` 규칙 준수 확인 (수정이 새로운 위반을 만들지 않는지)
3. 수정 계획 문서의 체크박스 업데이트 (`- [x]`)

### Step 5. 커밋 & Push

```
1. 수정 완료 후 /git-commit 스킬로 커밋
2. git push (원격에 코드 반영)
```

### Step 6. PR 답글

push 완료 **후에만** 답글을 작성한다.

```bash
# 리뷰 코멘트에 답글
gh api "repos/{owner}/{repo}/pulls/{PR번호}/comments/{comment_id}/replies" \
  -f body="수정 완료했습니다. {간단 설명}"
```

---

## 가드레일

### 하드 가드레일 (절대 위반 불가)

- **push 전 답글 금지** — 반드시 코드 수정 → 커밋 → push → 답글 순서. push 없이 답글만 달면 CodeRabbit이 변경사항을 확인할 수 없음
- **커밋은 `/git-commit` 스킬 사용 필수** — 임의 형식 `git commit` 금지
- **기존 obesity 마이그레이션 파일 수정/삭제 금지**
- **git stash 금지**

### 소프트 가드레일

- CodeRabbit 제안은 "우선 반영 권장"으로 높음 우선순위에 포함
- 수정이 다른 테스트를 깨뜨리지 않는지 테스트 실행 권장
- 답글은 간결하게 ("수정 완료했습니다" + 핵심 변경 요약)

---

## 자기 검증 체크리스트

작업 완료 후 반드시 확인:

1. [ ] **PR 코멘트 전수 수집**: 이슈 코멘트 + 라인별 리뷰 코멘트 모두 수집했는가?
2. [ ] **CodeRabbit 식별**: CodeRabbit 코멘트를 별도 식별하고 우선 처리했는가?
3. [ ] **수정 계획 문서**: `docs/pr-modification-plan-{PR번호}.md` 생성했는가?
4. [ ] **순서 준수**: 코드 수정 → `/git-commit` → push → 답글 순서를 지켰는가?
5. [ ] **push 확인**: 답글 전에 push가 완료되었는가?
6. [ ] **규칙 준수**: 수정이 `.claude/rules/` 위반을 만들지 않았는가?
7. [ ] **체크박스 업데이트**: 수정 계획 문서의 완료 항목을 체크했는가?

---

## 참조 인덱스

| 파일 | 내용 |
|------|------|
| `references/feedback-collection.md` | PR 피드백 수집 절차 상세 (gh API, CodeRabbit 식별) |
| `references/modification-plan-template.md` | 수정 계획 문서 템플릿 |
| `references/evaluation-rubric.md` | 평가 루브릭 |
