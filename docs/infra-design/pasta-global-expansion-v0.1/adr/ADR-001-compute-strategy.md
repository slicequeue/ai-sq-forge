# ADR-001: 컴퓨트 전략 — Cloud Run 유지 + Phase 3 하이브리드 GKE Autopilot

- **상태**: Proposed
- **작성일**: 2026-04-22
- **작성자**: slicequeue (+ gcp-infra-architect 에이전트)
- **리뷰어**: 인프라팀 (K8s 책임자) / 백엔드 리드
- **관련**: ADR-003 (리전), ADR-005 (Terraform)

---

## 컨텍스트

- **현행**: GCP Cloud Run 기반 서버, 일본 단일 리전
- **통증**: DB 연결 이슈 반복, "AWS ECS 대비 안정성 저조" 체감
- **미래 워크로드**: Kafka 도입 예정(시점 미확정), WebSocket(보이스) 이미 존재
- **팀**: 글로벌 담당 1명(K8s 경험 부족) + 인프라팀 K8s 전담(책임자+실무자)
- **일정**: 연말까지 4리전 확장 완료
- **인프라팀 제안**: GKE 전환 검토 중

**결정할 사항**: Cloud Run 유지 / 즉시 GKE 풀이관 / 하이브리드 점진 전환 중 선택.

---

## 고려한 옵션

### Option A: Cloud Run 유지 + 안정화 보완

**설명**: GKE 전환 없이 Cloud Run 현행 유지. 2026년 최신 권장 패턴으로 안정화:
- Cloud SQL Managed Connection Pooling
- Cloud SQL Auth Proxy Sidecar (2026 GA)
- `min_instances=1` + CPU always allocated

**장점**:
- 전환 리스크 0
- 단기 통증 즉시 해결
- 담당자 K8s 역량 문제 없음

**단점**:
- Kafka 도입 확정 시 한계 (Cloud Run은 Kafka consumer로 부적합)
- 미래 부채 가능성

**비용**: 현 수준 유지 (Managed Pooling은 추가 비용 경미)

### Option B: 즉시 GKE Autopilot 풀이관

**설명**: 전 워크로드를 GKE Autopilot으로 이관. 표준화된 K8s 기반.

**장점**:
- 표준 플랫폼, 미래 확장성
- Kafka·WebSocket·기타 워크로드 통합 용이
- 인프라팀 전문성 최대 활용

**단점**:
- **일정 리스크 큼** — 연말 4리전 확장과 풀이관 병행 부담
- 담당자 K8s 학습 병목
- Cloud Run ↔ GKE 변환 불가 → 재설계 수준 작업
- 전환 중 장애 가능성 ↑

**비용**: 단기 +30~50% (idle 비용), 중기 최적화 필요

### Option C: **하이브리드 점진 전환** ⭐ 권고

**설명**:
- Phase 0~2: Cloud Run 유지, 안정화 + 리전 확장에 집중
- Phase 3 (연말 근처): Kafka 확정 시점에 GKE Autopilot **1리전 선도 도입** (도쿄). WebSocket/Kafka 워크로드만 이관. API·Batch·Client는 Cloud Run 유지.

**장점**:
- 단계적 리스크 (먼저 확장 완수 후 플랫폼 확장)
- 팀 K8s 학습 시간 확보
- 인프라팀 주도로 GKE 도입 — 담당자 부담 분산
- Kafka/WebSocket은 GKE가 명확히 유리, 나머지는 Cloud Run 유지가 유리 → **각 워크로드 최적 플랫폼**

**단점**:
- 2개 플랫폼 동시 운영 복잡성 (모니터링·배포·인증 이중)
- 통일성 측면 장기 부채

**비용**: Phase 3에서 +10~20% 점진

---

## 결정

> **선택: Option C (하이브리드 점진 전환)**

### 선택 근거

1. **Kafka 확정 전까지 GKE 기술 강제 근거 약함** — Cloud Run WebSocket GA, Managed Pooling/Auth Proxy로 안정성 해결 가능
2. **일정 리스크 최소화** — Phase 0~2에서 리전 확장에 집중. 플랫폼 전환을 Phase 3로 분리하여 두 리스크를 직렬화
3. **팀 역량 현실 반영** — 담당자 K8s 부족 + 인프라팀 K8s 전담 구조에서 Autopilot + 인프라팀 주도가 가장 현실적
4. **워크로드 특성별 최적화** — WebSocket·Kafka는 GKE가 유리, API·Batch·Client는 Cloud Run이 유리

### 수용한 트레이드오프

- 2개 플랫폼 동시 운영의 복잡성 — 모니터링·IaC·배포 파이프라인이 플랫폼별 이중화 필요
- 단기 표준화 지연 — "전부 K8s" 정리는 Phase 3 이후 과제

---

## 결과

### 긍정적 결과

- 리전 확장 일정 안정성 확보
- Cloud Run 통증 Phase 0에서 즉시 해결 → 고객 경험 조기 개선
- 팀 K8s 학습이 점진적 (Phase 3 도입 전까지 인프라팀과 협업 시간 확보)

### 부정적 결과 / 감수 사항

- Phase 3 시점에 GKE 도입을 다시 고민해야 하는 의사결정 비용
- 모니터링 대시보드가 Cloud Run + GKE 이중 구성

### 후속 작업

- [ ] Phase 0: Managed Pooling + Auth Proxy Sidecar 적용
- [ ] Phase 0: `min_instances=1` + CPU always allocated 설정
- [ ] Phase 3 진입 시점에 **Kafka 도입 확정 여부 재확인** → GKE 도입 트리거
- [ ] Phase 3: WebSocket 트래픽 측정 (동시연결 1000+ 초과 시 GKE 이관 재검토)

---

## 리스크 & 완화

| 리스크 | 가능성 | 영향 | 완화 |
|--------|-------|------|------|
| Kafka 도입이 Phase 3보다 앞당겨짐 | M | H | ADR 재검토 트리거 — Phase 순서 조정 |
| Cloud Run 안정화 효과 미미 | L | H | Phase 0에 baseline 측정 → 실패 시 Option B로 전환 검토 |
| 2플랫폼 운영 부담 과다 | M | M | Phase 3 종료 시점에 통합 여부 재검토 |

---

## 검증 포인트

- [ ] Phase 0: DB 이슈 재발률 **50% 감소** 측정
- [ ] Phase 0: 커넥션 timeout 에러 **0건 (1주)**
- [ ] Phase 3: GKE Autopilot 도입 시 Kafka consumer lag 허용 범위 내
- [ ] Phase 3: WebSocket 이관 후 P95 latency 변동 ±10% 이내

**재평가 시점**: Phase 3 종료 후 (2027-01). Kafka 사용 규모, WebSocket 규모, 담당 인력 변화 종합 평가.

---

## 참고

- [Cloud Run WebSockets GA](https://docs.cloud.google.com/run/docs/triggering/websockets)
- [Cloud SQL Managed Connection Pooling](https://docs.cloud.google.com/sql/docs/postgres/managed-connection-pooling)
- [GKE Autopilot overview](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)
- 에이전트 결정 프레임워크: `anvil/agents/gcp-infra-architect/references/decision-frameworks.md` §1
