---
name: flyway
description: "Flyway 마이그레이션 실행 및 상태 확인"
trigger: "/flyway"
args: "[migrate|info|repair|validate] (기본: migrate)"
version: "1.0"
last-modified: "2026-04-14"
changelog: "실전 프로젝트(pasta-japan-server)에서 forge로 역수입"
---

# /flyway

## 용도

Flyway 마이그레이션을 실행하거나 상태를 확인한다.

## 인자

| 인자 | 설명 | 기본값 |
|------|------|--------|
| `migrate` | 마이그레이션 실행 | ✅ (기본) |
| `info` | 마이그레이션 상태 확인 (적용/미적용 목록) | |
| `repair` | flyway_schema_history 보정 (실패 기록 정리) | |
| `validate` | 마이그레이션 파일과 DB 상태 검증 | |

## 실행 로직

### migrate (기본)
1. `./gradlew flywayInfo` 로 pending 마이그레이션 존재 여부 확인
2. pending이 있으면 `./gradlew flywayMigrate` 실행
3. 결과 출력 (적용된 마이그레이션 수, 현재 버전)

### info
1. `./gradlew flywayInfo` 실행
2. 최근 10개 마이그레이션 상태 요약 출력

### repair
1. 사용자에게 repair 사유 확인
2. `./gradlew flywayRepair` 실행
3. 결과 출력

### validate
1. `./gradlew flywayValidate` 실행
2. 검증 결과 출력

## 출력 형식

```
✓ Flyway migrate 완료: {N}개 마이그레이션 적용, 현재 버전 {version}
```
또는
```
✓ Flyway info: pending 마이그레이션 없음 (현재 버전: {version})
```

## 가드레일

- repair는 실행 전 반드시 사유를 확인한다
- 마이그레이션 실행 전 Docker(MySQL)가 실행 중인지 확인한다
- 에러 발생 시 로그 마지막 30줄을 출력하여 원인 파악을 돕는다
