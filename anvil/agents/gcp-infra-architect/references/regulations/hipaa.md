# HIPAA (미국) — GCP 헬스케어 컴플라이언스 매핑

> 참조 일자: 2026-04-21 (최신 확인 시 WebSearch 재실행 필수)

---

## 개요

HIPAA (Health Insurance Portability and Accountability Act)는 미국의 PHI(Protected Health Information) 보호 법률. **2026년 Security Rule 개정**으로 기존 "addressable"(권고) 안전장치 중 다수가 **필수(required)**로 전환됨.

---

## 2026 주요 변화 (핵심)

| 항목 | 기존 | 2026 개정 |
|------|------|-----------|
| 암호화 (저장/전송) | Addressable | **필수** |
| 다요소 인증 (MFA) | Addressable | **필수** |
| 백업 테스트 | Addressable | **필수** |
| 복구 능력 입증 | - | **72시간 내 데이터 복구 입증 가능해야 함** |
| 지리적으로 분리된 백업 | 권장 | **필수** |

---

## GCP BAA (Business Associate Agreement)

**필수 전제 조건**:
- HIPAA 대상 워크로드로 GCP 사용 시 **BAA 체결 필수**
- BAA 미커버 서비스에 PHI 저장/처리 **금지**
- BAA는 GCP 전체 인프라(모든 region/zone/network path) 커버
- 특정 "Covered Services" 리스트에 한해서만 PHI 허용

**주요 Covered Services** (2026년 기준, 최신은 공식 문서 확인):
- Cloud Healthcare API ← 헬스케어 전용, 최우선 고려
- Cloud Storage
- Compute Engine / GKE / Cloud Run
- Cloud SQL / Spanner / Firestore
- BigQuery
- Cloud Audit Logs
- Cloud KMS / CMEK
- VPC Service Controls
- Identity-Aware Proxy (IAP)

> **중요**: 서비스가 BAA 커버되더라도 **customer 설정**에 따라 HIPAA 준수 여부가 갈림 (Shared Responsibility). GCP는 "HIPAA-capable"이지 기본 "HIPAA-compliant"가 아님.

---

## 필수 기술 통제 (GCP 매핑)

| HIPAA 요구 | GCP 구현 |
|-----------|---------|
| 암호화 (at-rest) | 기본 암호화 + **CMEK** (Cloud KMS) 권장 |
| 암호화 (in-transit) | TLS 1.2+ 기본, VPC 간 암호화 |
| 접근 통제 (Access Control) | IAM 최소권한 원칙 + VPC SC |
| 감사 로그 (Audit) | **Cloud Audit Logs 전체 활성화** (Admin Activity, Data Access, System Event) |
| MFA | Workforce Identity Federation + MFA 강제 |
| 백업 / 복구 | Cross-region 백업 + **72시간 복구 테스트 증빙** |
| 네트워크 격리 | VPC Service Controls로 PHI 데이터 exfiltration 차단 |
| 키 관리 | Cloud KMS + CMEK + 키 로테이션 정책 |
| 모니터링 | Security Command Center + Cloud Monitoring 알림 |

---

## 데이터 레지던시 (Data Residency)

- HIPAA 자체는 데이터를 **미국 내 저장 강제 안 함** (환자 동의 + BAA + 통제 확보 시 해외 저장 가능)
- 그러나 **주(state)별 법규**(예: California CCPA/CMIA)로 강제될 수 있음
- **권고**: 미국 리전(`us-west1`, `us-central1`, `us-east4` 등) 사용 기본
- PHI의 **cross-border 이동** 시 환자 고지 + 동의 메커니즘 필요

---

## 설계 체크리스트 (에이전트 대조용)

### 필수 (누락 시 HIPAA 위반 위험)

- [ ] Google Cloud **BAA 체결**
- [ ] BAA **Covered Services만** 사용 (PHI 경로 전체)
- [ ] PHI 저장소에 **CMEK 적용** (Cloud KMS)
- [ ] **Cloud Audit Logs** (Admin + Data Access) 전체 활성화
- [ ] **VPC Service Controls** 경계 설정으로 PHI 유출 방지
- [ ] IAM **최소권한 원칙** + PHI 접근 역할 분리
- [ ] **MFA 강제** (모든 PHI 접근 사용자)
- [ ] **백업 cross-region** 구성 + 분기별 복구 테스트
- [ ] **72시간 복구 시나리오** 검증 증빙
- [ ] TLS 1.2+ 전체 경로 암호화
- [ ] **Kubernetes Secrets 평문 저장 금지** (GKE 사용 시 CMEK 연동)

### 권장

- [ ] Cloud Healthcare API 사용 검토 (PHI 전용 서비스)
- [ ] Identity-Aware Proxy (IAP) + Zero Trust 모델
- [ ] Security Command Center Premium
- [ ] Binary Authorization (GKE 시)

---

## 자주 간과되는 포인트

1. **Logging에 PHI 기록 금지** — 애플리케이션 로그에 환자 식별자 포함되면 로그 저장소도 BAA 범위에 들어와야 함
2. **개발/스테이징 환경에 운영 PHI 사용 금지** — 익명화/합성 데이터 필수
3. **외부 분석 도구 (비-GCP) 연동** — PHI가 BAA 미체결 서비스로 흘러가면 위반
4. **오래된 백업 보관 기간** — HIPAA는 6년 기록 보관 요구 (주의)

---

## 참고 자료

- [HIPAA Compliance on Google Cloud](https://cloud.google.com/security/compliance/hipaa)
- [GCP HIPAA BAA](https://cloud.google.com/terms/hipaa-baa)
- [HIPAA Compliance for Cloud Computing 2026 - Medcurity](https://medcurity.com/hipaa-cloud-compliance/)
- [HIPAA-Compliant Architecture on GCP](https://oneuptime.com/blog/post/2026-02-17-how-to-implement-hipaa-compliant-architecture-for-healthcare-applications-on-gcp/view)
