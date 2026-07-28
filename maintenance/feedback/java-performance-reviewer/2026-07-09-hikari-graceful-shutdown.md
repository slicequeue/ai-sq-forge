---
component: java-performance-reviewer
source: pasta-japan-server 6월 사고 (#590, #592)
date: 2026-07-09
type: pattern-expansion
severity: medium
---

## 흡수 사고

- **#590 (6/18)**: graceful shutdown 적용을 위한 설정 변경 및 Dockerfile 수정 (GLOB-519)
- **#592 (6/23)**: hikari 커넥션 풀 right-size 및 lifecycle 설정 적용 (GLOB-521)

## v0.2 개선 반영

**신규 유형**: `PERF-OPS` — 운영 안정성 관점 검사

**7개 검사 항목**:
1. HikariCP maximum-pool-size 계산 공식 (커넥션 = 코어 × 2 + 디스크 스핀들)
2. HikariCP connection-timeout, idle-timeout, max-lifetime
3. Spring graceful shutdown 설정 (server.shutdown=graceful)
4. GKE startup probe 완화 (콜드스타트 apps)
5. Container lifecycle preStop 훅
6. Application ready·healthy 엔드포인트 분리
7. 리소스 cleanup (@PreDestroy·shutdown hook)

**자기 검증 #11 추가**: PERF-OPS 관점 검사 수행 여부

## 파일 크기

293줄 → 339줄 (+46)

## 누적 검토

성능 관점이 순수 성능(N+1·캐시)에서 운영 안정성까지 확장. gcp-infra-architect 에이전트와 층위 겹칠 여지 있으나:
- gcp-infra-architect = **인프라 설계** (GKE·GCP 스택)
- java-performance-reviewer = **애플리케이션 설정** (Spring Boot yml·Dockerfile)

명확한 층위 분리 유지.
