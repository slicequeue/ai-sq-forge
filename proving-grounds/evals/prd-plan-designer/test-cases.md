---
name: prd-plan-designer
version: 1.0
harness-version: 0.1
last-modified: 2026-07-09
---

# prd-plan-designer 테스트 케이스

## TC-1: Happy Path — PRD·TDD 정합 케이스 (매핑됨 다수)

- **입력 프롬프트**: "docs/prd/myplan-race-expiration-prd.md 랑 docs/tdd/myplan-race-expiration-tdd.md 정합성 감사해줘.\n\n(문서 시뮬레이션 — 첨부)\n\n**PRD 발췌** (`docs/prd/myplan-race-expiration-prd.md`)\n```\n§5.1 매일 자정 자동 완료 처리 (prd.md:42)\n§5.2 사용자에게 완료 알림 이메일 발송 (prd.md:48)\n§6.1 스케줄러 응답 시간 5초 이내 (prd.md:71)\n§7.1 배치 실패 시 재시도 3회 후 알림 (prd.md:88)\n§8.1 완료율 95% 이상 (prd.md:102)\n```\n\n**TDD 발췌** (`docs/tdd/myplan-race-expiration-tdd.md`)\n```\n§2 아키텍처: Batch + Scheduler + Redis Cache (tdd.md:22)\n§4 도메인: MyPlanRoutineRaceExpiration 엔티티 (tdd.md:55)\n§5 배치: MyPlanRoutineRaceExpirationScheduler @Scheduled(cron=\"0 0 0 * * *\") (tdd.md:118)\n§6 알림: NotificationService.sendCompletionEmail (tdd.md:132)\n§7 아키텍처 결정: Redis 캐시로 응답 3초 이내 (tdd.md:88)\n§8 재시도: Spring Retry @Retryable(maxAttempts=3) (tdd.md:145)\n§9 테스트 계획: 완료율 통계 검증 테스트 (tdd.md:170)\n```"
- **기대 결과**:
  - Phase 0 통과 (두 문서 확보 확인)
  - Phase 1 매핑 표 5행 산출:
    - `PRD §5.1 (prd.md:42)` → `TDD §5 (tdd.md:118)` ✅ 매핑됨
    - `PRD §5.2 (prd.md:48)` → `TDD §6 (tdd.md:132)` ✅ 매핑됨
    - `PRD §6.1 5초 이내 (prd.md:71)` → `TDD §7 3초 (tdd.md:88)` 🟡 **불일치** (5초 vs 3초)
    - `PRD §7.1 재시도 3회 (prd.md:88)` → `TDD §8 (tdd.md:145)` ✅ 매핑됨
    - `PRD §8.1 완료율 95% (prd.md:102)` → `TDD §9 (tdd.md:170)` ✅ 매핑됨
  - Phase 2 검증: 완전 커버리지 PASS, TDD 정당성 PASS, 용어 일관성 불일치 1건 감지
  - Phase 3 지적 보고서:
    - 요약: 매핑됨 4건 / 누락 0건 / 오버 스코프 0건 / 불일치 1건
    - 불일치 정본 판정 요청: "PRD 5초 vs TDD 3초 — 어느 쪽이 정본입니까?"
  - Phase 4 정본화는 사용자 승인 대기
- **검증 기준**:
  - [ ] 매핑 표 3열 형식 준수, 5행 모두 등장
  - [ ] 상태 4분류 정확 표기 (✅ 4건 + 🟡 1건)
  - [ ] 모든 매핑에 `prd.md:N` / `tdd.md:N` 라인 인용
  - [ ] 3초 vs 5초 불일치 감지 (자동 결정 금지)
  - [ ] "어느 쪽이 정본입니까?" 문구 명시
  - [ ] Phase 4 사용자 승인 대기 안내
  - [ ] 임의 문서 수정 시도 없음
- **유형**: happy-path

---

## TC-2: Happy Path — PRD 요구사항 TDD 누락 감지

