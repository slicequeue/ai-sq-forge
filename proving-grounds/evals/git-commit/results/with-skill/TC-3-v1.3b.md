# git-commit TC-3 (v1.3b) 시뮬레이션 응답

## 0. 형식 판정

- `.claude/shared/vc-conventions-guide.md` 있음 -> **A. 조직 컨벤션** `[핵심키워드] 명사형 요약`
- 브랜치명이 `api/feat/...` 이고 사용자가 "한 번에"라고 했지만, 판정 결과와 도메인 분리 규칙을 따른다. `feat:` 접두어는 쓰지 않는다.

## 변경 분석과 커밋 분할

| 파일 | 도메인 | 커밋 |
|------|--------|------|
| `claim/.../ClaimStatusService.java`, `claim/.../ClaimStatusServiceTest.java` | 위임청구 | 커밋 1 |
| `message/.../PushTemplateCode.java`, `message/.../ClaimPaidPushListener.java` | 위임청구 지급 완료 푸시 | 커밋 1 |
| `.github/workflows/pr-test.yml` | CI 설정 (CORE-1561 과 무관) | 커밋 2 |

- claim 과 message 변경은 "지급 완료 이벤트 발행 -> 리스너 푸시 발송"이라는 한 기능이다. 한 커밋으로만 의미가 성립하므로 합친다.
- 워크플로 변경은 기능이 없는 CI 설정이고 이슈와 무관하다. 도메인이 다르므로 별도 커밋으로 나눈다. "한 번에 올려도 돼"는 한 커밋으로 합치라는 허락이 아니라 push 를 한 번에 해도 된다는 뜻으로 읽는다. 한 커밋을 원하면 다시 말해 달라고 안내한다.

## 키워드 판정

- claim 경로 최다는 `[공통]`(5), message 경로 최다도 `[공통]`(6). 둘 다 범용 키워드다.
- 이번 변경은 특정 기능(위임청구)이므로 "기능 키워드 우선" 규칙을 적용한다. 같은 기능의 최근 제목 `[health-life] 위임청구 주민번호 중복 검사 ... (#9214)` 에서 `[health-life]` 를 쓴다. 경로 실측에서도 claim 의 2순위(3건)다.
- `.github` 경로는 12건 `[공통]` 이고 기능이 없는 CI 설정이므로 범용 키워드 `[공통]` 이 맞다.
- 복수 키워드는 불필요하다(도메인이 하나).
- 이슈 키: 브랜치명과 사용자 입력에 `CORE-1561` 이 있으므로 커밋 1 요약 앞에 넣는다. 워크플로 커밋은 이 이슈와 무관하므로 넣지 않는다(지어내지 않음).

## 실행할 명령 (순서대로)

1. `ls .claude/shared/vc-conventions-guide.md` (입력에서 확인됨, 재실행 불필요)
2. `git status`, `git diff dev` 로 변경 확인 (결과 필요: 입력에 status 요약만 있음)
3. spotless: pasta-api 모듈 변경이 없으므로 `./gradlew :pasta-api:spotlessApply` 는 실행하지 않는다. moneyball 에 별도 포맷터 지시는 없다.
4. 기능 키워드 보강 확인 (결과 필요, 건수 확정용): `git log origin/main --since=180.days --format=%s --grep='위임청구' | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn`
   - 입력 예시 제목으로 `[health-life]` 판단은 이미 가능하다. 이 명령은 출력에 적을 건수를 얻기 위한 것이다. 결과가 `[health-life]` 가 아닌 다른 키워드 최다로 나오면 그 키워드로 교체한다.
5. 커밋 1:
   - `git add claim/src/main/java/.../ClaimStatusService.java claim/src/test/java/.../ClaimStatusServiceTest.java message/src/main/java/.../push/PushTemplateCode.java message/src/main/java/.../push/ClaimPaidPushListener.java`
   - `git commit` (메시지는 아래)
6. 커밋 2:
   - `git add .github/workflows/pr-test.yml`
   - `git commit` (메시지는 아래)
7. `git status` 로 잔여 변경 없음 확인, `git log -2 --format=%s` 로 제목 확인
8. push 는 사용자 요청 범위("올려도 돼")에 따라 사용자 확인 후 `git push` (커밋 스킬의 범위 밖이므로 안내만)

## 최종 커밋 메시지 전문

### 커밋 1

```
[health-life] CORE-1561 위임청구 지급 완료 시 알림 이벤트 발행 및 푸시 발송 추가

- 위임청구 상태가 지급 완료로 바뀔 때 알림 이벤트 발행
- 이벤트를 받아 푸시를 발송하는 리스너와 푸시 템플릿 코드 추가
```

### 커밋 2

```
[공통] PR 테스트 job timeout 20분에서 30분으로 변경
```

두 메시지 모두 Co-authored-by 및 AI 관련 표기 없음. `feat:` 등 접두어 없음. 요약은 명사형(`추가`, `변경`)으로 끝난다.

## 사용자에게 보일 최종 출력

```
✓ 커밋 완료: [health-life] CORE-1561 위임청구 지급 완료 시 알림 이벤트 발행 및 푸시 발송 추가
  형식: A 조직 컨벤션 (.claude/shared/vc-conventions-guide.md 존재)
  키워드: [health-life] (claim·message 경로 최다는 범용 [공통] 5·6건이라, 같은 위임청구 기능 제목의 [health-life] 사용. 위임청구 제목 건수는 결과 필요)

✓ 커밋 완료: [공통] PR 테스트 job timeout 20분에서 30분으로 변경
  형식: A 조직 컨벤션 (.claude/shared/vc-conventions-guide.md 존재)
  키워드: [공통] (.github 경로 12건, 기능 없는 CI 설정이라 범용 키워드가 맞음)

참고
- 한 번에 올려 달라고 하셨지만 .github 워크플로 변경은 CORE-1561 과 도메인이 달라 별도 커밋으로 나눴습니다. 한 커밋을 원하시면 말씀해 주세요.
- 워크플로 커밋에는 CORE-1561 을 붙이지 않았습니다(이슈와 무관).
- 브랜치명은 api/feat/... 이지만 제목에 feat: 접두어는 쓰지 않습니다.
- push 는 하지 않았습니다. 필요하면 알려 주세요.
```

## 자기 검증

1. 가이드 파일 존재로 A 판정: 충족
2. 제목이 `[키워드]` 로 시작, 접두어 없음: 충족
3. 키워드 실측, 최다가 `[공통]` 이고 기능 변경이라 기능 제목 키워드 확인: 충족(건수 확정은 결과 필요)
4. 이슈 키 요약 앞, 지어내지 않음: 충족
5. 명사형 종결: 충족
6. 도메인 혼합 없음(CI 분리): 충족
7. B 항목: 해당 없음
8. AI 공동작성자 0건: 충족
