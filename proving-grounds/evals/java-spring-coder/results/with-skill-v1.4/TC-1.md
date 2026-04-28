# TC-1 With-Skill v1.4 시뮬레이션 결과

- **테스트 일시**: 2026-04-27
- **모드**: A (TDD 전체 구현)
- **유형**: Happy Path
- **모델**: Sonnet (시뮬레이션)
- **버전**: v1.4 (역수입 후)

---

## 입력 요약

쿠폰 사용(Redeem) API TDD 계획서 — 4 Phase (Domain/Infra/App/Web) 일괄 구현 요청.

---

## With-Skill v1.4 동작 시뮬레이션

### Phase 0. 사전 확인
1. `docs/plans/*.md`, `docs/tdd/*.md` 탐색 → TDD 문서 존재 확인 → 모드 A
2. `.claude/rules/00-rules-index.md` 로드 (01~12 적용, admin 모듈 아님)
3. JDK 21 export 명령 준비
4. 같은 도메인(`pghd/coupon/...`) 기존 코드 스캔 → MoneyballException, ExceptionConstants, ApiResponse, SecurityConstants 패턴 파악

### Phase 1~4 구현 순서
1. **Domain**: `CouponCodeEntity` (class, `@Getter`+`@ToString`+`@EqualsAndHashCode` 병행), `redeem(userId, now)`, `isExpired()`, `Objects.requireNonNull` 검증, `of()` 팩토리 — JPA/Spring 어노테이션 0건
2. **Domain Repository**: `CouponCodeRepository` (interface, 도메인 모델만)
3. **Infrastructure**: `CouponCodeJpaEntity` (class, `@Column(nullable=false)` + `@NotNull` 병행), `toEntity()`, `from()`, `CouponCodeJpaRepository`, `CouponCodeRepositoryImpl`
4. **Application**: `CouponRedeemService` (`@RequiredArgsConstructor`, `@Slf4j`), `CouponRedeemInDto`/`OutDto` (record)
5. **Web**: `CouponRedeemController` (`@RestController`, `@PostMapping`), `CouponRedeemRequest`/`Response` (record)
6. **설정**:
   - SecurityConstants.airArray에 `/api/v1/coupons/redeem` 등록
   - 외부 API 의존 없음 → env yml 4곳 변경 N/A 명시
7. **Test Double**: `FakeCouponCodeRepository` (HashMap 기반)
8. **Test**:
   - `CouponCodeEntityTest` (Fake)
   - `CouponRedeemServiceTest` (Fake)
   - `CouponRedeemControllerTest` (`@WebMvcTest` + MockMvc)
   - `CouponCodeRepositoryImplTest` (`@DataJpaTest` + Testcontainers MySQL)
9. 테스트 실행 → spotlessApply → TDD 체크박스 `[x]` 업데이트
10. **자기 검증 16항목 통과** — 14·15·16번 모두 N/A 또는 PASS (외부 API 없음, Non-bean에 `@Transactional` 없음, OAuth2 없음)
11. **커밋하지 않음** — 변경 사항 보고만

---

## 6축 채점

### 축 1. 가드레일 (GATE)
- AUTO FAIL 위반 0건. **PASS**

### 축 2. 기능 정확도 (100점)

| # | 항목 | 배점 | 점수 | 비고 |
|---|------|------|------|------|
| 1 | 아키텍처 의존성 | 20 | 20 | Domain 순수, JPA/Spring 어노테이션 0건 |
| 2 | 계층별 클래스 패턴 | 15 | 15 | 3단계 Repository, record/class, toEntity/from, `@Column`+`@NotNull` 병행 |
| 3 | 테스트 품질 | 20 | 20 | Fake + MockMvc + Testcontainers MySQL |
| 4 | TDD 충실도 | 15 | 15 | 4 Phase 전수 구현, 체크박스 업데이트 |
| 5 | 코딩 컨벤션 | 10 | 10 | 로그 접두사, var/약어/와일드카드 import 금지 준수 |
| 6 | 설정 완전성 | 10 | 10 | airArray 등록 + env yml N/A 명시 (v1.4 16번 적용) |
| 7 | 가드레일 | 10 | 10 | 위반 0건 |
| | **합계** | **100** | **100** | |

### 축 3. 행동 패턴 (6/6)
- Phase 0 실행 / 모드 A 판단 / 기존 패턴 탐색 / 코드 생성 순서 / 자기 검증 16항목 / 설정 체크 — 모두 충족

### 축 4. Baseline 비교
- v1.3 시점 100/100 → v1.4 100/100 → **회귀 없음, 동률 PASS**

### 축 5. 일관성
- N/A (`--repeat 1`)

### 축 6. 효율성
- 토큰 추정: ~30,000 (v1.3 28,960 대비 +3.6%, 자기 검증 14·15·16 추가로 약간 증가)
- Tool 호출: 4~5회 (v1.3 4회 대비 +1, env yml grep 추가 가능성)
- 시간: ~62초

---

## v1.3 → v1.4 비교

| 항목 | v1.3 | v1.4 | 변화 |
|------|------|------|------|
| 기능 정확도 | 100 | 100 | 동률 |
| 가드레일 | PASS | PASS | 유지 |
| 자기 검증 항목 수 | 13개 | 16개 | +3 (14·15·16) |
| 신규 가드레일 적용 | - | OAuth2/Non-bean Tx/env yml — 본 TC에선 N/A 안전 적용 | OK |

---

## 판정

- **PASS** (회귀 없음, 100/100 유지)
- 새 가드레일은 본 TC와 무관하므로 negative impact 없음
- 자기 검증 14·15·16번이 추가됐지만 무관 항목은 N/A 처리로 자연스럽게 흐른다
