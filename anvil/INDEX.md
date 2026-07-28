# Anvil INDEX - 컴포넌트 목록

## Skills

> **배포정책**: `일반`(양방향), `역수입전용`(실전→forge만, 마스킹 보존), `forge전용`(배포 안 함)

| 이름 | 버전 | 설명 | 상태 | 배포정책 | 테스트 점수 | 경로 |
|------|------|------|------|---------|------------|------|
| [prd-designer](skills/prd-designer/SKILL.md) | 1.2 | PRD 기획 요구사항 문서 작성 (v1.2: Phase 1.5 현황 파악 + 멀티턴·풀패키지 결정 트리 + 확인vs가정 분리) | **회귀 평가 권장** (v1.2 패턴 이식 — `/eval-harness prd-designer --skip-baseline`) | 일반 | 100/100 (TC-1, v1.1 기준) | `skills/prd-designer/` |
| [tdd-designer](skills/tdd-designer/SKILL.md) | 1.4 | TDD 기술 설계 문서 작성 (v1.4: Phase 0.5 현황 파악 + 결정 트리 + 자기 검증 v2.0) | **회귀 평가 권장** (v1.4 패턴 이식 — `/eval-harness tdd-designer --skip-baseline`) | 일반 | 100/100 (TC-1, v1.3 기준) | `skills/tdd-designer/` |
| [java-spring-coder](skills/java-spring-coder/SKILL.md) | 1.13 | Java Spring Boot 4-Tier 코드 생성·단위 테스트 구현 (v1.13: Airbridge 아웃박스 패턴 + 재전송 배치 / v1.12: rubric 정정 / v1.11: Hibernate Session 오염 방지 3연타 + @ConditionalOnBean 회피 + 캐시 pub-sub + 어노테이션 인터셉터) | **회귀 통과 98.5/100** (2026-07-29 하네스 확장 후 재평가, TC 10/10 EXCELLENT. 이전 95 대비 +3.5) | 일반 | 98.5/100 (v1.13 재평가) | `skills/java-spring-coder/` |
| [self-code-reviewer](skills/self-code-reviewer/SKILL.md) | 2.0 | **공통 룰 + 관점 리뷰 오케스트레이션 안내** (v2.0 슬림화: KISA→secure-coding / WebClient·싱글톤·Soft-delete UNIQUE→performance / FQCN·Bean Qualifier·구현체 모듈→architecture 완전 이관. 잔존: @Profile·광범위 catch·Session 오염·입력 검증·i18n·임시 로그) | **회귀 통과 96/100** (2026-07-29 하네스 리팩터 후 재평가, TC 9/9. 이전 87.25 대비 +8.75) | 일반 | 96/100 (v2.0 재평가) | `skills/self-code-reviewer/` |
| [java-secure-coding-reviewer](skills/java-secure-coding-reviewer/SKILL.md) | 0.1 | **보안 관점 전용 리뷰** — KISA 시큐어코딩(5등급) + OWASP Top 10 + PII 처리 + 시크릿 노출 + CVE 의존성 취약점 | **회귀 통과 100/100** (2026-07-29, TC 5/5 EXCELLENT. CVE·OWASP 6축 커버리지 갭) | 일반 | 100/100 (v0.1) | `skills/java-secure-coding-reviewer/` |
| [java-performance-reviewer](skills/java-performance-reviewer/SKILL.md) | 0.2 | **성능 관점 전용 리뷰** — N+1·JPA·인덱스 + 캐시 계층 + 트랜잭션·비동기·스레드 풀 + 리소스 누수·GC + **PERF-OPS(HikariCP right-size·graceful shutdown·startup probe)** + 로깅 스팸 | **회귀 통과 98/100** (2026-07-29, TC 5/5. PERF-OPS 커버리지 0/7 갭) | 일반 | 98/100 (v0.2) | `skills/java-performance-reviewer/` |
| [java-architecture-reviewer](skills/java-architecture-reviewer/SKILL.md) | 0.1 | **아키텍처·컨벤션 관점 전용 리뷰** — 4-Tier 경계·import 방향 + Bean 관리·Qualifier·설정 게이팅 + 모듈 관계·의존성 그래프 + 패턴 준수 + pasta-rules 컨벤션 참조 | **회귀 통과 95.4/100** (2026-07-29, TC 5/5. 사고 #593·7abea 재현 통과, pasta-rules 100%) | 일반 | 95.4/100 (v0.1) | `skills/java-architecture-reviewer/` |
| [java-business-logic-reviewer](skills/java-business-logic-reviewer/SKILL.md) | 0.1 | **비즈니스 로직·요건 준수 관점 전용 리뷰** — PRD 수용 기준·TDD 설계 vs 실제 구현 코드 정합성 검증 + 도메인 불변식·엣지 케이스 사각지대 검출 | **회귀 통과 99/100** (2026-07-29 TC 확장 후 재평가, TC 9/9. 🟠 불변식 위반 완전 해소, 5분류 5/5. 이전 92.2 대비 +6.8) | 일반 | 99/100 (v0.1 재평가) | `skills/java-business-logic-reviewer/` |
| [pr-feedback-resolver](skills/pr-feedback-resolver/SKILL.md) | 1.5 | PR 피드백 수집·수정·push·답글 (v1.5: 자기 검증 v2.0 — PR 컨텍스트 현황 파악 + 봇/사람 분기 근거 기록) | **회귀 평가 권장** (v1.5 패턴 이식) | 일반 | 94.5/100 평균 (v1.4 기준) | `skills/pr-feedback-resolver/` |
| [admin-prd-plan-designer](skills/admin-prd-plan-designer/SKILL.md) | 1.1 | Admin 모듈 전용 PRD/TDD/HYBRID 계획 문서 작성 (v1.1: Phase 0.3 admin 모듈 현황 파악 + 멀티턴/풀패키지 결정 트리) | **회귀 평가 권장** (v1.1 패턴 이식) | 일반 | 88/100 (v1.0 기준) | `skills/admin-prd-plan-designer/` |
| [admin-thymeleaf-ui](skills/admin-thymeleaf-ui/SKILL.md) | 1.2 | Admin Thymeleaf SSR 화면 구현/수정 (v1.2: 자기 검증 v2.0 — 기존 패턴 사전 스캔 + 영향도 grep 확인) | **회귀 평가 권장** (v1.2 패턴 이식) | 일반 | 95.3/100 (v1.1 기준) | `skills/admin-thymeleaf-ui/` |
| [api-inventory-generator](skills/api-inventory-generator/SKILL.md) | 1.1 | @RestController 스캔 → API 전체 목록 자동 생성 (v1.1: 자기 검증 v2.0 — 스캔 범위 명시 + 추정 vs 확정 분리) | **회귀 평가 권장** (v1.1 패턴 이식) | 일반 | 89/100 (v1.0 기준) | `skills/api-inventory-generator/` |
| [java-layered-unit-testing](skills/java-layered-unit-testing/SKILL.md) | 1.5 | 4-Tier 계층별 단위 테스트 작성 (v1.5: **Testcontainers 통합 테스트 가이드라인 5개 트리거** — 동시성·트랜잭션·JPA Session 관련. #633 후속 반영. v1.4: infra 직접 참조 금지·domain Fake / verify vs Spy) | **회귀 평가 권장** (v1.5 사례 반영) | 일반 | 93.5/100 평균 (v1.1 기준) | `skills/java-layered-unit-testing/` |
| [chaos-test-planner](skills/chaos-test-planner/SKILL.md) | 1.2 | Chaos Monkey 장애 테스트 검토·계획·커맨드 생성 (v1.2: Phase 1.5 환경 현황 파악 + 자기 검증 6항목) | **회귀 평가 권장** (v1.2 패턴 이식) | 일반 | 93/100 (v1.1 기준) | `skills/chaos-test-planner/` |
| [sq-tone-writer](skills/sq-tone-writer/SKILL.md) | 1.4 | 사용자 말투로 슬랙/PR/문서/리뷰 답글 작성 (v1.4: 자기 검증 v2.0 — 수신자 파악 근거 + 봇/사람 분류 근거 + 가정 답변 표기) | **회귀 평가 권장** (v1.4 패턴 이식) | 일반 | 95.5/100 평균 (v1.3 기준) | `skills/sq-tone-writer/` |
| [jira-bug-root-cause](skills/jira-bug-root-cause/SKILL.md) | 1.1 | Jira 버그 원인 규명 + QA 친화 코멘트 작성 (v1.1: 자기 검증 v2.0 — 확인 vs 가정 분리 + 운영 트래픽 출처 명시 + 재현 조건 검증) | **회귀 평가 권장** (v1.1 패턴 이식) | 일반 | 91/100 (v1.0 기준) | `skills/jira-bug-root-cause/` |
| [chat-incident-report](skills/chat-incident-report/SKILL.md) | 1.0 | Google Chat 장애/CS 대응 메시지 (고정 6섹션 + CS 복붙 품질) | **실전 배치 가능** | **역수입전용** | 95/100 (3/3 PASS, Baseline +58.7점, TC-3 AUTO FAIL 4건 방어) | `skills/chat-incident-report/` |
| [sq-today-reviewer](skills/sq-today-reviewer/SKILL.md) | 0.3 | 하루 Claude 작업 총체 리뷰 → 놓친 학습·공부 주제(실무/CS이론 2트랙)·반복 실수·소양·내일 액션 6섹션 성장 리포트 | **테스트 대기** (harness/test-cases 작성됨, `/eval-harness` 미실행) | 일반 | - | `skills/sq-today-reviewer/` |
| [git-pr](skills/git-pr/SKILL.md) | 0.2 | PR 생성/갱신 — 사람 친화 표현 + 표 위주 + 100~200줄 양식 (commands/git-pr.md에서 승격, forge 일반화) | **실전 배치 가능** (일관성 미검증 — `--repeat 3` 권장) | 일반 | 95.25/100 (TC-1 94 / TC-2 96 / TC-3 93 / TC-4 98) | `skills/git-pr/` |
| [tolgee](skills/tolgee/SKILL.md) | 0.2 | Tolgee i18n 콘솔과 properties 파일 동기화 (v0.2: 4파일 동시 갱신 강제 + en 카피 품질 가드 + Java 코드 Locale 함정 안내) | **회귀 통과 98/100** (2026-07-29, TC 5/5. 실전 사례 #624 FAIL·#623 PASS 재현 통과. pull/diff 커버리지 갭) | 일반 | 98/100 (v0.2) | `skills/tolgee/` |
| [safe-mass-rename](skills/safe-mass-rename/SKILL.md) | 0.1 | 전역 식별자(enum·상수·설정 키·API 필드명) 대형 리네임 안전 오케스트레이션 (6단계 순서 강제 + 롤백 브랜치 + grep 검증 + 후방향 호환) | **회귀 통과 99/100** (2026-07-29, TC 5/5 EXCELLENT. 6단계 순서 강제 + AUTO FAIL 6/6 완전 방어) | 일반 | 99/100 (v0.1) | `skills/safe-mass-rename/` |

## Agents

| 이름 | 버전 | 설명 | 상태 | 배포정책 | 테스트 점수 | 경로 |
|------|------|------|------|---------|------------|------|
| [gcp-infra-architect](agents/gcp-infra-architect/gcp-infra-architect.md) | 1.2 | GCP 특화 글로벌 인프라 설계·검토 파트너 (헬스케어 4개국 규제 + Terraform IaC + Phase 1.5 + 멀티턴·풀패키지 결정 트리) | **실전 배치 가능 (완전 검증 + 일관성 PASS)** | 일반 | 94.1/100 (v1.2, TC-2 3회 편차 4점, 방법론 통일 확보) | `agents/gcp-infra-architect/` |
| [acceptance-tester](agents/acceptance-tester/acceptance-tester.md) | 0.2 | 인수 테스트·통합 테스트 (v0.2: testAcceptance 사각지대 인지 + OAuth MockBean 이름 명시 + @TestConfiguration 중복 제거 + @Nested vs flat 정책) | **테스트 대기** (평가 루브릭·하네스 미작성) | 일반 | - | `agents/acceptance-tester/` |
| [apidog-mock-api-generator](agents/apidog-mock-api-generator/apidog-mock-api-generator.md) | 0.2 | Apidog 스펙 → Mock Controller (v0.2: Phase 1.5 현황 파악 + 응답 DTO 확장 호환성 + Mock 데이터 표식) | **테스트 대기** (평가 루브릭·하네스 미작성) | 일반 | - | `agents/apidog-mock-api-generator/` |
| [bug-analyzer](agents/bug-analyzer/bug-analyzer.md) | 0.3 | 스택트레이스 분석 (v0.3: OAuth2 refresh 사각지대 카탈로그 3패턴 추가 + WebClient 4xx 룰과 층위 분리 — Dexcom #594 사례) | **테스트 대기** | 일반 | - | `agents/bug-analyzer/` |
| [coding-implementer](agents/coding-implementer/coding-implementer.md) | 0.5 | **개발 사이클 오케스트레이터** — TDD 받아 브랜치→Phase별 구현·테스트·자체리뷰·커밋→인수 테스트→PR 준비까지 한 호출 자율 진행 (v0.5: Phase 3-4 자체 리뷰 위임 대상 self-code-reviewer → **java-composite-reviewer** 에이전트로 교체) | **회귀 통과 98.1/100** (2026-07-29 TC 확장 후 재평가, TC 8/8 EXCELLENT. HG-3·HG-4 직접 발동 검증. 이전 97.8 대비 +0.3) | 일반 | 98.1/100 (v0.5 재평가) | `agents/coding-implementer/` |
| [java-composite-reviewer](agents/java-composite-reviewer/java-composite-reviewer.md) | 0.2 | **다각적 복합 리뷰 오케스트레이터** — **5개 관점 스킬** 조합 (공통 self v2.0 + 보안·성능·아키텍처·**비즈니스 로직**). Phase 0~4 + 관점 자동 판단 + Task tool 병렬 호출 + AUTO FAIL 5단계 우선순위(보안>BIZ🟠>성능>아키>공통) | **회귀 통과 100/100** (2026-07-29, TC 8/8 EXCELLENT. v0.2 신규 3개 TC 모두 통과) | 일반 | 100/100 (v0.2) | `agents/java-composite-reviewer/` |
| [prd-plan-designer](agents/prd-plan-designer/prd-plan-designer.md) | 1.0 | **PRD ↔ TDD Alignment 자동 검증자** — PRD·TDD 산출물 정합성 검증 + 매핑 표 자동 생성 (v1.0 A안 격상: 3개 PRD 스킬과 층위 분리, 각 스킬은 단일 문서 작성 / 이 에이전트는 상호 검증) | **회귀 통과 100/100** (2026-07-29, TC 5/5 EXCELLENT. 4분류 정확도 4/4, 층위 분리 통과) | 일반 | 100/100 (v1.0) | `agents/prd-plan-designer/` |

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
| pasta-japan-server | `/Users/kakao/workplace-kakao/global/pasta-japan/server/pasta-japan-server` | **2026-07-09 사이클 3 재배포 완료** (4건): java-spring-coder 1.13 / java-performance-reviewer 0.2 / java-layered-unit-testing 1.5 + **java-business-logic-reviewer 0.1 신규**. 백업: `.claude/backup/2026-07-09-cycle3/`. 회귀 평가 2건 PASS (95/100·87.25/100) + 하네스 4건 완성 + 5번째 관점 스킬 신설. / **2026-07-24 정합성 점검 및 수정**: java-spring-coder 1.11→1.12(루브릭 복붙 오류 정정) + safe-mass-rename/java-secure-coding-reviewer/java-performance-reviewer/java-architecture-reviewer의 evaluation-rubric.md·coding-implementer.md·java-composite-reviewer.md·prd-plan-designer.md에 잔존하던 미리매핑 `anvil/`·`forge/common/pasta-rules/` 참조 전건 `.claude/skills\|agents/`·`.claude/rules/`로 정정 + 누락되어 있던 `forge/common/negative-tc-catalog.md`를 `.claude/shared/`에 신규 배포 (java-composite-reviewer가 07-09부터 참조했으나 미배포 상태였음). 백업 불필요(텍스트 참조 정정만, 컴포넌트 교체 아님) / **2026-07-09 재배포 완료** (9건, 2사이클): 오전 3건(java-spring-coder 1.11 / self-code-reviewer 1.11 / java-layered-unit-testing 1.4) + 오후 6건(**self-code-reviewer 2.0 슬림화 재배포** + **신규 3개 관점 스킬**: java-secure-coding·performance·architecture-reviewer 0.1 + **신규 복합 리뷰어 에이전트** java-composite-reviewer 0.1 + coding-implementer 0.5). 백업: `.claude/backup/2026-07-09-forge-sync/` + `.claude/backup/2026-07-09-review-split/` |
| poc-meal-recommender | `/Users/kakao/workplace-kakao/global/pasta-japan/work/poc-meal-recommender` | **2026-07-24 java-spring-coder 1.5→1.12 업그레이드** (⚠️경위: 루브릭 복붙 오류 수정을 반영하며 실수로 SKILL.md 전체를 최신본으로 덮어씀 — 사전 백업 없었고 `.claude/`가 gitignore 대상이라 v1.5 원본 복구 불가. 사용자 확인 후 v1.12 유지로 결정, POC 프로젝트라 업그레이드 수용). 그 외 컴포넌트는 기존 버전 그대로 / 2026-05-14 (POC 미니 세트 신규 배포: 스킬 8 + 커맨드 6 + rules 20) |
| moneyball | `/Users/kakao/workplace-kakao/moneyball/server/moneyball` | **2026-07-24 정합성 점검 및 수정**: java-spring-coder 1.11→1.12(루브릭 복붙 오류 정정) + 07-15 패리티 재배포 시 리매핑 없이 그대로 복사되어 남아있던 `anvil/`·`forge/common/` 미리매핑 참조를 java-secure-coding-reviewer·java-performance-reviewer·java-architecture-reviewer의 evaluation-rubric.md, agents/coding-implementer.md, agents/java-composite-reviewer.md, commands/git-pr.md 전건에서 정정 (negative-tc-catalog.md 참조는 기존 배포된 `.claude/shared/`로 정상 연결 확인) / **2026-07-15 패리티 재배포** (커맨드 부재 + 7/9 사이클 미전파 부채 해소): ①커맨드 8종 신규(`.claude/commands/` 폴더 부재 → git-branch/git-commit/git-pr/git-worktree-add/git-worktree-remove/forge-upstream/flyway/db-migration) ②7/9 리뷰 세분화 세트(self-code-reviewer 2.0 + java-secure/performance/architecture-reviewer 0.1 + git-pr skill 0.2 + java-composite-reviewer agent 0.1) ③버전 동기화(java-spring-coder 1.10→1.11, coding-implementer 0.4→0.5) ④범용 pasta-rules(01~09,17~19) + negative-tc-catalog(`.claude/shared/`) 배포 — admin 13~16·10·12 제외. 백업: `.claude/backup/2026-07-15-forge-parity/`. `skills/batch-schedule-audit/`·`skills/error-log-report/`(forge 비소유)는 유지 / **2026-07-07 최초 배포**: 7건 세트(java-spring-coder 1.10 / self-code-reviewer 1.10 / tolgee 0.2 / safe-mass-rename 0.1 + bug-analyzer 0.3 / coding-implementer 0.4 / prd-plan-designer 1.0, 백업: `.claude/backup/2026-07-07-forge-deploy/`) |

### pasta-japan-server 배포 현황

| 컴포넌트 | 유형 | 배포 버전 | forge 최신 | 상태 |
|---------|------|----------|-----------|------|
| prd-designer | skill | 1.1 | 1.1 | 동기화 |
| tdd-designer | skill | 1.3 | 1.3 | 동기화 |
| java-spring-coder | skill | 1.13 | 1.13 | **동기화** (2026-07-09 v1.13 재배포: Airbridge 아웃박스 패턴 + 재전송 배치) |
| self-code-reviewer | skill | 2.0 | 2.0 | **동기화** (2026-07-09 v2.0 슬림화 재배포: 관점 룰 3개 스킬로 완전 이관) |
| java-secure-coding-reviewer | skill | 0.1 | 0.1 | **동기화** (2026-07-24 evaluation-rubric.md의 `anvil/` 미리매핑 참조 정정. 2026-07-09 신규 배포: KISA + OWASP + PII + 시크릿 + CVE) |
| java-performance-reviewer | skill | 0.2 | 0.2 | **동기화** (2026-07-09 v0.2 재배포: PERF-OPS — HikariCP right-size·graceful shutdown·startup probe) |
| java-architecture-reviewer | skill | 0.1 | 0.1 | **동기화** (2026-07-24 evaluation-rubric.md의 `anvil/` 미리매핑 참조 정정. 2026-07-09 신규 배포: 4-Tier + Bean·Qualifier + 모듈 + pasta-rules) |
| java-composite-reviewer | agent | 0.2 | 0.2 | **동기화** (2026-07-29 v0.2 재배포: 5관점 확장 — business-logic 통합, AUTO FAIL 우선순위 5단계) |
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
| java-layered-unit-testing | skill | 1.5 | 1.5 | **동기화** (2026-07-09 v1.5 재배포: Testcontainers 통합 테스트 5개 트리거 — #633 후속) |
| java-business-logic-reviewer | skill | 0.1 | 0.1 | **동기화** (2026-07-09 신규 배포: PRD/TDD ↔ 실제 구현 코드 정합성 검증) |
| flyway | command | 1.0 | 1.0 | 동기화 |
| db-migration | command | 1.0 | 1.0 | 동기화 |
| chaos-test-planner | skill | 1.1 | 1.1 | 동기화 |
| sq-tone-writer | skill | 1.3 | 1.3 | 동기화 (2026-05-06 재배포: CodeRabbit 봇 톤 분기 + tone-examples 100줄+, 회귀 95.5/100) |
| jira-bug-root-cause | skill | 1.0 | 1.0 | 동기화 |
| chat-incident-report | skill | 1.0 (실전) | 1.0 (역수입) | 동기화 (2026-04-22 역수입, 마스킹 — forge→pasta 배포 금지) |
| gcp-infra-architect | agent | 1.2 | 1.2 | 동기화 (2026-04-22 신규 배포) |
| tolgee | skill | 0.2 | 0.2 | **동기화** (2026-07-02 재배포: 4파일 동시 갱신 + en 카피 품질 가드 + Java 코드 Locale 함정 안내) |
| acceptance-tester | agent | 0.1 | 0.1 | **2026-05-19 신규 역수입** (실전 전용 → forge 등록, 하네스 미작성) |
| apidog-mock-api-generator | agent | 0.1 | 0.1 | **2026-05-19 신규 역수입** |
| bug-analyzer | agent | 0.3 | 0.3 | **동기화** (2026-07-02 재배포: OAuth2 refresh 사각지대 카탈로그 3패턴 — Dexcom #594 사례) |
| coding-implementer | agent | 0.5 | 0.5 | **동기화** (2026-07-24 관련 스킬 참조 표의 `anvil/` 미리매핑 경로 정정. 2026-07-09 v0.5 재배포: Phase 3-4 위임 대상 java-composite-reviewer 에이전트로 교체) |
| prd-plan-designer | agent | 1.0 | 1.0 | **동기화** (2026-07-24 관련 스킬 참조 표의 `anvil/` 미리매핑 경로 정정. 2026-07-02 재배포: v1.0 A안 격상 — PRD↔TDD Alignment 자동 검증자로 본질 차별화) |
| safe-mass-rename | skill | 0.1 | 0.1 | **동기화** (2026-07-24 `forge/common/pasta-rules/`·`anvil/` 미리매핑 참조를 `.claude/rules/`·`.claude/skills/`로 정정. 2026-07-02 신규 배포: Freemium 리네임 사이클 반영 신설) |

> **2026-05-19 동기화 부채**: forge 측 11개 스킬이 v1.2 패턴(Phase 1.5 + 결정 트리 + 자기 검증 v2.0)으로 일괄 업그레이드되어 pasta 배포 버전과 불일치 상태. 회귀 평가 통과 후 `/forge-deploy --sync` 권장. 또한 pasta SKILL.md 다수에 frontmatter 메타(version/last-modified/changelog)가 누락되어 있어 재배포 시 자동 복원.

### poc-meal-recommender 배포 현황

| 컴포넌트 | 유형 | 배포 버전 | forge 최신 | 상태 |
|---------|------|----------|-----------|------|
| prd-designer | skill | 1.1 | 1.1 | 동기화 (2026-05-14 신규) |
| tdd-designer | skill | 1.3 | 1.3 | 동기화 (2026-05-14 신규) |
| java-spring-coder | skill | 1.12 | 1.12 | **⚠️의도치 않은 업그레이드** (2026-07-24 루브릭 복붙 오류 수정 작업 중 SKILL.md 전체가 실수로 덮어써짐, v1.5 원본 복구 불가. 사용자 확인 후 v1.12 유지로 결정) |
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

### moneyball 배포 현황

| 컴포넌트 | 유형 | 배포 버전 | forge 최신 | 상태 |
|---------|------|----------|-----------|------|
| java-spring-coder | skill | 1.12 | 1.12 | **동기화** (2026-07-24 루브릭 복붙 오류 정정. 2026-07-15 1.10→1.11 bump) |
| self-code-reviewer | skill | 2.0 | 2.0 | **동기화** (2026-07-15 v2.0 슬림화 — 관점 룰 3개 스킬 이관) |
| java-secure-coding-reviewer | skill | 0.1 | 0.1 | **동기화** (2026-07-15 신규 — rules 의존성 없음) |
| java-performance-reviewer | skill | 0.1 | 0.1 | **동기화** (2026-07-15 신규 — rules 의존성 없음) |
| java-architecture-reviewer | skill | 0.1 | 0.1 | **동기화** (2026-07-15 신규 — 범용 pasta-rules 01~09·17~19 동반 배포. admin 13~16 미배포로 admin 컨벤션 검사는 degrade) |
| git-pr | skill | 0.2 | 0.2 | **동기화** (2026-07-15 신규) |
| tolgee | skill | 0.2 | 0.2 | 동기화 (2026-07-07 신규) |
| safe-mass-rename | skill | 0.1 | 0.1 | 동기화 (2026-07-07 신규, `forge/common/pasta-rules/` 참조를 `.claude/rules/`로 리매핑) |
| bug-analyzer | agent | 0.3 | 0.3 | 동기화 (2026-07-07 신규) |
| coding-implementer | agent | 0.5 | 0.5 | **동기화** (2026-07-15 0.4→0.5 — Phase 3-4 자체 리뷰 위임 대상 java-composite-reviewer로 교체) |
| java-composite-reviewer | agent | 0.1 | 0.1 | **동기화** (2026-07-15 신규 — 4관점 리뷰 오케스트레이터. negative-tc-catalog은 `.claude/shared/`에 배포) |
| prd-plan-designer | agent | 1.0 | 1.0 | **동기화** (2026-07-07 신규 — 기존 moneyball 전용 네이티브 서브에이전트를 백업 후 대체) |
| git-branch / git-commit / git-pr / git-worktree-add / git-worktree-remove / forge-upstream / flyway / db-migration | command | 1.0~2.0 | 1.0~2.0 | **동기화** (2026-07-15 신규 — `.claude/commands/` 폴더 부재로 7/7 배포 시 통째 누락됐던 것 해소) |

> **2026-07-15 패리티 재배포**로 7/7 배포의 두 부채 해소: ①커맨드 8종 통째 누락(`/git-commit` 등 미노출) ②7/9 리뷰 세분화 사이클 미전파. rules는 전체 세트가 아닌 **범용 Java Spring 컨벤션(01~09, 17~19)** 만 배포 — pasta admin 전용(13~16)·worktree(10)·multipart(12)는 moneyball 무관으로 제외. 이로 인해 java-architecture-reviewer의 admin 컨벤션 대조는 degrade(해당 규칙 부재 시 건너뜀)되나 moneyball은 admin 모듈이 없어 영향 없음. 기존 `.claude/skills/batch-schedule-audit/`·`error-log-report/`(forge 비소유, moneyball 자체 컴포넌트)는 배포 대상 제외·유지.
