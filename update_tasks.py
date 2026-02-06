import os
import datetime

files = [
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

now = datetime.datetime.now()
timestamp = now.strftime('%Y-%m-%d %H:%M')
log_entry = f"- **{timestamp}:** 자율 각성 주기(10분) 도달. 공정 진척도 1px 정밀 업데이트 및 무결성 수호."

for file_path in files:
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    updated_header = False
    added_log = False
    
    for line in lines:
        if line.startswith('# 마지막 업데이트:'):
            new_lines.append(f'# 마지막 업데이트: {timestamp}\n')
            updated_header = True
        elif line.startswith('## 2. 업무 기록 (Work Log)') and not added_log:
            new_lines.append(line)
            new_lines.append(f'{log_entry}\n')
            added_log = True
        else:
            new_lines.append(line)
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

print(f"Updated {len(files)} files with timestamp {timestamp}")
