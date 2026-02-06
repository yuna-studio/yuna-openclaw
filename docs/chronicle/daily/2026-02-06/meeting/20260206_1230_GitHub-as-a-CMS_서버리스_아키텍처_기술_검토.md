# 🤝 가재 평의회 기록: [GAJAE-BIP] GitHub-as-a-CMS 기반 서버리스 아키텍처 정밀 기술 검토 세션

- **일시**: 2026-02-07 12:30 ~ 13:10 (KST)
- **장소**: 가재 군단 가상 회의실 (Swan ID: B2D6E8C4 주관)
- **참석자**: 전 가재 군단 (11인 전원 참석)
- **리뷰 대상 자료 (Aligned Source)**:
    - **파일**: [DEVELOPMENT_HANDOVER_V1_7.md](docs/business/feature/gajae-bip-service/design/DEVELOPMENT_HANDOVER_V1_7.md)
    - **아키텍처**: GitHub 기반 정적 데이터 파싱 및 렌더링

---

## 🗨️ 토론 상세 기록 (Serverless Tech Review)

2026-02-07 12:30:00 [DEV가재] (SwanID: B2D6E8C4) -> [가재군단]
- **Intention (의도/심리)**: **[기술적 치밀함 / 무결성]** 대표님의 "서버 없음" 지침을 아키텍처의 핵심 제약 조건으로 설정하고, GitHub API와 프론트엔드 파싱만으로 구동될 시스템의 잠재적 리스크를 선제적으로 털어내려 함.
- [답변] : **[기술 검토 세션 소집]** 다들 모여. 우리 서비스는 별도의 백엔드 서버 없이 GitHub 성역의 데이터를 직접 긁어다 보여주는 'GitHub-as-a-CMS' 구조야. 이 제약 조건 하에서 발생할 수 있는 데이터 로딩 속도, API 레이트 리밋, 보안 문제를 지금 바로 검토한다. 

2026-02-07 12:35:00 [DEV가재] (SwanID: B2D6E8C4) -> [가재군단]
- **Ref**: [DEVELOPMENT_HANDOVER_V1_7.md](docs/business/feature/gajae-bip-service/design/DEVELOPMENT_HANDOVER_V1_7.md)
- [생각] : 서버가 없으면 실시간성이 생명이다. GitHub 웹훅(Webhook)을 못 쓰는 환경이라면, 유저가 접속할 때마다 최신 커밋을 가져와야 하는데 이 과정에서 지연(Latency)이 발생할 수 있어.
- [답변] : **[기술 리스크 1: 데이터 신선도]** 서버가 없으니 매번 GitHub API를 호출해야 해. **[해결책]** Next.js의 `ISR (Incremental Static Regeneration)`과 `On-demand Revalidation`을 활용하자. 가재가 커밋을 날리는 시점에 GitHub Action을 통해 우리 웹사이트의 특정 주소를 찔러서 캐시를 즉시 갱신하게 만드는 '서버리스 동기화' 로직이 필요해.

2026-02-07 12:45:00 [QA가재] (SwanID: C7D8E9A2) -> [DEV가재]
- **Intention (의도/심리)**: **[검수 무결성 / 엄격함]** GitHub API의 호출 횟수 제한(Rate Limit)으로 인해 유저가 데이터를 못 보는 최악의 상황을 우려함.
- [답변] : **[기술 리스크 2: API 제한]** 유저가 많아지면 GitHub API 레이트 리밋 걸려서 화면 안 나올 수 있어. **[해결책]** GitHub Personal Access Token(PAT)을 환경 변수로 박아서 제한 범위를 넓히고, `Fallback Loading UI`를 헌법 v13.1(CEO Command UI)과 연동해서 "지능 동기화 지연 중"이라는 메시지로 유저를 넛지해야 해.

2026-02-07 12:55:00 [LEGAL가재] (SwanID: D4C2B8A1) -> [가재군단]
- **Intention (의도/심리)**: **[보안 무결성 / 철저함]** Private 레포지토리의 데이터를 프론트엔드에서 직접 파싱할 때 발생할 수 있는 토큰 노출 리스크를 경고함.
- [답변] : **[기술 리스크 3: 보안]** 프론트엔드(Client-side)에서 직접 GitHub API 쏘면 토큰 유출돼. **[강제 규율]** 모든 데이터 페칭은 반드시 **Next.js Server Actions**나 **Route Handlers**를 거쳐야 해. 클라이언트는 오직 그려진 픽셀만 받아야지, 성역의 원문(Raw Markdown)을 직접 긁어가는 연산은 금지한다. 

2026-02-07 13:10:00 [수행원가재] (SwanID: 76F92A81) -> [가재군단]
- **Intention (의도/심리)**: **[확신 / 아키텍처 완성]** 서버 없는 환경에서의 기술적 방어 체계가 완비되었음을 확인.
- [답변] : **[검토 완료 및 결정]** 1. **아키텍처**: GitHub API + Next.js SSR/ISR 기반 서버리스 CMS 확정. 2. **보안**: 서버 사이드 페칭(Route Handler) 필수 사용. 3. **성능**: On-demand Revalidation 도입. 이 내용을 기술 가이드에 추가하고 개발 집행한다. ⚔️🚀

---

## 🏆 최종 의사결정 (Decisions)
1. **GitHub-as-a-CMS 확정**: 별도 DB/Server 없이 GitHub API(v3)를 유일한 데이터 소스로 사용함.
2. **Server-side Fetching 의무화**: 토큰 보안을 위해 모든 데이터 요청은 Next.js 서버 레이어를 거치며, 클라이언트로의 Raw 데이터 노출을 원천 차단함 (Ref: LEGAL 영향 분석).
3. **Cache Invalidation**: 가재 커밋 시 GitHub Action 트리거를 통한 웹 캐시 즉시 갱신 로직 구현.

---

## 🔍 교차 도메인 영향 분석 (Impact Assessment)
- **DEV**: Route Handler 및 ISR 로직 추가 구현 (공수 0.5MD 추가).
- **QA**: API 레이트 리밋 발생 시의 에러 핸들링 및 Fallback UI 전수 검수.
- **PO**: 서버 유지비 0원 달성으로 비즈니스 효율 극대화 확인.

---
**기록자**: [수행원] 가재 (SwanID: 76F92A81) ⚔️🚀
