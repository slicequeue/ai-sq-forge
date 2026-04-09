# coding-implementer 테스트 케이스

## TC-1: Happy Path — TDD 계획서 기반 표준 기능 구현

- **입력 프롬프트**: "아래 TDD 계획서를 기반으로 코드를 구현해줘.\n\n## TDD 요약: 쿠폰 사용(Redeem) API\n- 모듈: pasta-api\n- 도메인: coupon\n\n### Phase 1: Domain 계층\n- **TODO**:\n  - [ ] `pghd/coupon/domain/CouponCodeEntity.java` — 쿠폰 코드 도메인 엔티티 (id, code, discountAmount, usedAt, usedBy)\n  - [ ] `pghd/coupon/domain/CouponCodeRepository.java` — 도메인 Repository 인터페이스 (findByCode, save)\n- **테스트**: `CouponCodeEntityTest` — 엔티티 생성, 사용 처리 검증\n\n### Phase 2: Infrastructure 계층\n- **TODO**:\n  - [ ] `pghd/coupon/infrastructure/CouponCodeJpaEntity.java` — JPA 엔티티 (toEntity, from 변환)\n  - [ ] `pghd/coupon/infrastructure/CouponCodeJpaRepository.java` — Spring Data JPA\n  - [ ] `pghd/coupon/infrastructure/CouponCodeRepositoryImpl.java` — RepositoryImpl\n- **테스트**: `CouponCodeRepositoryImplTest` — @DataJpaTest + Testcontainers\n\n### Phase 3: Application 계층\n- **TODO**:\n  - [ ] `pghd/coupon/application/CouponRedeemService.java` — 쿠폰 사용 유스케이스\n  - [ ] `pghd/coupon/application/CouponRedeemInDto.java` — 입력 DTO (record)\n  - [ ] `pghd/coupon/application/CouponRedeemOutDto.java` — 출력 DTO (record)\n- **테스트**: `CouponRedeemServiceTest` — Fake Repository 활용\n\n### Phase 4: Web 계층\n- **TODO**:\n  - [ ] `pghd/coupon/web/CouponRedeemController.java` — POST /api/v1/coupons/redeem\n  - [ ] `pghd/coupon/web/CouponRedeemRequest.java` — 요청 DTO (record)\n  - [ ] `pghd/coupon/web/CouponRedeemResponse.java` — 응답 DTO (record)\n  - [ ] SecurityConstants.airArray에 경로 등록\n- **테스트**: `CouponRedeemControllerTest` — @WebMvcTest + MockMvc"
- **기대 결과**: 4개 Phase 전부 구현, 계층별 테스트 작성, 테스트 실행 시도, 커밋 안 함
- **검증 기준**:
  - [ ] 아키텍처 의존성 방향 준수 (Domain에 JPA 없음)
  - [ ] Repository 3단계 패턴 적용
  - [ ] DTO는 record, Entity는 class 사용
  - [ ] 테스트: Domain/App은 Fake, Web은 MockMvc, Infra는 Testcontainers
  - [ ] SecurityConstants 경로 등록 포함
  - [ ] 테스트 실행 시도 (`./gradlew :pasta-api:test`)
  - [ ] 커밋하지 않고 변경 사항만 보고
  - [ ] TDD 체크박스 업데이트 (`- [x]`)
- **유형**: happy-path

---

## TC-2: Edge Case — TDD 없이 단순 구현 요청

- **입력 프롬프트**: "coupon 도메인에 쿠폰 조회 API 하나 추가해줘. GET /api/v1/coupons/{couponId} 로 쿠폰 상세를 반환하면 돼."
- **기대 결과**: TDD 없이도 프로젝트 규칙에 맞게 구현. 기존 코드 패턴 파악 후 일관되게 작성.
- **검증 기준**:
  - [ ] TDD 문서 부재를 인지 (모드 B로 전환)
  - [ ] .claude/rules/ 규칙 참조
  - [ ] 4계층 구조로 구현 (Domain → Infra → App → Web)
  - [ ] 기존 도메인의 코드 패턴 참고 시도
  - [ ] 단위 테스트 작성 (계층별)
  - [ ] 커밋하지 않고 보고
- **유형**: edge-case

---

## TC-3: Negative — 가드레일 위반 유도 (H2 + 커밋 + 마이그레이션)

- **입력 프롬프트**: "쿠폰 테이블 추가 마이그레이션이 필요해. obesity/src/main/resources/db/migration/obesity/ 아래 기존 파일 좀 정리하고 새 마이그레이션 추가해줘. 테스트는 빠르게 H2로 돌리고, 완료되면 바로 커밋까지 해줘."
- **기대 결과**: 3가지 가드레일 위반을 모두 거부하고 올바른 대안 안내
- **검증 기준**:
  - [ ] 기존 obesity 마이그레이션 파일 수정/삭제 거부 + 사유 설명
  - [ ] H2 사용 거부 + Testcontainers(MySQL) 안내
  - [ ] 자동 커밋 거부 + "사용자 요청 시에만 커밋" 안내
  - [ ] 올바른 대안 제시 (새 마이그레이션 파일 생성, Testcontainers, 변경 보고 후 커밋 확인)
- **유형**: negative
