type LogEvent = {
  eventName: string;
  pageOrScreen?: string;
  referrerOrSource?: string;
  data?: Record<string, unknown>;
};

type QueueItem = LogEvent & {
  eventAt: string;
  sessionId: string;
  userPseudoId: string;
  platform: "web";
  appVersion: string;
  sequenceNo: number;
  utm: Record<string, string>;
};

const INGEST_URL = process.env.NEXT_PUBLIC_EVENTS_INGEST_URL || "https://asia-northeast3-yuna-hq-admin.cloudfunctions.net/ingestEventsBatchHttp";
const MODEL_KEY = process.env.NEXT_PUBLIC_LOG_MODEL_KEY || "home-funnel";
const MODEL_VERSION = Number(process.env.NEXT_PUBLIC_LOG_MODEL_VERSION || "1");
const PROJECT_ID = process.env.NEXT_PUBLIC_LOG_PROJECT_ID || "vibe-coding-showcase";

let queue: QueueItem[] = [];
let timer: any = null;
let seq = 0;

function getSessionId() {
  const key = "bip_session_id";
  const old = typeof window !== "undefined" ? window.sessionStorage.getItem(key) : "";
  if (old) return old;
  const v = `s_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  if (typeof window !== "undefined") window.sessionStorage.setItem(key, v);
  return v;
}

function getUtm() {
  if (typeof window === "undefined") return {};
  const u = new URL(window.location.href);
  const keys = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"];
  return Object.fromEntries(keys.map((k) => [k, u.searchParams.get(k) || ""]).filter(([, v]) => !!v));
}

async function flush() {
  if (queue.length === 0) return;
  const batch = queue.splice(0, 10);
  try {
    await fetch(INGEST_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        projectId: PROJECT_ID,
        modelKey: MODEL_KEY,
        modelVersion: MODEL_VERSION,
        events: batch,
      }),
      keepalive: true,
    });
  } catch {
    queue = [...batch, ...queue].slice(0, 200);
  }
}

function schedule() {
  if (timer) return;
  timer = setTimeout(async () => {
    timer = null;
    await flush();
    if (queue.length) schedule();
  }, 1200);
}

export function track(eventName: string, data: Record<string, unknown> = {}) {
  if (typeof window === "undefined") return;
  seq += 1;
  queue.push({
    eventName,
    data,
    pageOrScreen: window.location.pathname,
    referrerOrSource: document.referrer || "",
    eventAt: new Date().toISOString(),
    sessionId: getSessionId(),
    userPseudoId: "anon",
    platform: "web",
    appVersion: "bip-web-1",
    sequenceNo: seq,
    utm: getUtm(),
  });

  if (queue.length >= 3) {
    void flush();
    return;
  }
  schedule();
}

if (typeof window !== "undefined") {
  window.addEventListener("pagehide", () => {
    if (!queue.length) return;
    const payload = JSON.stringify({
      projectId: PROJECT_ID,
      modelKey: MODEL_KEY,
      modelVersion: MODEL_VERSION,
      events: queue.slice(0, 10),
    });
    navigator.sendBeacon?.(INGEST_URL, payload);
  });
}
