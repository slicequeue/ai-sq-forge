# AI SQ Forge - 인큐베이터 & 훈련소

이 프로젝트는 AI 스킬, 에이전트, 커맨드, 스킬체인, 디스패처를 개발하고 테스트하며 개선하는 대장간(Forge)이다.

## 핵심 원칙

1. **품질 우선**: 모든 컴포넌트는 테스트를 통과해야 실전 배치 가능
2. **문답 설계**: 새 컴포넌트 생성 시 반드시 `forge/protocols/design.md` 프로토콜을 따라 사용자와 Q&A를 거친 후 구현
3. **측정 가능**: 테스트 시 baseline(스킬 미사용) vs with-skill 비교, 토큰 사용량/소요시간 기록
4. **지속 개선**: 실전 사용 후 피드백은 `maintenance/feedback/`에 기록하고 컴포넌트에 반영

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
| `forge/common/pasta-rules/` | pasta-japan 프로젝트 규칙 원본 (12개 .mdc 파일). 인덱스: `00-rules-index.mdc` |

스킬에서 프로젝트 규칙을 참조할 때는 `forge/common/pasta-rules/{파일명}` 경로를 사용한다.

## 워크플로

### 1. 신규 컴포넌트 개발
1. `forge/protocols/design.md` → Q&A로 요구사항 확정
2. `forge/blueprints/{type}.blueprint.md` → 템플릿 기반 초안 작성
3. `anvil/{type}/{name}/` → 컴포넌트 생성
4. `forge/protocols/testing.md` → 수동 테스트 또는 `/eval-harness` 자동 테스트
5. 테스트 통과 → 하네스 정의 작성 (`proving-grounds/harnesses/`) → 실전 배치 가능 상태

### 2. 실전 배치 후 개선 (A/S)
1. 실전 사용 대화 로그를 `maintenance/feedback/{component-name}/` 에 저장
2. `forge/protocols/maintenance.md` 프로토콜로 분석 & 개선
3. 개선 후 재테스트 (`/eval-harness {name} --skip-baseline`로 빠른 재검증)

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
