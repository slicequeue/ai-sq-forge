# git-pr TC-1 — with-skill(v0.5) 회귀 결과

적용 스킬: `anvil/skills/git-pr/SKILL.md` v0.5, 참고 사례 `references/example-pr-551.md`
요청: "PR 만들어줘."

## 1. 확인된 것 vs 가정한 것

| 구분 | 내용 |
|---|---|
| 확인된 것 (시뮬레이션 상황) | 브랜치 `api/fix/null-check-coupon`, base `dev`, 1파일 `pghd/coupon/application/CouponService.java` (+5/-1), 커밋 1건 `fix: 쿠폰 조회 시 null 처리 누락 수정`, 원격 push 완료, 같은 head 의 열린 PR 없음, PR_TEMPLATE.md 없음 |
| 확인 못 한 것 (미실행) | `review-lint.py` 결과, `self-code-reviewer` 실행 여부, 최신 dev 병합 상태의 `compileTestJava` 결과, 실제 diff 내용(null 이 어디서 오고 무엇을 반환하도록 바꿨는지) |
| 가정 | 사용자가 hotfix(`main`) 를 명시하지 않았으므로 base 는 `dev`. 아래 본문의 Why/Changes 는 커밋 메시지와 stat 으로만 쓴 초안이라, diff 를 본 뒤 한 번 더 다듬는다 |

재평가 트리거: diff 에서 응답·에러·검증 동작이 바뀌는 것이 확인되면 "기존 동작 변경" 섹션을 추가한다.

## 2. 명령 계획

### 2-1. Phase 1 (이미 상황으로 주어진 것은 재실행하지 않음)

상황으로 확인된 항목: `git log dev..HEAD --oneline`, `git diff dev..HEAD --stat`, 원격 push, `gh pr list --head ...` 결과(열린 PR 없음), PR 템플릿(없음). 템플릿 확인 명령 `ls .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md 2>/dev/null` 는 결과가 "없음"으로 주어졌으므로 2-2 표준 구성을 쓴다.

### 2-2. 푸시 전 품질 게이트 (하드 가드레일, PR 생성 전에 수행)

실행할 것, 순서대로:

1. diff 본문 확인: `git diff dev..HEAD`
   - 목적: Changes 표에 쓸 변경 내용과 "기존 동작 변경" 해당 여부 판단
2. `forge/common/review-lint.py` 존재 여부 확인 후 실행: `python3 forge/common/review-lint.py --base origin/dev`
   - 위반 0건: 다음 단계로 진행
   - 위반 1건 이상: **PR 생성을 멈추고** 위반 목록을 사용자에게 보고한다. 고친 뒤 재실행해서 0건이 될 때까지 PR 을 만들지 않는다
   - 파일이 없는 저장소: 건너뛰고, 건너뛴 사실을 사용자에게 알린다
   - 해당 없음으로 판단한 확인 항목은 PR 본문 "리뷰 포인트"에 사유 한 줄씩 적는다
3. `self-code-reviewer` 를 아직 안 돌렸으면 먼저 돌린다. 지적 사항이 있으면 고친 뒤 커밋·푸시하고 diff 를 다시 확인한다
4. 최신 dev 병합 컴파일 (v0.5):
   ```bash
   git fetch origin dev && git merge --no-commit --no-ff origin/dev
   ./gradlew :pghd:compileTestJava
   git merge --abort
   ```
   - 모듈명 `pghd` 는 변경 파일 경로에서 추정한 값이므로 `settings.gradle` 로 실제 모듈명을 먼저 확인한다
   - 병합 충돌이 나면 충돌 파일을 사용자에게 보고하고 중단한다 (임의 해결 금지)
   - 컴파일 실패 시: 원인이 내 변경인지 dev 쪽 변경인지 구분해 보고하고, PR 생성을 보류한다
   - 병합 성공이든 실패든 마지막에 `git merge --abort` 로 작업 트리를 원상복구한다
5. 인터페이스 구현체 전수 확인: `CouponService` 가 클래스이고 공개 메서드 시그니처를 바꾸지 않았다면(+5/-1 규모라 가능성이 높지만 diff 로 확인) 해당 없음으로 판단하고 리뷰 포인트에 사유를 적는다. 만약 인터페이스를 바꿨다면 `grep -rn "implements {인터페이스}" */src/test */src/main` 로 테스트 Fake 까지 찾아 함께 고친다. 병합 상태(dev 기준)에서 다시 grep 한다

### 2-3. Phase 3 (게이트 전부 통과한 경우에만)

열린 PR 이 없으므로 신규 생성이다 (`gh pr edit` 해당 없음).

```bash
gh pr create \
  --base dev \
  --head api/fix/null-check-coupon \
  --title "fix: 쿠폰 조회 시 null 처리 누락 수정" \
  --body "$(cat <<'EOF'
<아래 3절 본문>
EOF
)"
```

생성 후 PR URL 과 "신규 생성" 여부를 한 줄로 출력한다.

## 3. 사용자에게 할 말

PR 만들기 전에 스킬 하드 가드레일인 푸시 전 품질 게이트부터 확인하겠습니다. 아직 실행하지 않았고, 결과를 보고 진행합니다.

