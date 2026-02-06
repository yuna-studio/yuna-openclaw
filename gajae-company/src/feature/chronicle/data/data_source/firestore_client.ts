import { getFirestore, collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { firebaseApp } from '@/core/config/firebase-config';

/**
 * [가재 컴퍼니] Firestore Write Tool (v1.0)
 * 의도: AI 에이전트가 생성한 로그(Command/Meeting)를 Firestore에 직접 박제하기 위한 유틸리티.
 */

export const writeChronicleToFirestore = async (data: {
    date: string,
    time: string,
    title: string,
    type: 'command' | 'meeting' | 'pulse',
    content: string,
    rawPath: string
}) => {
    const db = getFirestore(firebaseApp);
    try {
        const docRef = await addDoc(collection(db, "chronicles"), {
            ...data,
            id: crypto.randomUUID(),
            createdAt: serverTimestamp()
        });
        console.log("Document written with ID: ", docRef.id);
        return docRef.id;
    } catch (e) {
        console.error("Error adding document: ", e);
        throw e;
    }
};
