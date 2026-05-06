# Anvil INDEX - 컴포넌트 목록

## Skills

| 이름 | 버전 | 설명 | 상태 | 테스트 점수 | 경로 |
|------|------|------|------|------------|------|
| [prd-designer](skills/prd-designer/SKILL.md) | 1.1 | PRD 기획 요구사항 문서 작성 | **실전 배치 가능** | 100/100 (TC-1) | `skills/prd-designer/` |
| [tdd-designer](skills/tdd-designer/SKILL.md) | 1.3 | TDD 기술 설계 문서 작성 | **실전 배치 가능** | 100/100 (TC-1) | `skills/tdd-designer/` |
| [java-spring-coder](skills/java-spring-coder/SKILL.md) | 1.5 | Java Spring Boot 4-Tier 코드 생성·단위 테스트 구현 | **실전 배치 가능** (v1.5 회귀 PASS, FQCN 하드 가드레일 + AUTO FAIL #6 + TC-4 신규 PASS) | 95/100 평균 (TC-1 99 / TC-2 92 / TC-3 PASS / TC-4 94) | `skills/java-spring-coder/` |
| [self-code-reviewer](skills/self-code-reviewer/SKILL.md) | 1.5 | dev 기준 변경 코드 자체 리뷰 (FQCN 검출 + 19-arch-boundaries) | **실전 배치 가능** (v1.5 회귀 PASS 2026-05-06: TC-1 93 / TC-4 95) | 94/100 평균 (FQCN 자체 리뷰 단계 차단 동작) | `skills/self-code-reviewer/` |
| [pr-feedback-resolver](skills/pr-feedback-resolver/SKILL.md) | 1.4 | PR 피드백 수집·수정·push·답글 (사람 vs CodeRabbit 봇 호출 파라미터 분리) | **실전 배치 가능** (v1.4 회귀 PASS 2026-05-06: TC-1 95 / TC-3 94 — 매체 분기 sq-tone-writer 연계 정상) | 94.5/100 평균 | `skills/pr-feedback-resolver/` |
| [admin-prd-plan-designer](skills/admin-prd-plan-designer/SKILL.md) | 1.0 | Admin 모듈 전용 PRD/TDD/HYBRID 계획 문서 작성 (멀티턴 합의) | **실전 배치 가능** | 88/100 (TC-1) | `skills/admin-prd-plan-designer/` |
| [admin-thymeleaf-ui](skills/admin-thymeleaf-ui/SKILL.md) | 1.1 | Admin Thymeleaf SSR 화면 구현/수정 (AdminLTE, OAuth2/SecurityContext 격리 포함) | **실전 배치 가능** | 95.3/100 (v1.1 회귀: 94.7 → 95.3, TC-2 +2) | `skills/admin-thymeleaf-ui/` |
| [api-inventory-generator](skills/api-inventory-generator/SKILL.md) | 1.0 | @RestController 스캔 → API 전체 목록 자동 생성 | **실전 배치 가능** | 89/100 (TC-1) | `skills/api-inventory-generator/` |
| [java-layered-unit-testing](skills/java-layered-unit-testing/SKILL.md) | 1.1 | 4-Tier 계층별 단위 테스트 작성 (FQCN 절대 금지 + AUTO FAIL #5) | **실전 배치 가능** (v1.1 회귀 PASS 2026-05-06: TC-1 92 / TC-4 95, 가드레일 사후 교정 동작 입증) | 93.5/100 평균 | `skills/java-layered-unit-testing/` |
| [chaos-test-planner](skills/chaos-test-planner/SKILL.md) | 1.1 | Chaos Monkey 장애 테스트 검토·계획·커맨드 생성 | **실전 배치 가능** | 93/100 (TC-1) | `skills/chaos-test-planner/` |
| [sq-tone-writer](skills/sq-tone-writer/SKILL.md) | 1.3 | 사용자 말투로 슬랙/PR/문서/리뷰 답글 작성 (사람 + CodeRabbit 봇 톤 분기) | **실전 배치 가능** (v1.3 회귀 PASS 2026-05-06: TC-1 95 / TC-bot 96 — 봇 톤 분기 완벽 동작) | 95.5/100 평균 | `skills/sq-tone-writer/` |
| [jira-bug-root-cause](skills/jira-bug-root-cause/SKILL.md) | 1.0 | Jira 버그 원인 규명 + QA 친화 코멘트 작성 | **실전 배치 가능** | 91/100 (TC-1) | `skills/jira-bug-root-cause/` |
| [chat-incident-report](skills/chat-incident-report/SKILL.md) | 1.0 | Google Chat 장애/CS 대응 메시지 (고정 6섹션 + CS 복붙 품질) | **실전 배치 가능** | 95/100 (3/3 PASS, Baseline +58.7점, TC-3 AUTO FAIL 4건 방어) | `skills/chat-incident-report/` |
| [sq-today-reviewer](skills/sq-today-reviewer/SKILL.md) | 0.1 | 하루 Claude 작업 총체 리뷰 → 놓친 학습·공부 주제·반복 실수·소양·내일 액션 6섹션 성장 리포트 | **테스트 대기** | - | `skills/sq-today-reviewer/` |
| [git-pr](skills/git-pr/SKILL.md) | 0.2 | PR 생성/갱신 — 사람 친화 표현 + 표 위주 + 100~200줄 양식 (commands/git-pr.md에서 승격, forge 일반화) | **실전 배치 가능** (일관성 미검증 — `--repeat 3` 권장) | 95.25/100 (TC-1 94 / TC-2 96 / TC-3 93 / TC-4 98) | `skills/git-pr/` |

## Agents

| 이름 | 버전 | 설명 | 상태 | 테스트 점수 | 경로 |
|------|------|------|------|------------|------|
| [gcp-infra-architect](agents/gcp-infra-architect/gcp-infra-architect.md) | 1.2 | GCP 특화 글로벌 인프라 설계·검토 파트너 (헬스케어 4개국 규제 + Terraform IaC + Phase 1.5 + 멀티턴·풀패키지 결정 트리) | **실전 배치 가능 (완전 검증 + 일관성 PASS)** | 94.1/100 (v1.2, TC-2 3회 편차 4점, 방법론 통일 확보) | `agents/gcp-infra-architect/` |

## Commands

| 이름 | 버전 | 트리거 | 설명 | 배포 | 경로 |
|------|------|--------|------|------|------|
| [git-branch](commands/git-branch.md) | 1.0 | `/git-branch` | 프로젝트 브랜치 전략에 따라 작업 브랜치 생성 | ✓ | `commands/git-branch.md` |
| [git-commit](commands/git-commit.md) | 1.1 | `/git-commit` | 한국어 Conventional Commits 커밋 생성 | ✓ | `commands/git-commit.md` |
| [git-pr](commands/git-pr.md) | 2.0 | `/git-pr` | **스킬로 승격** — `skills/git-pr/SKILL.md`의 호환용 별칭 | ✓ | `commands/git-pr.md` |
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
| pasta-japan-server | `/Users/kakao/workplace-kakao/global/pasta-japan/server/pasta-japan-server` | 2026-04-28 (git-pr 0.2 재배포; 역수입 동기화: 2026-04-27) |

### pasta-japan-server 배포 현황

| 컴포넌트 | 유형 | 배포 버전 | forge 최신 | 상태 |
|---------|------|----------|-----------|------|
| prd-designer | skill | 1.1 | 1.1 | 동기화 |
| tdd-designer | skill | 1.3 | 1.3 | 동기화 |
| java-spring-coder | skill | 1.4 | 1.5 | **재배포 필요** (v1.5 회귀 PASS 완료: 2026-04-29, 95/100 평균. PR #527 FQCN 가드레일 검증) |
| self-code-reviewer | skill | 1.4 | 1.5 | **재배포 필요** (v1.5 회귀 PASS 2026-05-06: 94/100 평균. FQCN 검출 + 19-arch-boundaries 추가) |
| pr-feedback-resolver | skill | 1.3 | 1.4 | **재배포 필요** (v1.4 회귀 PASS 2026-05-06: 94.5/100 평균. 봇/사람 매체 분기 동작) |
| git-branch | command | 1.0 | 1.0 | 동기화 |
| git-commit | command | 1.1 | 1.1 | 동기화 |
| git-pr | command | 2.0 (별칭) | 2.0 (별칭) | 동기화 (2026-04-27 skill 승격) |
| git-pr | skill | 0.2 | 0.2 | 동기화 (2026-04-28 재배포; EXCELLENT 95.25 평가 통과 후, references/example-pr-551.md 포함) |
| git-worktree-add | command | 1.0 | 1.0 | 동기화 |
| git-worktree-remove | command | 1.0 | 1.0 | 동기화 |
| forge-upstream | command | 1.0 | 1.0 | 동기화 |
| admin-prd-plan-designer | skill | 1.0 | 1.0 | 동기화 |
| admin-thymeleaf-ui | skill | 1.1 | 1.1 | 동기화 (2026-04-27 역수입: OAuth2/SecurityContext 격리 섹션) |
| api-inventory-generator | skill | 1.0 | 1.0 | 동기화 |
| java-layered-unit-testing | skill | 1.0 | 1.1 | **재배포 필요** (v1.1 회귀 PASS 2026-05-06: 93.5/100 평균. FQCN 절대 금지 + AUTO FAIL #5) |
| flyway | command | 1.0 | 1.0 | 동기화 |
| db-migration | command | 1.0 | 1.0 | 동기화 |
| chaos-test-planner | skill | 1.1 | 1.1 | 동기화 |
| sq-tone-writer | skill | 1.2 | 1.3 | **재배포 필요** (v1.3 회귀 PASS 2026-05-06: 95.5/100 평균. CodeRabbit 봇 톤 분기 완벽 동작) |
| jira-bug-root-cause | skill | 1.0 | 1.0 | 동기화 |
| chat-incident-report | skill | 1.0 (실전) | 1.0 (역수입) | 동기화 (2026-04-22 역수입, 마스킹 — forge→pasta 배포 금지) |
| gcp-infra-architect | agent | 1.2 | 1.2 | 동기화 (2026-04-22 신규 배포) |
