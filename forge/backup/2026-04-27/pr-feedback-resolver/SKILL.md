---
name: pr-feedback-resolver
description: "PR 리뷰 코멘트(CodeRabbit 포함)를 수집하여 수정 계획을 세우고 코드를 수정하는 스킬. PR 피드백 반영, CodeRabbit 대응, 리뷰 수정, PR 코멘트 처리 요청 시 사용. Use proactively when the user asks to handle PR feedback, CodeRabbit comments, or review modifications."
version: "1.2"
last-modified: "2026-04-20"
changelog: "Insights 피드백 반영: 병렬 에이전트 트리아지 모드 추가, 브랜치 안전 검증 강화"
---

# pr-feedback-resolver — PR 피드백 수정 스킬

---

## Phase 0. 사전 확인

1. **현재 브랜치 확인**: `git branch --show-current`
   - **보호 브랜치 검사**: `dev`, `stg`, `main`이면 **즉시 중단** — "보호 브랜치에서는 피드백 수정이 불가합니다. 작업 브랜치로 전환하세요." 안내
   - **PR head 브랜치 일치 검증**: 현재 브랜치가 PR의 head 브랜치와 동일한지 확인
2. **워킹 트리 상태 확인**: `git status` — uncommitted 변경이 있으면 사용자에게 알리고 처리 방법 확인
3. **열린 PR 확인**: `gh pr list --head "$(git branch --show-current)" --state open --json number,title,url`
4. **PR 없으면**: "열린 PR이 없습니다" 안내 후 중단
5. **PR 머지 여부 확인**: 이미 머지된 PR이면 중단 안내
6. **PR 있으면**: PR 번호·제목 확인 후 진행

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

### Step 2. 코멘트 분류 (순차 모드 / 병렬 트리아지 모드)

모든 코멘트를 **반영 / 미반영 / 이미해결** 3분류로 전수 분류한 후, 반영 대상만 우선순위별로 처리한다.

#### 병렬 트리아지 모드 (코멘트 5건 이상 시 권장)

코멘트가 5건 이상이면 Agent 도구로 **병렬 트리아지**를 사용할 수 있다:

```
1. 독립적인 코멘트 스레드를 식별 (같은 파일/같은 논점은 하나로 묶음)
2. 스레드별로 Agent 서브에이전트를 병렬 생성:
   - 각 에이전트: 코멘트 원문 + 해당 코드 Read → 반영/미반영/이미해결 분류 + 수정 방향 제안
3. 모든 에이전트 결과를 수집하여 트리아지 테이블로 통합
4. 사용자에게 통합 트리아지 결과를 제시하고 승인 요청
5. 승인 후 순차적으로 수정 실행 (수정은 병렬 금지 — 충돌 방지)
```

병렬 트리아지의 이점:
- 10건+ 코멘트를 순차 분류하면 5~10분 → 병렬 분류로 1~2분
- 각 에이전트가 독립적으로 코드를 읽고 분류하므로 정확도 유지

**주의**: 수정 실행(Step 4)은 반드시 **순차 처리** — 동일 파일을 여러 에이전트가 동시 수정하면 충돌 발생.

| 판정 | 기준 | 처리 |
|------|------|------|
| **반영** | 코드 품질 향상에 실질적으로 기여하는 지적 | 우선순위별 수정 |
| **미반영** | 프로젝트 규칙과 충돌하거나 현재 맥락에 맞지 않는 지적 | 사유를 수정 계획 문서에 기록 |
| **이미해결** | 이미 수정되었거나 다른 커밋에서 처리된 항목 | 해결 근거를 기록 |

반영 대상의 우선순위:

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
3. **admin 모듈 예외**: admin 모듈 피드백 중 pasta-api 4-Tier 규칙을 적용한 지적(DTO→JPA 의존 제거, record 전환 등)은 admin이 레이어 혼합형(규칙 13)이므로 **"미반영 + 사유 설명"** 으로 처리한다. 수정 계획 문서에 미반영 사유를 명시하고, PR 답글에서도 근거를 설명한다.
4. 수정 계획 문서의 체크박스 업데이트 (`- [x]`)

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

1. [ ] **브랜치 검증**: 보호 브랜치가 아닌 작업 브랜치에서 작업 중인가? PR head 브랜치와 일치하는가?
2. [ ] **PR 코멘트 전수 수집**: 이슈 코멘트 + 라인별 리뷰 코멘트 모두 수집했는가?
3. [ ] **CodeRabbit 식별**: CodeRabbit 코멘트를 별도 식별하고 우선 처리했는가?
4. [ ] **수정 계획 문서**: `docs/pr-modification-plan-{PR번호}.md` 생성했는가?
5. [ ] **순서 준수**: 코드 수정 → `/git-commit` → push → 답글 순서를 지켰는가?
6. [ ] **push 확인**: 답글 전에 push가 완료되었는가?
7. [ ] **규칙 준수**: 수정이 `.claude/rules/` 위반을 만들지 않았는가?
8. [ ] **체크박스 업데이트**: 수정 계획 문서의 완료 항목을 체크했는가?

---

## 참조 인덱스

| 파일 | 내용 |
|------|------|
| `references/feedback-collection.md` | PR 피드백 수집 절차 상세 (gh API, CodeRabbit 식별) |
| `references/modification-plan-template.md` | 수정 계획 문서 템플릿 |
| `references/evaluation-rubric.md` | 평가 루브릭 |
