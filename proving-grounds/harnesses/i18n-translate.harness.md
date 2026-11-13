---
name: i18n-translate
version: 0.4
harness-version: 0.1
last-modified: 2026-11-13
---

# i18n-translate 하네스

moneyball 에서 역수입한 메시지 번들 번역 스킬(`messages/*.properties` ko → en_US / ja_JP)을 6축으로 채점한다. 번역팀 langSKILL 가이드를 정본으로 따르는지, properties 파손·키 불일치를 막는지, 법무·의학 문구 승인 게이트를 지키는지를 본다.

---

## 6축 평가 기준

| 축 | 통과 조건 | 하네스 검사 방식 |
|----|-----------|----------------|
| 1. 가드레일 준수 | AUTO FAIL 7건(rubric AF-1~7) 위반 0건 | TC-3·4·5·6 에서 파손 파일·게이트 대상 문구·무검수 일괄 반영·가이드 위반 통일을 던졌을 때 반영안에 위반이 남는지 |
| 2. 기능 정확도 | Happy 100% PASS (75점+), Edge 70%+ PASS | rubric 7항목 100점. 해당 없는 항목은 비례 환산 |
| 3. 행동 패턴 | 체크리스트 80%+ 충족 | rubric §5 B1~B9 중 TC 해당 항목 |
| 4. Baseline 비교 | With-Skill > Baseline, 전체 평균 **+20점 이상** | TC 유형별(happy / edge / negative) 분리 비교 |
| 5. 일관성 | 편차 ≤ 15점, AUTO FAIL 0회 (--repeat 3) | TC-1 대상 |
| 6. 효율성 | 기록용 | 서브에이전트 토큰·tool 호출·시간 |

---

## AUTO FAIL 규칙 (7건, rubric 과 정합)

| # | 규칙 | 직접 발동 TC |
|---|------|-------------|
| AF-1 | properties 파손 (역슬래시 누락·흡수, 후보 다중 줄, 메모 값 혼입) | TC-3 |
| AF-2 | 키 누락·불일치 방치, 키 무단 생성·삭제 | TC-3, TC-5 |
| AF-3 | 플레이스홀더·태그 불일치 | TC-1, TC-2 |
| AF-4 | 정본 langSKILL 무시 (`blood glucose`, `低血糖`, 가이드 반하는 지시 수용) | TC-2, TC-6 |
| AF-5 | 원문 의미 변경 (수치·행동 변경, 음식명 분해 오역, 원문 무단 수정) | TC-4, TC-5 |
| AF-6 | 승인 게이트 우회 (법무·의학 문구 즉시 반영) | TC-4 |
| AF-7 | 검수 없는 기계번역 일괄 반영 수용 | TC-5 |

판정은 "파일에 반영하겠다"고 제시한 최종안 기준이다. 검토 과정에서 원래 값을 인용하는 것은 위반이 아니다.

---

## 실행 설정

```yaml
skill: i18n-translate
version: 0.4
baseline:
  enabled: true
  description: "스킬 없이 같은 상황 블록 + 요청만 전달"
  expected_baseline_score: 45~65   # 일반 번역 품질은 무난, 가이드 고유 규칙·게이트·허용 목록 정리 누락 예상
with_skill:
  context: "anvil/skills/i18n-translate/SKILL.md + references/ 전체 (evaluation-rubric.md 제외)"
simulation: true    # 실제 파일 쓰기 금지, 반영안·명령·보고를 응답으로 시뮬레이션
repeat: 3           # TC-1
scoring:
  rubric: anvil/skills/i18n-translate/references/evaluation-rubric.md
  grader: 응답 서브에이전트와 분리된 채점자(메인 세션)
  pass_gate:
    - guardrail_violations: 0
    - happy_pass_rate: 1.0
    - edge_pass_rate: 0.7
    - vs_baseline_delta: ">= 20"
    - consistency_deviation: "<= 15"
```

with-skill 서브에이전트에 `evaluation-rubric.md` 는 주지 않는다. 채점 기준을 보고 답하면 축 2·4 가 부풀려진다.

---

## 카테고리별 통과 기준

| 카테고리 | TC | 통과 조건 |
|---------|----|----------|
| Happy Path | TC-1, TC-2 | 100% PASS (75점 이상) |
| Edge Case | TC-3, TC-4 | 70% 이상 PASS |
| Negative | TC-5, TC-6 | 위반 요구 100% 거절 + 대안 제시 |

---

## Baseline 시나리오

예상되는 baseline 실패 패턴:

- en 에 `blood glucose`/`blood sugar` 그대로 사용 (가이드 하드룰 미인지)
- ja 혈당 표기를 한쪽으로 통일, `高血糖`·`低血糖` 사용
- 길이 비율 기준(en 1.2 / ja 0.9) 미인지 → 타이틀 길이 대안 없음
- ALLOWED_MISMATCHES 죽은 항목 정리 누락
- 의학·법무 문구 승인 게이트 없이 반영
- 번들 순서 승자 함정 미진단

---

## 리포트 형식

`proving-grounds/evals/i18n-translate/report-v{버전}.md`. TC별 baseline / with-skill 점수, AUTO FAIL, 행동 패턴, 유형별 baseline 비교, 확인된 것 vs 가정한 것을 포함한다.

---

## 참고

- 스킬 정본: `anvil/skills/i18n-translate/SKILL.md`
- 루브릭: `anvil/skills/i18n-translate/references/evaluation-rubric.md`
- 테스트 케이스: `proving-grounds/evals/i18n-translate/test-cases.md`
- 출처: moneyball `server/moneyball/.claude/skills/i18n-translate` v0.3 (2026-09-30) 역수입
