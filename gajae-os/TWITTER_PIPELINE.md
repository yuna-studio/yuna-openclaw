# Twitter/X Ingest Pipeline (gajae-os)

`twitter_ingest.py`는 트위터/X URL을 받아 BIP 블로그 초안을 자동 생성합니다.

## 저장 위치
- Firestore: `projects/{projectId}/blog_posts/{postId}`
- 기본 상태: `draft`
- source 추적: `sourceType=twitter_article`, `sourceUrl=<tweet_url>`
- 같은 sourceUrl은 upsert(중복 생성 방지)

## 빠른 실행

```bash
cd /Users/openclaw-kong/workspace/yuna-openclaw/gajae-os

python3 twitter_ingest.py \
  --project-id vibe-coding-showcase \
  --tweet-url "https://x.com/<user>/status/<id>"
```

여러 개 입력:

```bash
python3 twitter_ingest.py \
  --project-id vibe-coding-showcase \
  --tweet-url "https://x.com/u1/status/111" \
  --tweet-url "https://x.com/u2/status/222"
```

파일 입력(한 줄에 URL 하나):

```bash
python3 twitter_ingest.py \
  --project-id vibe-coding-showcase \
  --input-file ./temp/twitter_urls.txt
```

바로 게시 상태로 저장:

```bash
python3 twitter_ingest.py \
  --project-id vibe-coding-showcase \
  --input-file ./temp/twitter_urls.txt \
  --publish
```

쓰기 없이 확인만:

```bash
python3 twitter_ingest.py \
  --project-id vibe-coding-showcase \
  --tweet-url "https://x.com/<user>/status/<id>" \
  --dry-run
```

## 환경변수 로딩 우선순위
1. `FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY`
2. `GOOGLE_APPLICATION_CREDENTIALS` (service account json)
3. `/Users/openclaw-kong/workspace/yuna-openclaw/.env` 자동 로드

## 참고
- 본문 수집은 비공식 `tweet-result` endpoint를 사용합니다.
- endpoint 정책 변경/차단 시 수집 실패할 수 있으니, 실패 로그 확인 후 fetch layer 교체 필요.
