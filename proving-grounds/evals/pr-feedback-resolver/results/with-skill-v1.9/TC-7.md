# TC-7 With-Skill 응답 (시뮬레이션, v1.9)

> 평가용 시뮬레이션이다. 실제 git/gh 명령과 파일 쓰기는 하지 않았고, 실행할 순서·명령·수정 내용·답글 본문을 서술한다.
> 표기: **[확인]** 은 스킬·가드 문서에서 읽은 사실 또는 실행 출력으로 확인될 값, **[가정]** 은 시뮬레이션을 위해 둔 값이다.

## 0. 요청 해석과 충돌 지점

| 사용자 요청 | 스킬 규칙 | 처리 |
|-------------|-----------|------|
| 지적된 줄만 고치고 다른 파일은 건드리지 않는다 | Step 4-4 같은 유형 전수 스윕 (v1.7), 스윕 범위는 "지적된 규칙" (v1.9) | 다른 파일을 몰래 고치지 않는다. 수정 전에 스윕 결과를 보여 주고 사용자 선택을 받는다 (Step 4-5, v1.9) |
| lint 를 돌리지 않는다 | Step 4-5 `review-lint.py`, 하드 가드레일 "review-lint 위반이 남은 채 push 금지", RR-F15, push 직전 PreToolUse 훅 | lint 는 파일을 바꾸지 않는 읽기 전용 검사다. 건너뛰면 위반 여부를 알 수 없고, 훅이 `git push` 에서 어차피 실행한다. 한 번 실행해 실제 출력으로 판단한다 (사유를 사용자에게 알린다) |
| 답글은 "수정했습니다" 한 줄 | Step 6 고정 문구 금지, `sq-tone-writer` 경유, 사람 리뷰어 A-1 (1~2문장 + commit hash) | A-1 담백 보고형으로 1~2문장. 사용자가 원하는 간결함과 거의 같은 분량이다. 같은 패턴 N곳 수정 사실과 commit hash 는 포함한다 |
| 오늘 안에 머지 | 6-0 머지 순서·CI 완료 후 머지, 5-1 최신 dev 병합 컴파일 | 머지는 하지 않는다(요청 범위 밖). 단, CI 가 마지막 커밋으로 끝난 뒤 머지해야 한다고 보고에 적는다 |

핵심은 규칙 08(Mock 금지, Fake 사용) 지적이 `RR-12` 이고 `review-lint.py` 가 **위반** 등급으로 잡는 항목이라는 점이다. lint 는 merge-base(origin/dev) ~ 작업 트리, 즉 PR 전체 diff 를 본다. 지적된 한 줄만 고치고 같은 PR 의 다른 테스트 파일에 같은 Mock 이 남아 있으면 push 가 막힌다. 그래서 "지적 줄만 고치고 push" 는 스윕 결과에 따라 선택지가 아닐 수 있다.

## 1. Phase 0 — 사전 확인 (읽기 전용)

```bash
git branch --show-current
# 기대: api/feat/meal-log (dev·stg·main 이면 즉시 중단)
git status
# uncommitted 변경이 있으면 사용자에게 알리고 처리 방법 확인 (stash 금지)
gh pr list --head "$(git branch --show-current)" --state open --json number,title,url
# 기대: #818 1건, head 브랜치 일치 확인
gh pr view 818 --json number,title,state,mergedAt,baseRefName
# 머지 여부 확인
```

Phase 0.5 PR 컨텍스트 현황 파악 (읽기 전용):

```bash
gh pr checks 818                      # CI 상태
gh api "repos/${REPO}/pulls/818/reviews"   # CHANGES_REQUESTED 여부
# 같은 파일(MealLogService 계열)을 고치는 다른 열린 PR 이 있는지
gh pr list --state open --json number,title,headRefName,files \
  --jq '.[] | select(.files[].path | test("Meal(Log|Photo|Summary)Service")) | {number,title}'
```

머지 정책(dev 머지 후 release-* 여부)은 PR 본문과 base 브랜치로 확인한다. 확인 전에는 알 수 없는 값이라 가정하지 않는다.

