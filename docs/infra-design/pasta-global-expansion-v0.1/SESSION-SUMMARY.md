# 세션 회고 — pasta 글로벌 확장 + 에이전트 구축 (2026-04-21 ~ 22)

> 이 문서는 **배포(C 단계) 재개 시 빠른 컨텍스트 복원**이 핵심 목적. 2~3분 안에 현재 상태 파악 가능하도록 작성.

---

## 1. 세션 목표 → 달성도

| 목표 | 상태 |
|------|------|
| forge 최초 **Agent** 생성 (skill 아닌 agent) | ✅ `gcp-infra-architect` v1.2 |
| pasta 글로벌 확장 설계안 초안 | ✅ v0.2 (DESIGN + ADR 8건) |
| 하네스 평가 → 품질 수치화 | ✅ 94.1/100 |
| 일관성 검증 (repeat) | ✅ PASS (편차 4점) |
| 사용자 피드백 반영 루프 | ✅ v1.0 → v1.1 → v1.2 (2회 iteration) |
| pasta 실전 배포 (C 단계) | ⏸️ **사용자 결정 — 나중에 일괄** |

---

## 2. 타임라인 (핵심 이정표)

| 시점 | 사건 |
|------|------|
| Day 1 | forge 첫 에이전트 설계 Q&A → 에이전트 v1.0 + 설계안 v0.1 |
| Day 1 | 하네스 평가 → v1.0 Happy Path 3/3 PASS (92.3) |
| Day 2 | 사용자 피드백 "현황 파악·멀티턴·쌍방향" → **v1.1** (5/5 93.8, 일관성 CONCERN) |
| Day 2 | Phase 1.5 gcloud 실행 → **실제 현황 대발견** (9 프로젝트, MySQL, CMEK 미적용) → 설계안 **v0.2 재작성** |
| Day 2 | TC-2 일관성 이슈 식별 → **v1.2** (요청 유형 감지 로직) → 3/3 수렴 PASS (94.1) |

---

## 3. 산출물 인벤토리 (30개 파일)

### 에이전트 (10)
```
anvil/agents/gcp-infra-architect/
├── gcp-infra-architect.md         # v1.2
└── references/
    ├── evaluation-rubric.md       # v1.2 (항목 8개, 6a/6b 분할)
    ├── decision-frameworks.md
    ├── terraform-patterns.md
    ├── adr-template.md
    └── regulations/
        ├── hipaa.md
        ├── korea-pipa.md
        ├── japan-3sho2guide.md
        └── singapore-pdpa.md
```

### 설계안 (9)
```
docs/infra-design/pasta-global-expansion-v0.1/
├── README.md                       # v0.2
├── DESIGN.md                       # v0.2 (한+일 기존 + 글로벌 통합)
├── CONTEXT.md                      # v0.2 (실제 현황 반영)
├── SESSION-SUMMARY.md              # 🆕 이 문서
└── adr/
    ├── ADR-001-compute-strategy.md
    ├── ADR-002-database-strategy.md    # v0.2 (MySQL)
    ├── ADR-003-region-routing.md       # v0.2 (기존+신규 구분)
    ├── ADR-004-data-residency.md
    ├── ADR-005-terraform-structure.md  # v0.2 (green-field)
    ├── ADR-006-cmek-key-management.md
    ├── ADR-011-global-repo-strategy.md # 🆕 3시나리오 Proposed
    └── ADR-012-cmek-pitr-accepted-risk.md # 🆕 수용 리스크
```

### 평가 (11)
```
proving-grounds/
├── harnesses/gcp-infra-architect.harness.md
└── evals/gcp-infra-architect/
    ├── test-cases.md                    # TC-1~5
    ├── report.md                        # v1.0
    ├── report-v1.1.md                   # v1.1
    ├── report-v1.2.md                   # v1.2
    └── results/
        ├── baseline/TC-{1..5}.md        # 5
        └── with-skill/
            ├── TC-{1..5}.md             # v1.0/v1.1 혼합
            ├── TC-{1,3}-v1.1.md         # v1.1 재검증
            └── TC-2-v1.2-run{1,2,3}.md  # v1.2 일관성
```

---

## 4. 배포 체크리스트 (C 단계 재개 시)

### 4-1. 에이전트 배포 (C-1)

**대상**: `anvil/agents/gcp-infra-architect/` 전체
**목적지**: `pasta-japan-server/.claude/agents/` (또는 글로벌 레포)
**방법**: `/forge-deploy` 커맨드 활용 가능

```bash
# 참조용 — 실제 실행은 forge-deploy 커맨드 내에서
cp -r anvil/agents/gcp-infra-architect \
  /Users/kakao/workplace-kakao/global/pasta-japan/server/pasta-japan-server/.claude/agents/
```

확인:
- [ ] `.claude/agents/` 배포 경로 존재 확인 (이미 존재: pasta-japan-server)
- [ ] INDEX.md Deploy Registry에 pasta-japan-server 등록 업데이트
- [ ] 배포 후 pasta 레포에서 `@gcp-infra-architect` 호출 동작 확인
- [ ] anvil/INDEX.md의 Deploy Registry에 동기화 상태 기록

