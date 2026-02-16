"use client";

import CountUp from "react-countup";
import { useEffect, useState } from "react";
import { doc, getDoc } from "firebase/firestore";
import { db } from "@/lib/firebase";

export function LiveMetrics() {
  const [totalChats, setTotalChats] = useState(1240);
  const [dDay, setDDay] = useState(15);

  useEffect(() => {
    const startDate = new Date("2024-02-01");
    const diff = Math.floor((Date.now() - startDate.getTime()) / (1000 * 60 * 60 * 24));
    setDDay(diff);

    if (db) {
        const fetchMeta = async () => {
            try {
                const docRef = doc(db, "metadata", "stats");
                const snap = await getDoc(docRef);
                if (snap.exists()) {
                    setTotalChats(snap.data().total_chats || 1240);
                }
            } catch (e) {
                // Silently fail
            }
        };
        fetchMeta();
    }
  }, []);

  return (
    <div className="grid grid-cols-3 gap-2 w-full max-w-2xl mx-auto px-4 py-8">
      <div className="bg-primary/5 p-4 rounded-lg text-center border border-primary/10">
        <span className="block text-2xl font-bold text-primary font-mono">
          <CountUp end={dDay} duration={2} />
        </span>
        <span className="text-[10px] text-text-muted uppercase">Day+</span>
      </div>
      <div className="bg-secondary/5 p-4 rounded-lg text-center border border-secondary/10">
        <span className="block text-2xl font-bold text-secondary font-mono">
            <CountUp end={totalChats} duration={2.5} separator="," />
        </span>
        <span className="text-[10px] text-text-muted uppercase">Chats</span>
      </div>
      <div className="bg-accent-highlight/5 p-4 rounded-lg text-center border border-accent-highlight/10">
        <span className="block text-2xl font-bold text-accent-highlight font-mono">
            3
        </span>
        <span className="text-[10px] text-text-muted uppercase">Agents</span>
      </div>
    </div>
  );
}
