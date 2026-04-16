---
description: JPA 엔티티(Persistence) 구현 규칙 및 Lombok 제약
globs: **/infrastructure/persistence/**/*JpaEntity.java
alwaysApply: false
---
# JPA Entity Guidelines
`infrastructure` 패키지에 위치하며, 실제 DB 테이블과 매핑됩니다.

## 1. Annotations & Lombok Rules
- **Class Level**:
  - ✅ `@Entity`, `@Table` (필수)
  - ✅ `@Getter` (필수)
  - ✅ `@NoArgsConstructor(access = AccessLevel.PROTECTED)` (JPA 필수)
  - ❌ `@Data`, `@Setter`, `@AllArgsConstructor` 금지.
  - ❌ `@Builder`는 클래스 레벨에 사용 금지 (생성자에만 사용).
- **Fields**: `@Column`, `@Id`, `@GeneratedValue` 등 사용.
- **Type Handling**: JSON 컬럼은 `@Type` 또는 `@Convert` 사용.

## 2. Conversion Methods
- **toEntity()**: JPA Entity를 Domain Entity로 변환하는 메서드 필수 구현.
- **from(DomainEntity)**: Domain Entity를 JPA Entity로 변환하는 정적 메서드(`static`) 필수 구현.

## 3. Builder Pattern
- **생성자 레벨**에 `@Builder`를 적용하여 필요한 필드만 초기화하도록 제한합니다.

## 4. Example
```java
@Entity
@Table(name = "pghd_table")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class SampleJpaEntity extends BaseSoftDeleteEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "sample_data")
    private String sampleData;

    @Builder // 생성자에만 적용
    public SampleJpaEntity(Long id, String sampleData) {
        this.id = id;
        this.sampleData = sampleData;
    }

    public DomainEntity toEntity() {
        return DomainEntity.builder()...build();
    }

    public static SampleJpaEntity from(DomainEntity entity) {
        return SampleJpaEntity.builder()...build();
    }
}
```
