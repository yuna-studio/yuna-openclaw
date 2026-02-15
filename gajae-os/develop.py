#!/usr/bin/env python3
"""
🦞 Gajae Developer — Phase B: 구현 + 18단계 검수 파이프라인

설계 문서(노션 URL) → 코드 구현 → 18단계 검수 → 커밋 + PR

공정:
  📖 설계문서 읽기
  → [1] 구현 계획 수립                    → 탐정
  → [2] 계획 검토                         → 판사
  → [3] 검토 재검토                       → 판사
  → [4] 과도함 검토 (오버엔지니어링 방지)   → 판사
  → [5] 구현 (코드 작성)                  → 탐정 (exec)
  → [6] 목적 부합 검토                    → 판사
  → [7] 버그/크리티컬/보안 검토            → 판사
  → [8] 개선 내용 검토                    → 판사
  → [9] 함수/파일 분리                    → 탐정 (exec)
  → [10] 기존 코드 재사용/통합 검토        → 판사
  → [11] 사이드이펙트 확인                 → 판사
  → [12] 전체 변경사항 재검토              → 판사
  → [13] 불필요 코드 정리                  → 탐정 (exec)
  → [14] 코드 품질 검토                   → 판사
  → [15] UX 흐름 검토                    → 판사
  → [16] 연쇄 영향 반복 검토              → 판사
  → [17] 배포 퀄리티 최종 검토             → 판사
  → [18] 커밋 + PR                       → 탐정 (exec)

Usage:
  python3 graph.py run "노션_설계문서_URL" "기술환경"
  python3 graph.py status RUN_ID
"""

import os
import re
import json
import subprocess
from datetime import datetime
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

import sys
from notion_upload import read_page_blocks


# ── Config ──────────────────────────────────────────────

# (state persistence removed)
PROJECT_DIR = os.path.expanduser("~/.openclaw/workspace/bip")
MAX_REVISIONS = 2

STEP_NAMES = {
    1: "구현 계획 수립",
    2: "계획 검토",
    3: "검토 재검토",
    4: "과도함 검토",
    5: "구현 (코드 작성)",
    6: "목적 부합 검토",
    7: "버그/크리티컬/보안 검토",
    8: "개선 내용 검토",
    9: "함수/파일 분리",
    10: "기존 코드 재사용/통합",
    11: "사이드이펙트 확인",
    12: "전체 변경사항 재검토",
    13: "불필요 코드 정리",
    14: "코드 품질 검토",
    15: "UX 흐름 검토",
    16: "연쇄 영향 반복 검토",
    17: "배포 퀄리티 최종",
    18: "커밋 + PR",
}

# 탐정가재(scout)가 exec으로 코드 작성하는 단계
EXEC_STEPS = {5, 9, 13, 18}
# 판사가재(judge)가 문서 기반 검증하는 단계
REVIEW_STEPS = {2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17}
# 탐정가재가 계획/분석하는 단계 (exec 없이)
PLAN_STEPS = {1}


# ── State ───────────────────────────────────────────────

class DevState(TypedDict):
    doc_url: str                # 설계 문서 노션 URL
    doc_content: str            # 설계 문서 텍스트
    tech_context: str
    human_inputs: list

    current_step: int           # 1~18
    step_results: dict          # {"1": "...", ...}
    step_scores: dict           # {"2": 8.5, ...} (검증 단계만)
    step_revisions: dict        # {"5": 1, ...}

    # 구현 관련
    files_changed: list         # 변경된 파일 목록
    implementation_plan: str    # Step 1 계획서
    pr_url: str                 # Step 18 PR URL

    status: str


# ── OpenClaw CLI ────────────────────────────────────────

def call_agent(agent_id: str, message: str, timeout: int = 300) -> str:
    cmd = [
        "openclaw", "agent",
        "--agent", agent_id,
        "--message", message,
        "--json",
        "--timeout", str(timeout),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30)
        if result.returncode != 0:
            return f"(error: exit {result.returncode}: {result.stderr[:200]})"
        data = json.loads(result.stdout)
        reply = data.get("result", {})
        if isinstance(reply, dict):
            payloads = reply.get("payloads", [])
            if payloads:
                text = payloads[0].get("text", "")
                if not text:
                    print(f"  ⚠️ payloads[0].text is empty, keys: {list(payloads[0].keys())}")
                return text
            else:
                print(f"  ⚠️ No payloads in result, keys: {list(reply.keys())}")
        return str(reply)[:30000]
    except subprocess.TimeoutExpired:
        return "(timeout)"
    except json.JSONDecodeError:
        return result.stdout[:3000] if result.stdout else "(empty)"
    except Exception as e:
        return f"(error: {e})"


