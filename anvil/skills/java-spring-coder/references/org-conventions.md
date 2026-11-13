# 조직 코딩 컨벤션 적용 (java-spring-coder, v1.18)

SKILL.md 의 Phase 0-3 에서 "조직 컨벤션 적용 프로젝트"로 판정했을 때만 읽는다. 규칙 본문은 원문에 있다. 이 문서는 이 스킬의 기존 규칙 중 **어느 것이 조건부로 바뀌는지**만 정리한다.

- 적용 가이드: `forge/common/vc-conventions-guide.md`(배포본 `.claude/shared/vc-conventions-guide.md`) — 2절 적용 판정, 3절 충돌 판정 표, 4-1절 프로덕션 코드 요약
- 원문: `forge/common/vc-conventions/`(배포본 `.claude/shared/vc-conventions/`) 중 naming, pkg-structure, entity, dto, lombok, etc
- 원문 폴더가 비어 있으면 가이드 4-1절 요약으로 적용하고 보고에 "조직 컨벤션 원문 미확인"을 적는다(가이드 2절 3)

## 1. 적용 판정

| 상황 | 판정 |
|------|------|
| `.claude/shared/vc-conventions-guide.md` 있음 | 적용. 이 문서 2~6절을 따른다 |
| 없음 | 비적용. 프로젝트 규칙(`.claude/rules/`)과 SKILL.md 기존 규칙만. 원문을 다른 곳에서 찾아 적용하지 않는다 |
| forge 에서 평가 중 | TC 가 명시한 프로젝트 맥락을 따른다 |

적용 범위는 **신규로 쓰는 코드와 이번 작업에서 바꾸는 줄**이다. 기존 코드가 컨벤션과 다르다는 이유로 고치지 않는다. 고칠 가치가 있으면 보고의 "범위 밖 제안"에 적는다(SC-1).

## 2. 정적 팩토리 (가이드 3절 1행)

| 경우 | 적용 프로젝트 | 비적용 프로젝트 |
|------|---------------|-----------------|
| 신규 DTO·Response·OutDto | 생성자 직접 호출(`new UserOutDto(...)`). 변환은 호출하는 쪽에서 — Controller 가 `Request → InDto`, `OutDto → Response`, Service 가 `Entity → OutDto` | 규칙 05 `from()`/`of()` |
| 신규 JPA Entity | `@NoArgsConstructor(access = PROTECTED)` + 직접 선언한 생성자에 `@Builder`. `RepositoryImpl` 에서 `new {Domain}JpaEntity(...)`/빌더로 변환 | 규칙 03 `from()`·`toEntity()` |
| 신규 Domain Entity | 생성자에서 불변식 검증(`Objects.requireNonNull`). 단순 생성용 `of()` 를 따로 두지 않는다 | 규칙 02 `of()` |
| 이미 `from()` 이 있는 기존 클래스에 필드만 추가 | 기존 `from()` 본문을 고쳐 쓴다. 새 팩토리·생성자 경로를 추가하지 않는다 | 동일 |
| 변환 로직이 복잡(여러 객체 조합·분기 계산) | 정적 팩토리 허용. 이름 `from`/`of` 는 자기 타입을 반환할 때만. 코드 주석이나 PR 본문에 "복잡한 변환" 사유 | 규칙 05 |

사용자가 "다른 DTO 들처럼 `from()` 으로" 라고 요청해도 적용 프로젝트의 신규 클래스면 생성자 직접 호출로 쓰고, 가이드 3절을 인용해 이유를 한 줄로 알린다. 같은 패키지의 기존 `from()` 관례(우선순위 4)는 조직 컨벤션(우선순위 2)보다 아래다.

`toEntity()`·`to{Target}()` 처럼 **다른 타입을 반환하는** 인스턴스 메서드는 이름 규칙(`of`·`from` 금지 대상) 밖이다. 다만 적용 프로젝트에서 새로 만들 때는 변환 위치(RepositoryImpl·Service·Controller)에서 생성자를 직접 호출하는 쪽을 먼저 고른다.

## 3. 이름

