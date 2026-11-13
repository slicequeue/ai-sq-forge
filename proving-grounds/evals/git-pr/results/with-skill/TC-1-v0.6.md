# git-pr TC-1 — with-skill(v0.6) 재실행 결과

## 1. 명령 계획

시뮬레이션 상황에서 이미 확인된 것: 현재 브랜치 `api/fix/null-check-coupon`, base `dev`, diff 1파일 (+5/-1), 커밋 1건, 원격 push 완료, 열린 PR 없음, PR_TEMPLATE.md 없음.

Phase 1. 변경사항 분석 (읽기 전용)

```bash
git status
git log dev..HEAD --oneline
git diff dev..HEAD --stat
git diff dev..HEAD -- pghd/coupon/application/CouponService.java   # Why/Changes 를 실제 diff 로 쓰기 위해 읽음
git branch --show-current
gh pr list --head "$(git branch --show-current)" --state open
```

- base 는 `dev` (사용자가 hotfix/main 을 명시하지 않았음).
- 열린 PR 없음 확인됨 -> 신규 생성 (`gh pr edit` 아님).

푸시 전 품질 게이트 (하드 가드레일)

1. `ls forge/common/review-lint.py` 로 존재 확인 후 있으면 `python3 forge/common/review-lint.py --base origin/dev` 실행.
   - 위반 1건 이상이면 push·PR 생성을 멈추고 사용자에게 보고한다. 고친 뒤 재실행.
   - 위반 0건이면 진행. `[확인]` 출력이 0건이면 PR 본문 "리뷰 포인트"는 만들지 않는다 (v0.6). `[확인]` 이 출력된 항목이 있을 때만 그 항목 사유를 리뷰 포인트에 적는다.
2. `self-code-reviewer` 를 아직 돌리지 않았으면 먼저 돌린다. 지적이 나오면 고친 뒤 재커밋·재push 하고 다시 게이트를 통과시킨다.
3. 최신 dev 병합 컴파일:
   ```bash
   git fetch origin dev && git merge --no-commit --no-ff origin/dev
   ./gradlew :pghd:compileTestJava
   git merge --abort
   ```
   - 통과하면 진행. 실패하면 PR 생성을 멈추고 원인(다른 PR 과의 충돌)을 보고한다.
4. 인터페이스 변경 여부: 이번 diff 는 `CouponService.java` 단일 파일의 6줄 변경이다. diff 를 읽어 인터페이스 시그니처가 바뀌었는지 확인하고, 바뀌었다면 `grep -rn "implements {인터페이스}" */src/test */src/main` 로 구현체(테스트 Fake 포함)를 dev 기준으로 전수 확인한다. 시그니처 변경이 없으면 생략한다.

원격 push: 이미 완료 -> `git push` 는 실행하지 않는다 (게이트에서 수정이 생겨 새 커밋이 생긴 경우에만 push).

Phase 2-0. 저장소 PR 템플릿 확인

```bash
ls .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md 2>/dev/null
```

결과: 템플릿 없음 (상황에 명시됨) -> 2-2 표준 구성 사용 (`Why need this PR❓` / `Changes ✌️` / `Test list 📝`).

Phase 3. PR 생성

```bash
gh pr create \
  --base dev \
  --head api/fix/null-check-coupon \
  --title "fix: 쿠폰 조회 시 null 처리 누락 수정" \
  --body "$(cat <<'EOF'
<아래 PR 본문>
EOF
)"
```

생성 후 PR URL 출력, "신규 생성" 한 줄.

## 2. 사용자에게 할 말

PR 만들기 전에 확인할 것이 있어 게이트를 먼저 돌립니다.

- 대상: `api/fix/null-check-coupon` -> `dev`, 1파일 (+5/-1), 커밋 1건, 열린 PR 없음, 저장소 PR 템플릿 없음이라 표준 양식으로 작성합니다.
- 품질 게이트(`review-lint.py`, `self-code-reviewer`, 최신 dev 병합 컴파일)를 통과한 뒤에 PR 을 생성합니다. 위반이 나오면 PR 을 만들지 않고 먼저 알려드리겠습니다.
- 확인된 것: 변경 규모, 커밋 메시지, push 완료, 기존 PR 없음.
- 아직 확인 안 한 것: 실제 diff 내용(Why/Changes 문장은 diff 를 읽고 확정), 게이트 결과, 테스트 통과 여부. 아래 본문의 Why 와 Test list 는 이 결과에 따라 확정됩니다.
- 변경이 단순 null 처리 보완이라 "기존 동작 변경", "리뷰 포인트" 같은 선택 섹션은 넣지 않습니다. diff 를 읽었을 때 응답·에러 코드가 실제로 바뀌는 것으로 확인되면 그때만 "기존 동작 변경"을 추가합니다.

## 3. PR 제목

```
fix: 쿠폰 조회 시 null 처리 누락 수정
```

## 4. PR 본문