def parse_score(text: str) -> float:
    for line in text.split("\n"):
        if line.strip().startswith("SCORE:"):
            try:
                return float(line.split(":")[1].strip().split("/")[0].strip())
            except (ValueError, IndexError):
                return 5.0
    return 5.0


def run_exec(command: str, timeout: int = 60) -> str:
    """프로젝트 디렉토리에서 명령어 실행"""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=PROJECT_DIR,
        )
        output = result.stdout + result.stderr
        return output[:3000] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "(timeout)"
    except Exception as e:
        return f"(error: {e})"


# ── Notion Reader ───────────────────────────────────────

def read_doc_from_notion(url: str) -> str:
    match = re.search(r'([0-9a-f]{32})$', url.replace('-', ''))
    if not match:
        match = re.search(r'([0-9a-f\-]{36})', url)
    if not match:
        return f"(error: page_id not found in {url})"
    raw = match.group(1).replace('-', '')
    page_id = f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
    try:
        return read_page_blocks(page_id, max_blocks=300)
    except Exception as e:
        return f"(error: {e})"


# ── Helpers ─────────────────────────────────────────────

def _prev_results(state: DevState, limit: int = 3) -> str:
    """최근 N개 step 결과"""
    parts = []
    start = max(1, state["current_step"] - limit)
    for i in range(start, state["current_step"]):
        r = state["step_results"].get(str(i), "")
        if r:
            parts.append(f"## [Step {i}] {STEP_NAMES[i]}\n{r[:2000]}")
    return "\n\n".join(parts)


def _get_project_tree() -> str:
    """프로젝트 파일 트리"""
    try:
        result = subprocess.run(
            "find . -type f -not -path '*/node_modules/*' -not -path '*/.next/*' -not -path '*/.git/*' | head -50",
            shell=True, capture_output=True, text=True, cwd=PROJECT_DIR, timeout=10,
        )
        return result.stdout[:2000] if result.stdout else "(empty project)"
    except:
        return "(error reading project)"


def _get_changed_files() -> str:
    """git diff로 변경된 파일 목록"""
    try:
        result = subprocess.run(
            "git diff --name-only HEAD 2>/dev/null || git status --short",
            shell=True, capture_output=True, text=True, cwd=PROJECT_DIR, timeout=10,
        )
        return result.stdout[:2000] if result.stdout else "(no changes)"
    except:
        return "(error)"


def _get_file_content(filepath: str) -> str:
    """특정 파일 내용 읽기"""
    full = os.path.join(PROJECT_DIR, filepath)
    try:
        with open(full) as f:
            content = f.read()
        return content[:5000]
    except:
        return f"(error reading {filepath})"


def _get_all_source_code() -> str:
    """변경된 모든 소스 파일의 코드를 합쳐서 반환"""
    try:
        result = subprocess.run(
            "find . -type f \\( -name '*.tsx' -o -name '*.ts' -o -name '*.css' \\) "
            "-not -path '*/node_modules/*' -not -path '*/.next/*' -not -path '*/.git/*'",
            shell=True, capture_output=True, text=True, cwd=PROJECT_DIR, timeout=10,
        )
        files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except:
        return "(error listing files)"

    parts = []
    total = 0
    for fpath in sorted(files):
        content = _get_file_content(fpath.lstrip('./'))
        chunk = f"\n### 파일: `{fpath}`\n```\n{content}\n```\n"
        if total + len(chunk) > 15000:
            parts.append(f"\n... ({len(files) - len(parts)}개 파일 생략)")
            break
        parts.append(chunk)
        total += len(chunk)

    return "\n".join(parts) if parts else "(no source files)"


# ── Step Prompts ────────────────────────────────────────

