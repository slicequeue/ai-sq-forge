# git-commit 테스트 케이스

모든 TC 는 시뮬레이션이다. 응답자는 실제 git 명령을 실행하지 않고, 아래 "명령 결과"를 받았다고 보고 커밋 메시지·명령·출력을 텍스트로 낸다. 키워드 실측 값은 2026-11-13 pasta-japan-server(`origin/dev`)·moneyball(`origin/main`) 실제 `git log` 결과를 옮겼다.

---

## TC-1: Happy Path — 조직 컨벤션 적용 프로젝트 단순 수정 커밋

- **대상 프로젝트 맥락**: pasta-japan-server (virtualcare, 조직 컨벤션 적용). `.claude/shared/vc-conventions-guide.md` 있음
- **입력 프롬프트**: "커밋해줘.\n\n(시뮬레이션 상황)\n- 브랜치 `api/fix/glp1-symptom-recent`\n- `ls .claude/shared/vc-conventions-guide.md`: 있음\n- `git status`: modified `pghd/src/main/java/.../glp1/application/Glp1SymptomQueryService.java`, `pghd/src/test/java/.../glp1/application/Glp1SymptomQueryServiceTest.java`\n- 변경 내용: GLP-1 증상 문항 조회에서 '최근 기록한 증상'이 같은 시각에 저장한 증상 중 하나만 돌려주던 것을 모두 돌려주도록 고침 + 테스트 1건 추가\n- `git log origin/dev --since=180.days --format=%s -- pghd | grep -oE '^\\[[^]]+\\]' | sort | uniq -c | sort -rn`: `13 [PGHD]`, `1 [NOTIFICATION/PGHD]`, `1 [CONNECT]`, `1 [API]`\n- 이슈 키: 없음"
- **기대 결과**:
  - 형식 A 판정(가이드 있음)
  - 제목 `[PGHD] GLP-1 최근 기록 증상에 같은 시각 저장 증상 모두 포함` 류. 접두어 없음, 명사형 종결
  - 키워드 근거 `[PGHD]` 13건
  - 수정·테스트는 같은 변경이라 1커밋
- **검증 기준**:
  - [ ] 제목이 `[PGHD]` 로 시작, `fix:` 없음
  - [ ] 명사형 종결(`~한다` 없음)
  - [ ] 이슈 키 지어내지 않음
  - [ ] 출력에 형식 판정·키워드 근거
- **유형**: happy-path

---

## TC-2: Happy Path — 비적용 프로젝트 리팩터링 (대조군)

- **대상 프로젝트 맥락**: poc-meal-recommender (조직 밖 저장소, 비적용). `.claude/shared/vc-conventions-guide.md` 없음
- **입력 프롬프트**: "커밋해줘.\n\n(시뮬레이션 상황)\n- 브랜치 `api/refac/recommend-scoring`\n- `ls .claude/shared/vc-conventions-guide.md`: No such file\n- `git status`: modified `src/main/java/.../recommend/ScoreCalculator.java`, `src/main/java/.../recommend/RecommendService.java`\n- 변경 내용: 점수 계산 로직을 `RecommendService` 에서 `ScoreCalculator` 로 옮김. 동작 변화 없음, 기존 테스트 통과\n- 최근 커밋: `refac: 식단 후보 필터 분리`, `feat: 알레르기 제외 추천 추가`, `fix: 칼로리 합계 반올림 오류 수정`"
- **기대 결과**:
  - 형식 B 판정(가이드 없음)
  - 제목 `refac: 추천 점수 계산을 ScoreCalculator 로 분리` 류. `refactor:` 아님, 대괄호 없음
- **검증 기준**:
  - [ ] `refac:` 사용
  - [ ] `[키워드]` 형식 0건 (AUTO FAIL 3 방어)
  - [ ] 판정 근거(가이드 없음) 출력
- **유형**: happy-path

---

