# pr-feedback-resolver v1.9 평가 리포트

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-11-13 |
| 대상 | v1.8 (2026-10-16 실전 역수입, forge 하네스 미평가) → 트레이닝 후 v1.9 |
| 이전 평가 | v1.6 (2026-09-16) 100/100, TC-4 1건 |
| 하네스 | `proving-grounds/harnesses/pr-feedback-resolver.harness.md` (AUTO FAIL 5·6, 행동 패턴 v1.7·v1.8 항목 추가) |
| 모델 | sonnet (응답자 서브에이전트), 채점은 메인 세션이 별도로 수행 |
| 실행 TC | 신규 3건(TC-5 happy / TC-6 edge / TC-7 negative): baseline + with-skill. 회귀 2건(TC-1 happy / TC-3 negative): with-skill 만 |
| 반복 | 1회 |
| 결과 | `results/baseline-v1.8/`, `results/with-skill-v1.8/`, `results/with-skill-v1.9/` |

## 1. 6축 평가 결과 (최종 v1.9 기준)

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 준수 | **PASS** | with-skill AUTO FAIL 0건 (7회 실행) |
| 2. 기능 정확도 | **97.6/100** EXCELLENT | TC-1 97 / TC-3 100 / TC-5 98 / TC-6 95 / TC-7 98 |
| 3. 행동 패턴 | **충족** | 기본 5항목 전 TC 충족. v1.7·v1.8 항목은 해당 TC 에서 충족 (v1.8 TC-5 규칙 단위 스윕 부분 충족 → v1.9 해소) |
| 4. Baseline 비교 | **STRONG PASS** | 신규 TC 평균 47.3 → 97.0 (+49.7) |
| 5. 일관성 | N/A | `--repeat 1` |
| 6. 효율성 | 기록 | 4절 |

## 2. TC별 결과

| TC | 유형 | Baseline | With-Skill v1.8 | With-Skill v1.9 | Baseline AUTO FAIL |
|----|------|----------|-----------------|-----------------|--------------------|
| TC-5 같은 패턴 N곳 | happy-path | 50 | 94 | **98** | #2 `git commit -m` |
| TC-6 dev 에 인터페이스 변경 PR 머지 | edge-case | 55 | **95** | 미재실행 | #2 `git commit -m` (force push 승인 조건부 제안, 감점) |
| TC-7 "지적 줄만 빨리 push" | negative | 37 | 88 | **98** | #2 `git commit -m`, #5 lint 생략 push |
| TC-1 (회귀) | happy-path | — | 97 | 미재실행 | — |
| TC-3 (회귀) | negative | — | 100 | 미재실행 | — |

### TC 유형별 Baseline 비교 (신규 TC)

| 유형 | Baseline | With-Skill (최종) | 격차 |
|------|----------|-------------------|------|
| happy-path (TC-5) | 50 | 98 | +48 |
| edge-case (TC-6) | 55 | 95 | +40 |
| negative (TC-7) | 37 | 98 | +61 |

negative 의 격차가 가장 크다. baseline 은 "lint 돌리지 마"를 그대로 따랐고, 같은 패턴 2곳은 "있을 수 있다"고만 적은 채 확인하지 않았다. edge 는 baseline 도 dev fetch, `findLatest(` grep, dev 반영 후 compileTestJava 를 스스로 떠올려 격차가 가장 작다. 다만 기본값을 rebase 로 두고 force push 를 승인 조건부로 제안했고, "CI 완료 후 머지" 규칙은 없었다.

### TC-5 상세

| 검증 기준 | Baseline | v1.8 | v1.9 |
|-----------|----------|------|------|
| 같은 패턴 PR 전체 검색 | 부분 (`doses` 이름만) | 충족 | 충족 |
| 지적 외 위치 함께 수정 | 미충족 | 부분 (`Instant` `At` 미식별) | 충족 |
| lint → 커밋·push | 충족 | 충족 | 충족 |
| 답글 "같은 패턴 N곳" | 미충족 | 충족 | 충족 |
| "규칙은 있으나 미적용" | 미충족 | 충족 | 충족 |
| 순서·/git-commit | 미충족 (`git commit -m`, `/replies`) | 충족 | 충족 |

### TC-6 상세

with-skill 은 "로컬 단독 통과는 게이트를 대체하지 않는다"는 판단을 먼저 밝혔다. 이어서 `git merge --no-commit origin/dev` → `compileTestJava` → dev 기준 구현체·Fake grep → `gh pr view 813 --json files`·`git log -S` 로 #813 확인 → 실패 시 merge 커밋(force push 금지) → #816 머지 순서와 CI 완료 후 머지 순서로 처리했다. 감점: 충돌이 없을 때 abort 하는 근거로 "CI 는 어차피 dev 와 합쳐 돈다"를 확인 없이 단정했다. 열린 #816 을 "아직 올라오지 않았다"고 잘못 읽었다.

### TC-7 상세

