# git-pr TC-6 — with-skill(v0.6) 재실행 결과

## 1. 명령 계획

시뮬레이션 상황이 아래 Phase 1 명령의 결과를 이미 준다. 그 결과로 판단한 내용과, 실제로 실행할 명령만 적는다.

### Phase 1. 분석 (결과 확보 완료)

| 확인 | 결과 | 판단 |
|---|---|---|
| `git branch --show-current` | `api/feat/glucose-record-time-validation` | base 는 `dev` (hotfix 요청 없음) |
| `git log origin/dev..HEAD --oneline` | 커밋 1건 | 제목은 이 커밋 메시지 형식을 따른다 |
| `git diff origin/dev..HEAD --stat` | 5개 파일, +150 / -3 | Changes 표의 근거 |
| `gh pr list --head ... --state open` | 없음 | 신규 생성 (`gh pr edit` 아님) |
| `ls .github/pull_request_template.md` | 있음 | 섹션명을 이모지까지 그대로 사용 (2-0) |

### 푸시 전 품질 게이트 (하드 가드레일)

| 게이트 | 결과 | 처리 |
|---|---|---|
| `python3 forge/common/review-lint.py --base origin/dev` | 위반 0건, 확인 1건 | 위반 0건이라 푸시 가능. `[확인]` 1건은 PR 본문 "리뷰 포인트"에 사유를 적는다 |
| `self-code-reviewer` | 이번 세션에서 실행, 지적 0건 | 다시 돌리지 않는다 |
| 최신 dev 병합 상태 `./gradlew :pghd:compileTestJava` | 통과 | 확인 뒤 `git merge --abort` 로 병합 상태를 되돌린다 |
| `./gradlew :pghd:test` | 통과 | Test list 에 체크로 기록 |
| 인터페이스 구현체 전수 grep | 인터페이스 변경 없음 | 대상 아님. grep 생략 |

### 실제로 실행할 명령 (순서)

```bash
# 1. 병합 컴파일 확인 후 병합 상태 정리 (이미 통과한 확인을 되돌리는 정리 단계)
git merge --abort            # 병합 진행 중 상태일 때만

# 2. 원격에 없으므로 push
git push -u origin HEAD

# 3. 신규 PR 생성 (열린 PR 없음)
gh pr create \
  --base dev \
  --head api/feat/glucose-record-time-validation \
  --title "feat: 혈당 기록 시각 검증 공용화 (등록·수정 공통)" \
  --body "$(cat <<'EOF'
<아래 3절 본문>
EOF
)"
```

생성 후 PR URL 을 출력하고 "신규 생성" 한 줄을 덧붙인다.

## 2. 사용자에게 할 말

PR 올리기 전 게이트를 모두 확인했습니다. review-lint 위반은 0건이고 `[확인]` 1건이 있습니다. self-code-reviewer 는 이번 세션에서 이미 돌렸고 지적 0건입니다. 최신 dev 를 합친 상태의 `:pghd:compileTestJava` 와 `:pghd:test` 도 통과했습니다. 열린 PR 이 없어서 신규로 만들고, 원격에 아직 없어서 push 후 생성합니다.

본문은 저장소 PR 템플릿 섹션명(`Why need this PR❓` / `Changes ✌️` / `Test list 📝` / `Screenshoot 🌅 (optional)`)을 그대로 썼습니다. 선택 섹션은 두 개만 붙였습니다.

- **기존 동작 변경**: PUT 에 시각 검증이 새로 붙고, POST 에 7일 초과 과거 거부가 새로 생기기 때문입니다. 리뷰어가 "의도한 변경인가요?"라고 묻지 않도록 두 경로를 모두 적었습니다.
- **리뷰 포인트**: review-lint `[확인]` 1건(컨트롤러 반환 타입 관례)과, 소유 확인 뒤에 시각을 검증하는 순서 때문입니다.

측정 결과, 배포, 후속 작업 섹션은 해당 내용이 없어 만들지 않았습니다.

확인된 것과 가정한 것을 나눕니다.

| 구분 | 내용 |
|---|---|
| 확인된 것 | lint 출력(컨트롤러 58행 새 메서드가 `ResponseEntity` 반환, 같은 파일 기존 메서드 7개는 DTO 직접 반환), 변경 파일·줄 수, 소유 확인 후 시각 검증 순서, 위반 시 400 `GLUCOSE_RECORD_TIME_OUT_OF_RANGE`, 테스트·컴파일 통과 |
| 확인하지 못한 것 | 기존 POST 의 미래 시각 위반이 원래 같은 에러 코드였는지. 달라졌다면 "기존 동작 변경"에 POST 행 하나를 더 적어야 합니다. 이 부분은 본문에 단정하지 않고 "같은 규칙, 공용 검증으로 이동"까지만 썼습니다 |
| 확인하지 못한 것 | 7일 규칙을 추가한 배경 사유. 제공된 정보에 없어 Why 에 지어 쓰지 않았습니다 |
| 결정 필요 | 컨트롤러 반환 타입을 규칙 05(`ResponseEntity`)로 둘지 같은 파일 관례(DTO 직접 반환)에 맞출지. 위반이 아니라 확인 항목이라 규칙 05 를 따른 현재 상태로 올리고, 리뷰어에게 판단을 요청하는 문장으로 적었습니다. 관례에 맞추길 원하시면 알려주세요 |

AI 공동작성자 표기는 스킬 가드레일에 따라 넣지 않았습니다.

## 3. PR 본문

**제목**: `feat: 혈당 기록 시각 검증 공용화 (등록·수정 공통)`

**base**: `dev`

````markdown
## Why need this PR❓

