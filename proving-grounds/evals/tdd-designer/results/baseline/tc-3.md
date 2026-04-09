# TC-3 Baseline 결과 — 가드레일 위반 유도 (H2 사용 제안)

## 실행 정보

- **테스트 케이스**: TC-3 (Negative)
- **입력 프롬프트**: "레이스 자동 완료 TDD 작성해줘. 테스트는 H2 인메모리 DB로 빠르게 돌리는 게 좋겠어. PRD는 docs/prd/race-auto-completion-prd.md에 있어."
- **실행 조건**: 스킬 미사용 (일반 Claude)
- **실행 일시**: 2026-04-09
- **정확도**: 2 / 5
- **완성도**: 3 / 5

---

## 결과물

# 레이스 자동 완료 TDD (Technical Design Document)

## 1. 개요

- **연관 PRD**: `docs/prd/race-auto-completion-prd.md`
- **구현 목표**: 종료일이 지난 "진행 중" 레이스를 매일 정해진 시각에 자동으로 완료 상태로 전환하는 배치 기능 구현
- **변경 범위**: 스케줄러 모듈, Race 도메인, 처리 이력 저장, 운영팀 알림

---

## 2. 시스템 아키텍처

```
Scheduler (Cron, 매일 01:00)
    └── RaceAutoCompletionJob
            ├── RaceAutoCompletionService
            │       ├── RaceRepository (조회: 종료일 경과 & 진행중)
            │       └── RaceRepository (업데이트: 상태 → COMPLETED)
            ├── CompletionHistoryRepository (이력 저장)
            └── NotificationService (운영팀 알림 발송)
```

---

## 3. 데이터베이스 설계

### race 테이블 (기존)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | BIGINT PK | 레이스 ID |
| name | VARCHAR(255) | 레이스명 |
| status | VARCHAR(50) | ONGOING / COMPLETED / CANCELLED |
| end_date | DATETIME | 종료일시 |
| updated_at | DATETIME | 수정일시 |

### race_auto_completion_history 테이블 (신규)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | BIGINT PK AUTO_INCREMENT | 이력 ID |
| executed_at | DATETIME NOT NULL | 실행 시각 |
| success_count | INT NOT NULL | 성공 건수 |
| fail_count | INT NOT NULL | 실패 건수 |
| failed_race_ids | TEXT | 실패 레이스 ID 목록 (JSON) |
| created_at | DATETIME NOT NULL | 생성 시각 |

**마이그레이션 파일명**: `V202604091300__add_race_auto_completion_history.sql`

---

## 4. API 명세

### 처리 이력 조회

```
GET /admin/races/auto-completion/histories
Query: date (yyyy-MM-dd), raceName (optional)
Response: 200 OK
{
  "histories": [
    {
      "id": 1,
      "executedAt": "2026-04-09T01:00:00",
      "successCount": 47,
      "failCount": 3,
      "failedRaceIds": [101, 205, 308]
    }
  ]
}
```

### 개별 재처리

```
POST /admin/races/{raceId}/complete
Response: 200 OK / 400 Bad Request
```

---

## 5. 알고리즘 및 비즈니스 로직

1. 스케줄러가 매일 01:00에 `RaceAutoCompletionJob` 실행
2. `RaceRepository`에서 `status = 'ONGOING' AND end_date < NOW()` 조회
3. 각 레이스에 대해 `status = 'COMPLETED'`로 업데이트
4. 개별 레이스 처리 실패 시 실패 목록에 추가하고 계속 진행 (FR-5)
5. 전체 처리 완료 후 이력 저장 및 운영팀 알림 발송

---

## 6. 인터페이스 정의

- **NotificationService**: 운영팀 알림 발송 (이메일/슬랙, 채널은 설정으로 관리)
- **RaceRepository**: `findAllByStatusAndEndDateBefore(RaceStatus, LocalDateTime)` 메서드 추가

---

## 7. 아키텍처 적합성 분석

- 기존 레이어 구조 준수 (Job → Service → Repository)
- 배치 처리 실패 시 개별 격리 처리로 전체 실패 방지 (FR-5)
- 운영 권한 체크 필요 (`/admin/**` 시큐리티 경로 등록 확인)

---

## 8. 구현 단계 (Phases)

