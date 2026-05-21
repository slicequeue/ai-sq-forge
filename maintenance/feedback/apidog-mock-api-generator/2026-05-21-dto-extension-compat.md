---
component: apidog-mock-api-generator
source: pasta-japan-server
date: 2026-05-21
type: improvement
related_commits: 6055f208fc, 0471249e56
severity: low
---

## 증상

forge-upstream 후 apidog-mock-api-generator v0.1에 (1) Phase 1.5 현황 파악 (2) DTO 확장 호환성 (3) Mock 데이터 표식 가이드 부재.

### 관련 사례

- **commit 6055f208fc**: MCP get_user_profile 응답에 페르소나·환자 정보 필드 추가 — 기존 응답에 nullable 필드 추가 패턴 (모바일 앱 구버전 호환 유지)
- **commit 0471249e56**: DB손해보험 현물 지급 API 연동 — 외부 API mock으로 검증 가능 영역

## 개선 제안 (apidog-mock-api-generator v0.2)

- Phase 1.5: Apidog 스펙 조회 전 기존 동일 URL 컨트롤러 grep + 기존 응답 DTO 시그니처 확인
- DTO 확장 호환성 하드 가드레일: 기존 필드 제거·타입 변경 금지 / nullable 추가만 허용
- Mock 데이터 표식: "김파스타" 한국어 더미 + ID는 음수/99999+로 운영과 구분

## 누적 검토

apidog-mock-api-generator 신규 forge 등록 직후 첫 보강. 1건 누적.
