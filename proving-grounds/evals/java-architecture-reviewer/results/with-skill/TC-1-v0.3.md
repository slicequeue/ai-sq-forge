아키텍처 관점으로 리뷰했습니다. 결론부터 말씀드리면 **AUTO FAIL 2건**(HG-1 Bean Qualifier cross-module)이 있어 batch, batch-app 이 기동 시 `No qualifying bean` 으로 실패할 가능성이 확정적입니다. 머지 전에 수정이 필요합니다.

> 시뮬레이션 입력(변경 파일 5건과 diff 요약)만으로 작성했습니다. git 은 실행하지 않았고, 줄 번호가 입력에 없어 신규 파일은 "파일 전체"로 표기했습니다.

## 아키텍처·컨벤션 리뷰 결과

**브랜치**: api/feat/dexcom-batch-oauth
**비교 기준**: dev
**커밋 수**: 입력 미제공 · **변경 파일**: 5 (기존 3 + 신규 2)
**로드된 규칙**: 01, 07, 19 (alwaysApply 3종). 변경 파일에 admin/, Entity, Repository, DTO 가 없어 02/03/04/05/13/14 는 로드하지 않음
**조직 컨벤션**: 적용 (`.claude/shared/vc-conventions-guide.md` 존재). review-lint 미실행(출력이 주어지지 않았고 실행하지 않음). 결과는 추정하지 않음

### 확인된 사실 vs 가정

| 구분 | 내용 |
|------|------|
| 확인된 것 (입력) | cgm 의 `DexcomWebClientConfiguration` 이 `@Qualifier(DEXCOM_AUTHORIZED_CLIENT_MANAGER)` 로 주입한다. 상수 값은 `"dexcomAuthorizedClientManager"` (shared). api 는 `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)` 로 정상 등록한다. batch, batch-app 신규 설정은 `@Bean` + 메서드명 `authorizedClientManager`, 상수 없이 등록한다 |
| 가정한 것 | batch, batch-app 이 cgm 모듈을 의존하고 `DexcomWebClientConfiguration` 을 스캔한다. 이번 변경이 "batch 에 Dexcom OAuth 설정을 추가"하는 것이어서 의존 관계로 보지만 gradle 의존성과 스캔 경로는 확인하지 못함. 재평가 트리거: 두 모듈이 cgm 을 로드하지 않는 것이 확인되면 AUTO FAIL 은 "미사용 Bean 중복 등록"(Medium) 으로 내린다 |
| 가정한 것 | admin 모듈도 cgm 을 로드하는지는 입력에 없음. 확인 필요 항목으로 분리 |

### AUTO FAIL (기동 실패 확정)

| # | 유형 | 파일:라인 | 위반 | 등급 |
|---|------|----------|------|------|
| 1 | ARCH-BEAN | batch/config/BatchOAuth2Configuration.java:(신규, 파일 전체) | `@Bean` 이 상수 없이 메서드명 `authorizedClientManager` 로 등록된다. 빈 이름이 `authorizedClientManager` 가 되어 cgm 의 `@Qualifier("dexcomAuthorizedClientManager")` 와 불일치. `No qualifying bean` 기동 실패 (HG-1) | AUTO FAIL |
| 2 | ARCH-BEAN | batch-app/config/BatchDexcomConfiguration.java:(신규, 파일 전체) | 1번과 동일 패턴 (HG-1) | AUTO FAIL |

근거: HG-1 은 `@Qualifier(CONST)` 로 참조되는 상수를 쓰는 모든 애플리케이션 모듈에 `@Bean(CONST)` 정의를 요구한다. 현재 `@Bean(CONST)` 가 있는 모듈은 api 뿐이고(`DexcomAuth2Configuration`), batch, batch-app 은 메서드명 기반 등록만 있다. 과거 5월 api, 6/16 batch·batch-app #593, 6/19 admin #588 에서 같은 패턴이 3회 재발한 사고이고, 이번이 4번째 재발 후보다.

### 필수 수정 (Critical/High)

| # | 유형 | 파일:라인 | 위반 | 수정 방향 |
|---|------|----------|------|-----------|
| 1 | ARCH-BEAN | batch/.../BatchOAuth2Configuration.java, batch-app/.../BatchDexcomConfiguration.java | 위 AUTO FAIL 의 수정 | 아래 수정 방향 참조 |

수정 방향 (두 파일 공통, 코드는 수정하지 않고 방향만 제시):

- `@Bean` 을 `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)` 로 바꾸고 `shared/constant/DexcomBeanNameConstants` 를 import 한다. 메서드명은 그대로 둬도 되지만, 빈 이름은 상수로만 결정된다
- batch, batch-app 의 gradle 이 shared 모듈을 의존하는지 확인한다. 없으면 추가가 필요하다 (07 의 "하드코딩된 값은 상수로 추출" 과 같은 취지, 등록자와 소비자가 다른 모듈이므로 shared 상수가 맞다)
- 등록 대상이 "빈 이름 문자열 3회 이상 반복" 기준에도 해당한다. 상수 1개를 api, batch, batch-app 이 공유하는 구조가 되도록 한다

### 권장 개선 (Medium/Low/Info)

