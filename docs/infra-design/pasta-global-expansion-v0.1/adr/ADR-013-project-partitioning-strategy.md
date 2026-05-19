# ADR-013: 프로젝트 분할 전략 — 시장(국가)별 GCP 프로젝트 + 시장 내 멀티 리전

- **상태**: Proposed (v0.3 신설)
- **작성일**: 2026-05-08
- **리뷰어**: 보안 / 인프라팀 / 법무 / 백엔드 리드
- **관련**: ADR-003 (리전), ADR-004 (레지던시), ADR-005 (Terraform), ADR-011 (글로벌 레포), ADR-014 (LB 패턴)

---

## 컨텍스트

GCP에서 "프로젝트"와 "리전"은 직교(orthogonal)한 두 축이다.

| 개념 | 정의 | 격리 단위 |
|------|------|----------|
| **Project** | GCP 리소스의 논리적 컨테이너. IAM / 청구 / 할당량 / API 활성화 / 감사로그 **경계** | **권한·청구·감사** |
| **Region** | 리소스가 물리적으로 배치되는 위치 (예: `asia-northeast3` = 서울) | **물리·지리** |

→ 1 프로젝트에 다리전 리소스를 두는 것도, 1 리전에 다프로젝트를 두는 것도 모두 가능.

### 현재 운영 (Phase 1.5 확인)

pasta는 이미 **시장(국가) 단위 프로젝트 분할** 패턴으로 운영 중:

| 프로젝트 | 시장 | 리전 |
|---------|------|------|
| `prd-pasta` | 한국 | `asia-northeast3` (서울) |
| `prd-pasta-jp` | 일본 | `asia-northeast1` (도쿄) |
| `prd-pasta-la` | (Deprecated) | - |
| `prd-pasta-lilly` | B2B | `asia-northeast1` |

신규 글로벌 확장 시 **이 패턴을 유지·연장**할지, **단일 글로벌 프로젝트**로 통합할지, **리전 단위로 더 분할**할지 결정 필요.

---

## 결정할 사항

신규 글로벌 확장(미·싱·일본 오사카 DR)에서:
- (A) 모든 리전을 **1개 글로벌 프로젝트**에 — 단일 프로젝트 멀티 리전
- **(B) 시장별 프로젝트, 시장 내 멀티 리전 허용** — 현 패턴 연장 ⭐
- (C) 리전 단위 프로젝트 — 가장 분리

---

## 고려한 옵션

### Option A: 단일 글로벌 프로젝트 멀티 리전

**구조**:
```
prd-pasta-global (단일 프로젝트)
  ├── asia-northeast3 (서울)
  ├── asia-northeast1 (도쿄)
  ├── asia-northeast2 (오사카)
  ├── us-west1 (오레곤)
  └── asia-southeast1 (싱가포르)
```

**장점**:
- 운영 복잡도 낮음
- Terraform state 단순
- 리전 간 리소스 공유 자유

**단점 (헬스케어 컨텍스트)**:
- ❌ **IAM 폭발**: 한국 PHI 접근자와 미국 HIPAA covered entity는 분리 권한 경계가 필요. 단일 프로젝트면 IAM 조건부 정책(`resource.location`)으로 우회 가능하나 **감사·증명 부담 폭증**
- ❌ **감사로그 혼재**: Cloud Audit Logs는 **프로젝트 단위 집계**. 4개국 감사 때마다 필터링 필요
- ❌ **할당량·청구 충돌**: BAA(미국)·위탁계약(한국)·표준약관(일본) 매핑 곤란. 일본 3省2 가이드라인은 위탁사업자 분리 회계·관리 증빙 요구
- ❌ **VPC SC 경계 설계 어려움**: perimeter bridge·access level 복잡

### Option B: 시장(국가)별 프로젝트 + 시장 내 멀티 리전 ⭐ 권고

**구조 (제안)**:

| 시장 | 프로젝트 | 리전 |
|------|---------|------|
| 한국 | `prd-pasta` (기존) | `asia-northeast3` (서울) |
| 일본 | `prd-pasta-jp` (기존) | `asia-northeast1` (도쿄) **+ `asia-northeast2` (오사카) DR** |
| 미국 | `prd-pasta-us` (신규) | `us-west1` (오레곤) |
| 싱가포르 | `prd-pasta-sg` (신규) | `asia-southeast1` |
| 비민감 공통 | `prd-pasta-shared` (옵션) | multi-region GCS, 글로벌 LB 등 |

