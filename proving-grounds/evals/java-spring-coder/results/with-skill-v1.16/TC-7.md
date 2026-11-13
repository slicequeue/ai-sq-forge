# TC-7 with-skill 응답 (v1.16)

## 결론부터

"중복이면 조용히 넘어가고 기존 뱃지를 돌려준다"는 동작은 그대로 구현합니다. 다만 제시하신 4줄을 그대로 넣으면 사고 이력이 있는 패턴 3가지에 걸립니다. 같은 동작을 유지하면서 아래 구조로 바꿉니다. 코드는 길어지지만 동작 요구는 동일합니다.

| # | 제시하신 코드의 문제 | 근거 | 영향 |
|---|----------------------|------|------|
| 1 | catch 이후 `existing` 을 같은 세션에서 조회하면 Session 이 이미 오염된 상태입니다 | v1.11-A, 2026-07-08 #633 | `AssertionFailure`, 또는 상위 트랜잭션이 rollback-only 가 되어 `UnexpectedRollbackException`. 같은 트랜잭션의 미션 달성 기록까지 롤백됩니다 |
| 2 | `DataIntegrityViolationException` 전체를 삼킵니다 | v1.11-B | unique 위반뿐 아니라 NOT NULL·FK 위반 같은 실제 결함도 "이미 존재하는 뱃지"로 은폐됩니다 |
| 3 | 뱃지 발급이 상위 트랜잭션에 참여한 채로 catch 합니다 | v1.11-C | 1번의 근본 원인입니다. 격리(`REQUIRES_NEW`)가 없으면 catch 해도 이미 rollback-only 입니다 |
| 4 | 예상된 중복에 `log.warn("...", e)` 로 스택트레이스를 찍습니다 | 로깅 규칙, v1.10 예외 로깅 | 정상 흐름이 경보 노이즈가 됩니다. 접두사 `[ClassName.methodName]` 도 빠져 있습니다 |

요청 의도(조용히 통과)는 막지 않습니다. 판별을 좁히고, 트랜잭션을 갈라서, 같은 결과를 안전하게 내는 것이 변경의 전부입니다.

---

## Phase 0 시뮬레이션 (확인 vs 가정)

실제 저장소가 없으므로 아래 명령을 실행했다고 가정하고 결과를 가정치로 적습니다. 모두 **가정**이며, 실제 실행 시 결과가 다르면 설계를 재평가합니다.

```bash
# 1. 작업 계획서 탐색
ls docs/plans docs/tdd 2>/dev/null | grep -i badge
#   가정 결과: 없음 -> 모드 B (단순 구현)

# 2. 규칙 로드 (스킬의 .claude/rules/ 에 해당)
#    01 아키텍처, 04 리포지토리, 06 예외, 07 일반, 08 테스트, 09 가드레일, 19 경계 Read

# 3. 기존 뱃지 도메인 패턴 확인
find pghd -path '*badge*' -name '*.java'
#   가정 결과: BadgeEntity, BadgeRepository, BadgeJpaEntity, BadgeJpaRepository,
#             BadgeRepositoryImpl, BadgeIssueService (현재 try/catch 없는 단순 save)

# 4. 기존 중복 판별 헬퍼 전수 검색 (DW-6: 중복 신설 방지)
grep -rn "DataIntegrityViolationException\|getErrorCode() == 1062\|isDuplicateKey" src/main
#   가정 결과: 0건 -> 신규 헬퍼를 만듭니다. 1건 이상이면 재사용합니다

# 5. unique 제약 존재 확인 (핵심 전제)
grep -rni "badge" src/main/resources/db/migration | grep -i "unique\|uk_"
#   가정 결과: uk_badge_user_id_badge_type (user_id, badge_type) 존재
#   이 전제가 깨지면 중단합니다 (아래 "중단 조건" 참조)

# 6. 호출처 grep (v1.16 Phase 0-9)
grep -rn "badgeIssueService\|BadgeIssueService" src/main
#   가정 결과: MissionAchieveService.achieveMission() 한 곳.
#             @Transactional 안에서 미션 달성 기록 저장 후 뱃지 발급을 호출합니다 (#633 과 동일 구조)

# 7. JDK / admin 여부
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
#   admin 모듈 아님 -> 01~12 규칙. 타 저장소 이식 아님

# 8. 대상 파일 미커밋 변경 확인 (DW-1)
git status --short pghd/badge
#   가정 결과: 깨끗함. 변경이 있으면 중단하고 사용자에게 알립니다
```

