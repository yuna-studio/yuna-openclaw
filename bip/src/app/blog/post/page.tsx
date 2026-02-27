"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { collection, getDocs, query, where } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { marked } from "marked";
import { ChevronLeft } from "lucide-react";
import { track } from "@/lib/logging";
import { TuningLoader } from "@/components/ui/tuning-loader";
import { Footer } from "@/components/ui/footer";

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

function stripSourceMetaBlock(md: string): string {
  const src = String(md || "");
  return src
    .replace(/\n?##\s*원문\s*메타[\s\S]*$/m, "")
    .trim();
}

// removed hardcoded seed post


export default function BlogPostPage() {
  const [projectId, setProjectId] = useState("");
  const [slug, setSlug] = useState("");
  const [category, setCategory] = useState("");

  useEffect(() => {
    if (typeof window === "undefined") return;
    const p = new URLSearchParams(window.location.search);
    setProjectId(String(p.get("projectId") || ""));
    setSlug(String(p.get("slug") || ""));
    setCategory(String(p.get("category") || ""));
  }, []);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [posts, setPosts] = useState<BlogPost[]>([]);

  useEffect(() => {
    if (!slug) return;
    track("view_blog_detail", { projectId, slug });
  }, [projectId, slug]);

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

  const selected = useMemo(() => posts.find((p) => p.slug === slug) || posts[0], [posts, slug]);
  const selectedTags = Array.isArray(selected?.tags) ? selected.tags : [];
  const selectedTagFromTags = selectedTags.find((t) => t.startsWith("배너:") || t.startsWith("badge:"))?.split(":").slice(1).join(":").trim();
  const selectedCoverFromTags = selectedTags.find((t) => t.startsWith("커버:") || t.startsWith("cover:"))?.split(":").slice(1).join(":").trim();

  const listHref = projectId
    ? `/blog?projectId=${encodeURIComponent(projectId)}${category ? `&category=${encodeURIComponent(category)}` : ""}`
    : `/blog${category ? `?category=${encodeURIComponent(category)}` : ""}`;

  return (
    <main className="min-h-screen bg-background text-text-primary">
      <header className="h-14 sticky top-0 z-40 flex items-center px-4 backdrop-blur-md bg-white/80 border-b border-gray-200">
        <Link
          href={listHref}
          className="p-2 -ml-2 text-text-secondary hover:text-text-primary transition-colors flex items-center gap-1 group"
        >
          <ChevronLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-medium">아티클 목록</span>
        </Link>
      </header>

      <div className="w-full max-w-3xl mx-auto px-4 py-6 pb-24">
        {loading ? <TuningLoader className="py-20" /> : null}
        {error ? <div className="text-red-400">{error}</div> : null}

        {!loading && !error && selected ? (
          <article className="bg-white border border-border rounded-2xl p-5 lg:p-7">
            <div className="relative rounded-xl overflow-hidden border border-border mb-5">
              <img
                src={selected.coverImage || selected.thumbnailUrl || selectedCoverFromTags || "/og-image.jpg"}
                alt={`${selected.title} 배너`}
                className="w-full h-48 md:h-64 object-cover"
              />
              <span className="absolute left-2 bottom-2 inline-flex items-center rounded-md bg-black/65 text-white text-[11px] font-semibold px-2 py-1">
                {selected.bannerTag || selected.badgeTag || selected.cardTag || selectedTagFromTags || selected.category || "아티클"}
              </span>
            </div>

            <h1 className="text-2xl font-bold mb-1 leading-tight">{selected.title}</h1>
            <p className="text-xs text-text-muted mb-4">
              {selected.displayDate || ""} {selected.category ? `· ${selected.category}` : ""}
            </p>
            {selected.summary ? <p className="text-sm text-text-secondary mb-4">{selected.summary}</p> : null}
            <div
              className="doc-content prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: String(marked.parse(stripSourceMetaBlock(selected.contentMd || ""), { breaks: true })) }}
            />
          </article>
        ) : null}
      </div>

      <Footer />
    </main>
  );
}
