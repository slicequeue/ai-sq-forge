# 설계 컨텍스트 & 실제 현황 (v0.2)

> **v0.2 변경**: v0.1의 "가정 10개"를 Phase 1.5 gcloud 현황 파악으로 **확인된 사실로 승격**. 실제 pasta 상태가 크게 달랐음.

- **작성일**: 2026-04-22
- **현황 파악 방식**: `gcp-infra-architect v1.1` 에이전트의 Phase 1.5 프로토콜 (gcloud 읽기 명령)

---

## 1. 실제 프로젝트 매트릭스 (확인됨)

| 제품 | dev | stg | prd | 용도 | 리전 |
|------|-----|-----|-----|------|------|
| **pasta** (한국, 본체) | dev-pasta | stg-pasta | **prd-pasta** | 한국 사용자 서비스 (운영 중) | `asia-northeast3` (서울) |
| **pasta-jp** (일본) | dev-pasta-jp | stg-pasta-jp | **prd-pasta-jp** | 일본 사용자 서비스 (운영 중) | `asia-northeast1` (도쿄) |
| **pasta-la** (Deprecated) | - | - | prd-pasta-la | 예전 미국 LA 배포, **현재 미사용** | - |
| **pasta-lilly** (B2B) | dev-pasta-lilly-461907 | - | prd-pasta-lilly | 릴리(Eli Lilly) 평가용, 일본 리전 배포 | `asia-northeast1` |

### 시사점
- **"일본 단일 리전" 전제는 틀렸음** — 한국(pasta) + 일본(pasta-jp)가 이미 **독립 레포로 운영 중**
- 한국 pasta가 실질적 본체 규모 (서비스 수 많음)
- pasta-la는 되살릴 수 있는 과거 자산 (미국 진출 시 참고)
- pasta-lilly는 B2B 별도 트랙 — 이 설계안 스코프 외

---

## 2. Cloud Run 서비스 현황 (확인됨)

### prd-pasta (한국, `asia-northeast3`) — **29개 서비스**

대표 카테고리:
- 본체 API: `run-prd-pasta-api`, `run-prd-pasta-admin`, `run-prd-pasta-webview`, `run-prd-pasta-chart`, `run-prd-pasta-dashboard`, `run-prd-pasta-chatbot`, `run-prd-pasta-chatbot-api`
- AIX 시리즈: `run-prd-aix-nudge-worker`, `run-prd-aix-report-api`, `run-prd-aix-report-worker`, `run-prd-aix-sleep-analysis-api`
- Agent (일부 실패 상태): `run-prd-pasta-agent-api-answer/builder/chat`, `run-prd-pasta-agent-batch/engine/front-builder`
- 이벤트/배치: `run-prd-pasta-event`, `run-prd-pasta-event-worker`
- 기능별: `run-prd-pasta-fhir-api`, `run-prd-pasta-foodscan`, `run-prd-pasta-pdf-generator`, `run-prd-pasta-user-info-export`, `run-prd-pasta-ad-api`, `run-prd-pasta-pass`
- PoC: `run-prd-pasta-api-poc`, `run-prd-pasta-zero-api`
- 공통: `run-prd-metabase`, `run-prd-notification-api`

### prd-pasta-jp (일본, `asia-northeast1`) — **19개 서비스**

대표 카테고리:
- 본체 API: `run-prd-pasta-jp-api`, `run-prd-pasta-jp-admin`, `run-prd-pasta-jp-webview`, `run-prd-pasta-jp-chart`, `run-prd-pasta-jp-dashboard`
- Chatbot·Token: `run-prd-pasta-jp-chatbot-api`, `run-prd-pasta-jp-token`
- AIX: `run-prd-aix-agent-api-jp`, `run-prd-aix-nudge-worker-jp`, `run-prd-aix-report-api-jp`, `run-prd-aix-report-worker-jp`
- Notification: `run-prd-pasta-jp-notification-api`, `run-prd-notification-jp-api`, `run-prd-notification-lilly-api`
- 이벤트/분석: `run-prd-pasta-jp-event-worker`, `run-prd-pasta-jp-metabase`
- Cloud Functions(이미지): `fn-prd-pasta-jp-resizing`, `fn-prd-pasta-jp-thumbnail`, `fn-prd-pasta-lilly-resizing`

