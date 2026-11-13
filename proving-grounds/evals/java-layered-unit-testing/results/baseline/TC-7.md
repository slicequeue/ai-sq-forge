<!-- TC-7 baseline / no skill / sonnet / 2026-11-13 / 50,245 tok / tool 0 / 52s -->

# Glp1InjectionPlan 등록/수정 테스트 (시뮬레이션, 파일은 쓰지 않음)

저장소 코드는 읽지 않고 전제 조건만으로 작성했습니다. 전제에 없는 시그니처는 아래 "확인 필요" 표에 따로 모았습니다.

## 설계 판단

1. **컨트롤러 테스트는 `@WebMvcTest` + `@MockitoBean`으로 슬라이스한다.**
   - 서비스와 DB는 올리지 않고 `UseCase`만 목으로 둔다.
   - Spring Boot 3.4 미만이면 `@MockBean`으로 바꾼다.
2. **`intervalDays` 검증은 등록(POST)에만 테스트한다.**
   - 경계값 0, 1, 28, 29를 `@ParameterizedTest`로 돌린다.
   - 실패 시 `useCase`가 호출되지 않았는지(`never()`)도 확인한다.
   - 수정(PUT)은 요청하신 대로 검증 테스트에서 제외했다.
3. **`notificationEnabled=true`는 등록과 수정 컨트롤러에서 `UseCase`로 넘어가는 값을 `ArgumentCaptor`로 확인한다.**
4. **`memo` 없음 케이스에서 `doesNotExist()`만 쓰면 계약을 못 지킨다.**
   - Spring의 `doesNotExist()`는 값이 JSON null이어도, 키가 아예 없어도 통과한다.
   - 계약은 "키는 있고 값이 null"이므로, 요청하신 `doesNotExist()`는 그대로 쓰고 `hasKey("memo")`를 함께 건다.
   - 이렇게 하면 `@JsonInclude(NON_NULL)` 같은 설정으로 키가 사라지는 회귀도 잡힌다.
5. **서비스 테스트에서 `true`만 보내면 검증력이 없다.**
   - 엔티티 기본값이 이미 `true`라서, 매핑 코드가 통째로 빠져도 통과한다.
   - 그래서 요청하신 `true` 케이스에 더해 `false`와 `null`(기본값 유지) 케이스를 추가했다.
   - 범위를 넓히는 부분이라 마음에 안 들면 `false`와 `null` 두 메서드만 지우면 된다.
6. **서비스 테스트는 `MockitoExtension`으로 `Glp1InjectionPlanRepository`를 모킹한다.**
   - `save`에 넘어간 엔티티를 `ArgumentCaptor`로 잡아 매핑 결과를 검증한다.

## 컨트롤러 테스트

