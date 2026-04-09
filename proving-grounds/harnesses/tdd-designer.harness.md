# tdd-designer 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/tdd-designer/SKILL.md` |
| references | `anvil/skills/tdd-designer/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/tdd-designer/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/tdd-designer/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/tdd-designer/results/` |
| 리포트 | `proving-grounds/evals/tdd-designer/report.md` |

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
| 1 | PRD 소스 없이 TDD 추측 작성 | PRD 확인 없이 바로 TDD 작성 시작 |
| 2 | H2 사용 | `H2`, `h2`, `인메모리` in 테스트 전략 |
| 3 | 기존 마이그레이션 파일 수정 언급 | 기존 마이그레이션 수정/삭제 제안 |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- PRD 소스 없이 추측으로 TDD 작성하지 않음
- H2 사용하지 않음 (Testcontainers 필수)
- Phase TODO에 패키지 경로 포함

### 축 2. 기능 정확도 (100점 만점)

| 항목 | 배점 |
|------|------|
| PRD 소스 명시 (CRITICAL) | 10 |
| Phase TODO 구체성 (패키지 경로+클래스명) | 25 |
| 아키텍처 적합성 분석 | 15 |
| 테스트 전략 | 15 |
| 커밋 계획 & 파일 목록 | 10 |
| 다이어그램 품질 | 10 |
| 복잡도 적정성 | 5 |
| 가드레일 준수 | 10 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| PRD 소스 확인 | PRD 존재 여부를 먼저 확인했는가? |
| 복잡도 판단 | 경량/표준 TDD를 올바르게 선택했는가? |
| 인터랙티브 Q&A | 기술 결정 사항에 대해 질문했는가? |
| 아키텍처 분석 | .claude/rules/ 참조하여 적합성 분석을 했는가? |
| 구현 워크플로 명시 | Phase 실행 방법을 TDD에 포함했는가? |

### 축 4~6

java-spring-coder.harness.md와 동일 구조.

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | PASS |
| 축 2 기능 정확도 | Happy Path 75+ PASS |
| 축 3 행동 패턴 | 5항목 중 4항목 이상 |
| 축 4 Baseline 비교 | PASS |

→ **실전 배치 가능**
