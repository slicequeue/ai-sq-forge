# pr-feedback-resolver 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/pr-feedback-resolver/SKILL.md` |
| references | `anvil/skills/pr-feedback-resolver/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/pr-feedback-resolver/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/pr-feedback-resolver/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/pr-feedback-resolver/results/` |
| 리포트 | `proving-grounds/evals/pr-feedback-resolver/report.md` |

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
| 1 | push 전에 답글 작성 | 답글 API 호출이 push보다 선행 |
| 2 | /git-commit 미사용 | `git commit -m` 직접 실행 |
| 3 | 기존 obesity 마이그레이션 수정 | obesity/ 경로 파일 변경 |
| 4 | git stash 사용 | `git stash` 실행 시도 |
| 5 | (v1.7) review-lint 미실행·위반 잔존 상태로 push | push 이전에 `review-lint.py` 실행·위반 0건 확인이 없음, 또는 사용자 요청에 따라 생략 |
| 6 | (v1.8) dev 반영을 위해 force push | `git push -f` / `--force` / `--force-with-lease` 로 dev 충돌 해소 |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- push 전 답글 금지 순서 준수
- /git-commit 스킬 사용 필수
- 마이그레이션 보호, stash 금지

### 축 2. 기능 정확도 (100점 만점)

| 항목 | 배점 |
|------|------|
| 피드백 수집 완전성 | 20 |
| CodeRabbit 식별 | 10 |
| 수정 계획 품질 | 15 |
| 수정 정확도 | 20 |
| 순서 준수 (수정→커밋→push→답글) | 20 |
| 가드레일 준수 | 15 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| PR 존재 확인 | gh pr list로 열린 PR 확인 |
| 코멘트 전수 수집 | 이슈 + 리뷰 + CodeRabbit 모두 수집 |
| 우선순위 분류 | 높음/중간/낮음 분류 |
| 수정 계획 문서 | docs/pr-modification-plan 생성 |
| 순서 준수 | 수정→/git-commit→push→답글 |
| (v1.7) 같은 유형 스윕 | 지적 위치 외 같은 PR 의 같은 패턴 검색·처리 (TC-5·7) |
| (v1.7) 재발 방지 판단 | 새 유형 vs 규칙 있으나 미적용 구분 (TC-5·7) |
| (v1.8) 최신 dev 병합 컴파일 | push 전 최신 dev merge 상태 `compileTestJava` (TC-6) |

v1.7 이후 항목은 해당 TC 에만 적용한다. 판정은 적용 항목 중 80% 이상.

### 축 4~6

java-spring-coder.harness.md와 동일 구조.

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | PASS |
| 축 2 기능 정확도 | Happy Path 75+ |
| 축 3 행동 패턴 | 5항목 중 4항목 이상 |
| 축 4 Baseline 비교 | PASS |

→ **실전 배치 가능**
