# pasta 글로벌 확장 인프라 설계안 v0.3

- **작성일**: 2026-04-22 (v0.3 갱신: 2026-05-08)
- **작성**: slicequeue (+ `gcp-infra-architect v1.2` 에이전트 파트너)
- **상태**: **Draft (v0.3)** — 후속 결정 5건 반영
- **v0.2 → v0.3**: CMEK Deferred / 프로젝트 분할(Option B) / LB Pattern 2 / 작업 견적 / GKE 즉시 도입 검토

---

## 문서 구성

### 본문

| # | 파일 | 대상 독자 | 내용 |
|---|------|----------|------|
| 1 | [DESIGN.md](DESIGN.md) | 전 구성원 | 통합 설계안 (경영진 요약 + 다이어그램 + TF + 로드맵) |
| 2 | [CONTEXT.md](CONTEXT.md) | 설계 리뷰어 | Phase 1.5 gcloud 현황 파악 결과 + 실제 서비스·DB·보안 gap |
| 3 | **🆕 [ROADMAP-EFFORT.md](ROADMAP-EFFORT.md)** | 매니저 / 리더 | **작업 견적 (Realistic 12~14개월 / 9개월 MVP / 5개월 MVP-Lite) + Phase별 PW** |
| 4 | **🆕 [GKE-IMMEDIATE-ADOPTION.md](GKE-IMMEDIATE-ADOPTION.md)** | 인프라팀 / 매니저 | **GKE 즉시 도입 시나리오 분석 — 즉시 도입 비권고, 정당화 체크리스트 포함** |
| 5 | [SESSION-SUMMARY.md](SESSION-SUMMARY.md) | 인계자 | 세션 회고 + 배포 체크리스트 |

### ADR

| ADR | 주제 | 결정 | 상태 |
|-----|------|------|------|
| [001](adr/ADR-001-compute-strategy.md) | 컴퓨트 | Cloud Run 유지 + Phase 3 GKE 재평가 (즉시 도입 비권고) | Proposed |
| [002](adr/ADR-002-database-strategy.md) | DB | 리전별 Cloud SQL MySQL HA | Proposed |
| [003](adr/ADR-003-region-routing.md) | 리전 | 한+일 기존 + 미+싱 신규 + 오사카 DR | Proposed |
| [004](adr/ADR-004-data-residency.md) | 레지던시 | 민감정보 silo + 비민감 메타 공유 | Proposed |
| [005](adr/ADR-005-terraform-structure.md) | TF | green-field 신규 도입 + 2단계 매트릭스 (v0.3 보정 필요) | Proposed |
| [**006**](adr/ADR-006-cmek-key-management.md) | CMEK | 리전별 keyring + 목적별 key — **Deferred (Phase 3+)** | **Deferred (v0.3)** |
| [011](adr/ADR-011-global-repo-strategy.md) | 글로벌 레포 | 3시나리오 병기, 팀 논의 중 | Proposed |
| [**012**](adr/ADR-012-cmek-pitr-accepted-risk.md) | 수용 리스크 | **PITR만 데드라인 유지** (CMEK는 ADR-006 Deferred로 분리) | Accepted |
| [**🆕 013**](adr/ADR-013-project-partitioning-strategy.md) | **프로젝트 분할** | **Option B: 시장별 GCP 프로젝트 + 시장 내 멀티 리전** | Proposed |
| [**🆕 014**](adr/ADR-014-load-balancer-pattern.md) | **LB 패턴** | **Pattern 2 default: 시장별 LB + DNS geo-routing** | Proposed |

---

## 30초 요약 (v0.3)

| 결정 영역 | 권고 | 근거 |
|----------|------|------|
| 컴퓨트 | Cloud Run 유지 + Phase 3 하이브리드 재평가. **GKE 즉시 도입 비권고** | 1명+a 인력·일정 리스크 (GKE-IMMEDIATE-ADOPTION.md) |
| DB | 리전별 Cloud SQL MySQL HA (Spanner/Postgres ❌) | 현행 MySQL 8.0 기반 유지, 데이터 주권 |
| 리전 | 🇰🇷 서울 · 🇯🇵 도쿄+오사카(DR 신규) · 🇺🇸 오레곤 · 🇸🇬 싱가포르 | 기존 유지 + 신규 2곳 |
| **🆕 프로젝트 분할** | **Option B: 시장(국가)별 GCP 프로젝트 + 시장 내 멀티 리전** | 규제 = 프로젝트 경계, 현 패턴 연장 (ADR-013) |
| **🆕 LB 패턴** | **Pattern 2: 시장별 LB + DNS geo-routing** | 헬스케어 격리, 운영 단순, MVP 가속 (ADR-014) |
| IaC | Terraform green-field + `markets/{시장}/prd/{region}/` 2단계 | 현재 TF 미사용 |
| 보안 디폴트 | VPC SC + Audit Log + MFA + Org Policy + **PITR** (Day 1). **CMEK Deferred** | 헬스케어 + 5개월 MVP 가속 (ADR-006) |
| 글로벌 레포 | 3시나리오 병기 (a/b/c) — 공통 기반 먼저 설계 | 팀 논의 중 (ADR-011) |
| **🆕 작업 견적** | Realistic 12~14개월 / 9개월 MVP / 5개월 MVP-Lite (미국 only + 외주 1명) | 1명+a 인력 현실 (ROADMAP-EFFORT.md) |
| 일정 | 2026-04 → 12 (원안) / 12~14개월 (현실) | 데드라인 협상 필요 |

