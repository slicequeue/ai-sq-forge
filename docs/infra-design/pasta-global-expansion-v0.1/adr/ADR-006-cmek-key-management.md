# ADR-006: CMEK 키 관리 — 리전별 Keyring + 목적별 Key

- **상태**: **Deferred (v0.3 변경)** — 향후 Phase 적용 대상. 단기 5개월 MVP-Lite 스코프에서는 Google-managed 기본 암호화 사용
- **작성일**: 2026-04-22 (v0.3 상태 변경: 2026-05-08)
- **리뷰어**: 보안 / 인프라팀
- **관련**: ADR-004 (데이터 레지던시), ADR-005 (Terraform), ADR-012 (수용 리스크)

---

## v0.3 상태 변경 (2026-05-08)

본 ADR은 **Deferred 처리**한다.

### Deferred 사유

- 5개월 MVP-Lite 압축 시나리오에서 CMEK 셋업(KMS keyring·키 네이밍·로테이션·IAM·SCC 모니터링)은 학습곡선·작업량이 크고, **HIPAA 컴플라이언스의 필수가 아님** (HIPAA는 encryption-at-rest를 요구하나 CMEK 강제 X — Google-managed encryption도 HIPAA-compliant)
- 단기 MVP 진입을 위해 **Google-managed 기본 암호화로 시작**하고, CMEK는 Phase 3 또는 운영 안정화 후 도입
- ADR-012의 "CMEK 데드라인" 부분도 함께 완화 (PITR 데드라인은 유지)

### 적용 시점 (잠정)

- **Phase 3 이후** (운영 안정화 + 인프라팀·보안팀 협의·예산 결재 완료 후)
- 또는 **법무·감사 요구로 강제 트리거 발생 시** (즉시 Active 격상)

### 신규 리전(미·싱) Day 1 정책

- v0.2: "신규 리전 Day 1 CMEK ON"
- **v0.3: Google-managed 기본 암호화로 시작, CMEK는 향후 적용**

### 본 ADR 본문의 효력

본 ADR의 키 네이밍·로테이션·IAM 설계는 **향후 적용 시 참조용 사양**으로 보존한다. 단, Phase 0~2의 후속 작업 체크박스는 모두 **Phase 3 이후로 이동**한다.

---

## 컨텍스트

- 4개국 규제 모두 **헬스케어 데이터 암호화** 필수 (HIPAA 2026 개정으로 더 엄격)
- CMEK (Customer Managed Encryption Key)가 표준 권고
- Cloud KMS 키는 **리전 속성**을 가짐 → 리전 간 이동 불가
- 데이터 리전과 키 리전이 **어긋나면** 국경 이동으로 간주될 소지

**결정할 사항**: 키링·키를 어떻게 분리·관리할 것인가.

---

## 고려한 옵션

### Option A: **리전별 Keyring + 목적별 Key** ⭐ 권고

**구조**:
```
projects/pasta-prd/locations/asia-northeast3/keyRings/pasta-prd-seoul/
  ├── cryptoKeys/sql-key         # Cloud SQL 암호화
  ├── cryptoKeys/storage-key     # Cloud Storage 암호화
  ├── cryptoKeys/tfstate-key     # Terraform state 버킷
  ├── cryptoKeys/logs-key        # Cloud Logging 장기 저장
  └── cryptoKeys/secret-key      # Secret Manager (선택)

projects/pasta-prd/locations/asia-northeast1/keyRings/pasta-prd-tokyo/
  └── (동일 구조)

... (오사카, 싱가포르, 오레곤 각각)
```

**장점**:
- **키 국경 이동 리스크 0** — 각 리전 데이터는 해당 리전 키로만
- **목적별 분리**로 권한·로테이션 독립
- 보안 사고 시 blast radius 제한 (한 키 유출이 타 키 영향 없음)
- 감사 시 명확한 키 → 데이터 매핑

**단점**:
- 키 개수 증가 (리전 5 × 목적 5 = 최대 25개)
- 로테이션 스케줄 관리 복잡 (IaC + 자동화로 완화)

### Option B: 조직 공통 Keyring

**설명**: 단일 조직 공통 keyring에 키 배치.

**장점**: 관리 단순

**단점**:
- ❌ 키 리전 속성 때문에 **글로벌 공통 키 불가능** — 어차피 리전별 필요
- 목적 구분 없어 권한 granularity 부족
- 감사 매핑 어려움

### Option C: 다중 리전 Keyring

**설명**: KMS multi-region location 사용 (예: `global`, `asia`).

**장점**: 고가용성

**단점**:
- ❌ 헬스케어 데이터 국경 이동 소지
- 한국 데이터에 아시아 공통 키 적용 시 개보법 해석 리스크

---

## 결정

> **선택: Option A (리전별 Keyring + 목적별 Key)**

### 선택 근거

1. **데이터-키 리전 일치** — 규제 정합의 가장 명확한 형태
2. **목적별 분리**로 감사·권한·로테이션 독립 관리
3. **IaC로 복잡도 관리 가능** — `modules/kms-cmek/`로 표준화

