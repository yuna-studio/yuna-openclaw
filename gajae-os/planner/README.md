# Planner - PO Level Feature Planning Agent

## 구조

```
대표님 → 비서가재 → spawn(Researcher) → spawn(Planner) → 1-Pager 결과
```

## 사용법

비서가재에게 다음과 같이 요청:

```
"데일리부동산에 알림 기능 기획해줘"
"뉴스 큐레이션 앱 MVP 기획해줘"
"기존 앱에 소셜 로그인 추가하는 거 기획해줘"
```

## 공정

1. **Researcher** (spawn 1) — 시장 조사, 경쟁사 분석, 웹 검색
2. **Planner** (spawn 2) — Researcher 결과 기반으로:
   - Phase 1: 가설 수립
   - Phase 2: MVP 스펙 설계
   - Phase 3: 메트릭 설계
   - Phase 4: GTM 설계
   - Phase 5: 자가 검증 (7점 커트라인, 최대 2회 재시도)

## 출력

- `gajae-os/planner/outputs/YYYY-MM-DD-{기능명}.md` — 최종 1-Pager
- `gajae-os/planner/outputs/YYYY-MM-DD-{기능명}-research.md` — 시장 조사 보고서

## 평가 기준

7개 항목 각 10점 만점, **평균 7점 이상**이면 PASS:
- 가설 명확성
- 근거 충분성
- P0 최소성
- 실현 가능성
- 메트릭 측정 가능성
- Go/Stop 기준 명확성
- 리스크 인식

## 파일 구조

```
gajae-os/planner/
├── README.md          ← 이 파일
├── RESEARCHER.md      ← Researcher 에이전트 프롬프트
├── PLANNER.md         ← Planner 에이전트 프롬프트
└── outputs/           ← 결과물 저장
```
