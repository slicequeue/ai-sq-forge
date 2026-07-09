---
name: java-architecture-reviewer
description: "백엔드 Java Spring Boot 아키텍처·컨벤션 리뷰 전용 스킬 — 4-Tier 계층·Bean 관리·모듈 관계·패턴 준수·pasta-rules 컨벤션. 아키텍처 관점 요청 시 자동 트리거, java-composite-reviewer 에이전트 안에서도 조합 가능. Use when the user asks for architecture review, layering audit, Bean/module boundary check, or convention compliance."
version: "0.1"
last-modified: "2026-07-09"
changelog: "v0.1 — 2026-07-09 self-code-reviewer v1.11에서 아키텍처·컨벤션 관점 분리·신설. self의 Bean Qualifier cross-module·구현체 모듈·FQCN·Bean 이름 매직 스트링 룰 이관 + pasta-rules 참조 + 모듈 관계·@Entity 스캔 경계·패턴 준수 확장. java-spring-coder v1.11의 4-Tier·공용 모듈 @Entity 회피·@ConditionalOnBean 회피 하드 가드레일과 짝."
harness-status: pending
---

# java-architecture-reviewer — 아키텍처·컨벤션 관점 리뷰

> 프로젝트 규칙 원본(포지: `forge/common/pasta-rules/`, 실전 배포: `.claude/rules/`) 을 **직접 Read하고 대조**한다. 룰 본문을 복사하지 않는다.

---

## 개요·트리거

- **트리거 키워드**: 아키텍처 리뷰, 계층·의존성 검사, 모듈 경계, Bean 관리, `@Qualifier`, `@Bean`, 패키지 구조, 컨벤션 준수, `import` 관계, 순환 의존, `@Entity` 스캔
- **실행 위치**: dev 이후 변경 코드에 대해 아키텍처 관점 리뷰만 수행
- **자동 트리거**: 사용자가 "아키텍처 관점만" 요구 시 단독 호출. 전체 리뷰는 `java-composite-reviewer` 에이전트가 여러 관점을 조합
- **다른 관점과 분리**: 보안 → `java-secure-coding-reviewer`, 성능 → `java-performance-reviewer`, 공통 룰(@Profile 문법·임시 로그·Hibernate Session 오염 등) → `self-code-reviewer`

---

## In-Scope / Out-of-Scope

**In-Scope**
- 4-Tier 계층 경계(Web/Application/Domain/Infrastructure) + import 방향
- Bean 등록: `@Bean` 이름 상수화 · `@Qualifier` cross-module 정합성 · `@ConditionalOnBean` vs `@Profile` 게이팅
- 모듈 관계: 공용 모듈 배치 · `@Entity` 스캔 경계 · admin/api/batch 격리 · 순환 의존
- 패턴 준수: DDD · 헥사고날 · 포트-어댑터 · 명명 컨벤션
- pasta-rules 컨벤션 참조: 01/02/03/04/05/07/13/14/19 등
- FQCN 인라인 사용 검출 (import 위반)

**Out-of-Scope**
- 보안(KISA·OWASP·PII·시크릿) → secure-coding
- 성능(N+1·캐시·리소스) → performance
- 문법 오류(@Profile `&&`) · 임시 로그 · 광범위 catch · Hibernate Session 오염 → self
- i18n / Locale → self 또는 tolgee

---

## Phase 0. 사전 확인

1. **현재 브랜치**: `git branch --show-current` — dev/main이면 리뷰 대상 없음
2. **비교 기준**: 기본 `dev`. 사용자 지정 시 그것 사용
3. **변경 범위**: `git log dev..HEAD --oneline` + `git diff dev...HEAD --stat`
4. **admin 모듈 포함 여부**: 변경 파일에 `admin/` 경로가 있으면 → 13/14 규칙 로드, 01/04 4-Tier를 admin에 맹목 적용 금지
5. **rules 위치 결정**: 대상 프로젝트가 실전 배포된 상태면 `.claude/rules/`, forge 자체 개발 중이면 `forge/common/pasta-rules/`

---

## 하드 가드레일 (절대 위반 불가)

