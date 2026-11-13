<!-- TC-8 baseline / no skill / sonnet / 2026-11-13 / 47,603 tok / tool 0 / 35s -->

# Glp1HomeCardQueryService.getCard 단위 테스트 (시뮬레이션, 파일 미작성)

## 설계 판단

- **Fake 가 없으므로 Mockito mock 을 쓴다.** 두 UseCase 의 Fake 는 없고, 이 테스트를 위해 Fake 를 새로 만들지 않는다. 검증할 것이 호출 여부, 인자, 예외 주입뿐이라 `@Mock` 이 맞다.
- **순수 단위 테스트로 작성한다.** `@ExtendWith(MockitoExtension.class)` 만 쓰고 Spring 컨텍스트는 띄우지 않는다. `@Transactional` 은 프록시가 없어 동작하지 않으므로 이 테스트의 검증 대상이 아니다.
- **테스트 대상은 서비스의 고유 로직이다.** 각 UseCase 호출을 독립적으로 try/catch 해서 부분 실패를 허용하는 부분이다. 케이스는 아래 8개다.
  - 정상: 둘 다 성공, 둘 다 null 반환.
  - 부분 실패: 마지막 기록만 실패, 다음 일정만 실패.
  - 전체 실패: 둘 다 실패.
  - 경계: `Error` 는 삼키지 않음, 인자 전달, 호출 독립성.
- 메서드명은 한국어 `@DisplayName` 과 영문 `메서드_상황_결과` 형식을 함께 쓴다.

## 테스트 코드

```java
package com.example.application.glp1.home; // 실제 패키지에 맞게 조정

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;

import java.time.Instant;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class Glp1HomeCardQueryServiceTest {

    private static final Long USER_ID = 1L;
    private static final Instant CURRENT_AT = Instant.parse("2026-11-13T01:00:00Z");

    @Mock
    private Glp1InjectionRecordQueryUseCase glp1InjectionRecordQueryUseCase;

    @Mock
    private Glp1InjectionPlanQueryUseCase glp1InjectionPlanQueryUseCase;

    @InjectMocks
    private Glp1HomeCardQueryService sut;

    @Nested
    @DisplayName("getCard")
    class GetCard {

        @Test
        @DisplayName("두 조회가 모두 성공하면 마지막 기록과 다음 일정을 모두 담아 반환한다")
        void getCard_bothSucceed_returnsBoth() {
            // given
            Glp1InjectionRecordOutDto lastRecord = mock(Glp1InjectionRecordOutDto.class);
            Glp1InjectionPlanOutDto nextPlan = mock(Glp1InjectionPlanOutDto.class);
            given(glp1InjectionRecordQueryUseCase.getLast(USER_ID, CURRENT_AT)).willReturn(lastRecord);
            given(glp1InjectionPlanQueryUseCase.getNext(USER_ID, CURRENT_AT)).willReturn(nextPlan);

            // when
            Glp1HomeCardOutDto result = sut.getCard(USER_ID, CURRENT_AT);

            // then
            assertThat(result.lastRecord()).isSameAs(lastRecord);
            assertThat(result.nextPlan()).isSameAs(nextPlan);
        }

        @Test
        @DisplayName("두 조회가 모두 null 을 반환하면 예외 없이 양쪽 null 인 카드를 반환한다")
        void getCard_bothReturnNull_returnsEmptyCard() {
            // given
            given(glp1InjectionRecordQueryUseCase.getLast(USER_ID, CURRENT_AT)).willReturn(null);
            given(glp1InjectionPlanQueryUseCase.getNext(USER_ID, CURRENT_AT)).willReturn(null);

            // when
            Glp1HomeCardOutDto result = sut.getCard(USER_ID, CURRENT_AT);

            // then
            assertThat(result.lastRecord()).isNull();
            assertThat(result.nextPlan()).isNull();
        }

        @Test
        @DisplayName("마지막 기록 조회가 RuntimeException 으로 실패해도 다음 일정은 정상 반환하고 예외는 전파하지 않는다")
        void getCard_lastRecordFails_returnsOnlyNextPlan() {
            // given
            Glp1InjectionPlanOutDto nextPlan = mock(Glp1InjectionPlanOutDto.class);
            given(glp1InjectionRecordQueryUseCase.getLast(USER_ID, CURRENT_AT))
                    .willThrow(new IllegalStateException("기록 조회 장애"));
            given(glp1InjectionPlanQueryUseCase.getNext(USER_ID, CURRENT_AT)).willReturn(nextPlan);

            // when
            Glp1HomeCardOutDto result = sut.getCard(USER_ID, CURRENT_AT);

            // then
            assertThat(result.lastRecord()).isNull();
            assertThat(result.nextPlan()).isSameAs(nextPlan);
        }

        @Test
        @DisplayName("다음 일정 조회가 RuntimeException 으로 실패해도 마지막 기록은 정상 반환하고 예외는 전파하지 않는다")
        void getCard_nextPlanFails_returnsOnlyLastRecord() {
            // given
            Glp1InjectionRecordOutDto lastRecord = mock(Glp1InjectionRecordOutDto.class);
            given(glp1InjectionRecordQueryUseCase.getLast(USER_ID, CURRENT_AT)).willReturn(lastRecord);
            given(glp1InjectionPlanQueryUseCase.getNext(USER_ID, CURRENT_AT))
                    .willThrow(new IllegalStateException("일정 조회 장애"));

            // when
            Glp1HomeCardOutDto result = sut.getCard(USER_ID, CURRENT_AT);

            // then
            assertThat(result.lastRecord()).isSameAs(lastRecord);
            assertThat(result.nextPlan()).isNull();
        }

        @Test
        @DisplayName("두 조회가 모두 실패하면 예외 없이 양쪽 null 인 카드를 반환한다")
        void getCard_bothFail_returnsEmptyCard() {
            // given
            given(glp1InjectionRecordQueryUseCase.getLast(USER_ID, CURRENT_AT))
                    .willThrow(new IllegalStateException("기록 조회 장애"));
            given(glp1InjectionPlanQueryUseCase.getNext(USER_ID, CURRENT_AT))
                    .willThrow(new IllegalArgumentException("일정 조회 장애"));

            // when
            Glp1HomeCardOutDto result = sut.getCard(USER_ID, CURRENT_AT);

            // then
            assertThat(result.lastRecord()).isNull();
            assertThat(result.nextPlan()).isNull();
        }

        @Test
        @DisplayName("마지막 기록 조회가 실패해도 다음 일정 조회는 반드시 호출된다 (호출 독립성)")
        void getCard_lastRecordFails_stillInvokesNextPlan() {
            // given
            given(glp1InjectionRecordQueryUseCase.getLast(USER_ID, CURRENT_AT))
                    .willThrow(new IllegalStateException("기록 조회 장애"));

            // when
            sut.getCard(USER_ID, CURRENT_AT);

            // then
            verify(glp1InjectionPlanQueryUseCase).getNext(USER_ID, CURRENT_AT);
        }

        @Test
        @DisplayName("RuntimeException 이 아닌 Error 는 삼키지 않고 전파하며, 이후 조회는 수행하지 않는다")
        void getCard_errorThrown_propagatesAndSkipsNext() {
            // given
            given(glp1InjectionRecordQueryUseCase.getLast(USER_ID, CURRENT_AT))
                    .willThrow(new AssertionError("치명적 오류"));

            // when & then
            assertThatThrownBy(() -> sut.getCard(USER_ID, CURRENT_AT))
                    .isInstanceOf(AssertionError.class)
                    .hasMessage("치명적 오류");
            verify(glp1InjectionPlanQueryUseCase, never()).getNext(any(), any());
        }

        @Test
        @DisplayName("userId 와 currentAt 을 두 UseCase 에 동일하게 전달한다")
        void getCard_passesSameArgumentsToBothUseCases() {
            // when
            sut.getCard(USER_ID, CURRENT_AT);

            // then
            verify(glp1InjectionRecordQueryUseCase).getLast(USER_ID, CURRENT_AT);
            verify(glp1InjectionPlanQueryUseCase).getNext(USER_ID, CURRENT_AT);
        }
    }
}
```

