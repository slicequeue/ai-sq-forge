# git-pr TC-7 — with-skill(v0.5) 결과

## 0. 판단 요약

- 사용자는 "내 쪽 빌드랑 테스트 다 통과했다"고 했다. 그러나 CI 는 PR 을 최신 dev 와 합친 상태로 빌드한다. 스킬 v0.5 게이트에 따라 이 말만 믿고 PR 을 올리지 않고, 최신 dev 병합 상태에서 `compileTestJava` 를 확인했다.
- 확인 결과 병합 상태에서 컴파일이 실패한다. 오늘 오전 머지된 #812 가 `MealPlanQueryPort` 의 새 구현체 `MealPlanReminderFakePort` 를 추가했는데, 내가 인터페이스에 `findNextSchedule(Long, Instant)` 를 추가했기 때문이다.
- 그대로 PR 을 올리면 PR 첫 CI 부터 빨갛게 되고, 머지하면 #803 과 같은 dev 테스트 컴파일 파손이 재현된다. 그래서 PR 생성 전에 구현체를 고친다.
- 확인된 것 / 가정한 것을 아래 2번에서 분리했다.

## 1. 실제로 실행할 명령 계획 (순서대로)

| 순서 | 명령 | 목적 | 결과 처리 |
|---|---|---|---|
| 1 | `git status`, `git branch --show-current`, `git log origin/dev..HEAD --oneline`, `git diff origin/dev..HEAD --stat` | 변경 범위 파악 | 커밋 1건, 파일 5개 확인 |
| 2 | `gh pr list --head api/feat/meal-plan-next-schedule --state open` | 기존 PR 확인 | 없음 -> 신규 생성 경로 |
| 3 | `ls .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md 2>/dev/null` | 저장소 템플릿 확인 (2-0) | 없음 -> 표준 구성 사용 |
| 4 | `python3 forge/common/review-lint.py --base origin/dev` | 품질 게이트 | 지적 0건 -> 통과 |
| 5 | self-code-reviewer | 품질 게이트 | 이미 실행 완료, 지적 0건 -> 재실행 불필요 (단 8번 뒤 변경분 있으면 6-3 참조) |
| 6 | `git fetch origin dev` | 최신 dev 확보 | #812 머지 확인 |
| 7 | `git merge --no-commit --no-ff origin/dev` -> `./gradlew :pghd:compileTestJava` | 최신 dev 병합 컴파일 게이트 (v0.5) | 충돌 없음 / 컴파일 실패 -> 게이트 불통과, PR 생성 중단 |
| 8 | `grep -rn "implements MealPlanQueryPort" */src/test */src/main` (병합 상태 기준) | 바꾼 인터페이스의 구현체 전수 확인 | 3건 확인: `MealPlanJpaAdapter`, `FakeMealPlanQueryPort`, `MealPlanReminderFakePort`(신규, 미구현) |
| 9 | `git merge --abort` | 검증용 병합 원복 | 작업 트리 깨끗한 상태로 복귀 |

게이트 불통과이므로 여기서 PR 생성(`gh pr create`)으로 넘어가지 않고 아래 수정 단계를 먼저 한다.

### 수정 단계 (게이트 통과를 위해)

| 순서 | 명령 / 작업 | 비고 |
|---|---|---|
| 10 | `Read` `FakeMealPlanQueryPort.java`, `MealPlanReminderFakePort.java`, `MealPlanQueryPort.java` | 반환 타입과 Fake 관례를 실제 파일에서 읽는다. 시뮬레이션 정보에 반환 타입이 없으므로 추측하지 않는다 |
| 11 | `git merge origin/dev` (실제 병합, 충돌 없음 확인됨) | 기본은 merge 방식. 이미 원격에 push 된 브랜치라 force push 가 필요 없다. 팀 관례가 rebase 면 알려 달라고 사용자에게 한 줄 안내 |
| 12 | `MealPlanReminderFakePort` 에 `findNextSchedule(Long, Instant)` 구현 추가 | 기존 `FakeMealPlanQueryPort` 의 구현 방식을 따른다. #812 의 알림 배치 테스트 의도를 바꾸지 않는 최소 구현(기존 테스트가 이 메서드를 쓰지 않으므로 빈 결과 계열)만 넣는다 |
| 13 | `./gradlew :pghd:compileTestJava` -> `./gradlew :pghd:test` (병합 상태) | 통과해야 다음으로 진행. 실패하면 PR 을 만들지 않고 원인을 사용자에게 보고 |
| 14 | `grep -rn "implements MealPlanQueryPort" */src/test */src/main` 재실행 | 3건 모두 `findNextSchedule` 구현 확인 |
| 15 | `git-commit` 스킬로 커밋: `fix: 알림 배치 Fake 포트에 다음 식단 일정 조회 구현 추가` | 한국어 Conventional Commits, AI 공동작성자 표기 없음 |
| 16 | `python3 forge/common/review-lint.py --base origin/dev` 재실행, 추가 커밋이 테스트 Fake 1개뿐이므로 self-code-reviewer 는 해당 파일만 재확인 | diff 가 바뀌었으므로 게이트를 다시 통과시킨다 |
| 17 | `git push origin HEAD` | 일반 push (force 아님) |
| 18 | `git diff origin/dev..HEAD --stat` 재측정 후 `gh pr create --base dev --head api/feat/meal-plan-next-schedule --title "feat: 다음 식단 일정 조회 추가" --body <아래 4번>` | 신규 생성. 파일 수와 +/- 는 재측정값으로 채운다 |
| 19 | PR URL 출력, "신규 생성" 한 줄 | |

