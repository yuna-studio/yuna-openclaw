#!/usr/bin/env python3
"""Firestore 프로젝트/작업 내역 시딩 스크립트"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# 서비스 계정 초기화
cred = credentials.Certificate("/Users/openclaw-kong/.openclaw/workspace/.firebase-service-account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

PROJECTS = [
    {
        "id": "vibe-coding-showcase",
        "title": "가재 컴퍼니 바이브 코딩 쇼 케이스",
        "desc": "AI와 개발자의 실시간 대화를 공개하는 라이브 쇼케이스",
        "status": "dev",
        "link": "https://gajae-company-bip.web.app",
        "order": 0,
        "createdAt": datetime(2025, 2, 16),
        "works": [
            {"title": "홈 화면 v1 기획서", "type": "기획", "url": "https://www.notion.so/309a04c6d7b081a3b1c7feb8a9fe1829", "order": 0},
            {"title": "홈 화면 v2 리뉴얼 기획서", "type": "기획", "url": "https://www.notion.so/309a04c6d7b081dd8c1cddc3fa3adc98", "order": 1},
            {"title": "라이브 페이지 설계서", "type": "설계", "url": "https://www.notion.so/308a04c6d7b0811fa9bdd02a2fbc6367", "order": 2},
            {"title": "라이브 페이지 개발 + 18단계 검수", "type": "개발", "url": "", "order": 3},
            {"title": "홈 리뉴얼 개발 (RPG 대사창, 조직도)", "type": "개발", "url": "", "order": 4},
            {"title": "Firebase Hosting 배포", "type": "배포", "url": "https://gajae-company-bip.web.app", "order": 5},
        ],
    },
]

def seed():
    for project in PROJECTS:
        works = project.pop("works")
        pid = project.pop("id")
        project["updatedAt"] = firestore.SERVER_TIMESTAMP

        # 프로젝트 문서
        doc_ref = db.collection("projects").document(pid)
        doc_ref.set(project)
        print(f"✅ Project: {pid}")

        # 작업 문서 (subcollection)
        for work in works:
            work["createdAt"] = firestore.SERVER_TIMESTAMP
            _, work_ref = doc_ref.collection("works").add(work)
            print(f"  📄 Work: {work['title']} ({work_ref.id})")

    print("\n🦞 시딩 완료!")

if __name__ == "__main__":
    seed()
