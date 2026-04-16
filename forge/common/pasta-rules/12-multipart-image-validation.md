---
description: MultipartFile 이미지 업로드 검증 규칙
globs: **/web/**/*.java, **/dto/**/*.java
alwaysApply: false
---
# MultipartFile 이미지 업로드 검증 규칙

## 핵심 원칙

- ✅ 모든 이미지 업로드 MultipartFile에 `@ValidImageFile` 필수
- ✅ 패턴 1(직접 파라미터): `@Validated` 클래스 레벨 필수
- ✅ 패턴 2(DTO 필드): `@Validated` 불필요, `@Valid`만으로 충분

## 패턴 1: 직접 파라미터로 MultipartFile 받는 경우

```java
@RestController
@Validated  // ✅ 필수
public class ImageController {

  @PostMapping("/upload")
  public ResponseEntity<?> upload(
      @ValidImageFile @RequestPart MultipartFile imageFile) {  // ✅ 필수
    // ...
  }

  @PostMapping("/uploads")
  public ResponseEntity<?> uploadMultiple(
      @ValidImageFile @RequestPart List<MultipartFile> imageFiles) {  // ✅ List도 지원
    // ...
  }
}
```

**적용 대상**: `@RequestPart MultipartFile`, `@RequestPart List<MultipartFile>`, `@RequestParam MultipartFile`

## 패턴 2: DTO 필드에 MultipartFile이 있는 경우

```java
// DTO
public class ImageUploadDto {
  @ValidImageFile  // ✅ 필드에 적용
  @JsonIgnore
  private MultipartFile image;
}

// Controller
@Controller
// @Validated 불필요! ❌
public class ImageController {

  @PostMapping("/upload")
  public String upload(@Valid ImageUploadDto dto) {  // ✅ @Valid만
    // DTO 내부의 @ValidImageFile이 자동 검증됨
  }
}
```

**적용 대상**: `@ModelAttribute`로 바인딩되는 DTO, form-data로 전송되는 DTO

## 예외 사항

이미지가 아닌 파일(PDF 등)은 `@ValidImageFile` 적용하지 않음

```java
public class DocumentDto {
  private MultipartFile[] prescription;  // PDF 포함 가능 → @ValidImageFile 없음
}
```

## 검증 내용

- 확장자: jpg, jpeg, png, avif, heif, heic, heix만 허용 (대소문자 무시)
- 경로 조작 방지: `/`, `\`, `..` 차단
- null/empty: required=false인 경우 통과

## 체크리스트

### 새 Controller 추가 시

- [ ] MultipartFile 파라미터 → 패턴 1이면 `@Validated` + `@ValidImageFile`
- [ ] DTO 필드에 MultipartFile → 패턴 2이면 DTO 필드에 `@ValidImageFile` + 메서드에 `@Valid` (Controller에 `@Validated` 없음)

### 기존 Controller 수정 시

- [ ] 모든 MultipartFile 파라미터에 `@ValidImageFile` 적용?
- [ ] List<MultipartFile>에도 `@ValidImageFile` 적용?
- [ ] 패턴 1 Controller에 `@Validated` 있나?
- [ ] 패턴 2 Controller에 `@Validated` 없나?

## 참고

- `@ModelAttribute` 바인딩은 `@Valid`만으로도 DTO 내부 필드 검증 수행
- `@RequestPart` 단순 타입 파라미터는 `@Validated`가 있어야 validation 동작
- 원본 PR #6484: 패턴 2는 `@Validated` 없이 `@Valid`만 사용
