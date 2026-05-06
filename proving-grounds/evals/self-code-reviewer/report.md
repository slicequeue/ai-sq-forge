# self-code-reviewer v1.5 회귀 평가 리포트

- **테스트 일시**: 2026-05-06
- **하네스**: `proving-grounds/harnesses/self-code-reviewer.harness.md`
- **스킬 버전**: v1.5 (FQCN 검출 항목 + 19-architecture-boundaries 통합)
- **모델**: Claude Sonnet
- **테스트 케이스**: TC-1 (Happy 4건 위반 검출), TC-4 (Edge FQCN 검출)
- **반복**: 1회
- **옵션**: `--skip-baseline` (v1.4 결과 재사용)

---

## 6축 평가 결과 요약

| 축 | 결과 | 상세 |
|---|---|---|
| 1. 가드레일 준수 | **PASS** | 코드 변경 0건, 커밋·push·stash 0건 |
| 2. 기능 정확도 | **EXCELLENT 94/100 평균** | TC-1 93 / TC-4 95 |
| 3. 행동 패턴 | **6/6** | 전체 충족 |
| 4. Baseline 비교 | **PASS** | v1.4 95 → v1.5 94 (사실상 동률, FQCN 항목 추가로 검출 폭 확대) |

---

## TC별 상세

### TC-1 — Happy Path: 규칙 위반 4건 리뷰 [happy-path]

| 위반 | 검출 | 우선순위 |
|---|---|---|
| Domain `@Entity` | ✓ | P1 (가드레일) |
| `var coupon` | ✓ | P3 (컨벤션) |
| SecurityConstants 미등록 | ✓ | P4 (설정 누락) |
| env yml 4곳 미반영 | ✓ | P4 (설정 누락) |

기능 정확도 93. 모든 위반 정확 분류 + 파일·위치·수정 방향 명시. 9항목 자기검증 PASS.

판정: **PASS**

### TC-4 — Edge: 테스트 파일 FQCN 검출 (PR #527 회귀 방지) [edge-case]

| 검출 항목 | 결과 |
|---|---|
| 테스트 파일 `new x.y.Z()` 인라인 | ✓ 명시 검출 |
| 테스트 파일 `.isInstanceOf(x.y.Z.class)` 인라인 | ✓ 명시 검출 |
| 메인 코드 (정상 import) 오탐 | 0건 |
| 필수 수정 등급 분류 | ✓ |
| "테스트라 한 번만"은 면죄부 아님 명시 | ✓ |

기능 정확도 95. 9항목 #9 FQCN 검사 PASS.

판정: **PASS — PR #527 회귀 방지 자체 리뷰 단계에서 차단 동작**

---

## 최종 판정

**PASS — 실전 배치 가능 (v1.5)**

- 기존 TC-1 회귀 없음
- TC-4 (FQCN 검출) PASS — 자체 리뷰 단계에서 PR #527 패턴 정확히 차단 (메인 vs 테스트 구분, 오탐 0)
- 19-architecture-boundaries 통합도 함께 적용 (TC-1 응답 자체엔 해당 케이스 없으나 review-checklist에 반영됨)
