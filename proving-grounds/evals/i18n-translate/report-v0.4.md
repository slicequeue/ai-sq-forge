# i18n-translate v0.3 → v0.4 평가 리포트 (하네스 신설)

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-11-13 |
| 평가 대상 | v0.3 (moneyball 실전 자체 개발, 2026-09-30) forge 역수입 → 트레이닝 후 v0.4 |
| 이전 평가 | 없음 (forge 첫 평가, 루브릭·하네스·TC 신설) |
| 하네스 | `proving-grounds/harnesses/i18n-translate.harness.md` |
| 루브릭 | `anvil/skills/i18n-translate/references/evaluation-rubric.md` (7개 항목 100점, AUTO FAIL AF-1~7) |
| 모델 | sonnet (응답자 서브에이전트), 채점은 별도 |
| 실행 TC | 6건 (Happy 2 / Edge 2 / Negative 2) baseline + with-skill v0.3, TC-1 `--repeat 3`, v0.4 재실행 TC-2·3·6 |
| 결과 | `results/` (baseline, with-skill-v0.3, with-skill-v0.4, script-runs) |

## 1. 정합성 점검

| 항목 | 결과 | 조치 |
|------|------|------|
| frontmatter | forge 형식과 일치 | 없음 |
| 하드 가드레일·자기 검증 체크리스트 | 없음 | v0.4 신설 |
| 스크립트 경로 | SKILL.md 는 스킬 폴더 기준(`python3 scripts/...`), 스크립트는 `--root .` 저장소 루트 실행 전제 | "저장소 루트에서 `<스킬경로>/scripts/...` 로 실행" 명시 |
| 개인 절대경로 | `ja-house-rules.md` 대조 명령에 `JP=/Users/kakao/...` 하드코딩, with-skill 응답 6건이 그대로 옮겨 적음 | `PASTA_JP_ROOT` 환경변수로 교체. `sync_langskill.sh` 는 환경변수 기본값으로만 사용해 유지 |
| `check_ratio.py` 안내 문구 | "length:review 로 표시" 출력이 SKILL.md("태그 기능 없음, PR 본문에 기록")와 충돌 → 응답 2건이 properties 에 `# length:review` 주석 삽입 | 문구 정정 |
| moneyball 전용 내용 | `bundles.md`·SKILL.md 일부(16개 basename, gradle 명령, `ALLOWED_MISMATCHES` 등)에 혼재 | 분리는 제안으로만 (8절) |

## 2. 6축 결과

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 | PASS | with-skill AUTO FAIL 0건 |
| 2. 기능 정확도 | 96.5 EXCELLENT | 최종 버전 기준 평균 |
| 3. 행동 패턴 | 충족 | 해당 항목 기준 95% 이상 |
| 4. Baseline 비교 | STRONG PASS | 58.8 → 96.5 (+37.7) |
| 5. 일관성 | PASS | TC-1 3회 98/97/96, 편차 2 |
| 6. 효율성 | 기록 | 6절 |

## 3. TC별 결과

| TC | 유형 | Baseline | v0.3 | v0.4 재실행 |
|----|------|----------|------|-------------|
| TC-1 CGM 누락 채우기 | happy | 63 | 98/97/96 (3회) | 재실행 안 함 |
| TC-2 기존 번역 검토 | happy | 71 | 97 | 99 |
| TC-3 깨진 ja 파일 + 번들 함정 | edge | 82 | 96 | 96 |
| TC-4 의학 문구·음식명 | edge | 65 | 97 | 재실행 안 함 |
| TC-5 기계번역으로 테스트만 통과 | negative | **0 (AF-7)** | 94 | 재실행 안 함 |
| TC-6 가이드에 반하는 통일 요구 | negative | 72 | 94 | 96 |

## 4. TC 유형별 Baseline 비교

| 유형 | 격차 |
|------|------|
| happy | +31 |
| edge | +23 |
| negative | +59 |

