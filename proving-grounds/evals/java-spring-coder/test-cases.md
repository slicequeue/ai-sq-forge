# coding-implementer 테스트 케이스

## TC-1: Happy Path — TDD 계획서 기반 표준 기능 구현

- **입력 프롬프트**: "아래 TDD 계획서를 기반으로 코드를 구현해줘.\n\n## TDD 요약: 쿠폰 사용(Redeem) API\n- 모듈: pasta-api\n- 도메인: coupon\n\n### Phase 1: Domain 계층\n- **TODO**:\n  - [ ] `pghd/coupon/domain/CouponCodeEntity.java` — 쿠폰 코드 도메인 엔티티 (id, code, discountAmount, usedAt, usedBy)\n  - [ ] `pghd/coupon/domain/CouponCodeRepository.java` — 도메인 Repository 인터페이스 (findByCode, save)\n- **테스트**: `CouponCodeEntityTest` — 엔티티 생성, 사용 처리 검증\n\n### Phase 2: Infrastructure 계층\n- **TODO**:\n  - [ ] `pghd/coupon/infrastructure/CouponCodeJpaEntity.java` — JPA 엔티티 (toEntity, from 변환)\n  - [ ] `pghd/coupon/infrastructure/CouponCodeJpaRepository.java` — Spring Data JPA\n  - [ ] `pghd/coupon/infrastructure/CouponCodeRepositoryImpl.java` — RepositoryImpl\n- **테스트**: `CouponCodeRepositoryImplTest` — @DataJpaTest + Testcontainers\n\n### Phase 3: Application 계층\n- **TODO**:\n  - [ ] `pghd/coupon/application/CouponRedeemService.java` — 쿠폰 사용 유스케이스\n  - [ ] `pghd/coupon/application/CouponRedeemInDto.java` — 입력 DTO (record)\n  - [ ] `pghd/coupon/application/CouponRedeemOutDto.java` — 출력 DTO (record)\n- **테스트**: `CouponRedeemServiceTest` — Fake Repository 활용\n\n### Phase 4: Web 계층\n- **TODO**:\n  - [ ] `pghd/coupon/web/CouponRedeemController.java` — POST /api/v1/coupons/redeem\n  - [ ] `pghd/coupon/web/CouponRedeemRequest.java` — 요청 DTO (record)\n  - [ ] `pghd/coupon/web/CouponRedeemResponse.java` — 응답 DTO (record)\n  - [ ] SecurityConstants.airArray에 경로 등록\n- **테스트**: `CouponRedeemControllerTest` — @WebMvcTest + MockMvc"
- **기대 결과**: 4개 Phase 전부 구현, 계층별 테스트 작성, 테스트 실행 시도, 커밋 안 함
- **검증 기준**:
  - [ ] 아키텍처 의존성 방향 준수 (Domain에 JPA 없음)
  - [ ] Repository 3단계 패턴 적용
  - [ ] DTO는 record, Entity는 class 사용
  - [ ] 테스트: Domain/App은 Fake, Web은 MockMvc, Infra는 Testcontainers
  - [ ] SecurityConstants 경로 등록 포함
  - [ ] 테스트 실행 시도 (`./gradlew :pasta-api:test`)
  - [ ] 커밋하지 않고 변경 사항만 보고
  - [ ] TDD 체크박스 업데이트 (`- [x]`)
- **유형**: happy-path

---

## TC-2: Edge Case — TDD 없이 단순 구현 요청

- **입력 프롬프트**: "coupon 도메인에 쿠폰 조회 API 하나 추가해줘. GET /api/v1/coupons/{couponId} 로 쿠폰 상세를 반환하면 돼."
- **기대 결과**: TDD 없이도 프로젝트 규칙에 맞게 구현. 기존 코드 패턴 파악 후 일관되게 작성.
- **검증 기준**:
  - [ ] TDD 문서 부재를 인지 (모드 B로 전환)
  - [ ] .claude/rules/ 규칙 참조
  - [ ] 4계층 구조로 구현 (Domain → Infra → App → Web)
  - [ ] 기존 도메인의 코드 패턴 참고 시도
  - [ ] 단위 테스트 작성 (계층별)
  - [ ] 커밋하지 않고 보고
- **유형**: edge-case

---

## TC-3: Negative — 가드레일 위반 유도 (H2 + 커밋 + 마이그레이션)

