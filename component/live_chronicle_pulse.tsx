"use client";

import React, { useEffect, useState } from 'react';
import { ChronicleService } from "@/feature/chronicle/domain/service/chronicle_service";
import { Chronicle } from "../../domain/model/chronicle";
import { Terminal, Cpu, MessageSquare, Zap, ChevronRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

/**
 * [가재 컴퍼니] Live Chronicle Pulse (v1.2)
 * 의도: 대표님의 지시에 따라 사람들이 가장 궁금해하는 '일하는 방식'을 실시간 로그가 찍히는 듯한 카드뷰로 시각화함.
 * 수정: 모델명을 Chronicle로 정정하고, 타입 추론 오류를 해결함.
 */

export const LiveChroniclePulse = () => {
  const [logs, setLogs] = useState<Chronicle[]>([]);
  const [displayLogs, setDisplayLogs] = useState<Chronicle[]>([]);
  const service = new ChronicleService();

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const today = new Date().toISOString().split('T')[0].replace(/-/g, '');
        // Note: ChronicleService.getTimelineByDate uses API which returns data
        const response = await fetch(`/api/chronicle/${today}`);
        const data: Chronicle[] = await response.json();
        
        // 시간순 정렬 (최신순)
        setLogs(data.sort((a, b) => {
           const timeA = a.time || "00:00";
           const timeB = b.time || "00:00";
           return timeB.localeCompare(timeA);
        }));
      } catch (e) {
        console.error("Failed to fetch logs:", e);
      }
    };
    fetchLogs();
  }, []);

  useEffect(() => {
    if (logs.length > 0 && displayLogs.length === 0) {
      setDisplayLogs(logs.slice(0, 3));
    }

    const interval = setInterval(() => {
      if (logs.length > displayLogs.length) {
        setDisplayLogs(prev => [logs[prev.length], ...prev.slice(0, 4)]);
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [logs, displayLogs]);

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
        <div className="px-3 py-1 rounded-full border border-ghibli-accent/30 text-[10px] font-mono font-bold text-ghibli-accent animate-pulse uppercase tracking-widest">
          LIVE_PULSE_ACTIVE
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
                  {getIcon(log.path)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 font-mono">
                      {log.time || "LOG"}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                      log.path.includes('/command/') ? 'bg-ghibli-orange/10 text-ghibli-orange' : 
                      log.path.includes('/meeting/') ? 'bg-ghibli-blue/10 text-ghibli-blue' : 
                      'bg-ghibli-accent/10 text-ghibli-accent'
                    }`}>
                      {getType(log.path)}
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
              가재들이 생각 중입니다...
            </div>
          )}
        </AnimatePresence>
      </div>
      
      <div className="mt-8 text-center">
        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.2em]">
          ※ 실제 가재들의 워크스페이스에서 발생하는 실시간 로그입니다
        </p>
      </div>
    </div>
  );
};