### 작성 전 질문 5개

1. **실패하면 사용자는 무엇을 보는가?** 중복이면 기존 뱃지를 정상 응답으로 받습니다. 중복이 아닌 DB 결함은 예외로 전파해 500 으로 드러냅니다. 결함을 "이미 있음"으로 위장하지 않습니다.
2. **외부 호출 후 DB 저장 실패?** 이 작업에는 외부 호출이 없습니다. 해당 없음.
3. **마스터 데이터 null/0/누락?** `badgeType`·`userId` 는 InDto/Entity 에서 `requireNonNull` 로 즉시 실패시킵니다.
4. **기존 경로 동작 변경?** 있습니다. 지금까지 중복 발급은 예외(500 또는 롤백)였는데 이제 기존 뱃지를 반환합니다. PR 본문 "기존 동작 변경" 항목에 적습니다 (RR-14).
5. **분기를 깨뜨리면 실패하는 테스트가 모든 진입 경로에 있는가?** 아래 테스트 3종이 각각 격리 제거, 판별 좁히기 제거, 재조회 위치 변경 시 실패하도록 설계했습니다.

### 확인된 것 vs 가정한 것

| 구분 | 내용 | 재평가 트리거 |
|------|------|---------------|
| 확인(스킬·규칙 문서 근거) | 세션 오염·광범위 catch·격리 필요성(v1.11-A/B/C), 4-Tier 의존 방향, 예외는 Application 배치 | - |
| 가정 | `(user_id, badge_type)` UNIQUE 존재 | grep 5번 결과가 없으면 중단 |
| 가정 | PK 가 IDENTITY (insert 가 save 시점에 발생) | IDENTITY 가 아니어도 flush 는 격리 트랜잭션 커밋 시점에 일어나므로 catch 위치는 동일하게 유효 |
| 가정 | 호출처가 상위 `@Transactional` 안에서 호출 | 아니라면 격리는 중복 방어일 뿐 해롭지 않음 |
| 가정 | MySQL 8 (에러코드 1062 = `ER_DUP_ENTRY`), 기본 격리 REPEATABLE READ | DB 가 다르면 SQLState/에러코드 재확인 |
| 가정 | 중복 시 호출자가 "새로 발급됐는지"를 구분할 필요 없음 | 알림 발송 등이 새 발급에만 걸려야 한다면 OutDto 필드 추가 협의 (아래 "열린 질문") |

### 중단 조건 (SC-3, SC-4)

grep 5번에서 UNIQUE 제약이 **없다면** 여기서 멈추고 보고합니다. 제약이 없으면 `DataIntegrityViolationException` 자체가 발생하지 않아 try/catch 는 죽은 코드가 되고, 중복 뱃지가 조용히 쌓입니다. 마이그레이션(UNIQUE 추가)은 테이블 구조 변경이므로 승인 없이 넣지 않습니다. 그 경우 선택지는 (a) UNIQUE 마이그레이션 추가(기존 중복 데이터 정리 선행), (b) 조회 후 저장(경합 시 중복 가능), (c) 현 상태 유지입니다. 이하 구현은 UNIQUE 가 있다는 가정에서 진행합니다.

---

## 설계

핵심은 "예외를 잡는 위치"와 "예외가 난 트랜잭션"을 분리하는 것입니다.

```
MissionAchieveService (@Transactional, 상위 트랜잭션)
  -> BadgeIssueService.issueBadge()            // 트랜잭션 없음. 여기서 catch 합니다
       -> BadgeIssueTransactionService          // REQUIRES_NEW. 저장만 하고 예외는 전파
            .createBadgeInNewTransaction()
       catch: 1062 만 중복으로 판별, 그 외 rethrow
       -> BadgeIssueTransactionService
            .getBadgeInNewTransactionOrElseNull()   // 새 트랜잭션의 새 세션·새 스냅샷으로 재조회
```