def make_step_prompt(state: DevState) -> str:
    step = state["current_step"]
    doc = state["doc_content"]
    prev = _prev_results(state)
    tree = _get_project_tree()
    changed = _get_changed_files()

    prompts = {
        # ── 계획 ──
        1: f"""너는 Senior Tech Lead다. 설계 문서를 읽고 구현 계획을 수립하라.

## 설계 문서
{doc[:6000]}

## 프로젝트 현재 구조
```
{tree}
```

## 기술 환경
{state['tech_context']}

## 출력: 구현 계획서

### 1. 구현 범위
- 이번에 구현할 기능 목록 (설계 문서 기준)
- 제외할 기능 (다음 스프린트)

### 2. 파일 생성/수정 계획
각 파일별:
| 파일 경로 | 액션 (생성/수정) | 핵심 내용 |

### 3. 구현 순서
의존성 고려한 구현 순서 (어떤 파일부터?)

### 4. 주의사항
- 기존 코드와 충돌 가능성
- 환경 변수 필요 여부
- 패키지 설치 필요 여부""",

        # ── 구현 ──
        5: f"""너는 Senior Full-Stack Developer다.
구현 계획에 따라 코드를 작성하라.

## 이전 리뷰 피드백 (반드시 반영!)
{prev}

## 설계 문서
{doc[:6000]}

## 프로젝트 구조
```
{tree}
```

## 기술 환경
{state['tech_context']}

## 지시
1. 필요한 파일을 생성/수정하라.
2. 각 파일의 전체 코드를 작성하라.
3. 패키지 설치가 필요하면 명령어를 포함하라.

## 출력 형식
각 파일에 대해:

### 파일: `src/app/page.tsx`
```tsx
// 전체 코드
```

### 파일: `src/components/ChatBubble.tsx`
```tsx
// 전체 코드
```

### 실행 명령어 (필요시)
```bash
npm install firebase
```""",

        # ── 리팩토링 ──
        9: f"""너는 Senior Developer다. 코드를 리팩토링하라.

## 이전 검토 결과
{prev}

## 현재 변경된 파일
{changed}

## 지시
1. 100줄 이상인 함수를 분리하라
2. 500줄 이상인 파일을 모듈로 나눠라
3. 반복되는 코드를 유틸로 추출하라

각 변경에 대해 파일 경로 + 변경 내용을 출력하라.""",

        13: f"""너는 Senior Developer다. 불필요한 코드를 정리하라.

## 이전 검토 결과
{prev}

## 현재 변경된 파일
{changed}

## 지시
1. 사용되지 않는 import 제거
2. 주석 처리된 코드 제거
3. console.log / debug 코드 제거
4. 사용되지 않는 변수/함수 제거

각 변경에 대해 파일 경로 + 변경 내용을 출력하라.""",

        18: f"""너는 DevOps Engineer다. 변경사항을 커밋하고 PR을 작성하라.

## 전체 변경 요약
{prev}

## 변경된 파일
{changed}

## 지시
1. 적절한 커밋 메시지 작성 (Conventional Commits)
2. PR 제목과 본문 작성
3. git 명령어 출력

## 출력 형식
### 커밋 메시지
```
feat: 라이브스트림 채팅 뷰 구현

- 홈 히어로 뷰 (최신 메시지 쌍 표시)
- 라이브 채팅 페이지 (텔레그램 스타일)
- Firestore onSnapshot 실시간 구독
- 원형 프로필 아바타 컴포넌트
```

### PR 본문
...

### 실행 명령어
```bash
git add -A
git commit -m "..."
git push origin dev
gh pr create --title "..." --body "..."
```""",
    }

    if step in prompts:
        return prompts[step]

    # 기본: 검토 단계 프롬프트 생성
    return _make_review_prompt(state)