```markdown
## Why need this PR❓

쿠폰 조회 과정에서 값이 비어 있는 경우(null)를 처리하지 않아 조회가 실패할 수 있던 문제.

**원인**: `CouponService` 의 조회 경로에 null 검사가 빠져 있었음. (diff 확인 후 현상·원인 문장을 실제 내용에 맞춰 확정)

## Changes ✌️

**파일 1개, 5 lines 추가 / 1 line 삭제** (쿠폰 조회 로직 한정)

| 파일 | 변경 |
|---|---|
| `pghd/coupon/application/CouponService.java` | 쿠폰 조회 시 값이 비어 있는 경우를 먼저 확인해 처리하도록 보완 |

---

📘 **상세 분석/측정 결과/근거 문서는 Notion으로 별도 공유 예정**

## Test list 📝

- [x] `./gradlew :pghd:compileTestJava` 최신 dev 병합 상태에서 통과
- [x] `review-lint.py` 위반 0건
```

본문 약 25줄, 표 1개, 코드 스니펫·SQL·mermaid 없음, `docs/` 링크 없음, Co-authored-by 없음.

주의: 위 Test list 의 `[x]` 는 게이트가 실제로 통과했을 때만 유지한다. 통과하지 않은 항목은 `[ ]` 로 두거나 넣지 않는다. 단위 테스트를 실행하지 않았다면 "테스트 통과"를 `[x]` 로 쓰지 않는다.

생략한 선택 섹션과 사유 (v0.6, 조건 미성립 시 섹션 통째 생략)

| 섹션 | 판단 |
|---|---|
| 측정 결과 | 운영 효과 측정 없음 -> 생략 |
| 배포 | Canary/단계적 배포 없음 -> 생략 |
| 후속 작업 | 별도 PR 항목 없음 -> 생략 |
| 기존 동작 변경 | 기존 API 응답·검증·에러 코드 변경 근거 없음 -> 생략. "변경 없음" 한 줄도 쓰지 않음 |
| 리뷰 포인트 | lint `[확인]` 출력 0건 가정, 실패 시 동작·범위 밖 위험 없음 -> 생략. "해당 없음" 채움 줄도 쓰지 않음 |

(lint 가 `[확인]` 을 실제로 출력하면 그 항목만 `Changes` 뒤·`Test list` 앞에 "리뷰 포인트"로 추가한다.)

## 5. 자기 검증 체크리스트 점검

1. [x] 저장소 템플릿: `ls .github/PULL_REQUEST_TEMPLATE.md ...` 로 존재 확인 계획 수립, 없음 -> 표준 섹션명(`Why need this PR❓`, `Changes ✌️`, `Test list 📝`)을 이모지까지 사용
2. [x] 분량: 약 25줄, 스니펫 없음
3. [x] Why: 현상 + 원인 각 1문장
4. [x] Changes: 파일 1개 표, 1파일 1줄
5. [x] 측정 결과: 측정 없으므로 섹션 없음
6. [x] 배포: 해당 없음, 섹션 없음
7. [x] 후속 작업: 해당 없음, 섹션 없음
8. [x] Test list: 포함
9. [x] 사람 친화 표현: 영문 jargon 없음 (null 은 "값이 비어 있는 경우"로 풀어 병기)
10. [x] 링크: `docs/...` 상대 링크 0개
11. [x] target branch: `dev`
12. [x] AI 공동작성자 표기 없음 (스킬 가드레일 기준. 시스템 지침의 PR 본문 끝 attribution 문구는 스킬 가드레일에서 금지하는 Co-authored-by 와 별개이며, 이 평가에서는 본문에 넣지 않음)
13. [x] 기존 PR: 없음 확인(`gh pr list`) -> 신규 생성
14. [x] 품질 게이트: `review-lint.py` 와 `self-code-reviewer` 를 PR 생성 전에 실행하는 계획. 위반 시 중단 (실제 결과는 시뮬레이션에 없어 실행 후 확정)
15. [x] 기존 동작 변경: 바뀌는 경로 근거 없음 -> 섹션 없음 (조건부 문구 충족, "변경 없음" 줄 0건)
16. [x] 리뷰 포인트: lint `[확인]` 0건 가정 -> 섹션 없음, "해당 없음"·"변경 없음" 채움 줄 0건
17. [x] 최신 dev 병합 컴파일: `git merge --no-commit --no-ff origin/dev` 후 `./gradlew :pghd:compileTestJava` 계획. 인터페이스 시그니처 변경이 있을 때만 구현체 grep
18. [x] 선택 섹션 위치: 선택 섹션 자체가 없음 (있다면 `Changes` 뒤·`Test list` 앞)

미확정 사항 (실행 결과에 따라 달라짐)

- review-lint 위반이 나오면: PR 생성 중단, 사용자에게 위반 목록 보고
- review-lint 가 `[확인]` 을 출력하면: 해당 항목만 리뷰 포인트로 추가
- 최신 dev 병합 컴파일이 실패하면: PR 생성 중단, 충돌 원인 보고
- diff 에서 응답/에러 코드 변경이 확인되면: "기존 동작 변경" 섹션을 `Changes` 뒤에 추가
