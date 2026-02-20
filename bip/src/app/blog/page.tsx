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
  sourceUrl?: string;
  sourceType?: string;
};

const X_ARTICLE_SEED: BlogPost = {
  id: "x-2016144348535234775",
  slug: "specialist-to-generalist-solo-founder",
  title: "억대 연봉이라는 '황금 수갑'을 풀고, 나는 야생으로 왔다.",
  summary: "스페셜리스트에서 제너럴리스트, 그리고 1인 창업가로의 진화",
  category: "트위터 아티클",
  displayDate: "2026-01-27",
  order: -999,
  sourceType: "twitter_article",
  sourceUrl: "https://x.com/romantic_coding/status/2016144348535234775",
  contentMd: `## 스페셜리스트에서 제너럴리스트, 그리고 1인 창업가로의 진화

남들이 부러워하는 곳, 흔히 말하는 '네카라쿠배' 중 한 곳에서 모바일 개발자로 일했습니다.
안정적인 시스템, 높은 연봉, 뛰어난 동료들. 개발자로서 더할 나위 없는 환경이었습니다.

하지만 아이러니하게도, 연차가 쌓일수록 갈증은 커져만 갔습니다.

### 1. 부품이 아닌, '엔진'이 되고 싶었다.

거대 기업의 개발자는 거대한 기계의 정교한 톱니바퀴입니다.
한 분야의 스페셜리스트가 되기를 강요받죠.

하지만 저는 욕심이 많았습니다.
내 손으로 만든 코드가, 내 손으로 만든 화면이, 내 의도대로 사용자에게 닿아 하나의 **온전한 프로덕트**로 작동하길 원했습니다.

그래서 과감하게 기술 스택을 바꿨습니다.
하나의 코드로 다양한 플랫폼에 닿을 수 있는 Flutter로 전향했고, 풀스택의 꿈을 꾸기 시작했습니다.

### 2. 코딩만으로는 비즈니스가 되지 않는다.

시니어 개발자로서의 다음 커리어를 고민할 때,
모두가 이직이나 팀장을 말했지만 저는 **작은 스타트업**을 선택했습니다.

이유는 단순했습니다.
**개발(How to build)을 넘어 무엇을, 왜, 누구에게 팔 것인가(What, Why, Who)를 배우고 싶었기 때문**입니다.

그곳에서 저는 개발자의 껍질을 깨고 나왔습니다.

- 마케팅: 내 앱을 사람들에게 알리는 법
- 그로스: 데이터를 보고 성장을 설계하는 법
- UI/UX: 사용자를 설득하는 디자인
- 실행력: 완벽함보다 빠른 검증이 중요하다는 것

이 과정을 통해 단순한 코더가 아니라 **프로덕트 메이커**로 진화했습니다.

### 3. AI, 그리고 2~3년의 런웨이

결정적인 트리거는 AI의 등장입니다.
혼자서 기획, 디자인, 개발, 마케팅을 수행하는 시대가 열렸고,
올라운더 역량 위에 AI가 더해지면서 자신감이 확신으로 바뀌었습니다.

현실적인 준비도 마쳤습니다.
수입 없이도 2~3년 버틸 런웨이를 확보한 뒤 시작한, 계산된 베팅입니다.

### 4. 실패해도 남는 장사다

저는 린 스타트업 방식을 믿습니다.

- 작게 만들고
- 빠르게 검증하고
- 실패하면 피봇한다

설령 서비스가 실패하더라도,
그 과정에서 "바닥부터 런칭까지 혼자 제품을 만든 경험"은 남습니다.
그 경험은 어떤 커리어보다 강력한 포트폴리오가 됩니다.

---

원문: [X 아티클 보기](${"https://x.com/romantic_coding/status/2016144348535234775"})`,
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

  const mergedPosts = useMemo(() => {
    const hasSeed = posts.some((p) => p.slug === X_ARTICLE_SEED.slug);
    return hasSeed ? posts : [X_ARTICLE_SEED, ...posts];
  }, [posts]);

  const filtered = useMemo(() => {
    let out = mergedPosts;
    if (category) out = out.filter((p) => String(p.category || "") === category);
    return out;
  }, [mergedPosts, category]);

  const selected = useMemo(() => filtered.find((p) => p.slug === slug) || filtered[0], [filtered, slug]);
  const twitterArticles = useMemo(
    () => mergedPosts.filter((p) => String(p.category || "") === "트위터 아티클"),
    [mergedPosts]
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

      <div className="w-full max-w-6xl mx-auto px-4 py-6">
        {loading ? <div className="text-text-muted">로딩 중...</div> : null}
        {error ? <div className="text-red-400">{error}</div> : null}

        {!loading && !error ? (
          <>
            {twitterArticles.length > 0 ? (
              <section className="mb-4">
                <div className="mb-2 flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-text-secondary">트위터 아티클</h2>
                  <span className="text-xs text-text-muted">좌우로 넘겨보기</span>
                </div>
                <div className="flex gap-3 overflow-x-auto pb-1 snap-x snap-mandatory">
                  {twitterArticles.map((p) => {
                    const href = projectId
                      ? `/blog?projectId=${encodeURIComponent(projectId)}&slug=${encodeURIComponent(p.slug)}`
                      : `/blog?slug=${encodeURIComponent(p.slug)}`;
                    return (
                      <Link
                        key={`tw-${p.id}`}
                        href={href}
                        className="snap-start min-w-[280px] max-w-[320px] rounded-xl border border-border bg-white p-2.5"
                      >
                        <div className="rounded-lg overflow-hidden border border-border mb-2">
                          <img src="/og-image.jpg" alt={p.title} className="w-full h-28 object-cover" />
                        </div>
                        <p className="text-sm font-bold leading-snug line-clamp-2">{p.title}</p>
                        <p className="text-xs text-text-secondary mt-1 line-clamp-2">{p.summary || "요약 없음"}</p>
                      </Link>
                    );
                  })}
                </div>
              </section>
            ) : null}

            <div className="grid lg:grid-cols-[360px_1fr] gap-4">
            <aside className="space-y-3">
              <div className="bg-white border border-border rounded-2xl p-3">
                <p className="text-[11px] text-text-muted mb-2">카테고리</p>
                <div className="flex flex-wrap gap-2">
                  <Link className="text-xs px-2 py-1 rounded bg-gray-100" href={projectId ? `/blog?projectId=${encodeURIComponent(projectId)}` : "/blog"}>전체</Link>
                  {Array.from(new Set(mergedPosts.map((p) => p.category).filter(Boolean))).map((c) => (
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

              <div className="space-y-3">
                {filtered.map((p) => {
                  const active = selected?.id === p.id;
                  const href = projectId
                    ? `/blog?projectId=${encodeURIComponent(projectId)}${category ? `&category=${encodeURIComponent(category)}` : ""}&slug=${encodeURIComponent(p.slug)}`
                    : `/blog?${category ? `category=${encodeURIComponent(category)}&` : ""}slug=${encodeURIComponent(p.slug)}`;
                  return (
                    <Link
                      key={p.id}
                      href={href}
                      onClick={() => track("click_blog_item", { projectId, slug: p.slug })}
                      className={`block rounded-2xl border p-3 transition-colors ${
                        active ? "border-primary bg-primary/5" : "border-border bg-white hover:bg-gray-50"
                      }`}
                    >
                      <div className="rounded-xl overflow-hidden border border-border mb-3">
                        <img src="/og-image.jpg" alt={p.title} className="w-full h-36 object-cover" />
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
            </aside>

            <article className="bg-white border border-border rounded-2xl p-5 lg:p-7">
              {selected ? (
                <>
                  <h1 className="text-2xl font-bold mb-1 leading-tight">{selected.title}</h1>
                  <p className="text-xs text-text-muted mb-4">{selected.displayDate || ""} · {selected.category || ""}</p>
                  {selected.summary ? <p className="text-sm text-text-secondary mb-4">{selected.summary}</p> : null}
                  {selected.sourceUrl ? (
                    <a href={selected.sourceUrl} target="_blank" rel="noreferrer" className="inline-flex mb-5 text-xs px-2 py-1 rounded-full bg-gray-100 border border-border text-text-secondary">
                      원문(X) 보기
                    </a>
                  ) : null}

                  <div className="doc-content prose prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: String(marked.parse(selected.contentMd || "")) }} />
                </>
              ) : (
                <div className="text-sm text-text-muted">게시글이 없습니다.</div>
              )}
            </article>
          </div>
          </>
        ) : null}
      </div>
    </main>
  );
}
