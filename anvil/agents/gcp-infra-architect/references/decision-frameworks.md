# 아키텍처 결정 프레임워크

GCP 글로벌 헬스케어 서비스 설계에서 자주 맞닥뜨리는 핵심 결정들의 판단 트리.

## 목차
- [1. Cloud Run ↔ GKE 전환 판단](#1-cloud-run--gke-전환-판단)
- [2. 리전 배치 전략](#2-리전-배치-전략)
- [3. 데이터베이스 선택](#3-데이터베이스-선택)
- [4. 메시징·이벤트 선택](#4-메시징이벤트-선택)
- [5. 시크릿·키 관리](#5-시크릿키-관리)

---

## 1. Cloud Run ↔ GKE 전환 판단

### 핵심 질문: "지금 Cloud Run의 한계에 부딪혔는가?"

**무조건 GKE 권장 금지.** GCP는 Standard ↔ Autopilot 변환도 불가능하며, Cloud Run → GKE 마이그레이션은 **재설계 수준 작업**. 전환 비용이 유지 비용보다 큰지 먼저 평가.

### Cloud Run 유지 근거 (≥3개 해당 시 유지 권고)

- [ ] HTTP/gRPC 중심 요청·응답 모델
- [ ] 팀 K8s 운영 경험 부족
- [ ] 피크 트래픽과 idle 격차 큼 (scale-to-zero 가치 큼)
- [ ] 서비스 수 < 30 (Cloud Run 단위 관리 용이)
- [ ] 상태유지 (StatefulSet) 불필요
- [ ] 장기 실행 워크로드(>60분) 없음 또는 Cloud Run Jobs로 충분

### GKE 전환 임계점 (≥3개 해당 시 전환 검토)

- [ ] **Kafka·NATS·WebSocket** 등 비 HTTP 프로토콜·양방향 통신
- [ ] **GPU/TPU** 필요 (추론 서빙 등)
- [ ] **사이드카 패턴** (Istio, Envoy 확장 등) 필수
- [ ] **CronJob·Batch 파이프라인** 수가 많고 의존성 복잡 (Cloud Run Jobs 한계 초과)
- [ ] **멀티 컨테이너 Pod** 필요 (Cloud Run도 최근 sidecar 지원하지만 제약 있음)
- [ ] **네트워크 정책(NetworkPolicy)·Service Mesh**로 마이크로세그멘테이션 필수
- [ ] 서비스 수 100+ → K8s 네임스페이스·라벨링이 관리 이점 큼
- [ ] **전용 IP·고정 egress** 요구 (Cloud Run도 가능하지만 복잡)

### 하이브리드 (권장 기본값)

대부분의 현실 케이스는 **Cloud Run + GKE 혼용**이 최적:
- **API 서버 (HTTP/gRPC)** → Cloud Run
- **백그라운드 워커 / Kafka consumer / 장시간 잡** → GKE
- **ML 추론 (GPU)** → GKE
- **관리자 툴·내부 API** → Cloud Run

### 전환 시 체크포인트

1. 현 Cloud Run 설정을 **Helm/Kustomize**로 재기술 가능한지 PoC
2. **Ingress·TLS 관리** (Cloud Run의 자동 인증서 → GKE는 cert-manager)
3. **IAM 서비스 계정** 매핑 (Workload Identity)
4. **Secret 관리** (Cloud Run의 Secret Manager 연동 → GKE의 External Secrets)
5. **Autopilot vs Standard** — SRE 인력 < 2명이면 Autopilot
6. **비용 계산** — Cloud Run scale-to-zero 포기 시 idle 비용 증가분

---

## 2. 리전 배치 전략

### 핵심 질문: "건강정보의 데이터 주권을 어떻게 지킬 것인가?"

헬스케어는 **리전별 완전 분리가 기본 원칙** (한국 개보법, 일본 3省2가이드라인이 사실상 강제). 그 위에 "글로벌 로직"만 공유.

### 패턴 A: 리전별 완전 분리 (Regional Silo) — **헬스케어 기본 추천**

```
한국 사용자 → asia-northeast3 (서울) → 서울 DB (민감정보)
일본 사용자 → asia-northeast1 (도쿄) → 도쿄 DB
미국 사용자 → us-west1 (오레곤)       → 미국 DB
싱가포르 사용자 → asia-southeast1     → 싱가포르 DB
```

- **장점**: 규제 충돌 없음, blast radius 제한, 인프라 독립
- **단점**: 리소스 중복 비용, 데이터 집계 어려움 (분석용 별도 파이프라인)
- **적합**: 헬스케어, 금융, 법규 엄격 도메인 (**파스타 권고**)

### 패턴 B: Active-Active 멀티리전 (Spanner 등)

```
모든 리전 동시 활성 + Spanner multi-region으로 데이터 공유
```

- **장점**: 장애 격리, latency 최적화, 단일 논리 DB
- **단점**: 헬스케어에 **부적합** — 데이터가 리전 간 자동 복제되어 주권 위반 소지
- **적합**: 비민감 글로벌 서비스 (헬스케어 제외)

### 패턴 C: Active-Passive (DR)

```
Primary 리전 + 다른 리전에 Standby
```

- **장점**: 단순, 비용 저렴
- **단점**: Standby 리전이 놀고 있음, fail-over 연습 필요
- **적합**: 리전 1개 + DR만 필요한 단계, 초기 도입

### 파스타 권고 (한·일·미·싱)

**하이브리드 패턴**:
```
민감정보 저장소: 리전별 완전 분리 (패턴 A)
글로벌 메타데이터 (지역 독립): 패턴 B 또는 중앙 집중 리전
정적 자산 / CDN: Cloud CDN 글로벌
인증: 지역별 Identity Pool (OR 중앙 인증 후 JWT)
```

### 리전 선택

| 사용자 | 리전 | 비고 |
|--------|------|------|
| 한국 | `asia-northeast3` (서울) | 민감정보 서울 고정 |
| 일본 | `asia-northeast1` (도쿄), DR: `asia-northeast2` (오사카) | |
| 미국 | `us-west1` (오레곤) 또는 `us-central1` (아이오와) | HIPAA 대응 리전 |
| 싱가포르 | `asia-southeast1` (싱가포르) | DR 옵션은 별도 검토 |

---

## 3. 데이터베이스 선택

### 결정 트리

```
Q1: ACID + 글로벌 일관성 + 수평 확장 필요?
 ├ YES → Spanner (단, 멀티리전 구성이 헬스케어 데이터 주권과 충돌하지 않는지 확인)
 └ NO  → Q2

Q2: 관계형 + 리전 내 저장 + 일반적 RDBMS 기능?
 ├ YES → Cloud SQL (Postgres / MySQL) per region
 └ NO  → Q3

Q3: 대규모 문서·반정형 데이터 + 실시간 동기화?
 ├ YES → Firestore (region-scoped)
 └ NO  → Q4

Q4: 분석·집계 중심, 운영 아닌 데이터 웨어하우스?
 ├ YES → BigQuery (리전 지정 필수)
 └ NO  → Q5 (특수 케이스)

Q5: 캐시 / 세션 / Rate limit / 실시간 리더보드?
 └ Memorystore (Redis / Memcached) per region
```

### 헬스케어 시 주의

- **Spanner 멀티리전** 사용 시 자동 복제가 헬스케어 규제와 충돌 가능
  - 해결: **리전별 Spanner 인스턴스 분리** 또는 Cloud SQL per region
- **Cloud Healthcare API** (FHIR/DICOM/HL7v2) 사용 검토 — PHI 전용 설계

### 파스타 권고 초안 (Phase별)

| Phase | DB 전략 |
|-------|---------|
| Phase 1 (현행 + 한국·일본) | Cloud SQL (Postgres) per region, 리전 내 HA |
| Phase 2 (미국·싱가포르 추가) | 동일 패턴 확장 |
| Phase 3 (운영 성숙) | 분석은 리전별 BigQuery → Dataflow로 익명화 집계 |

---

## 4. 메시징·이벤트 선택

| 선택지 | 장점 | 단점 | 적합한 경우 |
|--------|------|------|-------------|
| **Pub/Sub** | 완전 관리형, 글로벌, 고성능 | 순서 보장 제한, Kafka 호환 X | 대부분의 비동기 작업, 이벤트 알림 |
| **Eventarc** | Cloud Run·GKE 트리거 자동 연동 | Pub/Sub 기반 wrapping | Cloud Run에서 Pub/Sub 소비 시 |
| **Pub/Sub Lite** | 비용 저렴, Kafka 호환 | 리전 한정, 관리 부담 | 로그/메트릭 스트리밍, 저비용 요구 |
| **Confluent Kafka on GKE** | 기존 Kafka 자산 활용, 강한 순서 보장 | 운영 부담, SRE 필요 | Kafka 기반 기존 시스템 마이그레이션 |

### 권고

- 신규는 **Pub/Sub 우선** 검토
- Kafka 반드시 필요하면 **Confluent Cloud (매니지드)** 검토 후 자체 운영 최후
- 헬스케어 데이터를 이벤트로 흘릴 때 **리전 바운더리 유지** (글로벌 Pub/Sub도 리전 옵션 사용)

---

## 5. 시크릿·키 관리

### 원칙

- **애플리케이션 시크릿** → Secret Manager
- **암호화 키 (KMS)** → Cloud KMS + CMEK
- **CI/CD 인증** → Workload Identity Federation (static key 지양)

### CMEK 적용 대상 (헬스케어)

- Cloud Storage (PHI 버킷)
- Cloud SQL / Spanner 인스턴스
- GKE etcd
- Cloud Logging / Audit Log 저장소
- BigQuery 데이터셋

### 키 로테이션

- 정기 로테이션 (예: 90일)
- 리전별 별도 키 (서울 키는 서울 리전, 도쿄 키는 도쿄 리전)
- **키 보관 리전 = 데이터 저장 리전** (국경 넘지 않도록)

---

## 결정 프레임워크 사용법

이 문서는 에이전트가 결정을 내릴 때 참조하는 **사고의 뼈대**. 다만 항상 **조건부 권고**로 기술하고, 사용자의 제약(팀 규모/역량/예산)을 들어본 뒤 최종 권고안을 만든다. 단정 금지.
