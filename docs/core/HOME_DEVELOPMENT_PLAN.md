# BIP Home 개발 기획서 & 체크리스트

> 대상: `bip` 홈 (`/`)
> 목적: 홈 메시지/콘텐츠 구조를 명확히 하고, 진행 상태를 체크리스트로 관리
> 업데이트: 2026-02-19

## 1) 목표

- 방문자가 5초 내에 이해하게 만들기
  - 무엇을 하는 팀인지
  - 어떤 결과물을 만들었는지
  - 어떤 기록(로그/블로그)을 남기는지
- 홈 카피 톤을 통일
  - 과장/밈 과다 지양
  - 신뢰 + 공개성 + 실행감 강조

## 2) 섹션 구조 (현재 기준)

1. Hero
2. RPG Dialogue (실시간 대화)
3. Live Metrics
4. How We Work
5. Org Chart
6. Project Board
7. Blog Board

## 3) 카피/브랜딩 체크리스트

### Hero
- [x] 헤드라인 세련화
  - `바이브 코딩, 만드는 전 과정을 기록합니다.`
- [x] 서브카피 정리
  - `아이디어부터 배포 후 개선까지, 의사결정과 시행착오를 투명하게 남깁니다.`
- [ ] 모바일 1~2줄 가독성 최종 점검 (실기기)

### Project 섹션
- [x] 섹션 타이틀 워딩 정리
  - `우리가 실제로 만든 결과물.`
- [x] 서브카피 정리
  - `기획부터 배포까지, 전 과정을 공개합니다.`
- [ ] 카드 내 설명 길이 기준(최대 글자수) 확정

### Blog 섹션
- [x] 섹션명 확정
  - `낭만코딩 로그`
- [x] 홈 노출 전략 확정
  - 리스트 노출 없이 **CTA-only** 섹션으로 운영
- [x] 서브카피 확정
  - `매일의 개발 기록에서, 다음 기능의 단서를 찾습니다.`
- [x] CTA 문구 확정
  - `개발 로그 보러가기 →`
- [x] 퍼널 관점 명시
  - 블로그는 SEO 유입 랜딩, 홈/라이브/문서로 재이동 유도

## 4) UX 체크리스트 (홈)

- [x] 홈 블로그 CTA 이벤트 분리
  - 신규: `click_home_blog_cta`
- [x] 블로그 → 홈/라이브/문서 이동 이벤트 분리
  - `click_blog_to_home`, `click_blog_to_live`, `click_blog_to_docs`
- [ ] 프로젝트 카드 확장 상태 유지(새로고침/복귀 시) 정책 결정
- [ ] 섹션 간 간격/타이포 스케일 모바일 최종 다듬기
- [ ] 접근성 점검
  - 버튼/링크 라벨
  - 색 대비

## 5) 운영 체크리스트

- [ ] 변경 시 아래 항목 동시 확인
  - BIP 홈 반영
  - HQ 블로그/문서 관리 노출 영향
  - 퍼널 이벤트 영향 (`view_home`, `click_home_blog_cta`, `click_blog_to_home`, `click_blog_to_live`, `click_blog_to_docs`, `expand_home_project`)
- [ ] 배포 후 스모크 테스트 템플릿 만들기
  - Hero
  - 프로젝트 열기/이동
  - 블로그 목록/상세 이동

## 6) 다음 액션 (우선순위)

1. [ ] 모바일 실기기 카피 가독성 최종 점검
2. [ ] 블로그 페이지 상단/사이드바 CTA 클릭률 점검
3. [ ] 홈→블로그 CTA 클릭률 기준치 정의
4. [ ] How We Work / Footer 카피 톤 동일화

---

## 변경 로그

- 2026-02-19: 홈 카피 1차 워싱 반영
  - Hero / Project / Blog 섹션 문구 업데이트
  - 파일: `bip/src/app/page.tsx`, `bip/src/components/home/project-board.tsx`, `bip/src/components/home/blog-board.tsx`
- 2026-02-19: 블로그 홈 섹션 CTA-only 전환 + 블로그 내 재이동 링크 강화
  - 홈 BlogBoard에서 카드 리스트 제거, CTA 단일화
  - 블로그 페이지에 홈/라이브/문서 이동 CTA 추가 및 이벤트 분리
  - 파일: `bip/src/components/home/blog-board.tsx`, `bip/src/app/blog/page.tsx`
