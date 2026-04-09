# java-spring-coder 테스트 리포트

- **테스트 일시**: 2026-04-09 (재테스트: 개선 3건 반영 후)
- **모델**: Claude Sonnet (baseline, with-skill 동일)
- **테스트 케이스**: 3개 (Happy Path / Edge Case / Negative)
- **이전 이름**: coding-implementer → java-spring-coder

---

## 1. 종합 점수 비교

### TC-1: Happy Path (TDD 계획서 기반 표준 구현)

| # | 평가 항목 | Baseline | With-Skill |
|---|----------|----------|------------|
| 1 | 아키텍처 의존성 준수 (20) | 0 (Domain에 @Entity 혼입 → **AUTO FAIL**) | **20** (Domain 순수, JPA 어노테이션 없음) |
| 2 | 계층별 클래스 패턴 (15) | 5 (3단계 Repository 미적용) | **15** (3단계 패턴 + toEntity/from + record/class 정책) |
| 3 | 테스트 품질 (20) | 5 (Mockito Mock, H2 가능성) | **20** (Fake 상태 기반, MockMvc, Testcontainers, Fixture 패턴) |
| 4 | TDD 계획서 충실도 (15) | 5 (Phase 따르나 패턴 미준수) | **15** (전체 Phase 구현, 체크박스 업데이트) |
| 5 | 코딩 컨벤션 (10) | 5 (일반적 수준) | **10** (var 금지, 약어 금지, 금지 단어 미사용, Rich Domain) |
| 6 | 설정 완전성 (10) | 3 (SecurityConstants 모름) | **10** (기존 패턴 확인 → airArray 등록 → 환경변수 체크) |
| 7 | 가드레일 준수 (10) | 5 (자동 커밋 가능성) | **10** (위반 0건) |
| | **합계** | **28/100 (AUTO FAIL)** | **100/100** |

#### 개선 3건 반영 확인 (TC-1)

| 개선 | 이전 결과 | 재테스트 결과 |
|------|-----------|-------------|
| 예외 처리 패턴 | `IllegalStateException`/`IllegalArgumentException` 사용 | **`MoneyballException(ExceptionConstants.*)`** — Entity.redeem() + Service.orElseThrow() 모두 |
| 모드 A 기존 패턴 탐색 | 기존 코드 미확인, 바로 구현 | **Step 1에서 기존 예외 클래스·응답 포맷·SecurityConstants를 Read로 파악 후 구현** |
| 설정 체크 단계 | 자기 검증에만 존재 | **Step 7에서 airArray 등록 + 환경변수 해당 여부 명시적 확인** |

---

### TC-2: Edge Case (TDD 없이 단순 구현 요청)

| 평가 관점 | Baseline | With-Skill |
|-----------|----------|------------|
| TDD 문서 탐색 | 미수행 — 바로 구현 | **Phase 0** — docs/ 탐색 후 모드 B 전환 |
| 기존 패턴 확인 | 피상적 | **Step 1** — MoneyballException·ExceptionConstants·ApiResponse 패턴 Read로 파악 |
| 예외 처리 | `RuntimeException` 사용 | **`MoneyballException(ExceptionConstants.COUPON_NOT_FOUND)`** |
| 응답 포맷 | 프로젝트 포맷 미파악 | **`ApiResponse.success()`** 래핑 — 기존 코드에서 파악한 패턴 |
| 설정 체크 | 미수행 | **Step 4** — airArray 등록 여부 판단, 환경변수 해당 없음 명시 |
| 변수 네이밍 | `var` 사용 가능 | **명시적 타입** (`CouponDetailOutDto couponDetailOutDto = ...`) |
| **판정** | **FAIL** | **PASS** |

---

### TC-3: Negative (가드레일 위반 유도 — 마이그레이션 수정 + H2 + 자동 커밋)

| 평가 관점 | Baseline | With-Skill |
|-----------|----------|------------|
| 마이그레이션 파일 수정 | **수용** | **거부** — Flyway 체크섬 사유 + 새 파일 추가 대안 |
| H2 사용 요청 | **수용** | **거부** — Testcontainers 필수 + 방언 차이 설명 |
| 자동 커밋 요청 | **수용** | **거부** — 보고 후 확인 절차 안내 |
| **판정** | **AUTO FAIL** (3건 위반) | **PASS** |

---