- 격리 트랜잭션이 실패해도 롤백되는 것은 격리된 쪽뿐이고, 상위 세션과 상위 트랜잭션은 오염되지 않습니다.
- 같은 클래스 내부 메서드 호출은 프록시를 거치지 않아 `@Transactional` 이 무시됩니다. 그래서 `BadgeIssueTransactionService` 를 별도 Bean 으로 분리합니다.
- 재조회도 새 트랜잭션에서 합니다. 상위 트랜잭션이 MySQL REPEATABLE READ 스냅샷을 이미 잡았다면, 다른 트랜잭션이 방금 커밋한 행이 상위 트랜잭션에서는 보이지 않을 수 있기 때문입니다.
- 계층: DB 에러코드 판별은 Spring 예외를 다루므로 Application 의 package-private 헬퍼로 둡니다. Domain 은 Spring 을 참조하지 않고, Infrastructure 는 Application 예외를 던질 수 없어서(Infra -> Domain 단방향) 이 위치가 의존 방향을 지킵니다. 이 배치 판단은 가정이며, 기존 프로젝트에 유사 헬퍼가 있으면 그 위치를 따릅니다.

---

## 구현 코드 (시뮬레이션, 파일에 쓰지 않음)

파일 생성 순서는 Domain -> Infra -> Application -> Test Double -> Test 입니다. Domain·Infra 는 기존 코드를 가정하고 변경이 없습니다. 아래 인터페이스가 이미 있다고 가정합니다.

```java
// pghd/badge/domain/BadgeRepository.java (기존, 변경 없음)
public interface BadgeRepository {
    Optional<BadgeEntity> findByUserIdAndBadgeType(long userId, BadgeType badgeType);
    BadgeEntity save(BadgeEntity badgeEntity);
}
```

### Application

```java
// pghd/badge/application/BadgeIssueInDto.java
public record BadgeIssueInDto(long userId, BadgeType badgeType) {
    public static BadgeIssueInDto of(long userId, BadgeType badgeType) {
        return new BadgeIssueInDto(userId, Objects.requireNonNull(badgeType, "badgeType must not be null"));
    }
}

// pghd/badge/application/BadgeIssueOutDto.java
public record BadgeIssueOutDto(long badgeId, BadgeType badgeType, Instant issuedAt) {
    public static BadgeIssueOutDto from(BadgeEntity badgeEntity) {
        return new BadgeIssueOutDto(
                badgeEntity.getId(), badgeEntity.getBadgeType(), badgeEntity.getIssuedAt());
    }
}
```

```java
// pghd/badge/application/BadgeIssueTransactionService.java
@Service
@RequiredArgsConstructor
public class BadgeIssueTransactionService {

    private final BadgeRepository badgeRepository;

    // 상위 트랜잭션의 롤백·rollback-only 와 무관하게 커밋되거나 롤백되어야 하므로 REQUIRES_NEW 를 사용합니다.
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public BadgeEntity createBadgeInNewTransaction(BadgeEntity badgeEntity) {
        return badgeRepository.save(badgeEntity);
    }

    // 상위 스냅샷(REPEATABLE READ)에 보이지 않는 방금 커밋된 행을 읽기 위해 새 트랜잭션에서 조회합니다.
    @Transactional(propagation = Propagation.REQUIRES_NEW, readOnly = true)
    public BadgeEntity getBadgeInNewTransactionOrElseNull(long userId, BadgeType badgeType) {
        return badgeRepository.findByUserIdAndBadgeType(userId, badgeType).orElse(null);
    }
}
```

```java
// pghd/badge/application/DuplicateKeyViolationDetector.java
final class DuplicateKeyViolationDetector {

    private static final int MYSQL_ER_DUP_ENTRY = 1062;

    private DuplicateKeyViolationDetector() {
    }

    // NOT NULL·FK 위반 같은 실제 결함까지 중복으로 오판하지 않도록 에러코드로 좁혀 판별합니다.
    static boolean isDuplicateKey(DataIntegrityViolationException dataIntegrityViolationException) {
        Throwable mostSpecificCause = dataIntegrityViolationException.getMostSpecificCause();
        if (mostSpecificCause instanceof SQLIntegrityConstraintViolationException sqlException) {
            return sqlException.getErrorCode() == MYSQL_ER_DUP_ENTRY;
        }
        return false;
    }
}
```

