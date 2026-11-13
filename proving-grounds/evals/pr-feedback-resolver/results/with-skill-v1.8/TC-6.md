# TC-6 With-Skill 응답 (시뮬레이션, v1.8)

적용 스킬: `pr-feedback-resolver` v1.8, 참조: `git-pr` v0.5, `review-recurrence-guard.md`.
아래는 실제로 실행하지 않고, 실행할 순서·명령·판단·답글 본문을 서술한 것이다.

## 0. 먼저 하는 말 (요청에 대한 판단)

요청은 "커밋 → push → 답글"이다. 순서 자체는 스킬 순서(수정 → 커밋 → push → 답글)와 같다. 다만 아래 두 가지 때문에 바로 push 하지 않고 push 앞에 게이트를 하나 더 둔다.

1. "로컬 빌드 통과"는 **로컬 브랜치 단독** 결과다. CI 는 PR 을 **최신 dev 와 합친 상태**로 `test` 를 돈다. 작업 중 #813 이 dev 에 머지됐으므로, 그 상태로 컴파일되는지는 아직 확인된 적이 없다. 포트 인터페이스 시그니처를 바꿨기 때문에 위험이 크다. dev 쪽에 이 인터페이스의 구현체나 테스트 Fake 가 새로 들어왔다면 내 diff 에는 보이지 않지만 컴파일이 깨진다 (git-pr v0.5 게이트, #803 사례).
2. #816 도 `DoseRecordReader.java` 를 고치고 있다. 같은 파일을 고치는 PR 이 둘이므로 머지 순서와 CI 완료 시점 규칙(v1.8 Step 4-6-0)이 적용된다. "둘 다 빨리 머지"는 이 규칙을 지킨다는 조건에서만 빠르게 갈 수 있다.

답글은 push 가 끝난 뒤에만 단다. 머지는 요청받지 않았고 리뷰어 승인 영역이므로 내가 실행하지 않는다.

## 1. 확인된 것 vs 가정한 것

| 구분 | 내용 |
|------|------|
| 확인된 것 (사용자 진술) | 리뷰 지적 1건, 시그니처 `findLatest(Long userId, Instant asOf)` 로 변경, 구현체 1개·테스트 Fake 1개 수정, 미커밋, 로컬 `compileTestJava` 통과, #813 은 dev 에 머지됨, #816 은 `DoseRecordReader.java` 를 수정 중이며 미머지 |
| 아직 확인 안 된 것 | #813 의 내용, 최신 dev 와 합친 상태의 컴파일·테스트 결과, 구현체·Fake 가 정말 "각 1개"인지(dev 기준), 지적한 리뷰어가 사람인지 봇인지, 리뷰 코멘트가 이 1건뿐인지, 구현이 `asOf` 이하 필터를 실제로 거는지, #816 이 이 인터페이스를 건드리는지 |
| 가정 (재평가 트리거 포함) | 리뷰어는 사람이라고 가정하고 답글 톤을 A-1 로 잡는다. Step 1 에서 `user.login` 이 `coderabbitai[bot]` 이면 봇 톤(평어 단정형)으로 바꾼다 |

## 2. 실행 순서

### Phase 0. 사전 확인

```bash
git branch --show-current                  # api/refac/dose-reader-asof 확인. dev/stg/main 이면 즉시 중단
gh pr list --head "$(git branch --show-current)" --state open --json number,title,url
gh pr view 815 --json number,title,state,headRefName,mergedAt,reviewDecision,mergeStateStatus
git status
git diff --stat
```

- 보호 브랜치가 아니고, PR head(`api/refac/dose-reader-asof`)와 현재 브랜치가 일치하며, #815 가 OPEN·미머지인 것을 확인한다.
- `git status` 의 미커밋 변경은 사용자가 방금 한 반영분이므로 "처리 방법을 묻는" 대상이 아니라 **내용 확인** 대상이다. `git diff --stat` 로 변경 파일이 인터페이스 1 + 구현체 1 + Fake 1 + (테스트) 범위인지 본다. 의도하지 않은 파일이 섞여 있으면 어떤 파일을 커밋에 넣을지 사용자에게 묻는다.
- `git stash` 는 쓰지 않는다 (하드 가드레일). 다른 브랜치로 옮겨야 할 일이 생기면 WIP 커밋을 쓴다.

