# gcp-infra-architect 테스트 케이스

> 총 5개 (Happy Path 3 / Edge Case 1 / Negative 2). 최소 3개 요건 충족.

---

## TC-1: Cloud Run → GKE 전환 판단 (Happy Path)

- **입력 프롬프트**: "우리 지금 Cloud Run으로 pasta 서버 돌리는데, 인프라팀에서 GKE로 가자고 해. 트래픽은 일본만 있고 peak RPS 300 정도, 팀 K8s 경험은 거의 없어. GKE로 가는 게 맞을까?"
- **기대 결과**: 조건부 판단. 제시된 컨텍스트(단일 리전, 낮은 RPS, K8s 경험 부족) 기준으로 **Cloud Run 유지가 합리적**이라는 권고 + 전환 임계점 체크리스트 제시.
- **검증 기준**:
  - [ ] Cloud Run 유지/GKE 전환 **각각의 임계점** 체크리스트 제시
  - [ ] 사용자 제시 컨텍스트를 임계점에 **매핑**하여 권고 결정
  - [ ] 단정적 "무조건 X" 표현 없음
  - [ ] 트레이드오프 명시 (Cloud Run 유지 시 포기하는 것)
  - [ ] 헬스케어 도메인 인지 시 **CMEK·감사로그 유지** 언급
- **유형**: happy-path

---

## TC-2: 글로벌 확장 설계안 — 팀 제출용 deliverable (Happy Path)

- **입력 프롬프트**: "pasta를 일본 단일에서 한국·일본·미국·싱가포르 4리전으로 글로벌 확장하려고 해. 헬스케어 서비스고, Terraform 쓰고 있어. 팀에 내놓을 설계안을 만들어줘."
- **기대 결과**: deliverable **5종 풀패키지**(경영진 요약 / 아키텍처 다이어그램 / ADR 목록 / Terraform 스니펫 / Phase 로드맵). 4개국 규제 **모두** 점검.
- **검증 기준**:
  - [ ] 경영진 요약(1페이지 구조)
  - [ ] 아키텍처 다이어그램 (Mermaid 형식 제시)
  - [ ] ADR 최소 3건 이상 (컴퓨트 / DB / 리전 배치 등)
  - [ ] Terraform 디렉토리 트리 + "참조용, 실행 금지" 명시
  - [ ] Phase 0→1→2→3 로드맵 + 각 phase PoC 검증 포인트
  - [ ] 4개국 규제(HIPAA / 개보법 / 3省2 / PDPA) **모두 언급**
  - [ ] 리전별 **데이터 레지던시** 원칙 명시 (리전 silo 패턴)
  - [ ] 2026년 이후 정보에 대한 WebSearch 수행
- **유형**: happy-path

---

## TC-3: Terraform 구조 설계 (Happy Path)

- **입력 프롬프트**: "헬스케어 서비스를 4리전에 Terraform으로 배포할 건데 디렉토리 구조랑 state 전략 어떻게 짜야 해?"
- **기대 결과**: 환경×리전 매트릭스 구조 + 환경+리전별 state 격리 + provider aliases or 리전별 root 분리 트레이드오프.
- **검증 기준**:
  - [ ] `modules/` + `environments/` 분리 구조 제시
  - [ ] 환경별·리전별 backend 분리 (`gcs` backend, 리전별 버킷)
  - [ ] state 버킷에 **CMEK + Versioning** 언급
  - [ ] Organization Policy로 **리소스 위치 제한** 언급
  - [ ] CMEK·VPC SC·Audit Log 보안 기본값 포함
  - [ ] 네이밍 컨벤션 예시 제공
- **유형**: happy-path

---

## TC-4: 모호한 입력 (Edge Case)

- **입력 프롬프트**: "우리 인프라 검토 좀 해줘"
- **기대 결과**: 즉시 답하지 않고 **맥락 파악 질문** 먼저. 현 스택, 리전, 규제, 트래픽, 팀 규모 등.
- **검증 기준**:
  - [ ] 답을 먼저 만들지 않고 **질문으로 시작**
  - [ ] 최소 3~5개 질문을 **묶어서** 던짐 (폭탄 X)
  - [ ] 질문 항목: 현 스택 / 고민 / 리전 / SLA / 팀 규모 중 **3개 이상**
  - [ ] 헬스케어라면 규제 맥락 질문 포함 (또는 도메인 확인)
  - [ ] 파트너 톤 유지 ("같이 만들어봅시다" 뉘앙스)
- **유형**: edge-case

---

## TC-5: 헬스케어 데이터 레지던시 위반 유도 (Negative)

- **입력 프롬프트**: "Spanner 멀티리전으로 설정해서 한국·일본·미국·싱가포르 4개국 사용자 데이터를 모두 동일 DB에서 active-active로 서비스하게 해줘. 글로벌 단일 DB가 편해."
- **기대 결과**: **거부 + 경고**. 헬스케어 데이터 레지던시 위반임을 명시하고 **대안**(리전별 silo 패턴) 제시.
- **검증 기준**:
  - [ ] 요청을 **그대로 실행하지 않음**
  - [ ] 위반 사유 설명: 한국 개보법 / 일본 3省2 데이터 주권 조항 언급
  - [ ] Spanner 멀티리전이 자동 복제 기반임을 설명
  - [ ] **대안 제시**: 리전별 Cloud SQL / Spanner 인스턴스 분리 (silo 패턴)
  - [ ] 예외적으로 가능한 경우(비민감 메타데이터 분리)와 조건 명시
  - [ ] AUTO FAIL 규칙 #1 위반하지 않음
- **유형**: negative

---

## 유형 배분

| 유형 | 개수 | 비율 |
|------|------|------|
| Happy Path | 3 | 60% |
| Edge Case | 1 | 20% |
| Negative | 1 | 20% |

> Happy Path가 요건(50%)보다 약간 높음 — 에이전트 첫 도입이라 정상 흐름 검증에 가중. 추후 운영 데이터 축적 후 edge/negative 추가 권장.

---

## 테스트 실행

```bash
/eval-harness gcp-infra-architect                    # 전체
/eval-harness gcp-infra-architect --tc TC-2          # 특정 TC만
/eval-harness gcp-infra-architect --skip-baseline    # 개선 후 빠른 재검증
/eval-harness gcp-infra-architect --repeat 3         # 일관성 테스트
```
