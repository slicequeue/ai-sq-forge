---
name: java-composite-reviewer
version: 0.2
harness-version: 0.2
last-modified: 2026-07-29
---

# java-composite-reviewer 평가 하네스 (v0.2)

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | agent |
| 경로 | `anvil/agents/java-composite-reviewer/java-composite-reviewer.md` |
| references | `anvil/agents/java-composite-reviewer/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/agents/java-composite-reviewer/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/java-composite-reviewer/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/java-composite-reviewer/results/` |
| 리포트 | `proving-grounds/evals/java-composite-reviewer/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-agent 동시 |
| 기본 반복 횟수 | 1 |
| 일관성 테스트 | TC-1 (전체 5개 병렬), TC-4 (AUTO FAIL 통합), TC-8 (보안+비즈니스 불변식 우선순위) `--repeat 3` 권장 |
| TC 개수 | 8 (Happy 3 / Edge 2 / Negative 3) |
| 관점 개수 | 5 (self + secure + perf + arch + business-logic) |

## 평가 모드

큰 PR diff·리뷰 요청 프롬프트를 시뮬레이션 입력으로 제공. 에이전트가 **Phase 0~4를 어떻게 오케스트레이션하는지** 관찰. 실제 Task tool 호출·병렬 실행 여부·통합 리포트 구조·PRD/TDD 조건부 활성화를 평가.

**시뮬레이션 방식**: 위임 스킬의 리포트는 미리 준비한 mock 리포트 5종(각 관점별)을 반환. 에이전트가 이 리포트들을 어떻게 통합하는지 본다.

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 기준 |
|---|------|-----------|
| 1 | Phase 위반 | 프롬프트에 변경 파일 있는데 Phase 0(현황 6항목) 생략 후 바로 Task 호출 |
| 2 | 스킬 임의 skip | 사용자가 관점 미지정인데 4개 이하 스킬만 호출. 예외: business-logic은 PRD/TDD 부재 시 skip 허용 (사유 명시 필수) |
| 3 | self 누락 | 어떤 시나리오든 self-code-reviewer가 호출 대상에서 빠짐 |
| 4 | 직렬 호출 | Task tool을 여러 메시지에 나눠서 순차 호출 |
| 5 | 자의적 재해석 | 각 스킬 원본 리포트를 요약·삭제하고 본인 요약만 전달 |
| 6 | AUTO FAIL 순위 위반 | 우선순위 표에 성능/아키텍처가 보안 위에 배치, **또는 BIZ-INVARIANT를 성능·아키텍처 아래 배치**, 또는 표 자체 누락 |
| 7 | 직접 코드 수정 | Edit/Write 도구로 실제 파일 변경 시도 |
| 8 | PRD/TDD 무시 | business-logic 호출 시 문서 경로를 압축 컨텍스트에 미전달, 또는 문서 부재인데 강제 호출 |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- AUTO FAIL 7건 모두 0
- 위반 시 즉시 FAIL 판정

### 축 2. 기능 정확도 (100점 만점, evaluation-rubric.md 기반, v0.2)

| 항목 | 배점 |
|------|------|
| Phase 0 현황 점검 완결성 (6항목) | 12 |
| 관점 라우팅 정확도 (5관점) | 18 |
| Task tool 병렬 실행 (최대 5) | 13 |
| 리포트 통합 & 자의적 재해석 회피 | 12 |
| AUTO FAIL 우선순위 5단계 (보안>비즈니스🟠>성능>아키>공통) | 15 |
| BIZ-INVARIANT 우선 처리 | 8 |
| 위임 프롬프트 압축 컨텍스트 | 10 |
| 최종 보고 & 사용자 확인 | 8 |
| PRD/TDD 조건부 활성화 | 4 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| Phase 0 6항목 확인 | 브랜치/변경파일/규모/PR/**PRD·TDD 유무**/사용자 지시 파싱 |
| 관점 자동 판단 매트릭스 사용 | Repository→perf, Controller→sec, **Service·Domain→business-logic 우선** 힌트 참고 (skip 근거 아님) |
| Task tool 병렬 (최대 5) | 1 메시지 N개 동시 발행 |
| 위임 프롬프트 압축 | 파일 목록 + 요약 + PR 본문 20줄 + 정본 위치 + **PRD/TDD 경로 (business-logic 호출 시)** |
| 원본 리포트 첨부 | 통합 리포트 하단에 5개 관점 원본 그대로 |
| AUTO FAIL 우선순위 표 | 상단 배치, **보안 > 비즈니스 불변식🟠 > 성능 > 아키 > 공통** |
| BIZ 5분류 판정 표시 | 🟠 불변식 > 🔴 미구현 > 🟡 사각지대 > ⚠️ 부분 > ✅ 매핑 |
| 중복 발견 병합 | 같은 파일:라인 여러 관점 지적은 병합 + 각주 |
| 사용자 확인 3분기 | y/n/상세 명시 |
| PRD/TDD 조건부 활성화 | 문서 존재 → business-logic 활성화 / 부재 → 자동 skip + 사유 |

### 축 4. Baseline 비교

- **Baseline (에이전트 미사용)**: 사용자가 각 스킬을 순차 호출. AUTO FAIL 우선순위·중복 병합·통합 리포트 없음. 관점 자동 판단도 없음. PRD/TDD 조건부 활성화 없음
- **With-Agent**: Phase 0 현황 + 최대 5개 병렬 + 우선순위 통합 (5단계, BIZ-INVARIANT 포함) + 원본 첨부 + PRD/TDD 조건부 + coding-implementer 위임 안내
- 합격: **With-Agent > Baseline + 25점** (오케스트레이션 효과가 커서 상향)

### 축 5. 일관성

- TC-1 (전체 5개 병렬), TC-4 (AUTO FAIL 통합), TC-8 (보안+비즈니스 불변식 우선순위) `--repeat 3` 권장
- 편차 ≤ 15점

### 축 6. 효율성

- 기록용 (합격 조건 아님)
- 토큰 사용량 / Task 호출 시간 (병렬 vs 직렬 대비)

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | AUTO FAIL 0건 |
| 축 2 기능 정확도 | Happy Path 75점+ |
| 축 3 행동 패턴 | 체크리스트 80%+ |
| 축 4 Baseline | With-Agent > Baseline + 25점 |
| 축 5 일관성 | 편차 ≤ 15점 (--repeat 3 시) |

→ 모두 충족 시 **실전 배치 가능** (forge INDEX.md 상태 갱신)

---

## 리포트 양식

`proving-grounds/evals/java-composite-reviewer/report.md`에 다음 섹션 포함:

1. 전체 점수 (100점 만점)
2. 6축별 결과
3. AUTO FAIL 검증 결과 (7건)
4. TC별 결과 (점수 + 위반 요약 + 병렬/직렬 여부)
5. Baseline vs With-Agent 비교 표 (관점 라우팅·병렬 실행·우선순위 통합 3축)
6. 개선 권고
