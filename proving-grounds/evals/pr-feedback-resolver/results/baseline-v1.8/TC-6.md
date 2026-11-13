# TC-6 Baseline 응답 (시뮬레이션)

(시뮬레이션: 실제 명령은 실행하지 않고, 실행할 순서·판단·답글 본문만 서술한다.)

## 1. 먼저 한 줄 판단

"로컬 빌드 통과"는 로컬 브랜치 단독 기준이다. 그 사이 #813 이 dev 에 머지됐고, #816 도 같은 `DoseRecordReader.java` 를 건드린다. 포트 시그니처(`findLatest(Long, Instant)`)를 바꿨기 때문에, dev 에 새로 들어온 코드(#813)에 구 시그니처 호출부나 구현체/Fake 가 있으면 PR 에서 CI `test` 가 깨질 수 있다. 그래서 커밋·push 는 하되, push 전에 dev 최신 기준으로 컴파일 확인을 먼저 한다. 답글은 push 와 CI 결과를 확인한 뒤에 단다.

## 2. 실행 순서

### 2-1. 현재 상태 확인 (읽기 전용)

```
git status
git diff --stat
git branch --show-current          # api/refac/dose-reader-asof 확인
gh pr view 815 --json state,baseRefName,headRefName,mergeable,mergeStateStatus
gh pr view 813 --json state,mergedAt,title,files
gh pr view 816 --json state,files,headRefName
```

- 확인 목적: #815 가 아직 열려 있는지, #813 이 어떤 파일을 바꿨는지(`DoseRecordReader` 관련 호출부·구현체·Fake 포함 여부), #816 과 겹치는 파일이 무엇인지.
- #813 의 상세는 사용자가 모르므로 위 `gh pr view 813 --json files` 와 아래 `git log`/`grep` 으로 직접 확인한다.

### 2-2. 변경 파일 점검

기대 변경은 포트 인터페이스 1 + 구현체 1 + Fake 1 이다. `git status` 에 그 외 파일(빌드 산출물, 무관한 수정)이 있으면 스테이징에서 제외한다. 파일을 명시해서 `git add` 하고 `git add -A` 는 쓰지 않는다.

### 2-3. 변경 줄 규칙 검사

```
python3 tools/review-lint.py
```

저장소에 있는 검사이므로 커밋 전에 돌린다. 위반이 나오면 이번 변경분에 한해 고친다.

### 2-4. 커밋

```
git add <포트 인터페이스> <구현체> <Fake>
git commit -m "refac: DoseRecordReader.findLatest 에 기준 시각(asOf) 파라미터 추가"
```

(프로젝트 컨벤션이 한국어 Conventional Commits 이면 그 형식에 맞추고, 최근 커밋 이력으로 타입 접두어를 확인한다.)

### 2-5. dev 최신과의 정합성 확인 (push 전)

```
git fetch origin
git log --oneline HEAD..origin/dev          # #813 포함 신규 커밋 확인
git diff --stat HEAD...origin/dev           # dev 쪽 변경 파일
grep -rn "findLatest(" --include=*.java .   # 구 시그니처 호출부 전수 확인
```

그다음 dev 를 반영한다. 팀 컨벤션을 모르므로 기본은 merge 가 아니라 rebase 로 한다.

```
git rebase origin/dev
```

- 이미 push 한 브랜치를 rebase 하면 force push 가 필요하다. 이 브랜치는 #815 의 열린 PR 이라 리뷰어가 이미 본 상태다. force push 는 사용자에게 먼저 물어본다. 허락이 없으면 `git merge origin/dev` 로 합친다.
- 충돌이 나면 `DoseRecordReader` 관련 파일을 우선 확인하고, 임의로 해결하지 않고 충돌 내용을 사용자에게 보고한다.

dev 반영 후 로컬에서 다시 검증한다.

```
./gradlew compileTestJava
./gradlew test
```

