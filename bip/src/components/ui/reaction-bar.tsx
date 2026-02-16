"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Heart } from "lucide-react";
import { db } from "@/lib/firebase";
import {
  collection,
  addDoc,
  onSnapshot,
  query,
  orderBy,
  limit,
  where,
  doc,
  getDoc,
  setDoc,
  increment,
} from "firebase/firestore";

function formatCount(n: number): string {
  if (n < 100) return String(n);
  if (n < 1_000) return "100+";
  if (n < 10_000) return `${Math.floor(n / 1_000)}천+`;
  if (n < 100_000) return `${Math.floor(n / 10_000)}만+`;
  if (n < 1_000_000) return `${Math.floor(n / 10_000)}만+`;
  if (n < 10_000_000) return `${Math.floor(n / 1_000_000)}백만+`;
  if (n < 100_000_000) return `${Math.floor(n / 10_000_000)}천만+`;
  if (n < 1_000_000_000) return `${Math.floor(n / 100_000_000)}억+`;
  return `${Math.floor(n / 1_000_000_000)}0억+`;
}

const SESSION_ID = typeof window !== "undefined"
  ? sessionStorage.getItem("reaction-session") || (() => {
      const id = Math.random().toString(36).slice(2, 10);
      sessionStorage.setItem("reaction-session", id);
      return id;
    })()
  : "server";

interface FloatingHeart {
  id: number;
  x: number;        // 시작 x (vw)
  drift: number;     // 좌우 흔들림
  duration: number;  // 올라가는 시간
  size: number;      // 크기
  delay: number;
}

export function ReactionBar() {
  const [hearts, setHearts] = useState<FloatingHeart[]>([]);
  const [count, setCount] = useState(0);
  const [showCheer, setShowCheer] = useState(false);
  const [heartbeat, setHeartbeat] = useState(false);
  const lastProcessed = useRef<string>("");
  const cheerTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const beatTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // 누적 카운트 실시간 구독
  useEffect(() => {
    const counterRef = doc(db, "counters", "reactions");
    const unsub = onSnapshot(counterRef, (snap) => {
      if (snap.exists()) {
        setCount(snap.data().heart || 0);
      }
    });
    return () => unsub();
  }, []);

  // 실시간 리액션 파티클 구독 (최근 1분)
  useEffect(() => {
    const oneMinuteAgo = new Date(Date.now() - 60 * 1000).toISOString();
    const q = query(
      collection(db, "reactions"),
      where("timestamp", ">", oneMinuteAgo),
      orderBy("timestamp", "desc"),
      limit(20)
    );

    let isInitial = true;
    const unsub = onSnapshot(q, (snapshot) => {
      // 첫 스냅샷은 기존 데이터 → 파티클 무시
      if (isInitial) {
        isInitial = false;
        return;
      }
      snapshot.docChanges().forEach((change) => {
        if (change.type === "added") {
          const data = change.doc.data();
          if (data.sessionId === SESSION_ID) return;
          if (change.doc.id === lastProcessed.current) return;
          lastProcessed.current = change.doc.id;
          spawnHearts();
          // 응원 토스트
          setShowCheer(true);
          if (cheerTimer.current) clearTimeout(cheerTimer.current);
          cheerTimer.current = setTimeout(() => setShowCheer(false), 3000);
          // 두근두근
          setHeartbeat(true);
          if (beatTimer.current) clearTimeout(beatTimer.current);
          beatTimer.current = setTimeout(() => setHeartbeat(false), 3000);
        }
      });
    });

    return () => unsub();
  }, []);

  const spawnHearts = () => {
    const id = Date.now() + Math.random();
    const newHearts: FloatingHeart[] = Array.from({ length: 3 + Math.floor(Math.random() * 3) }).map((_, i) => ({
      id: id + i,
      x: 5 + Math.random() * 15,           // 좌측 영역 (5~20vw)
      drift: (Math.random() - 0.5) * 40,    // 좌우 흔들림
      duration: 2.5 + Math.random() * 1.5,  // 2.5~4초
      size: 16 + Math.random() * 16,        // 16~32px
      delay: Math.random() * 0.3,           // 약간의 딜레이
    }));

    setHearts((prev) => [...prev, ...newHearts]);
    setTimeout(() => {
      setHearts((prev) => prev.filter((h) => h.id < id));
    }, 5000);
  };

  const triggerReaction = async () => {
    spawnHearts();
    try {
      // 개별 리액션 기록 (파티클 공유용)
      await addDoc(collection(db, "reactions"), {
        type: "heart",
        timestamp: new Date().toISOString(),
        sessionId: SESSION_ID,
      });
      // 누적 카운터 +1
      const counterRef = doc(db, "counters", "reactions");
      await setDoc(counterRef, { heart: increment(1) }, { merge: true });
    } catch (e) {
      console.error("Reaction save failed:", e);
    }
  };

  return (
    <>
      {/* 배경 하트 올라가는 레이어 */}
      <div className="fixed inset-0 pointer-events-none z-40 overflow-hidden">
        <AnimatePresence>
          {hearts.map((h) => (
            <motion.div
              key={h.id}
              initial={{
                opacity: 0.8,
                x: `${h.x}vw`,
                y: "100vh",
                scale: 0.5,
              }}
              animate={{
                opacity: [0.8, 0.9, 0.6, 0],
                x: `${h.x + h.drift / 10}vw`,
                y: "-10vh",
                scale: [0.5, 1.2, 1, 0.8],
              }}
              exit={{ opacity: 0 }}
              transition={{
                duration: h.duration,
                delay: h.delay,
                ease: "easeOut",
              }}
              className="absolute text-reaction-heart"
              style={{ fontSize: h.size }}
            >
              ❤️
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* 좌측 하단 하트 버튼 */}
      <div className="fixed bottom-6 left-6 z-50 flex items-center gap-2">
        <div className="relative">
          <button
            onClick={triggerReaction}
            className="p-3 rounded-full glass shadow-xl hover:shadow-2xl active:scale-90 transition-all group"
            aria-label="응원하기"
          >
            <Heart
              className={`transition-colors ${heartbeat ? "text-reaction-heart fill-reaction-heart animate-heartbeat" : "text-reaction-heart fill-reaction-heart/20 group-hover:fill-reaction-heart"}`}
              size={28}
            />
          </button>
          {/* 카운트 뱃지 — 우측 상단 */}
          {count > 0 && (
            <div className="absolute -top-1.5 -right-1.5 bg-reaction-heart rounded-full min-w-[22px] h-[22px] flex items-center justify-center px-1 shadow-sm">
              <span className="text-white font-bold text-[10px] font-mono leading-none">{formatCount(count)}</span>
            </div>
          )}
        </div>
        {/* 응원 토스트 — 하트 버튼 바로 오른쪽 */}
        <AnimatePresence>
          {showCheer && (
            <motion.div
              initial={{ opacity: 0, x: -8, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: -4, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="bg-white/95 backdrop-blur-sm rounded-full px-3 py-1.5 shadow-md border border-gray-100 whitespace-nowrap"
            >
              <span className="text-xs text-charcoal/70">누군가 응원하고 있어요 ❤️</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  );
}
