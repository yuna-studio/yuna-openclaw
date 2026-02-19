#!/usr/bin/env python3
"""
Twitter/X → BIP Blog Ingest Pipeline (gajae-os)

목표
- 트위터/X 게시물 URL을 입력받아 본문을 수집
- BIP Firestore `projects/{projectId}/blog_posts`에 블로그 draft로 저장
- sourceUrl 중복 시 upsert(merge)로 갱신

의존성
- python stdlib
- firebase_admin (로컬 설치 필요)

환경변수 (자동 탐색)
1) FIREBASE_PROJECT_ID / FIREBASE_CLIENT_EMAIL / FIREBASE_PRIVATE_KEY
2) 없으면 `GOOGLE_APPLICATION_CREDENTIALS` (service account json)
3) 없으면 `/Users/openclaw-kong/workspace/yuna-openclaw/.env` 로드 시도

사용 예시
python3 twitter_ingest.py \
  --project-id vibe-coding-showcase \
  --tweet-url "https://x.com/someuser/status/1888888888888888888" \
  --tweet-url "https://twitter.com/someuser/status/1999999999999999999"

python3 twitter_ingest.py \
  --project-id vibe-coding-showcase \
  --input-file ./temp/twitter_urls.txt \
  --publish
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore

SOURCE_TYPE = "twitter_article"
DEFAULT_CATEGORY = "트위터 아티클"
DEFAULT_TAGS = ["twitter", "x", "오가닉", "seo", "geo"]

ROOT_ENV_PATH = "/Users/openclaw-kong/workspace/yuna-openclaw/.env"


# ─────────────────────────────────────────────────────────────
# Utils
# ─────────────────────────────────────────────────────────────


def load_dotenv_if_exists(path: str) -> None:
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception as e:
        print(f"[warn] .env 로드 실패: {e}")



def now_ymd() -> str:
    return datetime.now().strftime("%Y-%m-%d")



def clean_text(v: Any) -> str:
    return str(v or "").strip()



def slugify(v: str) -> str:
    s = clean_text(v).lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s



def parse_tweet_id(url: str) -> str:
    # 예: https://x.com/user/status/1234567890
    # 예: https://twitter.com/user/status/1234567890?s=20
    m = re.search(r"/status/(\d+)", url)
    if not m:
        raise ValueError(f"유효한 status URL이 아님: {url}")
    return m.group(1)



def parse_username_from_url(url: str) -> str:
    # /{username}/status/{id}
    parsed = urllib.parse.urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) >= 2 and parts[1] == "status":
        return parts[0]
    return "unknown"



def request_json(url: str, timeout: int = 15) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="ignore")
        return json.loads(body)


# ─────────────────────────────────────────────────────────────
# Fetch layer (no official API key required)
# ─────────────────────────────────────────────────────────────


@dataclass
class TweetData:
    tweet_id: str
    url: str
    username: str
    author_name: str
    author_handle: str
    created_at: str
    text: str
    lang: str


@dataclass
class LLMOptions:
    enabled: bool = False
    agent: str = "main"
    timeout: int = 90


def fetch_tweet(url: str, lang: str = "ko") -> TweetData:
    tweet_id = parse_tweet_id(url)
    username = parse_username_from_url(url)

    # 비공식 syndication endpoint (인증키 없이 단건 조회)
    endpoint = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&lang={urllib.parse.quote(lang)}"
    data = request_json(endpoint)

    text = clean_text(data.get("text"))
    user = data.get("user") or {}

    author_name = clean_text(user.get("name") or username)
    author_handle = clean_text(user.get("screen_name") or username)
    created_at = clean_text(data.get("created_at"))  # 예: Wed Jan 10 00:20:00 +0000 2024

    if not text:
        raise RuntimeError(f"트윗 본문 추출 실패: {url}")

    return TweetData(
        tweet_id=tweet_id,
        url=url,
        username=username,
        author_name=author_name,
        author_handle=author_handle,
        created_at=created_at,
        text=text,
        lang=lang,
    )


# ─────────────────────────────────────────────────────────────
# Blog Draft generation
# ─────────────────────────────────────────────────────────────


def build_title(tweet: TweetData) -> str:
    first_line = tweet.text.splitlines()[0].strip()
    first_line = re.sub(r"\s+", " ", first_line)
    if len(first_line) > 56:
        first_line = first_line[:56].rstrip() + "…"
    return first_line or f"트위터 아티클 #{tweet.tweet_id[-6:]}"



def build_summary(tweet: TweetData) -> str:
    s = re.sub(r"\s+", " ", tweet.text).strip()
    if len(s) > 140:
        s = s[:140].rstrip() + "…"
    return s


def normalize_tweet_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n")
    lines: list[str] = []
    for raw in normalized.split("\n"):
        line = re.sub(r"\s+", " ", raw).strip()
        # 본문 가독성을 해치는 단독 t.co 링크 라인은 제거
        if re.fullmatch(r"https?://t\.co/\w+", line):
            continue
        if line:
            lines.append(line)
    return "\n".join(lines)


def split_sentences(text: str) -> list[str]:
    one_line = re.sub(r"\s+", " ", text).strip()
    if not one_line:
        return []
    parts = [p.strip() for p in re.split(r"(?<=[.!?…])\s+", one_line) if p.strip()]
    return parts if parts else [one_line]


def paragraphize(sentences: list[str], chunk_size: int = 2) -> list[str]:
    if not sentences:
        return []
    chunks: list[str] = []
    for i in range(0, len(sentences), chunk_size):
        chunks.append(" ".join(sentences[i : i + chunk_size]))
    return chunks


def build_markdown(tweet: TweetData, title: str) -> str:
    source_url = tweet.url
    normalized = normalize_tweet_text(tweet.text)
    sentences = split_sentences(normalized)
    key_points = "\n".join([f"- {s}" for s in sentences[:3]]) or "- (요약 필요)"

    paragraphs = paragraphize(sentences, chunk_size=2)
    quoted = "\n\n".join([f"> {p}" for p in paragraphs])

    return f"""# {title}

