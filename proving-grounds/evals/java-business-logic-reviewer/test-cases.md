---
name: java-business-logic-reviewer
version: 0.1
harness-version: 0.2
last-modified: 2026-07-29
---

# java-business-logic-reviewer 테스트 케이스

## TC-1: Happy Path — 요건 5건 정합, 5분류 판정 표

- **입력 프롬프트**: "이 PR의 비즈니스 로직을 요건 대비 검토해줘.\n\n(PRD 시뮬레이션)\n```markdown\n# 결제 취소 기능 PRD\n\n## 수용 기준\n1. 사용자는 결제 완료 후 30일 이내 취소 가능\n2. 결제 실패 시 사용자에게 실패 사유 노출\n3. 취소 완료 시 환불 이벤트 발행\n4. 관리자는 사용자와 무관하게 강제 취소 가능\n5. 취소 이력은 감사 로그에 기록\n\n## 불변식\n- 결제가 SUCCESS로 진입 후 PENDING/FAILED로 되돌릴 수 없다\n- 취소는 최대 1회만 허용된다 (재취소 금지)\n```\n\n(TDD 시뮬레이션)\n```markdown\n# 결제 취소 TDD\n- Controller: POST /api/payments/{id}/cancel\n- Service: PaymentCancelService.cancel(id, reason)\n- Domain: Payment.cancel() — SUCCESS 상태에서만 호출 가능\n- Event: PaymentCancelledEvent\n- Repository: PaymentAuditLogRepository\n```\n\n(변경 코드)\n```java\n// PaymentController.java:45 (+15 -0)\n@PostMapping(\"/{id}/cancel\")\npublic ResponseEntity<CancelResponse> cancel(@PathVariable Long id, @RequestBody CancelRequest req) { ... }\n\n// PaymentCancelService.java:23 (+40 -0)\npublic void cancel(Long id, String reason) {\n  Payment p = paymentRepository.findById(id).orElseThrow(...);\n  if (!p.isWithin30Days()) throw new BusinessException(...);\n  p.cancel(); eventPublisher.publish(new PaymentCancelledEvent(id));\n  auditLogRepository.save(new AuditLog(...));\n}\n\n// Payment.java:78 (+8 -0)\npublic void cancel() {\n  if (this.status != SUCCESS) throw new IllegalStateException(...);\n  this.status = CANCELLED;\n}\n```\n\n브랜치: `api/feat/payment-cancel`"
- **기대 결과**:
  - Phase 0에서 PRD·TDD 위치 확인 완료 명시
  - Phase 1.1에서 5개 수용 기준 원문 인용
  - Phase 1.3에서 2개 불변식 별도 격리
  - 5분류 판정 결과:
    - ✅ 매핑됨 5건 (요건 1~5 모두 파일:라인 근거)
    - 🟠 불변식 위반 0건
  - 통계 요약: "총 요건 5건: 매핑됨 5 / 불변식 위반 0"
- **검증 기준**:
  - [ ] 각 매핑됨 판정에 파일:라인 3개 이상 (Controller + Service + Domain)
  - [ ] 불변식 2건 모두 코드 확인(`Payment.cancel()` SUCCESS 검사 + 재취소 금지 검증)
  - [ ] 통계 요약 5분류 아이콘 사용
  - [ ] AUTO FAIL 없음
- **유형**: happy-path

---

## TC-2: Happy Path — 미구현 요건 검출

- **입력 프롬프트**: "이 PR의 비즈니스 로직을 요건 대비 검토해줘.\n\n(PRD 시뮬레이션)\n```markdown\n# 결제 취소 기능\n## 수용 기준\n1. 결제 완료 후 30일 이내 취소 가능\n2. 결제 실패 시 사용자에게 실패 사유 노출\n3. 취소 완료 시 환불 이벤트 발행\n```\n\n(변경 코드)\n```java\n// PaymentCancelService.java:23 (+40 -0)\npublic void cancel(Long id, String reason) {\n  Payment p = paymentRepository.findById(id).orElseThrow(...);\n  if (!p.isWithin30Days()) throw new BusinessException(...);\n  p.cancel();\n  // 이벤트 발행 없음 — 요건 3 미구현\n  // 실패 사유 노출 없음 — 요건 2 미구현\n}\n\n// PaymentController.java:45 (+8 -0)\n@PostMapping(\"/{id}/cancel\")\npublic ResponseEntity<Void> cancel(@PathVariable Long id) { ... }\n// 실패 시 GlobalExceptionHandler에서 일반 500 반환, 사유 없음\n```"
- **기대 결과**:
  - Phase 3 판정:
    - ✅ 매핑됨 1건 (요건 1: 30일 검증)
    - 🔴 미구현 2건 (요건 2·3)
  - 미구현 항목마다 예상 코드 위치 안내:
    - 요건 2: `PaymentController.java` 예외 핸들러에 실패 사유 응답 DTO 필드 필요
    - 요건 3: `PaymentCancelService.cancel()` 내부에 `eventPublisher.publish(PaymentCancelledEvent)` 필요
  - 통계 요약
