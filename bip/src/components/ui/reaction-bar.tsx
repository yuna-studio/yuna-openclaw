"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Heart } from "lucide-react";
import { db, rtdb } from "@/lib/firebase";
import {
  collection,
  addDoc,
  onSnapshot,
  query,
  orderBy,
  limit,
  where,
  doc,
  setDoc,
  increment,
} from "firebase/firestore";
import { ref, set, onValue, onDisconnect, serverTimestamp as rtdbTimestamp } from "firebase/database";

interface FloatingHeart {
  id: number;
  x: number;
  drift: number;
  duration: number;
  size: number;
  delay: number;
}

export function ReactionBar() {
  const [hearts, setHearts] = useState<FloatingHeart[]>([]);
  const [showCheer, setShowCheer] = useState(false);
  const lastProcessed = useRef<string>("");
  const cheerTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const sessionId = useRef<string>("");
  const lastTrigger = useRef<number>(0);
  const sessionCount = useRef<number>(0);
  const [viewerCount, setViewerCount] = useState(0);

  const MAX_PER_SESSION = 50;
  const THROTTLE_MS = 500;

  // 클라이언트에서만 session ID 생성 (하이드레이션 안전)
  useEffect(() => {
    const stored = sessionStorage.getItem("reaction-session");
    if (stored) {
      sessionId.current = stored;
    } else {
      const id = Math.random().toString(36).slice(2, 10);
      sessionStorage.setItem("reaction-session", id);
      sessionId.current = id;
    }
  }, []);

  // Presence: 실시간 접속자 수 (홈/라이브 공통)
  useEffect(() => {
    if (!rtdb) return;

    const viewerId = Math.random().toString(36).slice(2, 10);
    const viewerRef = ref(rtdb, `viewers/${viewerId}`);
    const countRef = ref(rtdb, "viewers");

    set(viewerRef, { joinedAt: rtdbTimestamp() });
    onDisconnect(viewerRef).remove();

    const unsub = onValue(countRef, (snap) => {
      const val = snap.val();
      setViewerCount(val ? Object.keys(val).length : 0);
    });

    const cleanup = () => {
      set(viewerRef, null);
    };
    window.addEventListener("beforeunload", cleanup);

    return () => {
      cleanup();
      unsub();
      window.removeEventListener("beforeunload", cleanup);
    };
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
      if (isInitial) {
        isInitial = false;
        return;
      }
      snapshot.docChanges().forEach((change) => {
        if (change.type === "added") {
          const data = change.doc.data();
          if (data.sessionId === sessionId.current) return;
          if (change.doc.id === lastProcessed.current) return;
          lastProcessed.current = change.doc.id;
          spawnHearts();
          setShowCheer(true);
          if (cheerTimer.current) clearTimeout(cheerTimer.current);
          cheerTimer.current = setTimeout(() => setShowCheer(false), 3000);
        }
      });
    });

    return () => unsub();
  }, []);

  const spawnHearts = useCallback(() => {
    const id = Date.now() + Math.random();
    const newHearts: FloatingHeart[] = Array.from({ length: 3 + Math.floor(Math.random() * 3) }).map((_, i) => ({
      id: id + i,
      x: 5 + Math.random() * 15,
      drift: (Math.random() - 0.5) * 40,
      duration: 2.5 + Math.random() * 1.5,
      size: 16 + Math.random() * 16,
      delay: Math.random() * 0.3,
    }));

    setHearts((prev) => [...prev, ...newHearts]);
    setTimeout(() => {
      setHearts((prev) => prev.filter((h) => h.id < id));
    }, 5000);
  }, []);

  const triggerReaction = useCallback(async () => {
    const now = Date.now();
    // 쓰로틀: 0.5초에 1번만
    if (now - lastTrigger.current < THROTTLE_MS) {
      spawnHearts();
      return;
    }
    // 세션당 50회 제한
    if (sessionCount.current >= MAX_PER_SESSION) {
      spawnHearts();
      return;
    }
    lastTrigger.current = now;
    sessionCount.current += 1;

    spawnHearts();
    try {
      await addDoc(collection(db, "reactions"), {
        type: "heart",
        timestamp: new Date().toISOString(),
        sessionId: sessionId.current,
      });
      const counterRef = doc(db, "counters", "reactions");
      await setDoc(counterRef, { heart: increment(1) }, { merge: true });
    } catch (e) {
      console.error("Reaction save failed:", e);
    }
  }, [spawnHearts]);

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
          {viewerCount >= 3 && (
            <div className="absolute -top-7 left-0 text-[10px] text-text-muted bg-white/90 border border-gray-100 rounded-full px-2 py-0.5 shadow-sm whitespace-nowrap">
              {viewerCount >= 10 ? `시청자 ${viewerCount}명` : "몇 명이 보는 중"}
            </div>
          )}
          <button
            onClick={triggerReaction}
            className="flex items-center gap-1.5 px-3 py-2.5 rounded-full glass shadow-xl hover:shadow-2xl active:scale-90 transition-all group"
            aria-label="응원하기"
          >
            <Heart
              className="transition-colors text-reaction-heart fill-reaction-heart animate-heartbeat"
              size={22}
            />
            <span className="text-xs font-bold text-text-muted">응원하기</span>
          </button>
        </div>
        {/* 응원 토스트 */}
        <AnimatePresence>
          {showCheer && (
            <motion.div
              initial={{ opacity: 0, x: -8, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: -4, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="bg-white/95 backdrop-blur-sm rounded-full px-3 py-1.5 shadow-md border border-gray-100 whitespace-nowrap"
            >
              <span className="text-xs text-text-secondary">누군가 응원하고 있어요 ❤️</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  );
}
