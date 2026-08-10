"use client";

import { useState, useCallback, useRef } from "react";
import { ApiError } from "@/lib/types";
import { MAX_RETRIES } from "@/lib/constants";

interface UseApiCallReturn<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  execute: (...args: unknown[]) => Promise<T | null>;
  retry: () => Promise<T | null>;
  canRetry: boolean;
  reset: () => void;
}

export function useApiCall<T>(
  apiFunction: (...args: unknown[]) => Promise<T>
): UseApiCallReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const lastArgsRef = useRef<unknown[]>([]);

  const canRetry = retryCount < MAX_RETRIES;

  const execute = useCallback(
    async (...args: unknown[]): Promise<T | null> => {
      lastArgsRef.current = args;
      setLoading(true);
      setError(null);
      setRetryCount(0);

      try {
        const result = await apiFunction(...args);
        setData(result);
        setLoading(false);
        return result;
      } catch (err) {
        const apiErr = err as ApiError;
        setError(apiErr);
        setLoading(false);
        return null;
      }
    },
    [apiFunction]
  );

  const retry = useCallback(async (): Promise<T | null> => {
    if (retryCount >= MAX_RETRIES) return null;

    setRetryCount((c) => c + 1);
    setLoading(true);
    setError(null);

    try {
      const result = await apiFunction(...lastArgsRef.current);
      setData(result);
      setLoading(false);
      return result;
    } catch (err) {
      const apiErr = err as ApiError;
      setError({
        ...apiErr,
        retriesExhausted: retryCount + 1 >= MAX_RETRIES,
      });
      setLoading(false);
      return null;
    }
  }, [apiFunction, retryCount]);

  const reset = useCallback(() => {
    setData(null);
    setLoading(false);
    setError(null);
    setRetryCount(0);
  }, []);

  return { data, loading, error, execute, retry, canRetry, reset };
}
