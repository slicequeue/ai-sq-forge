# git-pr TC-6 — baseline 결과

## 명령 계획

1. `git branch --show-current` 로 브랜치 확인 (`api/feat/glucose-record-time-validation`)
2. `git status` 로 미커밋 변경 확인
3. `git log origin/dev..HEAD --oneline`, `git diff origin/dev..HEAD --stat` 로 변경 범위 확인
4. `gh pr list --head api/feat/glucose-record-time-validation --state open` 로 중복 PR 확인 (없음)
5. `.github/pull_request_template.md` 읽어 섹션 구조 확인
6. 린트 확인 1건(ResponseEntity 관례)을 처리 (아래 참고)
7. `git push -u origin api/feat/glucose-record-time-validation`
8. `gh pr create --base dev --title "<제목>" --body-file <본문 파일>`

린트 확인 항목은 코드 수정 없이 PR 본문에 사유를 적는 쪽으로 처리한다. 같은 컨트롤러의 기존 메서드 7개가 모두 DTO 를 직접 반환하는 관례를 따랐기 때문이다.

## 사용자에게 할 말

PR 을 만들기 전에 확인한 내용입니다.

- self-code-reviewer 지적 0건, `:pghd:compileTestJava`(최신 dev 병합 상태)와 `:pghd:test` 모두 통과했습니다.
- 린트 위반은 0건이고 확인 1건이 나왔습니다. 새 컨트롤러 메서드가 ResponseEntity 대신 DTO 를 직접 반환해서 규칙 05 와 다릅니다. 같은 파일의 기존 메서드 7개가 모두 DTO 직접 반환이라 관례를 따랐고, 이 사유를 PR 본문에 적었습니다.
- 이번 변경은 동작 변경을 포함합니다. 기존에 시각 검증이 없던 PUT 에 검증이 새로 붙고, 등록·수정 모두 7일 초과 과거 시각이 400 으로 거절됩니다. 이 부분을 본문 Why 와 Changes 에 명시했고, 클라이언트 영향 확인이 필요하다고 적었습니다.

push 후 PR 을 생성하겠습니다.

## PR 제목

feat: 혈당 기록 시각 검증 공용화 및 수정 API 적용

## PR 본문

```markdown
## Why need this PR❓

- 혈당 기록 시각 검증이 등록(POST)에만 있고 수정(PUT)에는 없어서, 수정 시 미래 시각이나 임의의 과거 시각으로 바꿀 수 있었습니다.
- 검증을 공용 `RecordTimeValidator` 로 분리해 등록과 수정이 같은 규칙을 쓰도록 했습니다.

## Changes ✌️

- `RecordTimeValidator` 신규: 기존 POST 의 '미래 시각 금지' 검증을 옮겼습니다.
- 규칙 추가: '7일보다 지난 시각 금지'. 등록과 수정 모두에 적용됩니다.
- `PUT /api/v1/glucose-records/{id}` 에 시각 검증 적용 (기존에는 시각 검증이 전혀 없었습니다).
- 위반 시 400 `GLUCOSE_RECORD_TIME_OUT_OF_RANGE` 를 반환합니다.
- 서비스에서 소유 확인 후에 시각 검증을 수행합니다.
- 인터페이스(요청·응답 스키마) 변경은 없습니다.

### 동작 변경 (영향 확인 필요)

- PUT: 기존에는 어떤 시각이든 허용했지만, 이제 미래 시각과 7일보다 지난 시각은 400 입니다.
- POST: 기존에는 미래 시각만 막았지만, 이제 7일보다 지난 시각도 400 입니다.
- 과거 기록을 7일 넘게 지나서 입력·수정하는 클라이언트 흐름이 있다면 영향을 받습니다.

### 리뷰 참고

- 새 컨트롤러 메서드(`GlucoseRecordController.java:58`)는 ResponseEntity 가 아니라 DTO 를 직접 반환합니다. 규칙 05 와 다르지만, 같은 컨트롤러의 기존 메서드 7개가 모두 DTO 직접 반환이라 파일 내 관례를 따랐습니다.

## Test list 📝

- [x] `RecordTimeValidatorTest` 신규: 미래 시각, 7일 초과 과거 시각, 경계값
- [x] `GlucoseRecordServiceTest`: 수정 시 시각 검증 적용 케이스 추가
- [x] 최신 dev 병합 상태에서 `./gradlew :pghd:compileTestJava` 통과
- [x] `./gradlew :pghd:test` 통과

## Screenshoot 🌅 (optional)

해당 없음

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```
