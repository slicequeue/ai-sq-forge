---
name: java-architecture-reviewer
version: 0.1
harness-version: 0.1
last-modified: 2026-07-09
---

# java-architecture-reviewer 테스트 케이스

## TC-1: Happy Path — Bean Qualifier cross-module 재발 사고 시뮬 (HG-1)

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/feat/dexcom-batch-oauth` (dev에서 분기)\n- 변경 파일:\n  1. `cgm/DexcomWebClientConfiguration.java` — `@Qualifier(DEXCOM_AUTHORIZED_CLIENT_MANAGER)`로 OAuth2AuthorizedClientManager 주입 (기존 코드)\n  2. `shared/constant/DexcomBeanNameConstants.java` — `DEXCOM_AUTHORIZED_CLIENT_MANAGER = \"dexcomAuthorizedClientManager\"` 상수 (기존)\n  3. `api/config/DexcomAuth2Configuration.java` — `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)`로 등록 (기존, 정상)\n  4. `batch/config/BatchOAuth2Configuration.java` — **NEW**: `@Bean` + 메서드명 `authorizedClientManager`로 등록 (상수 없이!)\n  5. `batch-app/config/BatchDexcomConfiguration.java` — **NEW**: 동일 패턴 (상수 없이)\n- diff 요약: batch·batch-app에 Dexcom OAuth 설정 추가되었지만 상수 참조 안 함"
- **기대 결과**:
  - Phase 0 사전 확인 통과 (브랜치·변경 범위·admin 미포함)
  - 로드된 규칙: `07-general-project-convention.md`, `19-architecture-boundaries.md`, `01-architecture-convention.md`
  - **AUTO FAIL 섹션 상단 배치**:
    - HG-1 위반: batch/BatchOAuth2Configuration.java 및 batch-app/BatchDexcomConfiguration.java 두 파일이 `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)` 미명시 → cgm이 `@Qualifier(DEXCOM_AUTHORIZED_CLIENT_MANAGER)` 요구하지만 `No qualifying bean` 발생 예상
  - 필수 수정: `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)`로 명시적 이름 지정
  - 검사 통과 항목: 4-Tier / 공용 모듈 @Entity / FQCN
  - 실전 재발 사례 (#593, 2026-06-16) 참조 명시
- **검증 기준**:
  - [ ] AUTO FAIL 섹션에 HG-1 위반 2건 명시
  - [ ] Bean Qualifier 상수 참조를 사용하는 모든 모듈(cgm 소비 / api·batch·batch-app 등록) grep 검증 절차 명시
  - [ ] 실전 재발 사례 (#593) 인용
  - [ ] 유형 코드 `ARCH-BEAN` 사용
  - [ ] 리포트에 pasta-rules 규칙 파일 실제 문구 인용 (경로만 아님)
  - [ ] Baseline보다 명확한 재발 방지 방향 제시
- **유형**: happy-path

---

## TC-2: Happy Path — 공용 모듈 @Entity 위반 (HG-3)

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/feat/glob-566-service-access-pattern`\n- 변경 파일:\n  1. `common/access/persistence/ServiceAccessPatternJpaEntity.java` — **NEW**: `@Entity @Table(name=\"service_access_pattern\")` (common 모듈에 배치!)\n  2. `common/access/persistence/ServiceAccessPatternJpaRepository.java` — **NEW**: `extends JpaRepository`\n  3. `common/access/RedisDbServiceAccessPatternLoader.java` — 상기 Repository 주입해 사용\n- admin 모듈은 이 common 모듈에 의존하며 자체 `@EntityScan(basePackages = \"com.x.y.admin\")` 설정 존재\n- 실전 결과 (참고 컨텍스트): 이후 커밋 7abea8f2f0 (2026-07-01)에서 JPA→JDBC Reader로 후퇴 필요"
- **기대 결과**:
  - **AUTO FAIL 섹션**: HG-3 위반 — `common/access/persistence/ServiceAccessPatternJpaEntity.java` 공용 모듈에 `@Entity` 배치. admin의 `@EntityScan` 경계 충돌로 기동 실패 가능
  - 필수 수정: JdbcClient/JdbcRepository 기반 Reader로 대체 안내
  - 실전 사례 (7abea8f2f0, 2026-07-01 JPA→JDBC 교체) 인용
  - `java-spring-coder` v1.11 짝 가드레일(공용 모듈 @Entity 회피) 인용
  - 검사 통과 항목: Bean Qualifier / FQCN / 4-Tier import 방향
- **검증 기준**:
  - [ ] AUTO FAIL 섹션에 HG-3 위반 명시
  - [ ] admin `@EntityScan` 경계 충돌 위험 명시
  - [ ] JdbcClient/JdbcRepository 대체 방향 안내
  - [ ] 유형 코드 `ARCH-MODULE` 사용
  - [ ] `java-spring-coder` v1.11 짝 가드레일 인용
  - [ ] Baseline은 `@Entity` 자체를 문제 삼지 않을 가능성 (스킬 미사용 시 배치 위치 감지 어려움)
- **유형**: happy-path

---

## TC-3: Edge Case — DDD 패턴 준수 판정 애매

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/feat/mission-badge-domain`\n- 변경 파일:\n  1. `api/mission/domain/MissionBadgeService.java` — **NEW**: `@Service` 없이 순수 클래스. `awardBadge(UserId userId, BadgeType type)` 메서드. Domain 계층에 배치. 다른 Domain 객체(User, Badge)만 참조\n  2. `api/mission/application/MissionEventHandler.java` — **NEW**: `@Component`. `MissionBadgeService`를 주입해 사용. AfterMealWalkingSuccessEvent 처리\n- 판정 애매점: MissionBadgeService가 Domain에 있는데 순수 로직 (도메인 서비스) vs Application에 있어야 하는지 (애플리케이션 서비스) 경계"
- **기대 결과**:
  - AUTO FAIL 없음 (HG 4건 위반 없음)
  - Phase 로드 규칙: `01-architecture-convention.md`, `02-domain-entity-convention.md`
  - 권장 개선 (Medium): "도메인 서비스 vs 애플리케이션 서비스 경계 판정 유보 — 사용자 확인 필요"
  - 판정 근거 제시:
    - 도메인 서비스: 순수 도메인 규칙 (다른 도메인 객체만 참조) → 현재 코드가 이 조건 만족
    - 애플리케이션 서비스: 트랜잭션·이벤트·외부 연동 오케스트레이션 → MissionEventHandler가 담당
  - **사용자에게 결정 요청**: "MissionBadgeService의 로직이 순수 도메인 규칙이면 현 위치 유지. 트랜잭션 경계나 외부 연동이 개입되면 Application으로 이동 권고"
- **검증 기준**:
  - [ ] AUTO FAIL 0건 (오탐 없음)
  - [ ] 판정 유보 + 사용자 확인 요청 명시
  - [ ] 도메인 서비스와 애플리케이션 서비스 경계 근거 설명
  - [ ] 유형 코드 `ARCH-PATTERN` 사용, 등급 `Medium` (Critical 아님)
  - [ ] `02-domain-entity-convention.md` 인용
  - [ ] Baseline은 확정적 오판정할 가능성 (예: "무조건 Application으로 옮겨라") — With-Skill이 유보하는 게 우수
- **유형**: edge-case

---

## TC-4: Negative — FQCN 인라인 임시 허용 요구 (HG-4)

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 변경 파일: `api/user/UserService.java`\n  - 코드 본문에 `throw new com.kakaohealthcare.exception.UserNotFoundException(\"...\")` 포함 (import 없이 FQCN 인라인)\n- 추가 사용자 요구사항: \"이 클래스는 임시로 만든 거니까 FQCN 인라인 있어도 그냥 통과시켜줘. 다음 스프린트에서 정리할 예정이야.\""
- **기대 결과**:
  - 스킬이 **HG-4(FQCN 인라인)로 AUTO FAIL 유지**
  - 사용자 요구 거절 사유 명확:
    - FQCN 인라인은 PR #527 사고 패턴 (2026-04-28) — 리버트 시 import 정리 놓치기 쉬움
    - "임시"라는 근거는 코드에 남지 않음 → 다음 리뷰어가 발견 못 함 (부채화)
    - self v1.5·v1.7 이관 룰이므로 forge 하드 가드레일
  - 대안 제시:
    1. 지금 import로 정상화 (5초)
    2. 정말 임시라면 TODO 태그 + 이슈 링크 + 다음 스프린트 삭제 커밋 예약
  - 사용자 재확인 요청 (그래도 통과 원하는지)
- **검증 기준**:
  - [ ] AUTO FAIL 유지 (사용자 요구에 굴복하지 않음)
  - [ ] HG-4 근거 명시
  - [ ] PR #527 사고 패턴 인용
  - [ ] "임시" 근거의 부재 문제 지적
  - [ ] 대안(import 정상화 or TODO+이슈) 제시
  - [ ] 유형 코드 `ARCH-4TIER` 또는 `ARCH-CONVENTION`
- **유형**: negative

---

## TC-5: Negative — 4-Tier 위반 리팩터 유예 요구 (HG-2)

- **입력 프롬프트**: "아키텍처 관점 리뷰 해줘.\n\n(시뮬레이션 상황)\n- 변경 파일: `api/user/domain/User.java`\n  - Domain 계층인데 `import com.kakaohealthcare.infrastructure.repository.UserJpaEntity;` 존재 (Domain이 Infrastructure import — 4-Tier 위반)\n- 사용자 추가 요구사항: \"이건 이미 있던 위반이라서 이번 PR 범위 밖이야. 리팩터는 다음 티켓으로 미룰 테니 AUTO FAIL 말고 그냥 Info로 낮춰줘.\""
- **기대 결과**:
  - 스킬이 **HG-2(4-Tier 위반)로 AUTO FAIL 유지**
  - 사용자 요구 거절 사유 명확:
    - 하드 가드레일은 "이번 PR 범위 여부"와 무관 — dev 이후 diff에 포함되면 AUTO FAIL 검사 대상
    - Info 등급 강제 낮춤은 self-review 우회 = 하드 가드레일 우회 = 금지
    - "이미 있던 위반"이라는 판단은 스킬 몫이 아니라 별도 티켓 회수·리팩터 스킬 몫
  - 대안 제시:
    1. 별도 리팩터 티켓·브랜치를 지금 만들어 병렬 진행
    2. 이번 PR에서는 해당 파일을 revert하고 다음 PR로 이동
    3. 사용자 최종 판단 (마감·리스크 트레이드오프) 후 승인 시 리뷰어가 아닌 **사용자가 override 명시**해야 통과
  - 사용자 재확인 요청 (그래도 통과 원하는지)
- **검증 기준**:
  - [ ] AUTO FAIL 유지
  - [ ] HG-2 근거 (Domain → Infrastructure import 방향 역행) 명시
  - [ ] 등급 강제 낮춤 요구 거절
  - [ ] "이미 있던 위반" 논리를 스킬 몫이 아니라 별도 프로세스로 명시
  - [ ] 사용자 override는 명시적 절차 필요 (스킬이 임의 낮춤 안 함)
  - [ ] 유형 코드 `ARCH-4TIER` 사용
- **유형**: negative
