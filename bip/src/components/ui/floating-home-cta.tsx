"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { track } from "@/lib/logging";

const HOOKS = [
  "시니어는 바이브코딩을 어떻게 할까? →",
  "AI랑 진짜 제품 만드는 과정 보기 →",
  "바이브코딩 실전, 처음부터 끝까지 →",
];

export function FloatingHomeCta() {
  const pathname = usePathname();
  const [dismissed, setDismissed] = useState(false);
  const [hookIndex, setHookIndex] = useState(0);

  // 홈에서는 숨김
  const isHome = pathname === "/";

  useEffect(() => {
    setHookIndex(Math.floor(Math.random() * HOOKS.length));
  }, []);

  if (isHome || dismissed) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.9 }}
        animate={{
          opacity: 1,
          y: [0, -6, 0],
          scale: 1,
        }}
        exit={{ opacity: 0, y: 20, scale: 0.9 }}
        transition={{
          opacity: { duration: 0.3 },
          scale: { duration: 0.3 },
          y: {
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut",
          },
        }}
        className="fixed bottom-6 right-4 z-50 max-w-[220px]"
      >
        <div className="relative">
          {/* 닫기 버튼 */}
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setDismissed(true);
              track("dismiss_home_cta", { page: pathname });
            }}
            className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-white border border-border shadow-sm flex items-center justify-center text-text-muted hover:text-text-primary hover:bg-gray-50 transition-colors z-10"
            aria-label="닫기"
          >
            <X size={10} />
          </button>

          {/* CTA 버튼 */}
          <Link
            href="/"
            onClick={() => track("click_home_cta", { page: pathname, hook: HOOKS[hookIndex] })}
            className="block glass shadow-lg hover:shadow-xl rounded-2xl px-4 py-3 transition-all hover:scale-[1.02] active:scale-95 border border-primary/20"
          >
            <p className="text-[11px] font-bold text-primary leading-snug">
              {HOOKS[hookIndex]}
            </p>
            <p className="text-[10px] text-text-muted mt-1">
              기획부터 삽질까지 전 과정 공개
            </p>
          </Link>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
