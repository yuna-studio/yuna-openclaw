import { Activity } from "lucide-react";
import { UI_TEXT } from "@/lib/constants";

interface TuningLoaderProps {
  text?: string;
  size?: number;
  className?: string;
}

export function TuningLoader({
  text = UI_TEXT.SYNCING,
  size = 32,
  className = "py-40",
}: TuningLoaderProps) {
  return (
    <div className={`flex flex-col items-center justify-center gap-4 ${className}`}>
      <Activity className="text-primary animate-spin" size={size} />
      <span className="text-text-muted font-mono text-sm animate-pulse">{text}</span>
    </div>
  );
}
