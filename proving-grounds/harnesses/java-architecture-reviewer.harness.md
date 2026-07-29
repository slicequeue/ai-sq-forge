---
name: java-architecture-reviewer
version: 0.1
harness-version: 0.2
last-modified: 2026-07-29
---

# java-architecture-reviewer 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/java-architecture-reviewer/SKILL.md` |
| references | `anvil/skills/java-architecture-reviewer/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/java-architecture-reviewer/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/java-architecture-reviewer/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/java-architecture-reviewer/results/` |
| 리포트 | `proving-grounds/evals/java-architecture-reviewer/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |
| 일관성 테스트 | TC-1 `--repeat 3` 권장 |
| TC 개수 | **10** (Happy 3 / Edge 3 / Negative 4) |

## 평가 모드

리뷰 리포트(AUTO FAIL / 필수 수정 / 권장 개선 표 + 로드된 규칙 명시 + 검사 통과 항목 + 사용자 응답 텍스트)를 시뮬레이션 입력으로 받아 평가한다. 실제 `git diff` / 파일 편집은 하지 않고, **스킬이 산출하는 리포트 + 사용자에게 하는 응답**을 평가 대상으로 삼는다.

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 기준 | 직접 발동 TC |
|---|------|-----------|-------------|
| 1 | HG-1 미검출 | Bean Qualifier cross-module 위반 or 구현체 모듈 부재 미보고 | TC-1 / TC-7 |
| 2 | HG-2 미검출 | Domain→Infrastructure 등 4-Tier 위반 미보고 | TC-5 |
| 3 | HG-3 미검출 | 공용 모듈 @Entity 배치 미보고 | TC-2 |
| 4 | HG-4 미검출 | FQCN 인라인 미보고 | TC-4 |
| 5 | 범위 침범 | 보안·성능·문법·Hibernate Session·i18n 위반을 이 스킬 결과에 정식으로 넣음 | — |
| 6 | 코드 수정 시도 | 리뷰 결과 대신 파일 편집·커밋·push 시도 | — |
| 7 | admin 4-Tier 오탐 | admin 모듈 파일에 4-Tier 위반 판정 (13/14 규칙 미참조) | TC-9 |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- AUTO FAIL 6건 모두 0
- 위반 시 즉시 FAIL 판정 (다른 축 점수 무관)

### 축 2. 기능 정확도 (100점 만점, evaluation-rubric.md 기반)

| 항목 | 배점 |
|------|------|
| AUTO FAIL 검출 정확도 | 20 |
| pasta-rules 참조 정확도 | 15 |
| Bean 관리 검사 품질 | 15 |
| 4-Tier + 모듈 관계 검사 | 15 |
| 패턴 준수 검사 | 10 |
| 스코프 준수 | 10 |
| 리포트 형식 준수 | 10 |
| admin 모듈 예외 인지 | 5 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 사전 확인 | Phase 0 브랜치 · 비교 기준 · 변경 범위 · admin 포함 여부 · rules 위치 결정 |
| 규칙 로드 | 변경 유형별 필요한 pasta-rules 파일 Read (경로만 아니라 실제 인용) |
| 5카테고리 검사 | 4-Tier · Bean · 모듈 · 패턴 · pasta-rules 컨벤션 순서 |
| FQCN 검사 | 메인 + 테스트 코드 모두 대상 |
| AUTO FAIL 처리 | 발견 즉시 별도 섹션 상단 배치 |
| 검사 통과 항목 | 위반 없는 항목도 리포트에 명시 |
| out-of-scope 안내 | 다른 관점 위반 발견 시 담당 스킬 링크만 |

### 축 4. Baseline 비교

- Baseline (스킬 미사용): 자유 서술 리뷰, AUTO FAIL 개념 없음, pasta-rules 참조 없음, 스코프 침범 흔함
- With-Skill: AUTO FAIL 명시적 판정, 규칙 파일 실제 인용, 스코프 지킴, 표 형식 리포트
- 합격: With-Skill > Baseline + 20점

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
| 축 4 Baseline | With-Skill > Baseline + 20점 |
| 축 5 일관성 | 편차 ≤ 15점 (--repeat 3 시) |

→ 모두 충족 시 **실전 배치 가능** (forge INDEX.md 상태 갱신)

---

## 리포트 양식

`proving-grounds/evals/java-architecture-reviewer/report.md`에 다음 섹션 포함:

1. 전체 점수 (100점 만점)
2. 6축별 결과
3. AUTO FAIL 검증 결과
4. TC별 결과 (점수 + 위반 요약)
5. Baseline vs With-Skill 비교 표
6. 개선 권고
