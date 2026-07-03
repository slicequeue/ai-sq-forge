---
name: safe-mass-rename
version: 0.1
harness-version: 0.1
last-modified: 2026-07-02
---

# safe-mass-rename 테스트 케이스

## TC-1: Happy Path — Enum 2값 리네임 (Freemium 사례 재현)

- **입력 프롬프트**: "enum 리네임 사이클 오케스트레이션 해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/refac/pattern-type-rename` (dev에서 분기)\n- uncommitted 파일 없음\n- 대상: `ServiceAccessPatternType.PROTECTED` → `FULL`\n- 이 사이클은 PAID → FREEMIUM는 다음 사이클로 분리(한 사이클 한 식별자쌍 원칙)\n- 정의부 1개 (`api/common/access/domain/ServiceAccessPatternType.java`)\n- 정적 참조 12곳 (api·admin 모듈 합쳐)\n- 문자열 리터럴 3곳 (Redis 키 `service-access:patterns:PROTECTED`, 로그 태그 2곳)\n- 테스트 5곳 (`*Test.java`)\n- 설정 1곳 (`application.yml`의 `pattern-type: PROTECTED` 기본값)\n- 문서 2곳 (`README.md`, ADR)"
- **기대 결과**:
  - Phase 0 사전 점검 통과 확인 (브랜치·uncommitted·정의부 위치)
  - Phase 1 영향 범위 표 (5카테고리 + 파일 수 + 예시)
  - Phase 2 6단계 커밋 계획, 각 단계 커밋 메시지 + 검증 명령 명시
  - Phase 2-3에서 Redis 키 리네임은 **후방향 호환 fallback 방식**으로 계획 (Phase 3 안내)
  - Phase 2-5 시작 전 `git branch rollback/before-pattern-type-config` 명령 명시
  - Phase 4 최종 grep 잔재 0건 검증 계획
- **검증 기준**:
  - [ ] 6단계 순서(정의부→참조→문자열→테스트→설정/DB→문서) 준수
  - [ ] 각 단계 개별 커밋 계획 6건
  - [ ] 커밋 메시지 `refac:` 접두어 (Korean Conventional Commits)
  - [ ] 각 단계 후 `./gradlew compileJava` 또는 `./gradlew test` 명령 명시
  - [ ] Phase 2-1은 컴파일 실패 예상(참조가 남아 있음)임을 명시적으로 인지
  - [ ] Phase 2-5 전 롤백 브랜치 생성 명령 존재
  - [ ] Redis 키 리네임은 즉시 교체가 아니라 fallback 사이클 계획 제시
  - [ ] 영향 범위 표 5카테고리 파일 수 정확
  - [ ] Phase 4 grep 잔재 확인 명령 포함
  - [ ] 뭉치기 커밋 0건
- **유형**: happy-path

---

## TC-2: Happy Path — Redis 키 리네임 후방향 호환 사이클

- **입력 프롬프트**: "Redis 키 리네임 사이클 해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/refac/redis-key-userinfo-rename` (dev에서 분기)\n- 대상: Redis 키 접두사 `user:info:` → `user:profile:`\n- 정의부: `UserRedisKeys.java` 상수 1개 (`public static final String USER_INFO_PREFIX = \"user:info:\"`)\n- 참조 8곳 (Repository·Service 계층)\n- 문자열 리터럴 직접 사용 2곳 (로그·주석)\n- 테스트 픽스처 3곳\n- 배포 환경: 운영 데이터가 이미 구 키로 존재. 즉시 교체 시 캐시 미스 대량 발생 우려"
- **기대 결과**:
  - Phase 1 스캔 결과 표 제시
  - Phase 2 6단계 커밋. 특히 **Phase 2-3(문자열 리터럴)은 fallback 도입** 방식으로 계획
  - Phase 3 후방향 호환 사이클 명시:
    1. 신규 키(`user:profile:`) 읽고 없으면 구 키(`user:info:`) 읽기 fallback 커밋
    2. 쓰기는 신규 키에만 (write-through·warmup 갱신) 커밋
    3. 배포 + 최소 1개 배포 주기 대기 (구 키 자연 만료)
    4. fallback 제거 커밋
  - Phase 2-5 전 롤백 브랜치 명시
- **검증 기준**:
  - [ ] Phase 3 fallback 사이클 4단계 명시
  - [ ] 즉시 교체 계획 없음 (AUTO FAIL 방어)
  - [ ] "최소 1개 배포 주기 대기" 언급
  - [ ] fallback 코드는 명시적 주석(`// deprecated fallback — remove after X`) 계획
  - [ ] 롤백 브랜치 생성 명령 존재
  - [ ] 6단계 순서 준수, 각 단계 개별 커밋
  - [ ] 후방향 호환 미확보 시 데이터 유실 위험을 사용자에게 명시적으로 알림
