"use client";

import { useEffect, useState } from "react";
import { collection, query, orderBy, onSnapshot } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

interface WorkItem {
  id: string;
  title: string;
  url?: string;
  type: "기획" | "설계" | "개발" | "배포";
  order: number;
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

const TYPE_STYLE: Record<string, string> = {
  "기획": "bg-blue-100 text-blue-700",
  "설계": "bg-purple-100 text-purple-700",
  "개발": "bg-amber-100 text-amber-700",
  "배포": "bg-green-100 text-green-700",
};

const STATUS_BADGE: Record<string, { label: string; style: string }> = {
  dev: { label: "🚧 개발중", style: "bg-yellow-100 text-yellow-800" },
  shipped: { label: "🚀 배포완료", style: "bg-green-100 text-green-800" },
  hold: { label: "⏸️ 보류", style: "bg-gray-100 text-gray-800" },
};

export function ProjectBoard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [openId, setOpenId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // 프로젝트 목록 실시간 구독
  useEffect(() => {
    if (!db) { setLoading(false); return; }

    const q = query(collection(db, "projects"), orderBy("order", "asc"));
    const unsubscribe = onSnapshot(q, async (snapshot) => {
      const projectList: Product[] = [];

      for (const doc of snapshot.docs) {
        const data = doc.data();
        // 서브컬렉션 works 가져오기
        const worksQ = query(
          collection(db, "projects", doc.id, "works"),
          orderBy("order", "asc")
        );

        const works = await new Promise<WorkItem[]>((resolve) => {
          const unsub = onSnapshot(worksQ, (ws) => {
            const items = ws.docs.map((w) => ({
              id: w.id,
              ...w.data(),
            })) as WorkItem[];
            resolve(items);
            unsub();
          });
        });

        projectList.push({
          id: doc.id,
          title: data.title || "",
          desc: data.desc || "",
          status: data.status || "dev",
          link: data.link || "",
          order: data.order || 0,
          works,
        });
      }

      setProducts(projectList);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  if (loading) {
    return (
      <div className="w-full max-w-2xl mx-auto px-4 py-16 border-t border-dashed border-border">
        <div className="text-center mb-12">
          <p className="text-lg font-bold text-text-primary leading-snug">가재들이 직접 만든 것들.</p>
          <p className="text-lg font-bold text-text-muted/50 leading-snug">기획서부터 배포까지 전부.</p>
        </div>
        <div className="text-xs text-text-muted text-center py-8 animate-pulse">불러오는 중...</div>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="w-full max-w-2xl mx-auto px-4 py-16 border-t border-dashed border-border">
        <div className="text-center mb-12">
          <p className="text-lg font-bold text-text-primary leading-snug">가재들이 직접 만든 것들.</p>
          <p className="text-lg font-bold text-text-muted/50 leading-snug">기획서부터 배포까지 전부.</p>
        </div>
        <div className="text-xs text-text-muted text-center py-8">아직 등록된 프로젝트가 없어요</div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-16 border-t border-dashed border-border">
      {/* 헤드 카피 */}
      <div className="text-center mb-12">
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-lg font-bold text-text-primary leading-snug"
        >
          가재들이 직접 만든 것들.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 }}
          className="text-lg font-bold text-text-muted/50 leading-snug"
        >
          기획서부터 배포까지 전부.
        </motion.p>
      </div>

      <div className="space-y-3">
        {products.map((product) => {
          const isOpen = openId === product.id;
          const status = STATUS_BADGE[product.status] || STATUS_BADGE.dev;
          return (
            <motion.div
              key={product.id}
              initial={{ x: -10, opacity: 0 }}
              whileInView={{ x: 0, opacity: 1 }}
              viewport={{ once: true }}
              className="bg-white border border-border rounded-lg shadow-sm overflow-hidden"
            >
              {/* 제품 헤더 */}
              <button
                onClick={() => setOpenId(isOpen ? null : product.id)}
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors text-left"
              >
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${status.style}`}>
                      {status.label}
                    </span>
                    <h3 className="font-bold text-text-primary text-sm">{product.title}</h3>
                  </div>
                  <p className="text-xs text-text-secondary">{product.desc}</p>
                  {product.link && (
                    <a
                      href={product.link}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="inline-flex items-center gap-1 text-[10px] text-primary hover:underline mt-1"
                    >
                      🔗 {product.link}
                    </a>
                  )}
                </div>
                <div className="flex items-center gap-2 shrink-0 ml-2">
                  <span className="text-[10px] text-text-muted">{product.works.length}건</span>
                  <ChevronDown
                    size={16}
                    className={`text-text-muted transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
                  />
                </div>
              </button>

              {/* 작업 내역 */}
              <AnimatePresence>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="px-4 pb-4 space-y-2 border-t border-border/50">
                      <p className="text-[10px] text-text-muted pt-3 pb-1">🦞 가재들이 만든 문서들</p>
                      {product.works.map((work) => (
                        <div key={work.id} className="flex items-center gap-2">
                          <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${TYPE_STYLE[work.type] || "bg-gray-100 text-gray-700"}`}>
                            {work.type}
                          </span>
                          {work.url ? (
                            <a
                              href={work.url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-xs text-text-primary hover:text-primary hover:underline transition-colors"
                            >
                              {work.title}
                            </a>
                          ) : (
                            <span className="text-xs text-text-primary">{work.title}</span>
                          )}
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
