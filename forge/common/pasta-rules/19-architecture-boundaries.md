---
description: 모듈 간 아키텍처 경계 강제 규칙. 다른 도메인 접근, Repository import, 서비스 삭제 시 참고.
globs: **/*.java
alwaysApply: true
---
# Architecture Boundaries (아키텍처 경계 강제)

01-architecture-convention의 계층/의존성 원칙을 **강제**하는 구체적 금지 규칙. 위반 시 즉시 수정 필요.

## 1. 다른 도메인 Repository 직접 import 금지

```java
// ❌ 금지: 다른 도메인의 Repository/JpaRepository 직접 접근
import pghd.mealrecord.infrastructure.MealRecordJpaRepository;

public class ReportService {
  private final MealRecordJpaRepository mealRecordJpaRepository; // 도메인 경계 위반
}

// ✅ 허용: ClientService 인터페이스를 통한 접근
import pghd.report.domain.MealRecordClientService;

public class ReportService {
  private final MealRecordClientService mealRecordClientService; // Client 패턴
}
```

### 위반 감지 패턴

아래 패턴이 나타나면 아키텍처 경계 위반:
- 다른 도메인의 `*JpaRepository`를 import
- 다른 도메인의 `*JpaEntity`를 import
- 다른 도메인의 `*RepositoryImpl`를 import
- Infrastructure 계층에서 다른 도메인의 Infrastructure를 직접 참조

## 2. Service/공유 클래스 삭제 전 사용처 확인 필수

Service, Client, 유틸리티 등 **공유 가능성이 있는 클래스**를 삭제하기 전에 반드시 전체 프로젝트에서 사용처를 검색한다:

```bash
# 삭제 전 필수 확인
grep -r "ClientService" --include="*.java" .
grep -r "ClassName" --include="*.java" .
```

사용처가 1곳이라도 있으면:
1. 사용처를 먼저 대체 구현으로 전환
2. 사용처가 모두 제거된 후 삭제

**확인 없이 삭제 → 컴파일 에러 → 복원 작업** 순환을 방지한다.

## 3. Qualifier 기반 Bean 주입

동일 인터페이스의 구현체가 여러 개일 때 `@Qualifier`로 명시적 주입:

```java
// ❌ 금지: 모호한 주입
@RequiredArgsConstructor
public class SomeService {
  private final SomeClientService someClientService; // 어떤 구현체?
}

// ✅ 허용: 명시적 Qualifier
@RequiredArgsConstructor
public class SomeService {
  @Qualifier("s2sSomeClientServiceImpl")
  private final SomeClientService someClientService;
}
```

## 4. Service 반환 타입에서 JPA Entity 노출 금지

Application Service가 JPA Entity를 직접 반환하면 계층 경계가 무너진다:

```java
// ❌ 금지: JPA Entity 직접 반환
public MealRecordJpaEntity getMealRecord(Long id) { ... }

// ✅ 허용: Domain Entity 또는 DTO 반환
public MealRecordEntity getMealRecord(Long id) { ... }
public MealRecordOutDto getMealRecord(Long id) { ... }
```

## 5. 마이그레이션은 반드시 Feature 브랜치에서

DB 마이그레이션 파일(`V*.sql`)은 **feature 브랜치에서만 생성**한다:
- dev/stg/main에서 직접 마이그레이션 파일 생성 금지
- cherry-pick으로 복구해야 하는 상황을 방지
