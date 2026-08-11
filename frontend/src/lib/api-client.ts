import { ApiError } from "./types";
import { API_TIMEOUT_MS, MAX_RETRIES } from "./constants";
import { sleep } from "./utils";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || (() => {
  console.warn("[api-client] NEXT_PUBLIC_API_URL not set, falling back to API Gateway");
  return "https://asq6n6kw78.execute-api.us-east-1.amazonaws.com";
})();

interface ApiOptions {
  timeout?: number;
  retries?: number;
  headers?: Record<string, string>;
}

function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  // Read user from zustand persisted state
  try {
    const stored = localStorage.getItem("auth-store");
    if (stored) {
      const parsed = JSON.parse(stored);
      const user = parsed?.state?.user;
      if (user) return { "X-User": user };
    }
  } catch {
    // ignore
  }
  return {};
}

async function request<T>(
  method: "GET" | "POST" | "PUT" | "DELETE",
  path: string,
  body?: unknown,
  opts: ApiOptions = {}
): Promise<T> {
  const timeout = opts.timeout ?? API_TIMEOUT_MS;
  const maxRetries = opts.retries ?? MAX_RETRIES;
  let lastError: ApiError | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);

    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
        ...opts.headers,
      };

      const res = await fetch(`${API_BASE}${path}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timer);

      if (!res.ok) {
        const detail = await res.text().catch(() => "Unknown error");
        let message = detail;
        try {
          const parsed = JSON.parse(detail);
          message = parsed.detail || detail;
        } catch {
          // use raw text
        }

        lastError = {
          status: res.status,
          message,
          isTimeout: false,
          retriesExhausted: attempt === maxRetries,
        };

        // Don't retry 4xx errors (client errors)
        if (res.status >= 400 && res.status < 500) {
          throw lastError;
        }

        // Retry 5xx errors
        if (attempt < maxRetries) {
          await sleep(Math.pow(2, attempt) * 1000); // exponential backoff
          continue;
        }
        throw lastError;
      }

      return (await res.json()) as T;
    } catch (err) {
      clearTimeout(timer);

      if (err && typeof err === "object" && "status" in err) {
        throw err; // Already an ApiError
      }

      const isAbort =
        err instanceof DOMException && err.name === "AbortError";

      lastError = {
        status: 0,
        message: isAbort ? "Request timed out" : "Network error",
        isTimeout: isAbort,
        retriesExhausted: attempt === maxRetries,
      };

      if (attempt < maxRetries) {
        await sleep(Math.pow(2, attempt) * 1000);
        continue;
      }
    }
  }

  throw lastError ?? {
    status: 0,
    message: "Request failed",
    isTimeout: false,
    retriesExhausted: true,
  };
}

export async function apiGet<T>(
  path: string,
  params?: Record<string, string>,
  opts?: ApiOptions
): Promise<T> {
  let url = path;
  if (params) {
    const searchParams = new URLSearchParams(params);
    url = `${path}?${searchParams.toString()}`;
  }
  return request<T>("GET", url, undefined, opts);
}

export async function apiPost<T>(
  path: string,
  body: unknown,
  opts?: ApiOptions
): Promise<T> {
  return request<T>("POST", path, body, opts);
}

/**
 * Stream a response from the backend (for Agent Chat)
 */
export async function* apiStream(
  path: string,
  body: unknown
): AsyncGenerator<string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...getAuthHeaders(),
  };

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!res.ok || !res.body) {
    throw {
      status: res.status,
      message: "Stream connection failed",
      isTimeout: false,
      retriesExhausted: false,
    } as ApiError;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    yield decoder.decode(value, { stream: true });
  }
}