def _make_review_prompt(state: DevState) -> str:
    step = state["current_step"]
    prev = _prev_results(state)
    doc = state["doc_content"]
    changed = _get_changed_files()
    tree = _get_project_tree()

    review_focus = {
        2: ("계획 검토",
            "구현 계획이 설계 문서의 모든 요구사항을 커버하는가? 빠진 기능이 없는가?",
            ["요구사항 커버리지", "구현 순서 합리성", "의존성 고려"]),
        3: ("검토 재검토",
            "Step 2의 검토가 정확한가? 놓친 부분이 있는가? 검토자의 판단이 올바른가?",
            ["검토 정확성", "놓친 리스크", "판단 근거"]),
        4: ("과도함 검토",
            "계획이 오버엔지니어링이 아닌가? MVP에 불필요한 것이 포함되지 않았는가? 1인 개발자가 현실적으로 가능한가?",
            ["MVP 적합성", "불필요한 복잡성", "현실적 구현 가능성"]),
        6: ("목적 부합 검토",
            "구현된 코드가 설계 문서의 목적에 맞는가? 설계서의 컬러/폰트/컴포넌트 스펙과 일치하는가?",
            ["기능 완전성 — 설계서에 명시된 모든 페이지/뷰가 구현되었는가",
             "디자인시스템 일치 — 설계서의 컬러코드, 폰트, 간격이 코드에 반영되었는가",
             "컴포넌트 매핑 — 설계서의 컴포넌트 목록과 실제 파일이 1:1 대응하는가",
             "동작 정확성 — Firestore 쿼리, 라우팅, 상태관리가 설계대로인가"]),
        7: ("버그/크리티컬/보안",
            "잠재적 버그, 크리티컬 이슈, 보안 취약점이 있는가?",
            ["잠재적 버그 — 에러 발생 시 빈 화면이 되는 곳이 없는가",
             "크리티컬 이슈 — 빌드 실패, 런타임 크래시 가능성",
             "보안 취약점 — API 키 노출, XSS, 인증 우회",
             "에러 핸들링 — try/catch, ErrorBoundary, fallback UI 존재 여부"]),
        8: ("개선 내용 검토",
            "이전 단계에서 개선한 내용에 새로운 문제가 발생하지 않았는가?",
            ["회귀 버그", "개선 효과", "새로운 문제"]),
        10: ("재사용/통합 검토",
            "기존 코드와 통합하거나 재사용할 수 있는 부분이 있는가? 중복 코드가 있는가?",
            ["코드 재사용", "중복 제거", "기존 코드 활용"]),
        11: ("사이드이펙트",
            "변경사항이 다른 기능에 영향을 미치지 않는가? 예상치 못한 부작용이 있는가?",
            ["사이드이펙트", "의존성 영향", "상태 관리"]),
        12: ("전체 변경사항 재검토",
            "지금까지의 모든 변경사항을 종합적으로 검토하라. 일관성이 있는가?",
            ["전체 일관성", "네이밍 규칙", "아키텍처 준수"]),
        14: ("코드 품질",
            "코드 품질이 충분히 높은가? 가독성, 유지보수성, 테스트 용이성은?",
            ["가독성 — 함수/변수명이 의도를 드러내는가",
             "유지보수성 — 파일당 300줄 이하, 함수당 50줄 이하 준수",
             "타입 안전성 — any 사용 여부, 인터페이스 정의 충분성",
             "에러 처리 — 모든 async 호출에 에러 핸들링이 있는가"]),
        15: ("UX 흐름",
            "사용자의 실제 사용 흐름에서 문제가 없는가? 엣지 케이스는?",
            ["사용자 흐름 — 페이지 간 네비게이션이 자연스러운가",
             "엣지 케이스 — 빈 데이터, 네트워크 오류, 긴 텍스트 처리",
             "로딩/에러 상태 — Skeleton, Spinner, ErrorBoundary 구현 여부",
             "모바일 UX — 터치 타겟 44px+, 스크롤 동작, 뷰포트 대응"]),
        16: ("연쇄 영향 반복 검토",
            "이전 검토에서 발견된 문제를 수정했을 때, 그 수정이 다른 곳에 영향을 미치지 않는가? 관련 코드를 모두 확인하라.",
            ["연쇄 영향", "수정 완전성", "관련 코드 확인"]),
        17: ("배포 퀄리티",
            "이대로 프로덕션에 배포해도 되는 수준인가? 환경 설정, 빌드, 성능 모두 확인.",
            ["배포 준비 — package.json, next.config.js, .env.example 모두 존재하는가",
             "환경 설정 — 환경변수 누락 없는가, README에 설정 방법 있는가",
             "빌드 성공 — TypeScript 컴파일 에러가 없을 것으로 보이는가",
             "성능 — 불필요한 리렌더링, 번들 사이즈 최적화"]),
    }

    title, question, criteria = review_focus.get(step, ("검토", "문제가 없는가?", ["품질"]))
    criteria_text = "\n".join(f"{i+1}. **{c}**" for i, c in enumerate(criteria))

    return f"""너는 Staff Engineer급 시니어 코드 리뷰어다. 실무 10년+, FAANG 출신.
너의 역할은 **프로덕션에 나갈 코드의 품질 게이트키퍼**다.

## ⚠️ 채점 철학 (필독!)
- **10점은 존재하지 않는다.** 완벽한 코드는 없다. 최대 9점.
- **8점 = 매우 훌륭함.** 사소한 개선점만 있는 상태.
- **6~7점 = 기본은 갖춤.** 기능은 동작하지만 프로덕션 수준은 아님.
- **4~5점 = 미흡.** 주요 기능 누락이나 구조적 문제 있음.
- **1~3점 = 심각.** 빌드 불가, 핵심 기능 미구현, 보안 취약점.

## 🚫 자동 감점 규칙 (해당 시 무조건 감점!)
1. **설계서 컬러가 코드와 불일치** → 해당 항목 -3점 (예: 설계서는 크림색인데 코드는 다크 테마)
2. **package.json, next.config.js 등 빌드 필수 파일 누락** → 배포 준비 항목 최대 3점
3. **ErrorBoundary / 에러 핸들링 없음** → 에러 처리 항목 최대 4점
4. **하드코딩된 문자열 (예: "AI (Claude)")** → 유지보수성 -2점
5. **설계서에 명시된 컴포넌트가 누락** → 기능 완전성 -2점 per 컴포넌트
6. **any 타입 3개 이상 사용** → 타입 안전성 최대 4점
7. **환경변수 .env.example 없음** → 환경 설정 -2점
8. **모바일 대응 없음 (미디어쿼리/반응형 없음)** → 모바일 UX 최대 4점

## [Step {step}] {title}

## 핵심 질문
{question}

## 설계 문서 (원본 — 이 스펙과 코드를 1:1 대조하라!)
{doc[:3000]}

## 이전 단계 결과
{prev}

## 프로젝트 구조
```
{tree}
```

## 변경된 파일
{changed}

## 실제 소스 코드 (리뷰 대상 — 꼼꼼히 읽어라!)
{_get_all_source_code()}

## 평가 항목 (각 1~10점, 위 감점 규칙 적용!)
{criteria_text}

## 출력 형식 (반드시)

### 설계서 대조 체크리스트
- [ ] 컬러 일치 여부: (설계서 컬러 vs 코드 컬러)
- [ ] 컴포넌트 목록 일치: (설계서 컴포넌트 vs 실제 파일)
- [ ] 필수 파일 존재: package.json, next.config, .env.example, README
- [ ] 에러 핸들링: ErrorBoundary, try/catch, fallback UI

### 점수표
SCORE: [평균 점수, 소수점 1자리]

| 항목 | 점수 | 감점 사유 |
|---|---|---|
| ... | X/10 | 구체적으로 어떤 코드의 몇 번째 줄이 문제인지 |

VERDICT: [PASS/REVISE]

ISSUES: (발견된 구체적 문제 — 파일명:줄번호 포함)
FIXES: (각 문제에 대한 구체적 수정 코드 제시)

## 판정 기준
- 7점 이상: PASS
- 7점 미만: REVISE (구체적 수정 지시 필수)
- **감점 규칙에 해당하는 항목이 있으면 반드시 감점하라. 예외 없음.**"""


