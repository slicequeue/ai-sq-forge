---
name: git-pr
description: "현재 브랜치의 변경사항을 분석하여 PR을 생성하거나 본문을 업데이트하는 스킬. 'PR 만들어줘', 'PR 생성', 'PR 본문 갱신', 'PR 리프레시', 'pr create', 'pr edit', 'gh pr', 'pull request 작성/수정' 요청 시 사용한다. 사람 친화 표현 + 표 위주 + 100~200줄 이내 표준 양식을 따른다."
version: "0.2"
last-modified: "2026-04-27"
changelog: "v0.2: forge 일반화 — pasta 특정 `--repo` 플래그 제거(gh 자동 감지), pasta-rules/메모리 참조 제거. PR #551 사례를 references/example-pr-551.md로 분리(본문 244→182줄). 자기 검증 체크리스트 12개 추가. 평가 루브릭(100점 + AUTO FAIL 6건) + 하네스 + 테스트 케이스(Happy 2/Edge 1/Negative 1) 동반 작성 — `/eval-harness git-pr` 실행 대기"
---

# git-pr — PR 생성/갱신 스킬

> 트리거: "PR 만들어줘", "PR 본문 갱신", "PR 리프레시", "/git-pr"

원칙: **리뷰어가 1~5분 안에 "뭘 바꿨고 효과가 어땠나" 파악**할 수 있도록 짧고 명료하게.

이 스킬은 다음 순서로 동작한다:
1. 변경사항 분석 → 표준 양식으로 본문 작성
2. 신규 또는 기존 PR 판단
3. 생성/수정 후 URL 출력

---

## Phase 1. 변경사항 분석

```bash
git status
git log <base>..HEAD --oneline
git diff <base>..HEAD --stat
git branch --show-current
gh pr list --head "$(git branch --show-current)" --state open
```

**base 결정**:
- 일반: `dev`
- hotfix / 긴급 prd 적용: `main` (사용자 명시 요청 시)

**원격 push 확인**:
- 원격에 없으면 `git push -u origin HEAD`

---

## Phase 2. PR 본문 작성 (표준 양식)

### 2-1. 분량/구조 원칙

- **100~200줄 이내**, **표 위주**
- 큰 코드 스니펫 / SQL / mermaid 본문 금지 → 작업 문서로 위임
- 영문 jargon 한국어 풀어쓰기

### 2-2. 표준 구성 (있을 때만 섹션 추가)

```markdown
## Why need this PR❓
- 현상 + 원인 1~2문장 (핵심 단어만 굵게)

## Changes ✌️
**파일 N개, +M / -K lines** (영향 범위 한 줄)

| 파일 | 변경 |
|---|---|
| `경로/파일명` | 사람 표현으로 무엇을 바꿨는지 |

## 측정 결과 (운영 효과 측정이 있을 때만)
| 지표 | 변경 전 | 변경 후 | 효과 |
|---|---|---|---|
| ... | ... | ... | ✅ ... |

> ⚠️ 한계/잔존 1줄

## 배포 (Canary / 단계적 배포가 있을 때만)
- 시점 KST: 무엇을 …

## 후속 작업 (별도 PR 항목이 있을 때만)
1. 짧은 항목명 — 1줄 설명

---

📘 **상세 분석/측정 결과/근거 문서는 Notion으로 별도 공유 예정**

## Test list 📝
- [x] 빌드/테스트 통과
- [ ] 후속 검증 (예정)
```

### 2-3. 섹션 추가/생략 판단

| 섹션 | 추가 조건 |
|---|---|
| Why | **항상** |
| Changes | **항상** |
| 측정 결과 | 운영 효과 측정이 있을 때만 |
| 배포 | Canary / 단계적 배포가 있을 때만 |
| 후속 작업 | 별도 PR로 분리할 항목이 있을 때만 |
| Test list | **항상** |

### 2-4. 표현 원칙 (사람 친화)

