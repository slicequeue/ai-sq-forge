---
description: 도메인 엔티티(순수 객체) 구현 규칙 및 Lombok 제약
globs: **/domain/**/*.java
alwaysApply: false
---
# Domain Entity Guidelines
`domain` 패키지에 위치하는 엔티티는 비즈니스 로직의 핵심입니다.

## 0. Layer Dependency Rule
- ❌ 다른 레이어(Application, Web, Infrastructure) 참조 금지
- ✅ Java 표준 라이브러리, Domain Entity만 사용
- ✅ Repository 인터페이스는 Domain에 정의, 구현체는 Infrastructure에 위치

## 1. Implementation Pattern
- **Type**:
  - **도메인 엔티티는 항상 `class` 사용** (DTO는 `record` 사용)
  - 상태 변경이 필요한 경우: `class` 사용
  - 불변 데이터인 경우에도 도메인 엔티티는 `class` 사용 (DTO와 구분)
- **Constructors**: 유효성 검증 로직을 생성자에 포함하여 객체 생성 시점에 정합성을 보장합니다.
- **Methods**: 비즈니스 행위(Business Behavior)를 메서드로 구현합니다.

## 2. Primitive Type vs Wrapper Type Convention
- ✅ **원시형 사용 (Primitive Types)**:
  - **not-null 필수 필드**: 항상 원시형 사용 (예: `long userId`, `int dailyMealCount`)
  - **기본값이 있는 계산 변수**: 원시형 사용 (예: `float totalKcal = 0.0f`, `boolean isContainedAlcohol = false`)
  - **기본값이 있는 record 필드**: 원시형 사용 (예: `float totalKcal`, `boolean isContainedAlcohol`)
- ✅ **래퍼 타입 사용 (Wrapper Types)**:
  - **null 가능한 필드**: 래퍼 타입 사용 (예: `Long id`, `Float totalDailyKcal`, `Boolean isContainedAlcohol`)
  - **Optional 값**: 래퍼 타입 사용
- 📝 **판단 기준**:
  - DB 컬럼이 `NOT NULL`이고 도메인에서도 항상 값이 보장되는 경우 → 원시형
  - DB 컬럼이 `NULL` 가능하거나, 값이 없을 수 있는 경우 → 래퍼 타입
  - 계산 로직에서 기본값(0, false 등)으로 초기화되는 경우 → 원시형

## 3. Object Creation Pattern
- **생성자 우선 사용**: 도메인 엔티티는 **생성자를 통한 객체 생성을 우선** 사용합니다.
- **Builder 사용 조건**: Builder는 다음 경우에만 사용합니다:
  - 필드가 많아서 (10개 이상) 생성자 호출이 복잡한 경우
  - 선택적 필드가 많아서 다양한 조합으로 객체를 생성해야 하는 경우
  - 복잡한 초기화 로직이나 검증이 필요한 경우
- **팩토리 메서드**: `of()`, `from()`, `create()` 등의 정적 팩토리 메서드를 통해 생성자를 호출합니다.
- **임시·대기 상태**: 정식 완료 전 임시/대기 데이터를 나타낼 때는 `ofTemporary` 등 의미가 드러나는 이름을 사용합니다.

## 4. Lombok & Annotations Rules
- ✅ **Allowed**: `@Getter`, `@Builder` (필요한 경우만), `@ToString`, `@EqualsAndHashCode`
- ❌ **Forbidden**:
  - `@Setter`: 도메인 불변성 위반. 상태 변경은 비즈니스 메서드로 처리.
  - `@Data`: 너무 많은 기능 포함으로 금지.
  - `@AllArgsConstructor`: 의도치 않은 객체 생성 위험. 생성자 직접 구현 권장.
  - `@RequiredArgsConstructor`: 도메인 객체에서는 지양.
  - **No JPA Annotations**: `@Entity`, `@Table` 등 사용 절대 금지.

## 5. Example (생성자 우선 사용)
```java
@Getter
@ToString
@EqualsAndHashCode
public class User {
    private final String name;
    private final int age;
    private final String birthDate;
    private final String gender;

    // 생성자를 통한 객체 생성 (우선 사용)
    public User(String name, int age, String birthDate, String gender) {
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("Name cannot be null or empty");
        }
        this.name = name;
        this.age = age;
        this.birthDate = birthDate;
        this.gender = gender;
    }

    // 팩토리 메서드로 생성자 호출
    public static User of(String name, int age, String birthDate, String gender) {
        return new User(name, age, birthDate, gender);
    }
}
```

## 6. Example (Builder 사용 - 복잡한 경우만)
```java
@Getter
@Builder
@ToString
@EqualsAndHashCode
public class Glp1InjectionRecordEntity {
    private final Long id;              // null 가능 (DB에서 생성 전에는 null)
    private final long userId;          // not-null 필수 필드 → 원시형
    private final int dailyMealCount;   // not-null 필수 필드 → 원시형
    // ... 많은 필드들 (10개 이상) ...

    // Builder 패턴 사용 시 검증 로직 포함 권장
    @Builder
    public Glp1InjectionRecordEntity(...) {
        if (userId <= 0) throw new IllegalArgumentException("Invalid userId");
        // Assignments
    }

    // Business Logic (No Setter)
    public void update(...) { ... }
}
```
