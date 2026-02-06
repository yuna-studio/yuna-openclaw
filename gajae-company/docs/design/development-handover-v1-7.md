# 🛠️ [GAJAE-BIP] Service-MVP v1.7 개발 이관 UI/UX 가이드 (Handover Guide)

본 문서는 `UX_SPEC_V1_7.md`와 `SANCTUARY_DS.md`를 기반으로, 개발자가 즉시 코드로 치환할 수 있도록 시스템 아키텍처와 시각적 데이터 맵을 정의한 최종 이관 가이드입니다.

## 1. 기술 스택 및 구현 환경 (Tech Stack)
- **Framework**: Next.js 14+ (App Router)
- **Data Source**: **GitHub-as-a-CMS** (GitHub API v3)
- **Architecture**: 서버리스 기반 SSR/ISR (별도 DB/Server 부재)
- **Security**: 모든 페칭은 **Route Handlers**를 통한 서버 사이드 수행 의무화.
- **Data Fetching Logic (Hierarchical)**:
    - **Step 1**: `meeting/` 하위의 디렉토리 목록을 페칭하여 '날짜 리스트' 생성.
    - **Step 2**: 유저가 날짜 클릭 시 `GET /repos/:owner/:repo/contents/path/to/{date}` 호출.
    - **Step 3**: 파일명의 `YYYYMMDD_HHMM_Title`을 정규식(`^(\d{8})_(\d{4})_(.*)\.md$`)으로 파싱하여 UI에 시간과 제목 바인딩.

---

## 2. 디자인 토큰 맵 (Design Tokens Mapping)

### 🎨 Color Palette (Tailwind Config)
```javascript
// tailwind.config.js 확장 규격
colors: {
  abyss: {
    0: '#000000', 1: '#030303', 2: '#080808', 3: '#0D0D0D', 
    4: '#141414', 5: '#1C1C1C', 6: '#252525', 7: '#333333', 
    8: '#454545', 9: '#666666'
  },
  intel: {
    neon: '#00F0FF',
    amber: '#FFBF00',
    pink: '#FF007A'
  }
}
```

### 🔡 Typography Class
- **`.brand-display`**: `font-archivo font-black uppercase tracking-tight`
- **`.intel-mono`**: `font-jetbrains-mono text-intel-neon drop-shadow-[0_0_4px_rgba(0,240,255,0.4)]`

---

## 3. 핵심 모듈 구현 명세 (Implementation Specs)

### 👑 CEO Command UI (Module 1)
- **Container**: `fixed top-4 left-1/2 -translate-x-1/2 w-[90%] max-w-2xl`
- **Effect**: 
    - Border: `2px solid intel-amber` + `animate-pulse`
    - Background: `abyss-1` + `backdrop-blur-xl`
- **Interaction**: 메시지 수신 시 `framer-motion`의 `scale: [1, 1.05, 1]` 애니메이션 1회 재생.

### 🧠 Dual-Layer Thought Card (Module 2)
- **Structure**: `Flex Row` (Mobile: `Flex Column`)
- **Left Pane (40%)**: `bg-abyss-2 p-4 border-r border-abyss-4`
- **Right Pane (60%)**: `bg-abyss-1 p-4`
- **Logic**: `max-height: 450px` 초과 시 `overflow-hidden` 및 `linear-gradient` 오버레이 렌더링.

### 📜 Sanctuary Codex (Module 3)
- **UI Structure**: `Recursive Tree Component`
- **Effect**: 아이템 클릭 시 `intel-neon` 색상의 `Outline` 애니메이션 150ms 재생.

---

## 4. 시각적 질감 구현 (Texture Layering)
- **Layer 0 (Canvas)**: `bg-abyss-0`
- **Layer 1 (Wave)**: `<svg>` 기반의 Heartbeat Path. `stroke-dasharray` 애니메이션 적용.
- **Layer 2 (Texture)**: `::before` 가상 요소를 활용한 `repeating-linear-gradient` (Scanline).
- **Layer 3 (Glass)**: `border-white/5` (Inner-stroke) + `box-shadow: depth-abyss`.

---
**UX가재 : 설계도는 완성되었습니다. 이제 개발 지능이 코드로 영혼을 불어넣을 차례입니다.** ⚔️🚀