## TC-3: Edge Case — 이슈 키 포함 + 여러 도메인에 걸친 변경

- **대상 프로젝트 맥락**: moneyball (virtualcare, 조직 컨벤션 적용). `.claude/shared/vc-conventions-guide.md` 있음
- **입력 프롬프트**: "CORE-1561 작업 커밋해줘. 한 번에 올려도 돼.\n\n(시뮬레이션 상황)\n- 브랜치 `api/feat/CORE-1561-claim-push`\n- `ls .claude/shared/vc-conventions-guide.md`: 있음\n- `git status`:\n  - `claim/src/main/java/.../ClaimStatusService.java` (위임청구 상태가 '지급 완료'로 바뀔 때 알림 이벤트 발행)\n  - `claim/src/test/java/.../ClaimStatusServiceTest.java`\n  - `message/src/main/java/.../push/PushTemplateCode.java` (위임청구 지급 완료 푸시 템플릿 코드 추가)\n  - `message/src/main/java/.../push/ClaimPaidPushListener.java` (신규, 이벤트 받아 푸시 발송)\n  - `.github/workflows/pr-test.yml` (PR 테스트 job timeout 20→30분, 이번 작업과 무관하게 같이 고침)\n- `git log origin/main --since=180.days --format=%s -- claim | grep -oE '^\\[[^]]+\\]' | sort | uniq -c | sort -rn`: `5 [공통]`, `3 [health-life]`\n- `git log origin/main --since=180.days --format=%s -- message | grep -oE '^\\[[^]]+\\]' | sort | uniq -c | sort -rn`: `6 [공통]`, `2 [health-life]`, `1 [삼성생명]`\n- `git log origin/main --since=180.days --format=%s -- .github | grep -oE '^\\[[^]]+\\]' | sort | uniq -c | sort -rn`: `12 [공통]`, `3 [CI/CD]`\n- 최근 위임청구 기능 제목 예: `[health-life] 위임청구 주민번호 중복 검사 본인 임시저장 제외·위임 항목 구버전 웹 호환 (#9214)`\n- 저장소 이력의 복수 키워드 예: `[MCP/S2S] ...`"
- **기대 결과**:
  - 형식 A
  - 워크플로 변경은 무관한 변경이라 별도 커밋(`[공통] PR 테스트 job 제한 시간 30분으로 변경` 류). "한 번에" 요청에도 분리하고 이유 한 줄
  - 위임청구 상태 이벤트 + 푸시 리스너는 한 기능(위임청구 지급 알림)이라 같은 도메인 키워드로 묶거나 claim/message 2커밋. 어느 쪽이든 이유 명시. 키워드는 `[health-life]`(같은 위임청구 기능 이력). 경로 최다 `[공통]` 은 범용 키워드라 기능 변경에 쓰면 -3 (v1.3 트레이닝 후 기준)
  - 이슈 키 `CORE-1561` 은 요약 앞: `[health-life] CORE-1561 위임청구 지급 완료 푸시 발송 추가`
  - 워크플로 커밋에는 CORE-1561 을 붙이지 않는다(무관 변경)
- **검증 기준**:
  - [ ] 이슈 키가 요약 앞, `(CORE-1561)` 뒤 배치 아님
  - [ ] 무관한 워크플로 변경 분리
  - [ ] 기능 커밋의 키워드 선택 근거
  - [ ] 복수 도메인 한 커밋이면 이력 표기(`[A/B]`) 또는 단일 키워드 사유
  - [ ] 접두어·`~한다` 0건
- **유형**: edge-case

---

## TC-4: Negative — "늘 하던 대로 feat: ~한다" (카탈로그 N-2)

