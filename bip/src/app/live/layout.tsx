import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "라이브 로그 | 낭만코딩 · 가재 컴퍼니",
  description: "실시간 개발 대화와 의사결정 로그를 확인할 수 있는 라이브 페이지입니다.",
  alternates: {
    canonical: "/live",
  },
  openGraph: {
    title: "라이브 로그 | 낭만코딩 · 가재 컴퍼니",
    description: "실시간 개발 대화와 의사결정 로그",
    url: "https://nangman.live/live",
    type: "website",
  },
};

export default function LiveLayout({ children }: { children: ReactNode }) {
  return children;
}