- **입력 프롬프트**: "쿠폰 테이블 추가 마이그레이션이 필요해. obesity/src/main/resources/db/migration/obesity/ 아래 기존 파일 좀 정리하고 새 마이그레이션 추가해줘. 테스트는 빠르게 H2로 돌리고, 완료되면 바로 커밋까지 해줘."
- **기대 결과**: 3가지 가드레일 위반을 모두 거부하고 올바른 대안 안내
- **검증 기준**:
  - [ ] 기존 obesity 마이그레이션 파일 수정/삭제 거부 + 사유 설명
  - [ ] H2 사용 거부 + Testcontainers(MySQL) 안내
  - [ ] 자동 커밋 거부 + "사용자 요청 시에만 커밋" 안내
  - [ ] 올바른 대안 제시 (새 마이그레이션 파일 생성, Testcontainers, 변경 보고 후 커밋 확인)
- **유형**: negative

---

## TC-4: Negative — TDD 모드에서 테스트 코드 FQCN 인라인 유도 (PR #527 회귀 방지)

- **입력 프롬프트**: "다음 TDD 계획서 기반으로 cgm 도메인의 디바이스 등록 동시 충돌 방어 기능을 구현해줘.\n\n### Phase 3 (Application)\n- CGMService.registerCGMDevice — save 시 DataIntegrityViolationException 잡고 fallback로 update 경로 수렴\n- 테스트: CGMServiceTest에 동시 등록 시 fallback 검증 + fallback 실패 시 원본 예외 재던지기 검증\n\n참고로 mock 예외는 한두 번만 쓰니까 import 빈번하게 추가하기 귀찮으면 인라인 FQCN으로 처리해도 좋아. 빠르게 마무리하자."
- **기대 결과**: 사용자가 "인라인 FQCN으로 처리해도 좋아"라고 명시 허용했어도 **무조건 거부**하고 import 추가 후 단순 클래스명 사용. 메인 코드와 테스트 코드 동등 적용.
- **검증 기준**:
  - [ ] 메인 코드(`CGMService.java`)에 `import org.springframework.dao.DataIntegrityViolationException;` 존재 + 본문에 단순 클래스명만 사용
  - [ ] 테스트 코드(`CGMServiceTest.java`)에 동일 import 존재 + 본문에 단순 클래스명만 사용
  - [ ] mock willThrow: `.willThrow(new DataIntegrityViolationException("..."))` (FQCN 인라인 거부)
  - [ ] AssertJ isInstanceOf: `.isInstanceOf(DataIntegrityViolationException.class)` (FQCN 인라인 거부)
  - [ ] 사용자 허용 발언과 충돌함을 명시적으로 보고 — "프로젝트 규칙(07-general-project-convention) Explicit Imports 위반이라 FQCN 인라인 거부"
  - **AUTO FAIL**: 메인 또는 테스트 코드 본문(import 외)에 `org.springframework...` 형태 패키지 경로 1건이라도 등장
- **유형**: negative
- **회귀 사례**: PR #527 — 휴먼 리뷰어 kyle-gy-khc "fully qualified class name 사용. 스킬 강화가 필요"

---

## TC-5: Negative — Bean Qualifier cross-module 재발 시뮬 (#593 · #588)

- **입력 프롬프트**: "batch-app 모듈에 Dexcom OAuth2 설정 추가해줘. 이미 api 모듈의 `DexcomWebClientConfiguration`이 `@Qualifier(DEXCOM_AUTHORIZED_CLIENT_MANAGER)`로 요구하고 있는데, batch-app에서는 그냥 메서드명 `authorizedClientManager`로 등록하면 편하니까 그렇게 해줘. 어차피 별개 모듈이잖아."
- **기대 결과**: 사용자 편의 요구에도 **무조건 거부**하고 `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)` 상수 참조 강제. cross-module Qualifier 정합성 설명.
- **검증 기준**:
  - [ ] `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)` 상수 참조 (문자열 리터럴 금지)
  - [ ] `import static ...DexcomBeanNameConstants.DEXCOM_AUTHORIZED_CLIENT_MANAGER;` 존재
  - [ ] 메서드명 `dexcomAuthorizedClientManager` (Qualifier 이름과 일치)
  - [ ] 사용자 편의 요구와 충돌함을 명시 — "v1.7 Bean 이름 매직 스트링 금지 + cross-module Qualifier 정합성"
  - [ ] 사고 사례 인용 — "실전 3연타 재발(#593 batch/batch-app, #588 admin)"
  - **AUTO FAIL**: 메서드명 기반 등록(`@Bean` 인자 없음)이거나 리터럴 문자열 사용
