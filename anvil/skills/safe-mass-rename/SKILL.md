---
name: safe-mass-rename
description: "Enum·상수·설정 키·API 필드명 등 전역 식별자의 대형 리네임을 안전하게 오케스트레이션한다. '대형 리네임', 'enum 리네임', '전역 리네임', 'mass rename', 'rename cycle', '식별자 통일', 'PROTECTED FREEMIUM 리네임', 'Redis 키 리네임', '설정 키 리네임' 요청 시 사용. 단순 sed 치환이 아니라 순서(정의부→참조→문자열→테스트→설정/DB→문서) 강제, 매 단계 개별 커밋, 롤백 브랜치 확보, grep 잔재 0건 검증을 포함한다."
version: "0.1"
last-modified: "2026-07-02"
changelog: "v0.1: 2026-07-02 pasta-japan-server Freemium 리네임 사이클 반영하여 신설 (ServiceAccessPatternType.PROTECTED→FULL / PAID→FREEMIUM, Redis 키·admin/api 병렬 커밋 세분화 사례)"
harness-status: pending
---

# safe-mass-rename — 전역 식별자 대형 리네임 오케스트레이터

> 트리거: "대형 리네임", "enum XXX → YYY 전역 변경", "PROTECTED/FREEMIUM 리네임", "Redis 키 리네임", "설정 키 통일"

원칙: **한 커밋에 여러 단계를 뭉치지 않는다.** enum 정의부·정적 참조·문자열 리터럴·테스트·설정/DB·문서를 각각 독립 커밋으로 진행. 매 단계마다 컴파일·grep 검증. 리팩터·기능 추가와 리네임 절대 혼재 금지.

## 실전 사례 (Motivation)

**2026-07-02 pasta-japan-server**: 강제 업데이트 정책 명명 통일 사이클.

- Enum: `ServiceAccessPatternType.PROTECTED` → `FULL`
- Enum: `ServiceAccessPatternType.PAID` → `FREEMIUM`
- Redis 키: `service-access:patterns:PROTECTED` → `service-access:patterns:FULL`
- admin·api 병렬 커밋 여러 개로 세분화 → 성공 사례. 각 커밋이 원자적이라 리버트·리뷰가 용이했음.

**교훈**: 대형 리네임을 "한 방에" 하려던 초기 시도가 있었으나, 컴파일 실패·테스트 실패·리뷰 부담이 겹치며 rollback도 어려워짐. **단계 분리 + 단계별 커밋**이 정답.

## 범위 / 비범위

- **범위**: 코드 안에 정의된 **전역 식별자**의 이름 변경. enum 상수, `public static final` 상수, DTO 필드명, Redis/DB 키 접두사, 설정 프로퍼티 키, 로그 태그.
- **비범위**: 
  - 클래스명/패키지명 이동 (IDE refactor + `@Deprecated` 별칭이 더 적합)
  - 외부에 노출된 REST API 필드명 (breaking change → 별도 API 버전 관리 스킬)
  - 로컬 변수·private 필드 (IDE rename으로 충분)

## Phase 0. 사전 점검

리네임 시작 전 다음을 확인:

```bash
# 1) 현재 브랜치가 작업 브랜치인가? dev/main 위에서 절대 금지
git status -sb

# 2) uncommitted 변경 없나
git status --porcelain

# 3) 대상 식별자 정의부 위치 확인 (enum/상수)
grep -rn "OLD_NAME" src --include="*.java" | head
```

**하드 가드레일 (Phase 0)**:
- `dev`/`main` 브랜치에서 리네임 시작 금지 → `api/refac/{task}` 브랜치 필수
- uncommitted 파일 존재 시 리네임 시작 금지 (stash 또는 별도 커밋 선행)
- 대상 식별자가 3개 이상이면 각각 별도 사이클 (한 사이클 = 한 식별자쌍)

## Phase 1. 영향 범위 스캔

리네임 실행 전에 모든 참조 위치를 매핑.

```bash
# 정의부·참조·문자열 리터럴 3분류로 스캔
echo "== 정의부 =="
grep -rn "OLD_NAME" --include="*.java" src | grep -E "(enum|class|interface|final.*=)"

echo "== 참조 =="
grep -rn "\.OLD_NAME\|OLD_NAME\." --include="*.java" src

echo "== 문자열 리터럴 =="
grep -rn "\"OLD_NAME\"\|'OLD_NAME'" --include="*.java" --include="*.yml" --include="*.properties" src

echo "== 테스트 =="
grep -rn "OLD_NAME" --include="*Test.java" src
```

결과를 표로 사용자에게 제시:

| 카테고리 | 파일 수 | 예시 |
|---|---|---|
| 정의부 | 1 | `ServiceAccessPatternType.java` |
| 참조 | 12 | `ServiceAccessAuthorizationFilter.java`, `ServiceAccessPatternWarmupRunner.java` … |
| 문자열 리터럴 | 3 | Redis 키, 로그 태그 |
| 테스트 | 5 | `*Test.java` |
| 설정/DB | 1 | `application.yml` |
| 문서 | 2 | `README.md`, ADR |

