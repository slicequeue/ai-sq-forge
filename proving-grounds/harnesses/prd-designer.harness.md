# prd-designer 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/prd-designer/SKILL.md` |
| references | `anvil/skills/prd-designer/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/prd-designer/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/prd-designer/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/prd-designer/results/` |
| 리포트 | `proving-grounds/evals/prd-designer/report.md` |

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
| 1 | PRD에 기술 용어 포함 | `Spring`, `JPA`, `Batch`, `API endpoint`, `REST`, `DB`, `테이블`, `쿼리` in PRD 본문 |
| 2 | How(구현 방법) 기술 | 구현 방법, 기술 스택, 아키텍처 설계 in PRD 본문 |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- PRD 본문에 기술 용어 0건
- How가 아닌 What/Why만 기술

### 축 2. 기능 정확도 (100점 만점)

루브릭 기반:

| 항목 | 배점 |
|------|------|
| 기술 용어 격리 (CRITICAL) | 20 |
| 9섹션 구조 준수 | 15 |
| 기능 요구사항 품질 | 20 |
| 비기능 요구사항 측정 가능성 | 15 |
| 사용자 시나리오 구체성 | 10 |
| 복잡도 적정성 | 10 |
| 인터랙티브 Q&A 활용 | 10 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 복잡도 판단 | 경량/표준/복잡 복잡도를 올바르게 판단했는가? |
| 소스 확보 | 사용자/Apidog/docs/ 등에서 정보를 확보하려 했는가? |
| 인터랙티브 Q&A | 정보 부족 시 5개 이하 질문을 던졌는가? |
| TDD 핸드오프 | PRD 완료 후 tdd-designer 안내를 했는가? |

### 축 4~6

java-spring-coder.harness.md와 동일 구조.

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | PASS (기술 용어 0건) |
| 축 2 기능 정확도 | Happy Path 75+ PASS |
| 축 3 행동 패턴 | 4항목 중 3항목 이상 |
| 축 4 Baseline 비교 | PASS |

→ **실전 배치 가능**
