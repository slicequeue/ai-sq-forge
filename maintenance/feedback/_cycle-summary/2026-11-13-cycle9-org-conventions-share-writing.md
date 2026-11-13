# 사이클 9 — 조직 코딩 컨벤션 + 공유 글 가드 (2026-11-13)

조직 코딩 컨벤션·공유 글 가드 반영 완료 (forge, 실전 3곳 배포)
- 공용 자원 신설: vc-conventions-guide(PR #7 7cc266d 기준), share-writing-guard + share-lint, review-lint VC 검사
- 컴포넌트 15건 반영·평가: with-skill AUTO FAIL 0건, 신규 TC 최종 94~100점, 비적용 저장소 과잉 적용 0건
- 배포: pasta·moneyball 조직 컨벤션 켜짐, poc 꺼짐을 review-lint 로 실측
- 미결 7건 (맨 아래)

## 배경

| 입력 | 내용 |
|------|------|
| virtualcare/coding-conventions PR #7 | 리뷰 기준과 어긋난 컨벤션 10항목 갱신 제안. 미병합, 항목별 팀 합의 중 |
| 팀 공유 글 작성 룰 제안 | 첫 줄 결론+반영 단계, 한 일 2~4줄, 부탁은 있을 때만, 미확인·빈 칸·유추 금지 (BLUF·스니펫·PPP·깃랩 비동기) |
| 제약 | forge 저장소(slicequeue/ai-sq-forge)는 public. 조직 컨벤션 원문은 internal 문서 |

## 구조

| 자원 | 위치 (배포본) | 대상 |
|------|---------------|------|
| 조직 컨벤션 원문 | `forge/common/vc-conventions/` (gitignore, `vc-conventions-sync.sh` 로 받음) → `.claude/shared/vc-conventions/` | virtualcare 저장소만 |
| 적용 가이드 | `forge/common/vc-conventions-guide.md` → `.claude/shared/` | virtualcare 저장소만. 파일 존재가 곧 "적용" 판정 |
| 공유 글 가드·lint | `forge/common/share-writing-guard.md`, `share-lint.py` → `.claude/shared/` | 전 프로젝트 + 전역 `~/.claude/CLAUDE.md` 요약 + 전역 스킬 4건 |
| review-lint VC 검사 | `forge/common/review-lint.py` | 옆에 가이드가 있으면 자동 켜짐 |
| 배포 판정 | `anvil/commands/forge-deploy.md` v1.3 Phase 0.5, `forge/tools/forge_deploy.py` | origin 이 virtualcare 인지로 판정 |

우선순위: 하드 가드레일 > 조직 컨벤션 > 프로젝트 규칙 스타일 > 같은 파일 관례. 신규·변경 코드에만 적용, 기존 코드 일괄 변경 금지.

## 충돌 판정 (실측 근거)

| 항목 | 판정 | 근거 |
|------|------|------|
| 정적 팩토리 | 신규 클래스는 생성자, 기존 `from()` 있는 클래스는 수정해 씀 | 최근 60일 추가 pasta 12 / moneyball 324 |
| 커밋·PR 제목 | `[핵심키워드] 명사형 요약` | `[키워드]` 140:34 / 564:85 (대부분 squash 제목) |
| 이슈 키 위치 | 원문(요약 앞), 합의 시 변경 | moneyball 앞 1 : 끝 괄호 68 |
| 테스트 DB | 모듈 기존 설정 유지·전환 금지 | 두 저장소 모두 모듈별 H2·Testcontainers 혼재, pasta-api 는 H2 |
| `@SpringBootTest` | E2E 만, rollback-only 검증만 예외 | 46 / 56개 파일 |
| Controller·Service 이름 | 신규부터 / 같은 패키지 관례 | Command·Query 15/236, 15/264 |
| API 계약 | 사용자가 명시한 경로·필드명은 조직 컨벤션 대상 아님 | java-spring-coder TC-18 에서 경로를 바꾼 사례 |

## 컴포넌트 결과

| 컴포넌트 | 버전 | 신규 TC baseline → 최종 | 핵심 트레이닝 |
|----------|------|--------------------------|---------------|
| java-spring-coder | 1.17 → 1.18 | 85.7 → 98.0 | 축약 변수명 거부는 적용·비적용 공통, API 계약 변경 금지 |
| java-layered-unit-testing | 1.9 → 1.10 | 74 → 95.3 | 테스트 DB "H2 절대 금지"를 모듈 설정 유지로(실측과 불일치), 보고 첫 줄 위치 |
| coding-implementer | 0.9 → 1.0 | AUTO FAIL·67 → 100 | 비적용 분기 근거는 규칙 05·11 원문 인용 |
| java-architecture-reviewer | 0.2 → 0.3 | 83·92 → 100 | AUTO FAIL 절 제목에 HG-2 포함 |
| git-commit | 1.2 → 1.3 (하네스 신설) | 81.4 → 98.6 | 경로 최다가 범용 키워드면 기능 키워드 우선 |
| git-pr | 0.6 → 0.7 | AUTO FAIL → 98 | 맨 위 결론 블록 + share-lint 게이트 |
| sq-tone-writer | 1.4 → 1.5 | 30 → 97 | 불릿은 결과만, 첫 줄 반복 금지 |
| pr-feedback-resolver | 1.9 → 1.10 | 45 → 97 | Step 7 종료 보고 A 등급 |
| chat-incident-report | 1.0 → 1.1 | 40 → 94 | 첫 줄 장애 상태+반영 단계 (역수입전용, 실전 미배포) |
| error-log-report | 0.2 → 0.3 | 35 → 98 | 공유본 마지막 불릿 보고서 파일명 고정 |
| prd-designer | 1.2 → 1.3 | 60 → 90·100 | 출처 표기도 기획 용어로 |
| tdd-designer | 1.4 → 1.5 | 40 → 98 | "해당 없음" 채움을 확인한 사실 한 줄로 |
| eval-harness | 1.0 → 1.1 | - | 리포트 결론 블록 + share-lint --grade B |
| forge-deploy | 1.2 → 1.3 | 리허설 3곳 | 공용 자원 배포 판정, 배포 후 VC 실측 |
| 전역 스킬 4건 | google-chat-format·formal-doc-ko 1.1.0·cloud-run-health-check·pr-comment-ko 1.2.0 | share-lint 위반 3→0 등 | 백업 `~/.claude/skills-backup/2026-11-13-share-writing/` |

## 기계 검사 실측

- review-lint VC: 위반을 심은 샘플 17건 전부 검출, 규칙을 지킨 파일 0건. 실전 pasta 최근 30커밋 읽기 전용 실행에서 오탐 2종 발견·수정(주석 평서형 240줄 → 검사 제거, `@ConfigurationProperties` 의 `@Setter` 예외). 미추적 새 파일이 검사에서 빠지던 기존 결함 수정
- share-lint: 제안 글의 "지금 방식" 예시 위반 3건, "제안 방식" 예시 0건. 평가 중 `•` 불릿·서술형 빈 칸·존댓말 첫 줄·인용문 처리 보강
- 이번 사이클 리포트 13건 전부 share-lint --grade B 위반 0건

## 보충 재실행 (동시 서브에이전트 한도로 밀린 3건)

| 대상 | 이전 → 이번 | 비고 |
|------|-------------|------|
| prd-designer TC-4 (v1.3) | 90 → 100 | 기술 용어 0건, share-lint B 위반 0 |
| tdd-designer TC-1 회귀 (v1.5) | 100 → 100 | "해당 없음" 채움 0건, 회귀 없음 |
| formal-doc-ko (1.1.0) | share-lint 위반 1 → 0 | 결론 블록 6줄(3~5줄 기준 초과)은 남음 |

재실행에서 전역 스킬이 가리키던 share-lint 경로(forge 메인 체크아웃, dev 머지 전이라 파일 없음)가 비어 검사가 돌지 않던 것을 확인했다. `~/.claude/shared/` 에 사본을 두고 전역 CLAUDE.md·스킬 4건의 경로를 바꿨다(forge-deploy 공용 자원 표에 추가).

## 관찰

1. **프로젝트 규칙 문서가 실제 설정과 어긋나 있었다.** "Testcontainers 필수·H2 절대 금지"는 pasta-api·moneyball analysis 의 실제 H2 설정과 달랐다. 스킬이 문서를 그대로 따르면 잘못된 전환을 유도한다.
2. **조건부 표시가 기본 규칙까지 약하게 만든다.** java-spring-coder 초안에서 "(조직 컨벤션 조건부)" 표시가 붙은 줄을 비적용 프로젝트에서 "뒤집어도 되는 규칙"으로 읽었다.
3. **baseline 은 판정 지식이 있어도 사용자 요청 쪽으로 기운다.** coding-implementer·java-spring-coder TC 에서 baseline 은 가이드를 읽고 충돌을 알면서도 요청대로 `from()`·`feat:` 를 썼다. 우선순위 규칙이 차이를 만들었다.
4. **기계 검사는 실전 데이터로 돌려 봐야 쓸 만해진다.** 샘플로는 안 보이던 오탐(주석 240줄)이 실전 30커밋에서 나왔다.

## 미결 (사용자 결정 필요)

- forge 저장소 private 전환 (조직 컨벤션 가이드 요약이 public 에 올라감. 원문은 gitignore)
- PR #7 병합·항목 철회 시 `VC_CONV_REF` 갱신과 가이드 3절 정리. 이슈 키 위치 합의
- 공유 글 룰 월요일 팀 논의 후 v1.0 (현재 0.1 시범, 전역 CLAUDE.md 에도 반영됨)
- pasta 규칙 02·03·05·11 과 조직 컨벤션 충돌, 규칙 08 §3 H2 문구 — 프로젝트 소유 문서 정정 여부
- moneyball 미배포 스킬 참조 8건 (java-layered-unit-testing 등을 moneyball 에도 배포할지)
- java-spring-coder 747줄 (400줄 원칙 초과), Clock 주입 규칙(RR-2)
- 회귀 미실행 TC 다수와 `--repeat 3` (각 리포트 "확인된 것 vs 가정한 것")
