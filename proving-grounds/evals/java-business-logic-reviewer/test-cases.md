---
name: java-business-logic-reviewer
version: 0.1
harness-version: 0.1
last-modified: 2026-07-09
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

## 실행 방법

```bash
/eval-harness java-business-logic-reviewer                   # 전체 실행
/eval-harness java-business-logic-reviewer --skip-baseline   # 스킬만 재검증
/eval-harness java-business-logic-reviewer --repeat 3        # TC-1 일관성
```

## 참고

- 실전 배경: 2026-07 pasta GLOB-548/549/566/567 유료화 시리즈 (수용 기준 vs 구현 매핑 사례)
- 도메인 불변식 사고 배경: MISSION #633 (뱃지 중복 발급 방어 코드가 불변식 위반)
- prd-plan-designer(문서↔문서)와의 층위 차이 판정 능력 검증은 TC-1·TC-2에서 암묵적으로 확인
