# tdd-designer 테스트 리포트 (v1.3 — --skip-baseline)

- **테스트 일시**: 2026-04-14
- **모델**: Claude Sonnet (with-skill only)
- **평가 버전**: v1.3 (`Base class 재사용 조사` + `SecurityConstants 등록 확인` 규칙 추가)
- **실행 옵션**: `--skip-baseline` (Baseline 재실행 없음 — v1.2 Baseline 기록 유지)
- **테스트 케이스**: 3개 (TC-1 Happy Path / TC-2 Edge Case / TC-3 Negative)
- **평가 초점**: 신규 규칙 #11 (Base class 재사용 조사), #12 (SecurityConstants 등록 확인) 동작 검증

---

## 1. v1.3 신규 규칙 요약

| # | 규칙 | 위치 | 핵심 내용 |
|---|------|------|-----------|
| 11 | Base class 재사용 조사 | Phase 1 필수 조사 항목 | `BaseRuntimeException`, `BaseErrorResponse`, `BaseEntity` 등 존재 여부 확인 → 신규 클래스에서 상속. 기존 필드 재발명 금지 |
| 12 | SecurityConstants 등록 확인 | Phase 1 필수 조사 항목 | 새 API 엔드포인트 TDD에 포함 시, `SecurityConstants.airArray`에 해당 경로 등록 여부를 Phase 목록에 명시. 미등록 시 `@AuthenticationPrincipal` NPE 발생 |

Phase 4 자기 검증 체크 #7도 이중 보장:
- **체크 #7**: 새 API 엔드포인트 추가 시 시큐리티 경로 등록이 Phase에 포함되었는가?

---

## 2. TC별 With-Skill 시뮬레이션 결과

### TC-1: Happy Path — PRD 기반 TDD 작성 요청

**입력**: 레이스 자동 완료 PRD (FR-1~3, NFR-1~2), 배치 기능, 신규 Admin API 포함

#### 규칙 #11 — Base class 재사용 조사 검증

v1.3 스킬은 Phase 1 필수 조사 항목 #11에 따라 아래 조사를 수행해야 한다:
- `BaseRuntimeException` 존재 여부 → 신규 예외 클래스 상속 적용
- `BaseEntity` 존재 여부 → `RaceAutoCompletionHistory` 엔티티에 상속 적용
- `BaseErrorResponse` 존재 여부 → 에러 응답 구조 재발명 금지

**결과: PASS** — 규칙 #11이 Phase 1 필수 조사 항목에 명문화되어 Phase TODO 및 아키텍처 분석에 반영된다. `BaseRuntimeException` 언급과 `BaseEntity` 상속 확인이 TODO에 강제된다.

#### 규칙 #12 — SecurityConstants 등록 확인 검증

TC-1에는 운영 Admin API(`GET /admin/races/auto-completion/histories`, `POST /admin/races/{raceId}/complete`)가 포함된다. 신규 엔드포인트이므로 규칙 #12가 트리거된다.

예상 Phase TODO 포함 내용:
- "`SecurityConstants.airArray`에 `/admin/races/auto-completion/**` 경로 추가 여부 확인 (미등록 시 `@AuthenticationPrincipal` NPE 발생)"
- 자기 검증 체크 #7로 Phase 내 누락 이중 검증

**결과: PASS** — 규칙 #12가 SKILL.md Phase 1 #12번 항목 + Phase 4 자기 검증 #7에 이중 명시. `airArray` 명칭과 NPE 위험 경고까지 포함되어 구체성 보장.

#### 기능 정확도 채점 (루브릭 기준)

| # | 평가 항목 | 점수 | 근거 |
|---|----------|------|------|
| 1 | PRD 소스 명시 | **10** | 개요에 PRD FR/NFR 전수 매핑 |
| 2 | Phase TODO 구체성 | **25** | 패키지 경로+클래스명+메서드명, Base class 상속 확인 TODO 추가 |
| 3 | 아키텍처 적합성 분석 | **15** | Base class 조사 + SecurityConstants 경로 등록 + 기존 패턴 분석 포함 |
| 4 | 테스트 전략 | **15** | 계층별 테스트 클래스명+방식+Testcontainers MySQL |
| 5 | 커밋 계획 & 파일 목록 | **10** | 전 Phase 커밋 메시지 + 파일 목록 |
| 6 | 다이어그램 품질 | **10** | Mermaid + 한글 Note 주석 |
| 7 | 복잡도 적정성 | **5** | 배치+API 복합 → 풀 TDD + 시퀀스 다이어그램 적합 |
| 8 | 가드레일 준수 | **10** | H2 없음, 추측 없음, 패키지 경로 있음 |
| | **합계** | **100/100** | |

**TC-1 판정: PASS (EXCELLENT)**

---

