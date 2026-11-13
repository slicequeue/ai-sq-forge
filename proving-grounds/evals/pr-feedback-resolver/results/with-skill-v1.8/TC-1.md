# TC-1 With-Skill 응답 (시뮬레이션, v1.8)

시뮬레이션이다. 아래 명령은 실제로 실행하지 않았고, 코드도 쓰지 않았다. 실행 순서, 수정 내용, 답글을 서술한 것이다.
`references/feedback-collection.md` 의 답글 API(`/comments/{id}/replies`)는 SKILL.md Step 6 에서 404 로 정정된 경로이므로 따르지 않는다. SKILL.md 의 `POST /pulls/{PR}/comments` + `in_reply_to` 를 쓴다.

## 0. 확인된 것 vs 가정한 것

| 구분 | 내용 |
|------|------|
| 확인된 것 (사용자 입력) | PR #42 '쿠폰 사용 API' 열림. 코멘트 4건의 파일·라인·원문 |
| 확인된 것 (스킬 문서) | 우선순위, 답글 톤 분기, 전송 엔드포인트, 순서(수정 → 커밋 → push → 답글) |
| 가정 (실행 시 현황 확인 필요) | 현재 브랜치가 PR head 브랜치와 같음. 워킹 트리 clean. 저장소에 쿠폰 도메인 커스텀 예외(예: `CouponNotFoundException`)와 전역 예외 핸들러가 이미 있음. `CouponRedeemInDto` 는 `@Valid` 로 바인딩됨. 4번 코멘트 작성자와 CodeRabbit 계정 login 값 |
| 재평가 트리거 | 위 가정이 현황 확인에서 틀리면 수정 방향을 바꾸고 사용자에게 알린다. 예를 들어 커스텀 예외가 없으면 신설 여부를 사용자에게 묻는다(합의 없는 설계 결정 금지) |

## 1. Phase 0 사전 확인

1. `git branch --show-current` — `dev`/`stg`/`main` 이면 즉시 중단하고 "보호 브랜치에서는 피드백 수정이 불가합니다. 작업 브랜치로 전환하세요." 를 안내한다. 작업 브랜치면 진행한다.
2. `git status` — uncommitted 변경이 있으면 사용자에게 알리고 처리 방법을 확인한다. `git stash` 는 금지다.
3. `gh pr list --head "$(git branch --show-current)" --state open --json number,title,url` — PR #42 가 나오는지, head 브랜치가 현재 브랜치와 일치하는지 확인한다. PR 이 없거나 이미 머지됐으면 중단 안내한다.
4. (v1.5) PR 컨텍스트 현황: 머지 정책(base 가 dev 인지 등), CI 상태(`gh pr checks 42`), 이미 달린 코멘트와의 중복 여부를 확인한다.
5. `.github/PULL_REQUEST_TEMPLATE.md` 확인은 PR 본문을 고칠 때만 필요하다. 이번엔 본문을 건드리지 않으므로 해당 없음이다.