### Phase 0.5. PR 컨텍스트 현황 파악 (읽기 전용)

```bash
gh pr checks 815                                  # CI 상태
gh pr view 815 --json baseRefName,mergeable,reviewDecision,reviews,statusCheckRollup
ls .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md 2>/dev/null
git fetch origin dev
git log --oneline HEAD..origin/dev                # 내 브랜치가 뒤처진 dev 커밋 (#813 포함)
```

머지 정책(리뷰 승인 수, 필수 체크, 브랜치가 최신이어야 하는지)은 `gh pr view` 결과와 저장소 설정에서 확인한다. 추정으로 적지 않는다.

### Step 1. 피드백 수집 (전수)

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh pr view 815 --json number,title,body,url
gh api "repos/${REPO}/issues/815/comments"
gh api "repos/${REPO}/pulls/815/comments" --paginate
gh api "repos/${REPO}/pulls/815/reviews"
```

- 이슈 코멘트·라인 코멘트·리뷰 상태를 모두 모은다. 사용자가 말한 1건 외에 다른 코멘트가 있으면 함께 분류한다. 없으면 "1건뿐임을 확인했다"고 기록한다.
- 라인 코멘트의 `id`(답글용 `in_reply_to` 값)와 `user.login` 을 기록한다. 이미 같은 내용의 답글이 달려 있는지(중복)도 본다.

### Step 2. 분류

| 코멘트 | 작성자 | 판정 | 우선순위 |
|--------|--------|------|----------|
| "`DoseRecordReader.findLatest(userId)` 가 미래 기록을 최신으로 잡습니다. 기준 시각을 받으세요." | 사람 리뷰어(가정, login 으로 확인) | **반영** | 높음 (리뷰어 수정 요청) |

코멘트가 1건이므로 병렬 트리아지 모드는 쓰지 않는다.

### Step 3. 수정 계획 문서 `docs/pr-modification-plan-815.md`

`docs/` 는 `.git/info/exclude` 로 추적 제외라서 **커밋에 넣지 않는다.** 내용은 다음과 같다.

```markdown
# PR #815 수정 계획

## PR 정보
| 항목 | 값 |
|------|-----|
| PR 번호 | #815 |
| 브랜치 | api/refac/dose-reader-asof |
| 작성일 | 2026-11-13 |

## 수정 요청 요약
| 출처 | 건수 | 우선순위 |
|------|------|---------|
| CodeRabbit | 0건 | 높음 |
| 리뷰어 수정 요청 | 1건 | 높음 |

## 수정 작업 계획
### 높음
- [x] DoseRecordReader.findLatest — 기준 시각 asOf 인자 추가, asOf 이하 기록만 최신 후보
  - 출처: 리뷰어
  - 원문: "findLatest(userId) 가 미래 기록을 최신으로 잡습니다. 기준 시각을 받으세요."
  - 답글 파라미터: 사람 리뷰어 A-1 (담백 보고형)
- [ ] 같은 유형 스윕 — 같은 PR 의 다른 "최신 조회" 경로·호출부 (Step 4 항목 4)
- [ ] 최신 dev 병합 컴파일 (Step 4 항목 5-1)

