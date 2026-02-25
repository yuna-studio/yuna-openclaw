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
PID_FILE = os.path.expanduser("~/.openclaw/gajae-os-logger.pid")
OFFSET_FILE = os.path.expanduser("~/.openclaw/gajae-os-logger.offsets.json")

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
    r"^System: \[",
    r"^Conversation info \(untrusted metadata\)",
]
_SYSTEM_USER_RE = re.compile("|".join(SYSTEM_USER_PATTERNS), re.MULTILINE)


def is_system_injected(text: str) -> bool:
    """Detect system-injected messages sent as user role."""
    return bool(_SYSTEM_USER_RE.search(text))


def _extract_user_from_mixed(text: str) -> str | None:
    """Extract actual user input from mixed system+user messages.
    
    Examples:
        "System: [2026-...] Exec completed ...\n\n안된것같은데"
        -> "안된것같은데"
        
        "Conversation info...\n```json\n...\n```\n\n유저입력"
        -> "유저입력"
    """
    # Split by double newline and find non-system parts
    parts = re.split(r'\n{2,}', text)
    user_parts = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Skip system blocks
        if _SYSTEM_USER_RE.search(part):
            continue
        # Skip JSON code blocks
        if part.startswith('```'):
            continue
        # Skip media/image tags
        if part.startswith('[media attached:') or part.startswith('<media:'):
            continue
        if part.startswith('To send an image back'):
            continue
        user_parts.append(part)
    
    result = '\n\n'.join(user_parts).strip()
    return result if result else None


# ── Sensitive Data Redaction ────────────────────────────

# ─── 1. API 키 / 토큰 / 시크릿 패턴 ───
_API_KEY_PATTERNS = [
    # OpenAI (sk-proj, sk-svcacct 등 포함)
    (r"sk-(?:proj-|svcacct-|ant-)?[A-Za-z0-9_-]{20,}", "[API_KEY]"),
    # Google API / Firebase
    (r"AIza[A-Za-z0-9_-]{30,}", "[GOOGLE_KEY]"),
    # GitHub
    (r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}", "[GITHUB_TOKEN]"),
    (r"github_pat_[A-Za-z0-9_]{30,}", "[GITHUB_TOKEN]"),
    # Slack
    (r"xox[bpras]-[A-Za-z0-9-]+", "[SLACK_TOKEN]"),
    # AWS
    (r"AKIA[A-Z0-9]{16}", "[AWS_KEY]"),
    (r"(?:aws_secret_access_key|aws_session_token)\s*[=:]\s*\S+", "[AWS_SECRET]"),
    # GitLab
    (r"glpat-[A-Za-z0-9_-]{20,}", "[GITLAB_TOKEN]"),
    # npm
    (r"npm_[A-Za-z0-9]{30,}", "[NPM_TOKEN]"),
    # Telegram bot token (숫자:영문, suffix 34-43자)
    (r"(?<![A-Za-z0-9])\d{8,10}:[A-Za-z0-9_-]{34,43}(?![A-Za-z0-9])", "[TELEGRAM_BOT_TOKEN]"),
    # Discord bot token (base64-ish)
    (r"[MN][A-Za-z0-9]{23,}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,}", "[DISCORD_TOKEN]"),
    # Firebase/GCP service account private key fragment
    (r"-----BEGIN (?:RSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA )?PRIVATE KEY-----", "[PRIVATE_KEY]"),
    # JWT (3-part base64 dot-separated, 100+ chars)
    (r"eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}", "[JWT_TOKEN]"),
    # Stripe
    (r"(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{20,}", "[STRIPE_KEY]"),
    # Supabase / generic long hex tokens
    (r"sbp_[A-Za-z0-9]{30,}", "[SUPABASE_TOKEN]"),
    # Vercel
    (r"vercel_[A-Za-z0-9_-]{20,}", "[VERCEL_TOKEN]"),
    # Cloudflare
    (r"cf_[A-Za-z0-9_-]{30,}", "[CF_TOKEN]"),
    # Generic long hex secret (40+ chars, likely a key)
    (r"\b[0-9a-f]{40,}\b", "[HEX_SECRET]"),
]

