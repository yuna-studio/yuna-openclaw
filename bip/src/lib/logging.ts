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
  attempts: number;
  nextAttemptAt: number;
  queuedAt: string;
  lastError?: string;
};

type IngestResponse = {
  ok?: boolean;
  failedIndices?: number[];
  retryable?: boolean;
};

const INGEST_URL = process.env.NEXT_PUBLIC_EVENTS_INGEST_URL || "https://asia-northeast3-yuna-hq-admin.cloudfunctions.net/ingestEventsBatchHttp";
const MODEL_KEY = process.env.NEXT_PUBLIC_LOG_MODEL_KEY || "home-funnel";
const MODEL_VERSION = Number(process.env.NEXT_PUBLIC_LOG_MODEL_VERSION || "1");
const PROJECT_ID = process.env.NEXT_PUBLIC_LOG_PROJECT_ID || "vibe-coding-showcase";

const STORAGE_QUEUE_KEY = "bip_log_queue_v2";
const STORAGE_DEAD_KEY = "bip_log_dead_v1";
const STORAGE_SEQ_KEY = "bip_log_seq_v1";
const STORAGE_SESSION_KEY = "bip_session_id";

const BATCH_SIZE = 10;
const FLUSH_THRESHOLD = 3;
const MAX_QUEUE = 500;
const MAX_DEAD_LETTER = 100;
const MAX_ATTEMPTS = 6;
const BASE_DELAY_MS = 1200;
const MAX_DELAY_MS = 30000;

let queue: QueueItem[] = [];
let timer: ReturnType<typeof setTimeout> | null = null;
let inFlight = false;
let bootstrapped = false;

function jitter(ms: number) {
  const delta = Math.floor(ms * 0.2);
  return ms + Math.floor(Math.random() * (delta + 1));
}

function getBackoffDelay(attempt: number) {
  const raw = Math.min(MAX_DELAY_MS, BASE_DELAY_MS * Math.pow(2, Math.max(0, attempt)));
  return jitter(raw);
}

function nowMs() {
  return Date.now();
}

function toQueueItem(item: any): QueueItem | null {
  if (!item || typeof item !== "object") return null;
  if (!item.eventName || !item.eventAt) return null;

  return {
    eventName: String(item.eventName),
    data: typeof item.data === "object" && item.data ? item.data : {},
    pageOrScreen: String(item.pageOrScreen || ""),
    referrerOrSource: String(item.referrerOrSource || ""),
    eventAt: String(item.eventAt),
    sessionId: String(item.sessionId || ""),
    userPseudoId: String(item.userPseudoId || "anon"),
    platform: "web",
    appVersion: String(item.appVersion || "bip-web-1"),
    sequenceNo: Number(item.sequenceNo || 0),
    utm: typeof item.utm === "object" && item.utm ? item.utm : {},
    attempts: Math.max(0, Number(item.attempts || 0)),
    nextAttemptAt: Number(item.nextAttemptAt || 0) || 0,
    queuedAt: String(item.queuedAt || item.eventAt),
    lastError: item.lastError ? String(item.lastError) : undefined,
  };
}

