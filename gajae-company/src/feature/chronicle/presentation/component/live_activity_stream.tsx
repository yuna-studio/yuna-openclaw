"use client";

import React, { useEffect, useState } from 'react';
import { Zap, MessageSquare, Clock, ArrowRight, Brain, Target, Activity, Quote, PlayCircle, Terminal, MessageSquareQuote, ChevronRight, User, Users } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { firebaseApp } from "@/core/config/firebase-config";
import { getFirestore, collection, query, orderBy, limit, onSnapshot } from "firebase/firestore";
import Image from "next/image";

/**
 * [가재 컴퍼니] Live Activity Stream v9.0 (Conversation Optimized)
 * 의도: 대표님의 지시에 따라 모든 계층 구조를 제거하고 '날것의 대화(Raw Logs)'에 집중한 UI.
 */

export const LiveActivityStream = () => {
  const [commands, setCommands] = useState<any[]>([]);
  const db = getFirestore(firebaseApp);

  useEffect(() => {
    const q = query(collection(db, "commands"), orderBy("createdAt", "desc"), limit(20));
    return onSnapshot(q, (snap) => {
        setCommands(snap.docs.map(doc => doc.data()));
    });
  }, [db]);

  const profileImg = "/assets/media/gajae-cute-chef.jpg";

  return (
    <div className="w-full max-w-4xl mx-auto py-8 md:py-12 px-3 md:px-6">
      <div className="flex items-center gap-3 mb-16 px-2">
        <div className="w-3 h-3 bg-red-500 rounded-full animate-ping" />
        <h2 className="text-3xl md:text-5xl font-black text-ghibli-text tracking-tighter uppercase italic">
            바이브 실황 <span className="text-slate-300 font-mono text-xl md:text-3xl not-italic ml-1">LOGS</span>
        </h2>
      </div>

      <div className="space-y-40">
        <AnimatePresence mode="popLayout">
          {commands.length > 0 ? commands.map((cmd) => (
            <motion.div key={cmd.id} initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} className="relative">
                {/* 👑 ROOT: RAW CEO INSTRUCTION */}
                <div className="mb-12 relative px-2">
                    <div className="flex items-center gap-4 mb-6">
                        <div className="w-12 h-12 md:w-16 md:h-16 rounded-[1.5rem] bg-ghibli-orange text-white flex items-center justify-center shadow-xl border-4 border-white shrink-0">
                            <Quote size={24} fill="currentColor" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <span className="text-[10px] font-black text-ghibli-orange uppercase tracking-widest block mb-0.5">King Direct Message</span>
                            <div className="flex items-center gap-3">
                                <span className="text-slate-300 font-mono text-xs font-bold">{cmd.date} | {cmd.time}</span>
                                {cmd.status === 'resolved' && <span className="px-2 py-0.5 rounded-md bg-green-100 text-green-600 text-[8px] font-black uppercase tracking-widest">Captured</span>}
                            </div>
                        </div>
                    </div>
                    <div className="bg-orange-50/40 p-8 md:p-10 rounded-[3rem] border-2 border-ghibli-orange/20 shadow-inner">
                        <p className="text-xl md:text-3xl text-ghibli-text font-black leading-tight italic whitespace-pre-wrap">
                            "{cmd.instruction}"
                        </p>
                    </div>
                </div>

                {/* 💬 THE LOG STREAM (Conversation Fidelity) */}
                <div className="ml-4 md:ml-20 border-l border-slate-100 pl-6 md:pl-12 space-y-16 relative">
                    {cmd.logs?.map((log: any) => (
                        <motion.div key={log.id} className="relative group">
                            <div className="absolute -left-[32px] md:-left-[58px] top-10 w-4 h-4 md:w-8 md:h-8 rounded-full bg-white border-2 md:border-8 border-slate-100 group-hover:border-ghibli-accent transition-colors shadow-sm" />

                            <div className="ghibli-card p-8 md:p-12 bg-white border border-slate-100 shadow-2xl rounded-[3rem] transition-all duration-700 hover:shadow-ghibli-blue/10">
                                {/* Speaker Header */}
                                <div className="flex items-center gap-4 mb-10 pb-6 border-b-2 border-slate-50">
                                    <div className="w-12 h-12 md:w-16 md:h-16 rounded-full overflow-hidden border-2 border-white shadow-lg shrink-0">
                                        <Image src={profileImg} alt="G" width={64} height={64} className="object-cover" />
                                    </div>
                                    <div className="min-w-0 flex-1">
                                        <h4 className="text-lg md:text-2xl font-black text-ghibli-text truncate leading-tight mb-1">{log.response?.from}</h4>
                                        <div className="flex items-center gap-2">
                                            <span className="text-[10px] font-black text-ghibli-blue uppercase tracking-widest">Neural Sync</span>
                                            <div className="w-1 h-1 bg-slate-200 rounded-full" />
                                            <span className="text-[10px] font-mono text-slate-300">{log.timestamp}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Full Protocol Exposure */}
                                <div className="space-y-12">
                                    {/* Intent & Psychology */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="p-5 bg-slate-50/50 rounded-2xl border border-slate-100">
                                            <span className="text-[9px] font-black text-slate-300 uppercase block mb-2 tracking-widest">01. Intent</span>
                                            <p className="text-xs md:text-sm text-slate-600 font-bold leading-relaxed whitespace-pre-wrap">{log.intent}</p>
                                        </div>
                                        <div className="p-5 bg-blue-50/10 rounded-2xl border border-ghibli-blue/5">
                                            <span className="text-[9px] font-black text-ghibli-blue/30 uppercase block mb-2 tracking-widest">02. Psychology</span>
                                            <p className="text-xs md:text-sm text-slate-600 font-bold leading-relaxed whitespace-pre-wrap">{log.psychology}</p>
                                        </div>
                                    </div>

                                    {/* Logic Box */}
                                    <div className="bg-ghibli-bg p-8 rounded-[3rem] border-2 border-white shadow-inner relative overflow-hidden">
                                        <div className="absolute top-4 right-6 opacity-5 text-ghibli-blue"><Brain size={100} /></div>
                                        <span className="text-[9px] font-black text-ghibli-blue/30 uppercase tracking-widest block mb-4 relative z-10">03. Neural Thought Process</span>
                                        <p className="text-sm md:text-xl text-slate-700 font-bold leading-relaxed italic whitespace-pre-wrap relative z-10 opacity-80">
                                            {log.thought}
                                        </p>
                                    </div>

                                    {/* THE RESPONSE (The Chat Bubble) */}
                                    <div className="relative">
                                        <div className="bg-slate-900 p-8 md:p-12 rounded-[3.5rem] shadow-2xl relative border-l-[16px] border-ghibli-accent">
                                            <div className="flex flex-wrap items-center gap-3 mb-6">
                                                <div className="flex items-center gap-2 text-ghibli-accent/80 font-black text-[10px] uppercase tracking-widest bg-white/5 px-3 py-1 rounded-full">
                                                    <User size={12} /> {log.response?.from}
                                                </div>
                                                <ArrowRight size={14} className="text-white/20" />
                                                <div className="flex flex-wrap gap-2">
                                                    {log.response?.to?.map((recipient: string) => (
                                                        <span key={recipient} className="px-3 py-1 rounded-full bg-white/10 text-white text-[10px] font-black uppercase tracking-tighter">
                                                            @{recipient}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                            <p className="text-lg md:text-3xl text-white font-black leading-tight whitespace-pre-wrap underline decoration-ghibli-accent/20 decoration-8 underline-offset-[14px]">
                                                "{log.response?.text}"
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </motion.div>
          )) : (
            <div className="py-60 text-center">
                <div className="w-16 h-16 rounded-[2rem] border-8 border-ghibli-accent/10 border-t-ghibli-accent animate-spin mx-auto mb-6 shadow-2xl" />
                <p className="text-slate-400 font-black uppercase tracking-[0.8em] text-sm animate-pulse italic">Establishing High-Bandwidth Neural Link...</p>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
