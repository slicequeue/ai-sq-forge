# JavaScript 배치 · CSRF · 상호작용 패턴

## 파일 위치 원칙

| 종류 | 경로 예시 |
|------|-----------|
| 도메인 페이지 로직 | `static/js/cms/banner.js`, `static/js/claim/claim.js` |
| 공통 유틸 (ES module export) | `static/js/common.js` |
| 사이드바 트리 토글 | `static/js/sidebar.js` |

페이지에서 로드:

```html
<script type="module" th:src="@{/js/cms/banner.js}"></script>
```

`content` fragment **맨 아래**에 두어 DOM이 준비된 뒤 실행되게 한다.

## `common.js` (모듈)

`static/js/common.js`는 `export` 기반 유틸을 제공한다.

- `toggleDisplay(id)` — display 토글
- `openModal` / `closeModal` — `.modal` 단일 선택자 기반 (페이지에 모달 하나일 때)
- `fetchForm(url, data)` — `URLSearchParams` POST, CSRF 메타 사용

**주의**: 레거시 `fetchForm`은 헤더 객체에 `'header': header`, `'X-CSRF-Token': token` 형태로 넣는 등 **프로젝트 내 편차**가 있을 수 있다. 신규 코드는 아래 **권장 패턴**을 우선한다.

## CSRF 권장 패턴 (fetch / JSON)

Spring Security가 기대하는 헤더 **이름**은 환경마다 다를 수 있으므로, 메타 태그 `_csrf_header`의 **content 값**을 키로 쓴다.

`feeds-detail.js` 스타일:

```javascript
function getCsrfHeaders() {
  return {
    token: document.getElementById("_csrf").content,
    header: document.getElementById("_csrf_header").content
  };
}

const csrfHeaders = getCsrfHeaders();
fetch(url, {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    [csrfHeaders.header]: csrfHeaders.token
  },
  body: JSON.stringify(data)
});
```

- 메타는 `head.html`의 `id="_csrf"` / `id="_csrf_header"` (레이아웃 적용 페이지에만 존재).
- **하드코딩 토큰·프로퍼티 파일에 토큰 저장** 금지.

## jQuery `$.ajax` 계열

`elastic.js` 등에서는 `meta[name="_csrf"]`와 `X-CSRF-TOKEN`을 사용하는 예가 있다. **같은 화면·같은 파일 스타일**을 유지하고, 새 파일을 만들 때는 위 **동적 헤더 이름** 패턴을 권장한다.

## `sidebar.js`

- `sidebar.html` **하단**에서 `type="module"`로 로드.
- `import { toggleDisplay } from "./common.js"` — 메뉴 그룹 펼침.
- 사이드바에 새 접이식 그룹을 넣으면 **버튼 id와 `toggleDisplay` 대상 id**를 여기에 연결해야 할 수 있다.

## ES module vs 일반 스크립트

| 방식 | 사용 시점 |
|------|-----------|
| `type="module"` | `import`/`export` 사용, 파일 단위 스코프 |
| 인라인 / 무듈 | 소량의 초기화 (기존 페이지에 맞춤) |

전역 오염을 줄이려면 **신규는 module**을 우선한다.

## Alpine.js

`script.html`에 `alpinejs/cdn.min.js`가 포함되어 있다. 기존 화면에서 `x-data` 등을 쓰는지 확인 후 **같은 스타일**로만 확장한다.

## 정적 경로

- JS/CSS는 `th:src`, `th:href`로 연결해 **컨텍스트 경로** 변경에 대비한다.
- 브라우저에서 절대 경로 하드코딩은 피한다 (로컬·스테이징 불일치).

## 디버깅·보안

- `console.log`에 사용자 식별자·토큰·개인정보 출력 금지.
- 네트워크 오류 시에도 **민감 데이터를 alert**로 뿌리지 않는다.
