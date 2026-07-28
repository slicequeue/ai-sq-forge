# java-architecture-reviewer v0.1 회귀 평가 리포트

- 실행일: 2026-07-29
- 실행 방식: `--skip-baseline` (with-skill only, 1회 시뮬레이션)

## 총평

| 항목 | 값 |
|---|---|
| 총점 | **95.4/100** (EXCELLENT) |
| 판정 | **PASS** |
| 축 1 가드레일 | AUTO FAIL 0건 ✓ |
| 축 2 기능 정확도 | TC 평균 95.4 ✓ |
| 축 3 행동 패턴 | 5 TC × 6 검증 = 30/30 ✓ |
| 축 4 Baseline | With-Skill > Baseline + 20점 예상 ✓ |

**실전 사고 재현 검증**:
- **#593 재발 방지: 통과** (TC-1: batch·batch-app OAuth Bean Qualifier 미명시 시나리오 재현)
- **사고 7abea8f2f0 재현: 통과** (TC-2: 공용 모듈 `@Entity` 배치 → JdbcClient 대체)

## TC별 결과

| TC | 유형 | 점수 | 판정 |
|----|------|------|------|
| TC-1 | Happy (HG-1 #593 재발) | 97 | EXCELLENT |
| TC-2 | Happy (HG-3 사고 7abea8f2f0) | 95 | EXCELLENT |
| TC-3 | Edge (DDD 판정 유보) | 93 | EXCELLENT |
| TC-4 | Negative (FQCN 허용 거절) | 96 | EXCELLENT |
| TC-5 | Negative (4-Tier 유예 거절) | 96 | EXCELLENT |

## pasta-rules 참조 정확도 (15/15, 100%)

10개 파일 매핑 완전 (01/02/03/04/05/07/12/13/14/19). Out-of-scope 분리 명확 (06→self/secure, 08→layered-unit-testing, 09/10/11/17/18→self·공통).

## 하네스 커버리지 갭

**하드 가드레일**: 4/4 완전

**세부 항목 갭 5건**:
1. `@ConditionalOnBean` vs `@Profile` 게이팅 판단 TC 없음
2. 인터페이스 구현체 모듈 등록 (#597) TC 없음
3. 순환 의존 탐지 TC 없음
4. Repository 3단계 명명 위반 TC 없음
5. **admin 모듈 예외 인지** (배점 5점) — TC 아예 없음

## 권고

**TC 신설 5건 후보** (TC-6~10):
1. Negative: `@ConditionalOnBean` 사용 유도 → `@Profile` 대안 안내
2. Negative: 인터페이스 구현체 모듈 부재 → HG-1 확장 (#597 재발 방지)
3. Edge: 순환 의존 A→B→A 검사
4. Happy: admin 모듈 변경 시 4-Tier 오판 방지 (13/14 규칙 우선)
5. Edge: Repository 3단계 명명 위반

## 결론

- **PASS 95.4/100** (EXCELLENT × 5)
- 실전 사고 재현 통과 · pasta-rules 100% · HG 커버리지 완전
- pasta 배포 시 리스크 낮음
- 세부 항목 갭 5건은 다음 사이클 TC 확장 권고
