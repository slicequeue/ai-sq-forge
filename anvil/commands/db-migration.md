---
name: db-migration
description: "Flyway DB 마이그레이션 SQL 작성. CREATE TABLE, ALTER TABLE, INSERT/UPSERT 등 DB 스키마·데이터 마이그레이션 요청 시 사용. Use proactively when creating migration files, adding tables/columns, or inserting seed data."
trigger: "/db-migration"
args: "[작업 설명] — 생성할 마이그레이션 내용 (한국어/영어)"
version: "1.0"
last-modified: "2026-04-14"
changelog: "실전 프로젝트(pasta-japan-server)에서 forge로 역수입"
---

# /db-migration — Flyway DB 마이그레이션 SQL 작성

DB 마이그레이션 SQL 파일을 프로젝트 컨벤션에 맞게 작성한다.

---

## Phase 0. 사전 확인

SQL 작성 전 반드시 확인. 확인 없이 생성하지 않는다.

1. **대상 모듈 확인**: `pasta-api`, `admin`, `api`, `commerce` 등 어떤 모듈의 마이그레이션인지 확인
2. **기존 마이그레이션 탐색**: 같은 도메인의 기존 SQL 파일을 읽어 테이블 구조·컨벤션 파악
3. **관련 JPA Entity 확인**: 해당 테이블의 JpaEntity가 있으면 읽어서 컬럼 매핑 확인
4. **guardrails 확인**: `.claude/rules/09-guardrails.md` §3 (DB 마이그레이션 파일 보호) 준수

---

## 파일 네이밍

```
V<YYYYMMDDHHmm>__description.sql
```

- **타임스탬프**: 현재 시각 기준 `YYYYMMDDHHmm` (분 단위)
- **설명**: 영문 snake_case, 동작을 명확히 표현
- **예시**:
  - `V202604141400__create_home_card_cta_config.sql`
  - `V202604141400__upsert_home_card_cta_config_data.sql`
  - `V202604141400__alter_users_add_nickname_column.sql`

---

## 파일 배치 경로

```
{module}/src/main/resources/db/migration/{domain}/{sub-domain}/
```

같은 도메인의 기존 마이그레이션 파일 위치를 따른다. 새 도메인이면 도메인명으로 디렉토리 생성.

---

## CREATE TABLE 컨벤션

### 필수 규칙

```sql
CREATE TABLE {table_name}
(
    id         BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    -- 비즈니스 컬럼들 ...
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성 시각',
    updated_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 시각'
);
```

### 체크리스트

| 항목 | 규칙 |
|------|------|
| **PK** | `BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY` |
| **created_at** | `TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성 시각'` |
| **updated_at** | `TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 시각'` |
| **deleted_at** | soft delete 필요 시 `TIMESTAMP NULL DEFAULT NULL COMMENT '삭제 시각'` |
| **COMMENT** | 모든 컬럼에 COMMENT 필수 |
| **ENGINE/CHARSET/COLLATE** | 생략 — 서버 디폴트 사용 |
| **VARCHAR(URL)** | URL 저장 컬럼은 `VARCHAR(1024)` 이상 |
| **NOT NULL** | 비즈니스상 필수 필드는 반드시 `NOT NULL` |

### 금지 사항

- ❌ `DATETIME(6)` 사용 → `TIMESTAMP` 사용
- ❌ `created_at`, `updated_at`에 DEFAULT 없이 NOT NULL만 선언
- ❌ `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci` 명시 (서버 디폴트 사용)
- ❌ 도메인 경계 바깥 테이블(예: `users`)에 FK 제약 생성

---

## 인덱스 네이밍

| 종류 | 패턴 | 예시 |
|------|------|------|
| 일반 인덱스 | `idx_{column1}_{column2}` | `idx_user_id_local_date` |
| 유니크 인덱스 | `uk_{column1}_{column2}` | `uk_card_type_data_status` |
| 외래키 | `fk_{소스축약}_{참조컬럼}_{대상축약}_{pk}` | `fk_schedule_plan_id_plan_id` |

- 컬럼명은 DB 컬럼명 **그대로** 사용 (약어·축약 지양)
- MySQL 64자 제한 초과 시에만 길이 축소 (의미 유지)

---

## ALTER TABLE 컨벤션