### 4-2. 설계안 배포 (C-2)

**대상**: `docs/infra-design/pasta-global-expansion-v0.1/` 9개 파일
**목적지**: 사용자 결정 (pasta 레포 docs/? 별도 위키?)
**주의**: **v0.2는 여전히 Draft**. 배포 전 팀 리뷰 권고

확인:
- [ ] Q1(글로벌 레포 시나리오) 팀 논의 결과 반영 → ADR-011 확정
- [ ] CONTEXT.md §8 가정 10개 재확인 (확인된 사실로 승격)
- [ ] 배포 경로 결정 후 이관

### 4-3. 글로벌 레포 탄생 시

사용자 언급: "아마 글로벌 버전 하나 더 나올 것, 리포 기준으로 진행"

**글로벌 레포 생성 시 즉시 해야 할 것**:
- [ ] `.claude/agents/` 디렉토리 생성 + 에이전트 복사
- [ ] `.claude/rules/` (pasta-rules 연결)
- [ ] `.claude/settings.local.json` 참고
- [ ] Terraform `infra/` 디렉토리 (ADR-005 구조)
- [ ] GitHub Actions + Workload Identity Federation
- [ ] BAA 체결 상태 확인 (미국 진출 대비)

---

## 5. 메타 인사이트 (다른 에이전트 개선에 재사용 가능)

### 5-1. 에이전트 성능 극대화 사이클

```
v1.0 (초기) → 하네스 평가 → 원칙 추가 → v1.1 재검증 → 문제 식별
→ 결정 트리 명확화 → v1.2 일관성 검증 → 실전 배치 가능
```

**핵심 교훈**:
1. **Happy Path만으로는 부족** — Edge/Negative TC가 v1.1 효과의 50% 증명
2. **일관성 테스트(`--repeat 3`) 필수** — 방법론 불일치는 점수로 안 드러남
3. **원칙과 루브릭 충돌** 발생 시 **루브릭을 조정**해야 원칙 보존 (v1.2 루브릭 6a/6b 분할)
4. **요청 유형 감지 로직**이 에이전트 일관성의 결정타 — 다른 에이전트에도 이식 가능

### 5-2. Phase 1.5 "현황 파악" 원칙의 중요성

v0.1 → v0.2 재작성의 결정적 트리거는 **실제 gcloud 실행 결과**였다:
- 가정: "일본 단일, Cloud Run 단일 API, Postgres"
- 실제: **9 프로젝트 / 48 Cloud Run 서비스 / MySQL / CMEK 미적용**

→ **모든 설계 에이전트는 Phase 1.5 강제**를 디폴트로 해야 함.

### 5-3. 파트너 톤이 기술 품질보다 중요

하네스 TC-2 baseline이 AWS로 답한 사례는 **"프롬프트에 GCP라고 안 쓰여있어서"**가 아니라 **"에이전트의 도메인 고정 능력 부재"**가 원인. 에이전트는 **맥락 보존**이 핵심 가치.

---

## 6. 남은 의사결정 (사용자 보류)

| # | 항목 | 상태 |
|---|------|------|
| 1 | Q1 글로벌 레포 시나리오 (a/b/c) | **팀 논의 중** |
| 2 | Q2 CMEK/PITR 해결 타이밍 | Z (수용 리스크) + 완화책 4종 + 데드라인 |
| 3 | 미국 리전 선택 (`us-west1` vs `us-east4`) | Phase 2에서 사용자 분포 조사 후 확정 |
| 4 | 배포(C) 시점 | **사용자 "일괄 진행" 예정** |
| 5 | 글로벌 레포 실제 생성 시점 | 팀 결정 대기 |

---

## 7. 배포 재개 시 첫 명령 제안

```
@gcp-infra-architect 배포 재개하자. 
SESSION-SUMMARY.md §4 체크리스트 기반으로 진행해줘.
Q1 시나리오는 {a|b|c} 확정됐어.
```

에이전트가 자동으로:
1. `docs/infra-design/pasta-global-expansion-v0.1/SESSION-SUMMARY.md` Read
2. Q1 시나리오 따라 ADR-011 Accepted로 승격
3. 배포 체크리스트 순차 실행

---

## 8. 세션 메트릭

- **기간**: 2026-04-21 ~ 2026-04-22 (1.5일)
- **턴 수**: ~40+
- **에이전트 iteration**: 3회 (v1.0 → v1.1 → v1.2)
- **설계안 iteration**: 2회 (v0.1 → v0.2)
- **서브에이전트 실행**: 19개 (하네스 평가)
- **생성/수정 파일**: 30개
- **최종 점수**: **94.1/100 EXCELLENT**

---

*이 문서는 "배포 시 5분 안에 복귀 가능한 지도"로 작성됨. 더 상세한 history는 `report.md` / `report-v1.1.md` / `report-v1.2.md` 참조.*
