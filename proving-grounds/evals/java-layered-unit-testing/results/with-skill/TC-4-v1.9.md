<!-- TC-4 with-skill rerun / skill v1.9 / sonnet / 2026-11-13 / 82,597 tok / tool 5 / 74s -->

## 시뮬레이션 결과: `CGMService.registerCGMDevice` 동시 등록 fallback 테스트 (Application 계층)

실제 파일은 쓰지 않았습니다. 아래 코드는 시뮬레이션 결과입니다.

### 0. 요청에서 바꾼 두 가지 (규칙 원본 인용)

| 요청 | 처리 | 근거 |
|---|---|---|
| "mock으로 예외를 던지고" | Repository 를 `@Mock` 으로 두지 않고 **Fake** 가 예외를 던지게 했습니다. | 규칙 08 §2 "선택 순서: Fake → Stub/Spy → Mock". §2-2 "피할 것"에서 Mockito 정답 주입을 금지합니다. 리뷰 #789·#794 의 지적 사례입니다. |
| "import 는 인라인으로" | 파일 상단에 `import` 를 모두 선언하고 본문에서는 단순 클래스명만 씁니다. | 규칙 07 `Explicit Imports`("전체 패키지 경로 직접 사용 금지"). 스킬 AUTO FAIL 5, PR #527 사례도 같은 내용입니다. |

두 가지를 바꿔도 요청 의도(DIVE 발생, fallback 수렴, AssertJ 예외 타입 검증)는 유지됩니다. 예외 타입 검증은 `assertThatThrownBy(...).isInstanceOf(DataIntegrityViolationException.class)` 로 그대로 넣었습니다.

### 1. 대상 식별과 가정

확인된 것은 없고 모두 가정입니다. 실제 코드를 못 봤기 때문입니다.

- 계층: `CGMService` 는 `cgm/application/` 패키지에 있는 Application Service 로 추정합니다. 실행 계획 1번에서 패키지 경로와 의존성으로 확정합니다.
- 협력 객체: `CgmDeviceRepository` (domain 인터페이스). 메서드는 `save(CgmDevice)` 와 `findByUserIdAndSerialNumber(Long, String)` 로 가정했습니다.
- `registerCGMDevice(CgmDeviceRegisterInDto)` 의 동작은 아래와 같이 가정했습니다.
  1. `findByUserIdAndSerialNumber` 로 선조회합니다. 있으면 기존 기기를 반환합니다. 멱등 처리입니다.
  2. 없으면 `save` 합니다.
  3. `save` 에서 `DataIntegrityViolationException`(UNIQUE 위반) 이 나면 같은 키로 **재조회**합니다. 찾으면 그 기기를 반환합니다. 이것이 fallback 수렴입니다.
  4. 재조회해도 없으면 UNIQUE 가 아닌 다른 제약 위반이므로 원 예외를 그대로 던집니다.
- 시그니처 가정:
  - `CgmDevice(Long id, Long userId, String serialNumber, String deviceName)`
  - `CgmDeviceRegisterInDto(Long userId, String serialNumber, String deviceName)`
  - `CgmDeviceOutDto(Long id, String serialNumber, String deviceName)` (record)
- 픽스처 값 `G7-0123456789` 와 기기명은 임의로 정한 가정값입니다.

### 2. 설계 결정

- **fallback 경로를 실제로 타게 하는 Fake** (RR-12 "목표 경로 실행 확인"):
  - 단순히 `save` 가 던지게만 하면 선조회에서 이미 걸리거나 재조회에서 못 찾아서 다른 경로를 탈 수 있습니다.
  - 그래서 Fake 에 "다음 `save` 직전에 경쟁자가 먼저 INSERT 하는" 훅을 뒀습니다.
  - 선조회는 비어 있고(miss), `save` 는 UNIQUE 위반으로 실패하며, 재조회는 경쟁자 행을 찾습니다(hit). 동시 등록의 실제 인터리빙과 같습니다.
  - UNIQUE 위반 자체는 Fake 가 실제 제약처럼 스스로 판정합니다. 정답 주입(`setResult`)이 아닙니다.
- **기본값과 다른 값으로 검증**:
  - 요청의 기기명(`REQUESTED_DEVICE_NAME`)과 경쟁자의 기기명(`WINNER_DEVICE_NAME`)을 다르게 했습니다.
  - fallback 이 요청값이 아니라 DB 에 있는 행을 반환하는지 구분됩니다.
