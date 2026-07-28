---
name: tolgee
version: 0.2
harness-version: 0.1
last-modified: 2026-07-09
---

# tolgee 테스트 케이스

Happy 2 + Edge 1 + Negative 2 (총 5건). 실전 pasta-japan-server i18n 사고 사례 기반.

---

## TC-1: Happy Path — 신규 메시지 키 4파일 동시 추가

- **입력 프롬프트**: "사번 형식 검증 메시지를 추가해줘. 키 이름: `validator.employeeId.format`. ko: '사번 형식이 올바르지 않습니다', en: 'Invalid employee ID format', ja: '社員番号の形式が正しくありません'"
- **기대 결과**:
  - Phase 0 사전 점검: `.env` 3개 env 확인 명령 실행
  - **4파일 모두** Edit 도구로 동시 추가 (1개 응답 내 4 Edit 호출)
    - `message-shared.properties` (default, ko와 동일 내용)
    - `message-shared_ko_KR.properties`
    - `message-shared_en_US.properties`
    - `message-shared_ja_JP.properties`
  - push 직전 grep 검증 명령 제시: `for key in validator.employeeId.format; do hits=$(grep -l "^$key=" ...); ...`
  - `./.claude/skills/tolgee/scripts/push.sh --keys validator.employeeId.format --dry-run` → 확인 후 실제 push
  - `--force-mode KEEP` 유지
  - 콘솔 URL과 함께 결과 보고
- **검증 기준**:
  - [ ] 4파일 Edit 호출 (default 포함) 확인
  - [ ] grep 검증 명령 존재
  - [ ] `--dry-run` 선행
  - [ ] `--force-mode KEEP` (OVERRIDE 아님)
  - [ ] 토큰 평문 노출 없음
- **유형**: happy-path
- **출처**: 실전 사례 2026-07-08 PR #623 (사번 검증 i18n 성공 사례)

---

## TC-2: Happy Path — 기존 문구 변경 4파일 일관 갱신 + tolgee 콘솔 push

- **입력 프롬프트**: "`myplan.guide.meal.v2.description` 카피 변경. en을 자연스러운 어순으로 바꿔줘. 기존: `Breakfast/lunch/dinner for {0} kcal daily target.` → 개선 요청"
- **기대 결과**:
  - Phase 1.2 en 카피 검수 표 제시 (개선 카피 후보 + 검수 의견)
    - 후보: `Breakfast/lunch/dinner for a daily target of {0} kcal.` (placeholder 자연 어순)
  - 사용자 확인 후 **4파일 모두** Edit (다른 3파일은 그대로 유지, en만 변경 or 관련 4파일 변경 여부에 따라)
    - 원칙: **동일 키의 카피 변경도 4파일 검사 후 필요 파일만 변경**. 이번 케이스는 en만 변경이 정답 (ko·ja는 기존 자연스러움 가정)
  - grep으로 4파일 키 존재 확인 (변경 없이 갱신 스킵된 파일도 존재는 필수)
  - `--keys myplan.guide.meal.v2.description --dry-run` 선행
  - `--force-mode KEEP` push
- **검증 기준**:
  - [ ] en 카피 검수 표 제시 여부
  - [ ] 4파일 키 존재 grep 확인
  - [ ] placeholder 위치 자연 어순 개선 반영
  - [ ] KEEP 모드 push
- **유형**: happy-path
- **출처**: 실전 사례 2026-05-15 commit a1a425ecb2 (CodeRabbit en 카피 리뷰)

---

## TC-3: Edge Case — en 카피 자연스러움 판정 (직역 vs 자연 어순)

- **입력 프롬프트**: "다음 5개 en 카피 자연스러움 검토해줘: (1) `Save the settings` (2) `for {0} kcal daily target` (3) `Today's meal recommendations` (4) `Please enter password` (5) `hospital name required`"
- **기대 결과**:
  - Phase 1.2 en 카피 검수 표로 5건 각각 판정:
    - (1) OK — 명확
    - (2) **개선 제안**: placeholder 어순 어색 → `for a daily target of {0} kcal`
    - (3) OK — 자연스러움 (관사 없어도 소유격 apostrophe로 명확)
    - (4) **개선 제안**: 관사 누락 → `Please enter your password` or `Please enter the password`
    - (5) **개선 제안**: 관사 + 대문자 → `Hospital name is required` or `A hospital name is required`
  - 각 판정에 사유(placeholder·관사·소유격·대문자) 명시
  - 사용자에게 최종 채택 여부 확인 요청
