---
description: 전체 규칙 파일 인덱스. 주제별로 참고할 규칙 파일을 안내한다.
globs:
alwaysApply: true
---
# Cursor Rules (pasta-japan-server)

이 파일은 전체 규칙 파일의 인덱스 역할을 한다.
각 규칙은 아래 mdc 파일에 정의되어 있으며,
주제에 따라 해당 파일을 참고한다.

## 규칙 단일 소스 (Cursor · Claude Code)

- **편집 원본**: `.cursor/rules/*.md` — Cursor IDE 규칙(YAML 프론트매터 포함). 내용 변경은 이 파일들만 수정한다.
- **Claude Code**: `.claude/rules/*.md` 는 동일 규칙을 가리키는 **심볼릭 링크**로 두어 에이전트·도구 간 본문 불일치를 방지한다. (링크는 `.md`를 가리킴; 일부 뷰어는 확장자와 무관하게 마크다운으로 표시한다.)

## Rules

- [01-architecture-convention.md](01-architecture-convention.md): 아키텍처 패키지 구조 및 네이밍. 4계층(Web/Application/Domain/Infrastructure), 의존성 방향, Client/ClientService/ACL, S2S API URL.
- [02-domain-entity-convention.md](02-domain-entity-convention.md): 도메인 엔티티 구현 규칙. class 사용(record 금지), primitive/wrapper, Builder 제한, Lombok 허용/금지.
- [03-jpa-entity-convention.md](03-jpa-entity-convention.md): JPA 엔티티. @Entity/@Table/@Getter, toEntity()/from(), @Builder 생성자 레벨만.
- [04-repository-pattern-convention.md](04-repository-pattern-convention.md): 리포지토리 패턴. Domain *Repository — *JpaRepository — *RepositoryImpl, Domain ↔ JPA 변환.
- [05-dto-web-layer-convention.md](05-dto-web-layer-convention.md): DTO(record) 및 Controller 규칙. *Request/*Response, *InDto/*OutDto, of/from/to, Application만 주입.
- [06-exception-handling-convention.md](06-exception-handling-convention.md): 예외 처리. Application Layer 배치, MoneyballException 상속, ExceptionConstants, @RestControllerAdvice.
- [07-general-project-convention.md](07-general-project-convention.md): 프로젝트 전역. Clean/Hexagonal, Java 17+, Spring Boot 3.x, import/logging/네이밍, JavaDoc·주석(비즈니스 맥락만), 서비스 메서드 네이밍, Build & Test, DB 마이그레이션.
- [08-test-code-convention.md](08-test-code-convention.md): 테스트 코드. TDD, Fake 우선/Mock 제한, 메서드명 영어/DisplayName 한글, AssertJ, 레이어별 전략.
- [09-guardrails.md](09-guardrails.md): 가드라인. Testcontainers(MySQL) 유지, H2 전환 금지, 사용자 요청 없이 커밋 금지, obesity 마이그레이션 파일 보호.
- [10-worktree-safety-convention.md](10-worktree-safety-convention.md): Worktree 보호. worktree용 빌드/플러그인 임시 수정 커밋·푸시 금지.
- [11-git-workflow-convention.md](11-git-workflow-convention.md): Git 브랜치/커밋 메시지/PR. api/{feat|refac|fix}/..., 한국어 커밋, Pre-commit 체크리스트.
- [12-multipart-image-validation.md](12-multipart-image-validation.md): MultipartFile 이미지 검증. @ValidImageFile 필수, @RequestPart 시 @Validated 클래스 레벨.
- [13-admin-module-overview.md](13-admin-module-overview.md): admin 모듈의 구조, 경계, 레거시 예외. `admin/**/*` 작업 시 참고.
- [14-admin-thymeleaf-layout-convention.md](14-admin-thymeleaf-layout-convention.md): admin Thymeleaf 레이아웃, fragment, URL-View-File 정합 규칙.
- [15-admin-security-history-convention.md](15-admin-security-history-convention.md): admin 권한, CSRF, OIDC, AdminHistory 기록 규칙.
- [16-admin-static-assets-convention.md](16-admin-static-assets-convention.md): admin 페이지 JS, 전역 스크립트, sidebar, static 자산 규칙.
- [17-branch-discipline.md](17-branch-discipline.md): 런타임 브랜치 안전 규칙. 커밋 전 브랜치 확인, 보호 브랜치 커밋 금지, PR 머지 후 전환.
- [18-planning-before-implementation.md](18-planning-before-implementation.md): AI 도구 구현 전 계획 수립 규칙. 멀티파일 변경 시 계획 → 승인 → 구현 순서.
- [19-architecture-boundaries.md](19-architecture-boundaries.md): 모듈 간 아키텍처 경계 강제. 타 도메인 Repository import 금지, 삭제 전 사용처 확인.

## Find by topic

- 계층 구조, Web/Application/Domain/Infra, 의존성: [01-architecture-convention.md](01-architecture-convention.md)
- Controller, Request/Response, DTO record: [05-dto-web-layer-convention.md](05-dto-web-layer-convention.md)
- Domain Entity, class, primitive/wrapper, Builder: [02-domain-entity-convention.md](02-domain-entity-convention.md)
- JPA 엔티티, toEntity/from: [03-jpa-entity-convention.md](03-jpa-entity-convention.md)
- Repository 인터페이스/구현체: [04-repository-pattern-convention.md](04-repository-pattern-convention.md)
- Client/ClientService, ACL: [01-architecture-convention.md](01-architecture-convention.md)
- 예외, ExceptionHandler: [06-exception-handling-convention.md](06-exception-handling-convention.md)
- 네이밍, 로깅, 서비스 메서드, Build & Test: [07-general-project-convention.md](07-general-project-convention.md)
- JavaDoc, 인라인 주석, `{@code}` 반복 금지: [07-general-project-convention.md](07-general-project-convention.md) §3.1
- 테스트, Fake, Mock, DisplayName: [08-test-code-convention.md](08-test-code-convention.md)
- Testcontainers, 커밋 금지, 마이그레이션 보호: [09-guardrails.md](09-guardrails.md)
- Worktree 커밋 금지: [10-worktree-safety-convention.md](10-worktree-safety-convention.md)
- 브랜치, 커밋 메시지, PR: [11-git-workflow-convention.md](11-git-workflow-convention.md)
- 이미지 업로드, @ValidImageFile: [12-multipart-image-validation.md](12-multipart-image-validation.md)
- admin 모듈 구조, SSR 경계, 레거시 예외: [13-admin-module-overview.md](13-admin-module-overview.md)
- admin Thymeleaf layout, fragment, view 경로: [14-admin-thymeleaf-layout-convention.md](14-admin-thymeleaf-layout-convention.md)
- admin 보안, `@PreAuthorize`, OIDC, 감사 로그: [15-admin-security-history-convention.md](15-admin-security-history-convention.md)
- admin JS, sidebar, static 자산: [16-admin-static-assets-convention.md](16-admin-static-assets-convention.md)
- 브랜치 확인, 보호 브랜치 커밋 금지, PR 머지 후 전환: [17-branch-discipline.md](17-branch-discipline.md)
- AI 구현 전 계획 수립, 검증 없이 단정 금지: [18-planning-before-implementation.md](18-planning-before-implementation.md)
- 타 도메인 Repository 금지, 삭제 전 사용처 확인, Qualifier: [19-architecture-boundaries.md](19-architecture-boundaries.md)

## Always applied (alwaysApply: true)

- [01-architecture-convention.md](01-architecture-convention.md)
- [07-general-project-convention.md](07-general-project-convention.md)
- [09-guardrails.md](09-guardrails.md)
- [10-worktree-safety-convention.md](10-worktree-safety-convention.md)
- [17-branch-discipline.md](17-branch-discipline.md)
- [18-planning-before-implementation.md](18-planning-before-implementation.md)
- [19-architecture-boundaries.md](19-architecture-boundaries.md)
