"use client";

import Link from "next/link";
import { track } from "@/lib/logging";

export function BlogBoard() {
  return (
    <section className="w-full max-w-2xl mx-auto px-4 py-16 border-t border-dashed border-border">
      <div className="text-center">
        <p className="text-lg font-bold text-text-primary">낭만코딩 로그</p>
        <p className="text-sm text-text-muted mt-1">
          매일의 개발 기록에서,
          <span className="text-text-primary font-semibold"> 다음 기능의 단서</span>를 찾습니다.
        </p>

        <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-2">
          <Link
            href="/blog"
            onClick={() => track("click_home_blog_cta", { source: "home_section" })}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary"
          >
            최신 글 보러가기 →
          </Link>

          <Link
            href="/blog"
            onClick={() => track("click_home_blog_more", { source: "home_section" })}
            className="inline-flex items-center justify-center min-w-[132px] rounded-lg border border-primary/30 bg-primary/5 px-3 py-1.5 text-sm font-semibold text-primary hover:bg-primary/10 transition-colors"
          >
            블로그 전체 보기
          </Link>
        </div>
      </div>
    </section>
  );
}
