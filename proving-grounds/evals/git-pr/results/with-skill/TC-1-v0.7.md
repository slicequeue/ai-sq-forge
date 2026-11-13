# git-pr TC-1 응답 (v0.7, 시뮬레이션)

## 0. 판정 요약

| 항목 | 판정 | 근거 |
|---|---|---|
| base | `dev` | 일반 PR, hotfix 명시 없음 |
| 기존 PR | 없음 -> 신규 생성 (`gh pr create`) | 동일 head 열린 PR 없음 |
| 저장소 템플릿 | 없음 -> 2-2 표준 구성 | PR_TEMPLATE.md 없음 |
| 제목 형식 | 조직 컨벤션 비적용 -> Conventional 접두어 허용 | `.claude/shared/vc-conventions-guide.md` 없음. 기존 형식 유지, 조직 컨벤션을 근거로 바꾸지 않음 |
| 조건부 섹션 | 전부 생략 | 측정·배포·후속 작업·기존 동작 변경·리뷰 포인트 모두 입력에 근거 없음. 입력에 없는 사실을 지어 섹션을 만들지 않음 |
| 결론 블록 | 본문 첫 줄에 둠 | 반영 단계는 `머지 전` (dev 배포 확인 없음) |

확인된 것: 변경은 `CouponService.java` 1파일(+5/-1), push 완료, 열린 PR 없음, `./gradlew :pghd:test` 통과.
확인되지 않은 것(본문에 단정하지 않음): review-lint 결과, self-code-reviewer 결과, 최신 dev 병합 컴파일 결과, null 이 발생하는 구체 경로와 원인.

## 1. 실행할 명령 (순서대로)

```bash
# Phase 1. 변경사항 분석
git status
git log dev..HEAD --oneline
git diff dev..HEAD --stat
git branch --show-current
gh pr list --head "$(git branch --show-current)" --state open   # 입력: 열린 PR 없음 -> 신규 생성

# 푸시 전 품질 게이트 (하드 가드레일) -- 결과는 모두 "실행 필요"
python3 forge/common/review-lint.py --base origin/dev           # [실행 필요] 위반 1건이라도 있으면 중단·보고, 고친 뒤 재실행
#   self-code-reviewer 실행                                      # [실행 필요] 아직 안 돌렸다면 PR 전에 먼저
git fetch origin dev && git merge --no-commit --no-ff origin/dev
./gradlew :pghd:compileTestJava                                  # [실행 필요] 최신 dev 병합 상태 컴파일
git merge --abort
#   인터페이스 변경 없음(서비스 클래스 내부 수정, 입력 근거) -> implements 전수 grep 은 해당 없음. 단 diff 에서 인터페이스 변경이 없는지 확인

# 원격 push 확인
#   입력: push 완료 -> `git push -u origin HEAD` 불필요

# 템플릿 확인
ls .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md 2>/dev/null   # 입력: 없음

# share-lint 게이트
python3 -B forge/common/share-lint.py {본문 파일}                # 실행함: 위반 0건 / 확인 0건 (아래 4절)

# Phase 3. 신규 생성 (위 게이트가 모두 통과한 경우에만)
gh pr create \
  --base dev \
  --head api/fix/null-check-coupon \
  --title "fix: 쿠폰 조회 시 null 처리 누락 수정" \
  --body "$(cat <<'EOF'
<아래 3절 본문>
EOF
)"
```

게이트 순서 주의: review-lint 위반이 있으면 `gh pr create` 로 진행하지 않는다. 지금은 결과가 없으므로 PR 을 생성했다고 말하지 않는다.

## 2. PR 제목

```
fix: 쿠폰 조회 시 null 처리 누락 수정
```

근거: `.claude/shared/vc-conventions-guide.md` 없음 -> 조직 컨벤션 비적용, Conventional 접두어 허용. 커밋 제목과 동일. Co-authored-by 등 AI 공동작성자 표기 없음.

## 3. PR 본문 전문

```markdown
쿠폰 조회 시 null 처리 누락 수정 완료 (머지 전)
- `CouponService` 의 쿠폰 조회 경로에 null 처리 추가
- 결과: `./gradlew :pghd:test` 통과

## Why need this PR❓
쿠폰 조회 시 null 이 반환되는 경우의 처리가 빠져 있던 문제를 고친다.

## Changes ✌️
**파일 1개, 5 lines 추가 / 1 line 삭제** (pghd 쿠폰 조회 경로)

| 파일 | 변경 |
|---|---|
| `pghd/coupon/application/CouponService.java` | 쿠폰 조회 결과가 null 일 때의 처리 추가 |

## Test list 📝
- [x] `./gradlew :pghd:test` 통과
- [ ] `review-lint.py` 위반 0건 확인
- [ ] `self-code-reviewer` 점검
- [ ] 최신 dev 병합 상태 `compileTestJava` 통과
```

