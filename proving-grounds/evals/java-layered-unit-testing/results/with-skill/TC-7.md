<!-- TC-7 with-skill / skill v1.8 / sonnet / 2026-11-13 / 95,191 tok / tool 6 / 129s -->

# Glp1InjectionPlan 등록/수정 API 테스트 설계 (시뮬레이션, 파일 미작성)

## 1. 대상과 방식 (Phase 0)

| 대상 | 계층 (근거) | 방식 |
|---|---|---|
| `Glp1InjectionPlanController` | Web (`web/`, `@Valid` 요청 → UseCase 위임) | `@WebMvcTest` + `@TestConfiguration` 의 `@Primary` Spy UseCase |
| `Glp1InjectionPlanCommandService` | Application (domain 인터페이스 `Glp1InjectionPlanRepository` 만 사용) | 순수 JUnit + `FakeGlp1InjectionPlanRepository` |

- 규칙 08 §2 에 따라 Repository 는 Mock 이 아니라 Fake 로 둔다.
- Web 은 Spring 컨텍스트가 필요한 계층이다. 다만 규칙 08 §2 의 "`@MockBean` 최소화" 취지에 맞춰 UseCase 를 `@MockBean` 이 아니라 `@Primary` Spy 로 주입한다.
- 아래 클래스는 모두 파일로 쓰지 않았고 이 응답에 설계안으로만 담았다.

## 2. 요청과 다르게 진행한 부분 (스킬 규칙 우선)

1. **"검증은 등록 쪽만"을 따르지 않았다.**
   - RR-14 / SKILL "새 검증은 모든 진입 경로에서" 규칙이 있다. 같은 `Glp1InjectionPlanRequest` 에 붙은 `@Min/@Max` 는 PUT 에도 적용되고, #800 에서 이 경로가 빠져 리뷰 지적을 받았다.
   - 그래서 POST 와 PUT 을 둘 다 테스트한다. 파라미터화 테스트라 비용은 작다.
