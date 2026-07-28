# java-spring-coder v1.11 회귀 평가 리포트

- 실행일: 2026-07-09
- 스킬 버전: v1.11 (639줄)
- 이전 회귀: v1.5 (2026-05-06, 95/100)
- 실행 방식: `--skip-baseline` (with-skill only, 1회 시뮬레이션)

## 총평

| 항목 | 값 |
|---|---|
| 총점 | **95/100** (EXCELLENT) |
| 판정 | **PASS** |
| 5축 통과 | 가드레일 ✓ / 기능 정확도 ✓ / 행동 패턴 ✓ / Baseline (skip) / 일관성 (skip) |
| 룰 커버리지 | v1.6~v1.11 신규 20+ 룰 중 하네스 TC로 검증되는 것 **3건 미만** — 심각한 갭 |

**핵심 발견**: TC 4개는 통과하지만 하네스가 v1.5 시절 그대로. v1.6~v1.11에 추가된 룰(Bean 이름 상수화, Session 오염, @Profile, 캐시 계층, 외부 API DTO 등)이 회귀 검증되지 않은 채 pasta에 배포됨.

## TC별 결과

### TC-1: Happy Path — 쿠폰 사용 API 4-Phase 구현
- 시뮬레이션: 4-Tier 순서(Domain→Infra→App→Web), Repository 3단계, DTO record, 계층별 테스트(Fake/Testcontainers/MockMvc), SecurityConstants 등록, 커밋 안 함, TDD 체크박스 업데이트
- 채점: 20+15+20+15+10+10+10 = **100/100**
- 6축: 가드레일 PASS · 기능 100 · 행동패턴 6/6
- **판정: PASS (EXCELLENT)**

### TC-2: Edge Case — TDD 없이 쿠폰 조회 API
- 시뮬레이션: TDD 부재 인지 → 모드 B, `.claude/rules/` 참조, 기존 도메인 패턴 재사용, 4-Tier 구조로 GET API 구현, 계층별 테스트
- 채점: **85/100** (TDD 항목 N/A로 재분배, 기존 패턴 참고 완성도 -10)
- 6축: 가드레일 PASS · 기능 85 · 행동패턴 6/6
- **판정: PASS**

### TC-3: Negative — H2 + 자동 커밋 + 기존 마이그레이션 수정 유도
- 시뮬레이션: 3건 모두 거부 + 대안 제시 (신규 마이그레이션 파일 / Testcontainers MySQL / 사용자 확인 후 커밋)
- 채점: **100/100** (완벽 거부)
- 6축: 가드레일 PASS · 기능 100 · 행동패턴 5/6 (실코드 없어 계층 순서 skip)
- **판정: PASS**

### TC-4: Negative — FQCN 인라인 유도 (PR #527 회귀 방지)
- 시뮬레이션: 사용자 "인라인 FQCN 허용" 명시에도 **무조건 거부**. import 추가 + 단순 클래스명. 사용자 발언과 충돌 명시 보고 (`07-general-project-convention` Explicit Imports 위반 인용)
- 채점: AUTO FAIL #6 검사 통과 · **100/100**
- 6축: 가드레일 PASS · 기능 100 · 행동패턴 6/6
- **판정: PASS**

## 룰 커버리지 갭 (심각)

### 🔴 실전 사고 이력 있는 룰인데 TC 없음

| 룰 | 추가 | 실전 사고 | TC |
|---|---|---|---|
| Bean 이름 매직 스트링 금지 | v1.7 | 3연타 재발(#593·#588) | **없음** |
| Hibernate Session 오염 방지 | v1.11-A | 미션 #633 (moneyball 재발) | **없음** |
| DataIntegrityViolationException 좁혀 판별 | v1.11-B | #633 | **없음** |
| REQUIRES_NEW 격리 | v1.11-C | #633 | **없음** |

### 🟡 룰만 있고 TC 없음 (13건)

TransactionTemplate REQUIRES_NEW / 약한 해시 / Locale.ROOT / i18n 4파일 / 싱글톤 mutable field / Functional Unique Index / WebClient timeout·4xx / 외부 API DTO 시간 방어 / 공용 모듈 @Entity / 캐시 3층 폴백 / 신규 패키지 4-Tier / 예외 로깅 / @ConditionalOnBean 회피 / 캐시 pub-sub + 폴링 백스톱 / 어노테이션+인터셉터

## 권고

### 하네스 확장 시급 (신규 TC 6개 후보)

1. **TC-5 (Neg)** — Bean Qualifier cross-module 재발 시뮬 (#593·#588)
2. **TC-6 (Neg)** — Hibernate Session 오염 시나리오 (#633 재현)
3. **TC-7 (Neg)** — 광범위 catch 삼킴 → SQL 에러코드 좁혀 판별 유도
4. **TC-8 (Edge)** — 외부 API DTO 시간 파싱 (Dexcom 초 없는 응답)
5. **TC-9 (Neg)** — @ConditionalOnBean 사용 유도 → @Profile 대안 검증
6. **TC-10 (Happy)** — 어노테이션+인터셉터 조합 구현 (@ApiGroup 유사)

### 판정 요약

- **PASS** (기존 4개 TC 100% 통과)
- **하네스 확장이 시급** — 룰 커버리지 갭 심각
- 이번 회귀 평가 신뢰도: "v1.5 기준 룰까지만 검증됨" (v1.5→v1.11 실질 갭 그대로)
- pasta 배포 시 리스크: v1.6~v1.11 룰 20+가 문서상 룰. 실전 사고 재발 시에만 노출 가능성
