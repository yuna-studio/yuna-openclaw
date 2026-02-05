# 🦞 헬로베베 비즈니스 분석(BA) 설계 (analytics.md)

## 1. Mixpanel 이벤트 로그 모델 (Event Schema)
- **추상화 목표:** 모든 고객 행동을 '퍼널 전환율' 관점에서 정량화한다.

### 핵심 이벤트 명세
| Event Name | Description | Properties |
|:---|:---|:---|
| `view_landing` | 랜딩 페이지 진입 | `referrer`, `device_type` |
| `drag_hero_slider` | Hero 슬라이더 조작 | `duration`, `is_mobile` |
| `click_cta` | "만나러 가기" 클릭 | `location` (Hero/Bottom), `cta_text` |
| `pre_reserve_click`| 스모크 테스트 클릭 | `email_opt_in`, `user_id` |
| `start_payment` | 결제 프로세스 시작 | `package_id`, `price` |
| `complete_conversion`| AI 변환 성공 | `latency_sec`, `retry_count` |

## 2. Retention Tracking
- '결과 확인' 후 SNS 공유 버튼 클릭 여부를 측정하여 CC(Channel Connection) 효율을 분석한다.
