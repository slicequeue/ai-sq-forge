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
