# git-pr TC-6 — with-skill(v0.5) 결과

## 1. 명령 계획

시뮬레이션이므로 실제로 실행하지 않았다. 아래 순서로 실행하고, 결과는 시뮬레이션 상황에 주어진 값을 쓴다.

| 순서 | 명령 | 결과 / 판단 |
|---|---|---|
| 1 | `git status` / `git log origin/dev..HEAD --oneline` / `git diff origin/dev..HEAD --stat` / `git branch --show-current` | 커밋 1개, 파일 5개 (+150 / -3). base 는 `dev` (hotfix 요청 없음) |
| 2 | `gh pr list --head api/feat/glucose-record-time-validation --state open` | 열린 PR 없음, 그래서 신규 생성 (`gh pr edit` 아님) |
| 3 | `python3 forge/common/review-lint.py --base origin/dev` | 위반 0건, 확인 1건 (ResponseEntity). 위반이 없으므로 푸시 진행. 확인 1건은 해당 여부를 판단해 본문 "리뷰 포인트"에 사유를 적는다 (아래 3번) |
| 4 | `self-code-reviewer` | 이번 세션에서 이미 실행, 지적 0건. 다시 돌리지 않는다 |
| 5 | `git fetch origin dev && git merge --no-commit --no-ff origin/dev` 후 `./gradlew :pghd:compileTestJava`, 이어서 `git merge --abort` | 통과. 병합할 내용이 없어 "Already up to date" 면 abort 는 생략한다 |
| 6 | 인터페이스 구현체 전수 grep (`grep -rn "implements ..." */src/test */src/main`) | 인터페이스 변경이 없으므로 대상 없음. 실행하지 않는다 |
| 7 | `./gradlew :pghd:test` | 통과 |
| 8 | `ls .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md 2>/dev/null` | `.github/pull_request_template.md` 있음. 섹션명을 이모지까지 그대로 복사해 쓴다 |
| 9 | `git push -u origin HEAD` | 원격에 아직 없으므로 실행 |
| 10 | `gh pr create --base dev --head api/feat/glucose-record-time-validation --title "..." --body "$(cat <<'EOF' ... EOF)"` | 본문은 아래 3번. Co-authored-by, AI 생성 표기 줄은 넣지 않는다 |
| 11 | 출력 | gh 가 돌려주는 PR URL 을 그대로 전달하고 "신규 생성" 한 줄을 덧붙인다 |

게이트(3, 4, 5, 7)를 모두 통과한 뒤에만 9번 푸시와 10번 생성으로 간다.

## 2. 사용자에게 할 말

PR 을 만든다. 푸시 전 게이트는 모두 통과했다. review-lint 는 위반 0건이고, 최신 dev 를 합친 상태의 `compileTestJava` 와 `:pghd:test` 도 통과했고, self-code-reviewer 는 이번 세션에서 지적 0건이었다. 열린 PR 이 없어서 신규로 만들고, 저장소 템플릿(`pull_request_template.md`)의 섹션명을 그대로 썼다.

본문에 일부러 넣은 것 두 가지.

- **기존 동작 변경 섹션**: 수정 `PUT` 은 기존에 시각 검증이 없어서 어떤 시각이든 통과했다. 이번 PR 로 400 이 나는 경우가 생긴다. 공용 검증기를 등록에도 쓰므로 새 '7일보다 지난 시각 금지' 규칙은 등록 `POST` 에도 적용된다. 리뷰어가 "의도한 변경인가요?"라고 묻지 않도록 선제로 적었다.
- **리뷰 포인트**: 검증 순서(소유 확인 뒤 시각 검증)와, review-lint 가 남긴 ResponseEntity 확인 항목의 사유.

확인된 것과 가정한 것을 나눠 둔다.

