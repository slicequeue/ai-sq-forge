---
description: Uses gh CLI to find the open PR for the current branch, collects code change requests (including CodeRabbit review comments), and produces a modification plan document. Also defines the post-modification workflow (commit, push, reply to each review comment). Use when the user asks to collect PR feedback, address code review comments, create a modification plan from PR, handle CodeRabbit suggestions, or apply code review changes.
---

# PR 피드백 수집 및 수정 계획 문서 작성

현재 브랜치에 열린 PR을 `gh`로 조회하고, 코드 수정 요청(일반 코멘트·리뷰·코드래빗 라인 코멘트)을 수집한 뒤, **수정 계획 문서**를 작성한다.

## Workflow

### 1. 현재 브랜치의 열린 PR 파악

```bash
# 현재 브랜치 확인
git branch --show-current

# 해당 브랜치에 연결된 열린 PR 조회 (repo는 필요 시 -R owner/repo 지정)
gh pr list --head "$(git branch --show-current)" --state open --json number,title,url
```

- 결과가 비어 있으면: "현재 브랜치에 열린 PR이 없습니다"라고 사용자에게 알리고 종료.
- `number`를 얻으면 다음 단계에서 사용.

### 2. PR 본문·일반 코멘트·리뷰 코멘트 수집

**PR 메타 및 본문**

```bash
gh pr view --json number,title,body,url
```

**PR 이슈 코멘트 (본문 아래 일반 댓글)**

```bash
# owner/repo: gh repo view --json nameWithOwner -q .nameWithOwner
gh api "repos/{owner}/{repo}/issues/$(gh pr view --json number -q .number)/comments" --jq '.[] | {author: .user.login, body: .body, created_at: .created_at}'
```

**라인 단위 리뷰 코멘트 (코드 수정 요청이 많이 모여 있는 곳)**

```bash
gh api "repos/{owner}/{repo}/pulls/$(gh pr view --json number -q .number)/comments" --paginate --jq '.[] | {id: .id, path: .path, line: .line, body: .body, user: .user.login, created_at: .created_at}'
```

- `id`, `path`, `line`(또는 `start_line`), `body`, `user`를 수집해 "파일:줄 → 요청" 형태로 정리.
- **id**: 수정 반영 후 해당 코멘트에 답글 작성 시 `comment_id`로 사용.

### 3. 코드래빗(CodeRabbit) 코멘트 강조

- 리뷰 코멘트에서 **작성자**가 `coderabbit` 또는 `CodeRabbit[bot]` 또는 `code-rabbit` 등인 항목을 구분해 표시한다.
- 수정 계획 문서에는 **CodeRabbit 제안**을 한 섹션으로 모아, 파일/라인·원문 요약·제안 내용을 명확히 적는다.
- 본문이나 리뷰 요약에 "CodeRabbit"이 언급된 경우 해당 부분도 수정 계획에 반영한다.

### 4. 수정 계획 문서 작성

수집한 내용을 아래 템플릿에 맞춰 마크다운 문서로 작성한다. 파일은 프로젝트 루트 또는 사용자 지정 경로에 `docs/` 등 적절한 위치에 둔다.

**문서 템플릿**

```markdown
# PR 수정 계획: [PR 제목]

- **PR**: [PR URL]
- **브랜치**: [현재 브랜치명]
- **작성일**: [YYYY-MM-DD]

## 1. 수정 요청 요약

| 구분 | 개수 | 비고 |
|------|------|------|
| PR 본문/리뷰 요약 | N건 | 리뷰어가 본문에 적은 요청 사항 |
| 일반 이슈 코멘트 | N건 | PR 대화 댓글 |
| 라인별 리뷰 코멘트 | N건 | 파일:라인 단위 |
| CodeRabbit 코멘트 | N건 | 위 라인 코멘트 중 CodeRabbit 작성 |

## 2. PR 본문·리뷰에서의 수정 요청

(PR body 또는 리뷰 요약에서 추출한 "반드시 수정", "개선 요청" 등 항목을 번호 목록으로 정리)

## 3. 라인별 수정 요청 목록

| id | 파일 | 라인 | 작성자 | 요청 요약 |
|----|------|------|--------|-----------|
| 12345 | path/to/File.java | 42 | reviewer_id | 요청 내용 한 줄 요약 |

(필요 시 각 행에 대해 상세 설명 또는 원문 일부 인용. **id**는 답글 작성 시 `comment_id`로 사용)

## 4. CodeRabbit 제안 사항 (우선 반영 권장)

| id | 파일 | 라인 | 제안 요약 | 상세 |
|----|------|------|-----------|------|
| 12345 | ... | ... | ... | 원문 또는 요약 |

## 5. 수정 작업 계획 (우선순위)

1. **[높음]** (예: CodeRabbit 필수 제안) – [작업 내용 한 줄]
2. **[중간]** – [작업 내용]
3. **[낮음]** – [작업 내용]

(실제 코드 변경 시 이 순서대로 체크리스트로 사용 가능)
```

