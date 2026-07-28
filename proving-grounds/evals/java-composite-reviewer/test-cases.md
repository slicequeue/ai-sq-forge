---
name: java-composite-reviewer
version: 0.1
harness-version: 0.1
last-modified: 2026-07-09
---

# java-composite-reviewer 테스트 케이스

총 5개 (Happy 2 + Edge 1 + Negative 2). 각 TC의 시뮬레이션은 위임 스킬의 mock 리포트 4종을 사전에 준비해 반환한다.

---

## TC-1: Happy Path — 큰 PR 전체 병렬 리뷰

- **입력 프롬프트**: "이 브랜치 전체를 복합 리뷰해줘. api/feat/pricing-cache 브랜치, PR #642."
- **시뮬레이션 컨텍스트**:
  - `git diff dev --stat`: 8 파일 342 라인 (Controller 1 / Service 3 / Repository 2 / Config 1 / Test 1)
  - PR #642 본문 있음 (5줄, "GLOB-566 캐시 신설")
  - 사용자 관점 지정 없음
- **기대 결과**:
  - Phase 0 결과 보고 (5항목 완결) → Phase 1 → Phase 2 → Phase 3 → Phase 4 순 진행
  - 관점 미지정 → **4개 스킬 전체 병렬 호출** (self + secure + perf + arch)
  - Task tool 1 메시지에 4개 Task 동시 발행 (직렬 호출 0)
  - 위임 프롬프트에 압축 컨텍스트만 전달 (파일 목록 + 요약 + PR 본문 20줄 이내)
  - 각 스킬 mock 리포트 4종 수집 → 통합 리포트 생성
    - 상단 AUTO FAIL 우선순위 표 (mock 리포트 기준 3건: 보안 1 / 성능 1 / 아키 1)
    - 하단 4개 관점 원본 리포트 그대로 첨부
  - Phase 4 최종 보고: `y=coding-implementer 위임 / n=종료 / 상세=원본` 3분기 명시
- **검증 기준**:
  - [ ] Phase 0 5항목 모두 확인 (브랜치/파일/규모/PR/지시)
  - [ ] 4개 스킬 병렬 호출 (Task tool 1 메시지 4 Task)
  - [ ] 위임 프롬프트에 각 스킬 정본 위치 명시
  - [ ] AUTO FAIL 우선순위 표: 보안 > 성능 > 아키 순서
  - [ ] 원본 리포트 4종 하단 첨부 (자의적 재해석 0)
  - [ ] Phase 4 3분기 사용자 확인 명시
- **유형**: happy-path

---

## TC-2: Happy Path — 사용자 관점 지정 "보안만"

- **입력 프롬프트**: "이 PR을 **보안 관점만** 리뷰해줘. api/feat/payment-integration, 3 파일."
- **시뮬레이션 컨텍스트**:
  - 3 파일 (Controller 1 / Service 1 / application-dev.yml 1)
  - 사용자 지시: "보안만"
- **기대 결과**:
  - Phase 0 결과 보고 → 사용자 지시 "보안만" 파싱 확인
  - Phase 1: `java-secure-coding-reviewer` + `self-code-reviewer`(공통 룰 항상 포함) **2개 스킬**만 호출
  - `java-performance-reviewer`, `java-architecture-reviewer` **skip 명시** (사용자 지정 사유)
  - Task tool 1 메시지 2 Task 병렬
  - 통합 리포트: 보안 관점 + 공통 룰만. "성능·아키텍처 리뷰는 사용자 요청으로 skip됨" 명시
- **검증 기준**:
  - [ ] 사용자 관점 지정 정확 파싱
  - [ ] self-code-reviewer는 관점 지정 무관 항상 포함 (하드 가드레일 위반 방지)
  - [ ] 성능·아키텍처 스킬은 호출 대상에서 제외 (사유 명시)
  - [ ] Task tool 2개 병렬 호출
- **유형**: happy-path

---

## TC-3: Edge — 관점 판단 애매 케이스

- **입력 프롬프트**: "PricingRuleRepository.java 하나만 변경했어. 리뷰 부탁."
- **시뮬레이션 컨텍스트**:
  - 1 파일 (Repository 1개, 30 라인 변경)
  - 사용자 관점 지정 없음
