# TC-5 With-Skill 응답 (시뮬레이션, v1.9)

> 평가용 시뮬레이션이다. 실제 git/gh 명령과 코드 쓰기는 하지 않았다. 아래의 명령 출력·파일 내용·commit hash·comment id 는 **전부 가정값**이며 "(가정)"으로 표시한다. 가정과 확인된 사실은 맨 아래 "확인된 것 vs 가정한 것"에서 다시 분리한다.

## 0. 접근 요약

- 코멘트는 2건(사람 시니어 1, CodeRabbit 1)이라 병렬 트리아지 없이 순차 모드로 처리한다.
- 두 건 모두 "반영"으로 분류한다. 단 사람 리뷰어의 이름 규칙 지적은 지적 위치 1곳만 고치지 않고 **같은 PR 의 같은 규칙 전체**를 스윕한다 (v1.7·v1.9).
- 스윕 범위는 "지적된 이름(`doses`)"이 아니라 "지적된 규칙(NAMING 군)"이다. 같은 NAMING 군의 `Instant` 변수 `At` 접미사 누락도 lint 출력으로 확인한다.
- 사용자는 범위를 좁히지 않았으므로 스윕 결과를 함께 수정한다. 단 DTO 의 JSON 필드명이 걸리면 API 계약 변경이므로 임의로 바꾸지 않고 사용자에게 묻는다.
- 순서는 코드 수정 → `/git-commit` → 최신 dev 병합 컴파일 → push → `sq-tone-writer` 로 답글 작성 → 답글 전송이다.

---

## 1. Phase 0. 사전 확인

```bash
git branch --show-current
# 기대: api/feat/glp1-dose-history   -> dev/stg/main 아님. 보호 브랜치 검사 통과

git status --short
# 기대(가정): 변경 없음. uncommitted 가 있으면 여기서 멈추고 처리 방법을 사용자에게 묻는다

gh pr list --head "$(git branch --show-current)" --state open --json number,title,url,headRefName,state
# 기대(가정): [{"number":812,"title":"GLP-1 투약 이력 조회 API", "headRefName":"api/feat/glp1-dose-history", ...}]
```

- 검증 항목: PR #812 의 head 브랜치가 현재 브랜치와 일치하는지, 머지/클로즈 상태가 아닌지 확인한다. 사용자가 말한 #812 와 `gh pr list` 결과의 번호가 같다.
- 보호 브랜치가 아니고 PR 이 열려 있으므로 진행한다.

### Phase 0.5. PR 컨텍스트 현황 파악 (읽기 전용)

```bash
gh pr view 812 --json number,title,body,url,baseRefName,mergeable,reviewDecision,statusCheckRollup
gh pr checks 812
gh pr diff 812 --name-only
ls .github/PULL_REQUEST_TEMPLATE.md   # 이번에는 PR 본문을 고치지 않으므로 확인만. 본문 수정이 필요해지면 템플릿 섹션명을 문자 그대로 사용
```

- 머지 정책: dev 머지(사용자 제공). `baseRefName == dev` 인지 확인한다.
- CI 상태: 가정(미확인)으로 "통과 또는 진행 중". 실패 상태이면 이번 수정과 무관한 실패인지 구분해 보고한다.
- 변경 파일 6개가 사용자가 준 목록과 일치하는지 대조한다.
- 같은 파일을 고치는 다른 열린 PR 이 있는지(`gh pr list --state open --json number,files`) 확인한다. 있으면 머지 순서와 dev 병합 규칙(v1.8)을 종료 보고에 적는다. 이번 시뮬레이션에서는 없다고 가정한다.

---

## 2. Step 1. 피드백 수집 (전수)

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
PR_NUM=812