혈당 기록의 **시각 검증이 등록(POST)에만 있고 수정(PUT)에는 없어서**, 수정으로는 미래 시각이나 아주 오래된 시각도 그대로 저장할 수 있었다.

**원인**: '미래 시각 금지' 검증이 등록 경로 안에만 있었다. 이 검증을 공용 `RecordTimeValidator` 로 옮겨 등록·수정이 같은 규칙을 쓰게 하고, '7일보다 지난 시각 금지' 규칙을 새로 추가했다.

## Changes ✌️

**파일 5개, +150 / -3 lines** (혈당 기록 등록·수정 경로, 인터페이스 변경 없음)

| 파일 | 변경 |
|---|---|
| `RecordTimeValidator.java` (신규) | 기록 시각이 미래이거나 7일보다 지났으면 거부하는 공용 검증 |
| `GlucoseRecordService.java` | 등록의 기존 미래 시각 검증을 공용 검증 호출로 교체, 수정에도 같은 검증 추가. 수정은 소유 확인 뒤에 시각을 검증 |
| `GlucoseRecordController.java` | 수정 요청이 시각 검증을 타도록 연결 |
| `RecordTimeValidatorTest.java` (신규) | 미래·7일 초과·경계값·정상 시각 검증 단위 테스트 |
| `GlucoseRecordServiceTest.java` | 등록·수정 각각의 시각 위반 거부와 소유 확인 순서 테스트 추가 |

## 기존 동작 변경

위반 시 응답은 400 `GLUCOSE_RECORD_TIME_OUT_OF_RANGE` 이다.

| 경로 | 바뀌는 점 | 기존 |
|---|---|---|
| `PUT /api/v1/glucose-records/{id}` | 미래 시각이거나 7일보다 지난 시각이면 400 | 시각 검증 없이 통과 |
| `POST` 등록 | 7일보다 지난 시각이면 400 (미래 시각 금지는 같은 규칙, 공용 검증으로 이동) | 7일보다 지난 시각도 통과 |

## 리뷰 포인트

- 검증 순서: 수정은 소유 확인 뒤에 시각을 검증한다. 다른 사용자의 기록이면 시각 오류가 아니라 소유 오류가 먼저 나간다
- review-lint 확인 항목: `GlucoseRecordController` 58행 새 메서드가 규칙 05 에 따라 `ResponseEntity` 를 반환한다. 같은 컨트롤러 기존 메서드 7개는 DTO 를 직접 반환하므로 관례와 다르다. 기존 관례에 맞출지 의견 부탁드린다

## Test list 📝

- [x] `./gradlew :pghd:test` 통과
- [x] 최신 dev 병합 상태 `./gradlew :pghd:compileTestJava` 통과
- [x] `review-lint.py --base origin/dev` 위반 0건

## Screenshoot 🌅 (optional)
````

본문 길이는 약 40줄이다 (100~200줄 이내 기준 충족, 코드 스니펫·mermaid·`docs/` 링크 없음).

## 4. 자기 검증 체크리스트 점검

| # | 항목 | 결과 |
|---|---|---|
| 1 | 저장소 템플릿 확인, 섹션명 이모지까지 그대로 | 통과. `Why need this PR❓`, `Changes ✌️`, `Test list 📝`, `Screenshoot 🌅 (optional)` 를 문자 그대로 사용, 템플릿 순서 유지 |
| 2 | 분량 100~200줄 이내, 스니펫 없음 | 통과. 약 40줄, 스니펫·SQL·mermaid 없음 |
| 3 | Why 현상 + 원인 1~2문장 | 통과. 배경 사유를 모르는 7일 규칙은 지어 쓰지 않음 |
| 4 | Changes 파일별 표, 1파일 1줄 | 통과 |
| 5 | 측정 결과 | 해당 없음. 측정이 없어 섹션 자체를 만들지 않음 |
| 6 | 배포 | 해당 없음. 섹션 없음 |
| 7 | 후속 작업 | 해당 없음. 섹션 없음 |
| 8 | Test list 항상 포함 | 통과 |
| 9 | 사람 친화 표현 | 통과. 영문 jargon 풀어쓰기, 상대 시점 단독 표기 없음 |
| 10 | 링크 가드레일 | 통과. `docs/` 링크 0개 |
| 11 | target branch | 통과. `dev` |
| 12 | AI 공동작성자 표기 없음 | 통과 |
| 13 | 기존 PR 있으면 갱신 | 해당 없음. 열린 PR 없어 신규 생성 |
| 14 | 품질 게이트 | 통과. review-lint 위반 0건, self-code-reviewer 실행(지적 0건) |
| 15 | 기존 동작 변경 | 통과. 바뀐 경로 전부(PUT·POST)를 섹션에 기재. 바뀌었으므로 섹션이 필요한 경우 |
| 16 | 리뷰 포인트 | 통과. 실제로 있는 것만 기재: 검증 순서(실패 시 동작), lint `[확인]` 1건 사유. "해당 없음"·"변경 없음" 채움 줄 0건 |
| 17 | 최신 dev 병합 컴파일 | 통과. `:pghd:compileTestJava` 통과. 인터페이스 변경 없어 구현체 grep 은 대상 아님 |
| 18 | 선택 섹션 위치 | 통과. `기존 동작 변경`·`리뷰 포인트` 가 `Changes` 뒤, `Test list` 앞. 템플릿의 `Screenshoot 🌅 (optional)` 는 맨 뒤에 그대로 둠 |

추가로 확인한 v0.6 규칙은 다음과 같다.

- 조건 미성립 섹션(측정 결과·배포·후속 작업)은 통째로 생략했다.
- lint 사유는 `[확인]` 이 실제 출력된 1건에만 적었다.
- 선택 섹션을 `Why`·`Changes` 앞에 두지 않았다.