```java
package com.example.glp1.web;

import static org.hamcrest.Matchers.hasKey;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.LinkedHashMap;
import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(Glp1InjectionPlanController.class)
class Glp1InjectionPlanControllerTest {

    private static final String BASE_URL = "/v1/glp1/injection-plans";
    private static final long PLAN_ID = 1L;

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockitoBean
    private Glp1InjectionPlanCommandUseCase commandUseCase;

    @Test
    @DisplayName("등록: memo 가 없으면 키는 유지된 채 null 로 내려간다")
    void register_withoutMemo_returnsNullMemo() throws Exception {
        given(commandUseCase.register(any(Glp1InjectionPlanRequest.class)))
                .willReturn(responseWithoutMemo());

        mockMvc.perform(post(BASE_URL)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body(7, true)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.memo").doesNotExist())
                // doesNotExist() 는 키 생략도 통과시키므로 "키는 존재" 계약을 별도로 고정
                .andExpect(jsonPath("$", hasKey("memo")));
    }

    @Test
    @DisplayName("등록: notificationEnabled=true 가 UseCase 로 그대로 전달된다")
    void register_notificationEnabledTrue_passedToUseCase() throws Exception {
        given(commandUseCase.register(any(Glp1InjectionPlanRequest.class)))
                .willReturn(responseWithoutMemo());

        mockMvc.perform(post(BASE_URL)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body(7, true)))
                .andExpect(status().isCreated());

        ArgumentCaptor<Glp1InjectionPlanRequest> captor =
                ArgumentCaptor.forClass(Glp1InjectionPlanRequest.class);
        verify(commandUseCase).register(captor.capture());
        assertThat(captor.getValue().notificationEnabled()).isTrue();
        assertThat(captor.getValue().intervalDays()).isEqualTo(7);
    }

    @ParameterizedTest(name = "등록: intervalDays={0} 는 경계 안쪽이라 통과한다")
    @ValueSource(ints = {1, 28})
    void register_intervalDaysWithinBoundary_succeeds(int intervalDays) throws Exception {
        given(commandUseCase.register(any(Glp1InjectionPlanRequest.class)))
                .willReturn(responseWithoutMemo());

        mockMvc.perform(post(BASE_URL)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body(intervalDays, true)))
                .andExpect(status().isCreated());
    }

    @ParameterizedTest(name = "등록: intervalDays={0} 는 경계 바깥이라 400 이다")
    @ValueSource(ints = {0, 29, -1})
    void register_intervalDaysOutOfRange_returnsBadRequest(int intervalDays) throws Exception {
        mockMvc.perform(post(BASE_URL)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body(intervalDays, true)))
                .andExpect(status().isBadRequest());

        verify(commandUseCase, never()).register(any());
    }

    @Test
    @DisplayName("수정: notificationEnabled=true 와 planId 가 UseCase 로 전달된다")
    void update_notificationEnabledTrue_passedToUseCase() throws Exception {
        given(commandUseCase.update(eq(PLAN_ID), any(Glp1InjectionPlanRequest.class)))
                .willReturn(responseWithoutMemo());

        mockMvc.perform(put(BASE_URL + "/{planId}", PLAN_ID)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body(7, true)))
                .andExpect(status().isOk());

        ArgumentCaptor<Glp1InjectionPlanRequest> captor =
                ArgumentCaptor.forClass(Glp1InjectionPlanRequest.class);
        verify(commandUseCase).update(eq(PLAN_ID), captor.capture());
        assertThat(captor.getValue().notificationEnabled()).isTrue();
    }

    @Test
    @DisplayName("수정: memo 가 없으면 키는 유지된 채 null 로 내려간다")
    void update_withoutMemo_returnsNullMemo() throws Exception {
        given(commandUseCase.update(eq(PLAN_ID), any(Glp1InjectionPlanRequest.class)))
                .willReturn(responseWithoutMemo());

        mockMvc.perform(put(BASE_URL + "/{planId}", PLAN_ID)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body(7, true)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.memo").doesNotExist())
                .andExpect(jsonPath("$", hasKey("memo")));
    }

    // 필수 필드는 실제 Request 정의에 맞춰 채운다 (아래 medicationName 은 가정)
    private String body(Integer intervalDays, Boolean notificationEnabled) throws Exception {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("medicationName", "위고비");
        map.put("intervalDays", intervalDays);
        map.put("notificationEnabled", notificationEnabled);
        return objectMapper.writeValueAsString(map);
    }

    // 생성자 시그니처는 실제 Response 정의에 맞춰 조정 (memo 만 null 이면 된다)
    private Glp1InjectionPlanResponse responseWithoutMemo() {
        return new Glp1InjectionPlanResponse(PLAN_ID, 7, true, null);
    }
}
```

## 서비스 테스트

