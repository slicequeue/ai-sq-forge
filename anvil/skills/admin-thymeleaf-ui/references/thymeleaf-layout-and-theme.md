# Thymeleaf Layout Dialect · 프래그먼트 · AdminLTE

## 의존성 (확인용)

`admin/build.gradle`:

- `spring-boot-starter-thymeleaf`
- `nz.net.ultraq.thymeleaf:thymeleaf-layout-dialect`
- `org.thymeleaf.extras:thymeleaf-extras-springsecurity6`

## 네임스페이스

페이지 템플릿 상단에 통상 다음을 선언한다.

```html
<html xmlns:th="http://www.thymeleaf.org"
      xmlns:layout="http://www.ultraq.net.nz/thymeleaf/layout"
      layout:decorate="~{layout/layout}" lang="ko">
```

- `layout:decorate="~{layout/layout}"` — 레이아웃 템플릿 지정 (`~{...}` 리졸버 문법).
- 본문은 `<th:block layout:fragment="content">` 안에만 둔다.

## 레이아웃 조립 순서 (`layout/layout.html`)

1. `th:replace="/layout/fragments/head :: headFragment"`
2. `body` — `wrapper` — `top` — `sidebar`
3. **`layout:fragment="content"`** ← 각 페이지가 채움
4. `footer`
5. `th:replace` — `script` 프래그먼트

페이지는 **wrapper/사이드바를 중복 선언하지 않는다**.

## 공통 프래그먼트 역할

| 파일 | 내용 |
|------|------|
| `head.html` | CSS 스택, **CSRF meta** `id="_csrf"`, `id="_csrf_header"` |
| `top.html` | AdminLTE navbar, 로그아웃 폼 `th:action="@{/logout}"` `post` |
| `sidebar.html` | 브랜드, 트리 메뉴, **하단 `sidebar.js` (type=module)** |
| `footer.html` | 푸터 |
| `script.html` | jQuery, Bootstrap, AdminLTE, DataTables, TinyMCE, 공통 스크립트 등 |

## AdminLTE · Bootstrap 마크업 방향

- **페이지 껍데기**: `div.content-wrapper` → `div.content-header` / `div.content` (기존 목록·상세와 동일 계층).
- **사이드바 톤**: `sidebar-dark-primary`, 전체 배경 `#f4f6f9` 등은 `layout.html`과 맞춤.
- **버튼·테이블**: Bootstrap `btn`, `table`, `form-control`, `modal` 계열을 **같은 도메인의 기존 화면**과 동일하게 사용.
- **인라인 스타일**: 레거시에 `margin-left: 25px` 등이 많음 — **신규만 유별나게 다른 여백**을 만들지 말고 인접 템플릿을 복제 후 수정.

## Thymeleaf 레시피

### 링크·정적 리소스

- `th:href="@{/path}"`, `th:src="@{/js/...}"` — 컨텍스트 경로 대응.
- 경로 변수: `th:href="@{banner/{id}(id=${banner.id})}"` 등.

### 반복·분기

- `th:each`, `th:switch` / `th:case`, `th:if` / `th:unless`

### 시간

- ` #temporals.format(...) ` — 기존처럼 `atZone('Asia/Seoul')` 등 **업무 규칙에 맞는 존**을 유지.

### 폼

- `th:action`, `th:object`, `th:field` (사용하는 화면은 기존 따라감)
- `th:method="post"` + Spring `_method` 히든으로 PUT/DELETE (프로젝트 설정 전제)

### 모달·부분 뷰 (`th:fragment`)

1. 조각 전용 파일 또는 같은 도메인 파일에 `th:fragment="이름"` 정의.
2. 부모 페이지에서 `th:replace="~{경로 :: fragmentName}"` 또는 `th:replace="/cms/foo :: barFragment"`.

예: 목록 페이지가 등록 모달 조각을 끼워 넣는 패턴 (`banners.html` + `banner-register.html`).

### 레이아웃 없는 조각

- 모달 전용 html은 `layout:decorate` 없이 `th:fragment`만 정의할 수 있다 — **부모가 레이아웃을 담당**.

## 전역 스크립트와의 관계

- DataTables, TinyMCE, jQuery는 이미 **하단 공통 script**에 있음.
- 페이지에서는 **초기화 코드** 또는 **도메인 전용 로직**만 추가하는 것을 우선한다.

## 에러 템플릿

- `templates/error/400.html`, `403.html` 등 — 레이아웃과 다른 구조일 수 있음. 신규 에러 페이지 추가 시 기존 error 템플릿을 참고.
