# ADR-005: Terraform 구조 — Green-field 신규 도입 (v0.2 재작성)

- **상태**: Proposed
- **작성일**: 2026-04-22 (v0.2 재작성)
- **리뷰어**: 인프라팀 / DevOps
- **관련**: ADR-001, ADR-003, ADR-006, ADR-011
- **Supersedes**: v0.1 ADR-005 (기존 TF 있음 가정, 폐기)

---

## v0.2 변경 이유

v0.1은 "기존 Terraform 있음" 가정이었으나, Phase 1.5 확인 결과:
- `pasta-japan-server` 레포 내 `*.tf` 파일 **0건**
- 별도 IaC 레포 **없음** (사용자 확인)
- 현재 48개 Cloud Run 서비스 + 6개 DB 인스턴스가 **수동 배포 or CI/CD 스크립트 기반**

→ **Terraform 신규 도입 (green-field)**으로 방향 전환.

---

## 컨텍스트

- IaC는 Terraform으로 확정 (사용자 선택)
- 신규 글로벌 레포에서 처음부터 구축
- 4리전 × 3환경 = 최대 12 셀 매트릭스
- 기존 운영 리소스(48 서비스 + 6 DB)의 TF import 여부도 결정 필요

**결정할 사항**: 디렉토리 구조 / state 전략 / 기존 리소스 import 정책.

---

## 결정

### Option A: 환경×리전 매트릭스 + 리전별 state (v0.1 동일) ⭐ 권고

- 디렉토리 구조 v0.1과 동일
- state 버킷 리전별 분리, CMEK·Versioning
- Provider alias는 shared/ 공유 리소스에만

### 🆕 기존 리소스 Import 정책 (v0.2 신설)

기존 한·일 Cloud Run·Cloud SQL을 **TF로 가져올지** 결정:

| 옵션 | 설명 | 판정 |
|------|------|------|
| A1. **선택적 Import** | 신규 리전은 green-field TF, 기존 한·일은 **마이그레이션 시점(Phase 3)에 선택적 import** | ⭐ 권고 |
| A2. 전체 Import | Phase 1에 48개 서비스 전부 import | 작업 부담 과대, Phase 1 지연 |
| A3. Import 안 함 | 기존은 수동 계속, 신규만 TF | 운영 2-track 지속, 장기 부채 |

**권고**: A1. 신규 리전은 처음부터 TF, 기존은 Phase 3 통합 시점에 의미 있는 리소스(Cloud SQL, KMS, VPC 등)만 import. Cloud Run 서비스는 CI/CD와 분리 운영 가능.

---

## 디렉토리 구조

```
pasta-global-infra/               # 신규 레포 (가칭)
├── modules/
│   ├── cloud-run-service/
│   ├── cloud-sql-mysql-regional/ # v0.2: MySQL
│   ├── vpc-network-regional/
│   ├── kms-cmek/
│   ├── iam-baseline/
│   ├── logging-sink-regional/
│   └── vpc-service-controls/
├── environments/
│   ├── dev/asia-northeast3/
│   ├── stg/
│   │   ├── asia-northeast3/
│   │   └── asia-northeast1/
│   └── prd/
│       ├── asia-northeast1/      # 🇯🇵 도쿄 — Phase 3에 import
│       ├── asia-northeast2/      # 🇯🇵 오사카 DR — Phase 2 신규
│       ├── asia-northeast3/      # 🇰🇷 서울 — Phase 3에 import
│       ├── asia-southeast1/      # 🇸🇬 싱가포르 — Phase 2 신규
│       └── us-west1/             # 🇺🇸 오레곤 — Phase 2 신규
├── shared/
│   ├── org-policy/
│   ├── tfstate-buckets/
│   └── global-lb/
└── README.md
```

---

## State 전략

### Backend (리전별 분리)

```hcl
# environments/prd/asia-northeast3/backend.tf — 참조용, 실행 금지
terraform {
  backend "gcs" {
    bucket = "pasta-tfstate-prd-seoul"
    prefix = "infra/prd/asia-northeast3"
  }
}
```

### State 버킷 원칙

- 환경·리전 매트릭스 = 최대 **8 버킷** (dev 1 + stg 2 + prd 5)
- 각 버킷 CMEK + Versioning + Public access prevention
- Uniform Bucket-Level Access + Bucket Lock
- TF 운영 SA만 write

### Bootstrap 순서

1. 최초 1회 로컬 state로 tfstate 버킷 자체 생성 → remote migrate
2. 또는 `gcloud` 수동 생성 후 `terraform import`
3. 이후 모든 변경은 TF 관리

---

## 기존 리소스 Import 전략 (Phase 3)

### Import 대상 (의미 있는 것만)

- [ ] Cloud SQL 인스턴스 (한·일 기존 DB) — CMEK 도입 필수라 TF 관리 권고
- [ ] KMS KeyRing (도입 시)
- [ ] VPC·서브넷 (네트워크 정책 통일)
- [ ] Organization Policy
- [ ] Cloud Logging sink
- [ ] IAM 서비스 계정 (중요한 것만)

### Import 비대상 (현행 유지)

- Cloud Run 서비스 개별 설정 (CI/CD 배포 스크립트와 분리)
- Cloud Storage 버킷 (마이그레이션 시에만)
- Secret Manager (운영 민감, 별도 정책)

---

## 보안 기본값 (v0.1 유지)

- CMEK 기본 ON (variable 필수)
- Audit Log 전체 활성화
- Organization Policy 리전 제한
- VPC Service Controls 경계

---

## 결과

### 긍정적
- 신규 리전 Day 1부터 IaC 관리
- 기존 운영 무중단
- Terraform 학습 곡선 점진 (신규부터 시작 → Phase 3에 기존 편입)

### 부정적 / 감수
- Phase 3 import 작업 부담
- 2-track (TF / 수동) 일시 병존
- 기존 수동 리소스와 TF state drift 리스크

### 후속 작업

- [ ] Phase 1: 네이밍 컨벤션 문서 확정
- [ ] Phase 1: 모듈 세트 v1 구현
- [ ] Phase 1: CI 파이프라인 (fmt/validate/plan 자동)
- [ ] Phase 1: State 버킷 생성 스크립트
- [ ] Phase 2: 신규 리전 3개 TF apply (오사카·오레곤·싱가포르)
- [ ] Phase 3: 기존 한·일 Cloud SQL·VPC·KMS import + 재정비

---

## 리스크 & 완화

| 리스크 | 가능성 | 영향 | 완화 |
|--------|-------|------|------|
| 기존 리소스 drift (import 전까지) | M | M | Phase 3 전까지 수동 변경은 드물다고 가정, 변경 이력 문서화 |
| Import 작업 지연 | M | M | 핵심 리소스만 import, Cloud Run 등은 CI/CD로 계속 |
| 담당자 단독 apply 실수 | H (신규 도입) | H | prd는 PR 리뷰 + CI 기반 apply 강제 |
| 네이밍 규칙 실수 | M | L | Linter + PR 체크 |

---

## 검증 포인트

- [ ] Phase 1: `terraform plan` 오류 0
- [ ] Phase 1: 모듈 단위 테스트 (Terratest)
- [ ] Phase 2: 신규 리전 3개 동시 apply 가능
- [ ] Phase 3: 기존 import 후 drift 0

---

## 참고

- `anvil/agents/gcp-infra-architect/references/terraform-patterns.md`
- [Terraform GCP Best Practices](https://docs.cloud.google.com/docs/terraform/best-practices/root-modules)
- [Terraform import](https://developer.hashicorp.com/terraform/cli/import)