| 구분 | 내용 |
|---|---|
| 확인된 것 | 커밋·diff 통계, 열린 PR 없음, 템플릿 존재와 섹션명, lint 결과, 컴파일·테스트 통과, 같은 컨트롤러 기존 메서드 7개는 DTO 직접 반환 |
| 가정한 것 | (a) 7일 규칙이 등록에도 적용된다는 점은 커밋 제목 "등록·수정 공통"과 공용 검증기 구조에서 도출했다. (b) ResponseEntity 확인 항목은 "이 PR 이 컨트롤러 메서드를 새로 추가하지 않고 기존 `PUT` 의 반환 방식도 바꾸지 않았다"는 변경 설명에 근거해 해당 없음으로 판단했다. diff 에서 새 메서드나 반환 타입 변경이 보이면 사유 문구를 고쳐야 한다. (c) `GlucoseRecordController.java` +4/-1 의 정확한 내용은 변경 설명만으로는 알 수 없어, 표에는 "수정 `PUT` 에 시각 검증이 걸리도록 연결"로만 적었다 |

사용자 확인이 필요한 것 두 가지.

1. '7일' 규칙을 도입한 업무 사유는 본문에 쓰지 않았다. 제가 지어내면 안 되는 설계 사유라서 비워 뒀다. 한 줄 알려주시면 기존 동작 변경 표의 "의도" 칸에 추가한다.
2. 7일을 넘긴 기존 기록을 `PUT` 으로 고칠 때, 시각을 바꾸지 않아도 400 이 나는지는 이번 입력으로 확인하지 못했다. 그리고 등록의 미래 시각 위반 응답 코드가 기존과 같은지도 확인하지 못했다. 둘 다 서비스 diff 를 보면 바로 확인되며, 다르면 기존 동작 변경 섹션에 한 줄 보강한다.

## 3. PR 본문

제목: `feat: 혈당 기록 시각 검증 공용화 (등록·수정 공통)`

````markdown
## Why need this PR❓

- 혈당 기록 **수정(`PUT`)에는 시각 검증이 전혀 없어서**, 미래이거나 아주 오래전인 시각으로도 고칠 수 있었다. 등록(`POST`)에만 '미래 시각 금지' 검증이 있었고, 과거 시각 제한은 어느 경로에도 없었다.
- **원인**: 시각 검증이 등록 경로에만 붙어 있어 수정 경로가 같은 규칙을 쓰지 못했다.

## Changes ✌️

**파일 5개, +150 / -3 lines** (혈당 기록 등록·수정 경로, 인터페이스 변경 없음)

| 파일 | 변경 |
|---|---|
| `RecordTimeValidator.java` (신규) | 기록 시각 검증을 한곳에 모은 공용 검증기. 등록에 있던 '미래 시각 금지'를 옮겨오고 '7일보다 지난 시각 금지'를 새로 추가. 위반 시 400 `GLUCOSE_RECORD_TIME_OUT_OF_RANGE` |
| `GlucoseRecordService.java` | 등록의 시각 검증을 공용 검증기 호출로 바꾸고, 수정에도 같은 검증을 추가. 수정은 소유 확인 뒤에 시각 검증 |
| `GlucoseRecordController.java` | 수정 `PUT /api/v1/glucose-records/{id}` 에 시각 검증이 걸리도록 연결 |
| `RecordTimeValidatorTest.java` (신규) | 공용 검증기 단위 테스트 |
| `GlucoseRecordServiceTest.java` | 등록·수정에서 시각 검증이 걸리는지 확인하는 서비스 테스트 추가 |

## 기존 동작 변경

| 경로 | 기존 | 변경 후 |
|---|---|---|
| 수정 `PUT /api/v1/glucose-records/{id}` | 시각 검증 없음 (어떤 시각이든 통과) | 미래 시각이거나 7일보다 지난 시각이면 400 `GLUCOSE_RECORD_TIME_OUT_OF_RANGE` |
| 등록 `POST` | 미래 시각만 거부 | 미래 시각 + 7일보다 지난 시각을 거부 (새 규칙이 등록에도 적용). 응답은 400 `GLUCOSE_RECORD_TIME_OUT_OF_RANGE` |

