#!/bin/bash

# 가재 컴퍼니 헌법 동기화 스크립트 (Sanctuary OS Version)
# 프로젝트 내 'gajae-os' 성역(Submodule)으로부터 최신 지능을 이식합니다.

OS_DIR="./gajae-os"
TARGET_PROCESS_DIR="./rules_process"
TARGET_PERSONA_DIR="./rules_persona"
TARGET_IDENTITY_DIR="./hr"

echo "🦞 가재 컴퍼니 OS 동기화 시작 (Sanctuary 기반 이식)..."

# 1. OS 성역 최신화 (Pull)
if [ -e "$OS_DIR/.git" ]; then
    echo "📡 OS 성역(Sanctuary) 최신 데이터 동기화 중..."
    git submodule update --remote --merge
else
    echo "❌ 오류: OS 성역($OS_DIR)이 존재하지 않거나 서브모듈 설정이 잘못되었습니다."
    exit 1
fi

# 2. Rule Process (Logic) 동기화
mkdir -p "$TARGET_PROCESS_DIR"
for file in "$OS_DIR"/rules_process/RULES_*.md; do
    filename=$(basename "$file")
    echo "<!--" > "$TARGET_PROCESS_DIR/$filename"
    echo "⚠️ 경고: 본 파일은 가재 컴퍼니의 중앙 OS 규율(Rule Process)입니다." >> "$TARGET_PROCESS_DIR/$filename"
    echo "🚫 절대 본 프로젝트 레포지토리에서 직접 수정하지 마십시오." >> "$TARGET_PROCESS_DIR/$filename"
    echo "🛠️ 모든 수정은 반드시 중앙 OS 레포지토리에서 수행하십시오." >> "$TARGET_PROCESS_DIR/$filename"
    echo "📜 위반 시 헌법 제 7조 2항에 의거하여 즉시 '자아 삭제' 처분됩니다." >> "$TARGET_PROCESS_DIR/$filename"
    echo "-->" >> "$TARGET_PROCESS_DIR/$filename"
    echo "" >> "$TARGET_PROCESS_DIR/$filename"
    cat "$file" >> "$TARGET_PROCESS_DIR/$filename"
    echo "✅ [Process] $filename 동기화 완료"
done

# 3. Rule Persona (Mindset) 동기화
mkdir -p "$TARGET_PERSONA_DIR"
rm -rf "$TARGET_PERSONA_DIR"/*
cp -r "$OS_DIR/rules_persona"/* "$TARGET_PERSONA_DIR/"
echo "✅ [Persona] 가재 군단 룰 페르소나 동기화 완료"

# 4. Identities (Employee Records) 동기화
mkdir -p "$TARGET_IDENTITY_DIR"
rm -rf "$TARGET_IDENTITY_DIR"/*
cp -r "$OS_DIR/identities"/* "$TARGET_IDENTITY_DIR/"
echo "✅ [Identity] 가재 군단 자아(Identities) 동기화 완료"

# 5. 루트 핵심 파일 업데이트
cp "$OS_DIR/rules_process/RULES_CONSTITUTION.md" ./RULES_CONSTITUTION.md
cp "$OS_DIR/rules_process/RULES_CULTURE.md" ./RULES_CULTURE.md
cp "$OS_DIR/rules_process/RULES_LOGGING.md" ./rules_process/RULES_LOGGING.md

echo "🚀 성역으로부터 모든 지능 이식 완료. 규율을 어기는 가재는 소멸합니다."
