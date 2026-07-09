---
component: self-code-reviewer
source: forge 내부 (사용자 재설계 제안)
date: 2026-07-09
type: major-refactor
severity: high
---

## 증상 (v1.11 시점)

- self-code-reviewer 파일이 489줄로 forge 원칙("본문 400줄 이내") 초과
- 6~7월 사이클에서 관점 혼재된 룰 7건 추가 (KISA·성능·아키텍처·공통)
- 관점 경계 없이 룰이 늘어나 관리 부담·중복 위험

## 사용자 재설계 제안 (2026-07-09)

> self-review 부류도 하위에 좀더 아키텍처 코딩 컨벤션 임포트 관계 모듈 관계 보는 것 / 코드 로직·비즈니스 로직 요건대로 잘 구현했는지 / 보안 문제 시큐어 코딩 / 성능 관점 이런식으로 다각적으로 리뷰 스킬을 쪼개고 그것을 에이전트가 스킬들을 입체적으로 활용해서 처리하는 백엔드 자바 전문 복합 리뷰어를 만들어보는 것

**Q&A 3라운드**로 C안(하이브리드) 확정:
- 공통은 self / 도메인 특수만 관점 스킬
- 각자 독립 자동 트리거 + 복합 리뷰어 안에서 조합
- 하네스 스킬 신설과 함께
- coding-implementer Phase 3-4 위임 대상: java-composite-reviewer 에이전트
- 리포트 형식은 self와 동일
- 이관된 룰 완전 제거 (슬림화)
- java-architecture-reviewer가 pasta-rules 참조

## v2.0 슬림화 결과

**489줄 → 316줄** (300 목표 +16 초과, 400 원칙 이내)

**이관 완료** (self에서 완전 제거):
- v1.7 KISA 시큐어코딩 → java-secure-coding-reviewer
- v1.5 FQCN 인라인 → java-architecture-reviewer
- v1.10 Bean Qualifier cross-module → java-architecture-reviewer
- v1.10 인터페이스 구현체 모듈 → java-architecture-reviewer
- v1.9 WebClient timeout·4xx retry → java-performance-reviewer
- v1.9 싱글톤 mutable field → java-performance-reviewer
- v1.9 Soft-delete UNIQUE → java-performance-reviewer

**잔존** (v2.0 공통 스코프):
- v1.11 @Profile 문법 · 광범위 catch · Session 오염 · 입력 형식 검증
- v1.10 임시 진단 로그 / v1.9 catch 부가 주석 / v1.8 i18n·Locale
- admin 모듈 검사 / 환경변수·SecurityConstants·마이그레이션·페이지네이션 등 도메인 무관 공통

**신규 v2.0 요소**:
- 최상단 "관점 리뷰 오케스트레이션" 섹션 (4가지 시나리오)
- 하드 가드레일 4번째: "스코프 침범 금지"
- 참조 인덱스에 4개 관점 스킬 + composite 에이전트 위치

## 3개 신설 스킬 요약

| 이름 | 스코프 | 파일 크기 |
|---|---|---|
| java-secure-coding-reviewer 0.1 | KISA + OWASP + PII + 시크릿 + CVE | 335줄 |
| java-performance-reviewer 0.1 | N+1·JPA + 캐시 + 트랜잭션 + 리소스 + GC | 293줄 |
| java-architecture-reviewer 0.1 | 4-Tier + Bean + 모듈 + 패턴 + pasta-rules | 269줄 |

각 하네스 3종(rubric·harness·test-cases) 스킬 신설과 함께 작성.

## 복합 리뷰어 신설

java-composite-reviewer 0.1 에이전트 (284줄):
- Phase 0~4 워크플로 (현황·계획·병렬 리뷰·통합·보고)
- Task tool 병렬 호출 (컨텍스트 격리)
- 관점 자동 판단 매트릭스 (파일 유형 → 관점 우선순위)
- AUTO FAIL 우선순위: 보안 > 성능 > 아키텍처 > 공통

## coding-implementer 갱신

v0.4 → v0.5:
- Phase 3-4 자체 리뷰 위임 대상: self-code-reviewer → java-composite-reviewer 에이전트
- 관점 지정 옵션 추가 (`--scope=security|performance|architecture|common`)

## 누적 검토

self-code-reviewer 역사상 **가장 큰 리팩터** (major bump v1.11 → v2.0). 6개월간 진화 방향(v1.5 FQCN → v1.11 4대 검출 룰)의 정리 지점. 향후 신규 룰 추가 시 관점별 스킬에 배치, 공통 룰만 self에 축적.