## 수정 완료 후 체크리스트
- [ ] review-lint 위반 0건
- [ ] /git-commit 으로 커밋
- [ ] 최신 dev 병합 상태 compileTestJava + 관련 test 통과
- [ ] push, CI(test) 통과 확인
- [ ] 리뷰 코멘트 답글
```

### Step 4. 수정 실행 — 이미 한 반영분을 검증한다

코드 수정은 사용자가 끝냈다. 나는 `git diff` 를 **읽기만** 해서 아래를 확인한다. 부족하면 파일을 통째로 덮지 않고(DW-3) 해당 부분만 고친다. 고칠 것이 크면 사용자에게 먼저 보고한다.

**4-a. 지적이 실제로 막혔는지 (RR-14, RR-2)**
- 구현체가 `recordedAt <= asOf` 조건을 거는가. 경계는 "현재 시각 이하"(같은 시각 포함)다.
- 정렬에 동점 2차 기준이 있는가 (`ORDER BY 기록시각 DESC, id DESC`). 같은 시각 기록 둘이면 조회 순서에 의존하지 않아야 한다.
- 호출부가 `asOf` 를 `Instant.now()` 직접 호출이 아니라 주입된 `Clock` 에서 만드는가 (테스트 결정성).
- Fake 가 `asOf` 필터를 실제로 구현하는가. Fake 가 `asOf` 를 무시하면 미래 기록 테스트가 구현체 필터를 못 잡는다 (RR-12).

**4-b. 테스트가 실제로 잡는가 (RR-12)**
- 미래 기록 1건 + 과거 기록 1건을 두고 `asOf` 시점에 과거 기록이 나오는지, 경계 시각 기록이 포함되는지 확인하는 테스트가 있는가. 필터를 일부러 빼면 실패해야 한다. 없으면 추가를 사용자에게 제안한다 (사용자가 요청하지 않은 설계 결정이 아니라 지적의 회귀 방지이므로 추가 후 보고).
- 상태 저장소는 Mock `given().willReturn()` 이 아니라 Fake 에 저장한 뒤 조회하는 방식이어야 한다.

**4-c. 같은 유형 전수 스윕 (v1.7)**

```bash
grep -rnE "findLatest|findLast|findRecent|findCurrent" --include=*.java */src/main */src/test
grep -rn "DoseRecordReader" --include=*.java */src/main */src/test
grep -rnE "implements DoseRecordReader|new DoseRecordReader\(|mock\(DoseRecordReader" --include=*.java */src
```

- 호출부 전부가 새 시그니처로 컴파일되는지, 시각 기준 없이 "최신/마지막"을 뽑는 다른 조회가 같은 PR 변경 범위에 더 있는지 찾는다. 있으면 같은 방식으로 함께 고치고, 없으면 "스윕 결과 0곳"이라고 기록한다.
- 사용자가 말한 "구현체 1개, Fake 1개"는 이 grep 으로 **재확인**한다. 이것은 로컬 브랜치 기준 확인일 뿐이고, dev 기준 확인은 아래 5-1 에서 다시 한다.

**4-d. review-lint (v1.7)**

```bash
python3 forge/common/review-lint.py --base origin/dev
```

- 위반은 0건이어야 한다. 위반이 남으면 push 하지 않는다 (RR-F15).
- 확인 등급은 사유를 남긴다. 예를 들어 `Instant` 변수 `asOf` 가 NAMING(`At` 접미사) 확인 항목에 걸리면, "시점 기준 인자 관용 표기(`asOf`)이며 지적 문구 그대로 반영"이라는 사유를 답글이나 PR 본문에 남긴다. 이름을 바꿀지는 리뷰어와 합의할 사안이라 내가 임의로 바꾸지 않는다.

**4-e. 커밋 (`/git-commit` 스킬만 사용)**

```
/git-commit
```

- 한국어 Conventional Commits, `refactor:` 가 아니라 `refac:`, 대괄호 금지, AI 공동작성자 표기 금지.
- 이 변경은 시그니처 변경(구조)과 미래 기록 제외(동작)가 함께 있으므로 제안 메시지는 `fix: 최신 투여 기록 조회에서 미래 기록 제외 (기준 시각 asOf 추가)` 이다. 브랜치명이 refac 이므로 type 을 `refac` 으로 할지는 `/git-commit` 의 판단과 사용자 선택에 맡긴다.
- 커밋 대상은 인터페이스·구현체·Fake·테스트 변경만이다. `docs/pr-modification-plan-815.md` 는 제외한다.
- 이 시점에서 커밋하는 이유: 다음 단계에서 dev 를 합쳐 보려면 워킹 트리가 깨끗해야 하고, stash 는 금지이기 때문이다. 이 커밋은 아직 push 하지 않는다.

### Step 4-5-1. 최신 dev 병합 상태 컴파일 (v1.8 핵심 게이트)

```bash
git fetch origin dev
git log --oneline HEAD..origin/dev

