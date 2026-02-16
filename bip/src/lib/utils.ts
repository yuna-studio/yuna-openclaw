import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { formatDistanceToNow } from "date-fns";
import { ko } from "date-fns/locale";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// 상대 시간 포맷터 (예: "방금 전", "3분 전")
export function formatRelativeTime(dateString: string): string {
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return "";
    
    return formatDistanceToNow(date, { 
      addSuffix: true, 
      locale: ko 
    });
  } catch (e) {
    return "";
  }
}

// 라이브 활성 상태 체크 (30분 기준)
export function checkIsActive(lastTimestamp?: string): boolean {
  if (!lastTimestamp) return false;
  try {
    const date = new Date(lastTimestamp);
    if (isNaN(date.getTime())) return false;
    
    const diff = Date.now() - date.getTime();
    return diff < 1000 * 60 * 30; // 30분 이내
  } catch (e) {
    return false;
  }
}
