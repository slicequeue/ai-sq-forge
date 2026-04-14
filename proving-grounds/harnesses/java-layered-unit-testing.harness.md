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

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- H2 사용 0건
- Domain 테스트에 Spring 컨텍스트 로드 0건
- 계층별 적절한 테스트 방식 적용

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

### 축 4~6

java-spring-coder.harness.md와 동일 구조.

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | PASS (H2 0건, Domain Spring 0건) |
| 축 2 기능 정확도 | Happy Path 75+ PASS |
| 축 3 행동 패턴 | 4항목 중 3항목 이상 |
| 축 4 Baseline 비교 | PASS |

→ **실전 배치 가능**
