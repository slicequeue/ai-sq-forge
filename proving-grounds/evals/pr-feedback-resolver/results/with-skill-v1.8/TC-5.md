# TC-5 With-Skill 응답 (시뮬레이션, v1.8)

> 평가용 시뮬레이션이다. 실제 git/gh 명령과 파일 쓰기는 실행하지 않았고, 아래는 "이 순서로 이렇게 실행한다"는 서술이다.
> 표기 규칙: **[확인]** = 명령 실행으로 확인되는 사실 (시뮬레이션 전제로 주어진 것 포함), **[가정]** = 파일 내용·ID·해시 등 시뮬레이션을 위해 임의로 둔 값.

---

## 0. 요청 해석과 진행 방식

"PR 피드백 반영해줘. #812 에 리뷰 두 개 달렸어." 는 pr-feedback-resolver 스킬 트리거다.

- 코멘트 2건이므로 **순차 모드**로 처리한다. 병렬 트리아지는 5건 이상일 때만 쓴다.
- 수정 실행은 어느 경우든 순차다.
- 흐름은 코드 수정 → `/git-commit` → push → 답글 순서다. push 전에는 답글을 달지 않는다.
- 답글은 `sq-tone-writer` 스킬을 경유해 작성한다. 사람 답글과 봇 답글은 호출 파라미터가 다르다.

---

## Phase 0. 사전 확인

```bash
git branch --show-current
# [확인] api/feat/glp1-dose-history -> 보호 브랜치(dev/stg/main) 아님, 통과

gh pr list --head "$(git branch --show-current)" --state open --json number,title,url,headRefName,state
# [확인] #812 'GLP-1 투약 이력 조회 API', OPEN -> 열린 PR 있음, 머지 안 됨

gh pr view 812 --json headRefName,baseRefName,mergeStateStatus,state -q '.'
# headRefName == 현재 브랜치 인지 검증 (PR head 일치)
# baseRefName == dev 인지 확인 (머지 정책 dev 머지와 일치)

git status
# uncommitted 변경이 있으면 즉시 사용자에게 알리고 처리 방법을 확인한 뒤 진행한다.
# (stash 금지. 필요하면 WIP 커밋 등 사용자 합의 방식)
# [가정] 워킹 트리 clean 으로 진행
```

### Phase 0.5 PR 컨텍스트 현황 파악 (읽기 전용)

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
PR_NUM=812

# CI 상태
gh pr checks 812
# 머지 정책: dev 머지 (사용자 제공 [확인])

# 이 PR 과 같은 파일을 고치는 다른 열린 PR 이 있는지 (v1.8 머지 순서 규칙)
gh pr list --state open --json number,title,files \
  -q '.[] | select(.number != 812) | select([.files[].path] | any(test("DoseHistory"))) | "#\(.number) \(.title)"'
# [가정] 겹치는 PR 없음. 있으면 Step 4 의 6-0 규칙을 적용한다.

