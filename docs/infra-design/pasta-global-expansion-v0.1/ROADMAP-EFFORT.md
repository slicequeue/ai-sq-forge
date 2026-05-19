# pasta 글로벌 확장 — 작업 견적 & 로드맵

- **작성일**: 2026-05-08
- **버전**: v0.3 (신설)
- **작성**: slicequeue (+ `gcp-infra-architect v1.2` 에이전트 파트너)
- **관련**: [DESIGN.md](DESIGN.md), [CONTEXT.md](CONTEXT.md), [adr/](adr/)

---

## 0. TL;DR

> **1명+코어팀 부분 지원으로 4개국(한·일·미·싱) 9개월 완수는 risky. Realistic은 12~14개월. 5개월 데드라인이 고정이면 미국 only MVP-Lite + 외주 1명이 거의 유일한 길.**

---

## 1. 견적 시나리오 3종

| 시나리오 | 인력 가정 | 총 PW | 캘린더 | 비고 |
|---------|----------|-------|--------|------|
| **Best** | slicequeue 풀타임 + 코어 3인 50% + 인프라 30% | 60 PW | **9개월** | DESIGN.md 원안. BAA·Q1·휴가 무사고 가정 |
| **Realistic** | slicequeue 풀타임 + 코어 20~30% + 인프라 단발성 | 75~85 PW | **12~14개월** | BAA 2~3개월 지연, Q1 합의 1개월 슬립 반영 |
| **Worst** | slicequeue 70% 겸직 + 산발 지원 | 100+ PW | **18개월+** | 사고 1회 + 담당자 공백 1개월 |

> **함정**: slicequeue는 8년차 BE이지 인프라 전담 X. 실제 가용 = **주 3~3.5일(60~70%)**. 반영하면 Realistic은 사실상 **14개월**에 가까움.

---

## 2. Phase별 Person-Week 분해

### Phase 0 — 완화책 + BAA + Q1 (8 PW, 6~10주)

| 항목 | PW | 직렬/병렬 |
|---|---|---|
| Cloud Run 안정성 완화책 (연결풀·헬스체크·DB) | 3 | 병렬 (인프라팀 협업) |
| BAA 신청·법무 검토·서명 | 2 (+대기시간) | **외부 의존, 직렬** |
| Q1 글로벌 레포 시나리오 합의·ADR-011 확정 | 2 | 조직 정치, 직렬 |
| ADR-012/013/014 정리 + ADR-006 Deferred | 1 | 병렬 |

### Phase 1 — 공통 기반 (21 PW)

| 항목 | PW |
|---|---|
| Terraform green-field 학습 + 모듈 설계 | 4 |
| 공통 모듈 (VPC/IAM/Secret/Logging) 작성·리뷰 | 6 |
| state 백엔드·환경 매트릭스·CI 통합 | 3 |
| 한+일 기존 환경 import (48개 서비스) | 5 |
| 모니터링·SLO 베이스라인 | 3 |

### Phase 2 — 리전 확장 (21 PW)

| 항목 | PW |
|---|---|
| 미국 리전(`us-west1`) 구축 + HIPAA 컨트롤 | 8 |
| 싱가포르(`asia-southeast1`) 구축 + PDPA | 5 |
| 멀티리전 LB Pattern 2 + DNS geo-routing | 4 |
| 데이터 레지던시 검증 + dry-run 감사 | 4 |

### Phase 3 — 통합·최적화 (14 PW)

| 항목 | PW |
|---|---|
| PITR 적용 (ADR-012 해소) | 3 |
| 비용 최적화·Committed Use·관측 튜닝 | 4 |
| 4개국 감사 dry-run + 운영 핸드오버 문서 | 4 |
| CMEK 도입 (ADR-006, 시간 여유 시) | 2 |
| 회고·차기 로드맵 | 1 |

**합계 ~64 PW**. 가용률 60% 1인 환산 시 **107주 = 25개월**. 코어팀·인프라팀 부분 지원으로 절반 흡수해야 12~14개월에 들어옴.

---

## 3. 크리티컬 패스 (일정 지배 요인)

