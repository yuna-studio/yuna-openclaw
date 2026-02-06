import os
import re

def resolve_index(content):
    # Resolve completion rate
    content = re.sub(r'<<<<<<< HEAD\n- \*\*전사 공정률\*\*: \*\*(.*?)\*\*\n=======\n- \*\*전사 공정률\*\*: \*\*(.*?)\*\*\n>>>>>>> .*?\n', 
                     lambda m: f"- **전사 공정률**: **{max(m.group(1), m.group(2))}**\n", content)
    
    # Resolve meeting lists (simplified: take all unique lines)
    def merge_lists(match):
        ours = match.group(1).strip().split('\n')
        theirs = match.group(2).strip().split('\n')
        combined = list(dict.fromkeys(ours + theirs)) # Keep order, unique
        return '\n'.join(combined) + '\n'

    content = re.sub(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> .*?\n', merge_lists, content, flags=re.DOTALL)
    return content

def resolve_task(content):
    # Resolve last update
    content = re.sub(r'<<<<<<< HEAD\n# 마지막 업데이트: (.*?)\n=======\n# 마지막 업데이트: (.*?)\n>>>>>>> .*?\n', 
                     lambda m: f"# 마지막 업데이트: {max(m.group(1), m.group(2))}\n", content)
    
    # Resolve work log
    def merge_logs(match):
        ours = match.group(1).strip().split('\n')
        theirs = match.group(2).strip().split('\n')
        combined = list(dict.fromkeys(ours + theirs))
        # Sort logs by timestamp (descending usually)
        combined.sort(reverse=True)
        return '\n'.join(combined) + '\n'

    content = re.sub(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> .*?\n', merge_logs, content, flags=re.DOTALL)
    return content

# Files to resolve
files = [
    'docs/chronicle/daily/2026-02-06/INDEX.md',
    'docs/task/attendant.md',
    'docs/task/ba.md',
    'docs/task/cs.md',
    'docs/task/dev.md',
    'docs/task/host.md',
    'docs/task/hr.md',
    'docs/task/legal.md',
    'docs/task/marketing.md',
    'docs/task/pm.md',
    'docs/task/po.md',
    'docs/task/qa.md',
    'docs/task/ux.md'
]

for f_path in files:
    if not os.path.exists(f_path): continue
    with open(f_path, 'r') as f:
        content = f.read()
    
    if 'INDEX.md' in f_path:
        new_content = resolve_index(content)
    else:
        new_content = resolve_task(content)
    
    with open(f_path, 'w') as f:
        f.write(new_content)
    print(f"Resolved {f_path}")
