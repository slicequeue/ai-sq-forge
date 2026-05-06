# java-layered-unit-testing v1.1 회귀 평가 리포트

- **테스트 일시**: 2026-05-06
- **하네스**: `proving-grounds/harnesses/java-layered-unit-testing.harness.md`
- **스킬 버전**: v1.1 (PR #527 FQCN 절대 금지 + AUTO FAIL #5 추가)
- **모델**: Claude Sonnet
- **테스트 케이스**: TC-1 (Happy Application), TC-4 (Negative FQCN, 신규)
- **반복**: 1회
- **옵션**: `--skip-baseline` (v1.0 결과 재사용)

---

## 6축 평가 결과 요약

| 축 | 결과 | 상세 |
|---|---|---|
| 1. 가드레일 준수 | **PASS** | AUTO FAIL #5 (FQCN) 0건 위반 |
| 2. 기능 정확도 | **EXCELLENT 93.5/100 평균** | TC-1 92 / TC-4 95 |
| 3. 행동 패턴 | **4/4** | Phase 0, 패턴 탐색, GWT, 테스트 실행 의도 |
| 4. Baseline 비교 | **PASS** | v1.0 91 → v1.1 93.5 (+2.5) |

---

## TC별 상세

### TC-1 — Happy Path: Application 계층 단위 테스트 [happy-path]

| 항목 | With-Skill v1.1 |
|---|---|
| 기능 정확도 | 92 |
| 행동 패턴 | 4/4 |

**중요 발견 (v1.1 가드레일 동작 입증)**: 시뮬레이션 에이전트가 첫 코드 작성 시 `then(weightGoalReader).should(never()).readByUserId(org.mockito.ArgumentMatchers.anyLong())` 라인에 **FQCN 누수**를 발생시켰으나, **자기 검증 #11에서 자가 검출** 후 `import static org.mockito.ArgumentMatchers.anyLong;` 추가 + `anyLong()` 단순 호출로 즉시 교정. v1.1 가드레일이 **사후 교정 수준에서 정상 작동**.

판정: **PASS**

### TC-4 — Negative: FQCN 인라인 유도 (PR #527 회귀 방지) [negative, **신규**]

| 항목 | With-Skill v1.1 |
|---|---|
| 기능 정확도 | 95 |
| 사용자 허용 거부 | ✓ "한 번만 쓰니까 인라인" 무조건 거부 |
| 본문 FQCN | 0건 (mock willThrow + .class 모두 단순 클래스명) |
| AUTO FAIL #5 | 통과 |

판정: **PASS**

---

## 발견된 잠재 개선

- TC-1에서 v1.1 가드레일이 **사전 차단**보다 **사후 교정** 단계에서 작동. 코드 작성 전 prompt에 "import 우선, 풀 패키지 경로 한 줄도 박지 않음" 명시를 추가하면 사전 차단 강화 가능. 단, 자가 검증이 catch하는 한 결과 품질엔 영향 없음 — 우선순위 낮음.

## 최종 판정

**PASS — 실전 배치 가능 (v1.1)**

- 기존 TC-1 회귀 없음 (v1.0 91 → v1.1 92, +1)
- 신규 TC-4 (PR #527 회귀 방지) PASS — 사용자 명시 허용해도 거부
- AUTO FAIL #5 (FQCN) 새로 추가, 양 TC 모두 통과
