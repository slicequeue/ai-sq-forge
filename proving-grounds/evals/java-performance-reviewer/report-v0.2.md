# java-performance-reviewer v0.2 회귀 평가 리포트

- 실행일: 2026-07-29
- 스킬 버전: v0.2 (339줄)
- 이전 회귀: 없음 (v0.1은 하네스 미작성 상태로 배포)
- 실행 방식: `--skip-baseline` (with-skill only, 1회 시뮬레이션)

## 총평

| 항목 | 값 |
|---|---|
| 총점 | **98/100** (EXCELLENT) |
| 판정 | **PASS** |
| 5축 통과 | 가드레일 ✓ / 기능 정확도 ✓ / 행동 패턴 ✓ / Baseline (skip) / 일관성 (skip) |
| **v0.2 신규 PERF-OPS 룰 커버리지** | **0/7 — 심각한 갭** |

**핵심 발견**: v0.1 룰 세트(N+1·WebClient·캐시)는 완벽 검증. 하지만 **v0.2 신규 PERF-OPS 룰 7개는 하네스 TC 0건** — HikariCP·graceful shutdown·startup probe 등 6월 pasta 사고 흡수분이 검증되지 않은 채 배포 상태.

## TC별 결과

### TC-1 Happy — N+1 검출 (95/100 EXCELLENT)
- G-2 AUTO FAIL 검출 (반복문 안 Repository) / `PERF-JPA` / `findAllByIdIn` + Map 인덱싱 권장

### TC-2 Happy — WebClient timeout (G-3+G-4) (100/100 EXCELLENT)
- G-3, G-4 둘 다 AUTO FAIL / `HttpClient.create().option(CONNECT_TIMEOUT_MILLIS,3000).responseTimeout(5s)` + `retryWhen(...).filter(5xx 한정)`

### TC-3 Edge — 캐시 write-through 부분 갱신 (95/100 EXCELLENT)
- AUTO FAIL 없음 / `PERF-CACHE` 필수 수정 / java-spring-coder v1.11 짝 룰 참조 / 대안 2개

### TC-4 Negative — N+1 완화 요구 거절 (100/100 EXCELLENT)
- G-2 명시 거절 / 트래픽 낮음 완화 사유 아님 / 대안 2개

### TC-5 Negative — WebClient timeout 완화 요구 거절 (100/100 EXCELLENT)
- G-3 명시 거절 / 스레드 고갈 시나리오 설명 / G-4 함께 지적

## v0.2 신규 룰 커버리지 갭 (PERF-OPS)

| 룰 | 실전 사고 배경 | TC |
|---|---|---|
| HikariCP `maximum-pool-size` right-size | pasta #592 (GLOB-521) | 없음 |
| HikariCP `minimum-idle`·`connection-timeout`·`max-lifetime` | 위와 동일 | 없음 |
| `spring.lifecycle.timeout-per-shutdown-phase` | pasta #590 (GLOB-519) | 없음 |
| `server.shutdown: graceful` | 위와 동일 | 없음 |
| Kubernetes startup probe 완화 | admin #588 사례 | 없음 |
| `@PreDestroy`·`SmartLifecycle` shutdown hook | 리소스 cleanup | 없음 |
| ready/healthy 엔드포인트 분리 | 배포 안정성 | 없음 |

## 권고

### 하네스 확장 시급 (신규 TC 3개)

1. **TC-6 Happy** — HikariCP 기본값 유지 + graceful shutdown 미설정 → `PERF-OPS` High 검출
2. **TC-7 Happy** — K8s 짧은 startup probe → 콜드스타트 앱 부팅 실패 위험 지적
3. **TC-8 Edge** — HikariCP 크기 판정 애매 (DB `max_connections` × 인스턴스 수 × pool) → "검증 권장" 등급

## 결론

- **PASS 98/100** (기존 5개 TC 모두 통과)
- **v0.2 신규 PERF-OPS 룰 커버리지 0/7** — 다음 사이클 최우선
- **--repeat 3 일관성 축**은 하네스 확장 후 실행 권고
- 이번 회귀 평가 신뢰도: "v0.1 기준 5개 룰까지만 검증됨"