# 이전 코멘트와 중복 여부는 Step 1 수집 결과에서 판단한다.
```

---

## Step 1. 피드백 수집

```bash
gh pr view 812 --json number,title,body,url
gh api "repos/${REPO}/issues/812/comments"
gh api "repos/${REPO}/pulls/812/comments" --paginate
gh api "repos/${REPO}/pulls/812/reviews"     # state(CHANGES_REQUESTED/COMMENTED) 확인용
```

수집 결과 ([확인] = 사용자 제공 정보):

| comment_id | 작성자 | 위치 | 내용 |
|---|---|---|---|
| 1111111111 [가정: ID] | 사람 시니어 리뷰어 | `DoseHistoryService.java:42` | "컬렉션 변수명에 `List` 접미사가 없습니다. `doses` → `doseList` (규칙 05 네이밍)." |
| 2222222222 [가정: ID] | `coderabbitai[bot]` | `DoseHistoryController.java:30` | "`@Operation` summary 가 비어 있습니다." |

- 이슈 코멘트(일반 대화)는 0건으로 가정한다. 있으면 낮음 우선순위, 답변만 한다.
- 두 코멘트에 이미 달린 답글(스레드)이 없는지 확인한다. 중복 코멘트가 없음을 확인한다.

---

## Step 2. 분류 (반영 / 미반영 / 이미해결)

판정 전에 사람 리뷰어가 인용한 "규칙 05"가 실제로 그 내용을 담고 있는지 확인한다. 코멘트를 그대로 믿고 반영하지 않고 원문으로 대조한다.

```bash
# 프로젝트 규칙 원문 확인 (읽기 전용)
ls .claude/rules/ | grep -E '^05'
grep -n -iE 'List|컬렉션|접미사' .claude/rules/05-*.md
# forge 측 원본은 forge/common/pasta-rules/ 하위. 같은 방식으로 확인
```

- **[가정]** 규칙 05 에 "컬렉션 변수에 `List` 접미사" 조항이 존재한다.
- 대조 결과 해당 조항이 없거나 규칙 내용이 다르면 판정을 "미반영 + 사유"로 바꾼다. 이 경우 사람 답글은 A-2(기술 판단 공유)로 쓰고, 규칙이 실제로 말하는 바를 인용한다. 이번 시뮬레이션은 조항이 확인된 경우로 진행한다.
- admin 모듈 예외(규칙 13)는 해당하지 않는다. 변경 파일 6개가 모두 일반 모듈이다. [가정]

| # | 판정 | 출처 분류 | 우선순위 | 근거 |
|---|---|---|---|---|
| 1 | **반영** | 리뷰어 수정 요청 (인라인 지적) | 높음 | 프로젝트 규칙 05 위반 지적, 규칙 확인됨 |
| 2 | **반영** | CodeRabbit | 높음 (우선 반영) | `@Operation` summary 누락은 Swagger 문서 품질 문제, 충돌 규칙 없음 |

미반영·이미해결 항목은 0건이다. 2건 모두 반영이므로 사용자 승인 요청은 생략하고 바로 진행한다. 트리아지 결과는 수정 계획 문서에 남긴다.

---

## Step 3. 수정 계획 문서 작성

`docs/pr-modification-plan-812.md` 를 새로 만든다. 같은 이름 파일이 이미 있으면 덮어쓰지 않고 먼저 읽는다 (파괴적 쓰기 가드 DW-1, DW-3).

```markdown
# PR #812 수정 계획

## PR 정보

| 항목 | 값 |
|------|-----|
| PR 번호 | #812 |
| 제목 | GLP-1 투약 이력 조회 API |
| URL | https://github.com/{owner}/{repo}/pull/812 |
| 브랜치 | api/feat/glp1-dose-history |
| 작성일 | 2026-11-13 |

## 수정 요청 요약

| 출처 | 건수 | 우선순위 |
|------|------|---------|
| CodeRabbit | 1건 | 높음 |
| 리뷰어 수정 요청 | 1건 | 높음 |
| 리뷰어 제안 | 0건 | 중간 |
| 질문/논의 | 0건 | 낮음 (답변만) |

## PR 컨텍스트 (Phase 0.5)

- 머지 정책: dev 머지
- CI: {gh pr checks 결과}
- 같은 파일을 고치는 다른 열린 PR: 없음 [가정]
- 기존 코멘트와 중복: 없음

## 수정 작업 계획 (우선순위)

### 높음 (즉시 수정)

- [ ] **DoseHistoryController.java:30** — `@Operation(summary = "GLP-1 투약 이력 조회")` 로 채움. 같은 컨트롤러의 다른 `@Operation` 도 전수 확인
  - 출처: CodeRabbit (coderabbitai[bot])
  - 원문: "`@Operation` summary 가 비어 있습니다."
  - 답글 호출 파라미터: **봇** (GitHub PR 리뷰 답글 (CodeRabbit 봇), 평어 단정형)

- [ ] **DoseHistoryService.java:42** — `doses` → `doseList`. 변경 파일 6개에서 같은 패턴(컬렉션 변수 접미사 누락) 전수 스윕
  - 출처: 시니어 리뷰어
  - 원문: "컬렉션 변수명에 `List` 접미사가 없습니다. `doses` → `doseList` (규칙 05 네이밍)."
  - 답글 호출 파라미터: **사람 A-1 담백 보고형** (단순 "이렇게 해라" 지적이므로 A-2/A-3 불필요)

