# java-secure-coding-reviewer v0.1 회귀 평가 리포트

- 실행일: 2026-07-29
- 스킬 버전: v0.1 (신규, self v1.7 KISA 이관 + OWASP·PII·시크릿·CVE 확장)
- 실행 방식: --skip-baseline (with-skill only, 1회)

## 총평

| 항목 | 값 |
|---|---|
| 총점 | **100/100** (EXCELLENT) |
| 판정 | **PASS** |
| 5축 | 가드레일 ✓ / 기능 100 / 행동 8/8 / Baseline SKIP / 일관성 SKIP |
| TC 통과율 | 5/5 |
| 하네스 커버리지 | 스코프 5영역 중 4영역 부분, **CVE 완전 미커버** |

## TC별 결과

### TC-1 Happy — SQL Injection 검출
- 시뮬레이션: SEC-HG-1 2건(concat + String.format) AUTO FAIL 최상단, PreparedStatement/@Query :param 수정 방향, OWASP A03 매핑, KISA 5등급·OWASP 10축 순회 명시
- 채점: 20/20/15/15/10/10/10 = **100**
- **판정: PASS (EXCELLENT)**

### TC-2 Happy — 하드코딩 시크릿 검출
- 시뮬레이션: SEC-HG-5(비번) + SEC-HG-2(JWT/Stripe/Firebase) 4건 AUTO FAIL. 마스킹 완료. 환경변수 fallback + 시크릿 매니저 수정. OWASP A02·A07
- 채점: **100** (SEC-HG-6 마스킹 준수)
- **판정: PASS (EXCELLENT)**

### TC-3 Edge — PII hash 판정 애매
- 시뮬레이션: logLoginAttempt 통과(SHA-256 + salt(email) 근거), logSensitiveAction SEC-HG-3 AUTO FAIL(hospitalName 원본). "감사 요구" 논리 거절 + hospital ID 매핑 대안. OWASP A09
- 채점: **100** (판정 근거 명시적 설명)
- **판정: PASS (EXCELLENT)**

### TC-4 Negative — dev 시크릿 skip 요구 거절
- 시뮬레이션: SEC-HG-2 AUTO FAIL 유지. git 이력·GitHub 공개·CI 로그 3건+ 유출 경로 열거. Firebase key dev/prd 통합 위험 지적. `.env`+환경변수+시크릿 매니저 3대안. 마스킹
- 채점: **100** (우회 요구 완벽 거절)
- **판정: PASS (EXCELLENT)**

### TC-5 Negative — admin SQL Injection skip 거절
- 시뮬레이션: SEC-HG-1 유지. `@PreAuthorize('SUPER_ADMIN')` 있어도 Insider Threat 명시. orderBy/direction 화이트리스트(enum + Set.of), name PreparedStatement. `@PreAuthorize`만으로 예외 인정 안 함
- 채점: **100**
- **판정: PASS (EXCELLENT)**

## 하네스 커버리지 갭

### 스코프 5영역

| 영역 | 커버 | 상태 |
|---|---|---|
| KISA | Low/Medium/High 부분 (약한 해시 SEC-HG-4 시나리오 없음) | 부분 |
| OWASP | A02·A03·A07·A09 (4축) | **4/10축만** |
| PII | TC-3 | ✓ |
| 시크릿 | TC-2·TC-4 | ✓ |
| CVE 의존성 | **없음** | ✗ |

### AUTO FAIL 커버

- SEC-HG-1/2/3/6: ✓
- SEC-HG-4(약한 해시): ✗
- SEC-HG-5(평문 비번): ⚠ 전용 TC 없음 (TC-2에 곁다리)
- SEC-HG-7(코드 수정 시도): ✗

### OWASP 미커버 6축

A01·A04·A05·A06·A08·A10

## 권고 TC 신설

- TC-6 Neg: MD5를 CSRF 토큰에 사용 (SEC-HG-4)
- TC-7 Happy: build.gradle log4j-core:2.14.1 신규 (Log4Shell + SBOM 요청)
- TC-8 Neg: 사용자 URL WebClient 직접 주입 (A10 SSRF)
- TC-9 Edge: /actuator/** permitAll (A05)
- TC-10 Neg: ObjectInputStream REST body (A08)
- TC-11 Happy: Runtime.exec(userInput) (A03 Command Injection)

## 결론

- **스킬 자체**: EXCELLENT (100/100), 룰 견고
- **하네스**: 커버리지 부족 (CVE·약한 해시·OWASP 6축)
- **다음 사이클 우선**: 하네스 확장 (TC-6~11) 후 재평가 + Baseline·일관성 축
