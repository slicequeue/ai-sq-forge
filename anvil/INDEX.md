# Anvil INDEX - 컴포넌트 목록

## Skills

| 이름 | 버전 | 설명 | 상태 | 테스트 점수 | 경로 |
|------|------|------|------|------------|------|
| [prd-designer](skills/prd-designer/SKILL.md) | 1.1 | PRD 기획 요구사항 문서 작성 | **실전 배치 가능** | 100/100 (TC-1) | `skills/prd-designer/` |
| [tdd-designer](skills/tdd-designer/SKILL.md) | 1.3 | TDD 기술 설계 문서 작성 | **실전 배치 가능** | 100/100 (TC-1) | `skills/tdd-designer/` |
| [java-spring-coder](skills/java-spring-coder/SKILL.md) | 1.3 | Java Spring Boot 4-Tier 코드 생성·단위 테스트 구현 | **실전 배치 가능** | 100/100 (TC-1) | `skills/java-spring-coder/` |
| [self-code-reviewer](skills/self-code-reviewer/SKILL.md) | 1.3 | dev 기준 변경 코드 자체 리뷰 (읽기 전용) | **실전 배치 가능** | 95/100 (TC-1) | `skills/self-code-reviewer/` |
| [pr-feedback-resolver](skills/pr-feedback-resolver/SKILL.md) | 1.1 | PR 피드백 수집·수정·push·답글 | **실전 배치 가능** | 95/100 (TC-1) | `skills/pr-feedback-resolver/` |
| [admin-prd-plan-designer](skills/admin-prd-plan-designer/SKILL.md) | 1.0 | Admin 모듈 전용 PRD/TDD/HYBRID 계획 문서 작성 (멀티턴 합의) | **실전 배치 가능** | 88/100 (TC-1) | `skills/admin-prd-plan-designer/` |
| [admin-thymeleaf-ui](skills/admin-thymeleaf-ui/SKILL.md) | 1.0 | Admin Thymeleaf SSR 화면 구현/수정 (AdminLTE) | **실전 배치 가능** | 95/100 (TC-1) | `skills/admin-thymeleaf-ui/` |
| [api-inventory-generator](skills/api-inventory-generator/SKILL.md) | 1.0 | @RestController 스캔 → API 전체 목록 자동 생성 | **실전 배치 가능** | 89/100 (TC-1) | `skills/api-inventory-generator/` |
| [java-layered-unit-testing](skills/java-layered-unit-testing/SKILL.md) | 1.0 | 4-Tier 계층별 단위 테스트 작성 (Domain/App/Web/Infra) | **실전 배치 가능** | 91/100 (TC-1) | `skills/java-layered-unit-testing/` |
| [chaos-test-planner](skills/chaos-test-planner/SKILL.md) | 1.1 | Chaos Monkey 장애 테스트 검토·계획·커맨드 생성 | **실전 배치 가능** | 93/100 (TC-1) | `skills/chaos-test-planner/` |
| [sq-tone-writer](skills/sq-tone-writer/SKILL.md) | 1.1 | 사용자 말투로 슬랙/PR/문서 작성 (SQ 톤 프로파일) | **실전 배치 가능** | 97/100 (TC-1) | `skills/sq-tone-writer/` |

## Agents

(아직 없음)

## Commands

