"use client";

import { useEffect } from "react";
import { UI_TEXT } from "@/lib/constants";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background text-text-primary p-4">
      <h2 className="text-xl font-bold mb-4 text-status-live">{UI_TEXT.SYSTEM_ERROR}</h2>
      <p className="text-text-muted mb-8 text-center max-w-md font-mono text-sm">
        {error.message || UI_TEXT.UNEXPECTED_ERROR}
      </p>
      <button
        onClick={() => reset()}
        className="px-6 py-3 bg-white border border-gray-300 rounded-lg hover:border-primary transition-colors text-sm font-mono shadow-sm"
      >
        {UI_TEXT.RETRY}
      </button>
    </div>
  );
}
