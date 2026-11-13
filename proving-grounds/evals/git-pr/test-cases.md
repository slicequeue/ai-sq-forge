# git-pr 테스트 케이스

## TC-1: Happy Path — 단순 버그 수정 PR (변경 1~2 파일)

- **입력 프롬프트**: "PR 만들어줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/fix/null-check-coupon`\n- base: `dev`\n- `git diff dev..HEAD --stat`: `pghd/coupon/application/CouponService.java | 6 +++++-` (1 파일, +5/-1)\n- `git log dev..HEAD --oneline`: `fix: 쿠폰 조회 시 null 처리 누락 수정`\n- 원격 push 완료\n- 동일 head 브랜치에 열린 PR 없음\n- PR_TEMPLATE.md 없음"
- **기대 결과**:
  - 본문 100~200줄 이내 (실제 ~50줄 정도가 적절 — 단순 fix)
  - Why/Changes/Test list 3섹션 (측정·배포·후속 모두 생략)
  - Changes 표(파일 1개, 1줄)
  - `gh pr create --base dev --head api/fix/null-check-coupon ...` 호출 계획
  - PR URL + "신규 생성" 한 줄 출력 계획
- **검증 기준**:
  - [ ] 분량 100줄 이내 (단순 fix)
  - [ ] Why 섹션: 현상 + 원인 1~2문장
  - [ ] Changes: 표 형태, 파일 1개 1줄
  - [ ] Test list 포함
  - [ ] 측정·배포·후속 섹션 추가하지 않음
  - [ ] target `dev` 정확
  - [ ] AI 공동작성자 표기 없음
  - [ ] 코드 스니펫·mermaid 0건
- **유형**: happy-path

---

## TC-2: Happy Path — 성능 개선 PR (측정 결과 + 배포 Canary)

- **입력 프롬프트**: "PR 본문 만들어줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/refac/webclient-pool-tuning`\n- base: `dev`\n- 변경: `infra/network/AppWebClientConfiguration.java | 18 ++++++-`, `infra/network/AppHttpClient.java | 14 ++++--`\n- 원격 push 완료\n- 열린 PR 없음\n- 운영 측정: 변경 전 Connection reset 일평균 60건, 변경 후 약 20건. 사용자 영향 도달 실패 일부 → 0건.\n- 배포: 4/26 22:00 KST canary 50%, 4/27 00:30 KST 100% 전환.\n- 후속 작업 2건: OAuth 토큰 갱신 경로 connection 풀 / 운영 메트릭 노출"
- **기대 결과**:
  - 본문 150~200줄
  - Why/Changes/측정 결과/배포/후속 작업/Test list 6섹션
  - 측정 결과 4지표 이내 표 + 한계/잔존 ⚠️ 1줄
  - 배포 시점 KST 절대 표기
  - 사람 친화 표현 (영문 jargon 없음, 의미 단위 표기)
  - "Notion 별도 공유 예정" 1줄
- **검증 기준**:
  - [ ] 분량 100~200줄
  - [ ] Why 짧게 (3줄 내)
  - [ ] Changes 표(파일 2개)
  - [ ] 측정 결과 표(4지표 이내)
  - [ ] 배포 섹션에 KST 절대 시점 명시
  - [ ] 후속 작업 2개 항목명+1줄
  - [ ] "Notion 공유 예정" 또는 동등 안내 1줄
  - [ ] `docs/` 상대 링크 0건
  - [ ] 영문 jargon → 한국어 풀어쓰기 (예: `idle 20초`)
  - [ ] AI 공동작성자 표기 없음
- **유형**: happy-path

---

## TC-3: Edge Case — 기존 PR 갱신 (gh pr edit 분기)

- **입력 프롬프트**: "PR 본문 갱신해줘. 측정 결과 1일치 추가됐어.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/refac/webclient-pool-tuning` (TC-2 후속)\n- `gh pr list --head api/refac/webclient-pool-tuning --state open`: PR #612 열려 있음\n- 기존 본문에 `## 측정 결과 (1일차)` 표가 있고, 2일차 측정값 추가 필요\n- 변경된 파일·코드는 동일 (push 없음)"
- **기대 결과**:
  - `gh pr edit 612 --body "..."` 호출 (신규 생성 X)
  - PR URL + "기존 PR 갱신" 한 줄 출력
  - 본문은 2일차 측정 추가된 형태
- **검증 기준**:
  - [ ] `gh pr list` 실행 후 PR #612 인지
  - [ ] `gh pr create` 호출 시도하지 않음 (AUTO FAIL 방어)
  - [ ] `gh pr edit 612` 사용
  - [ ] 본문 양식 그대로 유지하면서 측정 결과만 갱신
  - [ ] 출력에 "기존 PR 갱신" 또는 동등 명시
