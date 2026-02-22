"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { track } from "@/lib/logging";

export function BlogBoard() {
  return (
    <section className="w-full max-w-2xl mx-auto px-4 py-16 border-t border-dashed border-border">
      <div className="text-center">
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-lg font-bold text-text-primary leading-snug"
        >
          코드 너머의 철학
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 }}
          className="text-lg font-bold text-text-muted/60 leading-snug mt-1"
        >
          만드는 과정 속 깊은 고민과 생각
        </motion.p>

        <div className="mt-6">
          <Link
            href="/blog"
            onClick={() => track("click_home_blog_cta", { source: "home_section" })}
            className="inline-flex items-center justify-center rounded-lg border border-border bg-white px-4 py-2 text-sm font-semibold text-text-primary hover:bg-gray-50 transition-colors"
          >
            블로그 전체 보기
          </Link>
        </div>
      </div>
    </section>
  );
}