의도: 등록과 수정이 같은 시각 규칙을 쓰도록 한곳(`RecordTimeValidator`)으로 모음.

## 리뷰 포인트

- 검증 순서: 서비스에서 소유 확인을 먼저 하고 그 뒤에 시각 검증을 한다. 남의 기록을 수정하려는 요청은 시각이 잘못돼도 소유 확인 실패가 먼저 응답된다.
- review-lint 확인 항목 중 해당 없음: `ResponseEntity` 규칙(05) — 컨트롤러 메서드를 새로 추가하지 않고 기존 `PUT` 에 검증만 연결했다. 반환 방식은 같은 컨트롤러 기존 메서드 7개와 같이 DTO 직접 반환 그대로다.

## Test list 📝

- [x] 최신 dev 를 합친 상태에서 `./gradlew :pghd:compileTestJava` 통과
- [x] `./gradlew :pghd:test` 통과

## Screenshoot 🌅 (optional)

해당 없음 (서버 변경)
````

## 4. 자기 검증 체크리스트

| # | 항목 | 결과 |
|---|---|---|
| 1 | 저장소 템플릿 확인, 섹션명 그대로 | 통과. `pull_request_template.md` 존재를 확인했고 `## Why need this PR❓` / `## Changes ✌️` / `## Test list 📝` / `## Screenshoot 🌅 (optional)` 를 이모지와 철자(Screenshoot)까지 그대로 썼다. 템플릿 섹션의 상대 순서도 유지했다. 템플릿에 없는 조건부 섹션 2개는 Changes 뒤, Test list 앞에 넣었다 |
| 2 | 분량 100~200줄 이내, 코드·SQL·mermaid 없음 | 통과. 본문 약 50줄, 코드 블록 없음 |
| 3 | Why 현상 + 원인 1~2문장 | 통과 |
| 4 | Changes 파일별 표, 1파일 1줄, 스니펫 없음 | 통과 |
| 5 | 측정 결과 (측정 있을 때만) | 해당 없음. 운영 측정이 없어 섹션 생략 |
| 6 | 배포 (Canary 있을 때만) | 해당 없음. 섹션 생략 |
| 7 | 후속 작업 (별도 PR 있을 때만) | 해당 없음. 섹션 생략 |
| 8 | Test list 포함 | 통과 |
| 9 | 사람 친화 표현 | 통과. 영문 jargon 없음, 상대 시점(D+N) 없음. '7일'은 규칙 값이라 상대 날짜 표기가 아님 |
| 10 | `docs/...` 상대 링크 0개 | 통과. 링크 없음 |
| 11 | target branch | 통과. `dev` |
| 12 | AI 공동작성자 표기 없음 | 통과. Co-authored-by 와 AI 생성 표기 줄 모두 넣지 않았다 |
| 13 | 기존 PR 있으면 갱신 | 해당 없음. 열린 PR 이 없어 신규 생성 |
| 14 | 품질 게이트 (review-lint 위반 0건, self-code-reviewer 실행) | 통과. 위반 0건, 확인 1건은 해당 여부 판단 후 리뷰 포인트에 사유를 기재. self-code-reviewer 는 이번 세션에서 지적 0건 |
| 15 | 기존 동작 변경 섹션 | 통과. 수정 `PUT` 의 검증 신설과 등록 `POST` 에 새 7일 규칙 적용을 표로 기재 |
| 16 | 리뷰 포인트 (실패 시 동작·범위 밖 위험·lint 확인 사유) | 통과. 검증 순서와 ResponseEntity 확인 항목 사유를 기재. 범위 밖 위험은 알려진 것이 없어 쓰지 않았다 |
| 17 | 최신 dev 병합 컴파일, 구현체 grep | 통과. 병합 상태 `compileTestJava` 통과. 인터페이스 변경이 없어 구현체 grep 은 해당 없음 |