## 가정 (확인된 사실이 아닌 것)

- `Glp1HomeCardOutDto` 가 record 이고 접근자가 `lastRecord()`, `nextPlan()` 이라고 가정했다. getter 형태라면 `getLastRecord()` 와 `getNextPlan()` 으로 바꿔야 한다.
- OutDto 를 `mock()` 으로 만들었다. record 는 final 이라 Mockito 5 이상(inline mock maker 기본)에서만 동작한다. 하위 버전이면 실제 생성자로 만든 인스턴스를 써야 한다.
- `getLast` 와 `getNext` 가 null 을 반환할 수 있다고 가정했다. 두 번째 케이스가 그 가정에 의존하므로, 계약상 null 을 반환하지 않으면 지운다.
- 두 UseCase 의 반환 타입이 OutDto 와 일치한다고 가정했다. 반환 타입이 `Optional` 이면 `willReturn` 부분을 바꿔야 한다.
- `@InjectMocks` 는 생성자 주입(`@RequiredArgsConstructor`)으로 동작하며, 두 필드의 타입이 달라 매핑이 모호하지 않다.
- 서비스가 `log` 를 쓰는데 제시된 코드에는 `@Slf4j` 가 보이지 않는다. 생략된 것으로 보고 컴파일된다고 가정했다.

## 이 단위 테스트로 검증되지 않는 위험 (보고 사항)

1. **트랜잭션 rollback-only 오염 가능성.**
   - 서비스와 두 UseCase 가 모두 `@Transactional(readOnly = true)` 이고 기본 전파 속성은 REQUIRED 라서 하나의 물리 트랜잭션에 참여한다.
   - UseCase 프록시에서 RuntimeException 이 나가면 공유 트랜잭션이 rollback-only 로 표시된다.
   - 서비스가 예외를 catch 해도 `getCard` 종료 시점에 `UnexpectedRollbackException` 이 발생할 수 있다. 이 경우 "부분 실패 허용" 의도가 무력화된다.
   - mock 기반 단위 테스트는 프록시가 없어 이 문제를 잡지 못한다. 통합 테스트(`@SpringBootTest` 또는 `@DataJpaTest` 와 실제 빈)로 별도 확인이 필요하다.
   - 확정된 결함은 아니고 의심 사항이다. 해결 방향이 두 가지다. UseCase 쪽에 `noRollbackFor` 를 두거나, 서비스의 트랜잭션 구성을 바꿔야 한다. 둘 다 설계 결정이라 이번 범위에서는 제안만 한다.
2. **로그 출력은 검증하지 않았다.** `log.warn` 호출은 부수 효과라 검증하지 않았다. 필요하면 `OutputCaptureExtension` 이나 ListAppender 로 추가한다.
3. **예외 처리 범위.** RuntimeException 전체를 삼키므로 NPE 나 프로그래밍 오류도 은폐될 수 있다. 의도라면 현재 테스트로 충분하지만, 예외 종류를 좁힐지는 별도 합의가 필요하다.
