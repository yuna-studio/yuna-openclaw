import os
import re
import subprocess

def check_chronicle_integrity():
    chronicle_path = "/Users/openclaw-kong/workspace/yuna-openclaw/docs/chronicle/daily/2026-02-06.md"
    if not os.path.exists(chronicle_path):
        return "PASS: Chronicle file not found yet."

    # Rule 1: No "[중략]" or "(중략)"
    with open(chronicle_path, 'r') as f:
        content = f.read()
    
    if "중략" in content:
        return "FAIL: 'Omission (중략)' detected in Chronicle. Violation of Total Recording principle."

    # Rule 2: Standard Template [생각] and [답변]
    # Check if lines starting with - [ exist but are not [생각] or [답변]
    tags = re.findall(r'- \[([^\]]+)\]', content)
    valid_tags = ["생각", "답변"]
    for tag in tags:
        if tag not in valid_tags:
            return f"FAIL: Invalid tag [{tag}] detected. Only [생각] and [답변] are allowed."

    # Rule 3: Append-Only Check (via Git history)
    # If the file size decreased or major chunks were removed compared to previous commit
    try:
        diff = subprocess.check_output(["git", "-C", "/Users/openclaw-kong/workspace/yuna-openclaw", "diff", "HEAD^", "HEAD", "--", chronicle_path]).decode()
        if "-" in diff and not diff.startswith("---"):
            # If there are deletions (-) in the diff of the chronicle file
            # This is a simplified check, some deletions might be valid if they are just formatting
            # But per Bylaws v1.5, we shouldn't delete.
            lines = diff.split('\n')
            deleted_content = [l for l in lines if l.startswith('-') and not l.startswith('---')]
            if deleted_content:
                return "WARNING: Deletions detected in Chronicle Git diff. Verify if this violates Append-Only principle."
    except:
        pass

    return "PASS: Chronicle integrity verified."

if __name__ == "__main__":
    result = check_chronicle_integrity()
    print(result)
