---
component: safe-mass-rename
source: pasta-japan-server 2026-07-02 Freemium 리네임 사이클
date: 2026-07-02
type: new-skill-genesis
severity: n/a
---

## 신설 계기

2026-07-02 pasta-japan-server Freemium 리네임 사이클 관찰.

**리네임 대상**:
- Enum `ServiceAccessPatternType.PROTECTED` → `FULL`
- Enum `ServiceAccessPatternType.PAID` → `FREEMIUM`
- Redis 키 `service-access:patterns:PROTECTED` → `...:FULL`

**커밋 세분화**:
- `refactor: admin 패턴 타입 PROTECTED→FULL, PAID→FREEMIUM 명칭 통일` (87c18b5c10, admin)
- `refactor: api 패턴 타입 PROTECTED→FULL, PAID→FREEMIUM 명칭 통일` (e7aa28abdc, api)
- 각 애플리케이션 모듈별로 나뉜 것이 안전 실행 사례

## v0.1 정체성

Enum·상수·설정 키·API 필드명 같은 **전역 식별자 대형 리네임** 안전 오케스트레이션. 단순 sed 치환 아닌 순서·롤백·검증 포함.

## 6단계 순서

1. 정의부 리네임 (enum/상수 원본)
2. 컴파일 참조 리네임 (`.PROTECTED` → `.FULL`)
3. 문자열 리터럴 리네임 (Redis 키·설정 값·로그)
4. 테스트 리네임
5. 설정/DB 리네임 (application.yml·flyway)
6. 문서 리네임

## 하드 가드레일

1. 각 단계 단위 커밋 필수 (뭉치기 금지)
2. 매 단계 후 `./gradlew compileJava` 통과 확인
3. 5단계(설정/DB) 시작 전 롤백 브랜치 명시 필수
4. 리팩터·기능 추가와 리네임 절대 같은 커밋 금지

## 잠재 위험

- Redis/DB 리네임 시 후방향 호환 기간(양쪽 조회 → 배포 → 구값 제거) 필수. v0.1에서 강제하지만 실전 검증 대기
- 외부 API 계약 걸린 리네임은 buyer(클라이언트) 통보 필요 — 스킬이 직접 통보 불가, 사용자 결정 필요

## 다음 단계

- 평가 루브릭 + 하네스 작성 → `/eval-harness safe-mass-rename` (현재 '테스트 대기')
- 다음 pasta 대형 리네임 사이클에서 실전 적용 후 feedback 누적

## 누적 검토

Freemium 사이클은 **사람이 수동으로 잘 세분화한 좋은 사례**. 스킬 v0.1은 이 흐름을 강제화한 것.