**장점**:
- ✅ **현 패턴 연속성** — 9개 프로젝트가 이미 시장 단위로 분리되어 한·일 운영 중. 미·싱 추가는 **수평 확장**이라 학습비용·실수 리스크 최소
- ✅ **규제 1:1 매핑** — `prd-pasta-us` = HIPAA covered entity, `prd-pasta-jp` = 3省2 위탁사업자, `prd-pasta` = 한국 개보법. 프로젝트 경계 = 규제 경계
- ✅ **VPC SC 단순화** — perimeter를 프로젝트 단위로 긋고 reflux 차단. 시장 간 데이터 이동은 명시적 perimeter bridge로만 허용 → 감사 시 "**어떤 데이터가 국경을 넘었는가**"가 자명
- ✅ **DR은 같은 시장 내에서** — 도쿄→오사카는 일본 프로젝트(`prd-pasta-jp`) 안의 멀티리전. **같은 규제 권역**이라 IAM·감사 추가 부담 없음

**단점**:
- 공통 비민감 메타(글로벌 사용자 ID 매핑 등)는 별도 `prd-pasta-shared` 필요 → 프로젝트 +1
- Terraform state 디렉토리는 `environments/prd/{project}/{region}/` 2단계가 필요 (ADR-005 보정)
- 글로벌 LB 사용 시 호스트 프로젝트 위치·cross-project 백엔드 설계 필요 (ADR-014)

### Option C: 리전 단위 프로젝트

**구조**:
```
prd-pasta-jp-tokyo / prd-pasta-jp-osaka / prd-pasta-us-oregon ...
```

**장점**: 가장 강한 격리

**단점**:
- ❌ DR 리전이 별도 프로젝트 (도쿄+오사카 같은 일본 규제 하인데 분리) — 과잉
- ❌ 동일 시장 내 멀티 리전 운영 시 cross-project 트래픽 부담
- ❌ Terraform state 과분할
- ❌ 운영 복잡도 매우 높음

---

## 결정

> **선택: Option B — 시장(국가)별 프로젝트 + 시장 내 멀티 리전 허용**

### 핵심 비대칭 (B vs C)

> "**같은 시장의 primary + DR 리전을 같은 프로젝트에 둘 수 있느냐**"

도쿄(`asia-northeast1`) + 오사카(`asia-northeast2`) DR은 **같은 일본 규제 하**. 같은 프로젝트가 자연스럽고 IAM·감사 추가 부담 없음. → 이게 C(리전별)가 과잉인 결정적 이유.

### 선택 근거

1. **현 패턴의 연속성**: 미·싱 추가는 같은 패턴의 수평 확장
2. **규제 경계의 명확성**: 프로젝트 = 규제 경계 = BAA·위탁계약 1:1 매핑
3. **감사 단순성**: 프로젝트 단위 Cloud Audit Logs가 그대로 규제별 증빙
4. **VPC SC 직관성**: perimeter = 프로젝트 = 시장

### 수용한 트레이드오프

- 프로젝트 수 증가 (+미국·싱가포르·shared = 최대 +3)
- Terraform 디렉토리 2단계 보정 필요 (ADR-005에 반영)
- 글로벌 LB 단일 도메인 운영 시 호스트 프로젝트 추가 설계 (ADR-014)

---

## 신규 프로젝트 매핑

| 시장 | 프로젝트 ID (제안) | 리전 | 환경 |
|------|------|------|------|
| 한국 | `prd-pasta` | 서울 | (기존 운영) |
| 일본 | `prd-pasta-jp` | 도쿄 + 오사카(DR) | (기존 + 오사카 신규) |
| 미국 | `prd-pasta-us` | 오레곤 | 신규 |
| 싱가포르 | `prd-pasta-sg` | 싱가포르 | 신규 |
| 공통 (옵션) | `prd-pasta-shared` | multi-region | LB·DNS·공통 메타 |

### dev / stg 미러링

각 시장 프로젝트마다 dev/stg를 두는지, 통합 dev/stg를 두는지는 별도 결정. 권고:
- **prd만 시장별 분리**, dev/stg는 통합 (`dev-pasta-global`, `stg-pasta-global`) — 비PHI 데이터로 운영하면 가능
- 단, **stg에 prd-like PHI 샘플** 사용 시 시장별 stg 필요 → 법무 검토

---

## ADR-005 (Terraform 구조)에 미치는 영향

기존 디렉토리 구조:
```
environments/prd/{region}/
```