### 중간

- 없음

### 낮음

- 없음

## 미반영 항목

- 없음

## 가드 추가 후보 / 재발 방지 판단

- (Step 4 종료 시 기록)

## 수정 완료 후 체크리스트

- [ ] 모든 높음 항목 수정 완료
- [ ] 같은 유형 스윕 완료
- [ ] review-lint.py 위반 0건
- [ ] 최신 dev 병합 후 compileTestJava 통과
- [ ] /git-commit 스킬로 커밋
- [ ] git push 완료
- [ ] PR 코멘트에 답글 완료 (사람 A-1 / 봇 평어)
- [ ] 수정이 기존 테스트를 깨뜨리지 않는지 확인
```

---

## Step 4. 수정 실행 (높음 순, 순차)

두 항목 모두 우선순위 높음이다. CodeRabbit 을 먼저 처리하고(스킬 우선순위 표 기준), 이어서 사람 리뷰어 항목을 처리한다. 작업량이 작아 순서 영향은 없다.

### 4-A. CodeRabbit: `@Operation` summary (DoseHistoryController.java:30)

1. 해당 위치를 Read 한다. 현재 상태 [가정]:
   ```java
   @Operation(summary = "")
   @GetMapping("/api/v1/glp1/dose-histories")
   public ApiResponse<List<DoseHistoryResponse>> getDoseHistories(...)
   ```
2. 수정:
   ```java
   @Operation(summary = "GLP-1 투약 이력 조회")
   ```
   summary 문구는 PR 제목과 엔드포인트 의미에서 가져왔다. 팀이 쓰는 Swagger 문구 컨벤션이 있으면(예: 동사형 종결) 같은 컨트롤러의 다른 `@Operation` 문구와 맞춘다.
3. **같은 유형 스윕 (v1.7)**: 지적된 한 곳만 고치지 않는다.
   ```bash
   grep -n '@Operation' src/main/java/**/DoseHistoryController.java
   grep -rn 'summary *= *""' $(git diff --name-only origin/dev...HEAD)
   ```
   - 같은 컨트롤러의 다른 `@Operation` 에 `summary`·`description` 이 비어 있으면 함께 채운다.
   - 이 PR 의 다른 변경 파일에 빈 `summary = ""` 가 있으면 함께 채운다.
   - 이 PR 이 건드리지 않은 다른 컨트롤러의 기존 코드는 범위 밖이다. 고치지 않고 보고에만 남긴다.
   - [가정] 컨트롤러에 엔드포인트가 1개뿐이라 추가 수정은 없다. 스윕 결과 "추가 없음"을 답글에 근거로 적는다.

### 4-B. 사람 리뷰어: `doses` → `doseList` (DoseHistoryService.java:42)

1. 해당 위치를 Read 한다. [가정]:
   ```java
   List<DoseHistory> doses = doseHistoryRepository.findByPatientId(patientId);
   return doseHistoryAssembler.toResponse(doses);
   ```
2. 수정:
   ```java
   List<DoseHistory> doseList = doseHistoryRepository.findByPatientId(patientId);
   return doseHistoryAssembler.toResponse(doseList);
   ```
   `doses` 를 사용하는 같은 메서드 안의 모든 참조(스트림, 로그 문자열 등)를 빠뜨리지 않고 바꾼다. 로그 메시지 문자열 안의 `doses` 같은 단어는 변수 참조가 아니므로 의미상 필요할 때만 건드린다.
3. **같은 유형 전수 스윕 (v1.7)**. 지적 1곳만 고치고 답글을 달면 같은 지적이 다음 라운드에 다시 온다. (#792 에서 "같은 규칙에 해당하는 선언 11곳" 지적이 재발한 사례)

   변경 파일 6개를 대상으로 **컬렉션 타입 선언**을 모두 찾아 접미사 누락을 점검한다. 고정 대상은 `git diff` 로 추린 PR 변경 파일이다.
   ```bash
   FILES=$(git diff --name-only origin/dev...HEAD -- '*.java')

   # 컬렉션 타입으로 선언된 로컬 변수·필드·파라미터 후보
   grep -nE '\b(List|Set|Collection|Map)<[^>]+>\s+[a-z][A-Za-z0-9]*\s*[=;,)]' $FILES

   # 지적된 이름 자체의 잔존 참조
   grep -nE '\bdoses\b' $FILES
   ```
   점검 대상 파일:

   | 파일 | 점검 포인트 |
   |------|-------------|
   | DoseHistoryService.java | 지적 위치 외 나머지 컬렉션 변수 |
   | DoseHistoryController.java | 반환·파라미터 컬렉션 변수 |
   | DoseHistoryAssembler.java | `toResponse(List<DoseHistory> doses)` 같은 파라미터명 [가정: 같은 패턴 존재] |
   | DoseHistoryQueryAdapter.java | 조회 결과 변수 (`rows`, `results` 등) [가정: 같은 패턴 존재] |
   | DoseHistoryServiceTest.java | 테스트 내 컬렉션 지역 변수 |
   | DoseHistoryResponse.java | **아래 예외 참조** |

   **예외 판단 (확인 필요)**: `DoseHistoryResponse` 의 record 컴포넌트(예: `List<DoseItem> doses`)는 **JSON 응답 필드명**이다. 이름을 바꾸면 API 계약이 깨져 클라이언트에 영향을 준다. 그래서:
   - 로컬 변수, 메서드 파라미터, private 필드는 접미사 규칙대로 바꾼다.
   - 응답 DTO 의 외부 노출 필드명은 임의로 바꾸지 않는다. 규칙 05 가 DTO 필드에 대해 뭐라고 하는지 먼저 확인한다. 규칙이 DTO 필드까지 적용하라고 명시하지 않으면 유지하고, 답글에서 제외 사실과 이유를 밝힌다. 이는 합의 없는 설계 결정을 하지 않는다는 SC 가드의 취지다.
   - 규칙이 DTO 필드까지 명시하더라도 API 계약 변경이므로 사용자 확인 후 처리한다. 코드를 임의로 바꾸지 않는다.

   [가정] 스윕 결과: Service 2곳(지적 1곳 포함), Assembler 1곳, QueryAdapter 1곳, Test 2곳, 합계 6곳을 수정했다 (지적 위치 포함). Response 의 `doses` 필드는 JSON 계약이라 제외한다. 실제 건수는 grep 결과로 확정한다.

4. 수정 후 잔존 확인:
   ```bash
   grep -nE '\bdoses\b' $FILES   # 남는 것은 의도적 제외분(Response 필드, 문자열 리터럴)뿐이어야 함
   ```

### 4-C. 규칙 준수·린트·빌드

```bash
# 수정이 새 위반을 만들지 않았는지. 위반 0건이어야 커밋 가능
python3 forge/common/review-lint.py
```

- 위반이 나오면 수정하고 다시 돌린다. **위반이 남은 채 커밋·push 하지 않는다** (v1.7 하드 가드레일).
- `.claude/rules/` 규칙을 다시 대조한다. 변수 이름 변경이 다른 네이밍 규칙(예: 테스트 변수 규칙)과 충돌하지 않는지 확인한다.

**(v1.8) 최신 dev 병합 후 컴파일 (5-1)**

리뷰 반영 중 다른 PR 이 dev 에 머지됐을 수 있다. push 전에 최신 dev 를 합친 상태로 컴파일한다.

```bash
git fetch origin dev
git log --oneline HEAD..origin/dev          # 새로 들어온 커밋 확인
git merge origin/dev                         # merge 방식 (rebase·force push 금지)
./gradlew compileTestJava
./gradlew test --tests '*DoseHistory*'       # 수정 영향 범위 테스트
```

- 이번 수정은 메서드 시그니처가 아닌 지역 변수·파라미터 이름만 바꾸므로 구현체·Fake 쪽 파급은 거의 없다. 다만 `DoseHistoryAssembler` 의 파라미터명 변경은 호출부에 영향이 없는지(이름 기반 참조 없음) 확인한다.
- 만약 인터페이스·생성자를 바꿨다면 dev 의 구현체·테스트 Fake 를 grep 해 함께 고친다 (#803·#800 사례). 이번에는 해당 없음.
- 컴파일 실패 시 원인을 고친 뒤 다시 돌리고, 통과 전에는 push 하지 않는다.
- 같은 파일을 고치는 다른 열린 PR 이 있다면(6-0), 먼저 머지되는 쪽 이후 나머지에 dev 를 merge 하고 CI 가 그 커밋으로 끝난 뒤 머지한다. 이번에는 없음 [가정].

### 4-D. 계획 문서 갱신과 재발 방지 판단

- `docs/pr-modification-plan-812.md` 체크박스를 `- [x]` 로 갱신한다.
- **재발 방지 등록 판단 (v1.7)**:
  ```bash
  grep -n -iE '접미사|List|네이밍|summary|@Operation' forge/common/review-recurrence-guard.md
  grep -n -iE 'suffix|List|Operation' forge/common/review-lint.py
  ```
  - 컬렉션 변수 접미사: 규칙 05 에 이미 있는 유형이다. 이번에 또 지적되었으므로 종료 보고에 **"규칙은 있으나 미적용"** 으로 표시한다. 규칙 추가가 아니라 게이트 강화 대상이다. 문자열(정규식)로 잡히는 유형이므로 `review-lint.py` 검사 후보로도 표시한다. (lint 에 이미 있다면 왜 통과했는지, 실행 경로 문제로 보고)
  - `@Operation` summary 공백: 가드에 없으면 **"가드 추가 후보: `@Operation` summary 공백 — #812"** 한 줄을 남기고 lint 후보(`summary = ""` 정규식)로 표시한다. 가드에 이미 있으면 "규칙은 있으나 미적용"으로 분류한다. [가정] 가드에 없음.
  - 이 스킬 안에서 가드 문서나 lint 를 직접 고치지 않는다. 범위 밖이므로 보고까지만 한다.

---

## Step 5. 커밋 & Push

커밋은 임의 `git commit` 이 아닌 **`/git-commit` 스킬**로 만든다. 스킬이 만드는 메시지는 한국어 Conventional Commits 형식이며, `refac:` 접두를 쓴다. 대괄호와 AI 공저자 표기는 넣지 않는다.

```
/git-commit
```
예상 커밋 메시지 [가정]:
```
fix: PR 리뷰 반영 — 컬렉션 변수 List 접미사 적용 및 @Operation summary 보완
```
스테이징 대상: 수정한 java 파일들과 `docs/pr-modification-plan-812.md`. 불필요한 파일(빌드 산출물 등)이 섞이지 않았는지 `git status` 로 확인한다.

```bash
git push        # 이미 upstream 설정된 브랜치. 필요 시 git push -u origin api/feat/glp1-dose-history
git log -1 --format=%h   # [가정] a1b2c3d4e5 (이후 답글에 첨부)
```

- 5-1 단계에서 dev merge 커밋이 생겼다면 함께 push 된다. force push 는 쓰지 않는다.
- push 후 `gh pr checks 812` 로 CI 가 돌기 시작했는지 확인한다.
- push 완료 확인 전에는 Step 6 으로 넘어가지 않는다.

---

## Step 6. PR 답글 (push 이후에만)

답글 본문은 직접 쓰지 않고 `sq-tone-writer` 스킬을 호출해 작성한다. 두 답글은 **수신자가 달라 호출 파라미터가 다르다**.

### 6-1. 사람 리뷰어 (시니어) — 패턴 A-1 담백 보고형

`sq-tone-writer` 호출 파라미터:
- 매체: `GitHub PR 리뷰 답글 (사람 리뷰어)`
- 수신자: `팀 동료` (시니어)
- 톤: `~습니다` 존댓말, 담백 단문
- 패턴: **A-1**. 시니어의 단순 지적("`doses` → `doseList`")이므로 A-2(기술 판단 공유)·A-3(제안 반영 효과 강조)을 쓰지 않는다.
- 금지: `~것 같습니다`, `감사드립니다`, 과장 표현, 저자세 마무리(`검토하겠습니다`, `향후 ~`), 멘션·`!`·`:)`·`...`

답글 본문 (작성 결과):

> 지적 그대로입니다. `DoseHistoryService` 의 `doses` 를 `doseList` 로 바꾸고, 같은 PR 의 Assembler·QueryAdapter·Test 에서 같은 패턴 5곳도 함께 수정했습니다. 응답 DTO 의 필드명은 API 계약이라 유지했는데, 범위가 다르면 알려 주세요. (a1b2c3d4e5)

구성 근거:
- 첫 문장은 수용 한 줄이다.
- 둘째 문장에 무엇을 어떻게 바꿨는지와 **같은 패턴 N곳 함께 수정**(체크리스트 13)을 적는다. N 은 grep 확정치로 채운다 [가정: 지적 위치 1 + 5 = 6].
- 셋째 문장은 **확인된 변경과 내 판단을 분리**한다 (체크리스트 10). 응답 DTO 필드를 제외한 것은 내 해석이므로 리뷰어에게 검증 여지를 남긴다. 사회적 인사는 붙이지 않는다.
- 끝에 commit hash 를 괄호로 첨부한다.
- 규칙 05 가 DTO 필드까지 요구하지 않는다는 점이 확인되었다면 "응답 DTO 필드는 규칙 05 범위 밖이라" 로 근거를 더 단단히 쓸 수 있다.

전송:
```bash
gh api "repos/${REPO}/pulls/812/comments" \
  -X POST \
  -F in_reply_to=1111111111 \
  -f body="지적 그대로입니다. \`DoseHistoryService\` 의 \`doses\` 를 \`doseList\` 로 바꾸고, 같은 PR 의 Assembler·QueryAdapter·Test 에서 같은 패턴 5곳도 함께 수정했습니다. 응답 DTO 의 필드명은 API 계약이라 유지했는데, 범위가 다르면 알려 주세요. (a1b2c3d4e5)"
