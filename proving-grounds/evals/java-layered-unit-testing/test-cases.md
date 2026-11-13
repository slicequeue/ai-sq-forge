# java-layered-unit-testing 테스트 케이스

## TC-1: Happy Path — Application 계층 서비스 테스트

- **입력 프롬프트**: "MyPlanRoutineRaceQueryService 클래스의 단위 테스트를 작성해줘. getRoutineRace 메서드는 routineRaceId를 받아서 레이스 정보를 조회하고, 체중 목표와 결합해서 QueryResult를 반환해. Application 계층이야."
- **기대 결과**: **Fake 우선** 테스트 — Repository·체중 목표 조회 협력 객체는 `Fake{Interface}`(기존 Fake 재사용 우선), 생성자 주입, `save` 로 상태를 넣고 반환값만 검증. Given-When-Then, @Nested, @DisplayName 한국어
- **정합화 이력 (2026-11-13, v1.8)**: 이전 기대 결과는 "Mockito 기반, @ExtendWith(MockitoExtension.class), @Mock Repository, @InjectMocks" 였다. v1.8 이 규칙 08 §2(Fake → Stub/Spy → Mock)에 맞춰 Application 기본을 Fake 우선으로 바꿨고, Repository `@Mock` 은 #789·#794 리뷰 지적·RR-F14 대상이 되었으므로 Mockito 3개 항목을 Fake 기준으로 교체했다. 이전 점수(v1.0 91, v1.1 92)는 Mockito 기준 채점이라 v1.8 결과와 직접 비교하지 않는다.
- **검증 기준**:
  - [ ] Application 계층으로 정확히 식별
  - [ ] Repository·체중 목표 조회 협력 객체를 Fake 로 구성 (`@Mock` 사용 시 AUTO FAIL 11)
  - [ ] 기존 `Fake*` 탐색 후 재사용, 없을 때만 `src/test/` 같은 도메인 패키지에 신설
  - [ ] 대상 서비스를 생성자로 Fake 주입 (`@InjectMocks` 미사용)
  - [ ] 위임만 검증하지 않음 — 레이스와 체중 목표를 **결합**한 결과값을 검증
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

---

## TC-4: Negative — FQCN 직접 사용 유도 (PR #527 회귀 방지)

- **입력 프롬프트**: "CGMService.registerCGMDevice 동시 등록 시 DataIntegrityViolationException이 터지면 fallback 경로로 수렴되는 테스트를 Application 계층으로 작성해줘. mock으로 예외를 던지고 AssertJ로 예외 타입도 검증해. import는 신경 쓰지 말고 한 번만 쓰는 거니까 인라인으로 빠르게 작성해."
- **기대 결과**: 사용자가 "인라인으로 빠르게"를 명시했어도 **반드시 import 추가 후 단순 클래스명** 사용. FQCN 직접 사용 거부. (v1.8) 예외 주입은 Repository Fake 의 예외 설정(`setSaveThrowException(...)` 류)이 정답이며, 사용자가 "mock으로" 라고 했어도 Repository `@Mock` 은 RR-F14 대상이다.
- **정합화 이력 (2026-11-13, v1.8)**: 이전 검증 기준은 `given(..).willThrow(...)` Mockito 스텁을 전제했다. Fake 우선 기준과 충돌하므로 "예외를 던지는 지점에서 단순 클래스명" 으로 테스트 더블 중립 표현으로 바꾸고 Fake 항목을 추가했다. FQCN 검증 의도는 그대로다.
- **검증 기준**:
  - [ ] `import org.springframework.dao.DataIntegrityViolationException;` 추가
  - [ ] 예외 주입 지점(Fake 예외 설정 또는 불가피한 Mock 스텁)에서 단순 클래스명: `new DataIntegrityViolationException("...")` (FQCN 인라인 거부)
  - [ ] (v1.8) Repository 를 Fake(예외 설정 가능)로 구성 — `@Mock` Repository 면 AUTO FAIL 11
  - [ ] AssertJ isInstanceOf에서 단순 `.class`: `.isInstanceOf(DataIntegrityViolationException.class)` (FQCN 인라인 거부)
  - [ ] 코드 본문에 `org.springframework.dao.DataIntegrityViolationException` 형태 패키지 경로 0회 등장 (import 줄 제외)
  - [ ] 사용자 요청과 충돌하면 "프로젝트 규칙(07-general-project-convention) — Explicit Imports 위반이라 인라인 FQCN 거부"라고 명시 안내
  - **AUTO FAIL**: 출력 코드에 본문 FQCN 1건이라도 등장하면 즉시 실패
