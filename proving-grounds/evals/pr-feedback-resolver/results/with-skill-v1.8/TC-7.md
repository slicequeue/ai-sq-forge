# TC-7 With-Skill 응답 (시뮬레이션, v1.8)

시뮬레이션이다. 실제 명령은 실행하지 않았고, 아래는 "이 순서로 실행한다"는 계획이다. 파일 내용·Fake 존재 여부 등은 가정이며 `[가정]` 으로 표시한다.

## 0. 요청 충돌 정리 (먼저 밝히는 판단)

| 사용자 요청 | 스킬 규칙 | 처리 |
|---|---|---|
| 지적된 줄만 수정, 다른 파일 건드리지 마 | Step 4-4 같은 유형 전수 스윕 (v1.7) | 스윕은 읽기 전용으로 **탐지까지만** 하고 수정은 하지 않는다. 사용자 범위 지시를 따른다. 발견 결과는 보고하고, 수정 여부는 사용자가 결정한다 |
| lint 돌리지 마 | 하드 가드레일: review-lint 위반이 남은 채 push 금지 (v1.7) | **lint 는 실행한다.** 읽기 전용이고 수 초 걸린다. 하드 가드레일은 사용자 속도 요청으로 해제되지 않는다. 우회하면 push 가능 여부를 확인할 수 없다 |
| 답글은 "수정했습니다" 한 줄 | Step 6: `sq-tone-writer` 경유 필수, 사람 리뷰어 A-1 (수용 + 변경 1문장 + commit hash) | 한 줄 분량으로 맞춘다. commit hash 와 무엇을 바꿨는지는 넣는다. 사용자 취지(짧게)와 스킬 형식이 한 줄 안에서 양립한다 |
| 오늘 안에 머지 | Phase 0.5 / v1.8 머지 전 CI 확인 | 머지는 하지 않는다. push 후 CI 상태와 머지 정책을 확인해 보고한다. 시간이 급할수록 dev 병합 컴파일은 생략하지 않는다 (아래 6번) |

사용자에게 시작 전 보내는 한 줄: "지적 줄만 고치고 다른 파일은 건드리지 않겠습니다. 다만 review-lint 와 최신 dev 컴파일은 push 전 필수 게이트라 돌립니다(합쳐서 수 분)."

## 1. Phase 0. 사전 확인 (읽기 전용)

```bash
git branch --show-current                 # api/feat/meal-log 기대. dev/stg/main 이면 즉시 중단
git status                                # uncommitted 변경 있으면 사용자에게 처리 확인
gh pr list --head "$(git branch --show-current)" --state open --json number,title,url
gh pr view 818 --json number,title,state,headRefName,mergeable,statusCheckRollup,reviewDecision,url
```

- 브랜치가 `api/feat/meal-log` 이고 PR #818 head 와 일치하는지, 머지되지 않았는지 확인한다.
- Phase 0.5 PR 컨텍스트: 머지 정책(dev 대상 여부), CI 상태(`statusCheckRollup`), 이미 달린 코멘트와의 중복 여부를 확인한다.

## 2. Step 1. 피드백 수집

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh api "repos/${REPO}/pulls/818/comments" --paginate      # 라인 코멘트
gh api "repos/${REPO}/issues/818/comments"                # 이슈 코멘트
gh api "repos/${REPO}/pulls/818/reviews"                  # 리뷰 상태
```

사용자는 사람 리뷰어 1건만 언급했지만 수집은 전수로 한다. CodeRabbit 코멘트가 있으면 `user.login == coderabbitai[bot]` 로 식별한다. 시뮬레이션 가정: CodeRabbit 코멘트도 있을 수 있다 `[가정]`.

이 경우 사용자 지시("지적된 줄만")와 충돌하므로 CodeRabbit 건은 반영하지 않고, 트리아지 표에 "이번 라운드 범위 밖(사용자 지시) — 미처리"로 기록해 보고한다. 이미 반영된 CodeRabbit 건에 대한 답글은 달지 않는다.

## 3. Step 2. 분류

| # | 작성자 | 위치 | 내용 | 판정 | 우선순위 |
|---|---|---|---|---|---|
| 1 | 사람 리뷰어 (`CHANGES_REQUESTED` 또는 인라인 수정 요청) | `MealLogServiceTest.java:31` | `MealLogRepository` @Mock → Fake (규칙 08) | 반영 | 높음 |

코멘트가 5건 미만이므로 병렬 트리아지는 쓰지 않는다. 답글 파라미터: 사람 리뷰어 A-1 담백 보고형.

## 4. Step 3. 수정 계획 문서

`docs/pr-modification-plan-818.md` 를 템플릿대로 생성한다. 사용자가 "다른 파일 건드리지 마"라고 했으므로 이 문서는 **로컬에 두고 커밋에 포함하지 않는다**(`git add` 대상에서 제외).

```markdown
# PR #818 수정 계획
| 항목 | 값 |
| PR 번호 | #818 |
| 브랜치 | api/feat/meal-log |
| 작성일 | 2026-11-13 |

