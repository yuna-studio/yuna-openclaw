# 📗 플러터 클린 아키텍처 코딩 표준: [Best Practice]

본 문서는 가재 컴퍼니의 플러터(Flutter) 프로젝트에서 준수해야 할 '엄격한 클린 아키텍처' 및 '디렉토리 구조 규율'을 정의합니다.

## 1. 코딩 표준 (Null Safety)
- **! (Not Null Assertion) 사용 절대 금지**: 런타임 에러 방지를 위해 `!` 연산자 사용을 엄격히 금지한다.
- **방어적 Null 처리**: 반드시 `?` (Null Safe) 연산자를 사용하고, 값이 `null`일 경우에 대한 예외 처리 로직을 필수 구현한다.

## 2. 디렉토리 및 모듈 명명 규칙
- **단수형 명명 (Singular Form)**: 모든 폴더명은 반드시 단수형으로 작성한다.
    - 예: `entity` (O), `entities` (X) / `repository` (O), `repositories` (X)
- **레이어 구조 (Layer Structure)**:
    - `/lib/core`: 외부 라이브러리 래퍼 및 전역 설정 (Infrastructure)
    - `/lib/common`: 2개 이상의 피쳐에서 재사용되는 공유 자원
    - `/lib/feature`: 모듈화된 비즈니스 피쳐 (presentation, domain, data, docs 포함)

## 3. 아키텍처 레이어 규율
- **Presentation Layer**: 
    - **Widget**: 순수 View 역할. 비즈니스 로직 포함 금지. Bloc/Cubit에 이벤트 위임.
    - **Bloc/Cubit**: UI 상태 및 인터랙션 관리. UseCase를 호출하여 비즈니스 연산 수행.
- **Domain Layer**: 
    - **Entity**: 비즈니스 모델의 순수 정의.
    - **UseCase**: 단일 비즈니스 로직 단위. Repository 인터페이스 호출.
- **Data Layer**: 
    - **Repository Implementation**: 데이터 페칭 및 캐싱 전략 수행. UI 상태 보유 금지.
    - **Data Source**: 외부 API/DB(Firebase 등)와의 직접적 통신.

## 4. 인프라 격리 (Infrastructure Isolation)
- 외부 라이브러리(Dio, Firebase 등)를 피쳐 내부에서 직접 호출하는 것을 금지한다.
- 반드시 `core/` 레이어에 인터페이스나 래퍼를 생성하여 의존성을 격리한다.

---
**지휘 지침:** "구조의 무결성이 코드의 생명이며, 엄격한 분리가 지능의 확장성을 보장한다." ⚔️🚀
