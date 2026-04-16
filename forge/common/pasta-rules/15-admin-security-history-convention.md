---
description: admin 보안, 권한, 감사 로그 규칙.
globs: admin/**/*
alwaysApply: false
---

# Admin Security And History

## 인증과 권한

- 기본 웹 엔드포인트는 `@Controller`로 만들고, 권한은 `@PreAuthorize`로 명시한다.
- 새 화면, 메뉴, 액션을 추가할 때는 기존 authority 문자열 체계와 맞춘다.
- 인증 주체는 기존처럼 `@AuthenticationPrincipal OidcUser` 사용 패턴을 우선 따른다.

## CSRF

- 상태 변경 요청은 `head` fragment가 주입하는 `_csrf`, `_csrf_header` meta 값을 사용한다.
- 토큰 이름이나 헤더 값을 하드코딩하지 않는다.

## 감사 로그

- 운영자 조회/수정/삭제/진입 이력은 `AdminHistoryService`로 남긴다.
- 기능 식별자는 문자열을 새로 만들기보다 `AdminFunction` enum을 우선 사용한다.
- 노출 메시지는 관리자 행동을 추적할 수 있게 구체적으로 쓰되, 민감정보와 과도한 원문 payload는 주의한다.

## 점검 포인트

- 사이드바 메뉴를 노출했으면 실제 엔드포인트 권한과 일치하는지 확인한다.
- 업로드, 삭제, 비동기 요청은 403 케이스를 먼저 의심하고 CSRF와 authority를 함께 점검한다.
