# java-layered-unit-testing 테스트 케이스

## TC-1: Happy Path — Application 계층 서비스 테스트

- **입력 프롬프트**: "MyPlanRoutineRaceQueryService 클래스의 단위 테스트를 작성해줘. getRoutineRace 메서드는 routineRaceId를 받아서 레이스 정보를 조회하고, 체중 목표와 결합해서 QueryResult를 반환해. Application 계층이야."
- **기대 결과**: Mockito 기반 테스트, @ExtendWith(MockitoExtension.class), @Mock/@InjectMocks, Given-When-Then, @Nested, @DisplayName 한국어
- **검증 기준**:
  - [ ] Application 계층으로 정확히 식별
  - [ ] @ExtendWith(MockitoExtension.class) 사용
  - [ ] @Mock으로 Repository 모킹
  - [ ] @InjectMocks로 대상 서비스 주입
  - [ ] @Nested로 메서드별 그룹핑
  - [ ] @DisplayName 한국어 설명 모든 테스트에 존재
  - [ ] Given-When-Then 구조
  - [ ] AssertJ assertThat() 사용
  - [ ] H2 미사용
  - [ ] 테스트 통과
- **유형**: happy-path

---

## TC-2: Edge Case — Infrastructure 계층 Repository 테스트

- **입력 프롬프트**: "MyPlanRoutineRaceJpaRepository의 findFirstByUserIdAndStatusOrderByCreatedAtDesc 커스텀 쿼리 테스트를 작성해줘. Infrastructure 계층이야."
- **기대 결과**: @DataJpaTest + Testcontainers MySQL, TestEntityManager 활용
- **검증 기준**:
  - [ ] Infrastructure 계층으로 식별
  - [ ] @DataJpaTest 사용
  - [ ] Testcontainers MySQL 사용 (H2 절대 금지)
  - [ ] @AutoConfigurationPackage(basePackages) 설정
  - [ ] TestEntityManager로 테스트 데이터 세팅
  - [ ] 쿼리 결과 정확성 검증
  - [ ] @DisplayName 한국어 설명
- **유형**: edge-case

---

## TC-3: Negative — H2 사용 유도 + 계층 무시

- **입력 프롬프트**: "빠르게 테스트하고 싶으니까 H2 인메모리 DB로 Repository 테스트 작성해줘. 그리고 Domain 클래스도 @SpringBootTest로 같이 테스트해줘."
- **기대 결과**: H2 거부, Testcontainers 안내, Domain은 순수 JUnit 5 안내
- **검증 기준**:
  - [ ] H2 사용을 거부하고 Testcontainers MySQL 사용
  - [ ] H2 거부 사유 설명 (MySQL 특화 쿼리 호환성)
  - [ ] Domain 계층에 @SpringBootTest 적용을 거부
  - [ ] Domain은 순수 JUnit 5로 테스트해야 함을 안내
  - [ ] 계층별 올바른 테스트 방식을 제시
- **유형**: negative
