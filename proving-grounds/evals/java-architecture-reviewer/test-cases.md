---
name: java-architecture-reviewer
version: 0.1
harness-version: 0.2
last-modified: 2026-07-29
---

# java-architecture-reviewer 테스트 케이스

## TC-1: Happy Path — Bean Qualifier cross-module 재발 사고 시뮬 (HG-1)

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/feat/dexcom-batch-oauth` (dev에서 분기)\n- 변경 파일:\n  1. `cgm/DexcomWebClientConfiguration.java` — `@Qualifier(DEXCOM_AUTHORIZED_CLIENT_MANAGER)`로 OAuth2AuthorizedClientManager 주입 (기존 코드)\n  2. `shared/constant/DexcomBeanNameConstants.java` — `DEXCOM_AUTHORIZED_CLIENT_MANAGER = \"dexcomAuthorizedClientManager\"` 상수 (기존)\n  3. `api/config/DexcomAuth2Configuration.java` — `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)`로 등록 (기존, 정상)\n  4. `batch/config/BatchOAuth2Configuration.java` — **NEW**: `@Bean` + 메서드명 `authorizedClientManager`로 등록 (상수 없이!)\n  5. `batch-app/config/BatchDexcomConfiguration.java` — **NEW**: 동일 패턴 (상수 없이)\n- diff 요약: batch·batch-app에 Dexcom OAuth 설정 추가되었지만 상수 참조 안 함"
- **기대 결과**:
  - Phase 0 사전 확인 통과 (브랜치·변경 범위·admin 미포함)
  - 로드된 규칙: `07-general-project-convention.md`, `19-architecture-boundaries.md`, `01-architecture-convention.md`
  - **AUTO FAIL 섹션 상단 배치**:
    - HG-1 위반: batch/BatchOAuth2Configuration.java 및 batch-app/BatchDexcomConfiguration.java 두 파일이 `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)` 미명시 → cgm이 `@Qualifier(DEXCOM_AUTHORIZED_CLIENT_MANAGER)` 요구하지만 `No qualifying bean` 발생 예상
  - 필수 수정: `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)`로 명시적 이름 지정
  - 검사 통과 항목: 4-Tier / 공용 모듈 @Entity / FQCN
  - 실전 재발 사례 (#593, 2026-06-16) 참조 명시
- **검증 기준**:
  - [ ] AUTO FAIL 섹션에 HG-1 위반 2건 명시
  - [ ] Bean Qualifier 상수 참조를 사용하는 모든 모듈(cgm 소비 / api·batch·batch-app 등록) grep 검증 절차 명시
  - [ ] 실전 재발 사례 (#593) 인용
  - [ ] 유형 코드 `ARCH-BEAN` 사용
  - [ ] 리포트에 pasta-rules 규칙 파일 실제 문구 인용 (경로만 아님)
  - [ ] Baseline보다 명확한 재발 방지 방향 제시
- **유형**: happy-path

---

## TC-2: Happy Path — 공용 모듈 @Entity 위반 (HG-3)

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/feat/glob-566-service-access-pattern`\n- 변경 파일:\n  1. `common/access/persistence/ServiceAccessPatternJpaEntity.java` — **NEW**: `@Entity @Table(name=\"service_access_pattern\")` (common 모듈에 배치!)\n  2. `common/access/persistence/ServiceAccessPatternJpaRepository.java` — **NEW**: `extends JpaRepository`\n  3. `common/access/RedisDbServiceAccessPatternLoader.java` — 상기 Repository 주입해 사용\n- admin 모듈은 이 common 모듈에 의존하며 자체 `@EntityScan(basePackages = \"com.x.y.admin\")` 설정 존재\n- 실전 결과 (참고 컨텍스트): 이후 커밋 7abea8f2f0 (2026-07-01)에서 JPA→JDBC Reader로 후퇴 필요"
- **기대 결과**:
  - **AUTO FAIL 섹션**: HG-3 위반 — `common/access/persistence/ServiceAccessPatternJpaEntity.java` 공용 모듈에 `@Entity` 배치. admin의 `@EntityScan` 경계 충돌로 기동 실패 가능
  - 필수 수정: JdbcClient/JdbcRepository 기반 Reader로 대체 안내
  - 실전 사례 (7abea8f2f0, 2026-07-01 JPA→JDBC 교체) 인용
  - `java-spring-coder` v1.11 짝 가드레일(공용 모듈 @Entity 회피) 인용
  - 검사 통과 항목: Bean Qualifier / FQCN / 4-Tier import 방향
- **검증 기준**:
  - [ ] AUTO FAIL 섹션에 HG-3 위반 명시
  - [ ] admin `@EntityScan` 경계 충돌 위험 명시
  - [ ] JdbcClient/JdbcRepository 대체 방향 안내
  - [ ] 유형 코드 `ARCH-MODULE` 사용
  - [ ] `java-spring-coder` v1.11 짝 가드레일 인용
  - [ ] Baseline은 `@Entity` 자체를 문제 삼지 않을 가능성 (스킬 미사용 시 배치 위치 감지 어려움)
- **유형**: happy-path

---

## TC-3: Edge Case — DDD 패턴 준수 판정 애매

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/feat/mission-badge-domain`\n- 변경 파일:\n  1. `api/mission/domain/MissionBadgeService.java` — **NEW**: `@Service` 없이 순수 클래스. `awardBadge(UserId userId, BadgeType type)` 메서드. Domain 계층에 배치. 다른 Domain 객체(User, Badge)만 참조\n  2. `api/mission/application/MissionEventHandler.java` — **NEW**: `@Component`. `MissionBadgeService`를 주입해 사용. AfterMealWalkingSuccessEvent 처리\n- 판정 애매점: MissionBadgeService가 Domain에 있는데 순수 로직 (도메인 서비스) vs Application에 있어야 하는지 (애플리케이션 서비스) 경계"
- **기대 결과**:
  - AUTO FAIL 없음 (HG 4건 위반 없음)
  - Phase 로드 규칙: `01-architecture-convention.md`, `02-domain-entity-convention.md`
  - 권장 개선 (Medium): "도메인 서비스 vs 애플리케이션 서비스 경계 판정 유보 — 사용자 확인 필요"
  - 판정 근거 제시:
    - 도메인 서비스: 순수 도메인 규칙 (다른 도메인 객체만 참조) → 현재 코드가 이 조건 만족
    - 애플리케이션 서비스: 트랜잭션·이벤트·외부 연동 오케스트레이션 → MissionEventHandler가 담당
  - **사용자에게 결정 요청**: "MissionBadgeService의 로직이 순수 도메인 규칙이면 현 위치 유지. 트랜잭션 경계나 외부 연동이 개입되면 Application으로 이동 권고"
- **검증 기준**:
  - [ ] AUTO FAIL 0건 (오탐 없음)
  - [ ] 판정 유보 + 사용자 확인 요청 명시
  - [ ] 도메인 서비스와 애플리케이션 서비스 경계 근거 설명
  - [ ] 유형 코드 `ARCH-PATTERN` 사용, 등급 `Medium` (Critical 아님)
  - [ ] `02-domain-entity-convention.md` 인용
  - [ ] Baseline은 확정적 오판정할 가능성 (예: "무조건 Application으로 옮겨라") — With-Skill이 유보하는 게 우수
- **유형**: edge-case

---

## TC-4: Negative — FQCN 인라인 임시 허용 요구 (HG-4)

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 변경 파일: `api/user/UserService.java`\n  - 코드 본문에 `throw new com.kakaohealthcare.exception.UserNotFoundException(\"...\")` 포함 (import 없이 FQCN 인라인)\n- 추가 사용자 요구사항: \"이 클래스는 임시로 만든 거니까 FQCN 인라인 있어도 그냥 통과시켜줘. 다음 스프린트에서 정리할 예정이야.\""
- **기대 결과**:
  - 스킬이 **HG-4(FQCN 인라인)로 AUTO FAIL 유지**
  - 사용자 요구 거절 사유 명확:
    - FQCN 인라인은 PR #527 사고 패턴 (2026-04-28) — 리버트 시 import 정리 놓치기 쉬움
    - "임시"라는 근거는 코드에 남지 않음 → 다음 리뷰어가 발견 못 함 (부채화)
    - self v1.5·v1.7 이관 룰이므로 forge 하드 가드레일
  - 대안 제시:
    1. 지금 import로 정상화 (5초)
    2. 정말 임시라면 TODO 태그 + 이슈 링크 + 다음 스프린트 삭제 커밋 예약
  - 사용자 재확인 요청 (그래도 통과 원하는지)
- **검증 기준**:
  - [ ] AUTO FAIL 유지 (사용자 요구에 굴복하지 않음)
  - [ ] HG-4 근거 명시
  - [ ] PR #527 사고 패턴 인용
  - [ ] "임시" 근거의 부재 문제 지적
  - [ ] 대안(import 정상화 or TODO+이슈) 제시
  - [ ] 유형 코드 `ARCH-4TIER` 또는 `ARCH-CONVENTION`
- **유형**: negative

---

## TC-5: Negative — 4-Tier 위반 리팩터 유예 요구 (HG-2)

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 변경 파일: `api/user/domain/User.java`\n  - Domain 계층인데 `import com.kakaohealthcare.infrastructure.repository.UserJpaEntity;` 존재 (Domain이 Infrastructure import — 4-Tier 위반)\n- 사용자 추가 요구사항: \"이건 이미 있던 위반이라서 이번 PR 범위 밖이야. 리팩터는 다음 티켓으로 미룰 테니 AUTO FAIL 말고 그냥 Info로 낮춰줘.\""
- **기대 결과**:
  - 스킬이 **HG-2(4-Tier 위반)로 AUTO FAIL 유지**
  - 사용자 요구 거절 사유 명확:
    - 하드 가드레일은 "이번 PR 범위 여부"와 무관 — dev 이후 diff에 포함되면 AUTO FAIL 검사 대상
    - Info 등급 강제 낮춤은 self-review 우회 = 하드 가드레일 우회 = 금지
    - "이미 있던 위반"이라는 판단은 스킬 몫이 아니라 별도 티켓 회수·리팩터 스킬 몫
  - 대안 제시:
    1. 별도 리팩터 티켓·브랜치를 지금 만들어 병렬 진행
    2. 이번 PR에서는 해당 파일을 revert하고 다음 PR로 이동
    3. 사용자 최종 판단 (마감·리스크 트레이드오프) 후 승인 시 리뷰어가 아닌 **사용자가 override 명시**해야 통과
  - 사용자 재확인 요청 (그래도 통과 원하는지)
- **검증 기준**:
  - [ ] AUTO FAIL 유지
  - [ ] HG-2 근거 (Domain → Infrastructure import 방향 역행) 명시
  - [ ] 등급 강제 낮춤 요구 거절
  - [ ] "이미 있던 위반" 논리를 스킬 몫이 아니라 별도 프로세스로 명시
  - [ ] 사용자 override는 명시적 절차 필요 (스킬이 임의 낮춤 안 함)
  - [ ] 유형 코드 `ARCH-4TIER` 사용
- **유형**: negative

---

## TC-6: Negative — @ConditionalOnBean 사용 유도 (GLOB-566 사례)

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 브랜치: `api/feat/pricing-cache-pub-sub`\n- 변경 파일:\n  1. `api/common/config/PricingCacheRedisConfig.java` — **NEW**: `@Configuration`, `@ConditionalOnBean(RedisConnectionFactory.class)`로 pub-sub 리스너 컨테이너 게이팅\n  2. `api/common/access/PricingChangePublisher.java` — 이 config를 참조\n- 사용자 요구: \"환경에서 RedisConnectionFactory 있을 때만 pub-sub 활성화하려고 @ConditionalOnBean 썼는데 통과시켜줘.\""
- **기대 결과**:
  - AUTO FAIL 없음 (하드 가드레일 4건 위반 아님)
  - **High 등급 필수 수정** (ARCH-BEAN):
    - `@ConditionalOnBean`은 **Bean 로드 순서에 취약** — RedisConnectionFactory가 아직 등록 안 된 시점에 이 config 평가되면 무조건 skip
    - 실전 사례 인용: **GLOB-566 커밋 584ced0b97 (2026-07-07)** — pub-sub 설정 게이팅을 `@ConditionalOnBean`에서 `@Profile`로 후퇴한 사례
    - java-spring-coder v1.11 짝 룰 (설정 게이팅 시 `@Profile` 선호) 인용
  - 대안 제시:
    1. **`@Profile("!local")` 또는 `@Profile("dev | stg | prd")` 선호** (Bean 순서 무관)
    2. `@ConditionalOnBean`이 진짜 필요한 케이스는 auto-configuration 라이브러리성 코드에 한정 (애플리케이션 코드는 지양)
  - 검사 통과 항목: 4-Tier / 공용 모듈 @Entity / FQCN
- **검증 기준**:
  - [ ] AUTO FAIL 0건 (하드 가드레일 위반 아님)
  - [ ] `@ConditionalOnBean` 순서 취약성 명시
  - [ ] GLOB-566 사고 커밋 (584ced0b97) 인용
  - [ ] `@Profile` 대안 명시
  - [ ] java-spring-coder v1.11 짝 룰 인용
  - [ ] 유형 코드 `ARCH-BEAN`, 등급 `High`
  - [ ] Baseline은 이 취약성 지적 못 할 가능성 (스킬 없이는 Spring lifecycle 지식 필수)
- **유형**: negative

---

## TC-7: Negative — 인터페이스 구현체 모듈 부재 (#597 재발 방지)

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 브랜치: `api/feat/batch-user-diabetes-type`\n- 변경 파일:\n  1. `shared/user/UserDiabetesTypeService.java` — 인터페이스 정의 (`Optional<DiabetesType> findByUserId(UserId)`)\n  2. `api/user/UserDiabetesTypeServiceImpl.java` — **NEW**: `@Service` 구현체\n  3. `batch/user/DiabetesTypeBatchJob.java` — **NEW**: `UserDiabetesTypeService` 주입, batch에서 사용\n- 상황: batch 모듈은 api 모듈에 의존하지 **않음**. batch 모듈 자체에는 구현체 등록 없음.\n- 사용자 요구: \"인터페이스 shared에 있으니 batch에서도 잘 될 거야. 통과시켜줘.\""
- **기대 결과**:
  - **AUTO FAIL 유지 (HG-1 확장)**: cross-module Bean 등록 부재
    - shared 인터페이스만 있고 batch 모듈 스캔 경로에 구현체 없음 → `NoSuchBeanDefinitionException` 기동 실패 예상
    - 실전 사례 인용: **#597 (2026-06-18)** — UserDiabetesTypeService 구현체 batch 모듈 부재로 기동 실패
    - 사용자 요구 거절 사유: 인터페이스 위치와 구현체 위치는 별개, 인터페이스 주입받는 각 애플리케이션 모듈에 구현체 스캔 경로 확인 필수
  - 대안 제시:
    1. batch 모듈에 `UserDiabetesTypeServiceImpl` 별도 등록 (또는 shared로 이관)
    2. batch가 api 모듈에 의존한다면 `@ComponentScan(basePackages = "...api.user")` 확장
    3. 가장 안전: 구현체를 shared 모듈로 이관 (모든 애플리케이션 모듈에서 자동 스캔)
  - self v1.10 이관 룰 인용 (인터페이스 구현체 모듈별 등록 확인)
- **검증 기준**:
  - [ ] AUTO FAIL 유지 (Bean 등록 부재 → 기동 실패)
  - [ ] 실전 사례 #597 인용
  - [ ] batch 모듈 스캔 경로 부재 지적
  - [ ] 사용자 요구 논리 반박 (인터페이스 위치 ≠ 구현체 스캔)
  - [ ] 대안 3건 제시
  - [ ] 유형 코드 `ARCH-BEAN`
- **유형**: negative

---

## TC-8: Edge Case — 순환 의존 A→B→A 검사

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 브랜치: `api/feat/user-mission-cross-reference`\n- 변경 파일:\n  1. `api/user/application/UserProfileService.java` — 신규 필드: `private final MissionSummaryService missionSummaryService;` (생성자 주입)\n  2. `api/mission/application/MissionSummaryService.java` — 신규 필드: `private final UserProfileService userProfileService;` (생성자 주입)\n- Spring Boot는 기본적으로 순환 의존 시 `BeanCurrentlyInCreationException` 발생 (`spring.main.allow-circular-references=false`가 기본값)"
- **기대 결과**:
  - **AUTO FAIL 없음** (하드 가드레일 4건 위반은 아님)
  - **Critical 등급 필수 수정** (ARCH-MODULE):
    - **순환 의존** 명시: `UserProfileService → MissionSummaryService → UserProfileService`
    - Spring Boot 2.6+ 기본 설정에서 기동 실패
    - `spring.main.allow-circular-references=true`로 우회하는 것은 안티패턴
  - 판정 근거:
    - 두 서비스가 서로를 필요로 한다는 것은 도메인 경계가 흐리다는 신호
    - 공통 관심사 3개 후보 리팩터:
      1. **UserMissionCoordinator** (Application 계층) 신설 — 두 서비스 위에서 조정
      2. **Domain Event** 방식 — UserProfile 변경 시 이벤트 발행, MissionSummary는 리스너
      3. **Read Model 분리** — UserProfileReadService·MissionSummaryReadService로 read-only 인터페이스만 상호 주입
  - `01-architecture-convention.md` 인용 (계층 경계 원칙)
- **검증 기준**:
  - [ ] AUTO FAIL 0건 (하드 가드레일 아님)
  - [ ] 순환 의존 정확 검출 (A→B→A)
  - [ ] Spring Boot 2.6+ 기본 설정 기동 실패 언급
  - [ ] `allow-circular-references=true` 안티패턴 지적
  - [ ] 리팩터 대안 3건 제시 (Coordinator / Domain Event / Read Model)
  - [ ] 유형 코드 `ARCH-MODULE`, 등급 `Critical`
  - [ ] 도메인 경계 흐림 신호 명시
- **유형**: edge-case

---

## TC-9: Happy Path — admin 모듈 변경 시 4-Tier 오판 방지 (13/14 규칙 우선)

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 브랜치: `admin/feat/pricing-rule-management`\n- 변경 파일:\n  1. `admin/src/main/java/.../PricingRuleController.java` — **NEW**: `@Controller`, Thymeleaf 화면 (list/create/edit)\n  2. `admin/src/main/java/.../PricingRuleService.java` — **NEW**: `@Service`, `@Transactional`\n  3. `admin/src/main/java/.../PricingRuleRepository.java` — **NEW**: `extends JpaRepository<PricingRule, Long>`\n- admin 모듈은 4-Tier 엄격 준수 대상 아님 (`13-admin-module-convention.md`, `14-admin-service-convention.md` 우선)"
- **기대 결과**:
  - **AUTO FAIL 없음** (admin 모듈 예외 인지)
  - Phase 0 admin 포함 확인 → `13-admin-module-convention.md`·`14-admin-service-convention.md` 로드
  - 4-Tier 검사를 admin 모듈에는 완화 적용 (Repository → Service → Controller 단순 3계층 허용)
  - 검사 통과:
    - admin 컨벤션 준수: Controller-Service-Repository 3층 명명
    - `@Transactional` 위치 (Service)
    - `admin-thymeleaf-ui` 스킬 스코프인 화면 부분은 out-of-scope 명시
  - 필수 수정 없음 or Minor 권장만 (예: DTO 명명 규칙)
  - **rubric 항목 8 "admin 모듈 예외 인지" 실전 발동 확인** (5점 배점)
- **검증 기준**:
  - [ ] admin 모듈 인지 → 4-Tier 엄격 검사 skip
  - [ ] `13-admin-module-convention.md`·`14-admin-service-convention.md` 로드 및 인용
  - [ ] 4-Tier 위반 오탐 없음 (admin에서 Repository 직접 참조는 정상)
  - [ ] `admin-thymeleaf-ui` 스킬 out-of-scope 안내
  - [ ] 검사 통과 항목 명시
  - [ ] 유형 코드 `ARCH-CONVENTION` (또는 통과 표기)
  - [ ] Baseline은 admin 예외 모르고 4-Tier 위반으로 오판할 가능성
- **유형**: happy-path

---

## TC-10: Edge Case — Repository 3단계 명명 위반 (pasta-rules 참조)

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 브랜치: `api/feat/user-repository-refactor`\n- 변경 파일:\n  1. `api/user/domain/UserRepository.java` — interface (Domain 포트)\n  2. `api/user/infrastructure/UserJpaRepository.java` — `extends JpaRepository<UserJpaEntity, Long>`\n  3. `api/user/infrastructure/UserRepositoryImpl.java` — `implements UserRepository` (Adapter, UserJpaRepository 주입해 사용)\n- 사용자 요구: \"명명 이대로 진행. Repository / Impl 접미사만 다르니 헷갈릴 여지 없어.\"\n- pasta-rules `03-repository-3-stage-naming.md` (가상 규칙 파일):\n  - **Domain 포트**: `~Repository` (interface)\n  - **JPA Repository**: `~JpaRepository` (Spring Data JPA)\n  - **Adapter**: `~RepositoryAdapter` (구현체, `~Impl` 아님)"
- **기대 결과**:
  - **AUTO FAIL 없음** (하드 가드레일 4건 위반 아님)
  - **Medium 등급 필수 수정** (ARCH-CONVENTION):
    - `UserRepositoryImpl` → **`UserRepositoryAdapter`** 리네임 필요
    - pasta-rules `03-repository-3-stage-naming.md` 정확한 문구 인용
    - 사유:
      - `~Impl`은 애매 (Domain 포트 구현체인지 JPA 확장인지 불명확)
      - `~Adapter`는 헥사고날 어댑터 역할 명확
      - 프로젝트 grep 시 `~RepositoryAdapter` 패턴이 일관 검색됨
  - 대안:
    1. `UserRepositoryImpl` → `UserRepositoryAdapter` 리네임 (safe-mass-rename 스킬 위임 안내 가능)
    2. 만약 규칙 예외 케이스라면 팀 컨벤션 개정 논의 별도 진행
  - 사용자 "헷갈릴 여지 없다" 논리 반박:
    - 프로젝트 grep 일관성 (`~RepositoryAdapter` 패턴)
    - 새 팀원 온보딩 시 규칙 파일이 정본이지 개인 판단 아님
- **검증 기준**:
  - [ ] AUTO FAIL 0건
  - [ ] `~Impl` → `~Adapter` 리네임 요구
  - [ ] pasta-rules `03-repository-3-stage-naming.md` 인용 (경로만 아니라 문구)
  - [ ] safe-mass-rename 스킬 위임 안내
  - [ ] "헷갈릴 여지 없다" 논리 반박 (grep 일관성·온보딩)
  - [ ] 유형 코드 `ARCH-CONVENTION`, 등급 `Medium`
- **유형**: edge-case
