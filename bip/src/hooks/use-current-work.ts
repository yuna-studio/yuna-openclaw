"use client";

import { useEffect, useState } from "react";
import { doc, onSnapshot } from "firebase/firestore";
import { db } from "@/lib/firebase";

export interface CurrentWork {
  projectTitle: string;
  taskTitle: string;
  taskType: "기획" | "설계" | "개발" | "배포";
  updatedAt: string;
  isActive: boolean;
}

export function useCurrentWork() {
  const [data, setData] = useState<CurrentWork | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!db) {
      setLoading(false);
      return;
    }

    const ref = doc(db, "config", "current_work");
    const unsub = onSnapshot(ref, (snap) => {
      if (snap.exists()) {
        const d = snap.data();
        setData({
          projectTitle: d.projectTitle || "",
          taskTitle: d.taskTitle || "",
          taskType: d.taskType || "개발",
          updatedAt:
            d.updatedAt?.toDate?.()?.toISOString() ??
            new Date().toISOString(),
          isActive: d.isActive !== false,
        });
      } else {
        setData(null);
      }
      setLoading(false);
    });

    return () => unsub();
  }, []);

  return { data, loading };
}
