# 🏛️ [기획가재] 1-Pager: (3) 결제 (Payment)

**헌법 제 1조 제 1항 및 제 6조 제 2항에 의거하여 작성함.**

---

## 1. 배경 (Background)
- **Insight:** 유저는 분석 결과를 빨리 보고 싶어 하지만, 결제 단계에서 심리적 저항을 느낌.
- **Strategy:** "단 한 번의 커피값으로 만나는 미래"라는 프레이밍과 압도적인 결제 편의성 제공.

## 2. 가치 (Value)
- **사용자 가치:** "기다림 없는 즉각적인 호기심 해결 및 고품질 분석 리포트 소유권 획득."
- **비즈니스 가치:** 서비스의 유일한 수익 모델로서 LTV(Lifetime Value) 시작점.

## 3. 상세 요구사항 (Requirements & Wireframe)
### 3.1. 와이어프레임 (Wireframe Text)
- **[Order Summary]** 상단에 업로드한 사진 썸네일과 "우리 아이 AI 분석권 1회" 텍스트.
- **[Price Display]** 취소선이 그어진 정가(₩9,900)와 강조된 할인가(₩4,900) "오픈 기념 50% 할인 중!".
- **[Benefit Icons]** 결제 버튼 위에 "10분 내 분석 완료", "평생 소장 가능", "100% 환불 보장" 아이콘 배치.
- **[Payment List]** 
  - 간편결제 영역: 카카오페이, 네이버페이, 토스페이 큰 버튼.
  - 기타결제 영역: 일반 신용카드 (Dropdown/List).
- **[Sticky CTA]** 하단 고정 "₩4,900 결제하기" 버튼. 누를 때 가벼운 진동(Haptic) 효과.

### 3.2. 기능 요구사항
- **PG Integration:** 포트원(PortOne) SDK 연동을 통한 통합 결제창 호출.
- **Transaction Safety:** 결제 시작 시 서버에 'Pending' 주문 생성, 완료 후 Webhook을 통한 'Success' 확정.
- **Coupon Logic:** MVP에서는 생략하나, 확장 가능하도록 주문 테이블 설계.

## 4. 기술 제약 (Technical Constraints) - [개발가재] 시뮬레이션
- **Webhook Reliability:** 유저가 결제 완료 후 창을 바로 닫아도 서버에서 결제 완료 처리가 누락되지 않도록 Webhook 재시도 로직(Idempotency) 필수.
- **Mobile WebView:** 앱 내 웹뷰 결제 시 팝업 차단 및 딥링크(앱 호출) 처리 예외 사항 체크.

## 5. 로그 모델 (Log Model) - [분석가재] 시뮬레이션
- `payment_checkout_view`: 결제 화면 진입.
- `payment_method_selected`: 선호하는 결제 수단 추적.
- `payment_success_total`: 최종 전환율 측정.
- `payment_failed_error`: 실패 원인(한도초과, 단순변심 등) 분석.

## 6. 법률 (Legal) - [법률가재] 시뮬레이션
- **Refund Policy:** "디지털 상품 특성상 분석이 시작된 이후에는 청약철회가 제한됨"을 결제 버튼 직전 필수 체크박스로 배치.
- **VAT:** 모든 표시 가격은 부가세 포함임을 명시하여 가격 혼동 방지.

## 7. 테스트 (Test) - [테스트가재] 시뮬레이션
- **Scenario:** 결제 도중 브라우저 강제 종료 시 주문 상태 정합성 확인.
- **Test ID:** 포트원 테스트 모드를 활용한 실제 카드 승인 프로세스 전수 검사.

## 8. 디자인 방향성 (Design Direction) - [디자인가재] 시뮬레이션
- **Confidence UI:** 결제 버튼 주변에 '보안 인증' 마크나 'Safe Payment' 뱃지를 배치하여 심리적 안심 부여.
- **Color:** 버튼 컬러는 신뢰감을 주면서도 시선을 끄는 'Vivid Blue' 또는 'Primary Pink' 권장.
