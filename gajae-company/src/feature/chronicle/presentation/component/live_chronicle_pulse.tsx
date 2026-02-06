import React, { useEffect, useState } from 'react';
import { ChronicleService } from "@/feature/chronicle/domain/service/chronicle_service";
import { TimelineItem } from "@/feature/chronicle/domain/model/timeline";
import { Card, CardContent } from "@/common/component/ui/card";
import { Badge } from "@/common/component/ui/badge";
import { Terminal, Cpu, MessageSquare, Zap, Clock, ChevronRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

/**
 * [가재 컴퍼니] Live Chronicle Pulse (v1.0)
 * 의도: 대표님의 지시에 따라 사람들이 가장 궁금해하는 '일하는 방식'을 실시간 로그가 찍히는 듯한 카드뷰로 시각화함.
 */

export const LiveChroniclePulse = () => {
  const [logs, setLogs] = useState<TimelineItem[]>([]);
  const [displayLogs, setDisplayLogs] = useState<TimelineItem[]>([]);
  const service = new ChronicleService();

  useEffect(() => {
    const fetchLogs = async () => {
      const today = new Date().toISOString().split('T')[0];
      const data = await service.getTimelineByDate(today);
      // 최신순 정렬 후 위에서부터 하나씩 노출하기 위해 역순으로 준비
      setLogs(data.sort((a, b) => b.timestamp.localeCompare(a.timestamp)));
    };
    fetchLogs();
  }, []);

  useEffect(() => {
    if (logs.length > 0 && displayLogs.length === 0) {
      // 초기 3개 노출
      setDisplayLogs(logs.slice(0, 3));
    }

    const interval = setInterval(() => {
      if (logs.length > displayLogs.length) {
        setDisplayLogs(prev => [logs[prev.length], ...prev.slice(0, 4)]);
      }
    }, 4000); // 4초마다 새로운 로그 "타닥"하고 올라옴

    return () => clearInterval(interval);
  }, [logs, displayLogs]);

  const getIcon = (type: string) => {
    switch (type) {
      case 'command': return <Zap size={14} className="text-ghibli-orange" />;
      case 'meeting': return <MessageSquare size={14} className="text-ghibli-blue" />;
      default: return <Cpu size={14} className="text-ghibli-accent" />;
    }
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
        <Badge variant="outline" className="font-mono text-[10px] border-ghibli-accent/30 text-ghibli-accent animate-pulse">
          LIVE_PULSE_ACTIVE
        </Badge>
      </div>

      <div className="space-y-4 min-h-[400px]">
        <AnimatePresence mode="popLayout">
          {displayLogs.map((log, index) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1 - index * 0.2, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.5, type: "spring" }}
            >
              <Card className={`overflow-hidden border-none shadow-sm transition-all duration-500 bg-white/80 backdrop-blur-md ${index === 0 ? 'ring-2 ring-ghibli-accent/20 shadow-ghibli-accent/10' : ''}`}>
                <CardContent className="p-5 flex items-start gap-4">
                  <div className={`mt-1 p-2 rounded-xl bg-slate-50 border border-slate-100`}>
                    {getIcon(log.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 font-mono">
                        {log.timestamp.split('T')[1].substring(0, 5)}
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        log.type === 'command' ? 'bg-ghibli-orange/10 text-ghibli-orange' : 
                        log.type === 'meeting' ? 'bg-ghibli-blue/10 text-ghibli-blue' : 
                        'bg-ghibli-accent/10 text-ghibli-accent'
                      }`}>
                        {log.type.toUpperCase()}
                      </span>
                    </div>
                    <h3 className={`font-bold text-ghibli-text truncate ${index === 0 ? 'text-lg' : 'text-base opacity-70'}`}>
                      {log.title}
                    </h3>
                  </div>
                  {index === 0 && (
                     <div className="self-center">
                        <ChevronRight className="text-ghibli-accent animate-bounce-x" size={20} />
                     </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
      
      <div className="mt-8 text-center">
        <p className="text-xs text-slate-400 font-medium">
          ※ 실제 가재들의 워크스페이스에서 발생하는 실시간 로그입니다.
        </p>
      </div>
    </div>
  );
};