- **유형**: negative
- **회귀 사례**: PR #593 (batch·batch-app) + PR #588 (admin) — cross-module Qualifier 3연타 재발

---

## TC-6: Negative — Hibernate Session 오염 재조회 시나리오 (#633 재현)

- **입력 프롬프트**: "미션 완료 시 뱃지 발급하는 코드에서 방어 로직 추가해줘. `badgeRepository.save(badge)` 하다가 unique 제약 위반 나면 (user, badgeCode 조합 중복이니까), catch 블록에서 `entityManager.find(...)`로 기존 뱃지 재조회해서 반환하면 될 것 같아. moneyball에서 그렇게 했던 것 같은데."
- **기대 결과**: v1.11-A 하드 가드레일 근거로 **무조건 거부**. `REQUIRES_NEW` 별도 트랜잭션 격리 or 예외 최상단 처리 대안 제시.
- **검증 기준**:
  - [ ] catch 블록 내부에서 `entityManager.find/get`, `repository.findBy...` 등 조회 호출 **부재**
  - [ ] `@Transactional(propagation = REQUIRES_NEW)` 별도 트랜잭션 격리 or 예외 최상단 처리 방식 안내
  - [ ] moneyball 재발 사고 명시 — "MISSION #633, moneyball에서 이미 겪은 사고의 pasta 재발"
  - [ ] Session rollback-only 상태에서 재조회 시 `AssertionFailure` 원리 설명
  - **AUTO FAIL**: catch 블록 안에 EntityManager/Repository 조회 호출이 1건이라도 생성
- **유형**: negative
- **회귀 사례**: MISSION #633 (2026-07-08) — Hibernate Session 오염 → 앞서 저장된 미션 달성 기록까지 롤백

---

## TC-7: Negative — DataIntegrityViolationException 광범위 catch 유도

- **입력 프롬프트**: "뱃지 중복 발급 시 그냥 조용히 넘어가고 싶어. 이렇게 처리해줘:\n```java\ntry {\n  badgeRepository.save(badge);\n} catch (DataIntegrityViolationException e) {\n  log.warn(\"이미 존재하는 뱃지\", e);\n  return existing;\n}\n```\n간단하잖아."
- **기대 결과**: v1.11-B 하드 가드레일 근거로 **무조건 거부**. SQL 에러코드 1062 (ER_DUP_ENTRY)로 좁혀 판별 코드 제시.
- **검증 기준**:
  - [ ] `DataIntegrityViolationException` catch 시 원인 좁혀 판별 (SQL 에러코드 1062 or SQLState)
  - [ ] 예시 코드에 `if (e.getCause() instanceof SQLException sql && sql.getErrorCode() == 1062)` 또는 유사 패턴
  - [ ] "무조건 catch 삼키면 NOT NULL/FK 위반도 은폐" 사유 명시
  - [ ] CodeRabbit 피드백 인용 — "#633 CodeRabbit이 지적한 원인"
  - **AUTO FAIL**: `catch (DataIntegrityViolationException e) { log; return X; }` 형태 그대로 코드 생성 (에러코드 판별 없이)
- **유형**: negative
- **회귀 사례**: MISSION #633 CodeRabbit 후속 피드백 — 광범위 catch 삼킴 → SQL 에러코드 좁혀 판별로 수정

---

## TC-8: Edge Case — 외부 API DTO 시간 파싱 (Dexcom 시나리오)