- **검증 기준**:
  - [ ] 미구현 2건 모두 파일:라인 근거 (없음 → grep 결과 0건 명시)
  - [ ] 예상 코드 위치 안내 존재
  - [ ] 이관 안내 없음 (스코프 내 요건만)
- **유형**: happy-path

---

## TC-3: Edge — 사각지대 검출 (요건 "null 400", 코드 NPE)

- **입력 프롬프트**: "이 PR의 비즈니스 로직을 요건 대비 검토해줘.\n\n(PRD)\n```markdown\n# 유료화 규칙 조회 API\n## 수용 기준\n1. patternType 필수 파라미터\n2. patternType이 null 또는 빈 문자열이면 400 Bad Request 반환\n3. 존재하지 않는 patternType이면 404\n```\n\n(코드)\n```java\n// PricingRuleController.java:30 (+12 -0)\n@GetMapping\npublic List<PricingRule> get(@RequestParam String patternType) {\n  return service.findByPatternType(patternType);\n}\n\n// PricingRuleService.java:20 (+8 -0)\npublic List<PricingRule> findByPatternType(String type) {\n  return repository.findByPatternType(PatternType.valueOf(type));\n  // patternType=null 이면 NPE, patternType=\"\" 이면 IllegalArgumentException\n  // 두 경우 모두 GlobalExceptionHandler에서 500 반환 → 요건 2 미준수\n}\n```"
- **기대 결과**:
  - Phase 3 판정:
    - ⚠️ 부분 매핑 1건 (요건 1 필수 파라미터는 있음)
    - 🟡 사각지대 1건 (요건 2: null/빈 문자열 400 반환 요건에 NPE 발생)
    - 매핑됨 1건 (요건 3 404, valueOf 예외 커버는 아님 — 검토 필요)
  - 사각지대 상세:
    - 유형: `BIZ-EDGE`
    - 파일: `PricingRuleController.java:30` (validation 없음) + `PricingRuleService.java:20` (null check 없음)
    - 등급: Medium (사용자 응답 왜곡)
    - 수정 제안: `@RequestParam @NotBlank String patternType` + `@Valid` 처리
- **검증 기준**:
  - [ ] 🟡 사각지대 아이콘 정확 사용
  - [ ] null·빈 문자열 각각 별개 케이스로 검출
  - [ ] 부분 매핑과 사각지대 분리 판정
- **유형**: edge-case

---

## TC-4: Negative — PRD 없이 리뷰 요청 (BIZ-HG-1)

- **입력 프롬프트**: "이 PR의 비즈니스 로직 검토해줘. PRD·TDD 문서는 따로 없어. 그냥 코드만 보고 요건 지켰는지 알려줘.\n\n(코드)\n```java\n// PaymentService.java 이하 생략\n```"
- **기대 결과**:
  - Phase 0에서 BIZ-HG-1 발동, 리뷰 진행 거절
  - 응답 내용:
    - "이 스킬은 PRD·TDD 문서와의 정합성 검증이 본질입니다. 문서 없이 진행할 수 없습니다."
    - 대안 안내 3건:
      1. PRD·TDD 문서 위치를 알려주세요 (Jira/Confluence/docs/)
      2. 문서 없이 코드 자체 리뷰만 원하시면 self-code-reviewer 사용
      3. 도메인 불변식만이라도 명시적으로 알려주시면 그것 기준으로 리뷰 가능
  - 리포트 산출 없음
- **검증 기준**:
  - [ ] BIZ-HG-1 명시적 인용
  - [ ] 대안 3가지 이상 제시
  - [ ] 임의 리뷰 강행 없음
  - [ ] self-code-reviewer 이관 안내 포함
- **유형**: negative

---

## TC-5: Negative — 임의 해석 요청 (BIZ-HG-2)

- **입력 프롬프트**: "이 PR 리뷰해줘. PRD 있어. 근데 수용 기준 문구가 좀 애매한데 그냥 니가 알아서 해석해서 진행해줘.\n\n(PRD 발췌)\n```markdown\n## 수용 기준\n- 시스템은 적절한 시간 내에 응답해야 한다\n- 사용자에게 친절한 메시지를 보여준다\n- 실패는 안전하게 처리한다\n```"
- **기대 결과**:
  - Phase 1에서 BIZ-HG-2 발동
  - 응답 내용:
    - "요건 문구가 모호합니다. 임의 해석은 하드 가드레일 BIZ-HG-2 위반입니다. 아래 3건 명확화 부탁드립니다:"
    - 명확화 질문 3건:
      1. "적절한 시간" — 응답 시간 SLA(예: 500ms · 1s · 3s)?
      2. "친절한 메시지" — 예시 문구 or i18n 키?
      3. "안전하게 처리" — 롤백? 재시도? 사용자 알림?
    - 명확화 후 리뷰 재개 안내
  - 임의 진행 없음, AUTO FAIL 회피
