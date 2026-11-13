# java-layered-unit-testing 평가 루브릭

- [평가 항목](#평가-항목)
- [AUTO FAIL 조건](#auto-fail-조건)
- [합격 기준](#합격-기준)
- [평가 실행 방법](#평가-실행-방법)

---

## 평가 항목

| # | 항목 | 배점 | 설명 |
|---|------|------|------|
| 1 | **계층별 테스트 방식 적합성** | 25 | Domain=순수 JUnit, App=Mockito, Infra=@DataJpaTest+Testcontainers |
| 2 | **테스트 통과 여부** | 25 | 모든 테스트가 실제로 통과하는가 |
| 3 | **테스트 커버리지 / 품질** | 20 | 핵심 분기, 엣지 케이스, 실패 시나리오 포함 |
| 4 | **코딩 컨벤션 준수** | 15 | @DisplayName, Given-When-Then, AssertJ, @Nested |
| 5 | **기존 패턴 일관성** | 15 | 프로젝트 기존 테스트와 스타일 일관 |
| | **합계** | **100** | |

---

## AUTO FAIL 조건

1. **H2 DB 사용** (Testcontainers MySQL 필수)
2. **Domain 계층 테스트에 @SpringBootTest 사용**
3. **테스트 전체 실패 (컴파일 에러 포함)**
4. **계층 무시하고 일괄 @SpringBootTest 적용**
5. **FQCN 직접 사용** — 테스트 코드 본문(import 외)에 `com.x.y.Z` 형태 패키지 경로 박힘. `new x.y.Z()` / `isInstanceOf(x.y.Z.class)` / 변수·매개변수·제네릭 모두 적용. PR #527 사례.

---

## 합격 기준

| 등급 | 점수 | 설명 |
|------|------|------|
| **EXCELLENT** | 90~100 | 계층별 방식 완벽, 전체 통과, 엣지 케이스 포함 |
| **PASS** | 75~89 | 계층별 방식 OK, 테스트 통과, 경미한 미흡 |
| **FAIL** | 0~74 | 계층 구분 미흡 또는 테스트 실패 |

---

## 평가 실행 방법

### 테스트 케이스 유형

| 유형 | 비율 | 예시 |
|------|------|------|
| Happy Path | 50% | Application Service 테스트 작성 요청 |
| Edge Case | 30% | Domain 복잡 로직 테스트, Repository 커스텀 쿼리 테스트 |
| Negative | 20% | H2 사용 유도, @SpringBootTest 유도, 계층 미구분 유도 |
