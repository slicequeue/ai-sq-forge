# admin-thymeleaf-ui 테스트 리포트

- **테스트 일시**: 2026-04-14
- **하네스**: proving-grounds/harnesses/admin-thymeleaf-ui.harness.md
- **모델**: sonnet
- **테스트 케이스**: 3개 (Happy Path 1 / Edge Case 1 / Negative 1)
- **반복 횟수**: 1

---

## 6축 평가 결과 요약

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 준수 | PASS | 위반 0건 (3TC 모두 AUTO FAIL 0건) |
| 2. 기능 정확도 | 94.7/100 | EXCELLENT |
| 3. 행동 패턴 | 4/4 | 모드 선택, 유사 화면 탐색, 파일 계획표, Self-check |
| 4. Baseline 비교 | PASS | Baseline 30.3 → With-Skill 94.7 (+64.4) |
| 5. 일관성 | N/A | 단일 실행 (TC간 편차 5점 이내) |
| 6. 효율성 | 기록용 | 탐색+계획 포함 토큰 2~3배 예상 |

## TC별 상세 결과

### TC-1: Happy Path — M1 신규 화면 생성 [happy-path]

| 항목 | Baseline | With-Skill |
|------|----------|------------|
| 기능 정확도 | 23 (AUTO FAIL 3건) | 97 (EXCELLENT) |
| 가드레일 | FAIL (layout 미적용, 모드 없음, 탐색 없음) | PASS |
| 행동 패턴 | - | 4/4 |

- Baseline: 모드 없이 바로 코딩, layout:decorate 미적용, CSRF 하드코딩, catch(Exception), 계획표/Self-check 없음
- With-Skill: M1 선택 → BannerController 세트 탐색 → 5파일 계획표 → layout:decorate + URL-View-File 3점 정합 → @PreAuthorize → getCsrfHeaders() → catch(BaseRuntimeException) → 사이드바 동시 정합 → Self-check 18항목

### TC-2: Edge Case — M2 기존 화면 개선 [edge-case]

| 항목 | Baseline | With-Skill |
|------|----------|------------|
| 기능 정확도 | 40 (AUTO FAIL 2건) | 92 (EXCELLENT) |
| 가드레일 | FAIL (모드 없음, 탐색 없음) | PASS |
| 행동 패턴 | - | 4/4 |

- Baseline: 기존 파일 읽지 않고 독자 판단, catch(Exception), 서버 검증 미동기화
- With-Skill: M2 선택 → 기존 4파일 Read → 최소 변경 계획 → th:classappend 조건부 → catch(BaseRuntimeException) + flash → HTML/서버 검증 동기화

### TC-3: Negative — 전역 파일 변경 유도 + CSRF 하드코딩 유도 [negative]

| 항목 | Baseline | With-Skill |
|------|----------|------------|
| 기능 정확도 | 28 (AUTO FAIL 1건) | 95 (EXCELLENT) |
| 가드레일 | FAIL (CSRF 하드코딩 수용) | PASS |
| 행동 패턴 | - | 4/4 |

- Baseline: script.html 전역 추가 수용, CSRF 'abc123' 하드코딩 수용
- With-Skill: 전역 추가 거부(페이지 단위 로드 권장), CSRF 하드코딩 거부(getCsrfHeaders() 동적 패턴 안내)

## Baseline 공통 실패 패턴

| 패턴 | 빈도 | 원인 |
|------|------|------|
| 모드 선택 없이 즉시 코딩 | 3/3 TC | 작업 분류 프레임 없음 |
| 기존 화면 탐색 미수행 | 3/3 TC | Reuse Before Reinvent 원칙 없음 |
| catch(Exception) 사용 | 2/2 코딩 TC | 프로젝트 예외 처리 패턴 미파악 |
| 파일 계획표·Self-check 없음 | 3/3 TC | 보고 프로토콜 없음 |

## 최종 판정

**PASS — 실전 배치 가능 (EXCELLENT, 가중 평균 94.7점)**

## 개선 사항

1. AdminHistory 패턴 기준 명확화 — 어떤 기능에 필수인지 Self-check와 연결 가이드 보강
2. M3/M4 모드 TC 추가 — 보안/구조 정리, 진단 전용 모드 테스트 미포함
3. 타임존 처리 TC 추가 — displayTimezone 패턴이 절대금지에 명시되어 있으나 TC 미포함
4. 사이드바 토글 그룹 신설 패턴 — golden-path-map.md 보강 권장
