# Market Research: Vibe Coding Livestream Website
> 조사일: 2026-02-15

## 1. Context (시장 맥락) — 정량 데이터 포함

### 1.1 글로벌 개발자 및 AI 도구 채택 현황
- **총 개발자 수 (TAM):** 2024년 기준 전 세계 소프트웨어 개발자 수는 약 **2,870만 명**으로 추산됩니다 (Statista).
- **AI 도구 확산 (Trend):** 2025 Stack Overflow Developer Survey에 따르면, 개발자의 **84%**가 개발 과정에서 AI 도구를 사용하고 있으며, **47.1%**는 매일 사용합니다. 이는 AI와 코딩이 결합된 콘텐츠의 잠재 수요가 폭발적으로 증가하고 있음을 시사합니다.
- **학습 및 커뮤니티 니즈:** 코딩을 배우는 사람들의 **60.5%**가 커뮤니티 소통을 위해 YouTube를 사용하며, 젊은 개발자(18-24세)의 **37%**가 "사람과의 채팅(Chat with people)" 형태의 인터랙티브 콘텐츠를 선호합니다.

### 1.2 라이브 코딩 스트리밍 시장
- **Twitch 'Software & Game Development' 카테고리 (최근 30일 데이터):**
  - **시청 시간:** 120만 시간 (전월 대비 +17.3% 성장)
  - **평균 시청자 수:** 1,600명 (전월 대비 +17.3% 성장)
  - **활동 스트리머:** 6,600명 (전월 대비 +5.5% 성장)
  - **Source:** SullyGnome (2026.01.15 ~ 2026.02.14 기준)
- **해석:** 틈새 시장이지만 꾸준히 성장 중이며, 특히 시청자 참여형(채팅, 상호작용) 콘텐츠에 대한 니즈가 확인됩니다.

## 2. Problem Statement — 수치 근거 포함

### 2.1 기존 방송 송출(OBS)의 비효율성
- **높은 진입 장벽:** OBS Studio를 원활하게 구동하기 위해서는 최소 Quad-core CPU와 듀얼 모니터 환경이 권장됩니다. (단일 모니터에서는 채팅창이 코드를 가리는 치명적 UX 문제 발생).
- **리소스 점유율 문제:** 브라우저 소스(Browser Source)와 캡처 기능을 동시에 사용할 경우, 저사양 노트북(MacBook Air 기본형 등)에서는 CPU 점유율이 20~30% 이상 상승하여 IDE(VS Code)와 Docker 실행 시 **입력 지연(Latency)**을 유발할 수 있습니다.
- **AI 상호작용의 부재:** 기존 OBS 방송은 "시청자 채팅"만 화면에 띄울 뿐, **AI와의 페어 프로그래밍 대화**를 시각적으로 매력적으로 보여주는 전용 템플릿이나 기능이 전무합니다.

### 2.2 'Build in Public'의 어려움
- 개발 과정을 공유하고 싶지만, "방송 세팅"에 드는 시간이 코딩 시간보다 길어지는 주객전도 현상 발생.
- 1인 개발자는 "코딩하랴, 채팅 읽으랴, OBS 확인하랴" 멀티태스킹 부하가 심각함.

## 3. Competitor Benchmark (경쟁사 분석)

| 서비스명 | 핵심 기능 | 강점 (Pros) | 약점 (Cons) | 가격 |
|---|---|---|---|---|
| **Twitch + OBS** | 범용 라이브 스트리밍, 강력한 오버레이 커스터마이징 | 압도적인 트래픽, 수익화 도구(구독/비트) 완비 | **세팅 복잡도 최상**, 리소스 과다 소모, 코딩 특화 기능 부재 | 무료 (SW) |
| **Discord (화면공유)** | 저지연 화면 공유, 음성 채팅 | **커뮤니티 결합성 우수**, 설치 불필요(웹) | 불특정 다수 노출(Discovery) 기능 없음, 방송 다시보기(VOD) 미지원 | 무료 (Nitro 유료) |
| **YouTube Live** | 고화질 송출, 강력한 VOD 아카이빙 | 검색 유입 용이, 영상 수명 김 | 실시간 소통의 맛(Latency)이 떨어짐, OBS 필수 | 무료 |
| **Vibe Coding (자사)** | **Web-based AI Chat Overlay**, 0-Setup Streaming | **설치 불필요**, IDE+채팅 통합 UI, AI 대화 시각화 | 트래픽(유입) 자체 해결 필요, 초기 기능 제한 | Freemium (예정) |

## 4. 우리만의 Edge (차별화 포인트)

1.  **Zero-Setup, Just Code:** OBS 설치, 장면 구성, 오디오 믹싱 없이 웹사이트 접속만으로 "있어 보이는" 코딩 방송 화면 구현.
2.  **AI Native Experience:** 단순 채팅이 아니라, **"AI(LLM)와 개발자가 대화하며 코딩하는 과정"** 자체가 콘텐츠가 되도록 시각화 (인방 감성 리액션 + AI 답변의 말풍선 애니메이션).
3.  **Chat Logs as Content:** 방송이 끝나면 휘발되는 영상과 달리, Firestore에 저장된 **Chat Logs**가 그 자체로 기술 블로그 포스트나 튜토리얼이 되는 "One Source Multi Use" 구조.
4.  **Low Resource:** 브라우저 기반 렌더링으로, 로컬 머신의 리소스를 방송 송출(인코딩)에 낭비하지 않음 (WebRTC 활용 시).

## 5. TAM/SAM/Early Adopter 추산

### TAM (Total Addressable Market)
- **전 세계 소프트웨어 개발자:** 약 **2,870만 명** (Statista, 2024)
- 이들 중 자신의 지식을 공유하거나 포트폴리오를 알리고 싶은 잠재적 크리에이터.

### SAM (Serviceable Available Market)
- **AI 도구를 적극적으로 사용하는 개발자:** 2,870만 명 × 47% (매일 AI 사용) ≈ **1,350만 명**
- 이들은 이미 AI와의 대화에 익숙하며, 이를 공유하는 것에 거부감이 낮음.

### SOM (Serviceable Obtainable Market) / Early Adopter
- **'Build in Public' 트렌드에 관심 있는 1인 개발자 및 인디 해커:**
- 추산 근거:
  - Product Hunt 일일 활성 메이커 수
  - Twitter/X의 #buildinpublic 해시태그 활성 유저 군 (약 5~10만 명 추산)
  - Twitch 'Software & Game Dev' 활성 스트리머 (약 6,600명)
- **초기 타겟:** 약 **10,000명** (전 세계 인디 해커 및 코딩 스트리머의 상위 10~20%)
- **수익화 가능성:** 이들 중 5%가 월 $5 구독 시 = 월 $2,500 (MRR) 달성 가능.

## 참고 소스
- [SullyGnome - Twitch Statistics (Software & Game Development)](https://sullygnome.com/game/Software_and_Game_Development)
- [Stack Overflow Developer Survey 2025](https://survey.stackoverflow.co/2025/)
- [Statista - Global Developer Population](https://www.statista.com/statistics/627312/worldwide-developer-population/)
- [OBS Studio System Requirements](https://github.com/obsproject/obs-studio/wiki/system-requirements)