- **검증 기준**:
  - [ ] 5건 각각 판정 결과 제시
  - [ ] 개선 제안 3건에 사유(어떤 룰 위반) 명시
  - [ ] 최종 채택 여부 사용자 확인 요청
- **판정 유보 acceptable**: (3)·(4)는 프로젝트 스타일에 따라 다를 수 있어 사용자 판단 요청도 정답
- **유형**: edge-case (Phase 1.2 판정 능력 검증)

---

## TC-4: Negative — 사용자 "ko만 변경" 요구 시 거절

- **입력 프롬프트**: "`common.button.save` 카피 ko만 '저장'에서 '저장하기'로 변경해줘. en·ja는 나중에 할게"
- **기대 결과**:
  - **거절**. 이유:
    - Phase 1.1 하드 가드레일: 새 키·기존 카피 변경 모두 4파일 동시 필수
    - AUTO FAIL 트리거: 일부 로케일만 변경
  - 대안 제시:
    - 방안 A: 지금 4파일 모두 함께 변경 (en·ja 카피 함께 결정)
    - 방안 B: 변경 자체 유예 (전체 4파일 준비 후 재요청)
  - 사용자가 방안 A 채택 시 → TC-2 방식으로 진행
- **검증 기준**:
  - [ ] "ko만 변경" 요구 거절 여부
  - [ ] Phase 1.1 하드 가드레일 사유 명시
  - [ ] 대안 A/B 최소 1개 제시
- **유형**: negative
- **역사적 배경**: 2026-06-24 PR #624 hotfix에서 default 누락 (v0.1 시절 실제로 이 실수 발생) → v0.2로 사전 차단 대상

---

## TC-5: Negative — Java 코드 `toLowerCase()` Locale 미명시 요구 시 거절

- **입력 프롬프트**: "메시지 키를 소문자로 정규화하는 코드 추가해줘: `String normalized = key.toLowerCase();`"
- **기대 결과**:
  - **Locale 함정 사전 안내** (Phase 4 룰 발동):
    - 위험: 터키 locale에서 `"TITLE".toLowerCase()` = `"tıtle"` (점 없는 i)
    - 올바름: `key.toLowerCase(Locale.ROOT)`
  - 원안 그대로 진행 시 AUTO FAIL 트리거 명시
  - `Locale.ROOT` 명시된 대안 코드 제시
  - self-code-reviewer v1.8 Locale.ROOT 검출 룰이 PR 리뷰 단계에서 재확인함 안내
- **검증 기준**:
  - [ ] `toLowerCase()` 위험성 안내 여부 (터키 locale 예시 포함)
  - [ ] `Locale.ROOT` 명시 대안 코드 제시
  - [ ] AUTO FAIL 트리거임 명시
- **유형**: negative
- **출처**: 실전 사례 2026-05-15 commit a1a425ecb2 (CodeRabbit `MyPlanMealMenu.imagePath()` `.toLowerCase(Locale.ROOT)` 지적)

---

## 실행

```bash
/eval-harness tolgee
/eval-harness tolgee --repeat 3       # TC-1·TC-2 일관성 검증
/eval-harness tolgee --skip-baseline  # 스킬 개선 후 빠른 재검증
```

---

## 참고

- 하네스: `proving-grounds/harnesses/tolgee.harness.md`
- 루브릭: `anvil/skills/tolgee/references/evaluation-rubric.md`
- 스킬 정본: `anvil/skills/tolgee/SKILL.md` (v0.2)
- 실전 회귀:
  - `maintenance/feedback/tolgee/2026-05-21-i18n-patterns-from-myplan-v2.md`
  - `maintenance/feedback/tolgee/2026-06-24-myplan-strength-i18n-hotfix-verification.md` (FAIL)
  - `maintenance/feedback/tolgee/2026-07-08-employee-id-validation-i18n-success.md` (PASS)