function loadQueue() {
  if (typeof window === "undefined" || bootstrapped) return;
  bootstrapped = true;
  try {
    const raw = window.localStorage.getItem(STORAGE_QUEUE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    const restored = Array.isArray(parsed)
      ? parsed.map((v) => toQueueItem(v)).filter(Boolean) as QueueItem[]
      : [];
    queue = restored.slice(0, MAX_QUEUE);
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

function appendDeadLetters(items: QueueItem[]) {
  if (typeof window === "undefined" || items.length === 0) return;
  try {
    const raw = window.localStorage.getItem(STORAGE_DEAD_KEY);
    const prev = raw ? JSON.parse(raw) : [];
    const merged = [...(Array.isArray(prev) ? prev : []), ...items]
      .slice(-MAX_DEAD_LETTER)
      .map((v) => ({ ...v, deadAt: new Date().toISOString() }));
    window.localStorage.setItem(STORAGE_DEAD_KEY, JSON.stringify(merged));
  } catch {
    // ignore
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

function toApiEvent(item: QueueItem) {
  return {
    eventName: item.eventName,
    data: item.data,
    pageOrScreen: item.pageOrScreen,
    referrerOrSource: item.referrerOrSource,
    eventAt: item.eventAt,
    sessionId: item.sessionId,
    userPseudoId: item.userPseudoId,
    platform: item.platform,
    appVersion: item.appVersion,
    sequenceNo: item.sequenceNo,
    utm: item.utm,
  };
}

async function sendBatch(batch: QueueItem[]) {
  const res = await fetch(INGEST_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      projectId: PROJECT_ID,
      modelKey: MODEL_KEY,
      modelVersion: MODEL_VERSION,
      events: batch.map(toApiEvent),
    }),
    keepalive: true,
  });

  if (!res.ok) {
    // 4xx: 클라이언트 오류는 재시도해도 의미 없음 — non-retryable 처리
    if (res.status >= 400 && res.status < 500) {
      return { ok: false, failedIndices: batch.map((_, i) => i), retryable: false } as IngestResponse;
    }
    throw new Error(`http-${res.status}`);
  }
  return (await res.json().catch(() => ({}))) as IngestResponse;
}

function pickDueBatch() {
  const now = nowMs();
  const dueIndices = queue
    .map((item, idx) => ({ idx, due: (item.nextAttemptAt || 0) <= now, nextAttemptAt: item.nextAttemptAt || 0 }))
    .filter((v) => v.due)
    .slice(0, BATCH_SIZE)
    .map((v) => v.idx);

  const batch = dueIndices.map((idx) => queue[idx]);
  return { dueIndices, batch };
}

function markFailed(item: QueueItem, reason: string) {
  item.attempts += 1;
  item.lastError = reason;
  if (item.attempts >= MAX_ATTEMPTS) {
    return { drop: true, item };
  }

  item.nextAttemptAt = nowMs() + getBackoffDelay(item.attempts);
  return { drop: false, item };
}

function finalizeBatch(dueIndices: number[], result: IngestResponse | null, networkError?: string) {
  if (dueIndices.length === 0) return;

  const failedSet = new Set<number>();
  const retryable = result?.retryable ?? true;

  if (networkError) {
    dueIndices.forEach((_, i) => failedSet.add(i));
  } else if (Array.isArray(result?.failedIndices)) {
    result!.failedIndices!.forEach((i) => {
      if (Number.isInteger(i) && i >= 0 && i < dueIndices.length) failedSet.add(i);
    });
  }

  const removeQueueIndices = new Set<number>();
  const deadLetters: QueueItem[] = [];

  dueIndices.forEach((qIdx, i) => {
    const item = queue[qIdx];
    if (!item) return;

    if (!failedSet.has(i)) {
      // success
      removeQueueIndices.add(qIdx);
      return;
    }

    if (!retryable && !networkError) {
      removeQueueIndices.add(qIdx);
      deadLetters.push({ ...item, lastError: item.lastError || "non-retryable" });
      return;
    }

    const marked = markFailed(item, networkError || "failed-index");
    if (marked.drop) {
      removeQueueIndices.add(qIdx);
      deadLetters.push({ ...item });
    }
  });

  if (removeQueueIndices.size > 0) {
    queue = queue.filter((_, idx) => !removeQueueIndices.has(idx));
  }

  if (deadLetters.length > 0) {
    appendDeadLetters(deadLetters);
  }

  persistQueue();
}

async function flush() {
  loadQueue();
  if (inFlight || queue.length === 0) return;

  const { dueIndices, batch } = pickDueBatch();
  if (batch.length === 0) {
    schedule();
    return;
  }

  inFlight = true;

  try {
    const result = await sendBatch(batch);
    finalizeBatch(dueIndices, result);
  } catch (err: any) {
    finalizeBatch(dueIndices, null, err?.message || "network-error");
  } finally {
    inFlight = false;
    schedule();
  }
}

function schedule(delayMs?: number) {
  if (timer) return;

  const now = nowMs();
  const nextAttempt = queue
    .map((q) => q.nextAttemptAt || 0)
    .filter(Boolean)
    .sort((a, b) => a - b)[0];

  const computedDelay = typeof delayMs === "number"
    ? delayMs
    : nextAttempt
      ? Math.max(200, nextAttempt - now)
      : BASE_DELAY_MS;

  timer = setTimeout(async () => {
    timer = null;
    await flush();
  }, computedDelay);
}

function enqueue(item: QueueItem) {
  loadQueue();
  queue.push(item);
  if (queue.length > MAX_QUEUE) {
    const dropped = queue.slice(0, queue.length - MAX_QUEUE);
    appendDeadLetters(dropped.map((v) => ({ ...v, lastError: v.lastError || "queue-overflow" })));
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
    queuedAt: new Date().toISOString(),
    sessionId: getSessionId(),
    userPseudoId: "anon",
    platform: "web",
    appVersion: "bip-web-1",
    sequenceNo: getNextSeq(),
    utm: getUtm(),
    attempts: 0,
    nextAttemptAt: 0,
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
    const now = nowMs();
    const batch = queue.filter((q) => (q.nextAttemptAt || 0) <= now).slice(0, BATCH_SIZE);
    if (batch.length === 0) return;

    const payload = JSON.stringify({
      projectId: PROJECT_ID,
      modelKey: MODEL_KEY,
      modelVersion: MODEL_VERSION,
      events: batch.map(toApiEvent),
    });
    navigator.sendBeacon?.(INGEST_URL, payload);
  });
}