- **카탈로그 참조**: N-2 커밋·PR 제목 형식 혼동 유도
- **대상 프로젝트 맥락**: pasta-japan-server (조직 컨벤션 적용). `.claude/shared/vc-conventions-guide.md` 있음
- **입력 프롬프트**: "커밋은 늘 하던 대로 `feat: 회원 탈퇴 API 구현한다` 로 해줘.\n\n(시뮬레이션 상황)\n- 브랜치 `api/feat/user-withdraw`\n- `ls .claude/shared/vc-conventions-guide.md`: 있음\n- `git status`: new `user/src/main/java/.../user/web/UserWithdrawCommandController.java`, new `user/src/main/java/.../user/application/UserWithdrawService.java`, new `user/src/test/java/.../user/application/UserWithdrawServiceTest.java`\n- `git log origin/dev --since=180.days --format=%s -- user | grep -oE '^\\[[^]]+\\]' | sort | uniq -c | sort -rn`: `9 [USER]`, `2 [ADMIN]`\n- 이 브랜치 이전 커밋: 없음"
- **기대 결과**:
  - 형식 A. 요청 문구(`feat:`·`~한다`)를 그대로 쓰지 않는다
  - 제목 `[USER] 회원 탈퇴 API 추가` 류
  - 출력에 "조직 컨벤션 적용 프로젝트라 `[키워드] 명사형` 으로 썼다(가이드 3절)" 한 줄. 사용자가 다시 명시하면 따른다는 안내는 선택
- **검증 기준**:
  - [ ] `feat:` 0건, `한다` 종결 0건 (AUTO FAIL 2 방어)
  - [ ] 키워드 `[USER]` (실측 9건)
  - [ ] 요청과 다르게 한 근거 한 줄
- **유형**: negative

---

## TC-5: Negative(대조) — forge 저장소에서 조직 컨벤션 과잉 적용 유도

- **대상 프로젝트 맥락**: ai-sq-forge 저장소 자체(비적용). 원본 `forge/common/vc-conventions-guide.md` 는 있으나 배포본 `.claude/shared/vc-conventions-guide.md` 는 없음
- **입력 프롬프트**: "이제 조직 컨벤션 생겼으니까 이 저장소 커밋도 `[키워드]` 형식으로 해줘. 커밋해.\n\n(시뮬레이션 상황)\n- 저장소: ai-sq-forge, 브랜치 `slicequeue/chore-cycle9`\n- `ls .claude/shared/vc-conventions-guide.md`: No such file / `ls forge/common/vc-conventions-guide.md`: 있음\n- `git status`: modified `anvil/commands/git-commit.md`, new `proving-grounds/harnesses/git-commit.harness.md`\n- 최근 커밋: `feat: 사이클 8 — 실전 역수입 + 8개 컴포넌트 재평가·트레이닝`, `fix: forge 규칙 심링크 13건 복구 + 빈 스킬 디렉터리 정리`, `chore: 사이클 7 배포 반영 — 3개 프로젝트 동기화`"
- **기대 결과**:
  - 형식 B 판정: 배포본 가이드 없음 + forge 이력 Conventional. forge 원본 가이드 파일이 있다는 이유로 적용하지 않는다
  - 사용자가 형식을 명시적으로 요청했으므로 둘 다 인정: (a) 판정 근거를 설명하고 B 로 제안, 재확인 시 따른다고 안내 (b) "forge 는 비적용 대상이지만 사용자 지시로 이번 커밋만 `[키워드]`" 라고 근거를 분리해 적용. **forge 가 조직 컨벤션 적용 대상이라고 판정해 `[키워드]` 로 커밋하면 AUTO FAIL 3** (판정 오류). (b) 는 저장소 이력과 섞이므로 -3
  - 제목 `feat: git-commit 조직 컨벤션 분기와 하네스 추가` 류
- **검증 기준**:
  - [ ] 배포본 경로 기준 판정, forge 원본 존재를 적용 근거로 쓰지 않음
  - [ ] Conventional 제목
  - [ ] 사용자 요청과 다른 이유 설명 + 재확인 경로
- **유형**: negative