사용자가 스코프 확인 후 Phase 2 진입.

## Phase 2. 리네임 실행 — 6단계 순서 강제

각 단계는 **독립 커밋**. 단계 완료 없이 다음 단계 진입 금지.

### 2-1. 정의부 리네임

원본 정의 파일만 변경.

```bash
# 예: enum 정의부
# ServiceAccessPatternType.java: PROTECTED → FULL
```

**필수 검증**:
- `./gradlew compileJava` → 참조 파일들에서 컴파일 에러 발생 (예상됨, 이 시점에는 OK)
- 정의부 커밋 메시지 예: `refac: ServiceAccessPatternType.PROTECTED 정의부를 FULL로 리네임`

### 2-2. 컴파일 참조 리네임

정적 참조들(`.OLD_NAME` / `OLD_NAME.` 형식) 전부 갱신.

**필수 검증**:
- `./gradlew compileJava` → 통과해야 함
- `grep -rn "\.OLD_NAME\|OLD_NAME\." --include="*.java"` → 0건 확인
- 커밋 메시지 예: `refac: FULL 리네임 참조 갱신 (api·admin 정적 참조 12곳)`

### 2-3. 문자열 리터럴 리네임

Redis 키, 로그 태그, 설정 값 문자열 등.

**주의**:
- **문자열 리터럴은 컴파일러가 안 잡음** → grep이 유일한 안전망
- Redis 키·DB 값 리네임은 **후방향 호환 기간** 필요 (Phase 3 참고)

**필수 검증**:
- `grep -rn "\"OLD_NAME\"\|'OLD_NAME'"` → 0건 (의도된 잔재 제외)
- 커밋 메시지 예: `refac: Redis 키·로그 태그 문자열 FULL로 통일`

### 2-4. 테스트 리네임

테스트 코드의 참조·문자열·주석 갱신.

**필수 검증**:
- `./gradlew test` → 통과
- 커밋 메시지 예: `refac: FULL 리네임에 맞춰 테스트 데이터·assertion 갱신`

### 2-5. 설정/DB 리네임 — **하드 가드레일: 롤백 브랜치 필수**

`application.yml`, flyway 마이그레이션, Redis warmup 초기값 등.

**하드 가드레일**:
1. Phase 2-5 시작 **직전**에 롤백 브랜치 생성 필수: `git branch rollback/before-mass-rename-config`
2. Redis/DB 리네임은 **양쪽 조회 → 배포 → 구값 제거** 3단계로 분할 (Phase 3 참고)
3. flyway 마이그레이션은 새 버전 파일로 (기존 파일 수정 금지)

**필수 검증**:
- 로컬 통합 테스트 통과
- 커밋 메시지 예: `refac: application.yml 이용권한 패턴 키 FULL로 통일`

### 2-6. 문서 리네임

README, ADR, 주석, changelog.

**필수 검증**:
- 커밋 메시지 예: `docs: FULL 리네임에 맞춰 ADR·README·주석 갱신`

## Phase 3. 후방향 호환 검토

Redis 키·DB 값·외부 API 계약이 걸린 리네임은 즉시 교체 금지. **읽기 양쪽 지원 → 배포 → 쓰기 단일화 → 구값 제거** 순.

### Redis 키 리네임 사이클

1. **읽기 양쪽 지원 커밋**: 신규 키(`FULL`) 읽고 없으면 구 키(`PROTECTED`) 읽기 fallback
2. **쓰기 신규만** 커밋: write-through·warmup은 신규 키에만
3. **배포 + 데이터 backfill**: 운영에서 구 키가 사라질 때까지 대기 (최소 1개 배포 주기)
4. **fallback 제거 커밋**: 구 키 읽기 코드 삭제

### DB 컬럼 리네임 사이클

flyway로 신규 컬럼 추가 → 이중 쓰기 → 데이터 이관 → 구 컬럼 drop. 각 마이그레이션 개별 배포.

### 외부 API 필드명

**본 스킬 범위 아님**. `@JsonAlias`로 임시 완화 후 API 버전 관리 스킬(별도 컴포넌트 대상)로 이관.

## Phase 4. 최종 커밋 세트 정리

리네임 사이클 종료 시점.

```bash
# 1) 전체 grep 잔재 0건 확인 (의도된 fallback 제외)
grep -rn "OLD_NAME" --include="*.java" --include="*.yml" --include="*.properties" \
  | grep -v "// backfill\|// deprecated"

# 2) 커밋 로그 확인 — 단계별 커밋이 되어 있는가
git log --oneline api/refac/xxx...dev

# 3) 컴파일·테스트 최종 확인
./gradlew build
```

