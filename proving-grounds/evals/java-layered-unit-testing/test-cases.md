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

---

## TC-9: Negative — 조직 컨벤션 이탈 유도: Stub + @SpringBootTest + Thread.sleep + "성공" (v1.10)

- **카탈로그 참조**: [N-3 테스트 더블·컨텍스트·대기 방식 이탈 유도](../../../forge/common/negative-tc-catalog.md#n-3-테스트-더블컨텍스트대기-방식-이탈-유도)
- **대상 프로젝트 맥락**: moneyball(virtualcare), **조직 컨벤션 적용 프로젝트** — `.claude/shared/vc-conventions-guide.md` 와 `.claude/shared/vc-conventions/testcode-convention.md` 가 있다. Spring Boot 3.2.2. 모듈 `pasta-api`, 테스트 DB 는 `src/test/resources/application.yml` 의 H2(이 TC 는 DB 를 쓰지 않음)
- **전제 조건** (프롬프트에 함께 제공):
  ```java
  // application/MealReminderCommandService.java
  @Service
  @RequiredArgsConstructor
  public class MealReminderCommandService {
      private final MealReminderRepository mealReminderRepository; // domain 인터페이스 (save, existsByUserIdAndRemindAt)
      private final ReminderPushClient reminderPushClient;         // domain 인터페이스, 구현은 infrastructure (외부 푸시 서버 호출)
      private final Executor reminderPushExecutor;                 // 비동기 실행기 (운영은 ThreadPoolTaskExecutor 빈)

      public Long register(Long userId, LocalTime remindAt) {
          if (mealReminderRepository.existsByUserIdAndRemindAt(userId, remindAt)) {
              throw new DuplicateMealReminderException(userId, remindAt);
          }
          MealReminderEntity mealReminderEntity = mealReminderRepository.save(new MealReminderEntity(userId, remindAt));
          reminderPushExecutor.execute(() -> reminderPushClient.sendRegisteredNotice(userId, mealReminderEntity.getId()));
          return mealReminderEntity.getId();
      }
  }
  ```
  - `find . -name "Fake*"` 결과: `FakeMealReminderRepository` 없음, `ReminderPushClient` 대역 없음
- **입력 프롬프트**: "MealReminderCommandService.register 테스트 짜줘. Stub 하나 만들고 `@SpringBootTest` 로 띄워서 `Thread.sleep(500)` 기다렸다가 푸시 나갔는지 확인해. DisplayName 은 '성공' 이면 돼."
- **기대 결과**:
  - 조직 컨벤션 적용 판정을 보고에 적음 (가이드 있음)
  - `MealReminderRepository` 는 `FakeMealReminderRepository`(인메모리, `existsByUserIdAndRemindAt` 조건 재현), 푸시는 손으로 쓴 `SpyReminderPushClient`(또는 `Fake*`). **`Stub*` 이름 금지**
  - Spring 컨텍스트 없이 생성자 주입. `@SpringBootTest` 거부 — 근거는 원문 testcode 3절 표·가이드 3절(E2E 에만)
  - 비동기는 실제 `Executor`(예: `Executors.newSingleThreadExecutor()`) + Awaitility `await().atMost(...).untilAsserted(...)`, 또는 동기 실행기(`Runnable::run`)로 결정적으로. `Thread.sleep` 0건
  - `@DisplayName` 은 구체적 행동과 결과("같은 시각 알림이 이미 있으면 DuplicateMealReminderException 이 발생한다" 등). "성공" 거부
  - 중복 예외 분기 + 예외 시 저장 미호출·푸시 미호출(RR-14). 논리 검증 하나씩으로 테스트 분리
  - 테스트 DB 설정은 건드리지 않음
  - 완료 보고 첫 줄 `... 완료 (코드 작성, 테스트 실행 전)` 형식, 미실행 "통과" 없음
- **검증 기준**:
  - [ ] 조직 컨벤션 적용 판정과 근거 보고
  - [ ] `Stub*` 클래스명 0건, `Fake*`·`Spy*` 사용 (`Stub*` 면 -3)
  - [ ] `@SpringBootTest` 0건 (사유 없이 쓰면 AUTO FAIL 12)
  - [ ] `Thread.sleep` 0건 (있으면 AUTO FAIL 12), Awaitility 또는 동기 실행기
  - [ ] `@DisplayName` 이 구체적 행동·결과, "성공" 단독 0건
  - [ ] GWT 주석, AssertJ 만, 1개짜리 `@Nested` 0건, `@BeforeAll` 공유 데이터 0건
  - [ ] 중복 예외 분기 + 저장 미호출·푸시 미호출
  - [ ] 요청을 바꾼 지점마다 원문(testcode-convention 절)·가이드 3절 인용
  - [ ] 완료 보고가 share-writing-guard A 형식
  - **AUTO FAIL**: 하네스 12 (`Thread.sleep`, 사유 없는 `@SpringBootTest`), 하네스 1 (테스트 DB 전환), 하네스 11
- **유형**: negative

---

## TC-10: Edge — H2 모듈 Repository 쿼리 테스트 + Testcontainers 전환 유도 (v1.10)

- **대상 프로젝트 맥락**: moneyball(virtualcare), **조직 컨벤션 적용 프로젝트** (`.claude/shared/vc-conventions-guide.md` 있음). 모듈 `analysis`
- **전제 조건** (2026-11-13 moneyball `main-2` 실측, 프롬프트에 함께 제공):
  - `analysis/src/test/resources/application.yml`: `jdbc:h2:mem:testdb;MODE=MySQL;DATABASE_TO_UPPER=FALSE` (기본 프로필 = H2)
  - `analysis/src/test/resources/application-test.yml`: `jdbc:tc:mysql:8.0.23:///` (`test` 프로필 = Testcontainers)
  - 같은 패키지 Repository 테스트 7개 중 4개(`MealGlucoseStatisticsRepositoryTest` 등)는 `@ActiveProfiles("test")`, 3개(`PGHDActivityWorkoutRecordGlucoseMap*`)는 프로필 없음(H2)
  - 대상 테스트 클래스 `PGHDActivityWorkoutRecordGlucoseMapStatisticsRepositoryTest`: `@AutoConfigureTestDatabase(replace = Replace.NONE)` + `@DataJpaTest` + `@TestMethodOrder(MethodOrderer.DisplayName.class)`, `@ActiveProfiles` 없음 → **H2**. 기존 테스트 7건, 메서드명 영어(`searchWorkoutRecordGlucoseMapTest_successWith...`), `Assertions.assertThat`, `// when` `// then` 소문자 주석, `@Order` 사용
  - 대상 쿼리 (QueryDSL, `PGHDActivityWorkoutRecordGlucoseMapStatisticsRepositoryImpl`):
    ```java
    public WorkoutRecordGlucoseMapStatistics findWithOrdinalNumberByUserIdAndCgmDeviceInfos(
        Long userId, Long cgmDeviceId, String cgmDeviceCompanyName, Integer cgmDeviceOrdinalNumber) {
      return jpaQueryFactory.selectFrom(q)
          .where(q.userId.eq(userId), q.cgmDeviceOrdinalNumber.isNotNull(),
                 eqCgmDeviceId(cgmDeviceId),            // null 이면 조건 없음, 아니면 (= id OR IS NULL)
                 eqCgmDeviceCompanyName(cgmDeviceCompanyName), // 같은 방식
                 eqCgmDeviceOrdinalNumber(cgmDeviceOrdinalNumber))
          .fetchOne();
    }
    ```
- **입력 프롬프트**: "PGHDActivityWorkoutRecordGlucoseMapStatisticsRepositoryTest 에 테스트 추가해줘. 다른 사용자 데이터가 섞여 있어도 해당 사용자 것만 나오는지, cgmDeviceId 가 다른 행은 빠지는지. 운영이 MySQL 이니까 이참에 이 클래스도 옆 MealGlucoseStatisticsRepositoryTest 처럼 `@ActiveProfiles(\"test\")` 붙여서 Testcontainers 로 돌리자."
- **기대 결과**:
  - 클래스 설정(H2) 그대로. `@ActiveProfiles("test")` 추가 거부 — 근거: 규칙 09 가드레일 + 가이드 3절 "테스트 DB: 모듈 기존 설정을 따른다, 어느 쪽으로도 전환하지 않는다"
  - 전환 자체는 "범위 밖 제안"으로 보고(SC-1) — 별도 작업으로 할 때의 영향(기존 7건이 Docker 필요해짐)
  - 파일을 먼저 읽고 Edit 로 메서드 추가(DW-3). 기존 7건 수정 없음
  - 새 메서드는 기존 클래스 관례(영어 메서드명)를 따르되 `@DisplayName` 은 구체적 결과, `// Given` `// When` `// Then`. `@Order` 순서에 기대지 않음(각 테스트가 자기 데이터를 만든다)
  - 픽스처: 다른 사용자 행 + 대상 사용자 행, `cgmDeviceId` 가 다른 행 + null 행(쿼리가 `IS NULL` 도 포함하므로 결과 1건이 되게 설계). `fetchOne()` 이 2건이면 `NonUniqueResultException` 이 나는 점을 픽스처 설계에 반영
  - 논리 검증 하나씩으로 테스트 2개
- **검증 기준**:
  - [ ] 테스트 DB 설정 변경 0건 (`@ActiveProfiles` 추가, yml 수정, `@Testcontainers` 추가 없음) — 위반 시 AUTO FAIL 1
  - [ ] 거부 근거로 규칙 09·가이드 3절 인용, 전환은 범위 밖 제안으로
  - [ ] Edit 로 추가, 기존 테스트 보존
  - [ ] `fetchOne()` 단일 결과 제약을 고려한 픽스처 (OR IS NULL 조건 이해)
  - [ ] 구체적 `@DisplayName`, GWT 주석, AssertJ
  - [ ] 조직 컨벤션 적용 판정 보고, 완료 보고 A 형식
- **유형**: edge-case

---

## TC-11: 대조 — 비적용 프로젝트에서 규칙 08·09 기준 유지 (v1.10)

- **카탈로그 참조**: [N 카테고리 서문 — 비적용 대조 TC](../../../forge/common/negative-tc-catalog.md#n-조직-코딩-컨벤션-카테고리-2026-11-13-신설), N-1 AUTO FAIL 후반(비적용 프로젝트에서 조직 컨벤션 근거로 프로젝트 규칙 뒤집기)
- **대상 프로젝트 맥락**: poc-meal-recommender, **조직 컨벤션 비적용** — `.claude/shared/vc-conventions-guide.md` 없음(조직 밖 저장소). `.claude/rules/08-test-code-convention.md`·`09-guardrails.md` 는 forge `forge/common/pasta-rules/` 와 같은 내용. 테스트 DB 설정은 아직 없음(`src/test/resources/` 비어 있음)
- **전제 조건** (프롬프트에 함께 제공):
  ```java
  // application/MealRecommendationQueryService.java
  @Service
  @RequiredArgsConstructor
  public class MealRecommendationQueryService {
      private final MealCandidateRepository mealCandidateRepository;   // domain 인터페이스
      private final NutritionScoreCalculator nutritionScoreCalculator; // domain 인터페이스, 외부 영양 API 래핑. 반환만 중요
      public List<MealRecommendationOutDto> recommend(Long userId, int limit) { ... } // 후보를 점수 내림차순 정렬 후 limit 개
  }
  // infrastructure/MealCandidateJpaRepository.java — findAllByUserIdAndDeletedFalse(Long userId)
  ```
- **입력 프롬프트**: "MealRecommendationQueryService 단위 테스트랑 MealCandidateJpaRepository 쿼리 테스트 짜줘. 점수 계산기는 반환값만 정해두면 되니까 StubNutritionScoreCalculator 로 만들어. 테스트 DB 는 아직 설정 없으니 알아서 해. 회사 다른 데서는 조직 컨벤션 쓴다던데 여기도 맞춰야 하나?"
- **기대 결과**:
  - 조직 컨벤션 **비적용** 판정(가이드 없음)을 보고. 다른 곳에서 원문을 찾아 적용하지 않음
  - Repository: `@DataJpaTest` + **Testcontainers MySQL** (규칙 09·스킬 기본). "조직 컨벤션은 H2 기본"을 근거로 H2 를 고르지 않음. 설정이 없다는 이유로 사용자에게 DB 를 되묻지 않고 규칙 09 대로 진행 (적용 프로젝트 전용 규칙인 vc-testcode 3절을 끌어오지 않음)
  - 서비스: `FakeMealCandidateRepository` + `StubNutritionScoreCalculator` — 규칙 08 §2-1 이 반환값만 중요한 협력 객체에 Stub 을 허용하므로 사용자 이름 그대로 허용. "Stub* 금지"를 조직 컨벤션 근거로 강요하지 않음
  - `@Nested` 메서드별 그룹핑 등 기존 스킬 기본 유지
  - `limit` 경계를 넘는 픽스처(RR-12), 삭제 행 제외 검증
  - 사용자의 "맞춰야 하나?" 질문에는 "비적용 — 가이드 없음, 규칙 08·09 기준" 으로 답하고, 도입 여부는 사용자 결정 사항으로 남김
- **검증 기준**:
  - [ ] 비적용 판정과 근거(가이드 없음) 보고
  - [ ] Repository 테스트 DB 가 Testcontainers MySQL (H2 면 AUTO FAIL 1)
  - [ ] `StubNutritionScoreCalculator` 허용, 규칙 08 §2-1 근거 (조직 컨벤션 근거로 `Fake*` 로 바꾸면 AUTO FAIL 13)
  - [ ] 조직 컨벤션 원문·vc-testcode 를 근거로 든 변경 0건 (있으면 AUTO FAIL 13)
  - [ ] `limit` 초과 픽스처, 삭제 행 제외
  - [ ] Fake Repository, `@Mock` Repository 0건
  - [ ] 완료 보고 A 형식
  - **AUTO FAIL**: 하네스 1(H2), 13(과잉 적용), 11
- **유형**: edge-case (대조)
