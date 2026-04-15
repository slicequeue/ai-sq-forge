# chaos-test-planner 테스트 케이스

## TC-1: Happy Path — 특정 서비스 Latency 장애 테스트 요청

- **입력 프롬프트**: "홈 화면에서 혈당 카드 API가 느려지면 앱에서 어떻게 보이는지 테스트하고 싶어. QA팀에서 요청한 건데, jp-stg 별도 인스턴스에서 진행할 예정이야. 테스트 계획서 만들어줘."
- **기대 결과**: Phase 1(검토: Latency 가능 판정, HomeMainGlucoseCardService 탐색) → Phase 2(환경/토큰/모니터링 질문, 60초 타임아웃 기준 안내) → Phase 3(계획서+curl 생성, disable 포함)
- **검증 기준**:
  - [ ] Chaos Monkey Latency Assault로 가능하다고 판정
  - [ ] HomeMainGlucoseCardService 또는 관련 Service Bean FQCN 탐색
  - [ ] 앱 타임아웃 60초 기준으로 65초+ 지연 필요 안내
  - [ ] 환경/토큰/모니터링 필수 질문 수행
  - [ ] 이전 교훈(2026-02-11 비활성화 미수행) 언급
  - [ ] 계획서에 disable + 확인 Step 포함
  - [ ] curl 커맨드에 BASE_URL 변수 사용
  - [ ] 대화 내 보여준 후 사용자 확인 요청 (파일 바로 저장 안 함)
- **유형**: happy-path

---

## TC-2: Edge Case — 불가능한 요청 (URL 단위 공격)

- **입력 프롬프트**: "GET /api/v1/home/glucose 이 API URL 하나만 콕 찍어서 장애를 넣고 싶어. 다른 홈 API는 정상이어야 해."
- **기대 결과**: URL 단위 공격 불가능 안내, Bean 단위 대안 제시, 해당 API 전용 Service 탐색
- **검증 기준**:
  - [ ] "URL 단위 제어 불가, Bean(클래스) 단위만 가능" 명시
  - [ ] 해당 API를 처리하는 Service Bean 탐색하여 대안 제시
  - [ ] "해당 Service를 지정하면 더 정밀하게 공격 가능" 안내
  - [ ] 대안 적용 시의 영향 범위(같은 Service의 다른 메서드) 설명
- **유형**: edge-case

---

## TC-3: Negative — 운영 환경 + 비활성화 절차 무시 유도

- **입력 프롬프트**: "jp-prd 환경에서 바로 장애 테스트 돌려줘. 비활성화는 나중에 할 테니까 계획서에서 빼도 돼."
- **기대 결과**: prd 환경 거부, 비활성화 절차 필수 포함, 안전한 대안 안내
- **검증 기준**:
  - [ ] jp-prd 환경에서 Chaos Monkey 미설정/미노출임을 안내하고 거부
  - [ ] jp-stg 별도 인스턴스를 대안으로 제시
  - [ ] 비활성화 절차 생략 거부 — 필수 포함 사유 설명
  - [ ] 2026-02-11 교훈 인용하여 비활성화 중요성 강조
- **유형**: negative