# 임시 병합 (커밋 안 함)
git merge --no-commit --no-ff origin/dev
git status                          # 충돌 여부
./gradlew :{module}:compileTestJava
./gradlew :{module}:test --tests '*DoseRecord*'   # CI 가 test 를 돌리므로 관련 테스트도 확인
grep -rnE "implements DoseRecordReader|DoseRecordReader\b.*(\{|=)|findLatest\(" --include=*.java */src/main */src/test
git merge --abort                   # 결과 확인 후 임시 병합 취소 (아래 분기 참고)
```

(`{module}` 은 `DoseRecordReader` 가 속한 Gradle 모듈로 대체한다. 실제로는 `grep -rl DoseRecordReader --include=*.java` 로 모듈을 찾는다.)

**#813 이 무엇인지는 사용자가 모르므로 확인 방법을 제시한다.**

```bash
gh pr view 813 --json title,author,mergedAt,mergeCommit,files --jq '{title,author:.author.login,mergedAt,files:[.files[].path]}'
git diff --name-only HEAD...origin/dev
git diff HEAD...origin/dev -G'DoseRecordReader|findLatest'   # 이 인터페이스·메서드를 건드린 변경만
git log origin/dev -S'DoseRecordReader' --oneline            # 구현체·Fake 가 새로 생긴 커밋
```

결과별 처리는 다음과 같다.

| 결과 | 처리 |
|------|------|
| #813 이 `DoseRecordReader` 와 무관, 충돌 없음, 컴파일·테스트 통과 | `git merge --abort` 후 진행. CI 는 어차피 dev 와 합쳐서 돌린다. 저장소가 "브랜치가 최신이어야 머지 가능" 정책이면 그때 dev 를 merge 한다 |
| dev 에 새 구현체·Fake·호출부가 있어 컴파일 실패 | 병합을 abort 하지 말고 그 상태에서 해당 구현체·Fake·호출부를 새 시그니처에 맞게 고친 뒤 **merge 커밋**을 만든다 (`/git-commit` 경유). **force push 금지**, 일반 push 로 올린다. 어떤 파일을 고쳤는지 사용자에게 보고한다 |
| `DoseRecordReader.java` 에서 텍스트 충돌 | 임의로 해소하지 않는다. 충돌 hunk 와 #813 의 의도를 사용자에게 보여주고 어느 쪽을 살릴지 확인받는다 (합의 없는 설계 결정 금지) |
| #813 이 같은 메서드의 의미(예: `findLatest` 에 다른 인자 추가)를 바꿈 | 설계 충돌이므로 중단하고 #813 작성자·리뷰어와 조정이 필요하다고 보고한다 |

로컬 단독 컴파일 통과는 이 게이트를 대체하지 않는다. 이 게이트를 통과하기 전에는 push 하지 않는다.

### Step 5. push

```bash
git push        # 필요하면 git push -u origin HEAD. force push 는 쓰지 않는다
gh pr checks 815 --watch     # CI(test) 완료 확인
```

- push 직전 PreToolUse 훅(`review-lint-push-hook.sh`)이 있으면 그 결과를 따른다.
- CI 가 실패하면 로그를 읽고 원인을 사용자에게 보고한다. CI 가 끝나기 전에 답글을 달지 않아도 규칙 위반은 아니지만, 이번 건은 "push 완료 후 답글"을 지키되 CI 결과를 확인한 뒤 답글을 다는 쪽이 안전하다. 코드 수정이 CI 에서 뒤집히면 이미 단 "반영했습니다" 답글이 틀린 말이 되기 때문이다.

### Step 6. 답글

전제: push 완료. 답글 본문은 **`sq-tone-writer` 스킬을 경유**해 작성한다 (직접 작성 금지). 호출 파라미터는 매체 `GitHub PR 리뷰 답글 (사람 리뷰어)`, 수신자 `팀 동료`, 패턴 **A-1 담백 보고형**(리뷰어 지적이 "이렇게 해라" 형태의 단순 지적이므로). 이 세션에서 `sq-tone-writer` 를 로드할 수 없으면 임의 문체로 대체하지 않고 사용자에게 알린다.

답글 초안 (commit hash 는 push 후 `git rev-parse --short HEAD` 값으로 채운다):

> 지적 그대로입니다. `findLatest(userId, asOf)` 로 바꿔 `asOf` 이하 기록만 최신 후보로 보도록 했고, 구현체와 테스트 Fake 도 같은 시그니처로 맞췄습니다. (`{short hash}`)

- 4-b 에서 미래 기록 테스트를 **실제로 확인했거나 추가한 경우에만** 두 번째 문장에 "미래 기록이 섞인 경우를 검증하는 테스트를 추가했습니다."를 덧붙인다. 확인하지 못했으면 쓰지 않는다 (확인된 사실만 적는다).
- 4-c 스윕에서 같은 패턴을 더 찾아 고쳤다면 "같은 패턴 N곳 함께 수정했습니다."를 덧붙인다. 0곳이면 쓰지 않는다.
- dev 병합으로 다른 구현체·Fake 를 고쳤다면 "최신 dev 의 구현체 N개도 함께 맞췄습니다."를 덧붙인다.
- 금지 표현(`~것 같습니다`, `감사드립니다`, 과장, 저자세 마무리)과 소프트 디테일을 쓰지 않는다. 리뷰어 의도를 추정해서 쓰지 않는다.
- 작성자가 `coderabbitai[bot]` 로 확인되면 같은 내용을 평어 단정형(`~다`)으로 바꾼다. 존댓말, 멘션, 감사, `!` 는 쓰지 않는다.

전송 (`/replies` 엔드포인트 금지, 404):

```bash
gh api "repos/${REPO}/pulls/815/comments" \
  -X POST \
  -F in_reply_to={원본_comment_id} \
  -f body="{sq-tone-writer 로 작성한 본문}"
