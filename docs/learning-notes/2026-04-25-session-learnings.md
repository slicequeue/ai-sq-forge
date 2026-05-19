# 학습 노트 — 2026-04-25 세션

> 이번 세션(pasta 글로벌 확장 + gcp-infra-architect v1.2 구축)에서 관찰된 **직접 질문 / 암묵적 공백**을 학습 우선순위로 정리. 본인용 체크리스트.

---

## 🔴 긴급 — 이번 주 안 (업무 직결)

### 1. CMEK / PITR

**왜 긴급**: 현재 pasta DB에 둘 다 미적용. ADR-012로 Accepted Risk 기록했지만 감사 들어오면 방어해야 함.

- [ ] **CMEK 개념 이해** — Cloud KMS, 키 회전, 리전별 키, `encryption_key_name` 필드
- [ ] **PITR 개념 이해** — binary log 기반, `binary_log_enabled = true`, RPO 1초 vs 24시간 차이
- [ ] **침해 시나리오 상상** — "키 비활성화 → 즉시 봉쇄" 훈련 시뮬레이션

**자원**:
- [Cloud SQL CMEK 공식](https://cloud.google.com/sql/docs/mysql/configure-cmek)
- [Cloud SQL MySQL PITR](https://cloud.google.com/sql/docs/mysql/backup-recovery/pitr)
- [Cloud KMS 기초](https://cloud.google.com/kms/docs)

### 2. 4개국 헬스케어 규제 (암기 수준)

**왜 긴급**: 팀 미팅·경영진 질문 대응 시 본인이 바로 답해야. 에이전트 없이도 설명 가능 수준.

| 국가 | 핵심 포인트 | 마감·트리거 |
|------|------------|------------|
| 🇺🇸 HIPAA 2026 | BAA, CMEK, MFA, 72h 복구, 암호화 필수화 | 미국 진출 전 BAA 체결 |
| 🇰🇷 개보법 §28 | 국외이전 시 별도 동의, 의료정보 국내 저장 실무 표준 | 상시 |
| 🇯🇵 3省2 v2.0 | 위탁계약서 감사권 명시, 일본 내 저장 원칙 | 2025-03 발효 중 |
| 🇸🇬 NRIC 금지 | NRIC 인증 전면 금지 | **2026-12-31** |

**자원**: `anvil/agents/gcp-infra-architect/references/regulations/` 4개 파일

### 3. 우리 제품 라인업

**왜 긴급**: 글로벌 확장 설계 결정권자니까 조직 내 제품 지도 머릿속에 있어야.

```
prd-pasta      = 🇰🇷 한국 (asia-northeast3, Cloud Run 29개) ← 본체
prd-pasta-jp   = 🇯🇵 일본 (asia-northeast1, Cloud Run 19개) ← 본인 담당
prd-pasta-la   = ❌ Deprecated (과거 미국 LA)
prd-pasta-lilly = Eli Lilly B2B 평가용 (일본 리전)
```

- [ ] 조직에서 **"pasta 라인업 지도" 공식 문서** 있는지 확인. 없으면 정리해둘 가치
- [ ] 글로벌 레포 시나리오 Q1 — 팀 논의 현황 지속 팔로우

---

## 🟡 중요 — 이번 달 안 (설계 역량)

### 4. Cloud Run vs GKE 전환 임계점

- [ ] 유지 근거 / 전환 임계점 각각 체크리스트 암기 수준
- [ ] 우리 pasta 현 상태를 본인이 임계점에 직접 대입 가능해야
- [ ] GKE Autopilot vs Standard 차이 (Autopilot은 노드 관리 자동)

**자원**: `anvil/agents/gcp-infra-architect/references/decision-frameworks.md` §1

### 5. Regional Silo vs 멀티리전 DB

- [ ] Spanner 멀티리전이 자동 복제 → 헬스케어 데이터 주권 충돌한다는 점
- [ ] Regional Silo 패턴 (리전별 독립 스택)의 장단점
- [ ] 글로벌 분석은 **익명화 후 BigQuery 집계**가 표준 해법

### 6. Cloud Run DB 연결 안정화 (현 통증 해결책)

- [ ] **Managed Connection Pooling** (2026 GA) — GCP 네이티브
- [ ] **Auth Proxy Sidecar** — Cloud Run 사이드카 구성
- [ ] `min_instances >= 1` + CPU always allocated
- [ ] Hikari pool size 인스턴스당 작게 유지
- [ ] → **이거면 GKE 전환 없이도 현 통증 즉시 해결 가능**

---

## 🟢 도움됨 — 중장기 (전문성 누적)

### 7. GCP 보안 기본 스택 (헬스케어 디폴트)

| 도구 | 역할 | 실전 용도 |
|------|------|----------|
| Cloud KMS + CMEK | 키 자체 관리 | 모든 PHI 저장소 |
| VPC Service Controls | 프로젝트 경계 차단 | IAM 보완, 유출 방지 |
| Organization Policy | 리소스 위치 등 강제 | 거버넌스 차단막 |
| Workload Identity Federation | 서비스 계정 키 파일 대체 | CI/CD 전체 경로 |
| Cloud Audit Logs | 전 API 호출 기록 | 감사 대응 |
| Security Command Center | 이상 탐지·알림 | 운영 관측 |

### 8. Terraform 베스트 프랙티스

- 환경×리전 매트릭스 디렉토리
- GCS backend + CMEK + Versioning
- Workload Identity Federation (static key 금지)
- 모듈 variable `validation` 블록 활용

**자원**: `anvil/agents/gcp-infra-architect/references/terraform-patterns.md`

### 9. MySQL 8.0 운영 핵심 설정

```
availability_type = REGIONAL      # HA 필수
binary_log_enabled = true         # PITR 전제
point_in_time_recovery_enabled = true
require_ssl = true
deletion_protection = true
ipv4_enabled = false              # Private IP 전용
```

### 10. Forge 시스템 작동 원리

- **Deploy Registry**: 어떤 컴포넌트가 어느 프로젝트에 배포됐는지 + 버전 동기화 상태
- **하네스·루브릭·TC 3종**: 측정 가능한 품질 보증 구조
- **forge-deploy ↔ forge-upstream** 순환: 실전 개선 → 역수입 → 품질 검증 → 재배포
- **Phase 1.5 현황 파악**: 이번 본인 피드백으로 공식 원칙화됨 ✅

---

## 🔵 메타 — 일하는 방식 개선

### 본인이 이번 세션에서 잘한 것

1. **"갑자기 마이크로서비스 나오는 거 아냐?" 피드백** — Phase 1.5 원칙 탄생의 결정적 트리거
2. **"CMEK/PITR가 뭐임" 직접 질문** — 모르는 걸 인정하는 태도 (설계 품질 방어)
3. **"아직 논의 중이라 확답 어려워" (Q1)** — 확정 안 된 걸 확정됐다고 말 안 함 (신뢰도 유지)
4. **"Z 갈 수밖에 없는게 인프라랑 보안팀 협의 + 예산"** — 조직 현실 직시. 이상론 대신 실행 가능성

### 앞으로 강화하면 좋을 습관

1. **설계 논의 전 실제 현황 확인** — `gcloud`·레포 구조 먼저 보고 대화 시작
2. **규제 체크리스트 수동 점검 루틴** — 분기별로 4개국 규제 변동 체크 (특히 NRIC 2026.12.31 등 마감일)
3. **Deploy Registry 주기적 동기화 확인** — 구버전 실전 운영 상태 누적 방지
4. **에이전트 응답에 무조건 동의 X** — v0.1 설계안처럼 에이전트가 틀린 가정으로 쓸 수 있음. 본인 판단 유지

---

## 📖 읽을거리 우선순위

**이번 주 내**:
1. `anvil/agents/gcp-infra-architect/references/regulations/hipaa.md` — HIPAA 2026 개정
2. `anvil/agents/gcp-infra-architect/references/regulations/korea-pipa.md` — 개보법
3. [Cloud SQL CMEK](https://cloud.google.com/sql/docs/mysql/configure-cmek)
4. [Cloud SQL MySQL PITR](https://cloud.google.com/sql/docs/mysql/backup-recovery/pitr)

**이번 달 내**:
5. `anvil/agents/gcp-infra-architect/references/decision-frameworks.md` 전체
6. `anvil/agents/gcp-infra-architect/references/terraform-patterns.md`
7. `docs/infra-design/pasta-global-expansion-v0.1/` 전체 설계안

**여유 시**:
8. [GCP Architecture Center — Healthcare](https://cloud.google.com/architecture/healthcare)
9. [HashiCorp Terraform best practices](https://www.terraform.io/cloud-docs/best-practices)
10. [GKE Autopilot overview](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)

---

## 💡 마지막으로

이번 세션 회고는 **"부족함을 탓하는 것"이 아니라 "빠른 성장 지점 식별"** 목적입니다.

- 헬스케어 글로벌 인프라 설계는 **본인 혼자 감당 중인 영역** — 조직 내 유일한 연결점
- 에이전트가 보조해도 **최종 판단은 본인** → 개념 이해 깊이가 설계 신뢰도 좌우
- 규제 이슈는 **결정 번복 비용이 큼** (v0.1 재작성 사례처럼)

위 10개 중 **오늘 바로 5분 투자 가능한 것**부터 시작 권고:
→ CMEK / PITR / 4개국 규제 요약 — 3개만 읽으면 경영진 회의에서 바로 설명 가능한 수준 됨.
