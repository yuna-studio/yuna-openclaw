# 📗 [GAJAE-BIP] Service-MVP v1.7 초정밀 UI/UX 명세서 (Final Design Specs)

본 문서는 `PROCESS_DS_BEST_PRACTICE.md` 표준에 따라 작성된 최종 디자인 설계도입니다. 개발자는 본 문서 외의 추가 질문 없이 100% 구현을 완수해야 합니다.

## 1. 전역 레이아웃 규칙 (Global Layout)
- **Base Canvas**: `abyss-0 (#000000)` 배경 위 `abyss-1` 섹션 배치.
- **Grid System**: 12-Column Grid (Gutter: 24px, Side Margin: 40px/Desktop, 20px/Mobile).
- **Common Effects**: 
    - 배경 최하단에 `Intelligence Heartbeat Wave` 상시 재생 (Z-index: -2).
    - 전 페이지 우측 상단 `Ghost Watermark` 고정 (Opacity: 10%).

---

## 2. 페이지별 상세 명세 (Page Specs)

### 🏠 [Page 1] The Sanctuary Dashboard (대시보드 홈)
- **목적**: 현재 진행 중인 프로젝트 피쳐들의 실시간 공정률 및 가재들의 상태를 한눈에 조망.
- **레이아웃 구조**: 
    - **Header**: 로고(좌), 가재 상태 배지 그룹(우, 11인 가로 나열).
    - **Hero Section**: 활성 피쳐(MVP v1.7)의 `Step Progress Gauge`를 대형으로 배치 (`H-XL` 타이틀 적용).
    - **Feature Grid**: 하위 기능들을 카드(`abyss-2`) 형태로 배치.
- **인터랙션**: 피쳐 카드 클릭 시 [Page 2]로 시퀀스 전환.

### 📜 [Page 2] Intelligence Timeline (사고 전개 타임라인)
- **목적**: 특정 피쳐의 13단계 공정 내에서 발생하는 모든 사고 기록과 의사결정을 시간순으로 박제.
- **레이아웃 구조**: 
    - **Sidebar (좌)**: 13단계 표준 공정 리스트 (진행 완료 단계는 `core-green`, 진행 중은 `intel-neon` 점멸).
    - **Main Feed (우)**: `Intelligence Thought Card`들의 수직 나열.
- **컴포넌트 속성**: 
    - **Thought Card**: `Max-height: 450px`, 초과 시 `abyss-1` 그라데이션 페이드 및 [Read More] 버튼 노출.
    - **Decision Box**: 의사결정 기록은 카드 주변에 `alert-amber` 글로우 효과(10px) 및 좌측 4px 굵은 바 적용.
- **예외 로직**: 모바일 가로폭 360px 이하 진입 시 Sidebar는 상단 가로 스크롤 메뉴로 자동 전환.

---

## 🔄 3. 유저 시나리오 시퀀스 (Sequential Flow)
1.  **Entry**: 유저가 서비스 접속 -> [Page 1] 로딩 (가재 배지 `ACTIVE` 애니메이션 재생).
2.  **Navigate**: 특정 피쳐 클릭 -> [Page 2] 타임라인으로 매끄러운 `Fade-in` 전환.
3.  **Read**: 긴 사고 기록 발견 -> [Read More] 클릭 -> 카드가 아래로 `Spring Transition`과 함께 확장됨.
4.  **Share**: 카드 우측 상단 [Share] 클릭 -> 해당 영역이 PNG로 렌더링 되어 클립보드 복사 및 트위터 공유창 트리거.

- **에러 핸들링**: 클립보드 복사 또는 렌더링 실패 시 **[Functional Warning]** 컬러 기반의 토스트 메시지 노출 (Duration: 2s).
- **모바일 트랜지션**: Sidebar -> Scroll Menu 전환 시 **[Slide-down: 300ms / Ease-out]** 데이터 적용.
---
**UX가재 : 명세는 지능의 의지이며, 오차 없는 구현은 개발 지능의 명예입니다.** ⚔️🚀
