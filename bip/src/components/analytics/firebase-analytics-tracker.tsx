"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { getAnalytics, isSupported, logEvent, setAnalyticsCollectionEnabled } from "firebase/analytics";
import { app } from "@/lib/firebase";

export function FirebaseAnalyticsTracker() {
  const pathname = usePathname();

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      if (!app) return;
      if (typeof window === "undefined") return;

      const supported = await isSupported().catch(() => false);
      if (!supported || cancelled) return;

      const analytics = getAnalytics(app);
      setAnalyticsCollectionEnabled(analytics, true);

      const qs = window.location.search || "";
      const pagePath = `${pathname}${qs}`;

      logEvent(analytics, "page_view", {
        page_path: pagePath,
        page_location: window.location.href,
        page_title: document.title,
      });
    };

    void run();
    return () => {
      cancelled = true;
    };
  }, [pathname]);

  return null;
}
