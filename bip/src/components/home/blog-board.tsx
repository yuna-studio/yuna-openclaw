"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { collection, getDocs, query, where, limit, orderBy } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { ChevronRight, ChevronLeft } from "lucide-react";
import { track } from "@/lib/logging";

type BlogPost = {
  id: string;
  title: string;
  slug: string;
  summary?: string;
  category?: string;
  displayDate?: string;
  order?: number;
  bannerTag?: string;
  badgeTag?: string;
  cardTag?: string;
  coverImage?: string;
  thumbnailUrl?: string;
  tags?: string[];
};

export function BlogBoard() {
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  useEffect(() => {
    if (!db) {
      setLoading(false);
      return;
    }
    (async () => {
      try {
        const colRef = collection(db, "blog_posts");
        const snap = await getDocs(query(colRef, where("status", "==", "published")));
        const rows = snap.docs.map((d) => ({ id: d.id, ...(d.data() as any) })) as BlogPost[];
        rows.sort((a, b) => Number(b.order || 0) - Number(a.order || 0));
        setPosts(rows.slice(0, 5));
      } catch {
        // 실패 시 빈 상태 유지
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const updateScrollButtons = () => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 4);
    setCanScrollRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 4);
  };

  useEffect(() => {
    updateScrollButtons();
    const el = scrollRef.current;
    if (!el) return;
    el.addEventListener("scroll", updateScrollButtons, { passive: true });
    window.addEventListener("resize", updateScrollButtons);
    return () => {
      el.removeEventListener("scroll", updateScrollButtons);
      window.removeEventListener("resize", updateScrollButtons);
    };
  }, [posts]);

  const scroll = (dir: "left" | "right") => {
    const el = scrollRef.current;
    if (!el) return;
    const cardWidth = el.querySelector<HTMLElement>("a")?.offsetWidth || 260;
    el.scrollBy({ left: dir === "left" ? -cardWidth - 12 : cardWidth + 12, behavior: "smooth" });
  };

  return (
    <section className="w-full max-w-2xl mx-auto py-16 border-t border-dashed border-border">
      {/* 헤더 — 센터 정렬, 다른 섹션과 동일 스타일 */}
      <div className="text-center mb-10 px-4">
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
          className="text-lg font-bold text-text-muted/60 leading-snug"
        >
          만드는 과정 속 깊은 고민과 생각
        </motion.p>
      </div>

      {/* 캐러셀 — 좌우 패딩을 스크롤 내부 여백으로 처리 */}
      {loading ? (
        <div className="flex gap-3 overflow-hidden px-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="shrink-0 w-[220px] h-[200px] rounded-2xl bg-gray-100 animate-pulse" />
          ))}
        </div>
      ) : posts.length === 0 ? (
        <div className="text-center py-8 px-4">
          <p className="text-sm text-text-muted">아직 작성된 글이 없어요.</p>
          <Link
            href="/blog"
            className="inline-flex items-center justify-center rounded-lg border border-border bg-white px-4 py-2 mt-4 text-sm font-semibold text-text-primary hover:bg-gray-50 transition-colors"
          >
            블로그 전체 보기
          </Link>
        </div>
      ) : (
        <div className="relative group">
          {/* 좌측 화살표 */}
          {canScrollLeft && (
            <button
              onClick={() => scroll("left")}
              className="absolute left-1 top-1/2 -translate-y-1/2 z-10 w-8 h-8 rounded-full bg-white border border-border shadow-sm flex items-center justify-center text-text-secondary hover:text-text-primary hover:shadow-md transition-all opacity-0 group-hover:opacity-100"
              aria-label="이전"
            >
              <ChevronLeft size={16} />
            </button>
          )}

          {/* 우측 화살표 */}
          {canScrollRight && (
            <button
              onClick={() => scroll("right")}
              className="absolute right-1 top-1/2 -translate-y-1/2 z-10 w-8 h-8 rounded-full bg-white border border-border shadow-sm flex items-center justify-center text-text-secondary hover:text-text-primary hover:shadow-md transition-all opacity-0 group-hover:opacity-100"
              aria-label="다음"
            >
              <ChevronRight size={16} />
            </button>
          )}

          <div
            ref={scrollRef}
            className="flex gap-3 overflow-x-auto scrollbar-hide snap-x snap-mandatory pb-2 -mb-2"
            style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
          >
            {/* 좌측 여백 스페이서 */}
            <div className="shrink-0 w-4 -mr-3 md:w-[calc((100%-672px)/2+16px)] md:-mr-3" aria-hidden />

            {posts.map((p, i) => {
              const tags = Array.isArray(p.tags) ? p.tags : [];
              const tagFromTags = tags.find((t) => t.startsWith("배너:") || t.startsWith("badge:"))?.split(":").slice(1).join(":").trim();
              const coverFromTags = tags.find((t) => t.startsWith("커버:") || t.startsWith("cover:"))?.split(":").slice(1).join(":").trim();
              const bannerTag = p.bannerTag || p.badgeTag || p.cardTag || tagFromTags || p.category || "아티클";
              const coverSrc = p.coverImage || p.thumbnailUrl || coverFromTags || "/og-image.jpg";

              return (
                <motion.div
                  key={p.id}
                  initial={{ opacity: 0, y: 16 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.08 }}
                  className="snap-start shrink-0"
                >
                  <Link
                    href={`/blog/post?slug=${encodeURIComponent(p.slug)}`}
                    onClick={() => track("click_home_blog_card", { slug: p.slug })}
                    className="block w-[220px] rounded-2xl border border-border bg-white hover:shadow-md transition-shadow overflow-hidden"
                  >
                    <div className="relative h-28 overflow-hidden">
                      <img
                        src={coverSrc}
                        alt={p.title}
                        className="w-full h-full object-cover"
                      />
                      <span className="absolute left-2 bottom-2 inline-flex items-center rounded-md bg-black/65 text-white text-[10px] font-semibold px-1.5 py-0.5">
                        {bannerTag}
                      </span>
                    </div>
                    <div className="p-3">
                      <p className="text-[13px] font-bold leading-snug line-clamp-2 min-h-[2.5em]">
                        {p.title}
                      </p>
                      <p className="text-[11px] text-text-secondary mt-1.5 line-clamp-2">
                        {p.summary || ""}
                      </p>
                      <p className="text-[10px] text-text-muted mt-2">
                        {p.displayDate || ""}
                      </p>
                    </div>
                  </Link>
                </motion.div>
              );
            })}

            {/* 우측 여백 스페이서 */}
            <div className="shrink-0 w-4 -ml-3 md:w-[calc((100%-672px)/2+16px)] md:-ml-3" aria-hidden />
          </div>
        </div>
      )}

      {/* 더보러가기 CTA */}
      <div className="text-center mt-8 px-4">
        <Link
          href="/blog"
          onClick={() => track("click_home_blog_cta", { source: "home_section" })}
          className="inline-flex items-center gap-0.5 text-sm font-semibold text-text-secondary hover:text-primary transition-colors"
        >
          더보러가기
          <ChevronRight size={16} />
        </Link>
      </div>
    </section>
  );
}
