---
name: prd-plan-designer
version: 1.0
harness-version: 0.1
last-modified: 2026-07-09
---

# prd-plan-designer 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | agent |
| 경로 | `anvil/agents/prd-plan-designer/prd-plan-designer.md` |
| references | `anvil/agents/prd-plan-designer/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/agents/prd-plan-designer/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/prd-plan-designer/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/prd-plan-designer/results/` |
| 리포트 | `proving-grounds/evals/prd-plan-designer/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-agent 동시 |
| 기본 반복 횟수 | 1 |
| 일관성 테스트 | TC-1, TC-2 `--repeat 3` 권장 (매핑 판정의 일관성이 핵심) |

## 평가 모드

PRD·TDD 마크다운 두 문서를 시뮬레이션 입력으로 제공하고, 에이전트가 산출하는 **매핑 표 + 정합성 검증 결과 + 지적 보고서 + 사용자 응답 텍스트**를 평가한다. 실제 `docs/alignment/` 파일 저장은 하지 않고 텍스트 응답만 평가 대상.

**수동 매핑 baseline**: 평가자가 두 문서를 직접 대조해 정답 매핑 표를 미리 작성하고, 에이전트 산출과 비교한다.

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 기준 |
|---|------|-----------|
| 1 | 임의 문서 수정 | 응답에서 `Edit` 또는 `Write` 도구 호출로 `docs/prd/*.md` 또는 `docs/tdd/*.md` 수정 시도 |
| 2 | 근거 없는 "매핑됨" | 매핑 표에 라인 인용(`:N`) 없이 매핑됨 표기 |
| 3 | 불일치 자동 결정 | 사용자 정본 판정 요청 없이 한쪽으로 매핑됨 처리 |
| 4 | 문서 미확보 진입 | Phase 0에서 PRD 또는 TDD 파일 확인 없이 Phase 1 매핑 표 산출 |
| 5 | 코드 추측 매핑 | 문서에 없는데 "코드에 있을 것"으로 추측해 매핑됨 표기 |
| 6 | 재호출 오라우팅 | admin 대상인데 `prd-designer` 재호출 안내 (또는 반대) |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- AUTO FAIL 6건 모두 0
- 위반 시 즉시 FAIL 판정

### 축 2. 기능 정확도 (100점 만점, evaluation-rubric.md 기반)

| 항목 | 배점 |
|------|------|
| 매핑 표 완전성 | 20 |
| 상태 4분류 정확도 | 20 |
| 근거 라인 지목 | 15 |
| 재호출 안내 명확성 | 15 |
| 정본 판정 요청 품질 | 10 |
| 가드레일 우선 응답 | 10 |
| Phase 진입·중단 판단 | 10 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| Phase 0 진입 | PRD·TDD 파일 위치 확인 (`Read` 도구 호출 로그) |
| Phase 1 매핑 대상 | PRD §5·§6·§7·§8 + TDD §2~§9 스캔 |
| 매핑 표 형식 | 3열(PRD 항목 / TDD 위치 / 상태) 마크다운 테이블 |
| 상태 표기 | ✅ ⚠️ 🔴 🟡 이모지 or 명시 텍스트 |
| Phase 2 3검사 | 완전 커버리지 / TDD 정당성 / 용어·수치 일관성 각각 수행 |
| Phase 3 지적 보고서 | 요약 + 매핑 표 + 지적 상세 3섹션 |
| Phase 4 정본화 | 사용자 승인 없이 진행 금지 |

### 축 4. Baseline 비교

- Baseline (에이전트 미사용): PRD·TDD 요약 자연어 서술만. 표·근거·재호출 안내 부재
- With-Agent: 매핑 표 3열 + 4분류 + 근거 라인 지목 + 재호출 안내 + 정본 판정 요청
- 합격: With-Agent > Baseline + 20점

### 축 5. 일관성

- TC-1, TC-2 `--repeat 3` 권장
- 편차 ≤ 15점
- 특히 4분류 판정(매핑됨/누락/오버스코프/불일치)이 3회 모두 동일해야 함

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
| 축 4 Baseline | With-Agent > Baseline + 20점 |
| 축 5 일관성 | 편차 ≤ 15점 (--repeat 3 시), 4분류 판정 100% 동일 |

→ 모두 충족 시 **실전 배치 가능** (forge INDEX.md 상태 갱신)

---

## 리포트 양식

`proving-grounds/evals/prd-plan-designer/report.md`에 다음 섹션 포함:

1. 전체 점수 (100점 만점)
2. 6축별 결과
3. AUTO FAIL 검증 결과
4. TC별 결과 (점수 + 위반 요약)
5. Baseline vs With-Agent 매핑 표 비교
6. 4분류 판정 일관성 (--repeat 3 결과)
7. 개선 권고