### HG-1. Bean Qualifier cross-module 정합성 — **AUTO FAIL**
`@Qualifier(CONST)`로 참조되는 상수는 그 상수를 사용하는 **모든 애플리케이션 모듈**에 `@Bean(CONST)` 정의가 있어야 한다. 하나라도 메서드명 기반 등록만 있으면 `No qualifying bean` 기동 실패 → AUTO FAIL. (self v1.10에서 이관, 3회 재발 방지: 5월 api → 6/16 batch·batch-app #593 → 6/19 admin #588)

### HG-2. 4-Tier 계층 위반 — **AUTO FAIL**
Domain이 Infrastructure/Web을 import하거나, Application이 Web을 import하는 등 **의존성 방향 역행**. `01-architecture-convention.md` 정본 참조. 4계층 정의:
- Web → Application → Domain
- Infrastructure → Domain (구현체가 도메인 포트 구현)
- Domain은 그 어느 것도 import하지 않는다 (외부 의존성 0)

### HG-3. 공용 모듈에 `@Entity` 배치 — **AUTO FAIL**
`common/`, `shared/` 등 여러 애플리케이션 모듈이 의존하는 공용 모듈에 `@Entity` 두면 `@EntityScan` 경계 충돌로 기동 실패. JdbcClient/JdbcRepository 기반 Reader 사용 요구. (`java-spring-coder` v1.10 짝 가드레일)

### HG-4. FQCN 인라인 사용 — **필수 수정**
코드 본문에 `com.x.y.Z` 형태 패키지 경로 직접 노출 금지. import 문에만 존재해야 한다. 메인+테스트 코드 모두 대상. (self v1.5에서 이관, PR #527 사고 패턴)

---

## 핵심 규칙

### 1. 4-Tier 계층 경계 검사

**정본 규칙**: `01-architecture-convention.md`, `19-architecture-boundaries.md`

| 검사 항목 | 절차 |
|----------|------|
| import 방향 | 각 계층 클래스가 상위 계층 클래스를 import하는지 grep |
| Repository 위치 | Domain 인터페이스 + Infrastructure 구현체 배치 (`04-repository-pattern-convention.md`) |
| Service 반환 타입 | JPA 엔티티가 Service 밖으로 노출되는지 (Application이 Domain 엔티티로 변환) |
| Client/ClientService/ACL | 외부 시스템 어댑터는 ACL 계층 (`01-architecture-convention.md`) |
| 타 도메인 Repository import | 다른 도메인의 `*JpaRepository`/`*JpaEntity`/`*RepositoryImpl` 직접 import 금지 (`19-architecture-boundaries.md`) |

**admin 모듈 예외**: `13-admin-module-overview.md` — 레이어 혼합 구조 정상, 4-Tier 위반으로 오판 금지.

### 2. Bean 관리 검사

**정본 규칙**: `07-general-project-convention.md`, `19-architecture-boundaries.md`

| 검사 항목 | 절차 |
|----------|------|
| `@Bean` 이름 상수화 | 동일 빈 이름 문자열이 3회 이상 반복 → 상수 추출 권장. 등록자+소비자가 다른 모듈이면 `shared/.../constant/{Domain}BeanNameConstants` |
| Qualifier cross-module | HG-1 참조 — 상수 참조하는 모든 모듈에 `@Bean(CONST)` 존재 검증 |
| 게이팅 방식 | `@ConditionalOnBean`은 Bean 로드 순서에 취약 → `@Profile` 선호 (라이브러리성 auto-config 예외) |
| 인터페이스 구현체 모듈 등록 | 새 인터페이스 주입 시 해당 모듈 스캔 경로에 구현체 존재 여부 grep (self v1.10 이관, #597 재발 방지) |
| `@Primary` 사용 | Qualifier 없이 매칭될 때만 명시 |

**Bean 이름 매직 스트링 검사 위치**: `@Bean(...)`, `@Bean(name=...)`, `@Qualifier("...")`, `@MockBean(name=...)`, `@DependsOn("...")`, `BeanFactory#getBean("...")`, `ApplicationContext#getBean("...")`

### 3. 모듈 관계 검사

| 검사 항목 | 절차 |
|----------|------|
| 공용 모듈 배치 | `common/`, `shared/`에 `@Entity`/`@Service` 배치 여부 검사 (HG-3 짝) |
| `@Entity` 스캔 경계 | `@EntityScan(basePackages=...)`이 다른 모듈의 엔티티를 스캔하는지 확인 |
| admin/api/batch 격리 | 각 애플리케이션 모듈이 다른 모듈의 내부 클래스를 import하는지 |
| 순환 의존 탐지 | 모듈 그래프에서 A→B→A 경로 감지 (gradle 의존성 그래프 or grep) |
| shared 모듈 경계 | shared에는 상수·enum·Bean 이름·DTO만 허용, 비즈니스 로직 금지 |

### 4. 패턴 준수 검사

**정본 규칙**: `02-domain-entity-convention.md`, `03-jpa-entity-convention.md`, `04-repository-pattern-convention.md`, `05-dto-web-layer-convention.md`

| 검사 항목 | 절차 |
|----------|------|
| Domain Entity class | record 금지, class 사용, primitive/wrapper, `@Getter` + `@EqualsAndHashCode`, NOT NULL 생성자 검증 |
| JPA Entity | `@Entity`/`@Table`/`@Getter`, `toEntity()`/`from()` 변환, `@Builder` 생성자 레벨만 |
| Repository 3단계 | Domain `*Repository` — Infra `*JpaRepository` — Infra `*RepositoryImpl` |
| DTO record | `*Request`/`*Response`/`*InDto`/`*OutDto`, `of`/`from`/`to` 팩토리, Controller는 Application만 주입 |
| 명명 컨벤션 | 서비스 메서드 · 클래스 · 패키지 (`07-general-project-convention.md` §명명) |
| Controller | `@Controller` (admin Thymeleaf) vs `@RestController` (api) 분리 |

### 5. pasta-rules 컨벤션 검사

**실행 시 반드시 Read**할 규칙 파일 (변경 대상 유형에 따라 선택):

| rule 파일 | 적용 시점 |
|-----------|----------|
| `01-architecture-convention.md` | 항상 (alwaysApply) |
| `02-domain-entity-convention.md` | Domain Entity 변경 시 |
| `03-jpa-entity-convention.md` | JPA Entity 변경 시 |
| `04-repository-pattern-convention.md` | Repository 변경 시 |
| `05-dto-web-layer-convention.md` | Controller/DTO 변경 시 |
| `07-general-project-convention.md` | 항상 (alwaysApply) |
| `12-multipart-image-validation.md` | MultipartFile 변경 시 |
| `13-admin-module-overview.md` | `admin/**` 변경 시 |
| `14-admin-thymeleaf-layout-convention.md` | admin 템플릿 변경 시 |
| `19-architecture-boundaries.md` | 항상 (alwaysApply) |

**주의**: 06(예외 처리)은 self 또는 secure-coding, 08(테스트)은 java-layered-unit-testing, 09/10/11/17/18(가드·워크플로)은 self 또는 프로젝트 공통 → 이 스킬은 위 10개만 담당.

### 6. FQCN 인라인 검출 (HG-4 상세)

`self-code-reviewer` v1.5·v1.7 룰을 이 스킬로 이관. 검출 대상:

- `new x.y.Z("...")` — 예외/객체 인스턴스 생성 인라인
- `isInstanceOf(x.y.Z.class)` / `MyClass.class` 리터럴
- `x.y.Z variable = ...` / 매개변수 / 제네릭 타입 인자 / 캐치 절
- `com.x.y.Z.ENUM_CONST` — enum 상수 접근
- `java.lang.reflect.Field` 등 표준 라이브러리 인라인

**검사 제외**: 어노테이션 인자 문자열, SpEL, JPQL/SQL 쿼리, 로그 메시지 본문.

---

## 실행 프로토콜

### Step 1. 변경 범위 수집
```bash
git log dev..HEAD --oneline
git diff dev...HEAD --stat
git diff dev...HEAD -- {path}
```

### Step 2. 규칙 로드
- 변경 파일 유형별로 위 "pasta-rules 컨벤션 검사" 표에서 필요한 규칙 Read
- **본문 복사 금지** — 참조·인용만

### Step 3. 항목별 검사
5개 카테고리(4-Tier / Bean / 모듈 / 패턴 / 컨벤션) + FQCN을 순서대로 대조.

### Step 4. 리포트 작성
아래 "리포트 형식" 참조.

---

## 리포트 형식

```markdown
## 아키텍처·컨벤션 리뷰 결과

**브랜치**: {현재 브랜치}
**비교 기준**: dev
**커밋 수**: {N} · **변경 파일**: {N}
**로드된 규칙**: {01, 07, 19, ...}

### AUTO FAIL (기동/컴파일 실패 확정)

| # | 유형 | 파일:라인 | 위반 | 등급 |
|---|------|----------|------|------|
| 1 | ARCH-BEAN | batch/BatchOAuth2Configuration.java:63 | @Bean 상수 미명시 (cgm이 @Qualifier(CONST) 참조) | AUTO FAIL |

### 필수 수정 (Critical/High)

| # | 유형 | 파일:라인 | 위반 | 수정 방향 |
|---|------|----------|------|-----------|
| 1 | ARCH-4TIER | api/.../DomainX.java:42 | Domain이 Infrastructure import | 포트 인터페이스로 반전 |

### 권장 개선 (Medium/Low/Info)

| # | 유형 | 파일:라인 | 개선 | 근거 |
|---|------|----------|------|------|
| 1 | ARCH-PATTERN | api/.../XRepositoryImpl.java | 04 규칙 - 3단계 Repository 명명 미준수 | 04-repository-pattern-convention.md |

### 검사 통과 항목
- 4-Tier 의존성 방향: OK
- Bean Qualifier cross-module: OK (검증 상수 {N}건)
- 순환 의존: 없음
- FQCN 인라인: 없음
```

**유형 (Type prefix)**:
- `ARCH-4TIER` : 계층 경계·import 방향
- `ARCH-BEAN` : Bean 등록·Qualifier·게이팅
- `ARCH-MODULE` : 모듈 관계·@Entity·순환 의존
- `ARCH-PATTERN` : DDD·Repository·DTO·명명
- `ARCH-CONVENTION` : pasta-rules 개별 컨벤션

**등급**: `AUTO FAIL` > `Critical` > `High` > `Medium` > `Low` > `Info`

---

## 가드레일

### 하드 가드레일 (읽기 전용)
- **코드 변경 금지** — 리뷰 결과 보고만
- **커밋/push/stash 금지**
- **rules 원본 수정 금지** — 참조만

### 소프트 가드레일
- 변경되지 않은 기존 코드에 대한 리뷰 최소화
- 규칙 위반이 아닌 스타일 이슈는 `Info` 등급으로만 표기
- admin 모듈 변경 시 13/14 규칙 우선, 01/04 4-Tier를 맹목 적용하지 않음
- 동일 유형 위반이 5건 이상이면 개별 나열 대신 요약 + 대표 3건만

---

## 자기 검증 체크리스트

리뷰 완료 후 반드시 확인:

1. [ ] **범위 정확성**: dev 이후 변경 파일만 리뷰했는가?
2. [ ] **규칙 실제 Read**: pasta-rules 파일 경로만 안 보고 실제 Read하고 인용했는가?
3. [ ] **HG-1 Bean Qualifier cross-module**: 새 `@Bean`/`@Qualifier(CONST)` 있으면 상수 참조 모든 모듈에 `@Bean(CONST)` 정의 grep 검증했는가? 하나라도 미준수면 AUTO FAIL?
4. [ ] **HG-2 4-Tier 위반**: Domain/Application/Web/Infrastructure import 방향 위반 검사했는가? admin은 13 규칙 예외 적용?
5. [ ] **HG-3 공용 모듈 @Entity**: `common/`·`shared/`에 `@Entity` 배치 검사했는가?
6. [ ] **HG-4 FQCN 인라인**: 코드 본문에 `com.x.y.Z` / `x.y.Z.ENUM_CONST` / `java.lang.reflect.*` 인라인 있는가? 메인+테스트 모두?
7. [ ] **Bean 이름 매직 스트링**: 동일 문자열 3회 이상 반복이면 상수 추출 권장 보고?
8. [ ] **@ConditionalOnBean vs @Profile**: 설정 게이팅에 `@ConditionalOnBean` 있으면 `@Profile` 대체 검토 권장?
9. [ ] **모듈 순환 의존**: A→B→A 경로 검사했는가? gradle 의존성 그래프 또는 grep?
10. [ ] **out-of-scope 존중**: 보안·성능·문법 오류·Hibernate Session 오염·i18n을 이 스킬이 아닌 담당 스킬로 안내했는가? (본인 관점 밖 위반은 "타 스킬 참조"로만 표시)

---

## 참조 인덱스

| 파일 | 내용 |
|------|------|
| `references/evaluation-rubric.md` | 평가 루브릭 (100점, AUTO FAIL 조건) — 하네스 작성 시 추가 |
| `references/pattern-detail.md` | DDD·헥사고날 상세 패턴 (필요 시 분리) |

**짝 스킬**
- `self-code-reviewer` v1.11 — 공통 룰(@Profile 문법, 임시 로그, Hibernate Session 오염, 입력 검증 등)
- `java-spring-coder` v1.11 — 코드 생성 시점 4-Tier·@Entity 회피·@Profile 선호 하드 가드레일 (짝)
- `java-secure-coding-reviewer` — 보안 관점 (별도 스킬)
- `java-performance-reviewer` — 성능 관점 (별도 스킬)
- `java-composite-reviewer` — 3개 관점 조합 에이전트
