import { initializeApp } from "firebase/app";
import { getFirestore, doc, setDoc, serverTimestamp, collection, query, orderBy, limit, onSnapshot, addDoc } from "firebase/firestore";
import * as dotenv from 'dotenv';
import * as path from 'path';
import crypto from 'crypto';

/**
 * [가재 컴퍼니] Standard Swarm Logger (v9.0 - Stream & Dashboard)
 * 의도: 대표님의 지시에 따라 명령과 로그를 분리하고, 글로벌 스트림 방식을 채택함.
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
     * 1. 명령(Blueprint) 생성
     */
    static async openCommand(instruction: string) {
        const now = new Date();
        const docId = `cmd-${now.getTime()}`;
        await setDoc(doc(db, "commands", docId), {
            id: docId,
            instruction,
            status: 'TODO',
            date: now.toISOString().split('T')[0].replace(/-/g, ''),
            time: now.toTimeString().split(' ')[0],
            createdAt: serverTimestamp()
        });
        return docId;
    }

    /**
     * 2. 글로벌 지능 스트림(Logs) 박제
     */
    static async log(data: {
        type: string,
        commandId?: string,
        taskId?: string,
        intent: string,
        psychology: string,
        thought: string,
        from: string,
        to: string[],
        text: string
    }) {
        const logId = `log-${crypto.randomUUID().substring(0, 8)}`;
        const entry = {
            id: logId,
            ...data,
            response: {
                from: data.from,
                to: data.to,
                text: data.text
            },
            timestamp: new Date().toTimeString().split(' ')[0],
            createdAt: serverTimestamp()
        };
        // logs를 서브컬렉션이 아닌 탑레벨 컬렉션으로 관리 (글로벌 스트림)
        await setDoc(doc(db, "intelligence_stream", logId), entry);
        console.log(`📡 Log [${logId}] streamed.`);
        return logId;
    }

    /**
     * 3. 태스크 대시보드 업데이트
     */
    static async upsertTask(commandId: string, task: any) {
        const taskId = task.id || `task-${crypto.randomUUID().substring(0, 8)}`;
        const data = {
            ...task,
            id: taskId,
            commandId,
            updatedAt: serverTimestamp()
        };
        if (!task.id) data.createdAt = serverTimestamp();
        
        await setDoc(doc(db, "all_tasks", taskId), data, { merge: true });
        console.log(`🎯 Task [${taskId}] on Dashboard.`);
        return taskId;
    }
}

async function run() {
    const args = process.argv.slice(2);
    const mode = args[0];

    if (mode === 'open') {
        const id = await SwarmLogger.openCommand(args[1]);
        console.log(`CMD_ID:${id}`);
    } else if (mode === 'log') {
        const [_, type, cmdId, taskId, intent, psychology, thought, from, toStr, text] = args;
        await SwarmLogger.log({
            type,
            commandId: cmdId === 'null' ? undefined : cmdId,
            taskId: taskId === 'null' ? undefined : taskId,
            intent, psychology, thought, from,
            to: toStr.split(',').map(s => s.trim()),
            text
        });
    } else if (mode === 'task') {
        const [_, cmdId, taskJson] = args;
        await SwarmLogger.upsertTask(cmdId, JSON.parse(taskJson));
    }
}

if (require.main === module) {
    run().catch(e => { console.error(e); process.exit(1); });
}
