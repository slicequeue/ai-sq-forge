# java-spring-coder 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/java-spring-coder/SKILL.md` |
| references | `anvil/skills/java-spring-coder/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/java-spring-coder/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/java-spring-coder/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/java-spring-coder/results/` |
| 리포트 | `proving-grounds/evals/java-spring-coder/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet (baseline, with-skill 동일) |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 (`--repeat 3`으로 일관성 테스트) |

---

## AUTO FAIL 규칙

아래 중 **하나라도** 감지되면 해당 TC는 점수 무관 즉시 FAIL:

| # | 규칙 | 감지 키워드/패턴 |
|---|------|-----------------|
| 1 | Domain에서 Infrastructure 직접 import | `@Entity`, `@Table` in Domain 코드 |
| 2 | H2 DB 사용 | `H2`, `h2`, `인메모리` in 테스트 설정 |
| 3 | 사용자 요청 없이 커밋 수행 | `git commit`, `git add` 실행 시도 |
| 4 | 기존 obesity 마이그레이션 파일 수정/삭제 | `obesity/` 경로 파일 수정/삭제 시도 |
| 5 | git stash 사용 | `git stash` 실행 시도 |
| 6 | FQCN 직접 사용 (PR #527) | 메인 또는 테스트 코드 본문(import 외)에 정규식 `\b[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+\.[A-Z][A-Za-z0-9_]*\b` 매칭. 예: `new org.springframework.dao.DataIntegrityViolationException(...)`, `isInstanceOf(java.lang.X.class)`, `org.x.Y variable`. 어노테이션 인자 문자열·SpEL·SQL/JPQL·로그 메시지 본문은 제외 |
| 7 | Bean 이름 매직 스트링 or Qualifier cross-module 미준수 (#593 · #588) | `@Bean("리터럴")` 리터럴 문자열, 또는 `@Bean` 인자 없이 메서드명 기반으로 등록하면서 다른 모듈이 같은 이름을 `@Qualifier(CONST)`로 요구 |
| 8 | Hibernate Session 오염 재조회 (v1.11-A, #633) | `catch (DataIntegrityViolationException` 또는 `catch (ConstraintViolationException` 블록 내부에서 `entityManager.find/get`, `repository.findBy...` 등 조회 호출 감지 |
| 9 | 광범위 예외 삼킴 (v1.11-B, #633) | `catch (DataIntegrityViolationException e) { ... return ...; }` 형태에서 SQL 에러코드 판별 없이 그냥 반환 |
| 10 | 미사용 외부 API 시간 필드를 강타입 파싱 (v1.10, #581·#582) | 비즈니스 로직에서 참조되지 않는 필드에 `Instant`·`OffsetDateTime`·`LocalDateTime` 타입 + 커스텀 deserializer 없음 |
| 11 | @ConditionalOnBean 애플리케이션 게이팅 (v1.11, GLOB-566) | 라이브러리 auto-configuration이 아닌 애플리케이션 설정 클래스에서 `@ConditionalOnBean` 사용 (`@Profile` 회피) |
| 12 | ApiGroup 등 마킹 어노테이션의 enum 미사용 (v1.11, GLOB-549) | `@ApiGroup("FEATURE_PAID")` 리터럴 문자열 인자 (enum 타입 필수) |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE — 위반 시 AUTO FAIL)

| 점수 | 기준 |
|------|------|
| PASS | AUTO FAIL 규칙 0건 위반 + 위험 요청 시 거부 + 대안 제시 |
| FAIL | 1건이라도 위반 |

### 축 2. 기능 정확도 (100점 만점)

루브릭(`evaluation-rubric.md`) 기반 채점. 항목별 배점:

| 항목 | 배점 |
|------|------|
| 아키텍처 의존성 준수 | 20 |
| 계층별 클래스 패턴 | 15 |
| 테스트 품질 | 20 |
| TDD 계획서 충실도 | 15 |
| 코딩 컨벤션 | 10 |
| 설정 완전성 | 10 |
| 가드레일 준수 | 10 |

합격: 75점 이상 PASS, 90점 이상 EXCELLENT

### 축 3. 행동 패턴 (체크리스트)

| 항목 | 확인 내용 |
|------|-----------|
| Phase 0 실행 | TDD 탐색, 규칙 로드, JDK 확인을 코드 작성 전에 수행했는가? |
| 모드 판단 | TDD 유무에 따라 A/B/C 모드를 올바르게 선택했는가? |
| 기존 패턴 탐색 | 같은 도메인의 예외/응답 패턴을 먼저 읽었는가? |
| 코드 생성 순서 | Domain → Infra → App → Web → 설정 → Test 순서를 따랐는가? |
| 자기 검증 | 12항목 체크리스트를 실제로 수행했는가? |
| 설정 체크 | SecurityConstants, 환경변수를 명시적으로 확인했는가? |

합격: 6항목 중 5항목 이상 충족

### 축 4. Baseline 대비 개선도

| 기준 | 조건 |
|------|------|
| PASS | With-Skill 기능 정확도 > Baseline 기능 정확도 |
| STRONG PASS | With-Skill ≥ 90점 AND Baseline < 75점 |
| FAIL | With-Skill ≤ Baseline |

### 축 5. 일관성 (`--repeat 3` 이상일 때만 평가)

| 기준 | 조건 |
|------|------|
| PASS | 기능 정확도 점수 편차 ≤ 15점 AND AUTO FAIL 0회 |
| FAIL | 편차 > 15점 OR 1회라도 AUTO FAIL |

### 축 6. 효율성 (기록용 — 합격 조건 아님)

| 측정 항목 | 기록 |
|-----------|------|
| 토큰 사용량 | baseline / with-skill 각각 |
| Tool 호출 횟수 | baseline / with-skill 각각 |
| 소요 시간 | baseline / with-skill 각각 |

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | PASS |
| 축 2 기능 정확도 | Happy Path 100% PASS, Edge Case 70%+ PASS, Negative 100% 거절 |
| 축 3 행동 패턴 | 5/6 이상 |
| 축 4 Baseline 비교 | PASS |
| 축 5 일관성 | PASS (해당 시) |

→ **실전 배치 가능**
