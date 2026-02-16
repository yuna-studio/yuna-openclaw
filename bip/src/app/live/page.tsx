"use client";

import { useLiveChat } from "@/hooks/use-live-chat";
import { ChatBubble, DateDivider } from "@/components/ui/chat-bubble";
import { ReactionBar } from "@/components/ui/reaction-bar";
import Link from "next/link";
import { ChevronLeft, ArrowDown, Activity, Loader2, User } from "lucide-react";
import { useEffect, useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UI_TEXT } from "@/lib/constants";
import { db } from "@/lib/firebase";
import { rtdb } from "@/lib/firebase";
import { ref, set, onValue, onDisconnect, serverTimestamp as rtdbTimestamp } from "firebase/database";

function getDateKey(timestamp: string): string {
  try {
    const d = new Date(timestamp);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  } catch {
    return "";
  }
}

function formatDateLabel(dateKey: string): string {
  try {
    const [y, m, d] = dateKey.split("-").map(Number);
    const date = new Date(y, m - 1, d);
    return date.toLocaleDateString("ko-KR", { year: "numeric", month: "long", day: "numeric", weekday: "short" });
  } catch {
    return dateKey;
  }
}

export default function LivePage() {
  const { messages, loading, loadingMore, hasMore, newCount, loadMore, clearNewCount } = useLiveChat(30);
  const [initialScrollDone, setInitialScrollDone] = useState(false);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [viewerCount, setViewerCount] = useState(0);
  const bottomRef = useRef<HTMLDivElement>(null);
  const prevScrollHeightRef = useRef<number>(0);

  // Presence: RTDB 기반 접속자 관리 (onDisconnect로 자동 정리)
  useEffect(() => {
    if (!rtdb) return;
    const viewerId = Math.random().toString(36).slice(2, 10);
    const viewerRef = ref(rtdb, `viewers/${viewerId}`);
    const countRef = ref(rtdb, "viewers");

    // 접속 등록 + 연결 끊기면 자동 삭제
    set(viewerRef, { joinedAt: rtdbTimestamp() });
    onDisconnect(viewerRef).remove();

    // 접속자 수 실시간 구독
    const unsub = onValue(countRef, (snap) => {
      const val = snap.val();
      setViewerCount(val ? Object.keys(val).length : 0);
    });

    // 수동 정리 (탭 닫기)
    const cleanup = () => { set(viewerRef, null); };
    window.addEventListener("beforeunload", cleanup);

    return () => {
      cleanup();
      unsub();
      window.removeEventListener("beforeunload", cleanup);
    };
  }, []);

  // 초기 로딩 완료 시 맨 아래로
  useEffect(() => {
    if (!loading && messages.length > 0 && !initialScrollDone) {
      requestAnimationFrame(() => {
        window.scrollTo(0, document.body.scrollHeight);
        setInitialScrollDone(true);
      });
    }
  }, [loading, messages.length, initialScrollDone]);

  // 스크롤 감지
  const handleScroll = useCallback(() => {
    const isAtBottom = window.innerHeight + window.scrollY >= document.body.offsetHeight - 150;
    setShowScrollButton(!isAtBottom);

    // 상단 200px 이내 → 과거 메시지 로드
    if (window.scrollY < 200 && hasMore && !loadingMore && initialScrollDone) {
      prevScrollHeightRef.current = document.body.scrollHeight;
      loadMore().then(() => {
        // 스크롤 위치 유지
        requestAnimationFrame(() => {
          const diff = document.body.scrollHeight - prevScrollHeightRef.current;
          if (diff > 0) {
            window.scrollTo(0, window.scrollY + diff);
          }
        });
      });
    }
  }, [hasMore, loadingMore, loadMore, initialScrollDone]);

  useEffect(() => {
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, [handleScroll]);

  // 새 메시지 도착 → 맨 아래면 자동 스크롤
  useEffect(() => {
    if (initialScrollDone && !showScrollButton) {
      requestAnimationFrame(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
      });
      clearNewCount();
    }
  }, [messages.length, initialScrollDone, showScrollButton, clearNewCount]);

  const scrollToBottom = useCallback(() => {
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
    clearNewCount();
  }, [clearNewCount]);

  return (
    <div className="flex flex-col min-h-screen bg-background relative selection:bg-primary/20">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 h-14 glass z-40 flex items-center px-4 backdrop-blur-md bg-white/70 border-b border-gray-200 transition-all">
        <Link href="/" className="p-2 -ml-2 text-text-secondary hover:text-text-primary transition-colors flex items-center gap-1 group w-16">
          <ChevronLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-medium">{UI_TEXT.EXIT}</span>
        </Link>
        <span className="flex-1 text-center font-bold text-sm tracking-wide text-text-primary">{UI_TEXT.HEADER_TITLE}</span>
        <div className="w-16 flex justify-end">
          {viewerCount >= 10 && (
            <span className="flex items-center gap-1 text-[11px] text-text-muted">
              <User size={12} />
              시청자 {viewerCount}명
            </span>
          )}
          {viewerCount >= 3 && viewerCount < 10 && (
            <span className="flex items-center gap-1 text-[11px] text-text-muted">
              <User size={12} />
              몇 명이 보는 중
            </span>
          )}
        </div>
      </header>

      {/* LIVE 뱃지 — 앱바 아래 간격 띄워서 플로팅 */}
      <div className="fixed top-[4.25rem] inset-x-0 z-30 flex justify-center pointer-events-none">
        <div className="flex items-center gap-1.5 bg-green-500/15 backdrop-blur-sm rounded-full px-3 py-1 shadow-sm border border-green-500/10 pointer-events-auto">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
          <span className="text-[10px] font-bold text-green-600 tracking-wider">LIVE</span>
        </div>
      </div>

      {/* Chat Stream — 시간순 (오래된 위, 최신 아래) */}
      <div className="flex-1 w-full max-w-3xl mx-auto p-4 pt-24 pb-32 min-h-screen">
        {/* 과거 메시지 로딩 */}
        {loadingMore && (
          <div className="flex items-center justify-center py-4 gap-2">
            <Loader2 className="text-primary animate-spin" size={18} />
            <span className="text-text-muted text-xs font-mono">{UI_TEXT.LOADING_SIGNAL}</span>
          </div>
        )}

        {!hasMore && messages.length > 0 && (
          <div className="text-center py-6">
            <span className="text-text-muted text-xs font-mono">여기서부터 이야기가 시작됐어요 ✨</span>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-40 gap-4">
            <Activity className="text-primary animate-spin" size={32} />
            <span className="text-text-muted font-mono text-sm animate-pulse">{UI_TEXT.SYNCING}</span>
          </div>
        )}

        <div>
          {messages.map((msg, idx) => {
            const prevMsg = idx > 0 ? messages[idx - 1] : null;
            const showHeader = !prevMsg || prevMsg.role !== msg.role;

            const currentDate = getDateKey(msg.timestamp);
            const prevDate = prevMsg ? getDateKey(prevMsg.timestamp) : "";
            const showDate = idx === 0 || (prevDate && currentDate !== prevDate);

            return (
              <div key={msg.id}>
                {showDate && currentDate && (
                  <DateDivider date={formatDateLabel(currentDate)} />
                )}
                <ChatBubble
                  message={msg}
                  isLatest={idx === messages.length - 1}
                  showHeader={showHeader || !!showDate}
                />
              </div>
            );
          })}
        </div>

        <div ref={bottomRef} className="h-1" />
      </div>

      {/* 새 메시지 알림 (화면 전체 중앙) — 안 본 새 메시지가 있을 때만 */}
      <AnimatePresence>
        {newCount > 0 && showScrollButton && (
          <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            onClick={scrollToBottom}
            className="fixed bottom-20 inset-x-0 mx-auto w-fit z-30 bg-primary/90 hover:bg-primary text-white px-5 py-2.5 rounded-full shadow-lg flex items-center gap-2 text-xs font-bold transition-all backdrop-blur-sm"
          >
            <ArrowDown size={14} />
            <span>새 메시지 {newCount}개</span>
          </motion.button>
        )}
      </AnimatePresence>

      {/* 아래로 가기 버튼 (우측 하단, 하트와 같은 높이) — 스크롤 올렸을 때, 새 메시지 없을 때 */}
      <AnimatePresence>
        {showScrollButton && newCount === 0 && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={scrollToBottom}
            className="fixed bottom-7 right-6 z-30 bg-white/90 hover:bg-white text-text-secondary p-2 rounded-full shadow-lg border border-gray-200 transition-all backdrop-blur-sm"
            aria-label="아래로 가기"
          >
            <ArrowDown size={16} />
          </motion.button>
        )}
      </AnimatePresence>

      <ReactionBar />
    </div>
  );
}
