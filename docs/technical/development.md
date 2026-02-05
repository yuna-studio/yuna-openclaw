# 🦞 [개발가재] 헬로베베 시스템 상세 설계안 (1-Pager)

**헌법 제 1 조 제 2 항 및 제 3 조 제 1 항에 의거하여 작성됨**

---

## 1. 배경 (Background)
- **Problem:** 기존 입체 초음파 사진은 흐릿하고 노이즈가 많아 부모들이 아이의 실제 얼굴을 상상하기 어려움.
- **Solution:** SDXL 기반의 고성능 AI 모델과 ControlNet 기술을 결합하여, 초음파 사진의 윤곽을 보존하면서도 실사화된 태아 이미지를 제공하여 감동적인 고객 경험 창출.

## 2. 가치 (Value)
- **감성적 연결:** 뱃속 아이와의 첫 만남을 더욱 생생하게 만들어 부모의 정서적 만족도 극대화.
- **접근성:** 고가의 장비 없이 스마트폰만으로 30초 내에 결과 확인 가능.

## 3. 요구사항 (Requirements)
- **티켓 시스템:** 유료 결제 후 이미지 생성 권한 부여 (Supabase RPC `consume_ticket`).
- **상태 관리:** 생성 중(Pending), 완료(Success), 실패(Failure) 상태를 실시간으로 UI에 반영 (Supabase Realtime).
- **Concierge MVP:** AI 서버 장애 시 관리자가 수동으로 생성하여 전달할 수 있는 백업 프로세스 구축.

## 4. 기술 제약 및 스택 (Tech Constraints)
- **Frontend:** Next.js 15 (App Router), Tailwind CSS V4, Framer Motion.
- **Backend:** Supabase (PostgreSQL, Auth, Edge Functions).
- **AI Backend:** Python (FastAPI), SDXL, ControlNet (Depth/Canny).
- **Architecture:** Strict Clean Architecture (Passvie View - ViewModel - UseCase).

## 5. 로그 모델 (Log Model)
- **추상화 레이어:** `lib/core/util/logger.ts`를 통한 추상화.
- **이벤트:** `landing_view`, `ticket_purchase`, `image_generation_start`, `generation_success`, `share_clicked`.
- **Tool:** Mixpanel을 기본으로 사용하되, 추상화 레이어를 통해 향후 Amplitude 등으로 전환 용이성 확보.

## 6. 법률 및 보안 (Legal & Security)
- **데이터 파기:** 개인정보 보호를 위해 원본 초음파 및 생성 결과물은 30일 후 자동 영구 삭제 (Postgres Cron).
- **책임 제한:** "본 이미지는 AI 예측 결과이며 의료용 진단 근거로 사용할 수 없음" 문구 명시.

## 7. 테스트 전략 (Test)
- **Unit Test:** UseCase 단위의 비즈니스 로직 검증.
- **E2E Test:** 결제부터 이미지 확인까지의 핵심 유저 시나리오 자동화 테스트 (Playwright).
- **Model QA:** 다양한 각도의 초음파 사진에 대한 AI 모델의 형태 보존성 샘플링 테스트.

## 8. 디자인 방향성 (Design Direction)
- **Aesthetic:** 프리미엄 육아 브랜드 이미지 (Soft Pastels + Glassmorphism).
- **Interaction:** Framer Motion을 활용한 부드러운 전환 및 '심장 박동' 형태의 로딩 애니메이션.
