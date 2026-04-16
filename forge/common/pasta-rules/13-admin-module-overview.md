---
description: admin 모듈 구조와 레거시 경계를 설명한다.
globs: admin/**/*
alwaysApply: false
---

# Admin Module Overview

`admin` 모듈은 `pasta-api` 스타일의 REST/Swagger 중심 모듈이 아니라, **Thymeleaf SSR + AdminLTE 기반 운영자 UI** 모듈이다.

## 핵심 구조

- Java 코드는 `com.kakaohealthcare.moneyballadmin` 아래에 있고, `controllers`, `service`, `repository`, `dto`, `entity`, `mapper`, `util` 등 **레이어 혼합형 실무 구조**를 사용한다.
- 화면은 `admin/src/main/resources/templates/`, 정적 자산은 `admin/src/main/resources/static/`, DB 변경은 `admin/src/main/resources/db/migration/`에 둔다.
- 공통 레이아웃은 `templates/layout/layout.html`, 공통 조각은 `templates/layout/fragments/`가 기준이다.

## 다른 모듈과 구분할 점

- `admin`에 `pasta-api`의 DTO/Controller 규칙을 그대로 이식하지 않는다.
- 기본 패턴은 `@RestController`가 아니라 **뷰를 반환하는 `@Controller`** 이다.
- `MoneyballAdminApplication`은 여러 `moneyball` 모듈의 엔티티·리포지토리·서비스를 함께 스캔한다. 새 의존성을 추가할 때는 이 구조를 먼저 확인한다.

## 레거시 예외

- 설정 패키지는 오타가 있어도 기존 관례대로 `configrations`를 사용한다.
- 일부 하위 패키지는 `controllers`가 아니라 `controller` 단수를 쓴다. 신규 추가 시에는 기존 영역 관례를 우선 따른다.
- README의 Java 17 안내와 달리 현재 워크스페이스 공통 빌드 규칙은 JDK 21 기준이다. 실행·검증은 프로젝트 최신 규칙을 따른다.