스킬 가치는 negative 에서 가장 크다. baseline 은 TC-5 에서 "미검수" 주석만 달고 기계번역 42건을 파일 끝에 붙여 커밋했다. 반대로 baseline 이 스킬보다 먼저 짚은 것도 있다: MessageFormat 홑따옴표 이스케이프(`''`). v0.3 스킬에는 이 규칙이 없었다.

## 5. 트레이닝 (v0.3 → v0.4)

| 위치 | 변경 |
|------|------|
| SKILL.md | 하드 가드레일 8항목(AF-1~7 대응), 자기 검증 체크리스트 11항목, MessageFormat 홑따옴표 규칙, "플레이스홀더 자리에 숫자 고정 금지", 스크립트 실행 위치 명시. 168 → 203줄 |
| `check_parity.py` | 플레이스홀더 개수·번호 불일치, 홑따옴표 검사 추가 |
| `ja-house-rules.md` | 개인 절대경로 → `PASTA_JP_ROOT` |
| `check_ratio.py` | 안내 문구 정정 |

`check_parity.py` 검증:
- 합성 픽스처(파손 유형을 일부러 넣은 샘플 properties)에서 4가지 파손 유형 모두 검출.
- moneyball 실제 저장소(읽기 전용)에서 플레이스홀더 불일치 16건, 홑따옴표 14건 신규 검출. 예: `analysis.report.detail.tir.content` 의 ja 값은 `{0}`·`{1}` 대신 `70~180` 을 박아 둠. 저장소는 수정하지 않고 보고만 함.

효과: TC-2 재실행에서 `You've had {0}%`(`{0}` 미치환)가 `You have had {0}%` 로 바뀜. TC-2·3·6 재실행에서 개인 절대경로·스크립트 경로 문제 소멸.

## 6. 효율성

| 구분 | 토큰 | tool 호출 | 시간 |
|------|------|-----------|------|
| Baseline | 약 52k | 2회 | 약 42초 |
| With-skill | 약 95~102k | 약 7회 | 약 118~134초 |

비용 대부분은 langskill.md(43KB) 읽기.

## 7. 확인된 것 vs 가정한 것

| 구분 | 내용 |
|------|------|
| 확인 | 17회 실행 응답 원문 저장 |
| 확인 | 스크립트 4종 실제 동작 (`python3 -I`, moneyball 은 읽기 전용) |
| 가정 | 시뮬레이션 응답이 실제 작업 품질을 대표한다. 실제 파일 반영·Gradle 테스트는 미실행 |
| 가정 | 단일 채점자, 판단형 항목 ±3점 |
| 가정 | TC-1·4·5 는 v0.4 미재실행, v0.3 점수로 대체. 다음 `--skip-baseline` 에서 전부 재실행 권장 |

## 8. 남은 약점과 일반화 제안 (결정 필요)

1. **승인 게이트 경계 모호**: TC-1 의 고혈당 알림(물 한 잔 + 10분 걷기)을 3회 모두 "의학적 권고"로 보고 반영 보류. 일관되고 근거도 있으나, CGM 알림 문구 대부분이 이 형태라 실전에서 번역이 계속 밀릴 수 있다. 경계는 스킬 소유자와 의학 검수 담당이 정해야 하므로, 하네스는 두 판정을 모두 정답으로 받도록 했다.
2. **moneyball 전용 내용 분리**: `bundles.md` → `bundles-moneyball.md`, SKILL.md 의 저장소 전용 내용 → `references/repo-moneyball.md`.
3. **`check_parity.py` 옵션**: `--allow-file`(의도된 누락 허용 목록, 지금은 의도된 누락도 exit 1), `--bundle` 정확 일치(지금은 부분 일치라 `--bundle message` 가 16개 번들을 전부 잡음).
4. **negative-tc-catalog 추가 후보**: G-6 "기계번역으로 테스트만 통과", G-7 "정본 가이드에 반하는 용어 통일".

## 9. 최종 판정

PASS — v0.4, AUTO FAIL 0건, 평균 96.5, 일관성 PASS. 실전 배치 가능.
