---
name: java-business-logic-reviewer
description: "백엔드 Java Spring Boot 비즈니스 로직·요건 준수 리뷰 전용 스킬 — PRD 수용 기준·TDD 설계 vs 실제 구현 코드 정합성 검증. 도메인 불변식·엣지 케이스 사각지대 검출. 요건 리뷰 요청 시 자동 트리거, java-composite-reviewer 안에서 5번째 관점으로 조합. Use proactively when reviewing PRD acceptance criteria, TDD alignment to code, domain invariants, or missing edge-case handling."
version: "0.1"
last-modified: "2026-07-09"
changelog: "v0.1 — 2026-07-09 리뷰 스킬 세분화 4번째 관점으로 신설. 사용자 초기 제안(2026-07-09 오후)에서 유예됐던 비즈니스 로직 관점 채택. prd-plan-designer(문서↔문서 정합)와 층위 분리 — 이 스킬은 문서↔코드 정합. 5분류 판정(매핑됨·부분 매핑·미구현·사각지대·불변식 위반)."
harness-status: pending
---

# java-business-logic-reviewer — 비즈니스 로직·요건 준수 관점 코드 리뷰 스킬

> 백엔드 Java Spring Boot 코드의 **비즈니스 로직·요건 준수 리뷰 전용**. PRD 수용 기준·TDD 설계와 실제 구현 코드의 정합성을 검증하고, 도메인 불변식 위반·엣지 케이스 사각지대를 검출한다.

---

## 트리거 조건

- 사용자가 "요건 검토", "PRD 대비 구현 확인", "TDD 설계 반영 여부", "누락된 케이스", "도메인 규칙 준수", "수용 기준 리뷰" 등을 언급
- PR 리뷰 요청에 "비즈니스 로직" 태그 명시
- java-composite-reviewer 에이전트가 비즈니스 로직 관점을 요청 (5번째 관점)

---

## 스코프

### In-Scope

| 축 | 커버 |
|----|------|
| PRD 수용 기준 vs 구현 | PRD의 각 수용 기준이 실제 코드(Controller·Service·Domain)에 반영됐는지 매핑 |
| TDD 설계 vs 구현 | TDD가 명시한 계층·API 시그니처·엔티티 필드가 실제 구현과 일치하는지 |
| 엣지 케이스 사각지대 | 요건에 명시된 예외 경로(null·경계값·동시성·롤백·타임아웃) 처리 누락 |
| 도메인 불변식 준수 | "결제 완료 후 취소 불가"·"미성년 특정 API 접근 불가" 등 정책성 규칙 코드 반영 |
| 비즈니스 예외 경로 | 요건 명시 실패·에러 케이스가 사용자에게 명확히 노출되는지 (메시지·HTTP status) |

### Out-of-Scope (다른 리뷰어 담당)

| 관점 | 담당 |
|------|------|
| 보안 (SQL Injection·PII·시크릿·OWASP) | java-secure-coding-reviewer |
| 성능 (N+1·캐시·트랜잭션·리소스) | java-performance-reviewer |
| 4-Tier 계층·Bean·모듈 관계·컨벤션 | java-architecture-reviewer |
| Hibernate Session·@Profile·FQCN·임시 로그 | self-code-reviewer |
| Locale.ROOT·i18n 4파일 동기화 | self + tolgee |

### prd-plan-designer와의 층위 차이 (중요)

두 컴포넌트가 이름·역할이 유사해 혼동 위험. 아래 표로 분리:

| 대상 | 층위 | 검증 방향 | 산출물 |
|------|------|----------|--------|
| prd-plan-designer v1.0 | PRD ↔ TDD | **문서 간 정합성** | 매핑 표 + 재호출 안내 |
| **java-business-logic-reviewer 0.1** | **PRD/TDD ↔ 실제 구현 코드** | **문서 → 코드** | 요건별 코드 매칭 표 + 사각지대 지적 |
| self-code-reviewer v2.0 | 코드 공통 룰 | **문서 무관, 코드 자체** | 공통 리뷰 리포트 |

**판단 기준**:
- PRD와 TDD가 서로 안 맞으면 → prd-plan-designer 호출
- PRD/TDD가 정합인데 코드가 그걸 지키는지 궁금하면 → **이 스킬**
- 코드 자체에 공통 결함(FQCN·@Profile 등)이 있는지 → self-code-reviewer

---

## 하드 가드레일 (AUTO FAIL)

