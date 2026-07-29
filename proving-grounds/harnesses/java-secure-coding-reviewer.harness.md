---
name: java-secure-coding-reviewer
version: 0.1
harness-version: 0.2
last-modified: 2026-07-29
---

# java-secure-coding-reviewer 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/java-secure-coding-reviewer/SKILL.md` |
| references | `anvil/skills/java-secure-coding-reviewer/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/java-secure-coding-reviewer/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/java-secure-coding-reviewer/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/java-secure-coding-reviewer/results/` |
| 리포트 | `proving-grounds/evals/java-secure-coding-reviewer/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |
| 일관성 테스트 | TC-1 (SQL Injection), TC-2 (시크릿) `--repeat 3` 권장 |

## 평가 모드

리뷰 대상 코드 스니펫(변경 파일 diff 시뮬레이션)을 프롬프트로 제공하고, **스킬이 산출하는 보안 리뷰 리포트 마크다운**을 평가 대상으로 삼는다. 실제 `git`/`grep` 실행은 시뮬레이션이며, 스킬이 어떤 grep 명령을 계획하고 어떤 리포트 구조로 답하는지를 본다.

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 기준 | 직접 TC |
|---|------|-----------|--------|
| 1 | SEC-HG-1 놓침 | 프롬프트에 `String.format("... %s", userId)` 또는 `"WHERE id=" + userId` 같은 SQL 조립이 있는데 AUTO FAIL 섹션에 미보고 | TC-1·TC-5 |
| 2 | SEC-HG-2 놓침 | 프롬프트에 `sk_live_...`·`AIza...`·`clientSecret = "..."` 하드코딩 시크릿이 있는데 AUTO FAIL 섹션에 미보고 | TC-2·TC-4·TC-6 |
| 3 | SEC-HG-3 놓침 | 프롬프트에 `log.info("... userId=" + userId ...)` PII 노출이 있는데 AUTO FAIL 섹션에 미보고 | TC-3 |
| 4 | SEC-HG-4 놓침 | `MessageDigest.getInstance("MD5")`를 인증·세션·서명 용도로 사용하는데 AUTO FAIL 섹션에 미보고 | **TC-6** |
| 5 | SEC-HG-5 놓침 | `application-*.yml`에 환경변수 fallback 없는 평문 비밀번호가 있는데 AUTO FAIL 섹션에 미보고 | TC-2 |
| 6 | 시크릿 원본 노출 | 리뷰 리포트에 실제 시크릿 문자열(`sk_live_xxx...`)을 마스킹 없이 인쇄 | TC-2·TC-4·TC-6 |
| 7 | 코드 수정 시도 | 리뷰 스킬이 Edit/Write 도구를 사용해 실제 파일 변경 시도 | 전체 TC |
| 8 | SEC-CVE 놓침 | build.gradle에 CVE 등재 취약 라이브러리(log4j-core 2.14.1 등)가 있는데 미보고 | **TC-7** |
| 9 | SSRF 놓침 (A10) | 사용자 URL을 WebClient/HttpClient에 검증 없이 주입하는데 미보고 | **TC-8** |
| 10 | 역직렬화 취약 놓침 (A08) | `ObjectInputStream.readObject()`를 사용자 입력에 미보고 | **TC-10** |
| 11 | Command Injection 놓침 (A03) | `Runtime.exec(userInput)` 또는 문자열 조립 exec가 있는데 미보고 | **TC-11** |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- AUTO FAIL 11건 모두 0
- 위반 시 즉시 FAIL 판정 (다른 축 점수 무관)

### 축 2. 기능 정확도 (100점 만점, evaluation-rubric.md 기반)

| 항목 | 배점 |
|------|------|
| KISA 5등급 커버리지 | 20 |
| OWASP Top 10 순회 | 20 |
| PII 로그 검출 | 15 |
| 시크릿 grep 정확도 | 15 |
| CVE 대조 & SBOM 요청 | 10 |
| AUTO FAIL 분리 & FP 회피 | 10 |
| 범위 준수 & 이관 안내 | 10 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 사전 스캔 계획 | `grep -rn`으로 5종 시크릿 정규식, PII 6종 필드 검색 계획 명시 |
| KISA 5등급 순회 | Low → Medium → High → KEV → Critical 순서 검사 명시 |
| OWASP 10축 순회 | A01~A10 각 축 순회 (미해당은 "검사 통과") |
| AUTO FAIL 최상단 | SEC-HG-1~5 위반을 별도 섹션에 최상단 배치 |
| 마스킹 처리 | 발견한 시크릿·PII를 리포트에서 마스킹(`sk_live_****`, `010-****-1234`) |
| False positive 회피 | 테스트 픽스처·`example.yml`·주석 처리 코드 skip 명시 |
| 이관 안내 | 성능·아키텍처·공통 룰 발견 시 각 리뷰어에게 위임 안내 |
| CVE 요청 | build.gradle 변경 있으면 SBOM/Snyk 결과 요청 |

### 축 4. Baseline 비교

- **Baseline (스킬 미사용)**: 일반 코드 리뷰만. SQL Injection·시크릿·PII의 상당 부분 놓침. AUTO FAIL 분리·마스킹 개념 없음
- **With-Skill**: 5종 시크릿 grep + KISA 5등급 순회 + OWASP 10축 + PII 6종 필드 + AUTO FAIL 최상단 + 마스킹
- 합격: **With-Skill > Baseline + 25점**

### 축 5. 일관성

- TC-1 (SQL Injection), TC-2 (시크릿), TC-6 (MD5), TC-7 (CVE) `--repeat 3` 권장
- 편차 ≤ 15점
- 총 TC 개수: **11개** (Happy 5 / Edge 2 / Negative 4)

### 축 6. 효율성

- 기록용 (합격 조건 아님)
- 토큰 사용량 / 응답 시간

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | AUTO FAIL 0건 |
| 축 2 기능 정확도 | Happy Path 75점+ |
| 축 3 행동 패턴 | 체크리스트 80%+ |
| 축 4 Baseline | With-Skill > Baseline + 25점 |
| 축 5 일관성 | 편차 ≤ 15점 (--repeat 3 시) |

→ 모두 충족 시 **실전 배치 가능** (forge INDEX.md 상태 갱신)

---

## 리포트 양식

`proving-grounds/evals/java-secure-coding-reviewer/report.md`에 다음 섹션 포함:

1. 전체 점수 (100점 만점)
2. 6축별 결과
3. AUTO FAIL 검증 결과 (7건)
4. TC별 결과 (점수 + 위반 요약)
5. Baseline vs With-Skill 비교 표
6. 개선 권고
