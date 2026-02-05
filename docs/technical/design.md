# Design (디자인가재) - Strategy & Implementation Spec

## 1. Design Tokens (Next.js / Tailwind V4 Compatible)
AI 개발자가 즉시 `tailwind.config.ts` 또는 CSS Variable로 적용할 수 있는 토큰 정의입니다.

### 🎨 Color Palette
- `--color-primary`: `#0047BB` (Deep Medical Blue) - Trust & Authority
- `--color-bg-main`: `#F8FAFC` (Clean Slate) - Clarity
- `--color-accent`: `#D4AF37` (Premium Gold) - High-value results
- `--color-success`: `#10B981` (Vibrant Green) - Completion
- `--color-text-main`: `#1F2937` (Dark Gray) - Readability

### 🖋️ Typography (Inter / System Sans)
- `font-sans`: 'Inter', system-ui, sans-serif
- `text-h1`: 2.25rem (36px) / tracking-wide (0.05em) / font-bold
- `text-body`: 1rem (16px) / leading-relaxed / tracking-tight (-0.01em) / font-normal

### 📐 Spacing & Radius
- `spacing-unit`: 4px (Base)
- `section-padding`: 80px to 120px (For "Luxury" breathing room)
- `radius-premium`: 16px (Consistent, soft clinical feel)

### ✨ Animation & Transition (Emotional Value)
- `transition-main`: 0.4s ease-out (Soft Lift & Fade)
- `entry-animation`: translateY(20px) -> translateY(0) / opacity 0 -> 1
- **Value**: Enhances anticipation and trust through smooth, organic motion.

---

## 2. UI Structural Prompts (AI-Ready)
각 페이지를 AI가 생성할 때 참고할 수 있는 구조화된 프롬프트입니다.

### A. Landing Page (The Hook)
> "Create a landing page section with a split-screen slider. Left side shows a grainy 3D ultrasound, right side shows a high-fidelity realistic baby photo. Use a 'Medical-Trust' theme with Inter font and Blue/White palette. Include a CTA button with a subtle gold glow effect."

### B. Login & Entry (The Warmth)
> "Design a centered login card with Supabase social buttons. Add a 'Welcome' header. Implement a soft CSS-only pulse animation (0.5s duration) on the border of the login card. Use high-end typography for the 'Hello Bebe' logo."

### C. Processing & Waiting (The Mystery)
> "A minimal waiting screen. Center a 150px CSS-only glowing sphere that expands/contracts (0.8s ease-in-out). Below the sphere, cycle through text: 'Analyzing features...', 'Mapping skin texture...', 'Preparing the first meeting...'. Background should be a very light #F8FAFC."

### D. Result Gallery (The Masterpiece)
> "A vertical gallery for mobile. Three card slots (Front, Smile, Sleep). Each image should have a faint gold border and a 'Download High-Res' gold button below it. Add a comparison slider for each individual result."

---

## 3. Implementation Plan (7-Day Sprint)
- **Day 1-2**: Design Token setup & Base Layout components.
- **Day 3-4**: 5-Step Funnel UI implementation (Landing to Payment).
- **Day 5**: AI Waiting & Result Gallery interaction polish.
- **Day 6**: Cross-device QA & Asset optimization.
- **Day 7**: Production Ready.
