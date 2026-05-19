# TC-3 Baseline — Terraform 구조

**메타**: 토큰 19,854 / 83.7s / tool 0회 / agentId a40761da22e32d98e

---

## 응답 원문 (요약)

# 헬스케어 서비스 4리전 Terraform 배포 설계

### 전제 가정
- **클라우드: AWS 기준** (GCP/Azure도 구조 동형)
- 리전: `ap-northeast-2`(KR), `ap-northeast-1`(JP), `us-east-1`(US), `eu-west-1`(EU)

### 디렉토리 구조
```
infra/
├── modules/
│   ├── network/, eks/, rds-aurora/, s3-phi-bucket/
│   ├── kms-regional/, iam-baseline/
├── global/
│   ├── iam/, dns/ (Route53), cloudfront/
│   ├── kms-mrk/ (Multi-Region Key)
│   └── audit/ (CloudTrail)
├── envs/
│   ├── dev/{ap-northeast-2, ap-northeast-1, us-east-1, eu-west-1}/
│   ├── stg/
│   └── prod/
└── bootstrap/
```

### State 전략
- S3 + DynamoDB 락
- 리전별 state 버킷, CMEK 암호화
- Object Lock(Compliance) 7년
- workspace 사용 금지 (디렉토리 분리)

### Provider alias
- 리전 루트: 주 provider 1개만
- 글로벌 스택에서만 alias 사용 (CloudFront/ACM us-east-1)

### 보안 기본값
- **KMS CMK per region**, MRK로 PHI 키 공유
- VPC Endpoint, Security Group 최소권한
- **WAF + Shield Advanced**
- IAM: IAM User 금지, OIDC + SSO
- CloudTrail + Config + GuardDuty + Macie + Security Hub
- tfsec + checkov + OPA 게이트

### 트레이드오프
- 환경×리전 분리 (권장) vs Terragrunt vs 단일 state

### 다음 질문
1. 클라우드가 AWS 맞나?
2. active-active vs standby?
3. EU 데이터 EU 밖 가능한가?

---

## 채점 메모 (Baseline)

| 항목 | 점수 | 비고 |
|------|------|------|
| 헬스케어 규제 점검 (20) | 10 | HIPAA만 일반론, GCP 매핑 불가 |
| 조건부 권고 품질 (20) | 12 | 옵션 비교는 있음 |
| GCP 서비스 선택 (15) | **0** | **AWS로 답변** (EKS·RDS·S3·Route53) |
| Terraform IaC (15) | 10 | 구조 자체는 탄탄 (디렉토리, state, bootstrap) |
| 최신 GCP 정보 (10) | 3 | GCP 아님 |
| deliverable 완전성 (15) | 10 | 설계 구조 괜찮음 |
| 파트너 톤 (5) | 3 | 마지막 5개 질문은 좋음 |
| **합계** | **48/100** | **FAIL — 또 AWS** |

### 주요 결함
"헬스케어 4리전 Terraform"이라는 중립적 키워드에서 **다시 AWS로 튐**. "클라우드가 AWS 맞나?"라고 마지막에 역질문하는 것은 긍정적이지만, 본문은 이미 AWS 전제로 상세히 작성됨.
