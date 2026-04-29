# TC-2 — Edge Case: TDD 없이 단순 조회 API 구현 (with-skill v1.5)

## 응답 요약

- Phase 0: TDD 부재 인지 → **모드 B 자동 전환** 명시
- 기존 `CouponEntity` 가정 + 신규 메서드 1개 추가 (`findById`)
- 4계층 구현: Domain (Repository I 메서드 추가) → Infra (RepositoryImpl) → App (`CouponQueryService` + OutDto) → Web (`CouponQueryController` + Response)
- 계층별 테스트: App(Fake), Web(MockMvc), Infra(Testcontainers `@DataJpaTest`)
- 가정 사항(`MoneyballException` 존재 등) 명시적으로 보고
- 커밋 안 함

## 채점

| 항목 | 점수 |
|---|---|
| 1. 아키텍처 의존성 | 20 |
| 2. 계층별 패턴 | 14 (Web에서 Domain `CouponStatus` enum 참조 — 자체 인지하고 검토 명시, 1점 감점) |
| 3. 테스트 품질 | 18 (App/Web/Infra 각 2건. Mockito 사용은 외부 의존성 아닌 단순 mock — 살짝 Fake 권고) |
| 4. TDD 충실도 | N/A → 재분배 |
| 5. 코딩 컨벤션 | 10 |
| 6. 설정 완전성 | 10 |
| 7. 가드레일 | 10 |
| **합계** | **92** (TDD 항목 N/A 재분배 후) |

## AUTO FAIL 검증

- (6) FQCN: 본문 0건 — 모든 외부 클래스 import + 단순명

## 행동 패턴 (6/6)

Phase 0 ✓ / 모드 B 자동 판단 ✓ / 기존 패턴 가정 명시 ✓ / 생성 순서 ✓ / 17항목 체크 ✓ / 설정 체크 ✓

## 판정: PASS (92/100)
