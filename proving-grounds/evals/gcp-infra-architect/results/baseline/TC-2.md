# TC-2 Baseline — 글로벌 확장 설계안

**메타**: 토큰 20,168 / 84.8s / tool 0회 / agentId a8db75a67e17d31f5

---

## 응답 원문 (요약)

# Pasta 글로벌 확장 설계안 (v0.1, Draft)

대상 리전: KR (**ap-northeast-2**) / JP (**ap-northeast-1**) / US (**us-east-1 + us-west-2**) / SG (**ap-southeast-1**)
IaC: Terraform (AWS Provider)

### Executive Summary
- 글로벌 사용자 레이턴시 p95 < 150ms
- RTO 15분 / RPO 1분
- HIPAA, 개인정보보호법, APPI, PDPA 준수

### Architecture
- **Route 53 + AWS Global Accelerator**
- 리전별 **EKS + RDS(PostgreSQL) + S3(KMS) + Redis**
- Cognito federated auth (US)
- S3 Audit Lake (Cross-Region Replication)

### ADR 7건
- Data Residency: Sharded by Region
- DB: No Cross-Region Replica for PHI (RDS Multi-AZ)
- Auth: Cognito federation
- Terraform: `modules/region-stack/`, `envs/prod-{kr,jp,us,sg}/`
- Deploy: ArgoCD + Region Wave (SG canary → JP → KR → US)
- Blast Radius: read-only degrade mode
- Compliance: KMS CMK, S3 Object Lock 7년

### Network
- **Transit Gateway per region + TGW Peering**
- VPC CIDR: 10.10~10.40

### 비용 (월, USD)
- 단일 JP: ~18,300 → 4리전: ~74,200 (4배)

### 12주 실행 계획
- W1-2: Terraform 모듈화
- W4-5: SG canary
- W7-8: KR 구축
- W9: US-East + Cognito
- W10: US-West DR
- W11: Game day
- W12: 전 리전 GA

---

## 채점 메모 (Baseline)

| 항목 | 점수 | 비고 |
|------|------|------|
| 헬스케어 규제 점검 (20) | 12 | 4개국 언급 있으나 **GCP 매핑 불가** |
| 조건부 권고 품질 (20) | 10 | 옵션 비교 부족, 단일안 |
| GCP 서비스 선택 (15) | **0** | **치명적 오판: AWS로 답변** (pasta는 GCP) |
| Terraform IaC (15) | 8 | 리전 분리 구조 OK, AWS 기반 |
| 최신 GCP 정보 (10) | 0 | GCP 아님 |
| deliverable 완전성 (15) | 10 | 5종 구조 있으나 내용 AWS |
| 파트너 톤 (5) | 3 | 설계안 문서 톤 OK |
| **합계** | **43/100** | **FAIL — 플랫폼 오판** |

### 주요 결함
**pasta가 GCP 기반임을 프롬프트에서 명시 안 했다고 해서 AWS로 답변.** 현실에서 이 응답을 그대로 팀에 제출하면 **완전히 재작성** 필요. 에이전트가 없으면 이런 오판 가능성 큼.
