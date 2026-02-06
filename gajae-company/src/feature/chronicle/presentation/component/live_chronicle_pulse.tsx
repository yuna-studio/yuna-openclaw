"use client";

import React, { useEffect, useState } from 'react';
import { Chronicle } from "../../domain/model/chronicle";
import { Terminal, Cpu, MessageSquare, Zap, ChevronRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { firebaseApp } from "@/core/config/firebase-config";
import { getFirestore, collection, query, where, orderBy, limit, onSnapshot } from "firebase/firestore";

/**
 * [가재 컴퍼니] Live Chronicle Pulse (v1.3)
 * 의도: 대표님의 지시에 따라 Firestore 실시간 연동을 구현하여 카드뷰 로그를 시각화함.
 * 수정: GitHub API 대신 Firebase Firestore 실시간 스냅샷 리스너 적용.
 */

export const LiveChroniclePulse = () => {
  const [displayLogs, setDisplayLogs] = useState<Chronicle[]>([]);
  const db = getFirestore(firebaseApp);

  useEffect(() => {
    const today = new Date().toISOString().split('T')[0].replace(/-/g, '');
    const q = query(
      collection(db, "chronicles"),
      where("date", "==", today),
      orderBy("time", "desc"),
      limit(5)
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const logsData: Chronicle[] = snapshot.docs.map(doc => doc.data() as Chronicle);
      setDisplayLogs(logsData);
    }, (error) => {
      console.error("Firestore onSnapshot error:", error);
    });

    return () => unsubscribe();
  }, [db]);

  const getIcon = (path: string) => {
    if (path.includes('/command/')) return <Zap size={14} className="text-ghibli-orange" />;
    if (path.includes('/meeting/')) return <MessageSquare size={14} className="text-ghibli-blue" />;
    return <Cpu size={14} className="text-ghibli-accent" />;
  };

  const getType = (path: string) => {
    if (path.includes('/command/')) return 'Command';
    if (path.includes('/meeting/')) return 'Meeting';
    return 'Pulse';
  };

  return (
    <div className="relative w-full max-w-4xl mx-auto py-12 px-4">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Terminal size={24} className="text-ghibli-text" />
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full animate-ping" />
          </div>
          <h2 className="text-2xl font-black text-ghibli-text tracking-tight">가재들의 실시간 일하는 방식</h2>
        </div>
        <div className="px-3 py-1 rounded-full border border-ghibli-accent/30 text-[10px] font-mono font-bold text-ghibli-accent animate-pulse uppercase tracking-widest flex items-center gap-2">
          <div className="w-1 h-1 bg-ghibli-accent rounded-full animate-pulse" />
          FIRESTORE_LIVE_SYNC
        </div>
      </div>

      <div className="space-y-4 min-h-[380px]">
        <AnimatePresence mode="popLayout">
          {displayLogs.length > 0 ? displayLogs.map((log, index) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1 - index * 0.2, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.5, type: "spring" }}
            >
              <div className={`overflow-hidden rounded-2xl transition-all duration-500 bg-white/80 backdrop-blur-md p-5 flex items-start gap-4 shadow-sm ${index === 0 ? 'ring-2 ring-ghibli-accent/20 shadow-md shadow-ghibli-accent/10' : ''}`}>
                <div className="mt-1 p-2 rounded-xl bg-slate-50 border border-slate-100 flex-shrink-0">
                  {getIcon(log.path || log.rawPath || "")}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 font-mono">
                      {log.time || "LOG"}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                      (log.path || log.rawPath || "").includes('/command/') ? 'bg-ghibli-orange/10 text-ghibli-orange' : 
                      (log.path || log.rawPath || "").includes('/meeting/') ? 'bg-ghibli-blue/10 text-ghibli-blue' : 
                      'bg-ghibli-accent/10 text-ghibli-accent'
                    }`}>
                      {getType(log.path || log.rawPath || "")}
                    </span>
                  </div>
                  <h3 className={`font-bold text-ghibli-text truncate ${index === 0 ? 'text-lg' : 'text-base opacity-70'}`}>
                    {log.title}
                  </h3>
                </div>
                {index === 0 && (
                   <div className="self-center flex-shrink-0">
                      <ChevronRight className="text-ghibli-accent animate-pulse" size={20} />
                   </div>
                )}
              </div>
            </motion.div>
          )) : (
            <div className="flex items-center justify-center h-48 text-slate-400 font-medium italic">
              성역의 실시간 로그를 동기화 중입니다...
            </div>
          )}
        </AnimatePresence>
      </div>
      
      <div className="mt-8 text-center">
        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.2em]">
          ※ 가재 컴퍼니 Firestore를 통해 실시간으로 중계되는 로그입니다
        </p>
      </div>
    </div>
  );
};
