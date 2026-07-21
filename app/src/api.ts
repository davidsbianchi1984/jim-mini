// Thin typed client for the JIM-mini / Guardian API.
const DEFAULT_BASE = "http://127.0.0.1:8000";
export function getBase(): string { return localStorage.getItem("jim.base") || DEFAULT_BASE; }
export function setBase(url: string) { localStorage.setItem("jim.base", url.replace(/\/+$/, "")); }

async function req<T>(path: string, opts: { method?: string; body?: unknown; token?: string } = {}): Promise<T> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (opts.token) headers["authorization"] = `Bearer ${opts.token}`;
  const res = await fetch(getBase() + path, {
    method: opts.method || "GET", headers,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const d = (data && (data.detail || data.message)) || res.statusText;
    throw new Error(typeof d === "string" ? d : JSON.stringify(d));
  }
  return data as T;
}

export interface Guidance { delivered: boolean; source?: string; content: string; references?: string[] }
export interface MonitorResult {
  detected: boolean; condition?: string; severity?: string; reason?: string;
  guidance?: Guidance | null; escalation?: unknown; forecast?: unknown;
}
export interface CheckinResult {
  id: string; mood: number; energy: number; insights: unknown[];
  guardian: { detected: boolean; guidance?: Guidance | null; escalation?: unknown; forecast?: unknown };
}
export interface BaselineMetric { metric: string; value?: number; state?: string; samples?: number }

export const api = {
  health: () => req<{ status: string; tandem: boolean }>("/health"),
  enroll: (body: { display_name: string; birthdate: string; terms_consent: boolean }) =>
    req<{ id: string; display_name: string; user_token: string }>("/enroll", { method: "POST", body }),
  monitor: (uid: string, body: { heart_rate: number; respiration?: number; stress_level?: number }, token: string) =>
    req<MonitorResult>(`/monitor/${uid}`, { method: "POST", body, token }),
  checkin: (uid: string, body: { mood: number; energy: number; note?: string }, token: string) =>
    req<CheckinResult>(`/checkin/${uid}`, { method: "POST", body, token }),
  coach: (uid: string, body: { area: string; message: string }, token: string) =>
    req<Guidance>(`/coach/${uid}`, { method: "POST", body, token }),
  baseline: (uid: string, token: string) =>
    req<BaselineMetric[]>(`/baseline/${uid}`, { token }),
};
