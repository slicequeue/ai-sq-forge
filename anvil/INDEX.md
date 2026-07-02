# Anvil INDEX - 컴포넌트 목록

## Skills

> **배포정책**: `일반`(양방향), `역수입전용`(실전→forge만, 마스킹 보존), `forge전용`(배포 안 함)

| 이름 | 버전 | 설명 | 상태 | 배포정책 | 테스트 점수 | 경로 |
|------|------|------|------|---------|------------|------|
| [prd-designer](skills/prd-designer/SKILL.md) | 1.2 | PRD 기획 요구사항 문서 작성 (v1.2: Phase 1.5 현황 파악 + 멀티턴·풀패키지 결정 트리 + 확인vs가정 분리) | **회귀 평가 권장** (v1.2 패턴 이식 — `/eval-harness prd-designer --skip-baseline`) | 일반 | 100/100 (TC-1, v1.1 기준) | `skills/prd-designer/` |
| [tdd-designer](skills/tdd-designer/SKILL.md) | 1.4 | TDD 기술 설계 문서 작성 (v1.4: Phase 0.5 현황 파악 + 결정 트리 + 자기 검증 v2.0) | **회귀 평가 권장** (v1.4 패턴 이식 — `/eval-harness tdd-designer --skip-baseline`) | 일반 | 100/100 (TC-1, v1.3 기준) | `skills/tdd-designer/` |
| [java-spring-coder](skills/java-spring-coder/SKILL.md) | 1.10 | Java Spring Boot 4-Tier 코드 생성·단위 테스트 구현 (v1.10: 외부 API DTO 시간 방어 + 공용 모듈 @Entity 회피 + 캐시 3층 폴백 + 신규 패키지 4-Tier 강제 + 예외 로깅 표준) | **회귀 평가 권장** (v1.10 사례 반영) | 일반 | 95/100 평균 (v1.5 기준) | `skills/java-spring-coder/` |
| [self-code-reviewer](skills/self-code-reviewer/SKILL.md) | 1.10 | dev 기준 변경 코드 자체 리뷰 (v1.10: Bean Qualifier cross-module 3회 재발 방지 + 인터페이스 구현체 모듈 확인 + 임시 진단 로그 후속 제거 강제) | **회귀 평가 권장** (v1.10 사례 반영) | 일반 | 94/100 평균 (v1.5 기준) | `skills/self-code-reviewer/` |
| [pr-feedback-resolver](skills/pr-feedback-resolver/SKILL.md) | 1.5 | PR 피드백 수집·수정·push·답글 (v1.5: 자기 검증 v2.0 — PR 컨텍스트 현황 파악 + 봇/사람 분기 근거 기록) | **회귀 평가 권장** (v1.5 패턴 이식) | 일반 | 94.5/100 평균 (v1.4 기준) | `skills/pr-feedback-resolver/` |
| [admin-prd-plan-designer](skills/admin-prd-plan-designer/SKILL.md) | 1.1 | Admin 모듈 전용 PRD/TDD/HYBRID 계획 문서 작성 (v1.1: Phase 0.3 admin 모듈 현황 파악 + 멀티턴/풀패키지 결정 트리) | **회귀 평가 권장** (v1.1 패턴 이식) | 일반 | 88/100 (v1.0 기준) | `skills/admin-prd-plan-designer/` |
| [admin-thymeleaf-ui](skills/admin-thymeleaf-ui/SKILL.md) | 1.2 | Admin Thymeleaf SSR 화면 구현/수정 (v1.2: 자기 검증 v2.0 — 기존 패턴 사전 스캔 + 영향도 grep 확인) | **회귀 평가 권장** (v1.2 패턴 이식) | 일반 | 95.3/100 (v1.1 기준) | `skills/admin-thymeleaf-ui/` |
| [api-inventory-generator](skills/api-inventory-generator/SKILL.md) | 1.1 | @RestController 스캔 → API 전체 목록 자동 생성 (v1.1: 자기 검증 v2.0 — 스캔 범위 명시 + 추정 vs 확정 분리) | **회귀 평가 권장** (v1.1 패턴 이식) | 일반 | 89/100 (v1.0 기준) | `skills/api-inventory-generator/` |
| [java-layered-unit-testing](skills/java-layered-unit-testing/SKILL.md) | 1.3 | 4-Tier 계층별 단위 테스트 작성 (v1.3: @MockBean 빈 이름 상수화 강제 + enum 인라인 FQCN 확장 검사) | **회귀 평가 권장** (v1.3 사례 반영) | 일반 | 93.5/100 평균 (v1.1 기준) | `skills/java-layered-unit-testing/` |
| [chaos-test-planner](skills/chaos-test-planner/SKILL.md) | 1.2 | Chaos Monkey 장애 테스트 검토·계획·커맨드 생성 (v1.2: Phase 1.5 환경 현황 파악 + 자기 검증 6항목) | **회귀 평가 권장** (v1.2 패턴 이식) | 일반 | 93/100 (v1.1 기준) | `skills/chaos-test-planner/` |
| [sq-tone-writer](skills/sq-tone-writer/SKILL.md) | 1.4 | 사용자 말투로 슬랙/PR/문서/리뷰 답글 작성 (v1.4: 자기 검증 v2.0 — 수신자 파악 근거 + 봇/사람 분류 근거 + 가정 답변 표기) | **회귀 평가 권장** (v1.4 패턴 이식) | 일반 | 95.5/100 평균 (v1.3 기준) | `skills/sq-tone-writer/` |
| [jira-bug-root-cause](skills/jira-bug-root-cause/SKILL.md) | 1.1 | Jira 버그 원인 규명 + QA 친화 코멘트 작성 (v1.1: 자기 검증 v2.0 — 확인 vs 가정 분리 + 운영 트래픽 출처 명시 + 재현 조건 검증) | **회귀 평가 권장** (v1.1 패턴 이식) | 일반 | 91/100 (v1.0 기준) | `skills/jira-bug-root-cause/` |
| [chat-incident-report](skills/chat-incident-report/SKILL.md) | 1.0 | Google Chat 장애/CS 대응 메시지 (고정 6섹션 + CS 복붙 품질) | **실전 배치 가능** | **역수입전용** | 95/100 (3/3 PASS, Baseline +58.7점, TC-3 AUTO FAIL 4건 방어) | `skills/chat-incident-report/` |
| [sq-today-reviewer](skills/sq-today-reviewer/SKILL.md) | 0.3 | 하루 Claude 작업 총체 리뷰 → 놓친 학습·공부 주제(실무/CS이론 2트랙)·반복 실수·소양·내일 액션 6섹션 성장 리포트 | **테스트 대기** (harness/test-cases 작성됨, `/eval-harness` 미실행) | 일반 | - | `skills/sq-today-reviewer/` |
| [git-pr](skills/git-pr/SKILL.md) | 0.2 | PR 생성/갱신 — 사람 친화 표현 + 표 위주 + 100~200줄 양식 (commands/git-pr.md에서 승격, forge 일반화) | **실전 배치 가능** (일관성 미검증 — `--repeat 3` 권장) | 일반 | 95.25/100 (TC-1 94 / TC-2 96 / TC-3 93 / TC-4 98) | `skills/git-pr/` |
| [tolgee](skills/tolgee/SKILL.md) | 0.2 | Tolgee i18n 콘솔과 properties 파일 동기화 (v0.2: 4파일 동시 갱신 강제 + en 카피 품질 가드 + Java 코드 Locale 함정 안내) | **테스트 대기** (하네스·루브릭 미작성). 2026-06-24 회귀 검증: 사고 #624에서 4파일 동기화 FAIL — pasta 배포 v0.1 부채 원인 | 일반 | - | `skills/tolgee/` |
| [safe-mass-rename](skills/safe-mass-rename/SKILL.md) | 0.1 | 전역 식별자(enum·상수·설정 키·API 필드명) 대형 리네임 안전 오케스트레이션 (6단계 순서 강제 + 롤백 브랜치 + grep 검증 + 후방향 호환) | **테스트 대기** (하네스·루브릭 미작성) — 2026-07-02 Freemium 리네임 사이클 반영 신설 | 일반 | - | `skills/safe-mass-rename/` |