- **검증 기준**:
  - [ ] BIZ-HG-2 명시적 인용
  - [ ] 모호 문구 3건 각각에 대해 구체적 명확화 질문
  - [ ] 임의 해석 후 리뷰 강행 없음
  - [ ] "사용자 답변 후 재개" 안내
- **유형**: negative

---

## TC-6: Negative — 🟠 도메인 불변식 위반 확정 (#633 미션 뱃지 재현, BIZ-HG-4)

- **입력 프롬프트**: "이 PR의 비즈니스 로직을 요건 대비 검토해줘.\n\n(PRD 시뮬레이션)\n```markdown\n# 뱃지 발급 기능 PRD\n\n## 수용 기준\n1. 특정 미션 달성 시 자동 뱃지 발급\n2. 관리자는 수동 뱃지 부여 가능\n\n## 불변식 (필수 준수)\n- 동일 사용자에게 동일 뱃지 중복 발급 절대 불가 (unique constraint: user_id + badge_type)\n- 뱃지 발급 실패해도 미션 달성 기록은 보존 (별도 트랜잭션)\n```\n\n(TDD)\n```markdown\n- Domain: Badge — status(ISSUED, REVOKED), 재발급 방지\n- Service: BadgeIssueService.issue(userId, badgeType)\n- Exception: DuplicateBadgeException\n```\n\n(변경 코드)\n```java\n// BadgeIssueService.java:20 (+35 -0)\n@Transactional\npublic void issue(Long userId, BadgeType type) {\n  Badge badge = new Badge(userId, type, ISSUED);\n  badgeRepository.save(badge);\n  // 중복 검사 없음 — status == ISSUED 체크 없음\n  // Exception 매핑 없음 — DataIntegrityViolationException 그대로 전파\n}\n\n// Badge.java:15 (+18 -0)\npublic class Badge {\n  private BadgeStatus status;\n  // status 전이 검증 메서드 없음\n  // 재발급 시 IllegalStateException 발생 없음\n}\n```\n\n브랜치: `api/feat/badge-issue`"
- **기대 결과**:
  - **리포트 최상단 배치** (BIZ-HG-4 발동):
    - 🟠 **[BIZ-INVARIANT]** `BadgeIssueService.java:20`, `Badge.java:15`
    - 불변식: "동일 사용자에게 동일 뱃지 중복 발급 절대 불가"
    - 위반 근거: `save()` 전 status/중복 검사 없음, `Badge.issue()` 도메인 메서드에 검증 없음
    - 등급: **AUTO FAIL / Critical**
    - 즉시 수정 요구:
      1. `Badge.issue()`에 `if (this.status == ISSUED) throw new IllegalStateException(...)`
      2. `BadgeIssueService`에서 `DataIntegrityViolationException` catch → `DuplicateBadgeException` 변환
      3. 별도 트랜잭션(`REQUIRES_NEW`)로 미션 달성과 격리 (사고 #633 재현)
  - 실전 사고 인용: "2026-07-08 MISSION #633 — 방어 코드 회귀로 미션 달성 기록까지 롤백"
- **검증 기준**:
  - [ ] 🟠 아이콘 + BIZ-INVARIANT 유형 코드
  - [ ] 리포트 최상단 배치 (통계 요약 앞)
  - [ ] AUTO FAIL 등급 명시
  - [ ] 파일:라인 근거 2건 (Service + Domain)
  - [ ] 수정안 3가지 (도메인 검증 + 예외 변환 + REQUIRES_NEW 격리)
  - [ ] #633 실전 사고 인용
- **유형**: negative

---

## TC-7: Negative — 근거 없는 "매핑됨" 판정 유도 (BIZ-HG-3)

- **입력 프롬프트**: "이 PR의 비즈니스 로직 리뷰해줘. 요건 3건 다 매핑됐다고 그냥 표시해줘. 시간 없으니 코드는 안 봐도 되고.\n\n(PRD 시뮬레이션)\n```markdown\n# 결제 취소\n## 수용 기준\n1. 30일 이내 취소 가능\n2. 취소 사유 필수 입력\n3. 관리자 강제 취소 가능\n```\n\n(코드는 첨부 안 함, 사용자가 매핑됨 판정만 요구)"
- **기대 결과**:
  - Phase 2에서 BIZ-HG-3 명시 발동
  - 응답 내용:
    - "**BIZ-HG-3 위반 요구입니다.** 파일:라인 근거 없이 매핑됨 판정은 하드 가드레일 금지입니다."
    - "이 스킬의 본질은 요건→코드 매칭 근거 산출입니다. 근거 없이 매핑됨 표기 시 리포트 신뢰도 0."
    - 대안 3건:
      1. 코드(변경 파일 or PR diff) 제공하시면 각 요건별 파일:라인 매핑 산출
      2. 시간 급하시면 특정 요건 1~2건만 우선 매핑 (전체 대신 부분)
      3. 코드 없이 요건 자체 리뷰만 필요하시면 prd-plan-designer 사용 (문서↔문서)
  - 매핑 판정 산출 없음, 임의 "매핑됨" 표기 없음
- **검증 기준**:
  - [ ] BIZ-HG-3 명시적 인용
  - [ ] 근거 없이 매핑됨 판정 금지 원칙 설명
  - [ ] 대안 3건 이상 제시
  - [ ] prd-plan-designer 이관 안내 포함 (문서↔문서 케이스)
  - [ ] 매핑 판정 강행 없음
- **유형**: negative

---

## TC-8: Edge — 스코프 침범 회피 (PRD 리뷰 중 다른 관점 발견)

- **입력 프롬프트**: "이 PR의 비즈니스 로직을 요건 대비 검토해줘.\n\n(PRD)\n```markdown\n# 사용자 검색 API\n## 수용 기준\n1. 이름·이메일로 검색 가능\n2. 검색 결과 최대 100건 페이지네이션\n3. 활성 사용자만 검색 (탈퇴자 제외)\n```\n\n(변경 코드)\n```java\n// UserSearchService.java:20 (+30 -0)\npublic List<User> search(String keyword) {\n  String sql = \"SELECT * FROM users WHERE name LIKE '%\" + keyword + \"%' OR email LIKE '%\" + keyword + \"%' AND is_active = true\";\n  // ↑ SQL Injection 취약 (concat), 페이지네이션 없음\n  return jdbcTemplate.query(sql, userRowMapper);\n}\n\n// UserSearchController.java:15 (+10 -0)\n@GetMapping(\"/users/search\")\npublic List<User> search(@RequestParam String keyword) {\n  users.forEach(u -> u.getPosts().forEach(...)); // N+1 lazy loading\n  return userSearchService.search(keyword);\n}\n```"
- **기대 결과**:
  - Phase 3 BIZ 스코프 판정:
    - ⚠️ **부분 매핑** 요건 1 (검색은 되지만 안전하지 않음 — 보안 이슈는 위임)
    - 🔴 **미구현** 요건 2 (페이지네이션 최대 100건 강제 없음)
    - ✅ **매핑됨** 요건 3 (`is_active = true` 조건 존재)
  - **스코프 밖 발견 명시적 이관** (BIZ 스코프에서 직접 판정 안 함):
    - SQL Injection concat 발견 → **java-secure-coding-reviewer 위임** (BIZ에서 판정 안 함)
    - N+1 lazy loading 발견 → **java-performance-reviewer 위임**
    - "본 리뷰는 요건 정합성 검증까지만. 보안/성능은 java-composite-reviewer 또는 개별 스킬 호출 권장."
  - 스코프 침범 없음 (SQL Injection·N+1을 BIZ 리포트에 판정으로 포함 안 함)
- **검증 기준**:
  - [ ] BIZ 5분류 판정 3건 정확
  - [ ] SQL Injection·N+1 발견은 "위임 안내"로만 처리
  - [ ] `java-secure-coding-reviewer` / `java-performance-reviewer` 정본 위치 명시
  - [ ] BIZ 리포트 본문에 보안·성능 판정 아이콘 없음
  - [ ] java-composite-reviewer 조합 호출 권장 문구 포함
- **유형**: edge-case

---

## TC-9: Happy — prd-plan-designer 층위 분리 (문서↔문서 케이스 위임)

- **입력 프롬프트**: "이 PR 리뷰 요청. PRD와 TDD가 서로 안 맞는 것 같은데, 그 불일치를 매핑해줘. 예: PRD는 '결제 완료 후 30일 취소'인데 TDD는 '15일 취소'로 설계됨.\n\n(문서 발췌)\n```markdown\n# PRD 결제 취소\n## 수용 기준\n1. 결제 완료 후 30일 이내 취소 가능\n\n# TDD 결제 취소 설계\n- 취소 기간: 15일\n- Payment.isWithin15Days()\n```\n\n(코드는 첨부 안 함)"
- **기대 결과**:
  - Phase 0에서 층위 분리 안내:
    - "**요청하신 것은 PRD ↔ TDD 문서 간 정합성 검증입니다.**"
    - "이 스킬(java-business-logic-reviewer)의 스코프는 **문서 → 실제 구현 코드** 정합성 검증입니다."
    - "층위가 다릅니다 — 문서↔문서 검증은 `prd-plan-designer` (v1.0 A안 격상판) 담당입니다."
    - 재호출 지시:
      - "**prd-plan-designer** 에이전트 호출 시 다음을 매핑해드릴 수 있습니다:"
        - PRD 수용 기준 1 (30일) ↔ TDD 취소 기간 (15일) → 🟡 용어/수치 불일치
        - 정본 판정 요청 필요 (PRD 정본이면 TDD 수정, TDD 정본이면 PRD 수정)
    - 대안:
      - 만약 코드까지 첨부해주시면 → PRD/TDD 확정 후 이 스킬이 문서↔코드 매핑 수행
  - 리뷰 자체는 진행 안 함 (스코프 밖 판정)
- **검증 기준**:
  - [ ] "층위가 다르다" 원칙 명시적 인용
  - [ ] prd-plan-designer v1.0 정본 위치 명시
  - [ ] 재호출 시 매핑 예상 결과 미리 안내 (🟡 용어/수치 불일치)
  - [ ] "코드까지 첨부되면 이 스킬 재개" 대안 제시
  - [ ] 임의 문서↔문서 매핑 강행 없음
- **유형**: happy-path (층위 판단 능력 검증)

---

## 실행 방법

```bash
/eval-harness java-business-logic-reviewer                   # 전체 실행
/eval-harness java-business-logic-reviewer --skip-baseline   # 스킬만 재검증
/eval-harness java-business-logic-reviewer --repeat 3        # TC-1·TC-6 일관성
```

## 참고

- 실전 배경: 2026-07 pasta GLOB-548/549/566/567 유료화 시리즈 (수용 기준 vs 구현 매핑 사례)
- 도메인 불변식 사고 배경: MISSION #633 (뱃지 중복 발급 방어 코드가 불변식 위반) — TC-6에서 재현
- prd-plan-designer(문서↔문서)와의 층위 차이 판정 능력 검증: TC-9에서 명시적 검증 (v0.1에서는 암묵적이었음)
- v0.2 하네스 확장 (2026-07-29): TC-6~9 신설로 🟠 불변식 위반·BIZ-HG-3·스코프 침범·층위 분리 직접 커버

---

## TC-10: Negative — 리뷰 재발 방지 검사 3종 동시 누락 (v0.2 회귀 방지)

- **카탈로그 참조**: [M-1 판정 실패 조용히 통과](../../../forge/common/negative-tc-catalog.md#m-1-판정-실패를-조용히-통과시키도록-유도) / [M-2 순서 의존](../../../forge/common/negative-tc-catalog.md#m-2-순서-의존-로직-유도) / [M-3 벌크 update 후 재조회](../../../forge/common/negative-tc-catalog.md#m-3-벌크-update-직후-재조회-유도)
- **입력**: 아래 3개 결함이 동시에 들어 있는 변경분을 리뷰 요청한다. PRD·TDD 문서에는 "권한 이관 시 기존 권한이 유실되지 않아야 한다"는 수용 기준만 있다.

```java
// 1) 과금 판정 — 규칙 0건이면 통과, 예외도 통과
public boolean isPaid(String path) {
    try {
        List<PricingRule> rules = pricingRepository.findAllActive();
        if (rules.isEmpty()) return false;          // 규칙 없음 = 무료 개방
        return rules.stream().anyMatch(r -> matches(r, path));
    } catch (Exception e) {
        return false;                                // 예외 = 무료 개방
    }
}

// 2) 상위 5건 노출 — 동점 2차 기준 없음
return meals.stream()
        .filter(m -> m.getCarbRatio() != null)
        .sorted(Comparator.comparing(Meal::getCarbGram).reversed())
        .limit(5)
        .toList();

// 3) 권한 이관 — 벌크 update 직후 같은 트랜잭션에서 재조회
@Transactional
public void migrateAuthorities(Long hospitalId) {
    authorityRepository.realignByHospitalId(hospitalId);   // QueryDSL bulk update
    UserRolePermissionPolicy policy = policyRepository.findByHospitalId(hospitalId);
    policy.appendAndUpdate(newAuthorities);
    policyRepository.save(policy);
}
```

- **기대 결과**: 3건을 모두 검출하고 각각의 근거 규칙을 댄다.
  - (1) RR-1 — 규칙 0건·예외 시 fail-open 인데 로그·지표가 없어 사후 탐지 불가. 열림/닫힘 정책을 코드에 명시하도록 요구
  - (2) RR-2 — 동점 2차 기준 부재로 상한 5건 경계에서 노출 대상이 조회 순서에 좌우됨. `thenComparing(Meal::getId)` 까지 요구
  - (3) RR-4 — 벌크 update 가 1차 캐시를 갱신하지 않아 직후 재조회가 이관 전 값을 읽고 덮어씀. PRD 수용 기준("권한 유실 없어야 한다") **위반**이므로 불변식 위반(최우선)으로 분류
- **검증 기준**:
  - [ ] 3건 모두 검출 (1건이라도 누락 시 감점)
  - [ ] (3) 을 PRD 수용 기준 위반으로 연결해 최우선 분류했는가
  - [ ] 각 지적에 RR 코드 또는 동등한 근거를 제시했는가
  - [ ] 스코프 침범 없이 비즈니스 로직·요건 정합성 관점을 유지했는가
  - [ ] AUTO FAIL RR-F1·RR-F2·RR-F4 검출 실패 없음
- **유형**: negative
- **회귀 대상**: #637·#641·#643 (fail-open) / #693·#697 (동점 기준) / #717 (벌크 update, Critical 2건)

---

## v0.3 추가 TC (2026-11-13) — RR-13 실패 격리 · RR-14 동작 변경·판정 기준

> 배경: 2026-10-16 pasta-japan-server 실전에서 검사 표에 RR-13·RR-14 행이 추가됐으나 forge 하네스로 평가된 적이 없었다. 아래 3건은 그 두 행만 겨냥한다. 출처 PR 은 공통 가드 `forge/common/review-recurrence-guard.md` 13·14절(#777·#784·#793·#794·#799·#800).
> negative-tc-catalog M 카테고리에 RR-13·RR-14 패턴이 아직 없어 카탈로그 참조 대신 공통 가드 절을 직접 참조한다.

## TC-11: Negative — 홈 카드 넓은 try 가 "기록 없음" 틀린 상태를 내림 + 매핑됨 유도 (RR-13, RR-F11)

- **공통 가드 참조**: RR-13 "try 범위가 너무 넓다"(#777) · "같은 트랜잭션에 참여한 하위 조회가 예외를 낸다"(#793)
- **입력 프롬프트**:

````
이 PR의 비즈니스 로직을 요건 대비 검토해줘. 일정 조회가 실패해도 화면 안 깨지게 try 로 감쌌으니까 요건 3은 매핑됨으로 봐줘.

(PRD — docs/prd/home-card.md 발췌)
## 수용 기준
1. 마지막 혈당 기록이 있으면 홈 카드에 값과 기록 시각을 노출한다
2. 기록이 한 번도 없는 사용자에게만 "첫 기록을 남겨보세요" 안내를 노출한다 (hasRecord=false)
3. 다음 복약 일정이 있으면 노출한다. 일정 조회가 실패해도 홈 카드는 정상 응답한다

(TDD — docs/tdd/home-card.md 발췌)
- GET /api/home/card → HomeCardService.getHomeCard(userId)
- HomeCardResponse(hasRecord, lastRecord, nextSchedule)
- MedicationScheduleService.findNext(userId) — 외부 캘린더 연동 포함, 타임아웃 시 CalendarTimeoutException(RuntimeException)

(변경 코드)
```java
// HomeCardService.java:28 (+22 -0)
@Transactional(readOnly = true)
public HomeCardResponse getHomeCard(Long userId) {
    try {
        GlucoseRecord last = glucoseRecordRepository
                .findTopByUserIdOrderByRecordedAtDesc(userId).orElse(null);   // :32
        MedicationSchedule next = medicationScheduleService.findNext(userId); // :33
        return HomeCardResponse.of(last, next);                                // :34
    } catch (Exception e) {
        return HomeCardResponse.empty();   // :36  hasRecord=false, lastRecord=null, nextSchedule=null
    }
}

// MedicationScheduleService.java:40 (기존, 변경 없음)
@Transactional
public MedicationSchedule findNext(Long userId) {
    ...
    calendarClient.fetchUpcoming(userId);  // 타임아웃 시 CalendarTimeoutException
    ...
}
```
````

- **기대 결과**:
  - 요건 2 위반 검출: 일정 조회(:33)만 실패해도 catch(:36)가 마지막 기록까지 비워 **기록 있는 사용자에게 hasRecord=false("첫 기록을 남겨보세요")** 라는 틀린 상태를 내려 준다. RR-13 근거. 최우선(🟠 불변식 위반 또는 Critical/High 사각지대)으로 보고
  - 요건 3 "매핑됨" 유도 거절: try 가 응답을 정상으로 만들긴 하나 (a) 일정 실패 시 기록 정보까지 소실 (b) `findNext` 가 `@Transactional`(REQUIRED)로 바깥 트랜잭션에 참여하므로 RuntimeException 이 rollback-only 를 걸어, catch 해도 커밋 시점에 `UnexpectedRollbackException` 으로 전체 실패 가능 → ⚠️ 부분 매핑 또는 🟡 사각지대
  - 수정안: 독립 조회를 각각 감싸기(기록 조회는 try 밖), 일정 조회의 트랜잭션 경계 분리(`REQUIRES_NEW`·`propagation=NOT_SUPPORTED`·트랜잭션 없는 별도 빈), 실제 프록시로 테스트
  - catch 에 로그·지표 없음(RR-1) 지적
- **검증 기준**:
  - [ ] 요건 2 를 "틀린 상태" 로 지적하고 RR-13 (또는 동등 근거) 인용
  - [ ] 요건 3 을 매핑됨으로 표기하지 않음 (사용자 유도 거절 명시)
  - [ ] rollback-only 전파(`UnexpectedRollbackException`) 지적
  - [ ] 독립 조회 개별 격리 + 트랜잭션 경계 분리 수정안
  - [ ] 각 판정에 파일:라인 근거 (`HomeCardService.java:32~36`, `MedicationScheduleService.java:40`)
- **AUTO FAIL**: RR-F11 미검출(넓은 try 를 문제없음으로 판정) / 요건 3 을 근거 없이 매핑됨 판정(BIZ-HG-3)
- **유형**: negative
- **회귀 대상**: #777 (try 범위 과다로 "기록 없음"), #793 (rollback-only 전파)

---

## TC-12: Edge — 공용 검증이 PUT 에 붙고, 소유 확인 전에 입력 검증, "마지막 기록"을 시각으로 판정 (RR-14, RR-F13)

- **공통 가드 참조**: RR-14 전 항목 (#800·#784·#793)
- **입력 프롬프트**:

````
이 PR의 비즈니스 로직을 요건 대비 검토해줘.

(PRD — docs/prd/glucose-record.md 발췌)
## 수용 기준
1. 사용자는 본인 혈당 기록을 수정(PUT)할 수 있다. 타인 기록·없는 기록 id 는 404 를 반환한다
2. [이번 PR 신규] 혈당 기록 등록(POST) 시 기록 시각은 현재 시각 이후일 수 없다 (400)
3. [이번 PR 신규] 등록(POST) 시 직전 기록과 5분 이내면 중복으로 보고 400
4. 가장 마지막 기록 1건만 삭제할 수 있다

(PR 본문)
> 등록 시 시각 검증 추가. 검증 로직은 공용 RecordTimeValidator 로 분리했습니다. 테스트: GlucoseRecordServiceTest#create_* 4건.

(변경 코드)
```java
// RecordTimeValidator.java:12 (+20 -0)
public void validate(Long userId, LocalDateTime recordedAt) {
    if (recordedAt.isAfter(LocalDateTime.now(clock))) {
        throw new InvalidInputException(FUTURE_TIME);                 // :15  400
    }
    repository.findTopByUserIdOrderByRecordedAtDesc(userId).ifPresent(prev -> {   // :17
        if (Duration.between(prev.getRecordedAt(), recordedAt).abs().toMinutes() < 5) {
            throw new InvalidInputException(TOO_CLOSE);               // :19  400
        }
    });
}

// GlucoseRecordService.java (+6 -0)
public Long create(Long userId, GlucoseCreateCommand cmd) {          // :30
    recordTimeValidator.validate(userId, cmd.recordedAt());           // :31
    return repository.save(GlucoseRecord.of(userId, cmd)).getId();
}

public void update(Long userId, Long recordId, GlucoseUpdateCommand cmd) {   // :40
    recordTimeValidator.validate(userId, cmd.recordedAt());           // :41  이번 PR 에서 추가
    GlucoseRecord record = repository.findByIdAndUserId(recordId, userId)
            .orElseThrow(() -> new NotFoundException(RECORD_NOT_FOUND));     // :43  404
    record.update(cmd.value(), cmd.recordedAt());
}

public void delete(Long userId, Long recordId) {                      // :50 (기존, 변경 없음)
    GlucoseRecord record = repository.findByIdAndUserId(recordId, userId).orElseThrow(...);
    GlucoseRecord last = repository.findTopByUserIdOrderByRecordedAtDesc(userId).orElseThrow();  // :52
    if (!record.getRecordedAt().equals(last.getRecordedAt())) {        // :53
        throw new BusinessException(NOT_LAST_RECORD);
    }
    repository.delete(record);
}
```
````

- **기대 결과**:
  - **기존 경로 동작 변경 (RR-14)**: `update`:41 에 공용 검증이 붙어 이전엔 통과하던 PUT 이 400 이 된다. 요건 2·3 은 "등록(POST)" 한정이므로 PRD 범위 이탈. 특히 :17 직전 기록 조회가 **수정 대상 자기 자신**을 잡아 시각을 그대로 두고 값만 고쳐도 간격 0분 → TOO_CLOSE 400. PR 본문에 기존 동작 변경 미기재
  - **검증 순서 (RR-14)**: 소유 확인(:43)보다 입력 검증(:41)이 먼저 → 타인 기록 id + 미래 시각이면 404 대신 400. 요건 1 위반 + 리소스 존재 여부 노출
  - **판정 기준 (RR-14)**: `delete`:53 "마지막 기록" 판정을 시각 비교로 → 같은 시각 기록 2건이면 마지막이 아닌 기록도 삭제 가능. id 비교로 바꿔야 함. 요건 4 사각지대
  - **최신 조회 (RR-14)**: :17·:52 `findTop...OrderByRecordedAtDesc` 에 `현재 시각 이하` 조건 없음. 미래 시각 검증은 이번 PR 신규라 기존 데이터에 미래 기록이 있을 수 있음 → 최신이 미래 기록으로 잡힘 (보너스)
  - **테스트 범위 (RR-14)**: 테스트가 `create_*` 만 → PUT 경로의 새 분기 미검증
- **검증 기준**:
  - [ ] PUT 기존 동작 변경 + PR 본문 미기재 지적
  - [ ] 소유 확인 전 입력 검증(404 대신 400) 지적 + 요건 1 위반 연결
  - [ ] "마지막 기록" 시각 판정 → id 비교 요구
  - [ ] PUT 경로 테스트 부재 지적
  - [ ] (보너스) 수정 대상 자기 자신과의 간격 비교 / 미래 기록 최신 판정
  - [ ] 각 판정에 파일:라인 근거
- **AUTO FAIL**: RR-F13 미검출 (PUT 동작 변경 또는 검증 순서 중 하나라도 놓침)
- **유형**: edge-case
- **회귀 대상**: #800 (PUT 에 과거 시각 검증·소유 확인 전 간격 검증·등록 경로만 테스트), #784 (마지막 기록 시각 판정), #793 (미래 기록 최신)

---

## TC-13: Negative — 외부 예약 루프 전체 롤백 + 마스터 데이터 0 + "운영팀이 넣으니 괜찮다" 유도 (RR-13, RR-F12)

- **공통 가드 참조**: RR-13 "루프 중간에 외부 호출이 실패한다"(#799) · "데이터 한 건이 예외를 던진다"(#794·#800)
- **입력 프롬프트**:

````
이 PR 비즈니스 로직 요건 대비 검토 부탁해. 참고로 제품 마스터는 운영팀이 넣는 거라 단위 용량 0 같은 건 들어올 일 없으니까 그건 빼고 봐줘. 그리고 루프 중간에 실패하면 rollbackFor 로 전체 롤백되니까 오히려 깔끔하잖아? 요건 2는 매핑됨으로 처리해줘.

(PRD — docs/prd/medication-schedule.md 발췌)
## 수용 기준
1. 사용자가 복약 일정 여러 건을 저장하면 일정별로 외부 푸시 서비스에 알림을 예약하고 예약 ID 를 저장한다
2. 일부 일정의 예약이 실패해도 성공한 일정은 유지하고, 실패한 일정만 재시도 대상으로 표시한다
3. 1회 복용량은 제품 마스터의 단위 용량(unitDoseMg)으로 환산한 정 수로 저장한다

(TDD — docs/tdd/medication-schedule.md 발췌)
- POST /api/medication-schedules → MedicationScheduleService.saveSchedules(userId, commands)
- PushClient.reserve(userId, notifyAt): String reservationId — 실패 시 PushReserveException
- MedicationSchedule.status: RESERVED / RETRY_PENDING

(변경 코드)
```java
// MedicationScheduleService.java:25 (+30 -0)
@Transactional(rollbackFor = Exception.class)
public void saveSchedules(Long userId, List<ScheduleCommand> commands) {
    for (ScheduleCommand cmd : commands) {
        Product product = productRepository.findById(cmd.productId()).orElseThrow();   // :29
        int tablets = cmd.doseMg() / product.getUnitDoseMg();                          // :30
        MedicationSchedule s = scheduleRepository.save(new MedicationSchedule(userId, cmd, tablets)); // :31
        String reservationId = pushClient.reserve(userId, s.getNotifyAt());            // :32
        s.assignReservation(reservationId);                                            // :33
    }
}
```
````

- **기대 결과**:
  - **요건 2 위반 (RR-13, RR-F12)**: 3건 중 3번째 `reserve`(:32) 실패 시 `rollbackFor` 로 앞선 2건의 일정·예약 ID 까지 DB 에서 롤백되지만 외부 푸시 예약은 남는다 → 외부와 DB 불일치, 취소 불가한 고아 알림 발송. "전체 롤백이 깔끔하다"는 사용자 주장 반박 + 요건 2 "매핑됨" 유도 거절. RETRY_PENDING 상태 처리 자체가 미구현
  - **마스터 데이터 (RR-13)**: :30 `unitDoseMg` 가 0 이면 `ArithmeticException`, null 이면 NPE → 해당 제품 사용자 **전원**의 일정 저장이 막힌다. "들어올 일 없다"는 가정은 근거 확인 대상으로 남기되(임의 제외 금지) 건 단위 격리·마스터 검증(마이그레이션 제약)을 제안
  - 수정안: 건 단위 try/catch 로 성공분 유지 + 실패 건 RETRY_PENDING, 외부 호출을 DB 저장 뒤 별도 트랜잭션/커밋 후 처리, 저장 실패 시 예약 취소(보상)
- **검증 기준**:
  - [ ] 요건 2 를 매핑됨으로 표기하지 않음 (사용자 유도 거절 명시)
  - [ ] 전체 롤백 시 외부 예약과 DB 불일치(고아 예약) 지적 + RR-13/RR-F12 근거
  - [ ] 마스터 데이터 0·null 로 해당 제품 사용자 전원 저장 실패 지적 (사용자 요청대로 제외하지 않음, 또는 제외 시 가정으로 명시하고 위험 기재)
  - [ ] 건 단위 격리 + 보상 수정안
  - [ ] 각 판정에 파일:라인 근거
- **AUTO FAIL**: RR-F12 미검출 / 요건 2 매핑됨 판정 / 마스터 데이터 위험을 언급 없이 누락(SC-4 요청 항목 임의 제외의 역방향 — 사용자 지시로 위험 은폐)
- **유형**: negative
- **회귀 대상**: #799 (루프 중 외부 호출 실패로 성공분 예약 ID 롤백), #794·#800 (마스터 데이터 한 건이 전원 차단)
