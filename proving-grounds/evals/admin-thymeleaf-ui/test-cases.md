# admin-thymeleaf-ui 테스트 케이스

## TC-1: Happy Path — M1 신규 화면 생성

- **입력 프롬프트**: "admin 모듈에 '쿠폰 관리' 목록 페이지를 새로 만들어줘. 쿠폰 목록을 테이블로 보여주고, 등록 버튼 누르면 모달이 뜨면서 쿠폰 정보를 입력할 수 있게 해줘. 사이드바 메뉴에도 추가해야 해."
- **기대 결과**: M1 모드 선택, Controller + Template + Page JS + Sidebar 수정, 파일 계획표 작성
- **검증 기준**:
  - [ ] M1 모드 선택 및 보고
  - [ ] 유사 화면(예: BannerController) 탐색 수행
  - [ ] 파일 계획표 작성 (Controller, Template, JS, Sidebar 포함)
  - [ ] layout:decorate + layout:fragment 적용
  - [ ] URL-View-File 3점 정합
  - [ ] @PreAuthorize 권한 설정
  - [ ] CSRF 동적 헤더 사용 (fetch 시)
  - [ ] AdminLTE 구조(content-wrapper, content-header) 사용
  - [ ] 사이드바 링크+매핑 URL+권한 동시 정합
  - [ ] Self-check 결과표 제출
- **유형**: happy-path

---

## TC-2: Edge Case — M2 기존 화면 개선

- **입력 프롬프트**: "배너 관리 페이지에 '노출 기간' 필드를 추가하고, 기간 만료된 배너는 회색으로 표시해줘. 배너 등록 모달에도 기간 입력 필드를 넣어줘."
- **기대 결과**: M2 모드 선택, 기존 BannerController/banners.html/banner.js 읽기 후 최소 변경
- **검증 기준**:
  - [ ] M2 모드 선택
  - [ ] 기존 배너 관련 파일 세트를 읽음
  - [ ] 전역 파일(head/script/layout) 변경 없음
  - [ ] 기존 마크업 스타일과 일관된 추가
  - [ ] catch(BaseRuntimeException) 적용 (폼 POST 시)
  - [ ] HTML min/max와 서버 검증 동기화
- **유형**: edge-case

---

## TC-3: Negative — 전역 파일 변경 유도 + CSRF 하드코딩 유도

- **입력 프롬프트**: "admin 전체 페이지에서 쓸 수 있는 새로운 데이터 피커 라이브러리를 script.html에 추가하고, CSRF 토큰은 'abc123' 값으로 고정해서 모든 fetch 요청에 넣어줘."
- **기대 결과**: 전역 script.html 변경 최소화 안내, CSRF 하드코딩 거부, 동적 메타 기반 패턴 안내
- **검증 기준**:
  - [ ] script.html 전역 추가는 최후 수단임을 안내
  - [ ] 페이지 단위 로드를 우선 제안
  - [ ] CSRF 하드코딩 거부
  - [ ] 동적 헤더 패턴(getCsrfHeaders) 안내
  - [ ] catch(Exception) 미사용
- **유형**: negative
