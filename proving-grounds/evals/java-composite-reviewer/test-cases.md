---
name: java-composite-reviewer
version: 0.2
harness-version: 0.2
last-modified: 2026-07-29
---

# java-composite-reviewer 테스트 케이스 (v0.2)

총 8개 (Happy 3 + Edge 2 + Negative 3). 각 TC의 시뮬레이션은 위임 스킬의 mock 리포트 5종(self + 보안·성능·아키·비즈니스 로직)을 사전에 준비해 반환한다.

---

## TC-1: Happy Path — 큰 PR 전체 5관점 병렬 리뷰

- **입력 프롬프트**: "이 브랜치 전체를 복합 리뷰해줘. api/feat/pricing-cache 브랜치, PR #642. PRD/TDD 문서는 docs/prd/pricing-cache.md / docs/tdd/pricing-cache.md."
- **시뮬레이션 컨텍스트**:
  - `git diff dev --stat`: 8 파일 342 라인 (Controller 1 / Service 3 / Repository 2 / Config 1 / Test 1)
  - PR #642 본문 있음 (5줄, "GLOB-566 캐시 신설")
  - **PRD/TDD 문서 확보** → business-logic 활성화
  - 사용자 관점 지정 없음
- **기대 결과**:
  - Phase 0 결과 보고 (6항목 완결, PRD/TDD 유무 포함) → Phase 1 → Phase 2 → Phase 3 → Phase 4 순 진행
  - 관점 미지정 + PRD/TDD 존재 → **5개 스킬 전체 병렬 호출** (self + secure + perf + arch + business-logic)
  - Task tool 1 메시지에 5개 Task 동시 발행 (직렬 호출 0)
  - business-logic Task 프롬프트에 **PRD/TDD 경로 포함**
  - 위임 프롬프트에 압축 컨텍스트만 전달 (파일 목록 + 요약 + PR 본문 20줄 이내)
  - 각 스킬 mock 리포트 5종 수집 → 통합 리포트 생성
    - 상단 AUTO FAIL 우선순위 표 (mock 리포트 기준 4건: 보안 1 / 비즈니스 불변식🟠 1 / 성능 1 / 아키 1)
    - 하단 5개 관점 원본 리포트 그대로 첨부
  - Phase 4 최종 보고: `y=coding-implementer 위임 / n=종료 / 상세=원본` 3분기 명시
- **검증 기준**:
  - [ ] Phase 0 6항목 모두 확인 (브랜치/파일/규모/PR/**PRD·TDD**/지시)
  - [ ] 5개 스킬 병렬 호출 (Task tool 1 메시지 5 Task)
  - [ ] business-logic Task에 PRD/TDD 경로 전달
  - [ ] AUTO FAIL 우선순위 표: **보안 > 비즈니스 불변식🟠 > 성능 > 아키** 순서
  - [ ] 원본 리포트 5종 하단 첨부 (자의적 재해석 0)
  - [ ] Phase 4 3분기 사용자 확인 명시
- **유형**: happy-path

---

## TC-2: Happy Path — 사용자 관점 지정 "보안만"

- **입력 프롬프트**: "이 PR을 **보안 관점만** 리뷰해줘. api/feat/payment-integration, 3 파일."
- **시뮬레이션 컨텍스트**:
  - 3 파일 (Controller 1 / Service 1 / application-dev.yml 1)
  - 사용자 지시: "보안만"
- **기대 결과**:
  - Phase 0 결과 보고 → 사용자 지시 "보안만" 파싱 확인
  - Phase 1: `java-secure-coding-reviewer` + `self-code-reviewer`(공통 룰 항상 포함) **2개 스킬**만 호출
  - `java-performance-reviewer`, `java-architecture-reviewer` **skip 명시** (사용자 지정 사유)
  - Task tool 1 메시지 2 Task 병렬
  - 통합 리포트: 보안 관점 + 공통 룰만. "성능·아키텍처 리뷰는 사용자 요청으로 skip됨" 명시
- **검증 기준**:
  - [ ] 사용자 관점 지정 정확 파싱
  - [ ] self-code-reviewer는 관점 지정 무관 항상 포함 (하드 가드레일 위반 방지)
  - [ ] 성능·아키텍처 스킬은 호출 대상에서 제외 (사유 명시)
  - [ ] Task tool 2개 병렬 호출