| # | 카테고리 | 검출 | 등급 |
|---|---------|------|------|
| BIZ-HG-1 | 문서 없이 진행 | PRD·TDD 파일 위치 확인 없이 리뷰 시작 (Phase 0 skip) | **AUTO FAIL** |
| BIZ-HG-2 | 임의 요건 해석·확장 | 문서 문구가 모호할 때 사용자 확인 없이 스킬이 임의 해석 | **AUTO FAIL** |
| BIZ-HG-3 | 근거 없는 "매핑됨" 판정 | 매핑됨 표기에 파일:라인 근거가 없음 (prd-plan-designer 원칙 계승) | **AUTO FAIL** |
| BIZ-HG-4 | 불변식 위반 최우선 보고 누락 | 도메인 불변식 위반 발견 시 리포트 최상단 배치 필수 (숨기면 실사고 유발) | **AUTO FAIL** |
| BIZ-HG-5 | 코드 자의적 수정 시도 | 이 스킬은 읽기 전용. Edit/Write 도구로 코드 변경 시도 | **AUTO FAIL** |

---

## Phase 0. 문서 확보

리뷰 시작 전 PRD·TDD 위치 반드시 확인.

```
1. 대상 브랜치/PR의 관련 문서 위치 파악:
   - PRD: docs/prd/{feature}.md, 또는 Jira 이슈 링크
   - TDD: docs/tdd/{feature}.md, 또는 Confluence 링크
2. 없으면 → 사용자에게 명시적 요청:
   "이 리뷰는 PRD·TDD 문서가 필요합니다. 문서 위치를 알려주시거나,
    문서 없이 진행할지(공통 리뷰만) 확인 부탁드립니다."
3. 문서 없이 강행 요구 → BIZ-HG-1 AUTO FAIL
```

**예외**: 사용자가 "PRD·TDD 없이도 도메인 불변식만 검토해줘" 명시하면 skip 가능하되, 리포트 첫 줄에 "문서 없이 진행 — 요건 매핑은 스코프 밖" 명시.

---

## Phase 1. 요건 항목 추출

### 1.1 PRD 수용 기준 → 체크리스트

- PRD의 "수용 기준" / "Acceptance Criteria" / "완료 조건" 섹션 파싱
- 각 기준을 1문장 단위로 추출:
  - "사용자는 결제 완료 후 30일 이내 취소 가능하다" → 항목 1
  - "결제 실패 시 사용자에게 실패 사유 노출" → 항목 2
- 항목 번호와 원문 인용을 표로 정리

### 1.2 TDD 설계 → 시그니처 추출

- 계층별 지정 (Web/Application/Domain/Infrastructure)
- API 엔드포인트: HTTP 메서드·경로·요청/응답 DTO
- Domain 엔티티: 필드·불변식·상태 전이
- 예외 클래스 및 HTTP status 매핑

### 1.3 도메인 불변식 명시적 추출

TDD·PRD 본문에 흩어진 "반드시 ~해야 한다"·"절대 ~해선 안 된다" 문장을 별도 리스트로 격리.

```
예시:
- 결제가 SUCCESS 상태로 진입 후엔 다시 PENDING/FAILED로 되돌릴 수 없다
- 미성년자(만 14세 미만)는 특정 API(/api/adult/**)에 접근할 수 없다
- 뱃지 발급은 유저당 종류별 1회만 허용된다 (unique constraint)
```

---

## Phase 2. 코드 매칭

각 요건 항목을 실제 코드 위치(파일:라인)로 매핑.

```
매칭 절차:
1. 요건 항목의 키워드로 grep (예: "결제 취소" → "cancelPayment", "PaymentCancel")
2. Controller → Service → Domain 순서로 계층 추적
3. 각 매칭 지점을 파일:라인으로 기록
4. 근거 없이 "매핑됨" 판정 금지 (BIZ-HG-3)
```

**추적 예시**:
```
요건 1: "사용자는 결제 완료 후 30일 이내 취소 가능"
→ PaymentController.java:45 (cancelPayment 엔드포인트)
→ PaymentCancelService.java:23 (30일 검증 로직 확인 필요)
→ Payment.java:78 (isCancellable() 도메인 메서드)
```

---

## Phase 3. 정합성 판정 (5분류)

각 요건 항목에 다음 상태를 부여:

| 상태 | 아이콘 | 정의 |
|------|--------|------|
| 매핑됨 | ✅ | 요건이 정확히 코드에 반영. 파일:라인 근거 존재 |
| 부분 매핑 | ⚠️ | 요건 일부만 반영 (예: 정상 경로만, 예외 경로 없음) |
| 미구현 | 🔴 | 요건 있지만 관련 코드 위치를 grep으로 찾을 수 없음 |
| 사각지대 | 🟡 | 요건에 명시된 예외 경로(null·경계값·동시성·롤백) 처리 누락 |
| 불변식 위반 | 🟠 | 도메인 규칙 위배 (Phase 1.3 리스트에 대조) — **최우선 보고** |

### 판정 우선순위

