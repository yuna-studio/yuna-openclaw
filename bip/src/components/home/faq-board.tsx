"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { collection, getDocs, query, where } from "firebase/firestore";
import { db } from "@/lib/firebase";

type FaqPost = {
  id: string;
  title: string;
  slug: string;
  summary?: string;
  order?: number;
  displayDate?: string;
};

const fallbackFaq: Array<{ q: string; a: string }> = [
  {
    q: "바이브코딩 실전 사례를 어디서 볼 수 있나요?",
    a: "홈 프로젝트 보드, 개발문서(/docs), 라이브 로그(/live)에서 실제 작업 흐름을 바로 확인할 수 있습니다.",
  },
  {
    q: "SEO/GEO 오가닉 유입 관련 기록도 있나요?",
    a: "블로그에서 실험 결과를, 개발문서에서 구현 기준을 공개합니다. 전략부터 적용 로그까지 순서대로 볼 수 있습니다.",
  },
  {
    q: "이 사이트는 어떤 과정을 공개하나요?",
    a: "문제정의, 기능설계, 구현, 실패 원인, 지표 개선까지 전체 사이클을 공개합니다.",
  },
];

export function FAQBoard() {
  const [items, setItems] = useState<FaqPost[]>([]);

  useEffect(() => {
    if (!db) return;

    (async () => {
      try {
        // HQ 블로그 관리에서 category=FAQ 로 작성한 글로벌 게시글을 홈 FAQ로 사용
        const snap = await getDocs(
          query(
            collection(db, "blog_posts"),
            where("status", "==", "published"),
            where("category", "==", "FAQ")
          )
        );

        const rows = snap.docs.map((d) => ({ id: d.id, ...(d.data() as any) })) as FaqPost[];
        rows.sort((a, b) => Number(a.order || 0) - Number(b.order || 0));
        setItems(rows.slice(0, 3));
      } catch {
        setItems([]);
      }
    })();
  }, []);

  const faq = useMemo(() => {
    if (items.length === 0) return fallbackFaq;

    return items.map((it) => ({
      q: it.title,
      a: it.summary || "답변 내용을 HQ 블로그 관리에서 FAQ 카테고리로 입력해 주세요.",
      slug: it.slug,
    }));
  }, [items]);

  return (
    <section className="w-full max-w-2xl mx-auto px-4 py-10">
      <div className="bg-white border border-border rounded-xl p-5 space-y-4">
        <h2 className="text-lg font-bold">낭만코딩은 어떤 사이트인가요?</h2>
        <p className="text-sm text-text-secondary leading-relaxed">
          낭만코딩은 바이브코딩 기반 Build in Public 아카이브입니다.
          기획부터 개발, 배포, 운영, 개선까지의 의사결정 로그를 문서/라이브/블로그로 공개합니다.
        </p>

        <div className="space-y-3">
          <h3 className="text-base font-semibold">자주 묻는 질문 (FAQ)</h3>
          {faq.map((item, idx) => (
            <div key={idx}>
              <p className="text-sm font-semibold">Q{idx + 1}. {item.q}</p>
              <p className="text-sm text-text-secondary">A. {item.a}</p>
              {"slug" in item && item.slug ? (
                <Link href={`/blog?slug=${encodeURIComponent(String(item.slug))}`} className="text-xs text-primary">
                  관련 글 보기 →
                </Link>
              ) : null}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
