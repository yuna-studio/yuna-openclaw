import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Design System Colors (Warm Cream Tone)
        background: "#FAF6F0", // Warm Cream
        panel: "#FFFFFF",      // White
        overlay: "rgba(250, 246, 240, 0.8)", 
        
        primary: {
          DEFAULT: "#4A5D23", // Earth Green (카키)
          glow: "rgba(74, 93, 35, 0.3)",
        },
        
        text: {
          primary: "#2C3E50",   // Dark Navy (본문)
          secondary: "#5D6D7E", // Slate (보조)
          muted: "#95A5A6",     // Light Gray (비활성)
        },
        
        status: {
          live: "#E74C3C",    // Red
          success: "#27AE60", // Green
        },
        
        reaction: {
          heart: "#E91E63", // Pink
          lol: "#F1C40F",   // Yellow
        },
        
        border: {
          DEFAULT: "#E5E7EB",   // Light Gray
          highlight: "#D7DBDD", // Darker Gray
        }
      },
      fontFamily: {
        sans: ["Pretendard", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        "pulse-fast": "pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "float": "float 3s ease-in-out infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-5px)" },
        }
      }
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
export default config;