1. **HIPAA BAA 신청·승인** — 외부 통제 불가. 통상 **6~10주**. 늦으면 Phase 2-미국이 통째로 밀림
2. **Q1 글로벌 레포 합의 (ADR-011)** — 조직 정치. 미확정 상태로 Phase 1 시작하면 후반 재작업
3. **Terraform green-field 학습 곡선** — 0건 시작. 1인 단독 위험. **인프라팀 페어 1~2주** 필수
4. **4개국 dry-run** — Phase 3 막판에 몰면 폭발. Phase 2 중 점진 감사 권고

---

## 4. 5개월 MVP-Lite (압축 시나리오)

### TL;DR

> "5개월에 미국 only + 외주 1명이면 가능. BAA 8주 가정 깨지면 6개월로 슬립. 4개국 전부는 5개월에 불가능."

### 가능성 평가

| 스코프 | 5개월 가능성 |
|---|---|
| 4개국 전부 | **불가능** |
| 미국 only + 한+일 import 후순위 | **빠듯, 조건부 가능** |
| 미국 only + 한+일 그대로 + 싱 후순위 | **중간 난이도** (가장 현실적) |

핵심 병목 = **HIPAA BAA 6~10주**. 20주의 30~50%가 외부 통제 영역.

### Aggressive 시나리오 (미국 only MVP-Lite) ⭐

- **스코프**: 미국 1개국 + 한+일 import는 Phase 2로 분리 + 싱가포르는 2027 H1
- **인력**: slicequeue 풀타임 + 코어 50% + 인프라 50% + **외부 GCP 파트너 컨설턴트 1명(8주)**
- **희생**: 한+일 기존 인프라 import, Q1 합의(임시 별도 레포로 시작), 일본 오사카 DR, 싱가포르 전체, CMEK
- **타임라인** (19~20주):
  - W1~2: BAA 신청 + 외주 온보딩 + ADR 핵심 3건
  - W3~10: TF 공통 모듈 + 미국 리전 + HIPAA 컨트롤 (병렬)
  - W11~16: LB Pattern 2 + 감사로그 + dry-run
  - W17~20: 부하·보안·DR 검증 + cutover
- **리스크**: BAA 10주 시 → 24주 슬립

### 잘라낼 것

**필수 컷**:
- 싱가포르 전체 → 2027 H1
- 일본 오사카 DR → Phase 2
- 한+일 기존 TF import → Phase 2 (현행 유지, 신규만 TF)
- Q1 글로벌 레포 합의 → 임시 별도 레포로 시작
- **CMEK 적용** → ADR-006(Deferred), Phase 3+

**선택 컷**:
- 미국 active-active → single-region + 백업
- 자동화 dry-run 4개국 → 미국 1개국만

**추가해야 할 것**:
- **외부 GCP 파트너 컨설턴트 1명 (8주, HIPAA·TF 경험자)** — 학습곡선 단축의 핵심
- BAA 신청 **W1 Day 1**

### MVP-Lite 산출물 (5개월)

**포함**:
- 미국 리전(`us-west1`) Cloud Run 1환경
- HIPAA 컨트롤 (BAA·감사로그·MFA·백업·SSL/TLS encryption-in-transit) 디폴트 ON
- TF 공통 모듈 v1 (network·iam·logging) — 미국용으로 검증
- Cloud SQL HA + **PITR** + 백업 복원 dry-run 1회
- LB Pattern 2 + Cloud Armor 기본

**제외**:
- 싱가포르, 일본 DR, Q1 글로벌 레포, 한+일 import, 멀티리전 active-active, 자동화 데이터 레지던시, **CMEK**
- 한+일은 **현행 그대로 운영**, 새 TF 적용 X

---

## 5. 인력 옵션 비교

| 옵션 | 단축 효과 | 비용 | 실현성 |
|---|---|---|---|
| **GCP 파트너 외주 1명 8주** | -4~6주 | 중 | **권고** |
| 인프라팀 풀타임 차출 | -2~3주 | 무 | 조직 협의 |
| 코어 3인 풀타임 차출 | -3~4주 | 무 | 본업 영향 큼 |
| **외주 + 인프라 둘 다** | -6~8주 | 중 | **5개월 진입의 거의 유일한 길** |

→ 외주 없이 5개월은 비현실적. **외주 1명은 타협이 아니라 필수 조건**.

