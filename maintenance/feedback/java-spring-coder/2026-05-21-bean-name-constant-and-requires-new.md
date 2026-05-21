---
component: java-spring-coder
source: pasta-japan-server
date: 2026-05-21
type: improvement
related_commits: a6b72daa82, 0fc9b52338, 1066af4f54
severity: medium
---

## 증상

오늘 작업에서 2개 주요 패턴이 코드 작성 단계에서 사전 가이드되지 못함:

### 1. Bean 이름 매직 스트링 + 모듈 위치 (a6b72daa82 / 0fc9b52338)

`@Bean`/`@Qualifier`/`@MockBean(name=...)`가 다중 모듈에서 같은 빈 이름 문자열을 반복 사용. PR 리뷰 단계에서 "상수화 + shared 모듈 이동" 지적 → 후속 커밋 2건 발생.

### 2. 외부 enqueue 실패 마킹 트랜잭션 전파 (1066af4f54)

`AiInsightOnDemandGenerationService`에서 Cloud Task enqueue 실패 시 요청 상태를 FAILED로 마킹하는 코드가 같은 트랜잭션에 있어, 호출 측 트랜잭션 롤백 시 FAILED 마킹도 함께 롤백되는 잠재 버그. `TransactionTemplate`에 `PROPAGATION_REQUIRES_NEW` 명시 필요.

## 수정 내용

### 1. Bean 상수화
- `shared/.../constant/DexcomBeanNameConstants` 신규 → `public static final String DEXCOM_AUTHORIZED_CLIENT_MANAGER`
- `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)`, `@Qualifier(DEXCOM_AUTHORIZED_CLIENT_MANAGER)`, `@MockBean(name = DEXCOM_AUTHORIZED_CLIENT_MANAGER)` 형태로 8곳 교체

### 2. REQUIRES_NEW
```java
this.transactionTemplate = new TransactionTemplate(platformTransactionManager);
this.transactionTemplate.setPropagationBehavior(TransactionDefinition.PROPAGATION_REQUIRES_NEW);
```

## 개선 제안 (java-spring-coder v1.7 가드레일)

### A. Bean 이름 상수 패턴 가이드 (Phase 0 또는 패턴 가이드)

신규 `@Bean` 메서드 작성 시:
- **단일 모듈에서만 참조** → 메서드 이름을 빈 이름으로 사용 (기본). 별도 상수 불필요
- **여러 모듈/테스트에서 참조** → 빈 이름을 `public static final String` 상수로 추출
- **상수 위치**: 빈 등록자(A 모듈)와 소비자(B 모듈)가 같은 모듈이면 등록자 클래스 내. 다른 모듈이면 **shared 모듈의 `*Constants` 클래스**로 분리 (config → config 의존 외관 회피)

```java
// 다중 모듈 공유 시 — shared 모듈
package com.x.shared.constant;
public final class DexcomBeanNameConstants {
    public static final String DEXCOM_AUTHORIZED_CLIENT_MANAGER = "dexcomAuthorizedClientManager";
    private DexcomBeanNameConstants() {}
}

// 빈 등록자 — api 모듈
@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)
public OAuth2AuthorizedClientManager dexcomAuthorizedClientManager(...) { ... }

// 소비자 — cgm 모듈
public DexcomClient(@Qualifier(DEXCOM_AUTHORIZED_CLIENT_MANAGER) OAuth2AuthorizedClientManager mgr) { ... }
```

### B. TransactionTemplate 전파 명시 의무

`TransactionTemplate` 생성 시 **즉시** `setPropagationBehavior` 호출 의무화. 기본값(`PROPAGATION_REQUIRED`)이 의도와 다른 경우가 매우 많음.

**REQUIRES_NEW가 필요한 전형 케이스** (스킬 본문에 명시):
1. 외부 시스템 호출 실패 후 **실패 마킹**이 호출 측 트랜잭션 결과와 **독립**적으로 커밋되어야 할 때
2. 감사 로그/이력 기록이 호출 측 롤백과 무관하게 남아야 할 때
3. 알림 발송 큐 enqueue 실패 후 retry 큐 적재

**REQUIRED 유지가 적절한 케이스**:
1. 보조 도메인 변경이 본 트랜잭션과 운명을 같이해야 할 때 (예: 주문 + 결제 묶음)

판단 가이드 추가 (자기 검증 체크리스트):
- [ ] 외부 호출 실패 마킹이 같은 트랜잭션에 있으면 REQUIRES_NEW 검토했는가?
- [ ] TransactionTemplate 생성 후 `setPropagationBehavior`를 명시했는가? (기본값 유지가 의도라면 주석으로 명시)

### C. 약한 해시 알고리즘 금지 (시큐어코딩)

`MessageDigest.getInstance("MD5"|"SHA-1"|"SHA1")` 금지. 사용 시점에 즉시 `SHA-256` 이상 강제.

## 변경 파일 (참고)

- `api/.../config/DexcomAuth2Configuration.java`
- `cgm/.../client/DexcomWebClientConfiguration.java`
- `shared/.../constant/DexcomBeanNameConstants.java` (신규)
- `pasta-api/.../AiInsightOnDemandGenerationService.java`

## 누적 검토

java-spring-coder 관련 본 카테고리 신규. 1건 누적.
