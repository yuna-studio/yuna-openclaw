"use client";

import React, { useEffect, useState } from 'react';
import { Terminal, Zap, MessageSquare, Clock, ArrowRight, User } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { firebaseApp } from "@/core/config/firebase-config";
import { getFirestore, collection, query, orderBy, limit, onSnapshot } from "firebase/firestore";

/**
 * [가재 컴퍼니] Live Activity Stream (v1.0)
 * 의도: Firestore의 'commands'와 'meetings'를 실시간으로 통합하여 "피터지는 빌드 현장"을 중계함.
 */

interface Activity {
  id: string;
  type: 'command' | 'meeting';
  title: string;
  time: string;
  author: string;
  instruction?: string;
  host?: string;
}

export const LiveActivityStream = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const db = getFirestore(firebaseApp);

  useEffect(() => {
    // Interleave updates from both collections
    const commandsQuery = query(collection(db, "commands"), orderBy("createdAt", "desc"), limit(10));
    const meetingsQuery = query(collection(db, "meetings"), orderBy("createdAt", "desc"), limit(10));

    let latestCommands: Activity[] = [];
    let latestMeetings: Activity[] = [];

    const updateActivities = () => {
      const merged = [...latestCommands, ...latestMeetings]
        .sort((a, b) => b.time.localeCompare(a.time))
        .slice(0, 8);
      setActivities(merged);
    };

    const unsubCommands = onSnapshot(commandsQuery, (snap) => {
      latestCommands = snap.docs.map(doc => ({ ...doc.data(), type: 'command' } as Activity));
      updateActivities();
    });

    const unsubMeetings = onSnapshot(meetingsQuery, (snap) => {
      latestMeetings = snap.docs.map(doc => ({ ...doc.data(), type: 'meeting' } as Activity));
      updateActivities();
    });

    return () => {
      unsubCommands();
      unsubMeetings();
    };
  }, [db]);

  return (
    <div className="w-full max-w-5xl mx-auto py-12 px-4">
      <div className="flex items-center justify-between mb-10">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-3">
             <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
             <h2 className="text-2xl font-black text-ghibli-text tracking-tighter uppercase">성역 실시간 중계 <span className="text-slate-300 font-mono ml-2 text-lg">Live Feed</span></h2>
          </div>
          <p className="text-sm text-slate-400 font-medium italic">군단의 지능이 실시간으로 박제되는 순간입니다.</p>
        </div>
        <div className="px-4 py-1.5 rounded-xl border-2 border-ghibli-accent/10 bg-white/50 text-[10px] font-black text-ghibli-accent font-mono uppercase tracking-widest shadow-sm">
          Sanctuary_Sync_Active
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 min-h-[400px]">
        <AnimatePresence mode="popLayout">
          {activities.length > 0 ? activities.map((act, index) => (
            <motion.div
              key={act.id}
              initial={{ opacity: 0, scale: 0.98, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.4, delay: index * 0.05 }}
              className={`ghibli-card p-6 flex flex-col justify-between border-2 transition-all duration-500 hover:shadow-xl ${
                act.type === 'command' 
                ? 'bg-orange-50/30 border-ghibli-orange/10 hover:border-ghibli-orange/30' 
                : 'bg-blue-50/30 border-ghibli-blue/10 hover:border-ghibli-blue/30'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className={`px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest flex items-center gap-1.5 ${
                    act.type === 'command' ? 'bg-ghibli-orange text-white' : 'bg-ghibli-blue text-white'
                  }`}>
                    {act.type === 'command' ? <Zap size={10} /> : <MessageSquare size={10} />}
                    {act.type}
                  </div>
                  <div className="flex items-center gap-2 text-slate-400 font-mono text-[10px] font-bold">
                    <Clock size={12} />
                    {act.time}
                  </div>
                </div>
                
                <h3 className="text-lg font-black text-ghibli-text leading-tight mb-3 line-clamp-2">
                  {act.title}
                </h3>
                
                <p className="text-xs text-slate-500 font-medium line-clamp-2 mb-4 italic">
                  {act.type === 'command' ? act.instruction : `주관: ${act.host || act.author}`}
                </p>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                <div className="flex items-center gap-2">
                   <div className="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center border border-slate-200">
                      <User size={12} className="text-slate-400" />
                   </div>
                   <span className="text-[10px] font-black text-slate-400 uppercase tracking-wider">{act.author}</span>
                </div>
                <div className={`text-[10px] font-black flex items-center gap-1 ${
                    act.type === 'command' ? 'text-ghibli-orange' : 'text-ghibli-blue'
                }`}>
                    세부 공정 확인 <ArrowRight size={12} />
                </div>
              </div>
            </motion.div>
          )) : (
            <div className="col-span-full flex flex-col items-center justify-center py-32 border-2 border-dashed border-slate-200 rounded-[3rem] bg-slate-50/50">
               <div className="w-12 h-12 rounded-full border-4 border-ghibli-accent/20 border-t-ghibli-accent animate-spin mb-4" />
               <p className="text-slate-400 font-black text-sm uppercase tracking-widest">Awaiting First Pulse...</p>
               <p className="text-xs text-slate-300 mt-2 italic">대표님의 명령이 박제되기를 기다리고 있습니다.</p>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