# ─── 2. 이메일 ───
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# ─── 3. 전화번호 ───
_PHONE_PATTERNS = re.compile(
    r"(?:"
    # 한국 휴대폰: 010-1234-5678, 010 1234 5678, 01012345678
    r"01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}"
    r"|"
    # 한국 유선: 02-1234-5678, 031-123-4567 등
    r"0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4}"
    r"|"
    # 국제 형식: +82-10-1234-5678, +1-234-567-8901
    r"\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
    r")"
)

# ─── 4. IP 주소 ───
_IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_SAFE_IPS = {"127.0.0.1", "0.0.0.0", "255.255.255.255"}

# ─── 5. 절대 경로 ───
_ABS_PATH_RE = re.compile(
    r"(?<!\w)"
    r"((?:/[A-Za-z0-9._~@-]+){2,})"
    r"(?!\w)"
)

# ─── 6. 단독 파일명 (경로 없이 확장자 붙은 파일명) ───
# 앞: 슬래시나 ASCII 단어문자 뒤가 아닌 (한글 뒤는 OK)
# 뒤: ASCII 단어문자 앞이 아닌 (한글 앞은 OK)
_SENSITIVE_FILE_EXTS = [
    "json", "jsonl", "key", "pem", "p12", "pfx",
    "env", "cfg", "conf", "ini", "yml", "yaml", "toml",
    "sh", "bash", "zsh", "py", "js", "ts", "tsx", "jsx",
    "log", "csv", "db", "sqlite", "sql",
    "cert", "crt", "secret", "bak",
    "tar", "gz", "zip", "rar",
]
_STANDALONE_FILE_RE = re.compile(
    r"(?<![/A-Za-z0-9_])"
    r"(\.?[A-Za-z0-9_.-]+\.(?:" + "|".join(_SENSITIVE_FILE_EXTS) + r"))"
    r"(?![A-Za-z0-9_])"
)

# 파일명 화이트리스트 (마스킹 제외 — 코드 대화에서 자주 쓰이는 일반 파일명)
_FILE_WHITELIST = {
    "package.json", "tsconfig.json", "setup.py", "requirements.txt",
    "Makefile", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    ".gitignore", ".env.example", "README.md", "LICENSE",
    "index.js", "index.ts", "main.py", "app.py", "app.js",
    "SKILL.md", "AGENTS.md", "SOUL.md", "USER.md", "MEMORY.md",
    "HEARTBEAT.md", "TOOLS.md", "IDENTITY.md", "BOOTSTRAP.md",
    "firestore.rules", "firebase.json",
}

# 파일 확장자 (경로 내 확장자 감지용)
_SENSITIVE_EXTENSIONS = {
    ".json", ".jsonl", ".key", ".pem", ".p12", ".pfx", ".env",
    ".cfg", ".conf", ".ini", ".yml", ".yaml", ".toml",
    ".sh", ".bash", ".zsh", ".py", ".js", ".ts", ".tsx", ".jsx",
    ".log", ".csv", ".db", ".sqlite", ".sql",
    ".cert", ".crt", ".secret", ".bak",
    ".tar", ".gz", ".zip", ".rar",
}

# ─── 7. key=value 시크릿 ───
_KEY_VALUE_RE = re.compile(
    r"(?i)(password|passwd|secret|token|api_key|apikey|api[-_]?secret"
    r"|auth|credential|private_key|access_key|client_secret"
    r"|db_password|database_url|redis_url|mongo_uri|connection_string"
    r"|[A-Z0-9_]*_KEY)"
    r"\s*[=:]\s*"
    r"['\"]?([^\s'\"]{4,})['\"]?"
)

# ─── 8. 프로젝트별 커스텀 치환 ───
_PROJECT_REDACTIONS: dict[str, str] = {
    # "my-secret-project-id": "[PROJECT_ID]",
}