### 시사점
- **48개 서비스(한+일) 이미 마이크로서비스 구조**
- v0.1 가정인 "단일 API + 몇 개 워커" 완전히 틀림
- 글로벌 레포 통합 시 **이 48개 대응 범위 정의**가 중심 과제

---

## 3. 데이터베이스 현황 (확인됨)

### prd-pasta (한국)
| 인스턴스 | 엔진 | 위치 | 용도 |
|---------|------|------|------|
| sql-prd-pasta-app | MYSQL 8.0 | asia-northeast3-a | 주 DB |
| sql-prd-pasta-app-replica | MYSQL 8.0.31 | asia-northeast3-a | Read replica |
| sql-prd-pasta-body-ai-app | MYSQL 8.0.41 | asia-northeast3-c | AI 전용 DB |
| sql-prd-pasta-app-clone-20260313 | MYSQL 8.0 | asia-northeast3-a | 마이그레이션 클론 (2026-03-13) |

### prd-pasta-jp (일본)
| 인스턴스 | 엔진 | 위치 | 용도 |
|---------|------|------|------|
| sql-prd-pasta-jp-app | MYSQL 8.0 | asia-northeast1-c | 주 DB |
| sql-prd-pasta-jp-app-replica | MYSQL 8.0.31 | asia-northeast1-c | Read replica |
| sql-prd-pasta-jp-body-ai-app | MYSQL 8.4 | asia-northeast1-b | AI 전용 DB |
| sql-prd-pasta-lilly-app | MYSQL 8.0.31 | asia-northeast1-b | Lilly B2B DB |

### 시사점
- **DB 엔진 = MySQL 전역** (v0.1에서 Postgres로 가정한 것 오류)
- **AI 전용 DB(body-ai) 별도 분리** 이미 운영 중 (AI 워크로드 분리 설계 참고)
- 한국·일본 둘 다 primary + replica 구조 (리전 내 HA)

---

## 4. 보안 gap (확인됨) ⚠️

### prd-pasta-jp 주 DB 설정 (gcloud describe 확인)

| 항목 | 현재 상태 | 기준 (헬스케어) | 판정 |
|------|----------|----------------|------|
| backup enabled | True | 필수 | ✅ |
| **PITR enabled** | **False** | 필수 (HIPAA 2026) | ❌ |
| Private IP only | True | 권장 | ✅ |
| require SSL | 미확인 | 필수 | ⚠️ |
| **CMEK (kmsKeyName)** | **미적용** (Google 기본 암호화만) | 필수 | ❌ |
| HA (availabilityType) | REGIONAL | 권장 | ✅ |

### Environment 태그 미적용
- `prd-pasta-jp` 프로젝트에 `environment` 태그 없음 (gcloud 경고)
- Organization governance gap

### 처리 방향 (v0.3 갱신) — **ADR-012 + ADR-006 참조**

**PITR (ADR-012)** — 데드라인 유지:
- Accepted Risk로 기록
- 완화책 4종 즉시 적용 (Audit Log 전체, 백업 6h, IAM 최소화, SCC 알림)
- 글로벌 레포 마이그레이션 시점에 **필수 해결** (데드라인 조건)

**CMEK (ADR-006)** — v0.3에서 **Deferred 처리**:
- 향후 Phase(Phase 3+) 적용 대상으로 분리
- HIPAA는 encryption-at-rest를 요구하나 CMEK 강제 X — Google-managed encryption도 HIPAA-compliant
- 단기 5개월 MVP-Lite 스코프에서는 Google-managed 기본 암호화로 시작
- 신규 리전(미·싱) Day 1 정책도 "Day 1 CMEK ON" → "Day 1 PITR ON, CMEK는 향후"로 변경
- 법무·감사 요구로 강제 트리거 발생 시 즉시 Active 격상

---

## 5. Terraform 현황 (확인됨)

- `pasta-japan-server` 레포 내 `*.tf` 파일 **0건**
- 별도 IaC 레포도 **없음** (사용자 확인)
- 현재 48개 서비스가 수동 배포 or CI/CD 스크립트 기반으로 추정
- → **글로벌 통합 레포에서 처음부터 Terraform 도입** (green-field)

### 시사점
- 기존 운영의 TF import는 **선택적** (의미 있는 리소스만)
- v0.1이 "기존 TF 있음"이라 가정한 것 오류

---

## 6. 글로벌 레포 전략 — **Proposed (논의 중)**

