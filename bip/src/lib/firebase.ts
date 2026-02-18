import { initializeApp, getApps, getApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getDatabase } from "firebase/database";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  databaseURL: process.env.NEXT_PUBLIC_FIREBASE_DATABASE_URL,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

const hasCoreFirebaseConfig =
  !!firebaseConfig.apiKey &&
  !!firebaseConfig.authDomain &&
  !!firebaseConfig.projectId &&
  !!firebaseConfig.appId;

// SSR/Build 시 환경변수가 비어 있으면 초기화하지 않고 null 반환
const app = hasCoreFirebaseConfig
  ? !getApps().length
    ? initializeApp(firebaseConfig)
    : getApp()
  : null;

export const db: any = app ? getFirestore(app) : null;
export const rtdb: any =
  app && firebaseConfig.databaseURL
    ? (() => {
        try {
          return getDatabase(app);
        } catch {
          return null;
        }
      })()
    : null;
