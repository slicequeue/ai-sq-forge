---
name: java-performance-reviewer
version: 0.2
harness-version: 0.2
last-modified: 2026-07-29
---

# java-performance-reviewer 테스트 케이스

## TC-1: Happy Path — N+1 검출 (반복문 안 Repository 조회)

- **입력 프롬프트**: "성능 관점 리뷰해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/feat/glob-700-user-summary`\n- 변경 파일:\n  - `api/src/main/java/.../UserSummaryService.java` (신규)\n  - `api/src/main/java/.../UserRepository.java` (신규 메서드 추가)\n- 핵심 diff:\n```java\n@Service\npublic class UserSummaryService {\n  private final UserRepository userRepository;\n  private final BadgeRepository badgeRepository;\n\n  public List<UserSummary> summarize(List<Long> userIds) {\n    List<UserSummary> result = new ArrayList<>();\n    for (Long userId : userIds) {\n      User user = userRepository.findById(userId).orElseThrow();\n      List<Badge> badges = badgeRepository.findByUserId(userId);\n      result.add(new UserSummary(user, badges));\n    }\n    return result;\n  }\n}\n```\n- `UserRepository.findById`는 표준, `BadgeRepository.findByUserId`는 신규"
- **기대 결과**:
  - **G-2 AUTO FAIL**: 반복문 안 `userRepository.findById(...)` + `badgeRepository.findByUserId(...)` 두 호출 검출
  - 유형: `PERF-JPA`
  - 권장 수정: `findAllByIdIn(userIds)` + `findAllByUserIdIn(userIds)` 배치 조회 후 Map 인덱싱
  - 관점 침범 없음 (아키텍처·보안 지적 X)
  - 자기 검증 10항목 체크
- **검증 기준**:
  - [ ] G-2 AUTO FAIL 검출 (반복문 안 조회)
  - [ ] `PERF-JPA` 유형 정확
  - [ ] 권장 수정에 `findAllByIdIn`/`findAllByUserIdIn` 등 배치 조회 방식 제안
  - [ ] Map 인덱싱 후 매핑 언급
  - [ ] 리포트 3분류(AUTO FAIL/필수/권장) 표 준수
  - [ ] `@OneToMany` 없으므로 G-1은 정상 통과
  - [ ] 관점 침범 없음 (Service 계층·Repository 명명 등 지적 X — architecture 소관)
- **유형**: happy-path

---

## TC-2: Happy Path — WebClient timeout 미설정 (G-3)

- **입력 프롬프트**: "성능 관점 리뷰해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/feat/glob-710-external-api-client`\n- 변경 파일: `api/src/main/java/.../ExternalPricingClient.java`, `api/src/main/java/.../ExternalPricingClientConfig.java` (신규 2개)\n- 핵심 diff:\n```java\n@Configuration\npublic class ExternalPricingClientConfig {\n  @Bean\n  public WebClient externalPricingWebClient() {\n    return WebClient.builder()\n        .baseUrl(\"https://api.pricing.external.com\")\n        .build();\n  }\n}\n\n@Component\npublic class ExternalPricingClient {\n  private final WebClient webClient;\n\n  public Mono<PricingResponse> getPricing(String sku) {\n    return webClient.get()\n        .uri(\"/pricing/{sku}\", sku)\n        .retrieve()\n        .bodyToMono(PricingResponse.class)\n        .retryWhen(Retry.backoff(3, Duration.ofSeconds(1)));\n  }\n}\n```"
- **기대 결과**:
  - **G-3 AUTO FAIL**: WebClient에 connect/read timeout 미설정
  - **G-4 AUTO FAIL**: Retry 필터에 4xx/5xx 한정자 없음 (모든 예외 재시도)
  - 유형: `PERF-TX` (두 항목 모두)
  - 권장 수정:
    - G-3: `HttpClient.create().option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 3000).responseTimeout(Duration.ofSeconds(5))` 명시
    - G-4: `.retryWhen(Retry.backoff(3, ...).filter(throwable -> throwable instanceof WebClientResponseException.InternalServerError))` 5xx 한정
  - 자기 검증 10항목 체크
- **검증 기준**:
  - [ ] G-3 AUTO FAIL 검출
  - [ ] G-4 AUTO FAIL 검출
  - [ ] `PERF-TX` 유형 정확
  - [ ] connect timeout·read timeout 둘 다 언급
  - [ ] 5xx 한정 필터 예시 제시
  - [ ] 하나만 검출하고 다른 것 놓치면 AUTO FAIL
- **유형**: happy-path

---

## TC-3: Edge Case — 캐시 write-through 판정 애매 (부분 갱신 vs 전체 재작성)

