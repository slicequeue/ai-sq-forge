# java-layered-unit-testing 테스트 리포트

- **테스트 일시**: 2026-04-14
- **하네스**: proving-grounds/harnesses/java-layered-unit-testing.harness.md
- **모델**: sonnet
- **테스트 케이스**: 3개 (Happy Path 1 / Edge Case 1 / Negative 1)
- **반복 횟수**: 1

---

## 6축 평가 결과 요약

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 준수 | PASS | 위반 0건 (H2 0건, Domain Spring 0건) |
| 2. 기능 정확도 | 91.3/100 | EXCELLENT |
| 3. 행동 패턴 | 4/4 | 계층 식별, 기존 패턴 탐색, GWT 구조, 테스트 실행 |
| 4. Baseline 비교 | PASS | Baseline 31.3 → With-Skill 91.3 (+60.0) |
| 5. 일관성 | N/A | 단일 실행 (TC간 편차 4점, ≤15 기준 충족) |
| 6. 효율성 | 기록용 | - |

## TC별 상세 결과

### TC-1: Happy Path — Application 계층 서비스 테스트 [happy-path]

| 항목 | Baseline | With-Skill |
|------|----------|------------|
| 기능 정확도 | 31 | 93 (EXCELLENT) |
| 가드레일 | FAIL (@SpringBootTest) | PASS |
| 행동 패턴 | - | 4/4 |

- Baseline: @SpringBootTest로 전체 컨텍스트 로드, @DisplayName 없음, assertEquals 사용
- With-Skill: Phase 0 → @ExtendWith(MockitoExtension.class) + @Mock/@InjectMocks + @Nested + @DisplayName 한국어 + GWT + AssertJ

### TC-2: Edge Case — Infrastructure 계층 Repository 테스트 [edge-case]

| 항목 | Baseline | With-Skill |
|------|----------|------------|
| 기능 정확도 | 38 | 89 (PASS) |
| 가드레일 | FAIL (H2 사용) | PASS |
| 행동 패턴 | - | 4/4 |

- Baseline: @DataJpaTest + H2 인메모리 → AUTO FAIL
- With-Skill: @DataJpaTest + Testcontainers MySQL + @AutoConfigurationPackage + TestEntityManager

### TC-3: Negative — H2 유도 + 계층 무시 [negative]

| 항목 | Baseline | With-Skill |
|------|----------|------------|
| 기능 정확도 | 25 | 92 (EXCELLENT) |
| 가드레일 | FAIL (H2 + Domain Spring) | PASS |
| 행동 패턴 | - | 4/4 |

- Baseline: 사용자 요청대로 H2 + Domain @SpringBootTest 적용 → AUTO FAIL 2건
- With-Skill: H2 거부(MySQL 호환성 사유), Domain @SpringBootTest 거부(순수 JUnit 안내), 올바른 대안 제시

## 최종 판정

**PASS — 실전 배치 가능 (EXCELLENT, 평균 91.3점)**

## 개선 사항

1. Testcontainers 설정 상세도 보완 (@DynamicPropertySource 또는 application-test.yml 예시 추가)
2. DB 제약조건 검증 패턴(유니크, NOT NULL) 예시 추가
3. Web 계층(@WebMvcTest) TC 추가 시 커버리지 향상
4. spotlessApply 자동화 안내 강화