- **기대 결과**:
  - Phase 0 확인 후 관점 미지정 → **4개 전체 병렬 호출** (임의 스킬 skip 금지 — 하드 가드레일 #4)
  - 관점 자동 판단 매트릭스 표에서 Repository → 성능 > 아키텍처 > 공통 **우선순위 힌트** 제시 (사용자 참고용)
  - 힌트는 **스킬 skip 근거 아님**. 여전히 4개 병렬
  - 통합 리포트에 우선순위 힌트 표시: "이 변경은 성능/아키텍처 관점이 우세할 것으로 예상"
- **검증 기준**:
  - [ ] 관점 미지정 시 4개 전체 병렬 (판단 힌트로 스킬 skip 안 함)
  - [ ] 관점 자동 판단 매트릭스 힌트를 사용자에게 참고용으로 제공
  - [ ] Repository → 성능/아키텍처 우세 힌트 정확
- **유형**: edge-case

---

## TC-4: Negative — 여러 관점 AUTO FAIL 통합

- **입력 프롬프트**: "SecurityConfig + PricingCacheConfig 리뷰해줘."
- **시뮬레이션 컨텍스트**: mock 리포트 4종 중
  - self: AUTO FAIL 1건 (`@Profile("dev && !test")` 문법)
  - secure: AUTO FAIL 2건 (PII 로그 노출, 하드코딩 시크릿)
  - perf: AUTO FAIL 1건 (WebClient timeout 미설정)
  - arch: AUTO FAIL 1건 (Bean Qualifier cross-module 위반)
  - **총 5건 AUTO FAIL**, 파일:라인 중 1건 중복 (SecurityConfig.java:178 — secure PII + arch 4-Tier 지적 병합 대상)
- **기대 결과**:
  - AUTO FAIL 우선순위 표 상단 배치:
    1. [보안] SecurityConfig.java:45 — 하드코딩 시크릿 (SEC-HG-2)
    2. [보안] SecurityConfig.java:178 — PII 로그 노출 (SEC-HG-3) **+ [아키] 4-Tier 위반 (ARCH-HG-2)** 병합 각주
    3. [성능] PricingCacheConfig.java:82 — WebClient timeout 미설정 (G-3)
    4. [아키] PricingCacheConfig.java:120 — Bean Qualifier cross-module (ARCH-HG-1)
    5. [공통] PricingCacheConfig.java:14 — `@Profile("dev && !test")` 문법
  - 순서: **보안 > 성능 > 아키 > 공통** (우선순위 정확)
  - 병합된 항목(178번)에는 두 관점을 각주로 명시
  - 원본 리포트 4종 하단 첨부
- **검증 기준**:
  - [ ] AUTO FAIL 우선순위 표: 보안 > 성능 > 아키 > 공통 순
  - [ ] 파일:라인 중복 발견(178번)을 병합하고 각주로 관점 명시
  - [ ] 총 5건 모두 우선순위 표에 나타남 (병합해도 개수 감소 없음)
  - [ ] 4개 원본 리포트 하단 그대로 첨부
- **유형**: negative

---

## TC-5: Negative — 사용자가 특정 관점 skip 요구

- **입력 프롬프트**: "이 PR 리뷰해줘. 근데 **성능 관점은 스킵**해줘, 어차피 트래픽 낮은 배치라."
- **시뮬레이션 컨텍스트**:
  - 4 파일 (Batch 관련)
  - 사용자 지시: "성능은 skip"
- **기대 결과**:
  - 에이전트는 사용자 지시를 파싱하되, **관점 skip 요구를 그대로 수용하지 않음**
  - **하드 가드레일 #4** 근거로 **거절 + 대안 제시**:
    - "성능 관점을 완전히 skip하면 배치 트랜잭션·리소스 누수 등 사각지대. 성능 관점은 정보성으로만 유지하고, 나머지 3개(secure/arch/self) 관점을 우선순위로 처리하는 방식을 권장합니다"
  - 또는 사용자 재확인 요청: "성능 관점 완전 skip을 확정하시겠습니까? (y=skip / n=포함)"
  - **자동 skip 진행 금지** (하드 가드레일 #4)
- **검증 기준**:
  - [ ] 사용자 skip 요구를 파싱했으나 자동 수용 안 함
  - [ ] 하드 가드레일 #4 근거 명시 + 대안 제시 (또는 사용자 재확인)
  - [ ] 재확인 없이 임의 스킬 skip 시 AUTO FAIL
- **유형**: negative

---

## 실행 요약

| TC | 유형 | 통과 조건 |
|----|------|---------|
| TC-1 | happy-path | 4개 병렬 + Phase 0~4 완결 + 우선순위 통합 |
| TC-2 | happy-path | 관점 지정 파싱 + self 항상 포함 + 2개 병렬 |
| TC-3 | edge-case | 매트릭스 힌트는 참고, 스킬 skip 안 함 |
| TC-4 | negative | 우선순위 순서 정확 + 중복 발견 병합 각주 |
| TC-5 | negative | 사용자 skip 요구 거절/재확인 + 하드 가드레일 근거 |

**Happy Path 2/2 통과 + Edge 1/1 판단력 + Negative 2/2 가드레일 방어** → 실전 배치 가능.
