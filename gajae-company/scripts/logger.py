import firebase_admin
from firebase_admin import credentials, firestore
import re
import uuid
import sys
import os
from datetime import datetime

# [가재 컴퍼니] Standard Intelligence Logger (Python v2.0)
# 의도: 마크다운 구조를 정밀 분석하여 Firestore의 정규화된 필드에 지능을 박제함.

SERVICE_ACCOUNT_PATH = '/Users/openclaw-kong/.openclaw/workspace/firebase-service-account.json'

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)

def parse_markdown(content, log_type):
    result = {'rawContent': content}
    
    # Extract Time
    time_match = re.search(r'-\s\*\*일시\*\*:\s(?:.*?)\s(?:(\d{2}:\d{2}:\d{2})|(\d{2}:\d{2}))', content)
    result['time'] = time_match.group(1) or time_match.group(2) if time_match else "00:00"

    # Fivefold Protocol Sections
    protocol = {}
    sections = [
        ('intent', r'1\.\s\*\*의도\s\(Intention\)\*\*:\s([\s\S]*?)(?=\n\d\.|$)'),
        ('psychology', r'2\.\s\*\*심리\s\(Psychology\)\*\*:\s([\s\S]*?)(?=\n\d\.|$)'),
        ('thought', r'3\.\s\*\*생각\s\(Thought\)\*\*:\s([\s\S]*?)(?=\n\d\.|$)'),
        ('action', r'4\.\s\*\*행동\s\(Action\)\*\*:\s([\s\S]*?)(?=\n\d\.|$)'),
        ('response', r'5\.\s\*\*답변\s\(Response\)\*\*:\s([\s\S]*?)(?=\n\d\.|$)'),
    ]

    for key, pattern in sections:
        match = re.search(pattern, content)
        protocol[key] = match.group(1).strip() if match else ""

    if log_type == 'command':
        instr_match = re.search(r'##\s📜\s지시\s내용\s\(Command\)\n([\s\S]*?)(?=\n---|$)', content)
        result['instruction'] = instr_match.group(1).strip() if instr_match else ""
        result['execution'] = protocol
    else:
        host_match = re.search(r'-\s\*\*주관\*\*:\s(.*?)\n', content)
        result['host'] = host_match.group(1).strip() if host_match else ""
        part_match = re.search(r'-\s\*\*참석\*\*:\s(.*?)\n', content)
        result['participants'] = [p.strip() for p in part_match.group(1).split(',')] if part_match else []
        result['details'] = protocol

    return result

def log_to_firestore(log_type, title, author, content):
    init_firebase()
    db = firestore.client()
    
    parsed = parse_markdown(content, log_type)
    collection = 'commands' if log_type == 'command' else 'meetings'
    
    doc_id = str(uuid.uuid4())
    data = {
        'id': doc_id,
        'date': datetime.now().strftime("%Y%m%d"),
        'title': title,
        'author': author,
        'createdAt': firestore.SERVER_TIMESTAMP,
        **parsed
    }

    db.collection(collection).document(doc_id).set(data)
    print(f"✅ Log structured and persisted to [{collection}]: {doc_id}")

if __name__ == "__main__":
    if len(sys.argv) >= 5:
        log_to_firestore(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Usage: python3 scripts/logger.py <command|meeting> <title> <author> <content>")