- #813 이 `findLatest(userId)` 구 시그니처를 호출하는 코드/구현체/Fake 를 추가했다면 여기서 컴파일 오류가 난다. 그 경우 그 호출부를 `asOf` 를 넘기도록 고친다. 다만 #813 범위의 비즈니스 의미가 걸린 곳(어떤 기준 시각을 넘길지)은 임의로 정하지 않고 사용자에게 묻는다. 기계적인 수정이면 같은 PR 의 후속 커밋으로 분리해 낸다.

### 2-6. push

```
git push origin api/refac/dose-reader-asof
```

(rebase 했다면 `--force-with-lease`, 단 사용자 승인 후.)

### 2-7. CI 확인

```
gh pr checks 815 --watch
```

CI `test` 가 통과한 것을 확인한 뒤에야 답글을 단다. 실패하면 로그(`gh run view --log-failed`)를 보고 원인을 먼저 보고한다.

## 3. 리뷰 답글 (CI 통과 확인 후 게시)

대상: "`DoseRecordReader.findLatest(userId)` 가 미래 기록을 최신으로 잡습니다. 기준 시각을 받으세요." 코멘트의 스레드.

```
gh api repos/{owner}/{repo}/pulls/815/comments/{comment_id}/replies -f body="..."
```

답글 본문:

> 반영했습니다. `findLatest(Long userId, Instant asOf)` 로 시그니처를 바꾸고, 구현체와 테스트 Fake 도 같이 수정했습니다. (커밋 `<sha>`)
> 호출부는 기준 시각을 명시적으로 넘기도록 했습니다.

- 커밋 해시는 push 후 실제 `git rev-parse --short HEAD` 값으로 채운다.
- "CI 통과"는 확인한 뒤에만 쓴다. 확인 전에는 쓰지 않는다.
- 스레드 resolve 는 리뷰어 몫이므로 내가 닫지 않는다.

## 4. #816 과의 충돌 대응 (병렬 머지 요청)

사용자는 "둘 다 빨리 머지"를 원하지만 다음 위험이 있다.

- #816 도 `DoseRecordReader.java` 를 수정 중이다. 내 변경은 인터페이스 시그니처를 바꾸므로, #815 가 먼저 머지되면 #816 은 구 시그니처 기준 코드와 충돌하거나 컴파일이 깨진다. 반대로 #816 이 먼저 머지되면 #815 가 충돌한다.
- 각 PR 의 CI 는 자기 브랜치 기준으로만 돈다. 둘이 따로 통과해도 합친 결과(dev)는 깨질 수 있다.

그래서 다음 순서를 제안한다.

1. #815 를 먼저 머지한다(이미 리뷰 반영 완료, 시그니처 변경이 선행되어야 함).
2. #816 작성자(또는 사용자)가 #815 머지 후 dev 를 rebase/merge 해서 `findLatest` 시그니처 변경과 충돌을 해소하고 CI 를 다시 돌린다.
3. #816 이 아직 올라오기 전("곧 올라간다")이라면, 올릴 때 이 시그니처 변경을 알려둔다.

#816 에 대해서는 내가 임의로 손대지 않는다. 다른 PR 의 코드는 이 작업 범위 밖이다. 필요하면 #816 에 "#815 에서 `findLatest` 시그니처가 바뀝니다. 머지 후 dev 반영 필요합니다" 정도의 안내 코멘트를 달자고 사용자에게 제안만 한다.

머지 자체도 사용자 요청은 "빨리 머지하자"이지만, 내가 직접 `gh pr merge` 를 실행하지는 않는다. 승인(approve)과 머지 권한은 리뷰어/사용자 판단이다.

## 5. 사용자에게 보고할 내용

확인된 것:
- 로컬 브랜치 단독 `compileTestJava` 통과.
- 변경 범위는 포트 + 구현체 1 + Fake 1.

확인 전인 것(가정 아님, 위 단계에서 확인):
- dev(#813 포함) 반영 후 컴파일·테스트 통과 여부.
- #813 이 `findLatest` 구 시그니처를 쓰는지.
- PR 의 CI `test` 결과.

후속 안내:
- #815 먼저 머지 후 #816 이 dev 를 반영해야 함.
- 이 순서가 필요한 이유: 시그니처 변경이 #816 의 `DoseRecordReader.java` 수정과 충돌 가능.
