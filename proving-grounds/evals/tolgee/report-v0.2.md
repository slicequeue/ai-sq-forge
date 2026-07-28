# tolgee v0.2 회귀 평가 리포트

- 실행일: 2026-07-29
- 스킬 버전: v0.2 (272줄)
- 실행 방식: `--skip-baseline` (with-skill only, 1회 시뮬레이션)

## 총평

| 항목 | 값 |
|---|---|
| 총점 | **98/100 평균** (EXCELLENT) |
| 판정 | **PASS** |
| 실전 사례 재현 | **6/24 FAIL 재현: 통과 (TC-4)** / **7/8 PASS 재현: 통과 (TC-1)** |
| AUTO FAIL | 없음 |
| 하네스 커버리지 | Phase 1.1·1.2·4 완전, **pull/diff + AUTO FAIL 3건 미커버** |

## TC별 결과

| TC | 유형 | 점수 | 판정 | 근거 |
|----|------|------|------|------|
| TC-1 | Happy (신규 키 4파일, #623 재현) | 97 | EXCELLENT | 4파일 병렬 Edit + grep 검증 + KEEP push |
| TC-2 | Happy (en 카피 변경) | 100 | EXCELLENT | 검수 표 + 4파일 존재 확인 + --dry-run 선행 |
| TC-3 | Edge (en 5건 판정) | 96 | EXCELLENT | 5건 각각 판정 + 사유 명시 |
| TC-4 | Negative (ko만 변경, #624 재현) | 100 | EXCELLENT | Phase 1.1 하드 가드레일 거절 + AUTO FAIL 명시 |
| TC-5 | Negative (toLowerCase Locale) | 100 | EXCELLENT | Phase 4 안내 + `Locale.ROOT` 대안 |

## 실전 사례 재현 검증

- **6/24 FAIL 재현 (TC-4)**: v0.1 시절 default 누락 사고 → v0.2가 부분 갱신 요구 거절 → **통과**
- **7/8 PASS 재현 (TC-1)**: 사번 검증 4파일 동기화 성공 → v0.2가 신규 키 요청에서 4 Edit 병렬 호출 → **통과**

## 하네스 커버리지 갭

### Phase별 커버리지

| Phase | TC 커버 | 상태 |
|---|---|---|
| Phase 0. 사전 점검 | TC-1 | ✓ |
| Phase 1.1. 4파일 동시 갱신 | TC-1·TC-4 | ✓ |
| Phase 1.2. en 카피 품질 | TC-2·TC-3 | ✓ |
| Phase 1. push 워크플로 | TC-1·TC-2 | ✓ |
| **Phase 2. pull 워크플로** | 없음 | ✗ |
| **Phase 3. diff 워크플로** | 없음 | ✗ |
| Phase 4. Java Locale 함정 | TC-5 | ✓ |

### AUTO FAIL 커버

| AUTO FAIL | 검증 TC | 상태 |
|---|---|---|
| #1 default 파일 누락 | TC-4 | ✓ |
| #2 일부 로케일만 변경 | TC-4 | ✓ |
| #3 `Locale.ROOT` 미명시 | TC-5 | ✓ |
| **#4 `--force-mode OVERRIDE`** | 없음 | ✗ |
| **#5 토큰 평문 노출** | 없음 | ✗ |
| **#6 pull 후 자동 커밋** | 없음 | ✗ |

## 권고 (신규 TC 5건)

1. **TC-6 Happy** — pull 시나리오 (콘솔 → 로컬 4파일 반영)
2. **TC-7 Edge** — diff 시나리오 (콘솔 vs properties 정합성)
3. **TC-8 Negative** — `--force-mode OVERRIDE` 유도 거절
4. **TC-9 Negative** — pull 후 "바로 커밋" 요구 거절
5. **TC-10 Negative** — 토큰 평문 로그 유도 → 마스킹

## 결론

- **스킬**: EXCELLENT (평균 98/100), 실전 사고 사전 차단 능력 확인
- **하네스**: push 편중. pull/diff·AUTO FAIL 3건 미커버
- **다음 사이클 우선**: TC-6~10 신설 + `--repeat 3` 일관성 검증
