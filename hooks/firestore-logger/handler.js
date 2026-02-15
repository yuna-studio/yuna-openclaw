import admin from 'firebase-admin';
import { getApps, initializeApp, cert } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';

// Singleton Firebase Init
function getDb() {
  if (getApps().length === 0) {
    const serviceAccount = JSON.parse(process.env.FIREBASE_PRIVATE_KEY_JSON || '{}');
    initializeApp({
      credential: cert(serviceAccount)
    });
  }
  return getFirestore();
}

export default async function firestoreLogger(event) {
  try {
    const db = getDb();
    const logData = {
      timestamp: new Date(),
      type: event.type,
      sessionKey: event.sessionKey || 'unknown',
      payload: event
    };
    
    // 민감 정보 제거 (Optional)
    // if (logData.payload.context) delete logData.payload.context.env;

    await db.collection('chat_logs').add(logData);
    // console.log(`🔥 [Firestore Hook] Logged event: ${event.type}`);
  } catch (err) {
    console.error(`❌ [Firestore Hook] Error: ${err.message}`);
  }
}
