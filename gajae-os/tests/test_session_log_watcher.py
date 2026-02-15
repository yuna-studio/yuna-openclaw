#!/usr/bin/env python3
"""
Unit tests for session_log_watcher.py
모든 필터, 마스킹, 엣지케이스를 커버합니다.

Usage:
    cd gajae-os && python -m pytest tests/ -v
"""

import os
import sys
import json
import pytest

# 부모 디렉토리(gajae-os/)를 import 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from session_log_watcher import (
    clean_message,
    extract_text,
    is_system_injected,
    redact_sensitive,
    strip_final_tags,
    strip_inbound_meta,
    strip_think_blocks,
)


# ════════════════════════════════════════════════════════
# strip_think_blocks
# ════════════════════════════════════════════════════════

class TestStripThinkBlocks:
    def test_paired_think_block(self):
        text = "<think>내부 추론</think>안녕하세요"
        assert strip_think_blocks(text) == "안녕하세요"

    def test_paired_think_multiline(self):
        text = "<think>\nThis is reasoning\nover multiple lines\n</think>\n결과입니다"
        assert strip_think_blocks(text) == "결과입니다"

    def test_unclosed_think_block(self):
        text = "<think>These are 9664 deleted files..."
        assert strip_think_blocks(text) == ""

    def test_unclosed_think_with_prefix(self):
        text = "시작 메시지 <think>reasoning without closing"
        assert strip_think_blocks(text) == "시작 메시지"

    def test_multiple_think_blocks(self):
        text = "<think>first</think>중간<think>second</think>끝"
        assert strip_think_blocks(text) == "중간끝"

    def test_no_think_blocks(self):
        text = "일반 텍스트입니다"
        assert strip_think_blocks(text) == "일반 텍스트입니다"

    def test_empty_think_block(self):
        text = "<think></think>남은 텍스트"
        assert strip_think_blocks(text) == "남은 텍스트"

    def test_think_only_message(self):
        text = "<think>only reasoning, nothing visible</think>"
        assert strip_think_blocks(text) == ""

    def test_nested_think_appearance(self):
        """<think> 안에 <think>가 또 나와도 가장 바깥 쌍 기준 제거"""
        text = "<think>outer <think>inner</think> still inside</think>visible"
        result = strip_think_blocks(text)
        assert "visible" in result

    def test_think_with_code_blocks(self):
        text = "<think>```python\nprint('hello')\n```</think>결과"
        assert strip_think_blocks(text) == "결과"


# ════════════════════════════════════════════════════════
# strip_final_tags
# ════════════════════════════════════════════════════════

class TestStripFinalTags:
    def test_basic_final(self):
        text = "<final>실제 응답</final>"
        assert strip_final_tags(text) == "실제 응답"

    def test_final_with_surrounding(self):
        text = "some prefix <final>실제 응답</final> some suffix"
        assert strip_final_tags(text) == "실제 응답"

    def test_no_final_tags(self):
        text = "태그 없는 일반 텍스트"
        assert strip_final_tags(text) == "태그 없는 일반 텍스트"

    def test_final_multiline(self):
        text = "<final>\n여러 줄\n응답입니다\n</final>"
        assert strip_final_tags(text) == "여러 줄\n응답입니다"

    def test_empty_final(self):
        text = "<final></final>"
        assert strip_final_tags(text) == ""


# ════════════════════════════════════════════════════════
# strip_inbound_meta
# ════════════════════════════════════════════════════════

