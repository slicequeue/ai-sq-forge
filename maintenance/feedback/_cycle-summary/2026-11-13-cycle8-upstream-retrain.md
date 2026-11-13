# 사이클 8 — 실전 역수입 + 재평가·트레이닝 (2026-11-13)

## 배경

사이클 7 배포(2026-09-16) 이후 forge 커밋이 없는 동안, 실전 저장소에서 컴포넌트가 직접 수정됐다. forge 원본이 실전보다 한 사이클 뒤처진 상태였다.

| 출처 | 내용 |
|------|------|
| pasta-japan-server `.claude/` (2026-10-16) | GLP-1 PR 19건 리뷰 45건 대응: 스킬 6건·에이전트 1건 수정, `review-recurrence-guard` RR-13·14·L·§16 추가, `review-lint.py`·푸시 훅 신설. forge 평가 없이 실전 적용 |
| moneyball `.claude/` (2026-09-30) | 자체 개발 스킬 `i18n-translate` v0.3. 루브릭·하네스 없음 |
| poc-meal-recommender | 9/16 이후 변화 없음 |

## 역수입 방식

- 3-way 병합(ours=forge, base=forge 를 배포 경로로 바꾼 사본, theirs=실전본)으로 실전에서 실제로 바꾼 부분만 forge 에 얹었다. 경로 표기만 다른 공통 가드 3종·루브릭 2건은 forge 원본 유지.
- 배포 시 제거되는 줄(근거, proving-grounds 참조) 복원, 체크리스트 번호 순서 정리.
- 백업: `forge/backup/2026-11-13-upstream/`

## 평가·트레이닝 결과

컴포넌트별 독립 에이전트가 신규 TC(10/16 변경 겨냥, Negative·Edge 중심)를 추가하고 baseline·with-skill 을 응답자·채점자 분리로 실행한 뒤, 감점 원인을 스킬에 반영해 재실행했다.

| 컴포넌트 | 역수입 | 최종 | 점수 | 신규 TC baseline → with-skill | 트레이닝 핵심 |
|----------|--------|------|------|-------------------------------|---------------|
| java-spring-coder | 1.16 | 1.17 | 97.6 | 66.7 → 97.7 | 주석 존댓말 규칙을 독립 절로 분리(본문 문체 전염) |
| self-code-reviewer | 2.3 | 2.4 | 96.0 | 59 → 97 | lint 결과 지어내기 금지(미실행 표기), RR-9 스코프 경계 |
| java-layered-unit-testing | 1.8 | 1.9 | 93.4 | 60.7 → 91.7 | 평가 자원의 Mockito 정답 정정, 예시 오류, 요청 외 분기·결함 수정 후 제출 |
| pr-feedback-resolver | 1.8 | 1.9 | 97.6 | 47.3 → 97.0 | 규칙 단위 스윕, lint 는 PR 전체 diff |
| git-pr | 0.5 | 0.6 | 98.4 | 62(전부 AUTO FAIL) → 97.7 | "해당 없음" 채움 섹션 금지, 선택 섹션 위치 고정 |
| java-business-logic-reviewer | 0.3 | 0.4 | 100 | 55 → 100 | 출처 PR 인용, 외부 호출 보상 판단 |
| coding-implementer | 0.8 | 0.9 | 100 | 28 → 100 (happy) | Phase 3-0: 미확정 설계 결정은 구현 전 확인, 가드가 정한 항목은 묻지 않음 |
| i18n-translate | 0.3 | 0.4 | 96.5 | 58.8 → 96.5 | 하네스 신설, 하드 가드레일·자기 검증, check_parity 플레이스홀더·홑따옴표 검사 |

with-skill AUTO FAIL 전 컴포넌트 0건.

## 공용 자원 반영

| 파일 | 반영 |
|------|------|
| `review-recurrence-guard.md` | RR-12 표 끊김 수정, §15 `[위반]` 잔존 시 완료 보고·커밋 금지 / `[확인]` 원문 인용 / 미실행 추정 금지 / FQCN·LAYER 리뷰 소유권, §16 답할 수 없는 질문 처리, RR-L 표에 주석 문체 |
| `negative-tc-catalog.md` | D-3 품질 게이트 우회 유도, M-7~M-10 |
| `review-lint.py` | 저장소 루트 `src/test/`·`domain/` 경로 미판정 결함 수정(실측 확인), 주석 평서형 `[확인]` 검사, ResponseEntity 메시지 문장 정정 |

## 관찰 (다음 사이클 입력)

1. **실전 직접 수정이 forge 평가를 건너뛴다.** 10/16 수정분 7건 중 6건에서 forge 평가로 결함이 나왔다(주석 규칙 매몰, lint 결과 지어내기, 사후 확인, 평가 자원과 규칙 충돌 등). 실전 수정 후 역수입·평가까지의 지연이 4주였다.
2. **규칙 추가가 평가 자원과 충돌할 수 있다.** java-layered-unit-testing v1.8(Fake 우선)은 기존 루브릭·TC 가 Mockito 를 정답으로 채점하고 있어, 평가 자원부터 고치지 않으면 올바른 응답이 감점됐다.
3. **수정이 반대 방향 실패를 만든다.** coding-implementer(사후 확인 → 과잉 질문), java-business-logic-reviewer(PR 인용 강화 → RR 과잉 인용). 수정 후 재실행이 필수다.
4. **baseline 강도는 TC 유형보다 "프로젝트 규칙 의존도"에 좌우된다.** java-layered-unit-testing 은 happy-path 에서도 +29 격차(테스트 더블 기본값 차이).

## 미결 (사용자 결정 필요)

- Clock 주입 규칙(RR-2 확장): java-spring-coder 5건 중 4건이 `Instant.now()` 직접 호출
- java-spring-coder SKILL.md 723줄(400줄 원칙 초과) — references 분리 여부
- i18n-translate moneyball 전용 내용 분리, 의학적 권고 승인 게이트 경계
- 규칙 08 §3 H2 언급과 스킬의 H2 금지 충돌 (pasta 원본, 프로젝트 소유 문서)
- 실전 재배포: pasta·moneyball 사본이 forge 최신보다 뒤처짐. 실전 `review-lint.py` 에도 루트 경로 결함 존재
- 공통: `--repeat 3` 일관성, 미재실행 회귀 TC
