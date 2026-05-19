# AI SQ Forge - 인큐베이터 & 훈련소

이 프로젝트는 AI 스킬, 에이전트, 커맨드, 스킬체인, 디스패처를 개발하고 테스트하며 개선하는 대장간(Forge)이다.

## 핵심 원칙

1. **품질 우선**: 모든 컴포넌트는 테스트를 통과해야 실전 배치 가능
2. **하네스 필수**: 모든 스킬/에이전트는 반드시 하네스 정의(`proving-grounds/harnesses/`)와 평가 루브릭(`references/evaluation-rubric.md`)을 갖춰야 한다
3. **문답 설계**: 새 컴포넌트 생성 시 반드시 `forge/protocols/design.md` 프로토콜을 따라 사용자와 Q&A를 거친 후 구현
4. **측정 가능**: `/eval-harness`로 6축 자동 채점 (가드레일, 정확도, 행동패턴, 비교, 일관성, 효율성)
5. **지속 개선**: 실전 피드백 → 개선 → `/eval-harness --skip-baseline`로 재검증
6. **현황 파악 우선 (Phase 1.5)**: 설계·분석형 컴포넌트는 **가정 대신 실제 현황**으로 시작. 가능하면 읽기 전용 명령(`gcloud`, `find *.tf`, `grep` 등)으로 실제 상태 확보 후 설계 진행. 접근 불가 시 사용자에게 출력 요청. **"가정 10개 쓰고 진행"보다 "현황 확인 후 진행"**이 설계 신뢰도에 우수. ([증거: gcp-infra-architect v0.1 → v0.2 전면 재작성 사례](./docs/infra-design/pasta-global-expansion-v0.1/SESSION-SUMMARY.md))
7. **확인된 사실 vs 가정 분리**: 응답에 "확인된 것 vs 가정한 것"을 명시적으로 분리 표기. 가정 기반 결정은 재평가 트리거와 함께 기록.
8. **요청 유형 감지 (v2.0)**: "설계안/제출용/문서/deliverable/패키지/리뷰용" 키워드 감지 시 **풀패키지 default**. 단순 분석·논의는 멀티턴 점진. 애매할 때 풀패키지 + "턴별 분할 원하시면" 선택지 병기. ([근거: gcp-infra-architect v1.1 TC-2 일관성 이슈 v1.2에서 해결](./proving-grounds/evals/gcp-infra-architect/report-v1.2.md))

## 디렉토리 구조

```
forge/           → 메타 시스템 (블루프린트, 프로토콜, 공통 자원)
  forge/common/  → 프로젝트 공통 규칙/자원 (여러 스킬이 참조하는 원본)
anvil/           → 컴포넌트 저장소 (skills, agents, commands, skill-chains, dispatchers)
proving-grounds/ → 테스트 영역 (harnesses, evals, 결과 비교)
maintenance/     → A/S 영역 (실전 피드백, 개선 로그)
```

## 공통 자원 (forge/common/)

| 폴더 | 내용 |
|------|------|
| `forge/common/pasta-rules/` | pasta-japan 프로젝트 규칙 원본 (17개 .md 파일). 인덱스: `00-rules-index.md` |

스킬에서 프로젝트 규칙을 참조할 때는 `forge/common/pasta-rules/{파일명}` 경로를 사용한다.

## 워크플로

### 1. 신규 컴포넌트 개발
1. `forge/protocols/design.md` → Q&A로 요구사항 확정
2. **Phase 1.5 현황 파악** → 대상 프로젝트·시스템의 실제 상태 확보 (가정 제거)
3. `forge/blueprints/{type}.blueprint.md` → 템플릿 기반 초안 작성
4. `anvil/{type}/{name}/` → 컴포넌트 생성 (**`references/evaluation-rubric.md` 필수 포함**)
5. **하네스 정의 작성** → `proving-grounds/harnesses/{name}.harness.md` + `test-cases.md` 작성 (Happy 2 + Edge 1 + **Negative 1 필수**)
6. `/eval-harness {name}` → 6축 자동 채점 실행. **Happy Path 중 1개는 `--repeat 3` 일관성 테스트 권고**
7. 테스트 통과 + 일관성 PASS → `anvil/INDEX.md` 상태 업데이트 → 실전 배치 가능

### 2. 실전 배치 후 개선 (A/S)
1. 실전 사용 대화 로그를 `maintenance/feedback/{component-name}/`에 저장
2. `forge/protocols/maintenance.md` 프로토콜로 분석 & 개선
3. `/eval-harness {name} --skip-baseline`로 재검증 (하네스가 회귀 방지)

## 컴포넌트 유형

| 유형 | 설명 | 저장 위치 |
|------|------|-----------|
| **Skill** | SKILL.md 기반 독립 작업 단위 | `anvil/skills/{name}/` |
| **Agent** | 역할+지침+가드레일 전문가 페르소나 | `anvil/agents/{name}/` |
| **Command** | 슬래시 커맨드로 트리거되는 단위 작업 | `anvil/commands/{name}.md` (플랫 파일) |
| **Skill Chain** | 여러 스킬/커맨드를 엮은 워크플로 | `anvil/skill-chains/{name}/` |
| **Dispatcher** | 사용자 요청을 분석해 적절한 컴포넌트로 라우팅 | `anvil/dispatchers/{name}/` |

## 가드레일

- 컴포넌트 SKILL.md/AGENT.md가 과도하게 길어지면 → `references/` 하위로 분리
- 각 컴포넌트 폴더에는 반드시 INDEX.md(또는 SKILL.md 내 참조 인덱스) 포함
- 테스트 미통과 컴포넌트는 실전 배치 불가
- 하드 가드레일(절대 위반 불가 규칙)은 컴포넌트 본문에 직접 기술
