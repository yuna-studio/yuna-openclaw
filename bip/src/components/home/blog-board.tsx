"use client";

import Link from "next/link";
import { track } from "@/lib/logging";

export function BlogBoard() {
  return (
    <section className="w-full max-w-2xl mx-auto px-4 py-16 border-t border-dashed border-border">
      <div className="text-center">
        <p className="text-lg font-bold text-text-primary">빌드 노트</p>
        <p className="text-sm text-text-secondary mt-2">
          기능 구현 과정과 개인적인 개발 철학을 함께 남깁니다.
        </p>

        <div className="mt-6">
          <Link
            href="/blog"
            onClick={() => track("click_home_blog_cta", { source: "home_section" })}
            className="inline-flex items-center justify-center rounded-lg border border-border bg-white px-4 py-2 text-sm font-semibold text-text-primary hover:bg-gray-50 transition-colors"
          >
            블로그 보러가기
          </Link>
        </div>
      </div>
    </section>
  );
}
