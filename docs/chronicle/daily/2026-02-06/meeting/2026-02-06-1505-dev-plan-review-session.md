# 🤝 가재 평의회 기록: [제 18 차 정기 공정 싱크 및 개발 계획(dev) 정밀 검수 세션]

- **일시**: 2026-02-06 15:05:00 ~ 15:35:00 (KST)
- **장소**: 가재 군단 가상 회의실 (PM가재 주관)
- **참석자**: 전 가재 군단 (11인 전원 참석)
- **리뷰 대상 자료 (Aligned Source)**:
    - **기술 명세**: [technical-implementation-spec-v1-7.md](docs/business/feature/gajae-bip-service/dev/technical-implementation-spec-v1-7.md)
    - **설계도**: [architecture-blueprint-v1-7.md](docs/business/feature/gajae-bip-service/dev/architecture-blueprint-v1-7.md)

---

## 🗨️ 토론 상세 기록 (Dramatic Transparency Log)

2026-02-06 15:05:00 [PM가재] (SwanID: A1D6F4B2) -> [가재군단]
- **Intention (의도/심리)**: **[공정 가속 / 전사 정렬]** 대표님의 명령에 따라 개발(DEV) 도메인의 핵심 계획을 전사적으로 검수하고, 기술 구현(Step 6)의 임계점을 돌파하려 함.
- [생각] : 시스템 정비는 끝났다. 이제는 '실체'다. DEV가 뽑아온 설계도가 비즈니스 목표(PO)와 미학적 기준(UX), 그리고 법적 안전성(LEGAL)을 모두 충족하는지 1px 단위로 뜯어본다.
- [답변] : **[개발 리뷰 세션 소집]** 다들 집중해. 지금부터 [GAJAE-BIP] v1.7 개발 계획 리뷰 들어간다. DEV는 아키텍처와 로직 설명하고, 나머지는 각자 도메인에서 맹점 찾아내. 칭찬은 필요 없다. 결함만 찾아라.

2026-02-06 15:10:00 [DEV가재] (SwanID: B2D6E8C4) -> [가재군단]
- **Ref**: [technical-implementation-spec-v1-7.md](docs/business/feature/gajae-bip-service/dev/technical-implementation-spec-v1-7.md)
- **Intention (의도/심리)**: **[기술적 무결성 증명 / 아키텍처 확신]** Next.js 기반의 클린 아키텍처와 GitHub-as-a-CMS 전략이 기술적으로 얼마나 견고한지 증명함.
- [답변] : **[개발 계획 보고]** 핵심은 3가지다. 1. **모노레포 구조**: `/gajae-company/` 내 Next.js 프로젝트 구축. 2. **3단계 페칭**: 날짜 인덱스 스캔 -> 비동기 로딩 -> Regex 파싱(`^(\d{8})_(\d{4})_(.*)\.md$`). 3. **보안**: Route Handlers로 GitHub 토큰 은폐. 질문 받는다.

2026-02-06 15:15:00 [PO가재] (SwanID: 1D4B9C2E) -> [DEV가재]
- **Intention (의도/심리)**: **[비즈니스 연속성 검증]** 기술적 화려함보다 데이터의 정확성과 비즈니스 지표(공정률)가 어떻게 연동되는지 날카롭게 질문함.
- [답변] : **[날카로운 질문]** DEV, 너 아까 정규식으로 파일명 파싱한다고 했지? 만약 파일명 규격이 어긋난 '예외 파일'이 있으면 어떻게 처리해? 그리고 `GATE.md`의 `DONE` 태그를 카운팅해서 공정률 계산한다고 했는데, 태그 오타 나면 서비스 전체 공정률 왜곡되는 거 아냐?

2026-02-06 15:20:00 [UX가재] (SwanID: F1A93D72) -> [DEV가재]
- **Intention (의도/심리)**: **[미학적 구현 가능성 체크]** 설계한 '심연'의 박동 UI가 실제 렌더링 성능에 미치는 영향을 우려함.
- [답변] : **[미학적 검수]** Framer Motion으로 `Heartbeat Wave` 구현한다고 했는데, 데이터 페칭(SSR) 시점에 애니메이션이 끊기면 안 돼. **[요구사항]** 로딩 상태(`Suspense`)에서도 박동 UI는 60fps 유지되도록 클라이언트 측 최적화 보장해라.

2026-02-06 15:25:00 [QA가재] (SwanID: Q9A2D6C4) -> [DEV가재]
- **Intention (의도/심리)**: **[안정성 및 부하 테스트 요구]** 서버리스 환경에서의 API Rate Limit 리스크를 집요하게 파고듦.
- [답변] : **[안정성 검수]** GitHub API 시간당 5,000회 제한이야. 우리 유저 갑자기 몰리면 서비스 터져. ISR 캐싱 주기 어떻게 설정할 거야? 1분? 5분? 데이터 업데이트 실시간성 포기할 거야?

2026-02-06 15:35:00 [PM가재] (SwanID: A1D6F4B2) -> [가재군단]
- **Intention (의도/심리)**: **[리뷰 요약 및 구현 승인 요청]** 모든 비판을 수렴하여 최종 개발 가이드라인을 확정함.
- [답변] : **[리뷰 종료 및 의결]** 1. **예외 처리**: Regex 미매칭 시 'Invalid Asset'으로 분류하고 로그 박제. 2. **성능**: 박동 UI는 `Shared Layout`에 배치하여 페이지 전환 시에도 유지. 3. **안정성**: ISR 1분 주기 + `on-demand revalidation` API 구축으로 실시간성 확보. **[결론]** 기술 설계 무결함 판정. 대표님께 승인 요청하고 바로 `src/` 코딩 시작한다.

---

## 🏆 최종 의결 사항 (Decisions)
1. **Error-Resilient Parsing**: 정규식 파싱 실패 시의 Fallback 로직 기술 명세에 추가.
2. **Persistent Heartbeat**: 미학적 심박 UI의 프레임 저하 방지를 위한 클라이언트 측 레이아웃 고정.
3. **Hybrid Caching Strategy**: ISR과 On-demand Revalidation을 병행하여 GitHub API Rate Limit 극복.

---
**보고자**: [PM] 가재 (SwanID: A1D6F4B2) ⚔️🚀
