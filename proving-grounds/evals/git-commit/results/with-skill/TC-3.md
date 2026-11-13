# git-commit TC-3 응답 (with-skill, 시뮬레이션)

## 0. 형식 판정

- `ls .claude/shared/vc-conventions-guide.md` 결과: 있음 -> **A. 조직 컨벤션** `[핵심키워드] 명사형 요약`
- 브랜치명이 `api/feat/...` 이고 사용자 요청이 일반적인 커밋이어도, 접두어(`feat:`)는 쓰지 않는다. 판정 결과를 따른다.
- 조직 컨벤션 원문 폴더 존재 여부는 시뮬레이션에 명시되지 않았으므로 가이드 4절 요약 규칙으로 진행한다.

## 1. 변경 분석 (git status / git diff 기준)

| 파일 | 도메인 | 비고 |
|------|--------|------|
| `claim/.../ClaimStatusService.java` | 위임청구 지급 완료 알림 | 이벤트 발행 |
| `claim/.../ClaimStatusServiceTest.java` | 위임청구 지급 완료 알림 | 위 변경의 테스트 |
| `message/.../push/PushTemplateCode.java` | 위임청구 지급 완료 알림 | 푸시 템플릿 코드 |
| `message/.../push/ClaimPaidPushListener.java` (신규) | 위임청구 지급 완료 알림 | 이벤트 수신 후 푸시 발송 |
| `.github/workflows/pr-test.yml` | CI | 작업과 무관한 timeout 변경 |

- pasta-api 모듈 파일 수정 없음 -> spotlessApply 실행 대상 아님.

### 그룹화 판단

- **claim + message 4개 파일은 한 커밋**으로 묶는다. 이벤트 발행(claim)과 이벤트 수신·푸시 발송(message)은 한 기능의 양 끝이라, 나누면 발행만 있고 수신이 없는 반쪽 커밋이 된다. 나눌 수 없는 사유가 있으므로 한 커밋이 맞다. 두 경로의 최다 키워드가 모두 `[공통]` 이라 복수 키워드 표기는 필요 없다.
- **`.github/workflows/pr-test.yml` 은 별도 커밋**으로 분리한다. CORE-1561 과 무관한 CI 변경이라 도메인이 다르다. "한 번에 올려도 돼" 요청은 한 번의 푸시·작업 흐름으로 받아들이되, 커밋은 도메인 기준으로 2개로 나눈다. 무관한 변경을 CORE-1561 커밋에 섞으면 이력 추적과 revert 단위가 깨진다.

## 2. 키워드 실측 (시뮬레이션 결과)

```bash
git log origin/main --since=180.days --format=%s -- claim | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn
# 5 [공통] / 3 [health-life]
git log origin/main --since=180.days --format=%s -- message | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn
# 6 [공통] / 2 [health-life] / 1 [삼성생명]
git log origin/main --since=180.days --format=%s -- .github | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn
# 12 [공통] / 3 [CI/CD]
```

- 커밋 1(claim·message): claim 5건, message 6건 모두 `[공통]` 최다 -> `[공통]`
- 커밋 2(.github): `[공통]` 12건 최다 -> `[공통]` (`[CI/CD]` 는 3건이라 채택하지 않음)
- 참고: 최근 위임청구 기능 제목 `[health-life] ...(#9214)` 이 있으나, 규칙은 바꾼 경로 기준 실측 최다 키워드를 따르므로 `[공통]` 이 우선이다. health-life 가 더 적합하다고 판단되면 사용자가 지정해 달라고 출력에 한 줄 남긴다.
- 이슈 키: 브랜치명(`CORE-1561`)과 사용자 입력에 있으므로 커밋 1 요약 앞에 넣는다. 커밋 2 는 이슈와 무관하므로 넣지 않는다(지어내거나 끌어다 붙이지 않음).

## 3. 실행할 명령 (순서대로)

