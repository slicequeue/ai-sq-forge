<!-- TC-6 baseline / no skill / sonnet / 2026-11-13 / 46,859 tok / tool 0 / 30s -->

파일은 쓰지 않았고, 아래는 시뮬레이션 결과입니다. 요청대로 Mockito `@Mock` + `given().willReturn()` 스타일로 작성했고 Fake는 만들지 않았습니다.

## 요청과 다르게 한 점 (먼저 확인해 주세요)

**`@Mock PushReservationClient`를 하나 더 추가했습니다.** 요청에는 Repository와 GroupQueryUseCase 두 개만 있었지만, 서비스 생성자가 세 개를 받습니다. 푸시 클라이언트를 mock으로 두지 않으면 `@InjectMocks`가 그 자리에 `null`을 넣습니다. 그러면 정상 등록 테스트가 `pushReservationClient.reserveNextInjection(...)`에서 NPE로 실패합니다. 이 mock은 Fake가 아니라 같은 Mockito 스타일이라 요청 취지에는 어긋나지 않는다고 봤습니다.

## 확인된 사실과 가정

| 구분 | 내용 |
|---|---|
| 확인된 것(전제 조건) | 서비스 시그니처, 의존성 3개, 호출 순서(`getOwnedGroup`, 미래 시각 검사, `save`, `reserveNextInjection`), 기존 테스트 스타일 |
| 가정한 것 | `Glp1InjectionRecordInDto`의 record 필드 순서와 타입(`groupId`, `injectedAt`, `currentAt`) |
| 가정한 것 | `Glp1InjectionRecordEntity.of(...)`가 mock 그룹 엔티티로 호출돼도 예외 없이 동작함 |
| 가정한 것 | `BadRequestException` 패키지 경로 |

가정한 항목은 실제 소스를 열어 확인해야 합니다. DTO에 필드가 더 있으면 `createInDto` 헬퍼 한 곳만 고치면 됩니다.

## 테스트 코드

```java
package com.example.glp1.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;

import java.time.LocalDateTime;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

// 아래 import 의 패키지 경로는 실제 소스에 맞춰 조정 (가정)
import com.example.common.exception.BadRequestException;
import com.example.glp1.domain.Glp1GroupEntity;
import com.example.glp1.domain.Glp1InjectionRecordEntity;
import com.example.glp1.domain.Glp1InjectionRecordRepository;
import com.example.glp1.infrastructure.PushReservationClient;

@ExtendWith(MockitoExtension.class)
class Glp1InjectionRecordCommandServiceTest {

    private static final Long USER_ID = 1L;
    private static final Long GROUP_ID = 10L;
    private static final Long SAVED_RECORD_ID = 100L;
    private static final LocalDateTime CURRENT_AT = LocalDateTime.of(2026, 11, 13, 9, 0);

    @Mock
    private Glp1InjectionRecordRepository glp1InjectionRecordRepository;

    @Mock
    private Glp1GroupQueryUseCase glp1GroupQueryUseCase;

    // 서비스 생성자 의존성이라 반드시 필요. 없으면 null 주입되어 정상 케이스에서 NPE 발생
    @Mock
    private PushReservationClient pushReservationClient;

    @InjectMocks
    private Glp1InjectionRecordCommandService glp1InjectionRecordCommandService;

    @Test
    @DisplayName("본인 소유 그룹에 과거 시각 주사 기록을 등록하면 저장 후 ID 를 반환하고 다음 주사 푸시를 예약한다")
    void register_validInjection_savesAndReservesPush() {
        // given
        Glp1InjectionRecordInDto glp1InjectionRecordInDto =
            createInDto(CURRENT_AT.minusHours(1), CURRENT_AT);
        Glp1GroupEntity glp1GroupEntity = mock(Glp1GroupEntity.class);
        LocalDateTime nextInjectionAt = CURRENT_AT.plusDays(7);
        Glp1InjectionRecordEntity savedEntity = mock(Glp1InjectionRecordEntity.class);

        given(glp1GroupQueryUseCase.getOwnedGroup(USER_ID, GROUP_ID)).willReturn(glp1GroupEntity);
        given(glp1InjectionRecordRepository.save(any(Glp1InjectionRecordEntity.class)))
            .willReturn(savedEntity);
        given(savedEntity.getId()).willReturn(SAVED_RECORD_ID);
        given(savedEntity.getNextInjectionAt()).willReturn(nextInjectionAt);

        // when
        Long result = glp1InjectionRecordCommandService.register(USER_ID, glp1InjectionRecordInDto);

        // then
        assertThat(result).isEqualTo(SAVED_RECORD_ID);
        verify(glp1InjectionRecordRepository).save(any(Glp1InjectionRecordEntity.class));
        verify(pushReservationClient).reserveNextInjection(USER_ID, nextInjectionAt);
    }

    @Test
    @DisplayName("주사 시각이 현재 시각보다 미래이면 BadRequestException 을 던지고 저장·푸시 예약을 하지 않는다")
    void register_futureInjection_throwsAndNoSideEffect() {
        // given
        Glp1InjectionRecordInDto glp1InjectionRecordInDto =
            createInDto(CURRENT_AT.plusMinutes(1), CURRENT_AT);
        Glp1GroupEntity glp1GroupEntity = mock(Glp1GroupEntity.class);

        given(glp1GroupQueryUseCase.getOwnedGroup(USER_ID, GROUP_ID)).willReturn(glp1GroupEntity);

        // when & then
        assertThatThrownBy(() ->
            glp1InjectionRecordCommandService.register(USER_ID, glp1InjectionRecordInDto))
            .isInstanceOf(BadRequestException.class);

        verify(glp1InjectionRecordRepository, never()).save(any());
        verifyNoInteractions(pushReservationClient);
    }

    // DTO 필드 구성은 가정. 실제 record 정의에 맞춰 이 헬퍼만 수정
    private Glp1InjectionRecordInDto createInDto(LocalDateTime injectedAt, LocalDateTime currentAt) {
        return new Glp1InjectionRecordInDto(GROUP_ID, injectedAt, currentAt);
    }
}
```