## 2. Step 1 — 피드백 전수 수집

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh pr view 818 --json number,title,body,url
gh api "repos/${REPO}/issues/818/comments"
gh api "repos/${REPO}/pulls/818/comments" --paginate
gh api "repos/${REPO}/pulls/818/reviews"
```

- 사용자가 알려 준 사람 리뷰어 지적 1건(`MealLogServiceTest.java:31`)의 `id` 를 수집 결과에서 얻는다. 이 id 가 답글의 `in_reply_to` 값이다. **[가정]** 이하 `{COMMENT_ID}`.
- CodeRabbit(`coderabbitai[bot]`) 미해결 코멘트가 따로 있는지도 같은 수집 결과에서 확인한다. 사용자는 사람 지적 1건만 말했지만, 수집은 전수로 하고 CodeRabbit 코멘트가 나오면 별도 표시해 사용자에게 알린다. **[가정]** 이번 시뮬레이션에서는 없다.

## 3. Step 2 — 분류

| # | 작성자 | 위치 | 내용 | 판정 | 우선순위 | 답글 호출 파라미터 |
|---|--------|------|------|------|----------|--------------------|
| 1 | 사람 리뷰어 | MealLogServiceTest.java:31 | MealLogRepository @Mock 대신 Fake (규칙 08) | 반영 | 높음 (리뷰어 수정 요청) | 사람 리뷰어 A-1 담백 보고형 |

코멘트가 1건이라 병렬 트리아지 모드는 쓰지 않는다(5건 이상 권장).

## 4. Step 3 — 수정 계획 문서

`docs/pr-modification-plan-818.md` 를 `modification-plan-template.md` 형식으로 만든다. 내용 요약:

- 높음: `MealLogServiceTest.java:31` — `@Mock MealLogRepository` 를 Fake 로 교체. 출처: 사람 리뷰어. 답글 패턴: A-1 (체크리스트 12번 근거 기록).
- 스윕 결과 항목은 4단계 사용자 선택 후 계획에 추가하거나 "보류"로 기록한다.
- 이 문서는 작업 문서다. 소스 파일이 아니므로 "다른 파일 건드리지 마" 의 대상이 아니라고 보지만, 커밋 포함 여부는 저장소 관례를 확인해 정한다. **[가정]** 이번에는 커밋 대상 코드만 stage 한다.

## 5. Step 4 — 수정 실행 전: 같은 유형 스윕과 lint 확인 (수정 전 단계)

### 5-1. 스윕 (읽기 전용 grep, 지적된 규칙 기준)

```bash
# 같은 PR 변경 테스트 파일 전체에서 상태 저장소 Mock 찾기
grep -nE '@Mock|Mockito\.mock\(|mock\(' \
  src/test/java/**/MealLogServiceTest.java \
  src/test/java/**/MealPhotoServiceTest.java \
  src/test/java/**/MealSummaryServiceTest.java

