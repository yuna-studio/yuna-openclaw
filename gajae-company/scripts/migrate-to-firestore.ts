import admin from 'firebase-admin';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

/**
 * [가재 컴퍼니] Firestore Migration Script (v1.2)
 * 의도: 로컬 Markdown 파일 기반의 연대기를 Firestore로 이전하여 실시간성 및 확장성 확보.
 * 수정: Service Account Key를 명시적으로 로드하여 인증 문제 해결.
 */

// WARNING: In a real environment, you'd use environment variables or a secure vault.
// For this session, I will check if a service account key exists in the workspace.
const SERVICE_ACCOUNT_PATH = '/Users/openclaw-kong/.openclaw/workspace/firebase-service-account.json';

if (!admin.apps.length) {
    if (fs.existsSync(SERVICE_ACCOUNT_PATH)) {
        const serviceAccount = JSON.parse(fs.readFileSync(SERVICE_ACCOUNT_PATH, 'utf8'));
        admin.initializeApp({
            credential: admin.credential.cert(serviceAccount),
            projectId: 'gajae-company-bip'
        });
        console.log('✅ Initialized Firebase Admin with Service Account.');
    } else {
        // Fallback to application default (may fail if not logged in via gcloud)
        admin.initializeApp({
            projectId: 'gajae-company-bip'
        });
        console.log('⚠️ Initialized Firebase Admin with default credentials.');
    }
}

const db = admin.firestore();

async function migrateChronicles() {
    const workspaceRoot = '/Users/openclaw-kong/.openclaw/workspace/';
    const dailyBase = path.join(workspaceRoot, 'docs/chronicle/daily');
    
    if (!fs.existsSync(dailyBase)) {
        throw new Error(`Directory not found: ${dailyBase}`);
    }

    const dates = fs.readdirSync(dailyBase).filter(f => {
        try {
            return fs.statSync(path.join(dailyBase, f)).isDirectory();
        } catch (e) { return false; }
    });

    console.log(`🚀 Found ${dates.length} days of records. Starting migration...`);

    const batch = db.batch();
    let count = 0;

    for (const date of dates) {
        const types = ['command', 'meeting'];
        for (const type of types) {
            const typePath = path.join(dailyBase, date, type);
            if (!fs.existsSync(typePath)) continue;

            const files = fs.readdirSync(typePath).filter(f => f.endsWith('.md'));
            
            for (const file of files) {
                const filePath = path.join(typePath, file);
                const content = fs.readFileSync(filePath, 'utf8');
                
                const titleMatch = content.match(/^# (?:👑 CEO 지시 기록|🤝 협업 회의록): \[(.*?)\]/m);
                const title = titleMatch ? titleMatch[1] : file.replace('.md', '');
                
                const timeMatch = content.match(/- \*\*일시\*\*: (?:.*?) (?:(\d{2}:\d{2}:\d{2})|(\d{2}:\d{2}))/);
                const time = timeMatch ? (timeMatch[1] || timeMatch[2]) : "00:00";

                const docId = crypto.createHash('md5').update(`${date}-${type}-${file}`).digest('hex');
                const docRef = db.collection('chronicles').doc(docId);

                batch.set(docRef, {
                    id: docId,
                    date: date.replace(/-/g, ''), // YYYYMMDD
                    time: time,
                    title: title,
                    type: type,
                    content: content,
                    rawPath: filePath.replace(workspaceRoot, ''),
                    createdAt: admin.firestore.FieldValue.serverTimestamp()
                });
                
                count++;
                if (count % 400 === 0) {
                    await batch.commit();
                    console.log(`📦 Committed batch (${count} records)`);
                }
            }
        }
    }
    
    await batch.commit();
    console.log(`✅ Migration completed. Total ${count} records uploaded.`);
}

migrateChronicles().catch(async (e) => {
    console.error('❌ Migration failed:', e);
});
