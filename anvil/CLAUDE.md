# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

`anvil/`은 AI SQ Forge의 **컴포넌트 저장소**다. Claude Code용 Skills, Agents, Commands, Skill Chains, Dispatchers를 보관한다. 이 디렉토리의 모든 파일은 마크다운 기반이며, 실행 코드는 없다.

## 아키텍처

```
anvil/
├── skills/{name}/        # SKILL.md 기반 독립 작업 단위 (자동 트리거)
├── agents/{name}/        # AGENT.md 기반 전문가 페르소나
├── commands/{name}.md    # 슬래시 커맨드 (플랫 파일, 파일명 = 트리거명)
├── skill-chains/{name}/  # 여러 스킬/커맨드를 엮은 워크플로
├── dispatchers/{name}/   # 요청을 분석해 적절한 컴포넌트로 라우팅
└── INDEX.md              # 전체 컴포넌트 목록 및 상태 (실전 배치 가능 여부, 테스트 점수)
```

각 컴포넌트 폴더 구조:
```
{name}/
├── SKILL.md (or AGENT.md)   # 메인 정의 파일 (역할, 지침, 가드레일)
└── references/              # 상세 패턴/예시 (본문 400줄 초과 시 분리)
```

**예외 — Commands는 플랫 파일 구조:**
```
commands/
├── git-branch.md    # 파일명 = 커맨드명, 폴더 없이 .md 파일로 직접 배치
├── git-commit.md
└── git-pr.md
```
Commands는 `.claude/commands/` 디렉토리 심볼릭 링크로 통째 연결되므로, 파일명이 곧 슬래시 커맨드 트리거명이 된다 (`git-branch.md` → `/git-branch`). 폴더로 감싸지 않는다.

## 컴포넌트 작성 규칙

- **SKILL.md frontmatter**: `name`과 `description` 필수. description에 트리거 키워드를 포함해야 Claude Code가 자동 매칭한다.
- **본문 400줄 이내** 유지. 초과 시 `references/`로 분리한다.
- **하드 가드레일은 본문에 직접 기술** — references로 분리하지 않는다.
- **자기 검증 체크리스트 필수** — 스킬이 스스로 품질을 검증하는 장치.
- 블루프린트 참조: `forge/blueprints/{type}.blueprint.md`

## 컴포넌트 개발 워크플로

신규 컴포넌트를 만들 때 반드시 아래 순서를 따른다:

1. **설계**: `forge/protocols/design.md` — Q&A로 요구사항 확정 (즉시 구현 금지)
2. **초안**: `forge/blueprints/{type}.blueprint.md` 템플릿 기반 작성
3. **생성**: `anvil/{type}/{name}/`에 컴포넌트 배치
4. **등록**: `anvil/INDEX.md`에 추가
5. **테스트**: `forge/protocols/testing.md` — baseline vs with-skill 비교 테스트
6. **배치 판정**: Happy Path 100% PASS + Edge Case 70% 이상 → 실전 배치 가능

## 테스트

테스트 결과는 `proving-grounds/evals/{component-name}/`에 저장된다. 테스트 프로토콜은 `forge/protocols/testing.md` 참조.

테스트 통과 기준 (Quality Gate):
- Happy Path 100% PASS
- Edge Case 70% 이상 PASS
- 하드 가드레일 위반 0건
- Baseline 대비 정확도 또는 완성도 개선

## Git 컨벤션

이 프로젝트의 git 워크플로는 `commands/` 내 3개 커맨드로 정의되어 있다:

- **브랜치**: `api/{type}/{task-name}` 형식 (type: feat/refac/fix). base branch는 `dev`.
- **커밋**: 한국어 Conventional Commits. `refactor:` 대신 **`refac:`** 사용. 대괄호(`[API]`) 금지. Co-authored-by에 AI 정보 포함 금지.
- **PR**: target은 `dev`. 한국어로 작성. PR_TEMPLATE.md가 있으면 따른다.

## 실전 피드백 반영 (A/S)

실전 사용 후 문제 발견 시 `maintenance/feedback/{component-name}/`에 기록하고, `forge/protocols/maintenance.md` 프로토콜로 분석 및 개선한다. 동일 피드백 3회 이상 반복 시 `skill-creator` 활용을 검토한다.

## 공통 자원

스킬에서 프로젝트 규칙을 참조할 때는 `forge/common/pasta-rules/{파일명}` 경로를 사용한다 (인덱스: `00-rules-index.mdc`).
