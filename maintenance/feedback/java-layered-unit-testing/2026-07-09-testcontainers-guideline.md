---
component: java-layered-unit-testing
source: pasta-japan-server MISSION #633 후속
date: 2026-07-09
type: guideline-expansion
severity: medium
---

## 흡수 사고 (후속)

MISSION #633 (2026-07-08) 최종 리팩터에서 `Testcontainers 통합 테스트 추가`. Hibernate Session 오염 회귀 검증용.

## v1.5 개선 반영

**신규 섹션 5)**: 통합 테스트 (`@SpringBootTest` + Testcontainers) — 5개 트리거 표

**Testcontainers 사용 트리거**:
1. **동시성 시나리오** — race condition, 중복 삽입 경합 (#633 뱃지 중복 케이스)
2. **트랜잭션 경계 검증** — REQUIRES_NEW 격리 여부, propagation 정합
3. **JPA Session 관련 로직** — Session 오염, EntityManager flush 순서
4. **DB 제약 사고** — unique/NOT NULL/FK 위반 실제 오류 코드 확인
5. **write-through·pub-sub 캐시** — Redis + DB 정합성 검증

**기존 단위 테스트로 대체 불가한 경우에만** Testcontainers. 단위 테스트가 대안일 때는 우선 단위 테스트.

## 파일 크기

269줄 → 287줄 (+18)

## 자기 검증

기존 자기 검증에 통합 테스트 트리거 확인 항목 추가.

## 누적 검토

v1.3 (FQCN) → v1.4 (infra 직접 참조 금지·Fake) → v1.5 (Testcontainers 트리거). **테스트 계층 격리**에서 **통합 테스트 도입 기준** 확장. Fake vs Testcontainers 선택 기준 명확화.
