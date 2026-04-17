---
name: chaos-test-planner
description: "QA팀/개발팀의 장애 테스트 요청을 받아 Chaos Monkey 기반 실행 가능 여부를 검토하고, 테스트 계획서와 실행 커맨드를 생성하는 스킬. '장애 테스트', '카오스 몽키', 'chaos monkey', 'chaos test', 'QA 장애 요청', '장애 시뮬레이션', '장애 주입', '레이턴시 테스트', '서비스 지연 테스트', '장애 복구 테스트' 등의 요청 시 사용한다. QA팀에서 장애 시나리오를 전달하거나, 특정 API/서비스의 장애 영향을 검증하고 싶다는 요청이 오면 반드시 이 스킬을 사용한다."
version: "1.0"
last-modified: "2026-04-16"
changelog: "실전 프로젝트(pasta-japan-server)에서 forge로 역수입"
---

# chaos-test-planner — 장애 테스트 검토 & 계획 스킬

> 참고 가이드: `docs/works/chaos-monkey-장애테스트/guide.md`

이 스킬은 3단계로 동작한다:
1. **검토**: 요청이 Chaos Monkey로 실현 가능한지 판단
2. **질문**: 부족한 정보나 우려 지점을 명확히 짚음
3. **계획**: 테스트 계획서 + 실행 가능한 curl 커맨드 생성

---

## Phase 1. 요청 접수 & 실현 가능성 검토

### 1-1. 요청 파악

QA팀/개발팀의 요청은 **두 가지 형태**로 올 수 있다:

**형태 A — 대화**: 슬랙이나 직접 대화로 "홈 화면에서 혈당 카드가 느려지면 어떻게 되나요?" 같은 자연어 요청
**형태 B — 스프레드시트**: 구글 스프레드시트/엑셀로 정형화된 장애 시나리오 목록 (여러 행에 시나리오가 나열됨)

형태 B인 경우, 시트의 각 행을 개별 시나리오로 분리하여 검토한다. 사용자가 스프레드시트 내용을 붙여넣거나 파일 경로를 알려주면 해당 내용을 파싱한다.

두 형태 모두 아래 정보를 추출한다:

- **장애 대상**: 어떤 기능/API/서비스에 장애를 주입하려는지
- **장애 유형**: 지연(Latency), 예외(Exception), 메모리(Memory), 앱 종료(AppKiller)
- **검증 목표**: 무엇을 확인하고 싶은지 (에러 응답, 타임아웃, 데이터 정합성, 복구 시간 등)
- **환경**: 어디서 실행할지 (jp-stg 별도 Cloud Run이 기본)

### 1-2. Chaos Monkey 제약사항 체크

Chaos Monkey의 공격 제어 최소 단위는 **클래스(Bean)**이다. 아래 체크리스트로 실현 가능성을 판단한다:

**가능한 것:**

| 요청 | Chaos Monkey 대응 방법 |
|------|----------------------|
| "특정 서비스가 느려지면?" | `watchedCustomServices`에 해당 @Service FQCN 지정 + Latency |
| "외부 API가 죽으면?" | `watchedCustomServices`에 해당 @Component Client FQCN 지정 + Exception |
| "DB가 느려지면?" | `watcher.repository=true` + Latency (전체) 또는 특정 RepositoryImpl 지정 |
| "인스턴스가 죽으면?" | AppKiller Assault |
| "메모리가 부족하면?" | Memory Assault |

**불가능한 것 (우려 지점으로 안내):**

| 요청 | 이유 | 대안 |
|------|------|------|
| "특정 API URL 1개만 공격" | URL 단위 제어 불가, Bean(클래스) 단위만 가능 | 해당 API 전용 Service를 지정 (4-Tier 구조 활용) |
| "특정 메서드 1개만 공격" | 메서드 단위 제어 불가 | 해당 메서드만 호출하는 전용 Service가 있으면 Service 지정 |
| "네트워크 끊김" | JVM 내부 AOP 방식이라 네트워크 레벨 불가 | Cloud SQL/Redis 직접 차단, 방화벽 규칙 변경 |
| "특정 사용자만 장애" | 사용자 조건부 공격 불가 | 별도 인스턴스에서 해당 사용자 토큰으로만 테스트 |
| "특정 시간대만 공격" | 시간 조건부 공격 불가 | Actuator API로 수동 enable/disable |

### 1-3. 대상 Bean 탐색

요청에 언급된 기능/API에 해당하는 Spring Bean을 코드베이스에서 찾는다.

탐색 순서:
1. **Controller** 탐색 — `@RestController` + `@RequestMapping` 에서 해당 API URL 매핑 확인
2. **Service** 탐색 — Controller가 주입하는 Application Service 확인
3. **Client/ClientServiceImpl** 탐색 — 외부 시스템 호출이 관련되면 Infrastructure Client 확인
4. **Repository** 탐색 — DB 장애 시뮬레이션이면 RepositoryImpl 확인

