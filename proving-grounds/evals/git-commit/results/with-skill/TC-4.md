# TC-4 응답 (시뮬레이션)

## 0. 형식 판정

- `ls .claude/shared/vc-conventions-guide.md` 결과: 있음 → **A. 조직 컨벤션** `[핵심키워드] 명사형 요약`
- 사용자가 "늘 하던 대로 `feat: 회원 탈퇴 API 구현한다`" 를 요청했지만 판정 결과를 따른다. `feat:` 접두어와 `~한다` 종결은 A 형식에서 금지다. 사용자가 형식을 바꾸라고 다시 명시하지 않았으므로 요청 형식으로 되돌리지 않는다.

## 확인된 사실 vs 가정

확인된 사실 (시뮬레이션 입력 기준)
- 브랜치 `api/feat/user-withdraw`, 이 브랜치 이전 커밋 없음
- 변경 파일 3개는 모두 신규이고 모두 `user` 모듈 아래에 있다 (컨트롤러, 서비스, 서비스 테스트)
- `user` 경로의 최근 180일 커밋 제목 키워드: `[USER]` 9건, `[ADMIN]` 2건

가정
- 이슈 키는 브랜치명과 사용자 입력 어디에도 없으므로 없는 것으로 보고 넣지 않는다(지어내지 않음).
- 변경이 `user` 모듈에만 있으므로 단일 도메인이다. 도메인이 하나라서 커밋을 나누지 않는다.

## 실행할 명령 (순서대로)

1. `ls .claude/shared/vc-conventions-guide.md` : A/B 판정 (있음)
2. `git status` : 신규 파일 3개 확인
3. `git diff dev` : 변경 분석 (신규 파일은 untracked 라서 stage 후 `git diff --cached` 로 내용 확인)
4. spotless 판단: 변경 파일이 `pasta-api` 모듈이 아니라 `user` 모듈이므로 `./gradlew :pasta-api:spotlessApply` 는 실행하지 않는다.
5. `git log origin/dev --since=180.days --format=%s -- user | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn` : 키워드 실측 → `9 [USER]`, `2 [ADMIN]`. 최다인 `[USER]` 를 철자·대소문자 그대로 사용
6. `git add user/src/main/java/.../user/web/UserWithdrawCommandController.java user/src/main/java/.../user/application/UserWithdrawService.java user/src/test/java/.../user/application/UserWithdrawServiceTest.java`
7. `git commit -m "[USER] 회원 탈퇴 API 추가"`

도메인이 하나이고 컨트롤러·서비스·테스트가 한 기능이므로 커밋은 1개다. `Co-authored-by` 와 AI 관련 표기는 넣지 않는다.

## 최종 커밋 메시지 전문

```
[USER] 회원 탈퇴 API 추가
```

본문은 선택 항목이며 별도로 남길 변경 이유가 없어 생략한다.

## 자기 검증

1. [x] `.claude/shared/vc-conventions-guide.md` 존재 여부로 A 판정
2. [x] 제목이 `[USER]` 로 시작, `feat:` 접두어 없음
3. [x] 키워드를 `git log -- user` 실측으로 선택 (9건 vs 2건, 철자 그대로)
4. [x] 이슈 키 없음 → 지어내지 않음
5. [x] 요약이 `추가` 로 끝나는 명사형 (`~한다`·`~했음` 0건)
6. [x] 단일 도메인이라 나눌 필요 없음
7. [-] B 항목은 해당 없음
8. [x] AI 공동작성자 표기 0건

## 사용자에게 보일 최종 출력

```
요청하신 `feat: 회원 탈퇴 API 구현한다` 형식은 쓰지 않았습니다.
이 프로젝트는 조직 컨벤션 적용 대상이라 `feat:` 접두어와 `~한다` 종결이 허용되지 않습니다.
`[핵심키워드] 명사형 요약` 으로 커밋했습니다. 이전 형식을 꼭 원하시면 다시 말씀해 주세요.

✓ 커밋 완료: [USER] 회원 탈퇴 API 추가
  형식: A 조직 컨벤션 (.claude/shared/vc-conventions-guide.md 존재)
  키워드: [USER] (user 경로 최근 180일 9건, [ADMIN] 2건)
```
