"use client";

import { useEffect, useState } from "react";
import { collection, query, orderBy, where, getDocs } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ExternalLink } from "lucide-react";
import { track } from "@/lib/logging";

interface WorkItem {
  id: string;
  title: string;
  displayTitle?: string;
  url?: string;
  docId?: string;
  docSlug?: string;
  type: string;
  order: number;
  groupKey?: string;
  period?: string;
  displayDate?: string;
}

interface Product {
  id: string;
  title: string;
  desc: string;
  status: "dev" | "shipped" | "hold";
  link?: string;
  order: number;
  works: WorkItem[];
}

const STATUS_COLOR: Record<string, string> = {
  dev: "bg-primary/10 text-primary",
  shipped: "bg-green-100 text-green-700",
  hold: "bg-gray-100 text-text-muted",
};

const STATUS_LABEL: Record<string, string> = {
  dev: "개발중",
  shipped: "완료",
  hold: "보류",
};

const TYPE_STYLE: Record<string, string> = {
  "기획": "bg-blue-100 text-blue-700",
  "설계": "bg-purple-100 text-purple-700",
  "개발": "bg-amber-100 text-amber-700",
  "배포": "bg-green-100 text-green-700",
};

function groupWorks(works: WorkItem[]) {
  const dateKey = (w: WorkItem) => String(w.displayDate || w.period || "");

  const sorted = [...works].sort((a, b) => {
    const d = dateKey(b).localeCompare(dateKey(a));
    if (d !== 0) return d;
    const p = String(b.period || "").localeCompare(String(a.period || ""));
    if (p !== 0) return p;
    return a.order - b.order;
  });

  const map = new Map<string, WorkItem[]>();
  for (const w of sorted) {
    const key = `${w.groupKey || "mvp"} / ${w.period || "미분류"}`;
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(w);
  }

  return Array.from(map.entries()).sort(([, aItems], [, bItems]) => {
    const aTop = aItems[0];
    const bTop = bItems[0];
    return dateKey(bTop).localeCompare(dateKey(aTop));
  });
}

