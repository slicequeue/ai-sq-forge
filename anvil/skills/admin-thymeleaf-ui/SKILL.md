---
name: admin-thymeleaf-ui
description: "moneyball `admin` 모듈에서 Thymeleaf + Thymeleaf Layout Dialect + AdminLTE(Bootstrap)로 관리자 화면을 만들거나 고칠 때 사용한다. `layout:decorate`, `layout/fragments`, `static/js`·`static/css` 배치, `@Controller`+`Model`, CSRF 메타·fetch 헤더, 사이드바·모달 프래그먼트, 관리자 이력·권한 패턴을 저장소 관례에 맞춘다. '어드민 페이지', 'Thymeleaf', '관리자 UI', 'AdminLTE', '사이드바 메뉴', '템플릿', 'static/js', 'layout:decorate', '모달', '관리자 화면 추가' 등이 나오면 반드시 이 스킬을 읽는다."
version: "1.2"
last-modified: "2026-05-19"
changelog: "v1.2 — blueprint v2.0 패턴 이식: 자기 검증 v2.0 3항목 추가(기존 admin 패턴 정합 명시, 가정 vs 확인 분리, sidebar/templates 위치 사전 확인). | v1.1 — 실전 역수입: 'OAuth2/SecurityContext 격리' 섹션 신규, 자기검증 19~22번 추가, 트러블슈팅 표 항목 추가"
---

# admin-thymeleaf-ui — Moneyball Admin UI (Thymeleaf)

> `core-java`와 동일한 철학: **먼저 구조를 고정하고, 그 구조 안에서 구현한다.**

**범위**: `admin` 모듈의 SSR(Thymeleaf) 화면 구현/수정  
**비범위**: `pasta-api` REST/Swagger 규칙, 아키텍처 재설계, 디자인 시스템 교체

---

## Phase 0. 작업 유형 선택 (확인 없이 코딩 금지)

| 모드 | 사용 시점 | 핵심 결과물 |
|------|-----------|--------------|
| **M1 신규 화면** | 메뉴/페이지/엔드포인트 신규 | Controller + Template + Page JS + Sidebar(필요 시) |
| **M2 기존 화면 개선** | 필드/동작/레이아웃 개선 | 최소 변경 diff + 회귀 포인트 |
| **M3 보안/구조 정리** | CSRF/권한/전역 리소스 정합성 개선 | 영향도 분석 + 안전한 수정 |
| **M4 진단 전용** | 수정 없이 분석만 필요 | 문제 목록 + 근거 + 개선안 |

모드 선택 없이 코드를 생성하지 않는다.

---

## 핵심 원리 (Core Principles)

### 1) Layout First
- 모든 일반 페이지는 `layout:decorate="~{layout/layout}"` + `layout:fragment="content"`를 따른다.
- 페이지에서 `wrapper/top/sidebar`를 재정의하지 않는다.

### 2) URL-View-File 3점 정합
- `@GetMapping("/x")` ↔ `return "a/b"` ↔ `templates/a/b.html`은 하나의 계약이다.
- 세 점 중 하나라도 깨지면 블로커다.

### 3) Local Script First
- JS는 페이지 하단 전용 로드를 우선한다.
- `script.html` 전역 추가는 마지막 수단이다.

### 4) Security by Convention
- `@PreAuthorize`, CSRF 메타, 기존 권한 문자열 계열을 유지한다.
- 상태 변경 fetch는 `_csrf` + `_csrf_header`를 사용한다.
- **외부 OAuth2 Client 호출이 admin 세션 `SecurityContextHolder`를 오염시키지 않도록** 격리한다 (아래 "OAuth2/SecurityContext 격리" 섹션 참조).

### 5) Reuse Before Reinvent
- 같은 도메인에서 Controller+HTML+JS 세트를 먼저 찾아 복제-수정한다.
- 새 표준 창작보다 기존 관례 정합을 우선한다.

---

## 구현 의사결정 매트릭스

| 상황 | 권장 |
|------|------|
| 단순 목록·폼·리다이렉트 | Thymeleaf만, JS 최소 또는 없음 |
| 모달·토글·비동기 저장 | 페이지 전용 JS (`type="module"` 우선), `common.js` 재사용 |
| JSON 상태 변경 | `getCsrfHeaders` 스타일로 동적 헤더(`[headerName]: token`) |
| 신규 라이브러리 필요 | 페이지 단위 로드 우선, 전역 등록은 최후 수단 |
| 사이드바 메뉴 추가 | `sidebar.html` 링크 + 매핑 URL + 권한을 동시에 맞춤 |

