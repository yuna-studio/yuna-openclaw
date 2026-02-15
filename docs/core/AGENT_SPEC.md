# 🦞 비서가재 (Secretary Lobster) — 기능 명세서

> 최종 업데이트: 2026-02-15

## 개요

비서가재는 OpenClaw 기반의 AI 비서 에이전트로, 대표님(CEO)의 텔레그램 채널에서 운영됩니다.
단순 대화를 넘어 **자동화 시스템 운영, 기획 에이전트 오케스트레이션, 로그 관리**를 수행합니다.

---

## 시스템 구성

```
대표님 (Telegram)
    ↕
비서가재 (OpenClaw Main Agent)
    ├── Logger (세션 로그 → Firestore)
    ├── Planner (기획 에이전트)
    └── (향후 확장)
```

---

## 모듈 1: Logger

> 코드: `gajae-os/logger.py`
> 테스트: `gajae-os/tests/test_logger.py` (174 unit tests)

### 기능
OpenClaw 세션 로그를 실시간으로 Firestore에 업로드하는 백그라운드 워커.

### 동작 방식
- 1초 간격 폴링으로 세션 JSONL 파일 감시
- 신규 메시지만 Firestore `chat_logs` 컬렉션에 업로드
- PID 락 → 중복 실행 방지
- 오프셋 파일 → 재시작 시 중복 업로드 방지

### 필터링 (업로드에서 제외)
| 대상 | 처리 |
|---|---|
| `system`, `tool` role | 스킵 |
| `session`, `model_change`, `thinking_level_change`, `custom` 타입 | 스킵 |
| 시스템 주입 메시지 (Pre-compaction, HEARTBEAT 등) | 스킵 |
| `<think>...</think>` 블록 | 제거 (unclosed 포함) |
| `<final>...</final>` 태그 | 태그만 제거, 내용 보존 |
| Conversation info, [Telegram ...], [media attached] 등 메타데이터 | 제거 |
| `HEARTBEAT_OK`, `NO_REPLY` | 스킵 |

### 민감정보 마스킹 (Redaction)
| 카테고리 | 패턴 | 치환 |
|---|---|---|
| API 키 | OpenAI, Anthropic, Google, GitHub, Slack, AWS, Stripe, Vercel, Cloudflare 등 | `[API_KEY]`, `[GITHUB_TOKEN]` 등 |
| 토큰 | Telegram Bot, Discord, JWT, npm, Supabase, GitLab | `[*_TOKEN]` |
| PEM 키 | `-----BEGIN PRIVATE KEY-----` | `[PRIVATE_KEY]` |
| 이메일 | `user@domain.com` | `[EMAIL]` |
| 전화번호 | 한국 (010, 02, +82 등) / 국제 | `[PHONE]` |
| IP 주소 | 내부/외부 (127.0.0.1 등 safe IP 제외) | `[IP_ADDR]` |
| 절대 경로 | `/Users/xxx/...`, `/home/xxx/...` | `…/filename.ext` 또는 `…/last/segments` |
| 단독 파일명 | `config.yaml`, `secret.key` 등 (화이트리스트 제외) | `[FILE:.ext]` |
| dotenv | `.env`, `.env.local`, `.env.production` (`.env.example` 제외) | `[DOTENV]` |
| key=value | `password=`, `token:`, `database_url=` 등 | `key=[REDACTED]` |
| 긴 hex | 40자+ hex 문자열 | `[HEX_SECRET]` |

### 화이트리스트 (마스킹 제외)
`package.json`, `tsconfig.json`, `setup.py`, `docker-compose.yml`, `.gitignore`, `.env.example`, `firestore.rules`, `firebase.json`, OpenClaw 설정 파일 등

### 인프라
- Firestore 프로젝트: `gajae-company-bip`
- 컬렉션: `chat_logs`
- 서비스 계정: `.firebase-service-account.json` (gitignored)
- 로그: `~/.openclaw/gajae-os-logger.log`
- PID: `~/.openclaw/gajae-os-logger.pid`
- 오프셋: `~/.openclaw/gajae-os-logger.offsets.json`

---

