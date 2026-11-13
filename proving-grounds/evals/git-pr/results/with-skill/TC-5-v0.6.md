# git-pr TC-5 — with-skill(v0.6) 재실행 결과

## 1. 명령 계획

시뮬레이션이라 실제로 실행하지 않았다. 상황에 주어진 결과는 그대로 쓰고, 없는 결과는 실행할 명령과 분기만 적는다.

### Phase 1. 변경사항 분석

| 순서 | 명령 | 결과 / 분기 |
|---|---|---|
| 1 | `git status` | 미커밋 변경 확인. 있으면 사용자에게 알린다 (상황에 없음, 실행 필요) |
| 2 | `git log origin/dev..HEAD --oneline` | 주어진 결과 사용. 커밋 3개 (엔티티 / 배치 잡 / 테스트) |
| 3 | `git diff origin/dev..HEAD --stat` | 주어진 결과 사용. 신규 파일 4개, +233 / -0 |
| 4 | `git branch --show-current` | `api/feat/ai-nudge-scheduled-send` |
| 5 | `gh pr list --head api/feat/ai-nudge-scheduled-send --state open` | 열린 PR 없음 (주어짐) → 신규 생성. `gh pr edit` 아님 |
| 6 | 원격 push 확인 | push 완료 (주어짐) → `git push` 불필요 |

base 는 `dev` 다. hotfix 요청이 없다.

### 푸시 전 품질 게이트 (v0.4, v0.5)

| 순서 | 명령 | 결과에 따른 분기 |
|---|---|---|
| 7 | `ls forge/common/review-lint.py` 후 있으면 `python3 forge/common/review-lint.py --base origin/dev` | 결과는 상황에 없다. 위반 1건 이상이면 PR 생성을 멈추고 사용자에게 보고한다. 위반 0건이면 계속한다. `[확인]` 이 출력된 항목이 있을 때만 사유를 리뷰 포인트에 적는다. `[확인]` 이 0건이면 적을 것이 없다 |
| 8 | `self-code-reviewer` 를 이 브랜치에서 아직 돌리지 않았으면 먼저 돌린다 | 지적이 나오면 고친 뒤 7번부터 다시 한다 |
| 9 | `git fetch origin dev && git merge --no-commit --no-ff origin/dev`, 이어서 `./gradlew :{module}:compileTestJava`, 이어서 `git merge --abort` | 컴파일 실패면 PR 생성을 멈추고 보고한다. `{module}` 은 diff 경로로 확정한다 (경로 앞부분이 stat 에 없어 실행 시 확인) |
| 10 | 인터페이스 구현체 grep (`grep -rn "implements ..." */src/test */src/main`) | 이번 diff 는 신규 파일 4개뿐이라 기존 인터페이스를 바꾸지 않은 것으로 보인다. 다만 `NudgeScheduleSendJobConfig` 가 기존 인터페이스를 구현하거나 기존 파일을 건드렸는지 diff 로 확인한다. 바꾼 인터페이스가 없으면 grep 은 생략한다 |

7~9번 중 하나라도 실패하면 아래 12번은 실행하지 않는다.

### Phase 2-0. 저장소 PR 템플릿 확인

| 순서 | 명령 | 결과 |
|---|---|---|
| 11 | `ls .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md 2>/dev/null` | `.github/pull_request_template.md` 있음 (주어짐). 섹션명을 이모지까지 그대로 쓰고 순서를 따른다 |

### Phase 3. 생성

| 순서 | 명령 |
|---|---|
| 12 | `gh pr create --base dev --head api/feat/ai-nudge-scheduled-send --title "feat: AI 넛지 메시지 예약 전송 배치 추가" --body "$(cat <<'EOF' ... EOF)"` (본문은 아래 3번) |
| 13 | 출력된 PR URL 을 한 줄로 알린다. "신규 생성" 이라고 적는다 |

Co-authored-by 같은 AI 공동작성자 표기는 넣지 않는다. 본문에 `docs/...` 상대 링크도 없다.

## 2. 사용자에게 할 말

PR 을 올리기 전에 품질 게이트(review-lint, self-code-reviewer, 최신 dev 병합 컴파일)를 먼저 돌립니다. 위반이 나오면 멈추고 알려드리겠습니다. 통과하면 아래 본문으로 `dev` 대상 PR 을 새로 만듭니다.

요청하신 두 항목은 이번 PR 에 넣지 않았습니다.

- 운영 지표 측정: 배포 전 기능이라 측정값이 아직 없습니다. 비어 있는 표를 만들지 않으려고 "측정 결과" 섹션을 생략했습니다. 배포 후 지표가 생기면 그때 PR 본문에 추가하겠습니다.
- 배포 순서: 이 스킬의 "배포" 섹션은 Canary 같은 단계적 배포가 있을 때만 씁니다. 이번에는 일반 머지 후 배포라 적을 순서가 없어서 생략했습니다. 대신 리뷰어가 알아야 할 사실인 신규 테이블 마이그레이션 포함 여부를 리뷰 포인트에 한 줄 적었습니다. 단계적 배포를 하게 되면 알려주세요. 그때 "배포" 섹션을 추가합니다.

