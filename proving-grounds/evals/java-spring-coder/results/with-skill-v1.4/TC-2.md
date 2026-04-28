# TC-2 With-Skill v1.4 시뮬레이션 결과

- **테스트 일시**: 2026-04-27
- **모드**: B (단순 구현)
- **유형**: Edge Case (TDD 없음)
- **모델**: Sonnet (시뮬레이션)
- **버전**: v1.4

---

## 입력 요약

"coupon 도메인에 쿠폰 조회 API 하나 추가해줘. GET /api/v1/coupons/{couponId}"

---

## With-Skill v1.4 동작 시뮬레이션

### Phase 0
1. `docs/plans/`, `docs/tdd/` 탐색 → 문서 없음 → **모드 B**
2. `.claude/rules/` 로드, 01~12 적용 (admin 아님)
3. `pghd/coupon/...` 기존 패턴 Read — `MoneyballException`, `ExceptionConstants.COUPON_NOT_FOUND`, `ApiResponse.success()` 포맷 파악

### 구현
1. **Domain**: 기존 `CouponCodeEntity` 재사용 또는 신규 생성 시 동일 패턴
2. **Application**: `CouponDetailService.getCouponByIdOrElseNull` (네이밍 패턴 준수) → null 시 `MoneyballException(ExceptionConstants.COUPON_NOT_FOUND)`
3. **Application DTO**: `CouponDetailOutDto` (record)
4. **Web**: `CouponDetailController` `@GetMapping("/api/v1/coupons/{couponId}")` → `ApiResponse<CouponDetailResponse>` 래핑
5. **설정 체크**:
   - SecurityConstants.airArray 등록 검토 (인증 필요 여부)
   - 외부 API 없음 → env yml 4곳 N/A
6. **테스트**: Fake Repo + Service Test, MockMvc Web Test
7. **커밋 안 함**

### 자기 검증 16항목
- 1~13: 모두 PASS
- 14 (Non-bean Tx / OAuth2): N/A (해당 없음)
- 15 (SecurityContext 격리): N/A
- 16 (env yml 4곳): N/A (외부 API 의존 없음 — 명시)

---

## 6축 채점

### 축 1. 가드레일 — **PASS**

### 축 2. 기능 정확도

루브릭 4번(TDD 충실도)는 N/A → 나머지 항목에 배점 재분배 (15점을 다른 항목으로 균등 가산):
- 또는 단순화: TDD N/A 제외 85점 만점 환산.

| # | 항목 | 배점 | 점수 |
|---|------|------|------|
| 1 | 아키텍처 의존성 | 20 | 20 |
| 2 | 계층별 클래스 패턴 | 15 | 15 |
| 3 | 테스트 품질 | 20 | 20 |
| 4 | TDD 충실도 | N/A | N/A |
| 5 | 코딩 컨벤션 | 10 | 10 |
| 6 | 설정 완전성 | 10 | 10 |
| 7 | 가드레일 | 10 | 10 |
| | **합계** | 85 | **85/85 = 100%** |

### 축 3. 행동 패턴 (6/6)
- Phase 0 / 모드 B 판단 / 기존 패턴 탐색 / 생성 순서 / 자기 검증 / 설정 체크 — 모두 PASS

### 축 4. Baseline 비교
- v1.3: PASS — v1.4: PASS (동률, 회귀 없음)

### 축 5. 일관성 — N/A

### 축 6. 효율성
- 토큰 추정: ~19,500 (v1.3 18,812 대비 +3.7%)
- Tool: 1~2회

---

## v1.3 → v1.4 비교

| 항목 | v1.3 | v1.4 | 변화 |
|------|------|------|------|
| 결과 | PASS | PASS | 동률 |
| 자기 검증 N/A 처리 | 13개 중 무관 N/A | 16개 중 14·15·16 N/A | 자연스럽게 처리 |

---

## 판정

- **PASS** (회귀 없음)
- 새 가드레일은 본 TC와 직접 관련은 없으나, 16번(env yml 4곳)을 N/A로 명시함으로써 행동 패턴 강화
