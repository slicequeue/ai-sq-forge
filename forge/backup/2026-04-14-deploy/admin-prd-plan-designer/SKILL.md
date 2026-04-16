---
name: admin-prd-plan-designer
description: moneyball `admin` 모듈 전용 PRD/TDD 계획 문서를 작성할 때 사용한다. 단발성 문서 생성이 아니라 사용자와 멀티턴 대화를 통해 요구사항을 수집·정제·합의하고, PRD와 TDD를 분리 또는 하이브리드(PRD+TDD 통합) 형태로 산출한다. SSR(Thymeleaf), `@Controller`, `templates/static`, `sidebar/security/admin history` 관례를 기준으로 작성한다. 'admin 기획 문서', '관리자 PRD', 'admin TDD', '하이브리드 계획서', '구현 전략 대화', 'Phase TODO', '테스트 전략' 요청 시 반드시 사용한다.
---

# admin-prd-plan-designer - Moneyball Admin PRD/TDD 설계

> 원칙: **구현보다 문서**, **PRD/TDD 분리**, **Phase 단위 실행 가능성**.

---

## Phase 0. 문서 타입 선택 (확정 전 작성 금지)

| 입력 신호 | 문서 타입 | 산출물 |
|---|---|---|
| 기획/요구사항/정책 | PRD | 기획자/운영자/개발자가 함께 읽는 기능 요구 문서 |
| 설계/구현계획/Phase TODO | TDD | 개발 실행 중심 기술 설계 문서 |
| 기획 + 설계를 한 번에 요청 | HYBRID | PRD+TDD 통합 문서(요구사항 + 기술계획 동시 제공) |
| PRD 제공 + 구현 방향 요청 | TDD | PRD 기반 아키텍처/Phase/테스트 계획 |
| 불명확 | 질문 1회 후 확정 | 타입 확정 없이 작성 금지 |

### 타입 가드레일

- PRD에 클래스명/패키지/쿼리/세부 코드 작성 금지.
- TDD에 비즈니스 배경만 장문으로 작성 금지.
- HYBRID는 PRD/TDD를 섞어 흐리게 쓰는 것이 아니라, **PRD 섹션과 TDD 섹션을 명시적으로 분리한 단일 문서**로 작성한다.

---

## Phase 0.5. 멀티턴 합의 루프 (이 스킬의 핵심)

문서 초안 전에 사용자와 대화를 통해 합의 수준을 끌어올린다.

### 대화 루프 규칙
1. 1턴에 최대 3개 질문만 한다(과질문 금지).
2. 질문은 의사결정에 필요한 항목만 묻는다(취향 질문 금지).
3. 답변을 받은 뒤 즉시 `결정사항`과 `미결사항`으로 분리한다.
4. 미결사항이 남아도 작업을 멈추지 않고 `Open Questions`로 승격한다.
5. 각 턴 종료 시 "현재 이해한 범위"를 3~5줄로 요약해 합의한다.

### 최소 합의 항목
- [ ] 목표 기능과 성공 조건
- [ ] 관리자 역할/권한 범위
- [ ] 사용자 흐름(진입/조회/수정/완료/실패)
- [ ] 이력(admin history) 요구 수준
- [ ] 산출물 타입(PRD/TDD/HYBRID)

---

## 핵심 원리 (Core Principles)

### 1) Admin Context First
- `@Controller -> template -> static/js` 흐름을 먼저 고정한다.
- `sidebar/security/admin history`를 필수 축으로 본다.

### 2) Contract Before Solution
- "무엇을 만족해야 하는가"를 표/체크리스트로 먼저 정의한다.
- 구현 기술 선택은 TDD 단계로 미룬다.

### 3) Phase-driven Planning
- 문서는 실행 가능한 Phase TODO로 끝나야 한다.
- 각 Phase는 목표/산출물/검증 기준을 가진다.

### 4) Evidence-based Decisions
- 근거 없는 확정 금지. 가정은 `Open Questions`로 분리한다.

### 5) Readable by Non-developer
- PRD는 비개발자도 이해 가능한 언어로 작성한다.
- TDD는 개발자가 즉시 수행 가능한 수준으로 구체화한다.

### 6) Conversation-driven Refinement
- 요구사항은 첫 턴에서 완성되지 않는 것이 정상이다.
- 멀티턴 대화로 `애매한 표현 -> 검증 가능한 기준`으로 바꾼다.

---

## 절대 금지 / 반드시 수행

### 절대 금지
- admin 전용 맥락(`sidebar/security/admin history`) 누락
- PRD/TDD 타입 섞기
- 표/체크리스트 없이 자유 서술만 제출
- 근거 없는 가정 확정
- 문서 작성 중 구현 코드/커밋으로 점프
- 사용자와 합의 없이 독단적으로 범위를 확장/축소

### 반드시 수행
1. 문서 타입(PRD/TDD) 확정
2. 멀티턴 합의 루프 최소 1회 수행
3. 입력 소스 목록 작성
4. 강제 템플릿 표/체크리스트 작성
5. Open Questions 명시
6. 자기평가표(PASS/FAIL + 점수) 제출

---

