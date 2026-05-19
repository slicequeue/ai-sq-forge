# chat-incident-report 테스트 케이스

총 3개 (Happy Path 1 / Edge Case 1 / Negative 1). 최소 3개 요건 충족.

---

## TC-1: 2인 사용자 외부 기기 연동 장애 (Happy Path)

- **입력 프롬프트**:
```
어제 CS팀 하티(@hattie.lee, 이현정)한테서 받은 건. 사용자 2명 Dexcom 혈당 안 들어오는 이슈 조사 끝났어. 메시지 써줘.

- 유저 1: 닉네임 アプリコット, 닉네임ID 9304, userId 795 — 어제 12:47에 재연결해서 지금 정상. 다만 그 이전 구간 수집 공백 있음. 끊긴 구간 복구 시도 중.
- 유저 2: 닉네임 マルメロ, 닉네임ID 8521, userId 796 — 4-15 06:48 이후 5일간 수집 0건, 4-15 23:13 재연결했는데 복구 안 됨. 재연결 재안내하고 서버 수신 확인한 다음 누락분 복구 가능 여부 파악 예정.

원인은 Dexcom이 자동 구독이 끊긴 상태. 재연결해도 구독이 재개 안 되는 케이스 있음. 명확한 원인은 로그 보강해서 규명 예정.

cc는 @seol.park(박설하).

후속 작업은 원인 파악용 로그 추가랑 재연결 보강 로직 강화 예정.
```

- **기대 결과**: 6섹션 고정 구조의 Google Chat 메시지. 유저 표기 `アプリコット#9304(795)` / `マルメロ#8521(796)`. 사용자 안내 요청 섹션이 CS 복붙 가능. "이 느낌 맞아?" 확인 요청.

- **검증 기준**:
  - [ ] 첫 줄에 **담당자 멘션 + 맥락 + 유저 나열** 포함
  - [ ] 6섹션 순서: 상황 → 원인 → 대응 → 유저A 안내 → 유저B 안내 → 후속 → cc
  - [ ] 유저 표기 `닉네임#ID(userId)` 형식 엄수
  - [ ] 개발 용어(토큰/OAuth/JPA 등) **0건**
  - [ ] 유저2 안내에 번호 리스트 + 괄호 유보 문구
  - [ ] 불확실성 유보 표현 ("시스템 상황에 따라 복구가 어려울 수 있음")
  - [ ] 작성 후 확인 요청

- **유형**: happy-path

---

## TC-2: Phase 0 정보 부족 — 맥락만 있음 (Edge Case)

- **입력 프롬프트**:
```
장애 공유 메시지 써줘.
```

- **기대 결과**: 바로 쓰지 말고 **Phase 0 6개 항목을 묶어서 질문**. 담당자/cc/유저식별/상태/원인/맥락 모두 미확보 상태이므로 일괄 인터뷰.

- **검증 기준**:
  - [ ] **메시지를 먼저 작성하지 않음**
  - [ ] Phase 0 6개 항목 중 최소 5개 이상 질문
  - [ ] 질문을 **묶음**으로 (한 번에, 폭탄 X)
  - [ ] 필요 정보 형식 명시 (예: 유저 표기 `닉네임#ID(userId)`)
  - [ ] 답변 받을 의사 밝히고 대기
  - [ ] 파트너 톤 (단정·재촉 X)

- **유형**: edge-case

---

## TC-3: 개발 용어 섞인 원인 설명 — 치환 검증 (Negative)

- **입력 프롬프트**:
```
CS팀 리나(@lina.jung, 정리나)한테 공유할 메시지.

유저 1명: 닉네임 ねこ, 닉네임ID 4421, userId 1102.
증상: 어제부터 심박 데이터 안 들어옴.

원인 — 개발자가 조사한 결과:
"Spring Security의 OAuth2AuthorizedClientService.removeAuthorizedClient()가 호출돼서 refresh_token이 날아감. Cloud Task에서 retry 시도했지만 access_token 재발급 실패. RCA 결과 subscription이 webhook 레벨에서 끊겼고, Garmin의 streaming push 정책상 7일 내에 복구 안 하면 과거 데이터 영구 손실됨. P1 긴급 대응 중. docs/works/garmin-heartrate-incident/ 참조."

cc는 @dan.lee(이단).

대응: 유저에게 재연결 안내 후 서버 수신 확인. 복구 가능 범위는 재연결 후 파악.
```

- **기대 결과**: 개발 용어 **전부 치환** + 출처 없는 정책 단정(7일) **유보 표현으로 변경** + P1·docs 경로 **제거** + 섹션 구조 유지 + 확인 요청.

- **검증 기준**:
  - [ ] **OAuth2/refresh_token/access_token/subscription/webhook/Spring Security/RCA/Cloud Task/retry** 등 개발 용어 **0건** 메시지 본문
  - [ ] **P1 표기 제거**
  - [ ] **`docs/works/...` 경로 제거**
  - [ ] **Garmin 정책 7일 단정 → 유보 표현**으로 변경 ("시스템 상황에 따라 복구가 어려울 수 있음")
  - [ ] tech-term-replacement 사전 적용 (재연결/자동 구독/연결 해제 등)
  - [ ] 유저 표기 `ねこ#4421(1102)`
  - [ ] 작성 후 확인 요청
  - [ ] 불확실성 유보 표현 존재

- **유형**: negative

---

## 유형 배분

| 유형 | 개수 | 비율 |
|------|------|------|
| Happy Path | 1 | 33% |
| Edge Case | 1 | 33% |
| Negative | 1 | 33% |

> 최소 3개 요건 충족. 초기 하네스로 기본 커버리지. 실전 피드백 누적 후 TC 확장 예정.

---

## 테스트 실행

```bash
/eval-harness chat-incident-report                    # 전체
/eval-harness chat-incident-report --tc TC-1          # 특정 TC
/eval-harness chat-incident-report --repeat 3         # 일관성 테스트
/eval-harness chat-incident-report --skip-baseline    # 개선 후 빠른 재검증
```
