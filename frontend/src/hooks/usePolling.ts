"use client";

import { useEffect, useRef, useCallback } from "react";
import { POLL_INTERVAL_MS } from "@/lib/constants";

interface UsePollingOptions {
  url: string;
  interval?: number;
  enabled: boolean;
  onData?: (data: unknown) => void;
  onComplete?: () => void;
  onError?: (error: unknown) => void;
}

export function usePolling({
  url,
  interval = POLL_INTERVAL_MS,
  enabled,
  onData,
  onComplete,
  onError,
}: UsePollingOptions) {
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const onDataRef = useRef(onData);
  const onCompleteRef = useRef(onComplete);
  const onErrorRef = useRef(onError);

  // Keep refs in sync via effect
  useEffect(() => {
    onDataRef.current = onData;
    onCompleteRef.current = onComplete;
    onErrorRef.current = onError;
  });

  const poll = useCallback(async () => {
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_BASE}${url}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      onDataRef.current?.(data);

      // Check if operation is complete
      if (data.status === "complete" || data.status === "done" || data.progress === 100) {
        onCompleteRef.current?.();
      }
    } catch (err) {
      onErrorRef.current?.(err);
    }
  }, [url]);

  useEffect(() => {
    if (!enabled) {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      return;
    }

    // Poll immediately on enable
    poll();

    // Then poll at interval
    timerRef.current = setInterval(poll, interval);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [enabled, interval, poll]);
}
