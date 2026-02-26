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

/** 홈 페이지용 — 섹션 카드 */
export function CurrentWorkBanner() {
  const { data, loading } = useCurrentWork();

  const [ago, setAgo] = useState("");
  useEffect(() => {
    if (!data?.updatedAt) return;
    setAgo(timeAgo(data.updatedAt));
    const timer = setInterval(() => setAgo(timeAgo(data.updatedAt)), 5000);
    return () => clearInterval(timer);
  }, [data?.updatedAt]);

  if (loading) {
    return (
      <div className="w-full max-w-2xl mx-auto px-4 pb-8">
        <div className="flex items-center gap-2 mb-3">
          <div className="h-6 w-24 bg-gray-200 rounded-full animate-pulse" />
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="h-4 w-16 bg-gray-200 rounded animate-pulse" />
            <div className="h-4 w-24 bg-gray-200 rounded animate-pulse" />
          </div>
          <div className="h-5 w-3/4 bg-gray-200 rounded animate-pulse" />
          <div className="flex items-center justify-between">
            <div className="h-4 w-12 bg-gray-200 rounded animate-pulse" />
            <div className="h-3 w-20 bg-gray-200 rounded animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  if (!data || !data.isActive) return null;

  return (
    <div className="w-full max-w-2xl mx-auto px-4 pb-8">
      {/* 섹션 헤더 */}
      <div className="flex items-center gap-2 mb-3">
        <div className="flex items-center gap-1.5 bg-primary/10 px-2.5 py-1 rounded-full">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          <span className="text-xs font-bold text-primary">지금 작업 중</span>
        </div>
        <span className="text-[10px] text-text-muted">현재 진행 중인 태스크</span>
      </div>

      {/* 카드 */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4"
      >
        {/* 상단: 활성 표시 + 프로젝트명 */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
            <span className="text-[10px] font-bold text-primary tracking-wider uppercase">
              작업 중
            </span>
          </div>
          <span className="text-xs font-mono font-bold text-text-muted">
            {data.projectTitle}
          </span>
        </div>

        {/* 메인: 태스크 제목 */}
        <p className="text-sm font-bold text-text-primary leading-snug mb-3">
          {data.taskTitle}
        </p>

        {/* 하단: 타입 배지 + 업데이트 시간 */}
        <div className="flex items-center justify-between">
          <span
            className={`text-[9px] font-bold px-2 py-0.5 rounded ${
              TYPE_STYLE[data.taskType] || "bg-gray-100 text-text-muted"
            }`}
          >
            {data.taskType}
          </span>
          {ago && (
            <span className="text-[10px] text-text-muted font-mono">
              {ago} 업데이트
            </span>
          )}
        </div>
      </motion.div>
    </div>
  );
}

/** 라이브 페이지용 — 플로팅 pill (기존 LIVE 뱃지 대체) */
export function CurrentWorkBannerPill() {
  const { data, loading } = useCurrentWork();

  // 데이터 없거나 로딩 중이면 기본 LIVE pill
  if (loading || !data || !data.isActive) {
    return (
      <div className="absolute top-[4.25rem] inset-x-0 z-30 flex justify-center pointer-events-none">
        <div className="flex items-center gap-1.5 bg-white/90 backdrop-blur-sm rounded-full px-3 py-1 shadow-sm border border-border pointer-events-auto">
          <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
          <span className="text-[10px] font-bold text-primary tracking-wider">
            LIVE
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="absolute top-[4.25rem] inset-x-0 z-30 flex justify-center pointer-events-none">
      <motion.div
        initial={{ opacity: 0, y: -4 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-2 bg-white/90 backdrop-blur-sm rounded-full px-3 py-1.5 shadow-sm border border-border pointer-events-auto max-w-[320px]"
      >
        {/* LIVE 표시 */}
        <div className="flex items-center gap-1 shrink-0">
          <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
          <span className="text-[10px] font-bold text-primary tracking-wider">
            LIVE
          </span>
        </div>

        {/* 구분선 */}
        <div className="w-px h-3 bg-border shrink-0" />

        {/* 작업 타입 배지 */}
        <span
          className={`text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0 ${
            TYPE_STYLE[data.taskType] || "bg-gray-100 text-text-muted"
          }`}
        >
          {data.taskType}
        </span>

        {/* 작업 제목 */}
        <span className="text-[10px] text-text-secondary truncate">
          {data.taskTitle}
        </span>
      </motion.div>
    </div>
  );
}
