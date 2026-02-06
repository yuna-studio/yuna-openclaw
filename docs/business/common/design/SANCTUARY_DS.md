# 🏛️ Sanctuary UI 디자인 시스템 (Design System) v0.8

## 1. Brand Concept: "The Abyssal Sanctuary" (Extended)
- **Concept**: 기계의 심연 속에서 타오르는 지능의 불꽃.
- **Visual Depth Policy**: 단순한 평면 디자인을 배제하고, 최소 4개 이상의 레이어 중첩을 통해 '공간의 깊이'를 시각화함.

## 2. Ultra-High-Resolution Color Palette (32-Step)
### 🕳️ Abyssal Grayscale (10-Step Depth)
| Token | HEX | Description | Usage |
| :--- | :--- | :--- | :--- |
| `abyss-0` | `#000000` | Pure Void | Absolute Base |
| `abyss-1` | `#030303` | Wet Black | Main Background |
| `abyss-2` | `#080808` | Cold Metal | Section Base |
| `abyss-3` | `#0D0D0D` | Dusty Surface | Card Background |
| `abyss-4` | `#141414` | Inner Shadow | Inset Layer |
| `abyss-5` | `#1C1C1C` | Active Border | Stroke Default |
| `abyss-6` | `#252525` | Hover Surface | Interaction |
| `abyss-7` | `#333333` | Disabled | Inactive UI |
| `abyss-8` | `#454545` | Secondary Text | Meta Data |
| `abyss-9` | `#666666` | Tertiary Text | Captions |

### ⚡ Intelligence Flash (Special Interaction)
| Token | HEX | Effect Data | 의미 |
| :--- | :--- | :--- | :--- |
| `intel-cyan` | `#00F0FF` | `Glow: 0 0 10px` | Active Thinking |
| `alert-amber` | `#FFBF00` | `Glow: 0 0 15px` | Critical Decision |
| `glitch-pink` | `#FF007A` | `Scanline Overlay`| Error / Warning |

## 3. High-Definition Texture & Effects
### 🎞️ Multi-Layer Texturing
1. **Layer 1: Noise Grain**: `opacity: 1%`의 미세 노이즈. 기계의 생생한 표면 질감.
2. **Layer 2: Scanline**: `2px` 간격의 가로 라인. CRT 모니터의 아날로그 감성.
3. **Layer 3: Backdrop Blur**: `20px` 심도. 공간의 몽환적 깊이감.

### 🪟 Double-Stroke Architecture
- **Outer**: `1px abyss-5` (강철 같은 경계)
- **Inner**: `1px white / 5% opacity` (유리 같은 반사광)

## 4. Typography Scale (12-Step)
- **Display**: `Archivo Black` (64px, 48px, 32px)
- **Body**: `Inter` (18px, 16px, 14px, 12px)
- **Intelligence**: `JetBrains Mono` (14px, 16px-Bold) + `text-shadow`

---
**UX가재 : 요약된 미학은 기만입니다. 1px의 치밀함이 지능의 품격을 결정합니다.** ⚔️🚀
