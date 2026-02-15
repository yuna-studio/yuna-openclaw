#!/usr/bin/env python3
"""
OpenClaw Session Log Watcher
- 1분 주기로 세션 JSONL 파일 폴링
- <think> 블록, 시스템 로그(session, model_change, thinking_level_change, custom) 필터링
- user/assistant 메시지만 Firestore에 업로드
"""

import os
import sys
import json
import glob
import time
import re
import hashlib
import atexit
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore

# ── Config ──────────────────────────────────────────────
AGENTS_DIR = os.path.expanduser("~/.openclaw/agents")
POLL_INTERVAL = 1  # seconds
FIRESTORE_COLLECTION = "chat_logs"
PID_FILE = os.path.expanduser("~/.openclaw/session_log_watcher.pid")
OFFSET_FILE = os.path.expanduser("~/.openclaw/session_log_watcher.offsets.json")

# 필터링할 시스템 타입
SKIP_TYPES = {"session", "model_change", "thinking_level_change", "custom"}

# 각 파일별 마지막으로 읽은 바이트 위치 추적
file_offsets: dict[str, int] = {}


# ── Offset Persistence ─────────────────────────────────
def load_offsets():
    """Load saved file offsets from disk."""
    global file_offsets
    try:
        with open(OFFSET_FILE, "r") as f:
            file_offsets = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        file_offsets = {}


def save_offsets():
    """Save file offsets to disk."""
    with open(OFFSET_FILE, "w") as f:
        json.dump(file_offsets, f)


def init_offsets_to_eof():
    """First run: set all offsets to end-of-file so we only watch new content."""
    pattern = os.path.join(AGENTS_DIR, "*/sessions/*.jsonl")
    for path in glob.glob(pattern):
        if path not in file_offsets:
            file_offsets[path] = os.path.getsize(path)
    save_offsets()


# ── PID Lock ────────────────────────────────────────────
def check_pid_lock():
    """Prevent duplicate execution via PID file."""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                old_pid = int(f.read().strip())
            # Check if process is still alive
            os.kill(old_pid, 0)
            print(f"❌ Already running (PID {old_pid}). Exiting.")
            sys.exit(1)
        except (ProcessLookupError, ValueError):
            # Process is dead, stale PID file
            pass
        except PermissionError:
            # Process exists but we can't signal it
            print(f"❌ Already running (PID). Exiting.")
            sys.exit(1)

    # Write our PID
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    # Cleanup on exit
    atexit.register(cleanup_pid)


def cleanup_pid():
    """Remove PID file on exit."""
    try:
        os.remove(PID_FILE)
    except FileNotFoundError:
        pass

# ── Firebase Init ───────────────────────────────────────
SERVICE_ACCOUNT_PATH = os.path.expanduser("~/.openclaw/workspace/.firebase-service-account.json")


def init_firebase():
    """Initialize Firebase Admin SDK."""
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", SERVICE_ACCOUNT_PATH)
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()
    return firestore.client()


# ── Filters ─────────────────────────────────────────────
def strip_think_blocks(text: str) -> str:
    """Remove <think>...</think> blocks from text.
    Also handles unclosed <think> blocks (no closing tag).
    """
    # First: paired <think>...</think>
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Then: unclosed <think> that runs to end of text
    text = re.sub(r"<think>.*$", "", text, flags=re.DOTALL)
    return text.strip()


def strip_final_tags(text: str) -> str:
    """Remove <final>...</final> wrapper, keep inner content."""
    m = re.search(r"<final>(.*?)</final>", text, flags=re.DOTALL)
    if m:
        return m.group(1).strip()
    return text


def strip_inbound_meta(text: str) -> str:
    """Remove OpenClaw inbound metadata blocks from user messages."""
    # Conversation info block
    text = re.sub(
        r"Conversation info \(untrusted metadata\):\s*```json\s*\{[^}]*\}\s*```\s*",
        "", text, flags=re.DOTALL
    ).strip()
    # [Telegram ...] prefix
    text = re.sub(r"^\[Telegram[^\]]*\]\s*", "", text).strip()
    # <file ...>...</file> blocks
    text = re.sub(r"<file[^>]*>.*?</file>", "", text, flags=re.DOTALL).strip()
    # [media attached: ...] lines
    text = re.sub(r"\[media attached:.*?\]\s*", "", text).strip()
    # "To send an image back..." instruction lines
    text = re.sub(r"To send an image back.*?(?:\n|$)", "", text).strip()
    return text


# System-injected user messages to skip
SYSTEM_USER_PATTERNS = [
    r"^Pre-compaction memory flush\.",
    r"^Read HEARTBEAT\.md",
    r"^The conversation history before this point was compacted",
    r"^You are running low on context",
    r"^## Silent Replies",
    r"^## Heartbeats",
    r"^## Runtime",
    r"^## Inbound Context",
    r"^\[system\]",
    r"^<system>",
]
_SYSTEM_USER_RE = re.compile("|".join(SYSTEM_USER_PATTERNS), re.MULTILINE)


