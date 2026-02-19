"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { collection, getDocs, query, where } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { marked } from "marked";
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
};

export default function BlogPage() {
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
    track("view_blog_list", { projectId, category, slug: slug || undefined });
  }, [projectId, category, slug]);

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

  const filtered = useMemo(() => {
    let out = posts;
    if (category) out = out.filter((p) => String(p.category || "") === category);
    return out;
  }, [posts, category]);

  const selected = useMemo(() => filtered.find((p) => p.slug === slug), [filtered, slug]);

  return (
    <main className="min-h-screen bg-background text-text-primary">
      <header className="h-14 sticky top-0 z-40 flex items-center px-4 backdrop-blur-md bg-white/80 border-b border-gray-200">
        <Link href="/" className="p-2 -ml-2 text-text-secondary hover:text-text-primary transition-colors flex items-center gap-1 group w-24">
          <ChevronLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-medium">홈</span>
        </Link>
        <span className="flex-1 text-center font-bold text-sm tracking-wide">블로그</span>
        <div className="w-24" />
      </header>

      <div className="w-full max-w-4xl mx-auto px-4 py-8">
        {loading ? <div>로딩 중...</div> : null}
        {error ? <div className="text-red-600">{error}</div> : null}

        {!loading && !error ? (
          <div className="grid md:grid-cols-[280px_1fr] gap-4">
            <aside className="bg-white border border-border rounded-xl p-3 h-fit">
              <p className="text-xs text-text-muted mb-2">카테고리</p>
              <div className="flex flex-wrap gap-2 mb-3">
                <Link className="text-xs px-2 py-1 rounded bg-gray-100" href={projectId ? `/blog?projectId=${encodeURIComponent(projectId)}` : "/blog"}>전체</Link>
                {Array.from(new Set(posts.map((p) => p.category).filter(Boolean))).map((c) => (
                  <Link
                    key={c}
                    className="text-xs px-2 py-1 rounded bg-gray-100"
                    href={projectId ? `/blog?projectId=${encodeURIComponent(projectId)}&category=${encodeURIComponent(String(c))}` : `/blog?category=${encodeURIComponent(String(c))}`}
                  >
                    {c}
                  </Link>
                ))}
              </div>

              <div className="space-y-2">
                {filtered.map((p) => (
                  <Link
                    key={p.id}
                    href={projectId
                      ? `/blog?projectId=${encodeURIComponent(projectId)}${category ? `&category=${encodeURIComponent(category)}` : ""}&slug=${encodeURIComponent(p.slug)}`
                      : `/blog?${category ? `category=${encodeURIComponent(category)}&` : ""}slug=${encodeURIComponent(p.slug)}`}
                    onClick={() => track("click_blog_item", { projectId, slug: p.slug })}
                    className={`block rounded-lg border p-2 ${selected?.id === p.id ? "border-primary bg-primary/5" : "border-gray-200"}`}
                  >
                    <p className="text-sm font-semibold line-clamp-2">{p.title}</p>
                    <p className="text-[11px] text-text-muted">{p.displayDate || ""}</p>
                  </Link>
                ))}
              </div>
            </aside>

            <article className="bg-white border border-border rounded-xl p-5">
              {selected ? (
                <>
                  <h1 className="text-2xl font-bold mb-1">{selected.title}</h1>
                  <p className="text-xs text-text-muted mb-4">{selected.displayDate || ""} · {selected.category || ""}</p>
                  {selected.summary ? <p className="text-sm text-text-muted mb-4">{selected.summary}</p> : null}
                  <div className="doc-content prose prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: String(marked.parse(selected.contentMd || "")) }} />
                  <script
                    type="application/ld+json"
                    dangerouslySetInnerHTML={{
                      __html: JSON.stringify({
                        "@context": "https://schema.org",
                        "@type": "BlogPosting",
                        headline: selected.title,
                        description: selected.summary || "",
                        datePublished: selected.displayDate || undefined,
                        dateModified: selected.displayDate || undefined,
                        author: {
                          "@type": "Organization",
                          name: "낭만코딩 · 가재 컴퍼니",
                        },
                        publisher: {
                          "@type": "Organization",
                          name: "낭만코딩 · 가재 컴퍼니",
                        },
                        mainEntityOfPage: projectId
                          ? `https://nangman.live/blog?projectId=${encodeURIComponent(projectId)}&slug=${encodeURIComponent(selected.slug)}`
                          : `https://nangman.live/blog?slug=${encodeURIComponent(selected.slug)}`,
                      }),
                    }}
                  />
                  <div className="mt-8 pt-4 border-t border-dashed border-border">
                    <Link href="/" onClick={() => track("click_blog_to_home", { projectId, slug: selected.slug })} className="text-sm font-semibold text-primary">홈으로 이동 →</Link>
                  </div>
                </>
              ) : (
                <div className="text-sm text-text-muted">왼쪽 목록에서 글을 선택해 주세요.</div>
              )}
            </article>
          </div>
        ) : null}
      </div>
    </main>
  );
}
