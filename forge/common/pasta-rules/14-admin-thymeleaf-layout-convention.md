---
description: admin Thymeleaf 레이아웃과 템플릿 정합 규칙.
globs: admin/**/*
alwaysApply: false
---

# Admin Thymeleaf Layout

## Layout First

- 일반 페이지는 `layout:decorate="~{layout/layout}"`와 `layout:fragment="content"`를 기본으로 사용한다.
- 페이지 본문은 `content-wrapper`, `content`, `content-header` 같은 AdminLTE 구조를 유지한다.
- `head`, `top`, `sidebar`, `footer`, `script`는 직접 복제하지 말고 `layout/fragments/*`를 재사용한다.

## URL-View-File 정합

- `@GetMapping("/x")` -> `return "a/b"` -> `templates/a/b.html`은 하나의 계약이다.
- 페이지를 추가하거나 이름을 바꿀 때는 매핑, 반환 문자열, 템플릿 경로를 항상 함께 수정한다.

## 템플릿 작성 규칙

- 리소스와 액션 경로는 `th:src`, `th:href`, `th:action`을 우선 사용한다.
- 페이지 전용 script는 템플릿 상단 또는 본문 초입에서 명시적으로 로드한다.
- 모달, 재사용 UI, 권한 조각은 fragment로 분리하고 `th:replace`로 포함한다.

## 전역 변경 가드레일

- `layout/layout.html`과 `layout/fragments/*` 변경은 모든 페이지에 영향을 주므로 마지막 수단으로만 수정한다.
- 비슷한 화면이 있으면 새 패턴을 만들기보다 기존 Controller + HTML + JS 세트를 복제해 맞춘다.