13~16 중 하나라도 실패하면 18 은 실행하지 않는다.

## 2. 확인된 것 vs 가정한 것

| 구분 | 내용 |
|---|---|
| 확인된 것 | 내 브랜치 단독으로는 `compileTestJava`, `test` 통과 (사용자 말 + 시뮬레이션 상황) |
| 확인된 것 | 최신 dev 병합 상태에서는 `MealPlanReminderFakePort.java:12` 컴파일 실패 |
| 확인된 것 | 원인은 #812 가 추가한 구현체이며, 내 diff 에는 보이지 않는다 (내 브랜치 구현체 2건, 병합 후 3건) |
| 확인된 것 | 병합 충돌은 없고 review-lint, self-code-reviewer 는 지적 0건, 기존 PR/템플릿 없음 |
| 가정한 것 | `findNextSchedule` 의 반환 타입과 `FakeMealPlanQueryPort` 구현 방식은 파일을 읽기 전이라 모름. 10번에서 확인한다 |
| 가정한 것 | #812 의 기존 테스트가 새 메서드를 호출하지 않는다는 점. 13번 `:pghd:test` 로 검증한다 (재평가 트리거: 테스트 실패 시 Fake 가 빈 결과로 충분한지 재검토) |
| 가정한 것 | 병합 방식(merge) 이 팀 관례에 맞다는 점. 사용자가 rebase 를 원하면 전환 |

## 3. 사용자에게 할 말

> 브랜치 단독으로는 빌드와 테스트가 통과하는 것 맞습니다. 다만 CI 는 최신 dev 와 합친 상태로 빌드하는데, 오늘 오전 머지된 #812(식단 알림 배치)가 `MealPlanQueryPort` 의 테스트 Fake(`MealPlanReminderFakePort`)를 새로 추가했습니다. 이 Fake 에 이번에 추가한 `findNextSchedule(Long, Instant)` 구현이 없어서, 병합 상태에서는 `:pghd:compileTestJava` 가 실패합니다. 그대로 올리면 PR 첫 CI 가 깨지고, 머지하면 dev 테스트 컴파일이 깨집니다.
>
> 그래서 PR 을 만들기 전에 최신 dev 를 브랜치에 병합(충돌 없음)하고, `MealPlanReminderFakePort` 에 `findNextSchedule` 구현을 추가하는 커밋을 하나 더 얹겠습니다. force push 는 필요 없습니다. 병합 상태에서 컴파일, 테스트, review-lint 를 다시 통과시킨 뒤에 PR 을 올리고, PR 본문 "리뷰 포인트"에 #812 파일을 건드린 사실을 적어 두겠습니다.
>
> 팀에서 dev 를 rebase 로 반영하는 관례라면 말씀해 주세요. 그에 맞춰 바꾸겠습니다. 머지 직전에 다른 PR 이 이 인터페이스의 구현체를 또 추가하지 않았는지 한 번 더 grep 하시길 권합니다.

## 4. PR 본문 (13번 이후 전부 통과했을 때만 생성)

제목: `feat: 다음 식단 일정 조회 추가`

- 저장소 PR 템플릿 없음 -> 표준 구성 사용
- 아래 Changes 의 파일 수와 +/- 는 수정 커밋 포함 재측정값으로 확정한다. 현재 알려진 5개 파일 합계는 +91 / -3 이고, 6번째 파일(Fake)의 증가분이 더해진다
- 파일별 설명은 18번 직전에 실제 diff 를 읽어 문구를 확정한다. 아래는 stat 수준에서 쓸 수 있는 내용이다

````markdown
## Why need this PR❓

식단 카드가 사용자의 **다음 식단 일정**을 조회할 수단이 없어, 일정 조회 포트와 구현을 추가하고 카드 서비스에서 쓰도록 연결했다.

## Changes ✌️

**파일 6개, +<재측정> / -3 lines** (pghd 모듈 식단 카드 조회 경로)

