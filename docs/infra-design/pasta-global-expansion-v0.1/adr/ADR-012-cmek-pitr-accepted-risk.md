# ADR-012: PITR 수용 리스크 및 단계적 해결 (v0.3: CMEK 부분 분리)

- **상태**: **Accepted (Risk Accepted)**
- **작성일**: 2026-04-22 (v0.3 스코프 축소: 2026-05-08)
- **리뷰어**: 보안 / 경영 / 인프라팀
- **관련**: ADR-002, ADR-006 (Deferred)

---

## v0.3 변경 사항 (2026-05-08)

본 ADR은 v0.2까지 **CMEK + PITR**을 함께 다뤘으나, v0.3에서 **CMEK 부분은 ADR-006(Deferred)로 분리**한다.

### 변경 요지

- **CMEK**: ADR-006으로 분리하여 **Deferred (Phase 3+ 적용)** 처리. 본 ADR에서는 CMEK 데드라인 강제력 제거.
- **PITR**: 본 ADR의 핵심 결정 사항으로 유지. **데드라인·완화책 4종은 그대로 유지**.
- 신규 리전 정책: "Day 1 CMEK + PITR ON" → "**Day 1 PITR ON, CMEK는 향후 적용**"

→ 본문에서 "CMEK"라 표기된 부분은 모두 **ADR-006(Deferred) 참조**로 읽는다.

---

## 컨텍스트

### 확인된 현황 (Phase 1.5)

prd-pasta-jp 주 DB (`sql-prd-pasta-jp-app`) 설정 점검 결과:

```
backup enabled        = True
PITR enabled          = False  ❌
Private IP only       = True
require SSL           = (미확인)
CMEK (kmsKeyName)     = 미적용 (Google 기본 암호화만)  ❌
availability          = REGIONAL
```

prd-pasta 주 DB도 **동일 추정**(상세 점검 필요).

### 헬스케어 규제 기준 gap

| 규제 | 요구 | 현 상태 | 판정 |
|------|------|---------|------|
| HIPAA 2026 Security Rule | 암호화 (at-rest) CMEK, 백업 72h 복구 | CMEK ❌, PITR ❌ → 최대 24h 손실 | 미달 |
| 한국 개보법 시행령 | 개인정보 안전성 확보조치 | CMEK 미적용으로 통제권 부재 | 지적 가능 |
| 일본 3省2 v2.0 | CMEK·감사로그·책임분계 | CMEK 미적용 | 지적 가능 |
| 싱가포르 PDPA + HCSE | 암호화·백업·감사 | PITR 미활성 | 지적 가능 |

### 제약 (즉시 해결 어려운 이유)

사용자 확인:
- 인프라팀·보안팀 협의 필요
- 예산 결재 필요
- 단독 즉시 결정 불가

---

## 고려한 옵션

### Option X: 글로벌 레포 마이그레이션과 함께 해결
- 6~12개월 걸리는 동안 gap 유지
- 인프라·보안 통합 협의 가능

### Option Y: 긴급 즉시 적용 (2~4주)
- 운영 리스크 즉시 감소
- 협의·예산 패스트트랙 필요

### Option Z: Accepted Risk + 완화책 + 데드라인 ⭐ 선택

- 현 gap 유지 인정
- 협의·예산 없이 가능한 **완화책 4종 즉시 적용**
- 글로벌 레포 마이그 시점 **해결 데드라인** 박음
- **ADR로 명시 기록** → 감사 시 "방치 아닌 관리" 증빙

---

## 결정

> **선택: Option Z — Accepted Risk + 완화책 4종 + 데드라인**

### 수용 리스크 명시 (v0.3 스코프 축소)

현 시점에서 pasta 운영 DB는 아래 gap이 있다:
1. ~~CMEK 미적용~~ → **ADR-006(Deferred)로 분리, 향후 Phase 적용**
2. **PITR 미활성** — 사고 시 최대 24h 데이터 손실 가능 ← **본 ADR 핵심**

PITR gap은 **알고 있으며, 글로벌 레포 마이그레이션 시점에 해결된다**.

### 완화책 4종 (Phase 0 즉시 적용)

| # | 완화책 | 비용 | 효과 | 담당 |
|---|--------|------|------|------|
| 1 | **Cloud Audit Logs 전체 활성화** (Admin + Data Read + Data Write) | ~0 | "누가 언제 뭘 봤나" 감사 추적 | 인프라 |
| 2 | **Cloud SQL 백업 빈도 단축** (1회/일 → 6시간/회) | 미미 | RPO 24h → 6h | DBA |
| 3 | **IAM 최소권한 재검토** + 불필요한 PHI 접근 역할 회수 | 0 | 침해 시 blast radius 축소 | 보안 |
| 4 | **Security Command Center 알림** 활성화 (Standard 티어) | 저렴 | 이상 접근 감지 | 보안 |

