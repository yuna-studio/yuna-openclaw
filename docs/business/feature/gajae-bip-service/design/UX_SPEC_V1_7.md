# 📗 [GAJAE-BIP] Service-MVP v1.7 초정밀 UI/UX 명세서 (Final v1.5)

## 7. 웹 서비스 특화 최적화 명세 (Web-specific Specs)

본 서비스는 웹 브라우저 환경을 최우선으로 하며, 다음과 같은 웹 특화 인터랙션과 기술 규격을 준수한다.

### 7.1 브라우저 인터랙션 (Mouse & Hover)
- **Intelligence Aura Effect**:
    - **Trigger**: 마우스 커서가 `Thought Card` 영역에 진입할 때.
    - **Visual**: 커서 위치를 중심으로 반지름 `150px`의 은은한 `intel-neon` 광채(Radial Gradient)가 카드 배경에 동적으로 추종.
    - **CSS Data**: `background: radial-gradient(circle at var(--mouse-x) var(--mouse-y), rgba(0, 240, 255, 0.15), transparent 80%)`.

### 7.2 웹 확산 엔진 (Deep-Link Engine)
- **Anchor Logic**: 각 사고 기록 블록은 고유한 `id` (예: `#20260206-1234`)를 보유함.
- **Shared Experience**: 외부에서 해당 링크로 접속 시, 부드러운 `Smooth Scroll`과 함께 해당 카드가 3회 점멸하며 유저 시선을 고정함.

### 7.3 기술적 웹 표준 (Technical Standard)
- **Framework**: Next.js (App Router) + Server Components.
- **Data Navigation**: 
    - `meeting/` 하위의 **날짜별 디렉토리 구조**를 탐색기(Explorer) UI로 직결 렌더링한다.
    - 파일명의 `HHMM` 시간 데이터를 파싱하여 UI상에서 자동 정렬을 수행한다.
- **SEO**: 피쳐명, 가재 ID, 의사결정 요약을 메타데이터로 자동 추출하여 검색 엔진에 노출.
- **Platform Support**: Chrome, Safari, Edge (Desktop & Mobile Browser) 완벽 대응.

---
**UX가재 : 웹의 본질은 연결이며, 브라우저를 넘어 전파되는 지능의 실체를 빚어냅니다.** ⚔️🚀
