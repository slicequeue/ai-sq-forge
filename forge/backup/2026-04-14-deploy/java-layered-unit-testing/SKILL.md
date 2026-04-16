---
description: Senior Java Spring Boot unit testing guidelines for layered architecture (Web, Application, Domain, Infrastructure). Adheres to project conventions including pure domain tests, Mockito-based application/web tests, and Testcontainers-based infrastructure tests. Use when the user asks to write tests, add unit tests, or test a specific class/layer.
---

# Layered Unit Testing (Java/Spring Boot)

## Instructions

Follow these guidelines based on the layer of the class being tested. Always use **JUnit 5**, **Mockito**, and **AssertJ**. Use **JDK 21**.

### 1. Domain Layer (`domain/`)
Domain entities and logic should be "pure" and free from Spring/JPA dependencies.

- **Type**: Pure JUnit 5 unit test.
- **Dependencies**: None or minimal mocks.
- **Focus**: Business logic, state transitions, validation, and domain-driven rules.
- **Example**:
  ```java
  @Test
  @DisplayName("목표 감량치가 주당 0.5kg이면 일일 적자 칼로리는 500kcal이다")
  void calculateDailyDeficit() {
      MyPlanNutrientRatio ratio = new MyPlanNutrientRatio(2000, false);
      assertThat(ratio.getCarbohydrateGram()).isEqualTo(200.0f);
  }
  ```

### 2. Application Layer (`application/`)
Handles use cases, flow control, and DTO mapping.

- **Type**: Mockito-based unit test.
- **Annotations**: `@ExtendWith(MockitoExtension.class)`, `@Mock`, `@InjectMocks`.
- **Focus**: Coordination logic, calling domain services/entities, repository interface interactions, and DTO conversion.
- **Pattern**: `Given-When-Then` style. Use `@Nested` for grouping method-specific tests.
- **Example**:
  ```java
  @ExtendWith(MockitoExtension.class)
  class MyPlanRoutineRaceQueryServiceTest {
      @Mock private MyPlanRoutineRaceRepository repository;
      @InjectMocks private MyPlanRoutineRaceQueryService service;

      @Test
      void returnsQueryResult_whenRaceExists() {
          // given
          when(repository.findById(1L)).thenReturn(Optional.of(mockRace));
          // when
          var result = service.getRoutineRace(new MyPlanRoutineRaceIdInDto(1L));
          // then
          assertThat(result.routineRaceId()).isEqualTo(1L);
      }
  }
  ```

### 3. Web Layer (`web/`)
Handles requests, validation, and response formatting.

- **Type**: Unit test with Mockito (standard) or `@WebMvcTest` (if integration with Spring MVC is needed).
- **Focus**: Controller logic, request mapping, status codes, and proper DTO usage.
- **Example**: Use `@InjectMocks` on the controller and `@Mock` for services. Verify `ResponseEntity` status and body.

### 4. Infrastructure Layer (`infrastructure/`)
Handles DB persistence and external API clients.

- **Type**: `@DataJpaTest` for repositories.
- **MANDATORY (Guardrail)**: Always use **Testcontainers (MySQL)**. Never use H2 for testing MySQL-specific queries.
- **Focus**: Query accuracy, mapping correctness, and DB constraints.
- **Example**:
  ```java
  @DataJpaTest
  @AutoConfigurationPackage(basePackages = { "com.kakaohealthcare..." })
  class MyRepositoryTest {
      @Autowired private MyJpaRepository repository;
      @Autowired private TestEntityManager em;
  }
  ```

## General Conventions

1.  **Naming**: Class name should be `{ClassName}Test`. Methods should be descriptive or use `whenX_thenY`.
2.  **Display Names**: Use `@DisplayName("한국어 설명")` for all test classes and methods.
3.  **Assertions**: Always use AssertJ's `assertThat()`.
4.  **Formatting**: Run `./gradlew :pasta-api:spotlessApply` (or module equivalent) after writing tests.
5.  **Clean Code**: Avoid redundant comments. Early return in tests where applicable. Use Constants for recurring test data.

## Workflow Pattern

1.  Identify the layer of the class.
2.  Select the appropriate testing type (Pure, Mockito, or DataJpaTest).
3.  Implement setup logic (Mocking or Persisting).
4.  Write test cases using Given-When-Then.
5.  **Verify**: Run the test using `./gradlew :{module}:test --tests {ClassName}`.

## Examples

### Domain Layer Example (Pure JUnit 5)

```java
// MyPlanNutrientRatioTest.java
class MyPlanNutrientRatioTest {
  @Test
  @DisplayName("2000kcal 기준 탄수화물 그램 = 40% * 2000 / 4 = 200g")
  void carbohydrateGram_2000kcal() {
    MyPlanNutrientRatio ratio = new MyPlanNutrientRatio(2000, MyPlanNutrientRatioType.GENERAL);
    assertThat(ratio.getCarbohydrateGram()).isEqualTo(200.0f);
  }
}
```

### Application Layer Example (Mockito)

```java
// MyPlanRoutineRaceQueryServiceTest.java
@ExtendWith(MockitoExtension.class)
class MyPlanRoutineRaceQueryServiceTest {
  @Mock private MyPlanRoutineRaceRepository routineRaceRepository;
  @Mock private MyPlanWeightGoalRepository weightGoalRepository;
  @InjectMocks private MyPlanRoutineRaceQueryService queryService;

  @Nested
  @DisplayName("getRoutineRace")
  class GetRoutineRace {
    @Test
    @DisplayName("레이스가 존재하고 체중 목표가 있으면 QueryResult를 반환한다")
    void returnsQueryResult_whenRaceAndWeightGoalExist() {
      // Given
      Long routineRaceId = 1L;
      when(routineRaceRepository.findById(routineRaceId)).thenReturn(Optional.of(mockRace));
      when(weightGoalRepository.findById(any())).thenReturn(Optional.of(mockWeightGoal));

      // When
      MyPlanRoutineRaceQueryResult result = queryService.getRoutineRace(new MyPlanRoutineRaceIdInDto(routineRaceId));

      // Then
      assertThat(result.routineRaceId()).isEqualTo(routineRaceId);
      verify(routineRaceRepository).findById(routineRaceId);
    }
  }
}
```

### Infrastructure Layer Example (@DataJpaTest)

```java
// MyPlanRoutineRaceJpaRepositoryTest.java
@DataJpaTest
@AutoConfigurationPackage(basePackages = { "com.kakaohealthcare.moneyball.myplan" })
class MyPlanRoutineRaceJpaRepositoryTest {
  @Autowired private MyPlanRoutineRaceJpaRepository repository;
  @Autowired private TestEntityManager em;

  @Test
  @DisplayName("특정 사용자의 활성 레이스를 조회하면, 가장 최근의 활성 레이스가 반환된다")
  void findByUserIdAndStatus() {
    // Given
    MyPlanRoutineRaceJpaEntity entity = MyPlanRoutineRaceJpaEntity.builder()
        .userId(1L)
        .status(MyPlanRoutineStatus.ACTIVE)
        .build();
    em.persistAndFlush(entity);

    // When
    Optional<MyPlanRoutineRaceJpaEntity> result = repository.findFirstByUserIdAndStatusOrderByCreatedAtDesc(1L, MyPlanRoutineStatus.ACTIVE);

    // Then
    assertThat(result).isPresent();
    assertThat(result.get().getUserId()).isEqualTo(1L);
  }
}
```