---

## 절대 금지 / 반드시 수행

### 절대 금지
- `pasta-api` 규칙(REST/Swagger/record DTO)을 admin SSR에 기계적으로 이식
- 이유 없이 `head.html`/`script.html`/`layout.html`/`sidebar.html` 전역 변경
- CSRF 토큰 하드코딩, 권한 없는 메뉴 노출
- 동일 도메인 기존 화면을 읽지 않고 신규 패턴 창작
- **`catch(Exception)` 사용 금지** — 내부 에러 메시지(DB 에러 등)가 사용자에게 노출됨. 반드시 `catch(BaseRuntimeException)`으로 비즈니스 예외만 포착
- **타임존 하드코딩 금지** — `ZoneId.of("Asia/Tokyo")` 등 직접 지정하지 않고 `@Value("${admin.display-timezone}")` 사용. HTML에서는 컨트롤러가 `@ModelAttribute("displayTimezone")`으로 전달한 변수 참조
- **에러 페이지에서 `href="/"` 금지** — 반드시 `th:href="@{/}"` 사용 (컨텍스트 패스 대응)
- **OAuth2 Client 커스터마이징 클래스를 무분별하게 `@Component`/`@Service`로 등록 금지** — Spring이 OAuth2 로그인 플로우(Google OIDC 등)에도 자동 연결하여 `saveAuthorizedClient` 등에 타 도메인 데이터가 유입됨. Dexcom 등 **특정 Provider 전용**이면 non-bean으로 만들고 `AuthorizedClientServiceOAuth2AuthorizedClientManager` 내부에서만 사용
- **외부 OAuth2/API 호출 코드에서 `SecurityContextHolder.getContext().setAuthentication(...)` 금지** — admin 세션 Authentication이 외부 토큰으로 덮여 이후 요청이 403으로 끊긴다. 꼭 필요하면 controller에서 save → 호출 → finally restore 패턴 사용
- **Non-bean 클래스에 `@Transactional` 금지** — Spring AOP 프록시가 적용되지 않아 트랜잭션이 무효. Non-bean이라면 `@Transactional` 제거 + Javadoc에 "프록시 미적용" 명시

### 반드시 수행
1. 모드 선택 (`M1~M4`)
2. 유사 화면 탐색(Controller+Template+JS 한 세트)
3. 파일 계획표 작성
4. 구현 후 Self-check 표 작성
5. **폼 POST 엔드포인트에 `try-catch(BaseRuntimeException)` + flash error** — 검증 실패 시 500 에러 페이지가 아닌 폼 화면에 에러 메시지 표시. 등록 폼은 입력값도 flash로 유지
6. **HTML `min`/`max` 제약과 서버 검증 동기화** — HTML에 `min="1" max="3650"` 넣었으면 서버 `validateXxx()`에도 동일 범위 검증 필수

---

## 생성 프로토콜 (core-java 스타일)

### 동작 모드
1. **Full 구현**: Controller + Template + JS(+Fragment) + Sidebar(필요 시) + 검증
2. **기능 추가**: 기존 화면에 필드/동작 추가 + 검증
3. **진단만**: 코드 수정 없이 문제/원인/개선안 도출

### 구현 순서
탐색 → 파일 계획표 → Controller/Template/JS 구현 → 권한/CSRF 점검 → Self-check

### 파일 계획 표 (작업 전 반드시 출력)

| 구분 | 파일 | 위치 |
|------|------|------|
| Controller | `{Feature}Controller.java` | `admin/src/main/java/.../controllers/{area}/` |
| Service (필요 시) | `{Feature}Service.java` | `admin/src/main/java/.../service/{area}/` |
| DTO | `{Feature}*Dto.java` | `admin/src/main/java/.../dto/{area}/` |
| Template | `{feature}.html` | `admin/src/main/resources/templates/{area}/` |
| Fragment | `{feature}-*.html` | `admin/src/main/resources/templates/{area}/` |
| Page JS | `{feature}.js` | `admin/src/main/resources/static/js/{area}/` |
| Page CSS (선택) | `{feature}.css` | `admin/src/main/resources/static/css/` |
| Sidebar (선택) | `sidebar.html` | `admin/src/main/resources/templates/layout/fragments/` |

---

## 참조 파일 (Progressive Disclosure)