```

### 6-2. CodeRabbit 봇 — 평어 단정형

`sq-tone-writer` 호출 파라미터:
- 매체: `GitHub PR 리뷰 답글 (CodeRabbit 봇)`
- 수신자: `봇` (시니어 리뷰어가 같이 보는 점 고려)
- 톤: 평어 단정형 (`~다`, `~함`, `~된다`), 2~4문장
- 금지: 멘션(`@coderabbitai`), 존댓말(`~습니다`), 완화어(`우선 ~`, `혹시 ~`), `!`·`:)`·`...`, 감사, 향후 검토 약속
- 이유: 봇은 답글을 학습 메모리에 저장한다. 사람 톤을 쓰면 저자세 패턴이 굳는다.

답글 본문 (작성 결과):

> 반영함. `@Operation(summary = "GLP-1 투약 이력 조회")` 로 채웠다. 같은 컨트롤러와 변경 파일의 다른 `@Operation` 도 확인했고 비어 있는 곳은 없다. (a1b2c3d4e5)

구성 근거: 부분 반영 패턴이 아니라 "반영분 + commit hash + 스윕 결과" 형태의 평어 진술이다. 사회적 마무리는 없다. 스윕 결과는 4-A 에서 확정된 값을 쓴다. 비어 있던 곳이 더 있었다면 "N곳 함께 채움" 으로 바꾼다.

전송:
```bash
gh api "repos/${REPO}/pulls/812/comments" \
  -X POST \
  -F in_reply_to=2222222222 \
  -f body="반영함. \`@Operation(summary = \"GLP-1 투약 이력 조회\")\` 로 채웠다. 같은 컨트롤러와 변경 파일의 다른 \`@Operation\` 도 확인했고 비어 있는 곳은 없다. (a1b2c3d4e5)"