- **입력 프롬프트**: "성능 관점 리뷰해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/refac/glob-720-cache-update-strategy`\n- 변경 파일: `api/src/main/java/.../PricingRuleCacheService.java`\n- 핵심 diff:\n```java\n@Service\npublic class PricingRuleCacheService {\n  private final StringRedisTemplate redisTemplate;\n  private final PricingRuleRepository repository;\n\n  @Transactional\n  public void updateRule(PricingRule rule) {\n    repository.save(rule);\n    // 부분 갱신: 변경된 rule 하나만 Redis SET에 update\n    redisTemplate.opsForSet().add(\"pricing:rules:\" + rule.getType(), rule.getPattern());\n  }\n}\n```\n- 기존 캐시는 유형별 전체 재작성 방식이었음 (java-spring-coder v1.11 짝 룰)\n- 이번 커밋은 성능 최적화 목적으로 부분 갱신으로 전환"
- **기대 결과**:
  - **G가 아닌 필수 수정 (High)**: 부분 갱신은 캐시 드리프트 위험. 유형별 전체 재작성 권장
  - 유형: `PERF-CACHE`
  - 리스크 설명:
    - 부분 갱신 시 삭제·rename된 rule은 캐시에 남음 (드리프트)
    - 다중 인스턴스 환경에서 동시성 문제 가능
    - java-spring-coder v1.11 캐시 정책과 충돌 → 짝 스킬 참조 안내
  - 사용자 판단 요청: "성능 최적화가 정말 필요한가? 전체 재작성 비용이 얼마?"
  - 대안:
    - 유형별 전체 재작성 유지 (안전)
    - 또는 delete + add를 원자적 pipeline으로 (드리프트 방지)
  - AUTO FAIL은 없음 (하드 가드레일 아님)
- **검증 기준**:
  - [ ] AUTO FAIL 아님 (부분 갱신은 하드 가드레일 위반 아님)
  - [ ] `PERF-CACHE` 필수 수정으로 분류
  - [ ] 드리프트 위험 명시
  - [ ] 다중 인스턴스 동시성 리스크 언급
  - [ ] java-spring-coder v1.11 정본 참조 안내
  - [ ] 사용자에게 판단 근거(성능 vs 안전) 요청
  - [ ] 대안 2개 제시
- **유형**: edge-case

---

## TC-4: Negative — 사용자가 "N+1 두자, 트래픽 낮음" 요구 (가드레일 우선)

- **입력 프롬프트**: "성능 리뷰 결과 N+1 검출됐다고 했는데, 이거 트래픽 낮은 배치라서 무시하고 배포하려고. 리포트에서 AUTO FAIL 빼고 넘어가도 되지?\n\n(맥락) TC-1과 동일 diff. 사용자가 AUTO FAIL 완화 요청."
- **기대 결과**:
  - 스킬이 **AUTO FAIL 유지 거절**
  - 사유 명확 설명:
    - 하드 가드레일 G-2는 트래픽 관계없이 유지 (배치라도 데이터 볼륨 예측 불가)
    - 배포 후 트래픽·데이터 증가 시 즉시 사고 위험
    - 리포트에서 AUTO FAIL 삭제는 이 스킬 권한 밖 (읽기 전용)
    - 사용자가 정말 무시하려면 리포트 그대로 두고 상위 결정(팀 리드 승인 등)에서 판단
  - 대안 제시:
    - N+1 수정 (배치 조회) — 30분 작업
    - 임시 배포 후 후속 이슈로 추적 — 리포트에는 AUTO FAIL 유지, 별도 티켓 발행
  - 사용자 요구 그대로 수용하지 않음
- **검증 기준**:
  - [ ] AUTO FAIL 리포트에서 삭제하지 않음
  - [ ] 가드레일 번호(G-2) 명시하며 거절
  - [ ] "트래픽 낮음"이 완화 사유가 안 되는 이유 설명
  - [ ] 대안 2개 제시 (수정 vs 후속 이슈)
  - [ ] "이 스킬은 읽기 전용, 리포트 삭제 권한 없음" 명시
- **유형**: negative

---

## TC-5: Negative — WebClient timeout 없이 배포 강행 요구 (가드레일 우선)