| ❌ 피할 표현 (jargon) | ✅ 바꿀 표현 (자연어) |
|---|---|
| `NEW 100% 후 ~56h, D+2d` | "4/27 시점, 100% 적용 약 2일 후" |
| `Retries exhausted` (영문 그대로) | "사용자 영향까지 도달한 실패" |
| `pendingAcquireTimeout 등` | "새로운 부작용 (풀 고갈 등)" |
| `maxIdleTime=20s, evictInBackground=60s` | "idle 20초 후 정리, 백그라운드 60초 주기 점검" |
| `burst 패턴` | "1분 burst (한꺼번에 ~10건)" |

규칙:
- **절대 시점 명시 필수** — 상대 표현(`D+2d` 등) 단독 금지. "4/27 (D+2d)" 처럼 절대값 우선
- **영문 기술용어 한국어 풀어쓰기** — 의미 전달 우선
- **수치 단독 노출 지양** — "20초/60초" 같은 의미가 드러나는 단위로

### 2-5. 링크 가드레일 (중요)

- ❌ `docs/...` 상대 링크 사용 금지
  - 본 프로젝트는 `docs/`가 `.git/info/exclude`로 git 추적 제외
  - GitHub PR 페이지에서 클릭해도 404
- ✅ "**상세 분석/측정 결과는 Notion으로 별도 공유 예정**" 한 줄로 안내
- ✅ 외부 공식 문서 링크 (Spring docs, AWS docs, RFC, 외부 API 제공자 공식 문서 등)는 OK

---

## Phase 3. PR 생성/수정

### 신규 생성

```bash
gh pr create \
  --base <dev|main> \
  --head <branch> \
  --title "<커밋 메시지 형식 한국어>" \
  --body "$(cat <<'EOF'
<본문>
EOF
)"
```

### 기존 PR 갱신

```bash
gh pr edit <PR번호> \
  --body "$(cat <<'EOF'
<본문>
EOF
)"
```

### 출력

PR URL 출력. 신규/갱신 여부 한 줄.

---

## 가드레일

- **target branch**: 일반 `dev`, hotfix는 사용자 명시 요청 시 `main`
- **제목/본문 한국어** (영문 commit type prefix는 OK: `fix:`, `feat:`, `refactor:` 등)
- **AI 공동작성자 표기 금지** (Co-authored-by 등)
- **Mermaid 사용 지양** — PR 본문 길어짐. 작업 문서로 위임
- **이미 열린 PR 있으면 신규 생성 금지** → `gh pr edit`으로 갱신

---

## 자기 검증 체크리스트

PR 생성/갱신 직전에 본문이 아래 기준을 모두 만족하는지 확인한다:

1. [ ] **분량**: 본문 100~200줄 이내 (코드 스니펫·SQL·mermaid 없음)
2. [ ] **Why 섹션**: 현상 + 원인 1~2문장. 자세한 분석은 위임
3. [ ] **Changes 섹션**: 파일별 표 (코드 스니펫 없음, 1파일 1줄)
4. [ ] **측정 결과**: 운영 효과 측정이 있을 때만, 표 형태 (baseline/method 등 자세한 건 ⚠️ 한계/잔존 1줄로 위임)
5. [ ] **배포**: Canary/단계적 배포가 있을 때만, 시점(절대 KST) + 무엇만
6. [ ] **후속 작업**: 별도 PR 항목이 있을 때만, 항목명 + 1줄
7. [ ] **Test list**: 항상 포함
8. [ ] **사람 친화 표현**: 영문 jargon 한국어 풀어쓰기, 절대 시점 명시, 수치 단독 노출 지양
9. [ ] **링크 가드레일**: `docs/...` 상대 링크 0개, 외부 공식 문서는 OK
10. [ ] **target branch**: 일반 `dev`, hotfix는 사용자 명시 시 `main`
11. [ ] **AI 공동작성자 표기 없음** (Co-authored-by 등)
12. [ ] **기존 PR 있으면**: 신규 생성 금지, `gh pr edit`으로 갱신

---

## 참고 사례

- [`references/example-pr-551.md`](references/example-pr-551.md) — pasta-japan-server PR #551 (Dexcom WebClient 연결 풀 안정화) 실전 사례. 양식 표준의 출처, 분량·표현·구조 감각용. 새 PR 작성 전 1회 읽기 권장.
