# TASKS_7DAY.md - 헬로베베 웹 런칭 최종 로드맵 (Next.js)

## 🎯 목표: 2026년 2월 11일(화) 런칭 (MVP: 실사 3장 티켓 시스템)

### [Day 1: 2/4] 인프라 및 기반 구축 (오늘)
- [x] Next.js 15 + Tailwind V4 + Supabase 환경 설정
- [x] Strict Clean Architecture 폴더 구조 세팅
- [ ] Supabase Auth (Google/Apple) 연동 및 `profiles` 스키마 정의

### [Day 2: 2/5] 퍼널 UI 및 인증 (Mock 전력 질주 - 오늘)
- [x] Mock Auth (Google/Apple) 연동 및 가상 `profiles` 스키마 연결
- [x] 5단계 설득 랜딩 페이지 (Mock 데이터 연결 및 UX 플로우 완성)
- [x] Mock 티켓(1매) 자동 지급 로직 구현 완료
- [x] PG 결제 모달 Mockup (성공 시나리오 강제 연결)
- [🏗️] 전 페이지 UI/UX 폴리싱 및 모바일 반응형 선행 작업 (Day 6에서 당겨옴)

### [Day 3: 2/6] 실전 연동 및 데이터 아키텍처 (인프라 확보 시 즉시 가동)
- [ ] 티켓 잔액 조회 및 소진 RPC (`consume_ticket`) 구현
- [ ] PG(PortOne/Toss) 결제 모달 연동 및 결제 성공 시 티켓 충전
- [ ] 티켓 부족 시 결제 유도 팝업 UX 처리

### [Day 4: 2/7] AI 프로세싱 레이어
- [ ] 초음파 사진 업로드 UI 및 Supabase Storage 연동
- [ ] AI 백엔드(Python API) 연동 및 실시간 상태(Realtime) 트래킹
- [ ] '생명의 숨결' 감성 대기 화면 (애니메이션 + 텍스트) 구현

### [Day 5: 2/8] 결과 갤러리 및 보관
- [ ] 생성 완료된 이미지 3종(정면, 미소, 수면) 갤러리 UI
- [ ] Before/After 슬라이더 비교 컴포넌트 구현
- [ ] 고해상도 이미지 다운로드 및 공유(인스타 템플릿) 기능

### [Day 6: 2/9] 폴리싱 및 데이터 보안
- [ ] 개인정보처리방침/이용약관 동의 프로세스 최종 점검
- [ ] 24시간/30일 데이터 자동 파기 로직(Cron) 검증
- [ ] 모바일 반응형 최적화 및 Lighthouse 성능 점검

### [Day 7: 2/10] 최종 QA 및 배포
- [ ] Vercel/Fly.io 프로덕션 배포 및 도메인 연결
- [ ] 전수 QA (결제 -> 생성 -> 다운로드 전체 흐름)
- [ ] 마케팅 준비 (인스타 홍보용 이미지 생성)

---
**[Action Item: 기획가재]**
- 매일 오전 10시 각 가재 진척도 체크 및 `monitor_log.md` 기록
- 기술적 병목(결제/AI 연동) 발생 시 즉시 대안 마련
