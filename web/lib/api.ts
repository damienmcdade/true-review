/**
 * Browser-side API helper. Always routes through Next.js's same-origin
 * /api/proxy/* rewrite so we never hit CORS, preflight, or extension
 * privacy-blockers. The actual Railway URL is hidden from the client.
 *
 * Server-side code (RSC, route handlers, server actions) should still call
 * the API directly via process.env.NEXT_PUBLIC_API_URL because it can.
 */
const PROXY = '/api/proxy';
const TIMEOUT_MS = 30_000;

export type ApiError = {
  status: number | null;
  kind: 'timeout' | 'network' | 'rate_limit' | 'server' | 'client' | 'parse';
  message: string;
};

export async function apiFetch<T>(
  path: string,
  init?: RequestInit & { timeoutMs?: number }
): Promise<{ data: T | null; error: ApiError | null }> {
  const controller = new AbortController();
  const timeoutMs = init?.timeoutMs ?? TIMEOUT_MS;
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const url = path.startsWith('/') ? `${PROXY}${path}` : `${PROXY}/${path}`;

  try {
    const res = await fetch(url, {
      ...init,
      signal: controller.signal,
      cache: init?.cache ?? 'no-store',
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers ?? {})
      }
    });

    if (!res.ok) {
      let text = '';
      try {
        text = await res.text();
      } catch {
        // ignore
      }
      const kind: ApiError['kind'] =
        res.status === 429
          ? 'rate_limit'
          : res.status >= 500
            ? 'server'
            : 'client';
      const message =
        res.status === 429
          ? 'You\'re sending requests too quickly. Wait a minute and try again.'
          : res.status >= 500
            ? 'The True Review service hit an error. Try again in a moment.'
            : extractDetail(text) || `Request failed with status ${res.status}.`;
      return { data: null, error: { status: res.status, kind, message } };
    }

    try {
      const data = (await res.json()) as T;
      return { data, error: null };
    } catch (e) {
      return {
        data: null,
        error: {
          status: res.status,
          kind: 'parse',
          message: 'Response was not valid JSON.'
        }
      };
    }
  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : 'Unknown error';
    const isAbort = message.includes('aborted') || message.includes('signal');
    return {
      data: null,
      error: {
        status: null,
        kind: isAbort ? 'timeout' : 'network',
        message: isAbort
          ? `The request took longer than ${Math.round(timeoutMs / 1000)}s. Try again.`
          : 'Couldn\'t reach the API. Check your connection or browser extensions and try again.'
      }
    };
  } finally {
    clearTimeout(timer);
  }
}

function extractDetail(body: string): string | null {
  if (!body) return null;
  try {
    const j = JSON.parse(body) as { detail?: unknown; error?: unknown };
    if (typeof j.detail === 'string') return j.detail;
    if (j.detail && typeof j.detail === 'object') return JSON.stringify(j.detail);
    if (typeof j.error === 'string') return j.error;
  } catch {
    // fall through
  }
  return body.slice(0, 200);
}
