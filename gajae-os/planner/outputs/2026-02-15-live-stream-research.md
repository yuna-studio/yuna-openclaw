# Market Research: 바이브코딩 라이브스트림 웹사이트 (Vibe Coding Livestream)
> 조사일: 2026-02-15

## 1. 시장 현황 (Market Context)
**"Build in Public"의 진화: AI와의 공생(Symbiosis) 전시**
- **시장 트렌드**: 2024~2025년을 거치며 'Build in Public'은 단순한 개발 과정 공유를 넘어, **"AI 도구(Cursor, Copilot 등)를 얼마나 능숙하게 다루는지"**를 보여주는 콘텐츠로 진화했습니다.
- **성장성**: 라이브 스트리밍 시장은 지속적으로 성장 중이며(Kick 등의 신규 플랫폼 부상), 특히 기술/개발 카테고리에서는 "AI Pair Programming"이 주요 콘텐츠로 자리 잡았습니다. Cursor AI 등을 활용한 코딩 방송이 YouTube와 Twitch에서 인기 콘텐츠로 부상했습니다.
- **타겟 유저**:
    - **크리에이터(개발자)**: 자신의 프로덕트 제작 과정을 보여주며 팬덤을 모으고 싶은 1인 창업가.
    - **시청자**: 최신 AI 코딩 워크플로우를 배우고 싶거나, 실시간으로 프로젝트가 완성되는 과정을 즐기는 예비 창업가 및 개발자.

## 2. 경쟁사 및 유사 서비스 분석
| 서비스명 | 핵심 기능 | 강점 | 약점 | 비고 |
|---|---|---|---|---|
| **Twitch (Dev Category)** | 실시간 코딩 방송, 채팅, 후원 | 압도적인 유저 베이스, 강력한 커뮤니티 기능(이모티콘, 레이드) | 개발 방송은 'Game'에 비해 니치 마켓, 신규 유입이 어려움 | 가장 대중적인 레퍼런스 |
| **YouTube Live** | 고화질 방송, VOD 자동 저장 | 검색 유입이 용이함, 긴 호흡의 콘텐츠에 적합 | 실시간 상호작용(Latency)이 Twitch보다 다소 느릴 수 있음 | "Cursor AI Tutorial" 등의 검색어와 연계 강력 |
| **Cursor AI (Tool)** | AI 기반 코드 에디터 (자체 방송 기능 없음) | 현재 가장 핫한 AI 코딩 도구, 유저들이 자발적으로 방송 콘텐츠로 활용 | 방송 플랫폼이 아닌 '도구'임 | 본 기획의 '핵심 콘텐츠'가 되는 도구 |
| **Indie Hackers** | 텍스트/포럼 기반 Build in Public | 진지한 피드백, 창업가 커뮤니티 | '실시간성'과 '엔터테인먼트' 요소 부족 | 커뮤니티 피드백의 원천 |

**특이사항**: "바이브코딩"처럼 **'AI와의 대화 로그 자체'를 메인 콘텐츠로 시각화**하여 스트리밍하는 전용 웹사이트 형태의 직접적인 경쟁 서비스는 뚜렷하지 않음. 기존에는 방송 송출 화면(OBS)의 일부로 채팅창을 보여주는 방식이 주류임.

## 3. 유저 Pain Point
- **방송 세팅의 복잡함 (Streamer)**: 코딩 화면, AI 채팅창, 시청자 채팅창, 캠 화면 등을 OBS로 구성하는 것이 번거로움. 특히 "AI와의 대화" 텍스트 가독성을 높이기 위한 레이아웃 설정이 어려움.
- **맥락 파악의 어려움 (Viewer)**: 중간에 들어온 시청자는 현재 AI에게 무엇을 시켰는지, 어떤 에러를 해결 중인지 파악하기 어려움 (기존 방송은 긴 코드를 보여주기 때문).
- **상호작용의 부재 (Interaction)**: 개발자가 코딩에 집중하면 시청자 채팅을 놓치기 쉬움. "조용한 방송"이 되기 십상.

## 4. 기회 영역 (Opportunity)
- **"AI 대화의 엔터테인먼트화"**: 복잡한 코드 에디터 화면 대신, **"AI와 티키타카하는 채팅 로그"**를 메인으로 보여주어 비개발자도 맥락을 이해하기 쉽게 시각화.
- **인방 감성의 Gamification**:
    - AI가 코드를 짤 때마다 화면에 **하트/리액션 애니메이션**이 터지게 하여(기획안의 '인방 느낌'), 정적인 코딩 방송에 시각적 쾌감 부여.
    - 시청자가 클릭으로 하트를 보내면 개발자 화면에도 띄워주는 양방향 소통.
- **실시간 맥락 공유 (Sync)**: Firestore 연동을 통해 OBS 송출 화면이 아닌, **웹사이트 자체에서 텍스트를 렌더링**하면 시청자가 직접 스크롤을 올려 이전 대화를 볼 수 있음 (기존 영상 스트리밍의 한계 극복).

## 참고 소스
- **Trends**: [The State of Live Coding 2025](https://creativecodingtech.com), [Live Streaming Trends 2025 (Stream Hatchet)](https://www.streamhatchet.com)
- **UI/UX**: [Twitch Chat Overlay CSS Guide](https://soundalerts.com/blog/customized-chat-overlays-with-css-for-twitch-guide), [Nutty Multichat Overlay](https://nutty.gg)
- **Community**: [Reddit r/IndieHackers - Build in Public Feedback](https://www.reddit.com/r/indiehackers/)
- **Content**: [YouTube @cursor_ai](https://www.youtube.com/@cursor_ai) (Cursor AI 활용 사례)
