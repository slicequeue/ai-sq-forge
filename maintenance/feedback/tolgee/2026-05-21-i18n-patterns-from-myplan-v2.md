---
component: tolgee
source: pasta-japan-server
date: 2026-05-21
type: improvement
related_commits: 869c972f90, a1a425ecb2, ec3323a54a
severity: medium
---

## 증상

tolgee 스킬은 2026-05-19 forge로 역수입(v0.1)됐으나, 같은 주에 진행된 i18n 작업에서 발생한 사고·지적 사례 3건이 스킬에 반영되지 않았음. 사용자가 직접 forge-upstream 확인 단계에서 누락 지적.

### 사례 1. 4파일 동기화 (정상 패턴 — 박제 필요)

- **commit 869c972f90 (2026-05-15) feat: 마이플랜 v2 응답 조립 및 Facade·i18n 연동**
- v2 응답에 필요한 키 6종을 `message-shared.properties + _ko_KR + _en_US + _ja_JP` 4파일 모두에 동시 추가
- 24개 항목 동시 갱신이 정상이지만, 단일 파일 누락 사고는 운영 환경에서 자주 발생 (현재 운영에서는 어겨지지 않았지만 가드 없음)

### 사례 2. CodeRabbit 영문 카피 지적 (실제 누수)

- **commit a1a425ecb2 (2026-05-15) fix: CodeRabbit 리뷰 반영 — Locale·overflow·Web DTO 의존성·en 카피**
- `myplan.guide.meal.v2.description` 영문 카피가 단순 직역:
  - before: `Breakfast/lunch/dinner for {0} kcal daily target.`
  - after: `Breakfast/lunch/dinner for a daily target of {0} kcal.`
- placeholder 위치가 한국어 어순 그대로 → CodeRabbit 자동 리뷰가 자연어 개선 요청

### 사례 3. Locale.ROOT 누락 (자바 코드 측)

- 같은 commit a1a425ecb2에서 `MyPlanMealMenu.imagePath()`의 `toLowerCase()` 호출이 `Locale.ROOT` 명시 누락 → CodeRabbit "터키 locale 등 JVM 기본 Locale 의존 회피" 지적
- 후속 수정: `.toLowerCase(Locale.ROOT)` 명시
- tolgee 스킬은 i18n 책임자로서 properties뿐 아니라 자바 코드 측 Locale 함정도 안내해야 한다는 영역 확장 필요

## 수정 내용

PR 리뷰어(CodeRabbit + 휴먼)가 잡아 직접 수정. 자체 리뷰·코드 작성 단계에서 사전 차단 실패.

## 개선 제안 (tolgee v0.2 가드레일)

### A. 4파일 동시 갱신 강제 (Phase 1.1 신규)

- 신규 키 추가는 Edit 도구로 4파일 동시에 (한 응답에 4 호출). 단일 파일만 추가 금지.
- push 직전 자동 검증: `grep -l "^{키}=" message-shared*.properties` 결과가 정확히 4건인지 확인

### B. en 카피 품질 가드 (Phase 1.2 신규)

push 직전 en 카피만 별도 표로 사용자에게 제시. 점검 항목:
1. placeholder `{0}` 위치가 영어 어순(주어+동사+목적어)에 맞는가
2. 관사·소유격 적절한가
3. 단위 표현이 자연어인가

### C. 자바 코드 Locale 함정 안내 (Phase 4 신규)

tolgee 스킬은 i18n 책임자로서 자바 코드 측 4대 함정을 사용자에게 사전 안내:
1. `Locale.ROOT` 누락 (toLowerCase/toUpperCase)
2. `String.format` 로케일 의존 (내부 키·로그 용도)
3. MessageFormat placeholder는 위치 기반(`{0}`,`{1}`)만 사용
4. ja 카피는 줄바꿈 미사용 정책 — `\n` split 가정 금지

## 변경 파일 (참고)

- `shared/src/main/resources/messages/message-shared.properties` (+6키)
- `shared/src/main/resources/messages/message-shared_en_US.properties` (+6키 → 1키 카피 개선)
- `shared/src/main/resources/messages/message-shared_ja_JP.properties` (+6키)
- `myplan/.../MyPlanMealMenu.java` (Locale.ROOT 추가)

## 누적 검토

tolgee 영역 신규 피드백. 1건 누적이지만 다발성 (commit 2건 + 패턴 3종)이라 v0.2 즉시 강화 정당함.

## 연계 스킬

- `self-code-reviewer v1.8`: Locale.ROOT 누락 검출 룰 추가
- `java-spring-coder v1.8`: Locale.ROOT 강제 + 4파일 동기화 + placeholder 위치 기반
