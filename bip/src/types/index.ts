export interface ChatLog {
  id: string;
  role: "user" | "assistant" | "home" | "system";
  content: string;
  timestamp: string; // ISO 8601 string
  model?: string;
  agent?: string;
}