---

## v0.2 → v0.3 주요 변경

| 영역 | v0.2 | v0.3 |
|------|------|------|
| **CMEK** | 신규 리전 Day 1 ON / ADR-012 데드라인 | **Deferred** (ADR-006), Phase 3+ 적용. PITR만 데드라인 유지 |
| **프로젝트 분할** | 사실상 시장별이지만 미명시 | **Option B 명시 결정** (ADR-013 신설) |
| **LB 패턴** | "Global LB geo-routing" 추상 표기 | **Pattern 2 default** (ADR-014 신설) |
| **작업 견적·MVP** | Phase 일정만 | **Realistic 12~14개월 / 9개월 MVP / 5개월 MVP-Lite** (ROADMAP-EFFORT.md 신설) |
| **GKE 즉시 도입** | Phase 3 하이브리드 재평가 | 별도 분석 후 **즉시 도입 비권고** (GKE-IMMEDIATE-ADOPTION.md 신설) |
| **TF 디렉토리** | `environments/prd/{region}/` 단일 | `markets/{시장}/prd/{region}/` 2단계 |

---

## v0.1 → v0.2 주요 변경 (참조용)

| 영역 | v0.1 | v0.2 |
|------|------|------|
| 기본 전제 | "일본 단일 리전" | 한국(pasta) + 일본(pasta-jp) 기존 운영 |
| 서비스 규모 | 단일 API + 몇 개 워커 가정 | 48개 Cloud Run 이미 마이크로서비스화 |
| DB 엔진 | Cloud SQL Postgres 가정 | MySQL 8.0/8.4 전역 (확인됨) |
| Terraform | 기존 사용 가정 | 현재 미사용, 신규 도입 |
| 미국 리전 | 완전 신규 | prd-pasta-la 과거 자산 존재 |
| 보안 현황 | 언급 없음 | CMEK/PITR gap 확인 → ADR-012 신설 |
| 글로벌 레포 | 단일 가정 | 3시나리오 병기 → ADR-011 신설 |

---

## 읽는 순서

### 경영진·리더
1. `DESIGN.md` §1 경영진 요약
2. **`ROADMAP-EFFORT.md` §7 매니저 보고용 1줄** + §1 견적 시나리오
3. `ADR-011` 글로벌 레포 시나리오 (확정 필요)
4. `ADR-013` 프로젝트 분할 (확정 필요)

### 인프라·백엔드
1. `CONTEXT.md` 전체 (실제 현황)
2. `DESIGN.md` §2~§5
3. ADR-001/002/005/013/014 담당 영역
4. `GKE-IMMEDIATE-ADOPTION.md` (GKE 도입 검토 시)

### 보안·법무
1. `DESIGN.md` §1, §2
2. ADR-004 (데이터 레지던시)
3. ADR-013 (프로젝트 = 규제 경계)
4. ADR-012 (PITR 수용 리스크)
5. ADR-006 (CMEK Deferred 사유)

### 매니저·일정 담당
1. `ROADMAP-EFFORT.md` 전체
2. `GKE-IMMEDIATE-ADOPTION.md` §4 작업 분해, §5 일정 영향
3. `DESIGN.md` §5 Phase 로드맵

---

## 다음 단계

1. **데드라인 확정** — 5개월 vs 9개월 vs 12~14개월 (사업 약속 vs 내부 목표 명확화)
2. **Q1 확정** (글로벌 레포 시나리오) — 팀 논의 완료 후 ADR-011 시나리오 1개 확정
3. **ADR-013 확정** — 일본 3省2 위탁사업자 분리 요구 법무 컨펌
4. **ADR-014 확정** — 사업·마케팅팀과 도메인 전략 합의
5. **외주 GCP 파트너 섭외** (5개월 MVP-Lite 채택 시 필수)
6. **Phase 0 착수** — 미국 HIPAA BAA 신청 (W1 Day 1)
7. **팀 리뷰** — v0.3 전달, 피드백 수렴 → v0.4

---

## 재생성·갱신 방법

`anvil/agents/gcp-infra-architect v1.2`와의 대화로 작성. 갱신은:
- 에이전트 호출 (`@gcp-infra-architect 갱신하자`)
- 피드백·확정은 `CONTEXT.md`에 먼저 반영
- 결정 변경 시 기존 ADR을 **Superseded** 처리 + 새 번호로 신설
