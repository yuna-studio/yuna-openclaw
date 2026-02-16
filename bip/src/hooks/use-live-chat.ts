import { useEffect, useState, useRef, useCallback } from "react";
import {
  collection,
  query,
  orderBy,
  limit,
  onSnapshot,
  getDocs,
  startAfter,
  Timestamp,
  QueryDocumentSnapshot,
  DocumentData,
} from "firebase/firestore";
import { db } from "@/lib/firebase";
import { ChatLog } from "@/types";

const PAGE_SIZE = 30;

function docToLog(doc: QueryDocumentSnapshot<DocumentData>): ChatLog {
  const data = doc.data();
  let timestamp = new Date().toISOString();

  try {
    if (data.timestamp instanceof Timestamp) {
      timestamp = data.timestamp.toDate().toISOString();
    } else if (typeof data.timestamp === "string") {
      timestamp = data.timestamp;
    } else if (typeof data.timestamp === "number") {
      timestamp = new Date(data.timestamp).toISOString();
    }
  } catch {
    // fallback
  }

  return {
    id: doc.id,
    role: data.role || "assistant",
    content: data.content || "",
    timestamp,
    model: data.model,
    agent: data.agent,
  } as ChatLog;
}

export function useLiveChat(initialLimit = PAGE_SIZE) {
  // messages는 시간순: [0]=오래된, [n]=최신 (렌더링용)
  const [messages, setMessages] = useState<ChatLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [newCount, setNewCount] = useState(0);
  const [error, setError] = useState<Error | null>(null);
  const oldestDocRef = useRef<QueryDocumentSnapshot<DocumentData> | null>(null);
  const initialLoadDone = useRef(false);
  // 재구독 트리거: 값이 바뀌면 useEffect가 다시 실행됨
  const [subKey, setSubKey] = useState(0);

  // 백그라운드→포그라운드 복귀 시 재구독
  useEffect(() => {
    const handleVisibility = () => {
      if (document.visibilityState === "visible") {
        // 구독 재시작 (subKey 변경 → onSnapshot useEffect 재실행)
        setSubKey((k) => k + 1);
      }
    };
    document.addEventListener("visibilitychange", handleVisibility);
    return () => document.removeEventListener("visibilitychange", handleVisibility);
  }, []);

  // 실시간 구독: 최신 N개
  useEffect(() => {
    if (!db) {
      setError(new Error("Firestore not initialized"));
      setLoading(false);
      return;
    }

    try {
      const q = query(
        collection(db, "chat_logs"),
        orderBy("timestamp", "desc"),
        limit(initialLimit)
      );

      const unsubscribe = onSnapshot(
        q,
        (snapshot) => {
          // desc로 받아서 reverse → 시간순
          const logsDesc = snapshot.docs.map(docToLog);
          const logs = [...logsDesc].reverse(); // 오래된→최신

          // 가장 오래된 doc 커서 (desc 기준 마지막 = 가장 오래된)
          if (snapshot.docs.length > 0) {
            oldestDocRef.current = snapshot.docs[snapshot.docs.length - 1];
          }

          if (!initialLoadDone.current) {
            initialLoadDone.current = true;
            setMessages(logs);
          } else {
            // 실시간 업데이트: 기존 과거 메시지 유지 + 최신 메시지 머지
            setMessages((prev) => {
              const existingIds = new Set(prev.map((m) => m.id));
              const newMsgs = logs.filter((l) => !existingIds.has(l.id));

              if (newMsgs.length > 0) {
                setNewCount((c) => c + newMsgs.length);
                // 기존 메시지 + 새 메시지를 시간순 정렬
                const merged = [...prev, ...newMsgs].sort(
                  (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
                );
                return merged;
              }

              // 기존 메시지 content 업데이트 (수정된 경우)
              const logsMap = new Map(logs.map((l) => [l.id, l]));
              let updated = false;
              const result = prev.map((m) => {
                const fresh = logsMap.get(m.id);
                if (fresh && fresh.content !== m.content) {
                  updated = true;
                  return fresh;
                }
                return m;
              });
              return updated ? result : prev;
            });
          }

          setLoading(false);
          if (snapshot.docs.length < initialLimit) {
            setHasMore(false);
          }
        },
        (err) => {
          console.error("Firestore Subscribe Error:", err);
          setError(err);
          setLoading(false);
        }
      );

      return () => unsubscribe();
    } catch (err) {
      console.error("Setup Error:", err);
      setError(err as Error);
      setLoading(false);
    }
  }, [initialLimit, subKey]);

  // 과거 메시지 로드 (위로 스크롤)
  const loadMore = useCallback(async () => {
    if (!db || !oldestDocRef.current || loadingMore || !hasMore) return;

    setLoadingMore(true);
    try {
      const q = query(
        collection(db, "chat_logs"),
        orderBy("timestamp", "desc"),
        startAfter(oldestDocRef.current),
        limit(PAGE_SIZE)
      );

      const snapshot = await getDocs(q);

      if (snapshot.docs.length === 0) {
        setHasMore(false);
        setLoadingMore(false);
        return;
      }

      if (snapshot.docs.length < PAGE_SIZE) {
        setHasMore(false);
      }

      oldestDocRef.current = snapshot.docs[snapshot.docs.length - 1];

      const olderLogs = snapshot.docs.map(docToLog).reverse(); // 시간순

      setMessages((prev) => {
        const existingIds = new Set(prev.map((m) => m.id));
        const newLogs = olderLogs.filter((l) => !existingIds.has(l.id));
        return [...newLogs, ...prev]; // 앞에 prepend (과거)
      });
    } catch (err) {
      console.error("Load more error:", err);
    }
    setLoadingMore(false);
  }, [loadingMore, hasMore]);

  const clearNewCount = useCallback(() => {
    setNewCount(0);
  }, []);

  return { messages, loading, loadingMore, hasMore, newCount, error, loadMore, clearNewCount };
}
