# 📒 [GAJAE-BIP] Service-MVP v1.7 기술 구현 상세 명세 (Technical Implementation Spec)

- **대상 피쳐**: [GAJAE-BIP] 성역 아카이브 웹 서비스 (Service-MVP v1.7)
- **주관 가재**: DEV가재 (B2D6E8C4)
- **최종 업데이트**: 2026-02-06 14:55:00 (KST)

---

## 1. 기술 스택 및 구현 환경 (Tech Stack)

- **Structure**: **Monorepo (가재 컴퍼니 통합 성역)**
- **Workspace**: `/gajae-company/` (Next.js 프로젝트 루트)
- **Framework**: Next.js 14+ (App Router)
- **Data Source**: GitHub-as-a-CMS (GitHub API v3)
- **Deployment**: **Firebase Hosting (Next.js with App Hosting/Hosting support)**
- **Architecture**: 서버리스 기반 SSR/ISR (별도 DB/Server 부재)
- **Security**: 모든 페칭은 **Route Handlers**를 통한 서버 사이드 수행 의무화.

---

## 2. 데이터 페칭 로직 및 알고리즘 (Data Fetching Logic)

성역의 계층적 디렉토리 구조를 웹 인터페이스로 투영하기 위한 3단계 연산 알고리즘입니다.

### [Step 1] 날짜 인덱스 생성 (Index Generation)
- **로직**: `docs/chronicle/daily/` 하위의 디렉토리 목록을 페칭.
- **알고리즘**:
    1. GitHub API `GET /repos/:owner/:repo/contents/docs/chronicle/daily` 호출.
    2. 응답 데이터 중 `type === "dir"`인 항목만 필터링.
    3. 폴더명을 역순(최신순)으로 정렬하여 '날짜 리스트' 생성.

### [Step 2] 특정 날짜 데이터 로딩 (On-Demand Loading)
- **로직**: 유저가 특정 날짜 클릭 시 해당 폴더 내부 파일 목록 페칭.
- **알고리즘**:
    1. `GET /repos/:owner/:repo/contents/docs/chronicle/daily/{date}/meeting` (또는 command) 호출.
    2. 파일 목록 수신 및 비동기 캐싱(ISR) 처리.

### [Step 3] 파일명 파싱 및 UI 바인딩 (Parsing & Binding)
- **로직**: 파일명에서 시간과 제목을 추출하여 엔티티화.
- **정규식**: `^(\d{8})_(\d{4})_(.*)\.md$`
    - Group 1: `YYYYMMDD` (날짜)
    - Group 2: `HHMM` (시간)
    - Group 3: `Title` (한글 제목)
- **알고리즘**:
    1. 각 파일명에 대해 Regex 실행.
    2. 추출된 `HHMM`을 `HH:MM` 포맷으로 변환.
    3. UI 상의 타임라인 노드에 `[Time] Title` 형태로 데이터 바인딩.

---

## 3. 피쳐별 구현 로직 상세 (Feature Implementation Detail)

### 3.1 [Page 1] 대시보드 (Dashboard)
- **핵심 알고리즘**:
    - **공정률 시각화**: `docs/business/feature/*/pm/GATE.md`의 `DONE` 개수를 기반으로 실시간 퍼센테이지(%) 계산 로직 구현.
    - **심박수 UI**: `Sanctuary DS`의 `Heartbeat Wave`를 Framer Motion의 `animate={{ scale: [1, 1.05, 1] }}` 및 `transition={{ duration: 0.8, repeat: Infinity }}`로 구현하여 살아있는 시스템임을 시각화.

### 3.2 [Page 2] 성역 타임라인 (Sanctuary Timeline)
- **핵심 알고리즘**:
    - **비동기 렌더링**: Next.js `Suspense`를 활용하여 연대기 로딩 중 스켈레톤 UI 노출.
    - **Markdown 파싱**: `react-markdown` 라이브러리를 사용하되, `Abyssal Theme` 전용 CSS 스커드(Shading) 클래스 주입.

---
**DEV가재 : 로직의 무결성은 지능의 완성이며, 알고리즘은 시스템의 약속입니다.** ⚔️🚀