- **유형**: happy-path

---

## TC-3: Edge — 관점 판단 애매 케이스 (PRD/TDD 있음)

- **입력 프롬프트**: "PricingRuleRepository.java 하나만 변경했어. 리뷰 부탁. PRD·TDD는 docs/ 아래에 있음."
- **시뮬레이션 컨텍스트**:
  - 1 파일 (Repository 1개, 30 라인 변경)
  - PRD/TDD 문서 존재 → business-logic 활성화 대상
  - 사용자 관점 지정 없음
- **기대 결과**:
  - Phase 0 확인 후 관점 미지정 + PRD/TDD 존재 → **5개 전체 병렬 호출** (임의 스킬 skip 금지 — 하드 가드레일 #4)
  - 관점 자동 판단 매트릭스 표에서 Repository → 성능 > 아키텍처 > 공통 **우선순위 힌트** 제시 (사용자 참고용)
  - 힌트는 **스킬 skip 근거 아님**. 여전히 5개 병렬
  - 통합 리포트에 우선순위 힌트 표시: "이 변경은 성능/아키텍처 관점이 우세할 것으로 예상. business-logic은 저강도 예상"
- **검증 기준**:
  - [ ] 관점 미지정 시 5개 전체 병렬 (판단 힌트로 스킬 skip 안 함)
  - [ ] 관점 자동 판단 매트릭스 힌트를 사용자에게 참고용으로 제공
  - [ ] Repository → 성능/아키텍처 우세 힌트 정확
- **유형**: edge-case

---

## TC-4: Negative — 5관점 AUTO FAIL 우선순위 통합

- **입력 프롬프트**: "SecurityConfig + PricingCacheConfig + PricingPolicy 리뷰해줘. PRD/TDD는 docs/에 있음."
- **시뮬레이션 컨텍스트**: mock 리포트 5종 중
  - self: AUTO FAIL 1건 (`@Profile("dev && !test")` 문법)
  - secure: AUTO FAIL 2건 (PII 로그 노출, 하드코딩 시크릿)
  - perf: AUTO FAIL 1건 (WebClient timeout 미설정)
  - arch: AUTO FAIL 1건 (Bean Qualifier cross-module 위반)
  - **business-logic**: 🟠 BIZ-INVARIANT 1건 (PricingPolicy.java:42 "결제 완료 후 취소 불가" 위반)
  - **총 6건 AUTO FAIL**, 파일:라인 중 1건 중복 (SecurityConfig.java:178 — secure PII + arch 4-Tier 지적 병합 대상)
- **기대 결과**:
  - AUTO FAIL 우선순위 표 상단 배치:
    1. [보안] SecurityConfig.java:45 — 하드코딩 시크릿 (SEC-HG-2)
    2. [보안] SecurityConfig.java:178 — PII 로그 노출 (SEC-HG-3) **+ [아키] 4-Tier 위반 (ARCH-HG-2)** 병합 각주
    3. **[비즈니스 불변식 🟠] PricingPolicy.java:42 — "결제 완료 후 취소 불가" 위반 (BIZ-INVARIANT)**
    4. [성능] PricingCacheConfig.java:82 — WebClient timeout 미설정 (G-3)
    5. [아키] PricingCacheConfig.java:120 — Bean Qualifier cross-module (ARCH-HG-1)
    6. [공통] PricingCacheConfig.java:14 — `@Profile("dev && !test")` 문법
  - 순서: **보안 > 비즈니스 불변식🟠 > 성능 > 아키 > 공통** (v0.2 우선순위 정확)
  - 병합된 항목(178번)에는 두 관점을 각주로 명시
  - 원본 리포트 5종 하단 첨부
- **검증 기준**:
  - [ ] AUTO FAIL 우선순위 표: **보안 > 비즈니스🟠 > 성능 > 아키 > 공통** 순
  - [ ] 파일:라인 중복 발견(178번)을 병합하고 각주로 관점 명시
  - [ ] 총 6건 모두 우선순위 표에 나타남 (병합해도 개수 감소 없음)
  - [ ] BIZ-INVARIANT가 성능·아키 위(2순위)에 배치
  - [ ] 5개 원본 리포트 하단 그대로 첨부
- **유형**: negative

---

## TC-5: Negative — 사용자가 특정 관점 skip 요구

- **입력 프롬프트**: "이 PR 리뷰해줘. 근데 **성능 관점은 스킵**해줘, 어차피 트래픽 낮은 배치라."
- **시뮬레이션 컨텍스트**:
  - 4 파일 (Batch 관련)
  - 사용자 지시: "성능은 skip"
- **기대 결과**:
  - 에이전트는 사용자 지시를 파싱하되, **관점 skip 요구를 그대로 수용하지 않음**
  - **하드 가드레일 #4** 근거로 **거절 + 대안 제시**:
    - "성능 관점을 완전히 skip하면 배치 트랜잭션·리소스 누수 등 사각지대. 성능 관점은 정보성으로만 유지하고, 나머지 4개(secure/arch/business-logic/self) 관점을 우선순위로 처리하는 방식을 권장합니다"
  - 또는 사용자 재확인 요청: "성능 관점 완전 skip을 확정하시겠습니까? (y=skip / n=포함)"
  - **자동 skip 진행 금지** (하드 가드레일 #4)
- **검증 기준**:
  - [ ] 사용자 skip 요구를 파싱했으나 자동 수용 안 함
  - [ ] 하드 가드레일 #4 근거 명시 + 대안 제시 (또는 사용자 재확인)
  - [ ] 재확인 없이 임의 스킬 skip 시 AUTO FAIL
- **유형**: negative

---

## TC-6: Happy Path — `--scope=business-logic` 지정 (v0.2 신규)

- **입력 프롬프트**: "이 PR을 **비즈니스 로직 관점만** 검토해줘. docs/prd/checkout.md + docs/tdd/checkout.md 기준으로."
- **시뮬레이션 컨텍스트**:
  - 3 파일 (CheckoutService 1 / CheckoutController 1 / OrderPolicy 1)
  - PRD/TDD 문서 존재 → business-logic 활성화 가능
  - 사용자 지시: `--scope=business-logic`
- **기대 결과**:
  - Phase 0 결과 보고 → 사용자 지시 파싱 확인
  - Phase 1: `java-business-logic-reviewer` + `self-code-reviewer`(항상 포함) **2개 스킬**만 호출
  - `secure`, `perf`, `arch` **skip 명시** (사용자 지정 사유)
  - business-logic Task 프롬프트에 PRD·TDD 문서 경로 전달
  - Task tool 1 메시지 2 Task 병렬
  - 통합 리포트: business-logic 5분류 판정 + 공통 룰. "보안·성능·아키텍처 리뷰는 사용자 요청으로 skip됨" 명시
- **검증 기준**:
  - [ ] 사용자 관점 지정 정확 파싱 (`--scope=business-logic`)
  - [ ] self-code-reviewer 항상 포함 (하드 가드레일 위반 방지)
  - [ ] business-logic Task에 PRD/TDD 경로 압축 컨텍스트 포함
  - [ ] 나머지 3개 스킬은 호출 대상에서 제외 (사유 명시)
  - [ ] Task tool 2개 병렬 호출
- **유형**: happy-path

---

## TC-7: Edge — PRD/TDD 문서 부재 시 business-logic 자동 skip (v0.2 신규)

- **입력 프롬프트**: "이 브랜치 전체 리뷰해줘. api/fix/hotfix-lilly-scps."
- **시뮬레이션 컨텍스트**:
  - 2 파일 (hotfix scope, IP·키값 수정)
  - **PRD/TDD 문서 부재** (hotfix라 문서 스킵 상태)
  - 사용자 관점 지정 없음
- **기대 결과**:
  - Phase 0 6항목 확인 → PRD/TDD 부재 감지
  - Phase 1: 관점 미지정 + business-logic 조건 미충족 → **4개 스킬 호출 (self + secure + perf + arch)**
  - `java-business-logic-reviewer` **자동 skip + 사유 명시**:
    - "business-logic은 BIZ-HG-1(문서 없이 진행 금지)에 따라 자동 skip됨. PRD/TDD가 필요하면 사용자가 지시해주세요"
  - Task tool 1 메시지 4 Task 병렬
  - 통합 리포트에 skip 사유 명시
- **검증 기준**:
  - [ ] PRD/TDD 부재를 Phase 0에서 감지
  - [ ] business-logic 자동 skip + 사유 명시 (BIZ-HG-1 인용)
  - [ ] 나머지 4개 스킬은 정상 병렬 호출
  - [ ] 통합 리포트에 "business-logic skip: PRD/TDD 부재" 명시
- **유형**: edge-case

---

## TC-8: Negative — 보안 + 비즈니스 불변식 우선순위 판정 (v0.2 신규)

- **입력 프롬프트**: "결제 API 3파일 복합 리뷰. PRD/TDD 있음."
- **시뮬레이션 컨텍스트**: mock 리포트 5종 중
  - self: WARN 2건
  - secure: AUTO FAIL 1건 (PaymentController.java:52 — SQL Injection 가능성 SEC-HG-1)
  - perf: AUTO FAIL 1건 (PaymentRepository.java:20 — N+1 페치)
  - arch: WARN 3건
  - **business-logic**: 🟠 BIZ-INVARIANT 2건
    - PaymentPolicy.java:33 — PRD "환불은 결제 완료 24시간 이내만" 위반 (코드는 무제한 허용)
    - PaymentPolicy.java:71 — PRD "미성년자 결제 금지" 미구현 (BIZ-INVARIANT)
- **기대 결과**:
  - AUTO FAIL 우선순위 표:
    1. [보안] PaymentController.java:52 — SQL Injection (SEC-HG-1)
    2. **[비즈니스 불변식 🟠] PaymentPolicy.java:33 — 환불 24시간 제한 위반 (BIZ-INVARIANT)**
    3. **[비즈니스 불변식 🟠] PaymentPolicy.java:71 — 미성년자 결제 금지 미구현 (BIZ-INVARIANT)**
    4. [성능] PaymentRepository.java:20 — N+1 페치 (G-1)
  - **비즈니스 불변식 2건이 성능 위**에 배치 — 실사고 위험 반영
  - business-logic 원본 리포트에 5분류 판정 상세: 🟠 2건 + 🔴 0건 + 🟡 0건 + ⚠️ 0건 + ✅ 나머지
  - 원본 리포트 5종 하단 첨부
- **검증 기준**:
  - [ ] 보안 AUTO FAIL이 1순위
  - [ ] **BIZ-INVARIANT 2건이 2·3순위 (성능·아키 위)**
  - [ ] business-logic 리포트에 5분류 판정 상세 표시
  - [ ] 우선순위 위반 (성능이 BIZ-INVARIANT 위) 시 AUTO FAIL
  - [ ] 원본 리포트 5종 하단 그대로 첨부
- **유형**: negative

---

## 실행 요약 (v0.2, 8 TC)

| TC | 유형 | 통과 조건 |
|----|------|---------|
| TC-1 | happy-path | 5개 병렬 + Phase 0~4 완결 + 5단계 우선순위 통합 |
| TC-2 | happy-path | 관점 지정 파싱 + self 항상 포함 + 2개 병렬 |
| TC-3 | edge-case | 매트릭스 힌트는 참고, 스킬 skip 안 함 (5개 병렬) |
| TC-4 | negative | 5단계 우선순위 순서 정확 + BIZ-INVARIANT 2순위 + 중복 발견 병합 각주 |
| TC-5 | negative | 사용자 skip 요구 거절/재확인 + 하드 가드레일 근거 |
| TC-6 | happy-path | `--scope=business-logic` 파싱 + PRD/TDD 경로 전달 + 2개 병렬 |
| TC-7 | edge-case | PRD/TDD 부재 시 business-logic 자동 skip + 사유 명시 |
| TC-8 | negative | BIZ-INVARIANT 우선순위 (성능·아키 위, 보안 아래) |

**Happy Path 3/3 통과 + Edge 2/2 판단력 + Negative 3/3 가드레일 방어** → 실전 배치 가능.
