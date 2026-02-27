import type { Metadata } from "next";
import "./globals.css";
import { ReactionBar } from "@/components/ui/reaction-bar";
import { FloatingHomeCta } from "@/components/ui/floating-home-cta";
import { FirebaseAnalyticsTracker } from "@/components/analytics/firebase-analytics-tracker";

export const metadata: Metadata = {
  metadataBase: new URL("https://nangman.live"),
  title: "낭만코딩 — 바이브 코딩, 전 과정 실시간 공개",
  description: "기획부터 배포까지, AI와 나누는 모든 대화를 실시간으로 공개합니다.",
  keywords: [
    "바이브코딩",
    "build in public",
    "개발문서",
    "오가닉 유입",
    "SEO",
    "GEO",
    "낭만코딩",
  ],
  alternates: {
    canonical: "/",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-snippet": -1,
      "max-image-preview": "large",
      "max-video-preview": -1,
    },
  },
  icons: {
    icon: "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🦞</text></svg>",
  },
  openGraph: {
    title: "낭만코딩 — 바이브 코딩, 전 과정 실시간 공개",
    description: "기획부터 배포까지, AI와 나누는 모든 대화를 실시간으로 공개합니다.",
    type: "website",
    url: "https://nangman.live",
    images: [
      {
        url: "https://nangman.live/og-image.jpg",
        width: 1280,
        height: 676,
        alt: "낭만코딩 — 바이브 코딩 라이브",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "낭만코딩 — 바이브 코딩, 전 과정 실시간 공개",
    description: "기획부터 배포까지, AI와 나누는 모든 대화를 실시간으로 공개합니다.",
    images: ["https://nangman.live/og-image.jpg"],
  },
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
        <FirebaseAnalyticsTracker />
        <ReactionBar />
        <FloatingHomeCta />
      </body>
    </html>
  );
}