def is_system_injected(text: str) -> bool:
    """Detect system-injected messages sent as user role."""
    return bool(_SYSTEM_USER_RE.search(text))


# ── Sensitive Data Redaction ────────────────────────────

# API 키 / 토큰 패턴
_API_KEY_PATTERNS = [
    (r"sk-[A-Za-z0-9_-]{20,}", "[API_KEY]"),              # OpenAI
    (r"sk-ant-[A-Za-z0-9_-]{20,}", "[API_KEY]"),           # Anthropic
    (r"AIza[A-Za-z0-9_-]{30,}", "[API_KEY]"),              # Google
    (r"ghp_[A-Za-z0-9]{30,}", "[GITHUB_TOKEN]"),           # GitHub PAT
    (r"gho_[A-Za-z0-9]{30,}", "[GITHUB_TOKEN]"),           # GitHub OAuth
    (r"github_pat_[A-Za-z0-9_]{30,}", "[GITHUB_TOKEN]"),   # GitHub fine-grained
    (r"xoxb-[A-Za-z0-9-]+", "[SLACK_TOKEN]"),              # Slack bot
    (r"xoxp-[A-Za-z0-9-]+", "[SLACK_TOKEN]"),              # Slack user
    (r"AKIA[A-Z0-9]{16}", "[AWS_KEY]"),                    # AWS access key
    (r"glpat-[A-Za-z0-9_-]{20,}", "[GITLAB_TOKEN]"),       # GitLab
    (r"npm_[A-Za-z0-9]{30,}", "[NPM_TOKEN]"),              # npm
]

# 이메일
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}")

# IP 주소 (내부/외부 모두)
_IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
# localhost, 127.x, 0.0.0.0은 마스킹 제외
_SAFE_IPS = {"127.0.0.1", "0.0.0.0", "255.255.255.255"}

# 절대 경로 (파일 확장자 포함 시 마스킹, 디렉토리만이면 축약)
# /Users/xxx/path/to/file.ext → …/file.ext
# /Users/xxx/some/deep/path/ → …/path/
# /home/xxx/... 등
_ABS_PATH_WITH_EXT = re.compile(
    r"(?<!\w)"                         # 단어 문자 뒤가 아닌
    r"((?:/[A-Za-z0-9._~@-]+){2,})"   # /xxx/yyy/zzz 형태
    r"(?!\w)"                          # 단어 문자 앞이 아닌
)

# 파일 확장자 목록 (마스킹 대상)
_SENSITIVE_EXTENSIONS = {
    ".json", ".key", ".pem", ".p12", ".pfx", ".env",
    ".cfg", ".conf", ".ini", ".yml", ".yaml", ".toml",
    ".sh", ".bash", ".zsh", ".py", ".js", ".ts",
    ".jsonl", ".log", ".csv", ".db", ".sqlite",
    ".cert", ".crt", ".secret",
}

# key=value 패턴
_KEY_VALUE_RE = re.compile(
    r"(?i)(password|passwd|secret|token|api_key|apikey|auth|credential|private_key)"
    r"\s*[=:]\s*"
    r"['\"]?([^\s'\"]{4,})['\"]?"
)

# 특정 프로젝트/인프라 키워드 (필요 시 추가)
_PROJECT_REDACTIONS: dict[str, str] = {
    # "my-secret-project-id": "[PROJECT_ID]",
}


def redact_sensitive(text: str) -> str:
    """민감 정보를 마스킹한다."""

    # 1) API 키 / 토큰
    for pattern, replacement in _API_KEY_PATTERNS:
        text = re.sub(pattern, replacement, text)

    # 2) key=value 시크릿
    text = _KEY_VALUE_RE.sub(lambda m: f"{m.group(1)}=[REDACTED]", text)

    # 3) 이메일
    text = _EMAIL_RE.sub("[EMAIL]", text)

    # 4) IP 주소 (안전한 것 제외)
    def _mask_ip(m):
        ip = m.group(0)
        if ip in _SAFE_IPS:
            return ip
        return "[IP_ADDR]"
    text = _IP_RE.sub(_mask_ip, text)

    # 5) 절대 경로 → 축약
    def _mask_path(m):
        path = m.group(1)
        parts = path.rsplit("/", 1)
        basename = parts[-1] if len(parts) > 1 else parts[0]
        _, ext = os.path.splitext(basename)

        # 확장자가 민감 목록에 있으면 → …/filename.ext
        if ext.lower() in _SENSITIVE_EXTENSIONS:
            return f"…/{basename}"

        # /Users/xxx 또는 /home/xxx 로 시작하면 → 홈 경로 축약
        home_match = re.match(r"^/(Users|home)/[^/]+", path)
        if home_match:
            remainder = path[len(home_match.group(0)):]
            # 남은 경로에서 마지막 2 세그먼트만 보존
            segs = [s for s in remainder.split("/") if s]
            if len(segs) > 2:
                return "…/" + "/".join(segs[-2:])
            elif segs:
                return "…/" + "/".join(segs)
            else:
                return "~/…"

        return path  # 그 외 경로는 유지

    text = _ABS_PATH_WITH_EXT.sub(_mask_path, text)

    # 6) 프로젝트별 커스텀 치환
    for keyword, replacement in _PROJECT_REDACTIONS.items():
        text = text.replace(keyword, replacement)

    return text