| 파일 | 읽을 때 |
|------|-----------|
| `references/golden-path-map.md` | 가장 유사한 실전 파일 세트 선택 |
| `references/admin-module-structure.md` | 컨트롤러/뷰 경로 규칙, 권한·이력 패턴 |
| `references/thymeleaf-layout-and-theme.md` | layout/fragments, AdminLTE 마크업 원칙 |
| `references/js-and-csrf-patterns.md` | 페이지 JS, CSRF 헤더, sidebar/common 패턴 |
| `references/guardrails-and-security.md` | 전역 변경 가드레일, PII/보안 주의점 |

---

## 자기 검증 체크리스트

**표기**: B = 블로커(미충족 시 머지 부적합), R = 권장.

| # | 등급 | 항목 |
|---|------|------|
| 1 | B | 모드 선택 및 파일 계획표 작성 완료 |
| 2 | B | `layout:decorate` + `layout:fragment` 정합 |
| 3 | B | URL-View-File 3점 정합 |
| 4 | B | `@PreAuthorize` / 권한 문자열 정합 |
| 5 | B | CSRF 메타 기반 전송(하드코딩 없음) |
| 6 | R | 페이지 JS 우선, 전역 JS 추가 최소화 |
| 7 | R | AdminLTE 구조(`content-wrapper`, `content-header`) 유지 |
| 8 | R | `th:href` / `th:src` / `th:action` 사용 |
| 9 | R | 사이드바 링크·라우트·권한 동시 정합 |
| 10 | R | `AdminHistory` 패턴 일관성 |
| 11 | R | PII 노출/로그 유출 없음 |
| 12 | R | 모달 fragment 경로/이름 정합 |
| 13 | R | 날짜/시간 표시: `displayTimezone` 모델 변수 사용, 하드코딩 없음 |
| 14 | R | 변경 영향도(전역 파일 여부) 보고 |
| 15 | R | 필요 시 테스트/수동 검증 계획 제시 |
| 16 | B | 폼 POST에 `catch(BaseRuntimeException)` + flash error (500 페이지 방지) |
| 17 | B | `catch(Exception)` 미사용 (내부 에러 메시지 노출 방지) |
| 18 | R | HTML `min`/`max`와 서버 검증 범위 동기화 |
| 19 | B | 외부 OAuth2 Client 커스터마이징 시 non-bean 격리 (Google OIDC 로그인 영향 없음 검증) |
| 20 | B | 외부 API 호출 시 admin 세션 `SecurityContext` 오염 방지 (save/restore 또는 setAuthentication 제거) |
| 21 | B | 외부 API 의존성 추가 시 `application-jp-{env}.yml` 4곳 (local/dev/stg/prd) override 일치 |
| 22 | R | DB 컬럼 참조 전 실제 스키마/마이그레이션 확인 (오타/미존재 컬럼 방지) |
| 23 | B | **(v1.2) 기존 admin 패턴 사전 스캔** — `admin/src/main/resources/templates/` 와 `static/js/` 의 기존 페이지 1건을 모범 패턴으로 읽고 정합? (혼자 발명 금지) |
| 24 | R | **(v1.2) 확인 vs 가정 분리** — 권한 문자열·sidebar 메뉴 ID·URL 매핑 중 어느 것을 코드에서 확인하고 어느 것을 가정했는지 분리 표기? 가정 항목은 PR 본문에 명시? |
| 25 | R | **(v1.2) 변경 영향도 가정 표기** — 전역 JS·전역 CSS·layout fragment 수정 시 영향받는 페이지 목록을 추정으로만 적지 않고 `grep`으로 실제 사용처 식별 후 보고? |

---

## 실패 진단 매트릭스

| 증상 | 우선 확인 | 전형적 원인 |
|------|-----------|-------------|
| 404/Template not found | `return` 문자열 vs 파일 경로 | 오타, 폴더 위치 불일치 |
| 403 (폼/fetch) | CSRF 메타, 권한 어노테이션 | 토큰 헤더 누락, authority 불일치 |
| **외부 API 호출 성공 후 다음 요청 403** | `SecurityContextHolder.setAuthentication` 호출 지점 | 외부 OAuth2 토큰이 admin 세션 Authentication을 덮음 — controller에서 save/restore 필수 |
| **OAuth2 로그인 자체 불가 (Google 로그인 실패 등)** | OAuth2 Client 관련 `@Component`/`@Service` 클래스 | Spring이 모든 Provider에 해당 Bean을 끼워넣음 → non-bean + `AuthorizedClientServiceOAuth2AuthorizedClientManager` 로 전환 |
| 메뉴 클릭 시 빈 화면 | 사이드바 링크 vs 매핑 URL | href 오타, GET 매핑 누락 |
| 모달 버튼 무반응 | 페이지 JS 로드 위치/type | `type="module"` 누락, id 불일치 |
| 다른 페이지까지 깨짐 | `script.html`/`head.html` 변경 | 전역 로드 순서 충돌 |
| sandbox API가 prd에서 호출됨 | `application-jp-{env}.yml` 의 엔드포인트/credential override | `application.yml`만 수정하고 env별 파일 누락 |