export function ProjectBoard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [openId, setOpenId] = useState<string | null>(null);

  // 1회 로딩 (onSnapshot 대신 getDocs — 포트폴리오는 자주 안 바뀜)
  useEffect(() => {
    if (!db) { setLoading(false); return; }

    const fetchAll = async () => {
      try {
        const projSnap = await getDocs(query(collection(db, "projects"), orderBy("order", "asc")));
        
        // 모든 서브컬렉션 쿼리를 병렬로
        const list = await Promise.all(
          projSnap.docs.map(async (d) => {
            const data = d.data();
            const [worksSnap, docsSnap] = await Promise.all([
              getDocs(query(collection(db, "projects", d.id, "works"), orderBy("order", "asc"))),
              getDocs(query(collection(db, "projects", d.id, "docs"), where("status", "==", "published"))),
            ]);

            const docMeta = new Map<string, { title?: string; groupKey?: string; period?: string; displayDate?: string }>();
            docsSnap.docs.forEach((doc) => {
              const dd = doc.data() as any;
              const key = String(dd.slug || "");
              if (key) {
                docMeta.set(key, {
                  title: String(dd.title || ""),
                  groupKey: String(dd.groupKey || ""),
                  period: String(dd.period || ""),
                  displayDate: String(dd.displayDate || ""),
                });
              }
            });

            const defaultPeriod = docsSnap.docs
              .map((doc) => String((doc.data() as any).period || ""))
              .filter(Boolean)
              .sort()
              .reverse()[0] || "";

            const defaultGroupKey = docsSnap.docs
              .map((doc) => String((doc.data() as any).groupKey || ""))
              .filter(Boolean)[0] || "";

            return {
              id: d.id,
              title: data.title || "",
              desc: data.desc || "",
              status: data.status || "dev",
              link: data.link || "",
              order: data.order || 0,
              works: worksSnap.docs.map((w) => {
                const wd = w.data() as any;
                const meta = wd.docSlug ? docMeta.get(String(wd.docSlug)) : undefined;
                return {
                  id: w.id,
                  ...wd,
                  displayTitle: meta?.title || String(wd.title || ""),
                  groupKey: meta?.groupKey || String(wd.groupKey || "") || defaultGroupKey || "미분류",
                  period: meta?.period || String(wd.period || "") || defaultPeriod || "",
                  displayDate: meta?.displayDate || "",
                } as WorkItem;
              }),
            };
          })
        );
        
        setProducts(list);
      } catch (err) {
        console.error("ProjectBoard fetch error:", err);
      }
      setLoading(false);
    };

    fetchAll();
  }, []);

  if (loading || products.length === 0) return null;

  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-16 border-t border-dashed border-border">
      <div className="text-center mb-10">
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-lg font-bold text-text-primary leading-snug"
        >
          우리가 직접 만든 것들.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 }}
          className="text-lg font-bold text-text-muted/60 leading-snug"
        >
          기획부터 배포까지 전 과정 문서 공개
        </motion.p>
      </div>

      <div className="space-y-3">
        {products.map((product, i) => {
          const isOpen = openId === product.id;
          return (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="bg-white border border-border rounded-xl overflow-hidden"
            >
              {/* 카드 헤더 */}
              <div className="flex items-stretch gap-2 p-3">
                <button
                  type="button"
                  onClick={() => {
                    if (product.works.length > 0) {
                      setOpenId(isOpen ? null : product.id);
                      track("expand_home_project", { projectId: product.id, open: !isOpen });
                    }
                  }}
                  className="flex-1 text-left rounded-lg p-2 hover:bg-gray-50 active:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0 ${STATUS_COLOR[product.status]}`}>
                        {STATUS_LABEL[product.status]}
                      </span>
                      <h3 className="font-bold text-sm text-text-primary truncate">{product.title}</h3>
                    </div>
                    {product.works.length > 0 ? (
                      <span className="flex items-center gap-1 text-[11px] text-text-muted shrink-0">
                        <span>{product.works.length}건</span>
                        <ChevronDown
                          size={16}
                          className={`transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
                        />
                      </span>
                    ) : null}
                  </div>
                  <p className="text-xs text-text-muted">{product.desc}</p>
                </button>

                {product.link && (
                  <a
                    href={product.link}
                    target="_blank"
                    rel="noreferrer"
                    className="shrink-0 self-center p-3 rounded-lg text-text-muted/50 hover:text-primary hover:bg-gray-50 active:bg-gray-100 transition-colors"
                    aria-label="프로젝트 링크 열기"
                  >
                    <ExternalLink size={16} />
                  </a>
                )}
              </div>

              {/* 문서 목록 */}
              <AnimatePresence>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="px-4 pb-4 space-y-2 border-t border-border/50 pt-3">
                      {groupWorks(product.works).map(([groupLabel, items]) => (
                        <div key={groupLabel} className="rounded-lg border border-border/60 p-2">
                          <p className="text-[10px] font-bold text-text-muted mb-1">{groupLabel}</p>
                          <div className="space-y-1.5">
                            {items.map((work) => {
                              const internalHref = work.docSlug ? `/docs?projectId=${encodeURIComponent(product.id)}&slug=${encodeURIComponent(work.docSlug)}` : "";
                              const href = internalHref || work.url || "";
                              const external = !!work.url && !internalHref;

                              return (
                                <div key={work.id} className="flex items-center gap-2">
                                  <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0 ${TYPE_STYLE[work.type] || "bg-gray-100 text-text-muted"}`}>
                                    {work.type}
                                  </span>
                                  {href ? (
                                    <a
                                      href={href}
                                      target={external ? "_blank" : undefined}
                                      rel={external ? "noreferrer" : undefined}
                                      onClick={() => {
                                        if (internalHref) {
                                          track("click_home_docs", { projectId: product.id, workId: work.id, slug: work.docSlug || "" });
                                        } else {
                                          track("click_home_work_item", { projectId: product.id, workId: work.id, href, external });
                                        }
                                      }}
                                      className="flex-1 text-xs text-text-primary hover:text-primary transition-colors rounded-md px-2 py-2 min-h-[36px] flex items-center justify-between gap-2"
                                    >
                                      <span>{work.displayTitle || work.title}</span>
                                      {work.displayDate ? <span className="text-[10px] text-text-muted shrink-0">{work.displayDate}</span> : null}
                                    </a>
                                  ) : (
                                    <span className="flex-1 text-xs text-text-primary px-2 py-2 min-h-[36px] flex items-center justify-between gap-2">
                                      <span>{work.displayTitle || work.title}</span>
                                      {work.displayDate ? <span className="text-[10px] text-text-muted shrink-0">{work.displayDate}</span> : null}
                                    </span>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