| 이름 | 버전 | 트리거 | 설명 | 배포 | 경로 |
|------|------|--------|------|------|------|
| [git-branch](commands/git-branch.md) | 1.0 | `/git-branch` | 프로젝트 브랜치 전략에 따라 작업 브랜치 생성 | ✓ | `commands/git-branch.md` |
| [git-commit](commands/git-commit.md) | 1.1 | `/git-commit` | 한국어 Conventional Commits 커밋 생성 | ✓ | `commands/git-commit.md` |
| [git-pr](commands/git-pr.md) | 1.0 | `/git-pr` | dev 대상 PR 생성/업데이트 | ✓ | `commands/git-pr.md` |
| [eval-harness](commands/eval-harness.md) | 1.0 | `/eval-harness` | 컴포넌트 자동 평가 하네스 실행 (6축 채점) | forge 전용 | `commands/eval-harness.md` |
| [git-worktree-add](commands/git-worktree-add.md) | 1.0 | `/git-worktree-add` | 병렬 작업용 git worktree 생성 | ✓ | `commands/git-worktree-add.md` |
| [git-worktree-remove](commands/git-worktree-remove.md) | 1.0 | `/git-worktree-remove` | git worktree 안전 제거 및 정리 | ✓ | `commands/git-worktree-remove.md` |
| [forge-deploy](commands/forge-deploy.md) | 1.1 | `/forge-deploy` | Forge 컴포넌트를 실전 프로젝트에 이식 | forge 전용 | `commands/forge-deploy.md` |
| [forge-upstream](commands/forge-upstream.md) | 1.0 | `/forge-upstream` | 실전 프로젝트에서 개선된 컴포넌트를 Forge로 upstream | ✓ | `commands/forge-upstream.md` |
| [flyway](commands/flyway.md) | 1.0 | `/flyway` | Flyway 마이그레이션 실행 및 상태 확인 | ✓ | `commands/flyway.md` |
| [db-migration](commands/db-migration.md) | 1.0 | `/db-migration` | Flyway DB 마이그레이션 SQL 작성 | ✓ | `commands/db-migration.md` |

## Skill Chains

| 이름 | 버전 | 설명 | 상태 | 테스트 점수 | 경로 |
|------|------|------|------|------------|------|
| [git-workflow-bcp](skill-chains/git-workflow-bcp/CHAIN.md) | 1.0 | Branch → Commit(논리 분할) → PR 일괄 실행 | **실전 배치 가능** | 93/100 (TC-1) | `skill-chains/git-workflow-bcp/` |

## Dispatchers

(아직 없음)

---

## Deploy Registry

컴포넌트가 배포된 프로젝트 연결 정보. 스킬 개선 시 연결된 프로젝트에 재배포 여부를 확인한다.

| 프로젝트 | 경로 | 최종 배포일 |
|---------|------|-----------|
| pasta-japan-server | `/Users/kakao/workplace-kakao/global/pasta-japan/server/pasta-japan-server` | 2026-04-17 |

### pasta-japan-server 배포 현황

| 컴포넌트 | 유형 | 배포 버전 | forge 최신 | 상태 |
|---------|------|----------|-----------|------|
| prd-designer | skill | 1.1 | 1.1 | 동기화 |
| tdd-designer | skill | 1.3 | 1.3 | 동기화 |
| java-spring-coder | skill | 1.3 | 1.3 | 동기화 |
| self-code-reviewer | skill | 1.3 | 1.3 | 동기화 |
| pr-feedback-resolver | skill | 1.1 | 1.1 | 동기화 |
| git-branch | command | 1.0 | 1.0 | 동기화 |
| git-commit | command | 1.1 | 1.1 | 동기화 |
| git-pr | command | 1.0 | 1.0 | 동기화 |
| git-worktree-add | command | 1.0 | 1.0 | 동기화 |
| git-worktree-remove | command | 1.0 | 1.0 | 동기화 |
| forge-upstream | command | 1.0 | 1.0 | 동기화 |
| admin-prd-plan-designer | skill | 1.0 | 1.0 | 동기화 |
| admin-thymeleaf-ui | skill | 1.0 | 1.0 | 동기화 |
| api-inventory-generator | skill | 1.0 | 1.0 | 동기화 |
| java-layered-unit-testing | skill | 1.0 | 1.0 | 동기화 |
| flyway | command | 1.0 | 1.0 | 동기화 |
| db-migration | command | 1.0 | 1.0 | 동기화 |
| chaos-test-planner | skill | 1.1 | 1.1 | 동기화 |