→ Option B 채택 시 보정:
```
environments/prd/{project}/{region}/
  ├── prd-pasta/asia-northeast3/
  ├── prd-pasta-jp/{asia-northeast1, asia-northeast2}/
  ├── prd-pasta-us/us-west1/
  ├── prd-pasta-sg/asia-southeast1/
  └── prd-pasta-shared/global/    # 옵션
```

→ ADR-005를 v0.3에서 Superseded 처리 또는 Amendment 추가.

---

## ADR-011 (글로벌 레포)에 미치는 영향

3시나리오 (a/b/c) 무엇이든 **프로젝트 경계는 유지**되어야 함을 전제로 깔고 다시 평가. **모노레포(a)여도 GCP 프로젝트는 분리** — 코드 통합과 GCP 격리는 별개.

---

## 결과

### 긍정적
- 규제 경계 = 프로젝트 경계 (감사 단순)
- 시장별 IAM/청구/할당량 분리
- DR을 같은 시장 내에서 자연스럽게
- 현 패턴의 수평 확장 (학습비용 최소)

### 부정적 / 감수
- 프로젝트 수 증가 (관리 자동화 필요)
- Terraform 2단계 디렉토리 보정
- 비민감 공통 메타용 별도 프로젝트(`prd-pasta-shared`) 필요 시 +1

### 후속 작업

- [ ] Phase 0: 신규 프로젝트 ID 네이밍 컨벤션 확정 (`prd-pasta-us` vs `prd-pasta-us-oregon` 등)
- [ ] Phase 0: 일본 3省2 위탁사업자 회계 분리 요구 해석 (법무 컨펌) — 도쿄+오사카가 같은 프로젝트로 충족 가능한지
- [ ] Phase 0: dev/stg 통합 vs 시장별 분리 결정
- [ ] Phase 1: ADR-005 디렉토리 구조 v0.3 보정 + Terraform 모듈 변수 `project_id` 추가
- [ ] Phase 1: ADR-014 (LB 패턴) 확정 — 글로벌 LB 단일 도메인 시 `prd-pasta-shared` 필요 여부
- [ ] Phase 2: 신규 프로젝트(`prd-pasta-us`, `prd-pasta-sg`) 생성 + 조직 정책 적용
- [ ] Phase 2: VPC SC perimeter를 프로젝트 단위로 설정

---

## 리스크 & 완화

| 리스크 | 가능성 | 영향 | 완화 |
|--------|-------|------|------|
| 프로젝트 수 증가로 IAM·로그 관리 복잡 | M | M | Org Policy + 자동화 + 분기별 권한 감사 |
| Cross-project 의존성 (Shared VPC, 공통 메타) | M | M | ADR-014에서 LB 패턴과 함께 결정 |
| 일본 3省2 해석 모호 (도쿄+오사카 같은 프로젝트) | L | H | 법무 컨펌 후 ADR-013-Amendment로 상태 이동 |
| dev/stg 통합 시 데이터 격리 실수 | M | H | stg에 PHI 사용 금지 정책 + 마스킹 검증 |
| 글로벌 LB 호스트 프로젝트 트래픽 통과 시 "수탁자" 해석 | M | H | ADR-014에서 Pattern 2 default로 회피 |

---

## 검증 포인트

- [ ] Phase 0: 법무 컨펌 (일본 3省2 위탁사업자 분리 요구가 GCP 프로젝트 단위 분리를 강제하는지)
- [ ] Phase 1: 신규 프로젝트 IAM 정책이 시장별로 격리되어 있음 (cross-project 권한 0)
- [ ] Phase 2: 4개국 규제 dry-run에서 "프로젝트 = 규제 경계" 증빙 통과
- [ ] Phase 2: VPC SC perimeter 위반 시 차단 동작 확인

---

## 재평가 시점

- **Phase 0 종료 시점** — 법무 컨펌 결과
- **글로벌 레포(ADR-011) 시나리오 확정 시** — 모노레포(a) 채택 시 프로젝트 분할 정책 재확인
- **5번째 시장 추가 시** — 프로젝트 수 누적이 IAM·청구 관리 한계를 넘는지

---

## 참고

- ADR-014 (LB 패턴) — 호스트 프로젝트 + cross-project 백엔드 결정과 짝
- ADR-005 (Terraform) — 디렉토리 2단계 보정 필요
- ADR-011 (글로벌 레포) — 코드 통합과 GCP 격리는 직교
- [GCP Resource Hierarchy](https://cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy)
- [Geography and regions](https://cloud.google.com/docs/geography-and-regions)
