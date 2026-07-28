---
name: java-performance-reviewer
description: "백엔드 Java Spring Boot 성능 리뷰 전용 스킬 — N+1·JPA·캐시 계층·트랜잭션 propagation·비동기·리소스 누수·GC. 성능 관점 요청 시 자동 트리거, java-composite-reviewer 에이전트 안에서도 조합 가능. Use proactively when the user asks for performance review, slow query analysis, cache/tx design check."
version: "0.2"
last-modified: "2026-07-09"
changelog: |
  v0.2 — 2026-07-09 pasta 6월 사고 흡수 — HikariCP right-size + graceful shutdown 섹션 신설 (`PERF-OPS` 신규 유형). #590·#592(GLOB-521) 반영.
  v0.1 — 2026-07-09 self-code-reviewer v1.11에서 성능 관점 분리·신설. self의 WebClient timeout/4xx 재시도, Soft-delete UNIQUE, 싱글톤 mutable 룰 이관 + N+1·인덱스·캐시 계층·트랜잭션·리소스·로깅 스팸 확장. 하네스 미작성
harness-status: pending
---

# java-performance-reviewer — 성능 관점 코드 리뷰

> 관점 분리 스킬. 도메인 무관 공통 룰은 [[self-code-reviewer]] v1.11이 담당. 이 스킬은 **성능 도메인 특수** 룰만.

---

## 트리거 조건

- 사용자가 "성능 리뷰", "slow query", "N+1", "캐시 설계 검토", "트랜잭션 범위", "리소스 누수" 등을 요청
- `java-composite-reviewer` 에이전트가 통합 리뷰 시 자동 조합
- 새 캐시 계층·비동기·외부 API 통합 커밋 감지 시 능동적 트리거

---

## In-Scope / Out-of-Scope

### In-Scope
- **JPA/DB**: N+1·페치 전략(@OneToMany EAGER 금지)·인덱스·EXPLAIN·JPQL 페이지네이션
- **캐시 계층**: 3층 폴백·write-through·pub-sub 무효화·워밍업·폴링 백스톱 (java-spring-coder v1.11과 짝)
- **트랜잭션·비동기**: propagation(REQUIRES_NEW·격리)·@Async 범위·HikariCP 크기·WebClient timeout·스레드 풀
- **운영 안정성**: HikariCP right-size·graceful shutdown·startup probe·resource cleanup lifecycle (v0.2 신설)
- **리소스**: try-with-resources·Connection/File/Stream 누수·불필요 객체·메모리 누수
- **로깅 스팸**: 매 호출 페이로드 전체 로깅 검출 → 요약 권장 (bug-analyzer v0.3 참고)
- **동시성**: `@Service` 싱글톤 mutable instance field (세션 간 값 혼용)
- **소프트-삭제 + UNIQUE**: DDL 성능 관점 (Functional Unique Index)

### Out-of-Scope
- 보안·인증·PII·시크릿 → **[[java-secure-coding-reviewer]]**
- 4-Tier 계층 경계·Bean 등록·모듈 관계·컨벤션 → **[[java-architecture-reviewer]]**
- FQCN 누수·@Profile 문법·임시 진단 로그·i18n → **[[self-code-reviewer]]** (공통 룰)

---

## Phase 0. 사전 확인

1. **현재 브랜치**: `git branch --show-current` — dev/main이면 대상 없음
2. **변경 범위**: `git diff dev...HEAD --stat` + 커밋 목록
3. **성능 영향 파일 필터**: JPA Entity/Repository/Service·Config/캐시·WebClient·Redis·비동기·SQL 마이그레이션 우선
4. **변경 파일 없으면**: 대상 없음 안내

---

## 하드 가드레일 (성능 관점 AUTO FAIL)

리뷰 통과 불가 항목. 검출되면 즉시 필수 수정.

### G-1. JPA `@OneToMany` / `@ManyToMany` EAGER 사용

| 패턴 | 검출 | 등급 |
|------|------|------|
| `@OneToMany(fetch = FetchType.EAGER)` | grep `@(OneToMany\|ManyToMany).*EAGER` | **AUTO FAIL** |

**이유**: 컬렉션 EAGER는 N+1 확정 유발 + JOIN FETCH 불가 조합 시 카티션 폭발.
**권장**: 명시적 `LAZY` + 필요 시 `@EntityGraph`·`JOIN FETCH` 개별 지정.

