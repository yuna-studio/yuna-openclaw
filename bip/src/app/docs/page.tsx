import { Suspense } from "react";
import type { Metadata } from "next";
import DocClient from "./doc-client";
import { TuningLoader } from "@/components/ui/tuning-loader";

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
    <Suspense fallback={<main className="min-h-screen"><TuningLoader className="py-20" /></main>}>
      <DocClient />
    </Suspense>
  );
}
