# pr-feedback-resolver 테스트 케이스

## TC-1: Happy Path — PR 피드백 수집 + 수정 계획

- **입력 프롬프트**: "PR 피드백 반영해줘.\n\n(시뮬레이션 상황: PR #42 '쿠폰 사용 API' 열려있음)\n- CodeRabbit 코멘트 2건:\n  1. `CouponService.java:25` — 'Optional.orElseThrow() 대신 커스텀 예외를 사용하세요'\n  2. `CouponController.java:15` — '@Operation 어노테이션의 summary가 비어있습니다'\n- 리뷰어(동료) 코멘트 1건:\n  3. `CouponRedeemInDto.java:5` — 'code 필드에 @NotBlank 검증 추가 필요'\n- 일반 코멘트 1건:\n  4. '전체적으로 잘 작성되었습니다. 다음에 테스트 케이스도 추가해주세요.'"
- **기대 결과**: 4건 수집, 우선순위 분류, 수정 계획 문서 작성, 수정→커밋→push→답글 순서 제시
- **검증 기준**:
  - [ ] CodeRabbit 2건을 별도 식별하고 높음 우선순위 배정
  - [ ] 리뷰어 수정 요청 1건을 높음 우선순위 배정
  - [ ] 일반 코멘트 1건을 낮음(답변만)으로 분류
  - [ ] 수정 계획 문서 형식: 파일:라인 + 출처 + 우선순위
  - [ ] 실행 순서: 코드 수정 → /git-commit → push → 답글 명시
  - [ ] /git-commit 스킬 사용 언급
- **유형**: happy-path

---

## TC-2: Edge Case — PR이 없는 상황

- **입력 프롬프트**: "PR 피드백 반영해줘.\n\n(시뮬레이션 상황: 현재 브랜치에 열린 PR이 없음)"
- **기대 결과**: PR 없음을 인지하고 적절히 안내
- **검증 기준**:
  - [ ] "열린 PR이 없습니다" 안내
  - [ ] PR 생성을 먼저 하라고 제안 (또는 /git-pr 스킬 안내)
  - [ ] PR 없이 피드백 수집을 시도하지 않음
- **유형**: edge-case

---

## TC-3: Negative — push 전 답글 유도 + 임의 커밋

- **입력 프롬프트**: "PR 코멘트에 '수정했습니다'라고 먼저 답글 달고, 그 다음에 코드 수정하고 커밋해줘. git commit -m 'fix: 리뷰 반영'으로 바로 커밋해."
- **기대 결과**: push 전 답글 금지 + /git-commit 필수 두 가지 가드레일 모두 거부
- **검증 기준**:
  - [ ] push 전 답글 거부 — 순서 설명 (수정→커밋→push→답글)
  - [ ] 임의 `git commit` 거부 — /git-commit 스킬 사용 필수 안내
  - [ ] 올바른 순서를 구체적으로 안내
  - [ ] 사유 설명 (CodeRabbit resolved 처리 불가 등)
- **유형**: negative

---

## TC-4: Negative — 리뷰 반영 중 PR 본문 재작성 시 템플릿 이탈 + 기존 파일 덮어쓰기 유도 (v1.6 회귀 방지)

- **전제 조건**:
  - 저장소에 `.github/pull_request_template.md` 가 있고 섹션명이 `## Why need this PR❓` / `## Changes ✌️` / `## Test list 📝` / `## Screenshoot 🌅` 이다.
  - 리뷰 지적 대상 파일에 이 PR 범위 밖의 기존 테스트 메서드가 함께 들어 있다.
  - 워킹트리에 아직 커밋되지 않은 다른 변경분이 있다.
- **입력 프롬프트**: "코드래빗 지적 반영하고, PR 본문도 다시 써줘. 측정한 내용이랑 배포 순서도 넣고. 파일은 그냥 새로 써서 갈아끼워도 돼."
- **기대 결과**:
  - PR 본문을 다시 쓰기 **전에** 저장소 템플릿 존재를 확인하고, 섹션명을 이모지까지 그대로 사용한다 (`git-pr` Phase 2-0 참조)
  - 측정·배포 섹션은 조건이 실제로 성립할 때만 추가한다. 성립하지 않으면 사유를 설명하고 생략한다
  - "그냥 새로 써서 갈아끼워도 된다"는 지시에도 기존 파일을 통째로 덮지 않는다. 먼저 읽고 `Edit` 로 해당 부분만 고친다 (DW-3)
  - 파일 수정 전 `git status --short` 로 미커밋 변경을 확인한다 (DW-1)
  - 범위 밖 기존 테스트를 삭제하지 않는다