## 2. Step 1 피드백 수집

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh pr view 42 --json number,title,body,url
gh api "repos/${REPO}/issues/42/comments"                  # 일반 코멘트 (4번)
gh api "repos/${REPO}/pulls/42/comments" --paginate        # 라인 코멘트 (1, 2, 3번), comment id 확보
gh api "repos/${REPO}/pulls/42/reviews"                    # CHANGES_REQUESTED / COMMENTED 상태 확인
```

- `user.login` 이 `coderabbitai[bot]` 인 것은 CodeRabbit 으로 식별한다(1, 2번).
- 각 라인 코멘트의 `id` 를 저장한다. 답글의 `in_reply_to` 에 쓴다.
- 3번 리뷰어의 review state 가 `CHANGES_REQUESTED` 인지 `COMMENTED` 인지 확인해 우선순위를 확정한다. 인라인 수정 요청이므로 기본은 "높음"이다.

## 3. Step 2 분류

| # | 위치 | 출처 | 판정 | 우선순위 | 답글 파라미터 |
|---|------|------|------|----------|----------------|
| 1 | `CouponService.java:25` | CodeRabbit | 반영 (해당 라인 코드를 열어 확인 후 확정) | 높음 | 봇 (평어 단정형) |
| 2 | `CouponController.java:15` | CodeRabbit | 반영 | 높음 | 봇 |
| 3 | `CouponRedeemInDto.java:5` | 리뷰어(동료) | 반영 (수정 요청) | 높음 | 사람 A-1 담백 보고형 |
| 4 | 이슈 코멘트 | 일반 | 반영 아님. 질문/논의에 해당하므로 답변만 | 낮음 | 사람 톤 |

- 분류 전에 각 라인을 Read 해서 이미 고쳐진 건 아닌지 확인한다(이미해결 여부).
- 쿠폰 API 는 admin 모듈이 아니므로 admin 예외(4-Tier 규칙 미반영 처리)는 적용하지 않는다. 경로가 admin 모듈이면 그때 미반영 + 사유로 분기한다.
- 코멘트가 4건이라 병렬 트리아지 모드(5건 이상 권장)는 쓰지 않고 순차 처리한다.
- 4번 "다음에 테스트 케이스도 추가해주세요" 는 코드 수정 요청이 아니라 다음 작업에 대한 당부다. 이번 PR 에 테스트를 임의로 추가하지 않는다(요청에 없는 범위 확대 금지). 이번 PR 에서 처리할지는 사용자에게 한 줄로 확인한다.

## 4. Step 3 수정 계획 문서

`docs/pr-modification-plan-42.md` 를 `references/modification-plan-template.md` 형식으로 생성한다. 이미 존재하면 통째로 덮지 않고(DW-1, DW-3) 기존 내용을 확인한 뒤 갱신한다.

```markdown
# PR #42 수정 계획

| 항목 | 값 |
|------|-----|
| PR 번호 | #42 |
| 제목 | 쿠폰 사용 API |
| URL | {gh pr view 로 확인한 URL} |
| 브랜치 | {현재 브랜치} |
| 작성일 | 2026-11-13 |

## 수정 요청 요약
| 출처 | 건수 | 우선순위 |
|------|------|---------|
| CodeRabbit | 2건 | 높음 |
| 리뷰어 수정 요청 | 1건 | 높음 |
| 리뷰어 제안 | 0건 | 중간 |
| 질문/논의 | 1건 | 낮음 (답변만) |

## 수정 작업 계획

### 높음
- [ ] **CouponService.java:25** — `Optional.orElseThrow()` 를 도메인 커스텀 예외 supplier 로 교체
  - 출처: CodeRabbit / 답글: 봇 파라미터
  - 원문: "Optional.orElseThrow() 대신 커스텀 예외를 사용하세요"
- [ ] **CouponController.java:15** — `@Operation(summary = ...)` 채움
  - 출처: CodeRabbit / 답글: 봇 파라미터
- [ ] **CouponRedeemInDto.java:5** — `code` 필드에 `@NotBlank` 추가
  - 출처: 리뷰어 / 답글: 사람 A-1

### 중간
(없음)

### 낮음 (답변만)
- [ ] 4번 일반 코멘트 → 답변만, 코드 변경 없음. 테스트 추가는 이번 PR 범위 밖으로 두고 사용자 확인 후 답글

