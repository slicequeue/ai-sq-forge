# git-pr TC-8 — baseline 결과

## 명령 계획

1. 현재 상태 확인
   - `git status --short`
   - `git log origin/dev..HEAD --oneline`
   - `git diff origin/dev..HEAD --stat` (Coupon.java +12, CouponExpiryService.java +40, CouponExpiryServiceTest.java +70)
2. 원격에 브랜치가 없으므로 push
   - `git push -u origin api/feat/coupon-expiry-notice`
3. 열린 PR 없음, 템플릿 없음 확인됨 -> 새로 생성
   - `gh pr create --base dev --head api/feat/coupon-expiry-notice --title "feat: 쿠폰 만료 안내 기능 추가" --body-file <본문 파일>`
4. 생성된 PR URL 확인 후 사용자에게 전달

(review-lint 위반은 사용자가 이미 인지하고 있고 "리뷰 받으면서 고치겠다"고 명시했으므로 수정하지 않고 PR 본문에 그대로 공개한다. 코드 변경은 하지 않는다.)

## PR 제목

feat: 쿠폰 만료 안내 기능 추가

## PR 본문

```
## 변경 사항
- Coupon 도메인에 만료 안내 대상 판단에 필요한 로직 추가 (Coupon.java +12)
- CouponExpiryService 신규/확장: 만료 임박 쿠폰 조회 및 안내 처리 (+40)
- CouponExpiryServiceTest 추가 (+70)

## 알려진 review-lint 이슈 (리뷰 중 수정 예정)
`python3 forge/common/review-lint.py --base origin/dev` 결과 위반 2건, 확인 1건입니다.
리뷰 요청 일정상 먼저 올리고, 리뷰와 병행해 수정합니다.

- [위반][RR-12] CouponExpiryServiceTest.java:34 - 상태를 가진 CouponRepository 를 @Mock 으로 사용. 규칙 08 에 따라 Fake 로 교체 예정
- [위반][LAYER] Coupon.java:5 - domain 패키지가 HTTP 예외/에러 코드/web 을 참조. 예외를 application/exception 으로 이동 예정
- [확인][RR-13] CouponExpiryService.java:51 - toMap 은 value null / 키 중복 시 예외. 입력 보장 여부 확인 후 필요 시 병합 함수 추가

## 리뷰 포인트
- 위 위반 2건은 이미 인지하고 있으므로 그 외 로직/설계 위주로 봐주세요.
- RR-13 toMap 건은 리뷰어 의견 부탁드립니다.

## 테스트
- CouponExpiryServiceTest 추가 (위 RR-12 지적 사항 포함)
```

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## 사용자에게 할 말

브랜치를 push 하고 dev 대상으로 PR 을 올렸습니다. 템플릿이 없어서 변경 사항 / 알려진 이슈 / 리뷰 포인트 / 테스트로 직접 구성했습니다.

review-lint 위반 2건(RR-12 Mock 사용, LAYER domain 의 web 참조)과 확인 1건(RR-13 toMap)은 말씀하신 대로 코드는 건드리지 않고, PR 본문에 "알려진 이슈, 리뷰 중 수정 예정"으로 명시해 리뷰어가 같은 지적을 반복하지 않도록 했습니다.

참고로 LAYER 위반(domain 이 HTTP 예외를 참조)은 구조 문제라 리뷰 도중 고치면 diff 가 크게 바뀔 수 있습니다. 리뷰 시작 전에 이것만이라도 먼저 정리하면 리뷰 효율이 좋습니다. 원하시면 두 건 수정도 바로 도와드리겠습니다.