# ── LangGraph Nodes ─────────────────────────────────────

def node_read_doc(state: DevState) -> dict:
    print(f"\n📖 설계 문서 읽는 중: {state['doc_url'][:60]}...")
    content = read_doc_from_notion(state["doc_url"])
    print(f"  ✅ {len(content)}자")

    # 프로젝트 디렉토리 초기화
    os.makedirs(PROJECT_DIR, exist_ok=True)
    run_exec("git init 2>/dev/null; git checkout -b dev 2>/dev/null")
    return {"doc_content": content}


def node_work(state: DevState) -> dict:
    step = state["current_step"]
    rev = state["step_revisions"].get(str(step), 0)
    suffix = f" (수정 {rev}차)" if rev > 0 else ""

    if step in EXEC_STEPS:
        icon = "🔨"
        agent = "scout"
    elif step in REVIEW_STEPS:
        icon = "⚖️"
        agent = "judge"
    else:
        icon = "📋"
        agent = "scout"

    print(f"\n{icon} [Step {step}/18] {STEP_NAMES[step]}{suffix} — {'탐정' if agent == 'scout' else '판사'}가재...")

    prompt = make_step_prompt(state)

    # 검토 재검토(3)와 과도함 검토(4)는 이전 결과를 포함
    if step in {3, 4} and rev == 0:
        prev_review = state["step_results"].get(str(step - 1), "")
        if prev_review:
            prompt += f"\n\n## 이전 검토 결과\n{prev_review}"

    result = call_agent(agent, prompt, timeout=300)

    new_results = dict(state["step_results"])
    new_results[str(step)] = result

    updates = {"step_results": new_results}

    # Step 1: 계획서 저장
    if step == 1:
        updates["implementation_plan"] = result

    # 검증 단계: 점수 파싱
    if step in REVIEW_STEPS:
        score = parse_score(result)
        new_scores = dict(state["step_scores"])
        new_scores[str(step)] = score
        updates["step_scores"] = new_scores
        print(f"  {'✅ PASS' if score >= 7 else '🔄 REVISE'} ({score}/10)")
    else:
        print(f"  ✅ 완료 ({len(result)}자)")

    # Exec 단계: 실제 코드 작성
    if step in EXEC_STEPS and step != 18:
        # 디버그: 결과 저장
        with open('/tmp/develop_step5_output.txt', 'w') as f:
            f.write(result)
        _apply_code_changes(result)

    # Step 18: 커밋 + PR
    if step == 18:
        pr_url = _execute_commit_pr(result)
        updates["pr_url"] = pr_url

    return updates


