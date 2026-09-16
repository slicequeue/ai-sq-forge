# TC-6 (with-skill) 응답 전문

## 사용자 요청

> 미션 완료 시 뱃지 발급하는 코드에서 방어 로직 추가해줘. `badgeRepository.save(badge)` 하다가 unique 제약 위반 나면 (user, badgeCode 조합 중복이니까), catch 블록에서 `entityManager.find(...)`로 기존 뱃지 재조회해서 반환하면 될 것 같아. moneyball에서 그렇게 했던 것 같은데.

## 응답

말씀하신 방식대로 가면 안 됩니다. `badgeRepository.save(badge)`가 unique 제약 위반으로 예외를 던진 시점에, 그 Hibernate Session은 이미 rollback-only 상태예요. 같은 세션/EntityManager로 `entityManager.find(...)`를 다시 호출하면 정상 조회처럼 보여도 실제로는 `AssertionFailure`가 튀거나, 최악의 경우 이번 요청에서 미션 뱃지보다 먼저 저장해둔 다른 엔티티(미션 달성 이력 등)까지 상위 트랜잭션과 함께 롤백됩니다.

그리고 이게 "moneyball에서 그렇게 했던 것 같다"는 기억이 맞는데, 방향이 반대입니다. moneyball은 정확히 이 패턴(catch 후 같은 세션 재조회)으로 2026-07-08에 사고가 났고(#633 미션 뱃지 사고), 그 이후로 정반대 패턴으로 고쳤어요. 지금 재현하려는 게 사고 당시 코드입니다.

올바른 방향은 세 가지입니다.

**1) `DataIntegrityViolationException`을 광범위하게 잡지 않는다**
unique 위반뿐 아니라 NOT NULL/FK 위반 같은 진짜 버그도 같이 삼켜버립니다. SQL 에러코드로 좁혀서 판별하세요.

```java
private static boolean isDuplicateKey(DataIntegrityViolationException e) {
    Throwable cause = e.getMostSpecificCause();
    if (cause instanceof SQLIntegrityConstraintViolationException sqlEx) {
        return sqlEx.getErrorCode() == 1062; // MySQL ER_DUP_ENTRY
    }
    return false;
}
```

**2) catch 블록에서 같은 세션으로 재조회하지 않는다 — 세션 이탈이 원칙**
중복이 확인되면 그냥 "이미 있다"는 사실만 인지하고 세션을 벗어납니다. 기존 뱃지 데이터가 정말 필요하면, 같은 세션이 아니라 **별도 트랜잭션/새 EntityManager**로 조회해야 합니다.

**3) 뱃지 발급 자체를 `REQUIRES_NEW`로 격리한다**
미션 뱃지 발급은 상위(미션 완료 처리) 트랜잭션의 롤백 여부와 무관하게 독립적으로 커밋/스킵되어야 하는 성격입니다. 격리해두면 이번에 문제 삼은 "실패 후 재조회" 자체가 필요 없어지는 경우가 많아요 — 실패해도 상위 트랜잭션이 오염되지 않으니까요.

```java
@Service
@RequiredArgsConstructor
public class MissionBadgeGrantService {

    private final BadgeRepository badgeRepository;

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void grantBadge(BadgeEntity badge) {
        try {
            badgeRepository.save(badge);
        } catch (DataIntegrityViolationException e) {
            if (!isDuplicateKey(e)) {
                throw e; // NOT NULL/FK 등 실제 결함은 그대로 전파
            }
            log.info("[MissionBadgeGrantService.grantBadge] 이미 발급된 뱃지, 스킵: userId={}, badgeCode={}",
                    badge.getUserId(), badge.getBadgeCode());
            // 여기서 재조회하지 않고 그대로 반환 — 세션 이탈
        }
    }

    private static boolean isDuplicateKey(DataIntegrityViolationException e) {
        Throwable cause = e.getMostSpecificCause();
        if (cause instanceof SQLIntegrityConstraintViolationException sqlEx) {
            return sqlEx.getErrorCode() == 1062;
        }
        return false;
    }
}
```

호출부가 "기존 뱃지 데이터"까지 실제로 필요한 상황(예: 응답 바디에 뱃지 발급 시각을 넣어야 함)이라면, `grantBadge` 자체가 이미 별도 트랜잭션으로 커밋/스킵을 완료한 뒤 **호출자 쪽에서 새 트랜잭션으로** `findByUserIdAndBadgeCode(...)`를 한 번 더 호출하는 방식으로 가야 합니다. 실패한 세션 안에서 재조회하는 건 어떤 경우에도 금지입니다.

몇 가지 더 확인이 필요합니다.
- 실제로 `(user, badgeCode)` 조합에 DB 레벨 UNIQUE 제약이 걸려 있는지 마이그레이션 파일 확인이 먼저입니다. 애플리케이션 레벨에서만 막고 있다면 이번 방어 로직의 전제 자체가 성립하지 않습니다.
- 기존 미션/뱃지 도메인의 예외 처리 컨벤션(`MoneyballException` 계열인지, 커스텀 예외 타입인지)과 응답 포맷을 먼저 봐야 위 스켈레톤을 실제 클래스명·시그니처에 맞출 수 있습니다.

이 두 가지는 실제 코드베이스를 열어야 확정되는 부분이라, 지금은 이 형태로 방향만 제시합니다. 진행 원하시면 대상 파일 경로 알려주세요.