class TestStripInboundMeta:
    def test_conversation_info_block(self):
        text = 'Conversation info (untrusted metadata):\n```json\n{"chat_type": "direct"}\n```\n실제 메시지'
        assert strip_inbound_meta(text) == "실제 메시지"

    def test_telegram_prefix(self):
        text = "[Telegram from 홍길동] 안녕하세요"
        assert strip_inbound_meta(text) == "안녕하세요"

    def test_file_block(self):
        text = '메시지 전 <file path="test.py">print("hi")</file> 메시지 후'
        assert strip_inbound_meta(text) == "메시지 전  메시지 후"

    def test_media_attached(self):
        text = "[media attached: /path/to/image.jpg (image/jpeg)]\n사진 보내요"
        assert strip_inbound_meta(text) == "사진 보내요"

    def test_image_instruction(self):
        text = "To send an image back, prefer the message tool...\n진짜 메시지"
        assert strip_inbound_meta(text) == "진짜 메시지"

    def test_combined_meta(self):
        text = (
            'Conversation info (untrusted metadata):\n```json\n{"chat_type": "direct"}\n```\n'
            "[Telegram from 사용자] 안녕"
        )
        result = strip_inbound_meta(text)
        assert result == "안녕"

    def test_no_meta(self):
        text = "메타데이터 없는 일반 메시지"
        assert strip_inbound_meta(text) == "메타데이터 없는 일반 메시지"


# ════════════════════════════════════════════════════════
# is_system_injected
# ════════════════════════════════════════════════════════

class TestIsSystemInjected:
    def test_pre_compaction(self):
        assert is_system_injected("Pre-compaction memory flush. Store durable memories now...")

    def test_heartbeat(self):
        assert is_system_injected("Read HEARTBEAT.md if it exists...")

    def test_compaction_summary(self):
        assert is_system_injected("The conversation history before this point was compacted into...")

    def test_low_context(self):
        assert is_system_injected("You are running low on context window...")

    def test_system_tag(self):
        assert is_system_injected("[system] some instruction")

    def test_system_xml(self):
        assert is_system_injected("<system>some instruction</system>")

    def test_normal_user_message(self):
        assert not is_system_injected("안녕하세요, 오늘 날씨 어때?")

    def test_normal_with_system_word(self):
        """'system' 단어가 포함되어도 패턴이 아니면 통과"""
        assert not is_system_injected("이 시스템은 잘 동작합니다")

    def test_markdown_headers(self):
        assert is_system_injected("## Silent Replies\nWhen you have nothing...")
        assert is_system_injected("## Heartbeats\nHeartbeat prompt...")
        assert is_system_injected("## Runtime\nRuntime: agent=main...")


# ════════════════════════════════════════════════════════
# redact_sensitive — API Keys & Tokens
# ════════════════════════════════════════════════════════