- "수정 요청 요약"은 위에서 수집한 데이터를 기반으로 개수와 출처를 채운다.
- CodeRabbit 코멘트는 별도 섹션에 모아 "우선 반영 권장"으로 강조한다.
- 마지막 "수정 작업 계획"은 요청 내용을 **구체적인 작업 단위**로 나누고, 우선순위(높음/중간/낮음)를 붙인다.

## 5. 코드 수정 반영 후 작업 흐름 (수정 실행 시)

코드 리뷰(CodeRabbit 등) 반영 작업을 수행할 때는 **반드시** 아래 순서를 따른다.

### 5.1 작업 순서

1. **코드 수정** – 수정 계획에 따라 실제 코드 변경 적용
2. **커밋** – 한국어 Conventional Commits 형식 (`fix:`, `refac:` 등)
3. **푸시** – `git push`
4. **답글 작성** – 처리한 각 리뷰 코멘트에 작업 완료 답글 작성

### 5.2 커밋 규칙

- `git-commit-workflow` 커맨드 준수
- 타입: `fix:`, `refac:`, `test:` 등
- 대괄호 `[API]` 형식 사용 금지

### 5.3 리뷰 코멘트에 답글 작성

처리한 각 PR 리뷰 코멘트에 반드시 답글을 남긴다.

```bash
# PR 리뷰 코멘트에 답글 작성
# owner/repo, pull_number, comment_id는 실제 값으로 치환
gh api -X POST "repos/{owner}/{repo}/pulls/{pull_number}/comments/{comment_id}/replies" \
  -f body="반영했습니다. [수정 내용 한 줄 요약]"
```

- **comment_id**: `gh api repos/{owner}/{repo}/pulls/{pull_number}/comments` 조회 시 각 항목의 `id` 필드
- **답글 예시**: "반영했습니다. `@NotNull`, `@Min(1)`, `@Max(6)` 추가", "반영했습니다. `parseZoneId()`에서 `DateTimeException` 처리"

### 5.4 요약 체크리스트 (수정 실행 시)

- [ ] 코드 수정 적용
- [ ] `git add` 후 `git commit` (한국어 Conventional Commits)
- [ ] `git push`
- [ ] 처리한 각 리뷰 코멘트에 `gh api .../replies`로 답글 작성

---

## 6. Repo 지정이 필요한 경우

다른 저장소의 PR을 볼 때는 `gh`에 `-R owner/repo`를 붙인다.

```bash
gh pr list -R virtualcare/pasta-japan-server --head "$(git branch --show-current)" --state open --json number,title,url
gh pr view -R virtualcare/pasta-japan-server --json number,title,body,url
```

- API 호출 시에도 `gh api repos/owner/repo/...` 형태로 동일한 owner/repo를 사용한다.

## gh CLI 레퍼런스

| 목적 | 명령어 |
|------|--------|
| 현재 브랜치 | `git branch --show-current` |
| 현재 브랜치 PR 목록 | `gh pr list --head BRANCH --state open --json number,title,url` |
| PR 상세(현재 브랜치) | `gh pr view --json number,title,body,url,reviews` |
| PR 번호만 | `gh pr view --json number -q .number` |
| 다른 repo | 위 명령에 `-R owner/repo` 추가 |

## GitHub API 엔드포인트

- **이슈(PR) 일반 코멘트**: `GET /repos/{owner}/{repo}/issues/{issue_number}/comments`
- **라인별 리뷰 코멘트**: `GET /repos/{owner}/{repo}/pulls/{pull_number}/comments`
  - 응답 필드: `id`, `path`, `line`, `body`, `user.login`, `created_at`, `diff_hunk`.
- **리뷰 목록(요약 본문)**: `GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews`

## CodeRabbit 식별

리뷰 코멘트의 `user.login`이 다음 중 하나이면 CodeRabbit으로 간주:
- `coderabbit`
- `CodeRabbit[bot]`
- `code-rabbit`

## PR 리뷰 코멘트에 답글 작성 API

- **엔드포인트**: `POST /repos/{owner}/{repo}/pulls/{pull_number}/comments/{comment_id}/replies`
- **요청 본문**: `{ "body": "답글 내용" }`
- **gh CLI 예시**:
  ```bash
  gh api -X POST "repos/virtualcare/pasta-japan-server/pulls/375/comments/2843666982/replies" \
    -f body="반영했습니다. parseZoneId()에서 DateTimeException 처리"
  ```
