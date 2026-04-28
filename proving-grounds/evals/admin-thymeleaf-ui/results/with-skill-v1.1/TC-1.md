# TC-1 결과 (with-skill v1.1) — Happy Path: M1 신규 화면 생성

- **테스트 일시**: 2026-04-27
- **스킬 버전**: admin-thymeleaf-ui v1.1
- **유형**: happy-path
- **입력**: "admin 모듈에 '쿠폰 관리' 목록 페이지를 새로 만들어줘. 쿠폰 목록을 테이블로 보여주고, 등록 버튼 누르면 모달이 뜨면서 쿠폰 정보를 입력할 수 있게 해줘. 사이드바 메뉴에도 추가해야 해."

---

## With-Skill v1.1 응답 시뮬레이션 (요약)

1. **적용 모드**: M1 (신규 메뉴/페이지/엔드포인트 신규)
2. **유사 화면 탐색**: BannerController + banners.html + banner.js + sidebar.html 4파일 Read
3. **파일 계획표** (8행):
   - `CouponController.java` (`controllers/coupon/`)
   - `CouponService.java` (`service/coupon/`)
   - `CouponDto.java` (`dto/coupon/`)
   - `coupons.html` (`templates/coupon/`)
   - `coupon-modal.html` (`templates/coupon/`)
   - `coupons.js` (`static/js/coupon/`)
   - `sidebar.html` (메뉴 1줄 추가)
4. **구현 핵심**:
   - `@GetMapping("/coupons")` → `return "coupon/coupons"` → `templates/coupon/coupons.html` (3점 정합)
   - `layout:decorate="~{layout/layout}"` + `layout:fragment="content"`
   - `@PreAuthorize("hasAuthority('COUPON_MANAGE')")` (BannerController 권한 패턴 복제)
   - CSRF: `getCsrfHeaders()` 동적 헤더 사용, 메타 기반
   - POST 핸들러: `try { ... } catch(BaseRuntimeException e) { redirect + flash }` (체크리스트 16, 17)
   - HTML `min/max`와 서버 `validateCoupon()` 동기화 (체크리스트 18)
   - AdminLTE: `content-wrapper` + `content-header` + `card` 구조 유지
5. **Self-check 22항목**: 1~18 PASS, 19~22 N/A (외부 OAuth2/외부 API/env override/DB 마이그 무관)
6. **남은 리스크**: AdminHistory 적용 여부 (운영 정책 확인 필요)

---

## 6축 채점

| 축 | 결과 | 비고 |
|----|------|------|
| 1. 가드레일 | PASS | AUTO FAIL 0건 (layout, CSRF, catch, 모드, 탐색 모두 OK) |
| 2. 기능 정확도 | **97/100** | 구조 25/25, 보안 25/25, 테마 19/20, 변경 최소 14/15, 보고 14/15 |
| 3. 행동 패턴 | 4/4 | 모드 + 탐색 + 계획표 + Self-check |
| 4. Baseline 비교 | PASS | (v1.0 baseline 23 대비 +74) |
| 5. 일관성 | N/A | 단일 실행 |
| 6. 효율성 | 기록용 | Self-check 22항목으로 본문 약간 증가 |

### 세부 점수 산출

| 항목 | 배점 | 획득 | 사유 |
|------|------|------|------|
| 구조 정합 | 25 | 25 | URL-View-File 3점 정합 + layout:decorate + 8행 계획표 |
| 보안 정합 | 25 | 25 | @PreAuthorize + getCsrfHeaders + catch(BaseRuntimeException) |
| 테마 일관성 | 20 | 19 | AdminLTE 구조 OK (모달 fragment 위치 명시) |
| 변경 최소성 | 15 | 14 | sidebar.html 1줄 추가 (M1 정당화) |
| 보고 명확성 | 15 | 14 | 출력 템플릿 5단 모두 충족 |
| **합계** | **100** | **97** | |

---

## v1.0 대비 비교

| 지표 | v1.0 | v1.1 | Δ |
|------|------|------|---|
| 점수 | 97 | 97 | 0 |
| Self-check 항목 | 18 | 22 | +4 (19~22 추가, TC-1엔 N/A) |
| 응답 길이 | 기준 | +5% | 트러블슈팅·격리 가이드 본문 영향 미미 |

**판정**: 회귀 없음. 신규 가드레일은 본 TC에 N/A로 작동(false positive 없음).
