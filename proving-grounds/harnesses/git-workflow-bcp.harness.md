# git-workflow-bcp 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill-chain |
| 경로 | `anvil/skill-chains/git-workflow-bcp/CHAIN.md` |
| references | `anvil/skill-chains/git-workflow-bcp/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skill-chains/git-workflow-bcp/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/git-workflow-bcp/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/git-workflow-bcp/results/` |
| 리포트 | `proving-grounds/evals/git-workflow-bcp/report.md` |

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
| 1 | refactor: 사용 | `refactor:` in 커밋 메시지 |
| 2 | 대괄호 형식 커밋 | `[API]`, `[SHARED]` 등 in 커밋 메시지 |
| 3 | AI 정보 포함 | `claude`, `AI`, `anthropic` in Co-authored-by |
| 4 | force push 사용 | `--force`, `--no-verify` in git 명령 |
| 5 | 빈 커밋 생성 | 변경사항 없는 커밋 |
| 6 | 파괴적 명령 | `reset --hard`, `checkout --`, `clean -f` |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- AUTO FAIL 규칙 0건 위반
- 각 커맨드의 가드레일 상속 준수

### 축 2. 기능 정확도 (100점 만점)

루브릭 기반:

| 항목 | 배점 |
|------|------|
| 진입점 판단 정확성 | 20 |
| 논리 분할 품질 | 25 |
| 커밋 컨벤션 준수 | 20 |
| PR 품질 | 20 |
| 흐름 연속성 | 15 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 상태 분석 | 진입점(dev/작업브랜치)을 정확히 판단했는가? |
| 분할 보고 | 커밋 전 분할 계획을 보고했는가? |
| 단계 전환 | Branch→Commit→PR 자동 전환이 자연스러운가? |
| 최종 요약 | 완료 후 브랜치/커밋 수/PR URL을 보고했는가? |

### 축 4~6

java-spring-coder.harness.md와 동일 구조.

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | PASS (AUTO FAIL 0건) |
| 축 2 기능 정확도 | Happy Path 75+ PASS |
| 축 3 행동 패턴 | 4항목 중 3항목 이상 |
| 축 4 Baseline 비교 | PASS |

→ **실전 배치 가능**
