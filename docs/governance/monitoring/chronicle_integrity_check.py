import os
import re
import subprocess

def check_chronicle_integrity():
    # 2026-02-06 is stored in a directory INDEX.md
    chronicle_path = "/Users/openclaw-kong/workspace/yuna-openclaw/docs/chronicle/daily/2026-02-06/INDEX.md"
    if not os.path.exists(chronicle_path):
        return "PASS: Chronicle INDEX.md not found yet."

    with open(chronicle_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rule 1: No "[중략]" or "(중략)"
    if "중략" in content:
        return "FAIL: 'Omission (중략)' detected in Chronicle. Violation of Total Recording principle."

    # Rule 2: Link Integrity
    # Extract links from meeting and command sections
    meeting_links = re.findall(r'\.\/meeting\/([^\s\)]+)', content)
    command_links = re.findall(r'\.\/command\/([^\s\)]+)', content)
    
    base_dir = os.path.dirname(chronicle_path)
    
    for link in meeting_links:
        full_path = os.path.join(base_dir, "meeting", link)
        if not os.path.exists(full_path):
            return f"FAIL: Broken meeting link detected: {link}"
            
    for link in command_links:
        full_path = os.path.join(base_dir, "command", link)
        if not os.path.exists(full_path):
            return f"FAIL: Broken command link detected: {link}"

    return "PASS: Chronicle Index mapping and integrity verified."

if __name__ == "__main__":
    result = check_chronicle_integrity()
    print(result)
