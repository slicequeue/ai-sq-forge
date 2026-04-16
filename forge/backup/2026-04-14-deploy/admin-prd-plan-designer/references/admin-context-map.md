# admin Context Map

## 1) 실행 흐름 기준선
- admin 기능은 기본적으로 `@Controller -> templates -> static/js`의 SSR 흐름을 따른다.
- JSON API 중심 설계보다 화면 진입/렌더링/상호작용 흐름을 먼저 정의한다.

## 2) 네비게이션 정합
- 신규 기능은 `sidebar` 진입 경로(메뉴 위치, 링크, 권한)를 요구사항 단계에서 명시한다.
- 메뉴 노출 규칙과 실제 URL 매핑이 다르면 운영 혼선이 발생한다.

## 3) 보안/권한
- 접근 권한(`@PreAuthorize` 등)은 PRD 비기능 요구와 TDD 보안 설계 양쪽에 반영한다.
- 상태 변경 동작은 CSRF 고려가 필요하다(문서에서 누락 금지).

## 4) 감사 이력(admin history)
- 관리자 기능은 조회/변경 행위 이력 정책이 중요하다.
- 어떤 액션을 언제, 어떤 수준으로 기록할지 PRD/TDD에 명확히 남긴다.

## 5) 문서 작성 최소 확인 영역
- Controller(경로/권한), Template(화면 흐름), Static JS(상호작용), Sidebar(진입), Security(제약).

## 6) Thymeleaf · 레이아웃 (Cursor **14**)
- 일반 페이지: `layout:decorate="~{layout/layout}"`, 본문 `layout:fragment="content"`. `head`/`sidebar` 등은 **fragment 복제 금지** → `layout/fragments/*` 재사용.
- **URL–뷰명–파일 정합**: `@GetMapping`/`@PostMapping` ↔ `return "…"` ↔ `templates/...html` 을 화면마다 **한 세트**로 문서·실행 TODO에 적는다.
- 모달·재사용 UI는 fragment + `th:replace`.

## 7) Static · sidebar (Cursor **16**)
- 페이지별 `templates/...html` 과 **동일 베이스 이름**의 `static/js/*.js` 를 우선한다. 전역 `layout/fragments/script.html` 변경은 최소화.
- `fetch`/XHR은 CSRF **meta**에서 토큰·헤더명을 읽는 기존 패턴을 따른다(하드코딩 금지).
- **sidebar**에 링크를 추가하면 **컨트롤러 매핑·`sec:authorize`(또는 동등)·실제 권한**을 함께 맞춘다([15]와 동일 이슈).

## 8) 모듈 경계 (Cursor **13**)
- admin은 pasta-api식 4계층 문서를 그대로 붙이기보다 **실제 패키지**(controllers/service/repository 혼합) 관례를 따른다.
- `MoneyballAdminApplication` 스캔·타 모듈(JPA 빈) 의존 시 **이름 충돌**을 Phase/TODO에 명시한다.
- DB 마이그레이션이 **어느 모듈 Flyway**(admin vs pasta-api)에 둘지 HYBRID/TDD에 한 줄이라도 고정한다(가정 숨김 금지).

## 9) SSOT vs `works/` 실행 계획 (큰 기능 권장)
- **HYBRID/PRD/TDD**: 요구·FR·결정·Alignment·Open Questions의 단일 근거.
- **`works/<기능>/plan.md`**: 인덱스 + Phase 순서 + **FR→파일 매핑**.
- **`plan-01`~**: `- [ ]` TODO·DoD·**Cursor 규칙 교차 참조**(00 → 13~16 등).
- 스펙 변경 순서: **SSOT 먼저** → `works/` 정리.

## 10) 보안 점검 (admin MVC vs REST)
- 신규 경로는 **`SecurityFilterChain`**(`authorizeHttpRequests`/`requestMatchers` 등)과 **`@PreAuthorize`** 양쪽에서 누락·불일치가 없는지 본다.
- 팀의 REST/API 전용 보안 체크리스트를 admin 화면에 그대로 적용하지 말고, **SSR 진입·정적 리소스·OIDC 콜백** 등 admin에 필요한 예외를 문서에 남긴다.