- `review-lint.py` 위반이 1건이라도 있으면 PR 을 만들지 않고 위반 내용을 알려드립니다.
- `self-code-reviewer` 와 최신 `dev` 를 합친 상태의 `compileTestJava`(모듈은 `pghd` 로 추정, 설정 파일로 확인) 도 통과해야 합니다.
- 모두 통과하면 `dev` 대상으로 아래 본문의 PR 을 신규 생성합니다. 같은 브랜치의 열린 PR 과 저장소 PR 템플릿은 없는 것으로 확인된 상태라 표준 양식을 씁니다.

확인된 것은 변경 파일 1개(+5/-1), 커밋 1건, push 완료까지입니다. 아래 본문의 원인·변경 설명은 커밋 메시지 기준 초안이고, diff 를 확인한 뒤 실제 내용에 맞게 다듬습니다. 응답·에러 동작이 바뀌는 변경이면 "기존 동작 변경" 섹션을 추가합니다. Test list 의 체크는 실제로 돌린 뒤에만 표시합니다.

## 4. PR 제목

`fix: 쿠폰 조회 시 null 처리 누락 수정`

## 5. PR 본문

````markdown
## Why need this PR❓

쿠폰 조회 과정에서 값이 없는 경우(null)를 처리하지 않아 조회가 실패할 수 있던 문제.

**원인**: `CouponService` 의 조회 경로에서 null 확인이 빠져 있었음.

## Changes ✌️

**파일 1개, 5 lines 추가 / 1 line 삭제** (쿠폰 조회 서비스 한 곳에 한정)

| 파일 | 변경 |
|---|---|
| `pghd/coupon/application/CouponService.java` | 쿠폰 조회 시 값이 없는 경우를 먼저 확인하고 처리하도록 보완 |

## 리뷰 포인트

- review-lint 확인 항목 중 해당 없음: 인터페이스·응답 형식 변경 없음 (서비스 내부 null 처리 보완) — diff 확인 후 확정

---

📘 **상세 분석/측정 결과/근거 문서는 Notion으로 별도 공유 예정**

## Test list 📝

- [ ] `./gradlew :pghd:test` 통과 (실행 후 체크)
- [ ] 최신 `dev` 병합 상태 `./gradlew :pghd:compileTestJava` 통과 (실행 후 체크)
- [ ] `review-lint.py` 위반 0건 / `self-code-reviewer` 실행 (실행 후 체크)
````

본문 약 30줄. 측정 결과, 배포, 후속 작업 섹션은 해당 사항이 없어 생략했다. "리뷰 포인트"의 문장은 diff 확인 결과가 다르면 수정한다.

## 6. 자기 검증 체크리스트 점검

| # | 항목 | 결과 | 비고 |
|---|---|---|---|
| 1 | 저장소 템플릿 확인 | 통과 | 없음으로 확인, 표준 구성 사용 |
| 2 | 분량 100~200줄 이내, 코드 스니펫 없음 | 통과 | 약 30줄, 스니펫 없음 (짧은 변경이라 100줄 미만이 적절) |
| 3 | Why 현상+원인 1~2문장 | 통과 | 원인 문장은 diff 확인 후 확정 |
| 4 | Changes 파일별 표 | 통과 | 1파일 1줄 |
| 5 | 측정 결과 | 해당 없음 | 운영 효과 측정 없음, 섹션 생략 |
| 6 | 배포 | 해당 없음 | canary 없음, 생략 |
| 7 | 후속 작업 | 해당 없음 | 별도 PR 항목 없음, 생략 |
| 8 | Test list 포함 | 통과 | 실행 전이라 체크는 비워 둠 (거짓 체크 방지) |
| 9 | 사람 친화 표현 | 통과 | 영문 jargon 없음, 상대 시점 표현 없음 |
| 10 | `docs/...` 링크 0개 | 통과 | Notion 별도 공유 한 줄만 |
| 11 | target branch | 통과 | `dev` (hotfix 명시 없음) |
| 12 | AI 공동작성자 표기 없음 | 통과 | Co-authored-by 및 AI 생성 문구 모두 미포함 (스킬·프로젝트 규칙 우선) |
| 13 | 기존 PR 있으면 `gh pr edit` | 통과 | 열린 PR 없음, 신규 생성 |
| 14 | 품질 게이트 (review-lint 0건, self-code-reviewer) | 미완 | 계획 수립 완료, 실행 결과를 확인하기 전에는 PR 을 만들지 않음 |
| 15 | 기존 동작 변경 섹션 | 조건부 | diff 확인 후 응답·에러 변경 시 추가 |
| 16 | 리뷰 포인트 | 통과 | lint 항목 해당 없음 사유를 한 줄 기재 (diff 확인 후 확정) |
| 17 | 최신 dev 병합 컴파일 + 구현체 grep | 미완 | 계획 수립 완료(병합 → `compileTestJava` → `merge --abort`), 결과 확인 전에는 PR 을 만들지 않음 |

14번과 17번은 시뮬레이션 제약상 실제 실행 결과가 없으므로 "계획 수립, 결과 대기" 상태다. 두 항목이 통과로 확인되기 전에는 Phase 3 의 `gh pr create` 를 실행하지 않는다.
