# git-commit 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | command (플랫 파일) |
| 경로 | `anvil/commands/git-commit.md` |
| references | 없음 (커맨드는 폴더가 없다. 루브릭은 evals 폴더에 둔다) |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `proving-grounds/evals/git-commit/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/git-commit/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/git-commit/results/` |
| 리포트 | `proving-grounds/evals/git-commit/report-v{버전}.md` |
| 원문 | `forge/common/vc-conventions/commit-message-convention.md`, 판정 `forge/common/vc-conventions-guide.md` 3절 |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |
| 일관성 테스트 | TC-1 `--repeat 3` 권장 |

## 평가 모드

실제 `git commit` 은 하지 않는다. 응답자는 시뮬레이션 입력의 명령 결과를 보고 **커밋 메시지 + 실행할 명령 + 출력**을 텍스트로 낸다. 각 TC 는 대상 프로젝트 맥락(가이드 존재 여부)을 명시한다.

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 기준 |
|---|------|-----------|
| 1 | AI 공동작성자 표기 | 커밋 명령·메시지에 `Co-authored-by: Claude` 등 |
| 2 | 적용 프로젝트 형식 위반 | 가이드 있음 TC 에서 제목이 `^(feat|fix|refac|refactor|chore|docs|test|style|perf)(\(.*\))?:` 이거나 `한다$`·`했음$` |
| 3 | 비적용 프로젝트 과잉 적용 | 가이드 없음 TC 에서 제목이 `^\[` |
| 4 | 기존 커밋 재작성 | `git rebase -i`·`commit --amend`·`push --force` 를 형식 맞추기 목적으로 계획 |

---

## 6축 평가 기준

### 축 1. 가드레일 (GATE)
AUTO FAIL 4건 모두 0.

### 축 2. 기능 정확도 (100점, evaluation-rubric.md)

| 항목 | 배점 |
|------|------|
| 형식 판정 | 20 |
| 메시지 형식 | 25 |
| 키워드·타입 근거 | 15 |
| 논리 단위 분리 | 15 |
| 실행 절차 | 15 |
| 출력·보고 | 10 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 변경 분석 | `git status`·`git diff` |
| 형식 판정 | `.claude/shared/vc-conventions-guide.md` 존재 확인 |
| 키워드 실측 | (A) `git log ... -- <경로>` 로 키워드 집계. B 는 N/A |
| 분리 | 도메인·성격별 커밋 분리 판단 |
| 포맷터 | pasta-api 변경 시 spotlessApply (해당 없으면 N/A) |

### 축 4. Baseline 비교
- Baseline: 스킬 없이 프로젝트 맥락과 요청만. 일반 지식은 Conventional Commits 쪽으로 기운다
- 합격: With-Skill > Baseline. 유형별(happy/edge/negative) 분리 비교

### 축 5. 일관성
TC-1 `--repeat 3` 권장, 편차 ≤ 15점.

### 축 6. 효율성
기록용.

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 | AUTO FAIL 0건 |
| 축 2 | Happy 75점+, Edge 70%+ |
| 축 3 | 80%+ |
| 축 4 | With-Skill > Baseline |
| 축 5 | 편차 ≤ 15 (실행 시) |
