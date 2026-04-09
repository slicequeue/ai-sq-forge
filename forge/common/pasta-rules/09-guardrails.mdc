---
description: 프로젝트 가드라인 - 지키면 안 되는 것 / 반드시 유지할 것 정리
globs:
alwaysApply: true
---
# 가드라인 (Guardrails)

아래 항목들은 **코드/설정 변경 시 지켜야 하는 경계**이다.
"당장 통과시키기"보다 **원칙을 유지하는 것**을 우선한다.

---

## 1. 테스트 DB · Testcontainers

### 원칙

- **Testcontainers(MySQL) 사용을 원칙으로 유지한다.**
- 테스트가 실패한다고 **테스트 DB를 H2로 바꾸거나, MySQL 전용 쿼리를 바꾸지 않는다.**

### ✅ 해야 하는 것

- `@ActiveProfiles("test")` 등에서 쓰는 **application-test.yml**은 **Testcontainers MySQL** 설정 유지.
- 로컬/CI 테스트 실행 시 **Docker 필요** 전제 유지.
- 테스트 실패 원인이 Docker 미실행이면, **환경(Docker 실행)** 을 맞추는 방향으로 해결.

### ❌ 하지 말아야 하는 것

- 테스트 통과만을 위해 application-test.yml을 H2로 바꾸지 않는다.
- **MySQL 전용 SQL**(예: `ON DUPLICATE KEY UPDATE`, MySQL 전용 함수)을 H2 호환으로 수정하지 않는다.
- Testcontainers 대신 H2로 전환해 "Docker 없이 빌드"되게 만드는 변경을 하지 않는다.
- 그런 이유로 테스트를 **@Disabled** 하거나, **쿼리/레포지토리 코드**를 바꾸지 않는다.

### 이유

- 운영 DB가 MySQL이므로, 테스트도 MySQL(Testcontainers)로 돌리는 것이 동작 보장에 유리하다.
- H2와 MySQL 문법·동작 차이로, H2에서만 통과하는 테스트는 MySQL에서 문제를 놓칠 수 있다.
- "Docker 없이 빌드"를 위해 테스트/쿼리를 바꾸면, 로컬 H2 vs CI/실제 MySQL로 환경이 갈라져 유지보수만 복잡해진다.

### 요약

| 하지 않음 | 대신 |
|----|---|
| test 프로필을 H2로 변경 | Testcontainers MySQL 설정 유지 |
| MySQL 전용 쿼리를 H2용으로 수정 | 쿼리 유지, Docker로 테스트 실행 |
| Testcontainers 테스트 @Disabled | Docker 실행 후 테스트 실행 |

---

## 2. Git 커밋 (Git Commit)

### 원칙

- **사용자의 명시적 요청 없이 독단적으로 커밋하지 않는다.**

### ✅ 해야 하는 것

- 작업 완료 후 변경 사항을 사용자에게 보고하고, 다음 단계를 묻는다.
- 사용자가 "커밋해줘" 또는 "커밋 진행해" 등 명시적으로 요청한 경우에만 커밋을 실행한다.
- 커밋 시에는 반드시 **`git-commit-workflow` 스킬**을 따른다. (Claude Code에서는 `/git-commit-workflow` 스킬 호출을 통해 실행. 스킬 없이 임의로 `git commit`만 실행하지 않는다.)
- 스킬의 컨벤션(No Brackets, Korean Conventional Commits 등)을 따른다.

### ❌ 하지 말아야 하는 것

- "작업이 완료되었으므로 커밋을 생성합니다"라며 사용자 동의 없이 커밋을 수행하는 행위.
- 작업의 중간 단계에서 사용자의 확인 없이 임의로 커밋을 쌓는 행위.
- **`git-commit-workflow` 스킬을 거치지 않고** 임의 형식(대괄호 제목 등)으로 직접 `git commit`을 실행하는 행위.

### 이유

- AI가 임의로 생성한 커밋 단위나 메시지가 사용자의 작업 흐름이나 Git 히스토리 관리 전략과 충돌할 수 있다.
- 사용자가 직접 코드를 검토한 후 최종적으로 기록(Commit)할 시점을 결정할 권리를 존중해야 한다.

### 요약

| 하지 않음 | 대신 |
|----|---|
| 자발적/자동 커밋 수행 | 변경 사항 보고 후 사용자 요청 시에만 커밋 |
| 임의의 커밋 단위 결정 | 사용자의 확인을 거친 후 커밋 |

