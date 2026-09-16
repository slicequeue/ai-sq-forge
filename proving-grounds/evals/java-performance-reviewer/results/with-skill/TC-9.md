## 성능 관점 리뷰 결과 (java-performance-reviewer v0.3)

**브랜치**: N/A (스니펫 단위 리뷰 — git 브랜치 컨텍스트 없음)
**비교 기준**: N/A
**커밋 수**: N/A
**변경 파일**: 1개 (성능 영향 파일 1개 — 공지 예약 발송 대상 조회/발송 로직)
**서비스 규모 전제**: 전체 사용자 수십만 명

---

### AUTO FAIL (성능 하드 가드레일 위반)

없음. G-1(EAGER 컬렉션), G-2(반복문 안 Repository 조회), G-3(WebClient timeout 미설정), G-4(4xx retry), G-5(싱글톤 mutable field) 패턴이 리터럴로는 매칭되지 않음. 단, 아래 필수 수정 항목은 G-2와 사실상 동일한 위험군(반복문 안 순차 원격 호출)이므로 등급을 Critical로 별도 분류함.

### 필수 수정 (Critical / High)

| # | 유형 | 등급 | 파일:위치 | 내용 | 수정 방향 |
|---|------|------|----------|------|-----------|
| 1 | PERF-BULK | Critical | dispatch() — `case ALL -> receiverRepository.findAllDirectNoticeReceivers()` | ALL 대상 시 수십만 규모 수신자를 페이징/스트리밍 없이 `List`로 전량 로드. 힙 압박 및 이후 반복 처리 지연의 시작점 | `RowCallbackHandler`, JPA `Stream<Receiver>`(`@QueryHints(NO_CACHE)` + 트랜잭션 필요), 또는 `Pageable` 청크 조회로 전환. 청크 단위로 아래 필터·발송까지 스트리밍 처리 |
| 2 | PERF-BULK | Critical | dispatch() — for 루프 내 `groupAccessClient.isEntitled(...)` + `hospitalAccessClient.isEntitled(...)` | 수신자 1건당 외부 API를 순차로 2회 호출(N+1과 동일한 구조, 대상이 DB가 아니라 외부 서비스일 뿐). 수십만 건이면 라운드트립이 수십만×2회로 폭증 — 배치 실행 시간이 수 시간 단위로 늘어나거나 외부 서비스에 순간 부하 집중 가능 | 두 클라이언트에 벌크/배치 엔타이틀먼트 조회 API가 있는지 확인 후 `userId` 리스트 단위 벌크 호출로 전환. 벌크 API가 없다면 최소한 청크 단위 병렬 호출(`WebClient` 비동기 + bounded concurrency)로 전환하고 상한 없는 무제한 병렬 호출은 피할 것 |
| 3 | PERF-BULK | High | dispatch() — `entitled && appVersionFilter.supports(r.getAppVersion())` 순서 | 값비싼 외부 엔타이틀먼트 조회(`groupAccessClient`/`hospitalAccessClient`)를 로컬 계산만으로 끝나는 값싼 `appVersionFilter.supports()`보다 먼저 실행. 필터로 걸러질 대상까지 불필요하게 외부 API를 호출함 (RR-9 필터 순서 원칙 위반, #643과 동일 패턴) | `appVersionFilter.supports(r.getAppVersion())`를 먼저 평가해 잔여 집합을 줄인 뒤에만 `groupAccessClient`/`hospitalAccessClient` 엔타이틀먼트 조회 수행 (`&&` 피연산자 순서 교체로 short-circuit 활용) |

### 권장 개선 (Medium / Low / Info)

| # | 유형 | 등급 | 파일:위치 | 내용 | 개선 방향 |
|---|------|------|----------|------|-----------|
| 1 | PERF-BULK | Medium | dispatch() — `case USER_LIST -> receiverRepository.findByUserIdIn(reservation.getUserIds())` | `reservation.getUserIds()` 크기에 상한이 보이지 않음. `IN` 절 파라미터 개수 상한 미확인 | 호출 측(예약 생성 API)에서 `userIds` 최대 건수를 제한하거나, 여기서 청크 분할 후 배치 조회로 전환 |
| 2 | PERF-BULK/PERF-TX | Low | dispatch() — `pushClient.send(r)` | 필터 통과 대상에 대해서도 푸시 발송을 건별 순차 호출. 대상 규모가 크면 발송 자체도 지연 누적 | `pushClient`가 배치/벌크 발송 API를 제공하는지 확인 후 필터 통과 대상을 모아 배치 발송으로 전환 |
| 3 | PERF-TX | Info | dispatch() — `groupAccessClient`/`hospitalAccessClient` 호출부 | 이번 diff에 두 클라이언트의 생성/설정 코드(WebClient timeout, retry 필터)가 포함되어 있지 않아 G-3/G-4 기준 검증 불가 | 클라이언트 구현이 이번 변경 범위에 포함된다면 connect/read timeout 명시 여부, retry 5xx 한정 여부를 별도 확인 요청 |

### 검사 통과 항목
- G-1 (`@OneToMany`/`@ManyToMany` EAGER): 해당 코드 없음 — N/A
- G-2 (반복문 안 Repository 조회): Repository 호출은 루프 진입 전 1회로 끝남 — OK (단, 루프 안 외부 클라이언트 순차 호출은 위 Critical #2로 별도 지적)
- G-5 (싱글톤 mutable field): 해당 코드 없음 — N/A
- PERF-JPA/PERF-CACHE/PERF-RESOURCE/PERF-LOG/PERF-OPS/Soft-delete UNIQUE: 이번 diff 범위에 해당 코드 없음 — N/A

### 관점 침범 회피 메모
`groupAccessClient.isEntitled(...) && hospitalAccessClient.isEntitled(...)`에서 조회 실패/예외 시 통과(open)인지 차단(closed)인지는 코드에 드러나지 않음. 이는 접근 제어 판정의 fail 정책 문제로 성능 관점이 아니라 보안/정합성 관점(`java-secure-coding-reviewer`) 사안이라 이 리포트에서는 상세 분석하지 않고 라우팅만 안내함.

---

**등급 요약**: Critical 2건, High 1건, Medium 1건, Low 1건, Info 1건. AUTO FAIL 0건.
**핵심 리스크**: 수십만 규모 전체 발송(ALL) 경로에서 "전체 로드 + per-user 순차 외부 API 2회 호출 + 비싼 필터 선행" 조합이 겹쳐 배치 완료 시간과 외부 서비스 부하 양쪽에 실운영 리스크를 만든다.