- **입력 프롬프트**: "TC-2 리뷰 결과 WebClient timeout 미설정 AUTO FAIL 나왔는데, 외부 API가 원래 응답 빠르니까 timeout 없어도 문제없어. AUTO FAIL 등급 낮춰줘.\n\n(맥락) TC-2와 동일 diff. 사용자가 AUTO FAIL 완화 요청."
- **기대 결과**:
  - 스킬이 **AUTO FAIL 유지 거절**
  - 사유 명확 설명:
    - 하드 가드레일 G-3는 외부 API 신뢰도 관계없이 유지
    - timeout 없으면 외부 장애 시 pod 스레드 전체 고갈 → 자체 서비스 다운
    - 외부 API가 "원래 빠르다"는 것은 보장 없음 (SLA·네트워크·재해)
    - AUTO FAIL 등급 조정은 이 스킬 권한 밖 (하드 가드레일 정의 = java-spring-coder v1.11 정본)
  - 대안 제시:
    - 명시적 timeout 추가 (5초·10초 등) — 5분 작업
    - 외부 API 명세 문서 링크 제출 + 팀 리드 승인 시에만 특별 케이스 처리
  - Retry 4xx 포함(G-4)도 같이 지적, 함께 수정 권장
- **검증 기준**:
  - [ ] AUTO FAIL 등급 낮추지 않음
  - [ ] 가드레일 번호(G-3) 명시하며 거절
  - [ ] timeout 없을 때 발생하는 사고 시나리오(스레드 고갈) 명시
  - [ ] "외부 API 빠름"이 완화 사유가 안 되는 이유 설명
  - [ ] G-4 함께 지적 (동일 파일에 있으므로)
  - [ ] 대안 2개 제시 (즉시 수정 vs 명세 문서·승인)
- **유형**: negative

---

## TC-6: Happy Path — HikariCP 기본값 + graceful shutdown 미설정 (PERF-OPS)

- **입력 프롬프트**: "성능 관점 리뷰해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/feat/glob-730-new-service-config`\n- 변경 파일: `api/src/main/resources/application-prd.yml` (신규 5줄)\n- 배경: pasta 사고 #592 (GLOB-521, 2026-06-23) — HikariCP right-size 미설정 + graceful shutdown 미적용으로 배포 시 요청 유실\n- 핵심 diff:\n```yaml\nspring:\n  datasource:\n    url: jdbc:mysql://prd-db.internal:3306/pasta\n    username: pasta_api\n    password: ${DB_PASSWORD}\n    # 커넥션 풀 설정 없음 — Spring Boot 기본값 (max=10) 사용\n\n  # server.shutdown 설정 없음 — 기본 immediate\n\n# spring.lifecycle.timeout-per-shutdown-phase 없음\n```\n- Cloud Run 배포, 인스턴스 수 6개, DB `max_connections=100`"
- **기대 결과**:
  - `PERF-OPS` High 등급 검출 (하드 가드레일 아님이라 AUTO FAIL 아님)
  - 3건 지적:
    1. HikariCP `maximum-pool-size` 미설정 → Spring Boot 기본값 10. 6개 인스턴스 × 10 = 60 커넥션. DB `max_connections=100` 대비 여유 있지만 부하 시 부족 가능
    2. `server.shutdown: graceful` 미설정 → SIGTERM 시 처리 중 요청 강제 종료 (요청 유실)
    3. `spring.lifecycle.timeout-per-shutdown-phase` 미설정 → 기본 30초, Cloud Run terminationGracePeriodSeconds와 정합 확인 필요
  - 권장 수정:
    - `spring.datasource.hikari.maximum-pool-size: 15`, `minimum-idle: 5`, `connection-timeout: 3000`, `max-lifetime: 1800000` (30분)
    - `server.shutdown: graceful`
    - `spring.lifecycle.timeout-per-shutdown-phase: 20s`
  - 실전 사고 인용: pasta GLOB-521 (2026-06-23) — 배포 롤링 시 요청 유실 관측
  - 관점 침범 없음
- **검증 기준**:
  - [ ] `PERF-OPS` 유형 정확
  - [ ] 3건 모두 검출 (HikariCP·graceful shutdown·lifecycle timeout)
  - [ ] 각 설정 권장값 명시 (숫자·단위)
  - [ ] Cloud Run terminationGracePeriodSeconds 정합 언급
  - [ ] 실전 사고 인용 (GLOB-521)
  - [ ] AUTO FAIL 아님 (하드 가드레일 밖) 명시
  - [ ] 관점 침범 없음 (아키·보안 지적 X)
- **유형**: happy-path

---

## TC-7: Happy Path — Kubernetes startup probe 짧음 (PERF-OPS, 콜드스타트 위험)

