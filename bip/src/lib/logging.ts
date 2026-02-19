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

const STORAGE_QUEUE_KEY = "bip_log_queue_v1";
const STORAGE_SEQ_KEY = "bip_log_seq_v1";
const STORAGE_SESSION_KEY = "bip_session_id";

const BATCH_SIZE = 10;
const FLUSH_THRESHOLD = 3;
const MAX_QUEUE = 500;
const BASE_DELAY_MS = 1200;
const MAX_DELAY_MS = 30000;

let queue: QueueItem[] = [];
let timer: any = null;
let inFlight = false;
let retryAttempt = 0;
let bootstrapped = false;

function jitter(ms: number) {
  const delta = Math.floor(ms * 0.2);
  return ms + Math.floor(Math.random() * (delta + 1));
}

function getBackoffDelay() {
  const raw = Math.min(MAX_DELAY_MS, BASE_DELAY_MS * Math.pow(2, retryAttempt));
  return jitter(raw);
}

function loadQueue() {
  if (typeof window === "undefined" || bootstrapped) return;
  bootstrapped = true;
  try {
    const raw = window.localStorage.getItem(STORAGE_QUEUE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    queue = Array.isArray(parsed) ? parsed.slice(0, MAX_QUEUE) : [];
  } catch {
    queue = [];
  }
}

function persistQueue() {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_QUEUE_KEY, JSON.stringify(queue.slice(0, MAX_QUEUE)));
  } catch {
    // ignore quota errors
  }
}

function getSessionId() {
  if (typeof window === "undefined") return "server";
  const old = window.sessionStorage.getItem(STORAGE_SESSION_KEY);
  if (old) return old;
  const v = `s_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  window.sessionStorage.setItem(STORAGE_SESSION_KEY, v);
  return v;
}

function getNextSeq() {
  if (typeof window === "undefined") return 1;
  const prev = Number(window.sessionStorage.getItem(STORAGE_SEQ_KEY) || "0");
  const next = prev + 1;
  window.sessionStorage.setItem(STORAGE_SEQ_KEY, String(next));
  return next;
}

function getUtm() {
  if (typeof window === "undefined") return {};
  const u = new URL(window.location.href);
  const keys = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"];
  return Object.fromEntries(keys.map((k) => [k, u.searchParams.get(k) || ""]).filter(([, v]) => !!v));
}

async function sendBatch(batch: QueueItem[]) {
  const res = await fetch(INGEST_URL, {
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

  if (!res.ok) throw new Error(`http-${res.status}`);
  return res.json().catch(() => ({} as any));
}

async function flush() {
  loadQueue();
  if (inFlight || queue.length === 0) return;

  inFlight = true;
  const batch = queue.slice(0, BATCH_SIZE);

  try {
    await sendBatch(batch);

    // 성공한/실패한 이벤트 모두 서버 응답 기준으로 처리
    // failedIndices는 현재 retryable=false 정책이라 드롭
    queue = queue.slice(batch.length);
    persistQueue();

    retryAttempt = 0;
  } catch {
    retryAttempt += 1;
  } finally {
    inFlight = false;
    schedule();
  }
}

function schedule(delayMs?: number) {
  if (timer) return;
  const delay = typeof delayMs === "number" ? delayMs : (retryAttempt > 0 ? getBackoffDelay() : BASE_DELAY_MS);
  timer = setTimeout(async () => {
    timer = null;
    await flush();
  }, delay);
}

function enqueue(item: QueueItem) {
  loadQueue();
  queue.push(item);
  if (queue.length > MAX_QUEUE) {
    queue = queue.slice(queue.length - MAX_QUEUE);
  }
  persistQueue();
}

export function track(eventName: string, data: Record<string, unknown> = {}) {
  if (typeof window === "undefined") return;

  enqueue({
    eventName,
    data,
    pageOrScreen: window.location.pathname,
    referrerOrSource: document.referrer || "",
    eventAt: new Date().toISOString(),
    sessionId: getSessionId(),
    userPseudoId: "anon",
    platform: "web",
    appVersion: "bip-web-1",
    sequenceNo: getNextSeq(),
    utm: getUtm(),
  });

  if (queue.length >= FLUSH_THRESHOLD) {
    void flush();
    return;
  }

  schedule();
}

if (typeof window !== "undefined") {
  loadQueue();
  if (queue.length > 0) schedule(300);

  window.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") {
      void flush();
    }
  });

  window.addEventListener("pagehide", () => {
    if (!queue.length) return;
    const payload = JSON.stringify({
      projectId: PROJECT_ID,
      modelKey: MODEL_KEY,
      modelVersion: MODEL_VERSION,
      events: queue.slice(0, BATCH_SIZE),
    });
    navigator.sendBeacon?.(INGEST_URL, payload);
  });
}
