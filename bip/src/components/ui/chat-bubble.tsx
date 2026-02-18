import { ChatLog } from "@/types";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { motion } from "framer-motion";
import { User, Bot, Terminal, Search, Scale } from "lucide-react";
import Image from "next/image";
import { UI_TEXT } from "@/lib/constants";

interface ChatBubbleProps {
  message: ChatLog;
  isLatest?: boolean;
  showHeader?: boolean;
}

// 에이전트별 프로필 설정
type AgentProfile = {
  name: string;
  emoji: string;
  icon: typeof Bot;
  iconColor: string;
  bgColor: string;
  bubbleBg: string;
  bubbleBorder: string;
  avatar?: string;  // 이미지 경로
};

const AGENT_PROFILES: Record<string, AgentProfile> = {
  human: {
    name: UI_TEXT.USER_NAME,
    emoji: "👤",
    icon: User,
    iconColor: "text-gray-600",
    bgColor: "bg-gray-200",
    bubbleBg: "bg-[#4A5D23]/10",
    bubbleBorder: "border-[#4A5D23]/20",
    avatar: "/profile-nangman.jpg",
  },
  main: {
    name: "비서가재 🦞",
    emoji: "🦞",
    icon: Bot,
    iconColor: "text-emerald-600",
    bgColor: "bg-emerald-50",
    bubbleBg: "bg-white",
    bubbleBorder: "border-gray-100",
    avatar: "/profile-secretary.jpg",
  },
  scout: {
    name: "탐정가재 🔍",
    emoji: "🔍",
    icon: Search,
    iconColor: "text-amber-600",
    bgColor: "bg-amber-50",
    bubbleBg: "bg-amber-50/50",
    bubbleBorder: "border-amber-200/50",
    avatar: "/profile-scout.jpg",
  },
  judge: {
    name: "판사가재 ⚖️",
    emoji: "⚖️",
    icon: Scale,
    iconColor: "text-blue-600",
    bgColor: "bg-blue-50",
    bubbleBg: "bg-blue-50/50",
    bubbleBorder: "border-blue-200/50",
    avatar: "/profile-judge.jpg",
  },
  // scout/judge의 user = 비서가재가 명령
  commander: {
    name: "비서가재 🦞",
    emoji: "🦞",
    icon: Bot,
    iconColor: "text-emerald-600",
    bgColor: "bg-emerald-50",
    bubbleBg: "bg-emerald-50/50",
    bubbleBorder: "border-emerald-200/50",
    avatar: "/profile-secretary.jpg",
  },
};

function getProfile(message: ChatLog): { profile: AgentProfile; isLeft: boolean } {
  const agent = message.agent || "main";
  
  // main의 user = 대표님 (낭만코딩)
  if (message.role === "user" && (agent === "main" || !message.agent)) {
    return { profile: AGENT_PROFILES.human, isLeft: true };
  }
  
  // main의 assistant = 비서가재
  if (message.role === "assistant" && (agent === "main" || !message.agent)) {
    return { profile: AGENT_PROFILES.main, isLeft: false };
  }

  // scout/judge의 user = 비서가재가 명령 (우측)
  if (message.role === "user" && (agent === "scout" || agent === "judge")) {
    return { profile: AGENT_PROFILES.commander, isLeft: false };
  }

  // scout/judge의 assistant = 해당 에이전트 (우측)
  if (message.role === "assistant" && agent === "scout") {
    return { profile: AGENT_PROFILES.scout, isLeft: false };
  }
  if (message.role === "assistant" && agent === "judge") {
    return { profile: AGENT_PROFILES.judge, isLeft: false };
  }

  // fallback
  return { profile: AGENT_PROFILES.main, isLeft: false };
}

function formatTime(timestamp: string): string {
  try {
    const d = new Date(timestamp);
    return d.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit", hour12: false });
  } catch {
    return "";
  }
}

function maskToken(value: string): string {
  if (!value) return value;
  if (value.length <= 8) return "****";
  return `${value.slice(0, 3)}***${value.slice(-3)}`;
}

function maskUids(text: string): string {
  let out = text;

  // uid: XXXXX / uid=XXXXX / owner_uid=XXXXX
  out = out.replace(/\b(owner[_-]?uid|uid)\b\s*[:=]\s*([A-Za-z0-9_-]{10,})/gi, (_m, key, val) => {
    return `${key}: ${maskToken(val)}`;
  });

  // JSON 형태 "uid": "XXXXX"
  out = out.replace(/("uid"\s*:\s*")([A-Za-z0-9_-]{10,})(")/gi, (_m, p1, val, p3) => {
    return `${p1}${maskToken(val)}${p3}`;
  });

  // Firebase UID처럼 보이는 28자 토큰(문장 중 노출 방지)
  out = out.replace(/\b([A-Za-z0-9]{28})\b/g, (_m, val) => maskToken(val));

  return out;
}