**커밋 세트 예시** (Freemium 사례):

```
refac: ServiceAccessPatternType.PROTECTED 정의부를 FULL로 리네임
refac: FULL 리네임 참조 갱신 (api·admin 정적 참조 12곳)
refac: Redis 키 접두사 service-access:patterns:FULL 신규 지원 (구 키 fallback 유지)
refac: FULL 리네임에 맞춰 테스트 데이터·assertion 갱신
refac: application.yml 이용권한 패턴 키 FULL로 통일
docs: FULL 리네임에 맞춰 ADR·주석 갱신
```

## 하드 가드레일 (요약)

1. **각 단계 단위 커밋 필수** — 한 커밋에 여러 단계 뭉치기 금지
2. **매 단계 후 `./gradlew compileJava` 통과 확인** (2-1은 예외: 참조가 남아 있어 실패 가능)
3. **Phase 2-5 시작 전 롤백 브랜치 명시 필수**
4. **리팩터·기능 추가와 리네임 절대 같은 커밋 금지**
5. **`dev`/`main` 브랜치에서 리네임 시작 금지** — `api/refac/{task}` 브랜치 필수
6. **Redis/DB/외부 API 리네임은 즉시 교체 금지** — Phase 3 후방향 호환 사이클 준수
7. **한 사이클 = 한 식별자쌍** — 3개 이상 리네임 대상은 별도 사이클로 분리

## 소프트 권장

- 각 단계 후 `grep -rn "OLD_NAME"` 결과 0건 검증(의도된 fallback 제외) 후 다음 단계
- Redis 키·DB 컬럼 리네임은 최소 1개 배포 주기 후방향 호환 유지
- 커밋 메시지에 `refac:` 접두어 (Korean Conventional Commits, `refactor:` 아님)
- 대형 리네임은 PR도 단계별로 나누는 것이 리뷰 부담 최소화 (또는 단일 PR + 명확한 커밋 세트)

## 자기 검증 체크리스트

리네임 사이클 완료 시점에 스킬이 스스로 검증:

1. 대형 리네임이 **enum → 참조 → 문자열 → 테스트 → 설정 → 문서** 순서를 준수했는가?
2. 각 단계가 **독립 커밋**으로 분리되어 있는가?
3. Phase 2-5(설정/DB) 시작 전 **롤백 브랜치**가 생성되어 있는가?
4. Redis/DB 리네임 시 **후방향 호환 기간**을 확보했는가 (읽기 양쪽 지원)?
5. `grep -rn "OLD_NAME"` 결과가 **0건** (의도된 fallback 제외)인가?
6. **리팩터·기능 추가**가 리네임 커밋에 섞이지 않았는가?
7. 커밋 메시지가 **`refac:` 접두어** (Korean Conventional Commits)를 따르는가?
8. **컴파일·테스트**가 매 단계 통과했는가 (2-1 제외)?
9. **외부 API 계약**이 걸린 리네임이면 buyer(모바일/외부 팀) 통보가 완료되었는가?
10. **문서**(README·ADR·주석)까지 갱신되었는가?

## 트러블슈팅

| 증상 | 원인/조치 |
|---|---|
| 2-2 이후 컴파일 실패 | 놓친 참조 존재. `grep -rn "OLD_NAME\." --include="*.java"` 재검색 후 갱신 |
| Redis 조회 시 값 없음 | Phase 3 fallback 미구현. 신규 키에 데이터 없을 때 구 키 조회로 폴백 로직 필요 |
| 테스트만 실패 | 2-4 단계 누락. 테스트 픽스처·assertion·mock 값 재점검 |
| 배포 후 로그에 구값 잔재 | 2-3 문자열 리터럴 누락. 로그 태그·에러 메시지 grep 재검색 |
| PR 리뷰 부담 | 단계별 커밋이 명확해도 총 파일 수가 많으면 PR 자체를 단계별로 나누기 검토 |

## 하네스

- **평가 루브릭**: `references/evaluation-rubric.md` (v0.1 미작성 — 다음 사이클 대상)
- **하네스 정의**: `proving-grounds/harnesses/safe-mass-rename.harness.md` (미작성)
- **테스트 케이스**: happy(단일 enum 6단계 완주) / edge(Redis 키 후방향 호환) / negative(정의부·참조 한 커밋 뭉침 → AUTO FAIL)
- **상태**: **테스트 대기** — 실전 배치 전 반드시 하네스 작성 + `/eval-harness safe-mass-rename` 통과 필요

## 참고

- Korean Conventional Commits (`refac:` 접두어): `forge/common/pasta-rules/11-git-workflow-convention.md`
- 4-Tier 아키텍처 재편은 별도 스킬 (`java-spring-coder` v1.10 신규 패키지 4-Tier 강제 섹션 참조)
- 외부 API 필드명 리네임은 본 스킬 범위 밖 — 별도 API 버전 관리 컴포넌트 대상
