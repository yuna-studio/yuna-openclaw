"use client";

import { useState, useEffect, Suspense } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSanctuaryStore } from "../store/sanctuary_store";
import { Chronicle } from "../../domain/model/chronicle";
import { Calendar, ChevronRight, Clock, FileText, Sparkles, BookOpen } from "lucide-react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

const TimelineContent = ({ initialDates }: { initialDates: string[] }) => {
  const searchParams = useSearchParams();
  const filter = searchParams.get("filter");

  const { 
    selectedDate, 
    setSelectedDate, 
    timeline, 
    setTimeline, 
    isLoading, 
    setIsLoading 
  } = useSanctuaryStore();

  const filteredTimeline = filter === "command" 
    ? timeline.filter(item => item.path.includes("/command/"))
    : timeline;

  const fetchChronicles = async (date: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/chronicle/${date}`);
      const data = await response.json();
      setTimeline(data);
    } catch (error) {
      console.error("Fetch error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (initialDates.length > 0 && !selectedDate) {
      handleDateSelect(initialDates[0]);
    }
  }, [initialDates]);

  const handleDateSelect = (date: string) => {
    setSelectedDate(date);
    fetchChronicles(date);
  };

  const formatHeaderDate = (date: string) => {
    if (!date) return "날짜를 선택하세요";
    if (date.includes("-")) {
      const parts = date.split("-");
      if (parts.length === 3) return `${parts[0]}년 ${parts[1]}월 ${parts[2]}일`;
    }
    if (date.length === 8) {
      return `${date.slice(0, 4)}년 ${date.slice(4, 6)}월 ${date.slice(6, 8)}일`;
    }
    return date;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-12 text-ghibli-text">
      {/* Sidebar: Date List */}
      <div className="lg:col-span-1">
        <div className="sticky top-32">
            <h2 className="text-xl font-black mb-8 flex items-center gap-3 text-ghibli-accent uppercase tracking-wider">
                <BookOpen size={24} />
                Chronicle Index
            </h2>
            <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-4 scrollbar-thin">
            {initialDates.map((date) => (
                <button
                key={date}
                onClick={() => handleDateSelect(date)}
                className={`w-full text-left px-5 py-4 rounded-2xl transition-all flex items-center justify-between group ghibli-card ${
                    selectedDate === date 
                    ? "bg-ghibli-accent/10 border-ghibli-accent shadow-md translate-x-1" 
                    : "bg-white/50 border-slate-200 text-slate-500 hover:text-ghibli-text hover:bg-white"
                }`}
                >
                <span className="font-mono font-black">{date}</span>
                <ChevronRight size={18} className={`transition-transform duration-500 ${selectedDate === date ? "translate-x-1 text-ghibli-accent" : "opacity-30 group-hover:opacity-100"}`} />
                </button>
            ))}
            </div>
        </div>
      </div>

      {/* Main: Timeline Details */}
      <div className="lg:col-span-3">
        <header className="mb-12 flex items-end justify-between border-b-4 border-ghibli-accent/10 pb-10">
          <div>
            <h1 className="text-5xl font-black tracking-tight text-ghibli-text mb-4">
              {filter === "command" ? "The Will: CEO 명령" : formatHeaderDate(selectedDate || "")}
            </h1>
            <p className="text-lg text-slate-500 font-medium italic leading-relaxed max-w-xl">
              {filter === "command" 
                ? "시스템의 방향을 결정하는 대표님의 지엄한 지시 기록입니다." 
                : "가재 군단의 격돌과 합의, 지능의 박동을 따뜻한 서사로 기록한 연대기입니다."}
            </p>
          </div>
          {isLoading && (
            <div className="flex items-center gap-2 text-ghibli-accent text-xs font-black font-mono tracking-widest animate-pulse mb-2">
              <Sparkles size={16} />
              SYNCING SANCTUARY...
            </div>
          )}
        </header>

        <div className="relative border-l-4 border-ghibli-accent/10 ml-6 pl-12 space-y-12 py-4">
          <AnimatePresence mode="popLayout">
            {filteredTimeline.length > 0 ? (
              filteredTimeline.map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.5, delay: index * 0.05, ease: "easeOut" }}
                  className="relative group"
                >
                  {/* Timeline Dot */}
                  <div className="absolute -left-[64px] top-4 w-8 h-8 rounded-full bg-ghibli-bg border-4 border-ghibli-accent/20 flex items-center justify-center group-hover:border-ghibli-accent transition-colors duration-700 shadow-sm">
                    <div className={`w-2 h-2 rounded-full ${item.path.includes("/command/") ? "bg-ghibli-orange" : "bg-ghibli-green"} shadow-inner`} />
                  </div>
                  
                  <div className="ghibli-card p-10 hover:shadow-2xl transition-all duration-700 group-hover:-translate-y-1 bg-white/80 backdrop-blur-sm border-2">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-4 text-ghibli-accent text-sm font-mono font-black">
                            <Clock size={18} />
                            {item.time}
                        </div>
                        <div className={`text-[10px] font-black font-mono uppercase tracking-[0.2em] px-3 py-1.5 rounded-full border-2 ${
                            item.path.includes("/command/") 
                            ? "bg-ghibli-orange/10 border-ghibli-orange/20 text-ghibli-orange" 
                            : "bg-ghibli-green/10 border-ghibli-green/20 text-ghibli-green"
                        }`}>
                            {item.path.includes("/command/") ? "Will" : "Pulse"}
                        </div>
                    </div>
                    
                    <h3 className="text-2xl font-black text-ghibli-text mb-8 group-hover:text-ghibli-accent transition-colors tracking-tight leading-tight uppercase">
                        {item.title}
                    </h3>
                    
                    <div className="flex gap-4">
                      <Link 
                        href={`https://github.com/yuna-studio/yuna-openclaw/blob/main/${item.path}`}
                        target="_blank"
                        className="flex items-center gap-2 text-xs font-black text-slate-400 hover:text-ghibli-accent transition-all duration-300 bg-slate-50 px-5 py-3 rounded-2xl border-2 border-slate-100 hover:border-ghibli-accent/30 hover:bg-white shadow-sm"
                      >
                        <FileText size={16} />
                        SOURCE MARKDOWN
                      </Link>
                    </div>
                  </div>
                </motion.div>
              ))
            ) : !isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-slate-400 font-medium py-40 text-center italic text-xl handwritten"
              >
                No chronicles found for this date. <br />
                <span className="text-base not-italic mt-4 block text-slate-300">성역의 데이터가 아직 동기화되지 않았습니다.</span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export const TimelineView = ({ initialDates }: { initialDates: string[] }) => {
  return (
    <Suspense fallback={<div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Sparkles className="text-ghibli-accent animate-spin" size={48} />
        <span className="text-ghibli-accent font-black font-mono tracking-widest text-sm uppercase">Opening Sanctuary...</span>
    </div>}>
      <TimelineContent initialDates={initialDates} />
    </Suspense>
  );
};