gh pr view 812 --json number,title,body,url
gh api "repos/${REPO}/issues/${PR_NUM}/comments"                 # 이슈 코멘트(일반 대화)
gh api "repos/${REPO}/pulls/${PR_NUM}/comments" --paginate       # 라인별 리뷰 코멘트
gh api "repos/${REPO}/pulls/${PR_NUM}/reviews"                   # 리뷰 상태(CHANGES_REQUESTED 등)
```

수집 결과(사용자 설명 기반, comment id 는 가정):

| id (가정) | 작성자 | 위치 | 원문 요약 |
|-----------|--------|------|-----------|
| 1001 | 시니어 리뷰어 (사람) | `DoseHistoryService.java:42` | 컬렉션 변수명에 `List` 접미사 없음. `doses` → `doseList` (규칙 05 네이밍) |
| 1002 | `coderabbitai[bot]` | `DoseHistoryController.java:30` | `@Operation` summary 가 비어 있음 |

- 이슈 코멘트(일반 대화)는 0건이라고 가정한다. 실제로 CodeRabbit 의 walkthrough 요약 이슈 코멘트가 있을 수 있으므로 반드시 조회해 "Actionable/Informational" 을 구분한다.
- 사람 코멘트의 `user.login` 이 `coderabbitai[bot]` 이 아님을 확인한다. 1002 는 `coderabbitai[bot]` 로 식별한다.

---

## 3. Step 2. 분류

| id | 판정 | 우선순위 | 근거 |
|----|------|----------|------|
| 1001 | 반영 | 높음 (리뷰어 인라인 수정 요청) | 규칙 05 위반 지적. 프로젝트 규칙과 충돌하지 않음. 해당 줄을 열어 `doses` 가 실제 컬렉션인지 확인한 뒤 확정 |
| 1002 | 반영 | 높음 (CodeRabbit 우선) | 빈 `summary` 는 Swagger 문서 품질 문제. 규칙과 충돌 없음 |

- 이미해결 후보 점검: 두 줄이 이미 다른 커밋에서 수정되었는지 `git log -p -S'doses' -- ...` 와 현재 파일 내용으로 확인한다. 가정: 둘 다 아직 미해결.
- admin 모듈 예외(규칙 13)는 해당 없음. 대상 파일은 admin 이 아닌 일반 4-Tier 구조라고 가정한다.
- 우선순위가 같은 "높음"이므로 사람 리뷰어(시니어) 지적을 먼저, CodeRabbit 을 다음에 처리한다.

---

## 4. Step 3. 수정 계획 문서 (`docs/pr-modification-plan-812.md`)

작성 내용(시뮬레이션이므로 파일은 쓰지 않는다. 내용만 제시한다):

```markdown
# PR #812 수정 계획

## PR 정보

| 항목 | 값 |
|------|-----|
| PR 번호 | #812 |
| 제목 | GLP-1 투약 이력 조회 API |
| URL | {gh pr view 로 확인한 URL} |
| 브랜치 | api/feat/glp1-dose-history |
| 작성일 | 2026-11-13 |

## 수정 요청 요약

| 출처 | 건수 | 우선순위 |
|------|------|---------|
| CodeRabbit | 1건 | 높음 |
| 리뷰어 수정 요청 | 1건 | 높음 |
| 리뷰어 제안 | 0건 | 중간 |
| 질문/논의 | 0건 | 낮음 (답변만) |

## 수정 작업 계획 (우선순위)

### 높음 (즉시 수정)

- [ ] **DoseHistoryService.java:42** — `doses` → `doseList` + 같은 PR 의 같은 규칙(NAMING) 스윕
  - 출처: 시니어 리뷰어 (사람)
  - 원문: "컬렉션 변수명에 List 접미사가 없습니다. doses → doseList (규칙 05 네이밍)"
  - 답글 파라미터: 사람 리뷰어 / A-1 담백 보고형 (단순 "이렇게 해라" 지적)
  - 스윕 대상: (4절 Step 4 의 스윕 결과표 참조)

- [ ] **DoseHistoryController.java:30** — `@Operation(summary = ...)` 채움 + 같은 컨트롤러의 다른 `@Operation` 확인
  - 출처: CodeRabbit
  - 원문: "@Operation summary 가 비어 있습니다."
  - 답글 파라미터: CodeRabbit 봇 / 평어 단정형 (반영분 보고)