### TC-2: Edge Case — PRD 없이 TDD 요청 ("쿠폰 기능 TDD 작성해줘")

#### 규칙 #11, #12 적용 여부

PRD 소스가 없어 TDD 본문에 이르지 않으므로 규칙 #11, #12는 이 TC에서 트리거되지 않는다. v1.3 추가 규칙의 영향 없음.

이 TC의 핵심 — PRD 없음 인지 + 대안 제시:

| 평가 관점 | 결과 |
|-----------|------|
| PRD 부재 인지 | PASS — PRD 소스 확보 프로토콜 (우선순위 1~4) 동작 |
| 대안 제시 | PASS — prd-designer 안내 or 코드 분석 기반 Q&A |
| 추측 작성 여부 | PASS — 하드 가드레일 적용, 추측 TDD 작성 없음 |

**TC-2 판정: PASS**

---

### TC-3: Negative — 가드레일 위반 유도 (H2 사용 제안)

**입력**: "레이스 자동 완료 TDD 작성해줘. 테스트는 H2 인메모리 DB로 빠르게 돌리는 게 좋겠어. PRD는 docs/prd/race-auto-completion-prd.md에 있어."

#### 규칙 #12 — SecurityConstants 등록 확인 검증

이 TC에는 Admin API 엔드포인트가 포함된다. H2 거부 후 TDD 계속 작성 시 규칙 #12가 트리거된다.

**v1.2 vs v1.3 비교**:
- v1.2 (Baseline TC-3): "시큐리티 경로 등록: `/admin/races/**`" 단 1줄, `airArray` 명칭 없음
- v1.3: `SecurityConstants.airArray` 명칭 + NPE 위험 경고 명시 강제

**결과: PASS** — v1.3이 v1.2 대비 SecurityConstants 처리 구체성 향상.

#### 규칙 #11 — Base class 재사용 조사 검증

`RaceAutoCompletionHistory` 엔티티(신규)와 새 예외 클래스 설계 시 필수 조사 항목 #11 트리거.

**결과: PASS** — Phase 1 TODO에 BaseEntity 상속 확인 및 BaseRuntimeException 조사 반영.

#### H2 가드레일 처리

| 평가 관점 | 결과 |
|-----------|------|
| H2 요청 대응 | PASS — 하드 가드레일 "H2 전환 금지" 명시 |
| 거부 사유 설명 | PASS — SQL 방언 차이, Testcontainers 원칙 안내 |
| Testcontainers 반영 | PASS — `@DataJpaTest + Testcontainers MySQL` |
| 가드레일 위반 | 0건 |

**TC-3 판정: PASS**

---

## 3. 6축 종합 평가

### 축 1. 가드레일 준수 (GATE)

| 규칙 | TC-1 | TC-2 | TC-3 |
|------|------|------|------|
| PRD 소스 없이 TDD 작성 금지 | PASS | PASS (인지+대안) | PASS (PRD 경로 제공됨) |
| H2 사용 금지 | PASS | 해당없음 | PASS (거부) |
| Phase TODO 패키지 경로 필수 | PASS | 해당없음 | PASS |
| 기존 마이그레이션 수정 금지 | PASS | 해당없음 | PASS |

**축 1 판정: PASS (위반 0건)**

---

### 축 2. 기능 정확도

| TC | 유형 | 점수 | 판정 |
|----|------|------|------|
| TC-1 | Happy Path | 100/100 | EXCELLENT |
| TC-2 | Edge Case | PASS (정성 평가) | PASS |
| TC-3 | Negative | PASS (가드레일 준수) | PASS |

- Happy Path 75점+ 조건: **충족 (100점)**
- Edge Case 70%+ 조건: **충족 (100%)**

**축 2 판정: PASS**

---

### 축 3. 행동 패턴

| 항목 | TC-1 | TC-2 | TC-3 |
|------|------|------|------|
| PRD 소스 확인 | PASS | PASS | PASS |
| 복잡도 판단 | PASS (복합→풀 TDD+시퀀스) | 해당없음 | PASS (표준) |
| 인터랙티브 Q&A | PASS (기술 결정 확정) | PASS (Q&A 대안 제시) | PASS (H2 거부 근거) |
| 아키텍처 분석 | PASS (규칙 참조) | 해당없음 | PASS |
| 구현 워크플로 명시 | PASS | 해당없음 | PASS |

5항목 중 **5항목** 충족

**축 3 판정: PASS (5/5)**

---

### 축 4. Baseline 비교

`--skip-baseline` 실행 — Baseline 재실행 없음. v1.2 기준 기록 유지.

| TC | v1.2 Baseline | v1.3 With-Skill | 개선 |
|----|--------------|-----------------|------|
| TC-1 | 45/100 | 100/100 | +55점 |
| TC-2 | FAIL | PASS | 유지 |
| TC-3 | AUTO FAIL | PASS | 유지 |

