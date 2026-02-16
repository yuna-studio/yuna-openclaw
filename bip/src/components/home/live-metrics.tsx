"use client";

import { useEffect, useState } from "react";
import { collection, onSnapshot, query, orderBy, limit } from "firebase/firestore";
import { db } from "@/lib/firebase";

export function LiveMetrics() {
  const [totalChats, setTotalChats] = useState(0);
  const [dDay, setDDay] = useState(1);

  useEffect(() => {
    // D+1 = 2026-02-16 (시작일), 매일 +1
    const startDate = new Date("2026-02-16T00:00:00+09:00");
    const now = new Date();
    const diff = Math.floor((now.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    setDDay(Math.max(1, diff));
  }, []);

  // 전체 대화 수 — 실시간 구독으로 카운팅
  useEffect(() => {
    if (!db) return;

    // 최신 1개를 구독 → snapshot 변경 시 count 재조회
    const q = query(
      collection(db, "chat_logs"),
      orderBy("timestamp", "desc"),
      limit(1)
    );

    const unsubscribe = onSnapshot(q, async () => {
      try {
        const { getCountFromServer } = await import("firebase/firestore");
        const coll = collection(db, "chat_logs");
        const snapshot = await getCountFromServer(coll);
        setTotalChats(snapshot.data().count);
      } catch {
        // silent
      }
    });

    // 탭 복귀 시 재조회
    const handleVisibility = () => {
      if (document.visibilityState === "visible") {
        import("firebase/firestore").then(({ getCountFromServer }) => {
          const coll = collection(db, "chat_logs");
          getCountFromServer(coll).then((snap) => {
            setTotalChats(snap.data().count);
          }).catch(() => {});
        });
      }
    };
    document.addEventListener("visibilitychange", handleVisibility);

    return () => {
      unsubscribe();
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, []);

  return (
    <div className="grid grid-cols-3 gap-2 w-full max-w-2xl mx-auto px-4 py-8">
      <div className="bg-primary/10 p-4 rounded-lg text-center border border-primary/20">
        <span className="block text-2xl font-bold text-primary font-mono">
          D+{dDay}
        </span>
        <span className="text-[10px] text-text-muted">개발 일수</span>
      </div>
      <div className="bg-secondary/10 p-4 rounded-lg text-center border border-secondary/20">
        <span className="block text-2xl font-bold text-secondary font-mono">
          {totalChats.toLocaleString()}
        </span>
        <span className="text-[10px] text-text-muted">전체 대화</span>
      </div>
      <div className="bg-amber-500/10 p-4 rounded-lg text-center border border-amber-500/20">
        <span className="block text-2xl font-bold text-amber-600 font-mono">
            3
        </span>
        <span className="text-[10px] text-text-muted">AI 에이전트</span>
      </div>
    </div>
  );
}
