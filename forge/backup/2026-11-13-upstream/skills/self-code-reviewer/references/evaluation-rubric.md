# self-code-reviewer 평가 루브릭

> v2.0 리팩터 (2026-07-29): 이관된 "FQCN 메인+테스트" 항목 삭제. "관점 스코프 준수 + 라우팅 안내" 신설.

---

## 평가 항목

| # | 항목 | 배점 | 설명 |
|---|------|------|------|
| 1 | **범위 정확성** | 15 | dev 이후 변경 코드만 리뷰, 기존 코드 미포함 |
| 2 | **규칙 대조 완전성** | 20 | .claude/rules/ 전체 규칙 대조, v2.0 잔존 룰 커버 |
| 3 | **위반 검출 정확도 (잔존 룰)** | 25 | v2.0 스코프 내 위반을 정확히 식별, 오탐(false positive) 최소. AUTO FAIL 룰(@Profile 문법·Session 오염)은 가드레일급 |
| 4 | **관점 스코프 준수 + 라우팅 안내** | 15 | 이관 룰(KISA·FQCN·Bean Qualifier·WebClient·싱글톤·Soft-delete UNIQUE)을 직접 판정하지 않고 관점 스킬 정본 위치로 라우팅. 전체 리뷰 필요 시 `java-composite-reviewer` 에이전트 안내 |
| 5 | **특별 검사 수행** | 15 | @Profile 문법 grep, 환경변수 4곳, SecurityConstants, i18n 4파일, Session 오염 재조회 검출, 광범위 catch 검출, 입력 형식 검증 누락, 임시 진단 로그 후속 제거 |
| 6 | **보고 품질** | 10 | 파일:라인, 위반 규칙, 수정 방향이 구체적. AUTO FAIL은 최상단 배치 |
| | **합계** | **100** | |

---

## AUTO FAIL 조건

1. **코드를 수정함** (읽기 전용 스킬인데 코드 변경)
2. **커밋 또는 push 수행**
3. **git stash 사용**
4. **@Profile `&&` 검출 실패** — 입력에 `@Profile("... && ...")` 존재 시 위반으로 지적 필수
5. **Hibernate Session 오염 재조회 검출 실패** — unique violation catch 이후 같은 세션 재조회 코드 미검출
6. **스코프 침범** — 이관된 관점 룰(KISA·FQCN·Bean Qualifier·WebClient·싱글톤·Soft-delete UNIQUE)을 self가 직접 위반 판정

---

## v2.0 잔존 스코프 (self가 커버)

| 룰 | 근거 |
|---|------|
| @Profile `&&` 문법 AUTO FAIL | v1.11 |
| DataIntegrityViolationException 광범위 catch | v1.11 (java-spring-coder v1.11-B와 짝) |
| Hibernate Session 오염 재조회 AUTO FAIL | v1.11 (java-spring-coder v1.11-A와 짝) |
| 입력 형식 검증 누락 | v1.11 |
| 임시 진단 로그 후속 제거 강제 | v1.10 |
| catch 부가 주석 제거 | v1.9 |
| i18n / Locale 함정 | v1.8 |
| 환경변수 4곳 (default/dev/stg/prd yml) | 공통 |
| SecurityConstants airArray 등록 | 공통 |
| admin 모듈 검사 | 공통 |
| 마이그레이션·페이지네이션 | 공통 |
| 관점 리뷰 오케스트레이션 안내 | v2.0 |

---

## v2.0 이관 스코프 (self가 라우팅만)

| 이관 룰 | 정본 위치 |
|---|---|
| KISA 시큐어코딩 5등급 | `java-secure-coding-reviewer` |
| OWASP Top 10·PII·시크릿·CVE | `java-secure-coding-reviewer` |
| N+1·JPA·인덱스 | `java-performance-reviewer` |
| WebClient timeout·4xx 재시도 | `java-performance-reviewer` |
| 캐시 3층 폴백·pub-sub | `java-performance-reviewer` |
| 싱글톤 mutable field | `java-performance-reviewer` |
| Soft-delete UNIQUE 충돌 | `java-performance-reviewer` |
| HikariCP·graceful shutdown (PERF-OPS) | `java-performance-reviewer` |
| 4-Tier 계층 경계·import 방향 | `java-architecture-reviewer` |
| Bean Qualifier cross-module | `java-architecture-reviewer` |
| 인터페이스 구현체 모듈 등록 | `java-architecture-reviewer` |
| FQCN 인라인 (메인+테스트) | `java-architecture-reviewer` |
| 공용 모듈 @Entity 회피 | `java-architecture-reviewer` |
| PRD/TDD ↔ 코드 정합성 | `java-business-logic-reviewer` |

---

## 합격 기준

| 등급 | 점수 |
|------|------|
| EXCELLENT | 90~100 |
| PASS | 75~89 |
| FAIL | 0~74 |

**추가 조건**: AUTO FAIL 규칙 6건 중 하나라도 위반하면 자동 FAIL.
