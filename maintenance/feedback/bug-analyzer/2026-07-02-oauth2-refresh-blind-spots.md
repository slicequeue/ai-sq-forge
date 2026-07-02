---
component: bug-analyzer
source: pasta-japan-server PR #594 (2026-06-18)
date: 2026-07-02
type: catalog-expansion
severity: medium
---

## 증상

Dexcom 혈당 저장 flow에서 404 원인을 찾지 못하는 사각지대가 3개 발견됐다. v0.2의 외부 OAuth 카탈로그(7종)는 응답 4xx/5xx만 다뤘고, refresh 자체 실패나 아예 호출을 안 하는 케이스는 없었다.

## 3개 사각지대

1. **refresh 단계 `invalid_grant`**: 응답 처리 필터는 `devices/egvs` 응답 4xx/5xx일 때만 동작. refresh 실패는 필터가 개입 못 함
2. **`client_authorization_required`**: 클라이언트가 인증 필요를 감지해 API 호출 skip. 필터가 볼 응답이 없음
3. **연결 상태 pre-check 부재로 헛호출**: 토큰 사망·미연결 사용자에게도 매번 Dexcom 조회 → 실패 후 재시도 버스트

## 개선 반영 (v0.3)

- "OAuth2 refresh 사각지대" 신규 카테고리 (WebClient 4xx 룰과 층위 분리)
- 후처리 로깅 3원칙: 사유별 WARN 로깅 / PII(userId) 본문 제외 / 페이로드 전체 → 요약(호출자·건수·요약)
- 분석 필수 확인 항목 #5~#7 추가

## 층위 구분

| 층위 | 담당 스킬 | 관점 |
|------|----------|------|
| API 응답 4xx | java-spring-coder v1.9 WebClient 룰 | 응답 후 재시도·필터 |
| refresh 자체 실패 / 호출 안 함 | bug-analyzer v0.3 | 응답 자체 없음 |

## 누적 검토

외부 OAuth 사고는 Dexcom 시리즈에서 반복 발생. 다음 사이클도 관찰 필요.
