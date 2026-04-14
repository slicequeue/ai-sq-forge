# 가드레일 · 보안 · 회귀

## 전역 파일 — 변경 시 영향 범위

| 파일 | 영향 | 원칙 |
|------|------|------|
| `layout/fragments/head.html` | 전 페이지 CSS·CSRF 메타 | 최소 diff, 신규 CSS는 가능하면 페이지/도메인 단위 |
| `layout/fragments/script.html` | 전 페이지 JS 로드 순서·충돌 | 새 라이브러리 **최후 수단**; 페이지 로드 우선 |
| `layout/layout.html` | 전체 HTML 뼈대 | 거의 수정 금지 |
| `layout/fragments/sidebar.html` | 내비게이션·`sidebar.js` | URL·권한·실제 매핑 동시 검증 |

## Spring Security

- 새 URL은 **인증/인가 규칙**에 걸리는지 확인 (`SecurityConfig` 및 `@PreAuthorize`).
- 로그아웃은 `top.html`의 `POST /logout` 패턴을 유지.
- **CSRF**: SSR 폼은 Spring이 자동 처리. **AJAX/fetch**는 메타 기반 헤더 — `js-and-csrf-patterns.md` 참고.

## 개인정보·민감 데이터

- 관리자 화면은 본질적으로 민감 데이터가 많다. **표시 최소화**, **HTML data-* 남용 금지**, **클라이언트 로그 금지**.
- 서버 로그는 프로젝트 전역 규칙(MDC, 마스킹) 준수.

## 관리자 이력

- 기능에 따라 `AdminHistory`가 **법적·운영적** 의미를 가질 수 있다. 메시지 형식은 **동일 도메인 기존 코드**를 복제해 일관성 유지.

## 하지 말 것 (Anti-patterns)

1. **레이아웃 없는** 전체 페이지를 메뉴에 물려 사용자가 헤더·CSRF 없이 조작하게 만들기.
2. **전역 script**에 페이지 한 곳만 쓰는 무거운 라이브러리 추가.
3. pasta-api용 **record DTO·Swagger** 규칙을 admin 폼에 기계적으로 적용.
4. CSRF 토큰을 **스크립트 상수**로 박아 넣기.
5. 사이드바에만 링크 추가하고 **Controller 매핑·권한**을 빼먹기.

## 테스트·품질

- `admin` 모듈: **Testcontainers MySQL** 등 프로젝트 가드라인 유지.
- UI 회귀는 자동화가 제한적이므로, 가능하면 **Controller 파라미터·Service** 단위로 검증.
- Thymeleaf 템플릿 오타(`layout:fragement` 등)는 컴파일 타임에 잡히지 않을 수 있음 — **뷰 이름·파일명**을 이중 확인.

## 장애 시 의심 순서

1. 뷰 이름과 파일 경로 불일치  
2. CSRF 누락으로 403  
3. `@PreAuthorize`와 실제 권한 불일치  
4. 전역 JS 순서 충돌(다른 페이지에서만 재현)