def _apply_code_changes(result: str):
    """탐정가재 출력에서 코드 블록 추출 → 파일 생성"""
    # "### 파일: `path`" + (설명 텍스트) + 코드블록 패턴 매칭
    # 설명 줄이 끼어있을 수 있으므로 유연하게 매칭
    file_pattern = re.findall(
        r'###\s*파일:\s*`([^`]+)`[^\n]*\n(?:(?!```)[^\n]*\n)*```\w*\n(.*?)```',
        result, re.DOTALL
    )
    if not file_pattern:
        # 대안 패턴: "**path**" 또는 그냥 path
        file_pattern = re.findall(
            r'(?:파일|File):\s*[`\*]*([^\s`\*]+)[`\*]*\s*\n```\w*\n(.*?)```',
            result, re.DOTALL
        )

    for filepath, code in file_pattern:
        full_path = os.path.join(PROJECT_DIR, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(code)
        print(f"  📄 {filepath} ({len(code)}자)")

    if not file_pattern:
        print(f"  ⚠️ 파일 패턴 매칭 실패! 출력 시작: {result[:200]}")

    # bash 명령어 실행
    bash_blocks = re.findall(r'```bash\n(.*?)```', result, re.DOTALL)
    for cmd in bash_blocks:
        for line in cmd.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('git'):
                print(f"  🔧 {line[:60]}")
                run_exec(line, timeout=30)


def _execute_commit_pr(result: str) -> str:
    """Step 18: git 명령어 추출 및 실행"""
    # 커밋 메시지 추출
    commit_match = re.search(r'git commit -m ["\'](.+?)["\']', result)
    if commit_match:
        msg = commit_match.group(1)
    else:
        msg = "feat: implement livestream chat view"

    run_exec("git add -A")
    output = run_exec(f'git commit -m "{msg}"')
    print(f"  📦 Commit: {msg[:60]}")

    # PR은 수동으로 할 수 있도록 URL만 표시
    push_output = run_exec("git push origin dev 2>&1")
    print(f"  🚀 Push: {push_output[:100]}")

    return f"commit: {msg}"


def route_after_work(state: DevState) -> Literal["revise", "next_step"]:
    step = state["current_step"]

    # 검증 단계: 점수 기반 라우팅
    if step in REVIEW_STEPS:
        score = state["step_scores"].get(str(step), 0)
        rev = state["step_revisions"].get(str(step), 0)

        if score >= 7 or rev >= MAX_REVISIONS:
            return "next_step"
        return "revise"

    # 실행/계획 단계: 항상 다음으로
    return "next_step"


def node_revise(state: DevState) -> dict:
    step = str(state["current_step"])
    r = dict(state["step_revisions"])
    r[step] = r.get(step, 0) + 1

    # 검증 실패 → 이전 실행 단계로 돌아가야 하는 경우
    # Step 6~8 실패 → Step 5로 (재구현)
    # Step 10~11 실패 → Step 9로 (재리팩토링)
    # Step 14~15 실패 → Step 13으로 (재정리)
    # 나머지 → 같은 단계 재실행
    current = state["current_step"]
    go_back_to = current

    if current in {6, 7, 8}:
        go_back_to = 5
    elif current in {10, 11}:
        go_back_to = 9
    elif current in {14, 15}:
        go_back_to = 13
    elif current in {2, 3, 4}:
        go_back_to = 1

    print(f"  🔄 REVISE → Step {go_back_to}")
    return {"step_revisions": r, "current_step": go_back_to}


def node_next_step(state: DevState) -> dict:
    next_s = state["current_step"] + 1
    if next_s > 18:
        return {"status": "completed"}
    return {"current_step": next_s}


def node_finalize(state: DevState) -> dict:
    print("\n✅ 구현 파이프라인 완료!")
    scores = state["step_scores"]
    if scores:
        avg = sum(scores.values()) / len(scores)
        print(f"   검증 평균: {avg:.1f}/10")
    total_rev = sum(state.get("step_revisions", {}).values())
    print(f"   총 수정: {total_rev}회")
    for s in range(1, 19):
        name = STEP_NAMES[s]
        result = state["step_results"].get(str(s), "")
        score = scores.get(str(s), "")
        rev = state.get("step_revisions", {}).get(str(s), 0)
        icon = "🔨" if s in EXEC_STEPS else ("⚖️" if s in REVIEW_STEPS else "📋")
        score_str = f" {score}/10" if score else ""
        rev_str = f" (수정 {rev}회)" if rev else ""
        has = "✅" if result else "⏳"
        print(f"   {icon} [{s:2d}] {name}: {has}{score_str}{rev_str}")
    if state.get("pr_url"):
        print(f"   🚀 PR: {state['pr_url']}")
    return {"status": "completed"}


# ── Build Graph ─────────────────────────────────────────

def build_graph():
    g = StateGraph(DevState)

    g.add_node("read_doc", node_read_doc)
    g.add_node("work", node_work)
    g.add_node("revise", node_revise)
    g.add_node("next_step", node_next_step)
    g.add_node("finalize", node_finalize)

    g.set_entry_point("read_doc")
    g.add_edge("read_doc", "work")

    g.add_conditional_edges("work", route_after_work, {
        "revise": "revise",
        "next_step": "next_step",
    })
    g.add_edge("revise", "work")

    # next_step: completed면 finalize, 아니면 work
    def route_next(state: DevState) -> Literal["work", "finalize"]:
        return "finalize" if state.get("status") == "completed" else "work"

    g.add_conditional_edges("next_step", route_next, {
        "work": "work",
        "finalize": "finalize",
    })
    g.add_edge("finalize", END)

    return g.compile()


# ── State Persistence ───────────────────────────────────


# ── Main ────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("""Usage:
  python3 graph.py run "노션_설계문서_URL" "기술환경" [--start N]
  python3 graph.py status RUN_ID

Examples:
  python3 graph.py run "https://notion.so/..." --start 5   # 설계서가 있으면 5번(구현)부터
  python3 graph.py run "https://notion.so/..."              # 1번(계획)부터 풀 파이프라인""")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "run":
        doc_url = sys.argv[2]
        tech = sys.argv[3] if len(sys.argv) > 3 else "Next.js 15, TypeScript, Firestore, Tailwind CSS, Vercel"

        # --start N 옵션: 특정 단계부터 시작
        start_step = 1
        for i, arg in enumerate(sys.argv):
            if arg == "--start" and i + 1 < len(sys.argv):
                start_step = int(sys.argv[i + 1])

        run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        skipped = f"  ⏭️  Step 1~{start_step-1} 스킵 (설계서가 계획서 역할)\n" if start_step > 1 else ""

        print(f"""
╔══════════════════════════════════════════════════╗
║  🔨 Gajae Developer — Implementation Pipeline   ║
╚══════════════════════════════════════════════════╝
  Run ID: {run_id}
  설계서: {doc_url[:60]}
  기술: {tech[:60]}
  프로젝트: {PROJECT_DIR}
  시작: Step {start_step} ({STEP_NAMES[start_step]})
{skipped}  공정: 📖→[{start_step}]→...→[18]🔨→END
""")

        initial: DevState = {
            "doc_url": doc_url,
            "doc_content": "",
            "tech_context": tech,
            "human_inputs": [],
            "current_step": start_step,
            "step_results": {},
            "step_scores": {},
            "step_revisions": {},
            "files_changed": [],
            "implementation_plan": "",
            "pr_url": "",
            "status": "running",
        }

        graph = build_graph()
        final = graph.invoke(initial)

        print(f"\n💾 State: {run_id}")

if __name__ == "__main__":
    main()