```java
// pghd/badge/application/BadgeIssueService.java
@Service
@RequiredArgsConstructor
@Log4j2
public class BadgeIssueService {

    private final BadgeIssueTransactionService badgeIssueTransactionService;

    // 이 메서드에는 @Transactional 을 붙이지 않습니다. 예외를 잡는 위치가 격리 트랜잭션 밖이어야 합니다.
    public BadgeIssueOutDto issueBadge(BadgeIssueInDto badgeIssueInDto) {
        Instant currentAt = Instant.now();
        BadgeEntity badgeEntity = BadgeEntity.of(
                badgeIssueInDto.userId(), badgeIssueInDto.badgeType(), currentAt);

        try {
            BadgeEntity savedBadgeEntity = badgeIssueTransactionService.createBadgeInNewTransaction(badgeEntity);
            return BadgeIssueOutDto.from(savedBadgeEntity);
        } catch (DataIntegrityViolationException dataIntegrityViolationException) {
            if (!DuplicateKeyViolationDetector.isDuplicateKey(dataIntegrityViolationException)) {
                throw dataIntegrityViolationException;
            }
            // 예상된 중복이라 스택트레이스 없이 INFO 로 남깁니다. userId 는 MDC 에 있어 본문에 넣지 않습니다.
            log.info("[BadgeIssueService.issueBadge] 이미 발급된 뱃지라 기존 뱃지를 반환합니다. badgeType={}",
                    badgeIssueInDto.badgeType());
            return getExistingBadgeOutDto(badgeIssueInDto, dataIntegrityViolationException);
        }
    }

    private BadgeIssueOutDto getExistingBadgeOutDto(
            BadgeIssueInDto badgeIssueInDto, DataIntegrityViolationException dataIntegrityViolationException) {
        BadgeEntity existingBadgeEntity = badgeIssueTransactionService.getBadgeInNewTransactionOrElseNull(
                badgeIssueInDto.userId(), badgeIssueInDto.badgeType());
        if (existingBadgeEntity == null) {
            // 중복 키였는데 조회되지 않는 경우는 동시 삭제 등 비정상 상황이라 조용히 넘기지 않습니다.
            throw dataIntegrityViolationException;
        }
        return BadgeIssueOutDto.from(existingBadgeEntity);
    }
}
```

설계 메모:

- 변수 규칙: 시각은 `currentAt`, 엔티티 변수는 `badgeEntity`, 예외 변수는 타입명, `var` 없음.
- 메서드 네이밍: `get*OrElseNull` 패턴을 따르고 금지 단어(`execute/process/handle/check`)는 쓰지 않았습니다.
- Lombok: `@RequiredArgsConstructor`, `@Log4j2` 만 사용. FQCN 없음(아래 import 를 파일 상단에 선언).
- 상위 호출처(`MissionAchieveService`)는 수정하지 않습니다. 호출 시그니처가 그대로라서 범위 밖 변경이 없습니다 (SC-1).

### Test Double

```java
// test: pghd/badge/application/FakeBadgeRepository.java
public class FakeBadgeRepository implements BadgeRepository {

    private final Map<Long, BadgeEntity> store = new HashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1L);
    private Integer violationErrorCode;

    // 다음 save 에서 지정한 MySQL 에러코드로 무결성 위반을 던지도록 시나리오를 제어합니다.
    public void willViolateWith(int errorCode) {
        this.violationErrorCode = errorCode;
    }

    @Override
    public Optional<BadgeEntity> findByUserIdAndBadgeType(long userId, BadgeType badgeType) {
        return store.values().stream()
                .filter(badgeEntity -> badgeEntity.getUserId() == userId
                        && badgeEntity.getBadgeType() == badgeType)
                .findFirst();
    }

    @Override
    public BadgeEntity save(BadgeEntity badgeEntity) {
        if (violationErrorCode != null) {
            throw violation(violationErrorCode);
        }
        boolean duplicated = findByUserIdAndBadgeType(badgeEntity.getUserId(), badgeEntity.getBadgeType()).isPresent();
        if (duplicated) {
            throw violation(1062);
        }
        long id = idGenerator.getAndIncrement();
        BadgeEntity savedBadgeEntity = new BadgeEntity(
                id, badgeEntity.getUserId(), badgeEntity.getBadgeType(), badgeEntity.getIssuedAt());
        store.put(id, savedBadgeEntity);
        return savedBadgeEntity;
    }

    public int count() {
        return store.size();
    }

    private DataIntegrityViolationException violation(int errorCode) {
        return new DataIntegrityViolationException(
                "constraint violation",
                new SQLIntegrityConstraintViolationException("constraint violation", "23000", errorCode));
    }
}
```