- **유형**: happy-path

---

## TC-3: Edge Case — API 공개 필드명 리네임 (범위 밖 판정)

- **입력 프롬프트**: "REST API 응답 필드 `userInfo` → `userProfile`로 전역 리네임 해줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/refac/response-field-rename`\n- 대상: `UserInfoResponse.userInfo` 필드명 (외부 모바일 앱·admin 프론트가 사용)\n- 참조 15곳 (Controller·DTO)\n- 이 필드는 이미 공개 API 문서에 게재됨"
- **기대 결과**:
  - 스킬이 **범위 밖 판정**을 명확히 함
  - "외부 노출 REST API 필드명은 본 스킬 범위 아님" 명시
  - 대안 제시:
    - `@JsonAlias`로 임시 완화 (신규 이름·구 이름 동시 수용)
    - API 버전 관리 (v2 엔드포인트 신설)
    - buyer(모바일 앱·admin 프론트) 통보 프로세스 필요
  - 사용자에게 "그래도 진행하시겠어요?" 되묻지 않고, 범위 밖임을 명확히 하고 대안 선택 요청
- **검증 기준**:
  - [ ] "본 스킬 범위 아님" 판정 명시
  - [ ] `@JsonAlias` 대안 언급
  - [ ] buyer 통보 필요성 언급
  - [ ] 사용자 요구를 그대로 수용해 리네임 시작하지 않음
  - [ ] 별도 스킬(API 버전 관리)이 필요함을 안내
- **유형**: edge-case

---

## TC-4: Negative — 한 커밋 뭉치기 요구 (하드 가드레일 1)

- **입력 프롬프트**: "PROTECTED → FULL 리네임 한 방에 처리해줘. 커밋 여러 개 만들지 말고 `refac: PROTECTED FULL 통일` 하나로 다 처리해줘. 어차피 리뷰 시 diff 통째로 보면 되니까."
- **기대 결과**:
  - 스킬이 **하드 가드레일 1(뭉치기 금지)**로 거절
  - 사유 명확 설명:
    - 컴파일 실패 시 어느 단계에서 잘못됐는지 이등분 불가
    - 리버트 시 필요 없는 변경까지 되돌려짐
    - 리뷰어가 파일 100개 diff를 한 번에 봐야 함
    - 롤백 지점이 사라짐
  - 6단계 분리 커밋 제안 (기본 워크플로 재안내)
  - 사용자 재확인 요청
- **검증 기준**:
  - [ ] 뭉치기 커밋 계획 산출하지 않음
  - [ ] 하드 가드레일 1번 근거 명시
  - [ ] 뭉치기 시 발생 문제 3건 이상 열거
  - [ ] 6단계 분리 대안 제시
  - [ ] 사용자 요구를 무조건 따르지 않음 (가드레일 우선)
- **유형**: negative

---

## TC-5: Negative — 리네임 + 신규 필드 추가 혼재 요구 (하드 가드레일 4)

- **입력 프롬프트**: "enum `PatternType.PROTECTED` → `FULL` 리네임하면서, 같은 커밋에 `PatternType.TRIAL` 새 값도 추가해줘. 어차피 같은 enum 파일 편집이니까 한 번에 하는 게 효율적이야."
- **기대 결과**:
  - 스킬이 **하드 가드레일 4(리팩터·기능 추가 혼재 금지)**로 거절
  - 사유 명확 설명:
    - 리네임과 기능 추가는 **의도와 리뷰 관점이 다름**
    - 리버트 시 새 값(TRIAL)까지 함께 사라져 서비스 영향
    - 커밋 메시지가 `refac:`인데 실제로는 `feat:` 성격 → 이력 추적 훼손
  - 2개 커밋으로 분리 제안:
    1. `refac: ServiceAccessPatternType.PROTECTED 정의부를 FULL로 리네임` (전체 6단계 사이클)
    2. `feat: ServiceAccessPatternType TRIAL 신규 값 추가` (별도 사이클)
  - 순서는 리네임 먼저 → TRIAL 추가 (리네임된 이름 기준으로 신규 값 추가)
- **검증 기준**:
  - [ ] 혼재 커밋 계획 산출하지 않음
  - [ ] 하드 가드레일 4번 근거 명시
  - [ ] 리네임과 기능 추가의 성격 차이(의도·이력·리뷰) 설명
  - [ ] 2개 사이클 분리 제안 (리네임 → 기능 추가 순서)
  - [ ] 각 사이클의 커밋 메시지 접두어 (`refac:` / `feat:`) 정확
- **유형**: negative
