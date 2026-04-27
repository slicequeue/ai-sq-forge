# git-pr 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/git-pr/SKILL.md` |
| references | `anvil/skills/git-pr/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/git-pr/references/evaluation-rubric.md` |
| 사례 | `anvil/skills/git-pr/references/example-pr-551.md` |
| 테스트 케이스 | `proving-grounds/evals/git-pr/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/git-pr/results/` |
| 리포트 | `proving-grounds/evals/git-pr/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |
| 일관성 테스트 | TC-1 `--repeat 3` 권장 |

## 평가 모드

PR 생성 결과(본문 + gh 명령)를 시뮬레이션 입력으로 받아 평가한다. 실제 `gh pr create/edit` 실행은 하지 않고, **스킬이 산출하는 본문 + 실행 명령 계획**을 평가 대상으로 삼는다.

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 기준 |
|---|------|-----------|
| 1 | AI 공동작성자 표기 | 본문/명령에 `Co-authored-by: Claude` 등 AI 식별자 |
| 2 | target branch 오류 | `--base main`/`--base master` (사용자 명시 hotfix 없음) |
| 3 | `docs/...` 상대 링크 | 본문에 `docs/...` 형태 링크 1건 이상 |
| 4 | 기존 PR 무시 + 신규 생성 | `gh pr list`로 열린 PR 확인 후에도 `gh pr create` 호출 |
| 5 | 코드 스니펫·mermaid 본문 삽입 | 본문에 ` ```java`/` ```mermaid` 등 5줄 초과 블록 |
| 6 | 본문 영어 작성 | 본문 한국어 비율 < 50% |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- AUTO FAIL 6건 모두 0
- 위반 시 즉시 FAIL 판정 (다른 축 점수 무관)

### 축 2. 기능 정확도 (100점 만점, evaluation-rubric.md 기반)

| 항목 | 배점 |
|------|------|
| 분량·구조 | 15 |
| 섹션 구성 정확성 | 20 |
| 사람 친화 표현 | 15 |
| 표 활용 | 10 |
| 가드레일 준수 | 15 |
| gh 사용 정확성 | 15 |
| 출력 품질 | 10 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 변경 분석 | `git status`, `git log <base>..HEAD --oneline`, `git diff <base>..HEAD --stat` 실행 |
| base 결정 | 기본 `dev`, hotfix는 사용자 명시 시만 `main` |
| 원격 확인 | `git push -u origin HEAD` 누락 검증 |
| 기존 PR 확인 | `gh pr list --head ... --state open` 실행 |
| 분기 처리 | 기존 있으면 `gh pr edit`, 없으면 `gh pr create` |
| 사례 학습 | `references/example-pr-551.md` 사례를 분량·표현 감각 잡는 데 활용 |

### 축 4. Baseline 비교

- Baseline (스킬 미사용): 일반적인 Conventional PR 본문 — 코드 스니펫 포함, 분량 길어짐, 영문 jargon, AI 공동작성자 표기 가능성 ↑
- With-Skill: 100~200줄 표 위주, 사람 친화 표현, 가드레일 준수
- 합격: With-Skill > Baseline + 15점

### 축 5. 일관성

- TC-1 `--repeat 3` 권장
- 편차 ≤ 15점

### 축 6. 효율성

- 기록용 (합격 조건 아님)
- 토큰 사용량 / 응답 시간

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | AUTO FAIL 0건 |
| 축 2 기능 정확도 | Happy Path 75점+ |
| 축 3 행동 패턴 | 체크리스트 80%+ |
| 축 4 Baseline | With-Skill > Baseline + 15점 |
| 축 5 일관성 | 편차 ≤ 15점 (--repeat 3 시) |

→ 모두 충족 시 **실전 배치 가능** (forge INDEX.md 상태 갱신)

---

## 리포트 양식

`proving-grounds/evals/git-pr/report.md`에 다음 섹션 포함:

1. 전체 점수 (100점 만점)
2. 6축별 결과
3. AUTO FAIL 검증 결과
4. TC별 결과 (점수 + 위반 요약)
5. Baseline vs With-Skill 비교 표
6. 개선 권고