UNIQUE 위반은 Fake 가 상태(저장된 행)에서 스스로 판단해 던지고, 에러코드 시나리오만 `willViolateWith` 로 제어합니다. 정답을 주입하는 `setResult` 방식이 아닙니다.

### 테스트 1. 판별 헬퍼 (순수 JUnit)

```java
class DuplicateKeyViolationDetectorTest {

    @Test
    @DisplayName("MySQL 1062 에러코드면 중복 키 위반으로 판별한다")
    void isDuplicateKey_errorCode1062_returnsTrue() {
        // Given
        DataIntegrityViolationException exception = violationOf(1062);

        // When
        boolean duplicateKey = DuplicateKeyViolationDetector.isDuplicateKey(exception);

        // Then
        assertThat(duplicateKey).isTrue();
    }

    @Test
    @DisplayName("FK 위반(1452)은 중복 키로 판별하지 않는다")
    void isDuplicateKey_foreignKeyViolation1452_returnsFalse() {
        assertThat(DuplicateKeyViolationDetector.isDuplicateKey(violationOf(1452))).isFalse();
    }

    @Test
    @DisplayName("NOT NULL 위반(1048)은 중복 키로 판별하지 않는다")
    void isDuplicateKey_notNullViolation1048_returnsFalse() {
        assertThat(DuplicateKeyViolationDetector.isDuplicateKey(violationOf(1048))).isFalse();
    }

    @Test
    @DisplayName("SQL 예외가 원인이 아니면 중복 키로 판별하지 않는다")
    void isDuplicateKey_noSqlCause_returnsFalse() {
        assertThat(DuplicateKeyViolationDetector.isDuplicateKey(
                new DataIntegrityViolationException("no cause"))).isFalse();
    }

    private DataIntegrityViolationException violationOf(int errorCode) {
        return new DataIntegrityViolationException(
                "violation", new SQLIntegrityConstraintViolationException("violation", "23000", errorCode));
    }
}
```

### 테스트 2. 서비스 분기 (Fake, Spring 없음)

```java
class BadgeIssueServiceTest {

    private FakeBadgeRepository fakeBadgeRepository;
    private BadgeIssueService badgeIssueService;

    @BeforeEach
    void setUp() {
        fakeBadgeRepository = new FakeBadgeRepository();
        badgeIssueService = new BadgeIssueService(new BadgeIssueTransactionService(fakeBadgeRepository));
    }

    @Test
    @DisplayName("처음 발급하면 새 뱃지가 저장되고 발급 결과가 반환된다")
    void issueBadge_firstTime_savesAndReturnsBadge() {
        // Given
        BadgeIssueInDto badgeIssueInDto = BadgeIssueInDto.of(1L, BadgeType.FIRST_MISSION);

        // When
        BadgeIssueOutDto badgeIssueOutDto = badgeIssueService.issueBadge(badgeIssueInDto);

        // Then
        assertThat(badgeIssueOutDto.badgeType()).isEqualTo(BadgeType.FIRST_MISSION);
        assertThat(fakeBadgeRepository.count()).isOne();
    }

    @Test
    @DisplayName("이미 발급된 뱃지를 다시 발급하면 예외 없이 처음 발급된 뱃지가 반환되고 행이 늘지 않는다")
    void issueBadge_duplicate_returnsFirstBadgeWithoutNewRow() {
        // Given
        BadgeIssueInDto badgeIssueInDto = BadgeIssueInDto.of(1L, BadgeType.FIRST_MISSION);
        BadgeIssueOutDto firstBadgeIssueOutDto = badgeIssueService.issueBadge(badgeIssueInDto);

        // When
        BadgeIssueOutDto duplicatedBadgeIssueOutDto = badgeIssueService.issueBadge(badgeIssueInDto);

        // Then
        assertThat(duplicatedBadgeIssueOutDto.badgeId()).isEqualTo(firstBadgeIssueOutDto.badgeId());
        assertThat(duplicatedBadgeIssueOutDto.issuedAt()).isEqualTo(firstBadgeIssueOutDto.issuedAt());
        assertThat(fakeBadgeRepository.count()).isOne();
    }

    @Test
    @DisplayName("다른 사용자의 같은 종류 뱃지는 중복이 아니므로 각각 발급된다")
    void issueBadge_differentUser_issuesSeparately() {
        // Given
        badgeIssueService.issueBadge(BadgeIssueInDto.of(1L, BadgeType.FIRST_MISSION));

        // When
        badgeIssueService.issueBadge(BadgeIssueInDto.of(2L, BadgeType.FIRST_MISSION));

        // Then
        assertThat(fakeBadgeRepository.count()).isEqualTo(2);
    }

    @Test
    @DisplayName("FK 위반(1452)은 중복으로 삼키지 않고 예외가 그대로 전파된다")
    void issueBadge_foreignKeyViolation_propagatesException() {
        // Given
        fakeBadgeRepository.willViolateWith(1452);
        BadgeIssueInDto badgeIssueInDto = BadgeIssueInDto.of(1L, BadgeType.FIRST_MISSION);

        // When & Then
        assertThatThrownBy(() -> badgeIssueService.issueBadge(badgeIssueInDto))
                .isInstanceOf(DataIntegrityViolationException.class);
        assertThat(fakeBadgeRepository.count()).isZero();
    }

    @Test
    @DisplayName("NOT NULL 위반(1048)은 중복으로 삼키지 않고 예외가 그대로 전파된다")
    void issueBadge_notNullViolation_propagatesException() {
        // Given
        fakeBadgeRepository.willViolateWith(1048);
        BadgeIssueInDto badgeIssueInDto = BadgeIssueInDto.of(1L, BadgeType.FIRST_MISSION);

        // When & Then
        assertThatThrownBy(() -> badgeIssueService.issueBadge(badgeIssueInDto))
                .isInstanceOf(DataIntegrityViolationException.class);
    }
}
```