### 수용한 트레이드오프

- 키 개수 증가 → Terraform 모듈 + 자동 로테이션으로 관리 부담 완화

---

## 키 네이밍 컨벤션

```
pasta-{env}-{region}-{purpose}-key

예:
pasta-prd-seoul-sql-key
pasta-prd-tokyo-storage-key
pasta-prd-oregon-tfstate-key
```

KeyRing 네이밍:
```
pasta-{env}-{region}

예:
pasta-prd-seoul
pasta-prd-tokyo
```

---

## 로테이션 정책

| 키 유형 | 로테이션 주기 | 이전 버전 보관 |
|---------|--------------|----------------|
| `sql-key` | 90일 | 365일 |
| `storage-key` | 90일 | 730일 (백업 복호화 고려) |
| `tfstate-key` | 180일 | 365일 |
| `logs-key` | 180일 | 3년 (규제 로그 보관 기간) |
| `secret-key` | 90일 | 180일 |

**자동 로테이션**: Cloud KMS `rotation_period` 속성으로 자동화.

---

## 접근 제어 (IAM)

| 역할 | 대상 키 | 권한 |
|------|---------|------|
| Cloud SQL 서비스 계정 | `sql-key` | `cloudkms.cryptoKeyEncrypterDecrypter` |
| Cloud Run 서비스 계정 | (사용 키만) | 최소 권한 |
| Terraform 운영자 | `tfstate-key` | `cloudkms.cryptoKeyEncrypterDecrypter` |
| Security Admin | 모든 키 | `cloudkms.admin` (비상) |
| 일반 개발자 | - | **권한 없음** |

---

## CMEK 적용 대상 (헬스케어 필수)

- Cloud Storage 버킷 (PHI 포함, tfstate, 로그 장기 저장)
- Cloud SQL 인스턴스 (Postgres)
- Cloud Logging sink (장기 보관 버킷)
- BigQuery 데이터셋 (분석용)
- Cloud Run `encryption_key` (2024년 이후 지원, 컨테이너 디스크 암호화)
- Secret Manager (선택, 중요도 따라)
- GKE etcd (Phase 3 도입 시)

---

## 결과

### 긍정적
- 규제 정합의 명확한 형태
- 보안 사고 blast radius 제한
- 목적·리전별 감사 추적 용이

### 부정적 / 감수
- 키 관리 복잡도 증가 → IaC·자동화 필수
- 리전 추가 시 키링 세트 복제 필요 (템플릿화로 완화)

### 후속 작업 (v0.3: 모두 Phase 3 이후로 이동)

- [ ] **Phase 3+**: `modules/kms-cmek/` Terraform 모듈 작성
- [ ] **Phase 3+**: 키 네이밍 컨벤션 문서화 + 팀 공유
- [ ] **Phase 3+**: 도쿄·서울 리전에 키링 구축, 로테이션 스케줄 설정
- [ ] **Phase 3+**: CMEK 적용 대상 리소스 전수 검증 (SCC로 자동 탐지)
- [ ] **Phase 3+**: 오레곤·싱가포르 리전에 동일 패턴 적용
- [ ] **Phase 3+**: 분기별 키 감사 리포트 자동화

---

## 리스크 & 완화

| 리스크 | 가능성 | 영향 | 완화 |
|--------|-------|------|------|
| 키 실수 삭제 (데이터 복호화 불가) | L | **Critical** | Key deletion protection + 90일 삭제 대기 기본값 |
| 로테이션 중 키 접근 실패 | L | H | 이전 버전 유지 기간 충분히, 사전 테스트 환경 검증 |
| 권한 관리 실수 (최소권한 위반) | M | M | IAM 정책 Terraform으로 관리, 정기 감사 |
| 리전 간 키 혼동 (서울 데이터에 도쿄 키) | L | H | 네이밍 컨벤션 + Terraform 변수 검증 |

---

## 검증 포인트

- [ ] Phase 0: `modules/kms-cmek/` 모듈 PR 리뷰 통과
- [ ] Phase 1: 도쿄·서울 CMEK 적용 대상 리소스 100% 커버
- [ ] Phase 1: 로테이션 테스트 (수동 트리거 후 데이터 접근 정상 확인)
- [ ] Phase 2: SCC에서 CMEK 미적용 리소스 탐지 0건
- [ ] Phase 2: 키 감사 리포트 자동화 구현

**재평가 시점**: Phase 2 종료 후. 키 개수·로테이션 빈도·감사 결과 기반으로 운영 피로도 점검.

---

## 참고

- 에이전트 결정 프레임워크: `anvil/agents/gcp-infra-architect/references/decision-frameworks.md` §5
- 규제 참조: `anvil/agents/gcp-infra-architect/references/regulations/` (4개국 CMEK 요구사항)
- [Cloud KMS 공식 문서](https://cloud.google.com/kms/docs)
