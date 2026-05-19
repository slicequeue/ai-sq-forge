# 일본 3省2ガイドライン — GCP 헬스케어 매핑

> 참조 일자: 2026-04-21 (최신 확인 시 WebSearch 재실행 필수)

---

## 개요

일본의 의료정보 클라우드 이용 표준은 "**3省2ガイドライン**" (3개 부처 2개 가이드라인)으로 통칭:

| 가이드라인 | 발행처 | 최신 버전 | 대상 |
|-----------|--------|-----------|------|
| 의료정보시스템 안전관리 가이드라인 | **후생노동성** | **v6.0 (2023.05)** | 의료기관 |
| 의료정보 취급 정보시스템·서비스 제공자 안전관리 가이드라인 | **경산성 + 총무성** | **v2.0 (2025.03)** | 시스템/서비스 제공자 (CSP 포함) |

의료 DX 진전에 따른 **클라우드 활용 확대**를 공식 수용한 개정. 전자 카르테의 외부 저장(클라우드 이전)이 정상 궤도.

---

## 2026 핵심 동향

- v2.0 (2025.03) 개정 핵심: 의료기관과 서비스 제공자 간 **권한·책임 관계 명확화**
- 클라우드 이전 시 **위탁계약서 필수 항목** 구체화
- 보안 사고 발생 시 **보고 체계** 강화

---

## 주요 요구사항 (요약)

### 1. 책임분계 (責任分界)
- 의료기관(이용자)과 서비스 제공자(CSP 포함) 간 **책임 범위 문서화**
- GCP의 경우 Google Cloud Shared Responsibility Model + **별도 위탁계약서** 필요
- 사고 발생 시 책임 주체·통보 절차 명시

### 2. 데이터 레지던시
- **원칙: 일본 내 저장**
- 국외 저장 시 해당국 법률·이전받는 자의 보호수준 사전 평가 필수
- 실무상 일본 의료기관의 해외 리전 사용은 매우 제한적

### 3. 기술 통제
- 암호화 (저장/전송)
- 접근 제어 (역할 기반)
- **모든 접근 로그 보관** (최소 수년)
- 백업 + 복구 시험
- 통신 경로 암호화

### 4. 운영 통제
- 위탁계약서에 **감사권** 명시
- 정기 보안 감사 (외부 감사 포함)
- 인시던트 대응 체계 문서화
- **개인정보 취급자 교육**

### 5. 물리·환경 통제
- 데이터센터 물리 보안 (GCP 자체 인증으로 대체 가능)
- **이중화** 및 재해 복구 (BCP)

---

## GCP 매핑

| 3省2 요구 | GCP 구현 |
|-----------|---------|
| 일본 내 저장 | `asia-northeast1` (도쿄) 또는 `asia-northeast2` (오사카) |
| 암호화 at-rest | 기본 암호화 + **CMEK** (Cloud KMS 일본 리전 키) |
| 암호화 in-transit | TLS 1.2+ + VPC Service Controls |
| 접근 제어 | IAM + 조직 정책 + Workforce Identity |
| 접근 로그 | Cloud Audit Logs (Admin + Data Access + System Event) |
| 장기 로그 보관 | Log Router → Cloud Storage (리전 지정) |
| 백업 + 복구 | 도쿄 ↔ 오사카 cross-region 백업 (일본 내 이중화) |
| BCP | 멀티 존 구성 + 오사카 리전 fallback |
| 감사권 | GCP 제3자 감사 리포트 + Cloud Audit Logs 전체 조회 |

---

## 일본 리전 선택

| 리전 | 용도 |
|------|------|
| `asia-northeast1` (도쿄) | 주 리전 |
| `asia-northeast2` (오사카) | DR·백업 리전 (도쿄 장애 대비) |

**권고**: Primary는 도쿄, DR/백업은 오사카. 둘 다 일본 내.

---

## 설계 체크리스트 (에이전트 대조용)

### 필수

- [ ] 의료정보는 **일본 내 리전** (도쿄/오사카) 저장
- [ ] **CMEK** (Cloud KMS 일본 리전 키)
- [ ] **위탁계약서** 작성 (Google Cloud 약관 + 추가 조항)
- [ ] **Cloud Audit Logs** 전체 활성화 + 장기 보관
- [ ] **VPC Service Controls** 경계 (일본 리전 제한)
- [ ] **Organization Policy**로 리소스 위치 제한 (`asia-northeast1`, `asia-northeast2`)
- [ ] 도쿄 ↔ 오사카 **cross-region 백업**
- [ ] **IAM 최소권한** + 의료정보 접근자 별도 역할
- [ ] 암호화 전송 (TLS 1.2+)
- [ ] **인시던트 대응 체계** 문서화 + GCP와의 통보 체계 정립

### 권장

- [ ] **Security Command Center Premium**
- [ ] Identity-Aware Proxy (IAP)
- [ ] Binary Authorization (GKE 시)
- [ ] 정기 **외부 보안 감사**
- [ ] **BCP 시나리오** 분기별 훈련

---

## 자주 간과되는 포인트

1. **Google Workspace / Looker** 등 GCP 외 서비스로 의료정보가 흐르면 별도 평가 필요
2. **로그 분석 (BigQuery 등)** 시 다리전 구성이면 일본 외 이전 발생 가능
3. **GKE Artifact Registry** — 이미지 저장소가 글로벌이면 일본 리전 지정 필수
4. **위탁계약서에 감사권·조기통보·삭제의무 명시** 안 되면 감독 당국 지적 사유

---

## 참고 자료

- [厚生労働省 医療情報システム安全管理ガイドライン](https://www.mhlw.go.jp/)
- [経済産業省 医療情報を取り扱う情報システム・サービスの提供事業者における安全管理ガイドライン](https://www.meti.go.jp/policy/mono_info_service/healthcare/teikyoujigyousyagl.html)
- [AWS - 医療情報ガイドラインの改定から読み解くクラウド化](https://aws.amazon.com/jp/blogs/news/japan-security-guidelines-for-medical-information-systems-2023-06/)
- [3省2ガイドライン 解説 (日立システムズ)](https://www.hitachi-systems.com/solution/s0311/medinfo/guideline/)
