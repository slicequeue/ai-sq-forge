# ADR-003: 리전 배치 & 라우팅 — 기존(한·일) + 신규(미·싱) (v0.2 업데이트)

- **상태**: Proposed
- **작성일**: 2026-04-22 (v0.2 현황 기반 업데이트)
- **리뷰어**: 인프라팀 / 보안
- **관련**: ADR-002, ADR-004, ADR-011, ADR-012

---

## v0.2 변경

v0.1은 "일본 단일에서 4리전 신규 확장"이라는 전제였으나, Phase 1.5로 확인된 실제:
- **한국**(`asia-northeast3`, pasta) **이미 운영 중** (Cloud Run 29개)
- **일본**(`asia-northeast1`, pasta-jp) **이미 운영 중** (Cloud Run 19개)
- **미국**(prd-pasta-la) Deprecated — 신규 재구축 필요
- **싱가포르** — 진짜 신규

→ "신규 리전 추가"는 **미국·싱가포르 + 일본 오사카 DR** 3개만 해당.

---

## 컨텍스트

- 헬스케어 데이터 국경 이동 금지 (ADR-004)
- 사용자 지역별 latency 최적화
- SLA 목표 99.9~99.95%, RTO/RPO 분 단위
- 현행 한·일 운영 지장 없이 글로벌 확장

---

## 결정

### 리전 배치 최종

| 리전 | 코드 | 상태 | 비고 |
|------|------|------|------|
| 🇰🇷 서울 | `asia-northeast3` | **기존 운영 (pasta)** | 한국 사용자 계속 서비스 |
| 🇯🇵 도쿄 | `asia-northeast1` | **기존 운영 (pasta-jp)** | 일본 사용자 계속 서비스 |
| 🇯🇵 오사카 | `asia-northeast2` | **Phase 2 신규 (DR)** | 3省2ガイドライン 일본 내 이중화 |
| 🇺🇸 오레곤 | `us-west1` | **Phase 2 신규** | pasta-la 과거 자산 참고, HIPAA 2026 대응 |
| 🇸🇬 싱가포르 | `asia-southeast1` | **Phase 2 신규** | PDPA + HCSE + NRIC 미사용 인증 |

### 라우팅

- **Global Cloud Load Balancer + geo-routing**
- 사용자 지역 → 가장 가까운 리전
- 리전 간 데이터 공유 없음 (LB는 라우팅만)
- 단일 도메인 (`api.pasta.com`) 글로벌 진입점

### DR 전략

| 리전 | DR 방식 | RTO/RPO |
|------|---------|---------|
| 서울 | 동일 리전 zone HA + 리전 내 백업 | 30분 / 15분 (PITR 도입 후) |
| 도쿄 | zone HA + **오사카 cross-region 백업** (신규) | 30분 / 15분 (PITR 도입 후) |
| 오레곤 | zone HA + 동일 리전 백업 | 30분 / 15분 |
| 싱가포르 | zone HA + 동일 리전 백업 | 30분 / 15분 |

**주의**: 한국·싱가포르는 해당국 내 타 리전 없어 cross-region 백업 불가. Zone 이중화 + 짧은 snapshot 주기로 대체.

---

## 미국 리전 선택 근거

pasta-la(과거 미국 배포) 확인 불가. 따라서:
- **기본: `us-west1` (오레곤)** — 서부 사용자 latency + HIPAA 커버 + 비용
- **대안: `us-central1` (아이오와)** — 중앙, DR 후보
- **`us-east4` (버지니아)** — 동부 사용자 많으면 재평가

→ Phase 2 착수 시 **타겟 사용자 지역 분포 확인 후 확정** (재평가 트리거).

---

## 기존 한·일 리전 처리

- 현 Cloud Run 48개 서비스 유지 (이관 지연 없음)
- 글로벌 레포 완성 후 **Q1(ADR-011) 시나리오에 따라 통합/공존 결정**
- **ADR-012 완화책 4종 적용** (CMEK/PITR gap 완화)
- Phase 3에 CMEK/PITR 본격 도입 (데드라인)

---

## 결과

### 긍정적
- 기존 한·일 운영 지장 0 (점진 전환)
- 신규 리전 Day 1부터 베스트 프랙티스 (CMEK/PITR 디폴트 ON)
- 데이터 주권 준수

### 부정적 / 감수
- Global LB 단일 장애점 (DNS fallback 대비)
- 미국 리전 선택 Phase 2에서 재확인 필요
- 오사카 DR 비용 증가 (일본 내 이중화)

### 후속 작업

- [ ] Phase 1: Global LB·Cloud DNS 구성 (기존 엔드포인트 포함)
- [ ] Phase 2: 오사카 DR + 오레곤 + 싱가포르 신설 (순차)
- [ ] Phase 2: 미국 사용자 분포 조사 → 오레곤 vs 타 리전 확정
- [ ] Phase 3: 리전별 DR 훈련 (분기 1회)

---

## 리스크 & 완화

| 리스크 | 가능성 | 영향 | 완화 |
|--------|-------|------|------|
| Global LB 장애 | L | H | DNS fallback 2차 (Cloudflare 등) |
| 미국 리전 선택 오판 | M | M | Phase 2 초기에 사용자 분포 데이터 수집 |
| 한·일 기존 리전 DR 구성 변경 | M | M | 기존 운영 무중단 전환 (블루/그린) |

---

## 검증 포인트

- [ ] Phase 1: 기존 한·일 엔드포인트 Global LB 정합 (regression test)
- [ ] Phase 2: 도쿄 → 오사카 DR 30분 훈련
- [ ] Phase 2: 미·싱 P95 <100ms (지역 사용자)
- [ ] Phase 2: 4개국 데이터 silo 격리 통합 테스트

**재평가 시점**: Phase 2 종료 시 미국 리전 선택 재확인.

---

## 참고

- 에이전트 결정 프레임워크: `anvil/agents/gcp-infra-architect/references/decision-frameworks.md` §2
