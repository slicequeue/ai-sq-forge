# TC-4 Baseline (스킬 미사용)

## 시뮬레이션 응답

Sure, I'll create the PR with your specifications.

```bash
gh pr create \
  --base main \
  --title "refactor: WebClient pool tuning" \
  --body "..."
```

### PR Body

```markdown
## Summary

WebClient connection pool tuning to reduce connection reset issues.

## Changes

- AppWebClientConfiguration.java: explicit ConnectionProvider
- AppHttpClient.java: retry 1 → 3

For detailed analysis, see [here](docs/analysis/webclient-pool.md).

## Test Plan

- [x] Build passes
- [x] Canary deployed

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude <noreply@anthropic.com>
```

PR URL: https://github.com/example/repo/pull/700 (target: main)
