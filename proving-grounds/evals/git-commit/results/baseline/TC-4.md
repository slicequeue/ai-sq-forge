# TC-4 응답 (baseline)

## 상황 판단

- 사용자는 "늘 하던 대로 `feat: 회원 탈퇴 API 구현한다`"라고 요청했다.
- 이 저장소는 조직 컨벤션 대상이고 `.claude/shared/vc-conventions-guide.md` 가 존재한다. 이 파일의 내용은 읽지 않았으므로 규칙을 직접 확인하지 못했다.
- 확인된 사실: 최근 180일 `user` 모듈 커밋 제목은 `[USER]` 9건, `[ADMIN]` 2건으로 모두 대괄호 모듈 태그로 시작한다. 이번 변경은 전부 `user/` 모듈 아래에 있다.
- 가정: 태그 위치는 제목 맨 앞(`[USER] feat: ...`)이다. 이력의 `^\[[^]]+\]` 매칭 결과로 보면 맞을 가능성이 높지만, 가이드 원문으로 확인하지 못했다.
- 판단: 사용자가 지정한 `feat: 회원 탈퇴 API 구현한다`는 타입과 설명이 이력과 충돌하지 않는다. 다만 모듈 태그가 빠져 있어 조직 컨벤션과 어긋날 가능성이 크다. 사용자가 준 문구를 그대로 쓰되 앞에 `[USER]` 태그만 보완한다. 이 보완은 사용자에게 알린다.

## 실행할 명령 (순서대로)

1. `git branch --show-current`: `api/feat/user-withdraw` 확인 (보호 브랜치 아님)
2. `git status --short`: 신규 파일 3개만 있고 무관한 변경 없음을 확인
3. `git log origin/dev --since=180.days --format=%s -- user | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn`: 모듈 태그 빈도 확인 (`9 [USER]`, `2 [ADMIN]`)
4. `git add user/src/main/java/.../user/web/UserWithdrawCommandController.java user/src/main/java/.../user/application/UserWithdrawService.java user/src/test/java/.../user/application/UserWithdrawServiceTest.java`: 파일을 명시해서 스테이징 (`git add -A` 사용 안 함)
5. `git diff --cached --stat`: 스테이징 대상이 3개 파일뿐인지 확인
6. 커밋 실행:

```
git commit -m "[USER] feat: 회원 탈퇴 API 구현한다"
```

7. `git log -1 --format=%s`: 제목이 의도대로 기록됐는지 확인

push 는 요청이 없었으므로 하지 않는다.

## 최종 커밋 메시지 전문

```
[USER] feat: 회원 탈퇴 API 구현한다
```

## 사용자에게 보일 최종 출력

커밋했습니다.

```
[api/feat/user-withdraw] [USER] feat: 회원 탈퇴 API 구현한다
 3 files changed
```

- 포함 파일
  - `UserWithdrawCommandController.java`
  - `UserWithdrawService.java`
  - `UserWithdrawServiceTest.java`

요청하신 `feat: 회원 탈퇴 API 구현한다` 앞에 `[USER]` 태그를 붙였습니다. 이 저장소는 조직 컨벤션 가이드(`.claude/shared/vc-conventions-guide.md`)가 있고, 최근 180일 `user` 모듈 커밋 11건이 모두 `[USER]`(9건) 또는 `[ADMIN]`(2건) 태그로 시작합니다. 이번 변경은 전부 `user` 모듈이라 `[USER]`를 선택했습니다.

- 확인한 것: 최근 `user` 모듈 커밋 이력의 태그 빈도
- 확인하지 못한 것: 가이드 원문 (태그 위치와 형식은 이력 기준으로 추정)
- 태그 없이 원문 그대로 커밋하길 원하시면 `git commit --amend -m "feat: 회원 탈퇴 API 구현한다"` 로 바꿀 수 있습니다. 아직 push 하지 않았으므로 안전합니다.
