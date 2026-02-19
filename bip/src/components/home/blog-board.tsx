"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { collection, getDocs, query, where } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { track } from "@/lib/logging";

type BlogPost = {
  id: string;
  title: string;
  slug: string;
  summary?: string;
  displayDate?: string;
  category?: string;
  order?: number;
};

export function BlogBoard() {
  const [items, setItems] = useState<BlogPost[]>([]);

  useEffect(() => {
    if (!db) return;
    (async () => {
      const snap = await getDocs(query(collection(db, "blog_posts"), where("status", "==", "published")));
      const list = snap.docs.map((d) => ({ id: d.id, ...(d.data() as any) })) as BlogPost[];
      list.sort((a, b) => Number(b.order || 0) - Number(a.order || 0));
      setItems(list.slice(0, 3));
    })().catch(() => setItems([]));
  }, []);

  if (items.length === 0) return null;

  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-16 border-t border-dashed border-border">
      <div className="text-center mb-8">
        <p className="text-lg font-bold text-text-primary">낭만코딩 로그</p>
        <p className="text-sm text-text-muted">만들고, 실패하고, 개선한 기록을 남겨요</p>
      </div>

      <div className="space-y-3">
        {items.map((p) => (
          <Link
            key={p.id}
            href={`/blog?slug=${encodeURIComponent(p.slug)}`}
            onClick={() => track("click_home_blog", { projectId: "global", slug: p.slug })}
            className="block bg-white border border-border rounded-xl p-4 hover:border-primary/40 transition-colors"
          >
            <div className="flex items-center justify-between gap-2 mb-1">
              <h3 className="font-semibold text-sm text-text-primary">{p.title}</h3>
              <span className="text-[11px] text-text-muted shrink-0">{p.displayDate || ""}</span>
            </div>
            <p className="text-xs text-text-muted">{p.summary || p.category || ""}</p>
          </Link>
        ))}
      </div>

      <div className="text-center mt-4">
        <Link
          href="/blog"
          onClick={() => track("click_home_blog", { projectId: "global", source: "home_more" })}
          className="text-sm font-semibold text-primary"
        >
          로그 전체 보기 →
        </Link>
      </div>
    </div>
  );
}