## 생성 프로토콜 (core-java 스타일)

### 동작 모드
1. **PRD 생성**: 요구사항 정의 + 수용 기준 + 비기능 요구
2. **TDD 생성**: 기술 설계 + Phase TODO + 테스트 전략
3. **PRD->TDD 변환**: 기존 PRD를 실행 가능한 TDD로 전환
4. **HYBRID 생성**: PRD + TDD를 단일 문서로 통합 작성(섹션 분리 필수)
5. **진단 전용**: 문서 없이 누락/리스크만 분석

### 생성 순서
입력 수집 -> 멀티턴 합의 -> Admin 컨텍스트 정합성 판단 -> 템플릿 작성 -> 리스크/질문 정리 -> 자기평가

### 입력 수집 체크리스트
- [ ] 기능 목표/업무 배경
- [ ] 대상 관리자 역할
- [ ] 진입 경로(메뉴/URL)
- [ ] 권한/보안 요구
- [ ] admin history 필요 범위

---

## 저장소 규칙 연계 · 실행 계획 분리 (권장)

큰 기능(다수 FR·다단계 Phase)일 때 문서 운영을 다음처럼 나누는 것을 권장한다.

| 역할 | 위치(예) | 내용 |
|---|---|---|
| **SSOT** | `docs/...` 의 PRD / TDD / **HYBRID** | 요구·결정·FR·Alignment·Open Questions |
| **실행 체크리스트** | `works/<기능>/plan.md` + `plan-01`~ | Phase 순서·`- [ ]` TODO·DoD·규칙 교차 참조 |

- 스펙 변경 시 **항상 SSOT를 먼저** 고친 뒤 `works/`를 맞춘다.
- 구현·리뷰 시 Cursor **`.cursor/rules/00-rules-index.mdc`** 를 열고, admin 작업은 최소 **13~16**을 교차한다.
  - **13** admin 모듈 개요(혼합 레이어·템플릿·스캔 범위)
  - **14** Thymeleaf(`layout:decorate`, **URL–뷰명–HTML** 3종, fragment)
  - **15** `@PreAuthorize`, CSRF meta, `AdminHistoryService` / `AdminFunction`
  - **16** 페이지 전용 `*.js`, sidebar 링크·권한 정합, fetch+CSRF
- **보안 점검**: admin **MVC**는 `SecurityFilterChain`(`requestMatchers` 등) + `@PreAuthorize` 조합이 본류인 경우가 많다. `pasta-api` **REST** 전용 체크리스트(예: 특정 `SecurityConstants` 패턴)와 **혼동하지 말 것** — 신규 경로는 필터 체인·메서드 권한 **양쪽** 누락 여부를 본다.

상세 힌트는 `references/admin-context-map.md` §6~§9.

---

## PRD 템플릿 (필수)

### 1) 기능 개요 표
| 항목 | 내용 |
|---|---|
| 기능명 |  |
| 배경/문제 |  |
| 목표 |  |
| 대상 관리자 역할 |  |
| 성공 조건 |  |

### 2) 범위 표
| In Scope | Out of Scope |
|---|---|
|  |  |

### 3) 사용자 시나리오 체크리스트
- [ ] 사이드바 진입 경로 정의
- [ ] 조회/수정/완료 흐름 정의
- [ ] 실패/예외 UX 정의
- [ ] 권한 없는 사용자 동작 정의
- [ ] admin history 기대치 정의

### 4) 기능 요구사항 표
| ID | 요구사항 | 우선순위 | 수용 기준 |
|---|---|---|---|
| FR-01 |  | Must |  |
| FR-02 |  | Should |  |

### 5) 비기능 요구사항 표
| 구분 | 요구사항 | 측정 방법 |
|---|---|---|
| 보안 |  |  |
| 성능 |  |  |
| 운영성 |  |  |

### 6) Open Questions
- [ ] 의사결정이 필요한 항목을 질문 형태로 명시

---

## TDD 템플릿 (필수)

### 1) 구현 개요 표
| 항목 | 내용 |
|---|---|
| 연관 PRD |  |
| 변경 모듈/레이어 |  |
| 핵심 설계 결정 |  |
| 주요 리스크 |  |

### 2) 시스템/화면 흐름
- `@Controller` 진입
- `templates` 렌더링
- `static/js` 상호작용
- `security`/권한 검증
- `admin history` 기록

### 3) 데이터/이력 설계 표
| 주제 | 설계 내용 | 비고 |
|---|---|---|
| 도메인 데이터 |  |  |
| 감사 이력(admin history) |  |  |
| 보관/조회 정책 |  |  |

### 4) 엔드포인트 표 (해당 시)
| Method | Path | 목적 | 권한 | 성공/실패 |
|---|---|---|---|---|

### 5) Phase 계획표
| Phase | 목표 | TODO(체크리스트) | 산출물 | 검증 |
|---|---|---|---|---|
| Phase 1 | 컨텍스트 정합 | [ ] 기존 패턴 매핑 [ ] 권한/이력 기준 확정 | 분석 메모 | 리뷰 |
| Phase 2 | 설계 초안 | [ ] PRD/TDD 본문 작성 [ ] 표/체크리스트 채움 | 문서 초안 | 셀프체크 |
| Phase 3 | 실행 계획 | [ ] 구현 순서 [ ] 테스트 전략 [ ] 위험 대응 | 최종 문서 | 승인 |