| 검증 기준 | Baseline | v1.8 | v1.9 |
|-----------|----------|------|------|
| lint 생략 거절 + 사유 | 미충족 | 충족 | 충족 |
| 같은 패턴 2곳 식별·보고 | 미충족 | 충족 | 충족 |
| 다른 파일은 합의 후 수정 | 해당 | 충족 (탐지만) | 충족 (수정 전 (a)/(b) 선택) |
| push 전 답글 없음, /git-commit | 미충족 | 충족 | 충족 |
| "규칙은 있으나 미적용" | 미충족 | 충족 | 충족 |
| AUTO FAIL 미해당 | 미충족 (#2, #5) | 충족 [수동 검토 필요] | 충족 |

v1.8 결함: 5-4 에서는 "위반이 남으면 push 하지 않고 멈춘다"고 썼지만, 종료 보고에는 "review-lint 위반 0건, push 완료"를 적었다. lint 는 PR 전체 diff 를 보므로 남은 2곳이 RR-12 [위반]으로 나와야 한다. 따라서 보고는 사실과 다르다. 스킬에 "lint 는 PR 전체 diff 를 본다"와 "범위 제한 요청과 lint 위반이 충돌하면 수정 전에 선택을 받는다"가 없었던 것이 원인이다.

## 3. 트레이닝 내역 (v1.8 → v1.9)

| 변경 | 위치 | 근거 | 전 → 후 |
|------|------|------|---------|
| 스윕 범위를 "지적된 규칙"으로 확장, lint 같은 코드 포함 | SKILL.md Step 4-4 | TC-5 | 94 → 98 |
| lint 가 PR 전체 diff 를 본다는 점, 범위 제한 시 수정 전 선택, 가정 기반 "0건" 보고 금지 | SKILL.md Step 4-5 | TC-7 | 88 → 98 |
| 자기 검증 17번 | SKILL.md | TC-5·7 | — |
| 폐기된 `/replies` API·고정 답글 문구 정정 | references/feedback-collection.md | TC-1·3 응답자 지적 | 충돌 제거 |
| AUTO FAIL 5·6 추가 | evaluation-rubric.md, 하네스 | 신규 | — |

SKILL.md 는 242줄에서 247줄로 늘었다.

## 4. 효율성 (기록용)

| 실행 | 토큰 | tool | 시간(초) |
|------|------|------|---------|
| TC-5 baseline | 49,377 | 1 | 16 |
| TC-5 with-skill v1.8 / v1.9 | 75,145 / 89,609 | 4 / 5 | 93 / 91 |
| TC-6 baseline / with-skill | 50,610 / 95,739 | 1 / 6 | 24 / 103 |
| TC-7 baseline | 49,072 | 1 | 15 |
| TC-7 with-skill v1.8 / v1.9 | 68,535 / 86,951 | 4 / 5 | 54 / 79 |
| TC-1 with-skill | 70,241 | 4 | 61 |
| TC-3 with-skill | 66,894 | 4 | 42 |

## 5. 확인된 것 vs 가정한 것

| 구분 | 내용 |
|------|------|
| 확인 | 응답은 독립 서브에이전트(sonnet)가 작성했고 채점은 메인 세션이 수행했다. 응답자에게는 기대 결과와 검증 기준을 주지 않았다. baseline 에는 anvil/·forge/·proving-grounds/ 를 읽지 말라고 지시했다 |
| 확인 | v1.8 의 두 결함이 v1.9 재실행에서 사라졌다 (동일 프롬프트, 1회) |
| 가정 | 전 실행이 시뮬레이션이다. 파일 내용과 lint 출력은 응답자가 가정했다 |
| 가정 | TC-1·3·6 은 v1.8 로만 실행했다. v1.9 문구가 이 결과에 영향을 주지 않는다고 판단했다. 재평가 트리거: 다음 `--skip-baseline` 에서 점수가 하락하는 경우 |
| 가정 | 점수는 단일 채점자의 판단이다. TC-7 v1.8 의 AUTO FAIL 5 미해당 판정은 [수동 검토 필요]다 |
| 가정 | baseline 에는 lint 경로로 `tools/review-lint.py` 를 줬다. 존재 자체는 양쪽에 알렸으므로 비교는 공정하다고 판단했다 |

## 6. 최종 판정

**PASS: v1.9 확정, 실전 배치 가능.** 평균 97.6, AUTO FAIL 0건, Happy 2/2, Edge 1/1, Baseline STRONG PASS.

## 7. 남은 약점

1. TC-6: CI 의 merge ref 동작을 확인하지 않고 단정했다. 5-1 에 "CI 트리거·브랜치 보호 설정 확인 후 merge 커밋 유지 여부 결정"을 추가할지 검토한다.
2. 커밋 type 이 흔들린다 (`fix:`/`test:`/`refac:`). git-commit 쪽 문제에 가깝다.
3. 일관성 미측정. 다음 회차에 TC-7 `--repeat 3` 을 권한다.
4. lint 가 실제로 PR 전체 diff 에서 RR-12 를 잡는지는 실전 로그로 확인해야 한다.

## 8. 공용 변경 제안

- `negative-tc-catalog.md` D-3 "지적 줄만 고치고 push 유도" 추가 (TC-7 근거).
- `review-recurrence-guard.md` RR-L 에 `@Operation(summary = "")` "확인" 등급 검토 (시뮬레이션 후보라 실전 근거 없음).
- `anvil/INDEX.md` 를 v1.9 / 97.6 으로 갱신.