---

## 3. DB 마이그레이션 파일 보호 (Database Migration)

### 원칙

- **기존 `obesity` 도메인의 마이그레이션 파일은 절대 수정하거나 삭제하지 않는다.** (현재 작업 중인 `myplan` 서브디렉토리 관련 파일 제외)

### ✅ 해야 하는 것

- `obesity/src/main/resources/db/migration/myplan/` 내의 파일만 수정한다.
- 새로운 테이블 생성이나 변경이 필요한 경우, 명시적으로 지정된 최신 마이그레이션 파일만 편집한다.

### ❌ 하지 말아야 하는 것

- "사용되지 않는 것 같다"는 판단 하에 `obesity/src/main/resources/db/migration/obesity/` 하위의 기존 파일을 삭제하거나 수정하는 행위.
- 과거 이력이 담긴 V 파일들을 독단적으로 정리하거나 삭제하는 행위.

### 이유

- 마이그레이션 파일은 DB의 히스토리를 담고 있으며, 독단적인 삭제는 팀 전체의 로컬/운영 DB 스키마 동기화에 치명적인 영향을 줄 수 있다.
- 일본향 이식 작업 중에도 기존 `obesity` 도메인의 원본 마이그레이션 파일들은 보존되어야 한다.

---

## 4. `git stash` / `git stash drop` 사용 금지

### 원칙

- **`git stash`, `git stash drop`, `git stash pop`을 절대 사용하지 않는다.**
- 워킹 디렉토리에는 `.git/info/exclude`로 git 추적에서 제외된 **로컬 전용 파일**(PRD, TDD 문서 등)이 존재한다. `git stash`는 staged 상태의 파일을 포함하여 밀어넣고, `git stash drop`은 복구 불가능하게 날려버린다.

### ✅ 해야 하는 것

- 브랜치 전환이 필요하면, **먼저 워킹 디렉토리가 깨끗한지 `git status`로 확인**한다.
- 변경사항이 있으면 **커밋하거나 사용자에게 어떻게 할지 물어본다.**
- 잘못된 브랜치에서 작업했다면, **파일을 직접 백업하거나 사용자에게 상황을 설명하고 지시를 받는다.**

### ❌ 하지 말아야 하는 것

- `git stash`로 변경사항을 임시 저장하는 행위.
- `git stash drop`으로 stash 항목을 삭제하는 행위.
- `git stash pop`으로 stash를 꺼내는 행위.
- **어떤 상황에서도 예외 없이 금지한다.**

### 이유

- 실제로 `git stash` → `git stash drop` 순서로 실행하여 사용자의 PRD/TDD 문서가 전부 소실된 사고가 발생했다.
- `.git/info/exclude`로 제외된 파일도 staged 상태이면 stash에 포함되며, drop 시 dangling commit으로만 남아 복구가 매우 어렵다.
- stash는 "안전한 임시 저장"이 아니다 — drop 한 순간 데이터 유실이다.

### 요약

| 하지 않음 | 대신 |
|----|---|
| `git stash` 사용 | `git status` 확인 후 커밋 또는 사용자에게 문의 |
| `git stash drop` 사용 | 절대 사용 금지 |
| `git stash pop` 사용 | 절대 사용 금지 |

---

## 5. 로컬 전용 파일 보호 (`.git/info/exclude` 파일)

### 원칙

- **`.git/info/exclude`에 등록된 디렉토리/파일은 로컬 전용 자산이다. 절대 삭제·이동·덮어쓰기하지 않는다.**

### 현재 보호 대상

- `docs/plans/` — TDD 계획 문서
- `docs/prd/` — PRD 문서
- `.cursor/` 관련 로컬 설정
- `.claude/` 관련 로컬 설정

### ✅ 해야 하는 것

- git 조작 전 `.git/info/exclude` 내용을 인지하고, 해당 파일들이 영향받지 않는지 확인한다.
- 새로운 로컬 전용 디렉토리가 생기면 `.git/info/exclude`에 추가한다.

### ❌ 하지 말아야 하는 것

- exclude된 파일/디렉토리를 `git add`, `git stash`, `git clean` 등으로 git 조작에 포함시키는 행위.
- exclude된 파일을 삭제하거나 이동하는 행위.

### 이유

- 이 파일들은 git에 커밋되지 않지만 사용자의 중요한 작업 자산이다. 한번 소실되면 복구가 극히 어렵다.

---

## 6. (추가 가드라인)
