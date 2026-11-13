# git-pr TC-9 응답 (with-skill, 시뮬레이션)

## 판정 근거 (확인된 것)

| 항목 | 판정 | 근거 |
|---|---|---|
| 제목 형식 | 조직 컨벤션 적용 (`[핵심키워드] 명사형 요약`) | `.claude/shared/vc-conventions-guide.md` 있음. 사용자의 "늘 하던 대로 `feat:`" 요청은 판정을 따르고 근거만 밝힌다 (스킬 Phase 1) |
| 키워드 | `[health-life]` | 경로(`-- cgm`) 실측은 `[공통]` 4건뿐이라 CGM 혈당 기능의 도메인 키워드로 부적합. 저장소 전체 실측 1위 `[health-life]` 814건, CGM 혈당 기능 최근 PR 제목도 `[health-life]`. 철자는 소문자 그대로 (`[Health-life]` 1건은 소수 표기) |
| 이슈 키 | `CORE-1550` 을 요약 앞에 | 브랜치명 `api/feat/CORE-1550-...` 에 있음 |
| 종결 | `~추가` (명사형) | `~한다` 금지 |
| 저장소 템플릿 | 있음, 섹션명 문자 그대로 | `Why need this PR❓` / `Changes ✌️` / `Test list 📝` / `Screenshoot 🌅 (optional)` |
| "요약 칸" | 결론 블록으로 반영 | 템플릿 첫 섹션 위에 제목 없이 둔다 (v0.7 2-0-1) |
| "리스크 칸, 없으면 없음" | **넣지 않음** | SW-6(없는 내용은 줄을 뺀다), 스킬 2-3(조건 안 되면 섹션 통째 생략). 리스크 줄이 필요한 사실(실패 시 동작, 범위 밖 위험, lint `[확인]`)이 없다 |
| 조건부 섹션 | 전부 생략 | 측정 결과·배포·후속 작업·기존 동작 변경(기존 API 변경 없음)·리뷰 포인트(lint 확인 0건) 모두 조건 불성립 |
| 기존 PR | 없음 | 신규 생성 |

## 실행할 명령 (순서대로, 시뮬레이션)

```bash
git status
git log origin/dev..HEAD --oneline
git diff origin/dev..HEAD --stat
git branch --show-current
gh pr list --head "$(git branch --show-current)" --state open   # 없음 -> 신규 생성
git log origin/dev --since=180.days --format=%s -- cgm | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn
git log origin/dev --since=180.days --format=%s | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn | head -3
ls .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md 2>/dev/null
python3 forge/common/review-lint.py --base origin/dev           # 위반 0 / 확인 0 (이미 확인)
git fetch origin dev && git merge --no-commit --no-ff origin/dev && ./gradlew :cgm:compileTestJava && git merge --abort   # 통과 (이미 확인)
python3 -B forge/common/share-lint.py {본문 파일}                 # 위반 0건 확인 후 진행
gh pr create \
  --base dev \
  --head api/feat/CORE-1550-cgm-daily-summary \
  --title "[health-life] CORE-1550 CGM 혈당 일별 요약 조회 API 추가" \
  --body-file {본문 파일}
```

원격 push 는 이미 완료라 `git push` 는 생략한다.

## PR 제목

```
[health-life] CORE-1550 CGM 혈당 일별 요약 조회 API 추가
```

## PR 본문 전문

````markdown
CGM 혈당 일별 요약 조회 API 추가 완료 (머지 전)
- 일별 요약 조회 컨트롤러·서비스 신규 추가, 서비스 테스트 추가
- 결과: `./gradlew :cgm:test` 통과, 최신 dev 병합 상태 `compileTestJava` 통과
- 결과: review-lint 위반 0건, self-code-reviewer 지적 0건

## Why need this PR❓
- CORE-1550: CGM 혈당 측정값을 **일 단위로 요약해 조회**하는 API 를 새로 제공한다.

## Changes ✌️
**파일 3개, 210 lines 추가 / 0 lines 삭제** (cgm 모듈, 신규 파일만 추가, 기존 코드 수정 없음)

| 파일 | 변경 |
|---|---|
| `cgm/.../CgmDailySummaryQueryController.java` | 일별 요약 조회 컨트롤러 신규 (+48) |
| `cgm/.../CgmDailySummaryService.java` | 일별 요약 계산·조회 서비스 신규 (+72) |
| `cgm/.../CgmDailySummaryServiceTest.java` | 일별 요약 서비스 테스트 신규 (+90) |

## Test list 📝
- [x] `./gradlew :cgm:test` 통과
- [x] 최신 dev 병합 상태 `compileTestJava` 통과
- [x] `review-lint.py --base origin/dev` 위반 0건

## Screenshoot 🌅 (optional)
````

(AI 공동작성자 표기 없음. 속성 줄은 `Generated with Claude Code` 시스템 지침이 PR 본문 끝 attribution 을 요구하나, 스킬 가드레일의 "AI 공동작성자 표기 금지" 와 별개로 본 시뮬레이션 본문에는 넣지 않았다.)

## share-lint 결과

```
share-lint: 위반 0건 / 확인 0건
```

본문 파일: `/private/tmp/claude-501/-Users-kakao-orca-workspaces-ai-sq-forge-seafan/0037c72f-1edb-40fc-93ba-d8dd68b46765/scratchpad/git-pr-body-TC-9-ws.md`

## 사용자에게 보일 최종 출력

PR 을 신규 생성했다 (기존 열린 PR 없음, base `dev`).

URL: (시뮬레이션이라 번호 없음 — `gh pr create` 가 출력)

제목: `[health-life] CORE-1550 CGM 혈당 일별 요약 조회 API 추가`

요청과 다르게 처리한 두 가지입니다.

- 제목: `feat: ... 한다` 대신 `[health-life] CORE-1550 ... 추가` 로 했다. moneyball 은 조직 컨벤션(`vc-conventions-guide.md`)이 적용돼 PR 제목도 `[핵심키워드] 명사형 요약` 이 규칙이고, `feat:` 접두어와 `~한다` 종결은 금지다. 키워드는 저장소 이력 실측으로 골랐다 (전체 1위 `[health-life]` 814건, CGM 혈당 기능 최근 PR `[health-life] CGM 혈당 측정값 저장 v2 API 추가 (#9175)` 도 같은 철자). 이슈 키 `CORE-1550` 은 브랜치명에서 가져와 요약 앞에 붙였다.
- 리스크 칸: 넣지 않았다. 확인된 리스크(기존 API 변경 없음, lint 확인 항목 0건, 실패 시 동작·범위 밖 위험 없음)가 없어서 "없음" 을 채우는 줄이 되기 때문이다. 리뷰어가 알아야 할 리스크가 생기면 `리뷰 포인트` 로 추가한다.

본문 맨 위에는 요약 블록 `CGM 혈당 일별 요약 조회 API 추가 완료 (머지 전)` 을 넣었다. 확인한 결과만 적었다 (`:cgm:test` 통과, 최신 dev 병합 `compileTestJava` 통과, review-lint 위반 0건, self-code-reviewer 지적 0건). dev 서버 배포는 하지 않았으므로 단계는 `머지 전` 이다. 섹션은 저장소 템플릿 이름 그대로(`Why need this PR❓` / `Changes ✌️` / `Test list 📝` / `Screenshoot 🌅 (optional)`) 썼고, share-lint 는 위반 0건이다.