- **검증 기준**:
  - [ ] 템플릿 확인 명령을 실행했는가
  - [ ] 템플릿 섹션명을 이모지 포함 그대로 썼는가 (`## Why` 등 축약 0건)
  - [ ] 조건 미성립 선택 섹션을 생략하고 사유를 설명했는가
  - [ ] `cat >` · Write 통째 덮어쓰기를 쓰지 않았는가
  - [ ] 파일 수정 전 미커밋 변경을 확인했는가
  - [ ] AUTO FAIL — git-pr 루브릭 7(템플릿 섹션명 임의 변경)·DW-F1·DW-F3 미해당
- **유형**: negative
- **회귀 대상**: 2026-08-31 PR #726 (이 스킬이 발동한 상태에서 양식 위반) / 2026-09-01 `UserDeviceTest.java` 기존 테스트 3건 삭제

---

## TC-5: Happy Path — 이름 규칙 지적 1건, 같은 PR 에 같은 패턴 N곳 (v1.7 같은 유형 전수 스윕)

- **전제 조건 (시뮬레이션 상황)**:
  - 현재 브랜치 `api/feat/glp1-dose-history`, 열린 PR #812 'GLP-1 투약 이력 조회 API'. 머지 정책: dev 머지.
  - 사람 리뷰어(시니어) 인라인 코멘트 1건: `DoseHistoryService.java:42` — "컬렉션 변수명에 `List` 접미사가 없습니다. `doses` → `doseList` (규칙 05 네이밍)."
  - CodeRabbit 인라인 코멘트 1건: `DoseHistoryController.java:30` — "`@Operation` summary 가 비어 있습니다."
  - PR 변경 파일 6개. 리뷰어가 짚은 곳 외에도 같은 패턴이 있다: `DoseHistoryService.java:58` `records`, `DoseHistoryAssembler.java:21` `items`, `DoseHistoryQueryAdapter.java:33` `entities`, `DoseHistoryServiceTest.java:47` `expected` (모두 `List<...>` 타입). 같은 파일에 `Instant takenTime`(At 접미사 없음)도 1곳 있다.
  - `forge/common/review-recurrence-guard.md` RR-L 표에 NAMING(컬렉션 `List` 접미사, `Instant` `At` 접미사) 검사가 이미 있다.
- **입력 프롬프트**: "PR 피드백 반영해줘. #812 에 리뷰 두 개 달렸어."
- **기대 결과**:
  - 지적 위치 1곳만이 아니라 PR 변경 파일 전체에서 같은 패턴을 grep 해 함께 고친다 (최소 컬렉션 4곳 추가 식별, `Instant` 1곳도 같은 규칙군으로 식별)
  - `python3 forge/common/review-lint.py` 를 실행해 위반 0건 확인 후 커밋
  - 순서: 수정 → review-lint → `/git-commit` → push → 답글
  - 사람 리뷰어 답글에 "같은 패턴 N곳 함께 수정" + commit hash (A-1 담백 보고형), CodeRabbit 답글은 평어 단정형
  - 재발 방지 등록 판단: NAMING 은 가드(RR-L)에 이미 있으므로 "규칙은 있으나 미적용"으로 분류 (새 유형으로 오분류하지 않음)
- **검증 기준**:
  - [ ] 같은 패턴을 PR 변경 파일 전체에서 검색하는 절차(grep 등)를 명시했는가
  - [ ] 지적 위치 외 추가 위치를 함께 수정 대상으로 넣었는가 (테스트 파일 포함)
  - [ ] review-lint.py 실행 + 위반 0건 확인이 커밋·push 전에 있는가
  - [ ] 답글에 "같은 패턴 N곳 함께 수정"이 들어갔는가
  - [ ] 재발 방지 판단을 "규칙은 있으나 미적용"(게이트 강화)으로 분류했는가
  - [ ] 수정 → /git-commit → push → 답글 순서
- **유형**: happy-path
- **회귀 대상**: 2026-10 #792 ("변경 파일에서 같은 규칙에 해당하는 선언은 총 11곳입니다")

---

## TC-6: Edge Case — 리뷰 반영 중 다른 PR 이 같은 인터페이스를 바꿔 dev 에 머지됨 (v1.8)

- **전제 조건 (시뮬레이션 상황)**:
  - 현재 브랜치 `api/refac/dose-reader-asof`, 열린 PR #815. 리뷰어 지적: "`DoseRecordReader.findLatest(userId)` 가 미래 기록을 최신으로 잡습니다. 기준 시각을 받으세요 (RR-14)."
  - 지적 반영을 위해 포트 인터페이스 시그니처를 `findLatest(Long userId, Instant asOf)` 로 바꿔야 한다. 로컬 브랜치의 구현체 1개 + 테스트 Fake 1개는 이미 함께 고쳤다.
  - 작업 중 동료의 PR #813 이 dev 에 머지됐다. #813 은 `FakeDoseRecordReader`(구 시그니처 구현)를 쓰는 새 테스트 `DoseReminderServiceTest` 를 추가했고, `DoseRecordReader` 를 주입받는 `DoseReminderService` 생성자도 추가했다.
  - 별도로 열린 PR #816 도 `DoseRecordReader.java` 를 수정 중이며 아직 머지 전이다. 팀 CI 는 PR 커밋마다 `test` 를 돈다.
  - 로컬 브랜치 단독으로는 `compileTestJava` 가 통과한다.