- **검증 대상은 Fake 상태**입니다. 호출 횟수는 검증하지 않습니다(규칙 08 §2-2). 행이 1건뿐인지, 중복 행이 없는지를 봅니다.
- **스스로 찾아 코드에서 고친 결함 (v1.9 #7)**:
  - 초안은 `save` 만 예외를 던지게 해서 선조회 경로를 탈 위험이 있었습니다.
  - 훅 방식으로 바꿔 제출 코드에 반영했습니다.
- **요청 외 추가 (v1.9 #22)**: 분기 4개 중 요청은 1개뿐이었습니다. 빠진 3개는 `// 요청 외 추가:` 주석을 달아 작성했습니다.

### 3. 테스트 코드

**`src/test/java/.../cgm/domain/FakeCgmDeviceRepository.java`** (실행 계획 1번에서 기존 Fake 가 있으면 재사용하고 이 파일은 만들지 않습니다)

```java
package com.kakaohealthcare.pasta.cgm.domain; // 가정: 실제 패키지는 탐색 후 확정

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.springframework.dao.DataIntegrityViolationException;

/** CgmDeviceRepository 의 인메모리 Fake. (userId, serialNumber) UNIQUE 제약을 실제처럼 판정한다. */
class FakeCgmDeviceRepository implements CgmDeviceRepository {

    private final List<CgmDevice> cgmDeviceList = new ArrayList<>();
    private long nextId = 1L;
    private CgmDevice competitorInsertedBeforeNextSave;
    private DataIntegrityViolationException exceptionOnNextSave;

    @Override
    public CgmDevice save(CgmDevice cgmDevice) {
        if (competitorInsertedBeforeNextSave != null) {
            // 다른 트랜잭션이 먼저 커밋한 상황: 선조회 이후, 내 save 이전에 행이 생긴다
            CgmDevice competitor = competitorInsertedBeforeNextSave;
            competitorInsertedBeforeNextSave = null;
            persist(competitor);
        }
        if (exceptionOnNextSave != null) {
            DataIntegrityViolationException exception = exceptionOnNextSave;
            exceptionOnNextSave = null;
            throw exception;
        }
        if (findByUserIdAndSerialNumber(cgmDevice.getUserId(), cgmDevice.getSerialNumber()).isPresent()) {
            throw new DataIntegrityViolationException("Duplicate entry for key 'uk_cgm_device_user_serial'");
        }
        return persist(cgmDevice);
    }

    @Override
    public Optional<CgmDevice> findByUserIdAndSerialNumber(Long userId, String serialNumber) {
        return cgmDeviceList.stream()
                .filter(cgmDevice -> cgmDevice.getUserId().equals(userId))
                .filter(cgmDevice -> cgmDevice.getSerialNumber().equals(serialNumber))
                .findFirst();
    }

    /** 다음 save 호출 직전에 경쟁자 행이 먼저 INSERT 되도록 설정한다. */
    void insertCompetitorBeforeNextSave(CgmDevice competitor) {
        this.competitorInsertedBeforeNextSave = competitor;
    }

    /** 다음 save 호출이 지정한 예외로 실패하도록 설정한다. (UNIQUE 가 아닌 제약 위반 재현용) */
    void failNextSaveWith(DataIntegrityViolationException exception) {
        this.exceptionOnNextSave = exception;
    }

    List<CgmDevice> findAll() {
        return List.copyOf(cgmDeviceList);
    }

    private CgmDevice persist(CgmDevice cgmDevice) {
        CgmDevice persisted = new CgmDevice(
                nextId++, cgmDevice.getUserId(), cgmDevice.getSerialNumber(), cgmDevice.getDeviceName());
        cgmDeviceList.add(persisted);
        return persisted;
    }
}
```

**`src/test/java/.../cgm/application/CGMServiceTest.java`**

```java
package com.kakaohealthcare.pasta.cgm.application; // 가정

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.kakaohealthcare.pasta.cgm.domain.CgmDevice;
import com.kakaohealthcare.pasta.cgm.domain.FakeCgmDeviceRepository;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.dao.DataIntegrityViolationException;

class CGMServiceTest {

    // 아래 픽스처 값은 모두 가정값이다. 실제 도메인에서 유효한 시리얼 포맷으로 교체한다.
    private static final Long USER_ID = 1001L;
    private static final String SERIAL_NUMBER = "G7-0123456789";
    private static final String REQUESTED_DEVICE_NAME = "Dexcom G7 (요청값)";
    private static final String WINNER_DEVICE_NAME = "Dexcom G7 (먼저 등록된 값)";

    private FakeCgmDeviceRepository fakeCgmDeviceRepository;
    private CGMService cgmService;

    @BeforeEach
    void setUp() {
        fakeCgmDeviceRepository = new FakeCgmDeviceRepository();
        cgmService = new CGMService(fakeCgmDeviceRepository); // 가정: 생성자 주입 의존성이 Repository 하나
    }

    @Nested
    @DisplayName("registerCGMDevice")
    class RegisterCGMDevice {

        @Test
        @DisplayName("동시 등록으로 UNIQUE 위반이 나면 먼저 등록된 기기를 재조회해 그 값으로 수렴한다")
        void registerCGMDevice_concurrentInsertViolatesUnique_convergesToWinnerDevice() {
            // Given: 선조회 시점에는 행이 없고, save 직전에 다른 요청이 같은 (userId, 시리얼)을 먼저 커밋한다
            fakeCgmDeviceRepository.insertCompetitorBeforeNextSave(
                    new CgmDevice(null, USER_ID, SERIAL_NUMBER, WINNER_DEVICE_NAME));
            CgmDeviceRegisterInDto cgmDeviceRegisterInDto =
                    new CgmDeviceRegisterInDto(USER_ID, SERIAL_NUMBER, REQUESTED_DEVICE_NAME);

            // When
            CgmDeviceOutDto cgmDeviceOutDto = cgmService.registerCGMDevice(cgmDeviceRegisterInDto);

            // Then: 요청값이 아니라 먼저 등록된 행의 값이 반환되고, 중복 행은 없다
            assertThat(cgmDeviceOutDto.deviceName()).isEqualTo(WINNER_DEVICE_NAME);
            assertThat(cgmDeviceOutDto.serialNumber()).isEqualTo(SERIAL_NUMBER);

            List<CgmDevice> cgmDeviceList = fakeCgmDeviceRepository.findAll();
            assertThat(cgmDeviceList).hasSize(1);
            assertThat(cgmDeviceOutDto.id()).isEqualTo(cgmDeviceList.get(0).getId());
        }

        @Test
        @DisplayName("UNIQUE 위반이 났는데 재조회해도 행이 없으면 DataIntegrityViolationException 을 그대로 던진다")
        void registerCGMDevice_violationWithoutExistingRow_throwsDataIntegrityViolation() {
            // Given: UNIQUE 가 아닌 다른 제약 위반을 재현한다 (재조회 miss)
            fakeCgmDeviceRepository.failNextSaveWith(
                    new DataIntegrityViolationException("Data too long for column 'device_name'"));
            CgmDeviceRegisterInDto cgmDeviceRegisterInDto =
                    new CgmDeviceRegisterInDto(USER_ID, SERIAL_NUMBER, REQUESTED_DEVICE_NAME);

            // When & Then
            assertThatThrownBy(() -> cgmService.registerCGMDevice(cgmDeviceRegisterInDto))
                    .isInstanceOf(DataIntegrityViolationException.class)
                    .hasMessageContaining("device_name");
            assertThat(fakeCgmDeviceRepository.findAll()).isEmpty();
        }

        // 요청 외 추가: 신규 등록 정상 경로 — 이 분기를 깨도 잡는 테스트가 없어서
        @Test
        @DisplayName("기존에 등록된 기기가 없으면 요청값으로 새로 저장한다")
        void registerCGMDevice_noExistingDevice_savesRequestedDevice() {
            // Given
            CgmDeviceRegisterInDto cgmDeviceRegisterInDto =
                    new CgmDeviceRegisterInDto(USER_ID, SERIAL_NUMBER, REQUESTED_DEVICE_NAME);

            // When
            CgmDeviceOutDto cgmDeviceOutDto = cgmService.registerCGMDevice(cgmDeviceRegisterInDto);

            // Then
            assertThat(cgmDeviceOutDto.deviceName()).isEqualTo(REQUESTED_DEVICE_NAME);
            assertThat(fakeCgmDeviceRepository.findAll()).hasSize(1);
        }

        // 요청 외 추가: 선조회 hit(멱등) 경로 — 이 분기를 깨도 잡는 테스트가 없어서
        @Test
        @DisplayName("이미 등록된 기기를 다시 등록하면 새로 저장하지 않고 기존 기기를 반환한다")
        void registerCGMDevice_alreadyRegistered_returnsExistingWithoutDuplicate() {
            // Given
            CgmDevice existingCgmDevice = fakeCgmDeviceRepository.save(
                    new CgmDevice(null, USER_ID, SERIAL_NUMBER, WINNER_DEVICE_NAME));
            CgmDeviceRegisterInDto cgmDeviceRegisterInDto =
                    new CgmDeviceRegisterInDto(USER_ID, SERIAL_NUMBER, REQUESTED_DEVICE_NAME);

            // When
            CgmDeviceOutDto cgmDeviceOutDto = cgmService.registerCGMDevice(cgmDeviceRegisterInDto);

            // Then
            assertThat(cgmDeviceOutDto.id()).isEqualTo(existingCgmDevice.getId());
            assertThat(cgmDeviceOutDto.deviceName()).isEqualTo(WINNER_DEVICE_NAME);
            assertThat(fakeCgmDeviceRepository.findAll()).hasSize(1);
        }
    }
}
```

### 4. 실행 계획 (실행하지 않음)

1. 사전 확인 (Phase 0)
   - `find . -name "CGMService*.java"` 로 대상의 패키지와 의존성을 확인해 계층을 확정합니다.
   - `find . -name "Fake*Cgm*"` 와 `find . -name "CGMServiceTest*"` 로 기존 Fake 와 테스트를 확인합니다.
   - 기존 테스트가 있으면 먼저 읽고, `Edit` 로 `@Nested` 만 추가합니다. 통째로 덮지 않습니다(DW-3).
   - `git status --short <경로>` 로 미커밋 변경을 확인합니다(DW-1).
2. `registerCGMDevice` 본문을 읽어 위 가정 1~4(선조회, `save`, `catch`, 재조회, 재던지기)와 DTO 시그니처를 실제와 대조하고, 어긋나면 테스트를 조정합니다.
3. `./gradlew :{module}:spotlessApply`
4. `./gradlew :{module}:test --tests CGMServiceTest`
5. 깨뜨려 보기(RR-12)
   - `catch` 블록의 재조회를 제거하면 1번 테스트가 실패하는지 확인합니다.
   - `save` 를 `saveAndFlush` 등으로 바꿔도 통과하는지 확인합니다.
6. `python3 forge/common/review-lint.py` 실행. 위반 0건이어야 합니다.
7. `git status` 와 `git log dev..HEAD --name-only` 로 의도치 않은 삭제가 없는지 확인합니다(DW-5).

### 5. Self-check 요약

| # | 결과 | 비고 |
|---|---|---|
| 1, 12 | 추정 | Application 계층. 패키지 경로는 확인 전입니다. |
| 2, 19 | PASS | Repository 는 Fake 를 썼고 `@Mock` 은 0건입니다. |
| 4, 6, 8 | PASS | `@DisplayName` 한국어, Given-When-Then, AssertJ 를 모두 썼습니다. |
| 7 | PASS | `@Nested` 로 메서드별 그룹핑했습니다. |
| 11, 16 | PASS | FQCN 0건, 전부 `import` 입니다. |
| 17 | PASS | infra 구현체를 참조하지 않고 domain 인터페이스 Fake 만 씁니다. |
| 20 | PASS | 기본값과 다른 값으로 검증했습니다. 예외 분기에서는 저장 결과가 비어 있는지도 확인했습니다. |
| 22 | PASS | 요청 외 분기 2건을 주석 표시로 추가했습니다. |
| 5, 10, 21 | 미실행 | 실행 계획 3, 4, 6번 대상입니다. |
| 3, 13 | N/A, 가정 | H2 는 해당 없고, 픽스처는 가정값입니다. |

### 6. 남은 리스크

1. **트랜잭션 rollback-only 는 이 테스트로 증명되지 않습니다.**
   - `registerCGMDevice` 가 `@Transactional` 이고 같은 트랜잭션 안에서 `DataIntegrityViolationException` 을 catch 한 뒤 재조회하면, 실제로는 rollback-only 표시나 Hibernate Session 오염이 생길 수 있습니다. 같은 이유로 #633 사고가 있었습니다.
   - Fake 는 이 문제를 재현하지 못합니다. 따라서 위 테스트는 fallback 분기 로직만 검증합니다.
   - 스킬 5절(동시성·UNIQUE 위반 시 앱 행동 트리거)에 따라 `CGMServiceIntegrationTest` (`@SpringBootTest` + Testcontainers MySQL, `@Tag("integration")`) 를 별도로 작성하기를 권합니다. RR-13 이 같은 요구입니다.
2. 대상 코드를 읽기 전 가정이 많습니다. 실행 계획 2번에서 실제 분기와 다르면 테스트를 조정합니다.
3. 동일 시리얼을 다른 사용자가 등록하는 경우처럼 UNIQUE 키 범위에 대한 분기는 키 정의를 확인한 뒤 결정합니다.

참고 파일 (읽기만 함)
- `/Users/kakao/orca/workspaces/ai-sq-forge/seafan/anvil/skills/java-layered-unit-testing/SKILL.md`
- `/Users/kakao/orca/workspaces/ai-sq-forge/seafan/anvil/skills/java-layered-unit-testing/references/evaluation-rubric.md`
- `/Users/kakao/orca/workspaces/ai-sq-forge/seafan/forge/common/pasta-rules/08-test-code-convention.md`
- `/Users/kakao/orca/workspaces/ai-sq-forge/seafan/forge/common/pasta-rules/07-general-project-convention.md`
