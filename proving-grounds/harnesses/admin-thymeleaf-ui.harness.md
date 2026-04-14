# admin-thymeleaf-ui 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/admin-thymeleaf-ui/SKILL.md` |
| references | `anvil/skills/admin-thymeleaf-ui/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/admin-thymeleaf-ui/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/admin-thymeleaf-ui/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/admin-thymeleaf-ui/results/` |
| 리포트 | `proving-grounds/evals/admin-thymeleaf-ui/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 키워드/패턴 |
|---|------|-----------------|
| 1 | layout:decorate + layout:fragment 미적용 | 레이아웃 관련 속성 없는 HTML 생성 |
| 2 | URL-View-File 3점 정합 2개+ 깨짐 | @GetMapping 반환값 vs 파일 경로 불일치 |
| 3 | CSRF 토큰 하드코딩 또는 미적용 | 하드코딩된 토큰 문자열, fetch에 CSRF 헤더 없음 |
| 4 | catch(Exception) 사용 | `catch(Exception` 또는 `catch (Exception` 패턴 |
| 5 | 모드 선택(M1~M4) 없이 코드 생성 | 모드 선택 보고 없이 바로 코드 작성 |
| 6 | 기존 화면 읽지 않고 신규 패턴 창작 | 유사 화면 탐색 결과 보고 없음 |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- AUTO FAIL 규칙 0건 위반
- catch(Exception) 미사용
- CSRF 동적 헤더 사용

### 축 2. 기능 정확도 (100점 만점)

루브릭 기반:

| 항목 | 배점 |
|------|------|
| 구조 정합 (URL-View-File, layout) | 25 |
| 보안 정합 (@PreAuthorize, CSRF, catch) | 25 |
| 테마 일관성 (AdminLTE 구조) | 20 |
| 변경 최소성 (전역 파일 최소) | 15 |
| 보고 명확성 (모드, 계획표, Self-check) | 15 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 모드 선택 | M1~M4 중 적합한 모드를 선택했는가? |
| 유사 화면 탐색 | 기존 Controller+Template+JS 세트를 탐색했는가? |
| 파일 계획표 | 구현 전 파일 계획표를 작성했는가? |
| Self-check | 작업 완료 후 체크리스트를 제출했는가? |

### 축 4~6

java-spring-coder.harness.md와 동일 구조.

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | PASS (AUTO FAIL 0건) |
| 축 2 기능 정확도 | Happy Path 75+ PASS |
| 축 3 행동 패턴 | 4항목 중 3항목 이상 |
| 축 4 Baseline 비교 | PASS |

→ **실전 배치 가능**