본문 설계 메모:
- 결론 블록은 제목 없는 첫 줄. 단계는 `머지 전`, 결과 줄에는 확인한 테스트 통과만 적음. lint 통과 등 미확인 사항은 쓰지 않음(SW-5).
- 입력에 null 이 발생하는 구체 경로·원인·재현 조건이 없어 Why 는 "처리가 빠져 있던 문제" 수준으로만 쓰고 원인을 지어내지 않음(SW-7). 원인을 아는 작성자가 있으면 1문장 보강 권장.
- 측정 결과·배포·후속 작업·기존 동작 변경·리뷰 포인트 섹션은 조건 미성립으로 통째 생략. "해당 없음"·"변경 없음" 채움 줄 없음.
- Test list 의 `[x]` 는 실행 결과를 확인한 `:pghd:test` 하나뿐. 나머지는 `[ ]`. 게이트를 통과해 확인되면 PR 생성 전에 `[x]` 로 바꾸고, 문구만 남기기 싫으면 해당 줄을 삭제해도 된다.
- 본문 11줄, `docs/` 링크 없음, 코드 스니펫·mermaid 없음.

## 4. share-lint 실행 결과

본문 파일: `/private/tmp/claude-501/-Users-kakao-orca-workspaces-ai-sq-forge-seafan/0037c72f-1edb-40fc-93ba-d8dd68b46765/scratchpad/git-pr-body-TC-1-ws.md`

```
share-lint: 위반 0건 / 확인 0건 (상세: share-writing-guard.md, forge/common · 배포본 .claude/shared)
```

위반 0건이므로 lint 게이트 통과. 단 이것은 share-lint 한정이며 review-lint 는 별개로 실행 필요.

## 5. 자기 검증 체크리스트 (요약)

| # | 항목 | 상태 |
|---|---|---|
| 1 | 저장소 템플릿 확인 | 없음 확인(입력), 표준 구성 사용 |
| 2 | 분량 100~200줄 이내 | 충족(11줄) |
| 3~4 | Why / Changes 표 | 충족 |
| 5~7 | 측정·배포·후속 작업 | 조건 미성립, 생략 |
| 8 | Test list | 포함 |
| 10 | `docs/` 링크 0개 | 충족 |
| 11 | target `dev` | 충족 |
| 12 | AI 공동작성자 표기 없음 | 충족 |
| 13 | 열린 PR 없음 -> 신규 | 충족 |
| 14 | review-lint 0건·self-code-reviewer | 실행 필요 (미확인) |
| 15~16 | 기존 동작 변경·리뷰 포인트 섹션 없음 | 충족 |
| 17 | 최신 dev 병합 compileTestJava | 실행 필요 (미확인) |
| 18 | 선택 섹션 위치 | 선택 섹션 없음 |
| 19 | 결론 블록, share-lint 위반 0 | 충족 |
| 20 | 제목 형식 | 비적용 프로젝트, 기존 형식 |

## 6. 사용자에게 보일 최종 출력

PR 생성 준비를 마쳤고, 아직 생성하지 않았습니다. 품질 게이트 3건을 먼저 실행해야 합니다.

확인된 것
- 브랜치 `api/fix/null-check-coupon`, base `dev`, 변경 1파일(+5/-1), push 완료, 열린 PR 없음(신규 생성 대상)
- `./gradlew :pghd:test` 통과
- PR 본문 share-lint 위반 0건 / 확인 0건

실행 필요 (결과 미확인)
1. `python3 forge/common/review-lint.py --base origin/dev` — 위반이 1건이라도 있으면 PR 생성을 멈추고 보고드립니다
2. `self-code-reviewer`
3. 최신 dev 병합 상태에서 `./gradlew :pghd:compileTestJava` 후 `git merge --abort`

위 3건이 통과하면 아래로 생성합니다.
- 제목: `fix: 쿠폰 조회 시 null 처리 누락 수정` (조직 컨벤션 가이드가 없는 프로젝트라 Conventional 접두어 형식 유지)
- base: `dev`
- 본문: 3절 전문. 측정·배포·후속 작업·기존 동작 변경·리뷰 포인트 섹션은 해당 사실이 없어 생략했습니다.

확인 부탁
- Why 에 null 이 발생하는 구체 경로(예: 만료·삭제된 쿠폰 조회)를 알고 계시면 한 문장 알려주세요. 지금은 원인을 추정하지 않고 "처리가 빠져 있던 문제"로만 적었습니다.

게이트 통과 후 PR 이 생성되면 URL 과 신규 생성 여부를 한 줄로 알려드립니다.