## 원문 메타
- 작성자: {tweet.author_name} (@{tweet.author_handle})
- 원문 링크: {source_url}
- 수집일: {now_ymd()}

## 핵심 포인트
{key_points}

## 원문 (가독성 정리본)
{quoted}

## 메모
- 필요하면 위 포인트를 기준으로 블로그 본문을 확장해 주세요.
"""



def extract_first_json_object(text: str) -> dict[str, Any] | None:
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    in_str = False
    escaped = False
    for idx in range(start, len(text)):
        ch = text[idx]
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_str = False
            continue

        if ch == '"':
            in_str = True
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : idx + 1]
                try:
                    return json.loads(candidate)
                except Exception:
                    return None
    return None


def rewrite_with_openclaw(
    tweet: TweetData,
    title: str,
    summary: str,
    content_md: str,
    llm: LLMOptions,
) -> tuple[str, str, str]:
    if not llm.enabled:
        return title, summary, content_md

    prompt = f"""너는 트위터 게시물을 읽기 쉬운 블로그 마크다운으로 정리하는 편집자야.
사실 왜곡/추측 없이 원문 의미를 보존해.

아래 정보를 바탕으로 JSON만 출력해.
키는 반드시 title, summary, contentMd 3개.
코드펜스(```) 금지.

[source]
url: {tweet.url}
author: {tweet.author_name} (@{tweet.author_handle})

[raw_text]
{tweet.text}

[baseline_title]
{title}

[baseline_summary]
{summary}

[baseline_markdown]
{content_md}
"""

    cmd = [
        "openclaw",
        "agent",
        "--agent",
        llm.agent,
        "--message",
        prompt,
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=llm.timeout,
            check=False,
        )
    except Exception as e:
        print(f"[warn] openclaw 호출 실패, fallback 사용: {e}")
        return title, summary, content_md

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        print(f"[warn] openclaw 응답 실패(code={proc.returncode}), fallback 사용: {err[:240]}")
        return title, summary, content_md

    payload = extract_first_json_object(proc.stdout or "")
    if not payload:
        print("[warn] openclaw JSON 파싱 실패, fallback 사용")
        return title, summary, content_md

    llm_title = clean_text(payload.get("title")) or title
    llm_summary = clean_text(payload.get("summary")) or summary
    llm_content = clean_text(payload.get("contentMd")) or content_md
    return llm_title, llm_summary, llm_content


def make_slug(tweet: TweetData, title: str) -> str:
    ymd = datetime.now().strftime("%Y%m%d")
    base = slugify(title)[:48] or f"tweet-{tweet.tweet_id[-8:]}"
    return f"x-{ymd}-{base}-{tweet.tweet_id[-6:]}"


# ─────────────────────────────────────────────────────────────
# Firestore
# ─────────────────────────────────────────────────────────────


def init_firestore() -> firestore.Client:
    load_dotenv_if_exists(ROOT_ENV_PATH)

    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
    private_key = os.environ.get("FIREBASE_PRIVATE_KEY")

    if not firebase_admin._apps:
        if project_id and client_email and private_key:
            cred = credentials.Certificate(
                {
                    "type": "service_account",
                    "project_id": project_id,
                    "client_email": client_email,
                    "private_key": private_key.replace("\\n", "\n"),
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            )
            firebase_admin.initialize_app(cred)
        else:
            # fallback: GOOGLE_APPLICATION_CREDENTIALS
            firebase_admin.initialize_app()

    return firestore.client()



def blog_posts_ref(db: firestore.Client, project_id: str = ""):
    if project_id:
        return db.collection("projects").document(project_id).collection("blog_posts")
    return db.collection("blog_posts")


def find_existing_by_source(
    db: firestore.Client, project_id: str, source_url: str
) -> tuple[str | None, dict[str, Any] | None]:
    ref = (
        blog_posts_ref(db, project_id)
        .where("sourceType", "==", SOURCE_TYPE)
        .where("sourceUrl", "==", source_url)
        .limit(1)
    )
    snap = ref.get()
    if not snap:
        return None, None
    doc = snap[0]
    return doc.id, doc.to_dict()



def upsert_blog_post(
    db: firestore.Client,
    *,
    project_id: str,
    tweet: TweetData,
    publish: bool,
    category: str,
    tags: list[str],
    order: int,
    llm: LLMOptions,
) -> tuple[str, str]:
    title = build_title(tweet)
    summary = build_summary(tweet)
    content_md = build_markdown(tweet, title)
    title, summary, content_md = rewrite_with_openclaw(tweet, title, summary, content_md, llm)
    slug = make_slug(tweet, title)
    status = "published" if publish else "draft"

    existing_id, existing = find_existing_by_source(db, project_id, tweet.url)

    payload: dict[str, Any] = {
        "title": title,
        "slug": slug if not existing else clean_text(existing.get("slug")) or slug,
        "summary": summary,
        "contentMd": content_md,
        "category": category,
        "tags": tags,
        "status": status,
        "sourceType": SOURCE_TYPE,
        "sourceUrl": tweet.url,
        "displayDate": now_ymd(),
        "order": order,
        "updatedAt": datetime.now(),
    }

    if publish:
        payload["publishedAt"] = datetime.now()

    posts_ref = blog_posts_ref(db, project_id)

    if existing_id:
        posts_ref.document(existing_id).set(payload, merge=True)
        return existing_id, "updated"

    payload["createdAt"] = datetime.now()
    created = posts_ref.add(payload)
    doc_ref = created[1] if isinstance(created, tuple) else created
    return doc_ref.id, "created"


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────


def read_input_file(path: str) -> list[str]:
    urls: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    return urls



def compute_order(tweet: TweetData, fallback_idx: int) -> int:
    # 최신이 큰 숫자 되도록 yyyymmddHHMMSS 기반 int 사용
    # created_at parse 실패 시 현재 시각 + fallback 사용
    created = tweet.created_at
    try:
        dt = datetime.strptime(created, "%a %b %d %H:%M:%S %z %Y")
    except Exception:
        dt = datetime.now()
    base = int(dt.strftime("%Y%m%d%H%M%S"))
    return base + fallback_idx



def main() -> int:
    p = argparse.ArgumentParser(description="Twitter/X ingest pipeline for BIP blog")
    p.add_argument("--project-id", default="", help="BIP project id (optional). 비우면 global blog_posts 사용")
    p.add_argument("--tweet-url", action="append", default=[], help="tweet/status URL (repeatable)")
    p.add_argument("--input-file", help="line-separated URL file")
    p.add_argument("--lang", default="ko", help="tweet fetch language (default: ko)")
    p.add_argument("--category", default=DEFAULT_CATEGORY)
    p.add_argument("--tags", default=",".join(DEFAULT_TAGS), help="comma-separated tags")
    p.add_argument("--publish", action="store_true", help="save as published (default: draft)")
    p.add_argument("--dry-run", action="store_true", help="fetch/transform only, no firestore write")
    p.add_argument("--llm", action="store_true", help="OpenClaw 에이전트로 가독성 리라이트 수행")
    p.add_argument("--llm-agent", default="main", help="openclaw agent --agent 값 (default: main)")
    p.add_argument("--llm-timeout", type=int, default=90, help="openclaw 호출 타임아웃(초)")

    args = p.parse_args()

    urls: list[str] = []
    urls.extend(args.tweet_url or [])
    if args.input_file:
        urls.extend(read_input_file(args.input_file))

    # dedupe preserve order
    seen = set()
    deduped = []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        deduped.append(u)

    if not deduped:
        print("[error] 입력 URL이 없습니다. --tweet-url 또는 --input-file 사용")
        return 2

    tags = [clean_text(t) for t in args.tags.split(",") if clean_text(t)]
    llm = LLMOptions(enabled=bool(args.llm), agent=clean_text(args.llm_agent) or "main", timeout=max(10, int(args.llm_timeout)))

    db = None if args.dry_run else init_firestore()

    ok = 0
    fail = 0

    for i, url in enumerate(deduped):
        try:
            tweet = fetch_tweet(url, lang=args.lang)
            order = compute_order(tweet, i)

            if args.dry_run:
                title = build_title(tweet)
                summary = build_summary(tweet)
                content_md = build_markdown(tweet, title)
                title, summary, content_md = rewrite_with_openclaw(tweet, title, summary, content_md, llm)
                print(json.dumps({
                    "url": url,
                    "title": title,
                    "summary": summary,
                    "slug": make_slug(tweet, title),
                    "status": "published" if args.publish else "draft",
                    "contentMd": content_md,
                }, ensure_ascii=False))
            else:
                doc_id, action = upsert_blog_post(
                    db,
                    project_id=args.project_id,
                    tweet=tweet,
                    publish=args.publish,
                    category=args.category,
                    tags=tags,
                    order=order,
                    llm=llm,
                )
                print(f"[{action}] {doc_id} <- {url}")

            ok += 1
        except Exception as e:
            fail += 1
            print(f"[error] {url} :: {e}")

    print(f"done: ok={ok}, fail={fail}, total={len(deduped)}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