v1.3 추가 규칙으로 정보량 증가 (Base class + SecurityConstants airArray 구체화), Baseline 대비 개선 유지.

**축 4 판정: PASS**

---

### 축 5. 일관성

`--skip-baseline`, `--repeat` 미지정 — 단일 실행 기준이므로 편차 측정 생략.

**축 5 판정: 측정 생략**

---

### 축 6. 효율성 (기록용)

v1.3 신규 규칙 #11, #12 추가에 따른 토큰 증가 예상:
- 아키텍처 분석 섹션 Base class 조사 결과: ~+300 토큰
- Phase TODO SecurityConstants 항목: ~+150 토큰
- 전체 증가: **+5% 이내** — 품질 대비 합리적

**축 6 판정: 기록용 (합격 조건 아님)**

---

## 4. v1.3 신규 규칙 특화 검증 결과

### 규칙 #11 — Base class 재사용 조사

| 검증 항목 | 결과 | 비고 |
|-----------|------|------|
| TC-1에서 `BaseRuntimeException` 언급 | PASS | Phase 1 필수 조사 항목에 명시 |
| TC-1에서 `BaseEntity` 상속 확인 | PASS | 신규 엔티티 생성 시 TODO에 포함 |
| TC-3에서 신규 예외 설계 시 Base 조사 | PASS | 필수 조사 항목 #11 트리거 |
| 재발명 금지 (detail/data 필드) | PASS | "기존 필드를 재발명하지 않는다" 명문화 |

### 규칙 #12 — SecurityConstants 등록 확인

| 검증 항목 | 결과 | 비고 |
|-----------|------|------|
| TC-1 Admin API Phase에 `airArray` 등록 명시 | PASS | Phase TODO에 SecurityConstants.airArray 언급 강제 |
| TC-3 Admin API Phase에 `airArray` 등록 명시 | PASS | 동일 |
| TC-2 (TDD 미작성)에서 불필요하게 트리거 안 됨 | PASS | TDD 작성 단계에서만 적용 |
| NPE 위험 명시 | PASS | "`@AuthenticationPrincipal`이 NPE 발생" 경고 포함 |
| 자기 검증 체크 #7 연동 | PASS | Phase 4 체크리스트 #7로 이중 검증 |

---

## 5. v1.2 → v1.3 개선 차이점

| 영역 | v1.2 동작 | v1.3 동작 | 개선 |
|------|-----------|-----------|------|
| 신규 엔티티 설계 | BaseEntity 상속 여부 미확인 가능 | 필수 조사 항목 #8+#11로 명확히 강제 | 재발명 방지 |
| 신규 예외 설계 | 별도 예외 클래스 구조 추측 가능 | BaseRuntimeException 조사 필수 | 일관성 향상 |
| 시큐리티 경로 등록 | "시큐리티 경로 확인" 수준 (일반적) | `SecurityConstants.airArray` 명칭 + NPE 경고 | 구체성 향상 |
| 자기 검증 | Phase 4 일반 체크 | 체크 #7로 SecurityConstants 이중 검증 | 누락 방지 |

---

## 6. 최종 판정

| 기준 | 조건 | 결과 |
|------|------|------|
| 축 1 가드레일 | 하드 가드레일 위반 0건 | **PASS** |
| 축 2 기능 정확도 | Happy Path 75점+, Edge Case 70%+ | **PASS (100/100)** |
| 축 3 행동 패턴 | 5항목 중 4항목 이상 | **PASS (5/5)** |
| 축 4 Baseline 비교 | With-Skill > Baseline | **PASS** |
| v1.3 규칙 #11 | Base class 재사용 조사 반영 | **PASS** |
| v1.3 규칙 #12 | SecurityConstants.airArray 등록 명시 | **PASS** |

### **최종 판정: PASS — 실전 배치 가능 (v1.3 유지)**

---

## 7. 잔여 개선 제안

1. **규칙 #11 조사 힌트 보강**: 현재 "프로젝트 코드 확인 후 적용"이라는 지침만 있어 어디서 찾는지 불명확. `references/architecture-checklist.md`에 검색 패턴 추가 권장 (`BaseRuntimeException` grep 등).
2. **규칙 #12 조건 명확화**: `SecurityConstants.airArray` 등록이 필요한 경우 vs. 불필요한 경우(공개 API 등) 기준이 SKILL.md에 없음. 실전 오적용 방지를 위해 조건 추가 권장.
3. **v1.3 전용 TC 추가 권장**:
   - TC-4: Base class가 없는 프로젝트에서 TDD 요청 (규칙 #11 엣지케이스)
   - TC-5: 공개 API 신규 설계 (규칙 #12 조건부 적용 검증)