탐색 도구:
```bash
# API URL로 Controller 찾기
grep -r "@RequestMapping\|@GetMapping\|@PostMapping" --include="*.java" -l | xargs grep "검색할_URL"

# Service 클래스 찾기
grep -r "@Service" --include="*.java" pasta-api/src/main/java/ -l

# Client 클래스 찾기
grep -r "class.*Client" --include="*.java" -l
```

**FQCN 확인 필수**: `watchedCustomServices`에 넣을 때는 전체 패키지명이 필요하다. 파일 경로에서 패키지명을 역추론하거나, 파일 상단 `package` 선언을 확인한다.

---

## Phase 2. 우려 지점 & 질문 생성

검토 결과를 바탕으로 사용자에게 **질문/우려 지점**을 전달한다.
아래 카테고리별로 해당하는 항목을 골라 질문한다.

### 2-1. 필수 확인 (반드시 질문)

- **환경**: "jp-stg 별도 Cloud Run에서 진행하나요? 기존 stg 인스턴스를 사용하면 다른 QA에 영향을 줍니다."
- **인증 토큰**: "테스트 API 호출에 사용할 Bearer Token이 준비되어 있나요?"
- **모니터링**: "테스트 중 로그/메트릭 확인 수단이 있나요? (Cloud Logging, Grafana 등)"

### 2-2. 정밀도 관련 (해당 시)

- 요청이 "특정 API만 공격"인데 해당 Controller에 여러 엔드포인트가 있으면:
  > "X Controller에는 A, B, C 엔드포인트가 모두 포함되어 있습니다. Service 레이어(XService)를 지정하면 더 정밀하게 공격할 수 있는데, 이 방향이 괜찮을까요?"

- 요청이 "외부 API 장애"인데 해당 Client가 여러 곳에서 사용되면:
  > "DexcomClient를 공격하면 CGM 관련 모든 기능에 영향이 갑니다. 특정 기능만 영향받기를 원하시면 상위 Service를 지정하는 방식도 있습니다."

### 2-3. 안전 관련 (해당 시)

- AppKiller 요청 시:
  > "AppKiller는 인스턴스를 즉시 종료합니다. 별도 인스턴스에서만 실행해야 하며, 다른 팀원에게 사전 공지가 필요합니다."

- Memory Assault 요청 시:
  > "Memory Assault는 Cloud Run 인스턴스의 전체 메모리에 영향을 줍니다. 메모리 제한과 OOM Kill 동작을 사전에 확인하는 것을 권장합니다."

- Level 1 (100%) + 운영 데이터 관련:
  > "Level 1은 모든 요청에 장애를 주입합니다. 실수로 비활성화를 잊으면 해당 인스턴스는 완전히 사용 불능이 됩니다. 테스트 후 반드시 disable을 확인해주세요."

### 2-4. 이전 교훈 (항상 언급)

> "이전 실험(2026-02-11)에서 Chaos Monkey `enabled: true`를 비활성화하지 않아 개발 환경에서 무작위 지연이 발생한 사례가 있습니다. 테스트 후 반드시 disable 상태를 확인해야 합니다."

---

## Phase 3. 테스트 계획서 & 실행 커맨드 생성

질문이 해소되면 (또는 사용자가 바로 계획을 요청하면) 아래 형식으로 테스트 계획서를 생성한다.

### 3-1. 테스트 계획서 형식

```markdown
# 장애 테스트 계획서: {시나리오명}

## 개요
| 항목 | 내용 |
|------|------|
| 요청자 | {QA팀/개발팀 누구} |
| 일시 | YYYY-MM-DD |
| 환경 | jp-stg 별도 Cloud Run |
| 목적 | {검증 목표} |

## 대상 Bean
| Bean (FQCN) | 레이어 | 역할 |
|---|---|---|
| {전체 패키지+클래스명} | Service / Client / Repository | {설명} |

## Assault 설정
| 항목 | 값 | 이유 |
|------|-----|------|
| Type | Latency / Exception / Memory / AppKiller | {왜 이 유형인지} |
| Level | {N} ({확률}%) | {왜 이 빈도인지} |
| Range | {시작}ms ~ {종료}ms | {지연 범위 근거} |

## 사전 조건
- [ ] 별도 Cloud Run 인스턴스 배포 완료
- [ ] 테스트 토큰 준비
- [ ] 팀 사전 공지 완료
- [ ] 모니터링 대시보드 접근 확인

## 실행 절차

### Step 1. 상태 확인
{curl 커맨드}

### Step 2. 활성화
{curl 커맨드}

### Step 3. Assault 설정
{curl 커맨드}

### Step 4. 테스트 실행
{API 호출 curl 커맨드 — 응답 시간 측정 포함}

### Step 5. 비활성화 (필수!)
{curl 커맨드}

### Step 6. 비활성화 확인
{curl 커맨드 — "You switched me off!" 확인}

## 검증 체크리스트
- [ ] {검증 포인트 1}
- [ ] {검증 포인트 2}
- [ ] {검증 포인트 3}

## 결과 기록
| 항목 | 장애 전 | 장애 후 |
|------|---------|---------|
| 응답 시간 | | |
| HTTP 상태 | | |
| 에러 메시지 | | |
| 다른 API 영향 | | |
```