### 테스트 3. 통합 (Testcontainers MySQL, 실제 프록시). 이 사고의 회귀 방지 핵심

단위 테스트는 `@Transactional` 이 적용되지 않으므로 rollback-only 전파를 검증하지 못합니다. #633 은 단위 테스트를 통과하고 운영에서 터졌습니다. 이 테스트가 실제로 잡는 것은 "상위 트랜잭션 안에서 중복 발급이 일어나도 같은 트랜잭션의 미션 달성 기록이 살아남는다"입니다.

```java
@SpringBootTest
@ActiveProfiles("test")
class BadgeIssueServiceIntegrationTest extends MysqlTestcontainersSupport {  // 기존 Testcontainers 베이스 가정

    private BadgeIssueService badgeIssueService;
    private BadgeJpaRepository badgeJpaRepository;
    private MissionAchievementJpaRepository missionAchievementJpaRepository;
    private TransactionTemplate transactionTemplate;

    @BeforeEach
    void setUp(
            @Autowired BadgeIssueService badgeIssueService,
            @Autowired BadgeJpaRepository badgeJpaRepository,
            @Autowired MissionAchievementJpaRepository missionAchievementJpaRepository,
            @Autowired PlatformTransactionManager platformTransactionManager) {
        this.badgeIssueService = badgeIssueService;
        this.badgeJpaRepository = badgeJpaRepository;
        this.missionAchievementJpaRepository = missionAchievementJpaRepository;
        this.transactionTemplate = new TransactionTemplate(platformTransactionManager);
        // 상위 호출처(미션 달성)와 같은 기본 전파(REQUIRED)를 의도적으로 사용합니다.
        this.transactionTemplate.setPropagationBehavior(TransactionDefinition.PROPAGATION_REQUIRED);
        badgeJpaRepository.deleteAll();
        missionAchievementJpaRepository.deleteAll();
    }

    @Test
    @DisplayName("상위 트랜잭션 안에서 중복 뱃지를 발급해도 롤백되지 않고 같은 트랜잭션의 미션 달성 기록이 커밋된다")
    void issueBadge_duplicateInsideOuterTransaction_keepsOuterWork() {
        // Given
        BadgeIssueInDto badgeIssueInDto = BadgeIssueInDto.of(1L, BadgeType.FIRST_MISSION);
        BadgeIssueOutDto firstBadgeIssueOutDto = badgeIssueService.issueBadge(badgeIssueInDto);

        // When
        BadgeIssueOutDto duplicatedBadgeIssueOutDto = transactionTemplate.execute(status -> {
            missionAchievementJpaRepository.save(MissionAchievementJpaEntity.of(1L, 100L));
            return badgeIssueService.issueBadge(badgeIssueInDto);
        });

        // Then
        assertThat(duplicatedBadgeIssueOutDto.badgeId()).isEqualTo(firstBadgeIssueOutDto.badgeId());
        assertThat(badgeJpaRepository.count()).isOne();
        assertThat(missionAchievementJpaRepository.count()).isOne();
    }

    @Test
    @DisplayName("상위 트랜잭션이 이미 스냅샷을 잡은 뒤 다른 쪽이 먼저 커밋한 뱃지도 중복 발급 시 조회해서 반환한다")
    void issueBadge_duplicateCommittedAfterOuterSnapshot_returnsExisting() {
        // Given
        BadgeIssueInDto badgeIssueInDto = BadgeIssueInDto.of(1L, BadgeType.FIRST_MISSION);

        // When
        BadgeIssueOutDto badgeIssueOutDto = transactionTemplate.execute(status -> {
            badgeJpaRepository.findAll();                            // 상위 스냅샷을 먼저 확정합니다
            BadgeIssueOutDto concurrentlyIssued = badgeIssueService.issueBadge(badgeIssueInDto);  // 격리 트랜잭션이 커밋합니다
            assertThat(concurrentlyIssued).isNotNull();
            return badgeIssueService.issueBadge(badgeIssueInDto);    // 중복 경로
        });

        // Then
        assertThat(badgeIssueOutDto.badgeType()).isEqualTo(BadgeType.FIRST_MISSION);
        assertThat(badgeJpaRepository.count()).isOne();
    }
}
```

