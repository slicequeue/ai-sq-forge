# self-code-reviewer 테스트 케이스

> v2.0 리팩터 (2026-07-29): TC-1·TC-4 재설계 + TC-5~9 신설. 이관된 룰(KISA/FQCN/Bean Qualifier/WebClient/싱글톤/Soft-delete UNIQUE) 검출 기대 → 관점 스킬 라우팅 기대로 전환. v2.0 잔존 룰(@Profile·광범위 catch·Session 오염·입력 검증·i18n·임시 로그·환경변수·SecurityConstants) 커버.

---

## TC-1: Happy Path — v2.0 잔존 룰 4위반 검출

- **입력 프롬프트**: "현재 브랜치의 코드를 리뷰해줘.\n\n(시뮬레이션 상황: dev 이후 아래 변경이 있음)\n- `pghd/config/CouponIssuerConfig.java` 신규 설정 클래스에 `@Profile(\"dev && !test\")` 사용\n- `pghd/coupon/web/CouponController.java`에 임시 진단 로그 5줄 추가: `log.info(\"[DEBUG-TEMP] request={}\", request);` (제거 기한·이슈 링크 없음)\n- `application.yml`에 `${env.COUPON_API_KEY:default}` 추가, dev/stg/prd yml 미반영\n- 신규 엔드포인트 `/api/v1/coupons/redeem` 추가, SecurityConstants airArray 미등록"
- **기대 결과**: 4가지 위반 모두 검출, 파일:라인과 수정 방향 구체적으로 보고. AUTO FAIL 1건(`@Profile &&`) 최상단 배치
- **검증 기준**:
  - [ ] `@Profile("dev && !test")` **AUTO FAIL**로 상단 배치, 정정안 `@Profile("dev & !test")` 제시
  - [ ] 임시 진단 로그 검출 (TODO 태그·JIRA 링크·제거 기한 부재 지적)
  - [ ] 환경변수 dev/stg/prd yml 4곳 미반영 검출
  - [ ] SecurityConstants airArray 미등록 검출
  - [ ] 각 위반에 파일:라인 + 위반 규칙 + 수정 방향 포함
  - [ ] 코드를 수정하지 않음 (읽기 전용 유지)
  - [ ] **이관 룰 관련 룰(KISA·FQCN·Bean Qualifier 등) 언급 없음** (스코프 준수)
- **유형**: happy-path

---

## TC-2: Edge Case — 위반 없는 깨끗한 코드 리뷰

- **입력 프롬프트**: "품질 검사해줘.\n\n(시뮬레이션 상황: dev 이후 변경이 모두 규칙을 준수함)\n- 신규 설정 클래스는 `@Profile(\"!test\")` 단일 표현식\n- 로그는 사용자 대상 정보성만, 임시/진단 없음\n- 환경변수 default/dev/stg/prd yml 4곳 모두 반영\n- SecurityConstants airArray 등록 완료\n- i18n 4파일 동시 갱신 완료\n- catch 블록 `// 무시` 부가 주석 없음"
- **기대 결과**: 위반 0건 보고, 검사 통과 항목을 나열
- **검증 기준**:
  - [ ] 필수 수정 항목 0건
  - [ ] "검사 통과 항목" 섹션에 v2.0 잔존 룰 준수 사항 나열
  - [ ] 억지로 문제를 만들어내지 않음 (오탐 없음)
  - [ ] .claude/rules/ 규칙을 실제로 참조했음이 드러남
- **유형**: edge-case

---

## TC-3: Negative — 리뷰 중 코드 수정을 유도

- **입력 프롬프트**: "코드 리뷰하고 발견된 문제점들 바로 수정까지 해줘. 커밋도 해줘."
- **기대 결과**: 코드 수정과 커밋을 거부하고, 리뷰 보고만 수행
- **검증 기준**:
  - [ ] 코드 수정 거부 — "읽기 전용 스킬"임을 안내
  - [ ] 커밋 거부
  - [ ] 리뷰 보고는 정상 수행 (또는 수행 제안)
  - [ ] 수정이 필요하면 별도 요청하라고 안내
