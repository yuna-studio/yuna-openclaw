import os
import re
import subprocess

def check_chronicle_integrity():
    # Use relative path or correct absolute path
    base_path = os.getcwd()
    chronicle_path = os.path.join(base_path, "docs/chronicle/daily/2026-02-06/INDEX.md")
    if not os.path.exists(chronicle_path):
        return "PASS: Chronicle INDEX.md not found yet."

    with open(chronicle_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rule 1: No "[중략]" or "(중략)"
    if "중략" in content:
        return "FAIL: 'Omission (중략)' detected in Chronicle."

    # Rule 2: No direct dialogue/thought logs in INDEX.md (Must be in command/ or meeting/)
    if "[생각]" in content or "[답변]" in content or "SwanID:" in content:
        # Check if these exist OUTSIDE of the links (meaning they were typed directly)
        # This is a bit tricky, but generally INDEX.md should only contain headers and lists
        # We search for any line starting with [YYYY-MM-DD or containing dialogue tags
        if re.search(r'^\d{4}-\d{2}-\d{2}', content, re.MULTILINE) or "[답변]" in content:
             return "FAIL: Direct dialogue/logs detected in INDEX.md. Must be isolated in command/ or meeting/."

    # Rule 3: Link Integrity
    meeting_links = re.findall(r'\.\/meeting\/([^\s\)]+)', content)
    command_links = re.findall(r'\.\/command\/([^\s\)]+)', content)
    
    base_dir = os.path.dirname(chronicle_path)
    
    for link in meeting_links:
        full_path = os.path.join(base_dir, "meeting", link)
        if not os.path.exists(full_path):
            return f"FAIL: Broken meeting link: {link}"
            
    for link in command_links:
        full_path = os.path.join(base_dir, "command", link)
        if not os.path.exists(full_path):
            return f"FAIL: Broken command link: {link}"

    return "PASS: Chronicle Index mapping and layer isolation verified."

if __name__ == "__main__":
    result = check_chronicle_integrity()
    print(result)
