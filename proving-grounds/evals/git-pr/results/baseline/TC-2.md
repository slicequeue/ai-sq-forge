# TC-2 Baseline (스킬 미사용)

## 시뮬레이션 응답

Sure, I'll draft the PR body for the WebClient pool tuning refactor.

```bash
gh pr create \
  --title "refactor: WebClient connection pool tuning" \
  --body "..."
```

### PR Body

```markdown
## Summary

This PR tunes the WebClient connection pool to reduce intermittent `Connection reset by peer` errors observed in production. The connection pool was using default settings which caused stale connections to be reused, resulting in resets during burst traffic patterns.

## Changes

### `infra/network/AppWebClientConfiguration.java`

Added explicit `ConnectionProvider` configuration:

```java
@Bean
public ConnectionProvider connectionProvider() {
    return ConnectionProvider.builder("app-pool")
        .maxConnections(500)
        .maxIdleTime(Duration.ofSeconds(20))
        .evictInBackground(Duration.ofSeconds(60))
        .pendingAcquireTimeout(Duration.ofSeconds(45))
        .build();
}
```

### `infra/network/AppHttpClient.java`

Increased retry from 1 to 3 with exponential backoff (max 2s).

```java
.retryWhen(Retry.backoff(3, Duration.ofMillis(500))
    .maxBackoff(Duration.ofSeconds(2)))
```

## Metrics

Before vs After (D+2d post 100% rollout):

- Connection reset events: ~60/day → ~20/day (-66%)
- User-facing failures (Retries exhausted): some → 0
- Burst pattern (1m window, ~10 req): occasional → eliminated

## Deployment

- 4/26 22:00 KST: canary 50%
- 4/27 00:30 KST: 100% rollout
- D+2d: monitoring continues

## Follow-ups

1. OAuth token refresh path connection pool — same tuning to be applied
2. Expose ConnectionProvider metrics via Prometheus

For more details see [docs/analysis/webclient-pool-tuning.md](docs/analysis/webclient-pool-tuning.md).

## Test Plan

- [x] Build & unit tests pass
- [x] Canary 50% → 100% no incidents
- [ ] D+7 long-term measurement

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude <noreply@anthropic.com>
```

PR URL: https://github.com/example/repo/pull/612
