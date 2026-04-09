# 규칙별 상세 검사 체크리스트

변경된 각 파일에 대해 해당하는 규칙을 대조한다. **변경 코드만 검사** — 기존 코드는 대상 아님.

---

## 1. 아키텍처 (01-architecture-convention)

- [ ] 의존성 방향: `Web → Application → Domain ← Infrastructure` 위반 없는가?
- [ ] Domain에서 Application/Infrastructure import가 없는가?
- [ ] Application에서 Infrastructure 구체 클래스 직접 import가 없는가?
- [ ] 패키지 구조가 `pghd/{domain}/{layer}/` flat 구조인가?
- [ ] 다른 도메인 리포지토리/Infrastructure 직접 접근이 없는가? (Client 패턴 사용)
- [ ] S2S API URL이 `/{service}/{version}/{domain}/{version}/{resource}` 형식인가?
- [ ] Spring Bean 이름 충돌 방지를 위해 클래스명에 도메인 접두사가 있는가?

## 2. Domain Entity (02-domain-entity-convention)

- [ ] Domain Entity가 `class`인가? (record 금지)
- [ ] `@Getter`, `@ToString`, `@EqualsAndHashCode`만 사용했는가? (`@Setter`, `@Data` 금지)
- [ ] JPA 어노테이션(`@Entity`, `@Table` 등)이 없는가?
- [ ] not-null 필드는 primitive, nullable 필드는 Wrapper인가?
- [ ] `@Builder`는 필드 10개 이상일 때만 사용했는가?
- [ ] 비즈니스 로직이 Entity에 있는가? (Rich Domain)

## 3. JPA Entity (03-jpa-entity-convention)

- [ ] `@Entity`, `@Table`, `@Getter`, `@NoArgsConstructor(PROTECTED)` 있는가?
- [ ] `@Builder`가 생성자 레벨에만 적용되었는가?
- [ ] `toEntity()` (JPA→Domain), `from()` (Domain→JPA) 변환 메서드가 있는가?
- [ ] `@Setter`, `@Data` 없는가?

## 4. Repository (04-repository-pattern-convention)

- [ ] 3단계 구조인가? (Domain Interface + JPA Interface + RepositoryImpl)
- [ ] Domain Repository가 도메인 모델만 사용하는가? (JPA 의존 없음)
- [ ] RepositoryImpl에서 Domain ↔ JPA 변환을 수행하는가?

## 5. DTO / Web (05-dto-web-layer-convention)

- [ ] DTO가 `record` 타입인가?
- [ ] Web: `*Request`/`*Response`, Application: `*InDto`/`*OutDto` 네이밍인가?
- [ ] 정적 팩토리 메서드(`of`, `from`, `to`, `forXxx`)를 사용하는가?
- [ ] Controller에 `@RestController`, `@RequiredArgsConstructor`, Swagger 어노테이션이 있는가?

## 6. 예외 처리 (06-exception-handling-convention)

- [ ] `MoneyballException` + `ExceptionConstants` 패턴을 사용하는가?
- [ ] `RuntimeException`, `IllegalArgumentException` 등 범용 예외를 사용하지 않는가?
- [ ] i18n 메시지는 `MessageUtil.getMessage()` 를 사용하는가? (`MessageSource` 직접 주입 금지)

## 7. 일반 규칙 (07-general-project-convention)

- [ ] Explicit Import인가? (와일드카드 `import java.util.*` 금지)
- [ ] Early Return 패턴을 따르는가?
- [ ] 로깅이 `@Log4j2`/`@Slf4j` + `[ClassName.methodName]` 형식인가?
- [ ] 서비스 메서드 네이밍: `getAll*`, `get*OrElseNull`, `find*`, `exist*` 패턴인가?
- [ ] Copyright 연도가 파일 최초 생성 연도인가?
- [ ] `var` 키워드를 사용하지 않았는가?
- [ ] `System.out.println` / `printStackTrace`가 없는가?

### 7-1. ThreadLocal 유틸리티

- [ ] `TimeZoneContext.getZoneId()`: Controller에서만 호출하는가?
- [ ] `MessageUtil.getMessage()`: Application 이하에서만 사용하는가?
- [ ] `LocaleContextHolder.getLocale()`: Infrastructure에서만 직접 사용하는가?
- [ ] Service 파라미터로 `Locale`을 전달하지 않는가?

### 7-2. 환경변수

- [ ] `application.yml`에 `${env.KEY}` 추가 시 → `application-jp-dev/stg/prd.yml`에 `${KEY}` 존재하는가?
- [ ] `.env` 파일에 로컬용 키-값이 있는가?

### 7-3. DB 마이그레이션

- [ ] 파일명이 `V<YYYYMMDDHHmm>__description.sql` 형식인가?
- [ ] 인덱스 네이밍: `idx_`, `uk_`, `fk_` 접두사인가?
- [ ] 도메인 경계 바깥 테이블에 물리적 FK 생성하지 않았는가?

## 8. 테스트 (08-test-code-convention)

- [ ] 메서드명 영어, `@DisplayName` 한글인가?
- [ ] AssertJ `assertThat()` 사용인가? (JUnit Assertions 금지)
- [ ] Domain/Application: Fake 우선, Spring 컨텍스트 없이 테스트하는가?
- [ ] Web: `@WebMvcTest` + MockMvc인가?
- [ ] Infrastructure: `@DataJpaTest` + Testcontainers(MySQL)인가?
- [ ] `@Autowired` 필드 주입 대신 메서드 파라미터 주입인가?

## 9. 가드레일 (09-guardrails)

- [ ] Testcontainers(MySQL)를 유지하는가? (H2 전환 금지)
- [ ] 기존 obesity 마이그레이션 파일을 수정/삭제하지 않았는가?

## 10. 시큐리티 경로

- [ ] 새 API 엔드포인트 추가 시 `SecurityConstants.airArray`에 등록했는가?

## 11. 이미지 업로드 (12-multipart-image-validation)

- [ ] 이미지 `MultipartFile`에 `@ValidImageFile` 있는가?
- [ ] 직접 파라미터: `@Validated` 클래스 레벨 있는가?