## 모듈 2: Planner

> 코드: `gajae-os/planner/`
> 프롬프트: `RESEARCHER.md`, `PLANNER.md`
> 출력: `gajae-os/planner/outputs/`

### 기능
PO(Product Owner) 레벨의 기획서(1-Pager)를 자동 생성하는 에이전트 시스템.

### 트리거 조건

| 대표님 요청 | 비서가재 판단 |
|---|---|
| "기획해줘", "플래닝하자", "1-Pager 뽑아줘" | → 즉시 Planner 가동 |
| "XX 기능 만들자", "XX 앱 만들자" (신규 기능/제품) | → "기획부터 돌릴까요?" 확인 후 가동 |
| "버튼 색 바꿔", "버그 고쳐" (단순 작업) | → 바로 실행 (Planner 불필요) |

### 공정 (2-Agent Pipeline)

```
비서가재 → spawn(Researcher) → spawn(Planner) → 결과 announce
```

#### Agent 1: Researcher
- **역할**: Market Research Analyst
- **도구**: `web_search` (최소 5회, 한/영 검색)
- **산출물**: 시장 조사 보고서 (시장 현황, 경쟁사 3개+, Pain Point, 기회 영역)
- **원칙**: 팩트만, 출처와 함께. 의견/추측 금지

#### Agent 2: Planner
- **역할**: PO 기획 전문가 (5개 Phase 순차 실행)
- **Phase 1 — Strategist**: Researcher 결과 기반 IF-THEN 가설 수립
- **Phase 2 — Product Designer**: P0/P1 구분, MVP 스펙 설계 (1인 개발자 제약)
- **Phase 3 — Data Scientist**: Primary/Counter Metric, Go/Stop 기준
- **Phase 4 — Growth Hacker**: Aha-Moment, 수동 운영 계획, 런칭 전략
- **Phase 5 — PO Critique**: 자가 검증 (7개 항목, 10점 만점)

### 평가 기준 (Phase 5)

| 항목 | 기준 |
|---|---|
| 가설 명확성 | 구체적이고 검증 가능한가? |
| 근거 충분성 | Researcher 데이터에 뒷받침되는가? |
| P0 최소성 | 하나라도 더 뺄 수 있지 않은가? |
| 실현 가능성 | 1인 개발자가 기간 내 구현 가능한가? |
| 메트릭 측정 가능성 | 실제로 측정할 인프라가 있는가? |
| Go/Stop 기준 명확성 | 구체적 수치인가? |
| 리스크 인식 | Counter Metric과 실패 시나리오를 정직하게 다뤘는가? |

### 판정

| 평균 점수 | 판정 | 액션 |
|---|---|---|
| **7점 이상** | ✅ PASS | 최종 1-Pager 출력 |
| **5~6점** | ⚠️ REVISE | 부족 항목 지적 후 Phase 1부터 재수행 (최대 2회) |
| **5점 미만** | ❌ REJECT | 근본적 재검토 필요 + 사유 |

### 산출물
- `gajae-os/planner/outputs/YYYY-MM-DD-{기능명}.md` — 최종 1-Pager
- `gajae-os/planner/outputs/YYYY-MM-DD-{기능명}-research.md` — 시장 조사 보고서

---

## 향후 확장 예정

| 모듈 | 설명 | 상태 |
|---|---|---|
| Logger | 세션 로그 → Firestore | ✅ 운영 중 |
| Planner | PO 기획 에이전트 | ✅ 구현 완료 |
| Coder | 코드 생성/리팩토링 에이전트 | 🔲 미정 |
| Deployer | CI/CD 자동화 | 🔲 미정 |
| Monitor | 서비스 헬스체크/알림 | 🔲 미정 |

---

## 운영 정보

- **에이전트명**: 비서가재 (Secretary Lobster) 🦞
- **플랫폼**: OpenClaw + Telegram
- **모델**: claude-opus-4-6-thinking (Google Antigravity)
- **Git**: `https://github.com/yuna-studio/yuna-openclaw.git`
- **브랜치**: `main` (production), `dev` (development)
- **워크스페이스**: `~/.openclaw/workspace`
