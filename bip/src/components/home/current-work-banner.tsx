"use client";

import { useCurrentWork } from "@/hooks/use-current-work";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

const TYPE_STYLE: Record<string, string> = {
  "기획": "bg-blue-100 text-blue-700",
  "설계": "bg-purple-100 text-purple-700",
  "개발": "bg-amber-100 text-amber-700",
  "배포": "bg-green-100 text-green-700",
};

function timeAgo(timestamp: string): string {
  try {
    const now = Date.now();
    const then = new Date(timestamp).getTime();
    const diff = Math.floor((now - then) / 1000);

    if (diff < 10) return "방금 전";
    if (diff < 60) return `${diff}초 전`;
    if (diff < 3600) return `${Math.floor(diff / 60)}분 전`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`;
    return `${Math.floor(diff / 86400)}일 전`;
  } catch {
    return "";
  }
}

/** 홈 페이지용 — 채팅 섹션과 자연스럽게 이어지는 컴팩트 status strip */
export function CurrentWorkBanner() {
  const { data, loading } = useCurrentWork();

  const [ago, setAgo] = useState("");
  useEffect(() => {
    if (!data?.updatedAt) return;
    setAgo(timeAgo(data.updatedAt));
    const timer = setInterval(() => setAgo(timeAgo(data.updatedAt)), 5000);
    return () => clearInterval(timer);
  }, [data?.updatedAt]);

  if (loading || !data || !data.isActive) return null;

  return (
    <div className="w-full max-w-2xl mx-auto px-4 pb-2">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-2 rounded-full px-3 py-1.5 bg-white/70 backdrop-blur-sm border border-border/50"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse shrink-0" />
        <span className="text-[10px] font-bold text-primary shrink-0">작업 중</span>
        <div className="w-px h-3 bg-border shrink-0" />
        <span
          className={`text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0 ${
            TYPE_STYLE[data.taskType] || "bg-gray-100 text-text-muted"
          }`}
        >
          {data.taskType}
        </span>
        <span className="text-[11px] font-medium text-text-primary truncate">
          {data.taskTitle}
        </span>
        <span className="text-[9px] text-text-muted/60 font-mono shrink-0 ml-auto whitespace-nowrap">
          {data.projectTitle}
        </span>
      </motion.div>
    </div>
  );
}

/** 라이브 페이지용 — 플로팅 pill */
export function CurrentWorkBannerPill() {
  const { data, loading } = useCurrentWork();

  if (loading || !data || !data.isActive) return null;

  return (
    <div className="absolute top-[4.25rem] inset-x-0 z-30 flex justify-center pointer-events-none">
      <motion.div
        initial={{ opacity: 0, y: -4 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-1.5 bg-white/90 backdrop-blur-sm rounded-full px-3 py-1.5 shadow-sm border border-border pointer-events-auto max-w-[90vw]"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse shrink-0" />
        <span className="text-[10px] font-bold text-primary shrink-0">작업 중</span>
        <span
          className={`text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0 ${
            TYPE_STYLE[data.taskType] || "bg-gray-100 text-text-muted"
          }`}
        >
          {data.taskType}
        </span>
        <span className="text-[10px] font-medium text-text-secondary truncate">{data.projectTitle}</span>
        <span className="text-text-muted/30 text-[10px]">›</span>
        <span className="text-[10px] text-text-muted truncate">{data.taskTitle}</span>
      </motion.div>
    </div>
  );
}