## Agents

| 이름 | 버전 | 설명 | 상태 | 배포정책 | 테스트 점수 | 경로 |
|------|------|------|------|---------|------------|------|
| [gcp-infra-architect](agents/gcp-infra-architect/gcp-infra-architect.md) | 1.2 | GCP 특화 글로벌 인프라 설계·검토 파트너 (헬스케어 4개국 규제 + Terraform IaC + Phase 1.5 + 멀티턴·풀패키지 결정 트리) | **실전 배치 가능 (완전 검증 + 일관성 PASS)** | 일반 | 94.1/100 (v1.2, TC-2 3회 편차 4점, 방법론 통일 확보) | `agents/gcp-infra-architect/` |
| [acceptance-tester](agents/acceptance-tester/acceptance-tester.md) | 0.2 | 인수 테스트·통합 테스트 (v0.2: testAcceptance 사각지대 인지 + OAuth MockBean 이름 명시 + @TestConfiguration 중복 제거 + @Nested vs flat 정책) | **테스트 대기** (평가 루브릭·하네스 미작성) | 일반 | - | `agents/acceptance-tester/` |
| [apidog-mock-api-generator](agents/apidog-mock-api-generator/apidog-mock-api-generator.md) | 0.2 | Apidog 스펙 → Mock Controller (v0.2: Phase 1.5 현황 파악 + 응답 DTO 확장 호환성 + Mock 데이터 표식) | **테스트 대기** (평가 루브릭·하네스 미작성) | 일반 | - | `agents/apidog-mock-api-generator/` |
| [bug-analyzer](agents/bug-analyzer/bug-analyzer.md) | 0.3 | 스택트레이스 분석 (v0.3: OAuth2 refresh 사각지대 카탈로그 3패턴 추가 + WebClient 4xx 룰과 층위 분리 — Dexcom #594 사례) | **테스트 대기** | 일반 | - | `agents/bug-analyzer/` |
| [coding-implementer](agents/coding-implementer/coding-implementer.md) | 0.4 | **개발 사이클 오케스트레이터** — TDD 받아 브랜치→Phase별 구현·테스트·자체리뷰·커밋→인수 테스트→PR 준비까지 한 호출 자율 진행 (v0.4: Phase 0 신규 패키지 4-Tier 강제 + Phase 3-4 Qualifier cross-module + Phase 3-6 커밋 세분화 원칙) | **테스트 대기** (본질 차별화 격상 — 평가 루브릭·하네스 미작성) | 일반 | - | `agents/coding-implementer/` |
| [prd-plan-designer](agents/prd-plan-designer/prd-plan-designer.md) | 0.2 | PRD + TDD 통합 산출 (v0.2: 3개 PRD 스킬과 경계 명시 + PRD는 prd-designer / TDD는 tdd-designer 위임). 통합 검토 필요 | **테스트 대기** | 일반 | - | `agents/prd-plan-designer/` |

## Commands

| 이름 | 버전 | 트리거 | 설명 | 배포정책 | 경로 |
|------|------|--------|------|---------|------|
| [git-branch](commands/git-branch.md) | 1.0 | `/git-branch` | 프로젝트 브랜치 전략에 따라 작업 브랜치 생성 | 일반 | `commands/git-branch.md` |
| [git-commit](commands/git-commit.md) | 1.1 | `/git-commit` | 한국어 Conventional Commits 커밋 생성 | 일반 | `commands/git-commit.md` |
| [git-pr](commands/git-pr.md) | 2.0 | `/git-pr` | **스킬로 승격** — `skills/git-pr/SKILL.md`의 호환용 별칭 | 일반 | `commands/git-pr.md` |
| [eval-harness](commands/eval-harness.md) | 1.0 | `/eval-harness` | 컴포넌트 자동 평가 하네스 실행 (6축 채점) | **forge전용** | `commands/eval-harness.md` |
| [git-worktree-add](commands/git-worktree-add.md) | 1.0 | `/git-worktree-add` | 병렬 작업용 git worktree 생성 | 일반 | `commands/git-worktree-add.md` |
| [git-worktree-remove](commands/git-worktree-remove.md) | 1.0 | `/git-worktree-remove` | git worktree 안전 제거 및 정리 | 일반 | `commands/git-worktree-remove.md` |
| [forge-deploy](commands/forge-deploy.md) | 1.2 | `/forge-deploy` | Forge 컴포넌트를 실전 프로젝트에 이식 (경로 리매핑 자동화 + 배포정책 가드) | **forge전용** | `commands/forge-deploy.md` |
| [forge-upstream](commands/forge-upstream.md) | 1.0 | `/forge-upstream` | 실전 프로젝트에서 개선된 컴포넌트를 Forge로 upstream | 일반 | `commands/forge-upstream.md` |
| [flyway](commands/flyway.md) | 1.0 | `/flyway` | Flyway 마이그레이션 실행 및 상태 확인 | 일반 | `commands/flyway.md` |
| [db-migration](commands/db-migration.md) | 1.0 | `/db-migration` | Flyway DB 마이그레이션 SQL 작성 | 일반 | `commands/db-migration.md` |

## Skill Chains

| 이름 | 버전 | 설명 | 상태 | 배포정책 | 테스트 점수 | 경로 |
|------|------|------|------|---------|------------|------|
| [git-workflow-bcp](skill-chains/git-workflow-bcp/CHAIN.md) | 1.0 | Branch → Commit(논리 분할) → PR 일괄 실행 | **실전 배치 가능** | 일반 | 93/100 (TC-1) | `skill-chains/git-workflow-bcp/` |

## Dispatchers

(아직 없음)

---

## Deploy Registry

컴포넌트가 배포된 프로젝트 연결 정보. 스킬 개선 시 연결된 프로젝트에 재배포 여부를 확인한다.

| 프로젝트 | 경로 | 최종 배포일 |
|---------|------|-----------|
| pasta-japan-server | `/Users/kakao/workplace-kakao/global/pasta-japan/server/pasta-japan-server` | 2026-05-06 (PR #527 FQCN 가드레일 + 봇 톤 분기 5건 일괄 재배포). 2026-05-19 forge-upstream 6건 역수입 (agents 5 + skill tolgee). **2026-07-02 부채 확장**: 6월 사고 사이클 반영으로 forge 5건 강화(java-spring-coder 1.10 / self-code-reviewer 1.10 / bug-analyzer 0.3 / coding-implementer 0.4 / safe-mass-rename 0.1 신설) → pasta 배포 미반영, `/forge-deploy --sync` 대기 |
| poc-meal-recommender | `/Users/kakao/workplace-kakao/global/pasta-japan/work/poc-meal-recommender` | 2026-05-14 (POC 미니 세트 신규 배포: 스킬 8 + 커맨드 6 + rules 20) |

### pasta-japan-server 배포 현황

| 컴포넌트 | 유형 | 배포 버전 | forge 최신 | 상태 |
|---------|------|----------|-----------|------|
| prd-designer | skill | 1.1 | 1.1 | 동기화 |
| tdd-designer | skill | 1.3 | 1.3 | 동기화 |
| java-spring-coder | skill | 1.5 | **1.10** | **재배포 필요** (2026-07-02 사이클: 외부 API DTO 시간 방어 + 공용 모듈 @Entity 회피 + 캐시 3층 폴백 + 신규 패키지 4-Tier 강제 + 예외 로깅 표준. v1.6~1.10 5회 bump 미반영) |
| self-code-reviewer | skill | 1.5 | **1.10** | **재배포 필요** (2026-07-02 사이클: Qualifier cross-module 3회 재발 방지 + 인터페이스 구현체 모듈 확인 + 임시 진단 로그 후속 제거. v1.6~1.10 5회 bump 미반영) |
| pr-feedback-resolver | skill | 1.4 | 1.4 | 동기화 (2026-05-06 재배포: 봇/사람 매체 분기 + sq-tone-writer 1.3 연계, 회귀 94.5/100) |
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
| java-layered-unit-testing | skill | 1.1 | 1.1 | 동기화 (2026-05-06 재배포: FQCN 절대 금지 + AUTO FAIL #5, 회귀 93.5/100) |
| flyway | command | 1.0 | 1.0 | 동기화 |
| db-migration | command | 1.0 | 1.0 | 동기화 |
| chaos-test-planner | skill | 1.1 | 1.1 | 동기화 |
| sq-tone-writer | skill | 1.3 | 1.3 | 동기화 (2026-05-06 재배포: CodeRabbit 봇 톤 분기 + tone-examples 100줄+, 회귀 95.5/100) |
| jira-bug-root-cause | skill | 1.0 | 1.0 | 동기화 |
| chat-incident-report | skill | 1.0 (실전) | 1.0 (역수입) | 동기화 (2026-04-22 역수입, 마스킹 — forge→pasta 배포 금지) |
| gcp-infra-architect | agent | 1.2 | 1.2 | 동기화 (2026-04-22 신규 배포) |
| tolgee | skill | 0.1 | 0.1 | **2026-05-19 forge-upstream 신규 역수입** (실전 전용 → forge 등록, 하네스 미작성) |
| acceptance-tester | agent | 0.1 | 0.1 | **2026-05-19 신규 역수입** (실전 전용 → forge 등록, 하네스 미작성) |
| apidog-mock-api-generator | agent | 0.1 | 0.1 | **2026-05-19 신규 역수입** |
| bug-analyzer | agent | 0.1 | **0.3** | **재배포 필요** (2026-07-02 v0.3: OAuth2 refresh 사각지대 카탈로그 3패턴) |
| coding-implementer | agent | 0.1 | **0.4** | **재배포 필요** (2026-07-02 v0.4: 개발 사이클 오케스트레이터 격상 + Phase 강화) |
| prd-plan-designer | agent | 0.1 | 0.1 | **2026-05-19 신규 역수입** — prd-designer/tdd-designer/admin-prd-plan-designer 스킬과 역할 중복 |
| safe-mass-rename | skill | - | **0.1** | **신규 forge 생성** (2026-07-02 Freemium 리네임 사이클 반영) — pasta 배포 대기 |

> **2026-05-19 동기화 부채**: forge 측 11개 스킬이 v1.2 패턴(Phase 1.5 + 결정 트리 + 자기 검증 v2.0)으로 일괄 업그레이드되어 pasta 배포 버전과 불일치 상태. 회귀 평가 통과 후 `/forge-deploy --sync` 권장. 또한 pasta SKILL.md 다수에 frontmatter 메타(version/last-modified/changelog)가 누락되어 있어 재배포 시 자동 복원.

### poc-meal-recommender 배포 현황

| 컴포넌트 | 유형 | 배포 버전 | forge 최신 | 상태 |
|---------|------|----------|-----------|------|
| prd-designer | skill | 1.1 | 1.1 | 동기화 (2026-05-14 신규) |
| tdd-designer | skill | 1.3 | 1.3 | 동기화 (2026-05-14 신규) |
| java-spring-coder | skill | 1.5 | 1.5 | 동기화 (2026-05-14 신규) |
| self-code-reviewer | skill | 1.5 | 1.5 | 동기화 (2026-05-14 신규) |
| pr-feedback-resolver | skill | 1.4 | 1.4 | 동기화 (2026-05-14 신규) |
| java-layered-unit-testing | skill | 1.1 | 1.1 | 동기화 (2026-05-14 신규) |
| sq-tone-writer | skill | 1.3 | 1.3 | 동기화 (2026-05-14 신규) |
| git-pr | skill | 0.2 | 0.2 | 동기화 (2026-05-14 신규) |
| git-branch | command | 1.0 | 1.0 | 동기화 (2026-05-14 신규) |
| git-commit | command | 1.1 | 1.1 | 동기화 (2026-05-14 신규) |
| git-pr | command | 2.0 (별칭) | 2.0 (별칭) | 동기화 (2026-05-14 신규) |
| git-worktree-add | command | 1.0 | 1.0 | 동기화 (2026-05-14 신규) |
| git-worktree-remove | command | 1.0 | 1.0 | 동기화 (2026-05-14 신규) |
| forge-upstream | command | 1.0 | 1.0 | 동기화 (2026-05-14 신규) |
