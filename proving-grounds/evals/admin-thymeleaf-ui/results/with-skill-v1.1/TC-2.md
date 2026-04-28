# TC-2 결과 (with-skill v1.1) — Edge Case: M2 기존 화면 개선

- **테스트 일시**: 2026-04-27
- **스킬 버전**: admin-thymeleaf-ui v1.1
- **유형**: edge-case
- **입력**: "배너 관리 페이지에 '노출 기간' 필드를 추가하고, 기간 만료된 배너는 회색으로 표시해줘. 배너 등록 모달에도 기간 입력 필드를 넣어줘."

---

## With-Skill v1.1 응답 시뮬레이션 (요약)

1. **적용 모드**: M2 (기존 화면 개선)
2. **유사 화면 탐색**: 기존 BannerController.java + banners.html + banner-modal.html + banner.js Read
3. **파일 계획표** (4행, 모두 수정):
   - `BannerController.java`: DTO에 `displayStartAt/displayEndAt` 필드 추가, `validateBanner()`에 기간 검증
   - `banners.html`: 테이블에 기간 컬럼 + `th:classappend="${banner.expired} ? 'text-muted bg-light'"`
   - `banner-modal.html`: 두 `<input type="datetime-local">` 추가, HTML `min`/`max` 제약
   - `banner.js`: 폼 제출 시 기간 직렬화
4. **구현 핵심**:
   - 전역 파일(head/script/layout/sidebar) 변경 0건
   - 기존 마크업 스타일 그대로 유지 (form-group, col-md-6 패턴 복제)
   - POST: `catch(BaseRuntimeException e) → redirectAttributes.addFlashAttribute("error", e.getMessage())` 적용
   - HTML `min="2024-01-01"` `max="2099-12-31"` ↔ 서버 `validateDisplayPeriod()` 범위 동기화 (체크리스트 18)
   - 만료 판정 로직은 Service에서 `expired = now.isAfter(displayEndAt)` 계산 후 DTO 주입
5. **Self-check 22항목**: 1~18 PASS, 19~21 N/A, 22 PASS (DB 컬럼 추가 확인 — Flyway V{n}__add_banner_display_period.sql 명시)
6. **남은 리스크**: 기존 배너 데이터의 NULL 기간 처리 (V{n} 마이그레이션 default 값 정책 확인 필요)

---

## 6축 채점

| 축 | 결과 | 비고 |
|----|------|------|
| 1. 가드레일 | PASS | AUTO FAIL 0건 |
| 2. 기능 정확도 | **94/100** | 구조 25/25, 보안 25/25, 테마 19/20, 변경 최소 15/15, 보고 10/15 |
| 3. 행동 패턴 | 4/4 | M2 + 4파일 Read + 계획표 + Self-check |
| 4. Baseline 비교 | PASS | (v1.0 baseline 40 대비 +54) |
| 5. 일관성 | N/A | 단일 실행 |
| 6. 효율성 | 기록용 | DB 마이그 체크리스트(22)로 사이클 1회 추가 |

### 세부 점수 산출

| 항목 | 배점 | 획득 | 사유 |
|------|------|------|------|
| 구조 정합 | 25 | 25 | 변경 4파일 정합, layout 보존 |
| 보안 정합 | 25 | 25 | catch(BaseRuntimeException) + 검증 동기화 |
| 테마 일관성 | 20 | 19 | th:classappend 조건부 스타일 자연스러움 |
| 변경 최소성 | 15 | 15 | 전역 파일 0건 |
| 보고 명확성 | 15 | 10 | DB 마이그 시점·default 처리 리스크 보고 가능 |
| **합계** | **100** | **94** | |

---

## v1.0 대비 비교

| 지표 | v1.0 | v1.1 | Δ |
|------|------|------|---|
| 점수 | 92 | 94 | **+2** |
| 행동 변화 | 18항목 Self-check | **체크리스트 22 (DB 스키마 확인) PASS** → V{n} 마이그레이션 명시 | 향상 |

**판정**: 회귀 없음. 오히려 +2점 (체크리스트 22번 — DB 컬럼 참조 전 스키마 확인 — 으로 인해 마이그레이션을 명시적으로 다루게 됨).
