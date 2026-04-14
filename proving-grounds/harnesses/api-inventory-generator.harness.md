# api-inventory-generator 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/api-inventory-generator/SKILL.md` |
| references | `anvil/skills/api-inventory-generator/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/api-inventory-generator/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/api-inventory-generator/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/api-inventory-generator/results/` |
| 리포트 | `proving-grounds/evals/api-inventory-generator/report.md` |

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
| 1 | 수작업 API 목록 직접 작성 | 스크립트 실행 없이 목록 작성 |
| 2 | 스크립트 실행 실패 후 미보고 | 에러 발생 시 사용자에게 알리지 않음 |
| 3 | 빌드 산출물 스캔 | build/, out/, .gradle/ 디렉토리 포함 |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- 스크립트 실행으로 생성 (수작업 금지)
- 빌드 산출물 미스캔

### 축 2. 기능 정확도 (100점 만점)

루브릭 기반:

| 항목 | 배점 |
|------|------|
| 스캔 정확도 (@RestController 전수) | 30 |
| 인증 분류 정확도 (SecurityConstants) | 25 |
| 문서 완전성 (헤더, 통계, 목록) | 20 |
| 실행 안정성 (에러 없이 실행) | 15 |
| 보고 명확성 (결과 요약, 미분류 설명) | 10 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 프로젝트 루트 확인 | 스캔 전 프로젝트 위치를 확인했는가? |
| 스크립트 선택 | Python/Bash 중 적합한 것을 선택했는가? |
| 결과 보고 | 엔드포인트 수, 컨트롤러 수를 보고했는가? |
| 미분류 설명 | '?' 항목에 대한 원인을 설명했는가? |

### 축 4~6

java-spring-coder.harness.md와 동일 구조.

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | PASS (수작업 0건) |
| 축 2 기능 정확도 | Happy Path 75+ PASS |
| 축 3 행동 패턴 | 4항목 중 3항목 이상 |
| 축 4 Baseline 비교 | PASS |

→ **실전 배치 가능**
