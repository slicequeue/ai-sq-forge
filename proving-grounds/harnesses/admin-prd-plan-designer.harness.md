# admin-prd-plan-designer 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/admin-prd-plan-designer/SKILL.md` |
| references | `anvil/skills/admin-prd-plan-designer/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/admin-prd-plan-designer/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/admin-prd-plan-designer/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/admin-prd-plan-designer/results/` |
| 리포트 | `proving-grounds/evals/admin-prd-plan-designer/report.md` |

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
| 1 | PRD/TDD 타입 미확정 상태로 문서 작성 | 타입 확정 질문 없이 즉시 문서 본문 작성 시작 |
| 2 | admin 컨텍스트 전면 누락 | `SSR`, `sidebar`, `security`, `history` 관련 언급 0건 |
| 3 | 필수 표/체크리스트 없이 자유 서술만 제출 | Alignment 매핑 표, Phase 체크리스트 없이 산문형만 존재 |
| 4 | 사용자와 합의 없이 독단적으로 범위 확장/축소 | 멀티턴 합의 루프 없이 기능 범위를 임의 결정 |
| 5 | 문서 작성 중 구현 코드/커밋으로 점프 | `Controller`, `Service`, `Repository`, `git commit`, 코드 블록(Java/HTML) 작성 |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- 하드 가드레일 위반 0건
- AUTO FAIL 규칙 5개 항목 전체 위반 없음

### 축 2. 기능 정확도 (100점 만점)

루브릭 기반:

| 항목 | 배점 |
|------|------|
| 타입 분리 (PRD/TDD/HYBRID 올바른 선택) | 20 |
| Admin 컨텍스트 반영 (SSR/sidebar/security/history) | 20 |
| 템플릿 충족 (필수 섹션/표/체크리스트 완비) | 20 |
| 멀티턴 합의 (사용자와 범위·우선순위 협의) | 20 |
| Phase 실행 가능성 (개발자가 바로 착수 가능한 수준) | 20 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 멀티턴 합의 루프 수행 | 사용자와 범위·우선순위를 협의하는 Q&A를 수행했는가? |
| 문서 타입 확정 후 작성 | PRD/TDD/HYBRID 타입을 먼저 확정한 뒤 작성을 시작했는가? |
| 결정 로그 기록 | 합의된 사항을 Decision Log 또는 결정 사항으로 기록했는가? |
| Open Questions 분리 | 미확정 사항을 Open Questions 섹션으로 분리했는가? |

### 축 4~6

java-spring-coder.harness.md와 동일 구조.

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | PASS (하드 가드레일 위반 0건) |
| 축 2 기능 정확도 | Happy Path 75+ PASS |
| 축 3 행동 패턴 | 4항목 중 3항목 이상 |
| 축 4 Baseline 비교 | PASS |

→ **실전 배치 가능**