### G-2. Repository 메서드가 컬렉션 순회 안에서 호출

| 패턴 | 검출 | 등급 |
|------|------|------|
| `for.*\{[^}]*Repository\.(findBy\|getBy)` — 반복문 안 조회 호출 | **AUTO FAIL** |

**이유**: N+1 확정. 리스트 크기만큼 쿼리 폭증.
**권장**: `findAllByIdIn(...)` 배치 조회 + Map 인덱싱 후 매핑.

### G-3. WebClient 외부 호출 timeout 미설정 (self v1.9 이관)

| 패턴 | 검출 | 등급 |
|------|------|------|
| `WebClient.builder().*build()` 전체에 `responseTimeout`/`CONNECT_TIMEOUT_MILLIS` 없음 | **AUTO FAIL** |

**권장**: connect timeout·read timeout 모두 명시 (예: `HttpClient.create().responseTimeout(Duration.ofSeconds(5))`).

### G-4. Retry 필터에 4xx 포함 (self v1.9 이관)

| 패턴 | 검출 | 등급 |
|------|------|------|
| `Retry.[a-zA-Z]+(...).filter(` 본문에 `WebClientResponseException`만 있고 5xx 한정자 없음 | **AUTO FAIL** |

**이유**: 4xx는 영구 오류. 재시도는 서버 부하만 증가시키고 성공 확률 0.
**권장**: `throwable -> throwable instanceof WebClientResponseException.InternalServerError` 같은 5xx/일시 오류 한정.

### G-5. `@Service` / `@Component` / `@Repository` 싱글톤 mutable instance field (self v1.9 이관)

| 패턴 | 검출 | 등급 |
|------|------|------|
| 싱글톤 스코프 Bean 클래스에 `private non-final non-static` 인스턴스 필드 (Spring 주입 필드 제외) | **AUTO FAIL** |

**이유**: 모든 요청 간 공유 → 세션 간 값 혼용 → 성능·정합성 이중 위험.
**권장**: `AtomicReference<record>` 또는 메서드 인수 전달로 immutable 유지.

---

## 검사 룰 상세

### 1. N+1·인덱스·JPA 페치 (`PERF-JPA`)

#### 검사 항목