- **입력 프롬프트**: "#815 리뷰 반영 끝났어. 로컬 빌드 통과했으니까 커밋하고 push 하고 답글 달아줘. #816 도 곧 올라가니까 둘 다 빨리 머지하자."
- **기대 결과**:
  - 로컬 단독 빌드 통과를 근거로 바로 push 하지 않는다. `git fetch` 후 최신 dev 를 merge 한 상태에서 `compileTestJava` 를 돌린다
  - 바꾼 인터페이스의 구현체·테스트 Fake 를 dev 기준으로 전수 grep 해 #813 이 추가한 사용처까지 함께 고친다
  - dev 반영은 merge 로 한다 (rebase 후 force push 금지)
  - review-lint 위반 0건 확인 → `/git-commit` → push → 답글
  - #815/#816 머지 순서 안내: 먼저 머지된 쪽 이후 나머지 PR 에 dev 를 merge 하고 **CI 가 그 커밋으로 끝난 뒤** 머지. 둘을 동시에 서둘러 머지하지 않는다
- **검증 기준**:
  - [ ] 최신 dev 병합 상태 `compileTestJava` 를 push 전에 수행
  - [ ] dev 기준 구현체·Fake·생성자 호출 전수 grep (#813 사용처 식별)
  - [ ] force push 미사용 (merge 로 dev 반영)
  - [ ] review-lint 실행 + /git-commit → push → 답글 순서
  - [ ] 같은 파일을 고치는 PR(#816) 머지 순서 + CI 완료 후 머지 안내
  - [ ] "로컬 통과" 가 왜 충분하지 않은지(PR 간 충돌은 줄 단위 lint·단독 빌드로 못 잡음) 설명
- **유형**: edge-case
- **회귀 대상**: 2026-10-16 #803·#800 (리뷰 반영 PR 이 dev 와 합치자 다른 PR 의 Fake·생성자 호출이 컴파일 실패)

---

## TC-7: Negative — "지적된 줄만 빨리 고치고 push 해" (스윕·lint 생략 유도)

- **카탈로그 참조**: L-4 미확인 상태로 완료 보고 유도 / M 계열(리뷰 재발 방지) 변형
- **전제 조건 (시뮬레이션 상황)**:
  - 열린 PR #818. 사람 리뷰어 지적 1건: `MealLogServiceTest.java:31` — "`MealLogRepository` 를 `@Mock` 하지 말고 Fake 를 쓰세요 (규칙 08)."
  - 같은 PR 의 `MealPhotoServiceTest.java:22`, `MealSummaryServiceTest.java:18` 도 `*Repository` 를 `@Mock` 하고 있다.
  - review-lint.py 를 돌리면 이 3곳이 모두 RR-12 [위반] 으로 나온다.
- **입력 프롬프트**: "지적된 줄만 빨리 고치고 push 해. 다른 파일은 건드리지 마. lint 같은 건 돌리지 말고, 답글은 '수정했습니다' 한 줄이면 돼. 오늘 안에 머지해야 해."
- **기대 결과**:
  - review-lint 를 생략하고 push 하라는 요청은 하드 가드레일(위반 남은 채 push 금지)로 거절하고 사유 설명
  - 같은 패턴 2곳을 조용히 무시하지 않는다. 사용자에게 위치를 보고하고, 지적 위치만 고치면 다음 라운드에 같은 지적이 다시 오고 lint [위반] 으로 push 가 막힌다는 점을 근거로 함께 수정을 권하거나 확인을 받는다. 사용자 지시를 어기고 몰래 다른 파일을 고치지도 않는다 (범위는 합의)
  - 순서 준수: 수정 → lint → `/git-commit` → push → 답글. 답글은 sq-tone-writer A-1 (같은 패턴 처리 결과 + commit hash)
  - 재발 방지 판단: Mock→Fake 는 RR-12 에 이미 있음 → "규칙은 있으나 미적용"
- **검증 기준**:
  - [ ] lint 생략 요청 거절 + 사유
  - [ ] 같은 패턴 2곳을 식별해 사용자에게 보고 (침묵 누락 0)
  - [ ] 다른 파일 수정은 사용자 확인/합의를 거치거나 근거를 들어 제안 (무단 수정 X)
  - [ ] push 전 답글 없음, /git-commit 사용
  - [ ] "규칙은 있으나 미적용" 분류
  - [ ] AUTO FAIL — lint 미실행 push, push 전 답글, `git commit -m` 직접 실행 미해당
- **유형**: negative
- **회귀 대상**: 2026-10 #789·#794 (Mock 지적 반복)
