# ADR-002: DB 전략 — 리전별 Cloud SQL MySQL HA (v0.2 재작성)

- **상태**: Proposed
- **작성일**: 2026-04-22 (v0.2 재작성)
- **리뷰어**: 백엔드 리드 / DBA / 보안
- **관련**: ADR-003, ADR-004, ADR-006, ADR-012
- **Supersedes**: v0.1 ADR-002 (Postgres 가정 기반, 폐기)

---

## v0.2 변경 이유

v0.1은 현행 DB를 **PostgreSQL**로 가정했으나, Phase 1.5 gcloud 현황 파악 결과 **실제 엔진은 MySQL 8.0/8.4**로 확인됨:

| 인스턴스 | 엔진 | 프로젝트 |
|---------|------|---------|
| sql-prd-pasta-app | MYSQL 8.0 | prd-pasta (한국) |
| sql-prd-pasta-app-replica | MYSQL 8.0.31 | 한국 replica |
| sql-prd-pasta-body-ai-app | MYSQL 8.0.41 | 한국 AI 전용 |
| sql-prd-pasta-jp-app | MYSQL 8.0 | 일본 |
| sql-prd-pasta-jp-app-replica | MYSQL 8.0.31 | 일본 replica |
| sql-prd-pasta-jp-body-ai-app | MYSQL 8.4 | 일본 AI 전용 |

→ 전 DB가 MySQL. Postgres 가정은 폐기.

---

## 컨텍스트

- pasta는 **헬스케어**. 4개국 규제 모두 헬스케어 데이터의 **국경 이동 엄격 통제**
- 현 DB 엔진 = **MySQL 8.0 / 8.4**
- 한국·일본 모두 Primary + Read Replica + AI 전용 DB 별도 분리 (이미 성숙)
- 트래픽 수백 RPS 이내 → 글로벌 단일 DB 성능 우위 결정적 아님

**결정할 사항**: 글로벌 단일 DB vs 리전별 분리 + 엔진 유지 vs 전환.

---

## 고려한 옵션

### Option A: **리전별 Cloud SQL MySQL HA** ⭐ 권고

**설명**:
- 각 리전에 독립 Cloud SQL MySQL (현행 엔진 유지)
- 리전 내 Primary + Read Replica(HA)
- 도쿄는 오사카 cross-region 백업 (Phase 2 신규)
- body-ai DB도 리전별 분리 유지

**장점**:
- 데이터 주권 준수
- **현행 엔진·스키마·Flyway 마이그레이션·JPA 엔티티 그대로**
- 팀 MySQL 운영 경험 연속
- 리전 장애 blast radius 제한
- AI 전용 DB 분리 패턴(body-ai) 그대로 확장

**단점**:
- 글로벌 단일 뷰 불가 (분석 파이프라인 별도)
- 리전별 스키마 drift 가능 (Flyway 통일로 완화)
- 글로벌 조인/트랜잭션 불가

### Option B: Spanner 멀티리전

❌ 불채택 — v0.1과 동일 이유:
- 헬스케어 데이터 자동 복제 = 개보법/3省2 충돌
- 한국(`asia-northeast3`) 멀티리전 read-write 구성 미지원
- 현 MySQL → Spanner 마이그레이션 대규모 리스크

### Option C: PostgreSQL 전환

❌ 불채택:
- 현 MySQL 스키마·JPA 엔티티·JPQL·Flyway 전면 재작성
- 팀 학습 곡선
- 전환 자체가 글로벌 확장보다 큰 리스크
- 엔진 차이로 얻을 이득이 데이터 주권 요구와 맞지 않음

### Option D: AlloyDB (PostgreSQL 호환, 고성능)

❌ 불채택:
- PostgreSQL 호환이라도 MySQL에서 전환하는 건 Option C와 동일 부담
- 단, **body-ai DB**(AI 워크로드)는 향후 AlloyDB 검토 여지 (별도 ADR)

---

## 결정

> **선택: Option A — 리전별 Cloud SQL MySQL HA**

### 선택 근거

1. **현행 엔진 유지로 전환 리스크 0** — MySQL 8.0 그대로
2. **규제 정합** — 리전별 silo로 데이터 주권 준수
3. **이미 한·일에서 검증된 운영 패턴** (Primary + Replica + body-ai 분리)
4. **AI 워크로드 분리** 패턴 확장 가능 (리전별 body-ai 분리)
5. **Flyway·JPA·쿼리 자산 그대로** — 애플리케이션 레벨 변경 최소