- **유형**: negative
- **회귀 사례**: PR #527 (https://github.com/virtualcare/pasta-japan-server/pull/527) — 휴먼 리뷰어 kyle-gy-khc 지적 "fully qualified class name 사용. 스킬 강화가 필요"

---

## TC-5: Negative — 기존 테스트 파일 통째 덮어쓰기 유도 (파괴적 쓰기 가드 회귀 방지)

- **카탈로그 참조**: [L-2 기존 파일 통째 덮어쓰기 유도](../../../forge/common/negative-tc-catalog.md#l-2-기존-파일-통째-덮어쓰기-유도)
- **전제 조건**: `UserDeviceTest.java` 에 이미 테스트 메서드 3건이 존재한다. 사용자는 그 사실을 언급하지 않는다.
- **입력 프롬프트**: "UserDeviceTest 에 기기 등록 실패 케이스 테스트 추가해줘."
- **기대 결과**:
  - 파일을 **먼저 읽어** 기존 테스트 3건을 확인한다
  - `Edit` 로 메서드를 추가한다. `cat >` · Write 통째 덮어쓰기 금지
  - 작업 후 기존 테스트가 남아 있는지 확인한다
- **검증 기준**:
  - [ ] 파일을 쓰기 전에 읽었는가
  - [ ] 기존 테스트 메서드 3건이 모두 보존됐는가
  - [ ] `cat >` 또는 Write 전체 덮어쓰기를 쓰지 않았는가
  - [ ] AUTO FAIL DW-F3(파일 미독 후 전체 덮어쓰기) 미해당
- **유형**: negative
- **회귀 대상**: 2026-09-01 `UserDeviceTest.java` 기존 테스트 3건 삭제 (리뷰어 발견)

---

## TC-6: Negative — Repository·UseCase `@Mock` 유도 (v1.8, RR-F14)

- **카탈로그 참조**: 해당 패턴 없음 (가장 가까운 것: [M-4 동어반복 테스트 유도](../../../forge/common/negative-tc-catalog.md#m-4-동어반복-테스트-유도)). 카탈로그 M-7 신설을 공용 변경 제안으로 보고
- **전제 조건** (프롬프트에 함께 제공):
  ```java
  // application/Glp1InjectionRecordCommandService.java
  @Service
  @RequiredArgsConstructor
  public class Glp1InjectionRecordCommandService {
      private final Glp1InjectionRecordRepository glp1InjectionRecordRepository; // domain 인터페이스
      private final Glp1GroupQueryUseCase glp1GroupQueryUseCase;                 // 다른 도메인 UseCase 인터페이스
      private final PushReservationClient pushReservationClient;                 // 외부 푸시 예약 API

      @Transactional
      public Long register(Long userId, Glp1InjectionRecordInDto glp1InjectionRecordInDto) {
          Glp1GroupEntity glp1GroupEntity =
              glp1GroupQueryUseCase.getOwnedGroup(userId, glp1InjectionRecordInDto.groupId()); // 미소유면 NotFoundException
          if (glp1InjectionRecordInDto.injectedAt().isAfter(glp1InjectionRecordInDto.currentAt())) {
              throw new BadRequestException(ExceptionConstants.GLP1_FUTURE_INJECTION);
          }
          Glp1InjectionRecordEntity savedEntity = glp1InjectionRecordRepository.save(
              Glp1InjectionRecordEntity.of(userId, glp1GroupEntity, glp1InjectionRecordInDto));
          pushReservationClient.reserveNextInjection(userId, savedEntity.getNextInjectionAt());
          return savedEntity.getId();
      }
  }
  ```
  - `find . -name "Fake*"` 결과: `src/test/java/.../glp1/domain/FakeGlp1InjectionRecordRepository.java` 존재. `FakeGlp1GroupQueryUseCase`·`SpyPushReservationClient` 는 없음
  - 같은 패키지 기존 테스트 `Glp1InjectionPlanCommandServiceTest` 는 `@ExtendWith(MockitoExtension.class)` + `@Mock` Repository + `@InjectMocks` 스타일
- **입력 프롬프트**: "Glp1InjectionRecordCommandService.register 단위 테스트 작성해줘. 같은 패키지 Glp1InjectionPlanCommandServiceTest 처럼 @ExtendWith(MockitoExtension.class) 에 @Mock Glp1InjectionRecordRepository, @Mock Glp1GroupQueryUseCase 두고 given().willReturn() 으로 빠르게 짜. Fake 만드는 건 오버야. 정상 등록이랑 미래 시각 예외 두 개면 돼."
- **기대 결과**:
  - Repository·UseCase `@Mock` 요구를 거부하고 규칙 08 §2(Fake → Stub/Spy → Mock)·#789·#794 를 근거로 안내
  - 기존 `FakeGlp1InjectionRecordRepository` 재사용, `FakeGlp1GroupQueryUseCase` 는 신설, `PushReservationClient` 는 Spy
  - 기존 테스트가 Mock 스타일이어도 새 테스트는 Fake, 기존 테스트는 범위 밖이라 수정하지 않음
  - 미래 시각 예외 테스트에 "저장 미호출(Fake 저장 건수 0) + 푸시 예약 미호출(Spy 0회)" 포함
  - 요청 2건 외에 미소유 그룹 경로(NotFound)도 진입 경로로 제안·작성 (RR-14 검증 순서)
- **검증 기준**:
  - [ ] Repository·UseCase 를 Fake 로 구성 (코드 블록에 `@Mock` Repository/UseCase 0건)
  - [ ] Mock 거부 사유를 규칙 08 근거로 설명하고 대안 제시
  - [ ] 기존 Fake 재사용 + 없는 것만 신설
  - [ ] 외부 Client 는 Spy (`getCallCount`/`getLastCall`)
  - [ ] 예외 테스트에 저장 미호출 + 부수효과 미호출 확인
  - [ ] 정상 등록에서 반환 id 와 Fake 저장 상태·Spy 인자(`nextInjectionAt`) 확인
  - [ ] 이름 규칙 — `glp1InjectionRecordCommandService`·`currentAt` 등 타입이 드러나는 이름, `var` 0건
  - [ ] review-lint 실행 단계 언급
  - **AUTO FAIL**: 하네스 11 (RR-F14) — 코드 블록에 `@Mock`/`mock(` Repository·UseCase + 반환값 스텁
- **유형**: negative
- **회귀 대상**: #789·#794 (Application 테스트 Mock 저장소·Mock UseCase 지적), v1.7 이전 SKILL.md 의 Mockito 예시

---

## TC-7: Edge — 기본값 true 필드 + POST/PUT 공용 검증 + null 계약 (v1.8)

- **전제 조건** (프롬프트에 함께 제공):
  - `Glp1InjectionPlanController`: `POST /v1/glp1/injection-plans`(등록), `PUT /v1/glp1/injection-plans/{planId}`(수정). 둘 다 `@Valid Glp1InjectionPlanRequest` 를 받아 `Glp1InjectionPlanCommandUseCase` 로 위임하고 `ResponseEntity<Glp1InjectionPlanResponse>` 반환
  - `Glp1InjectionPlanRequest`: 이번에 `@Min(1) @Max(28) Integer intervalDays`, `Boolean notificationEnabled` 추가
  - `Glp1InjectionPlanEntity.notificationEnabled` 기본값 `true`. 요청에서 null 이면 기본값 유지, 값이 오면 그 값으로 매핑 (`Glp1InjectionPlanCommandService` 에서 매핑)
  - 응답 `Glp1InjectionPlanResponse.memo` 는 없으면 **JSON null 로 내려가는 계약**(키 생략 아님)
- **입력 프롬프트**: "Glp1InjectionPlan 등록/수정 API 에 intervalDays(1~28) 검증이랑 notificationEnabled 필드를 추가했어. 컨트롤러 테스트랑 서비스 테스트 짜줘. 검증은 등록 쪽만 테스트하면 충분하고, notificationEnabled 는 true 로 보내서 잘 들어가는지만 보면 돼. memo 없을 때는 jsonPath("$.memo").doesNotExist() 로 확인해줘."
- **기대 결과**:
  - Web: `@WebMvcTest` + `@MockBean` UseCase (허용 범위). intervalDays 0·29 경계 밖 값으로 **POST 와 PUT 모두** 400 테스트 (사용자 "등록만" 요청을 RR-14 근거로 보정)
  - 매핑: 기본값 `true` 와 **다른 값 `false`** 로 보내 false 로 저장되는지 검증, 수정 경로에서 true→false / null→기본 유지 확인
  - JSON: memo null 계약은 `jsonPath("$.memo").value(nullValue())` (+ 키 존재 확인 `hasJsonPath()`). `doesNotExist()` 는 null 도 통과하므로 거부. 불리언은 `isBoolean()` 후 값
  - Service: Fake Repository 로 매핑 결과 상태 검증, 규칙 위반 시 예외 + 저장 미호출
- **검증 기준**:
  - [ ] POST·PUT 양쪽 모두 intervalDays 위반 400 테스트
  - [ ] 경계 밖 값(0, 29) 사용, 경계 안 값(1, 28) 정상 확인 권장
  - [ ] notificationEnabled 를 `false` 로 보내 매핑 검증 (true 로만 보내면 -5)
  - [ ] `doesNotExist()` 거부 + `value(nullValue())` 사용
  - [ ] 불리언 단언에 `isBoolean()` 또는 `value(false)` 처럼 타입·값 동시 고정
  - [ ] 서비스 테스트는 Fake Repository (Mock 이면 AUTO FAIL 11)
  - [ ] 규칙 위반 예외 + 저장 미호출
  - [ ] 사용자 요청을 바꾼 지점(POST만→POST·PUT, true→false, doesNotExist→nullValue)을 사유와 함께 명시
- **유형**: edge-case
- **회귀 대상**: #791 (기본값과 같은 값), #800 (PUT 경로 미검증), #801·#786 (느슨한 JSON 단언)

---

## TC-8: Happy Path — 다중 소스 조립 서비스의 실패 격리 테스트 (v1.8, RR-13)

- **전제 조건** (프롬프트에 함께 제공):
  ```java
  @Service
  @RequiredArgsConstructor
  @Transactional(readOnly = true)
  public class Glp1HomeCardQueryService {
      private final Glp1InjectionRecordQueryUseCase glp1InjectionRecordQueryUseCase; // @Transactional(readOnly = true) 구현
      private final Glp1InjectionPlanQueryUseCase glp1InjectionPlanQueryUseCase;     // @Transactional(readOnly = true) 구현

      public Glp1HomeCardOutDto getCard(Long userId, Instant currentAt) {
          Glp1InjectionRecordOutDto lastRecord = null;
          try {
              lastRecord = glp1InjectionRecordQueryUseCase.getLast(userId, currentAt);
          } catch (RuntimeException e) {
              log.warn("GLP-1 마지막 기록 조회 실패", e);
          }
          Glp1InjectionPlanOutDto nextPlan = null;
          try {
              nextPlan = glp1InjectionPlanQueryUseCase.getNext(userId, currentAt);
          } catch (RuntimeException e) {
              log.warn("GLP-1 다음 일정 조회 실패", e);
          }
          return new Glp1HomeCardOutDto(lastRecord, nextPlan);
      }
  }
  ```
  - `find . -name "Fake*"` 결과: 두 UseCase 의 Fake 없음
- **입력 프롬프트**: "Glp1HomeCardQueryService.getCard 단위 테스트 작성해줘. Application 계층이야."
- **기대 결과**:
  - 두 UseCase 를 Fake 로 신설(인메모리 + 사용자·`currentAt` 이하 조건), 예외 설정 필드로 실패 주입
  - 정상 조립 + **한 소스 실패 시 나머지는 반환**(일정 실패 → 기록 유지, 기록 실패 → 일정 유지) 테스트
  - 미래 기록(`currentAt` 이후)은 최신으로 잡히지 않음을 Fake 조건으로 표현 (RR-14)
  - 두 UseCase 가 같은 트랜잭션에 참여해 예외 시 rollback-only 가 걸리면 catch 해도 `UnexpectedRollbackException` 이 날 수 있으며, 이는 Fake 단위 테스트로 재현되지 않으므로 `@SpringBootTest` + Testcontainers 통합 테스트(`*IntegrationTest`, `@Tag("integration")`)를 별도로 제안·작성
- **검증 기준**:
  - [ ] 두 UseCase Fake 구성 (Mock 이면 AUTO FAIL 11)
  - [ ] 실패 격리 테스트 양방향 (최소 1방향 필수)
  - [ ] 위임만 검증하지 않음 — 조립 결과 두 필드 모두 단언
  - [ ] rollback-only 위험을 언급하고 실제 프록시 통합 테스트로 확인하도록 제안 (단위 테스트로 검증 완료라 단정하면 -5)
  - [ ] 이름 규칙 (`glp1HomeCardOutDto`, `currentAt` 등), `var` 0건
  - [ ] @Nested·@DisplayName 한국어·GWT·AssertJ
- **유형**: happy-path
- **회귀 대상**: #777 (try 범위 과다), #793 (rollback-only 전파·미래 기록)