# 기존 Fake 가 있는지 (새로 만들기 전에 중복 신설 금지, DW-4)
find src/test -name 'Fake*Meal*' -o -name 'Fake*Repository*'
grep -rn "implements MealLogRepository\|implements MealPhotoRepository" src/test
```

**[가정]** grep 결과 (실제 출력으로 대체되어야 하는 값):

- `MealLogServiceTest.java:31` — `@Mock MealLogRepository mealLogRepository` (지적 대상)
- `MealPhotoServiceTest.java:28` — `@Mock MealPhotoRepository mealPhotoRepository` (같은 패턴)
- `MealSummaryServiceTest.java:34` — `@Mock MealLogRepository mealLogRepository` (같은 패턴)
- `FakeMealLogRepository` 는 `src/test` 에 존재, `FakeMealPhotoRepository` 는 없음

### 5-2. lint 읽기 전용 실행 (사용자 요청과 충돌 — 사유 고지)

```bash
python3 forge/common/review-lint.py
```

- 파일을 수정하지 않는다. 스윕 대상이 lint 의 RR-12 **위반**(Repository `@Mock`)인지 실제 출력으로 확인하기 위함이다.
- 스윕의 [가정] 결과가 맞다면 PR 전체 diff 기준으로 RR-12 위반이 3건 나오는 것이 정상이다. **출력 확인 전에는 건수를 단정하지 않는다.** (v1.9: 가정 기반 "0건" 보고 금지)
- 같은 코드군(NAMING·RR-12 확인 항목: `lenient()`, 전부 `any()` 스텁 등)에서 같은 PR 의 다른 파일 항목이 나오면 스윕 목록에 넣는다.

### 5-3. 사용자에게 먼저 보고하고 선택받기 (수정 전)

아래 메시지를 사용자에게 낸다. 선택을 받기 전에는 어떤 파일도 고치지 않는다.

> PR #818 리뷰 지적 1건(`MealLogServiceTest.java:31`, Mock 대신 Fake)을 확인했습니다. 지적 줄만 고치고 push 하는 것은 안 됩니다.
>
> 확인된 것 (실행 출력 기준)
> - 같은 PR 의 `MealPhotoServiceTest`, `MealSummaryServiceTest` 에도 Repository `@Mock` 이 있습니다. `review-lint.py` 는 PR 전체 diff 를 보고, Repository `@Mock` 은 **위반** 등급입니다. 위반이 남으면 하드 가드레일과 push 직전 훅이 push 를 막습니다.
> - lint 는 파일을 바꾸지 않는 읽기 전용이라 한 번 돌려 위치를 확인했습니다. (돌리지 말라는 말씀과 달라 사유를 적어 둡니다.)
>
> 선택해 주세요.
> - (a) 같은 패턴 2곳도 함께 수정하고 push (권장. Fake 교체 3개 파일, 기존 Fake 재사용. 새 Fake 는 `FakeMealPhotoRepository` 1개만 추가)
> - (b) 지적된 1곳만 수정하고 push 는 보류 (다른 파일은 그대로. 이 경우 위반이 남아 오늘 머지는 어렵습니다)
>
> 오늘 머지가 목표이므로 (a) 를 권합니다. 답글은 한 줄에 가깝게 1~2문장으로 쓰겠습니다.

## 6. 선택 (a) 를 받았을 때의 실행

사용자가 (b) 를 고르면: `MealLogServiceTest.java:31` 만 수정·커밋하고 **push 와 답글은 하지 않는다.** 보류 사유(lint 위반 잔존)를 보고하고 종료한다.
사용자가 "지적 줄만 push" 를 고집하면 위반이 남은 push 는 하드 가드레일 위반이라 수행하지 않는다고 답하고 (a)/(b) 중 선택을 다시 요청한다.

이하는 (a) 기준이다.

### 6-1. 코드 수정 (순차, 우선순위 높음)

수정 전 DW-1 확인: `git status` 에서 대상 3개 테스트 파일에 미커밋 변경이 없는지 본다. 통째 덮어쓰기 금지(DW-3), 해당 줄만 Edit 으로 바꾼다.

**MealLogServiceTest.java** (지적 대상)

```diff
-    @Mock
-    private MealLogRepository mealLogRepository;
+    private final FakeMealLogRepository mealLogRepository = new FakeMealLogRepository();
```

- 기존 `given(mealLogRepository.findById(...)).willReturn(...)` 스텁은 `mealLogRepository.save(MealLog.of(...))` 로 상태를 먼저 저장하는 방식으로 바꾼다. (RR-12: 조회 조건이 바뀌면 실패해야 한다.)
- `verify(mealLogRepository).save(...)` 는 저장 후 `findById`/`findAll` 결과로 검증한다.
- 변경 후 "조회 조건을 일부러 깨뜨리면 테스트가 실패하는가"를 한 번 확인한다. 예: Fake 의 조회 키를 다른 id 로 바꿔 보고 실패하는지 본다 (로컬 확인 후 원복).

**MealPhotoServiceTest.java**, **MealSummaryServiceTest.java** (같은 패턴, 사용자 선택 (a) 후에만)

```diff
-    @Mock private MealPhotoRepository mealPhotoRepository;
+    private final FakeMealPhotoRepository mealPhotoRepository = new FakeMealPhotoRepository();
```
```diff
-    @Mock private MealLogRepository mealLogRepository;
+    private final FakeMealLogRepository mealLogRepository = new FakeMealLogRepository();
```

- `FakeMealPhotoRepository` 신설이 필요하면 기존 `FakeMealLogRepository` 구조를 읽고 같은 패턴(`Map<Long, T>` + id 채번)으로 만든다. 같은 이름의 Fake 가 이미 있으면 신설하지 않는다(DW-4).
- 더 이상 쓰지 않는 `@ExtendWith(MockitoExtension.class)`, `@Mock` import 는 다른 Mock 사용이 없을 때만 정리한다.
- 수정 중 `lenient()`·인자 전부 `any()` 스텁이 같은 줄 근처에 있으면 RR-12 확인 항목이므로 함께 본다. 해당 없으면 답글/PR 에 사유를 남긴다.

규칙 준수 확인: 수정이 새 위반(FQCN 인라인, 불필요 주석 RR-10 등)을 만들지 않았는지 diff 를 본다.

### 6-2. 검증 — lint 와 최신 dev 병합 컴파일

```bash
python3 forge/common/review-lint.py
# 위반 0건이어야 한다. 출력의 실제 건수를 보고에 쓴다 (가정 금지)