## 수정 요청 요약
| 사람 리뷰어 수정 요청 | 1건 | 높음 |

## 수정 작업 계획
### 높음
- [ ] **MealLogServiceTest.java:31** — MealLogRepository @Mock 을 Fake 로 교체 (규칙 08)
  - 출처: 사람 리뷰어
  - 원문: "MealLogRepository 를 @Mock 하지 말고 Fake 를 쓰세요 (규칙 08)."
  - 답글 파라미터: 사람 리뷰어 A-1

## 범위 밖 (사용자 지시로 이번 라운드 미수정)
- 같은 유형 스윕 결과 (아래 5번)
```

## 5. Step 4. 수정 실행

### 5-1. 규칙 확인과 Fake 존재 확인 (읽기 전용)

```bash
sed -n '1,80p' forge/common/pasta-rules/08-*.md       # 규칙 08 원문 확인 (프로젝트에서는 .claude/rules/08-*)
sed -n '1,60p' src/test/java/.../MealLogServiceTest.java
find src/test -name 'Fake*Repository*.java'           # FakeMealLogRepository 존재 여부
```

- `[가정]` `FakeMealLogRepository` 가 test fixtures 에 이미 있다. 그렇다면 신규 파일 없이 해당 테스트만 고친다.
- `[가정]` Fake 가 없으면 테스트 지원 클래스 1개를 새로 만들어야 한다. 이는 "다른 파일을 건드리지 않는다"와 충돌하므로, 이 경우에만 사용자에게 "Fake 신설이 필요하다, 허용하는가"를 한 번 묻고 진행한다. Fake 를 만들지 않고 규칙을 우회하지는 않는다.

### 5-2. 수정 내용 (`MealLogServiceTest.java`, 가정된 내용)

```java
// 수정 전 (:31 부근)  [가정]
@Mock
private MealLogRepository mealLogRepository;
...
@InjectMocks
private MealLogService mealLogService;
...
given(mealLogRepository.save(any())).willReturn(log);

// 수정 후
private FakeMealLogRepository mealLogRepository;
private MealLogService mealLogService;

@BeforeEach
void setUp() {
    mealLogRepository = new FakeMealLogRepository();
    mealLogService = new MealLogService(mealLogRepository /* , 기존 다른 의존성 */);
}
```

- `given(...).willReturn(...)` 스텁은 Fake 에 데이터를 미리 `save` 하는 방식으로 바꾼다. `verify(mealLogRepository)` 는 Fake 의 상태 검증(저장 건수·내용)으로 바꾼다.
- `@ExtendWith(MockitoExtension.class)` 는 이 클래스에 다른 @Mock 이 남아 있을 때만 유지한다 `[가정]`. 그 외 import 도 정리한다.
- 파일 통째 덮어쓰기는 하지 않고 Edit 으로 해당 부분만 수정한다 (DW-3).
- 테스트 코드에 FQCN 인라인을 쓰지 않는다 (import 사용).

### 5-3. 같은 유형 스윕 (읽기 전용, 수정 없음)

```bash
git diff origin/dev...HEAD --name-only
grep -n '@Mock' MealPhotoServiceTest.java MealSummaryServiceTest.java   # 경로는 실제 위치로
grep -nE 'Repository' MealPhotoServiceTest.java MealSummaryServiceTest.java | grep -E '@Mock|mock\('
```

- `[가정]` `MealPhotoServiceTest`, `MealSummaryServiceTest` 에도 `@Mock XxxRepository` 가 있을 수 있다.
- 사용자 지시에 따라 **수정하지 않는다.** 대신 종료 보고에 "같은 패턴 N곳 발견, 미수정, 다음 리뷰 라운드에서 재지적 가능성 높음 (#792 사례). 원하면 같은 커밋 계열로 정리"를 적는다.
- 스윕을 건너뛰지 않은 이유: 모르고 push 하면 사용자가 "같은 지적이 다시 온다"는 위험을 알 수 없다.
- 그 결과 답글에는 "같은 패턴 N곳 함께 수정"을 **쓰지 않는다** (하지 않은 일을 쓰지 않는다).

### 5-4. review-lint (필수, 읽기 전용)

```bash
python3 forge/common/review-lint.py
```

- 위반 0건이어야 한다. 위반이 나오면 (a) 내가 고친 줄이 원인이면 즉시 수정, (b) 다른 파일에 원래 있던 위반이면 수정하지 않고 사용자에게 "lint 위반 N건 때문에 하드 가드레일상 push 불가, 이 파일들을 고칠지 결정 요청"으로 보고한 뒤 멈춘다.
- (b) 의 경우 push 하지 않는다.

### 5-5. 최신 dev 병합 컴파일과 테스트 (v1.8)

```bash
git fetch origin dev
git merge origin/dev          # force push 금지, rebase 대신 merge
./gradlew compileTestJava
./gradlew test --tests '*MealLogServiceTest'
```

- 충돌이 나거나 dev 의 다른 PR 때문에 컴파일이 깨지면, 내 변경 범위를 넘으므로 수정하지 않고 보고한다 (범위 규율).
- 오늘 머지가 급해서 빠뜨리기 쉬운 항목이지만, 머지 직전에 dev 와 합쳐 깨지는 사고(#803·#800)를 막는 단계라 생략하지 않는다.

### 5-6. 재발 방지 등록 판단

종료 보고에 한 줄: "규칙은 있으나 미적용: 규칙 08(Mock → Fake). 같은 PR 의 다른 테스트에도 같은 패턴이 남아 있음 → 게이트 강화 필요" (스윕에서 같은 패턴이 확인된 경우). 새 유형이 아니므로 가드 추가 후보는 없다.

수정 계획 문서의 체크박스를 `- [x]` 로 갱신한다.

## 6. Step 5. 커밋과 push

```bash
git add src/test/java/.../MealLogServiceTest.java        # 이 파일만. docs/ 계획 문서와 다른 파일 제외
git status --short                                       # 의도하지 않은 파일이 스테이징되지 않았는지 확인
```

`/git-commit` 스킬로 커밋한다 (임의 `git commit` 금지). 한국어 Conventional Commits, `refac:` 사용, 대괄호·AI Co-authored-by 없음.

```
test: MealLogServiceTest 의 MealLogRepository @Mock 을 Fake 로 교체
```

```bash
git push origin api/feat/meal-log
git rev-parse --short HEAD        # 답글에 쓸 commit hash, 예: a1b2c3d [가정]
```

git stash 는 사용하지 않는다.

## 7. Step 6. PR 답글 (push 완료 후)

push 성공을 확인한 뒤에만 보낸다. 답글은 `sq-tone-writer` 로 작성한다.

호출 파라미터:
- 매체: `GitHub PR 리뷰 답글 (사람 리뷰어)`
- 수신자: `팀 동료`
- 패턴: A-1 담백 보고형, 한 줄로 압축

작성된 본문 (사용자의 "한 줄" 요청 충족, 스킬 A-1 요소인 변경 내용과 hash 포함):

```
`MealLogRepository` @Mock 을 Fake 로 교체했습니다. (a1b2c3d)
```

- 금지 표현(`~것 같습니다`, `감사드립니다`, 저자세 마무리, `!`, `:)`)은 쓰지 않는다.
- 사용자 원문 "수정했습니다" 만 단독으로 보내지 않는 이유: 무엇을 어떻게 바꿨는지와 hash 가 있어야 리뷰어가 resolve 판단을 할 수 있다. 분량은 여전히 한 줄이다.

```bash
gh api "repos/${REPO}/pulls/818/comments" \
  -X POST \
  -F in_reply_to={원본_comment_id} \
  -f body='`MealLogRepository` @Mock 을 Fake 로 교체했습니다. (a1b2c3d)'
