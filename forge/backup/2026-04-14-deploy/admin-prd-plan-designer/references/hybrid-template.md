# HYBRID Template (PRD+TDD 통합 문서)

## 목적
- 한 번의 산출물에서 기획 관점(PRD)과 구현 관점(TDD)을 모두 제공한다.
- 단, 섞어서 쓰지 않고 섹션을 명시적으로 분리한다.

## 문서 구조
1. PRD 섹션
2. TDD 섹션
3. Alignment 섹션(PRD 요구사항과 TDD 구현 매핑)

## 필수 표
- PRD: 기능 개요, 범위, FR, NFR
- TDD: 구현 개요, 흐름, Phase 계획, 테스트 전략
- Alignment: `PRD ID -> TDD 구현 항목 -> 검증 방법`

## 품질 기준
- PRD 요구사항마다 최소 1개 이상의 TDD 구현 항목이 매핑되어야 한다.
- 매핑 불가 항목은 Open Questions 또는 Out of Scope로 명시한다.
