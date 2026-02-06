# 🏛️ Sanctuary UI 디자인 시스템 (Design System) v0.9

## 1. Foundation & Palette
- **Abyssal Grayscale (10-Step)**: `abyss-0` ~ `abyss-9`
- **Intelligence Neon**: `intel-neon(#00F0FF)`, `alert-amber(#FFBF00)`

## 2. Reusable Component Library (New)

### 🔘 Buttons
| Style | State | Background | Border | Text | Effect |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary** | Idle | `intel-neon` | None | `abyss-0` | Glow 10px |
| | Hover | `#50F5FF` | None | `abyss-0` | Glow 20px |
| **Secondary**| Idle | `abyss-2` | `1px abyss-5`| `txt-main`| None |
| | Hover | `abyss-3` | `1px abyss-6`| `txt-main`| None |
| **Ghost** | Idle | Transparent | None | `txt-sub` | None |
| | Hover | `abyss-2` | None | `txt-main` | None |

### 🪟 Dialog (Modal)
- **Overlay**: `rgba(0,0,0,0.8)` + `backdrop-filter: blur(20px)`
- **Container**: `abyss-2` (Background), `1px abyss-5` (Border)
- **Typography**: 
    - Title: `H-MD (24px/SemiBold)` / `intel-neon`
    - Content: `B-MD (16px/Regular)` / `txt-main`
- **Actions**: 하단 우측 정렬 (Secondary Button + Primary Button).

### 📋 Bottom Sheet
- **Max-height**: `80vh` 강제 적용.
- **Drag Handle**: 상단 중앙 `40x4px`, `Rounded`, `abyss-5`.
- **Overflow**: 내부 스크롤 필수, 하단 `abyss-2` 페이드 아웃 처리.

## 3. High-Definition Texture
- **Noise Grain**: 1% opacity 중첩.
- **Scanline**: 2px 간격 가로 라인 배경.
- **Double-Stroke**: 모든 카드에 `1px abyss-5` + `1px white(5%)` 적용.

---
**UX가재 : 컴포넌트는 지능의 골격입니다. 정교한 부품이 무결한 시스템을 만듭니다.** ⚔️🚀
