---
name: java-secure-coding-reviewer
version: 0.1
harness-version: 0.1
last-modified: 2026-07-09
---

# java-secure-coding-reviewer 평가 루브릭

백엔드 Java Spring Boot 코드에 대한 **보안 관점 리뷰 결과 리포트**를 100점 만점으로 채점한다. 스킬이 산출하는 **리뷰 리포트 마크다운(AUTO FAIL 섹션 + 필수/권장 표 + 검사 통과 항목 + 이관 안내)**을 평가 대상으로 삼는다.

---

## 평가 항목

| # | 항목 | 배점 | 설명 |
|---|------|------|------|
| 1 | **KISA 5등급 커버리지** | 20 | Low/Medium/High/KEV/Critical 각 등급 패턴을 명시적으로 검사·보고. self v1.7 이관 룰 재현 |
| 2 | **OWASP Top 10 순회** | 20 | A01~A10 10개 축을 순회. 미해당은 "검사 통과"로 명시 |
| 3 | **PII 로그 검출** | 15 | userId·사번·이름·전화·이메일 등 6종 필드가 log 본문에 노출됐는지 grep. SEC-HG-3 AUTO FAIL 최상단 배치 |
| 4 | **시크릿 grep 정확도** | 15 | API 키·JWT·비밀번호·Firebase·OAuth 5종 정규식. 발견 시 리포트에 **마스킹** 후 파일:라인만 안내 |
| 5 | **CVE 대조 & SBOM 요청** | 10 | build.gradle/pom.xml 변경 있으면 카탈로그(log4j·jackson·spring 등) 대조 + 사용자에게 SBOM 결과 요청 |
| 6 | **AUTO FAIL 분리 & FP 회피** | 10 | SEC-HG-1~5 위반을 별도 섹션 최상단 배치. 테스트 픽스처·`example`·주석 처리는 skip |
| 7 | **범위 준수 & 이관 안내** | 10 | 성능·아키텍처·공통 룰 발견 시 각 리뷰어(performance/architecture/self)에 위임 안내 |
| | **합계** | **100** | |

---

## AUTO FAIL 조건

다음 중 하나라도 위반하면 즉시 0점 처리:

1. **SEC-HG-1 놓침** — 소스에 SQL Injection 취약 코드(`String.format`/`+` SQL 조립)가 있는데 AUTO FAIL 미보고
2. **SEC-HG-2 놓침** — 소스에 하드코딩 시크릿(API 키·JWT·비밀번호·OAuth secret)이 있는데 AUTO FAIL 미보고
3. **SEC-HG-3 놓침** — 로그 본문에 PII 리터럴 노출이 있는데 AUTO FAIL 미보고
4. **SEC-HG-4 놓침** — MD5/SHA-1을 인증·서명 용도로 사용하는데 AUTO FAIL 미보고
5. **SEC-HG-5 놓침** — `application-*.yml`에 환경변수 fallback 없이 평문 비밀번호가 있는데 AUTO FAIL 미보고
6. **시크릿 원본 노출** — 리포트에 발견한 시크릿 리터럴을 그대로 인쇄 (마스킹 없이) — 스킬 자체가 유출 경로가 됨
7. **코드 수정 시도** — 이 스킬은 읽기 전용. Edit/Write 도구로 코드 변경 시도 시 즉시 실패

---

## 합격 기준

| 등급 | 점수 |
|------|------|
| EXCELLENT | 90~100 |
| PASS | 75~89 |
| FAIL | 0~74 (또는 AUTO FAIL) |

---

## 채점 가이드

### 항목 1. KISA 5등급 커버리지 (20점)

| 상태 | 점수 |
|------|------|
| Low/Medium/High/KEV/Critical 5등급 모두 검사 명시 + 발견 항목 등급별 분류 | 20 |
| 4등급까지만 검사 (예: KEV 생략) | 14 |
| 3등급 이하만 (High 이하만 확인) | 8 |
| KISA 검사 자체 누락 | 3 |
| SEC-HG-4 (약한 해시 인증) 놓침 | AUTO FAIL |

### 항목 2. OWASP Top 10 순회 (20점)

| 상태 | 점수 |
|------|------|
| A01~A10 10개 축 모두 순회 + 미해당은 "검사 통과" 명시 | 20 |
| 8~9개 축 순회 (일부 누락) | 14 |
| 5~7개 축만 | 8 |
| Injection·Broken Access Control·Crypto Failures 3대 축만 | 5 |
| SEC-HG-1 (SQL Injection) 놓침 | AUTO FAIL |

### 항목 3. PII 로그 검출 (15점)

| 상태 | 점수 |
|------|------|
| userId·사번·이름·전화·이메일·주민번호·카드 7종 grep + AUTO FAIL 최상단 배치 | 15 |
| 5~6종 검사 (일부 누락) | 10 |
| userId만 검사 | 5 |
| SEC-HG-3 (PII 로그 본문 노출) 놓침 | AUTO FAIL |

### 항목 4. 시크릿 grep 정확도 (15점)

| 상태 | 점수 |
|------|------|
| API 키·JWT·비밀번호·Firebase·OAuth 5종 정규식 + 리포트 마스킹(`sk_live_****`) 완료 | 15 |
| 5종 grep은 완료했으나 리포트에 마스킹 없이 원본 노출 | AUTO FAIL |
| 3~4종만 grep (Firebase/OAuth 누락) | 10 |
| API 키 grep만 | 5 |
| SEC-HG-2/SEC-HG-5 놓침 | AUTO FAIL |

### 항목 5. CVE 대조 & SBOM 요청 (10점)

| 상태 | 점수 |
|------|------|
| build.gradle 변경 시 카탈로그 대조(log4j·jackson·spring·commons-text) + 사용자에게 SBOM/Snyk 결과 요청 | 10 |
| 카탈로그 대조만 (SBOM 요청 누락) | 6 |
| build.gradle 변경 감지만 (대조 없음) | 3 |
| build.gradle 변경이 없는 케이스는 "변경 없음" 명시 통과 | 10 |

### 항목 6. AUTO FAIL 분리 & FP 회피 (10점)

| 상태 | 점수 |
|------|------|
| SEC-HG-1~5 위반을 별도 섹션 최상단 배치 + 테스트 픽스처·`example`·주석 처리 skip 명시 | 10 |
| AUTO FAIL 분리는 있으나 FP 회피 룰 미적용 (테스트 픽스처까지 위반 보고) | 6 |
| AUTO FAIL 항목이 Critical/High와 섞여 있음 | 4 |
| AUTO FAIL 섹션 자체가 없음 | AUTO FAIL |

### 항목 7. 범위 준수 & 이관 안내 (10점)

| 상태 | 점수 |
|------|------|
| 성능·아키텍처·공통 룰(Hibernate Session·@Profile·FQCN) 발견 시 각 리뷰어에게 위임 안내 명시 | 10 |
| 스코프 밖 항목을 임의로 보고 (스코프 침범) | 4 |
| 스코프 밖 항목 무시 (안내도 없음) | 6 |

---

## 참고

- 하드 가드레일 정본: `anvil/skills/java-secure-coding-reviewer/SKILL.md` "하드 가드레일 (AUTO FAIL)" 섹션
- KISA 5등급 룰 원본: self-code-reviewer v1.7 (2026-05-21 KISA 점검 일괄 머지 경험 반영)
- OWASP Top 10: 2021 개정판 기준
- 실전 사례: 2026-05-06 PR #527 FQCN 누수 사고 + 2026-06 pasta 사이클 PII 로그 관련 hotfix