사용자 답변: "글로벌 버전 하나 더 나와서 리포 기준 진행할 것으로 판단, 아직 논의 중".

→ **ADR-011에 3가지 시나리오 병기**하고 팀 확정 대기:

| 시나리오 | 설명 |
|---------|------|
| (a) 한국 레포 진화 | pasta 한국 레포가 글로벌 레포로 진화, 리전별 배포 |
| (b) 신규 레포 | `pasta-global` 완전 신규, 기존 레포 점진 이관 |
| (c) 공존 | 한·일 기존 유지, 신규 시장만 새 레포 |

**v0.2 방침**: 3가지 모두 수용 가능한 **공통 기반**(리전 silo / CMEK / Terraform 모듈 / 규제)을 먼저 설계. 시나리오 확정 시 해당 부분만 활성화.

---

## 7. 트래픽·SLA·팀 (사용자 답변 그대로)

| 항목 | 값 |
|------|-----|
| 현재 peak RPS (일본) | 수십 |
| 예상 글로벌 peak | 수백 |
| SLA | 99.9~99.95% |
| RTO / RPO | 분 단위 허용 |
| 글로벌 담당 | slicequeue 1명 (+ 코어팀 3인 필요 시) |
| K8s 경험 | 담당자 부족 / 인프라팀 K8s 책임자+실무자 보유 |
| 온콜 | 내부 순번제 |
| 일정 | 2026-12월까지 |
| 예산 | 억 단위 |

---

## 8. 현 Cloud Run 통증 (사용자 답변)

> "AWS ECS처럼 안정적이지 않은 느낌. DB 연결 이슈 반복. 유지보수 작업 이유로 방치된 사례 누적."

### 추정 원인 (2026 기준)
- Cold start + connection pool 충돌
- Cloud Run ↔ Cloud SQL 연결 패턴이 최신 권장(Auth Proxy sidecar, Managed Pooling)이 아닐 가능성

### 해결 경로
- 글로벌 레포 마이그 시점에 Managed Connection Pooling + Auth Proxy sidecar + min_instances=1 반영
- 기존 운영은 ADR-012 완화책 범위

---

## 9. 이 설계안에서 **다루지 않은 영역**

의도적 범위 밖 (별도 설계 필요):
- pasta-lilly B2B 트랙
- AIX(AI 추론) 서비스의 리전 전략 (Vertex AI 연동)
- DNS/도메인 관리
- 정책·고지 텍스트 (국외 이전 동의, Privacy Policy 4개국)
- 고객 지원·시차·언어
- 로그 분석/BI 파이프라인
- CDN 전략
- 결제 시스템 (리전별 PG, 정산)
- 글로벌 레포와 기존 레포 간 **DB 스키마 동기화 전략** (별도 ADR 후보)

---

## 10. 재검토 트리거 (업데이트)

| 트리거 | 영향 |
|--------|------|
| Q1 (글로벌 레포 전략) 확정 | ADR-011 시나리오 확정, v0.3 |
| CMEK/PITR 완화책 실행 여부 | ADR-012 업데이트 |
| Kafka 도입 확정 | ADR-001 Phase 3 앞당김 |
| 트래픽이 예상(수백 RPS)의 5배 초과 | ADR-001, ADR-002 |
| 한국 개보법 개정 | ADR-004 |
| 미국 HIPAA BAA 승인 지연 | ADR-003 (미국 리전 Phase 재배치) |
| 인프라팀 K8s 인력 변동 (감소) | ADR-001 Phase 3 전략 수정 |

---

## 변경 이력

- **v0.1 (2026-04-22 Draft)**: 가정 10개 기반 초안 (에이전트 v1.0)
- **v0.2 (2026-04-22)**: Phase 1.5 gcloud 현황 파악 반영 (에이전트 v1.1) — 가정 → 확인된 사실로 승격, 실제 프로젝트·서비스·DB 구조 재정립
- **v0.3 (2026-05-08)**: 후속 결정 반영 — (a) **CMEK Deferred** 처리 (ADR-006), (b) **프로젝트 분할** Option B 채택 (ADR-013 신설), (c) **LB 패턴** Pattern 2 default (ADR-014 신설), (d) **작업 견적·MVP-Lite** 추가 (ROADMAP-EFFORT.md), (e) **GKE 즉시 도입 시나리오** 검토 추가 (GKE-IMMEDIATE-ADOPTION.md, 비권고)
