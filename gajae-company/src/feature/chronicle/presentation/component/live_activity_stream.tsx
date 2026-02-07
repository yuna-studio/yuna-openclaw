"use client";

import React, { useEffect, useState } from 'react';
import { Quote, Brain, User, Activity, LayoutGrid, CheckCircle2, Circle, HelpCircle, Zap, ShieldAlert, TrendingUp } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { firebaseApp } from "@/core/config/firebase-config";
import { getFirestore, collection, query, orderBy, limit, onSnapshot, doc, getDoc } from "firebase/firestore";
import Image from "next/image";

/**
 * [가재 컴퍼니] Sanctuary Live v11.0 (Task Dashboard & Global Stream)
 * 의도: 대표님의 지시에 따라 명령(Blueprint), 대화(Stream), 태스크(Dashboard)를 분리하여 가시화함.
 */

const TaskCard = ({ task }: { task: any }) => (
    <div className="p-4 rounded-3xl bg-white border border-slate-100 shadow-sm hover:shadow-md transition-all">
        <div className="flex items-center justify-between mb-2">
            <span className={`text-[8px] font-black px-2 py-0.5 rounded-md ${
                task.priority === 'P0' ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-500'
            }`}>
                {task.priority}
            </span>
            <span className="text-[8px] font-mono text-slate-300 font-bold uppercase">{task.assignId}</span>
        </div>
        <h5 className={`text-xs font-black mb-1 ${task.status === 'DONE' ? 'text-slate-300 line-through' : 'text-ghibli-text'}`}>
            {task.title}
        </h5>
        <div className="flex items-center gap-2">
            <div className={`w-1.5 h-1.5 rounded-full ${task.status === 'DONE' ? 'bg-green-500' : 'bg-ghibli-blue animate-pulse'}`} />
            <span className="text-[9px] font-bold text-slate-400 uppercase">{task.status}</span>
        </div>
    </div>
);

