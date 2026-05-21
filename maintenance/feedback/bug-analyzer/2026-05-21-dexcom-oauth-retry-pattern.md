---
component: bug-analyzer
source: pasta-japan-server
date: 2026-05-21
type: improvement
related_commits: 816c56d60e, 2dc6614cd2, f5ed7dd757
severity: medium
---

## 증상

이번 주 Dexcom OAuth refresh 관련 일시 장애 분석·수정이 3건 누적. forge-upstream으로 가져온 bug-analyzer v0.1에 외부 HTTP/OAuth 일시 장애 카탈로그가 없어 패턴 재사용 어려움.

### 사례

| commit | 내용 |
|--------|------|
| 816c56d60e (#570) | [CGM] Dexcom OAuth refresh 일시 장애 재시도 + refresh 호출 타임아웃 명시 |
| 2dc6614cd2 | Dexcom 재시도 조건에 ReadTimeout과 OAuth refresh I/O 일시 장애 추가 |
| f5ed7dd757 | Dexcom OAuth refresh 토큰 갱신에 connect/read 타임아웃 명시 |

3건 모두 외부 OAuth refresh 호출의 일시 장애에 대한 점진 개선.

## 개선 제안 (bug-analyzer v0.2)

v0.2 본문에 "외부 OAuth/HTTP 일시 장애 분석 카탈로그" 섹션 추가. 키워드별 분류 표:
- ReadTimeoutException / ConnectTimeoutException / OAuth2AuthorizationException / WebClientResponseException 4xx/5xx / Connection pool exhausted / SocketTimeoutException

분석 시 필수 확인 4항목:
1. WebClient timeout 설정 명시 여부
2. 재시도 조건이 일시 장애 한정인가 (4xx 재시도 위험)
3. 싱글톤 상태 동시성 (KbsmcEhrClient 2adbd26c26 사례)
4. 트랜잭션 전파 (REQUIRES_NEW 검토 — 1066af4f54)

## 누적 검토

bug-analyzer 신규 forge 등록 직후 첫 보강. 1건 누적이지만 3사례.