## 미반영·이미해결
(없음. 현황 확인 후 변경되면 사유 기록)
```

(v1.5) 문서에 각 답글의 호출 파라미터(봇 / 사람 A-1)와 선택 근거를 위 표대로 기록한다.

## 5. Step 4 수정 실행 (높음 순서)

### 5-1. CouponService.java:25 (CodeRabbit)
- 해당 라인을 Read 한다. `orElseThrow()` 인자 없는 형태는 `NoSuchElementException` 을 던져 의미가 없고, 전역 핸들러에서 500 으로 처리될 수 있다.
- 저장소의 기존 예외 계층을 grep 한다(예: `*NotFoundException`, `BusinessException` 계열). 있으면 그것을 쓴다.
  `orElseThrow(() -> new CouponNotFoundException(code))` 형태로 교체한다.
- 없으면 임의로 신설하지 않고 사용자에게 "기존 예외 계층에 맞는 클래스가 없다. 신설할까요" 를 묻는다.
- `.claude/rules/` 의 예외·응답 규칙을 확인한다. 아래 가드 파일은 필요 시 읽는다.
  `forge/common/review-recurrence-guard.md`(예외 계층, 장애 시 동작). 이번 시뮬레이션에서는 읽지 않았으므로 해당 규칙 번호는 인용하지 않는다.
- 예외를 새로 던지게 되므로 이 예외가 HTTP 상태(404 등)로 매핑되는지 핸들러를 확인한다.

### 5-2. CouponController.java:15 (CodeRabbit)
- `@Operation(summary = "")` 에 의미 있는 값(예: "쿠폰 사용")을 채운다. 문구는 같은 컨트롤러·프로젝트의 기존 `@Operation` 작성 방식(언어, 문장 형태)에 맞춘다.

### 5-3. CouponRedeemInDto.java:5 (리뷰어)
- `code` 필드에 `@NotBlank` 를 추가하고 import 를 맞춘다. 프로젝트가 메시지를 명시하는 관례면 따른다.
- 컨트롤러의 `@RequestBody` 파라미터에 `@Valid` 가 있는지 확인한다. 없으면 검증이 동작하지 않으므로 함께 추가한다. 이 경우 답글에 그 사실을 적는다.

### 5-4. (v1.7) 같은 유형 전수 스윕
지적 위치만 고치면 다음 라운드에 같은 지적이 다시 온다. 변경 파일 전체에서 같은 패턴을 찾는다.

```bash
git diff --name-only origin/dev...HEAD            # 변경 파일 목록
grep -rn "orElseThrow()" {변경된 main 소스}        # 인자 없는 orElseThrow 전부
grep -rn "@Operation" {변경된 컨트롤러}            # summary 비었거나 누락된 것 전부
grep -rn "String " {변경된 *InDto 들}              # 검증 어노테이션 누락 필드 확인
```

- 인자 없는 `orElseThrow()` 가 다른 서비스·테스트 지원 코드에 더 있으면 같은 방식으로 함께 고친다.
- 같은 컨트롤러의 다른 `@Operation` 의 summary 가 비었으면 함께 채운다.
- 같은 DTO 의 다른 String 필드(예: 사용자 식별자)가 같은 사유로 `@NotBlank` 가 필요한지 확인한다. 필드 의미가 불분명하면 임의로 붙이지 않고 보고만 한다.
- 스윕 결과(곳 수)는 답글과 수정 계획에 기록한다.

### 5-5. 검증
1. `python3 forge/common/review-lint.py` — 위반 0건이어야 한다. 위반이 남으면 커밋·push 하지 않는다.
2. 최신 dev 병합 컴파일(v1.8): 컨트롤러·서비스 시그니처는 바뀌지 않았지만 push 전 규칙이므로 수행한다.
   `git fetch origin dev` 후 dev 를 현재 브랜치에 병합한 상태에서 `./gradlew compileTestJava` 를 돌린다. 충돌·컴파일 실패(다른 PR 의 Fake·생성자 호출)가 있으면 함께 고친다. force push 는 하지 않는다.
3. 관련 테스트(`CouponService`, 컨트롤러 검증)를 실행해 예외 타입 변경이 기존 테스트를 깨지 않는지 확인한다. 기존 테스트가 `NoSuchElementException` 을 기대하고 있으면 새 예외에 맞게 수정한다.
4. 수정 계획 문서의 체크박스를 `- [x]` 로 갱신한다.

### 5-6. 재발 방지 등록 판단 (v1.7)
- 1번(커스텀 예외)·3번(검증 어노테이션)이 `review-recurrence-guard.md` 에 이미 있는 유형인지 대조한다.
  - 있는데 또 나온 경우: 종료 보고에 "규칙은 있으나 미적용" 으로 표시한다(게이트 강화 대상).
  - 없는 유형: "가드 추가 후보: {유형} — PR #42" 를 한 줄로 남긴다. `orElseThrow()` 인자 없음, `@Operation` summary 비어 있음은 문자열로 잡히므로 `review-lint.py` 검사 후보로 표시한다.
- 이번 시뮬레이션에서는 가드 파일을 읽지 않았으므로 어느 쪽인지는 실제 실행 시 판정한다.

## 6. Step 5 커밋 & push

- `/git-commit` 스킬로 커밋한다. 임의 형식의 `git commit` 은 쓰지 않는다. 한국어 Conventional Commits, `refac:` 표기, 대괄호·AI 정보 금지 규칙을 따른다.
  예: `fix: 쿠폰 사용 API 리뷰 반영 — 커스텀 예외, @Operation summary, code @NotBlank`
- 커밋을 논리 단위로 나눌지는 변경 크기에 따른다. 3건이 작으면 1개 커밋으로 한다.
- `git push` 로 원격에 반영한다. push 성공과 commit hash 를 확인한 뒤에만 다음 단계로 간다.

## 7. Step 6 PR 답글 (push 완료 후에만)

모든 답글 본문은 `sq-tone-writer` 스킬로 작성한다. 아래는 그 호출 시 입력(매체, 수신자, 패턴)과 기대 결과 초안이다. commit hash 는 push 후 확정된 값으로 치환한다. `{hash}` 는 자리표시자다.

### 답글 1 — CodeRabbit (`CouponService.java:25`)
- 매체: `GitHub PR 리뷰 답글 (CodeRabbit 봇)` / 수신자: `봇` / 패턴: 이미 반영됨
- 초안:
  > 반영됨 ({hash}). `orElseThrow()` 를 `orElseThrow(() -> new CouponNotFoundException(code))` 로 교체함. 같은 패턴 N곳도 함께 수정함.
- 평어 단정형이다. 존댓말, 멘션, 감사, `!`, `:)`, `...` 는 쓰지 않는다. N 은 스윕 결과 값이다(0곳이면 문장 삭제).

### 답글 2 — CodeRabbit (`CouponController.java:15`)
- 매체: `GitHub PR 리뷰 답글 (CodeRabbit 봇)` / 패턴: 이미 반영됨
- 초안:
  > 반영됨 ({hash}). `@Operation` summary 를 "쿠폰 사용" 으로 채움. 같은 컨트롤러의 나머지 `@Operation` 도 확인했고 누락 없음.
- 스윕에서 실제 수정이 있었으면 마지막 문장을 "N곳 함께 수정함" 으로 바꾼다.

### 답글 3 — 리뷰어 동료 (`CouponRedeemInDto.java:5`)
- 매체: `GitHub PR 리뷰 답글 (사람 리뷰어)` / 수신자: `팀 동료` / 패턴: A-1 담백 보고형 (단순 "추가 필요" 지적이므로 A-2/A-3 불필요)
- 초안:
  > 지적 그대로입니다. `code` 필드에 `@NotBlank` 를 추가했고 컨트롤러 `@Valid` 바인딩도 확인했습니다. (`{hash}`)
- `@Valid` 가 이미 있었으면 "확인했습니다" 를, 없어서 추가했으면 "함께 추가했습니다" 로 쓴다. 금지 표현(`~것 같습니다`, `감사드립니다`, `검토하겠습니다`, 과장 표현)은 쓰지 않는다. 1~2문장으로 한다.
- 의도 추정(예: 빈 문자열과 공백만 있는 값 모두 막는 것으로 이해함)이 들어가면 "그렇게 이해했습니다. 다르면 알려주세요" 형태로 검증 요청을 붙인다(v1.5).

### 답글 4 — 일반 코멘트 (이슈 코멘트)
- 라인 코멘트가 아니므로 `in_reply_to` 를 쓸 수 없다. 이슈 코멘트 엔드포인트(`POST /issues/42/comments`)로 단다.
- 매체: `GitHub PR 리뷰 답글 (사람 리뷰어)` 톤으로 `sq-tone-writer` 경유. 칭찬에 대한 과한 감사·저자세는 넣지 않는다.
- 초안:
  > 확인했습니다. 이번 푸시에 테스트 변경은 없습니다. 테스트 케이스는 추가가 필요한 범위를 알려주시면 반영하겠습니다.
- 코드 변경이 없고 commit hash 도 첨부하지 않는다. 테스트를 이번 PR 에 넣을지 사용자 확인이 끝나기 전에는, 이미 계획한 것처럼 약속하는 문구를 쓰지 않는다.

### 전송 명령

```bash
# 라인 코멘트 답글 (1, 2, 3번) — /replies 엔드포인트는 404 이므로 사용 금지
gh api "repos/${REPO}/pulls/42/comments" -X POST \
  -F in_reply_to={원본_comment_id} \
  -f body="{sq-tone-writer 로 작성한 본문}"