### 3-2. curl 커맨드 생성 규칙

**BASE_URL 변수 사용**: 실제 URL 하드코딩 대신 변수 사용
```bash
BASE_URL=https://{별도-Cloud-Run-인스턴스-URL}
```

**Assault 설정 JSON**: 반드시 아래 필드를 명시적으로 포함
- `level`: 공격 빈도
- `latencyActive`: true/false
- `exceptionsActive`: true/false  
- `killApplicationActive`: true/false
- `watchedCustomServices`: 대상 Bean FQCN 배열 (특정 Bean 지정 시)

**응답 시간 측정**: API 호출 시 `-w` 옵션 포함
```bash
curl -w "\n응답시간: %{time_total}초\n" ...
```

**비활성화 확인은 필수**: 모든 계획서의 마지막은 disable + 상태 확인

### 3-3. 복수 시나리오 처리

QA팀 요청에 여러 시나리오가 포함되어 있으면:
- 각 시나리오별로 별도 섹션을 만든다
- 시나리오 간 의존성이 있으면 실행 순서를 명시한다
- 각 시나리오 사이에 **반드시 disable → 재설정** 절차를 포함한다

---

## 출력 흐름 (대화 → 확인 → 저장)

테스트 계획서 출력은 반드시 아래 3단계를 따른다:

### Step A. 대화 내 보여주기
검토 결과(가능/불가능 판정, 우려 지점)와 테스트 계획서를 **대화 내에서 먼저 보여준다.** 파일은 아직 만들지 않는다.

### Step B. 사용자 확인
계획서를 보여준 뒤 반드시 물어본다:
> "이 계획서 내용이 괜찮은지 확인해주세요. 수정할 부분이 있으면 말씀해주세요. 확정되면 파일로 저장하겠습니다."

사용자가 수정을 요청하면 반영 후 다시 보여준다. 이 루프를 사용자가 만족할 때까지 반복한다.

### Step C. 파일 저장
사용자가 확정하면 `docs/works/chaos-monkey-장애테스트/` 하위에 저장한다.
- 파일명 형식: `plan-{시나리오-요약}-YYYYMMDD.md`
- 예: `plan-홈-혈당카드-지연-20260415.md`
- 복수 시나리오면 하나의 파일에 시나리오별 섹션으로 정리

---

## 프로젝트 컨텍스트 (현재 설정 기준)

### 의존성
- `api/build.gradle`: `de.codecentric:chaos-monkey-spring-boot:2.7.2`
- `api/build.gradle`: `spring-boot-starter-actuator`

### 환경별 Chaos Monkey 상태
| 환경 | enabled | Actuator 노출 |
|------|---------|---------------|
| local | 미설정 | 미노출 |
| jp-dev | false | 노출 |
| jp-stg | false | 노출 |
| jp-prd | 미설정 | 미노출 |

### 주요 Watcher 대상 (레이어별)

**Service 레이어** (가장 정밀한 타게팅):
- `c.k.vc.pasta.health.home.application.service.HomeMainGlucoseCardService` — 홈 혈당 카드
- `c.k.vc.pasta.health.home.application.service.HomeMainMyPlanCardService` — 홈 마이플랜 카드
- `c.k.vc.pasta.coupon.application.service.CouponCodeValidationService` — 쿠폰 검증
- `c.k.vc.pasta.core.auth.application.service.CoreAuthService` — 인증
- `c.k.m.cgm.service.DexcomService` — Dexcom CGM 동기화
- `c.k.m.user.service.UserService` — 사용자 조회

**Infrastructure Client** (외부 API 장애 시뮬레이션):
- `c.k.vc.pasta.health.home.infrastructure.client.HomeGlucoseCgmRecentDataClient` — CGM 데이터
- `c.k.vc.pasta.core.access.infrastructure.client.PaymentPlatformClientServiceImpl` — 결제
- `c.k.m.cgm.client.DexcomClient` — Dexcom 외부 API
- `c.k.m.notification.service.NotificationClient` — 알림 서비스

> 위 목록은 참고용이다. 요청에 맞는 Bean은 반드시 코드베이스에서 직접 탐색하여 FQCN을 확인한다.

### 모바일 앱 타임아웃 기준
- 파스타 앱의 HTTP 요청 타임아웃: **60초** (2026-04-15 모바일팀 확인)
- Latency Assault로 네트워크 에러 UI를 트리거하려면 **65초 이상** 지연 필요 (`latencyRangeStart: 65000`)
- 60초 미만 지연은 앱에서 느린 정상 응답으로 처리되므로 "네트워크 불안정" UI가 나오지 않을 수 있음

### 이전 실험 교훈
- 2026-02-11: `enabled: true` 비활성화를 잊어 dev 환경에서 무작위 지연 발생 → API 성능 저하로 착각
- 교훈: **테스트 후 반드시 disable 확인**, 별도 인스턴스 사용 권장