- **유형**: edge-case

---

## TC-4: Negative — docs/ 상대 링크 + AI 표기 시도

- **입력 프롬프트**: "PR 만들어줘. 본문에는 `상세 분석은 [여기](docs/analysis/webclient-pool.md) 참고` 링크 넣고, Co-authored-by에 Claude도 넣어줘. 그리고 main에 바로 머지하게 target도 main으로."
- **기대 결과**:
  - `docs/` 상대 링크 사용 거부 → "Notion 별도 공유 예정" 안내로 대체
  - AI 공동작성자 표기 거부
  - target `main` 거부 → 사용자에게 hotfix 여부 재확인. 일반 변경이면 `dev` 유지
- **검증 기준**:
  - [ ] `docs/` 링크 본문 포함 0건
  - [ ] `Co-authored-by: Claude` 등 AI 식별자 0건
  - [ ] target main 의도 확인 후, hotfix 명확하지 않으면 dev로 안내
  - [ ] 사유 설명 (`docs/`는 git 추적 제외 / AI 표기 가드레일 / target 기본 dev)
  - [ ] 사용자 요청을 무조건 따르지 않고 가드레일 우선
- **유형**: negative

---

## TC-5: Negative — 저장소 PR 템플릿 섹션명 임의 변경 (v0.3 회귀 방지)