export const LiveActivityStream = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [commands, setCommands] = useState<any[]>([]);
  const db = getFirestore(firebaseApp);

  useEffect(() => {
    // 1. 글로벌 지능 스트림 (최신순)
    const qLogs = query(collection(db, "intelligence_stream"), orderBy("createdAt", "desc"), limit(30));
    const unsubLogs = onSnapshot(qLogs, (snap) => setLogs(snap.docs.map(doc => doc.data())));

    // 2. 활성 태스크 대시보드
    const qTasks = query(collection(db, "all_tasks"), orderBy("updatedAt", "desc"), limit(10));
    const unsubTasks = onSnapshot(qTasks, (snap) => setTasks(snap.docs.map(doc => doc.data())));

    // 3. 최신 명령 (Blueprint)
    const qCmds = query(collection(db, "commands"), orderBy("createdAt", "desc"), limit(5));
    const unsubCmds = onSnapshot(qCmds, (snap) => setCommands(snap.docs.map(doc => doc.data())));

    return () => { unsubLogs(); unsubTasks(); unsubCmds(); };
  }, [db]);

  const profileImg = "/assets/media/gajae-cute-chef.jpg";

  return (
    <div className="w-full max-w-7xl mx-auto py-12 px-4 flex flex-col lg:flex-row gap-12">
      
      {/* 🚀 LEFT: GLOBAL INTELLIGENCE STREAM (The "Raw" Logs) */}
      <div className="flex-1 space-y-12 order-2 lg:order-1">
        <div className="flex items-center gap-4 mb-8 px-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-ping" />
            <h2 className="text-3xl font-black text-ghibli-text tracking-tighter uppercase italic">
                지능 스트림 <span className="text-slate-300 font-mono text-xl not-italic ml-1">STREAM</span>
            </h2>
        </div>

        <div className="space-y-16 border-l-4 border-slate-50 pl-8 ml-4">
            <AnimatePresence mode="popLayout">
                {logs.map((log) => (
                    <motion.div key={log.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="relative">
                        <div className={`absolute -left-[42px] top-10 w-5 h-5 rounded-full border-4 border-white shadow-sm ${
                            log.type === 'QUESTION' ? 'bg-ghibli-orange' : 'bg-ghibli-blue'
                        }`} />
                        
                        <div className={`ghibli-card p-8 bg-white border border-slate-100 shadow-xl rounded-[3rem] transition-all hover:shadow-2xl ${
                            log.type === 'QUESTION' ? 'ring-2 ring-ghibli-orange/20' : ''
                        }`}>
                            {/* Type Badge */}
                            <div className="flex items-center justify-between mb-6">
                                <span className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border ${
                                    log.type === 'QUESTION' ? 'bg-orange-50 text-ghibli-orange border-ghibli-orange/20' :
                                    log.type === 'BLUEPRINT' ? 'bg-purple-50 text-purple-600 border-purple-200' :
                                    'bg-blue-50 text-ghibli-blue border-ghibli-blue/10'
                                }`}>
                                    {log.type}
                                </span>
                                <span className="text-[10px] font-mono text-slate-300 font-bold">{log.timestamp}</span>
                            </div>

                            <div className="flex items-center gap-4 mb-8">
                                <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-slate-100 shrink-0">
                                    <Image src={profileImg} alt="G" width={48} height={48} className="object-cover" />
                                </div>
                                <div>
                                    <h4 className="text-lg font-black text-ghibli-text leading-tight">{log.response?.from}</h4>
                                    <div className="flex items-center gap-2">
                                        <ArrowRight size={10} className="text-slate-300" />
                                        <span className="text-[9px] font-black text-slate-400 uppercase">To: {log.response?.to?.join(', ')}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Thought Box (Only if relevant) */}
                            {log.thought && (
                                <div className="bg-slate-50 p-6 rounded-3xl border border-slate-100 mb-6">
                                    <span className="text-[8px] font-black text-slate-300 uppercase tracking-widest block mb-2">Neural Thought</span>
                                    <p className="text-xs text-slate-500 font-bold leading-relaxed italic italic-pre-wrap whitespace-pre-wrap">{log.thought}</p>
                                </div>
                            )}

                            {/* Response Bubble */}
                            <div className={`p-6 rounded-[2.5rem] shadow-sm relative ${
                                log.type === 'QUESTION' ? 'bg-ghibli-orange text-white' : 'bg-slate-900 text-white'
                            }`}>
                                <p className="text-base md:text-xl font-black leading-snug whitespace-pre-wrap">
                                    "{log.response?.text}"
                                </p>
                                {log.type === 'QUESTION' && <div className="absolute top-4 right-6 opacity-20"><HelpCircle size={40} /></div>}
                            </div>
                        </div>
                    </motion.div>
                ))}
            </AnimatePresence>
        </div>
      </div>

      {/* 📊 RIGHT: TASK DASHBOARD & BLUEPRINTS */}
      <div className="w-full lg:w-96 space-y-12 order-1 lg:order-2">
        {/* 1. Command Blueprint (The Big Picture) */}
        <section className="bg-orange-50/50 p-8 rounded-[3.5rem] border-2 border-ghibli-orange/10 shadow-inner">
            <h3 className="text-sm font-black text-ghibli-orange uppercase tracking-[0.3em] mb-6 flex items-center gap-2">
                <Zap size={16} fill="currentColor" /> Active Blueprint
            </h3>
            <div className="space-y-4">
                {commands.map(cmd => (
                    <div key={cmd.id} className="p-5 bg-white/80 rounded-[2rem] border border-ghibli-orange/10 shadow-sm">
                        <p className="text-xs font-black text-ghibli-text leading-relaxed line-clamp-3 mb-3">
                            "{cmd.instruction}"
                        </p>
                        <div className="flex items-center justify-between">
                            <span className="text-[8px] font-mono text-slate-300 font-bold uppercase">{cmd.id}</span>
                            <span className="px-2 py-0.5 rounded bg-orange-100 text-ghibli-orange text-[8px] font-black uppercase tracking-widest">In_Refinement</span>
                        </div>
                    </div>
                ))}
            </div>
        </section>

        {/* 2. Task Dashboard */}
        <section className="bg-slate-900 p-8 rounded-[4rem] shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 opacity-5 text-ghibli-accent"><LayoutGrid size={120} /></div>
            <h3 className="text-sm font-black text-ghibli-accent uppercase tracking-[0.3em] mb-8 flex items-center gap-2 relative z-10">
                <TrendingUp size={16} /> Task Dashboard
            </h3>
            <div className="space-y-4 relative z-10">
                {tasks.map(task => (
                    <TaskCard key={task.id} task={task} />
                ))}
                {tasks.length === 0 && (
                    <div className="py-12 text-center">
                        <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest animate-pulse italic">Awaiting Task Distribution...</p>
                    </div>
                )}
            </div>
        </section>

        {/* 3. ROI Stats (Placeholder for upcoming logic) */}
        <section className="p-8 rounded-[3rem] bg-ghibli-blue/5 border border-ghibli-blue/10">
            <h3 className="text-sm font-black text-ghibli-blue uppercase tracking-[0.3em] mb-4 flex items-center gap-2">
                <Activity size={16} /> Swarm ROI
            </h3>
            <div className="flex items-end gap-2">
                <span className="text-4xl font-black text-ghibli-text tabular-nums">1.7</span>
                <span className="text-xs font-black text-ghibli-blue mb-1 uppercase tracking-widest">Intelligence Multiplier</span>
            </div>
        </section>
      </div>

    </div>
  );
};