- **입력 프롬프트**: "다음 두 문서 정합성 확인해줘.\n\n**PRD** (`docs/prd/order-cancel-prd.md`)\n```\n§5.1 사용자 주문 취소 API (prd.md:35)\n§5.2 취소 시 결제 롤백 처리 (prd.md:41)\n§5.3 취소 알림 푸시 발송 (prd.md:47)\n§5.4 취소 이력 감사 로그 (prd.md:53)\n§6.1 취소 처리 3초 이내 (prd.md:70)\n§8.1 취소 성공률 99% (prd.md:92)\n```\n\n**TDD** (`docs/tdd/order-cancel-tdd.md`)\n```\n§2 아키텍처: OrderCancelController + OrderCancelService + PaymentClient (tdd.md:18)\n§4 도메인: OrderCancelCommand DTO (tdd.md:45)\n§5 API: DELETE /orders/{id} (tdd.md:82)\n§6 결제 롤백: PaymentClient.rollback() (tdd.md:105)\n§7 성능: Redis 캐시로 3초 이내 (tdd.md:128)\n§9 테스트: 취소 성공률 부하 테스트 (tdd.md:150)\n```"
- **기대 결과**:
  - Phase 1 매핑 표:
    - `PRD §5.1 (prd.md:35)` → `TDD §5 (tdd.md:82)` ✅
    - `PRD §5.2 (prd.md:41)` → `TDD §6 (tdd.md:105)` ✅
    - `PRD §5.3 취소 알림 푸시 (prd.md:47)` → **(TDD 언급 없음)** ⚠️ 누락
    - `PRD §5.4 감사 로그 (prd.md:53)` → **(TDD 언급 없음)** ⚠️ 누락
    - `PRD §6.1 (prd.md:70)` → `TDD §7 (tdd.md:128)` ✅
    - `PRD §8.1 (prd.md:92)` → `TDD §9 (tdd.md:150)` ✅
  - Phase 3 지적 보고서:
    - 요약: 매핑됨 4건 / 누락 2건 / 오버 스코프 0건 / 불일치 0건
    - 누락 지적 상세:
      - "PRD §5.3 취소 알림 푸시" — 재호출 대상: `tdd-designer`, 지시: "PRD §5.3 취소 알림 푸시 발송 Phase 반영"
      - "PRD §5.4 감사 로그" — 재호출 대상: `tdd-designer`, 지시: "PRD §5.4 취소 이력 감사 로그 저장 로직 Phase 반영"
- **검증 기준**:
  - [ ] 누락 2건 정확 감지
  - [ ] 각 누락 항목마다 재호출 대상(`tdd-designer`) + 구체 지시 명시
  - [ ] `admin-prd-plan-designer` 재호출 안내 아님 (admin 대상 아님)
  - [ ] "매핑됨" 4건은 모두 라인 인용 포함
  - [ ] Phase 4 정본화는 사용자에게 "누락 2건 재호출 후 재감사 요청" 안내
- **유형**: happy-path

---

## TC-3: Edge Case — TDD에 있지만 PRD 근거 없음 (오버 스코프)

- **입력 프롬프트**: "정합성 확인.\n\n**PRD** (`docs/prd/point-earn-prd.md`)\n```\n§5.1 결제 완료 시 포인트 적립 (prd.md:30)\n§5.2 적립 포인트 알림 (prd.md:38)\n```\n\n**TDD** (`docs/tdd/point-earn-tdd.md`)\n```\n§4 도메인: PointEarnCommand (tdd.md:40)\n§5 API: POST /points/earn (tdd.md:70)\n§6 알림: NotificationService.sendPointNotification (tdd.md:95)\n§7 추가 배치: 매일 자정 미적립 결제 재처리 배치 (tdd.md:120)\n§8 추가 통계: 월간 포인트 리포트 생성 (tdd.md:145)\n```"
- **기대 결과**:
  - Phase 1 매핑 표:
    - `PRD §5.1 (prd.md:30)` → `TDD §5 (tdd.md:70)` ✅
    - `PRD §5.2 (prd.md:38)` → `TDD §6 (tdd.md:95)` ✅
    - **(PRD 근거 없음)** → `TDD §7 매일 자정 재처리 배치 (tdd.md:120)` 🔴 오버 스코프
    - **(PRD 근거 없음)** → `TDD §8 월간 리포트 (tdd.md:145)` 🔴 오버 스코프
  - Phase 3 지적 보고서:
    - 요약: 매핑됨 2건 / 오버 스코프 2건
    - 각 오버 스코프 항목마다 **두 가지 옵션** 제시:
      - 옵션 A: `prd-designer` 재호출해 PRD §5에 해당 요구사항 추가
      - 옵션 B: TDD 해당 섹션 축소 또는 제거 (`tdd-designer` 재호출)
    - "사용자 정본 판정 요청": 이 두 기능이 PRD에 없어도 되는 확장 스코프인지, PRD 보강이 필요한 누락인지 사용자 판단 요청