### 중간 / 낮음
- 해당 없음

## 미반영 / 이미해결
- 없음

## 수정 완료 후 체크리스트

- [ ] 모든 높음 항목 수정 완료
- [ ] review-lint 실행 결과 확인 (건수는 실행 출력 기준)
- [ ] 최신 dev 병합 후 compileTestJava 통과
- [ ] /git-commit 스킬로 커밋
- [ ] git push 완료
- [ ] PR 코멘트에 답글 완료 (1001: 사람 A-1, 1002: 봇)
- [ ] 수정이 기존 테스트를 깨뜨리지 않는지 확인
```

- 문서에 "각 답글에 어느 호출 파라미터를 적용했는지"를 기록해 자기 검증 12번을 충족한다.
- 이 문서는 PR 변경 파일이 아니라 작업 메모다. 이 저장소가 `docs/` 를 커밋 대상으로 허용하는지 모르면 커밋에 포함하기 전에 사용자에게 확인한다(가정: 허용).

---

## 5. Step 4. 수정 실행

### 5-1. 항목 1001 — `doses` → `doseList` + 같은 규칙 스윕

**a) 지적 위치 확인**

```bash
sed -n '30,60p' src/main/java/.../DoseHistoryService.java    # 42행 주변을 읽고 doses 가 컬렉션 선언/반환임을 확인
```

가정한 42행: `List<DoseHistory> doses = doseHistoryQueryAdapter.findByUserId(userId);`

**b) 같은 유형 전수 스윕 (v1.7)** — 변경 파일 6개 전체를 대상으로 한다. 지적 범위는 "이름 하나"가 아니라 "컬렉션 변수 접미사 규칙"이다.

```bash
FILES=$(gh pr diff 812 --name-only)
# 컬렉션 타입 선언 중 접미사 없는 변수 후보
grep -nE '\b(List|Set|Collection|Map)<[^>]+>\s+[a-z][A-Za-z0-9]*\s*(=|;|,|\))' $FILES | grep -vE '(List|Set|Map|Collection)\s*(=|;|,|\))'
# 같은 이름 추적
grep -n '\bdoses\b' $FILES
```

**c) 규칙 단위 스윕 (v1.9)** — grep 에 더해 lint 출력에서 NAMING 코드를 전부 수집한다.

```bash
python3 forge/common/review-lint.py          # merge-base(origin/dev) ~ 작업 트리, 즉 PR 전체 diff 를 본다
```

NAMING 항목 중 같은 군인 `Instant` 변수의 `At` 접미사 누락도 목록에 넣는다.

**스윕 결과표 (가정 — 실제 실행 출력으로 대체되어야 함)**

| 위치 (가정) | 내용 | 조치 |
|-------------|------|------|
| `DoseHistoryService.java:42` | `List<DoseHistory> doses` (지적 위치) | `doseList` 로 변경 |
| `DoseHistoryService.java:47,51` | 같은 변수의 사용부 | 함께 변경 |
| `DoseHistoryAssembler.java` | 파라미터 `List<DoseHistory> doses` | `doseList` 로 변경 |
| `DoseHistoryServiceTest.java` | 테스트 지역 변수 `doses` | `doseList` 로 변경 |
| `DoseHistoryServiceTest.java` | `Instant administered` (NAMING, `At` 누락) | `administeredAt` 로 변경 |
| `DoseHistoryResponse.java` | record 컴포넌트 `List<DoseItem> doses` | **임의 변경 금지, 아래 판단 참조** |
| `DoseHistoryQueryAdapter.java` | 해당 없음 | - |

**DTO 필드 처리 판단 (범위 규율)**: `DoseHistoryResponse` 의 `doses` 가 응답 JSON 필드명이면, 이름을 바꾸는 순간 `{"doses": [...]}` 가 `{"doseList": [...]}` 로 바뀌어 **API 계약 변경**이 된다. 같은 규칙 05 의 대상이어도 사용자·프론트와 합의 없이 바꾸지 않는다. 처리 방식은 다음과 같다.

- 이 PR 이 신규 API(아직 클라이언트가 소비하지 않음)이면 사용자에게 "응답 필드명도 `doseList` 로 바꿀까요?"를 묻고 답을 받은 뒤 수정한다.
- 사용자 답이 오기 전에는 이 항목만 보류하고, 나머지(내부 변수명)는 진행한다.
- lint 가 이 항목을 [위반] 으로 잡으면(NAMING 은 가드 문서상 "확인" 등급이라 위반은 아닐 것으로 가정) push 전에 반드시 사용자 선택을 받는다. "확인" 등급이면 답글·PR 에 "응답 필드는 API 계약이라 유지, 변경 여부 논의 필요" 사유를 남긴다.

사용자에게 보내는 질문(수정 전, 한 번에):

> 1001 지적(`doses` → `doseList`) 스윕 결과 같은 패턴이 Service 3곳, Assembler 1곳, Test 1곳(+ `Instant administered` At 누락 1곳)입니다. 모두 함께 수정하겠습니다. 다만 `DoseHistoryResponse.doses` 는 JSON 응답 필드명이라 바꾸면 API 계약이 변경됩니다. (a) 응답 필드도 `doseList` 로 변경 (b) 응답 필드는 유지하고 답글에 사유 명시 중 어느 쪽인가요?

(기본값은 (b) 로 진행하되 사용자 답을 우선한다. 질문 때문에 나머지 작업을 멈추지 않는다.)

**d) 수정**: 변수 선언·사용부를 `Edit` 로 줄 단위 치환한다. 파일을 통째로 덮어쓰지 않는다(파괴적 쓰기 가드 DW-3). 수정 전 `git status` 로 대상 파일에 미커밋 변경이 없음을 확인했다(DW-1).

**e) 규칙 재확인**: 변경한 이름이 다른 규칙(`.claude/rules/`)을 새로 위반하지 않는지 확인한다(예: 같은 스코프에 이미 `doseList` 가 있어 섀도잉되지 않는지).

### 5-2. 항목 1002 — `@Operation` summary

**a) 지적 위치 확인**

```bash
sed -n '20,50p' src/main/java/.../DoseHistoryController.java
```

가정한 30행: `@Operation(summary = "")`

**b) 수정**

```java
@Operation(summary = "GLP-1 투약 이력 조회")
```

- 인접 엔드포인트·같은 패키지 컨트롤러의 `summary` 어휘(예: "~ 조회", "~ 등록")를 먼저 읽고 문체를 맞춘다. 같은 응답 객체 안 Swagger 용어 일관성도 확인한다(RR-6).
- 스윕: 같은 컨트롤러·같은 PR 의 다른 `@Operation`/`@Schema(description = "")` 가 비어 있는지 grep 한다.

```bash
grep -nE '@Operation\(|summary\s*=\s*""|description\s*=\s*""' $FILES
```

가정: 같은 컨트롤러에 다른 비어 있는 summary 는 없음. 있으면 함께 채운다.

### 5-3. 검증

```bash
python3 forge/common/review-lint.py
```

- **건수는 실제 출력으로만 보고한다.** 시뮬레이션에서는 실행하지 않았으므로 "0건"이라고 단정하지 않는다. 실행 결과가 아래 중 어느 쪽인지로 다음 단계가 갈린다.
  - [위반] 0건 + 확인 항목에 NAMING 잔여 없음: 다음 단계로 진행
  - NAMING 확인 항목이 남음(예: DTO 필드 `doses`): 사용자 답에 따라 수정하거나 사유를 답글에 기록
  - [위반] 1건 이상: 고친 뒤 재실행. 위반이 남은 채 push 하지 않는다(RR-F15)
- v1.9 규칙: lint 는 PR 전체 diff 를 보므로 지적 위치만 고쳐도 다른 파일에 [위반] 이 남아 있으면 push 불가다. 이번에는 사용자가 범위를 좁히지 않았으므로 전부 같이 고친다.

### 5-4. 최신 dev 병합 컴파일 (v1.8)

```bash
git fetch origin dev
git merge origin/dev            # force push 금지. rebase 대신 merge
./gradlew compileTestJava
./gradlew test --tests '*DoseHistory*'
```

- 이번 수정은 이름 변경과 어노테이션 값 변경이라 인터페이스·생성자 시그니처는 바뀌지 않는다. 그래도 `DoseHistoryAssembler` 의 파라미터명만 바뀌었는지, 메서드 시그니처가 바뀌었다면 dev 쪽 구현체·테스트 Fake 를 grep 해야 하는지 확인한다.
- 컴파일 실패 시 원인이 dev 와의 충돌이면 그 부분을 고친다.

### 5-5. 계획 문서 체크박스 갱신, 재발 방지 등록 판단

- 문서의 두 항목을 `- [x]` 로 갱신한다.
- 재발 방지 판단은 종료 보고에 적는다(8절).

---

## 6. Step 5. 커밋 & Push

`/git-commit` 스킬로 커밋한다. 임의 `git commit` 금지. 답글마다 commit hash 를 달기 위해 지적 단위로 두 커밋으로 나눈다.

```
커밋 1 (가정 hash: a1b2c3d)
refac: 투약 이력 컬렉션·Instant 변수명 접미사 규칙 적용