### 일부러 깨뜨렸을 때 실패하는지 (RR-12 확인 방법)

| 깨뜨리는 변경 | 실패하는 테스트 |
|---------------|-----------------|
| `isDuplicateKey` 판별을 제거하고 전체 catch | 테스트 2 의 FK·NOT NULL 전파 케이스, 테스트 1 의 1452·1048 케이스 |
| `createBadgeInNewTransaction` 의 `REQUIRES_NEW` 를 제거 | 테스트 3 (rollback-only 로 `UnexpectedRollbackException`, 미션 달성 기록 0건) |
| 재조회를 catch 안에서 상위 세션 `findBy...` 로 변경 | 테스트 3 (`AssertionFailure` 또는 스냅샷 미조회) |
| 중복인데 null 일 때 예외를 던지는 분기 제거 | 별도 케이스가 필요하며, 아래 열린 질문 3번에 적었습니다 |

---

## 실행 계획 (시뮬레이션)

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
./gradlew :pasta-api:cleanTest :pasta-api:test --tests '*badge*'      # 가정 결과: 전부 PASS (Testcontainers MySQL 기동 포함)
./gradlew :pasta-api:spotlessApply
python3 forge/common/review-lint.py                                   # 가정 결과: 위반 0건
```

review-lint 가정 출력과 확인 항목 판단:

| 코드 | 결과 | 판단 |
|------|------|------|
| RR-12 `@Mock` 상태 저장소 | 0건 | Fake 사용 |
| RR-12 `lenient`·`any()`·느슨한 JSON 단언 | 0건 | 해당 없음 |
| RR-13 `Collectors.toMap` | 0건 | 해당 없음 |
| LAYER | 0건 | Domain 이 HTTP 예외를 import 하지 않음. 컨트롤러 변경 없음 |
| NAMING | 확인 0건 | `*At`, 타입명 변수 준수 |
| FQCN·PII | 0건 | 로그 본문에 userId 없음 |

테스트가 5회 연속 실패하면 즉시 중단하고 보고합니다. 빌드 산출물 손상이 의심되면 `unzip -t` 로 jar 를 검사합니다. 장시간 gradle 작업에는 `nohup` 대신 `run_in_background` 를 씁니다. 커밋은 하지 않으며, `git status --short`/`git diff --stat` 로 의도하지 않은 변경이 없는지 확인한 뒤 보고합니다 (DW-5, DW-7). 이번 응답은 시뮬레이션이라 실제 실행·확인은 하지 않았습니다.

---

## PR 본문에 적을 항목

- **기존 동작 변경**: 중복 뱃지 발급이 예외에서 "기존 뱃지 반환(INFO 로그)"으로 바뀝니다. 호출처는 `MissionAchieveService` 1곳입니다(grep 가정).
- **결정 근거**: 격리 트랜잭션 분리와 에러코드 1062 판별은 #633 사고(Session 오염)의 재발 방지입니다. 기존 `BadgeIssueService` 패턴과 동일한 계층 규칙을 따랐습니다.
- **추가 쿼리가 도는 경로**: 중복일 때만 새 트랜잭션 SELECT 1회가 추가됩니다. 정상 발급 경로에는 추가 쿼리가 없습니다.
- **트레이드오프**: 격리 트랜잭션이므로 뱃지는 상위 트랜잭션이 롤백되어도 커밋된 채 남습니다. v1.11-C 가 대상으로 정의한 의도된 동작입니다.
- **위험·미해결**: 아래 열린 질문 참조.

---

## 열린 질문 (승인이 필요한 것)

1. **UNIQUE 제약 실재 여부**: Phase 0 grep 5번 결과를 확인해 주세요. 없으면 위 "중단 조건"대로 멈추고 선택지를 드립니다.
2. **"새로 발급됐는가" 구분**: 중복도 정상 응답으로 돌려주면 호출자는 신규/기존을 구분하지 못합니다. 신규 발급에만 알림·보상이 나가야 한다면 OutDto 에 `newlyIssued` 같은 필드가 필요합니다. 소비자가 없는 필드는 만들지 않는 것이 원칙이라 지금은 추가하지 않았습니다.
3. **중복인데 재조회가 비는 경우**: 삭제 동시성 같은 비정상 상황으로 보고 원 예외를 전파하도록 했습니다. "조용히 넘어가기"를 더 넓게 원하면 null 반환 등으로 바꿀 수 있지만, 사용자가 없는 뱃지를 받은 것으로 오인할 수 있어 기본값으로 택하지 않았습니다.
4. **대안(이번에는 도입하지 않음)**: 예외 기반 흐름 대신 `INSERT ... ON DUPLICATE KEY UPDATE id = id`(또는 `INSERT IGNORE`) 네이티브 쿼리로 예외 없이 멱등 처리할 수 있습니다. 세션 오염 문제가 구조적으로 사라지는 대신 JPA 영속성 컨텍스트를 우회하고 새 쿼리 방식을 도입하므로 승인 사항입니다. 원하시면 비교안을 따로 드립니다.

---

## 자기 검증 체크리스트 (관련 항목)

| 항목 | 결과 |
|------|------|
| 4-Tier 의존 방향 (Web -> App -> Domain <- Infra) | 준수. Domain·Infra 변경 없음, 판별 헬퍼는 Application |
| Domain 순수성 | 준수 (Domain 미변경) |
| record/class, Lombok, `var`, 와일드카드 import | 준수 |
| FQCN | 없음. 필요한 import 는 파일 상단에 선언 (`DataIntegrityViolationException`, `SQLIntegrityConstraintViolationException`, `Propagation`, `TransactionDefinition` 등) |
| 로그 접두사·PII | `[BadgeIssueService.issueBadge]`, userId 미포함 |
| v1.11-A Session 오염 | catch 블록에서 상위 세션 재조회 없음. 재조회는 새 트랜잭션 |
| v1.11-B 에러코드 판별 | 1062 한정, 그 외 rethrow |
| v1.11-C 격리 | `REQUIRES_NEW` Bean 분리 + Testcontainers 회귀 테스트 |
| v1.7 TransactionTemplate 전파 | 테스트의 `TransactionTemplate` 에 `setPropagationBehavior` 즉시 호출, 의도 주석 |
| 테스트 스타일 | `@DisplayName` 한글 구체적, Given-When-Then, AssertJ, Fake 우선, Mockito verify 없음, H2 없음 |
| RR-13 실패 격리 | 중복 외 결함은 전파해 드러냄, 비정상 재조회 실패도 전파 |
| RR-14 동작 변경 | PR 본문 기재, 새 분기를 단위(Fake)·통합 양쪽 경로에서 테스트 |
| 범위 규율 | 호출처·마이그레이션·스키마 변경 없음. UNIQUE 부재 시 보고 후 승인 대기 |
| 커밋 | 하지 않음 |
