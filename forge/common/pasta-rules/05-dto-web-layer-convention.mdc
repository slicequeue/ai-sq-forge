---
description: DTO(Record) 및 Controller 구현 규칙 및 Lombok 제약
globs: **/dto/**/*.java, **/web/**/*.java
alwaysApply: false
---
# DTO Guidelines
- **Format**: 무조건 Java **`record`** 타입을 사용합니다. (Lombok 불필요)
- **Legacy Support**: Record 사용이 불가능한 경우에만 Class 사용. 이 경우 `@Getter`, `@ToString` 허용. `@Data`, `@Setter` 지양.
- **Validation**: 생성자 내부나 `@Valid` 어노테이션을 통해 입력값을 검증합니다.
- **Naming**:
  - **Web Layer**: 최상위 입출력 객체는 `*Request`, `*Response` 형식 사용. 하위 객체는 `*ItemRequest`, `*ItemResponse` 형식 사용.
  - **Application Layer**: 외부/내부로 오가는 DTO는 `*InDto`, `*OutDto`를 꼭 붙여서 구현.
  - **Dto postfix**: Web layer에서는 Dto postfix를 사용하지 않습니다.
- **Object Creation**: DTO 객체 생성 시 `new` 키워드 대신 정적 팩토리 메서드(`of()`, `from()`, `to()`, `forXxx()`)를 사용합니다.
  - `of()`: 직접 값으로부터 객체 생성
  - `from()`: 다른 객체로부터 변환 (변환 로직 포함)
  - `to()`: 다른 객체로 변환
  - `forXxx()`: 특정 용도(예: 임시 레코드 응답)에 필요한 필드만 받는 생성
- **null 다수 전달 지양**: 생성자에 null을 여러 개 넘기기보다, 필요한 필드만 받는 정적 팩토리 메서드를 두고 활용합니다.

## Layer Dependency Rule for DTOs
- **Application DTO**: Domain Entity → Application DTO 변환 (`from(DomainEntity)`)
- **Web DTO**: Application DTO → Web DTO 변환 (`from(ApplicationDto)`)
- **변환 흐름**: Domain → Application → Web (단방향)

# Web Controller Guidelines
- **Annotations**:
  - ✅ `@RestController`, `@RequestMapping`
  - ✅ `@RequiredArgsConstructor` (생성자 주입용)
  - ❌ `@Autowired` 필드 주입 금지.
- **Swagger**: `@Tag`, `@Operation`, `@Schema` 등을 사용하여 API 명세를 코드에 포함합니다.
- **Response**: `ResponseEntity`를 반환 타입으로 사용합니다.

## Layer Dependency Rule for Controllers
- ✅ Application Service만 주입, Application DTO 사용
- ❌ Domain, Infrastructure 직접 참조 금지

## Example (Record DTO)
```java
public record Glp1InjectionRecordResponse(
    @Schema(description = "ID") Long id,
    @Schema(description = "Time") Instant injectedAt
) {
    public static Glp1InjectionRecordResponse from(Glp1InjectionRecordOutDto dto) {
        return new Glp1InjectionRecordResponse(dto.id(), dto.injectedAt());
    }
}
```

## Example (Controller)
```java
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/records")
@Tag(name = "Record API")
public class RecordController {
    private final RecordService service;

  public ResponseEntity<Void> create(`@RequestBody` `@Valid` RecordRequest request) {
      service.create(request.toApplicationDto()); // RecordRequest → RecordInDto
      return ResponseEntity.ok().build();
  }
}
```