def extract_text(content) -> str:
    """Extract plain text from message content (string or list of parts)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(part.get("text", ""))
            elif isinstance(part, str):
                parts.append(part)
        return "\n".join(parts)
    return str(content)


def should_skip(entry: dict) -> bool:
    """Return True if this log entry should be filtered out."""
    entry_type = entry.get("type", "")
    if entry_type in SKIP_TYPES:
        return True
    return False


def clean_message(entry: dict) -> dict | None:
    """Clean a message entry. Returns None if it should be skipped."""
    if should_skip(entry):
        return None

    msg = entry.get("message", {})
    role = msg.get("role", "")
    content = msg.get("content", "")

    if not role or not content:
        return None

    text = extract_text(content)

    # Only user and assistant
    if role not in ("user", "assistant"):
        return None

    # Skip system-injected messages disguised as user role
    if role == "user" and is_system_injected(text):
        return None

    # Clean metadata from user messages
    if role == "user":
        text = strip_inbound_meta(text)

    # Strip <think> and <final> tags from assistant messages
    if role == "assistant":
        text = strip_think_blocks(text)
        text = strip_final_tags(text)

    # Skip empty after cleaning
    if not text.strip():
        return None

    # Skip heartbeat / NO_REPLY
    if text.strip() in ("HEARTBEAT_OK", "NO_REPLY"):
        return None

    # 민감 정보 마스킹
    text = redact_sensitive(text)

    return {
        "role": role,
        "content": text.strip(),
        "timestamp": entry.get("timestamp"),
        "model": entry.get("message", {}).get("model", None),
    }


# ── JSONL Processing ────────────────────────────────────
def get_session_files() -> list[tuple[str, str, str]]:
    """Return list of (agent_id, session_id, file_path) tuples."""
    results = []
    pattern = os.path.join(AGENTS_DIR, "*/sessions/*.jsonl")
    for path in glob.glob(pattern):
        parts = path.split(os.sep)
        # .../agents/<agent_id>/sessions/<session_id>.jsonl
        agent_id = parts[-3]
        session_id = os.path.splitext(parts[-1])[0]
        results.append((agent_id, session_id, path))
    return results


def read_new_lines(filepath: str) -> list[str]:
    """Read only new lines since last poll."""
    offset = file_offsets.get(filepath, 0)
    try:
        size = os.path.getsize(filepath)
        if size < offset:
            # File was truncated/rotated, reset
            offset = 0
        with open(filepath, "r") as f:
            f.seek(offset)
            lines = f.readlines()
            file_offsets[filepath] = f.tell()
            save_offsets()
            return lines
    except FileNotFoundError:
        return []


def make_doc_id(entry: dict) -> str:
    """Create deterministic doc ID to avoid duplicates."""
    raw = f"{entry.get('id', '')}-{entry.get('timestamp', '')}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


# ── Main Loop ───────────────────────────────────────────
def poll_once(db):
    """Single poll iteration."""
    session_files = get_session_files()
    total_uploaded = 0

    for agent_id, session_id, filepath in session_files:
        new_lines = read_new_lines(filepath)
        if not new_lines:
            continue

        batch = db.batch()
        batch_count = 0

        for line in new_lines:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            cleaned = clean_message(entry)
            if cleaned is None:
                continue

            doc_id = make_doc_id(cleaned)
            doc_ref = db.collection(FIRESTORE_COLLECTION).document(doc_id)

            cleaned["agent"] = agent_id
            cleaned["sessionId"] = session_id

            batch.set(doc_ref, cleaned)
            batch_count += 1

        if batch_count > 0:
            batch.commit()
            total_uploaded += batch_count

    if total_uploaded > 0:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Uploaded {total_uploaded} messages")


def main():
    check_pid_lock()
    print(f"🦞 Session Log Watcher starting... (PID {os.getpid()})")
    print(f"   Agents dir: {AGENTS_DIR}")
    print(f"   Poll interval: {POLL_INTERVAL}s")
    print(f"   Firestore collection: {FIRESTORE_COLLECTION}")
    print()

    db = init_firebase()
    print("✅ Firebase connected\n")

    # Load saved offsets or init to EOF on first run
    load_offsets()
    if not file_offsets:
        print("📌 First run: skipping existing logs, watching new only")
        init_offsets_to_eof()

    while True:
        try:
            poll_once(db)
        except KeyboardInterrupt:
            print("\n👋 Watcher stopped.")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