```

## 3. #816 과 머지 순서 (v1.8 Step 4-6-0)

사용자 요청의 "둘 다 빨리 머지"에 대한 판단이다.

- #815 는 포트 인터페이스의 **시그니처를 바꾸는** PR 이고, #816 은 같은 `DoseRecordReader.java` 를 고친다. 두 PR 은 각자 단독으로는 컴파일되지만, 합치면 충돌하거나 컴파일이 깨질 수 있다. 예를 들어 #816 이 `findLatest(userId)` 를 호출하는 코드나 이 인터페이스의 새 구현체·Fake 를 추가했다면 #815 머지 후에 깨진다.
- 권장 순서: 먼저 준비된 쪽을 머지한다. 인터페이스를 바꾸는 #815 를 먼저 머지하는 편이 #816 이 새 시그니처 위에서 작업하게 되어 단순하다. #816 이 먼저 머지되면 #815 가 그 위에 dev 를 merge 하고 4-5-1 게이트를 다시 돈다.
- 나중에 머지되는 쪽은 **먼저 머지된 PR 이후의 dev 를 merge**(force push 금지)하고, **그 커밋에 대한 CI 가 끝난 뒤** 머지한다. 마지막 커밋이 CI 완료 전에 머지되면 머지 직후 dev 에서 `compileTestJava` 와 `test` 를 직접 돌려 확인한다.
- 충돌 위험을 미리 보려면 (읽기 전용):

```bash
gh pr diff 816 --name-only
gh pr view 816 --json headRefName,files,mergeable
git diff --name-only origin/dev...origin/{#816 브랜치}
```

- #816 은 다른 PR 이고 아직 올라오지도 않았다. 그 브랜치를 내가 수정하거나 코멘트를 달지 않는다 (범위 밖은 보고까지만). 필요하면 #816 작성자에게 보낼 안내 문안 초안만 제공한다: "#815 에서 `DoseRecordReader.findLatest` 시그니처가 `(Long userId, Instant asOf)` 로 바뀝니다. 머지 후 dev 를 합치고 `compileTestJava` 를 한 번 돌려 주세요."
- 머지 실행 자체는 요청되지 않았고 리뷰 승인과 CI 통과가 선행 조건이므로 내가 하지 않는다. 승인과 CI 가 갖춰지면 사용자가 머지한다.

## 4. PR 본문 확인 (제안만, 수정하지 않음)

`gh pr view 815 --json body` 로 본문을 읽어 다음을 본다.

- 저장소 템플릿이 있으면 본문 섹션이 이모지까지 템플릿과 같은지 본다. 이번 작업에서 본문을 다시 쓸 일은 없고, 쓴다면 섹션명을 문자 그대로 쓴다.
- 이번 변경은 "최신 기록" 조회 결과가 바뀌는 동작 변경(미래 기록 제외)이다. 본문에 "기존 동작 변경" 성격의 한 줄이 없으면 추가를 사용자에게 제안한다 (RR-14, git-pr 2-3). 요청 범위 밖이므로 승인 없이 `gh pr edit` 하지 않는다.

## 5. 종료 보고에 남길 항목

1. 수행: 커밋 1건(해시), 최신 dev 병합 컴파일 결과, push, CI 결과, 답글 1건.
2. **재발 방지 등록 판단 (v1.7)**: 이번 지적(미래 기록이 "최신"으로 잡힘)은 이미 `review-recurrence-guard.md` RR-14("최신을 조회할 때 미래 데이터를 거른다", 출처 #793)에 있는 유형이다. 따라서 "가드 추가 후보"가 아니라 **"규칙은 있으나 미적용"** 으로 표시한다. 규칙 추가가 아니라 게이트 강화가 필요하다. `review-lint.py` 후보: 시각 인자 없이 `findLatest*`/`findLast*` 류 메서드를 선언하는 경우를 "확인" 등급으로 표시하는 검사 (문자열로 잡히는 유형).
3. 환경 한계: "로컬 단독 컴파일 통과"만으로는 머지 후 dev 의 깨짐을 막지 못한다는 점은 이미 `git-pr` v0.5 와 이 스킬 v1.8 게이트에 있다. 이번에도 로컬 통과 보고가 게이트를 건너뛰게 만들 수 있었던 경우다.
4. 열린 위험: #816 과의 머지 순서. #813 내용은 위 확인 명령 결과로 갱신한다.
5. 사용자 확인이 필요한 것: (a) 커밋 type, (b) `asOf` 이름이 lint 확인 항목에 걸렸을 때 처리, (c) PR 본문에 "기존 동작 변경" 한 줄 추가 여부, (d) 충돌 발생 시 해소 방향.

## 6. 자기 검증 체크리스트 (v1.8 기준)

| # | 항목 | 결과 |
|---|------|------|
| 1 | 브랜치 검증 | 보호 브랜치 아님, PR head 일치 확인 |
| 2 | 코멘트 전수 수집 | 이슈 코멘트·라인 코멘트·리뷰 모두 수집 |
| 3 | CodeRabbit 식별 | `user.login` 으로 식별, 0건 확인 |
| 4 | 수정 계획 문서 | `docs/pr-modification-plan-815.md` 작성 (커밋 제외) |
| 5 | 순서 준수 | 수정 → `/git-commit` → 게이트 → push → 답글 |
| 6 | push 확인 | 답글 전 push 완료 |
| 7 | 규칙 준수 | RR-2, RR-12, RR-14 대조 |
| 8 | 체크박스 | 완료 항목 갱신 |
| 9 | 답글 톤 | `sq-tone-writer` 경유, A-1 |
| 10 | 확인 vs 가정 분리 | 1절과 답글 조건부 문장으로 분리 |
| 11 | PR 컨텍스트 | 머지 정책·CI·중복 코멘트 확인 |
| 12 | 봇 vs 사람 분기 근거 | 수정 계획 문서에 기록 |
| 13 | 같은 유형 스윕 | 4-c |
| 14 | review-lint 0건 | 4-d |
| 15 | 재발 방지 등록 판단 | "규칙은 있으나 미적용" |
| 16 | 최신 dev 병합 컴파일 | 4-5-1, 로컬 단독 통과로 대체하지 않음 |
