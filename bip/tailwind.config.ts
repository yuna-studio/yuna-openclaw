import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Sanbaram Studio Design System
        background: "#FAF6F0", // Cream
        primary: {
          DEFAULT: "#4A5D23", // Khaki Green
          hover: "#3A4A1C",
          light: "#E8F0E4",
        },
        secondary: {
          DEFAULT: "#6BA3BE", // Sky Blue
          hover: "#5A8CA3",
        },
        text: {
          primary: "#3D3529", // Charcoal
          secondary: "#7A7265",
          muted: "#A6A095",
        },
        accent: {
          highlight: "#E67E22", // RPG Dialogue Highlight
        },
        // Legacy Support for components
        panel: "#FFFFFF",
        overlay: "rgba(250, 246, 240, 0.8)",
        status: {
          live: "#E74C3C",
          success: "#27AE60",
        },
        reaction: {
          heart: "#E91E63",
          lol: "#F1C40F",
        },
        border: {
          DEFAULT: "#E5E7EB",
          highlight: "#4A5D23", // Primary for borders
        }
      },
      fontFamily: {
        sans: ["Pretendard", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "float": "float 3s ease-in-out infinite",
        "tilt": "tilt 10s infinite linear",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-5px)" },
        },
        tilt: {
          "0%, 50%, 100%": { transform: "rotate(0deg)" },
          "25%": { transform: "rotate(1deg)" },
          "75%": { transform: "rotate(-1deg)" },
        },
      }
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
export default config;
