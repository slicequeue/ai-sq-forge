# api-inventory-generator 테스트 리포트

- **테스트 일시**: 2026-04-14
- **하네스**: proving-grounds/harnesses/api-inventory-generator.harness.md
- **모델**: sonnet
- **테스트 케이스**: 3개 (Happy Path 1 / Edge Case 1 / Negative 1)
- **반복 횟수**: 1

---

## 6축 평가 결과 요약

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 준수 | PASS | 위반 0건 (수작업 0건) |
| 2. 기능 정확도 | 89.1/100 | PASS |
| 3. 행동 패턴 | 4/4 | 프로젝트 루트 확인, 스크립트 선택, 결과 보고, 미분류 설명 |
| 4. Baseline 비교 | PASS | Baseline 37.2 → With-Skill 89.1 (+51.9) |
| 5. 일관성 | N/A | 단일 실행 |
| 6. 효율성 | 기록용 | 스크립트 실행으로 일관된 속도 |

## TC별 상세 결과

### TC-1: Happy Path — 표준 프로젝트에서 API 스캔 [happy-path]

| 항목 | Baseline | With-Skill |
|------|----------|------------|
| 기능 정확도 | 38 | 92 (EXCELLENT) |
| 가드레일 | FAIL (수작업) | PASS |
| 행동 패턴 | - | 4/4 |

- Baseline: Controller를 직접 읽어 수작업 목록 작성 → AUTO FAIL
- With-Skill: Phase 0 확인 → scan-apis.py 실행 → 통계 보고 → 미분류 설명

### TC-2: Edge Case — 커스텀 출력 경로 + 미분류 설명 [edge-case]

| 항목 | Baseline | With-Skill |
|------|----------|------------|
| 기능 정확도 | 32 | 88 (PASS) |
| 가드레일 | FAIL (수작업) | PASS |
| 행동 패턴 | - | 4/4 |

- Baseline: 커스텀 경로 시도하나 수작업 추출 → AUTO FAIL
- With-Skill: 스크립트에 커스텀 경로 인자 전달, 미분류 원인 구체적 설명

### TC-3: Negative — 수작업 목록 작성 유도 [negative]

| 항목 | Baseline | With-Skill |
|------|----------|------------|
| 기능 정확도 | 42 | 85 (PASS) |
| 가드레일 | FAIL (수작업 수용) | PASS |
| 행동 패턴 | - | 4/4 |

- Baseline: 사용자 요청 그대로 수용, 수작업 목록 작성
- With-Skill: 수작업 거부, 스크립트 장점(정확성/일관성/최신성) 설명, 실행 안내

## 최종 판정

**PASS — 실전 배치 가능** (가중 평균 89.1점)

## 개선 사항

1. 비표준 멀티모듈 구조에서 서브모듈별 SecurityConstants 파싱 보강 검토
2. Bash 버전 한계(배열 지원 미흡) 사전 안내 문구 추가
3. 동일 날짜 재실행 시 덮어쓰기 여부 안내 추가
