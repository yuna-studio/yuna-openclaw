"use client";

import { useLiveChat } from "@/hooks/use-live-chat";
import { ChatBubble } from "@/components/ui/chat-bubble";
import { ReactionBar } from "@/components/ui/reaction-bar";
import Link from "next/link";
import { ChevronLeft, Zap, ArrowDown, Activity } from "lucide-react";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UI_TEXT } from "@/lib/constants";

export default function LivePage() {
  const { messages, loading, scrollRef, scrollToBottom } = useLiveChat(100); // 100개 제한
  const [showScrollButton, setShowScrollButton] = useState(false);

  // 스크롤 감지 로직
  useEffect(() => {
    const handleScroll = () => {
      // 윈도우 스크롤 기준
      const isAtBottom = window.innerHeight + window.scrollY >= document.body.offsetHeight - 150;
      setShowScrollButton(!isAtBottom);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // 새 메시지 수신 시 자동 스크롤 (사용자가 하단에 있을 때만)
  useEffect(() => {
    if (!showScrollButton && !loading) {
      scrollToBottom();
    }
  }, [messages, scrollToBottom, showScrollButton, loading]);

  return (
    <div className="flex flex-col min-h-screen bg-background relative selection:bg-primary/20">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 h-16 glass z-40 flex items-center px-4 justify-between backdrop-blur-md bg-white/70 border-b border-gray-200 transition-all">
        <Link 
          href="/" 
          className="p-2 -ml-2 text-text-secondary hover:text-text-primary transition-colors flex items-center gap-1 group"
        >
          <ChevronLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-medium">{UI_TEXT.EXIT}</span>
        </Link>
        
        <div className="flex items-center gap-2">
          <Zap size={16} className="text-reaction-lol fill-reaction-lol animate-pulse" />
          <span className="font-bold text-sm tracking-wide text-text-primary font-mono">{UI_TEXT.LIVE_LOGS_TITLE}</span>
        </div>
        
        <div className="w-12 flex justify-end">
            <div className="w-2 h-2 rounded-full bg-status-live animate-pulse" />
        </div>
      </header>

      {/* Chat Stream */}
      <div className="flex-1 w-full max-w-3xl mx-auto p-4 pt-24 pb-32 min-h-screen">
        {loading && (
          <div className="flex flex-col items-center justify-center py-40 gap-4">
            <Activity className="text-primary animate-spin" size={32} />
            <span className="text-text-muted font-mono text-sm animate-pulse">{UI_TEXT.SYNCING}</span>
          </div>
        )}
        
        <div className="space-y-4">
          {messages.map((msg, idx) => (
            <ChatBubble 
              key={msg.id} 
              message={msg} 
              isLatest={idx === messages.length - 1} 
            />
          ))}
        </div>
        
        {/* Invisible anchor for scrolling */}
        <div ref={scrollRef} className="h-1" />
      </div>

      {/* Scroll to Bottom Button (New Message Notification) */}
      <AnimatePresence>
        {showScrollButton && (
          <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            onClick={scrollToBottom}
            className="fixed bottom-24 left-1/2 -translate-x-1/2 z-30 bg-primary/90 hover:bg-primary text-white px-5 py-2.5 rounded-full shadow-lg flex items-center gap-2 text-xs font-bold transition-all backdrop-blur-sm"
          >
            <ArrowDown size={14} />
            <span>{UI_TEXT.NEW_LOGS}</span>
          </motion.button>
        )}
      </AnimatePresence>

      <ReactionBar />
    </div>
  );
}
