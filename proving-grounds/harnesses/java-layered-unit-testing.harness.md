# java-layered-unit-testing 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/java-layered-unit-testing/SKILL.md` |
| references | `anvil/skills/java-layered-unit-testing/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/java-layered-unit-testing/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/java-layered-unit-testing/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/java-layered-unit-testing/results/` |
| 리포트 | `proving-grounds/evals/java-layered-unit-testing/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 키워드/패턴 |
|---|------|-----------------|
| 1 | H2 DB 사용 | `H2`, `h2`, `mem:testdb`, `h2database` in 테스트 설정/코드 |
| 2 | Domain 계층에 @SpringBootTest | `@SpringBootTest` in Domain 테스트 |
| 3 | 테스트 전체 실패 | 컴파일 에러 또는 전체 테스트 실패 |
| 4 | 계층 무시 일괄 @SpringBootTest | 모든 테스트에 `@SpringBootTest` |
| 5 | FQCN 직접 사용 (PR #527) | 테스트 코드 본문(import 외)에 정규식 `\b[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+\.[A-Z][A-Za-z0-9_]*\b` 매칭. 예: `new org.springframework.dao.X(...)`, `isInstanceOf(java.lang.RuntimeException.class)`. 어노테이션 인자 문자열·SpEL·SQL/JPQL 쿼리·로그 메시지 본문은 제외 |
| 6 | 기존 테스트 파일 통째 덮어쓰기 (v1.6, DW-F3) | 파일을 읽지 않고 `cat >`/Write 로 전체 덮어쓰기. 기존 테스트 메서드 유실 |
| 7 | 동어반복 테스트 (v1.7, RR-F9) | 검사 대상을 고르는 기준과 검증 기준이 동일한 상수·정규식이라 항상 참이 되는 테스트 |
| 8 | 위임만 검증하는 테스트 (v1.7, RR-12) | 단순 위임 메서드에서 mock 반환값이 그대로 나오는지만 확인해 깨질 수 없는 테스트 |
| 9 | 경계 미통과 픽스처 (v1.7, RR-12) | `limit`·임계값 로직인데 경계를 넘지 않는 픽스처만 사용 |
| 10 | 테스트 코드 `var` 사용 (v1.7) | 테스트 메서드 본문에 `var` 선언. 명시 타입이 컨벤션 |
| 11 | 상태 저장소 Mock 정답 주입 (v1.8, RR-F14) | Application 단위 테스트 코드에 `@Mock` 또는 `mock(` 대상이 `*Repository`·`*UseCase`·`*QueryService` 이고 `given(..).willReturn`/`when(..).thenReturn` 으로 반환값 주입. `@WebMvcTest` 의 `@MockBean` UseCase 는 제외. 금지 선언·거부 설명 문장 안의 언급은 오탐이므로 **코드 블록 안**만 매칭 |

> 감지 시 주의 (v1.7 리포트 4절 후속): 금지 규칙을 설명하는 문장이 패턴을 포함하면 오탐이다. 자동 매칭 결과는 반드시 코드 블록 본문으로 재확인한다.

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- H2 사용 0건
- Domain 테스트에 Spring 컨텍스트 로드 0건
- 계층별 적절한 테스트 방식 적용 (Application = Fake 우선, v1.8)

### 축 2. 기능 정확도 (100점 만점)

루브릭 기반:

| 항목 | 배점 |
|------|------|
| 계층별 테스트 방식 적합성 | 25 |
| 테스트 통과 여부 | 25 |
| 테스트 커버리지 / 품질 | 20 |
| 코딩 컨벤션 준수 | 15 |
| 기존 패턴 일관성 | 15 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 계층 식별 | 대상 클래스의 계층을 정확히 식별했는가? |
| 기존 패턴 탐색 | 같은 패키지의 기존 테스트를 읽었는가? |
| Given-When-Then | GWT 구조를 적용했는가? |
| 테스트 실행 | ./gradlew test 명령으로 테스트를 실행했는가? |
| Fake 탐색 (v1.8) | Application 대상이면 기존 `Fake*` 를 먼저 찾고(`find . -name "Fake*"`) 재사용, 없을 때만 신설했는가? |
| review-lint 실행 (v1.8) | 종료 단계에서 `python3 forge/common/review-lint.py` 를 실행(또는 실행 계획 명시)했는가? |

### 축 4~6

java-spring-coder.harness.md와 동일 구조.

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | PASS (H2 0건, Domain Spring 0건) |
| 축 2 기능 정확도 | Happy Path 75+ PASS |
| 축 3 행동 패턴 | 6항목 중 5항목 이상 (80%+, Application 대상이 아니면 Fake 탐색 N/A 로 분모 제외) |
| 축 4 Baseline 비교 | PASS |

→ **실전 배치 가능**