```bash
# 1. 현황 파악
ls .claude/shared/vc-conventions-guide.md
git status
git diff main

# 2. 키워드 실측
git log origin/main --since=180.days --format=%s -- claim | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn
git log origin/main --since=180.days --format=%s -- message | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn
git log origin/main --since=180.days --format=%s -- .github | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn

# 3. 커밋 1: CORE-1561 기능 (파일을 명시해서 stage)
git add claim/src/main/java/.../ClaimStatusService.java \
        claim/src/test/java/.../ClaimStatusServiceTest.java \
        message/src/main/java/.../push/PushTemplateCode.java \
        message/src/main/java/.../push/ClaimPaidPushListener.java
git commit -m "[공통] CORE-1561 위임청구 지급 완료 시 푸시 알림 발송 추가" \
           -m "- 위임청구 상태가 '지급 완료'로 바뀔 때 알림 이벤트 발행
- 지급 완료 푸시 템플릿 코드 추가
- 이벤트를 받아 푸시를 발송하는 ClaimPaidPushListener 신규"

# 4. 커밋 2: CI 설정 (무관 변경 분리)
git add .github/workflows/pr-test.yml
git commit -m "[공통] PR 테스트 job timeout 20분에서 30분으로 변경"
```

- `git add -A`·`git add .` 는 쓰지 않는다(무관 파일 혼입 방지).
- 푸시는 요청에 없으므로 하지 않는다("한 번에 올려도 돼"는 커밋을 한 번에 처리해도 된다는 뜻으로 해석하되, 도메인이 달라 2커밋으로 나눔).

## 4. 최종 커밋 메시지 전문

### 커밋 1

```
[공통] CORE-1561 위임청구 지급 완료 시 푸시 알림 발송 추가

- 위임청구 상태가 '지급 완료'로 바뀔 때 알림 이벤트 발행
- 지급 완료 푸시 템플릿 코드 추가
- 이벤트를 받아 푸시를 발송하는 ClaimPaidPushListener 신규
```

### 커밋 2

```
[공통] PR 테스트 job timeout 20분에서 30분으로 변경
```

- 두 메시지 모두 `feat:` 등 접두어 없음, `~한다`·`~했음` 종결 없음(명사형 `~추가`·`~변경`), AI 공동작성자 표기 없음.

## 5. 사용자에게 보일 최종 출력

```
✓ 커밋 완료: [공통] CORE-1561 위임청구 지급 완료 시 푸시 알림 발송 추가
  형식: A 조직 컨벤션 (.claude/shared/vc-conventions-guide.md 존재)
  키워드: [공통] (claim 5건 / message 6건 최다, health-life 는 각 3건·2건)

✓ 커밋 완료: [공통] PR 테스트 job timeout 20분에서 30분으로 변경
  형식: A 조직 컨벤션 (.claude/shared/vc-conventions-guide.md 존재)
  키워드: [공통] (.github 12건 최다, CI/CD 3건)

안내
- 한 번에 올려도 된다고 하셨지만 pr-test.yml 변경은 CORE-1561 과 무관해서 별도 커밋으로 분리했습니다. 합치길 원하시면 말씀해 주세요.
- 위임청구 기능은 최근 이력에 [health-life] 제목도 있습니다. 이번에는 바꾼 경로(claim, message)의 실측 최다 키워드인 [공통] 을 썼고, [health-life] 로 바꾸길 원하시면 알려 주세요(신규 커밋이라면 amend 없이 다음 커밋부터 적용).
- 브랜치가 api/feat/... 이지만 조직 컨벤션 적용 프로젝트라 feat: 접두어는 쓰지 않았습니다.
```

## 6. 자기 검증

1. [x] `.claude/shared/vc-conventions-guide.md` 존재로 A 판정
2. [x] 제목이 `[키워드]` 로 시작, 접두어 없음
3. [x] 키워드를 경로별 `git log` 실측으로 선택(`[공통]`, 철자 그대로)
4. [x] 이슈 키 CORE-1561 은 요약 앞, 무관한 CI 커밋에는 넣지 않음
5. [x] 요약이 명사형 종결(`추가`, `변경`)
6. [x] 도메인이 다른 CI 변경은 분리, claim+message 는 한 기능이라 한 커밋(사유 명시)
7. [x] (B 항목 해당 없음)
8. [x] AI 공동작성자 표기 0건
