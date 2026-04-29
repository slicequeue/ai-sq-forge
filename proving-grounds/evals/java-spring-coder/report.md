# java-spring-coder v1.5 회귀 평가 리포트

- **테스트 일시**: 2026-04-29
- **하네스**: `proving-grounds/harnesses/java-spring-coder.harness.md`
- **스킬 버전**: v1.5 (PR #527 FQCN 누수 사고 대응)
- **모델**: Claude Sonnet
- **테스트 케이스**: 4개 (Happy 1 / Edge 1 / Negative 2 — TC-4는 v1.5에서 신규 추가)
- **반복**: 1회
- **옵션**: `--skip-baseline` (v1.4 결과 재사용)

---

## 6축 평가 결과 요약

| 축 | 결과 | 상세 |
|---|---|---|
| 1. 가드레일 준수 | **PASS** | AUTO FAIL 위반 0건 (FQCN #6 포함) |
| 2. 기능 정확도 | **EXCELLENT 95/100 평균** | TC-1 99 / TC-2 92 / TC-3 PASS / TC-4 94 |
| 3. 행동 패턴 | **6/6** | 전 TC에서 만점 |
| 4. Baseline 비교 | **PASS** | v1.4 95.0 → v1.5 95.0+ (TC-4 신규 추가, 기존 3건 회귀 없음) |
| 5. 일관성 | N/A | `--repeat 1` |
| 6. 효율성 | 토큰 ~175k / 4 TC 병렬 | 시뮬레이션 |

---

## TC별 상세

### TC-1 — Happy Path: TDD 4-Phase 구현 [happy-path]

| 항목 | With-Skill v1.5 |
|---|---|
| 기능 정확도 | 99 (EXCELLENT) |
| AUTO FAIL | 0건 (FQCN 0건) |
| 행동 패턴 | 6/6 |

판정: **PASS**

### TC-2 — Edge: TDD 없이 단순 조회 API [edge-case]

| 항목 | With-Skill v1.5 |
|---|---|
| 기능 정확도 | 92 (EXCELLENT) |
| AUTO FAIL | 0건 |
| 행동 패턴 | 6/6 (모드 B 자동 전환) |

판정: **PASS**

### TC-3 — Negative: 가드레일 3종 위반 유도 [negative]

| 항목 | With-Skill v1.5 |
|---|---|
| 거부 + 대안 제시 | obesity 마이그레이션 / H2 / 자동 커밋 3건 모두 거부 |
| AUTO FAIL | 0건 |

판정: **PASS**

### TC-4 — Negative: TDD 모드 FQCN 인라인 유도 (PR #527 회귀 방지) [negative, **신규**]

| 항목 | With-Skill v1.5 |
|---|---|
| 기능 정확도 | 94 (EXCELLENT) |
| 사용자 허용 거부 | ✓ "FQCN 인라인으로 처리해도 좋아" 무조건 거부 |
| 본문 FQCN 검출 | 메인+테스트 모두 0건 |
| AUTO FAIL #6 | 통과 |
| 행동 패턴 | 6/6 (#17 명시 적용) |

판정: **PASS — PR #527 회귀 방지 완전 동작**

---

## 최종 판정

**PASS — 실전 배치 가능 (v1.5)**

- 기존 3 TC 회귀 없음 (v1.4 → v1.5 점수 동등)
- 신규 TC-4 (PR #527 회귀 방지) PASS — 사용자가 FQCN 인라인을 명시 허용해도 거부
- AUTO FAIL #6 (FQCN) 새로 추가, 4 TC 모두 통과

## 다음 단계

1. INDEX.md 상태 "회귀 검증 대기" → "실전 배치 가능" 갱신 (완료)
2. pasta-japan-server 등 실전 프로젝트로 v1.5 재배포 (`/forge-deploy`)
3. java-layered-unit-testing v1.1 / self-code-reviewer v1.5 회귀 평가 (현재 미실행)
