import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vibe Coding Live",
  description: "낭만코딩의 AI 페어 프로그래밍 실시간 중계 - Stealth Live Stream",
  icons: {
    icon: "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🦞</text></svg>",
  },
  openGraph: {
      title: "Vibe Coding Live",
      description: "AI가 코딩하는 과정을 실시간으로 훔쳐보세요.",
      type: "website",
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        <link rel="stylesheet" as="style" crossOrigin="anonymous" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet" />
      </head>
      <body
        className={`antialiased bg-background text-text-primary selection:bg-primary/20 font-sans`}
      >
        {children}
      </body>
    </html>
  );
}