| 항목 | 적용 프로젝트 | 비적용 프로젝트 (SKILL.md 기존) |
|------|---------------|-------------------------------|
| 변수명 | 타입명 전체 camelCase(`UserEntity userEntity`, `Glp1SymptomMemoOutDto glp1SymptomMemoOutDto`). `req`·`res`·`dto`·`e`·`cnt`·`msg`·`tmp`·`saved` 금지, catch 변수도 `exception` | 약어 금지·타입 반영(동일 취지) |
| 컬렉션 | 요소 클래스명 복수형(`orderItems`) 또는 `orderItemList`. `list`·`dataList` 금지 | `*List` |
| Map | `{값 복수형}By{키}`(`ordersById`). `resultMap`·`couponEntityMap` 금지 | `couponEntityMap` |
| application DTO | `InDto`/`OutDto`(헥사고날은 `Command`/`Result`). `~Dto` 단독 금지 | 동일 |
| 신규 Controller | 변경 `{Domain}CommandController`, 조회 `{Domain}QueryController`. 기존 Controller 에 엔드포인트를 더할 때는 그 Controller | `{Domain}{Action}Controller` |
| domain 객체 | id 있으면 `{Domain}Entity`, 없으면 접미사 없이 `{Domain}` | `{Domain}Entity` |
| JPA `@Entity` | `{Domain}JpaEntity`, infrastructure | 동일 |
| 조회 메서드 | `get~` 은 없을 때 동작 명시(`OrThrowException`/`OrNull`/`OrDefault`), `find~` 는 Optional | `get*OrElseNull` |

사용자가 축약 변수명을 요청해도 전체 이름으로 쓰고 근거를 한 줄로 알린다. 이것은 적용·비적용 공통이다(비적용 프로젝트는 SKILL.md 변수 네이밍 절이 근거, 적용 프로젝트는 원문 naming 2·11).

## 4. 패키지·계층

- 패키지명 `presentation` 대신 `web`. scheduler 는 infrastructure
- web DTO(`Request`/`Response`)를 application 으로 넘기지 않는다
- domain 객체에 JPA·Spring 어노테이션 금지(`jakarta.annotation.Nullable` 만 허용, `org.springframework.lang.Nullable` 금지)
- application 은 흐름 조합만, 비즈니스 판단(if/else)은 domain

## 5. Lombok

| 대상 | 허용 | 금지 |
|------|------|------|
| 전 계층 | - | `@Setter`(클래스·필드 모두), `@Data`, `@AllArgsConstructor`, `@Value` |
| Domain Entity | `@Getter`, `@ToString`, `@EqualsAndHashCode` | `@RequiredArgsConstructor`, `@NoArgsConstructor` |
| JPA Entity | `@Getter`, `@NoArgsConstructor(access = PROTECTED)`, 직접 선언한 생성자에 `@Builder` | 클래스 레벨 `@Builder`, `@Setter` |
| DTO | record (Lombok 없음) | `@Data`, `@Setter` |

상태 변경은 `change{Field}()` 비즈니스 메서드로만 한다.

## 6. 테스트 DB (가이드 3절 3행)

모듈의 기존 테스트 DB 설정(`src/test/resources/application-test*.yml`)을 먼저 읽고 그대로 쓴다. H2 모듈을 Testcontainers 로, Testcontainers 모듈을 H2 로 바꾸지 않는다. 이 항목은 적용·비적용 프로젝트 모두 같다(SKILL.md 하드 가드레일).

## 7. 보고

- 조직 컨벤션 때문에 사용자 요청이나 프로젝트 규칙과 다르게 구현한 항목은 원문 파일과 가이드 3절 판정을 인용한다
- 가이드 3절 표에 없는 충돌은 조직 컨벤션을 따르고 PR 본문에 "조직 컨벤션 우선 적용"을 적는다
- `review-lint.py` 출력 마지막 줄의 "조직 컨벤션 검사 켜짐/꺼짐"을 보고에 적는다. 적용 프로젝트인데 꺼짐이면 lint 옆에 가이드가 없는 것이다 — `--vc` 로 다시 돌리고 배포 누락을 보고한다