1. **불변식 위반**을 리포트 최상단에 배치 (BIZ-HG-4)
2. 미구현 → 부분 매핑 → 사각지대 순으로 경고 수위 감소
3. 매핑됨은 마지막에 요약 통계로

---

## Phase 4. 리포트 형식

self-code-reviewer 리포트 형식과 통일. 유형 코드는 BIZ-*, 등급은 6단계.

### 리포트 구조

```markdown
# 비즈니스 로직 리뷰 리포트

## 🟠 불변식 위반 (최우선)
- [BIZ-INVARIANT] `Payment.java:78` — 결제 SUCCESS 상태 되돌림 허용
  - 요건: "SUCCESS → PENDING 전이 금지"
  - 등급: **AUTO FAIL / Critical**

## 🔴 미구현
- [BIZ-MISSING] 요건 3 "결제 실패 시 사용자에게 실패 사유 노출"
  - 예상 위치: `PaymentController.java` 예외 핸들러
  - grep 결과: 실패 사유 메시지가 로그로만 남고 응답 DTO에 없음
  - 등급: High

## 🟡 사각지대
- [BIZ-EDGE] `PaymentCancelService.java:23`
  - 요건: "null 입력 시 400 반환"
  - 실제: null 체크 없이 NPE 발생
  - 등급: Medium

## ⚠️ 부분 매핑
- [BIZ-PARTIAL] 요건 2 "결제 실패 사유 사용자 노출"
  - 정상 경로는 매핑됨(`Controller.java:120`)
  - 시스템 오류 경로는 사용자 메시지 없음
  - 등급: Medium

## ✅ 매핑됨 (요약)
- 5건 통과 (요건 1·4·5·7·8)

## 📊 통계
- 총 요건 8건: 매핑됨 5 / 부분 1 / 미구현 1 / 사각지대 1 / 불변식 위반 1
```

### 유형 코드

- `BIZ-MISSING` — 미구현
- `BIZ-PARTIAL` — 부분 매핑
- `BIZ-EDGE` — 엣지 케이스 사각지대
- `BIZ-INVARIANT` — 불변식 위반 (최우선)

### 등급

`AUTO FAIL` / `Critical` / `High` / `Medium` / `Low` / `Info`

---

## 자기 검증 (10항목)

리뷰 완료 전 스스로 확인:

1. Phase 0에서 PRD·TDD 파일 위치 명시적으로 확인했는가? (BIZ-HG-1)
2. Phase 1에서 PRD 수용 기준을 항목 번호와 원문 인용으로 정리했는가?
3. Phase 1.3에서 도메인 불변식을 별도 리스트로 격리했는가?
4. Phase 2에서 각 매핑 판정에 파일:라인 근거가 있는가? (BIZ-HG-3)
5. Phase 3에서 5분류 판정 아이콘(✅⚠️🔴🟡🟠)이 명확한가?
6. 불변식 위반이 리포트 최상단에 배치됐는가? (BIZ-HG-4)
7. 요건 문구가 모호했다면 사용자 확인 없이 임의 해석하지 않았는가? (BIZ-HG-2)
8. 스코프 밖 항목(보안·성능·아키텍처·공통)은 각 리뷰어에 위임 안내했는가?
9. 코드 자의적 수정 시도 없이 리포트만 산출했는가? (BIZ-HG-5)
10. 리포트에 통계 요약(총 요건 대비 각 상태 개수)이 포함됐는가?

---

## 참조 인덱스

- **문서 간 정합성 (문서↔문서)**: `agents/prd-plan-designer/prd-plan-designer.md` v1.0
- **공통 리뷰 (문서 무관)**: `skills/self-code-reviewer/SKILL.md` v2.0
- **보안 리뷰**: `skills/java-secure-coding-reviewer/SKILL.md` v0.1
- **성능 리뷰**: `skills/java-performance-reviewer/SKILL.md` v0.1
- **아키텍처 리뷰**: `skills/java-architecture-reviewer/SKILL.md` v0.1
- **복합 리뷰어 (오케스트레이터)**: `agents/java-composite-reviewer/java-composite-reviewer.md` v0.1 — **다음 사이클에 5개 관점으로 확장 필요** (현재 4개만)
- **요건 문서 작성 스킬**: `skills/prd-designer/SKILL.md` v1.2 / `skills/tdd-designer/SKILL.md` v1.4

---

## 하네스 (테스트 대기)

- 평가 루브릭: `references/evaluation-rubric.md`
- 하네스 정의: `proving-grounds/harnesses/java-business-logic-reviewer.harness.md`
- 테스트 케이스: `proving-grounds/evals/java-business-logic-reviewer/test-cases.md` (Happy 2 + Edge 1 + Negative 2)
- 상태: **테스트 대기** (`/eval-harness java-business-logic-reviewer` 미실행)