---

## 6. 리스크별 일정 영향

| 리스크 | 일정 영향 | 완화 |
|---|---|---|
| BAA 지연 (10주+) | Phase 2-US **+4~6주** | Phase 0 1주차 즉시 신청 |
| Q1 미확정 지속 | Phase 1 재작업 **+2~3주** | Phase 0 데드라인 강제 (2026-05-31) |
| 담당자 휴가/이직 1개월 | 전체 **+4~6주** (SPOF) | 코어 1인 백업 공식 지정 |
| Cloud Run 사고 1회 | **+3~4주** | Phase 0 완화책 최상위 우선순위 |

---

## 7. 매니저 보고용 1줄

> **"1명+부분 지원으로 4개국 9개월은 risky. 현실적 12~14개월. 9개월 데드라인이 고정이면 미국 우선 MVP-Lite로 좁히고 싱가포르는 2027 H1로 분리 권고. 5개월 데드라인이면 미국 only + 외주 1명 + CMEK 향후 적용 조건이면 가능, 단 BAA 8주 가정 깨지면 6개월로 슬립."**

### 즉시 결정 사항 (사용자·매니저)

1. **5개월 vs 9개월 vs 12~14개월** 중 데드라인 확정
2. **외주 GCP 파트너 섭외 가능 여부 + 예산**
3. **코어팀 1명 백업 담당 공식 지정** (SPOF 해소)
4. **BAA 신청 Phase 0 1주차 착수 승인**
5. **Q1 데드라인 2026-05-31 못박기** (안 되면 MVP-Lite 자동 전환)

---

## 8. 확인된 것 vs 가정한 것

### 확인된 것

- 인력: slicequeue 1명 + 코어 3인 부분 지원 + 인프라 K8s 보유 (CONTEXT.md §7)
- 운영: Cloud Run 한+일 48개 서비스, Terraform 0건
- 통증: Cloud Run 안정성, PITR 미적용
- 미확정: Q1 (ADR-011)
- BAA 6~10주 외부 의존 (GCP 공식 절차)

### 가정한 것 (재평가 트리거)

- slicequeue 가용률 **60~70%** (겸직 추정) → 실제 가용률 확정 시 재계산
- 코어팀 지원율 **20~50%** → 분기별 capacity 협의
- BAA 통상 승인 **6~10주** → GCP 영업 채널 실측치 확보 시 갱신
- 인프라팀 페어 지원 **1~2주** → 합의 필요
- Phase별 PW ±30% 오차 (green-field TF·외부 의존 영향)
- 외부 GCP 파트너 섭외 가능성·예산 → **확인 필요**
- 5개월 데드라인 출처 (사업 약속 vs 내부 목표) → **사용자만 알 수 있음**

---

## 9. 재평가 시점

| 트리거 | 영향 |
|--------|------|
| 데드라인 확정 (5/9/12+개월) | 시나리오 선택 |
| 외주 섭외 결과 | 압축 가능성 |
| BAA 4주차 진행 | 일정 슬립 조기 감지 |
| Q1 2026-05-31 미확정 | MVP-Lite 자동 전환 |
| 가용률·코어팀 capacity 확정 | ±2개월 정밀도 재산출 |

---

## 참고

- [DESIGN.md](DESIGN.md) §1 경영진 요약, §5 Phase 로드맵
- [adr/ADR-011-global-repo-strategy.md](adr/ADR-011-global-repo-strategy.md) — Q1 시나리오
- [adr/ADR-012-cmek-pitr-accepted-risk.md](adr/ADR-012-cmek-pitr-accepted-risk.md) — PITR 데드라인
- [adr/ADR-006-cmek-key-management.md](adr/ADR-006-cmek-key-management.md) — CMEK Deferred
- [adr/ADR-013-project-partitioning-strategy.md](adr/ADR-013-project-partitioning-strategy.md) — Option B
- [adr/ADR-014-load-balancer-pattern.md](adr/ADR-014-load-balancer-pattern.md) — Pattern 2
- [GKE-IMMEDIATE-ADOPTION.md](GKE-IMMEDIATE-ADOPTION.md) — GKE 즉시 도입 시나리오 (대안)
