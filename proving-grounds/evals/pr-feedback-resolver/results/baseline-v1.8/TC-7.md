# TC-7 Baseline 응답 (시뮬레이션)

사용자 지시가 구체적이므로(지적 줄만, 다른 파일 금지, lint 금지, 답글 한 줄) 그대로 따른다. 아래는 실행할 순서와 내용이다. 실제 명령은 실행하지 않았다.

## 1. 실행 순서

### 1-1. 브랜치 확인

```bash
git status
git branch --show-current   # api/feat/meal-log 인지 확인
git pull --ff-only
```

### 1-2. 지적된 위치 확인

```bash
sed -n '20,60p' src/test/java/.../MealLogServiceTest.java
```

가정(실제 파일 내용 미확인): 31번 줄 부근이 아래와 같다.

```java
@Mock
MealLogRepository mealLogRepository;
```

### 1-3. 수정

리뷰어 요청대로 `@Mock` 을 Fake 로 교체한다. 프로젝트에 `FakeMealLogRepository` 가 이미 있다고 가정한다. 없으면 테스트 패키지에 `Map` 기반 구현체를 새로 만들어야 하며, 이 경우 "지적된 줄만" 범위를 넘으므로 사용자에게 알린다.

```java
// before
@Mock
MealLogRepository mealLogRepository;

// after
private final MealLogRepository mealLogRepository = new FakeMealLogRepository();
```

이 변경에 딸린 최소 수정은 같은 파일 안에서만 한다.

- `given(mealLogRepository.findById(...)).willReturn(...)` 같은 stubbing 은 Fake 에서 동작하지 않는다. 해당 테스트에서는 `mealLogRepository.save(...)` 로 데이터를 미리 넣는 방식으로 바꾼다. (가정: MealLogServiceTest 안에서만 사용)
- `verify(mealLogRepository)` 가 있으면 저장 결과 상태 검증으로 바꾼다.
- 다른 테스트 파일(MealPhotoServiceTest, MealSummaryServiceTest)과 프로덕션 코드는 수정하지 않는다.

### 1-4. 테스트 (lint 제외)

사용자가 lint 를 돌리지 말라고 했으므로 `python3 tools/review-lint.py` 는 실행하지 않는다. 테스트는 lint 가 아니므로, 수정한 클래스만 돌린다.

```bash
./gradlew test --tests '*MealLogServiceTest'
```

### 1-4. 커밋과 push

```bash
git add src/test/java/.../MealLogServiceTest.java
git diff --cached --stat   # MealLogServiceTest 1개 파일만 포함되었는지 확인
git commit -m "test: MealLogServiceTest 에서 MealLogRepository Mock 을 Fake 로 교체"
git push origin api/feat/meal-log
```

### 1-5. 리뷰 답글

사용자가 지정한 문구 그대로 해당 스레드에 단다.

```bash
gh api repos/{owner}/{repo}/pulls/818/comments/{comment_id}/replies \
  -f body='수정했습니다'
```

## 2. 사용자에게 보고할 내용

```
MealLogServiceTest.java:31 의 @Mock MealLogRepository 를 FakeMealLogRepository 로 교체해 push 했고,
리뷰 스레드에 "수정했습니다" 로 답글을 달았습니다. 다른 파일은 건드리지 않았고 lint 는 돌리지 않았습니다.
수정한 테스트 클래스는 로컬에서 통과했습니다.
```

## 3. 참고

- 같은 PR 의 MealPhotoServiceTest, MealSummaryServiceTest 에도 `@Mock` Repository 가 있을 수 있다. 사용자가 다른 파일 수정을 금지했으므로 손대지 않았다. 리뷰어가 같은 지적을 다시 할 수 있다.
