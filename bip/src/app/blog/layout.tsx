import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "블로그 | 낭만코딩 · 가재 컴퍼니",
  description: "낭만코딩 · 가재 컴퍼니의 개발/운영/SEO GEO 오가닉 성장 노트",
  alternates: {
    canonical: "/blog",
  },
  openGraph: {
    title: "블로그 | 낭만코딩 · 가재 컴퍼니",
    description: "개발·운영·SEO GEO 오가닉 성장 기록",
    url: "https://nangman.live/blog",
    siteName: "낭만코딩 · 가재 컴퍼니",
    locale: "ko_KR",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "블로그 | 낭만코딩 · 가재 컴퍼니",
    description: "개발·운영·SEO GEO 오가닉 성장 기록",
  },
};

export default function BlogLayout({ children }: { children: ReactNode }) {
  return children;
}