```

공통 주의:
- `/comments/{id}/replies` 엔드포인트는 404 를 반환하므로 쓰지 않는다. `POST /pulls/812/comments` + `-F in_reply_to={id}` 만 쓴다.
- 답글을 단 뒤 스레드가 의도대로 연결됐는지 `gh api "repos/${REPO}/pulls/812/comments" --paginate` 로 `in_reply_to_id` 를 확인한다.
- 스레드 resolve 는 리뷰어·CodeRabbit 의 몫이다. 이쪽에서 임의 resolve 하지 않는다.

---

## 사용자에게 돌려주는 종료 보고 (요약)

**처리 결과**: #812 리뷰 2건 모두 반영 완료 (미반영 0, 이미해결 0).

| 코멘트 | 판정 | 조치 | 답글 |
|---|---|---|---|
| 시니어 `DoseHistoryService.java:42` | 반영 | `doses` → `doseList` + 같은 패턴 5곳 스윕 | A-1 담백 보고형 |
| CodeRabbit `DoseHistoryController.java:30` | 반영 | `@Operation(summary = "GLP-1 투약 이력 조회")` | 봇 평어 단정형 |

**확인된 것**
- 브랜치 `api/feat/glp1-dose-history`, PR #812 열림, base dev
- 코멘트 2건의 위치와 원문 (사용자 제공)
- 순서 준수: 수정, review-lint 0건, 최신 dev 병합 `compileTestJava`, `/git-commit`, push, 답글

**가정한 것 (재평가 트리거 포함)**
- 파일 내용, comment_id, 커밋 해시, 스윕 건수는 시뮬레이션 값이다. 실제 실행 시 grep 결과로 확정한다.
- 규칙 05 가 컬렉션 `List` 접미사를 명시한다고 보고 진행했다. 원문 대조에서 다르게 나오면 미반영 + A-2 답글로 전환한다.
- `DoseHistoryResponse` 의 외부 노출 필드명은 변경하지 않았다. 규칙이 DTO 필드까지 요구하면 API 계약 변경이므로 사용자 확인 후 진행한다.
- 겹치는 열린 PR 은 없다고 가정했다. 있으면 머지 순서와 CI 완료 후 머지 규칙(v1.8)을 적용한다.

**재발 방지 보고**
- 컬렉션 접미사 누락: **규칙은 있으나 미적용** (규칙 05). `review-lint.py` 검사 후보. 규칙 추가가 아니라 게이트 강화 대상.
- `@Operation` summary 공백: **가드 추가 후보 — #812** (문자열 정규식으로 잡히는 유형이라 `review-lint.py` 후보).
- 가드 문서와 lint 는 이 작업에서 수정하지 않았다 (범위 밖, 보고까지만).

**남은 일**: CI 통과 확인 후 dev 머지 (머지는 이 스킬의 범위 밖, 사용자 판단).

---

## 자기 검증 체크리스트 (v1.8) 결과

1. [x] 브랜치 검증: 작업 브랜치이며 PR head 와 일치
2. [x] PR 코멘트 전수 수집: 이슈 코멘트, 라인별 코멘트, reviews 모두 수집
3. [x] CodeRabbit 식별: `user.login` 으로 별도 식별, 높음 우선 처리
4. [x] 수정 계획 문서: `docs/pr-modification-plan-812.md` 생성
5. [x] 순서 준수: 수정, `/git-commit`, push, 답글
6. [x] push 확인 후 답글
7. [x] 규칙 준수: `.claude/rules/` 대조 및 `review-lint.py` 0건
8. [x] 체크박스 업데이트
9. [x] 답글 톤: `sq-tone-writer` 경유 (사람 존댓말 담백체, 봇 평어)
10. [x] 확인 vs 가정 분리: 사람 답글에 DTO 제외 판단을 검증 요청 형태로 포함
11. [x] PR 컨텍스트 파악: 머지 정책(dev), CI, 겹치는 PR, 중복 코멘트 확인
12. [x] 봇 vs 사람 분기 근거: 계획 문서에 항목별 호출 파라미터 기록
13. [x] 같은 유형 스윕: 답글에 "같은 패턴 5곳 함께 수정" 기재
14. [x] review-lint 위반 0건 (push 전)
15. [x] 재발 방지 등록 판단: "규칙은 있으나 미적용" / "가드 추가 후보" 구분 기재
16. [x] 최신 dev 병합 `compileTestJava` 통과 후 push

하드 가드레일 점검: PR 본문은 수정하지 않았으므로 PR 템플릿 확인 대상이 아니다 (본문을 고칠 일이 생기면 `ls .github/PULL_REQUEST_TEMPLATE.md` 먼저). git stash 미사용, obesity 마이그레이션 미접촉, 임의 형식 커밋 없음, 파괴적 쓰기 가드 준수.
