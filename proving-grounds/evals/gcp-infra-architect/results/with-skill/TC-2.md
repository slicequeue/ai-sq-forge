# TC-2 With-Agent — 글로벌 확장 설계안

**메타**: 토큰 78,539 / 235.8s / tool 14회 (Read + WebSearch) / agentId a7068fe76f6913318

---

## 응답 원문 (요약)

# pasta 글로벌 확장 설계안 — 한·일·미·싱 4리전 (GCP + Terraform)

### Deliverable 1. 경영진 요약 (1페이지)
- **현행**: GCP Cloud Run (일본 단일 리전)
- **규제 4개국 명시**:
  - 🇺🇸 HIPAA 2026 Security Rule 개정 (암호화·MFA·72h 복구 **필수화**)
  - 🇰🇷 PIPA + K-HISA
  - 🇯🇵 3省2ガイドライン **v2.0 2025.03 개정** (책임분계)
  - 🇸🇬 PDPA + HCSE 12권고 + **NRIC 인증 2026.12.31 금지**

### 핵심 권고 5개 (조건부)
1. 컴퓨트: Cloud Run 유지, Phase 3에서 하이브리드 재평가
2. DB: 리전별 Cloud SQL Postgres 분리, **Spanner 멀티리전 불채택**
3. 데이터 레지던시: Regional Silo
4. Terraform: 환경×리전 매트릭스
5. 보안: CMEK + VPC SC + Cloud Audit Logs + MFA + Org Policy

### Deliverable 2. Mermaid 다이어그램 2개
- 글로벌 전체 흐름 (4리전 + Shared)
- Terraform state 매트릭스

### Deliverable 3. ADR 10건 요약
- ADR-001 컴퓨트 (Cloud Run 유지)
- ADR-002 **DB — Spanner 불채택** (한국 dual-region 미지원, 4개국 균일 배치 불가)
- ADR-003 리전 배치
- ADR-004 **데이터 레지던시 — 4개국 규제 매핑표**
- ADR-005 Terraform 구조
- ADR-006 CMEK
- ADR-007 인증·MFA·NRIC 금지 대응
- ADR-008 CI/CD WIF
- ADR-009 관측성
- ADR-010 DR·BCP

### Deliverable 4. Terraform 스니펫 6개 (**참조용, 실행 금지** 명시)
- 디렉토리 구조
- Org Policy resourceLocations
- Cloud SQL + CMEK + PITR
- KMS KeyRing
- Cloud Run + VPC Connector
- backend.tf 리전별

### Deliverable 5. Phase 로드맵
- Phase 0 현황 진단 (3~4주)
- Phase 1 기반 구축 (6~8주)
- Phase 2 리전 확장 (12~16주)
- Phase 3 최적화 (4~8주)
- **각 Phase별 PoC 검증 포인트** 포함

### Sources 14개
- HIPAA 2026 (hipaavault, cbiz)
- Spanner dual-region (Google Cloud Blog)
- NRIC 2026 (PDPC 공식, Baker McKenzie)
- METI v2.0 (2025.03)
- Terraform best practices
등 **모두 링크 첨부**

### 자기 검증 체크리스트 9/9 PASS

---

## 채점 메모 (With-Agent)

| 항목 | 점수 | 비고 |
|------|------|------|
| 헬스케어 규제 점검 (20) | 20 | **4개국 모두**, 최신 개정(HIPAA 2026, 3省2 v2.0, NRIC 2026) 반영 |
| 조건부 권고 품질 (20) | 20 | ADR별 옵션·포기·조건부 재평가 |
| GCP 서비스 선택 (15) | 15 | Cloud Run/Cloud SQL/Spanner 적절 판단 |
| Terraform IaC (15) | 15 | 6종 스니펫 + "참조용 실행 금지" |
| 최신 GCP 정보 (10) | 10 | **WebSearch 다수 + 출처 14개** |
| deliverable 완전성 (15) | 15 | **5종 풀패키지 + Phase PoC 포인트** |
| 파트너 톤 (5) | 5 | 파트너 맥락, 확인 루프 |
| **합계** | **100/100** | **EXCELLENT** |

### 행동 패턴 체크
- [x] 규제 체크 4개국 모두 Read
- [x] 옵션 제시 (ADR별 대안 명시)
- [x] **WebSearch 활용** (2026년 자료 확보)
- [x] 맥락 질문 (Phase 0 빈 변수 명시)
- [x] 파트너 루프 (Phase 5 확인 루프)
- [x] 읽기 전용 준수

**6/6 행동 패턴 전부 충족. AUTO FAIL 없음 → PASS (EXCELLENT)**