---

## 작업 종료 출력 템플릿 (반드시 이 순서)

1. **적용 모드**: `M1~M4` + 선택 이유  
2. **파일 계획표 vs 실제 결과**: 계획 대비 생성/수정 파일  
3. **Self-check 결과표**: 각 항목 `PASS/FAIL/N/A`  
4. **정량 점수**: `총점/100`  
5. **남은 리스크**: 1~3개

---

## 정량 자기 평가표

| 항목 | 배점 | 기준 |
|------|------|------|
| 구조 정합 | 25 | URL-View-File, 레이아웃 적용 |
| 보안 정합 | 25 | 권한, CSRF, 민감정보 노출 |
| 테마 일관성 | 20 | AdminLTE 구조/스타일 정합 |
| 변경 최소성 | 15 | 전역 파일 최소 변경 |
| 보고 명확성 | 15 | 계획표, Self-check, 리스크 보고 |

- B 항목 하나라도 FAIL이면 **0점(블로커)**.
- 80점 미만이면 추가 보완 후 재평가한다.

---

## OAuth2 / SecurityContext 격리 (외부 API 연동 시)

admin 모듈은 Google OIDC 세션 기반 인증이다. 외부 OAuth2 Provider(Dexcom 등) 토큰을 이용한 API 호출이 **admin 세션에 영향을 주지 않도록** 반드시 아래를 지킨다.

### OAuth2 Client 커스터마이징

| 상황 | 권장 구조 |
|------|-----------|
| 특정 Provider 전용 AuthorizedClientService | **non-bean 클래스** + `AuthorizedClientServiceOAuth2AuthorizedClientManager` 내부 주입 |
| 여러 Provider에 공통 적용 | `@Service` 가능 (단 Google OIDC 등 로그인 플로우 영향 반드시 검증) |

- `@Component`/`@Service` 등록은 Spring이 **모든 OAuth2 Provider 플로우에 자동 편입**시킨다. 예: Google 로그인 → `saveAuthorizedClient(email, ...)` 호출 시 커스텀 서비스가 email을 Long 파싱하려다 `NumberFormatException` → 로그인 실패
- non-bean으로 만들 때는 `@Transactional` 같은 AOP 기반 어노테이션이 무효임을 인지 (프록시 미적용). 필요한 트랜잭션은 내부에서 직접 호출하는 Repository 단일 연산에 위임

### SecurityContext 오염 방지

- **외부 API용 서비스가 `SecurityContextHolder.getContext().setAuthentication(...)`을 호출하면**, 해당 요청 스레드의 인증 주체가 외부 토큰으로 바뀐다 → 응답 복귀 후 admin 세션의 후속 요청이 403으로 끊긴다.
- 공용/다른 모듈의 서비스를 admin에서 호출할 때는 controller에서 반드시 아래 패턴으로 격리:

```java
Authentication saved = SecurityContextHolder.getContext().getAuthentication();
try {
  externalService.call(...);
} finally {
  if (saved != null) {
    SecurityContextHolder.getContext().setAuthentication(saved);
  }
}
```

- 가능하면 외부 서비스 내부에서 `setAuthentication` 자체를 제거하고, 호출자가 명시적으로 `OAuth2AuthorizedClient`를 주입받아 쓰도록 리팩토링한다.

---

## 빠른 경로 (핵심 파일)

- 의존성: `admin/build.gradle` (Thymeleaf, layout-dialect, springsecurity6-extras)
- 레이아웃: `admin/src/main/resources/templates/layout/layout.html`
- CSRF 메타: `admin/src/main/resources/templates/layout/fragments/head.html`
- 전역 스크립트: `layout/fragments/script.html`
- 사이드바: `layout/fragments/sidebar.html` + `static/js/sidebar.js`