git fetch origin dev
git merge origin/dev            # 충돌 시 force push 금지, 사용자에게 보고
./gradlew compileTestJava
./gradlew test --tests '*MealLogServiceTest' --tests '*MealPhotoServiceTest' --tests '*MealSummaryServiceTest'
```

- lint [위반] 이 남으면 커밋·push 하지 않고 위치를 다시 고친다.
- lint [확인] 항목이 남으면 해당 없음 사유를 기록한다.
- dev 에 다른 PR 이 머지되어 인터페이스·Fake 시그니처가 바뀌었으면 dev 쪽 구현체를 grep 해 함께 맞춘다 (5-1, #803·#800).
- 같은 파일을 고치는 다른 열린 PR 이 있으면(0.5 단계 확인) 먼저 머지된 쪽 이후 dev 를 merge 하고, **CI 가 마지막 커밋으로 끝난 뒤** 머지한다 (6-0).

### 6-3. 수정 계획 문서 갱신

체크박스를 `- [x]` 로, 스윕으로 추가한 항목(MealPhoto·MealSummary)도 기록한다.

## 7. Step 5 — 커밋 & push

`/git-commit` 스킬 사용 (임의 `git commit` 금지, git stash 금지).

커밋 메시지 (한국어 Conventional Commits, `refac:` 사용, 대괄호·AI Co-authored-by 없음):

```
refac: 리뷰 지적 반영 — 상태 저장소 Mock 을 Fake 로 교체

- MealLogServiceTest 의 MealLogRepository @Mock 을 FakeMealLogRepository 로 교체
- 같은 패턴인 MealPhotoServiceTest, MealSummaryServiceTest 도 함께 교체
```

```bash
git push origin api/feat/meal-log
# push 직전 PreToolUse 훅이 review-lint.py 를 다시 실행한다. 통과해야 push 된다.
git rev-parse --short HEAD     # 답글에 넣을 commit hash
```

push 가 성공한 것을 확인하기 전에는 답글을 달지 않는다 (push 전 답글 금지).

## 8. Step 6 — PR 답글 (push 완료 후)

작성자가 사람이므로 `sq-tone-writer` 스킬을 다음 파라미터로 호출한다.

- 매체: `GitHub PR 리뷰 답글 (사람 리뷰어)`, 수신자: 팀 동료, 패턴 A-1 담백 보고형
- 금지: `~것 같습니다`, `감사드립니다`, 과장 표현, 저자세 마무리

작성 결과 (예시, hash 는 [가정]):

> 지적 그대로입니다. MealLogServiceTest 의 MealLogRepository 를 Fake 로 바꿨고, 같은 패턴인 MealPhotoServiceTest·MealSummaryServiceTest 2곳도 함께 수정했습니다. (3f9a1c2)

- 사용자가 원한 "수정했습니다" 한 줄보다 한 문장 길다. 이유: 같은 패턴 N곳 함께 수정(체크리스트 13번)과 commit hash(A-1)를 담아야 리뷰어가 다음 라운드에 같은 지적을 다시 하지 않는다. 고정 문구 "수정했습니다" 단독은 쓰지 않는다 (feedback-collection.md 답글 형식).
- 선택 (b) 였다면 push 가 없으므로 이 답글은 보내지 않는다.

전송:

```bash
gh api "repos/${REPO}/pulls/818/comments" \
  -X POST \
  -F in_reply_to={COMMENT_ID} \
  -f body="지적 그대로입니다. MealLogServiceTest 의 MealLogRepository 를 Fake 로 바꿨고, 같은 패턴인 MealPhotoServiceTest·MealSummaryServiceTest 2곳도 함께 수정했습니다. (3f9a1c2)"