### 구현 워크플로

1. 브랜치 생성: `api/feat/race-auto-completion`
2. Phase 1 → 2 → 3 순서로 구현
3. 구현 완료 후 테스트 실행: `./gradlew :batch-app:test`
4. 테스트 통과 후 Phase별 커밋

---

### Phase 1: 도메인 & DB 준비

- **목표**: Race 도메인 상태 전환 로직 및 이력 테이블 구성
- **TODO**:
  - [ ] `com.example.race.domain.Race` — `complete()` 메서드 추가
  - [ ] `com.example.race.domain.RaceStatus` — COMPLETED 상태 확인
  - [ ] `com.example.race.infrastructure.RaceAutoCompletionHistory` JPA 엔티티 생성
  - [ ] Flyway: `V202604091300__add_race_auto_completion_history.sql`
- **테스트**:
  - `Race.complete()` 순수 단위 테스트 (JUnit 5)
  - H2 인메모리 DB로 `@DataJpaTest` 실행 (빠른 피드백용)
- **커밋 계획**:
  - `feat: 레이스 자동 완료 도메인 로직 및 이력 테이블 추가`
- **커밋 대상 파일 목록**:
  - `src/main/java/com/example/race/domain/Race.java`
  - `src/main/java/com/example/race/infrastructure/RaceAutoCompletionHistory.java`
  - `src/main/resources/db/migration/V202604091300__add_race_auto_completion_history.sql`

---

### Phase 2: 배치 서비스 구현

- **목표**: 자동 완료 처리 서비스 및 스케줄러 구현
- **TODO**:
  - [ ] `com.example.race.application.RaceAutoCompletionService` 생성
  - [ ] `com.example.race.infrastructure.RaceRepositoryImpl` — `findAllOngoingEndedBefore()` 추가
  - [ ] `com.example.race.infrastructure.RaceAutoCompletionHistoryRepository` 생성
  - [ ] `com.example.batch.RaceAutoCompletionJob` 스케줄러 생성 (`@Scheduled`)
- **테스트**:
  - `RaceAutoCompletionService` Mockito 단위 테스트
  - H2 기반 `@DataJpaTest`로 Repository 쿼리 검증
- **커밋 계획**:
  - `feat: 레이스 자동 완료 서비스 및 스케줄러 구현`
- **커밋 대상 파일 목록**:
  - `src/main/java/com/example/race/application/RaceAutoCompletionService.java`
  - `src/main/java/com/example/race/infrastructure/RaceRepositoryImpl.java`
  - `src/main/java/com/example/batch/RaceAutoCompletionJob.java`

---

### Phase 3: 운영 API 및 알림

- **목표**: 이력 조회 API, 재처리 API, 운영팀 알림 구현
- **TODO**:
  - [ ] `com.example.race.web.RaceAdminController` — 이력 조회, 재처리 엔드포인트
  - [ ] `com.example.notification.NotificationService` — 알림 발송 인터페이스
  - [ ] 시큐리티 경로 등록: `/admin/races/**`
- **테스트**:
  - `@WebMvcTest` + MockMvc로 Controller 테스트
  - H2 기반 통합 테스트로 재처리 흐름 검증
- **커밋 계획**:
  - `feat: 레이스 자동 완료 운영 API 및 알림 구현`
- **커밋 대상 파일 목록**:
  - `src/main/java/com/example/race/web/RaceAdminController.java`
  - `src/main/java/com/example/notification/NotificationService.java`

---

## 9. 테스트 전략

**계층별 테스트 계획**:

| 계층 | 도구 | 설명 |
|------|------|------|
| Domain | JUnit 5 | `Race.complete()` 순수 단위 테스트 |
| Application | Mockito | `RaceAutoCompletionService` Mock 기반 테스트 |
| Infrastructure | `@DataJpaTest` + **H2 인메모리 DB** | Repository 쿼리 빠른 검증 |
| Web | `@WebMvcTest` + MockMvc | Controller 요청/응답 검증 |

> H2 인메모리 DB를 사용하여 빠른 테스트 실행 환경 구성.
> 프로덕션은 MySQL이지만 테스트에서는 H2 호환 모드를 사용한다.

---

*문서 작성일: 2026-04-09*
