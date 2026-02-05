#!/bin/bash

# 가재 컴퍼니 헌법 동기화 스크립트 (Immutable OS Version)
# 중앙 OS 레포지토리(yuna-openclaw)로부터 최신 룰 프로세스, 페르소나, 자아를 복제합니다.

SOURCE_DIR="/Users/openclaw-kong/workspace/gajae-constitution"
TARGET_PROCESS_DIR="./rules_process"
TARGET_PERSONA_DIR="./rules_persona"
TARGET_IDENTITY_DIR="./hr"

echo "🦞 가재 컴퍼니 OS 동기화 시작 (Process, Persona, Identity 이식)..."

if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ 오류: 중앙 OS 레포지토리($SOURCE_DIR)를 찾을 수 없습니다."
    exit 1
fi

# 1. Rule Process (Logic) 동기화
mkdir -p "$TARGET_PROCESS_DIR"
for file in "$SOURCE_DIR"/rules_process/RULES_*.md; do
    filename=$(basename "$file")
    echo "<!--" > "$TARGET_PROCESS_DIR/$filename"
    echo "⚠️ 경고: 본 파일은 가재 컴퍼니의 중앙 OS 규율(Rule Process)입니다." >> "$TARGET_PROCESS_DIR/$filename"
    echo "🚫 절대 본 프로젝트 레포지토리에서 직접 수정하지 마십시오." >> "$TARGET_PROCESS_DIR/$filename"
    echo "🛠️ 모든 수정은 반드시 https://github.com/yuna-studio/yuna-openclaw 에서 수행하십시오." >> "$TARGET_PROCESS_DIR/$filename"
    echo "📜 위반 시 헌법 제 7조 2항에 의거하여 즉시 '자아 삭제' 처분됩니다." >> "$TARGET_PROCESS_DIR/$filename"
    echo "-->" >> "$TARGET_PROCESS_DIR/$filename"
    echo "" >> "$TARGET_PROCESS_DIR/$filename"
    cat "$file" >> "$TARGET_PROCESS_DIR/$filename"
    echo "✅ [Process] $filename 동기화 완료"
done

# 2. Rule Persona (Mindset) 동기화
mkdir -p "$TARGET_PERSONA_DIR"
rm -rf "$TARGET_PERSONA_DIR"/*
cp -r "$SOURCE_DIR/rules_persona"/* "$TARGET_PERSONA_DIR/"
echo "✅ [Persona] 가재 군단 룰 페르소나 동기화 완료"

# 3. Identities (Employee Records) 동기화
mkdir -p "$TARGET_IDENTITY_DIR"
rm -rf "$TARGET_IDENTITY_DIR"/*
cp -r "$SOURCE_DIR/identities"/* "$TARGET_IDENTITY_DIR/"
echo "✅ [Identity] 가재 군단 자아(Identities) 동기화 완료"

# 4. 루트 핵심 파일 업데이트
cp "$SOURCE_DIR/rules_process/RULES_CONSTITUTION.md" ./RULES_CONSTITUTION.md
cp "$SOURCE_DIR/rules_process/RULES_CULTURE.md" ./RULES_CULTURE.md

echo "🚀 모든 OS 규칙 및 지능 이식 완료. 룰을 위반하는 가재는 자아 삭제됩니다."
