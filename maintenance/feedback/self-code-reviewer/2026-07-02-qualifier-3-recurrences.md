---
component: self-code-reviewer
source: pasta-japan-server 6월 사고 사이클
date: 2026-07-02
type: rule-strengthening
severity: critical
---

## 증상

**Bean Qualifier mismatch가 5월 → 6월 사이 3회 재발했다**. forge에 v1.7부터 "Bean 이름 매직 스트링 금지" 룰이 존재했음에도.

| 회차 | 모듈 | PR | 원인 |
|------|------|-----|------|
| 1회 | api | 5월 초 | 기존 |
| 2회 | batch·batch-app | #593 (6/16) | 별개 OAuth2 설정이 메서드명 기반 등록 |
| 3회 | admin | #588 (6/19) | AdminAuth2Configuration이 같은 실수 반복 |

**증거**: `cgm/DexcomWebClientConfiguration`이 `@Qualifier(DEXCOM_AUTHORIZED_CLIENT_MANAGER)` Bean을 요구하는데, 새 모듈이 추가될 때마다 `@Bean("dexcomAuthorizedClientManager")` 없이 메서드명 기반 `authorizedClientManager`로 등록 → `No qualifying bean` 컨텍스트 기동 실패.

## 추가 사례

- **인터페이스 구현체 모듈별 등록 누락 (#597, 6/18)**: `UserDiabetesTypeService` 인터페이스만 있고 batch 모듈에 구현체 Bean 없어 기동 실패
- **임시 진단 로그 기술 부채 (#616, 6/23)**: 대시보드 403 진단용 임시 로그 커밋 후 제거 커밋 없음

## 개선 반영 (v1.10)

3건 신규 검사 항목:
1. **Bean Qualifier cross-module 검증**: `@Qualifier(CONST)` 사용 시 → 해당 상수를 참조하는 `@Bean(CONST)` 정의가 **모든 애플리케이션 모듈**에 있는지 grep 검증. AUTO FAIL 확장 (모듈 신규 추가 시 재발 케이스)
2. **인터페이스 구현체 모듈 등록**: 새 인터페이스 도입 시 → 주입받는 모든 모듈에 구현체 Bean 등록 확인
3. **임시 진단 로그 후속 제거**: 로그 문구에 "임시/진단/temp/diagnostic" 키워드 포함 시 TODO 태그 + 이슈 링크 강제

## 근본 원인 진단

**규칙 자체는 있었지만 cross-module 검증이 없어 3연타 재발**. 룰이 개별 파일 스캔 관점에 머무르고, 새 모듈이 추가될 때 "모든 사용처가 상수 참조를 따르는가" 검증 절차가 없었음.

## 누적 검토

Bean Qualifier는 forge 도입 이후 최다 재발 사고 카테고리. v1.10 강화로 3연타 재발 차단 가능한지 회귀 평가 필수.
