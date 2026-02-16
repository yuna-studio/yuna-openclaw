export interface ChatLog {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string; // ISO 8601 string
  model?: string;
  agent?: string;
}

export type ReactionType = "heart" | "lol";

export interface LiveStatus {
  isActive: boolean;
  lastActive: string; // Relative time string
}

export interface Particle {
  id: number;
  x: number;
  y: number;
  emoji: string;
  rotation: number;
}