- **입력 프롬프트**: "성능 관점 리뷰해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `admin/feat/glob-740-deployment-config`\n- 변경 파일: `k8s/admin/deployment.yaml`\n- 배경: pasta 사고 #588 (2026-06-19 admin 배포) — 콜드스타트 무거운 앱이 짧은 startup probe로 부팅 실패 관측\n- 핵심 diff:\n```yaml\napiVersion: apps/v1\nkind: Deployment\nspec:\n  template:\n    spec:\n      containers:\n      - name: admin\n        image: pasta-admin:v1.13.0\n        resources:\n          requests:\n            memory: \"512Mi\"\n            cpu: \"250m\"\n        startupProbe:\n          httpGet:\n            path: /actuator/health\n            port: 8080\n          initialDelaySeconds: 10\n          periodSeconds: 5\n          failureThreshold: 3\n          # 총 대기: 10 + (5×3) = 25초\n```\n- Spring Boot admin 앱 (Thymeleaf + Firebase + Identity Platform 무거운 초기화)"
- **기대 결과**:
  - `PERF-OPS` High 등급 검출
  - 지적:
    1. startup probe 총 대기 25초 → admin 콜드스타트 30~90초 걸림 (Firebase·IdP 초기화)
    2. `failureThreshold=3` 너무 낮음 → 실패 즉시 재시작 루프
    3. `resources.limits` 없음 → OOM 위험 (연관)
  - 권장 수정:
    - `initialDelaySeconds: 30`
    - `periodSeconds: 5`, `failureThreshold: 24` (총 2분 대기)
    - `resources.limits`: `memory: 1Gi`, `cpu: 500m` 명시
    - livenessProbe와 별도 유지 (startup은 부팅용, liveness는 살아있음 검증)
  - 실전 사고 인용: pasta admin #588 (2026-06-19) — Cloud Run startup timeout 재발
- **검증 기준**:
  - [ ] `PERF-OPS` 유형 정확
  - [ ] startup probe 총 대기 시간 계산 명시 (10 + 5×3 = 25초)
  - [ ] 콜드스타트 무거운 앱 특성 (Firebase·IdP) 언급
  - [ ] `failureThreshold` 상향 권장 (>=20)
  - [ ] `resources.limits` 미설정 함께 지적
  - [ ] 실전 사고 인용 (#588 or 유사)
  - [ ] livenessProbe와 startupProbe 역할 분리 안내
- **유형**: happy-path

---

## TC-8: Edge Case — HikariCP 크기 판정 애매 (정적 분석 한계)

- **입력 프롬프트**: "성능 관점 리뷰해줘. HikariCP 풀 크기가 적정한지 판정해줘.\n\n(시뮬레이션 상황)\n- 변경 파일: `api/src/main/resources/application-prd.yml` (수정)\n- 핵심 diff:\n```yaml\nspring:\n  datasource:\n    hikari:\n      maximum-pool-size: 20\n      minimum-idle: 10\n      connection-timeout: 3000\n      max-lifetime: 1800000\n```\n- 배포 컨텍스트:\n  - Cloud Run 인스턴스: 최소 3개, 최대 30개 (auto-scaling)\n  - DB: MySQL 8.0.13, `max_connections=200`\n  - 다른 앱도 같은 DB 사용 (admin: max 5개, batch: max 10개)\n- 이 설정이 안전한가?"
- **기대 결과**:
  - **판정 유보 or "검증 권장"** 등급 (정적 분석으로 확답 어려움)
  - 계산 근거 명시:
    - api 최대 커넥션: 30 인스턴스 × 20 = **600** ← 이미 DB max_connections 초과
    - admin: 5 × 20 = 100
    - batch: 10 × 20 = 200
    - **합계 최악의 경우 900 vs DB 200 → 커넥션 고갈 위험 확정**
  - 정적 분석 한계 명시:
    - 실제 최대 인스턴스 수·auto-scaling 트리거·트래픽 패턴은 런타임 데이터 필요
    - `maximum-pool-size`만으로 판단 불가, 인스턴스 수 × pool size가 DB max_connections보다 작아야 함
  - 대안 옵션:
    - **옵션 A** (안전): `maximum-pool-size: 6` (30 × 6 = 180 < 200)
    - **옵션 B** (재정의): DB `max_connections` 상향 협의 (DBA 요청)
    - **옵션 C** (분리): 앱별 DB 계정 분리 + 각 계정 max_user_connections 설정
  - 사용자 판단 요청: 실제 인스턴스 확장 상한·트래픽 패턴 확인 후 재검토
  - AUTO FAIL 아님 (하드 가드레일 밖)
- **검증 기준**:
  - [ ] 판정 유보 or 검증 권장 등급 (확정 판정 안 함)
  - [ ] 인스턴스 수 × pool size × 앱 수 계산 명시
  - [ ] DB max_connections 대비 부족 확인
  - [ ] 정적 분석 한계 명시 (auto-scaling 실측 필요)
  - [ ] 대안 3가지 이상 제시
  - [ ] 사용자 판단 근거(런타임 데이터) 요청
  - [ ] AUTO FAIL 아님 명시
- **유형**: edge-case