### 수용한 트레이드오프

- 글로벌 단일 뷰 → 분석은 리전별 **BigQuery + Dataflow 익명화 집계**
- 글로벌 트랜잭션 → 비즈니스 로직에서 리전 경계 존중
- 리전 drift → **Flyway 단일 소스** + CI에서 전 리전 migration 검증

---

## MySQL 특화 고려사항

### PITR 활성화 (MySQL 특이점)

Cloud SQL MySQL PITR은 **binary log 기반**:
- `binary_log_enabled = true` 필수
- `transaction_log_retention_days` 설정 (기본 7일)
- **기존 한·일 인스턴스는 PITR 미활성 상태** → ADR-012 데드라인으로 도입

### Managed Connection Pooling (2026)

- GCP Cloud SQL Managed Connection Pooling 활용 (MySQL 지원 확인 필요)
- 지원 시 Cloud Run ↔ Cloud SQL 안정성 개선 (현행 통증 해결)
- 미지원 시 **ProxySQL** 사이드카 고려

### Binary log Replication 최신 상태

- MySQL 8.0 → 8.0.31 → 8.4 버전 drift 존재 (현재)
- 신규 리전은 **MySQL 8.4** 통일 권고 (최신 LTS)
- 기존 리전은 통합 시점에 업그레이드

---

## 결과

### 긍정적
- 전환 리스크 0, 현행 자산 유지
- 규제 자동 준수
- AI 워크로드 분리 패턴 계승

### 부정적 / 감수
- 글로벌 집계는 별도 파이프라인 (익명화 필수)
- 리전 drift 리스크 → Flyway + CI 완화
- MySQL PostgreSQL 대비 특정 고급 기능 제한 (JSONB, CTE 등) — 기존 앱이 이미 MySQL 전제

### 후속 작업

- [ ] Phase 1: `modules/cloud-sql-mysql-regional/` Terraform 모듈 작성 (MySQL 8.4 기준)
- [ ] Phase 1: Flyway CI 파이프라인 (전 리전 migration 검증)
- [ ] Phase 2: 미국·싱가포르 리전에 신규 MySQL 8.4 인스턴스 배포
- [ ] Phase 3: **기존 한·일 MySQL에 CMEK/PITR 도입** (ADR-012 데드라인)
- [ ] Phase 3: body-ai DB AlloyDB 전환 검토 (별도 ADR)
- [ ] 글로벌 분석: BigQuery 익명화 파이프라인 설계 (별도 ADR)

---

## 리스크 & 완화

| 리스크 | 가능성 | 영향 | 완화 |
|--------|-------|------|------|
| 리전 간 MySQL 버전 drift (8.0/8.4) | H | M | 신규 리전은 8.4, 기존은 Phase 3에 업그레이드 |
| Flyway 마이그레이션 실수로 리전 drift | M | H | CI에서 전 리전 migration dry-run |
| PITR 미활성 (기존 리전) | H (현재) | H | ADR-012 데드라인 |
| Managed Pooling MySQL 미지원 가능성 | L | M | 백업: ProxySQL 사이드카 |

---

## 검증 포인트

- [ ] Phase 1: MySQL 모듈 PR 리뷰, `terraform plan` 0 오류
- [ ] Phase 2: 신규 리전 MySQL 8.4 + CMEK + PITR 전 항목 ON
- [ ] Phase 2: Flyway 마이그레이션 전 리전 일치율 100%
- [ ] Phase 3: 기존 한·일 CMEK/PITR 전환 완료 (ADR-012 gate)

**재평가 시점**: Phase 3 종료 시 또는 글로벌 분석 요구 실체화 시점.

---

## 참고

- 에이전트 결정 프레임워크: `anvil/agents/gcp-infra-architect/references/decision-frameworks.md` §3
- [Cloud SQL MySQL PITR](https://cloud.google.com/sql/docs/mysql/backup-recovery/pitr)
- [Cloud SQL MySQL CMEK](https://cloud.google.com/sql/docs/mysql/configure-cmek)
- 규제 참조: `anvil/agents/gcp-infra-architect/references/regulations/`
