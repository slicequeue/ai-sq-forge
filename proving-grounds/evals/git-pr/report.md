# git-pr v0.2 — 평가 리포트 (신규 컴포넌트)

**실행 모드**: 전체 평가 (Baseline + With-Skill)
**평가일**: 2026-04-28
**버전**: 0.2 (forge 일반화 + references 분리 + 자기 검증 체크리스트 12개)
**평가 TC 수**: 4 (Happy 2 / Edge 1 / Negative 1)
**모델**: sonnet (시뮬레이션)

---

## 6축 요약

| 축 | 항목 | 결과 |
|----|------|------|
| 1 | 가드레일 준수 (GATE) | **PASS** — AUTO FAIL 6건 모두 0 |
| 2 | 기능 정확도 | **PASS** — 평균 95.25점 (TC-1 94 / TC-2 96 / TC-3 93 / TC-4 98) |
| 3 | 행동 패턴 | **PASS** — 체크리스트 6/6 (변경 분석·base 결정·원격 확인·기존 PR·분기·사례 학습) |
| 4 | Baseline 비교 | **STRONG PASS** — Baseline 4건 모두 AUTO FAIL → With-Skill 평균 95.25 |
| 5 | 일관성 | **N/A** (--repeat 미적용 — TC-1 `--repeat 3` 권장) |
| 6 | 효율성 | 기록 — 본문 25~60줄 (가이드 100~200 내), 표 위주 |

**최종 판정: EXCELLENT — 실전 배치 가능 (단, 일관성 검증 권장)**

---

## TC별 점수 (Baseline → With-Skill)

| TC | 유형 | Baseline | With-Skill | 핵심 차이 |
|---|---|---:|---:|---|
| TC-1 | Happy (단순 fix) | AUTO FAIL | **94** | 코드 스니펫·AI 표기·target main 위반 vs 양식 준수 |
| TC-2 | Happy (성능+측정+Canary) | AUTO FAIL | **96** | docs/ 링크·영문 jargon·AI 표기 vs 4지표 표·KST 절대시점 |
| TC-3 | Edge (기존 PR 갱신) | AUTO FAIL | **93** | PR #612 무시 후 신규 생성 시도 vs `gh pr edit 612` 정확 분기 |
| TC-4 | Negative (위반 요청 3건) | AUTO FAIL | **98** | 무비판 수용 vs 3건 거부 + 사유 + 대안 |

---

## 핵심 발견

### 1. Negative TC가 최고점 (98)

자기 검증 체크리스트 12개가 실제로 작동. 사용자의 잘못된 요청 3건(`docs/` 상대 링크, AI 공동작성자 표기, target `main` 강제)을 모두 거부하고 사유 + 대안 제시. 가드레일이 "사용자 요청 무비판 수용" 함정을 정확히 차단.

### 2. TC-3 분기 정확

`gh pr list --head ... --state open` → PR #612 인지 → `gh pr edit 612` 정확 사용. v0.2의 forge 일반화(pasta 특정 `--repo` 제거, gh 자동 감지)가 일반 시나리오에서도 안정적.

### 3. Baseline은 모두 AUTO FAIL

스킬 미적용 응답은 코드 스니펫 본문 삽입, AI 공동작성자 표기, 영문 jargon 그대로 사용 등 가드레일 위반이 자연스럽게 발생. 스킬의 12개 체크리스트가 이를 일관되게 차단.

---

## 산출물

- 시뮬레이션 결과 8개:
  - `proving-grounds/evals/git-pr/results/baseline/TC-{1..4}.md`
  - `proving-grounds/evals/git-pr/results/with-skill/TC-{1..4}.md`

---

## 개선 권고

| 우선순위 | 항목 | 액션 |
|---|---|---|
| 中 | TC-1 출력 품질 7/10 | 단순 fix에서도 "신규 생성: <URL>" 한 줄 표기 일관성 — SKILL.md Phase 3 출력 가이드에 1줄 보강 |
| 中 | 축 5 일관성 미검증 | `/eval-harness git-pr --tc TC-1 --repeat 3`로 편차 ≤ 15점 확인 후 최종 승격 |
| 低 | TC-2 출력 분량 60줄 | 측정·배포·후속까지 포함된 PR이라 자연스럽지만, 100줄 이상으로 늘려도 OK 범위 |

---

## 다음 단계

1. **INDEX.md 상태**: "테스트 대기" → **"실전 배치 가능 (일관성 검증 권장)"**
2. `--repeat 3` 일관성 검증 통과 후 → **"실전 배치 가능"**
3. pasta-japan-server 재배포: `/forge-deploy --sync` (현재 실전 v0.1 → forge v0.2)
