# TDD Template Guide (Admin)

## 목적
- TDD는 PRD를 **개발 실행 가능한 기술 계획**으로 변환하는 문서다.
- “무엇을 만들까”보다 “어떤 순서로 안전하게 구현/검증할까”를 다룬다.

## 필수 섹션
1. 구현 개요(연관 PRD, 변경 범위, 핵심 결정)
2. 시스템/화면 흐름(`@Controller -> template -> static/js`)
3. 데이터/이력 설계(admin history 포함)
4. 엔드포인트/권한 설계(해당 시)
5. Phase 계획표(목표, TODO, 산출물, 검증)
6. 테스트 전략(Web/Application/Infrastructure)
7. Open Questions
8. (권장) **Cursor rules 교차**: `.claude/rules/00-rules-index.mdc` 기준 admin **13~16** — 화면마다 URL–뷰–템플릿, fragment, 페이지 전용 JS, sidebar·권한, `SecurityFilterChain`+`@PreAuthorize`
9. (큰 기능 권장) **실행 계획 분리**: SSOT(`docs/…`) vs `works/…/plan-01~` 체크리스트 — 스펙 변경은 SSOT 우선

## 작성 규칙
- Phase는 완료 조건이 보이는 단위로 분리한다.
- 보안/권한/CSRF를 “추가 고려”가 아닌 필수 설계로 기록한다.
- 사이드바/진입 동선 영향 여부를 구조 변경 항목에 포함한다.

## 금지
- “나중에 확인”만 남기고 검증 방법을 쓰지 않는 설계.
