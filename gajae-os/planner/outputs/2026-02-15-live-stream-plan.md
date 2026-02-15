# 📋 PO's 1-Pager: 바이브코딩 라이브스트림 (Vibe Coding Livestream)
> 작성일: 2026-02-15
> 상태: ✅ PASS
> 검증 라운드: 1/3

## 1. Background & Opportunity
- **Context**: 2026년 개발 트렌드는 "AI Pair Programming"의 시각화입니다. 정적인 결과물 공유를 넘어, AI와의 티키타카(상호작용) 과정 자체가 콘텐츠가 되는 시대입니다.
- **Problem**: 기존 방송(YouTube/Twitch)은 코드 에디터 화면 전체를 송출하여, 모바일 시청자나 비개발자가 맥락을 따라가기 어렵습니다. 또한 개발자가 코딩 중일 때 시청자와의 소통이 단절됩니다.
- **Opportunity**: "채팅 로그" 형태의 UI로 AI 대화를 중계하면, 텍스트 가독성이 높아지고 모바일 친화적인 "Vibe"를 전달할 수 있습니다. 이는 가재컴퍼니의 "Build in Public" 철학을 가장 직관적으로 보여주는 장치가 됩니다.

---

## 2. Hypothesis
- **Belief**: "우리는 [AI 대화 로그를 실시간 채팅 UI로 시각화]하면, [방문자]가 [평균 3분 이상 체류하며 '살아있는 회사'라는 인상]을 받을 것이다."
- **Expected Outcome**:
  - 평균 세션 시간(Avg Session Duration) > 3분 (일반 랜딩페이지 대비 3배)
  - 재방문율(Retention) > 20% (방송 알림 시)
- **근거**: Market Research에서 언급된 "AI 도구 활용 능력 전시" 트렌드와 "실시간 맥락 공유"의 니즈. 텍스트 기반 스트리밍은 비디오보다 데이터 소모가 적고 접근성이 높음.

---

## 3. Solution & MVP Spec

### User Flow
1. **진입**: 유저가 `gajae.com` 접속 시, 화면 좌측(데스크탑) 또는 상단(모바일)에 "🔴 LIVE: AI와 대화 중" 배지 확인.
2. **관람**: AI와 개발자의 대화가 카카오톡/슬랙처럼 실시간으로 올라옴.
3. **피드백(Vibe)**: 새 메시지가 도착할 때마다 화면 하단에서 하트/이모지 파티클이 뽀글뽀글 올라옴 (인방 느낌).
4. **정보 탐색**: 우측(또는 하단)의 "회사 소개" 영역을 보며, 이 회사가 어떤 기술로 일하는지 자연스럽게 파악.

### Must-Have (P0) - 2주 내 구현 필수
- [ ] **Firestore Realtime Listener**: `chat_logs` 컬렉션의 최신 50개 메시지 로드 및 `onSnapshot` 연동.
- [ ] **Chat UI Component**: 
  - User(나) vs AI(Bot) 구분 디자인 (말풍선 방향/색상).
  - Markdown 렌더링 (코드 블록 하이라이팅 포함).
- [ ] **Vibe Animation System**: 
  - `onSnapshot` 트리거 시 CSS Keyframe 애니메이션(하트 floating) 자동 실행.
- [ ] **Status Indicator**: 마지막 로그 시간이 5분 이내면 "🔴 LIVE", 아니면 "⚫ OFFLINE (Replay)" 표시.

### Nice-to-Have (P1) - MVP 제외
- 시청자 참여형 리액션 (좋아요 버튼 클릭 시 Firestore 카운트 증가).
- 과거 로그 무한 스크롤 (비용 문제로 MVP 제외).
- 사운드 이펙트 (뉴 메시지 알림음).
- 다크/라이트 모드 토글 (시스템 설정 따름으로 대체).

### Technical Constraint
- **Firestore Cost**: 과도한 읽기 방지를 위해 `limit(50)` 필수. `useEffect` cleanup 확실히 하여 리스너 중복 방지.
- **Next.js SSR/CSR**: 실시간 데이터는 클라이언트 사이드(`useClient`)에서만 처리.

---

## 4. Success Metrics
| 구분 | 지표 | 기준 |
|---|---|---|
| **Primary** | **Avg Session Duration** | **Go: ≥ 3분** (유저가 읽을 거리가 충분한가?) |
| **Counter** | **Firestore Read Usage** | **Stop: ≥ 20k/day** (비용 급증 시 리스너 차단) |
| **Guardrail** | **Page Load Time** | < 1.5s (무거운 애니메이션으로 느려지면 안 됨) |
| **관찰 기간** | 런칭 후 1주 | 1주간 데이터 수집 후 P1 진행 결정 |

---

## 5. Go-to-Market & Operations
- **Aha-Moment**: 유저가 보고 있는 그 순간에 새 코드가 "타닥타닥" 찍히며 하트가 올라오는 순간. "지금 진짜로 일하고 있네?"
- **Manual Process**: 
  - 개발 시작 전 "오늘의 방송 제목"을 Firestore 설정 문서에 수동 입력 (Admin 페이지 개발 안 함).
- **Launch Plan**:
  - Twitter/Threads에 "제 코딩 라이브는 영상이 아닙니다. 텍스트입니다."로 어그로.
  - 개발자 커뮤니티(디스콰이엇, 긱뉴스)에 "Next.js + Firestore로 만든 텍스트 스트리밍" 기술 공유.

---

## 6. Critique Score (Self-Verification)
> *PO 관점에서 냉정하게 평가*

| 항목 | 평가 기준 | 점수 |
|---|---|---|
| **가설 명확성** | "Vibe"라는 추상적 가치를 체류 시간으로 구체화함. | 9/10 |
| **근거 충분성** | 시장 트렌드(Build in Public)와 기술적 이점(텍스트 스트리밍) 결합. | 8/10 |
| **P0 최소성** | 뷰어와 자동 애니메이션만 남기고, 유저 인터랙션(클릭)을 과감히 P1으로 미룸. 적절함. | 9/10 |
| **실현 가능성** | Next.js + Firestore는 이미 익숙한 스택. 2주 내 충분히 가능. | 10/10 |
| **메트릭 측정** | GA4와 Firebase Console로 즉시 확인 가능. | 10/10 |
| **Go/Stop 기준** | 비용(Read Usage)을 명확한 Stop 기준으로 설정하여 리스크 관리. | 9/10 |
| **리스크 인식** | "방송 안 할 때"의 썰렁함을 "Replay 모드"로 방어함. | 8/10 |
| **평균** | **PASS** | **9.0/10** |

### 검증 코멘트
- **승인(PASS)**: 1인 개발자의 리소스를 고려하여 "인터랙션"을 배제하고 "관전(View)"에 집중한 점이 훌륭함.
- **주의사항**: "OFFLINE" 모드일 때 너무 정적으로 보이지 않게, "마지막 방송: N시간 전" 문구를 감성적으로 잘 풀어내야 함. 비용 관리(Firestore limit)만 코드 레벨에서 철저히 하면 문제없음.
