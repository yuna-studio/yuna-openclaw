import { Suspense } from "react";
import type { Metadata } from "next";
import DocClient from "./doc-client";

export const metadata: Metadata = {
  title: "개발문서 | 낭만코딩 · 가재 컴퍼니",
  description: "실제 개발 과정, 아키텍처, 시행착오를 기록한 오픈 개발문서입니다.",
  alternates: {
    canonical: "/docs",
  },
  openGraph: {
    title: "개발문서 | 낭만코딩 · 가재 컴퍼니",
    description: "실제 개발 과정, 아키텍처, 시행착오를 기록한 오픈 개발문서",
    url: "https://nangman.live/docs",
    type: "website",
  },
};

export default function DocsPage() {
  return (
    <Suspense fallback={<main className="min-h-screen"><div className="max-w-3xl mx-auto px-4 py-10">로딩 중...</div></main>}>
      <DocClient />
    </Suspense>
  );
}