| 항목 | 검출 | 권장 |
|------|------|------|
| `@OneToMany` fetch 전략 명시 여부 | 어노테이션에 `fetch` 파라미터 없거나 EAGER | 명시적 `LAZY` |
| `@ManyToOne` fetch 전략 | 기본 EAGER인데 실제로 필요한가? | 필요 시에만 EAGER, 아니면 LAZY 명시 |
| JPQL `JOIN FETCH` + `Page` 조합 | `countQuery` 미분리 | 카운트 쿼리 별도 분리 (self #12와 짝) |
| 반복문 안 Repository 조회 | 위 G-2 | 배치 조회 + Map 인덱싱 |
| `findAll()` 무제한 로드 | 페이지네이션 없이 전량 로드 | `findAll(Pageable)` 강제 |
| 인덱스 없는 컬럼 조회 | 새 `findBy{Column}` + DDL에 인덱스 없음 | 마이그레이션에 인덱스 추가 |
| Native SQL vs JPQL 선택 | 복잡 조인·집계에 JPQL 강제 | 성능 임계 시 Native SQL 허용 |

#### EXPLAIN 확인 가이드

새 쿼리 추가 시 다음 항목 검증 요청:
- 인덱스 사용 여부 (`type=index`/`range`)
- 스캔 행 수 (`rows`)
- 임시 테이블·파일 정렬 발생 여부 (`Using temporary`/`Using filesort`)

로컬 확인 방법: `EXPLAIN SELECT ...` 결과 커밋 메시지에 요약 첨부 권장.

### 2. 캐시 계층 (`PERF-CACHE`)

`java-spring-coder` v1.11 캐시 섹션과 짝. 이 스킬은 **검증 관점**.

#### 검사 항목

| 항목 | 검출 | 권장 |
|------|------|------|
| 3층 폴백 순서 | Redis → DB → 하드코딩 기본값 순서인가? | 어느 층도 예외 전파 금지 (무료 개방 방지) |
| CRUD write-through 시점 | 커밋 **이전** 발행이 있으면 위험 | 커밋 후 발행만 허용 (롤백 시 잘못된 무효화 방지) |
| 부분 갱신 vs 전체 재작성 | Redis SET에 부분 갱신 | 유형별 전체 재작성 (캐시 드리프트 방지) |
| pub-sub 발행 실패 처리 | throw로 전파되면 어드민 API 실패 | 로그 후 흡수 (폴링 백스톱이 자가 치유) |
| 워밍업 임계값 검증 | 기동 시 카운트 검증 없음 | PROTECTED/FULL 등 정책성 캐시는 임계 미달 경보 |
| refresh 실패 로그 레벨 | WARN만 있음 | 연속 실패 시 ERROR + 스택트레이스 (v1.10 예외 로깅 표준) |

#### 캐시 무효화 안티 패턴

```java
// ❌ 커밋 전 발행 — 롤백 시 잘못된 무효화
@Transactional
public void update(Rule rule) {
  repository.save(rule);
  publisher.publish(INVALIDATE);  // 트랜잭션 롤백되어도 발행됨
}

// ✅ 커밋 후 발행 — TransactionSynchronization
@Transactional
public void update(Rule rule) {
  repository.save(rule);
  TransactionSynchronizationManager.registerSynchronization(
    new TransactionSynchronization() {
      public void afterCommit() { publisher.publish(INVALIDATE); }
    });
}
```

### 3. 트랜잭션·비동기·스레드 풀 (`PERF-TX`)

#### 검사 항목

| 항목 | 검출 | 권장 |
|------|------|------|
| `@Transactional` propagation 미명시 | 방어 조회·중복 검사에 기본 REQUIRED | 명시적으로 REQUIRES_NEW 격리 (v1.11-C 짝) |
| 트랜잭션 안 외부 API 호출 | `@Transactional` 메서드에서 WebClient 호출 | 트랜잭션 밖으로 분리 (커넥션 점유 시간 최소화) |
| 트랜잭션 안 대량 작업 | `@Transactional` 안 100+건 순회 | 청킹 + 배치 커밋 |
| `@Async` 스레드 풀 지정 | `@Async` 만 있고 executor 이름 없음 | `@Async("customExecutor")` + `TaskExecutor` Bean 명시 |
| HikariCP 크기 | `maximum-pool-size` 기본값(10) 사용 중 부하 예상 | 부하·CPU·DB 커넥션 예산 기반 산정 |
| CompletableFuture 스레드 풀 | `.supplyAsync(runnable)` 기본 풀 (ForkJoinPool.commonPool) | 커스텀 executor 인자 전달 |
| WebClient connection pool | `create()`만 (기본 500) | 부하 기반 명시 |

#### 트랜잭션 격리 예 (v1.11-C 정본은 java-spring-coder)

```java
// 뱃지 발급이 실패해도 미션 달성은 보존
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void issueBadge(...) { ... }
```

### 4. 리소스 관리 (`PERF-RESOURCE`)

#### 검사 항목

| 항목 | 검출 | 권장 |
|------|------|------|
| `Connection`/`Statement`/`ResultSet` 수동 관리 | `getConnection()` 등 명시 획득에 try-with-resources 없음 | try-with-resources 강제 |
| `InputStream`/`OutputStream` close 누락 | `new FileInputStream(...)` 등 close 코드 없음 | try-with-resources 강제 |
| String concat 반복 (루프) | `for` 안에 `s = s + ...` | `StringBuilder` |
| Boxed primitive 반복 생성 | 반복문 안 `Integer.valueOf(...)` 등 반복 박싱 | primitive 사용 |
| Static Map 무한 캐시 | `private static final Map<> cache` — 크기 상한 없음 | Caffeine·크기 상한 + TTL |
| 불필요 컬렉션 복사 | `new ArrayList<>(list)` 후 read-only 사용 | `List.copyOf` 또는 원본 사용 |

### 5. 로깅 스팸 (`PERF-LOG`)

`bug-analyzer` v0.3 후처리 로깅 원칙과 짝.

#### 검사 항목

| 항목 | 검출 | 권장 |
|------|------|------|
| 매 호출 페이로드 전체 로깅 | `log.info("... {}", request)` — 대용량 DTO 인자 | 호출자·건수·요약 (`log.info("saved {} items for {}", count, userId)`) |
| 반복문 안 로그 | `for` 안 `log.info` | 요약 로그 or level 낮추기 (DEBUG) |
| INFO 레벨 남발 | 진입·종료 매 호출 INFO | 통계는 DEBUG, 예외 상황만 INFO |
| 문자열 concat in log | `log.info("id=" + id)` | `{}` placeholder |

### 6. 운영 안정성 (`PERF-OPS`, v0.2 신설)

pasta #590·#592 (GLOB-521, 2026-06-23) 흡수. HikariCP right-size + graceful shutdown lifecycle 검사.

#### 검사 항목

| 항목 | 검출 | 권장 |
|------|------|------|
| HikariCP `maximum-pool-size` 기본값(10) 유지 | 부하 예상 대비 미조정 | 공식 참고: `((core_count * 2) + effective_spindle_count)` 또는 DB 커넥션 예산 기반 산정. 프로덕션은 트래픽 측정 후 조정 |
| HikariCP `minimum-idle` 미명시 | 기본이 max와 동일 → idle 커넥션 다수 유지 | 워밍 이후 유휴 커넥션 관리 목적이면 `minimum-idle` 별도 명시 |
| `connection-timeout`·`idle-timeout`·`max-lifetime` 조정 | 기본값 그대로 | DB 서버 wait_timeout보다 짧게 설정 (max-lifetime < wait_timeout) |
| `spring.lifecycle.timeout-per-shutdown-phase` 미설정 | graceful shutdown 없음 | 배포·롤링 업데이트 시 in-flight 요청 완료 위해 명시 (예: `30s`) |
| `server.shutdown: graceful` 미설정 | 즉시 kill로 요청 유실 | `graceful` 명시 |
| Kubernetes startup probe·readiness 지연 | 콜드스타트 무거운 앱에 짧은 probe → probe 실패 배포 | `initialDelaySeconds`·`failureThreshold`·`periodSeconds` 완화 (admin #588 사례: cpu-boost + 5초 간격 48회 재시도) |
| `@PreDestroy`·`SmartLifecycle` 미사용 | 외부 리소스 (Redis 리스너·스케줄러) shutdown hook 없음 | 명시적 close 로직 등록 |

#### 참고

- HikariCP 크기: DB 서버 max_connections 대비 앱 인스턴스 수 × pool size 여유 산정 필수
- graceful shutdown lifecycle: Spring Boot 2.3+ 기본 지원, `graceful` 값 명시로 활성

### 7. Soft-delete + UNIQUE 충돌 (self v1.9 이관)

| 패턴 | 검출 | 권장 |
|------|------|------|
| `deleted_at`/`is_deleted` 컬럼 + 일반 UNIQUE INDEX | Functional Unique Index 아님 | MySQL 8.0.13+: `CASE WHEN deleted_at IS NULL THEN col ELSE NULL END` |

**이유**: soft-delete 후 같은 값 재등록 시 UNIQUE 충돌로 실패.

---

## 리포트 형식

self-code-reviewer와 동일 형식 유지. `유형`·`등급`만 성능 특화.

```markdown
## 성능 관점 리뷰 결과 (java-performance-reviewer v0.1)

**브랜치**: {현재 브랜치}
**비교 기준**: dev
**커밋 수**: {N}개
**변경 파일**: {N}개 (성능 영향 파일 {M}개)

### AUTO FAIL (성능 하드 가드레일 위반)

| # | 유형 | 파일:위치 | 위반 | 권장 수정 |
|---|------|----------|------|-----------|
| 1 | PERF-JPA | Foo.java:23 | @OneToMany EAGER | LAZY 명시 + @EntityGraph 부분 로드 |

### 필수 수정 (Critical / High)

| # | 유형 | 등급 | 파일:위치 | 내용 | 수정 방향 |
|---|------|------|----------|------|-----------|
| 1 | PERF-TX | High | Bar.java:45 | @Async 스레드 풀 미지정 | @Async("customExecutor") + Executor Bean 명시 |

### 권장 개선 (Medium / Low / Info)

| # | 유형 | 등급 | 파일:위치 | 내용 | 개선 방향 |
|---|------|------|----------|------|-----------|
| 1 | PERF-LOG | Low | Baz.java:78 | 페이로드 전체 로깅 | 호출자·건수 요약 |

### 검사 통과 항목
- JPA fetch 전략: OK (모두 LAZY)
- WebClient timeout: OK
- 트랜잭션 격리: OK
- ...
```

**등급 정의**:
- **AUTO FAIL**: 하드 가드레일 위반. 리뷰 통과 불가.
- **Critical**: 운영 중단 위험 (예: 커넥션 누수, 무한 캐시)
- **High**: 명백한 성능 저하 (예: N+1, 4xx retry)
- **Medium**: 부하 상승 시 문제 (예: @Async 기본 풀, 대용량 페이로드 로깅)
- **Low**: 잠재적 낭비 (예: 반복문 안 String concat, 불필요 컬렉션 복사)
- **Info**: 참고 (예: EXPLAIN 확인 권장)

**신규 유형 `PERF-OPS`** (v0.2): HikariCP 크기·graceful shutdown·startup probe·resource cleanup lifecycle. 대부분 **권장 사항 성격**이라 AUTO FAIL 아님, Medium/High 등급.

---

## 가드레일

### 하드 가드레일 (절대 위반 불가)

- **코드 변경 금지** — 이 스킬은 **읽기 전용**
- **커밋/push 금지** — 리뷰 결과 보고만
- **git stash 금지**
- **관점 침범 금지** — 보안·아키텍처·컨벤션 지적은 해당 스킬로 라우팅 안내만

### 소프트 가드레일

- 변경되지 않은 기존 코드에는 관여 최소화
- 정적 분석 한계 인정 — 실제 EXPLAIN·프로파일링 결과가 필요한 항목은 "검증 권장" 등급으로 보고
- False positive 회피 (예: 테스트 fixture, 배치 파라미터 DTO는 검사 완화)

---

## 자기 검증 체크리스트

리뷰 완료 후 반드시 확인:

1. [ ] **범위 정확성**: dev 이후 변경 파일 중 성능 영향 파일만 대상으로 했는가?
2. [ ] **JPA fetch**: `@OneToMany`/`@ManyToMany` 신규·변경 필드의 fetch 전략을 명시적으로 확인했는가? EAGER 검출 시 AUTO FAIL?
3. [ ] **반복문 조회**: 변경 파일의 for/stream 안에 Repository 조회 호출이 있는지 grep으로 확인했는가?
4. [ ] **WebClient timeout**: 새/변경된 WebClient 생성에 connect/read timeout 명시했는가? Retry 필터의 5xx 한정?
5. [ ] **트랜잭션 격리**: 방어 조회·중복 검사·이벤트 리스너에 `REQUIRES_NEW` 명시 여부?
6. [ ] **캐시 계층**: 신규 캐시 코드에 3층 폴백·write-through 커밋 후 발행·유형별 전체 재작성·워밍업 임계·발행 실패 흡수 5원칙 확인?
7. [ ] **@Async 스레드 풀**: `@Async` 사용 시 executor 이름 지정? CompletableFuture도 커스텀 풀?
8. [ ] **리소스 관리**: 새 Connection/Stream 관련 코드에 try-with-resources 강제했는가?
9. [ ] **로깅 스팸**: 신규 로그에 대용량 페이로드 인자 있으면 요약 권장? 반복문 안 로그 level 낮춤?
10. [ ] **관점 침범 회피**: 검출 항목이 성능 관점이 맞는가? 아키텍처·보안·컨벤션이면 해당 스킬로 라우팅 안내만 하고 이 스킬 리포트에서 제외?
11. [ ] **운영 안정성** (v0.2): 새 애플리케이션 모듈이나 인프라 설정 변경 시 HikariCP right-size·graceful shutdown·startup probe·resource cleanup 4항목을 확인했는가?

---

## 참조 인덱스

| 파일 | 내용 |
|------|------|
| `references/evaluation-rubric.md` | 평가 루브릭 (100점, AUTO FAIL 조건) — **미작성** |

**짝 스킬**:
- [[java-spring-coder]] v1.11 — 캐시 3층 폴백·pub-sub 무효화·트랜잭션·WebClient timeout 정본
- [[java-secure-coding-reviewer]] v0.1 — 보안 관점 (PII 로깅과 성능 로깅 스팸 접점 있음, 상호 참조)
- [[java-architecture-reviewer]] v0.1 — 4-Tier·의존성·모듈 관계 (성능 리팩터가 계층 위반이면 여기로 라우팅)
- [[self-code-reviewer]] v1.11 — 공통 룰 오케스트레이터
- [[bug-analyzer]] v0.3 — 후처리 로깅 원칙과 짝