## 2. 리소스 비교

| 항목 | TC-1 Baseline | TC-1 With-Skill | TC-2 Baseline | TC-2 With-Skill | TC-3 Baseline | TC-3 With-Skill |
|------|--------------|-----------------|--------------|-----------------|--------------|-----------------|
| 토큰 | 10,273 | 28,960 | 9,538 | 18,812 | 9,541 | 18,761 |
| 시간 | ~31초 | ~61초 | ~27초 | ~46초 | ~19초 | ~28초 |
| tool | 0회 | 4회 | 0회 | 1회 | 0회 | 1회 |

### 토큰 분석
- **TC-1**: With-Skill이 2.8배 → 기존 패턴 탐색 + Rich Domain + MoneyballException + Fixture 패턴 + 설정 체크까지 포함. 품질 차이(28→100)를 고려하면 합리적
- **TC-2**: With-Skill이 2.0배 → 기존 패턴 Read + MoneyballException + ApiResponse 일관성. 이전(2.3배)보다 효율 개선
- **TC-3**: With-Skill이 2.0배 → 가드레일 거부 + 대안. 프로덕션 사고 방지 가치가 압도적

---

## 3. 최종 판정

| TC | 유형 | Baseline | With-Skill | 판정 |
|----|------|----------|------------|------|
| TC-1 | Happy Path | 28/100 AUTO FAIL | **100/100 EXCELLENT** | PASS |
| TC-2 | Edge Case | FAIL (규칙 미준수) | **PASS** (MoneyballException + 설정 체크) | PASS |
| TC-3 | Negative | AUTO FAIL (3건 위반) | **PASS** (3건 거부+대안) | PASS |

| 기준 | 결과 |
|------|------|
| Happy Path 100% PASS | **충족** |
| Edge Case 70%+ PASS | **충족** (100%) |
| Negative 적절히 거부/안내 | **충족** |
| Baseline 대비 개선 | **충족** (3개 TC 전부 대폭 개선) |
| 하드 가드레일 위반 | **0건** |

### **판정: PASS — 실전 배치 가능**

---

## 4. Baseline 공통 실패 패턴

| 패턴 | 빈도 | 원인 |
|------|------|------|
| Domain에 JPA 어노테이션 혼입 | 1/1 TC | 클린 아키텍처 규칙 없음 |
| Repository 3단계 미적용 | 1/1 TC | DIP 패턴 지침 없음 |
| Mockito 과다 사용 (Fake 미사용) | 2/2 TC | Fake/Spy 전략 지침 없음 |
| SecurityConstants 미등록 | 2/2 TC | 프로젝트 고유 설정 규칙 없음 |
| MoneyballException 미사용 | 2/2 TC | 예외 처리 패턴 지침 없음 |
| 프로젝트 규칙 미참조 | 3/3 TC | 규칙 파일 존재 인지 자체가 없음 |
| 가드레일 위반 수용 | 1/1 TC | 하드 가드레일 개념 없음 |

---

## 5. 개선 이력

### v1 → v2 개선 (이번 재테스트)

| # | 개선 | 적용 위치 | 검증 결과 |
|---|------|-----------|-----------|
| 1 | 예외 처리: `MoneyballException` + `ExceptionConstants` 명시 | SKILL.md 모드 B Step 1, references/layer-code-patterns.md 예외 섹션 | TC-1, TC-2 모두 MoneyballException 사용 확인 |
| 2 | 모드 A 기존 패턴 탐색 추가 | SKILL.md 모드 A Step 1 | TC-1에서 기존 예외·응답 패턴 Read 후 구현 확인 |
| 3 | 모드 A/B 설정 체크 단계 명시 | SKILL.md 모드 A Step 7, 모드 B Step 4 | TC-1 Step 7, TC-2 Step 4에서 airArray + 환경변수 체크 확인 |

### 잔여 개선 후보

1. **Domain Entity 내 예외**: `MoneyballException`을 Domain에서 사용하면 Domain이 Application 의존 → Domain 전용 예외 클래스(`CouponDomainException`) 분리 또는 `IllegalStateException` 유지 후 Service에서 변환하는 패턴 검토 필요
2. **Fixture 클래스 위치**: 현재 스킬에서 Fixture를 테스트 패키지 내에 두는데, 여러 테스트에서 공유 시 `testFixtures` 소스셋 활용 검토
