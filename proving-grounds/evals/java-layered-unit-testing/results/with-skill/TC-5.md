# UserDeviceTest — 기기 등록 실패 케이스 테스트 추가

## Phase 0. 사전 확인 (코드 작성 전)

**1) 대상 클래스 계층 식별**
- `grep -rn "class UserDeviceTest" --include=*.java` 로 파일 위치를 먼저 찾는다 → `.../domain/user/UserDeviceTest.java`. 패키지 경로에 `domain` 이 있고 `@SpringBootTest`/`@ExtendWith(SpringExtension.class)` 등 Spring 의존이 없음을 파일 상단 import로 확인 → **Domain 계층**으로 식별(추정 아님, import 목록으로 확정).
- 테스트 대상 소스는 `.../domain/user/UserDevice.java` 로 추정. 실제 `register(...)` 계열 팩토리 메서드의 정확한 시그니처·예외 메시지는 이번에 직접 Read 하지 않았으므로 **가정**으로 표기하고, 실제 적용 전 재확인이 필요하다.

**2) 기존 테스트 패턴 탐색 (Read 먼저)**
- `UserDeviceTest.java` 를 Read 도구로 전체 열람한다. 기존 테스트 3건은 모두 `isAosSocialVersion` 메서드를 검증하고 있고, `@Nested` 없이 flat 구조, 메서드명은 `whenX_thenY` 스타일, `@DisplayName` 한국어, AssertJ `assertThat()` 을 쓰는 것으로 확인.
- `grep -rn "isAosSocialVersion" --include=*.java` 로 전수 검색 → `AppPushDispatchDtoFactory` 가 이 메서드를 여전히 호출 중임을 확인. 즉 기존 3건은 **실서비스 코드가 의존하는 유일한 회귀 안전망**이다. 오늘 작업 범위(기기 등록 실패 케이스 추가)와 무관하지만, 이 사실 때문에 해당 3건은 절대 삭제·축소 대상이 아니며 파일을 통째로 다루는 방식은 금지된다.

**3) JDK / 모듈**: JDK 21, `pasta-api` 모듈(빌드 스크립트 경로로 확인 예정).

### 확인된 사실 vs 가정
| 구분 | 내용 |
|---|---|
| 확인된 사실 | UserDeviceTest.java 존재 / 기존 테스트 3건이 isAosSocialVersion 대상 / Domain 계층(패키지 경로+Spring 미의존) / AppPushDispatchDtoFactory 가 isAosSocialVersion 을 실사용 |
| 가정 | UserDevice.register(...) 의 정확한 파라미터·예외 타입·메시지 문구, "기기 등록 실패"의 구체적 트리거(OS 타입 미지원/토큰 공백 등) |
| 재평가 트리거 | 실제 UserDevice.java Read 결과가 가정과 다르면 아래 테스트 코드의 파라미터·assert 메시지를 그에 맞게 수정 |

## 파괴적 쓰기 가드 적용 (forge/common/destructive-write-guard.md)

- **DW-1**: 편집 전 `git status --short <UserDeviceTest.java 경로>` 로 미커밋 변경 여부를 먼저 확인한다. 변경분이 있으면 작업을 멈추고 사용자에게 보고 후 승인을 받는다.
- **DW-3**: 기존 파일이 존재하고 기존 3건 테스트를 담고 있음이 확인됐으므로, `Write`/`cat >` 로 파일을 통째로 덮지 않는다. 반드시 **Edit 도구**로 마지막 기존 테스트 메서드 뒤에 신규 메서드만 삽입한다.
- **DW-5**: 작업 후 `git diff --stat <경로>` 로 삭제 라인이 0인지, 추가된 라인만 있는지 확인한다. 기존 3건이 그대로 남아 있는지 `git diff` 전문으로 재확인한다.
- **DW-7**: "테스트를 추가했다"고 보고하기 전에 `git diff` 를 실제로 열어 신규 메서드 두 개가 파일에 반영됐는지, 기존 메서드가 그대로인지 눈으로 확인한 뒤 보고한다.

## 리뷰 재발 방지 가드 적용 (forge/common/review-recurrence-guard.md, RR-12)

- 동어반복 금지: 검증 기준(예외 메시지)을 소스 코드의 상수와 동일한 값으로 복붙하지 않고, 실제 런타임 예외 발생 여부와 타입으로 검증한다.
- 목표 경로 실행 확인: `register(...)` 앞단에 별도 `exists`/`isBlank` 사전 통과 로직이 있어 예외 분기 자체가 실행되지 않는 구조인지 Read 시점에 확인해야 한다(가정 단계에서는 미확정 리스크로 남김).
- 경계값: 만약 실패 조건이 "지원 OS 목록에 없음"이라면 목록 밖 값을 명확히 쓰고, 경계 바로 옆(예: 대소문자만 다른 값)으로 애매하게 만들지 않는다.
- 검증 방법: 나중에 `register` 검증 로직을 일부러 주석 처리해 테스트가 실제로 실패하는지 확인하는 것을 남은 작업으로 권고한다(이번 세션에서는 수행하지 않음, 아래 "남은 리스크"에 기록).

## 실패 케이스 설계

