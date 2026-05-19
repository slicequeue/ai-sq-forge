# Terraform 패턴 — GCP 글로벌 헬스케어 IaC

> 모든 스니펫은 **참조용, 실행 금지**. 실제 apply는 사용자 승인 후 운영팀이 수행.

## 목차
- [1. 디렉토리 구조](#1-디렉토리-구조)
- [2. State 관리 전략](#2-state-관리-전략)
- [3. Provider Aliases (멀티리전)](#3-provider-aliases-멀티리전)
- [4. 환경·리전 매트릭스](#4-환경리전-매트릭스)
- [5. 모듈 작성 원칙](#5-모듈-작성-원칙)
- [6. 보안 기본값](#6-보안-기본값)
- [7. 네이밍 컨벤션](#7-네이밍-컨벤션)
- [8. 안티패턴](#8-안티패턴)

---

## 1. 디렉토리 구조

권장 구조 (Google Cloud 공식 가이드 + 멀티리전 실전 패턴):

```
infra/
├── modules/                   # 재사용 가능 모듈
│   ├── cloud-run-service/
│   ├── gke-cluster/
│   ├── cloud-sql-regional/
│   ├── vpc-network/
│   ├── iam-baseline/
│   └── kms-cmek/
├── environments/              # 환경별 root 모듈
│   ├── dev/
│   │   ├── asia-northeast1/   # 리전별 디렉토리
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   ├── backend.tf     # 환경+리전별 state
│   │   │   └── terraform.tfvars
│   │   └── asia-northeast3/
│   ├── stg/
│   │   └── ...
│   └── prd/
│       ├── asia-northeast1/   # 도쿄 (일본 사용자)
│       ├── asia-northeast2/   # 오사카 (DR)
│       ├── asia-northeast3/   # 서울 (한국 사용자)
│       ├── asia-southeast1/   # 싱가포르 (싱가포르 사용자)
│       └── us-west1/          # 미국 사용자
├── shared/                    # 리전 독립 리소스 (IAM 조직, 공통 DNS 등)
│   └── org-policy/
└── README.md
```

### 왜 환경 × 리전 매트릭스인가?

- **Blast radius 제한** — 한 리전 장애가 다른 리전 state에 영향 없음
- **배포 독립성** — 서울만 먼저 deploy, 도쿄는 뒤에
- **규제 격리** — 한국 리전 state 파일도 한국 GCS 버킷에 저장 가능
- **롤백 용이** — 리전 단위로 state rollback

---

## 2. State 관리 전략

### Backend 구성

각 환경·리전별 `backend.tf`:

```hcl
# environments/prd/asia-northeast3/backend.tf (참조용, 실행 금지)
terraform {
  backend "gcs" {
    bucket = "pasta-tfstate-prd-seoul"
    prefix = "infra/asia-northeast3"
  }
}
```

### State 버킷 원칙

- **환경별 + 리전별 별도 버킷** (예: `pasta-tfstate-prd-seoul`, `pasta-tfstate-prd-tokyo`)
- **한국 사용자 인프라 state는 서울 리전 GCS에** — 규제 일관성
- 버킷에 **CMEK 적용** (KMS 같은 리전)
- **Versioning 활성화** (`lifecycle_rule`로 오래된 버전 정리)
- **IAM 엄격 제한** — TF 운영자 역할만 write, 나머지는 read 금지

### 샘플 state 버킷 (참조용)

```hcl
# shared/tfstate-buckets/main.tf (참조용)
resource "google_storage_bucket" "tfstate_seoul" {
  name     = "pasta-tfstate-prd-seoul"
  location = "ASIA-NORTHEAST3"
  
  versioning {
    enabled = true
  }
  
  uniform_bucket_level_access = true
  
  encryption {
    default_kms_key_name = google_kms_crypto_key.tfstate_seoul.id
  }
  
  lifecycle_rule {
    condition { num_newer_versions = 10 }
    action    { type = "Delete" }
  }
}
```

---

## 3. Provider Aliases (멀티리전)

단일 root 모듈에서 여러 리전 제어 시 provider alias 필수:

```hcl
# providers.tf (참조용, 실행 금지)
provider "google" {
  project = var.project_id
  region  = "asia-northeast3"   # 기본: 서울
}

provider "google" {
  alias   = "tokyo"
  project = var.project_id
  region  = "asia-northeast1"
}

provider "google" {
  alias   = "osaka"
  project = var.project_id
  region  = "asia-northeast2"
}

provider "google" {
  alias   = "us_west"
  project = var.project_id
  region  = "us-west1"
}

provider "google" {
  alias   = "singapore"
  project = var.project_id
  region  = "asia-southeast1"
}
```

모듈 호출 시:
```hcl
module "api_tokyo" {
  source = "../../modules/cloud-run-service"
  providers = { google = google.tokyo }
  # ...
}
```

> **실전 권장**: 규제 격리 강도가 높으면 provider alias보다 **리전별 root 모듈 디렉토리**로 분리하는 편이 안전. Alias 방식은 리전 1~2개 공유 리소스에만.

---

## 4. 환경·리전 매트릭스

### 권장 배치 (파스타 글로벌)

| 환경 | 한국 | 일본 | 미국 | 싱가포르 |
|------|------|------|------|---------|
| **dev** | 서울 (공유) | - | - | - |
| **stg** | 서울 | 도쿄 | - | - |
| **prd** | 서울 | 도쿄 + 오사카(DR) | 오레곤 | 싱가포르 |

- **dev는 최소화** — 비용 절감, 로컬·서울 1곳만
- **stg는 주요 리전만** — 멀티리전 동작 검증용
- **prd는 전체 리전** — 실 사용자 기준

---

## 5. 모듈 작성 원칙

### 5-1. 표준 구조

모든 모듈은 최소 아래 파일:
```
modules/{name}/
├── main.tf        # 리소스 정의
├── variables.tf   # 입력
├── outputs.tf     # 출력 (최소 1개 필수)
├── versions.tf    # provider 버전 핀
└── README.md      # 사용법 + 예시
```

### 5-2. 변수·출력 원칙

- **모든 리소스에 최소 1개 output** (다른 모듈에서 참조 가능)
- **project_id, region은 variable로** (하드코딩 금지)
- **민감값은 variable + `sensitive = true`**
- **required vs optional 변수 구분** (default 있으면 optional)

### 5-3. versions.tf (버전 고정)

```hcl
terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}
```

---

## 6. 보안 기본값 (헬스케어 필수)

모든 모듈에 기본 내장해야 할 것:

### 6-1. CMEK 기본 활성화

```hcl
# modules/cloud-sql-regional/main.tf (참조용 조각)
resource "google_sql_database_instance" "main" {
  # ...
  encryption_key_name = var.cmek_key_id  # CMEK 필수
}
```

### 6-2. Audit Log 활성화

```hcl
# shared/org-policy/audit.tf (참조용)
resource "google_project_iam_audit_config" "all" {
  project = var.project_id
  service = "allServices"
  
  audit_log_config { log_type = "ADMIN_READ" }
  audit_log_config { log_type = "DATA_READ" }
  audit_log_config { log_type = "DATA_WRITE" }
}
```

### 6-3. Organization Policy로 리전 제한

```hcl
# shared/org-policy/resource-location.tf (참조용)
resource "google_org_policy_policy" "resource_locations" {
  name   = "projects/${var.project_id}/policies/gcp.resourceLocations"
  parent = "projects/${var.project_id}"
  
  spec {
    rules {
      values {
        allowed_values = [
          "in:asia-northeast1-locations",   # 도쿄
          "in:asia-northeast2-locations",   # 오사카
          "in:asia-northeast3-locations",   # 서울
          "in:asia-southeast1-locations",   # 싱가포르
          "in:us-west1-locations",          # 오레곤
        ]
      }
    }
  }
}
```

### 6-4. VPC Service Controls

PHI 저장 프로젝트는 **VPC SC 경계** 안에 배치. 경계 밖 서비스로 데이터 나가는 경로 차단.

### 6-5. Workload Identity Federation

CI/CD (GitHub Actions 등)에서 service account key 파일 사용 금지 → Workload Identity Federation.

---

## 7. 네이밍 컨벤션

| 리소스 | 패턴 | 예시 |
|--------|------|------|
| 프로젝트 | `{product}-{env}` | `pasta-prd` |
| VPC | `{product}-{env}-vpc-{region}` | `pasta-prd-vpc-seoul` |
| 서비스 계정 | `{product}-{role}-{env}@...` | `pasta-runtime-prd@...` |
| Cloud Run | `{service}-{env}` | `api-prd` |
| GKE 클러스터 | `{product}-{env}-{region}` | `pasta-prd-tokyo` |
| Cloud SQL | `{product}-{env}-{region}-{n}` | `pasta-prd-seoul-01` |
| KMS KeyRing | `{product}-{env}-{region}` | `pasta-prd-seoul` |
| KMS Key | `{purpose}-key` | `sql-key`, `storage-key` |
| GCS Bucket | `{product}-{env}-{region}-{purpose}` | `pasta-prd-seoul-uploads` (GCS는 글로벌 유니크) |

---

## 8. 안티패턴 (피해야 할 것)

1. **단일 root state로 전 리전 관리** — blast radius 과대, 배포 독립성 상실
2. **하드코딩된 project_id / region** — 환경별 재사용 불가
3. **`terraform apply -target` 남용** — state 불일치 원인
4. **수동 리소스 혼재** — TF가 모르는 리소스 → drift 지속 발생
5. **Secret을 tfvars에 평문 저장** — Secret Manager 참조로
6. **CMEK 없는 PHI 저장소 생성** — 헬스케어 자동 위반
7. **`allUsers` / `allAuthenticatedUsers` IAM** — 헬스케어 절대 금지
8. **개발환경에 운영 CMEK 공유** — 키 경계 혼선

---

## 8-1. 최소 module 예시 (Cloud Run, 참조용)

```hcl
# modules/cloud-run-service/main.tf
resource "google_cloud_run_v2_service" "this" {
  name     = var.service_name
  location = var.region
  project  = var.project_id
  
  template {
    service_account = var.service_account_email
    
    containers {
      image = var.image
      
      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }
      
      env {
        name = "ENVIRONMENT"
        value = var.env
      }
    }
    
    vpc_access {
      connector = var.vpc_connector_id
      egress    = "ALL_TRAFFIC"
    }
  }
  
  # CMEK (헬스케어 필수)
  encryption_key = var.cmek_key_id
}

output "url" {
  value = google_cloud_run_v2_service.this.uri
}
```

---

## 참고 자료

- [Best practices for reusable modules (Google Cloud)](https://docs.cloud.google.com/docs/terraform/best-practices/reusable-modules)
- [Best practices for root modules](https://docs.cloud.google.com/docs/terraform/best-practices/root-modules)
- [Terraform Provider Aliases for Multi-Region GCP](https://oneuptime.com/blog/post/2026-02-17-how-to-configure-terraform-provider-aliases-for-multi-region-gcp-deployments/view)
- [Cloud Run Multi-Region Terraform (ahmetb)](https://github.com/ahmetb/cloud-run-multi-region-terraform)
