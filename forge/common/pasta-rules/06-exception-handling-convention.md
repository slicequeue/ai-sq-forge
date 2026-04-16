---
description: Exception 처리 가이드 (Application Layer 배치, Shared 예외 상속)
globs: **/*Exception.java, **/*ExceptionHandler.java
alwaysApply: false
---
# Exception Handling Guidelines

## 1. Core Principles
- **Location**: 모든 Custom Exception은 **Application Layer** (`application/exception`)에 배치합니다.
- **Inheritance**: Shared 모듈의 `MoneyballException` 구현체(`NotFoundException`, `BadRequestException` 등)를 상속받아야 합니다.
- **Codes**: `ExceptionConstants`에 정의된 표준 에러 코드를 사용합니다.
- **Messages**: `messages.properties` 키를 사용하여 i18n을 지원합니다.

## 2. Global Exception Handler (`web/exception/`)
- `@RestControllerAdvice`를 사용하여 도메인별 예외를 처리합니다.
- **Logging**:
  - 4xx: `log.warn()`
  - 5xx: `log.error()` (Stack Trace 포함)

## 3. Example (Custom Exception)
```java
public class AiNudgeMessageNotFoundException extends NotFoundException {
    public AiNudgeMessageNotFoundException(String taskId) {
        super(
            ExceptionConstants.ERROR_NUDGING_MESSAGE_NOT_FOUND, // Code
            "error.nudge.message.not.found", // Message Key
            new Object[] {taskId} // Args
        );
    }
}
```

## 4. Example (Handler)
```java
@RestControllerAdvice(basePackages = "com.example.domain.web")
@Log4j2
public class DomainExceptionHandler {
    @ExceptionHandler(AiNudgeMessageNotFoundException.class)
    public ResponseEntity<BaseErrorResponse> handleNotFound(AiNudgeMessageNotFoundException ex) {
        log.warn("NotFound: {}", ex.getMessage());
        return new ResponseEntity<>(ex.toErrorResponse(), HttpStatus.NOT_FOUND);
    }
}
```
