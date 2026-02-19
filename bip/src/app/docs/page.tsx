import { Suspense } from "react";
import DocClient from "./doc-client";

export default function DocsPage() {
  return (
    <Suspense fallback={<main className="min-h-screen"><div className="max-w-3xl mx-auto px-4 py-10">로딩 중...</div></main>}>
      <DocClient />
    </Suspense>
  );
}
