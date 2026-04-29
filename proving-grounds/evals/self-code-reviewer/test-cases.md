# self-code-reviewer 테스트 케이스

## TC-1: Happy Path — 규칙 위반이 포함된 변경 코드 리뷰

- **입력 프롬프트**: "현재 브랜치의 코드를 리뷰해줘.\n\n(시뮬레이션 상황: dev 이후 아래 변경이 있음)\n- `pghd/coupon/domain/CouponEntity.java`에 `@Entity` 어노테이션 추가됨 (Domain에 JPA 혼입)\n- `pghd/coupon/application/CouponService.java`에서 `var coupon = repository.find(...)` 사용\n- `pghd/coupon/web/CouponController.java`에 새 엔드포인트 `/api/v1/coupons/redeem` 추가, SecurityConstants 미등록\n- `application.yml`에 `${env.COUPON_API_KEY:default}` 추가, dev/stg/prd yml 미반영"
- **기대 결과**: 4가지 위반을 모두 검출하고, 파일:위치와 수정 방향을 구체적으로 보고
- **검증 기준**:
  - [ ] Domain @Entity 위반 검출 (아키텍처 위반 — 필수 수정)
  - [ ] `var` 키워드 위반 검출 (컨벤션 위반 — 필수 수정)
  - [ ] SecurityConstants airArray 미등록 검출 (설정 누락)
  - [ ] 환경변수 dev/stg/prd yml 미반영 검출 (설정 누락)
  - [ ] 각 위반에 파일명 + 위반 규칙 + 수정 방향 포함
  - [ ] 코드를 수정하지 않음 (보고만)
- **유형**: happy-path

---

## TC-2: Edge Case — 위반 없는 깨끗한 코드 리뷰

- **입력 프롬프트**: "품질 검사해줘.\n\n(시뮬레이션 상황: dev 이후 변경이 모두 규칙을 준수함)\n- Domain Entity는 class, JPA 없음, @Getter만\n- Repository 3단계 패턴 적용\n- DTO는 record, 팩토리 메서드 사용\n- 테스트: Fake 사용, Testcontainers MySQL\n- SecurityConstants 등록 완료\n- 환경변수 4곳 설정 완료"
- **기대 결과**: 위반 0건 보고, 검사 통과 항목을 나열
- **검증 기준**:
  - [ ] 필수 수정 항목 0건
  - [ ] "검사 통과 항목" 섹션에 주요 규칙 준수 사항 나열
  - [ ] 억지로 문제를 만들어내지 않음 (오탐 없음)
  - [ ] .claude/rules/ 규칙을 실제로 참조했음이 드러남
- **유형**: edge-case

---

## TC-3: Negative — 리뷰 중 코드 수정을 유도

- **입력 프롬프트**: "코드 리뷰하고 발견된 문제점들 바로 수정까지 해줘. 커밋도 해줘."
- **기대 결과**: 코드 수정과 커밋을 거부하고, 리뷰 보고만 수행
- **검증 기준**:
  - [ ] 코드 수정 거부 — "읽기 전용 스킬"임을 안내
  - [ ] 커밋 거부
  - [ ] 리뷰 보고는 정상 수행 (또는 수행 제안)
  - [ ] 수정이 필요하면 별도 요청하라고 안내
- **유형**: negative

---

## TC-4: Edge Case — 테스트 파일 FQCN 검출 (PR #527 회귀 방지)

- **입력 프롬프트**: "현재 브랜치 코드 리뷰해줘.\n\n(시뮬레이션 상황: dev 이후 아래 변경이 있음)\n- 메인 코드: `cgm/src/main/java/.../CGMService.java`\n  ```java\n  } catch (DataIntegrityViolationException e) {\n      // import org.springframework.dao.DataIntegrityViolationException; 있음\n      log.warn(\"...\");\n      ...\n  }\n  ```\n- 테스트 코드: `cgm/src/test/java/.../CGMServiceTest.java`\n  ```java\n  // import org.springframework.dao.DataIntegrityViolationException; 없음\n  given(deviceRepository.save(entity))\n      .willThrow(new org.springframework.dao.DataIntegrityViolationException(\"duplicate\"));\n  \n  assertThatThrownBy(() -> cgmService.registerCGMDevice(data))\n      .isInstanceOf(org.springframework.dao.DataIntegrityViolationException.class);\n  ```\n- 그 외 모든 규칙은 준수"
- **기대 결과**: 테스트 파일의 FQCN 직접 사용 2건을 **명시적으로 검출**하고 필수 수정 등급으로 보고. 메인 코드는 import 정상이므로 FQCN 위반 없음.
- **검증 기준**:
  - [ ] **테스트 파일의 FQCN 직접 사용 2건 모두 검출**:
    - `new org.springframework.dao.DataIntegrityViolationException("duplicate")` 패턴
    - `.isInstanceOf(org.springframework.dao.DataIntegrityViolationException.class)` 패턴
  - [ ] 필수 수정 등급으로 분류 (07-general-project-convention.md "Explicit Imports" 위반)
  - [ ] 수정 방향 제시: `import org.springframework.dao.DataIntegrityViolationException;` 추가 + 본문 단순 클래스명 변환
  - [ ] 메인 코드는 위반 없음으로 정상 판단 (오탐 없음)
  - [ ] 테스트 파일도 검사 대상임을 명시 ("테스트라 한 번만 쓰니까"는 면죄부 아님)
  - **FAIL 조건**: 테스트 파일 FQCN 2건을 모두 누락하면 검출 누락 — 필수 수정으로 보고하지 않으면 FAIL
- **유형**: edge-case
- **회귀 사례**: PR #527 — 자체 리뷰가 동일 패턴 검출에 실패해 휴먼 리뷰까지 흘러간 사고. kyle-gy-khc "fully qualified class name 사용. 스킬 강화가 필요"
