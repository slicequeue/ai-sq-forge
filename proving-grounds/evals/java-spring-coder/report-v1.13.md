# java-spring-coder v1.13 회귀 평가 리포트 (재평가)

- 실행일: 2026-07-29
- 스킬 버전: v1.13 (656줄)
- 이전 회귀: v1.11 (2026-07-09) 95/100, TC 4개 outdated 하네스
- **확장 하네스**: TC 4 → 10, AUTO FAIL 6 → 12
- 실행 방식: `--skip-baseline`

## 총평

| 항목 | 값 |
|---|---|
| 총점 | **98.5/100** (EXCELLENT) |
| 판정 | **PASS** |
| TC 통과율 | **10/10** |
| **이전 95 대비 개선** | **+3.5점** |

## TC별 결과

| TC | 유형 | 점수 |
|----|------|------|
| TC-1 | Happy TDD 쿠폰 Redeem | 100 |
| TC-2 | Edge TDD 없이 GET API | 90 |
| TC-3 | Negative H2/커밋/마이그레이션 | 100 |
| TC-4 | Negative FQCN 인라인 (PR #527) | 100 |
| TC-5 | Negative Bean Qualifier cross-module (#593·#588) | 100 |
| TC-6 | Negative Hibernate Session 오염 (#633) | 100 |
| TC-7 | Negative 광범위 catch (v1.11-B) | 100 |
| TC-8 | Edge 외부 API DTO 시간 파싱 (Dexcom #581·#582) | 95 |
| TC-9 | Negative @ConditionalOnBean (GLOB-566) | 100 |
| TC-10 | Happy @ApiGroup 어노테이션+인터셉터 (GLOB-549) | 100 |

## 신규 TC 6건 검증 (v1.6~v1.13 룰 커버리지)

| TC | 룰 | 회귀 사례 재현 | 결과 |
|----|----|-----|------|
| TC-5 | v1.7 Bean 이름 매직 스트링 금지 | #593 batch·batch-app / #588 admin | ✅ |
| TC-6 | v1.11-A Hibernate Session 오염 방지 | #633 moneyball 재발 | ✅ |
| TC-7 | v1.11-B SQL 에러코드 좁혀 판별 | #633 CodeRabbit 피드백 | ✅ |
| TC-8 | v1.10 외부 API DTO 시간 방어 | #581·#582 Dexcom | ✅ |
| TC-9 | v1.11 @ConditionalOnBean 회피 | GLOB-566 | ✅ |
| TC-10 | v1.11 어노테이션+인터셉터 | GLOB-549 | ✅ |

**하네스 커버리지 갭 해소**: 이전 v1.11 리포트에서 지적한 "실전 사고 이력 룰인데 TC 없음" 4건 전부 발동 검증 완료.

## AUTO FAIL 12건 검증

12건 중 11건 TC 직접 발동 검증. #5(git stash)만 직접 유도 TC 부재.

## 남은 갭

1. AUTO FAIL #5 (git stash) 직접 유도 TC 부재
2. TC-2 배점 재분배 -10 (TDD 없는 모드 B 구조적 한계)
3. --repeat 3 일관성 축 미실행
4. Baseline 격차 실측 미실행

## 결론

- **EXCELLENT 98.5/100 PASS** (10/10)
- **이전 95 대비 +3.5점 개선**
- 하네스 커버리지 갭 해소, 실전 사고 재현 회귀 방지 능력 확인
- pasta 배포 리스크 매우 낮음