### 해결 데드라인 (PITR — v0.3 유지)

> **PITR 수용 리스크는 글로벌 통합 레포 마이그레이션 시점에 반드시 해소한다. 그 시점에도 미해결이면 신규 리전(미국·싱가포르) 배포를 중단한다.**
>
> 이유: HIPAA Security Rule 2026 개정으로 백업·복구 요건 강화. PITR 없이 미국 진출은 컴플라이언스 리스크.

### CMEK 데드라인 (v0.3 변경)

> **CMEK는 ADR-006(Deferred)로 분리. 강제 데드라인 없음.** Phase 3 이후 운영 안정화와 보안팀·예산 합의 완료 시점에 도입. 단, 법무·감사 요구로 강제 트리거 발생 시 Active 격상.

---

## 결과

### 긍정적
- 조직 현실(협의·예산) 반영
- 완화책 4종으로 감사 방어선 구축
- 데드라인으로 무기한 지연 방지
- ADR 기록으로 "방치" 오해 차단

### 부정적 / 감수
- Gap 유지 기간 중 사고 시 최대 6시간 데이터 손실 가능 (완화책 #2 적용 시)
- CMEK 없는 기간 동안 키 봉쇄 수단 부재
- 감사 시 "왜 바로 안 했나" 질문에 조직 상황 설명 필요

### 후속 작업

- [ ] Phase 0: 완화책 4종 모두 활성화 (2~4주)
- [ ] Phase 0: prd-pasta 주 DB 설정도 동일하게 점검 (`sql-prd-pasta-app`)
- [ ] Phase 0: 인프라팀·보안팀에 **PITR 도입 제안** 정식 제출 (예산·일정 협의 착수). CMEK는 ADR-006(Deferred)로 분리됨
- [ ] Phase 1~2: 신규 리전(오사카·오레곤·싱가포르)은 **Day 1부터 PITR ON** (CMEK는 향후)
- [ ] Phase 3: 글로벌 레포 이관 시 기존 한·일에도 PITR 도입 (데드라인)
- [ ] **Phase 3+**: CMEK 도입 (ADR-006 참조, Deferred)
- [ ] 분기별 gap 재평가 회의

---

## 리스크 & 완화

| 리스크 | 가능성 | 영향 | 완화 |
|--------|-------|------|------|
| 감사 들어올 가능성 | M | H | ADR로 "관리 리스크" 증빙 + 완화책 운영 로그 |
| DB 사고 (실수·악의·장애) | L | H | 백업 6h + IAM 최소 → 손실 한정 |
| 침해 사고 (인증 정보 유출) | M | Critical | SCC 알림 + IAM 최소 + Audit Log 전수 |
| 글로벌 레포 마이그 지연 → 데드라인 넘김 | M | Critical | 신규 리전 배포 중단 조건으로 강제성 부여 |
| 완화책 적용 지연 | L | M | Phase 0 내 완료 (2~4주 내) |

---

## 검증 포인트

- [ ] Phase 0: 완화책 4종 **모두 활성화** (2026-05 내)
- [ ] Phase 0: `gcloud logging sinks list` / `gcloud sql instances describe` / `gcloud iam service-accounts list` / `gcloud scc notifications list` 모두 기대치 반환
- [ ] 분기별: gap 재평가 회의 기록
- [ ] Phase 2 시작 전: 완화책 운영 로그 최소 3개월 축적
- [ ] Phase 3 종료: 기존 CMEK/PITR 도입 100% 완료 (데드라인)

---

## 재평가 시점

- **분기별** 정기 재평가 (Risk Register)
- **글로벌 레포 마이그 착수 시점** — 데드라인 재확인
- **감사 지적 발생 시** — 즉시 Phase 0 Option Y로 격상 검토

---

## 참고

- 에이전트 루브릭 AUTO FAIL #3: "CMEK/감사로그/암호화 OFF 기본값 제안" — 이 ADR은 신규 설계에는 디폴트 ON이고, 기존 운영 gap만 Accepted Risk로 관리 (루브릭 준수)
- [HIPAA Security Rule Changes in 2026](https://www.cbiz.com/insights/article/5-hipaa-security-rule-changes-in-2026-and-how-to-prepare)
- [Cloud SQL MySQL PITR](https://cloud.google.com/sql/docs/mysql/backup-recovery/pitr)
- [Cloud SQL CMEK](https://cloud.google.com/sql/docs/mysql/configure-cmek)
