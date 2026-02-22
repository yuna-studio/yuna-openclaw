"use client";

import { useEffect, useState } from "react";
import { collection, query, orderBy, onSnapshot, getDocs } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ExternalLink } from "lucide-react";

interface WorkItem {
  id: string;
  title: string;
  url?: string;
  type: string;
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
            const worksSnap = await getDocs(
              query(collection(db, "projects", d.id, "works"), orderBy("order", "asc"))
            );
            return {
              id: d.id,
              title: data.title || "",
              desc: data.desc || "",
              status: data.status || "dev",
              link: data.link || "",
              order: data.order || 0,
              works: worksSnap.docs.map((w) => ({ id: w.id, ...w.data() })) as WorkItem[],
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
          기획서부터 배포까지 전부.
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
              <div className="flex items-center justify-between p-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${STATUS_COLOR[product.status]}`}>
                      {STATUS_LABEL[product.status]}
                    </span>
                    <h3 className="font-bold text-sm text-text-primary">{product.title}</h3>
                  </div>
                  <p className="text-xs text-text-muted">{product.desc}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0 ml-2">
                  {product.link && (
                    <a
                      href={product.link}
                      target="_blank"
                      rel="noreferrer"
                      className="text-text-muted/40 hover:text-primary transition-colors"
                    >
                      <ExternalLink size={14} />
                    </a>
                  )}
                  {product.works.length > 0 && (
                    <button
                      onClick={() => setOpenId(isOpen ? null : product.id)}
                      className="flex items-center gap-1 text-[10px] text-text-muted hover:text-primary transition-colors"
                    >
                      <span>{product.works.length}건</span>
                      <ChevronDown
                        size={14}
                        className={`transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
                      />
                    </button>
                  )}
                </div>
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
                    <div className="px-4 pb-4 space-y-1.5 border-t border-border/50 pt-3">
                      {product.works.map((work) => (
                        <div key={work.id} className="flex items-center gap-2">
                          <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${TYPE_STYLE[work.type] || "bg-gray-100 text-text-muted"}`}>
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
