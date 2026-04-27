# Golden Path 맵 (복사-수정 시작점)

신규 구현 시 0부터 만들지 말고, 아래 조합 중 가장 가까운 것을 복사-수정한다.

## 1) 목록 + 모달 등록 + 페이지 JS

| 용도 | 파일 |
|------|------|
| Controller | `admin/src/main/java/com/kakaohealthcare/moneyballadmin/controllers/cms/BannerController.java` |
| List Template | `admin/src/main/resources/templates/cms/banners.html` |
| Modal Fragment | `admin/src/main/resources/templates/cms/banner-register.html` |
| Page JS | `admin/src/main/resources/static/js/cms/banner.js` |

포인트:
- 목록 페이지에서 `th:replace`로 모달 fragment 삽입
- 페이지 하단 `type="module"` JS 로드

## 2) 사이드바 토글 메뉴

| 용도 | 파일 |
|------|------|
| Sidebar Markup | `admin/src/main/resources/templates/layout/fragments/sidebar.html` |
| Toggle JS | `admin/src/main/resources/static/js/sidebar.js` |
| Common Toggle Util | `admin/src/main/resources/static/js/common.js` |

포인트:
- 버튼 id와 토글 대상 id를 한 쌍으로 유지
- 사이드바 하단 module script 로드 패턴 유지

## 3) fetch + CSRF 상태 변경

| 용도 | 파일 |
|------|------|
| fetch CSRF 동적 헤더 | `admin/src/main/resources/static/js/cms/feeds-detail.js` |
| 공통 CSRF 사용 함수 예시 | `admin/src/main/resources/static/js/common.js` |
| CSRF meta 제공 | `admin/src/main/resources/templates/layout/fragments/head.html` |

포인트:
- `_csrf_header`를 키로 써서 헤더 이름 하드코딩 회피
- JSON/폼 전송 방식 혼용 시 기존 화면 패턴 우선

## 4) 상단/로그아웃/권한 연동

| 용도 | 파일 |
|------|------|
| Topbar | `admin/src/main/resources/templates/layout/fragments/top.html` |
| Security 노출/규칙 | `admin/src/main/java/com/kakaohealthcare/moneyballadmin/configrations/SecurityConfig.java` |

포인트:
- 로그아웃은 POST 폼 패턴 유지
- 권한 문자열은 동일 기능 컨트롤러와 맞춤

## 사용 규칙

1. 가장 가까운 Golden Path를 고른다.
2. 해당 경로에서 Controller + Template + JS를 **세트로** 읽는다.
3. 구조를 유지한 채 도메인 용어만 치환한다.
4. 마지막에 SKILL.md Self-check를 채운다.
