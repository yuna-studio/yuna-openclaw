"use client";

import { useEffect, useState } from "react";
import { collection, onSnapshot, query, orderBy, limit } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { motion } from "framer-motion";

export function LiveMetrics() {
  const [totalChats, setTotalChats] = useState(0);
  const [dDay, setDDay] = useState(1);

  useEffect(() => {
    const startDate = new Date("2026-02-16T00:00:00+09:00");
    const now = new Date();
    const diff = Math.floor((now.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    setDDay(Math.max(1, diff));
  }, []);

  useEffect(() => {
    if (!db) return;

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
          className="text-lg font-bold text-text-muted/50 leading-relaxed"
        >
          멈추지 않고 만들어가는 중.
        </motion.p>
      </div>
    </div>
  );
}
