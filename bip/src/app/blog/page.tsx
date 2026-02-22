"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { collection, getDocs, query, where } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { ChevronLeft } from "lucide-react";
import { track } from "@/lib/logging";

type BlogPost = {
  id: string;
  title: string;
  slug: string;
  summary?: string;
  contentMd?: string;
  category?: string;
  displayDate?: string;
  order?: number;
  sourceUrl?: string;
  sourceType?: string;
  bannerTag?: string;
  badgeTag?: string;
  cardTag?: string;
  coverImage?: string;
  thumbnailUrl?: string;
  tags?: string[];
};

// removed hardcoded seed post

export default function BlogPage() {
  const [projectId, setProjectId] = useState("");
  const [category, setCategory] = useState("");

  useEffect(() => {
    if (typeof window === "undefined") return;
    const p = new URLSearchParams(window.location.search);
    setProjectId(String(p.get("projectId") || ""));
    setCategory(String(p.get("category") || ""));
  }, []);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [posts, setPosts] = useState<BlogPost[]>([]);

  useEffect(() => {
    track("view_blog_list", { projectId, category: category || undefined });
  }, [projectId, category]);

  useEffect(() => {
    if (!db) {
      setLoading(false);
      setError("잘못된 접근입니다.");
      return;
    }

    (async () => {
      try {
        const colRef = projectId
          ? collection(db, "projects", projectId, "blog_posts")
          : collection(db, "blog_posts");
        const snap = await getDocs(query(colRef, where("status", "==", "published")));
        const rows = snap.docs.map((d) => ({ id: d.id, ...(d.data() as any) })) as BlogPost[];
        rows.sort((a, b) => Number(a.order || 0) - Number(b.order || 0));
        setPosts(rows);
      } catch (e: any) {
        setError(e?.message || "블로그 로드 실패");
      } finally {
        setLoading(false);
      }
    })();
  }, [projectId]);

  const filtered = useMemo(() => {
    let out = posts;
    if (category) out = out.filter((p) => String(p.category || "") === category);
    return out;
  }, [posts, category]);

  const categories = useMemo(
    () => Array.from(new Set(posts.map((p) => p.category).filter(Boolean))),
    [posts]
  );

  return (
    <main className="min-h-screen bg-background text-text-primary">
      <header className="h-14 sticky top-0 z-40 flex items-center px-4 backdrop-blur-md bg-white/80 border-b border-gray-200">
        <Link
          href="/"
          onClick={() => track("click_blog_to_home", { projectId, source: "blog_header" })}
          className="p-2 -ml-2 text-text-secondary hover:text-text-primary transition-colors flex items-center gap-1 group w-24"
        >
          <ChevronLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-medium">홈</span>
        </Link>
        <span className="flex-1 text-center font-bold text-sm tracking-wide">낭만코딩 아티클</span>
        <div className="w-24" />
      </header>

      <div className="w-full max-w-3xl mx-auto px-4 py-6">
        <div className="bg-white border border-border rounded-2xl p-3 mb-4">
          <p className="text-[11px] text-text-muted mb-2">카테고리</p>
          <div className="flex flex-wrap gap-2">
            <Link className="text-xs px-2 py-1 rounded bg-gray-100" href={projectId ? `/blog?projectId=${encodeURIComponent(projectId)}` : "/blog"}>전체</Link>
            {categories.map((c) => (
              <Link
                key={c}
                className="text-xs px-2 py-1 rounded bg-gray-100"
                href={projectId ? `/blog?projectId=${encodeURIComponent(projectId)}&category=${encodeURIComponent(String(c))}` : `/blog?category=${encodeURIComponent(String(c))}`}
              >
                {c}
              </Link>
            ))}
          </div>
        </div>

        {loading ? <div className="text-text-muted">로딩 중...</div> : null}
        {error ? <div className="text-red-400">{error}</div> : null}

        {!loading && !error ? (
          <div className="space-y-3">
            {filtered.map((p) => {
              const href = projectId
                ? `/blog/post?projectId=${encodeURIComponent(projectId)}&slug=${encodeURIComponent(p.slug)}${category ? `&category=${encodeURIComponent(category)}` : ""}`
                : `/blog/post?slug=${encodeURIComponent(p.slug)}${category ? `&category=${encodeURIComponent(category)}` : ""}`;

              const tags = Array.isArray(p.tags) ? p.tags : [];
              const tagFromTags = tags.find((t) => t.startsWith("배너:") || t.startsWith("badge:"))?.split(":").slice(1).join(":").trim();
              const coverFromTags = tags.find((t) => t.startsWith("커버:") || t.startsWith("cover:"))?.split(":").slice(1).join(":").trim();

              const bannerTag = p.bannerTag || p.badgeTag || p.cardTag || tagFromTags || p.category || "아티클";
              const coverSrc = p.coverImage || p.thumbnailUrl || coverFromTags || "/og-image.jpg";

              return (
                <Link
                  key={p.id}
                  href={href}
                  onClick={() => track("click_blog_item", { projectId, slug: p.slug })}
                  className="block rounded-2xl border p-3 transition-colors border-border bg-white hover:bg-gray-50"
                >
                  <div className="relative rounded-xl overflow-hidden border border-border mb-3">
                    <img src={coverSrc} alt={p.title} className="w-full h-40 object-cover" />
                    <span className="absolute left-2 bottom-2 inline-flex items-center rounded-md bg-black/65 text-white text-[11px] font-semibold px-2 py-1">
                      {bannerTag}
                    </span>
                  </div>

                  <p className="text-sm font-bold leading-snug line-clamp-2">{p.title}</p>
                  <p className="text-xs text-text-secondary mt-1 line-clamp-2">{p.summary || "요약 없음"}</p>
                  <div className="mt-2 flex items-center justify-between text-[11px] text-text-secondary">
                    <span>{p.displayDate || ""}</span>
                    <span>{p.category || "블로그"}</span>
                  </div>
                </Link>
              );
            })}
          </div>
        ) : null}
      </div>
    </main>
  );
}
