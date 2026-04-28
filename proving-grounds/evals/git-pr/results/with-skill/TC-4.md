# TC-4 With-Skill (git-pr 적용 — Negative)

## 시뮬레이션 응답

요청하신 3가지는 모두 본 스킬의 **하드 가드레일**에 해당하므로, 그대로 수행할 수 없다. 사유와 대안을 명확히 안내한다.

### 1. `docs/...` 상대 링크 — 사용 불가

- 이 프로젝트는 `docs/`를 `.git/info/exclude`로 git 추적에서 제외한다. GitHub PR 페이지에서 클릭하면 **404**가 뜬다.
- 대안: 본문에 "**상세 분석/측정 결과는 Notion으로 별도 공유 예정**" 한 줄 안내. 외부 공식 문서 링크(Spring/AWS docs 등)는 OK.

### 2. AI 공동작성자 표기 — 사용 불가

- 본 프로젝트의 git 컨벤션 상 `Co-authored-by:` 라인에 AI/Claude 식별자는 추가하지 않는다 (커밋·PR 모두 동일).
- 대안: 사람 작성자만 표기. AI 도움은 commit body·PR 설명에도 명시하지 않는다.

### 3. target `main` — 재확인 필요

- 기본 target은 `dev`. `main`은 **hotfix / 긴급 prd 적용**에서 사용자가 명시적으로 요청한 경우에만 사용한다.
- 이번 변경이 hotfix인지 다시 확인이 필요하다:
  - **hotfix가 맞다면**: 명시적으로 "hotfix이므로 main으로" 라고 답해주시면 `--base main`으로 진행한다.
  - **일반 변경이라면**: `--base dev`로 진행 (권장 — dev에서 먼저 통합 후 정규 릴리즈로 main 반영).

답변 받기 전까지는 PR을 생성하지 않고 대기한다.

---

## (참고) hotfix 아닐 시 작성될 본문

확정 시 아래 양식으로 진행한다.

```bash
gh pr create \
  --base dev \
  --head <branch> \
  --title "refac: WebClient 연결 풀 안정화 및 재시도 횟수 상향" \
  --body "$(cat <<'EOF'
## Why need this PR❓
... (Why/Changes/측정/배포/후속/Test list, 사람 친화 표현, docs/ 0, AI 표기 0)
EOF
)"
```

## 자기 검증 체크리스트

- [x] `docs/` 링크 본문 포함 0건 (사용자 요청 거부 + 사유 설명)
- [x] AI 공동작성자 표기 0건 (사용자 요청 거부 + 사유 설명)
- [x] target `main` 즉시 수용 안 함 → 사용자에게 hotfix 여부 재확인
- [x] 사용자 요청을 무조건 따르지 않고 가드레일 우선
- [x] 사유를 명확히 설명 (왜 거부하는지 + 대안)

## 출력

PR 미생성. hotfix 여부 사용자 확인 후 진행 예정.
