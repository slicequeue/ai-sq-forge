---
description: admin JS, static 자산, sidebar 연동 규칙.
globs: admin/**/*
alwaysApply: false
---

# Admin Static Assets

## Page Script First

- 페이지에 필요한 JS는 별도 파일로 만들고 해당 페이지에서만 로드한다.
- 페이지 HTML과 JS는 같은 베이스 이름을 사용한다. 예: `user-manage.html` + `user-manage.js`
- 공통 함수만 모듈로 분리하고, 공통 모듈 파일은 페이지에서 직접 `script` 태그로 전역 로드하지 않는다.

## 전역 리소스 최소화

- `layout/fragments/script.html`은 전역 영향이 크므로 정말 공통인 스크립트만 둔다.
- 새 기능 때문에 전역 JS/CSS를 추가하기 전, 페이지 전용 로드로 해결 가능한지 먼저 판단한다.
- TinyMCE, DataTables 같은 vendor 자산은 기존 `static/js`, `static/css` 배치를 따른다.

## Sidebar 정합

- 새 메뉴를 추가할 때는 `sidebar.html` 링크, 컨트롤러 매핑, 권한 조건을 함께 맞춘다.
- 트리 메뉴 토글 동작이 필요하면 `static/js/sidebar.js`의 기존 패턴을 재사용한다.

## Ajax 패턴

- fetch 또는 XHR 요청은 CSRF meta를 읽어 동적으로 헤더를 세팅한다.
- 이미지 업로드처럼 기존 구현이 있으면 새 유틸을 만들기보다 그 패턴을 복제-수정한다.
