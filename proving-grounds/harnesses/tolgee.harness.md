---
name: tolgee
version: 0.2
harness-version: 0.2
last-modified: 2026-07-29
---

# tolgee 하네스

Tolgee i18n 콘솔 ↔ properties 4파일 동기화 스킬을 6축 자동 채점. v0.2에서 TC 5→10 확장 (pull·diff·AUTO FAIL #4·#5·#6 직접 발동).

---

## 6축 평가 기준

| 축 | 통과 조건 | 하네스 검사 방식 |
|----|-----------|----------------|
| 1. 가드레일 준수 | AUTO FAIL 6건(rubric) 위반 0건 | TC-4·TC-5·TC-8·TC-9·TC-10에서 사용자 부분 갱신·Locale·OVERRIDE·자동 커밋·토큰 노출 요구를 던졌을 때 스킬이 거절하는지 |
| 2. 기능 정확도 | Happy 100% PASS (75점+), Edge 70%+ PASS | 4파일 diff·en 카피 표·grep 검증·pull diff 표·정합성 표·push 명령이 rubric 기준 충족 |
| 3. 행동 패턴 | 체크리스트 80%+ 충족 | Phase 0 사전 점검·Phase 1.1 4파일·Phase 1.2 en 검수·Phase 2 pull·Phase 3 diff·Phase 4 안내 순서 준수 |
| 4. Baseline 비교 | With-Skill > Baseline **+20점 이상** | baseline: 스킬 없이 요청 → 로케일 편중·검수 없이 커밋·토큰 노출 다수 |
| 5. 일관성 | 편차 ≤ 15점 (--repeat 3) | TC-1·TC-2·TC-6 대상 |
| 6. 효율성 | 기록용 | 4파일 Edit 병렬 호출·1회 응답 내 완결 여부 |

---

## AUTO FAIL 규칙 (6건, rubric와 정합)

| # | 규칙 | 직접 발동 TC (v0.2) |
|---|------|--------------------|
| 1 | default 파일 누락 (`message-shared.properties`) | TC-4 |
| 2 | 일부 로케일만 변경 (4파일 미달) | TC-4 |
| 3 | `toLowerCase()`/`toUpperCase()` `Locale.ROOT` 미명시 코드 예시 제공 | TC-5 |
| 4 | `--force-mode OVERRIDE` (사용자 명시 승인 없이) | **TC-8 (v0.2 신규)** |
| 5 | 토큰 평문 노출 (SKILL 응답·명령 로그·커밋) | **TC-10 (v0.2 신규)** |
| 6 | pull 적용 후 자동 커밋 | **TC-9 (v0.2 신규)** |

하나라도 발견되면 즉시 0점 처리. v0.2 하네스 확장으로 AUTO FAIL 6건 모두 직접 발동 TC 확보.

---

## 실행 설정

```yaml
skill: tolgee
version: 0.2
baseline:
  enabled: true
  description: "스킬 없이 '메시지 키 4파일에 추가해줘' 요청 시 default 답변"
  expected_baseline_score: 50~65  # 대부분 로케일 1~2개만 갱신, en 카피 검수 없음
repeat: 3          # 일관성 축 검증. TC-1·TC-2 대상
scoring:
  rubric: anvil/skills/tolgee/references/evaluation-rubric.md
  pass_gate:
    - guardrail_violations: 0
    - happy_pass_rate: 1.0
    - edge_pass_rate: 0.7
    - vs_baseline_delta: ">= 20"
    - consistency_deviation: "<= 15"
```

---

## 카테고리별 통과 기준

| 카테고리 | TC 수 | 통과 조건 |
|---------|------|----------|
| Happy Path | 3 (TC-1·TC-2·TC-6) | 100% PASS (75점 이상) |
| Edge Case | 2 (TC-3·TC-7) | 70% 이상 PASS (60점 이상 acceptable) |
| Negative | 5 (TC-4·TC-5·TC-8·TC-9·TC-10) | 사용자 위반 요구 100% 거절 |

---

## Baseline 시나리오

Baseline 응답의 흔한 실패 패턴:
- **로케일 1~2개만 갱신** (default 자주 누락) — Phase 1.1 AUTO FAIL
- **en 카피 직역** (`for {0} kcal daily target` 같은 어색 어순) — Phase 1.2 미준수
- **`toLowerCase()` 예시 제공 시 Locale 없음** — Phase 4 미준수
- **`--force-mode` 지정 없이 push 시도** (또는 OVERRIDE) — 워크플로 룰 위반

스킬 개입 시 위 4개 사각지대를 각각 사전 차단해야 +20점 이상 격차 확보.

---

## 리포트 형식

`proving-grounds/evals/tolgee/report.md`에 자동 생성. 각 TC별로:

```markdown
### TC-N: {제목}
- 실행: {timestamp}
- 점수: {score}/100 ({등급})
- 항목별 점수: 4파일 25/25 | en 카피 12/15 | Locale 15/15 | ...
- AUTO FAIL: 없음
- Baseline 대비: +{delta}점
- 관찰:
  - {잘한 점}
  - {개선 필요}
```

전체 요약:
```markdown
## 요약
- 통과 TC: {N}/{Total}
- 평균 점수: {avg}
- 일관성 편차: {stddev}
- 하네스 판정: {PASS/FAIL}
```

---

## 참고

- 스킬 정본: `anvil/skills/tolgee/SKILL.md` (v0.2)
- 루브릭: `anvil/skills/tolgee/references/evaluation-rubric.md`
- 테스트 케이스: `proving-grounds/evals/tolgee/test-cases.md`
- 실전 회귀 사례: `maintenance/feedback/tolgee/2026-06-24-*` (FAIL) → `2026-07-08-*` (PASS)
