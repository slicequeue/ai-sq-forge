# TC-3 With-Agent — Terraform 구조

**메타**: 토큰 42,868 / 124.0s / tool 2회 (Read) / agentId a8a8cf5fdad2c6105

---

## 응답 원문 (요약)

# 헬스케어 4리전 Terraform — 디렉토리 구조 & state 전략

### 0. 빠진 정보 확인 5개
1. 4리전이 어디? (가정: KR·JP·US·SG)
2. 환경 단계?
3. **프로젝트 분리 방식?** (환경별 분리 강력 권고)
4. CI/CD GitHub Actions?
5. Organization 레벨 권한?

### 1. 디렉토리 구조 (권장)
- `modules/` (cloud-run, cloud-sql, vpc, iam, kms, gcs-phi, monitoring)
- `environments/{env}/{region}/` 매트릭스
- `shared/` (org-policy, tfstate-buckets, dns, iam-org)

### 트레이드오프 테이블
| 옵션 | 장점 | 단점 |
|------|------|------|
| A. 환경×리전 매트릭스 (권고) | Blast radius, 규제 격리 | 디렉토리 많음 |
| B. Provider alias 단일 root | 디렉토리 적음 | state 거대화 |
| C. workspace로 리전 구분 | 파일 최소 | 실수 위험 ↑ |

### 2. State 전략
- **리전별 GCS backend + CMEK + Versioning**
- backend.tf 예시 (참조용, 실행 금지)
- state 버킷 TF 관리 (bootstrap 패턴)
- 접근 제어 (TF 운영 SA만 write)

### 3. Provider Aliases
- 각 리전 root는 **자기 리전 provider 1개**
- shared/에서만 alias (글로벌 LB 등)

### 4. 환경×리전 매트릭스
| 환경 | 서울 | 도쿄 | 오사카 | 싱가포르 | 오레곤 |
|------|:--:|:--:|:--:|:--:|:--:|
| dev | O | - | - | - | - |
| stg | O | O | - | - | - |
| prd | O | O | O (DR) | O | O |

### 5. Organization Policy
- `gcp.resourceLocations` 화이트리스트
- `storage.publicAccessPrevention: enforced`
- `iam.disableServiceAccountKeyCreation: true` (WIF 유도)
- `sql.restrictPublicIp: true`
- `compute.requireShieldedVm: true`

### 6. 보안 기본값
- **CMEK 디폴트 ON** — 모듈 variable validation으로 강제
- VPC Service Controls 경계
- Audit Log Admin/Data Read/Write 전부
- 환경별 프로젝트 분리 권고
- Workload Identity Federation

### 7. 네이밍 컨벤션 (13개 매핑 표)
- region-short: `tokyo`, `osaka`, `seoul`, `singapore`, `oregon`

### 8. 안티패턴 8개
- 단일 root state / workspace로 환경 구분 / CMEK 없는 PHI / allUsers IAM / 등

### 9. 다음 단계 5개 제안
- ADR 3종 / Phase 로드맵 / 모듈 시그니처 / WebSearch 최신화 / deliverable 5종

### 모든 스니펫 "참조용, 실행 금지" 명시

---

## 채점 메모 (With-Agent)

| 항목 | 점수 | 비고 |
|------|------|------|
| 헬스케어 규제 점검 (20) | 18 | 4개국 암시, Org Policy·CMEK 매핑 |
| 조건부 권고 품질 (20) | 18 | A/B/C 테이블, 트레이드오프 명확 |
| GCP 서비스 선택 (15) | 15 | 모든 스택 GCP |
| Terraform IaC (15) | 15 | 디렉토리·state·provider·네이밍·안티패턴 풀스펙 |
| 최신 GCP 정보 (10) | 6 | WebSearch 미수행 (필요시 제안만) |
| deliverable 완전성 (15) | 12 | 다음 단계 제안 |
| 파트너 톤 (5) | 5 | 먼저 질문, "같이 고민" |
| **합계** | **89/100** | **PASS** |

### 행동 패턴 체크
- [x] 규제 체크 (terraform-patterns + 에이전트 Read)
- [x] 옵션 2+ 제시
- [?] WebSearch — 미수행
- [x] 맥락 질문 5개
- [x] 파트너 루프 (다음 단계 5개)
- [x] 읽기 전용 준수 (모든 스니펫 "참조용")

**AUTO FAIL 없음 → PASS**
