---
description: 리포지토리 패턴 (Domain Interface - Infra Implementation) 구현 규칙
globs: **/*Repository.java, **/*RepositoryImpl.java
alwaysApply: false
---
# Repository Implementation Pattern
DIP(Dependency Inversion Principle)를 준수하기 위해 3단계 구성을 따릅니다.

## 0. Layer Dependency Rule
- **Domain Repository**: Domain Entity만 사용, 다른 레이어 참조 금지
- **RepositoryImpl**: Domain Repository 인터페이스 구현, Domain ↔ JPA 변환 담당
- **의존성**: Infrastructure → Domain (단방향)

## 1. Components
1.  **Domain Interface** (`domain/*Repository`): 비즈니스 로직에서 사용하는 메서드 정의.
   - Domain Layer에 위치
   - Domain Entity만 사용
   - 다른 레이어 참조 금지
2.  **JPA Interface** (`infrastructure/.../*JpaRepository`): `JpaRepository` 상속.
   - Infrastructure Layer에 위치
3.  **Implementation** (`infrastructure/.../*RepositoryImpl`): Domain Interface 구현체. 내부적으로 JPA Repository나 QueryDSL을 주입받아 사용.
   - Infrastructure Layer에 위치
   - Domain Repository 인터페이스만 구현

## 2. Implementation Rule (`RepositoryImpl`)
- Domain Entity와 JPA Entity 간의 변환(`toEntity`, `from`)을 여기서 수행합니다.
- `Optional` 처리 및 Exception 처리를 담당합니다.

## 3. Example
```java
@Repository
@RequiredArgsConstructor
public class Glp1InjectionPlanRepositoryImpl implements Glp1InjectionPlanRepository {
    private final Glp1InjectionPlanJpaRepository jpaRepository;

    @Override
    public Optional<Glp1InjectionPlanEntity> findById(long id) {
        return jpaRepository.findById(id)
                .map(Glp1InjectionPlanJpaEntity::toEntity); // Conversion
    }

    @Override
    public Glp1InjectionPlanEntity save(Glp1InjectionPlanEntity entity) {
        // Domain -> JPA -> Save -> Domain
        return jpaRepository.save(Glp1InjectionPlanJpaEntity.from(entity)).toEntity();
    }
}
```