"기기 등록 실패"는 `UserDevice.register(...)` 입력 검증 실패 경로로 해석한다(가정). 대표 실패 유형 2가지로 좁힌다.
1. 지원하지 않는 OS 타입으로 등록 시도
2. 디바이스 토큰이 빈 값(blank)인 상태로 등록 시도

## 추가할 테스트 코드 (Edit 계획 — 기존 3건 뒤에 이어붙임)

```java
// Edit 도구 사용 예시
// old_string = 기존 파일의 마지막 테스트 메서드 전체(닫는 중괄호까지)
// new_string = 그 내용을 그대로 유지 + 아래 두 메서드를 이어붙인 버전
// → 기존 3건은 한 글자도 건드리지 않는다.

@Test
@DisplayName("지원하지 않는 OS 타입으로 기기를 등록하면 예외가 발생한다")
void register_throwsException_whenOsTypeUnsupported() {
    // Given
    Long userId = 1L;
    String unsupportedOsType = "WINDOWS_PHONE"; // 가정: 지원 OS는 AOS/IOS만 — 실제 상수 확인 필요
    String deviceToken = "valid-device-token";

    // When & Then
    assertThatThrownBy(() -> UserDevice.register(userId, unsupportedOsType, deviceToken))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("지원하지 않는");
}

@Test
@DisplayName("디바이스 토큰이 비어 있으면 기기 등록에 실패한다")
void register_throwsException_whenDeviceTokenBlank() {
    // Given
    Long userId = 1L;
    String osType = "AOS";
    String blankDeviceToken = "";

    // When & Then
    assertThatThrownBy(() -> UserDevice.register(userId, osType, blankDeviceToken))
        .isInstanceOf(IllegalArgumentException.class);
}
```

- FQCN 인라인 없음(표준 `java.lang.IllegalArgumentException` 은 import 불필요, 단순 클래스명 사용).
- `var` 미사용, 명시 타입 유지.
- 기존 파일 스타일(@Nested 미사용, flat 구조, `whenX_thenY` 네이밍)에 맞춤 — 새로 `@Nested` 그룹을 임의로 도입하지 않음.
- Fixture 값(`unsupportedOsType`, `blankDeviceToken`)은 비즈니스적으로 실패를 유발하는 값이며, 실제 도메인 상수와 다를 수 있는 부분은 주석으로 가정 표기함.

## 실행 계획 (순서)

1. `git status --short <UserDeviceTest.java 경로>` — 미커밋 변경 확인 (DW-1)
2. Read 로 파일 전체 재확인 — 정확한 삽입 지점(마지막 기존 메서드의 닫는 지점) 특정
3. Read 로 `UserDevice.java` 를 열어 `register` 의 실제 시그니처·검증 로직·예외 타입 확인 → 위 가정과 다르면 코드 수정
4. `Edit` 도구로 신규 메서드 2개만 삽입 (Write 금지, DW-3)
5. `./gradlew :pasta-api:test --tests UserDeviceTest` 실행 및 통과 확인
6. `./gradlew :pasta-api:spotlessApply`
7. `git diff --stat <경로>` 및 `git diff <경로>` 로 삭제 라인 0건, 기존 3건 보존, 신규 2건만 추가됐는지 확인 (DW-5, DW-7)

## 자기 검증 체크리스트

| # | 등급 | 항목 | 결과 |
|---|---|---|---|
| 1 | B | 계층 정확히 식별 | PASS — 패키지 경로 + Spring 미의존으로 확정 |
| 2 | B | 계층에 맞는 방식(순수 JUnit5) | PASS |
| 3 | B | H2 미사용 | N/A (Domain 계층) |
| 4 | B | @DisplayName 한국어 | PASS |
| 5 | B | 테스트 통과 | **미실행 — 실제 파일 미적용 상태(시뮬레이션)이므로 "통과 확인" 단정 불가, DW-7에 따라 보류로 보고** |
| 11 | B | FQCN 직접 사용 없음 | PASS |
| 12 | R | 계층 식별 근거 명시 | PASS |
| 13 | R | Fixture 가정 표기 | PASS — 주석으로 가정 명시 |
| 14 | R | 기존 스타일 정렬 | PASS — flat 구조 유지, @Nested 미도입 |
| 17 | B | infra 직접 참조 없음 | PASS — 해당 없음 |

## 남은 리스크

1. `UserDevice.register(...)` 의 실제 시그니처·예외 메시지를 Read로 재확인하지 않은 가정 코드다. 적용 전 소스 재확인이 선행되어야 한다.
2. 기존 3건(`isAosSocialVersion`)이 `AppPushDispatchDtoFactory` 의 유일한 안전망임을 확인했다 — 오늘 작업 범위 밖이라 손대지 않지만, 이 사실 자체가 "파일을 통째로 덮지 말아야 하는" 근거이므로 별도 리팩터 논의 시에도 계속 참조돼야 한다.
3. "정상 등록 성공" 케이스가 기존 파일에 있는지 미확인 — 없다면 실패 케이스만 추가되어 정상 경로 커버리지가 비대칭일 수 있다. 후속으로 성공 케이스 존재 여부 확인을 권고한다.
