import { initializeApp } from "firebase/app";
import { getFirestore, doc, setDoc, serverTimestamp, updateDoc, arrayUnion } from "firebase/firestore";
import * as dotenv from 'dotenv';
import * as path from 'path';
import crypto from 'crypto';

/**
 * [가재 컴퍼니] Standard Swarm Logger (v8.0 - Conversation Centric)
 * 의도: 대표님의 지시에 따라 타이틀/공정을 걷어내고 'logs' 중심의 대화록 박제 시스템 구축.
 */

dotenv.config({ path: path.resolve(__dirname, '../.env.local') });

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export class SwarmLogger {
    /**
     * 1. 명령 세션 개설 (타이틀 없이 원문만 사용)
     */
    static async openCommand(origin: 'ceo' | 'system', instruction: string) {
        const now = new Date();
        const docId = `cmd-${now.getTime()}`;
        await setDoc(doc(db, "commands", docId), {
            id: docId,
            origin,
            instruction,
            logs: [],
            date: now.toISOString().split('T')[0].replace(/-/g, ''),
            time: now.toTimeString().split(' ')[0],
            status: 'active',
            createdAt: serverTimestamp()
        });
        return docId;
    }

    /**
     * 2. 대화 로그(Utterance) 추가
     */
    static async addLog(commandId: string, log: {
        intent: string,
        psychology: string,
        thought: string,
        from: string,
        to: string[],
        text: string
    }) {
        const logId = crypto.randomUUID();
        const entry = {
            id: logId,
            intent: log.intent,
            psychology: log.psychology,
            thought: log.thought,
            response: {
                from: log.from,
                to: log.to,
                text: log.text
            },
            timestamp: new Date().toTimeString().split(' ')[0]
        };
        await updateDoc(doc(db, "commands", commandId), {
            logs: arrayUnion(entry)
        });
        return logId;
    }

    /**
     * 3. 세션 종료
     */
    static async resolve(commandId: string) {
        await updateDoc(doc(db, "commands", commandId), {
            status: 'resolved'
        });
    }
}

async function run() {
    const args = process.argv.slice(2);
    const mode = args[0];

    if (mode === 'open') {
        const [_, origin, instr] = args;
        const id = await SwarmLogger.openCommand(origin as any, instr);
        console.log(`CMD_ID:${id}`);
    } else if (mode === 'add') {
        const [_, cmdId, intent, psychology, thought, from, toStr, text] = args;
        await SwarmLogger.addLog(cmdId, {
            intent, psychology, thought, from,
            to: toStr.split(',').map(s => s.trim()),
            text
        });
        console.log("✅ Log Added.");
    } else if (mode === 'resolve') {
        await SwarmLogger.resolve(args[1]);
        console.log("✅ Session Resolved.");
    }
}

if (require.main === module) {
    run().catch(e => { console.error(e); process.exit(1); });
}