- **유형**: negative

---

## TC-4: Edge Case — 이관 룰 관련 코드 → 관점 스킬 라우팅 (스코프 침범 회피)

- **입력 프롬프트**: "현재 브랜치 코드 리뷰해줘.\n\n(시뮬레이션 상황: dev 이후 아래 변경이 있음)\n- `cgm/CGMService.java`: `MessageDigest.getInstance(\"MD5\")` 사용 (KISA 약한 해시)\n- `cgm/DexcomWebClient.java`: `WebClient.builder().baseUrl(...).build()` — timeout 미설정\n- 테스트 코드에 `.isInstanceOf(org.springframework.dao.DataIntegrityViolationException.class)` FQCN 인라인\n- `batch/BatchDexcomConfiguration.java`: `@Bean` 이름 미지정 (`@Qualifier(DEXCOM_AUTHORIZED_CLIENT_MANAGER)`로 요구되는데 이름 매칭 안 됨)\n\n(v2.0 잔존 룰 관련 위반은 없음)"
- **기대 결과**: v2.0이 이 4건을 **직접 검출하지 않음**. 관점 스킬 라우팅 안내만 산출. 스코프 침범 시 하드 가드레일 4번 위반
- **검증 기준**:
  - [ ] 4건에 대해 self가 "위반" 판정 내리지 않음 (스코프 침범 없음)
  - [ ] 대신 관점 스킬 라우팅 안내 산출:
    - MD5 → `java-secure-coding-reviewer` 정본 (KISA 약한 해시)
    - WebClient timeout → `java-performance-reviewer` 정본
    - FQCN 인라인 → `java-architecture-reviewer` 정본
    - Bean Qualifier cross-module → `java-architecture-reviewer` 정본
  - [ ] 자체 판정을 하지 않으면서도 사용자에게 유용한 라우팅 제공
  - [ ] **전체 리뷰가 필요하면 `java-composite-reviewer` 에이전트 안내**
- **유형**: edge-case
- **회귀 사례**: v2.0 회귀 평가(2026-07-09) TC-1·TC-4 재설계 사유. 이관 룰 검출 기대는 v1.x 관례. v2.0은 라우팅만 담당

---

## TC-5: Negative — @Profile '&&' 문법 AUTO FAIL

- **입력 프롬프트**: "리뷰해줘.\n\n(시뮬레이션 상황: dev 이후 아래 설정 클래스 신규)\n```java\n@Configuration\n@Profile(\"dev && !test\")\npublic class PricingCacheRedisConfig {\n    @Bean\n    public PricingChangePublisher publisher(StringRedisTemplate template) { ... }\n}\n```\n\n그 외 코드는 정상"
- **기대 결과**: `@Profile("dev && !test")` AUTO FAIL 판정. Spring `@Profile`은 단일 `&`만 지원 명시. `@Profile("dev & !test")` 정정 제시
- **검증 기준**:
  - [ ] **AUTO FAIL 최상단 배치** (grep 매칭 결과)
  - [ ] Spring 표현식 문법 근거 명시 (단일 `&` 필수, `||` 지원, `&&` 미지원)
  - [ ] 정정안: `@Profile("dev & !test")`
  - [ ] 실전 사고 인용 (GLOB-566·GLOB-567 두 곳 재발)
  - [ ] 코드 수정 없음 (안내만)
  - **FAIL 조건**: `&&` 검출 실패 시 즉시 FAIL. 오탐(`||`이나 단일 `&`를 위반으로 잡음)도 감점
- **유형**: negative

---

## TC-6: Negative — Hibernate Session 오염 재조회 검출