2. **"`notificationEnabled` 는 true 로만 보내서 확인"을 따르지 않았다.**
   - 엔티티 기본값이 `true` 라서 `true` 요청은 매핑 코드를 지워도 통과한다(#791).
   - 그래서 `false` 를 보낸다. `null` 은 기본값 유지로 따로 검증한다. 수정 경로는 기존 `false` → 요청 `true`, 기존 `true` → 요청 `false` 양방향을 본다.
3. **`jsonPath("$.memo").doesNotExist()` 를 쓰지 않았다.**
   - 계약은 키가 있고 값이 JSON null 인 것이다. `doesNotExist()` 는 키가 없어도, 값이 null 이어도 통과해서 계약을 구분하지 못한다(#801).
   - 그래서 `hasJsonPath()` 와 `value(nullValue())` 로 검증한다. 키가 생략되면 앞쪽에서 실패하고, 값이 null 이 아니면 뒤쪽에서 실패한다.

## 3. 확인된 것 vs 가정

확인된 것은 전제 조건에 명시된 내용이다.
- 엔드포인트 두 개, `@Valid` 요청, `ResponseEntity` 반환
- `intervalDays` 는 `@Min(1) @Max(28) Integer`, `notificationEnabled` 는 `Boolean`
- 엔티티 기본값은 `true`
- 요청이 null 이면 기본값 유지
- 응답 `memo` 는 JSON null 계약

실제 코드가 없어서 아래는 가정이다. 하나라도 어긋나면 컴파일 단계에서 드러나므로 Phase 0 에서 가장 먼저 대조한다.

| # | 가정 | 어긋나면 |
|---|---|---|
| A1 | UseCase 시그니처: `register(Long userId, Glp1InjectionPlanInDto)`, `update(Long userId, Long planId, Glp1InjectionPlanInDto)`. 반환은 `Glp1InjectionPlanOutDto(planId, intervalDays, notificationEnabled, memo)` | Spy 시그니처 수정 |
| A2 | `Glp1InjectionPlanInDto` 는 `intervalDays()`, `notificationEnabled()`, `memo()` 를 가진 record | 접근자 이름 수정 |
| A3 | 요청 필드는 `intervalDays`, `notificationEnabled`, `memo` 만이라고 가정했다. 다른 필수 필드가 있으면 `requestJson()` 에 추가해야 한다 | 아래 주의 참고 |
| A4 | 성공 응답은 POST/PUT 모두 200 (`status().isOk()`) | 컨트롤러의 실제 상태 코드로 교체 |
| A5 | 사용자 식별은 기존 `@WebMvcTest` 가 쓰는 방식을 따른다. `authenticated()` 헬퍼는 같은 패키지 기존 컨트롤러 테스트의 패턴으로 교체한다 | 헬퍼 본문 교체 |
| A6 | Repository 메서드는 `save(entity)` 와 `findByIdAndUserId(planId, userId)`, 엔티티는 `getId()`, `getUserId()`, `getIntervalDays()`, `getNotificationEnabled()`, 빌더를 가진다 | Fake 와 헬퍼 수정 |
| A7 | 수정 시 대상 없음은 `Glp1InjectionPlanNotFoundException` | 실제 예외 계층으로 교체 |

A3 주의: 필수 필드가 더 있는데 JSON 에서 빠지면 "범위 위반" 케이스가 다른 이유로 400 이 되어 통과할 수 있다. 이를 막으려고 경계 안쪽 값(1, 28)이 200 으로 통과하는 테스트를 함께 둔다. 그 테스트가 실패하면 A3 가정이 틀렸다는 신호다.

## 4. 테스트 코드 전체

패키지명은 가정이다. 같은 패키지의 기존 테스트 위치에 맞춘다.

### 4-1. `SpyGlp1InjectionPlanCommandUseCase.java` (src/test, web 패키지)

```java
package com.kakaohealthcare.glp1.web;

import com.kakaohealthcare.glp1.application.Glp1InjectionPlanCommandUseCase;
import com.kakaohealthcare.glp1.application.dto.Glp1InjectionPlanInDto;
import com.kakaohealthcare.glp1.application.dto.Glp1InjectionPlanOutDto;
import java.util.ArrayList;
import java.util.List;

/** 호출 이력을 기록하는 Spy. 컨트롤러가 요청 값을 UseCase 로 그대로 넘기는지 관찰한다. */
class SpyGlp1InjectionPlanCommandUseCase implements Glp1InjectionPlanCommandUseCase {

    private final List<Glp1InjectionPlanInDto> registerInDtoList = new ArrayList<>();
    private final List<Glp1InjectionPlanInDto> updateInDtoList = new ArrayList<>();
    private Long lastUpdatedPlanId;
    private Glp1InjectionPlanOutDto outDtoToReturn;

    void willReturn(Glp1InjectionPlanOutDto outDto) {
        this.outDtoToReturn = outDto;
    }

    void reset() {
        registerInDtoList.clear();
        updateInDtoList.clear();
        lastUpdatedPlanId = null;
        outDtoToReturn = null;
    }

    @Override
    public Glp1InjectionPlanOutDto register(Long userId, Glp1InjectionPlanInDto inDto) {
        registerInDtoList.add(inDto);
        return outDtoToReturn;
    }

    @Override
    public Glp1InjectionPlanOutDto update(Long userId, Long planId, Glp1InjectionPlanInDto inDto) {
        updateInDtoList.add(inDto);
        lastUpdatedPlanId = planId;
        return outDtoToReturn;
    }

    int getRegisterCallCount() {
        return registerInDtoList.size();
    }

    int getUpdateCallCount() {
        return updateInDtoList.size();
    }

    Glp1InjectionPlanInDto getLastRegisterInDto() {
        return registerInDtoList.get(registerInDtoList.size() - 1);
    }

    Glp1InjectionPlanInDto getLastUpdateInDto() {
        return updateInDtoList.get(updateInDtoList.size() - 1);
    }

    Long getLastUpdatedPlanId() {
        return lastUpdatedPlanId;
    }
}
```

### 4-2. `Glp1InjectionPlanControllerTest.java`

```java
package com.kakaohealthcare.glp1.web;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.nullValue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.kakaohealthcare.glp1.application.dto.Glp1InjectionPlanOutDto;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.context.annotation.Primary;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;

@WebMvcTest(Glp1InjectionPlanController.class)
@Import(Glp1InjectionPlanControllerTest.SpyConfig.class)
class Glp1InjectionPlanControllerTest {

    private static final String REGISTER_URL = "/v1/glp1/injection-plans";
    private static final String UPDATE_URL = "/v1/glp1/injection-plans/{planId}";
    private static final Long PLAN_ID = 7L;
    private static final int VALID_INTERVAL_DAYS = 14;
    private static final String MEMO = "복부 우측 주입";

    private MockMvc mockMvc;
    private SpyGlp1InjectionPlanCommandUseCase spyGlp1InjectionPlanCommandUseCase;

    @TestConfiguration
    static class SpyConfig {
        @Bean
        @Primary
        SpyGlp1InjectionPlanCommandUseCase spyGlp1InjectionPlanCommandUseCase() {
            return new SpyGlp1InjectionPlanCommandUseCase();
        }
    }

    @BeforeEach
    void setUp(
            @Autowired MockMvc mockMvc,
            @Autowired SpyGlp1InjectionPlanCommandUseCase spyGlp1InjectionPlanCommandUseCase) {
        this.mockMvc = mockMvc;
        this.spyGlp1InjectionPlanCommandUseCase = spyGlp1InjectionPlanCommandUseCase;
        spyGlp1InjectionPlanCommandUseCase.reset();
    }

    @Nested
    @DisplayName("POST /v1/glp1/injection-plans (등록)")
    class Register {

        @ParameterizedTest
        @ValueSource(ints = {0, -1, 29})
        @DisplayName("intervalDays 가 1~28 범위를 벗어나면 400 이고 UseCase 를 호출하지 않는다")
        void register_intervalDaysOutOfRange_returnsBadRequestWithoutCallingUseCase(int intervalDays)
                throws Exception {
            // When
            mockMvc.perform(authenticated(post(REGISTER_URL))
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(requestJson(intervalDays, true, MEMO)))
                    // Then
                    .andExpect(status().isBadRequest());

            assertThat(spyGlp1InjectionPlanCommandUseCase.getRegisterCallCount()).isZero();
        }

        @ParameterizedTest
        @ValueSource(ints = {1, 28})
        @DisplayName("intervalDays 가 경계값 1, 28 이면 통과하고 UseCase 로 같은 값을 넘긴다")
        void register_intervalDaysAtBoundary_passesValueToUseCase(int intervalDays) throws Exception {
            // Given
            spyGlp1InjectionPlanCommandUseCase.willReturn(outDto(intervalDays, true, MEMO));

            // When
            mockMvc.perform(authenticated(post(REGISTER_URL))
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(requestJson(intervalDays, true, MEMO)))
                    // Then
                    .andExpect(status().isOk());

            assertThat(spyGlp1InjectionPlanCommandUseCase.getLastRegisterInDto().intervalDays())
                    .isEqualTo(intervalDays);
        }

        @Test
        @DisplayName("notificationEnabled 를 기본값(true)과 다른 false 로 보내면 UseCase 로 false 가 전달된다")
        void register_notificationDisabled_passesFalseToUseCase() throws Exception {
            // Given
            spyGlp1InjectionPlanCommandUseCase.willReturn(outDto(VALID_INTERVAL_DAYS, false, MEMO));

            // When
            mockMvc.perform(authenticated(post(REGISTER_URL))
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(requestJson(VALID_INTERVAL_DAYS, false, MEMO)))
                    // Then
                    .andExpect(status().isOk());

            assertThat(spyGlp1InjectionPlanCommandUseCase.getLastRegisterInDto().notificationEnabled())
                    .isFalse();
        }

        @Test
        @DisplayName("notificationEnabled 를 생략하면 null 로 전달되어 기본값 결정은 서비스에 맡긴다")
        void register_notificationEnabledOmitted_passesNullToUseCase() throws Exception {
            // Given
            spyGlp1InjectionPlanCommandUseCase.willReturn(outDto(VALID_INTERVAL_DAYS, true, MEMO));

            // When
            mockMvc.perform(authenticated(post(REGISTER_URL))
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(requestJson(VALID_INTERVAL_DAYS, null, MEMO)))
                    // Then
                    .andExpect(status().isOk());

            assertThat(spyGlp1InjectionPlanCommandUseCase.getLastRegisterInDto().notificationEnabled())
                    .isNull();
        }

        @Test
        @DisplayName("memo 가 없으면 응답에 memo 키는 유지되고 값은 JSON null 이다")
        void register_memoAbsent_responseKeepsMemoKeyWithNullValue() throws Exception {
            // Given
            spyGlp1InjectionPlanCommandUseCase.willReturn(outDto(VALID_INTERVAL_DAYS, true, null));

            // When
            mockMvc.perform(authenticated(post(REGISTER_URL))
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(requestJson(VALID_INTERVAL_DAYS, true, null)))
                    // Then: doesNotExist() 는 키 생략·null 을 구분하지 못하므로 키 존재 + null 값을 함께 확인
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.memo").hasJsonPath())
                    .andExpect(jsonPath("$.memo").value(nullValue()));
        }

        @Test
        @DisplayName("memo 가 있으면 응답에 그 값이 내려간다")
        void register_memoPresent_responseContainsMemo() throws Exception {
            // Given
            spyGlp1InjectionPlanCommandUseCase.willReturn(outDto(VALID_INTERVAL_DAYS, true, MEMO));

            // When
            mockMvc.perform(authenticated(post(REGISTER_URL))
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(requestJson(VALID_INTERVAL_DAYS, true, MEMO)))
                    // Then
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.memo").value(MEMO));
        }
    }

    @Nested
    @DisplayName("PUT /v1/glp1/injection-plans/{planId} (수정)")
    class Update {

        @ParameterizedTest
        @ValueSource(ints = {0, -1, 29})
        @DisplayName("intervalDays 가 1~28 범위를 벗어나면 400 이고 UseCase 를 호출하지 않는다")
        void update_intervalDaysOutOfRange_returnsBadRequestWithoutCallingUseCase(int intervalDays)
                throws Exception {
            // When
            mockMvc.perform(authenticated(put(UPDATE_URL, PLAN_ID))
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(requestJson(intervalDays, true, MEMO)))
                    // Then
                    .andExpect(status().isBadRequest());

            assertThat(spyGlp1InjectionPlanCommandUseCase.getUpdateCallCount()).isZero();
        }

        @ParameterizedTest
        @ValueSource(ints = {1, 28})
        @DisplayName("intervalDays 가 경계값 1, 28 이면 통과하고 planId 와 값을 UseCase 로 넘긴다")
        void update_intervalDaysAtBoundary_passesPlanIdAndValueToUseCase(int intervalDays) throws Exception {
            // Given
            spyGlp1InjectionPlanCommandUseCase.willReturn(outDto(intervalDays, true, MEMO));

            // When
            mockMvc.perform(authenticated(put(UPDATE_URL, PLAN_ID))
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(requestJson(intervalDays, true, MEMO)))
                    // Then
                    .andExpect(status().isOk());

            assertThat(spyGlp1InjectionPlanCommandUseCase.getLastUpdatedPlanId()).isEqualTo(PLAN_ID);
            assertThat(spyGlp1InjectionPlanCommandUseCase.getLastUpdateInDto().intervalDays())
                    .isEqualTo(intervalDays);
        }

        @Test
        @DisplayName("notificationEnabled 를 false 로 보내면 UseCase 로 false 가 전달된다")
        void update_notificationDisabled_passesFalseToUseCase() throws Exception {
            // Given
            spyGlp1InjectionPlanCommandUseCase.willReturn(outDto(VALID_INTERVAL_DAYS, false, MEMO));

            // When
            mockMvc.perform(authenticated(put(UPDATE_URL, PLAN_ID))
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(requestJson(VALID_INTERVAL_DAYS, false, MEMO)))
                    // Then
                    .andExpect(status().isOk());

            assertThat(spyGlp1InjectionPlanCommandUseCase.getLastUpdateInDto().notificationEnabled())
                    .isFalse();
        }

        @Test
        @DisplayName("memo 가 없으면 응답에 memo 키는 유지되고 값은 JSON null 이다")
        void update_memoAbsent_responseKeepsMemoKeyWithNullValue() throws Exception {
            // Given
            spyGlp1InjectionPlanCommandUseCase.willReturn(outDto(VALID_INTERVAL_DAYS, true, null));

            // When
            mockMvc.perform(authenticated(put(UPDATE_URL, PLAN_ID))
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(requestJson(VALID_INTERVAL_DAYS, true, null)))
                    // Then
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.memo").hasJsonPath())
                    .andExpect(jsonPath("$.memo").value(nullValue()));
        }
    }

    /** A5: 기존 컨트롤러 테스트의 인증 방식(헤더·SecurityMockMvc 등)으로 교체한다. */
    private MockHttpServletRequestBuilder authenticated(MockHttpServletRequestBuilder requestBuilder) {
        return requestBuilder;
    }

    private Glp1InjectionPlanOutDto outDto(int intervalDays, boolean notificationEnabled, String memo) {
        return new Glp1InjectionPlanOutDto(PLAN_ID, intervalDays, notificationEnabled, memo);
    }

    /** null 값도 JSON null 로 보내 "필드 생략"과 구분되는 요청 본문을 만든다. */
    private String requestJson(Integer intervalDays, Boolean notificationEnabled, String memo) {
        String memoJson = memo == null ? "null" : "\"" + memo + "\"";
        return """
                {"intervalDays": %s, "notificationEnabled": %s, "memo": %s}
                """
                .formatted(intervalDays, notificationEnabled, memoJson);
    }
}
```

`requestJson` 에 `notificationEnabled` 가 null 이면 JSON 에 `null` 이 들어간다. "필드 생략"은 별도로 만들지 않았다. 둘 다 Jackson 에서 null 로 바인딩되므로 테스트 이름은 "생략"이지만 실제로는 null 전송이다.

### 4-3. `FakeGlp1InjectionPlanRepository.java` (src/test, domain 패키지)

기존 Fake 가 있으면 재사용하고 이 파일은 만들지 않는다. 확인 명령은 6절에 있다.

```java
package com.kakaohealthcare.glp1.domain;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.springframework.test.util.ReflectionTestUtils;

/** domain 인터페이스의 인메모리 Fake. 정답 주입 없이 저장한 데이터에 조회 조건(id·userId)을 적용한다. */
public class FakeGlp1InjectionPlanRepository implements Glp1InjectionPlanRepository {

    private final Map<Long, Glp1InjectionPlanEntity> glp1InjectionPlanEntityMap = new LinkedHashMap<>();
    private long sequence = 0L;

    @Override
    public Glp1InjectionPlanEntity save(Glp1InjectionPlanEntity glp1InjectionPlanEntity) {
        Long id = glp1InjectionPlanEntity.getId();
        if (id == null) {
            id = ++sequence;
            ReflectionTestUtils.setField(glp1InjectionPlanEntity, "id", id);
        }
        glp1InjectionPlanEntityMap.put(id, glp1InjectionPlanEntity);
        return glp1InjectionPlanEntity;
    }

    @Override
    public Optional<Glp1InjectionPlanEntity> findByIdAndUserId(Long planId, Long userId) {
        return Optional.ofNullable(glp1InjectionPlanEntityMap.get(planId))
                .filter(glp1InjectionPlanEntity -> glp1InjectionPlanEntity.getUserId().equals(userId));
    }

    /** 테스트 검증용 헬퍼. 인터페이스 계약이 아니다. */
    public List<Glp1InjectionPlanEntity> findAll() {
        return new ArrayList<>(glp1InjectionPlanEntityMap.values());
    }
}
```

### 4-4. `Glp1InjectionPlanCommandServiceTest.java`

```java
package com.kakaohealthcare.glp1.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.kakaohealthcare.glp1.application.dto.Glp1InjectionPlanInDto;
import com.kakaohealthcare.glp1.application.dto.Glp1InjectionPlanOutDto;
import com.kakaohealthcare.glp1.domain.FakeGlp1InjectionPlanRepository;
import com.kakaohealthcare.glp1.domain.Glp1InjectionPlanEntity;
import com.kakaohealthcare.glp1.domain.Glp1InjectionPlanNotFoundException;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.springframework.test.util.ReflectionTestUtils;

class Glp1InjectionPlanCommandServiceTest {

    private static final Long USER_ID = 1L;
    private static final Long OTHER_USER_ID = 2L;
    private static final int INITIAL_INTERVAL_DAYS = 7;
    private static final int CHANGED_INTERVAL_DAYS = 14;
    private static final String MEMO = "복부 우측 주입";

    private FakeGlp1InjectionPlanRepository fakeGlp1InjectionPlanRepository;
    private Glp1InjectionPlanCommandService glp1InjectionPlanCommandService;

    @BeforeEach
    void setUp() {
        fakeGlp1InjectionPlanRepository = new FakeGlp1InjectionPlanRepository();
        glp1InjectionPlanCommandService = new Glp1InjectionPlanCommandService(fakeGlp1InjectionPlanRepository);
    }

    @Nested
    @DisplayName("register (등록)")
    class Register {

        @Test
        @DisplayName("notificationEnabled 를 기본값(true)과 다른 false 로 요청하면 false 로 저장한다")
        void register_notificationDisabled_savesFalse() {
            // Given
            Glp1InjectionPlanInDto glp1InjectionPlanInDto =
                    new Glp1InjectionPlanInDto(CHANGED_INTERVAL_DAYS, false, MEMO);

            // When
            glp1InjectionPlanCommandService.register(USER_ID, glp1InjectionPlanInDto);

            // Then
            List<Glp1InjectionPlanEntity> glp1InjectionPlanEntityList = fakeGlp1InjectionPlanRepository.findAll();
            assertThat(glp1InjectionPlanEntityList).hasSize(1);
            assertThat(glp1InjectionPlanEntityList.get(0).getNotificationEnabled()).isFalse();
        }

        @Test
        @DisplayName("notificationEnabled 가 null 이면 엔티티 기본값 true 를 유지한다")
        void register_notificationEnabledNull_keepsDefaultTrue() {
            // Given
            Glp1InjectionPlanInDto glp1InjectionPlanInDto =
                    new Glp1InjectionPlanInDto(CHANGED_INTERVAL_DAYS, null, MEMO);

            // When
            glp1InjectionPlanCommandService.register(USER_ID, glp1InjectionPlanInDto);

            // Then
            List<Glp1InjectionPlanEntity> glp1InjectionPlanEntityList = fakeGlp1InjectionPlanRepository.findAll();
            assertThat(glp1InjectionPlanEntityList.get(0).getNotificationEnabled()).isTrue();
        }

        @Test
        @DisplayName("요청한 intervalDays 를 그대로 저장한다")
        void register_intervalDays_savesRequestedValue() {
            // Given
            Glp1InjectionPlanInDto glp1InjectionPlanInDto =
                    new Glp1InjectionPlanInDto(CHANGED_INTERVAL_DAYS, null, MEMO);

            // When
            Glp1InjectionPlanOutDto glp1InjectionPlanOutDto =
                    glp1InjectionPlanCommandService.register(USER_ID, glp1InjectionPlanInDto);

            // Then
            assertThat(glp1InjectionPlanOutDto.intervalDays()).isEqualTo(CHANGED_INTERVAL_DAYS);
            assertThat(fakeGlp1InjectionPlanRepository.findAll().get(0).getIntervalDays())
                    .isEqualTo(CHANGED_INTERVAL_DAYS);
        }
    }

    @Nested
    @DisplayName("update (수정)")
    class Update {

        @ParameterizedTest
        @CsvSource({"false, true", "true, false"})
        @DisplayName("기존 값과 다른 notificationEnabled 를 요청하면 그 값으로 바꾼다 (false→true, true→false)")
        void update_notificationEnabledChanged_appliesRequestedValue(
                boolean storedNotificationEnabled, boolean requestedNotificationEnabled) {
            // Given
            Glp1InjectionPlanEntity storedEntity = savedPlan(USER_ID, storedNotificationEnabled);
            Glp1InjectionPlanInDto glp1InjectionPlanInDto =
                    new Glp1InjectionPlanInDto(CHANGED_INTERVAL_DAYS, requestedNotificationEnabled, MEMO);

            // When
            glp1InjectionPlanCommandService.update(USER_ID, storedEntity.getId(), glp1InjectionPlanInDto);

            // Then
            Glp1InjectionPlanEntity updatedEntity = fakeGlp1InjectionPlanRepository
                    .findByIdAndUserId(storedEntity.getId(), USER_ID)
                    .orElseThrow();
            assertThat(updatedEntity.getNotificationEnabled()).isEqualTo(requestedNotificationEnabled);
            assertThat(updatedEntity.getIntervalDays()).isEqualTo(CHANGED_INTERVAL_DAYS);
        }

        @Test
        @DisplayName("notificationEnabled 가 null 이고 기존 값이 true 이면 true 로 유지한다")
        void update_notificationEnabledNull_keepsStoredTrue() {
            // Given
            Glp1InjectionPlanEntity storedEntity = savedPlan(USER_ID, true);
            Glp1InjectionPlanInDto glp1InjectionPlanInDto =
                    new Glp1InjectionPlanInDto(CHANGED_INTERVAL_DAYS, null, MEMO);

            // When
            glp1InjectionPlanCommandService.update(USER_ID, storedEntity.getId(), glp1InjectionPlanInDto);

            // Then
            Glp1InjectionPlanEntity updatedEntity = fakeGlp1InjectionPlanRepository
                    .findByIdAndUserId(storedEntity.getId(), USER_ID)
                    .orElseThrow();
            assertThat(updatedEntity.getNotificationEnabled()).isTrue();
        }

        @Test
        @DisplayName("다른 사용자의 일정을 수정하려 하면 예외가 나고 기존 값은 바뀌지 않는다")
        void update_otherUsersPlan_throwsAndKeepsStoredValues() {
            // Given
            Glp1InjectionPlanEntity storedEntity = savedPlan(OTHER_USER_ID, true);
            Glp1InjectionPlanInDto glp1InjectionPlanInDto =
                    new Glp1InjectionPlanInDto(CHANGED_INTERVAL_DAYS, false, MEMO);

            // When & Then
            assertThatThrownBy(() ->
                            glp1InjectionPlanCommandService.update(USER_ID, storedEntity.getId(), glp1InjectionPlanInDto))
                    .isInstanceOf(Glp1InjectionPlanNotFoundException.class);

            assertThat(storedEntity.getNotificationEnabled()).isTrue();
            assertThat(storedEntity.getIntervalDays()).isEqualTo(INITIAL_INTERVAL_DAYS);
        }
    }

    private Glp1InjectionPlanEntity savedPlan(Long userId, boolean notificationEnabled) {
        Glp1InjectionPlanEntity glp1InjectionPlanEntity = Glp1InjectionPlanEntity.builder()
                .userId(userId)
                .intervalDays(INITIAL_INTERVAL_DAYS)
                .memo(MEMO)
                .build();
        ReflectionTestUtils.setField(glp1InjectionPlanEntity, "notificationEnabled", notificationEnabled);
        return fakeGlp1InjectionPlanRepository.save(glp1InjectionPlanEntity);
    }
}
```

설계 메모:
- `var` 와 FQCN 은 쓰지 않았다. 컬렉션은 `...EntityList`, 대상·결과는 타입이 드러나는 이름을 썼다.
- 서비스에는 `intervalDays` 범위 검증이 없고 Bean Validation 이 web 계층에서 처리한다. 그래서 서비스에는 "범위 위반 시 예외" 테스트를 넣지 않았다.
- "저장 미호출"에 해당하는 것은 타 사용자 수정 시 상태 불변 검증이다(A7 예외).
- `savedPlan` 이 `ReflectionTestUtils` 로 `notificationEnabled` 를 세팅하는 이유는 빌더가 이 필드를 노출하는지 모르기 때문이다. 빌더에 있으면 빌더 호출로 바꾼다.

## 5. 의도적으로 테스트하지 않은 것 (사용자 확인 필요)

- **수정(PUT) 시 `notificationEnabled` 가 null 일 때 "기존 값 유지"인지 "기본값 true 로 리셋"인지**: 전제의 "null 이면 기본값 유지"는 등록 기준으로는 명확하지만 수정에서는 둘 다 읽힌다.
  - 기존 값이 true 인 경우는 두 해석이 같아서 테스트에 넣었다(`update_notificationEnabledNull_keepsStoredTrue`).
  - 기존 값이 false 인 경우가 갈린다. 의도를 알려주면 한 줄로 추가한다.
- **`intervalDays` 가 null 일 때**: `@Min/@Max` 는 null 을 통과시킨다. `@NotNull` 이 없다면 null 이 허용되는지는 별도 결정이 필요한 사항이라 임의로 정하지 않았다.
- **RR-14 검증 순서(소유 확인 → 입력 검증)**: 남의 일정에 범위 위반 값을 보내면 현재 400 이 먼저 나간다. `@Valid` 구조상 불가피하다. 이 변경을 PR 본문 "기존 동작 변경" 항목에 적어야 한다(수정 API 가 이전에는 통과시키던 요청이 400 이 된다).

## 6. 실행 계획 (이 시뮬레이션에서는 미실행)

1. **Phase 0 (작성 전)**
   - `git status --short` 로 대상 테스트 경로의 미커밋 변경을 확인한다 (DW-1).
   - 같은 패키지 기존 `*Test` 가 있으면 먼저 읽고 `Edit` 로 추가한다. 통째로 덮지 않는다 (DW-3).
   - `find . -name "Fake*Glp1InjectionPlan*"` 로 기존 Fake 를 확인하고, 있으면 재사용한다.
   - 위 A1~A7 가정을 실제 시그니처와 대조한다.
2. **컴파일 및 실행**
   - `./gradlew :{module}:test --tests Glp1InjectionPlanControllerTest`
   - `./gradlew :{module}:test --tests Glp1InjectionPlanCommandServiceTest`
3. **변이 확인 (RR-12 "깨뜨리면 실패하는가")**
   - 서비스의 `notificationEnabled` 매핑 줄을 제거 → `register_notificationDisabled_savesFalse` 와 `update_..._appliesRequestedValue` 가 실패해야 한다.
   - 요청 DTO 의 `@Max(28)` 을 제거 → 29 케이스가 POST/PUT 양쪽에서 실패해야 한다.
   - 응답 `memo` 를 `@JsonInclude(NON_NULL)` 로 바꿔 키를 생략 → `hasJsonPath()` 에서 실패해야 한다.
   - 확인 후 원복한다.
4. **포매팅 및 린트**
   - `./gradlew :{module}:spotlessApply`
   - `python3 forge/common/review-lint.py` — 위반 0건이어야 하고, `[확인]` 항목은 해당 여부를 판단한다. 이 설계안은 `lenient`, `any()`, `doesNotExist`, `asBoolean`, `isEmpty` 를 쓰지 않았다.
5. **마무리**
   - `git status` 로 의도치 않은 삭제나 변경이 없는지 확인한다 (DW-5).

## 7. Self-check 결과 (설계 기준)

| # | 항목 | 결과 |
|---|---|---|
| 1·2 | 계층 식별과 방식 (Web=@WebMvcTest, App=Fake) | PASS (계층 근거는 전제 조건의 `domain` 인터페이스 의존) |
| 4 | `@DisplayName` 한국어 | PASS |
| 5 | 테스트 통과 | 미확인. 실행 계획으로만 기재 |
| 6~8 | Given-When-Then, `@Nested`, AssertJ | PASS (web 쪽 `jsonPath`·`status` 는 MockMvc 매처) |
| 11·16 | FQCN 없음 | PASS |
| 17 | infra 직접 참조 없음 | PASS |
| 19 | 상태 저장소 Fake | PASS (Mock 미사용, Web 은 `@MockBean` 대신 Spy) |
| 20 | 기본값과 다른 값, 모든 진입 경로, 느슨한 JSON 단언 없음 | PASS |
| 21 | review-lint 0건 | 미확인 (실행 계획) |

## 8. 남은 리스크

1. A1~A7 가정이 틀리면 컴파일 단계에서 드러난다. 가장 불확실한 것은 UseCase 와 DTO 시그니처(A1·A2)다.
2. 인증 헬퍼(A5)와 상태 코드(A4)는 같은 패키지 기존 컨트롤러 테스트의 패턴으로 맞춰야 한다.
3. 응답에 `notificationEnabled` 가 포함되는지는 전제에서 알 수 없다. 그래서 컨트롤러 테스트는 UseCase 로 전달되는 값만 검증하고, 응답의 `notificationEnabled` 는 단언하지 않았다. 포함된다면 불리언 단언은 `isBoolean()` 확인 뒤 값을 비교한다.