export function DateDivider({ date }: { date: string }) {
  return (
    <div className="flex items-center gap-3 my-6">
      <div className="flex-1 h-px bg-gray-200" />
      <span className="text-[11px] text-text-muted font-mono px-2">{date}</span>
      <div className="flex-1 h-px bg-gray-200" />
    </div>
  );
}

const markdownComponents = {
  pre({ children }: any) {
    return (
      <div className="overflow-x-auto max-w-full my-2 rounded-lg border border-gray-200 bg-gray-50">
        <pre className="p-3 text-xs font-mono whitespace-pre overflow-x-auto">
          {children}
        </pre>
      </div>
    );
  },
  code({ node, inline, className, children, ...props }: any) {
    if (inline) {
      return (
        <code className="bg-gray-100 rounded px-1 py-0.5 text-emerald-700 text-xs break-all" {...props}>
          {children}
        </code>
      );
    }
    return (
      <code className="text-xs" {...props}>
        {children}
      </code>
    );
  },
  table({ children }: any) {
    return (
      <div className="overflow-x-auto max-w-full my-2">
        <table className="text-xs border-collapse border border-gray-200 min-w-0">
          {children}
        </table>
      </div>
    );
  },
  th({ children }: any) {
    return <th className="border border-gray-200 px-2 py-1 bg-gray-50 text-left text-xs font-medium">{children}</th>;
  },
  td({ children }: any) {
    return <td className="border border-gray-200 px-2 py-1 text-xs">{children}</td>;
  },
};

export function ChatBubble({ message, isLatest, showHeader = true }: ChatBubbleProps) {
  const { profile, isLeft } = getProfile(message);
  const isSystem = message.role === "system";
  const time = formatTime(message.timestamp);
  const IconComponent = profile.icon;
  const maskedContent = maskUids(message.content || "");

  if (isSystem) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex w-full justify-center my-4"
      >
        <div className="bg-gray-100 border border-gray-200 px-4 py-1 rounded-full text-xs text-text-muted flex items-center gap-2">
          <Terminal size={12} />
          <span>{maskedContent}</span>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        "flex w-full",
        showHeader ? "mt-6" : "mt-2",
        isLeft ? "justify-start" : "justify-end"
      )}
    >
      <div
        className={cn(
          "flex flex-col min-w-0 max-w-[85%] md:max-w-[70%]",
          isLeft ? "items-start" : "items-end"
        )}
      >
        {showHeader && (
          <div className={cn("flex items-center gap-1.5 mb-1 opacity-70", isLeft ? "flex-row" : "flex-row-reverse")}>
            {profile.avatar ? (
              <div className="w-6 h-6 rounded-full overflow-hidden border border-black/5">
                <Image src={profile.avatar} alt={profile.name} width={24} height={24} className="w-full h-full object-cover" />
              </div>
            ) : (
              <div className={cn("w-5 h-5 rounded-full flex items-center justify-center border border-black/5", profile.bgColor)}>
                <IconComponent size={12} className={profile.iconColor} />
              </div>
            )}
            <span className="text-[10px] text-text-secondary font-mono">{profile.name}</span>
          </div>
        )}

        <div className={cn("flex items-end gap-1.5 min-w-0 max-w-full", isLeft ? "flex-row" : "flex-row-reverse")}>
          <div
            className={cn(
              "px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm min-w-0 max-w-full border",
              profile.bubbleBg,
              profile.bubbleBorder,
              isLeft ? "rounded-tl-none" : "rounded-tr-none"
            )}
            style={{ overflowWrap: "break-word", wordBreak: "break-word" }}
          >
            <div className="prose prose-sm max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0 overflow-hidden">
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                {maskedContent}
              </ReactMarkdown>
            </div>
          </div>

          {time && (
            <span className="text-[10px] text-text-muted font-mono shrink-0 pb-1">{time}</span>
          )}
        </div>

        {isLatest && !isLeft && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-1 mt-1 ml-1"
          >
            <span className="text-[10px] text-text-muted font-mono">{UI_TEXT.TYPING}</span>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
