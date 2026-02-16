"use client";

import { useLiveChat } from "@/hooks/use-live-chat";
import { ReactionBar } from "@/components/ui/reaction-bar";
import Link from "next/link";
import { ArrowRight, Circle, User, Bot } from "lucide-react";
import { checkIsActive, formatRelativeTime } from "@/lib/utils";
import { UI_TEXT } from "@/lib/constants";
import { useMemo } from "react";
import { AnimatePresence, motion } from "framer-motion";

export default function HomePage() {
  const { messages, loading, error } = useLiveChat(30);

  // 최신 user 메시지 1개, 최신 assistant 메시지 1개
  const { latestUser, latestAi } = useMemo(() => {
    let latestUser = null;
    let latestAi = null;
    // messages는 시간순(오래된→최신)이므로 뒤에서부터
    for (let i = messages.length - 1; i >= 0; i--) {
      const msg = messages[i];
      if (!latestUser && msg.role === "user" && (!msg.agent || msg.agent === "main")) latestUser = msg;
      if (!latestAi && msg.role === "assistant" && (!msg.agent || msg.agent === "main")) latestAi = msg;
      if (latestUser && latestAi) break;
    }
    return { latestUser, latestAi };
  }, [messages]);

  const lastMessage = messages[messages.length - 1];
  const isActive = checkIsActive(lastMessage?.timestamp);

  if (error) {
    return (
      <main className="flex flex-col items-center justify-center min-h-screen bg-background text-text-muted">
        <p>{UI_TEXT.UNEXPECTED_ERROR}</p>
      </main>
    );
  }

  return (
    <main className="flex flex-col items-center min-h-screen p-4 pt-8 relative overflow-hidden bg-background">
      {/* Background Ambience */}
      <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px] animate-pulse" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[400px] h-[400px] bg-yellow-100/50 rounded-full blur-[100px]" />

      {/* Status Header */}
      <div className="flex flex-col items-center gap-2 z-10 mt-4 mb-8">
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium glass border ${isActive ? 'text-status-success border-status-success/30' : 'text-text-muted border-gray-200'}`}>
          <Circle size={8} fill="currentColor" className={isActive ? "animate-pulse" : ""} />
          {isActive ? UI_TEXT.LIVE_ACTIVE : UI_TEXT.LIVE_OFFLINE}
        </div>
        {lastMessage && (
          <span className="text-xs text-text-secondary font-mono">
            {UI_TEXT.LAST_ACTIVITY} {formatRelativeTime(lastMessage.timestamp)}
          </span>
        )}
      </div>

      {/* Preview Bubbles — 고정 크기, 페이드 전환 */}
      <div className="w-full max-w-md mb-12 relative z-0">
        {loading ? (
          <div className="flex flex-col items-center gap-2 text-text-muted py-10">
            <span className="text-xs font-mono animate-pulse">{UI_TEXT.LOADING_SIGNAL}</span>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {/* 유저 버블 — 좌측 */}
            <AnimatePresence mode="wait">
              {latestUser && (
                <motion.div
                  key={latestUser.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.5 }}
                  className="flex justify-start"
                >
                  <div className="max-w-[75%]">
                    <div className="flex items-center gap-1.5 mb-1 opacity-60">
                      <div className="w-4 h-4 rounded-full bg-gray-200 flex items-center justify-center">
                        <User size={10} className="text-gray-600" />
                      </div>
                      <span className="text-[10px] text-text-secondary font-mono">{UI_TEXT.USER_NAME}</span>
                    </div>
                    <div className="px-4 py-3 rounded-2xl rounded-tl-none bg-primary/10 border border-primary/20 text-sm leading-relaxed">
                      <p className="line-clamp-3 whitespace-pre-wrap">{latestUser.content}</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* AI 버블 — 우측 */}
            <AnimatePresence mode="wait">
              {latestAi && (
                <motion.div
                  key={latestAi.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.5 }}
                  className="flex justify-end"
                >
                  <div className="max-w-[75%]">
                    <div className="flex items-center gap-1.5 mb-1 justify-end opacity-60">
                      <div className="w-4 h-4 rounded-full bg-primary/10 flex items-center justify-center">
                        <Bot size={10} className="text-primary" />
                      </div>
                      <span className="text-[10px] text-text-secondary font-mono">{UI_TEXT.AI_NAME}</span>
                    </div>
                    <div className="px-4 py-3 rounded-2xl rounded-tr-none bg-white border border-gray-100 shadow-sm text-sm leading-relaxed">
                      <p className="line-clamp-3 whitespace-pre-wrap">{latestAi.content}</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {!loading && messages.length === 0 && (
          <div className="text-center text-text-muted py-10 font-mono text-sm">
            &gt; {UI_TEXT.NO_LOGS}
          </div>
        )}
      </div>

      {/* Main Action — 우측 텍스트 버튼 */}
      <div className="w-full max-w-md flex justify-end z-20">
        <Link
          href="/live"
          className="group inline-flex items-center gap-1 text-sm text-text-secondary hover:text-primary transition-colors"
        >
          <span>{UI_TEXT.VIEW_FULL_LOG}</span>
          <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
        </Link>
      </div>

      <ReactionBar />
    </main>
  );
}
