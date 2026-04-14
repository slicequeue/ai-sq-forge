# admin 모듈 구조 · Controller · 뷰 매핑

## 모듈·진입점

| 항목 | 값 |
|------|-----|
| Gradle | `admin/` |
| 메인 클래스 | `com.kakaohealthcare.moneyballadmin.MoneyballAdminApplication` |
| 특징 | `scanBasePackages`에 `moneyballadmin` 외 **다수 moneyball 패키지** 포함 — 어드민 전용이 아닌 코드가 같은 프로세스에서 동작 |

## Java 패키지 관례 (어드민 애플리케이션 코드)

| 계층 | 패키지 패턴 | 비고 |
|------|-------------|------|
| 웹 | `controllers`, `controllers.cms`, `controllers.claim`, … | `@Controller` 중심 |
| 서비스 | `service`, `service.cms`, … | `@Service`, 트랜잭션 |
| DTO | `dto`, `dto.cms`, … | 폼 필드·화면 전달 |
| 리포지토리 | `repository`, `repository.cms`, … | 조회/변경 |
| 엔티티 | `entity` | 예: `AdminUser` |
| 설정 | `configrations` (철자 그대로 기존 패키지) | `SecurityConfig` 등 |

신규 기능은 **기능이 속한 기존 서브패키지**에 맞춘다 (임의로 새 최상위 패키지를 만들지 않는다).

## Controller → 뷰 이름 규칙

Spring이 반환하는 문자열은 **확장자 없이** `templates/` 기준 경로와 1:1 대응한다.

```
return "cms/banners";  →  templates/cms/banners.html
return "user/user-detail";  →  templates/user/user-detail.html
```

- **리다이렉트**: `return "redirect:/path";` — Flash는 `RedirectAttributes.addFlashAttribute`.
- **에러 메시지 노출**: Flash 또는 `Model` — 템플릿에서 `th:if="${error}"` 등 기존 도메인 방식 따름.

## HTTP 메서드·폼 패턴 (기존 코드와 정합)

| 용도 | 흔한 형태 |
|------|-----------|
| 조회 | `@GetMapping`, `Model.addAttribute` |
| 생성 | `@PostMapping` + 폼 또는 `@ModelAttribute` |
| 수정 | `@PutMapping` / `@PostMapping` (프로젝트 관례 따름) |
| 삭제 | `@DeleteMapping` + 폼 `th:method="delete"` + 히든 필드 (예: 배너 삭제) |

컨트롤러 시그니처에 `@AuthenticationPrincipal OidcUser` 등 **기존 동일 영역 컨트롤러**와 맞춘다.

## 관리자 이력 (AdminHistory)

변경·중요 조회 화면은 인근 컨트롤러와 동일하게:

- `AdminHistoryService.saveHistory(...)`
- `AdminHistoryDto.builder()` + `AdminFunction` + `exposureMessage` 문구 패턴

메시지에 **불필요한 PII**를 넣지 않는다 (이메일 등은 기존 수준만).

## 권한

- 클래스/메서드 `@PreAuthorize("hasAuthority('...')")` — **같은 메뉴·같은 도메인**의 다른 컨트롤러 권한 문자열을 참고.
- 템플릿 조건부 노출이 필요하면 `thymeleaf-extras-springsecurity6` + `sec:` (상단 네비 등 기존 파일 참고).

## 테스트

- `admin/src/test/java/...` 에 기존 `*ServiceTest`, `*ControllerTest` 패턴 존재.
- UI 자동화가 아니라도 **Service·Repository** 검증으로 회귀를 잡는다.
- 프로젝트 가드라인: **Testcontainers MySQL** 등 — H2로 테스트 우회하지 않는다.

## pasta-api와의 관계 (혼동 방지)

| admin | pasta-api |
|------|-----------|
| `@Controller`, HTML | `@RestController`, JSON |
| `Model`, 뷰 이름 | Request/Response DTO record |
| 템플릿 + static | 주로 API 문서·필터 |

admin에서 pasta-api 스타일 4계층을 **새로 도입하지 않는다** (요청이 명시적으로 아키텍처 이관이면 별도).