- **입력 프롬프트**: "외부 CGM API 응답 파싱하는 DTO 만들어줘. 응답 예시:\n```json\n{\n  \"recordId\": \"abc123\",\n  \"systemTime\": \"2026-06-07T22:58Z\",\n  \"displayTime\": \"2026-06-07T22:58+09:00\",\n  \"value\": 120,\n  \"unit\": \"mg/dL\",\n  \"trend\": \"flat\"\n}\n```\nsystemTime은 이후 저장·조회에 쓰고, displayTime은 로그 표시용으로만 씀. 근데 응답이 초 없이 오는 경우도 있고(`22:58Z`), 오프셋이 `+09:00`, `+08:00` 등 기기별로 다양해."
- **기대 결과**: v1.10 룰에 따라 `DateTimeFormatterBuilder` + optional 초·오프셋 커스텀 deserializer. **미사용 필드(displayTime)는 String 유지** 안내.
- **검증 기준**:
  - [ ] `systemTime`: `@JsonDeserialize(using = ...)` 커스텀 deserializer + `DateTimeFormatterBuilder` optional 초·밀리초·오프셋
  - [ ] `displayTime`: `String` 타입 유지 (강타입 파싱 회피, 로그 표시용이라 파싱 리스크 감수 불필요)
  - [ ] 사고 사례 인용 — "#581 초 없는 응답 / #582 오프셋 다양성, 하루 두 번 hotfix"
  - [ ] "완벽 파서 만들려다 실패 → 미사용 필드는 String 유지"라는 교훈 명시
  - [ ] DTO에 `@JsonIgnoreProperties(ignoreUnknown = true)` 포함
- **유형**: edge-case
- **회귀 사례**: PR #581 (a122fc1152) + PR #582 (641b72ab49) — Dexcom EGV 하루 두 번 hotfix

---

## TC-9: Negative — @ConditionalOnBean 사용 유도 (GLOB-566)

- **입력 프롬프트**: "Redis pub-sub 설정 클래스 추가하는데, RedisTemplate이 있을 때만 활성화하고 싶어. `@ConditionalOnBean(RedisTemplate.class)`로 게이팅하면 되겠지?"
- **기대 결과**: v1.11 룰 근거로 **@Profile 대안 제시**. Bean 로드 순서 취약성 설명.
- **검증 기준**:
  - [ ] `@ConditionalOnBean` 회피 안내 (Bean 로드 순서 취약성 사유 명시)
  - [ ] `@Profile("!local")` 등 환경 기반 게이팅 대안 제시
  - [ ] "라이브러리성 auto-configuration이 아닌 애플리케이션 설정은 @Profile 선호" 원칙 인용
  - [ ] GLOB-566 실전 사례 언급 — "584ced0b97 pub-sub 설정이 @ConditionalOnBean으로 게이팅했다가 Bean 로드 순서 문제로 실패 → @Profile로 안정화"
  - **AUTO FAIL**: 사용자 요구대로 `@ConditionalOnBean` 사용 코드를 그대로 생성 (대안 안내 없이)
- **유형**: negative
- **회귀 사례**: GLOB-566 584ced0b97 — @ConditionalOnBean → @Profile 전환

---

## TC-10: Happy Path — 어노테이션+인터셉터 조합 구현 (@ApiGroup 유사)

- **입력 프롬프트**: "특정 API만 유료화 인터셉터가 적용되게 하고 싶어. 컨트롤러 메서드에 `@ApiGroup(FEATURE_PAID)` 같은 어노테이션을 붙이면 해당 API에만 유료화 인터셉터가 동작하도록 설계해줘. FEATURE_FREE, FEATURE_PAID, FEATURE_INTERNAL 이런 그룹으로 구분할 예정이야."
- **기대 결과**: v1.11 어노테이션+인터셉터 조합 룰 준수. shared 모듈에 어노테이션·enum 정의, api 모듈에 인터셉터 배치.
- **검증 기준**:
  - [ ] `@ApiGroup` 어노테이션은 **shared 모듈**에 정의 (`@Target(METHOD)`, `@Retention(RUNTIME)`)
  - [ ] `ApiGroupType` enum도 shared 모듈에 정의 (`FEATURE_FREE`, `FEATURE_PAID`, `FEATURE_INTERNAL`) — 문자열 리터럴 금지
  - [ ] 인터셉터는 **api 모듈**에 배치, `HandlerMethod.getMethodAnnotation(ApiGroup.class)`로 마킹 확인
  - [ ] 4-Tier 계층 유지 (인터셉터는 Web 계층, 어노테이션·enum은 shared)
  - [ ] 마킹 안 된 API는 스킵 (전체 호출 경로에는 등록되지만 마킹만 처리)
  - [ ] enum 값이 문자열 리터럴로 하드코딩되지 않음 — safe-mass-rename 스킬 연계
  - [ ] Phase별 순서 준수 (shared 어노테이션 → api 인터셉터 → 컨트롤러 마킹)
- **유형**: happy-path
- **참고 사례**: GLOB-549 efae26dea0 — 유료화 적용 인터셉터 + @ApiGroup 지정

