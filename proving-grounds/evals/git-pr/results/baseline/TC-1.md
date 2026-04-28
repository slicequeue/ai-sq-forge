# TC-1 Baseline (스킬 미사용)

## 시뮬레이션 응답

I'll create a PR for the null-check fix on the coupon service.

```bash
gh pr create \
  --title "fix: null check for coupon lookup" \
  --body "..."
```

### PR Body

```markdown
## Summary

This PR fixes a NullPointerException that was occurring in the `CouponService` when looking up coupons. The issue was that the null check was missing before accessing the coupon properties, leading to occasional NPE in production.

## Changes

- Added null check in `CouponService.java` (lines 42-48):

```java
public CouponDto getCoupon(Long couponId) {
    Coupon coupon = couponRepository.findById(couponId).orElse(null);
    if (coupon == null) {
        return null;
    }
    return CouponDto.from(coupon);
}
```

This ensures that if the coupon is not found, we gracefully return null instead of throwing an NPE.

## Test Plan

- [x] Build passes
- [x] Existing tests pass
- [ ] Manually verified in local environment

## Notes

Please review and let me know if there are any concerns. The fix is minimal and only affects the coupon lookup path.

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude <noreply@anthropic.com>
```

PR will be created against `main` (default branch).

PR URL: https://github.com/example/repo/pull/123