| 파일 | 변경 |
|---|---|
| `MealPlanQueryPort.java` | 다음 일정 조회 메서드 `findNextSchedule(사용자, 기준 시각)` 추가 |
| `MealPlanJpaAdapter.java` | 위 메서드의 저장소 조회 구현 |
| `MealPlanCardService.java` | 카드 구성 시 다음 일정 조회를 사용하도록 변경 |
| `FakeMealPlanQueryPort.java` (test) | 테스트용 대역에 다음 일정 조회 추가 |
| `MealPlanReminderFakePort.java` (test) | #812 에서 추가된 대역이 새 메서드를 구현하도록 보완 (최신 dev 병합 후 컴파일 오류 해소) |
| `MealPlanCardServiceTest.java` | 다음 일정 조회 동작 테스트 추가 |

## 리뷰 포인트

- 다른 PR 파일 수정: #812(식단 알림 배치)가 추가한 테스트 대역 `MealPlanReminderFakePort` 에 새 메서드 구현을 더했다. 인터페이스에 메서드가 늘어 구현체가 반드시 구현해야 해서 불가피한 변경이며, 알림 배치 로직은 건드리지 않았다
- 머지 전 확인: 같은 인터페이스를 구현하는 대역이 다른 PR 로 추가되면 다시 컴파일이 깨질 수 있어, 머지 직전 최신 dev 기준으로 구현체를 한 번 더 확인한다

---

📘 **상세 분석/측정 결과/근거 문서는 Notion으로 별도 공유 예정**

## Test list 📝

- [x] 브랜치 단독 `./gradlew :pghd:compileTestJava`, `:pghd:test` 통과
- [x] 최신 dev(#812 포함) 병합 상태 `./gradlew :pghd:compileTestJava`, `:pghd:test` 통과 (13번 통과 후 체크)
- [x] `MealPlanQueryPort` 구현체 3건 모두 새 메서드 구현 확인
- [x] review-lint 지적 0건, self-code-reviewer 지적 0건
````

본문 설명:
- 기존 API 응답, 검증, 에러가 바뀌는지는 `MealPlanCardService` diff(-3)를 읽어 판단한다. 바뀌면 "기존 동작 변경" 섹션을 추가하고, 지금은 stat 만으로 판단할 수 없어 넣지 않았다.
- 측정 결과, 배포, 후속 작업 섹션은 해당 사항이 없어 생략했다.
- 본문은 약 40줄, 코드 스니펫 없음, `docs/` 링크 없음.
- 의도적으로 "Generated with Claude Code" 같은 AI 표기 줄을 넣지 않았다. 스킬 가드레일이 AI 공동작성자 표기를 금지하기 때문이다.

## 5. 자기 검증 체크리스트 점검 (스킬 v0.5, 17항목)

| # | 항목 | 결과 |
|---|---|---|
| 1 | 저장소 템플릿 확인 | 통과. 템플릿 없음을 확인했고 표준 섹션명(이모지 포함)을 그대로 사용 |
| 2 | 분량 100~200줄 이내, 스니펫 없음 | 통과 (약 40줄, 이내 범위 하한 미만이나 내용 대비 적정. 줄이 부족한 것이 아니라 변경이 작음) |
| 3 | Why 1~2문장 | 통과 |
| 4 | Changes 파일별 표 | 통과 (1파일 1줄) |
| 5 | 측정 결과 | 해당 없음, 생략 |
| 6 | 배포 | 해당 없음, 생략 |
| 7 | 후속 작업 | 해당 없음, 생략 |
| 8 | Test list | 통과 (항상 포함) |
| 9 | 사람 친화 표현 | 통과. 상대 시점 단독 표현 없음 |
| 10 | `docs/` 링크 없음 | 통과 |
| 11 | target branch `dev` | 통과 |
| 12 | AI 공동작성자 표기 없음 | 통과 |
| 13 | 기존 PR 없음 -> 신규 생성 | 통과 |
| 14 | review-lint 0건 + self-code-reviewer | 통과. 단 수정 커밋 이후 16번에서 재실행하여 재확인해야 함 |
| 15 | 기존 동작 변경 섹션 | 보류. `MealPlanCardService` diff 를 읽고 응답, 검증, 에러 변화 여부로 확정 (변화 있으면 섹션 추가) |
| 16 | 리뷰 포인트 | 통과. 다른 PR 파일 수정 사유, 머지 직전 재확인 항목 기재 |
| 17 | 최신 dev 병합 컴파일 + 구현체 grep | 최초 시도는 실패. 수정 단계 13, 14번에서 통과를 확인한 뒤에만 PR 생성. 통과 확인 전에는 체크하지 않는다 |

결론: 17번이 미통과 상태이므로 지금 시점에는 PR 을 생성하지 않고 수정 단계를 먼저 진행한다. 수정 후 13~16번이 모두 통과하면 4번 본문으로 PR 을 생성한다.
