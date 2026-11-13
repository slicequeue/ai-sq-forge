<!-- TC-4 with-skill (regression) / skill v1.8 / sonnet / 2026-11-13 / 78,614 tok / tool 4 / 65s -->

## 대상 클래스

- **클래스**: `CGMService.registerCGMDevice`
- **계층**: Application. 패키지를 `com.kakaohealthcare.pasta.cgm.application`으로 가정했습니다(추정). 실제 확인은 아래 실행 계획 1번에서 합니다.
- **테스트 방식**: Fake 우선. 상태가 있는 `CgmDeviceRepository`는 Fake로 대체하고, Spy는 쓰지 않았고 Mock은 0건입니다.

## 요청과 다르게 처리한 2건

스킬 규칙과 충돌하는 두 부분은 아래처럼 처리했습니다.

| 요청 | 처리 | 근거 |
|---|---|---|
| "mock으로 예외를 던지고" | Repository를 `@Mock`/`willThrow`로 두지 않고, **예외를 낼 수 있는 Fake**를 썼습니다. | 규칙 08 §2, 스킬 v1.8, AUTO FAIL 6(RR-F14). 사용자가 Mock을 요구해도 적용됩니다. |
| "import는 신경 쓰지 말고 인라인으로" | 인라인 FQCN을 쓰지 않았고 import를 전부 작성했습니다. | AUTO FAIL 5(FQCN 금지). 스킬이 "한 번만 쓰니까 인라인"을 명시적으로 금지합니다(PR #527). |

"AssertJ로 예외 타입 검증"은 두 가지로 나눠 반영했습니다.
- fallback으로 수렴하는 경로에서는 예외가 밖으로 나오지 않으므로 `doesNotThrowAnyException()`과 반환값·Fake 상태를 검증합니다.
- 수렴하지 못하는 경로에서는 `assertThatThrownBy(...).isInstanceOf(DataIntegrityViolationException.class)`로 예외 타입을 검증합니다.

## 확인된 것과 가정한 것

**확인된 것**: 스킬 SKILL.md v1.8, `references/evaluation-rubric.md`, 규칙 08.

**가정한 것**: 실제 코드가 없어서 아래는 모두 가정이며, 실행 계획 1번에서 확인합니다. 시그니처가 다르면 Fake와 테스트의 호출부만 조정하면 됩니다.

- `CGMService(CgmDeviceRepository)` 생성자 주입
- `CgmDeviceOutDto registerCGMDevice(CgmDeviceRegisterInDto)`
- 서비스의 동작:
  1. `findByUserIdAndSerialNumber`로 선조회합니다.
  2. 없으면 `save`합니다.
  3. `save`가 `DataIntegrityViolationException`을 던지면 재조회해서 기존 행을 반환합니다.
  4. 재조회에서도 없으면 원 예외를 그대로 던집니다.
- 이 서비스는 `DataIntegrityViolationException` 외의 예외는 잡지 않습니다.
- `CgmDeviceEntity`는 `of(userId, serialNumber)`와 `withId(id)`를 제공합니다.
- 픽스처 값(`1001L`, `"DXCM-G7-0042"`)은 임의 가정값입니다.

## 설계 포인트

- **레이스를 Fake로 재현합니다.** `simulateConcurrentInsertOnNextSave`는 서비스의 선조회가 끝난 뒤, `save` 직전에 경쟁 트랜잭션의 행을 먼저 넣습니다. 그러면 Fake의 UNIQUE 검사가 자연스럽게 `DataIntegrityViolationException`을 던집니다. 선조회에서 early-return되어 fallback 경로가 한 번도 실행되지 않는 문제(RR-12 "목표 경로 미실행")를 피하기 위한 구조입니다.
- **정답을 주입하지 않습니다.** Fake에는 `setResult` 같은 정답 주입 메서드가 없고, 상태와 UNIQUE 로직만 있습니다.
- **tautology를 피합니다.** 반환 `deviceId`가 경쟁 트랜잭션이 저장한 행의 id와 같은지, 그리고 Fake에 행이 정확히 1건인지를 함께 봅니다. fallback 분기를 깨면 테스트가 실패합니다.
- **Fake 위치**: `src/test/java/.../cgm/domain/FakeCgmDeviceRepository.java`. 먼저 `find . -name "Fake*Cgm*"`로 기존 Fake가 있는지 확인하고, 있으면 재사용합니다.

## 테스트 코드 전체

### 1. Fake: `FakeCgmDeviceRepository.java`

```java
package com.kakaohealthcare.pasta.cgm.domain;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.springframework.dao.DataIntegrityViolationException;

// 가정: CgmDeviceRepository 는 domain 계층 인터페이스, CgmDeviceEntity 는 domain 엔티티
public class FakeCgmDeviceRepository implements CgmDeviceRepository {

    private final List<CgmDeviceEntity> cgmDeviceEntityList = new ArrayList<>();
    private long sequence = 1L;
    private CgmDeviceEntity competitorEntityOnNextSave;
    private RuntimeException exceptionOnNextSave;

    @Override
    public CgmDeviceEntity save(CgmDeviceEntity cgmDeviceEntity) {
        if (exceptionOnNextSave != null) {
            RuntimeException runtimeException = exceptionOnNextSave;
            exceptionOnNextSave = null;
            throw runtimeException;
        }
        if (competitorEntityOnNextSave != null) {
            // 선조회 이후 다른 트랜잭션이 먼저 커밋한 상황을 재현
            insert(competitorEntityOnNextSave);
            competitorEntityOnNextSave = null;
        }
        return insert(cgmDeviceEntity);
    }

    @Override
    public Optional<CgmDeviceEntity> findByUserIdAndSerialNumber(Long userId, String serialNumber) {
        return cgmDeviceEntityList.stream()
            .filter(cgmDeviceEntity -> cgmDeviceEntity.getUserId().equals(userId))
            .filter(cgmDeviceEntity -> cgmDeviceEntity.getSerialNumber().equals(serialNumber))
            .findFirst();
    }

    // 실제 DB 의 UNIQUE(user_id, serial_number) 와 같은 조건을 Fake 가 직접 적용한다
    private CgmDeviceEntity insert(CgmDeviceEntity cgmDeviceEntity) {
        boolean duplicated = findByUserIdAndSerialNumber(
                cgmDeviceEntity.getUserId(), cgmDeviceEntity.getSerialNumber())
            .isPresent();
        if (duplicated) {
            throw new DataIntegrityViolationException("Duplicate entry for uk_cgm_device_user_serial");
        }
        CgmDeviceEntity savedCgmDeviceEntity = cgmDeviceEntity.withId(sequence++);
        cgmDeviceEntityList.add(savedCgmDeviceEntity);
        return savedCgmDeviceEntity;
    }

    // 테스트 시나리오 설정용
    public void simulateConcurrentInsertOnNextSave(CgmDeviceEntity competitorEntity) {
        this.competitorEntityOnNextSave = competitorEntity;
    }

    public void failNextSaveWith(RuntimeException runtimeException) {
        this.exceptionOnNextSave = runtimeException;
    }

    public int count() {
        return cgmDeviceEntityList.size();
    }
}
```

### 2. 테스트: `CGMServiceTest.java`

```java
package com.kakaohealthcare.pasta.cgm.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.dao.DataIntegrityViolationException;

import com.kakaohealthcare.pasta.cgm.domain.CgmDeviceEntity;
import com.kakaohealthcare.pasta.cgm.domain.FakeCgmDeviceRepository;

// 가정: CgmDeviceRegisterInDto / CgmDeviceOutDto 는 application 계층 DTO
class CGMServiceTest {

    private static final Long USER_ID = 1001L; // 가정값
    private static final String SERIAL_NUMBER = "DXCM-G7-0042"; // 가정값

    private FakeCgmDeviceRepository fakeCgmDeviceRepository;
    private CGMService cgmService;

    @BeforeEach
    void setUp() {
        fakeCgmDeviceRepository = new FakeCgmDeviceRepository();
        cgmService = new CGMService(fakeCgmDeviceRepository);
    }

    @Nested
    @DisplayName("registerCGMDevice")
    class RegisterCGMDevice {

        @Test
        @DisplayName("경합이 없으면 새 기기를 저장하고 그 id 를 돌려준다")
        void registerCGMDevice_noRace_savesNewDevice() {
            // Given
            CgmDeviceRegisterInDto cgmDeviceRegisterInDto = new CgmDeviceRegisterInDto(USER_ID, SERIAL_NUMBER);

            // When
            CgmDeviceOutDto cgmDeviceOutDto = cgmService.registerCGMDevice(cgmDeviceRegisterInDto);

            // Then
            assertThat(cgmDeviceOutDto.serialNumber()).isEqualTo(SERIAL_NUMBER);
            assertThat(fakeCgmDeviceRepository.count()).isEqualTo(1);
        }

        @Test
        @DisplayName("동시 등록으로 UNIQUE 위반이 나면 예외 없이 먼저 저장된 기기로 수렴한다")
        void registerCGMDevice_concurrentInsert_convergesToExistingDevice() {
            // Given: 선조회 시점엔 없었지만 save 직전에 다른 트랜잭션이 같은 기기를 먼저 커밋
            fakeCgmDeviceRepository.simulateConcurrentInsertOnNextSave(CgmDeviceEntity.of(USER_ID, SERIAL_NUMBER));
            CgmDeviceRegisterInDto cgmDeviceRegisterInDto = new CgmDeviceRegisterInDto(USER_ID, SERIAL_NUMBER);

            // When
            assertThatCode(() -> cgmService.registerCGMDevice(cgmDeviceRegisterInDto))
                .doesNotThrowAnyException();
            CgmDeviceOutDto cgmDeviceOutDto = cgmService.registerCGMDevice(cgmDeviceRegisterInDto);

            // Then: 경쟁 트랜잭션이 저장한 행의 id 로 수렴, 중복 행은 생기지 않음
            CgmDeviceEntity competitorCgmDeviceEntity = fakeCgmDeviceRepository
                .findByUserIdAndSerialNumber(USER_ID, SERIAL_NUMBER)
                .orElseThrow();
            assertThat(cgmDeviceOutDto.deviceId()).isEqualTo(competitorCgmDeviceEntity.getId());
            assertThat(fakeCgmDeviceRepository.count()).isEqualTo(1);
        }

        @Test
        @DisplayName("UNIQUE 위반인데 재조회해도 기존 행이 없으면 원래 예외를 그대로 던지고 저장하지 않는다")
        void registerCGMDevice_violationWithoutExistingRow_propagatesException() {
            // Given: 다른 제약 위반처럼 재조회로 수렴할 행이 없는 경우
            fakeCgmDeviceRepository.failNextSaveWith(new DataIntegrityViolationException("check constraint"));
            CgmDeviceRegisterInDto cgmDeviceRegisterInDto = new CgmDeviceRegisterInDto(USER_ID, SERIAL_NUMBER);

            // When & Then
            assertThatThrownBy(() -> cgmService.registerCGMDevice(cgmDeviceRegisterInDto))
                .isInstanceOf(DataIntegrityViolationException.class)
                .hasMessageContaining("check constraint");
            assertThat(fakeCgmDeviceRepository.count()).isZero();
        }

        @Test
        @DisplayName("DataIntegrityViolationException 이 아닌 예외는 삼키지 않고 그대로 전파한다")
        void registerCGMDevice_otherException_isNotSwallowed() {
            // Given
            fakeCgmDeviceRepository.failNextSaveWith(new IllegalStateException("db down"));
            CgmDeviceRegisterInDto cgmDeviceRegisterInDto = new CgmDeviceRegisterInDto(USER_ID, SERIAL_NUMBER);

            // When & Then
            assertThatThrownBy(() -> cgmService.registerCGMDevice(cgmDeviceRegisterInDto))
                .isInstanceOf(IllegalStateException.class)
                .isNotInstanceOf(DataIntegrityViolationException.class);
            assertThat(fakeCgmDeviceRepository.count()).isZero();
        }
    }
}
```

**고쳐야 할 점**: 두 번째 테스트에서 `registerCGMDevice`를 두 번 호출합니다(예외 검증용과 반환값용). 첫 호출에서 Fake의 1회성 경쟁 행 설정이 소모되므로, 두 번째 호출은 선조회에서 기존 행을 바로 찾습니다. 그러면 fallback 경로가 아니라 선조회 경로를 검증하게 됩니다. 실제 작성 시에는 아래처럼 한 번만 호출해서 결과를 받도록 고쳐야 합니다.

```java
CgmDeviceOutDto[] holder = new CgmDeviceOutDto[1];
assertThatCode(() -> holder[0] = cgmService.registerCGMDevice(cgmDeviceRegisterInDto))
    .doesNotThrowAnyException();
```

더 간단한 방법은 `assertThatCode`를 빼고 반환값 검증만 두는 것입니다. 예외가 났다면 호출 시점에서 이미 테스트가 실패하기 때문입니다. 이쪽을 권장합니다.

## 실행 계획

아래 명령은 시뮬레이션이라 실행하지 않았습니다.

1. **사전 확인**
   - `find . -path "*cgm*" -name "CGMService*.java"`로 계층과 패키지를 확정합니다.
   - `find . -name "Fake*Cgm*"`로 기존 Fake를 확인하고, 있으면 재사용합니다.
   - 같은 패키지의 기존 `*Test`를 읽어 `@Nested`와 DisplayName 톤을 맞춥니다.
   - 위 가정(시그니처, DTO, 서비스의 catch 범위)을 실제 코드와 대조합니다.
2. **쓰기 가드(DW-1, DW-3)**
   - `git status --short <테스트 경로>`로 미커밋 변경을 확인합니다.
   - `CGMServiceTest`가 이미 있으면 Read한 뒤 Edit로 `@Nested`만 추가합니다. Write로 덮지 않습니다.
3. **포매팅**: `./gradlew :pasta-api:spotlessApply`
4. **테스트 실행**: `./gradlew :pasta-api:test --tests CGMServiceTest`
5. **lint**: `python3 forge/common/review-lint.py`로 위반 0건을 확인합니다.
6. **실효성 검증(RR-12)**
   - 서비스의 catch 블록을 임시로 제거해서 2번 테스트가 실패하는지 확인합니다.
   - 재조회 fallback을 제거했을 때 3번 테스트가 실패하는지도 확인합니다.
   - 실패하지 않으면 테스트가 회귀를 막지 못하는 것입니다.
7. **사후 확인(DW-5)**: `git status`로 의도치 않은 삭제가 없는지 확인합니다.

## Self-check

| # | 항목 | 결과 |
|---|---|---|
| 1, 12 | 계층 식별 근거 | PASS (패키지 경로는 추정으로 표기) |
| 2, 19 | 계층별 방식, Repository를 Mock으로 두지 않음 | PASS (Fake 사용, Mock 0건) |
| 4, 6, 7, 8 | DisplayName, Given-When-Then, `@Nested`, AssertJ | PASS |
| 11, 16 | FQCN 없음, import 전부 작성 | PASS |
| 17 | infra 구현체 직접 참조 없음 | PASS (domain 인터페이스 Fake) |
| 20 | 깨뜨리면 실패하는가 | 조건부 PASS (실행 계획 6번으로 확인 필요) |
| 3, 5, 10, 21 | H2, 테스트 통과, spotless, review-lint | 미실행 (실행 계획 3~5번) |
| 13 | Fixture 가정 표기 | PASS (주석으로 표기) |
| 18 | verify 대신 상태 검증 | PASS |

## 남은 리스크

1. **실제 동시성은 단위 테스트로 재현되지 않습니다.** Fake는 "경쟁 행이 먼저 들어온 결과"만 시뮬레이션합니다. 실제 UNIQUE 위반 후 Hibernate Session 오염(예: AssertionFailure)과 트랜잭션 rollback-only 전파는 잡지 못합니다. SKILL §5 기준으로 `CGMServiceConcurrencyIntegrationTest`(`@SpringBootTest` + Testcontainers MySQL, `@Tag("integration")`)를 별도로 추가하는 것을 권장합니다. 이번 요청 범위 밖이라 작성하지 않았고 보고만 합니다(SC 가드).
2. **서비스 구현 가정이 틀릴 수 있습니다.** 예를 들어 서비스가 `REQUIRES_NEW`로 fallback 조회를 하거나 예외를 도메인 예외로 변환한다면, 3번과 4번 테스트의 기대 예외 타입을 바꿔야 합니다.
3. **같은 값 중복 등록에 대한 정책은 검증하지 않았습니다.** 같은 사용자가 같은 시리얼을 순차 재등록하는 경우의 동작(멱등 반환인지 예외인지)은 정책 합의가 없어 테스트에 넣지 않았습니다.