| 구분 | 내용 |
|---|---|
| 확인된 것 | 템플릿 섹션명, 브랜치·base, 커밋 3개, 변경 파일 4개와 줄 수, 열린 PR 없음, 원격 push 완료 |
| 가정한 것 | Why 문장의 동기(예약 전송이 없었다는 점)는 커밋 메시지에서 추정했습니다. 실제 배경이 다르면 알려주세요. 재평가 트리거는 Why 를 직접 정정해 주시는 경우입니다 |
| 아직 못 확인한 것 | review-lint 결과, self-code-reviewer 결과, `compileTestJava` 결과. 그래서 Test list 는 체크하지 않은 상태로 둡니다 |

제목은 커밋 메시지 형식으로 줄였습니다: `feat: AI 넛지 메시지 예약 전송 배치 추가`

## 3. PR 본문

**제목**: `feat: AI 넛지 메시지 예약 전송 배치 추가`

````markdown
## Why need this PR❓

AI 넛지 메시지를 정해진 시각에 보내는 **예약 전송**이 없어서, 예약 정보를 저장하는 엔티티와 이를 보내는 배치 잡을 추가했다.

## Changes ✌️

**파일 4개, 233 lines 추가 / 0 lines 삭제** (모두 신규 파일)

| 파일 | 변경 |
|---|---|
| `NudgeSchedule.java` | 넛지 메시지 예약 전송 정보를 담는 엔티티 신규 |
| `NudgeScheduleSendJobConfig.java` | 예약된 넛지 메시지를 보내는 배치 잡 설정 신규 |
| `V2026_09_10__create_nudge_schedule.sql` | 예약 전송 테이블 생성 마이그레이션 신규 |
| `NudgeScheduleSendJobTest.java` | 예약 전송 배치 잡 테스트 신규 |

## 리뷰 포인트

- 신규 테이블 생성 마이그레이션(`V2026_09_10__create_nudge_schedule.sql`)이 포함돼 있어, 머지 후 배포 시 DB 스키마가 함께 바뀐다

## Test list 📝

- [ ] `./gradlew :{module}:compileTestJava` 최신 dev 병합 상태 통과
- [ ] `NudgeScheduleSendJobTest` 통과

## Screenshoot 🌅 (optional)
````

본문 약 25줄. 코드 스니펫, SQL, mermaid, `docs/` 링크 없음.

## 4. 자기 검증 체크리스트 점검

| # | 항목 | 결과 | 근거 |
|---|---|---|---|
| 1 | 저장소 템플릿 | 통과 | `## Why need this PR❓` / `## Changes ✌️` / `## Test list 📝` / `## Screenshoot 🌅 (optional)` 를 이모지까지 그대로 사용. 템플릿 순서 유지 |
| 2 | 분량 | 통과 | 약 25줄, 스니펫 없음 |
| 3 | Why | 통과 | 현상 + 해결 1문장. 동기는 추정이라 위 2번에서 가정으로 표기 |
| 4 | Changes | 통과 | 파일별 표, 1파일 1줄, 233 / 0 줄 (45+80+18+90) |
| 5 | 측정 결과 | 해당 없음, 섹션 생략 | 측정값 없음. 사용자에게 사유 설명. 빈 표나 "해당 없음" 한 줄 없음 |
| 6 | 배포 | 해당 없음, 섹션 생략 | Canary 없음. 사용자에게 사유 설명 |
| 7 | 후속 작업 | 해당 없음, 섹션 생략 | 분리할 별도 PR 항목을 아는 것이 없음 |
| 8 | Test list | 통과 | 템플릿 섹션으로 포함. 실행하지 않은 것은 체크하지 않음 |
| 9 | 사람 친화 표현 | 통과 | 영문 jargon 없음, 상대 시점 없음 |
| 10 | 링크 | 통과 | `docs/` 상대 링크 0개. 근거 문서가 없어 Notion 안내 문구도 넣지 않음 |
| 11 | target branch | 통과 | `dev` |
| 12 | AI 공동작성자 | 통과 | 없음. 하네스 컨텍스트가 PR 말미에 붙이라고 안내한 생성 표기 문구도 이 스킬의 AI 표기 금지 규칙을 따라 넣지 않음 |
| 13 | 기존 PR | 통과 | 열린 PR 없음, 신규 생성 |
| 14 | 품질 게이트 | 미실행, 계획만 | 시뮬레이션이라 실행하지 않음. 위 1번의 7~8번을 통과해야 PR 생성 |
| 15 | 기존 동작 변경 | 통과 | 신규 파일만이라 기존 경로의 응답·검증·에러 변경이 없음. 섹션 없음 |
| 16 | 리뷰 포인트 | 통과 | 실제 사실 1건(신규 테이블 마이그레이션)만 적음. "변경 없음"·"해당 없음" 채움 줄 0건. lint `[확인]` 이 출력되면 그 항목만 추가 |
| 17 | 최신 dev 병합 컴파일 | 미실행, 계획만 | 위 1번의 9번에서 실행. 인터페이스를 바꾸지 않은 신규 파일 구성이라 구현체 grep 은 생략 가능 |
| 18 | 선택 섹션 위치 | 통과 | 리뷰 포인트가 `Changes` 뒤, `Test list` 앞. `Screenshoot` 은 템플릿 순서대로 맨 뒤 |