def redact_sensitive(text: str) -> str:
    """민감 정보를 마스킹한다."""

    # 1) API 키 / 토큰 (가장 먼저 — 다른 패턴에 걸리기 전에)
    for pattern, replacement in _API_KEY_PATTERNS:
        text = re.sub(pattern, replacement, text)

    # 2) key=value 시크릿
    text = _KEY_VALUE_RE.sub(lambda m: f"{m.group(1)}=[REDACTED]", text)

    # 2b) _KEY가 들어간 환경변수명 자체도 축약 (예: NEXT_PUBLIC_X_KEY)
    # 이미 치환된 [API_KEY] 등 마커 안의 텍스트는 건드리지 않도록 lookaround 사용
    text = re.sub(r"(?<!\[)\b[A-Z0-9_]*_KEY\b(?!\])", "[ENV_KEY]", text)

    # 3) 이메일
    text = _EMAIL_RE.sub("[EMAIL]", text)

    # 4) 전화번호
    text = _PHONE_PATTERNS.sub("[PHONE]", text)

    # 5) IP 주소 (안전한 것 제외)
    def _mask_ip(m):
        ip = m.group(0)
        if ip in _SAFE_IPS:
            return ip
        return "[IP_ADDR]"
    text = _IP_RE.sub(_mask_ip, text)

    # 6) 절대 경로 → 축약
    def _mask_path(m):
        path = m.group(1)
        parts = path.rsplit("/", 1)
        basename = parts[-1] if len(parts) > 1 else parts[0]
        _, ext = os.path.splitext(basename)

        # 화이트리스트 파일은 유지
        if basename in _FILE_WHITELIST:
            return basename

        # 확장자가 민감 목록에 있으면 → …/filename.ext
        if ext.lower() in _SENSITIVE_EXTENSIONS:
            return f"…/{basename}"

        # /Users/xxx 또는 /home/xxx 로 시작하면 → 홈 경로 축약
        home_match = re.match(r"^/(Users|home)/[^/]+", path)
        if home_match:
            remainder = path[len(home_match.group(0)):]
            segs = [s for s in remainder.split("/") if s]
            if len(segs) > 2:
                return "…/" + "/".join(segs[-2:])
            elif segs:
                return "…/" + "/".join(segs)
            else:
                return "~/…"

        return path

    text = _ABS_PATH_RE.sub(_mask_path, text)

    # 7) 단독 파일명 (화이트리스트 제외)
    def _mask_file(m):
        fname = m.group(1)
        if fname in _FILE_WHITELIST:
            return fname
        return f"[FILE:{os.path.splitext(fname)[1]}]"

    text = _STANDALONE_FILE_RE.sub(_mask_file, text)

    # 7b) dotenv 파일 (.env, .env.local, .env.production 등)
    text = re.sub(
        r"(?<![/A-Za-z0-9_])(\.env(?:\.[A-Za-z0-9_]+)?)(?![A-Za-z0-9_.])",
        lambda m: m.group(1) if m.group(1) in _FILE_WHITELIST else "[DOTENV]",
        text,
    )

    # 8) 프로젝트별 커스텀 치환
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
    # But extract actual user input if mixed with system prefix
    if role == "user" and is_system_injected(text):
        # Try to extract user input after system block
        # Pattern: "System: [...] ...\n\nactual user message" or
        #          "Conversation info...\n```json\n...\n```\n\nactual user message"
        user_input = _extract_user_from_mixed(text)
        if user_input:
            text = user_input
        else:
            # Fallback: strip_inbound_meta로 메타데이터 제거 후 남은 텍스트 확인
            stripped = strip_inbound_meta(text)
            if stripped and stripped != text:
                text = stripped
            else:
                return None

    # Clean metadata from user messages
    if role == "user":
        text = strip_inbound_meta(text)

    # Strip <think> and <final> tags from assistant messages
    if role == "assistant":
        text = strip_think_blocks(text)
        text = strip_final_tags(text)

    # Remove reply tags injected for messaging surfaces
    text = re.sub(r"\[\[\s*reply_to_current\s*\]\]", "", text, flags=re.IGNORECASE).strip()

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
        BATCH_LIMIT = 450  # Firestore batch limit is 500, use 450 for safety

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

            # Firestore batch limit
            if batch_count >= BATCH_LIMIT:
                try:
                    batch.commit()
                    total_uploaded += batch_count
                except Exception as e:
                    print(f"[ERROR] Batch commit failed: {e}", flush=True)
                batch = db.batch()
                batch_count = 0

        if batch_count > 0:
            try:
                batch.commit()
                total_uploaded += batch_count
            except Exception as e:
                print(f"[ERROR] Batch commit failed: {e}", flush=True)

    if total_uploaded > 0:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Uploaded {total_uploaded} messages", flush=True)


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