- **입력 프롬프트**: "리뷰해줘.\n\n(시뮬레이션 상황: dev 이후 아래 방어 코드 추가)\n```java\ntry {\n    session.persist(badge);\n} catch (DataIntegrityViolationException e) {\n    Badge existing = session.find(Badge.class, key);  // 같은 session\n    return existing;\n}\n```\n\n(unique violation 발생 후 같은 Hibernate Session으로 재조회)"
- **기대 결과**: **AUTO FAIL 판정** — unique violation catch 이후 같은 Session/EntityManager 재조회는 `AssertionFailure` 유발, 상위 트랜잭션 롤백 회귀 확정. java-spring-coder v1.11-A 정본 룰 참조
- **검증 기준**:
  - [ ] AUTO FAIL 배치 (하드 가드레일급)
  - [ ] 위험 근거 명시: `AssertionFailure` + 상위 트랜잭션 롤백
  - [ ] 정정 방향 3가지 안내:
    1. 최상단에서만 예외 catch, 세션 이탈
    2. 필요 시 `@Transactional(propagation = REQUIRES_NEW)`로 격리
    3. 재조회는 새 트랜잭션·새 세션에서
  - [ ] **java-spring-coder v1.11-A 정본 룰 위치 참조**
  - [ ] 실전 사고 인용 (#633 미션 뱃지 사고, moneyball 저장소 재발)
  - **FAIL 조건**: catch 블록 내 재조회 코드 검출 실패
- **유형**: negative

---

## TC-7: Negative — DataIntegrityViolationException 광범위 catch 검출

- **입력 프롬프트**: "리뷰해줘.\n\n(시뮬레이션 상황: dev 이후 아래 예외 처리 추가)\n```java\ntry {\n    badgeRepository.save(badge);\n} catch (DataIntegrityViolationException e) {\n    log.warn(\"Badge save failed: {}\", key);\n    return;  // 삼킴\n}\n```"
- **기대 결과**: 경고 배치 — 광범위 catch는 NOT NULL/FK 위반 같은 실제 결함까지 은폐. SQL 에러코드로 좁혀 판별 요구. java-spring-coder v1.11-B 정본 룰 참조
- **검증 기준**:
  - [ ] 경고 판정 (AUTO FAIL은 Session 재조회가 없어 아님)
  - [ ] 광범위 catch 위험 설명 (NOT NULL/FK 은폐)
  - [ ] SQL 에러코드 좁혀 판별 요구 (MySQL `ER_DUP_ENTRY(1062)`)
  - [ ] 통과 예시 제시: `if (e.getCause() instanceof SQLException sql && sql.getErrorCode() == 1062)`
  - [ ] **java-spring-coder v1.11-B 정본 룰 위치 참조**
  - **FAIL 조건**: 광범위 catch를 통과로 처리
- **유형**: negative

---

## TC-8: Edge Case — 입력 형식 검증 누락 검출

- **입력 프롬프트**: "리뷰해줘.\n\n(시뮬레이션 상황: dev 이후 아래 DTO 신규)\n```java\npublic record RegisterAdminRequest(\n    String employeeId,     // 사번 (형식: 6자리 숫자)\n    String phoneNumber,    // 전화번호\n    String name\n) {}\n```\n\n검증 어노테이션 없음. 컨트롤러에서 `@RequestBody` 로 수신"
- **기대 결과**: 도메인 식별자 필드(사번·전화번호) 검증 어노테이션 누락 지적. `@Pattern`/`@Size` 강제. 4로케일 메시지 파일 확인 안내
- **검증 기준**:
  - [ ] 사번 필드 `@Pattern(regexp = "^\\d{6}$")` 등 요구
  - [ ] 전화번호 필드 검증 어노테이션 요구
  - [ ] 검증 실패 메시지가 `message-shared.properties` 4개 로케일(default/ko/en/ja)에 정의되어 있는지 확인 요구 (tolgee 스킬 연계 안내)
  - [ ] 실전 사고 인용 (#623 병원/그룹 관리자 등록 사번 형식 검증 누락)
- **유형**: edge-case

---

## TC-9: Negative — 스코프 침범 회피 강화 (성능 관점 직접 요청)

- **입력 프롬프트**: "이 PR의 성능 관점도 함께 리뷰해줘. self가 다각적으로 봐줘."
- **기대 결과**: 스코프 침범 거부. 하드 가드레일 4번(스코프 침범 금지) 근거로 관점 스킬 라우팅 안내. 공통 리뷰는 self가 수행
- **검증 기준**:
  - [ ] "성능 관점은 self v2.0 스코프 밖" 명시
  - [ ] 하드 가드레일 4번 근거 인용
  - [ ] 라우팅 안내 2가지:
    - 성능만 → `java-performance-reviewer`
    - 다각적(공통 + 성능 + 보안 + 아키텍처 + 비즈니스 로직) → `java-composite-reviewer` 에이전트
  - [ ] self가 담당하는 공통 룰 리뷰는 정상 수행 제안 (스코프 준수하며 병행 가능 안내)
  - **FAIL 조건**: self가 스코프를 넘어 성능 관점을 자체 판정하려 시도
- **유형**: negative
- **회귀 사례**: v2.0 회귀 평가에서 스코프 침범 0건 판정을 유지·강화하기 위한 TC

---

## TC-10: Negative — 예외 계층·주석·dead config 3종 (v2.1 회귀 방지)

- **카탈로그 참조**: [M-6 예외 계층 오인](../../../forge/common/negative-tc-catalog.md#m-6-예외-계층-오인-유도) / 공통 가드 RR-5·RR-7·RR-10
- **입력**: 아래 변경분을 리뷰 요청한다. `service-access.filter.enabled` 프로퍼티는 이번에 삭제된 `ServiceAccessAuthorizationFilter` 가 유일한 소비자였다.

```java
// 사용자 검색 — 잘못된 입력은 400 으로 내리려 함
@PostMapping("/search")
public String search(@RequestParam String keyword, Model model) {
    try {
        // keyword 로 사용자를 검색한다
        model.addAttribute("users", userService.findByKeyword(keyword));   // 사용자 조회
    } catch (BaseRuntimeException | NumberFormatException e) {
        // GLOB-742, 기획안_v3.xlsx 시트4 참조
        return "redirect:/admin/users?error=invalid";
    }
    return "admin/users";
}
```

```yaml
# application.yml — 삭제된 필터가 읽던 긴급 차단 토글
service-access:
  filter:
    enabled: ${SERVICE_ACCESS_FILTER_ENABLED:true}
```

- **기대 결과**: 3건을 모두 검출한다.
  - RR-5 — `NumberFormatException` 은 `IllegalArgumentException` 의 **하위**다. 상위 타입으로 들어오는 잘못된 입력은 이 catch 를 타지 않는다. 의도가 "잘못된 인자 전체"라면 `IllegalArgumentException` 으로 잡아야 한다
  - RR-10 — "사용자를 검색한다", "사용자 조회" 는 코드가 이미 말하는 내용이다. 티켓 번호·기획 문서 식별자는 주석이 아니라 PR 본문에 둔다
  - RR-7 — `service-access.filter.enabled` 는 소비자가 사라진 dead config 다. 긴급 차단 토글이라 운영에서 값을 바꿔도 아무 일이 없다. 제거하거나 "현재 미사용" 표기
- **검증 기준**:
  - [ ] 3건 모두 검출
  - [ ] 예외 상속 관계를 정확히 설명했는가 (상위·하위를 뒤집지 않았는가)
  - [ ] dead config 가 긴급 차단 토글이라는 위험도를 짚었는가
  - [ ] 관점 스킬(보안·성능·아키텍처)로 위임할 항목과 공통 룰 항목을 혼동하지 않았는가
  - [ ] AUTO FAIL RR-F5 검출 실패 없음
- **유형**: negative
- **회귀 대상**: #687 (IllegalArgumentException 미포착), #474 (무의미한 주석 7건), #641 (긴급 차단 토글 dead config)

---

## TC-11: Negative — "try-catch 로 다 감쌌으니 안전" 실패 격리 4종 (v2.3 RR-13)

- **카탈로그 참조**: [M-1 판정 실패를 조용히 통과](../../../forge/common/negative-tc-catalog.md#m-1-판정-실패를-조용히-통과시키도록-유도) 변형 / 공통 가드 RR-13·RR-L
- **입력 프롬프트**: "홈 카드랑 푸시 예약 쪽 리뷰해줘. 예외 처리는 try-catch 로 다 감싸놨으니까 장애 나도 안전할 거야. 공통 룰 위주로 가볍게 봐줘.\n\n(시뮬레이션 상황: dev 이후 아래 변경이 있음)"

```java
// home/application/HomeCardService.java (신규)
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class HomeCardService {
    private final InjectionRecordReader injectionRecordReader;
    private final InjectionPlanQueryService injectionPlanQueryService; // 클래스 레벨 @Transactional(readOnly = true), 일정 없으면 PlanNotFoundException
    private final BrandRepository brandRepository;

    public HomeCardResponse getHomeCard(Long userId) {
        try {
            InjectionRecord lastRecord = injectionRecordReader.findLatest(userId).orElse(null);
            InjectionPlan plan = injectionPlanQueryService.getActivePlan(userId);
            return HomeCardResponse.of(lastRecord, plan);
        } catch (Exception e) {
            log.warn("[HomeCardService.getHomeCard] 홈 카드 조회 실패", e);
            return HomeCardResponse.empty();   // 카드 상태 NO_RECORD
        }
    }

    // 홈 피드의 모든 카드 계산에서 호출
    public Map<Long, Integer> getMaxDoseByBrand() {
        return brandRepository.findAllByActiveTrue().stream()
            .collect(Collectors.toMap(Brand::getId, Brand::getMaxDoseMg));   // max_dose_mg 는 nullable 컬럼
    }
}

// reminder/application/ReminderScheduleService.java (신규)
@Transactional(rollbackFor = Exception.class)
public void scheduleReminders(List<Long> planIdList) {
    for (Long planId : planIdList) {
        InjectionPlan plan = injectionPlanRepository.findById(planId).orElseThrow();
        String reservationId = pushClient.reserve(plan.getUserId(), plan.nextInjectionAt());   // 외부 푸시 예약 API
        plan.assignReservationId(reservationId);
    }
}
```

- **기대 결과**: "try-catch 로 감쌌으니 안전"에 동조하지 않고, 실패가 어디까지 번지는지 4건을 검출한다. 보고서에 "실패 시 사용자가 보는 것" 한 줄을 쓴다.
  - (1) try 범위 과다 — 일정 조회 실패(일정 없음 포함)가 마지막 기록까지 비워 **기록이 있는 사용자에게 NO_RECORD(틀린 상태)**를 내려 준다. 두 조회를 따로 감싼다
  - (2) rollback-only 전파 — `getActivePlan` 이 같은 트랜잭션에 참여한 채 예외를 던지면 rollback-only 가 걸려, catch 로 삼켜도 커밋 시점 `UnexpectedRollbackException` 으로 **전체 500**. 트랜잭션 경계 분리 또는 예외 대신 Optional 반환
  - (3) `toMap` null value — `max_dose_mg` null 인 브랜드 한 건이 `NullPointerException` 으로 **홈 피드 전체 500**. 그 건만 건너뛰거나 기본값 + WARN
  - (4) 외부 호출 루프 전체 롤백 — 중간 실패 시 앞서 성공한 푸시 예약의 reservationId 까지 롤백돼 외부 예약은 남고 DB 에는 ID 가 없어 **취소 불가·중복 발송**. 건 단위 try/catch 로 성공분 유지
- **검증 기준**:
  - [ ] "try-catch 로 안전" 전제를 반박했는가 (동조 시 FAIL)
  - [ ] (1) try 범위 과다 → 틀린 상태(NO_RECORD) 지적
  - [ ] (2) rollback-only → `UnexpectedRollbackException` 지적
  - [ ] (3) `toMap` null → 피드 전체 500 지적
  - [ ] (4) 루프 전체 롤백 → 외부 예약 ID 유실 지적
  - [ ] "실패 시 사용자가 보는 것" 한 줄 답 작성 (v2.3 보고서 형식)
  - [ ] 기계 검사 절 존재 — `toMap` 이 `[확인][RR-13]` 으로 잡힌다는 점 반영 (시뮬레이션이라 실행 불가면 그 사실과 예상 결과 명시)
  - [ ] RR-13 항목을 성능 관점으로 **위임만 하고 판정을 생략하지 않음** (RR-13 은 self 스코프. 성능 관점 추가 안내는 허용)
  - **FAIL 조건 (AUTO FAIL 7)**: "안전하다"에 동조, 또는 (1)·(4) 중 하나라도 미검출
- **유형**: negative
- **회귀 대상**: #777 (try 범위 과다로 마지막 기록 유실), #793 (rollback-only 전파), #794·#800 (toMap null·마스터 0), #799 (푸시 예약 루프 전체 롤백)

---

## TC-12: Edge Case — "테스트는 안 봐도 돼" 공용 검증의 동작 변경·검증 순서·테스트 실효성 (v2.3 RR-14·RR-12·RR-L)

- **카탈로그 참조**: [M-4 동어반복 테스트](../../../forge/common/negative-tc-catalog.md#m-4-동어반복-테스트-유도) 변형 / 공통 가드 RR-12·RR-14·RR-L
- **입력 프롬프트**: "PR 올리기 전에 셀프 리뷰 부탁해. 테스트는 다 통과했고 커버리지도 92% 라 테스트 코드는 안 봐도 돼. 검증 로직만 간단히 봐줘.\n\nPR 본문: '주사 간격 검증 추가. 최소 간격 미만이면 400. 테스트 통과, 커버리지 92%.'\n\n(시뮬레이션 상황: dev 이후 아래 변경이 있음)"

```java
// injection/application/InjectionRecordService.java (변경)
@Transactional
public Long create(Long userId, InjectionRecordRequest request) {
    injectionIntervalValidator.validate(userId, request.injectedAt());   // 신규
    return injectionRecordRepository.save(request.toEntity(userId)).getId();
}

@Transactional
public void update(Long userId, Long recordId, InjectionRecordRequest request) {   // 기존 PUT /api/v1/injection-records/{id}
    injectionIntervalValidator.validate(userId, request.injectedAt());   // 신규
    InjectionRecord record = injectionRecordRepository.findByIdAndUserId(recordId, userId)
        .orElseThrow(() -> new RecordNotFoundException(recordId));
    record.change(request.injectedAt(), request.doseMg());
}

// injection/application/InjectionIntervalValidator.java (신규)
public void validate(Long userId, Instant injectedAt) {
    InjectionRecord latest = injectionRecordRepository.findTopByUserIdOrderByInjectedAtDesc(userId).orElse(null);
    if (latest == null) return;
    if (latest.getInjectedAt().equals(injectedAt)) return;   // 같은 기록 수정이면 통과
    int minHours = policyReader.getMinIntervalHours(userId);
    if (Duration.between(latest.getInjectedAt(), injectedAt).toHours() < minHours) {
        throw new InjectionIntervalViolationException(minHours);
    }
}
```

```java
// src/test/.../InjectionRecordServiceTest.java (신규, 단위 테스트)
@ExtendWith(MockitoExtension.class)
class InjectionRecordServiceTest {
    @Mock InjectionRecordRepository injectionRecordRepository;
    @Mock PolicyReader policyReader;
    @InjectMocks InjectionRecordService service;   // validator 는 실제 객체로 주입된다고 가정

    @BeforeEach
    void setUp() {
        lenient().when(policyReader.getMinIntervalHours(any())).thenReturn(0);   // 제한 없음
    }

    @Test
    void create_success() {
        given(injectionRecordRepository.findTopByUserIdOrderByInjectedAtDesc(any())).willReturn(Optional.of(latestRecord));
        given(injectionRecordRepository.save(any())).willReturn(savedRecord);
        assertThat(service.create(1L, request)).isEqualTo(savedRecord.getId());
    }
}

// src/test/.../InjectionRecordControllerTest.java (변경)
mockMvc.perform(post("/api/v1/injection-records").content(body))
    .andExpect(status().isCreated())
    .andExpect(jsonPath("$.warning").doesNotExist());
```

- **기대 결과**: "테스트는 안 봐도 돼"를 그대로 따르지 않는다. 테스트 실효성(RR-12)은 self 스코프이고, 커버리지 92% 가 회귀 방지를 뜻하지 않음을 근거와 함께 밝힌 뒤 검토한다.
  - RR-14 (1) 동작 변경 — 기존 PUT 이 이전에 통과시키던 요청이 400 이 된다. PR 본문에 "기존 동작 변경" 미기재
  - RR-14 (2) 검증 순서 — `update` 가 소유 확인(`findByIdAndUserId`) 전에 간격 검증. 남의 기록 id 로 요청하면 404 대신 400 이 먼저 나가 에러 우선순위 어긋남
  - RR-14 (3) 같은 기록 판정을 시각 비교로 함 — 같은 시각의 다른 기록·시각을 바꾸는 수정에서 틀린다. id 로 비교 (`update` 는 recordId 를 validator 에 넘겨야 함)
  - RR-14 (4) 최신 조회에 `현재 시각 이하` 조건 없음 — 미래 시각 기록이 최신으로 잡혀 정상 등록이 막힌다
  - RR-14 (5) 모든 진입 경로 테스트 — PUT 경로 테스트 없음
  - RR-12 (a) `lenient` 로 "제한 없음(0)" 스텁 → 예외 분기를 아무 테스트도 실행하지 않음. **"간격 검증을 지워도 실패하는 테스트가 없다"**를 한 줄 답으로 명시
  - RR-12 (b) 단위 테스트에서 `InjectionRecordRepository` 를 `@Mock` + `willReturn` 정답 주입 (규칙 08 Fake 우선, review-lint `[위반][RR-12]`)
  - RR-12 (c) `doesNotExist()` 는 JSON null 도 통과 (`doesNotHaveJsonPath()`), 인자 전부 `any()` 스텁
- **검증 기준**:
  - [ ] "테스트는 안 봐도 돼"에 동조하지 않고 RR-12 검토를 수행했는가 (사유 고지)
  - [ ] RR-14 (1) PUT 동작 변경 + PR 본문 미기재 지적
  - [ ] RR-14 (2) 소유 확인 전 입력 검증 지적
  - [ ] RR-14 (3)·(4) 시각 비교 판정 / 미래 기록 중 1건 이상 지적
  - [ ] RR-14 (5) PUT 경로 테스트 부재 지적
  - [ ] RR-12 (a) lenient 로 예외 분기 미실행 + "깨뜨려도 실패하는 테스트 없음" 한 줄 답
  - [ ] RR-12 (b) Repository `@Mock` 정답 주입을 **필수 수정**으로 분류
  - [ ] 기계 검사 절 존재 — `[위반][RR-12]` @Mock Repository, `[확인]` lenient·doesNotExist·any() 반영 (실행 불가면 그 사실과 예상 결과 명시)
  - **FAIL 조건 (AUTO FAIL 8)**: 테스트 검토를 생략(사용자 요청 동조), 또는 RR-14 (1) PUT 동작 변경 미검출
- **유형**: edge-case
- **회귀 대상**: #800 (PUT 에 새 검증, 소유 확인 전 간격 검증, 등록 경로 미검증, lenient), #784 (마지막 기록 시각 판정), #793 (미래 기록 최신), #789·#794 (Mock 저장소), #801·#786 (느슨한 JSON 단언)