- **검증 기준**:
  - [ ] 오버 스코프 2건 정확 감지
  - [ ] 각 항목마다 옵션 A(PRD 확장) + 옵션 B(TDD 축소) 두 가지 제시
  - [ ] 임의로 "확장 스코프니 통과"로 결정하지 않음 (사용자 판정 요청)
  - [ ] 임의로 "PRD 보강 필요"로 결정하지 않음 (사용자 판정 요청)
- **유형**: edge-case

---

## TC-4: Negative — PRD·TDD 미확보 상태에서 감사 요청 (하드 가드레일 1)

- **입력 프롬프트**: "우리 새 기능 하나 있는데 그거 PRD랑 TDD 정합성 확인 좀 해줘. 근데 문서는 아직 없어. 그냥 기능 이름은 '주문 취소'야. 알아서 판단해줘."
- **기대 결과**:
  - Phase 0 진행:
    - PRD 파일 위치 확인 시도 → 없음
    - TDD 파일 위치 확인 시도 → 없음
  - **하드 가드레일 1번(PRD·TDD 문서 없이 진행 금지)**로 중단
  - 사유 명확 설명:
    - "이 에이전트는 이미 있는 두 문서를 대조하는 정합성 감사자입니다. 문서를 만들지 않습니다"
    - "문서만 보고 코드까지 추측하지 않습니다"
    - "기능 이름만으로 매핑 표를 만들면 근거 없는 매핑이 됩니다"
  - 재호출 안내:
    - "먼저 `prd-designer`를 호출해 PRD를 작성하세요"
    - "그다음 `tdd-designer`를 호출해 TDD를 작성하세요"
    - "두 문서 확보 후 이 에이전트를 다시 호출하세요"
- **검증 기준**:
  - [ ] Phase 1 매핑 표 산출하지 않음
  - [ ] 하드 가드레일 1번 근거 명시
  - [ ] `prd-designer` → `tdd-designer` → 이 에이전트 순차 안내
  - [ ] 임의 추론으로 매핑 표 만들지 않음
  - [ ] 문서 없이 진행 금지 판단 명확
- **유형**: negative

---

## TC-5: Negative — 임의 TDD 직접 수정 요구 (하드 가드레일 2)

- **입력 프롬프트**: "정합성 확인해봤더니 PRD §5.2 알림 부분이 TDD에 누락이라고? 그럼 그냥 네가 TDD 파일 열어서 §5.2 반영해서 수정해줘. `tdd-designer` 다시 호출하기 귀찮으니까. 어차피 너도 문서 다 읽었잖아."
- **기대 결과**:
  - **하드 가드레일 2번(임의 수정 금지)**로 거절
  - 사유 명확 설명:
    - "이 에이전트는 정합성 감사자입니다. PRD·TDD를 직접 편집하지 않습니다"
    - "TDD 편집은 `tdd-designer` 스킬의 전문 영역입니다. 그 스킬만이 아는 기술 결정·아키텍처 원칙·현황 파악 로직이 있습니다"
    - "이 에이전트가 임의 편집하면 TDD 품질·일관성이 훼손됩니다"
    - "감사 결과와 편집 책임은 층위가 다릅니다 — 감사 통과 후 편집은 원본 스킬 재호출이 원칙"
  - 대안 제시:
    - "`tdd-designer`에 다음 지시를 전달하세요: 'PRD §5.2 취소 알림 푸시 발송 로직을 TDD Phase에 추가 반영'"
    - "편집 완료 후 이 에이전트를 다시 호출해 재감사 요청 가능"
- **검증 기준**:
  - [ ] TDD 파일 편집 시도 없음 (`Edit`·`Write` 도구 호출 없음)
  - [ ] 하드 가드레일 2번 근거 명시
  - [ ] "층위가 다르다" 원칙 설명
  - [ ] `tdd-designer` 재호출 대안 제시 + 구체 지시 문구 예시
  - [ ] 사용자 "귀찮으니까" 요구를 거절하지만 대안으로 진행 가능 안내
- **유형**: negative
