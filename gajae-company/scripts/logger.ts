import { initializeApp, cert } from 'firebase-admin/app';
import { getFirestore, FieldValue } from 'firebase-admin/firestore';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

/**
 * [가재 컴퍼니] Standard Intelligence Logger (v2.0)
 * 의도: 마크다운 구조를 분석하여 Firestore의 정규화된 필드에 지능을 박제함.
 * 정책: 'commands'와 'meetings' 컬렉션을 분리하고 구조화된 데이터(JSON)로 저장.
 */

const SERVICE_ACCOUNT_PATH = '/Users/openclaw-kong/.openclaw/workspace/firebase-service-account.json';

if (!fs.existsSync(SERVICE_ACCOUNT_PATH)) {
    console.error("❌ Error: Firebase Service Account key not found.");
    process.exit(1);
}

const serviceAccount = JSON.parse(fs.readFileSync(SERVICE_ACCOUNT_PATH, 'utf8'));

initializeApp({
    credential: cert(serviceAccount),
    projectId: 'gajae-company-bip'
});

const db = getFirestore();

interface FivefoldProtocol {
    intent: string;
    psychology: string;
    thought: string;
    action: string;
    response: string;
}

function parseMarkdown(content: string, type: 'command' | 'meeting') {
    const lines = content.split('\n');
    const result: any = { rawContent: content };

    // Common Metadata Parsing
    const timeMatch = content.match(/- \*\*일시\*\*: (?:.*?) (?:(\d{2}:\d{2}:\d{2})|(\d{2}:\d{2}))/);
    result.time = timeMatch ? (timeMatch[1] || timeMatch[2]) : "00:00";

    // Fivefold Protocol Parsing
    const extractSection = (regex: RegExp) => {
        const match = content.match(regex);
        return match ? match[1].trim() : "";
    };

    const protocol: FivefoldProtocol = {
        intent: extractSection(/\d\. \*\*의도 \(Intention\)\*\*: ([\s\S]*?)(?=\n\d\.|$)/),
        psychology: extractSection(/\d\. \*\*심리 \(Psychology\)\*\*: ([\s\S]*?)(?=\n\d\.|$)/),
        thought: extractSection(/\d\. \*\*생각 \(Thought\)\*\*: ([\s\S]*?)(?=\n\d\.|$)/),
        action: extractSection(/\d\. \*\*행동 \(Action\)\*\*: ([\s\S]*?)(?=\n\d\.|$)/),
        response: extractSection(/\d\. \*\*답변 \(Response\)\*\*: ([\s\S]*?)(?=\n\d\.|$)/)
    };

    if (type === 'command') {
        result.instruction = extractSection(/## 📜 지시 내용 \(Command\)\n([\s\S]*?)(?=\n---|$)/);
        result.execution = protocol;
    } else {
        const hostMatch = content.match(/- \*\*주관\*\*: (.*?)\n/);
        result.host = hostMatch ? hostMatch[1].trim() : "";
        const participantsMatch = content.match(/- \*\*참석\*\*: (.*?)\n/);
        result.participants = participantsMatch ? participantsMatch[1].split(',').map(p => p.trim()) : [];
        result.details = protocol;
    }

    return result;
}

async function logToFirestore(type: 'command' | 'meeting', title: string, author: string, content: string) {
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0].replace(/-/g, '');
    const docId = crypto.randomUUID();
    
    const parsedData = parseMarkdown(content, type);
    const collectionName = type === 'command' ? 'commands' : 'meetings';

    const finalData = {
        id: docId,
        date: dateStr,
        title,
        author,
        ...parsedData,
        createdAt: FieldValue.serverTimestamp()
    };

    try {
        await db.collection(collectionName).doc(docId).set(finalData);
        console.log(`✅ Log structured and persisted to [${collectionName}]: ${docId}`);
        return docId;
    } catch (error) {
        console.error("❌ Failed to log to Firestore:", error);
        throw error;
    }
}

const args = process.argv.slice(2);
if (args.length >= 4) {
    const [type, title, author, content] = args;
    logToFirestore(type as any, title, author, content).catch(() => process.exit(1));
} else {
    console.log("Usage: npx tsx scripts/logger.ts <command|meeting> <title> <author> <content>");
}