```sql
-- 컬럼 추가
ALTER TABLE {table_name}
    ADD COLUMN {column_name} {type} {constraints} COMMENT '{설명}';

-- 컬럼 타입 변경
ALTER TABLE {table_name}
    MODIFY COLUMN {column_name} {new_type} {constraints} COMMENT '{설명}';

-- 인덱스 추가
ALTER TABLE {table_name}
    ADD INDEX idx_{column1}_{column2} ({column1}, {column2});
```

---

## INSERT / UPSERT 컨벤션

### 단순 INSERT (초기 데이터)

```sql
INSERT INTO {table_name} ({columns})
VALUES ({values});
```

- `created_at`, `updated_at`은 DEFAULT가 있으면 **생략** (불필요한 `NOW(6)` 호출 제거)

### UPSERT (중복 시 갱신)

유니크 키가 있는 테이블에 데이터를 넣을 때:

```sql
INSERT INTO {table_name} ({columns_without_timestamps})
VALUES ({values})
ON DUPLICATE KEY UPDATE {column1} = VALUES({column1}),
                        {column2} = VALUES({column2});
```

- `ON UPDATE CURRENT_TIMESTAMP`가 설정된 `updated_at`은 **자동 갱신되므로 생략**
- `created_at`도 INSERT 시 DEFAULT로 자동 설정되므로 **생략**
- 유니크 키 또는 PK 기준으로 동작 — **테이블의 유니크 키/PK를 반드시 사전 확인**

### UPSERT 사전 확인 체크리스트

1. [ ] 테이블에 UNIQUE KEY가 있는가? → `SHOW CREATE TABLE`로 확인
2. [ ] created_at에 `DEFAULT CURRENT_TIMESTAMP`가 있는가?
3. [ ] updated_at에 `ON UPDATE CURRENT_TIMESTAMP`가 있는가?
4. [ ] 위 2~3이 없으면 **ALTER로 먼저 정규화** 후 UPSERT

---

## 자기 검증 체크리스트

SQL 작성 완료 후 반드시 확인:

1. [ ] **파일명**: `V<YYYYMMDDHHmm>__description.sql` 형식인가?
2. [ ] **경로**: 같은 도메인의 기존 마이그레이션과 같은 디렉토리인가?
3. [ ] **created_at/updated_at**: `TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP` 패턴인가?
4. [ ] **updated_at**: `ON UPDATE CURRENT_TIMESTAMP` 포함인가?
5. [ ] **COMMENT**: 모든 컬럼에 COMMENT가 있는가?
6. [ ] **ENGINE/CHARSET**: 생략했는가? (서버 디폴트 사용)
7. [ ] **인덱스 네이밍**: `idx_`, `uk_`, `fk_` 접두사 + 컬럼명 그대로?
8. [ ] **UPSERT**: 유니크 키/PK 존재 확인, timestamp 컬럼 DEFAULT 확인?
9. [ ] **URL 컬럼**: `VARCHAR(1024)` 이상인가?
10. [ ] **FK 제약**: 도메인 경계 바깥 테이블 참조 FK 없는가?
11. [ ] **기존 마이그레이션 보호**: obesity 기존 파일 수정/삭제하지 않았는가?
12. [ ] **JPA Entity**: NOT NULL 컬럼에 `@NotNull` 어노테이션이 매핑되어 있는가?

---

## 가드레일

### 하드 가드레일

- **기존 obesity 마이그레이션 파일 수정/삭제 절대 금지** (guardrails §3)
- **스키마 접두사(`pasta.`) 절대 금지** — 테이블명만 사용
- **`DATETIME(6)` 사용 금지** — `TIMESTAMP` 사용
- **ENGINE/CHARSET/COLLATE 명시 금지** — 서버 디폴트

### 소프트 가드레일

- 가능하면 같은 도메인의 최신 마이그레이션을 참고하여 스타일 통일
- 한 파일에 DDL(ALTER)과 DML(INSERT)을 함께 넣어도 됨 (관련된 변경이면)
- 사용자 명시적 요청 없이 커밋하지 않음

---

## 출력 형식

```
✓ 마이그레이션 파일 생성: {파일 경로}
  - 내용: {간략 설명}
  - 체크리스트: 12/12 통과
```
