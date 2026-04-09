# Mermaid 다이어그램 작성 가이드

TDD 문서에서 사용하는 Mermaid 다이어그램 패턴.

- [시퀀스 다이어그램](#시퀀스-다이어그램)
- [ERD](#erd)
- [플로우차트](#플로우차트)
- [공통 규칙](#공통-규칙)

---

## 시퀀스 다이어그램

API 요청 흐름, 서비스 간 호출에 사용.

```mermaid
sequenceDiagram
    participant C as Client
    participant Ctrl as Controller
    participant Svc as RaceCompletionService
    participant Repo as RaceRepository
    participant DB as Database

    C->>Ctrl: POST /api/v1/races/complete-expired
    Ctrl->>Svc: completeExpiredRaces()
    Note right of Svc: 만료된 진행중 레이스 조회
    Svc->>Repo: findExpiredInProgressRaces(today)
    Repo->>DB: SELECT ... WHERE end_date < today AND status = 'IN_PROGRESS'
    DB-->>Repo: List<RaceEntity>
    Repo-->>Svc: raceEntityList
    Note right of Svc: 각 레이스 상태를 COMPLETED로 변경
    loop 각 레이스
        Svc->>Svc: raceEntity.complete()
    end
    Svc->>Repo: saveAll(raceEntityList)
    Repo->>DB: UPDATE race SET status = 'COMPLETED'
    Svc-->>Ctrl: 완료 건수
    Ctrl-->>C: 200 OK
```

---

## ERD

테이블 관계 표현에 사용.

```mermaid
erDiagram
    RACE {
        bigint id PK
        varchar name
        varchar status "IN_PROGRESS, COMPLETED, CANCELLED"
        date start_date
        date end_date
        datetime created_at
        datetime updated_at
    }

    RACE_PARTICIPANT {
        bigint id PK
        bigint race_id FK
        bigint member_id
        varchar status
        datetime joined_at
    }

    RACE ||--o{ RACE_PARTICIPANT : "참여자 목록"
```

---

## 플로우차트

비즈니스 로직 분기에 사용.

```mermaid
flowchart TD
    A[스케줄러 실행] --> B[만료된 진행중 레이스 조회]
    B --> C{조회 결과?}
    C -->|0건| D[종료 - 처리 대상 없음]
    C -->|1건 이상| E[페이지 단위 처리]
    E --> F[레이스 상태 COMPLETED로 변경]
    F --> G[참여자 알림 발송]
    G --> H{다음 페이지?}
    H -->|있음| E
    H -->|없음| I[완료 로그 기록]
```

---

## 공통 규칙

1. **한글 Note 주석 필수** — `Note right of Svc: 만료된 진행중 레이스 조회` 형태로 핵심 동작 설명
2. **participant alias 사용** — 긴 이름은 alias로 축약 (`participant Svc as RaceCompletionService`)
3. **DB 쿼리 힌트** — 시퀀스에서 DB 호출 시 실제 SQL 힌트 포함 권장
4. **ERD는 PK/FK/주요 컬럼만** — 모든 컬럼을 넣지 않음, 핵심만
5. **플로우차트 분기에 조건 명시** — `{조회 결과?}` 처럼 판단 기준을 적음
