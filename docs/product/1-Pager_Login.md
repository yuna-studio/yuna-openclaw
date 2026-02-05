# 🏛️ [기획가재] 1-Pager: (1) 로그인 (Login)

**헌법 제 1조 제 1항 및 제 6조 제 2항에 의거하여 작성함.**

---

## 1. 배경 (Background)
- **Pain Point:** 초기 진입 시 복잡한 가입 절차는 40% 이상의 이탈률을 유발함.
- **Context:** 'Hello Bebe'는 감성적인 첫인상이 중요하며, 분석 데이터의 영구 저장을 위해 '나'라는 주체 확립이 필수적임.

## 2. 가치 (Value)
- **사용자 가치:** "단 3초 만에 내 아이의 분석 데이터를 안전하게 보관할 수 있는 개인 공간 확보."
- **비즈니스 가치:** 유저 식별을 통한 리텐션 관리 및 유료 결제 데이터 연결의 교두보.

## 3. 상세 요구사항 (Requirements & Wireframe)
### 3.1. 와이어프레임 (Wireframe Text)
- **[Layer 1: Hero]** 화면 상단 40% 영역. 부드러운 구름이 움직이는 파스텔톤 배경 위로 "세상에서 가장 설레는 만남, Hello Bebe" 타이포그래피 배치.
- **[Layer 2: Graphic]** 중앙에 아기 신발이나 젖병 형태의 감성 일러스트 (Lottie 애니메이션: 숨쉬듯 천천히 커졌다 작아짐).
- **[Layer 3: Social Buttons]** 
  - `Btn_Kakao`: #FEE500 배경, "카카오로 3초 만에 시작하기".
  - `Btn_Apple`: #FFFFFF(White) 또는 #000000(Black) 배경, "Apple로 계속하기".
  - 각 버튼은 누를 때 0.95배로 작아지는 Scale 인터랙션 필수.
- **[Layer 4: Footer]** 하단 10% 영역. "시작 시 [이용약관] 및 [개인정보처리방침]에 동의하게 됩니다." (회색 12px 폰트).

### 3.2. 기능 요구사항
- **OAuth Integration:** Kakao, Apple 로그인 API 연동.
- **User Provisioning:** 최초 로그인 시 서버 DB에 유저 레코드 생성 및 `user_id` 발급.
- **Session Management:** JWT 기반 토큰 발급 및 클라이언트 보안 저장 (HttpOnly).

## 4. 기술 제약 (Technical Constraints) - [개발가재] 시뮬레이션
- **Security:** Apple 로그인 시 `Client Secret` 생성을 위한 `.p8` 키 관리 및 도메인 검증 필수.
- **SSR Handling:** 로그인 직후 `Redirect` 시 Next.js Middleware에서 세션 체크 병목 없도록 설계.

## 5. 로그 모델 (Log Model) - [분석가재] 시뮬레이션
- `enter_login_page`: 진입 시점.
- `click_auth_provider`: 어떤 버튼을 눌렀는가? (property: `provider`).
- `auth_success`: 로그인 성공 시 소요 시간(ms) 측정.
- `auth_abandon`: 소셜 창 띄운 후 60초 내 미완료 시 이탈 간주.

## 6. 법률 (Legal) - [법률가재] 시뮬레이션
- **Privacy:** 카카오/애플로부터 이메일 외 추가 정보 수집 시 반드시 '선택 동의' 처리.
- **Compliance:** 회원 탈퇴 시 모든 개인정보를 즉시 파기하거나 익명화 처리하는 로직 예약 필요.

## 7. 테스트 (Test) - [테스트가재] 시뮬레이션
- **Scenario:** 네트워크 불안정 시 소셜 팝업 호출 실패 대응 확인.
- **Edge Case:** 이미 가입된 이메일이 다른 Provider로 재진입 시 계정 통합 또는 별도 계정 생성 가이드 확인.

## 8. 디자인 방향성 (Design Direction) - [디자인가재] 시뮬레이션
- **Tone & Manner:** "Warm Ivory & Soft Pink". 산부인과/조리원 대기실의 평온함을 UI로 재현.
- **Typography:** 본문은 고딕(Pretendard), 제목은 감성적인 명조 계열(나눔명조 등) 혼용 권장.