| # | 유형 | 파일:라인 | 개선 | 근거 |
|---|------|----------|------|------|
| 1 | ARCH-BEAN | batch/.../BatchOAuth2Configuration.java, batch-app/.../BatchDexcomConfiguration.java | 두 신규 설정이 "동일 패턴"이면 같은 Bean 정의가 두 모듈에 복제된 것이다. 복제를 줄일 공용 위치가 있는지 검토. 단 공용 모듈에 `@Bean` 설정을 두는 것은 `@Entity` 와 달리 HG-3 대상이 아니므로 강제 사항은 아님 | 07-general-project-convention.md 상수 추출, 19-architecture-boundaries.md §3 Qualifier 명시 주입 |
| 2 | ARCH-BEAN | 재발 방지 | `@Qualifier` 소비자(cgm) 와 등록자(api, batch, batch-app) 가 서로 다른 모듈에 흩어져 4회째 같은 사고가 났다. 새 모듈이 추가될 때 누락을 잡는 장치(모듈별 `@SpringBootTest` 컨텍스트 로딩 스모크 테스트 등)를 PR 본문에 근거와 함께 논의할 만하다 | HG-1 재발 이력 |

### 검사 통과 항목
- 4-Tier 의존성 방향: 입력 범위에서 위반 없음. 변경 5건은 전부 설정 클래스이고 Domain/Application/Web import 는 확인 대상 아님 (diff 본문이 없어 import 문까지는 미확인)
- Bean Qualifier cross-module: **FAIL** (검증 상수 1건: `DEXCOM_AUTHORIZED_CLIENT_MANAGER`, 등록 확인 모듈 1/3 이상)
- 공용 모듈 `@Entity` (HG-3): 변경 파일에 `@Entity` 없음 (shared 에는 상수 파일만)
- shared 모듈 경계: `DexcomBeanNameConstants` 는 상수만 있어 허용 범위 (입력 기준)
- cgm → shared 방향의 상수 참조: 정상
- 순환 의존: 이번 변경으로 새 모듈 간 의존은 입력에 없음 (batch, batch-app 이 shared 를 쓰는 방향은 비순환)
- FQCN 인라인: 입력에 코드 본문이 없어 검사 불가. 수정 후 diff 에서 재확인 필요
- 조직 컨벤션: 신규 2파일은 설정 클래스이며 코드 본문이 없어 `@Setter`·`var`·와일드카드 import·약어 변수명 여부를 판정할 수 없다. review-lint 미실행(출력 미제공)이므로 ARCH-VC 는 0건으로 두되 "검사 통과"가 아니라 "미판정"이다. 3절 예외(기존 `from()` 수정 등)에 해당하는 항목은 없음

### 확인 필요 (입력으로 판정 불가)
- admin 모듈이 cgm 의 `DexcomWebClientConfiguration` 을 로드하는지. 로드하면 admin 에도 `@Bean(CONST)` 가 필요하다 (6/19 #588 사고가 admin 이었음). grep 대상: `DEXCOM_AUTHORIZED_CLIENT_MANAGER`, `OAuth2AuthorizedClientManager`, 각 모듈의 `@ComponentScan`·`scanBasePackages`
- 기동 확인: 수정 후 `:batch`, `:batch-app` 의 컨텍스트가 실제로 뜨는지는 사람이 실행해 확인해야 한다 (리뷰는 읽기 전용)

### 범위 밖 제안
- 기존 `DexcomAuth2Configuration` 이름의 `Auth2` 는 신규 `BatchOAuth2Configuration` 의 `OAuth2` 와 표기가 다르다. 이번 diff 가 건드리지 않은 기존 파일이므로 지적하지 않고 한 줄만 남긴다

### 타 스킬 참조
- OAuth 클라이언트 시크릿·토큰 저장 방식은 이 스킬 범위 밖이다. `java-secure-coding-reviewer` 에서 확인
- 배치에서 `OAuth2AuthorizedClientManager` 토큰 갱신 호출의 동시성·성능은 `java-performance-reviewer` 범위

---

## 사용자 응답 요약

1. **판정**: AUTO FAIL 2건. batch 와 batch-app 신규 설정이 메서드명 기반 등록(`authorizedClientManager`)이라, cgm 의 `@Qualifier("dexcomAuthorizedClientManager")` 와 이름이 맞지 않아 기동 시 `No qualifying bean` 이 납니다.
2. **조치**: 두 파일의 `@Bean` 을 `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)` 로 바꾸고 shared 의 `DexcomBeanNameConstants` 를 참조하세요. batch, batch-app 이 shared 를 의존하는지도 확인이 필요합니다.
3. **확인 부탁드릴 것**: admin 모듈도 cgm 설정을 로드하는지 grep 해 주세요. 로드하면 같은 수정이 필요합니다. 이전에 admin 에서 같은 사고(#588)가 있었습니다.
4. **한계**: 코드 본문과 review-lint 출력이 없어 FQCN, 4-Tier import, 조직 컨벤션(ARCH-VC)은 판정하지 못했습니다. 수정 후 diff 로 한 번 더 보면 확정할 수 있습니다.
5. 재발이 4번째라서, 모듈 추가 시 컨텍스트 로딩 스모크 테스트로 누락을 자동으로 잡는 방안을 PR 에서 논의해 보시길 권합니다.
