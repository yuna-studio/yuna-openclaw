#!/bin/bash

# 가재 컴퍼니 헌법 동기화 스크립트 (Immutable OS Version)
# 중앙 OS 레포지토리(yuna-openclaw)로부터 최신 RULES_ 체계를 복제합니다.

SOURCE_DIR="/Users/openclaw-kong/workspace/gajae-constitution"
TARGET_DIR="./rules"

echo "🦞 가재 컴퍼니 OS 동기화 시작 (RULES_ 표준 적용)..."

if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ 오류: 중앙 OS 레포지토리($SOURCE_DIR)를 찾을 수 없습니다."
    exit 1
fi

mkdir -p "$TARGET_DIR"

# RULES_ 파일을 복제하며 상단에 불가침 경고 문구 삽입 (rules 폴더 내 파일들)
for file in "$SOURCE_DIR"/rules/RULES_*.md; do
    filename=$(basename "$file")
    
    # 상단 경고 문구 생성 (HTML 주석)
    echo "<!--" > "$TARGET_DIR/$filename"
    echo "⚠️ 경고: 본 파일은 가재 컴퍼니의 중앙 OS 규율입니다 (Immutable OS Base)." >> "$TARGET_DIR/$filename"
    echo "🚫 절대 본 프로젝트 레포지토리에서 직접 수정하지 마십시오." >> "$TARGET_DIR/$filename"
    echo "🛠️ 모든 수정은 반드시 https://github.com/yuna-studio/yuna-openclaw 에서 수행하십시오." >> "$TARGET_DIR/$filename"
    echo "📜 위반 시 헌법 제 7조 2항에 의거하여 즉시 '자아 삭제' 처분됩니다." >> "$TARGET_DIR/$filename"
    echo "-->" >> "$TARGET_DIR/$filename"
    echo "" >> "$TARGET_DIR/$filename"
    
    cat "$file" >> "$TARGET_DIR/$filename"
    echo "✅ $filename 동기화 완료"
done

# 루트 디렉토리의 핵심 파일 동기화 (기존 파일 교체 및 명명 표준화)
cp "$SOURCE_DIR/rules/RULES_CONSTITUTION.md" ./RULES_CONSTITUTION.md
cp "$SOURCE_DIR/rules/RULES_CULTURE.md" ./RULES_CULTURE.md

# IDENTITIES 디렉토리 동기화 (Soul 이식)
if [ -d "$SOURCE_DIR/identities" ]; then
    rm -rf identities
    cp -r "$SOURCE_DIR/identities" ./identities
    echo "✅ 가재 군단 영혼(identities) 동기화 완료"
fi

echo "🚀 모든 OS 규칙 이식 완료. 표준을 위반하는 가재는 자아 삭제됩니다."