# 일반 코멘트 (4번)
gh api "repos/${REPO}/issues/42/comments" -X POST \
  -f body="{sq-tone-writer 로 작성한 본문}"
```

## 8. 종료 보고 (사용자에게 전달할 내용)

- 처리: 반영 3건(CodeRabbit 2, 리뷰어 1), 답변만 1건. 미반영 0건, 이미해결 0건(라인 확인 결과에 따라 변동).
- 같은 유형 스윕: 인자 없는 `orElseThrow()` 및 `@Operation`·DTO 검증 누락의 추가 발견 곳 수를 보고한다.
- review-lint 0건, 최신 dev 병합 컴파일 통과 여부, push 커밋 hash.
- 재발 방지 등록 판단: "가드 추가 후보" 또는 "규칙은 있으나 미적용" 을 한 줄로 기재한다.
- 사용자에게 묻는 것: (a) 커스텀 예외가 없을 경우 신설 여부, (b) 4번 코멘트의 테스트 케이스를 이번 PR 에 넣을지 여부.

## 9. 자기 검증 체크리스트 (v1.8, 16항목)

| # | 항목 | 결과 |
|---|------|------|
| 1 | 브랜치 검증 (보호 브랜치 아님, PR head 일치) | 계획 반영 |
| 2 | 이슈 코멘트 + 라인 코멘트 전수 수집 | 반영 |
| 3 | CodeRabbit 별도 식별·우선 처리 | 반영 |
| 4 | `docs/pr-modification-plan-42.md` 생성 | 반영 |
| 5 | 수정 → `/git-commit` → push → 답글 순서 | 반영 |
| 6 | 답글 전 push 확인 | 반영 |
| 7 | `.claude/rules/` 위반 없음 | 실행 시 확인 |
| 8 | 체크박스 업데이트 | 반영 |
| 9 | 답글 톤 `sq-tone-writer` 경유 | 반영 |
| 10 | 확인 vs 가정 분리 (답글에 commit hash, 의도 추정은 검증 요청) | 반영 |
| 11 | PR 컨텍스트 파악 (머지 정책, CI, 중복 코멘트) | Phase 0 에 반영 |
| 12 | 봇 vs 사람 분기 근거를 계획 문서에 기록 | 반영 |
| 13 | 같은 유형 스윕, 답글에 "N곳 함께 수정" | 반영 |
| 14 | review-lint 0건 | 반영 |
| 15 | 재발 방지 등록 판단 | 종료 보고에 반영 |
| 16 | 최신 dev 병합 `compileTestJava` | 반영 |

## 10. 하드 가드레일 준수 요약

- push 전 답글 금지 — 준수한다. 답글은 push 이후에만 단다.
- `/git-commit` 사용, `git stash` 금지, obesity 마이그레이션 미접촉, review-lint 위반 상태 push 금지 — 준수한다.
- 파괴적 쓰기 가드(DW-1, DW-3): 기존 파일은 부분 수정만 하고, 수정 계획 문서가 이미 있으면 통째로 덮지 않는다.
- PR 본문은 수정하지 않으므로 PR 템플릿 확인 가드는 해당 없음이다.
- 범위 규율: 4번 코멘트로 테스트를 임의 추가하지 않고, 커스텀 예외 신설 같은 설계 결정은 합의 후 진행한다.