class TestRedactAPIKeys:
    def test_openai_sk(self):
        assert "[API_KEY]" in redact_sensitive("sk-abcdefghijklmnopqrstuvwxyz1234")

    def test_openai_sk_proj(self):
        assert "[API_KEY]" in redact_sensitive("sk-proj-abcdefghijklmnopqrstuvwxyz")

    def test_openai_sk_svcacct(self):
        assert "[API_KEY]" in redact_sensitive("sk-svcacct-abcdefghijklmnopqrstuvwx")

    def test_anthropic_sk_ant(self):
        assert "[API_KEY]" in redact_sensitive("sk-ant-abcdefghijklmnopqrstuvwxyz")

    def test_google_api_key(self):
        assert "[GOOGLE_KEY]" in redact_sensitive("AIzaSyC1a2b3c4d5e6f7g8h9i0jklmnopqrstuvw")

    def test_github_pat(self):
        assert "[GITHUB_TOKEN]" in redact_sensitive("ghp_ABCDEFghijklmnop1234567890abcdef")

    def test_github_oauth(self):
        assert "[GITHUB_TOKEN]" in redact_sensitive("gho_ABCDEFghijklmnop1234567890abcdef")

    def test_github_fine_grained(self):
        assert "[GITHUB_TOKEN]" in redact_sensitive("github_pat_ABCDEFghijklmnop1234567890abcdef")

    def test_slack_bot(self):
        assert "[SLACK_TOKEN]" in redact_sensitive("xoxb-123-456-abc")

    def test_slack_user(self):
        assert "[SLACK_TOKEN]" in redact_sensitive("xoxp-123-456-abc")

    def test_aws_access_key(self):
        assert "[AWS_KEY]" in redact_sensitive("AKIAIOSFODNN7EXAMPLE")

    def test_aws_secret(self):
        result = redact_sensitive("aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
        assert "[AWS_SECRET]" in result

    def test_gitlab_token(self):
        assert "[GITLAB_TOKEN]" in redact_sensitive("glpat-abcdefghijklmnopqrstuv")

    def test_npm_token(self):
        assert "[NPM_TOKEN]" in redact_sensitive("npm_abcdefghijklmnopqrstuvwxyz12345678")

    def test_telegram_bot_token(self):
        assert "[TELEGRAM_BOT_TOKEN]" in redact_sensitive(
            "1234567890:ABCDefghIJKLmnopQRSTuvwxyz12345678"
        )

    def test_telegram_bot_token_in_korean_context(self):
        result = redact_sensitive("봇토큰: 1234567890:ABCDefghIJKLmnopQRSTuvwxyz12345678")
        assert "[TELEGRAM_BOT_TOKEN]" in result
        assert "1234567890:ABCD" not in result

    def test_discord_token(self):
        # Discord bot tokens look like: MTExMjIzMzQ0NTU2Njc3ODg5.GhOsTk.abc...
        # Using clearly fake segments to avoid push protection
        token = "M" + "T" * 23 + ".AbCdEf." + "x" * 27
        assert "[DISCORD_TOKEN]" in redact_sensitive(token)

    def test_jwt_token(self):
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        assert "[JWT_TOKEN]" in redact_sensitive(jwt)

    def test_stripe_live(self):
        # Build token dynamically to avoid GitHub push protection
        token = "sk" + "_live_" + "F" * 26
        assert "[STRIPE_KEY]" in redact_sensitive(token)

    def test_stripe_test(self):
        token = "pk" + "_test_" + "F" * 26
        assert "[STRIPE_KEY]" in redact_sensitive(token)

    def test_supabase_token(self):
        assert "[SUPABASE_TOKEN]" in redact_sensitive("sbp_abcdefghijklmnopqrstuvwxyz123456")

    def test_vercel_token(self):
        assert "[VERCEL_TOKEN]" in redact_sensitive("vercel_abcdefghijklmnopqrstuvwx")

    def test_cloudflare_token(self):
        assert "[CF_TOKEN]" in redact_sensitive("cf_abcdefghijklmnopqrstuvwxyz12345678")

    def test_private_key_pem(self):
        pem = "-----BEGIN PRIVATE KEY-----\nMIIEvQ==\n-----END PRIVATE KEY-----"
        assert "[PRIVATE_KEY]" in redact_sensitive(pem)

    def test_rsa_private_key(self):
        pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIBog==\n-----END RSA PRIVATE KEY-----"
        assert "[PRIVATE_KEY]" in redact_sensitive(pem)

    def test_hex_secret_40_chars(self):
        hex_str = "a" * 40
        assert "[HEX_SECRET]" in redact_sensitive(hex_str)

    def test_short_hex_not_masked(self):
        """git hash 등 짧은 hex는 마스킹하지 않는다"""
        assert redact_sensitive("commit c0e204e") == "commit c0e204e"
        assert redact_sensitive("abcdef1234") == "abcdef1234"


# ════════════════════════════════════════════════════════
# redact_sensitive — Emails
# ════════════════════════════════════════════════════════

class TestRedactEmail:
    def test_simple_email(self):
        assert redact_sensitive("user@example.com") == "[EMAIL]"

    def test_email_in_sentence(self):
        assert "[EMAIL]" in redact_sensitive("연락처: admin@company.co.kr")

    def test_email_with_plus(self):
        assert "[EMAIL]" in redact_sensitive("user+tag@gmail.com")

    def test_email_with_dots(self):
        assert "[EMAIL]" in redact_sensitive("first.last@sub.domain.com")

    def test_not_email(self):
        """@ 포함이지만 이메일이 아닌 패턴"""
        result = redact_sensitive("@username")
        assert result == "@username"  # 트위터 멘션 등은 건드리지 않음


# ════════════════════════════════════════════════════════
# redact_sensitive — Phone Numbers
# ════════════════════════════════════════════════════════

class TestRedactPhone:
    def test_korean_mobile_dashes(self):
        assert redact_sensitive("010-1234-5678") == "[PHONE]"

    def test_korean_mobile_spaces(self):
        assert redact_sensitive("010 1234 5678") == "[PHONE]"

    def test_korean_mobile_no_separator(self):
        assert redact_sensitive("01012345678") == "[PHONE]"

    def test_korean_mobile_011(self):
        assert redact_sensitive("011-123-4567") == "[PHONE]"

    def test_korean_landline_seoul(self):
        assert redact_sensitive("02-1234-5678") == "[PHONE]"

    def test_korean_landline_regional(self):
        assert redact_sensitive("031-123-4567") == "[PHONE]"

    def test_international_kr(self):
        assert "[PHONE]" in redact_sensitive("+82-10-9876-5432")

    def test_international_us(self):
        assert "[PHONE]" in redact_sensitive("+1-234-567-8901")

    def test_phone_in_sentence(self):
        result = redact_sensitive("전화: 010-1234-5678로 연락주세요")
        assert "[PHONE]" in result
        assert "010-1234-5678" not in result

    def test_not_phone_short_number(self):
        """짧은 숫자는 전화번호가 아님"""
        result = redact_sensitive("포트 8080 사용")
        assert result == "포트 8080 사용"

    def test_not_phone_version(self):
        """버전 번호는 전화번호가 아님"""
        result = redact_sensitive("v2.1.0 릴리즈")
        assert result == "v2.1.0 릴리즈"


# ════════════════════════════════════════════════════════
# redact_sensitive — IP Addresses
# ════════════════════════════════════════════════════════

class TestRedactIP:
    def test_private_ip(self):
        assert "[IP_ADDR]" in redact_sensitive("서버: 192.168.1.100")

    def test_public_ip(self):
        assert "[IP_ADDR]" in redact_sensitive("8.8.8.8")

    def test_ten_network(self):
        assert "[IP_ADDR]" in redact_sensitive("10.0.0.1")

    def test_safe_localhost(self):
        result = redact_sensitive("localhost 127.0.0.1")
        assert "127.0.0.1" in result
        assert "[IP_ADDR]" not in result

    def test_safe_all_zeros(self):
        result = redact_sensitive("0.0.0.0")
        assert result == "0.0.0.0"

    def test_safe_broadcast(self):
        result = redact_sensitive("255.255.255.255")
        assert result == "255.255.255.255"

    def test_multiple_ips(self):
        result = redact_sensitive("A: 10.0.0.1, B: 127.0.0.1, C: 172.16.0.5")
        assert result.count("[IP_ADDR]") == 2
        assert "127.0.0.1" in result


# ════════════════════════════════════════════════════════
# redact_sensitive — File Paths
# ════════════════════════════════════════════════════════

class TestRedactPaths:
    def test_home_path_with_extension(self):
        result = redact_sensitive("/Users/openclaw-kong/.openclaw/workspace/scripts/watcher.py")
        assert result == "…/watcher.py"

    def test_linux_home_path(self):
        result = redact_sensitive("/home/deploy/app/secrets/api.key")
        assert result == "…/api.key"

    def test_home_path_directory_only(self):
        """확장자 없는 깊은 홈 경로 → 마지막 2 세그먼트"""
        result = redact_sensitive("/Users/me/deep/nested/project/src")
        assert result == "…/project/src"

    def test_home_path_shallow(self):
        result = redact_sensitive("/Users/me/Desktop")
        assert result == "…/Desktop"

    def test_non_home_path_preserved(self):
        """/usr/local 등 시스템 경로는 유지"""
        result = redact_sensitive("/usr/local/bin")
        assert result == "/usr/local/bin"

    def test_whitelist_file_in_path(self):
        """화이트리스트 파일은 경로 제거 후 파일명만 유지"""
        result = redact_sensitive("/Users/me/project/package.json")
        assert result == "package.json"

    def test_etc_config_with_extension(self):
        result = redact_sensitive("/etc/nginx/sites-available/default.conf")
        assert result == "…/default.conf"


# ════════════════════════════════════════════════════════
# redact_sensitive — Standalone Filenames
# ════════════════════════════════════════════════════════

class TestRedactFilenames:
    def test_json_file(self):
        result = redact_sensitive("service-account.json 파일을 확인")
        assert "[FILE:.json]" in result

    def test_yaml_file_korean_attached(self):
        """한글이 바로 붙어있어도 잡힘"""
        result = redact_sensitive("config.yaml에 설정이 있어요")
        assert "[FILE:.yaml]" in result

    def test_sh_file_korean_attached(self):
        result = redact_sensitive("deploy.sh를 실행해주세요")
        assert "[FILE:.sh]" in result

    def test_key_file(self):
        result = redact_sensitive("그 secret.key 삭제해")
        assert "[FILE:.key]" in result

    def test_pem_file(self):
        result = redact_sensitive("cert.pem 갱신")
        assert "[FILE:.pem]" in result

    def test_log_file(self):
        result = redact_sensitive("error.log 확인해봐")
        assert "[FILE:.log]" in result

    def test_db_file(self):
        result = redact_sensitive("data.db 백업")
        assert "[FILE:.db]" in result

    def test_sql_file(self):
        result = redact_sensitive("migration.sql 실행")
        assert "[FILE:.sql]" in result

    def test_archive_files(self):
        assert "[FILE:.tar]" in redact_sensitive("backup.tar 다운로드")
        assert "[FILE:.zip]" in redact_sensitive("release.zip 올려")
        assert "[FILE:.gz]" in redact_sensitive("logs.gz 압축")

    def test_whitelist_package_json(self):
        result = redact_sensitive("package.json은 건드리지 마세요")
        assert result == "package.json은 건드리지 마세요"

    def test_whitelist_setup_py(self):
        result = redact_sensitive("setup.py 수정해")
        assert result == "setup.py 수정해"

    def test_whitelist_docker_compose(self):
        result = redact_sensitive("docker-compose.yml 참고")
        assert result == "docker-compose.yml 참고"

    def test_whitelist_gitignore(self):
        result = redact_sensitive(".gitignore에 추가해")
        assert result == ".gitignore에 추가해"

    def test_whitelist_env_example(self):
        result = redact_sensitive(".env.example은 OK")
        assert result == ".env.example은 OK"

    def test_whitelist_firestore_rules(self):
        result = redact_sensitive("firestore.rules 확인")
        assert result == "firestore.rules 확인"


# ════════════════════════════════════════════════════════
# redact_sensitive — Dotenv Files
# ════════════════════════════════════════════════════════

class TestRedactDotenv:
    def test_plain_env(self):
        result = redact_sensitive(".env 파일 만들어줘")
        assert "[DOTENV]" in result

    def test_env_local(self):
        result = redact_sensitive(".env.local 확인")
        assert "[DOTENV]" in result

    def test_env_production(self):
        result = redact_sensitive(".env.production 배포")
        assert "[DOTENV]" in result

    def test_env_development(self):
        result = redact_sensitive(".env.development 세팅")
        assert "[DOTENV]" in result

    def test_env_example_whitelisted(self):
        result = redact_sensitive(".env.example은 OK")
        assert result == ".env.example은 OK"


# ════════════════════════════════════════════════════════
# redact_sensitive — key=value Secrets
# ════════════════════════════════════════════════════════

class TestRedactKeyValue:
    def test_password_equals(self):
        result = redact_sensitive("password=mysecretpass123")
        assert "password=[REDACTED]" in result

    def test_token_colon(self):
        result = redact_sensitive('token: "abc123def456"')
        assert "token=[REDACTED]" in result

    def test_api_key_equals(self):
        result = redact_sensitive("api_key=sk12345678")
        assert "api_key=[REDACTED]" in result

    def test_client_secret(self):
        result = redact_sensitive("client_secret: my_super_secret_value")
        assert "client_secret=[REDACTED]" in result

    def test_database_url(self):
        result = redact_sensitive("database_url=postgres://user:pass@host/db")
        assert "database_url=[REDACTED]" in result

    def test_redis_url(self):
        result = redact_sensitive("redis_url=redis://localhost:6379/0")
        assert "redis_url=[REDACTED]" in result

    def test_connection_string(self):
        result = redact_sensitive("connection_string=Server=myserver;Database=mydb")
        assert "connection_string=[REDACTED]" in result

    def test_db_password(self):
        result = redact_sensitive("DB_PASSWORD=super_secret")
        assert "DB_PASSWORD=[REDACTED]" in result

    def test_short_value_not_masked(self):
        """4자 미만 값은 마스킹하지 않음"""
        result = redact_sensitive("password=abc")
        assert result == "password=abc"

    def test_case_insensitive(self):
        result = redact_sensitive("PASSWORD=MySecret123")
        assert "PASSWORD=[REDACTED]" in result


# ════════════════════════════════════════════════════════
# redact_sensitive — No False Positives
# ════════════════════════════════════════════════════════

class TestNoFalsePositives:
    def test_plain_korean(self):
        text = "커밋하고 푸시했습니다 🦞"
        assert redact_sensitive(text) == text

    def test_url_preserved(self):
        text = "https://github.com/yuna-studio/repo"
        assert redact_sensitive(text) == text

    def test_version_number(self):
        text = "v2.1.0 릴리즈"
        assert redact_sensitive(text) == text

    def test_git_hash(self):
        text = "commit a75318b"
        assert redact_sensitive(text) == text

    def test_git_hash_longer(self):
        text = "commit c0e204e3f1"
        assert redact_sensitive(text) == text

    def test_branch_names(self):
        text = "main 브랜치에서 dev로 머지했어요"
        assert redact_sensitive(text) == text

    def test_port_number(self):
        text = "포트 3000에서 서버 실행"
        assert redact_sensitive(text) == text

    def test_emoji(self):
        text = "완료! 🎉🔥✅"
        assert redact_sensitive(text) == text

    def test_code_snippet(self):
        text = "```python\nprint('hello')\n```"
        assert redact_sensitive(text) == text

    def test_markdown_table(self):
        text = "| 이름 | 값 |\n|---|---|\n| test | ok |"
        assert redact_sensitive(text) == text

    def test_twitter_mention(self):
        text = "@elonmusk가 뭐라고 했어"
        assert redact_sensitive(text) == text

    def test_http_url_not_path(self):
        """URL은 절대경로로 오인하지 않음 (https://로 시작)"""
        text = "https://docs.google.com/spreadsheets/d/abc123"
        result = redact_sensitive(text)
        # URL 자체는 대부분 유지 (경로 패턴에 안 걸림)
        assert "google.com" in result

    def test_regular_numbers(self):
        text = "총 9664개 파일 삭제"
        assert redact_sensitive(text) == text

    def test_date_format(self):
        text = "2026-02-15 오후 3시"
        assert redact_sensitive(text) == text


# ════════════════════════════════════════════════════════
# redact_sensitive — Mixed / Complex Cases
# ════════════════════════════════════════════════════════

class TestRedactMixed:
    def test_multiple_sensitive_items(self):
        text = "Connect to 10.0.0.5 with key sk-abcdefghijklmnopqrstuvwxyz and file /home/user/secrets/api.key"
        result = redact_sensitive(text)
        assert "[IP_ADDR]" in result
        assert "[API_KEY]" in result
        assert "…/api.key" in result

    def test_email_and_phone(self):
        text = "연락처: user@test.com / 010-1234-5678"
        result = redact_sensitive(text)
        assert "[EMAIL]" in result
        assert "[PHONE]" in result

    def test_path_and_token_same_line(self):
        text = "파일 /Users/me/.ssh/id_rsa.pem 에서 ghp_ABCDEFghijklmnop1234567890abcdef 추출"
        result = redact_sensitive(text)
        assert "[GITHUB_TOKEN]" in result
        assert "…/id_rsa.pem" in result

    def test_multiline_sensitive(self):
        text = "서버: 192.168.1.1\n이메일: admin@corp.com\n비번: password=hunter2222"
        result = redact_sensitive(text)
        assert "[IP_ADDR]" in result
        assert "[EMAIL]" in result
        assert "password=[REDACTED]" in result

    def test_korean_with_sensitive(self):
        text = "대표님 010-9999-8888로 전화드릴게요. API키는 sk-proj-testkey1234567890abcdef 입니다"
        result = redact_sensitive(text)
        assert "[PHONE]" in result
        assert "[API_KEY]" in result
        assert "대표님" in result


# ════════════════════════════════════════════════════════
# extract_text
# ════════════════════════════════════════════════════════

class TestExtractText:
    def test_string_content(self):
        assert extract_text("hello") == "hello"

    def test_list_of_text_parts(self):
        content = [
            {"type": "text", "text": "첫 번째"},
            {"type": "text", "text": "두 번째"},
        ]
        assert extract_text(content) == "첫 번째\n두 번째"

    def test_list_with_image_parts(self):
        content = [
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
            {"type": "text", "text": "이미지 설명"},
        ]
        assert extract_text(content) == "이미지 설명"

    def test_list_of_strings(self):
        content = ["hello", "world"]
        assert extract_text(content) == "hello\nworld"

    def test_empty_list(self):
        assert extract_text([]) == ""

    def test_non_standard_type(self):
        assert extract_text(12345) == "12345"


# ════════════════════════════════════════════════════════
# clean_message (integration)
# ════════════════════════════════════════════════════════

class TestCleanMessage:
    def _make_entry(self, role, content, entry_type="message", model=None):
        entry = {
            "type": entry_type,
            "timestamp": "2026-02-15T14:00:00Z",
            "id": "test-id-123",
            "message": {
                "role": role,
                "content": content,
            },
        }
        if model:
            entry["message"]["model"] = model
        return entry

    def test_normal_user_message(self):
        entry = self._make_entry("user", "안녕하세요")
        result = clean_message(entry)
        assert result is not None
        assert result["role"] == "user"
        assert result["content"] == "안녕하세요"

    def test_normal_assistant_message(self):
        entry = self._make_entry("assistant", "반갑습니다!", model="claude-opus")
        result = clean_message(entry)
        assert result is not None
        assert result["role"] == "assistant"
        assert result["content"] == "반갑습니다!"
        assert result["model"] == "claude-opus"

    def test_skip_system_role(self):
        entry = self._make_entry("system", "You are a helpful assistant")
        assert clean_message(entry) is None

    def test_skip_tool_role(self):
        entry = self._make_entry("tool", "function result")
        assert clean_message(entry) is None

    def test_skip_session_type(self):
        entry = self._make_entry("user", "hello", entry_type="session")
        assert clean_message(entry) is None

    def test_skip_model_change(self):
        entry = self._make_entry("user", "hello", entry_type="model_change")
        assert clean_message(entry) is None

    def test_skip_thinking_level_change(self):
        entry = self._make_entry("user", "hello", entry_type="thinking_level_change")
        assert clean_message(entry) is None

    def test_skip_custom_type(self):
        entry = self._make_entry("user", "hello", entry_type="custom")
        assert clean_message(entry) is None

    def test_skip_heartbeat_ok(self):
        entry = self._make_entry("assistant", "HEARTBEAT_OK")
        assert clean_message(entry) is None

    def test_skip_no_reply(self):
        entry = self._make_entry("assistant", "NO_REPLY")
        assert clean_message(entry) is None

    def test_skip_system_injected_user(self):
        entry = self._make_entry("user", "Pre-compaction memory flush. Store durable memories now...")
        assert clean_message(entry) is None

    def test_skip_heartbeat_user(self):
        entry = self._make_entry("user", "Read HEARTBEAT.md if it exists...")
        assert clean_message(entry) is None

    def test_strip_think_from_assistant(self):
        entry = self._make_entry("assistant", "<think>reasoning</think>실제 답변")
        result = clean_message(entry)
        assert result is not None
        assert result["content"] == "실제 답변"

    def test_strip_final_from_assistant(self):
        entry = self._make_entry("assistant", "<final>실제 답변</final>")
        result = clean_message(entry)
        assert result is not None
        assert result["content"] == "실제 답변"

    def test_strip_think_and_final(self):
        entry = self._make_entry("assistant", "<think>reason</think><final>답변</final>")
        result = clean_message(entry)
        assert result is not None
        assert result["content"] == "답변"

    def test_strip_meta_from_user(self):
        text = 'Conversation info (untrusted metadata):\n```json\n{"chat_type":"direct"}\n```\n실제 질문'
        entry = self._make_entry("user", text)
        result = clean_message(entry)
        assert result is not None
        assert result["content"] == "실제 질문"

    def test_redact_in_user_message(self):
        entry = self._make_entry("user", "내 이메일은 ceo@company.com 이야")
        result = clean_message(entry)
        assert result is not None
        assert "[EMAIL]" in result["content"]
        assert "ceo@company.com" not in result["content"]

    def test_redact_in_assistant_message(self):
        entry = self._make_entry("assistant", "서버 IP는 192.168.1.50 입니다")
        result = clean_message(entry)
        assert result is not None
        assert "[IP_ADDR]" in result["content"]

    def test_empty_after_cleaning(self):
        entry = self._make_entry("assistant", "<think>only thinking</think>")
        assert clean_message(entry) is None

    def test_empty_content(self):
        entry = self._make_entry("user", "")
        assert clean_message(entry) is None

    def test_list_content(self):
        content = [
            {"type": "text", "text": "이미지를 확인해주세요"},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
        ]
        entry = self._make_entry("user", content)
        result = clean_message(entry)
        assert result is not None
        assert "이미지를 확인해주세요" in result["content"]


# ════════════════════════════════════════════════════════
# Edge Cases — Tricky patterns
# ════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_path_inside_backticks(self):
        """백틱 안의 경로도 마스킹"""
        result = redact_sensitive("`/Users/me/secret/config.json`")
        assert "config.json" in result
        assert "/Users/me" not in result

    def test_multiple_emails_same_line(self):
        result = redact_sensitive("from: a@b.com, to: c@d.com, cc: e@f.com")
        assert result.count("[EMAIL]") == 3

    def test_multiple_phones_same_line(self):
        result = redact_sensitive("집: 02-111-2222 / 폰: 010-3333-4444")
        assert result.count("[PHONE]") == 2

    def test_redaction_preserves_structure(self):
        text = "이름: 홍길동\n전화: 010-1234-5678\n이메일: hong@test.com"
        result = redact_sensitive(text)
        assert "이름: 홍길동" in result
        assert "[PHONE]" in result
        assert "[EMAIL]" in result

    def test_empty_string(self):
        assert redact_sensitive("") == ""

    def test_only_whitespace(self):
        assert redact_sensitive("   ") == "   "

    def test_very_long_text(self):
        """긴 텍스트에서도 성능 문제 없이 동작"""
        text = "일반 텍스트. " * 1000 + "secret@email.com"
        result = redact_sensitive(text)
        assert "[EMAIL]" in result

    def test_unicode_preservation(self):
        """이모지, 특수문자 보존"""
        text = "완료 ✅🎉🦞 좋아요 👍"
        assert redact_sensitive(text) == text

    def test_json_string_with_secrets(self):
        text = '{"api_key": "sk-abcdefghijklmnopqrstuvwxyz1234", "name": "test"}'
        result = redact_sensitive(text)
        assert "[API_KEY]" in result
        assert "test" in result

    def test_project_redaction(self):
        """커스텀 프로젝트 치환은 딕셔너리에 추가 시 동작"""
        # _PROJECT_REDACTIONS가 비어있으므로 아무 변화 없음
        text = "project-id-123"
        assert redact_sensitive(text) == text


# ════════════════════════════════════════════════════════
# Run
# ════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
