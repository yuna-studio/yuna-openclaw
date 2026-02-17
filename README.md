# 🦞 가재 컴퍼니 — Gajae Company

> **1명의 사람과 3마리의 AI 가재가 만드는 바이브 코딩 쇼케이스**

## 🔴 Live

**[nangman.live](https://nangman.live)**

기획부터 배포까지, AI와 나누는 모든 대화를 실시간으로 공개합니다.

## 팀

| 이름 | 역할 |
|------|------|
| 낭만코딩 | CEO · 텔레그램으로 지시 |
| 비서가재 🦞 | 총괄 · 판단 · 실행 |
| 탐정가재 🔍 | 조사 · 기획 · 개발 |
| 판사가재 ⚖️ | 품질 검수 · 브랜드 가드 |

## 구조

```
yuna-openclaw/
├── gajae-os/          # AI 에이전트 파이프라인 (Python)
│   ├── planner.py     # 기획 파이프라인 (LangGraph)
│   ├── architect.py   # 설계 파이프라인
│   ├── develop.py     # 개발 파이프라인
│   ├── logger.py      # Firestore 채팅 로그 업로더
│   ├── notion_upload.py
│   └── tests/
├── scripts/           # 유틸리티 스크립트
│   └── seed_projects.py
├── docs/
│   └── core/AGENT_SPEC.md  # Planner 에이전트 스펙
└── bip/               # 프론트엔드 (Next.js, .gitignore)
```

## 기술 스택

- **에이전트**: OpenClaw + LangGraph (Python)
- **프론트엔드**: Next.js 15 + Tailwind CSS + Framer Motion
- **데이터**: Firebase Firestore (채팅 로그, 리액션, 포트폴리오)
- **실시간**: Firestore onSnapshot + RTDB (접속자 수)
- **배포**: Firebase Hosting + Cloudflare DNS
- **도메인**: nangman.live (GoDaddy + Cloudflare)
- **문서**: Notion API (기획서, 설계서 자동 업로드)

## 작동 방식

```
텔레그램 → 비서가재 판단 → ⚡ 직접 처리
                          → 🔄 파이프라인 (탐정 → 판사 → 배포)
```

모든 대화가 Firestore에 기록되고, 웹사이트에서 실시간으로 공개됩니다.

---

*Built with [OpenClaw](https://openclaw.ai) · © 2026 가재 컴퍼니*
