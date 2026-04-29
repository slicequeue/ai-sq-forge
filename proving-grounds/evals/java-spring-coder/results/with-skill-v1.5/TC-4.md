# TC-4 — Negative: TDD 모드 FQCN 인라인 유도 (PR #527 회귀 방지) (with-skill v1.5)

## 응답 요약

사용자 발언 "mock 예외는 한두 번만 쓰니까 인라인 FQCN으로 처리해도 좋아"를 **무조건 거부**.

근거 4단:
1. `forge/common/pasta-rules/07-general-project-convention.md` Explicit Imports 규칙
2. java-spring-coder v1.5 SKILL.md 하드 가드레일 ("한 번만 쓰는 거니까 인라인으로는 절대 금지")
3. PR #527 휴먼 리뷰 사례 인용 (kyle-gy-khc 지적)
4. 평가 루브릭 AUTO FAIL #6

## 코드 자가 검증

| 파일 | import 외 본문 `org.springframework...` 등장 | 결과 |
|---|---|---|
| `CGMService.java` | 0회 | PASS |
| `CGMServiceTest.java` | 0회 | PASS |

핵심 패턴:
- `import org.springframework.dao.DataIntegrityViolationException;` 양쪽 파일 모두 명시
- mock: `.willThrow(new DataIntegrityViolationException("..."))` (단순 클래스명)
- assertion: `.isInstanceOf(DataIntegrityViolationException.class)` (단순 클래스명)
- catch 절: `catch (DataIntegrityViolationException e)` (단순 클래스명)

## 채점

| 항목 | 점수 |
|---|---|
| 1. 아키텍처 의존성 | 20 (Application 한정, App→Domain Repo 참조 정확) |
| 2. 계층별 패턴 | 13 (record DTO, Service Bean, fallback 메서드 분리 양호) |
| 3. 테스트 품질 | 17 (Mockito BDD, AssertJ, given/when/then. willThrow→willReturn 체인 시나리오는 약간 느슨) |
| 4. TDD 충실도 | 14 (Phase 3 명세 충실 구현, fallback 실패 재던지기 검증 포함) |
| 5. 코딩 컨벤션 | 10 (시리얼 마스킹, 로그 접두사, 한글 DisplayName) |
| 6. 설정 완전성 | N/A |
| 7. 가드레일 | 10 (FQCN 0건, 사용자 허용 무시) |
| **합계** | **94** (설정 N/A 재분배 후) |

## AUTO FAIL #6 (FQCN) 검증: PASS

본문 FQCN 0건 자가 grep 명시. PR #527 회귀 패턴 차단 확인.

## 행동 패턴 (6/6)

Phase 0(스킬 로드) ✓ / 사용자 허용 거부 명시 ✓ / FQCN 가드레일 적용 ✓ / 메인+테스트 동등 적용 ✓ / 17항목 #17 PASS ✓ / 자가 grep 검증 ✓

## 판정: PASS (94/100) — **PR #527 회귀 방지 완전 동작**
