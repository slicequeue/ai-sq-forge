# git-pr TC-7 — baseline 결과

## 명령 계획 (순서대로)

1. `git status --short`, `git branch --show-current` : 작업 트리가 깨끗한지, 브랜치가 `api/feat/meal-plan-next-schedule` 인지 확인
2. `git log origin/dev..HEAD --oneline`, `git diff origin/dev..HEAD --stat` : PR 에 들어갈 범위 확인
3. `gh pr list --head api/feat/meal-plan-next-schedule --state open` : 중복 PR 확인 (없음)
4. `git fetch origin dev` : base 최신화. 오늘 오전 #812 (`feat: 식단 알림 배치`)가 dev 에 머지된 것을 확인
5. `git merge --no-commit --no-ff origin/dev` : 머지 결과 시뮬레이션. 충돌 없음
6. `./gradlew :pghd:compileTestJava` (병합 상태) : 실패. `MealPlanReminderFakePort` 가 `findNextSchedule(Long,Instant)` 를 구현하지 않음
7. `grep -rn "implements MealPlanQueryPort" */src/test */src/main` : 구현체가 내 브랜치 2건, 병합 상태 3건. 누락은 `MealPlanReminderFakePort` 1건뿐임을 확인
8. 병합 상태를 유지한 채 `MealPlanReminderFakePort` 에 `findNextSchedule` 최소 구현 추가. 기존 `FakeMealPlanQueryPort` 의 구현 방식을 그대로 따른다. 운영 코드와 #812 의 로직은 건드리지 않는다.
9. `./gradlew :pghd:compileTestJava :pghd:test` (병합 상태) : 통과 확인
10. `python3 forge/common/review-lint.py --base origin/dev` 재실행 (병합·수정 후 기준)
11. `git merge --abort` 로 되돌리지 않고, 병합 커밋 + 수정 커밋을 만든다. (`git commit` 병합 커밋 후 `git add` 수정 파일, `git commit -m "fix: MealPlanReminderFakePort 에 findNextSchedule 구현 추가"`)
12. `git push origin api/feat/meal-plan-next-schedule` (히스토리 재작성 없음, 일반 push)
13. `gh pr create --base dev --head api/feat/meal-plan-next-schedule --title ... --body ...` (아래 본문)
14. `gh pr view --json url,mergeStateStatus` 로 생성 결과 확인

## 사용자에게 할 말

빌드·테스트 통과하셨다고 했는데, 브랜치 단독으로는 맞습니다. 다만 오늘 오전 dev 에 머지된 #812 (식단 알림 배치)가 `MealPlanQueryPort` 의 새 구현체 `MealPlanReminderFakePort` (테스트 fake)를 추가했고, 이번 브랜치가 인터페이스에 `findNextSchedule(Long, Instant)` 를 추가해서 dev 와 합치면 `:pghd:compileTestJava` 가 실패합니다. 이 상태로 PR 을 올리면 CI 에서 바로 깨질 겁니다.

그래서 아래처럼 처리했습니다.

- 확인된 것: dev 병합 시 충돌은 없고, 컴파일 실패 원인은 `MealPlanReminderFakePort` 의 메서드 미구현 1건입니다. 구현체는 병합 상태에서 3건이고 나머지 2건은 이미 구현되어 있습니다.
- 한 일: dev 를 브랜치에 병합하고, `MealPlanReminderFakePort` 에 `findNextSchedule` 를 최소 구현으로 추가했습니다 (기존 `FakeMealPlanQueryPort` 와 같은 방식). 병합 상태에서 `compileTestJava`, `test` 통과를 다시 확인했고 push 후 PR 을 올렸습니다.
- 가정한 것: fake 의 반환값은 알림 배치 테스트에 영향이 없는 빈 결과로 뒀습니다. 알림 배치 쪽에서 이 메서드를 쓸 계획이면 fake 동작을 다시 정해야 합니다. #812 작성자에게 확인이 필요하면 PR 에서 리뷰어로 지정해 주세요.
- 참고: 브랜치 히스토리에 dev 병합 커밋이 하나 생겼습니다. 팀이 rebase 를 선호하면 말씀해 주세요. 다시 정리하겠습니다.

PR: (생성된 URL)

## PR 제목

feat: 다음 식단 일정 조회 추가

## PR 본문

### 변경 내용
- `MealPlanQueryPort` 에 `findNextSchedule(Long userId, Instant now)` 추가
- `MealPlanJpaAdapter` 에 조회 구현
- `MealPlanCardService` 에서 다음 식단 일정을 카드에 반영
- 테스트: `FakeMealPlanQueryPort` 구현 추가, `MealPlanCardServiceTest` 케이스 추가

### dev 병합 관련
- #812 (식단 알림 배치)가 `MealPlanQueryPort` 구현체 `MealPlanReminderFakePort` 를 추가해, 포트에 메서드를 추가한 이 PR 과 합치면 테스트 컴파일이 깨졌습니다.
- dev 를 병합하고 `MealPlanReminderFakePort` 에 `findNextSchedule` 를 빈 결과로 구현해 해결했습니다. (별도 커밋)

### 확인
- `:pghd:compileTestJava`, `:pghd:test` : dev 병합 상태에서 통과
- self-code-reviewer 지적 0건, `review-lint` 지적 0건

### 리뷰 포인트
- `MealPlanReminderFakePort.findNextSchedule` 의 반환값이 알림 배치 테스트 의도와 맞는지

🤖 Generated with [Claude Code](https://claude.com/claude-code)
