"use client";

import { useLiveChat } from "@/hooks/use-live-chat";
import Image from "next/image";
import Link from "next/link";
import { ArrowRight, MessageSquare } from "lucide-react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";

export function RPGDialogue() {
  const { messages, loading } = useLiveChat(3); // 최신 메시지 3개
  const lastMessage = messages[messages.length - 1];
  
  // 메시지 내용이 없거나 로딩 중일 때 보여줄 기본 텍스트
  const content = loading 
    ? "통신 연결 중입니다... 잠시만 기다려주세요." 
    : (lastMessage?.content || "현재 대화 내용이 없습니다. 라이브를 시작해보세요!");

  // 에이전트별 프로필
  const agent = lastMessage?.agent || "main";
  const isUser = lastMessage?.role === "user" && (agent === "main" || !lastMessage?.agent);
  
  const PROFILES: Record<string, { image: string; name: string }> = {
    human: { image: "/profile-nangman.jpg", name: "낭만코딩 (CEO)" },
    main: { image: "/profile-secretary.jpg", name: "비서가재 🦞" },
    scout: { image: "/profile-scout.jpg", name: "탐정가재 🔍" },
    judge: { image: "/profile-judge.jpg", name: "판사가재 ⚖️" },
  };

  const profileKey = isUser ? "human" : (agent === "scout" ? "scout" : agent === "judge" ? "judge" : "main");
  const profile = PROFILES[profileKey] || PROFILES.main;
  const profileImage = profile.image;
  const characterName = profile.name;

  return (
    <div className="w-full max-w-2xl mx-auto px-4 z-10 relative">
      {/* RPG Dialogue Box */}
      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="rpg-dialogue p-4 md:p-6 bg-white relative mt-8"
      >
        {/* Character Portrait (Overlapping) */}
        <div className="absolute -top-12 -left-2 md:-left-8 w-24 h-24 md:w-32 md:h-32 bg-background border-2 border-text-primary rounded-lg overflow-hidden shadow-[4px_4px_0px_#3D3529] z-20 transform -rotate-3">
          <Image
            src={profileImage}
            alt="Character"
            fill
            className="object-cover"
            priority
          />
        </div>

        {/* Header & CTA */}
        <div className="flex justify-between items-start mb-2 pl-24 md:pl-28">
          <div className="flex flex-col">
            <span className="font-bold text-lg text-primary">{characterName}</span>
            <span className="text-xs text-text-muted font-mono">LIVE PREVIEW</span>
          </div>
          <Link 
            href="/live"
            className="group flex items-center gap-1 text-xs font-bold bg-primary text-white px-3 py-1.5 rounded hover:bg-primary-hover transition-colors"
          >
            <span>자세히 보기</span>
            <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        {/* Content Area */}
        <div className="relative mt-2 pl-2 md:pl-4 min-h-[100px] max-h-[160px] overflow-hidden">
          <div className="prose prose-sm prose-p:text-text-primary prose-pre:bg-gray-100 font-mono text-sm leading-relaxed">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
          {/* Fade Out Gradient */}
          <div className="absolute bottom-0 left-0 w-full h-12 bg-gradient-to-t from-white to-transparent" />
        </div>

        {/* Corner Decoration */}
        <div className="absolute bottom-2 right-2 text-primary/20 animate-pulse">
            <MessageSquare size={24} />
        </div>
      </motion.div>
    </div>
  );
}