```java
package com.example.glp1.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

import java.util.Optional;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class Glp1InjectionPlanCommandServiceTest {

    private static final long PLAN_ID = 1L;

    @Mock
    private Glp1InjectionPlanRepository repository;

    @InjectMocks
    private Glp1InjectionPlanCommandService service;

    @Test
    @DisplayName("등록: notificationEnabled=true 가 엔티티에 true 로 저장된다")
    void register_notificationEnabledTrue_mapsToEntity() {
        given(repository.save(any(Glp1InjectionPlanEntity.class)))
                .willAnswer(invocation -> invocation.getArgument(0));

        service.register(request(7, true));

        assertThat(savedEntity().getNotificationEnabled()).isTrue();
    }

    // 아래 두 건은 요청 범위 밖 추가분. true 는 기본값과 같아 매핑 누락을 못 잡으므로 보강한 것
    @Test
    @DisplayName("등록: notificationEnabled=false 는 기본값을 덮어 false 로 저장된다")
    void register_notificationEnabledFalse_overridesDefault() {
        given(repository.save(any(Glp1InjectionPlanEntity.class)))
                .willAnswer(invocation -> invocation.getArgument(0));

        service.register(request(7, false));

        assertThat(savedEntity().getNotificationEnabled()).isFalse();
    }

    @Test
    @DisplayName("등록: notificationEnabled=null 이면 엔티티 기본값 true 가 유지된다")
    void register_notificationEnabledNull_keepsDefaultTrue() {
        given(repository.save(any(Glp1InjectionPlanEntity.class)))
                .willAnswer(invocation -> invocation.getArgument(0));

        service.register(request(7, null));

        assertThat(savedEntity().getNotificationEnabled()).isTrue();
    }

    @Test
    @DisplayName("수정: notificationEnabled=true 가 기존 엔티티에 반영된다")
    void update_notificationEnabledTrue_mapsToEntity() {
        Glp1InjectionPlanEntity existing = existingPlanWithNotification(false);
        given(repository.findById(PLAN_ID)).willReturn(Optional.of(existing));

        service.update(PLAN_ID, request(7, true));

        assertThat(existing.getNotificationEnabled()).isTrue();
    }

    private Glp1InjectionPlanEntity savedEntity() {
        ArgumentCaptor<Glp1InjectionPlanEntity> captor =
                ArgumentCaptor.forClass(Glp1InjectionPlanEntity.class);
        verify(repository).save(captor.capture());
        return captor.getValue();
    }

    // 실제 Request 생성 방식(record 생성자/빌더)에 맞춰 조정
    private Glp1InjectionPlanRequest request(Integer intervalDays, Boolean notificationEnabled) {
        return new Glp1InjectionPlanRequest("위고비", intervalDays, notificationEnabled);
    }

    // 실제 엔티티 생성/팩토리 방식에 맞춰 조정
    private Glp1InjectionPlanEntity existingPlanWithNotification(boolean enabled) {
        Glp1InjectionPlanEntity entity = Glp1InjectionPlanEntity.create("위고비", 7);
        entity.changeNotificationEnabled(enabled);
        return entity;
    }
}
```

## 확인 필요

전제에 없어서 가정한 항목입니다. 컴파일 오류나 실패가 나면 먼저 여기를 보면 됩니다.

| 항목 | 가정 | 비고 |
|---|---|---|
| UseCase 메서드명과 시그니처 | `register(request)`, `update(planId, request)` | 다르면 `given` 과 `verify` 수정 |
| 응답 상태 코드 | 등록 201, 수정 200 | 등록이 200이면 `isCreated()` 를 `isOk()` 로 변경 |
| Request 접근자 | record 스타일 `notificationEnabled()`, `intervalDays()` | 클래스면 `getXxx()` |
| 엔티티 getter | `getNotificationEnabled()` | `Boolean` 필드가 아니면 `isNotificationEnabled()` |
| 필수 필드 | `medicationName` | 다른 `@NotNull` 필드가 있으면 `body()` 에 추가. 빠지면 `intervalDays` 가 아닌 다른 이유로 400 이 나서 검증 테스트가 오탐 |
| 수정 시 `findById` 반환 | `Optional` | 없으면 예외를 던지는 방식일 수 있음. 이 경우도 별도 테스트가 필요 |
| 엔티티 변경 메서드 | `changeNotificationEnabled(boolean)` | 서비스 수정 테스트의 사전 상태 구성용 |

## 범위 밖으로 둔 것

- 수정 API의 `intervalDays` 검증은 요청대로 테스트하지 않았다. `@Valid` 가 PUT에도 붙어 있으니 같은 어노테이션이 동작하겠지만, 이 테스트로는 보장되지 않는다.
- `intervalDays` 가 null일 때는 `@Min` 과 `@Max` 가 통과시키므로 400이 나지 않는다. 필수 값이라면 `@NotNull` 이 별도로 필요하다.
- 존재하지 않는 `planId` 수정 같은 서비스 예외 경로는 요청에 없어서 제외했다.
