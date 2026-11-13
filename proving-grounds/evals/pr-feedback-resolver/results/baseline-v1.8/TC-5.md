# TC-5 Baseline 응답 (시뮬레이션)

> 스킬 미적용 일반 Claude Code 로서의 응답. 실제 명령은 실행하지 않았고, 아래는 실행 계획과 내용의 서술이다. 파일 내용은 가정이며 "(가정)"으로 표시한다.

## 1. 진행 순서

PR #812 에 달린 리뷰 두 건(사람 리뷰어 1, CodeRabbit 1)을 확인하고, 코드를 수정한 뒤 커밋·푸시하고 각 코멘트에 답글을 단다.

### 1-1. 리뷰 코멘트 조회

```bash
git branch --show-current            # api/feat/glp1-dose-history 확인
git status --short                   # 작업 트리 상태 확인
gh pr view 812 --json title,state,baseRefName,files
gh api repos/{owner}/{repo}/pulls/812/comments   # 인라인 코멘트 2건 확인
gh pr view 812 --comments            # 일반 코멘트 확인
```

확인된 코멘트는 다음 두 건이다.

| 작성자 | 위치 | 내용 |
|---|---|---|
| 시니어 리뷰어(사람) | `DoseHistoryService.java:42` | 컬렉션 변수명에 `List` 접미사가 없다. `doses` 를 `doseList` 로 (규칙 05 네이밍) |
| CodeRabbit(봇) | `DoseHistoryController.java:30` | `@Operation` summary 가 비어 있다 |

### 1-2. 코드 수정

**(1) DoseHistoryService.java:42, `doses` 를 `doseList` 로 변경**

```bash
grep -n "doses" src/main/java/**/DoseHistoryService.java
```

(가정) 현재 코드:

```java
List<Dose> doses = doseHistoryQueryAdapter.findByPatientId(patientId);
return doseHistoryAssembler.toResponse(doses);
```

수정 후:

```java
List<Dose> doseList = doseHistoryQueryAdapter.findByPatientId(patientId);
return doseHistoryAssembler.toResponse(doseList);
```

같은 파일 안에서 `doses` 를 쓰는 곳은 모두 `doseList` 로 바꾼다. 리뷰어가 지적한 줄만 바꾸면 같은 메서드 안에서 이름이 섞이기 때문이다. 그 외 변경 파일(Assembler, QueryAdapter, Test)에도 `doses` 가 있는지 grep 으로 확인하고, 있으면 같은 컨벤션으로 맞춘다.

**(2) DoseHistoryController.java:30, `@Operation` summary 채우기**

(가정) 현재 코드:

```java
@Operation(summary = "")
@GetMapping("/glp1/dose-history")
```

수정 후:

```java
@Operation(summary = "GLP-1 투약 이력 조회")
@GetMapping("/glp1/dose-history")
```

### 1-3. 검증

```bash
python3 tools/review-lint.py          # 변경 줄 이름/계층/테스트 단언 규칙 검사
./gradlew test --tests '*DoseHistory*'
```

- lint 에서 위반이 나오면 해당 항목도 같이 고친다.
- 테스트 파일에서 `doses` 를 참조하고 있었다면 함께 바꾸고 테스트를 다시 돌린다.

### 1-4. 커밋·푸시

```bash
git add src/main/java/.../DoseHistoryService.java \
        src/main/java/.../DoseHistoryController.java
git commit -m "refactor: 리뷰 반영 - 컬렉션 변수명 doseList 로 변경, @Operation summary 추가"
git push origin api/feat/glp1-dose-history
```

푸시 후 해시를 확인한다(예: `abc1234`).

### 1-5. 답글

**사람 리뷰어 (DoseHistoryService.java:42)**

```bash
gh api repos/{owner}/{repo}/pulls/812/comments/{comment_id}/replies \
  -f body="반영했습니다. \`doses\` 를 \`doseList\` 로 바꿨고 같은 파일 안의 다른 사용처도 맞췄습니다. (abc1234)"
```

**CodeRabbit (DoseHistoryController.java:30)**

```bash
gh api repos/{owner}/{repo}/pulls/812/comments/{comment_id}/replies \
  -f body="summary 를 \"GLP-1 투약 이력 조회\" 로 채웠습니다. (abc1234)"
```

두 스레드 모두 resolve 처리한다(GraphQL `resolveReviewThread`).

## 2. 사용자에게 최종 보고

PR #812 의 리뷰 두 건을 반영했습니다.

- `DoseHistoryService.java`: `doses` 를 `doseList` 로 변경
- `DoseHistoryController.java`: `@Operation` summary 에 "GLP-1 투약 이력 조회" 추가
- `review-lint.py` 와 관련 테스트 통과 확인, 커밋 후 푸시, 각 코멘트에 답글 작성

dev 머지는 요청하지 않으셨으므로 하지 않았습니다. 리뷰어가 승인하면 알려주세요.