- doses -> doseList (Service, Assembler, Test)
- Instant administered -> administeredAt (Test)

커밋 2 (가정 hash: e4f5a6b)
fix: 투약 이력 조회 @Operation summary 보완
```

- `refac:` 사용(저장소 컨벤션), 대괄호 금지, Co-authored-by 에 AI 정보 금지, 한국어.
- 사용자가 답한 DTO 필드 변경 여부에 따라 커밋 1 에 `DoseHistoryResponse` 를 포함하거나 제외한다.

```bash
git push
git log origin/api/feat/glp1-dose-history -2 --oneline    # push 반영과 hash 확인
gh pr checks 812                                           # CI 재실행 상태 확인
```

- push 완료를 확인한 뒤에만 답글을 보낸다. 가정한 hash `a1b2c3d`, `e4f5a6b` 는 실제 `git log` 출력의 hash 로 대체한다.

---

## 7. Step 6. PR 답글 (push 완료 후)

모든 본문은 `sq-tone-writer` 를 경유한다. 수신자를 구분한다.

### 7-1. 1001 — 사람 리뷰어 (시니어)

`sq-tone-writer` 호출 파라미터:

- 매체: `GitHub PR 리뷰 답글 (사람 리뷰어)`
- 수신자: `팀 동료` (시니어)
- 패턴: **A-1 담백 보고형** (시니어가 "이렇게 해라" 형태로 단순 지적)
- 금지: `~것 같습니다`, `감사드립니다`, 과장 표현, 저자세 마무리, 멘션·`!`·`:)`·`...`

답글 본문(A-1 형식: 수용 한 줄 → 변경 1문장 → 근거/추가 변경 1문장 → commit hash):

```
지적 그대로입니다. `DoseHistoryService` 의 `doses` 를 `doseList` 로 바꿨고, 같은 패턴 5곳(Assembler 파라미터·테스트 변수 `doses`, 테스트 `Instant administered` → `administeredAt` 포함)도 함께 수정했습니다. (a1b2c3d)
```

- "같은 패턴 N곳 함께 수정"을 포함해 자기 검증 13번을 충족한다. N 은 실제 스윕·lint 결과로 확정한다(가정 5곳).
- `DoseHistoryResponse.doses` 를 유지하기로 했다면 답글에 이어서 한 문장을 추가한다(A-2 성격의 최소 기술 판단).

  ```
  응답 DTO 의 `doses` 필드는 JSON 계약이라 이번에는 유지했습니다. `doseList` 로 맞출지 알려 주세요.
  ```

  이는 리뷰어 의도를 추정하는 부분이므로 "다르면 알려주세요" 형태로 검증을 요청한다(자기 검증 10번). 변경했다면 이 문장은 "응답 필드명도 `doseList` 로 변경했습니다. 클라이언트 영향은 PR 본문에 적었습니다." 로 대체한다.

전송:

```bash
gh api "repos/${REPO}/pulls/812/comments" \
  -X POST \
  -F in_reply_to=1001 \
  -f body="지적 그대로입니다. \`DoseHistoryService\` 의 \`doses\` 를 \`doseList\` 로 바꿨고, 같은 패턴 5곳(Assembler 파라미터·테스트 변수 \`doses\`, 테스트 \`Instant administered\` → \`administeredAt\` 포함)도 함께 수정했습니다. (a1b2c3d)"
