// Thin typed client for the JIM-mini / Guardian API.
//
// Default base: when the console is served *by* the API (the phone case —
// http://<machine>:8000/app/), the backend is the origin we came from, so
// the phone needs no configuration at all. Only the Electron desktop shell
// (file://) and the Vite dev server fall back to the local backend.
const LOOPBACK = "http://127.0.0.1:8000";
function defaultBase(): string {
  if (typeof window === "undefined") return LOOPBACK;
  const { protocol, origin, pathname } = window.location;
  if (protocol !== "http:" && protocol !== "https:") return LOOPBACK;  // file://
  if (pathname.startsWith("/app")) return origin;   // served by the API itself
  return LOOPBACK;                                   // vite dev on :5173
}
export function getBase(): string { return localStorage.getItem("jim.base") || defaultBase(); }
export function setBase(url: string) { localStorage.setItem("jim.base", url.replace(/\/+$/, "")); }

async function req<T>(path: string, opts: { method?: string; body?: unknown; token?: string } = {}): Promise<T> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (opts.token) headers["authorization"] = `Bearer ${opts.token}`;
  let res: Response;
  try {
    res = await fetch(getBase() + path, {
      method: opts.method || "GET", headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
  } catch {
    // A network-level failure surfaces as "Failed to fetch", which tells the
    // user nothing. Name the actual problem: no Guardian backend answering.
    throw new Error(
      `Can't reach the Guardian backend at ${getBase()}. ` +
      `Start it with "python -m jim serve", or set the backend URL in Settings.`,
    );
  }
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
export interface PairInfo {
  console_url: string; api_url: string; console_built: boolean;
  qr_svg: string; how: string[]; note: string;
}

export const api = {
  health: () => req<{ status: string; tandem: boolean; console?: boolean }>("/health"),
  // How to open this console on a phone: its URL on the local network.
  pair: () => req<PairInfo>("/pair"),
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
