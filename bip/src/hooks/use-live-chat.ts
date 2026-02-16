import { useEffect, useState, useRef, useCallback } from "react";
import {
  collection,
  query,
  orderBy,
  limit,
  onSnapshot,
  Timestamp,
} from "firebase/firestore";
import { db } from "@/lib/firebase";
import { ChatLog } from "@/types";

export function useLiveChat(msgLimit = 50) {
  const [messages, setMessages] = useState<ChatLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!db) {
        setError(new Error("Firestore not initialized"));
        setLoading(false);
        return;
    }

    try {
        const q = query(
          collection(db, "chat_logs"),
          orderBy("timestamp", "asc"),
          limit(msgLimit)
        );
    
        const unsubscribe = onSnapshot(q, (snapshot) => {
          const logs = snapshot.docs.map((doc) => {
            const data = doc.data();
            
            let timestamp = new Date().toISOString();
            
            try {
                if (data.timestamp instanceof Timestamp) {
                  timestamp = data.timestamp.toDate().toISOString();
                } else if (typeof data.timestamp === 'string') {
                  timestamp = data.timestamp;
                } else if (typeof data.timestamp === 'number') {
                  timestamp = new Date(data.timestamp).toISOString();
                }
            } catch (e) {
                // Date parsing error ignored
            }
    
            return {
              id: doc.id,
              role: data.role || "assistant",
              content: data.content || "",
              timestamp,
              model: data.model,
              agent: data.agent
            } as ChatLog;
          });
    
          setMessages(logs);
          setLoading(false);
        }, (err) => {
          setError(err);
          setLoading(false);
        });
    
        return () => unsubscribe();
    } catch (err) {
        setError(err as Error);
        setLoading(false);
    }
  }, [msgLimit]);

  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, []);

  return { messages, loading, error, scrollRef, scrollToBottom };
}
