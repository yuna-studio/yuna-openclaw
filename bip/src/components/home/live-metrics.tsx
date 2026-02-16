"use client";

import { useEffect, useState, useCallback } from "react";
import {
  collection,
  onSnapshot,
  query,
  orderBy,
  limit,
  doc,
} from "firebase/firestore";
import { db } from "@/lib/firebase";
import { motion } from "framer-motion";

export function LiveMetrics() {
  const [totalChats, setTotalChats] = useState(0);
  const [cheerCount, setCheerCount] = useState(0);
  const [dDay, setDDay] = useState(1);

  useEffect(() => {
    const startDate = new Date("2026-02-16T00:00:00+09:00");
    const now = new Date();
    const diff = Math.floor((now.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    setDDay(Math.max(1, diff));
  }, []);

  const fetchCount = useCallback(async () => {
    try {
      const { getCountFromServer } = await import("firebase/firestore");
      const coll = collection(db, "chat_logs");
      const snapshot = await getCountFromServer(coll);
      setTotalChats(snapshot.data().count);
    } catch {}
  }, []);

  // 전체 대화 수 — 새 메시지 감지 시 재집계
  useEffect(() => {
    if (!db) return;

    const q = query(collection(db, "chat_logs"), orderBy("timestamp", "desc"), limit(1));
    const unsubscribe = onSnapshot(q, () => {
      fetchCount();
    });

    const handleVisibility = () => {
      if (document.visibilityState === "visible") fetchCount();
    };
    document.addEventListener("visibilitychange", handleVisibility);

    return () => {
      unsubscribe();
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [fetchCount]);

  // 응원 수 실시간
  useEffect(() => {
    if (!db) return;
    const counterRef = doc(db, "counters", "reactions");
    const unsub = onSnapshot(counterRef, (snap) => {
      if (snap.exists()) {
        setCheerCount(snap.data().heart || 0);
      }
    });
    return () => unsub();
  }, []);

  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-16 border-t border-dashed border-border">
      <div className="text-center">
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-lg font-bold text-text-primary leading-relaxed"
        >
          <span className="text-primary font-mono">D+{dDay}</span>일째,{" "}
          <span className="text-primary font-mono">{totalChats.toLocaleString()}</span>번의 대화.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 }}
          className="text-lg font-bold text-text-muted/60 leading-relaxed"
        >
          멈추지 않고 만들어가는 중.
        </motion.p>
        {cheerCount > 0 && (
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-sm text-text-muted mt-3"
          >
            ❤️ 지금까지 <span className="font-bold text-reaction-heart">{cheerCount.toLocaleString()}</span>번의 응원을 받았어요
          </motion.p>
        )}
      </div>
    </div>
  );
}