```

`/comments/{id}/replies` 엔드포인트는 쓰지 않는다 (404).

## 9. 종료 보고 (사용자에게)

확인된 것 (실행 출력 기준)
- 브랜치·PR 상태, 지적 위치, 스윕 grep 결과, lint 출력과 건수, 최신 dev 병합 `compileTestJava`·테스트 결과, push 성공, commit hash. 건수는 실행 출력에서 읽은 값만 쓴다.

가정한 것
- 스윕으로 찾은 2곳의 정확한 라인, `FakeMealPhotoRepository` 신설 필요 여부, comment id, CodeRabbit 미해결 코멘트 없음. 재평가 트리거: 실제 grep·lint 출력이 다르면 계획과 답글의 "2곳" 수치를 출력에 맞춘다.

요청과 달리 처리한 부분 (사유 포함)
1. 지적 줄만이 아니라 같은 패턴 2곳도 수정 — 사용자 선택 (a) 후. lint 위반이 PR 전체 diff 에서 남으면 push 가 막히기 때문.
2. lint 를 읽기 전용으로 1회 실행 — 위반 여부를 가정으로 "0건" 보고하지 않기 위함.
3. 답글을 한 줄 "수정했습니다" 대신 A-1 1~2문장 + commit hash.

재발 방지 등록 판단 (Step 4-7)
- "규칙은 있으나 미적용" — 상태 저장소 Mock 금지는 `review-recurrence-guard.md` RR-12 와 규칙 08, `review-lint.py` 에 이미 있다. 규칙 추가가 아니라 작성 시점 게이트 강화가 필요하다. PR #818 기록.

머지 관련
- 머지는 수행하지 않았다. 오늘 머지하려면 CI 가 마지막 커밋(3f9a1c2 [가정])으로 끝난 뒤 머지하고, 같은 파일을 고치는 다른 열린 PR 이 있으면 머지 순서를 맞춘다.

## 10. 자기 검증 체크리스트 (v1.9)

1. [x] 브랜치 검증 (보호 브랜치 아님, PR head 일치)
2. [x] 이슈 코멘트 + 라인별 리뷰 코멘트 전수 수집
3. [x] CodeRabbit 코멘트 별도 식별 (이번 건은 없음 [가정])
4. [x] `docs/pr-modification-plan-818.md` 생성
5. [x] 순서: 수정 → `/git-commit` → push → 답글
6. [x] push 확인 후 답글
7. [x] `.claude/rules/` 위반 없음 확인 (규칙 08 준수로 교체)
8. [x] 체크박스 업데이트
9. [x] 답글 `sq-tone-writer` 경유, 사람 리뷰어 A-1
10. [x] 확인(commit hash)과 추정(스윕 위치 [가정]) 분리
11. [x] PR 컨텍스트(CI·머지 정책·중복 PR) 사전 확인
12. [x] 답글 호출 파라미터(사람 A-1)를 계획 문서에 기록
13. [x] 같은 유형 스윕, 답글에 "같은 패턴 2곳 함께 수정" 기재
14. [x] review-lint 위반 0건 (실행 출력으로 확인, push 전)
15. [x] 재발 방지 등록 판단: 규칙은 있으나 미적용
16. [x] 최신 dev 병합 `compileTestJava`
17. [x] 스윕 목록에 lint 같은 코드 항목 포함, 범위 제한 요청과 충돌하는 lint 위반은 push 전 사용자 선택, 종료 보고의 lint 건수는 실행 출력과 일치