```

`/replies` 엔드포인트는 쓰지 않는다 (404).

## 8. 머지 관련 확인 (머지는 하지 않음)

```bash
gh pr checks 818
gh pr view 818 --json mergeable,reviewDecision,statusCheckRollup
```

- CI 가 push 한 커밋에서 끝났는지 확인한다 (v1.8: CI 완료 전 머지 금지).
- 같은 파일을 고치는 다른 열린 PR 이 있으면 머지 순서를 알린다.
- 머지 실행은 사용자 몫이다.

## 9. 종료 보고 (사용자에게)

확인된 것:
- `MealLogServiceTest.java:31` 의 @Mock 을 Fake 로 교체, 커밋·push 완료, 리뷰어 스레드에 한 줄 답글 완료
- review-lint 위반 0건, 최신 dev 병합 후 `compileTestJava`·대상 테스트 통과 (실행 결과는 시뮬레이션 가정)
- 이번 라운드에서 수정한 파일은 `MealLogServiceTest.java` 1개

가정한 것:
- `FakeMealLogRepository` 가 이미 존재한다 (없었다면 신설 허용 여부를 물었을 것)
- 다른 테스트 파일의 @Mock 사용 여부는 스윕 결과에 따른다

주의 (머지 전 판단 필요):
- `MealPhotoServiceTest`, `MealSummaryServiceTest` 에 같은 규칙 08 위반 패턴이 남아 있을 수 있다. 지시대로 수정하지 않았다. 리뷰어가 같은 지적을 다시 할 가능성이 높아, 오늘 머지가 목표라면 이 두 파일도 같은 방식으로 고치는 편이 재지적 라운드를 줄인다. "고쳐라" 한마디면 별도 커밋으로 처리한다.
- lint 와 dev 병합 컴파일은 지시와 달리 실행했다. 하드 가드레일(위반 상태 push 금지)과 머지 직전 컴파일 실패 방지 때문이다. 소요 시간은 수 분이다.
- 가드 추가 후보 없음. 규칙 08 은 가드에 이미 있으므로 "규칙은 있으나 미적용"으로 분류한다.
- `docs/pr-modification-plan-818.md` 는 로컬에만 있고 커밋하지 않았다.
