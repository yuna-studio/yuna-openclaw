# 기술 아키텍처 및 폴더 구조 명세서 (v1.0)

## 1. 개요
본 문서는 가재 컴퍼니의 4대 핵심 피쳐(로그인, 업로드, 결제, 결과확인)를 안정적이고 확장 가능하게 구현하기 위한 **Strict Clean Architecture** 기반의 설계 명세를 정의합니다.

## 2. 폴더 구조 (Strict Clean Architecture)

`src/` 디렉토리를 기준으로 레이어별 관심사를 엄격히 분리합니다.

```text
src/
├── core/                 # 공통 유틸리티, 상수, 추상 로깅 인터페이스
│   ├── logger/           # 로깅 추상화 (Analytics interface)
│   ├── errors/           # 공통 에러 정의
│   └── utils/
├── domain/               # 비즈니스 로직 (최상위 계층, 의존성 없음)
│   ├── entities/         # 핵심 모델 (User, Payment, File, Result)
│   ├── usecases/         # 비즈니스 행위 (LoginUseCase, ProcessPayment 등)
│   └── repositories/     # 데이터 접근 인터페이스 (Interface only)
├── data/                 # 데이터 소스 구현체
│   ├── datasources/      # Remote (API), Local (DB/Storage)
│   ├── repositories/     # Domain Repository의 구체적 구현
│   └── mappers/          # DTO <-> Entity 변환
├── presentation/         # UI 및 상태 관리
│   ├── components/       # 재사용 가능한 UI 컴포넌트
│   ├── pages/            # 각 피쳐별 페이지
│   └── viewmodels/       # UI 상태 및 UseCase 호출 로직
└── infrastructure/       # 외부 라이브러리 설정 및 어댑터
    ├── auth/             # Social Login SDK 어댑터
    ├── payment/          # 결제 Gateway (Portone, Toss 등) 어댑터
    └── analytics/        # Mixpanel, Firebase 실제 구현체
```

## 3. 4대 핵심 피쳐 구현 상세

### 3.1 로그인 (Login)
- **Domain**: `LoginUseCase`를 통해 인증 로직 수행. `AuthRepository` 인터페이스 정의.
- **Data**: Firebase Auth 또는 OAuth API를 호출하는 `AuthRepositoryImpl` 구현.
- **Presentation**: 소셜 로그인 버튼 및 세션 관리 UI.

### 3.2 업로드 (Upload)
- **Domain**: `UploadFileUseCase` (파일 검증, 청크 분할 등 비즈니스 규칙).
- **Data**: S3 또는 서버 API로 파일을 전송하는 `FileRepositoryImpl`.
- **Infrastructure**: 파일 압축 및 전처리를 위한 라이브러리 래퍼.

### 3.3 결제 (Payment)
- **Domain**: `ProcessPaymentUseCase` (금액 검증, 주문 생성). `PaymentRepository` 인터페이스.
- **Data**: PG사 결제 승인 API 연동.
- **Infrastructure**: 결제창(I'mport 등) 라이브러리 어댑터 구현.

### 3.4 결과확인 (Result Verification)
- **Domain**: `GetProcessingResultUseCase` (상태 조회, 데이터 가공).
- **Data**: 서버 DB/Polling/WebSocket 연동.
- **Presentation**: 결과 대시보드 및 상세 리포트 뷰.

## 4. 의존성 분리 및 관심사 분리 (Strict Clean Architecture)

- **Dependency Rule**: 의존성은 항상 안쪽(Domain)으로만 향합니다.
- **Interface Segregation**: `Data` 레이어는 `Domain` 레이어의 인터페이스를 구현하며, `Domain`은 외부 라이브러리나 DB의 존재를 알지 못합니다.
- **Dependency Injection**: 하위 모듈의 구체적인 구현체는 DI(의존성 주입)를 통해 런타임에 결정하여 유연성을 확보합니다.

## 5. 데이터 로깅 (Mixpanel/Firebase) 추상화 및 모듈화

로깅 시스템의 교체나 병행 사용을 위해 추상화 레이어를 도입합니다.

- **Interface (`core/logger/AnalyticsService.ts`)**:
  ```typescript
  interface AnalyticsService {
    logEvent(name: string, params?: Record<string, any>): void;
    setUserContext(userId: string, traits?: Record<string, any>): void;
  }
  ```
- **Implementation (`infrastructure/analytics/`)**:
  - `MixpanelAnalyticsImpl`: Mixpanel SDK를 이용한 구현.
  - `FirebaseAnalyticsImpl`: Firebase SDK를 이용한 구현.
- **Module Wrapper**: `AnalyticsProvider`를 통해 한 번의 호출로 여러 플랫폼에 동시에 로깅하거나, 설정에 따라 스위칭 가능하도록 구현합니다.

## 6. 결론
본 아키텍처는 가재 컴퍼니의 핵심 비즈니스 로직을 외부 환경(UI, DB, SDK)으로부터 독립시켜 코드의 테스트 용이성과 유지보수성을 극대화합니다.