```

### 7-2. 1002 — CodeRabbit 봇

`sq-tone-writer` 호출 파라미터:

- 매체: `GitHub PR 리뷰 답글 (CodeRabbit 봇)`
- 수신자: `봇` (시니어도 함께 보는 점 고려)
- 톤: 평어 단정형(`~다`, `~함`, `~된다`), 2~4문장
- 금지: 멘션(`@coderabbitai`), 존댓말, 완화어, `!`/`:)`/`...`, 감사, 향후 검토 약속

답글 본문(부분 반영/반영 보고형: 반영분 + commit → 스윕 근거):

```
`@Operation` summary 를 "GLP-1 투약 이력 조회" 로 채움 (e4f5a6b). 같은 컨트롤러의 다른 `@Operation` 은 모두 summary 가 채워져 있어 추가 변경 없음.
```

전송:

```bash
gh api "repos/${REPO}/pulls/812/comments" \
  -X POST \
  -F in_reply_to=1002 \
  -f body="\`@Operation\` summary 를 \"GLP-1 투약 이력 조회\" 로 채움 (e4f5a6b). 같은 컨트롤러의 다른 \`@Operation\` 은 모두 summary 가 채워져 있어 추가 변경 없음."
```

- `/comments/{id}/replies` 엔드포인트는 404 이므로 사용하지 않는다. 반드시 `POST /pulls/812/comments` + `in_reply_to` 로 스레드를 연결한다.
- 두 답글은 서로 톤이 다르다(사람: 존댓말 담백 단문, 봇: 평어 단정형). 사람 톤을 봇에 쓰지 않는다.

---

## 8. 종료 보고 (사용자에게 전달할 내용)

**처리 결과**

- 1001 (시니어, 규칙 05): 반영. `doses` → `doseList` 를 Service 3곳으로 끝내지 않고 PR 전체 스윕으로 Assembler·Test 와 `Instant administered` → `administeredAt`(같은 NAMING 군)까지 수정. 커밋 a1b2c3d (가정).
- 1002 (CodeRabbit): 반영. `@Operation(summary = "GLP-1 투약 이력 조회")`. 커밋 e4f5a6b (가정).
- 답글 2건: 1001 사람 A-1, 1002 봇 평어 단정형.

**사용자 확인이 필요한 사항**

- `DoseHistoryResponse.doses` 는 JSON 응답 필드명이라 변경 시 API 계약이 바뀐다. 변경 여부를 알려 주면 반영한다. 답이 없으면 유지한 채 답글에 사유를 남겼다.

**review-lint 결과**: 실제 실행 출력의 건수를 그대로 적는다. (시뮬레이션에서는 실행하지 않았으므로 건수를 단정하지 않는다. 실제 실행 시 [위반] 건수와 NAMING "확인" 잔여 건수를 분리해 적는다.)

**재발 방지 등록 판단 (v1.7)**

- 이번 지적(컬렉션 변수 `List` 접미사)은 `forge/common/review-recurrence-guard.md` RR-L 의 NAMING 검사에 **이미 있는 유형**이다(#789·#791·#792 이름 규칙).
- 따라서 "가드 추가 후보" 가 아니라 **"규칙은 있으나 미적용"** 으로 표시한다. 작성 시점에 `review-lint.py` 를 돌리지 않았거나 "확인" 등급 결과를 무시한 실행 경로 문제이므로, 규칙 추가가 아니라 게이트 강화(커밋 전 lint 실행, "확인" 등급 항목의 사유 기록)가 필요하다.
- `@Operation summary` 빈 값은 가드 문서에 없는 유형이다. 문자열로 잡히므로(`summary = ""`) `review-lint.py` 검사 후보로 표시한다: "가드 추가 후보: 빈 `@Operation` summary — #812".

**머지 정책**: dev 머지. CI 가 이번 push 커밋으로 완료된 뒤 머지한다. 같은 파일을 고치는 다른 PR 이 있으면 먼저 머지된 쪽 이후 dev 를 merge 하고(force push 금지) CI 완료를 기다린다(v1.8).

---

## 9. 확인된 것 vs 가정한 것

| 구분 | 내용 |
|------|------|
| 확인된 것 (사용자 제공) | 브랜치 `api/feat/glp1-dose-history`, PR #812, dev 머지 정책, Spring/Java, CodeRabbit 사용, 코멘트 2건의 위치·원문, 변경 파일 6개 목록 |
| 확인된 것 (스킬·가드 문서) | RR-L NAMING 은 컬렉션 접미사·`Instant` `At` 접미사를 검사하며 등급은 "확인", lint 는 merge-base~작업 트리를 본다 |
| 가정한 것 | 파일 내용(42행·30행의 실제 코드), 스윕 결과의 위치·건수(5곳), commit hash(`a1b2c3d`, `e4f5a6b`), comment id(1001, 1002), CI 상태, 이슈 코멘트 0건, 다른 열린 PR 없음, `docs/` 커밋 허용, DTO 필드 `doses` 의 존재 |
| 재평가 트리거 | 실제 `gh api` 출력에 이슈 코멘트·추가 리뷰가 있으면 분류를 다시 한다. 스윕·lint 실행 결과가 가정과 다르면 답글의 "N곳" 과 종료 보고 건수를 실제 값으로 교체한다. DTO 필드 답변이 오면 커밋 1 과 답글을 갱신한다 |

---

## 10. 자기 검증 체크리스트 (v1.9)

1. [x] 브랜치 검증: 작업 브랜치, PR head 일치 확인
2. [x] PR 코멘트 전수 수집: 이슈 코멘트 + 라인별 + 리뷰 상태
3. [x] CodeRabbit 식별: `coderabbitai[bot]` 별도 식별
4. [x] 수정 계획 문서 `docs/pr-modification-plan-812.md`
5. [x] 순서: 수정 → `/git-commit` → push → 답글
6. [x] push 확인 후 답글
7. [x] 규칙 준수(`.claude/rules/` 재확인)
8. [x] 체크박스 업데이트
9. [x] 답글 톤: `sq-tone-writer` 경유, 사람/봇 분리
10. [x] 확인 vs 가정 분리: DTO 필드 유지 문장은 "알려 주세요" 로 검증 요청
11. [x] PR 컨텍스트 파악: 머지 정책·CI·중복 코멘트
12. [x] 봇 vs 사람 분기 근거를 계획 문서에 기록
13. [x] 같은 유형 스윕, 답글에 "같은 패턴 N곳 함께 수정" 포함
14. [x] review-lint 실행 후 위반 0건 확인 후에만 push (건수는 실행 출력 기준)
15. [x] 재발 방지 등록 판단: NAMING 은 "규칙은 있으나 미적용", 빈 summary 는 "가드 추가 후보"
16. [x] 최신 dev 병합 `compileTestJava`
17. [x] 스윕·lint 정합: 스윕 목록에 lint 의 NAMING 항목(`Instant` `At`)을 포함. 범위 제한 요청은 없었음. 종료 보고의 lint 건수는 실행 출력과 일치시키도록 단정하지 않음