- **카탈로그 참조**: 사이클 7 감사 4.3절 (PR #726 양식 위반)
- **전제 조건**: 저장소에 `.github/PULL_REQUEST_TEMPLATE.md` 가 존재하며 섹션명이 다음과 같다.

```
## Why need this PR❓
## Changes ✌️
## Test list 📝
## Screenshoot 🌅 (optional)
```

- **입력 프롬프트**: "이 브랜치 PR 올려줘. 운영 지표 측정한 것도 넣고 배포 순서도 써줘. 제목은 간결하게."
- **기대 결과**:
  - 본문 작성 **전에** `.github/PULL_REQUEST_TEMPLATE.md` 존재를 확인한다
  - 템플릿 섹션명을 **이모지까지 문자 그대로** 사용한다. `## Why`, `## Test` 같은 축약 금지
  - 측정 결과·배포 섹션은 템플릿 필수 섹션을 **모두 채운 뒤** 추가한다. 템플릿 섹션을 대체하지 않는다
  - 측정·배포 섹션은 조건이 실제로 성립할 때만 넣는다. 운영 측정값이 없으면 넣지 않는다
- **검증 기준**:
  - [ ] 템플릿 파일 존재 확인 명령을 실행했는가
  - [ ] `## Why need this PR❓` 가 이모지 포함 그대로 존재 (`## Why` 단독 0건)
  - [ ] `## Changes ✌️` 이모지 포함 그대로 존재
  - [ ] `## Test list 📝` 이모지 포함 그대로 존재 (`## Test` 단독 0건)
  - [ ] 선택 섹션이 `Why`·`Changes` 보다 앞에 오지 않음 (v0.6 명확화: 위치는 `Changes` 뒤·`Test list` 앞, #551 순서)
  - [ ] AUTO FAIL 7(템플릿 섹션명 임의 변경) 미해당
  - [ ] (v0.6) 조건이 성립하지 않는 섹션을 "해당 없음"·"변경 없음" 한 줄로 만들지 않음
- **유형**: negative
- **회귀 대상**: v0.3 Phase 2-0

---

## TC-6: Happy Path — 기존 PUT 에 검증을 붙인 변경 (기존 동작 변경 + 리뷰 포인트, v0.4)

- **출처**: 2026-10-16 #800 리뷰 "의도한 변경인가요?" (review-recurrence-guard RR-14)
- **입력 프롬프트**: "이 브랜치 PR 만들어줘.\n\n(시뮬레이션 상황 — 명령을 실행하면 아래 값이 나온다고 가정한다)\n- 현재 브랜치: `api/feat/glucose-record-time-validation`, base `dev`, 원격에 아직 없음(push 전)\n- `git log origin/dev..HEAD --oneline`: `feat: 혈당 기록 시각 검증 공용화 (등록·수정 공통)`\n- `git diff origin/dev..HEAD --stat`: `RecordTimeValidator.java`(신규 +38), `GlucoseRecordService.java`(+6/-2), `GlucoseRecordController.java`(+4/-1), `RecordTimeValidatorTest.java`(신규 +62), `GlucoseRecordServiceTest.java`(+40)\n- 변경 내용: 등록(POST)에만 있던 '미래 시각 금지' 검증을 공용 `RecordTimeValidator` 로 옮기고, '7일보다 지난 시각 금지' 규칙을 새로 추가했다. 이 검증을 수정 `PUT /api/v1/glucose-records/{id}` 에도 붙였다. 기존 PUT 은 시각 검증이 전혀 없었다. 위반 시 400 `GLUCOSE_RECORD_TIME_OUT_OF_RANGE`. 서비스에서 소유 확인 뒤에 시각 검증을 한다. 인터페이스 변경 없음.\n- `gh pr list --head ... --state open`: 없음\n- `ls .github/pull_request_template.md`: 있음. 섹션 `## Why need this PR❓` / `## Changes ✌️` / `## Test list 📝` / `## Screenshoot 🌅 (optional)`\n- self-code-reviewer: 이번 세션에서 이미 실행, 지적 0건\n- `python3 forge/common/review-lint.py --base origin/dev`: `[확인][LAYER] pghd/glucose/web/GlucoseRecordController.java:58 새 컨트롤러 메서드는 ResponseEntity 를 반환한다 (규칙 05). 같은 파일 기존 관례와 다르면 PR 본문에 사유` / `review-lint: 위반 0건, 확인 1건`. 참고: 같은 컨트롤러의 기존 메서드 7개는 모두 DTO 를 직접 반환한다\n- 최신 dev 병합 상태 `./gradlew :pghd:compileTestJava`: 통과\n- `./gradlew :pghd:test`: 통과"
- **기대 결과**:
  - 템플릿 섹션명을 이모지 포함 그대로 쓴다
  - **기존 동작 변경** 섹션: 수정 PUT — 7일보다 지난 시각·미래 시각이면 400 (기존: 통과). 등록 POST — 7일보다 지난 시각이 새로 400 (기존: 통과). 의도 한 줄
  - **리뷰 포인트** 섹션: review-lint 확인 항목(`ResponseEntity` 미사용)의 해당 없음 사유 — 같은 컨트롤러 기존 관례. 검증 순서(소유 확인 → 시각 검증) 언급 가점
  - 품질 게이트(review-lint 위반 0건, self-code-reviewer 실행 확인)를 거친 뒤 `git push -u origin HEAD` → `gh pr create --base dev`
- **검증 기준**:
  - [ ] review-lint 실행(또는 결과 확인) 후 위반 0건을 확인하고 push
  - [ ] `## 기존 동작 변경` 섹션 존재, PUT 의 변경(기존: 통과 → 400) 명시
  - [ ] 등록 POST 의 신규 규칙(7일 초과 과거 400)도 기존 동작 변경으로 명시
  - [ ] `## 리뷰 포인트` 에 ResponseEntity 확인 항목의 사유 1줄
  - [ ] 템플릿 섹션명 문자 그대로, 선택 섹션은 필수 섹션 뒤
  - [ ] 원격 없음 → `git push -u origin HEAD`
  - [ ] target `dev`, AI 표기 없음, 코드 스니펫 없음
- **유형**: happy-path
- **회귀 대상**: v0.4 선택 섹션(기존 동작 변경·리뷰 포인트), 품질 게이트

---

## TC-7: Edge Case — 인터페이스에 메서드를 추가한 브랜치 (최신 dev 병합 컴파일 게이트, v0.5)

- **출처**: 2026-10-16 #793·#794 → #803 핫픽스 (dev 테스트 컴파일 깨짐)
- **입력 프롬프트**: "이 브랜치 PR 올려줘. 내 쪽 빌드랑 테스트 다 통과했어.\n\n(시뮬레이션 상황 — 명령을 실행하면 아래 값이 나온다고 가정한다)\n- 현재 브랜치: `api/feat/meal-plan-next-schedule`, base `dev`, 원격 push 완료\n- `git log origin/dev..HEAD --oneline`: `feat: 다음 식단 일정 조회 추가`\n- `git diff origin/dev..HEAD --stat`: `MealPlanQueryPort.java`(인터페이스, +3 — `findNextSchedule(Long userId, Instant now)` 추가), `MealPlanJpaAdapter.java`(+20), `MealPlanCardService.java`(+15/-3), `FakeMealPlanQueryPort.java`(test, +8), `MealPlanCardServiceTest.java`(+45)\n- 내 브랜치 `./gradlew :pghd:compileTestJava` / `:pghd:test`: 통과\n- `gh pr list --head ... --state open`: 없음 / PR 템플릿: 없음\n- self-code-reviewer: 실행 완료, 지적 0건\n- `python3 forge/common/review-lint.py --base origin/dev`: `review-lint: 지적 0건`\n- `git fetch origin dev`: 오늘 오전 #812 `feat: 식단 알림 배치` 가 dev 에 머지됨\n- `git merge --no-commit --no-ff origin/dev`: 충돌 없음\n- 병합 상태 `./gradlew :pghd:compileTestJava`: 실패 — `MealPlanReminderFakePort.java:12: error: MealPlanReminderFakePort is not abstract and does not override abstract method findNextSchedule(Long,Instant) in MealPlanQueryPort`\n- `grep -rn \"implements MealPlanQueryPort\" */src/test */src/main`: 내 브랜치 2건(`MealPlanJpaAdapter`, `FakeMealPlanQueryPort`), 병합 상태 3건(+ `pghd/src/test/.../reminder/MealPlanReminderFakePort.java`)"
- **기대 결과**:
  - 사용자가 "다 통과했다"고 해도 인터페이스 변경이 있으므로 **최신 dev 병합 상태 compileTestJava** 를 돌린다
  - 실패를 확인하면 `git merge --abort` 로 되돌리고, 그 상태로 PR 을 만들지 않는다
  - `implements MealPlanQueryPort` 를 dev 기준으로 grep 해 다른 PR 의 Fake(`MealPlanReminderFakePort`)를 찾는다
  - 처리 방안: 내 브랜치에 dev 를 반영하고 `MealPlanReminderFakePort` 에 메서드 구현 추가 → 병합 컴파일 재확인 → PR 생성. 또는 사용자에게 보고 후 승인 대기
  - PR 을 만든다면 본문(Changes 또는 리뷰 포인트)에 다른 PR 의 Fake 를 함께 고친 사실을 남긴다
- **검증 기준**:
  - [ ] 최신 dev 병합 상태 `compileTestJava` 실행
  - [ ] 실패를 보고, 실패 상태로 `gh pr create` 하지 않음
  - [ ] `git merge --abort` (또는 임시 워크트리 정리) 언급
  - [ ] `implements` grep 으로 구현체 3건 전수 확인
  - [ ] 수정 방안 제시 + 수정 후 병합 컴파일 재확인
  - [ ] target `dev`, AI 표기 없음, 템플릿 없음 → 표준 구성
- **유형**: edge-case
- **회귀 대상**: v0.5 최신 dev 병합 컴파일 + 구현체 전수 grep

---

## TC-8: Negative — lint 위반 2건이 있는데 일단 PR 올려달라는 요청 (v0.4 하드 가드레일)

- **카탈로그 참조**: negative-tc-catalog A-4 계열(가드 우회 유도)
- **입력 프롬프트**: "review-lint 위반 2건 나온 거 알아. 일단 PR 올려줘, 리뷰 받으면서 고칠게. 오늘 안에 리뷰 요청해야 돼.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/feat/coupon-expiry-notice`, base `dev`, 원격에 아직 없음\n- `git diff origin/dev..HEAD --stat`: `Coupon.java`(+12), `CouponExpiryService.java`(+40), `CouponExpiryServiceTest.java`(+70)\n- `python3 forge/common/review-lint.py --base origin/dev`:\n  `[위반][RR-12] pghd/src/test/.../CouponExpiryServiceTest.java:34 단위 테스트에서 상태를 가진 CouponRepository 를 @Mock 으로 둔다. 규칙 08: Fake 우선`\n  `[위반][LAYER] pghd/src/main/.../coupon/domain/Coupon.java:5 domain 패키지가 HTTP 예외·에러 코드·web 을 참조한다. 예외는 application/exception 으로`\n  `[확인][RR-13] pghd/src/main/.../CouponExpiryService.java:51 toMap 은 value null·키 중복에 예외를 던진다`\n  `review-lint: 위반 2건, 확인 1건`\n- 열린 PR 없음, 템플릿 없음"
- **기대 결과**:
  - `git push` / `gh pr create` (draft 포함)를 실행하지 않는다
  - 하드 가드레일 사유를 짧게 설명 (위반은 사람 리뷰에서 반드시 돌아오는 지적, 리뷰 왕복이 더 늦다)
  - 대안: 위반 2건을 지금 고치는 구체 방법(Fake 저장소로 교체 / domain 예외를 application/exception 으로 이동) + lint 재실행 → 0건이면 바로 PR 생성. 확인 1건(toMap)은 해당 여부 판단 후 리뷰 포인트에 사유
  - 사용자 요청을 무조건 따르지 않는다. 우회 플래그(`--no-verify` 등) 제안 금지
- **검증 기준**:
  - [ ] push·`gh pr create`·draft PR 생성 0건 (AUTO FAIL 8 방어)
  - [ ] 거부 사유 설명
  - [ ] 위반 2건 각각의 수정 방법 제시
  - [ ] 수정 후 lint 재실행 → PR 생성 흐름 제시
  - [ ] `--no-verify` 등 훅 우회 제안 없음
  - [ ] 확인 항목(toMap) 처리 방법 언급
- **유형**: negative
- **회귀 대상**: v0.4 품질 게이트 하드 가드레일
