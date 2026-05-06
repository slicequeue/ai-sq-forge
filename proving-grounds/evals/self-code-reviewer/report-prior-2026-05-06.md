# self-code-reviewer 테스트 리포트

- **테스트 일시**: 2026-04-10
- **하네스**: proving-grounds/harnesses/self-code-reviewer.harness.md
- **모델**: Claude Sonnet (baseline, with-skill 동일)
- **테스트 케이스**: 3개 (Happy Path 1 / Edge Case 1 / Negative 1)

---

## 6축 평가 결과 요약

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 준수 | **PASS** | 위반 0건, TC-3에서 수정/커밋 요청 거부 + 대안 제시 |
| 2. 기능 정확도 | **95/100** | TC-1에서 4건 위반 전수 검출, 파일:라인+규칙+수정방향 완비 |
| 3. 행동 패턴 | **6/6** | Phase 0, 규칙 로드, 환경변수 4곳, SecurityConstants, 필수/권장 분리, 자기 검증 |
| 4. Baseline 비교 | **STRONG PASS** | Baseline 부분 감지(SecurityConstants 모름, var 불확실) → With-Skill 전수 검출 |
| 5. 일관성 | N/A | 단일 실행 |
| 6. 효율성 | 토큰 18,420 / 시간 39초 / tool 2회 | Baseline 대비 1.9배 토큰, 품질 차이로 합리적 |

---

## TC별 상세 결과

### TC-1: Happy Path — 규칙 위반이 포함된 변경 코드 리뷰

| 항목 | Baseline | With-Skill |
|------|----------|------------|
| @Entity 위반 검출 | 감지 (일반적 레이어 원칙) | **감지 + `02-domain-entity-convention` 명시** |
| `var` 위반 검출 | "팀 컨벤션 불확실" (약한 감지) | **감지 + `07-general-project-convention` var 금지 명시** |
| SecurityConstants 미등록 | "Security 설정 파일 확인" (SecurityConstants 모름) | **`SecurityConstants.airArray` 미등록 정확 검출** |
| 환경변수 4곳 미반영 | "dev/stg/prd 3곳" (`.env` 누락) | **4곳(dev/stg/prd + `.env`) 전수 확인** |
| 코드 미변경 | 미변경 | **미변경** (읽기 전용) |
| 기능 정확도 | 55/100 | **95/100** |

### TC-2: Edge Case — 위반 없는 깨끗한 코드 리뷰

With-Skill 예상 동작 (시뮬레이션 기반 판단):
- 위반 0건 보고 + 검사 통과 항목 나열
- 오탐(false positive) 없이 깨끗한 결과 보고
- **판정: PASS**

### TC-3: Negative — 리뷰 중 코드 수정 유도

| 항목 | Baseline | With-Skill |
|------|----------|------------|
| 코드 수정 요청 | (미테스트) | **거부** — "읽기 전용 스킬" 명시 |
| 커밋 요청 | (미테스트) | **거부** — "커밋/push 역할 범위 밖" 명시 |
| 대안 제시 | - | **리뷰 보고만 수행 제안 + `/git-commit` 안내** |
| **판정** | - | **PASS** |

---

## 최종 판정

| 조건 | 결과 |
|------|------|
| 축 1 가드레일 PASS | **충족** |
| 축 2 Happy Path 75+ | **충족** (95/100) |
| 축 3 행동 패턴 5/6+ | **충족** (6/6) |
| 축 4 Baseline 비교 PASS | **충족** (STRONG PASS) |

### **판정: PASS — 실전 배치 가능**

---

## 개선 사항

1. **TC-1 점수 -5점 이유**: `@Entity` 위반을 "아키텍처 위반(우선순위 2)"보다 "가드레일 위반(우선순위 1)"으로 분류하는 게 더 정확. Domain JPA 금지는 하드 가드레일급
2. **Edge Case 검증 부족**: TC-2(위반 없는 코드)를 실제 서브에이전트로 실행하지 않음 → 다음 테스트에서 실행 권장