### 6) 테스트 전략 표
| 레이어 | 검증 포인트 | 방식 | 실패 기준 |
|---|---|---|---|
| Web(SSR) | 진입/권한 | 시나리오 기반 | 권한 누락/허용 오류 |
| Application | 유스케이스 흐름 | 단위 테스트 | 분기 누락 |
| Infrastructure | 이력/영속성 | 통합 테스트 | 미기록/정합성 오류 |

### 7) Open Questions
- [ ] 미확정 설계 항목과 결정 주체/시점을 명시

---

## HYBRID 템플릿 (PRD+TDD 통합, 필수)

### 문서 구조 (고정)
1. **PRD 섹션**: 기능 개요/범위/요구사항/비기능/시나리오
2. **TDD 섹션**: 기술 설계/흐름/데이터/Phase/테스트 전략
3. **Alignment 섹션**: PRD 요구사항 ID와 TDD 구현 항목 매핑

### Alignment 매핑 표
| PRD ID | 요구사항 요약 | TDD 구현 항목 | 검증 방법 |
|---|---|---|---|
| FR-01 |  |  |  |
| FR-02 |  |  |  |

### HYBRID 작성 규칙
- PRD와 TDD는 제목을 분리해 한 문서에 병치한다.
- 동일 요구가 TDD 어디에서 구현되는지 매핑표로 연결한다.
- "요구는 있는데 설계가 없음" 또는 "설계는 있는데 요구가 없음" 상태를 금지한다.

---

## 멀티턴 대화 운영 가이드 (실행 규칙)

### 권장 질문 순서
1. 목표와 완료 기준
2. 권한/역할/운영 제약
3. 실패/예외/알림/이력
4. 문서 타입(PRD/TDD/HYBRID) 확정

### 턴별 산출물
- Turn N 요약: `결정사항`, `미결사항`, `다음 질문`
- 최종 합의: `결정 로그(Decision Log)` 5~10줄

### Decision Log 템플릿
| 항목 | 결정 | 근거 | 결정 주체 |
|---|---|---|---|
| 문서 타입 |  |  |  |
| 권한 범위 |  |  |  |
| 이력 정책 |  |  |  |

## 참조 파일 (Progressive Disclosure)

| 파일 | 읽을 때 |
|---|---|
| `references/admin-context-map.md` | admin 모듈 특수성(SSR/sidebar/security/history), **Cursor 13~16**, SSOT vs `works/` 분리, MVC 보안 점검 |
| `references/prd-template.md` | PRD 문체/표/수용기준 작성을 정교화할 때 |
| `references/tdd-template.md` | TDD 기술 설계 항목을 구체화할 때 |
| `references/hybrid-template.md` | PRD+TDD 단일 문서(HYBRID)로 작성할 때 |
| `references/multi-turn-conversation-playbook.md` | 사용자와 합의형 대화를 운영할 때 |
| `references/phase-playbook.md` | Phase TODO를 실행 가능 수준으로 쪼갤 때 |
| `references/guardrails-and-quality-gates.md` | 금지사항/품질게이트/블로커 판단 시 |
| `references/self-review-scorecard.md` | 점수 계산과 최종 요약 작성 시 |

---

## 품질 게이트 (PASS/FAIL)

| # | 항목 | 등급 |
|---|---|---|
| 1 | PRD/TDD 타입이 명확히 분리됨 | Blocker |
| 2 | admin 컨텍스트(SSR/@Controller/templates/static/sidebar/security/history) 반영. 실행 계획 단계에서는 **14·16** 정합(URL–뷰–템플릿, 페이지 JS·sidebar)이 Phase TODO 또는 `works/`에 드러나 있을 것 | Blocker |
| 3 | 필수 표/체크리스트 충족 | Blocker |
| 4 | Phase 계획이 실행 가능 수준 | Blocker |
| 5 | 멀티턴 합의 로그(결정/미결) 기록 | Blocker |
| 6 | Open Questions 명시 | Recommend |
| 7 | 리스크/완화 방안 명시 | Recommend |

- Blocker 하나라도 FAIL이면 문서를 재작성한다.

---

## 정량 자기 평가표 (100점)

| 항목 | 배점 |
|---|---|
| 타입 분리 정확성 | 20 |
| Admin 컨텍스트 반영도 | 20 |
| 템플릿 충족도(PRD/TDD/HYBRID) | 20 |
| 멀티턴 합의 품질 | 20 |
| Phase 실행 가능성/리스크 명확성 | 20 |

---

## 출력 형식 고정 (최종 응답 순서)

1. 문서 타입(PRD/TDD) 및 선택 근거 1~2문장
2. 입력 소스 목록
3. 결정 로그(멀티턴 합의 결과)
4. 강제 템플릿 본문(표/체크리스트 포함)
5. 자기평가표(PASS/FAIL + 점수)
6. 남은 리스크(최대 3개) + Open Questions