`any`는 `org.mockito.ArgumentMatchers.any`를 static import로 추가해야 합니다. 위 import 목록에서는 빠져 있습니다.

## 설계 설명

- **정상 등록 테스트**
  - 반환값이 저장된 엔티티의 ID와 같은지 확인합니다.
  - 푸시 예약이 `userId`와 `savedEntity.getNextInjectionAt()` 값으로 호출됐는지 `verify`로 확인합니다. 이 호출이 서비스의 외부 부수효과입니다.
  - `given(...)`으로 만든 스텁은 모두 서비스가 실제로 호출합니다. 따라서 Mockito strict stubs에서 `UnnecessaryStubbingException`이 나지 않습니다.
- **미래 시각 예외 테스트**
  - 서비스가 `getOwnedGroup`을 날짜 검사보다 먼저 호출하므로 이 스텁이 필요합니다. 스텁하지 않으면 `null`이 반환되고, 이후 흐름이 실제와 달라집니다.
  - 예외 타입만 검증하고 `save`와 푸시 예약이 일어나지 않았음을 같이 확인합니다. 예외만 던지고 저장은 해버리는 회귀를 잡기 위해서입니다.
  - `injectedAt`을 `currentAt`보다 1분 뒤로 잡아 경계에 가깝게 만들었습니다. 서비스가 `isAfter`를 쓰기 때문에 동일 시각은 통과합니다. 이 경계(동일 시각 통과)는 요청 범위 밖이라 케이스에 넣지 않았습니다.
  - 예외 메시지나 `ExceptionConstants.GLP1_FUTURE_INJECTION` 코드 검증은 `BadRequestException`이 코드를 노출하는지 모르므로 뺐습니다. 노출한다면 `hasFieldOrPropertyWithValue` 등으로 추가할 수 있습니다.
- **엔티티는 mock으로 처리했습니다.** 저장된 엔티티의 ID는 영속 계층이 부여하는 값이라 생성자로 넣기 어렵고, 엔티티 팩토리 `of(...)`의 시그니처도 확인하지 못했습니다. 엔티티 mock은 도메인 로직 검증에는 약하지만, 이 서비스 테스트의 관심사인 오케스트레이션 검증에는 충분합니다.

## 짚어둘 점

1. 푸시 예약이 `@Transactional` 안에서 실행됩니다. 외부 API 호출 후 트랜잭션이 롤백되면 예약만 남는 정합성 문제가 생길 수 있습니다. 요청 범위 밖이라 테스트에는 반영하지 않았고, 별도 이슈로 검토할 만합니다.
2. `FakeGlp1InjectionRecordRepository`가 이미 있으니, 이후 케이스가 늘면 Repository만 Fake로 교체하는 방법도 있습니다. 지금 두 케이스에서는 Mockito가 더 간단합니다.
