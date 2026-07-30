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
// The desktop shell starts its own backend and tells us where it is. That
// address wins over any stored loopback one: a saved "127.0.0.1:8000" from an
// earlier install would otherwise point at a leftover backend of an older
// version — which is exactly how an upgraded app kept meeting an old signup.
function desktopBackendUrl(): string | null {
  if (typeof window === "undefined") return null;
  const bridge = (window as { jimDesktop?: { backendUrl?: string | null } }).jimDesktop;
  return bridge?.backendUrl || null;
}

export function getBase(): string {
  const stored = localStorage.getItem("jim.base");
  const desktop = desktopBackendUrl();
  if (desktop) {
    // Only a remote address survives on the desktop; a loopback one is this
    // app's own business and must match the backend it started.
    if (stored && !/^https?:\/\/(127\.0\.0\.1|localhost|\[::1\])(:|\/|$)/.test(stored)) {
      return stored;
    }
    return desktop;
  }
  return stored || defaultBase();
}
export function setBase(url: string) { localStorage.setItem("jim.base", url.replace(/\/+$/, "")); }
export function clearBase() { localStorage.removeItem("jim.base"); }

// The console's own version, injected at build time (vite.config.ts). The
// backend states its version in /health for exactly this comparison — a
// stale backend from an older install answers /health perfectly well and
// then serves an older API, and "Not Found" on every new screen is the
// symptom. VersionGuard.tsx turns that into a sentence with a fix.
declare const __APP_VERSION__: string;
export const CONSOLE_VERSION: string =
  typeof __APP_VERSION__ !== "undefined" ? __APP_VERSION__ : "dev";

// Bring-your-own model key: stored on this device only, sent per-request as
// x-llm-api-key so generations run on the user's own credential. The backend
// never persists it; without one, the deployment's key (if any) answers.
export function getLlmKey(): string { return localStorage.getItem("jim.llmKey") || ""; }
export function setLlmKey(key: string) {
  if (key.trim()) localStorage.setItem("jim.llmKey", key.trim());
  else localStorage.removeItem("jim.llmKey");
}

async function req<T>(path: string, opts: { method?: string; body?: unknown; token?: string } = {}): Promise<T> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (opts.token) headers["authorization"] = `Bearer ${opts.token}`;
  const llmKey = getLlmKey();
  if (llmKey) headers["x-llm-api-key"] = llmKey;
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
  // A body is not guaranteed to be JSON — a crashed server answers plain
  // text ("Internal Server Error"), and surfacing a JSON.parse exception
  // instead of those words is how one error hides another.
  let data: unknown = null;
  try { data = text ? JSON.parse(text) : null; }
  catch { data = null; }
  if (!res.ok) {
    const body = data as { detail?: unknown; message?: unknown } | null;
    const d = (body && (body.detail || body.message)) || text.trim() || res.statusText;
    throw new Error(typeof d === "string" ? d : JSON.stringify(d));
  }
  return data as T;
}

export interface FirstAid {
  kind: string; title?: string; steps: string[];
  pace?: { compressions_per_minute: number; compression_to_breath_ratio: string;
           cue: { light: string; audio: string } };
}
export interface Guidance { delivered: boolean; source?: string; content: string; references?: string[];
  first_aid?: FirstAid | null;
  provenance?: { generated_by?: string; degraded?: boolean; degraded_reason?: string | null } }
export interface DriftCrossing {
  metric: string; label: string; unit: string; direction: "above" | "below";
  value: number; baseline: number; edge: number; delta: number; note: string;
}
export interface LiveAssistanceOption {
  kind: string; name: string; channel?: string; note?: string;
}
export interface FollowupResult {
  answered: boolean; reason?: string; helped?: boolean; next?: string;
  escalation_decision?: { tier: string; rationale?: string } | null;
  live_assistance?: { options: LiveAssistanceOption[]; contact_alerted: boolean;
    note: string } | null;
}
export interface MonitorResult {
  detected: boolean; condition?: string; severity?: string; reason?: string;
  guidance?: Guidance | null; escalation?: unknown; forecast?: unknown;
  // Spec [0039]: guidance that went out gets asked about.
  followup?: { id: string; question: string } | null;
  // Not an episode — a drift from this person's own baseline, which earns a
  // question rather than an alarm (jim/bands.py).
  drift?: { crossings: DriftCrossing[]; question: string } | null;
}
export interface CheckinResult {
  id: string; mood: number; energy: number; stress?: number | null; insights: unknown[];
  guardian: { detected: boolean; guidance?: Guidance | null; escalation?: unknown; forecast?: unknown };
}
export interface BaselineMetric { metric: string; value?: number; state?: string; samples?: number }
export interface PairInfo {
  console_url: string; api_url: string; console_built: boolean;
  qr_svg: string; how: string[]; note: string;
}
export interface MedSchedule { times?: string[]; as_needed?: boolean; max_per_day?: number }
export interface MedOut {
  id: string; name: string; dose: string; purpose?: string | null;
  schedule: MedSchedule; critical: boolean; archived: boolean;
}
export interface MedBoard {
  date: string; disclaimer: string;
  missed_critical: { name: string; slot: string }[];
  medications: (MedOut & { kind: "scheduled" | "as_needed";
    slots?: { slot: string; status: string; note?: string | null }[];
    taken_today?: number; max_per_day?: number | null })[];
}
export interface VigilStatus {
  armed: boolean; steward_name?: string; steward_channel?: string;
  quiet_days?: number; note?: string | null; last_heard_at?: string | null;
  silent_hours?: number | null; threshold_hours?: number;
  tripped?: boolean; tripped_at?: string | null;
}
export interface WatchChannel {
  drip_url: string; phone_reachable: boolean;
  last_drip_at: string | null; drips: number;
  shortcut: string[]; seed_hint: string;
}
export interface SeedReport {
  seeded: Record<string, { days: number; baseline: number; provisional: boolean }>;
}

export interface CareTeamStatus {
  linked: boolean;
  org_id?: string;
  department_id?: string;
  credential_held?: boolean;
  latest_plan?: CarePlan | null;
}
export interface CarePlan {
  id: string;
  goal: string;
  plan?: string | null;
  trigger: Record<string, unknown>;
  sealed_in_qrme_vault: boolean;
  created_at: string;
}

export interface CrashWatchStatus {
  armed: boolean;
  trusted_name?: string;
  trusted_channel?: string;
  attempts?: number;
  window_minutes?: number;
  contact_emergency_services?: boolean;
  asking?: boolean;
  attempt?: number;
  deadline_at?: string | null;
  concern?: string | null;
  tripped?: boolean;
  tripped_at?: string | null;
}
export interface JournalRow {
  id: string; text: string; created_at: string; vaulted?: boolean;
}

export interface CalmSession {
  kind: string; title: string; what: string; total_seconds: number;
  steps: { say: string; seconds: number }[];
}
export interface WorkoutPlan {
  minutes_asked: number; level: string; focus: string;
  rest_seconds_between_blocks: number; total_seconds: number; note: string;
  blocks: { name: string; seconds: number; cue: string }[];
}
export interface MealPlan {
  goal: string; preferences: string[];
  shape: { meals_per_day: number; orientation_calories: number; why: string };
  days: { day: number; meals: { slot: string; name: string }[] }[];
  disclaimer: string;
}

export const api = {
  // The help box — written directions about the app itself; no token, so a
  // lost person can ask before they have an account.
  help: (question: string) =>
    req<{ answer: string; ai: boolean; disclosure: string }>(
      "/help", { method: "POST", body: { question } }),

  health: () => req<{ status: string; version?: string; tandem: boolean;
                      console?: boolean }>("/health"),
  // How to open this console on a phone: its URL on the local network.
  pair: () => req<PairInfo>("/pair"),
  enroll: (body: { display_name: string; birthdate: string; terms_consent: boolean }) =>
    req<{ id: string; display_name: string; user_token: string }>("/enroll", { method: "POST", body }),
  // Accounts: the email is verified (emailed code) before the user exists.
  oauthProviders: () =>
    req<{ providers: { provider: string; name: string; configured: boolean;
                       setup?: string }[] }>("/auth/oauth/providers"),
  oauthStart: (provider: string, enroll?: Record<string, unknown>) =>
    req<{ url: string; state: string }>(
      `/auth/oauth/${provider}/start`, { method: "POST", body: { enroll } }),
  oauthClaim: (state: string) =>
    req<{ ready: boolean; id?: string; user_id?: string; email?: string;
          display_name?: string; user_token?: string }>(
      `/auth/oauth/claim?state=${encodeURIComponent(state)}`),
  signup: (body: { email: string; password: string; display_name: string; birthdate: string; terms_consent: boolean }) =>
    req<{ account_id: string; email: string; verified: boolean; code_delivery?: string;
          verification: "local" | "email";
          // Present when verification is "local" (no mail transport — the
          // machine owner is trusted and the account activates directly).
          id?: string; display_name?: string; user_token?: string }>(
      "/signup", { method: "POST", body }),
  verifyEmail: (body: { email: string; code: string }) =>
    req<{ id: string; display_name: string; user_token: string }>(
      "/verify-email", { method: "POST", body }),
  resendCode: (email: string) =>
    req<{ email: string; code_delivery: string }>(
      "/verify-email/resend", { method: "POST", body: { email } }),
  signin: (body: { email: string; password: string }) =>
    req<{ user_id: string; user_token: string; email: string; display_name?: string }>(
      "/signin", { method: "POST", body }),
  // Which model answers, as a picker rather than a config file.
  listModels: () =>
    req<{ providers: { name: string; label: string; configured: boolean;
                       model: string; network: boolean }[]; default: string }>("/models"),
  getModelChoice: (uid: string, token: string) =>
    req<{ provider: string; effective: string }>(`/model/${uid}`, { token }),
  setModelChoice: (uid: string, provider: string, token: string) =>
    req<{ provider: string; effective: string }>(
      `/model/${uid}`, { method: "PUT", body: { provider }, token }),

  // Your own normal, and the edges around it.
  getBands: (uid: string, token: string) =>
    req<{ sensitivity: string; bands: {
      metric: string; label: string; unit: string; margin: number;
      watch_high: boolean; watch_low: boolean; source: string;
      baseline: number | null; samples: number; provisional: boolean;
      low_edge: number | null; high_edge: number | null }[] }>(
      `/bands/${uid}`, { token }),
  setBand: (uid: string, metric: string,
            body: { margin?: number; watch_high?: boolean; watch_low?: boolean },
            token: string) =>
    req<{ metric: string; margin: number }>(
      `/bands/${uid}/${metric}`, { method: "PUT", body, token }),
  resetBand: (uid: string, metric: string, token: string) =>
    req<{ metric: string; margin: number }>(
      `/bands/${uid}/${metric}`, { method: "DELETE", token }),

  // Speaking and listening.
  getVoiceSettings: () =>
    req<{ provider: string; voice_id: string; speak_replies: boolean;
          key_set: boolean; key_source: string; device_fallback: boolean;
          voices: { id: string; name: string; gender: string; note: string }[] }>(
      "/settings/voice"),
  saveVoiceSettings: (body: { provider: string; api_key?: string;
                              voice_id?: string; speak_replies?: boolean }) =>
    req<{ provider: string }>("/settings/voice", { method: "PUT", body }),
  transcribe: (audio_base64: string) =>
    req<{ text: string }>("/voice/transcribe",
      { method: "POST", body: { audio_base64 } }),

  // The medicine cabinet: tracked in your words, never a pharmacist.
  // The care team is an organization (jim/careteam.py).
  specialistsCatalog: () =>
    req<{ qrme_url: string | null;
          conditions: { condition: string;
                        attached: { mode: string; label?: string | null;
                                    qrme_profile_id?: string | null } | null }[];
          starters: { profile_id: string; display_name: string; blurb?: string;
                      tags: string[]; avatar?: string | null;
                      avatar_kind?: string | null }[];
          note: string }>("/specialists/catalog"),
  attachSpecialist: (body: { condition: string; mode: "tandem";
                             label?: string; qrme_profile_id: string }) =>
    req<{ condition: string; label?: string }>(
      "/specialists", { method: "POST", body }),
  careTeamStatus: (uid: string, token: string) =>
    req<CareTeamStatus>(`/users/${uid}/care-team`, { token }),
  careTeamLink: (uid: string, token: string,
                 body: { org_id: string; department_id: string; owner_token: string }) =>
    req<CareTeamStatus>(`/users/${uid}/care-team`, { method: "PUT", body, token }),
  careTeamUnlink: (uid: string, token: string) =>
    req<unknown>(`/users/${uid}/care-team`, { method: "DELETE", token }),
  careTeamCoordinate: (uid: string, token: string, goal: string) =>
    req<CarePlan>(`/users/${uid}/care-team/coordinate`,
      { method: "POST", body: { goal }, token }),
  careTeamPlans: (uid: string, token: string) =>
    req<CarePlan[]>(`/users/${uid}/care-team/plans`, { token }),

  medsBoard: (uid: string, token: string) =>
    req<MedBoard>(`/meds/${uid}`, { token }),
  medsAdd: (uid: string, token: string, body: { name: string; dose: string;
            schedule: MedSchedule; purpose?: string; critical?: boolean }) =>
    req<MedOut>(`/meds/${uid}`, { method: "POST", body, token }),
  medsArchive: (uid: string, mid: string, token: string) =>
    req<MedOut>(`/meds/${uid}/${mid}`, { method: "DELETE", token }),
  medsLog: (uid: string, mid: string, token: string,
            body: { action: "taken" | "skipped"; slot?: string; note?: string }) =>
    req<MedBoard>(`/meds/${uid}/${mid}/log`, { method: "POST", body, token }),
  medsAdherence: (uid: string, token: string, days = 7) =>
    req<{ days: number; medications: { id: string; name: string;
          expected: number; taken: number; rate: number | null }[] }>(
      `/meds/${uid}/adherence?days=${days}`, { token }),

  // The crash watch: the vigil's acute sibling — a critical reading opens
  // "are you okay?", N unanswered attempts summon the programmed help.
  crashWatch: (uid: string, token: string) =>
    req<CrashWatchStatus>(`/crash-watch/${uid}`, { token }),
  armCrashWatch: (uid: string, body: {
    trusted_name: string; trusted_channel: string; attempts: number;
    window_minutes: number; contact_emergency_services: boolean;
  }, token: string) =>
    req<CrashWatchStatus>(`/crash-watch/${uid}`, { method: "PUT", body, token }),
  disarmCrashWatch: (uid: string, token: string) =>
    req<CrashWatchStatus>(`/crash-watch/${uid}`, { method: "DELETE", token }),
  imOkay: (uid: string, token: string) =>
    req<CrashWatchStatus>(`/crash-watch/${uid}/respond`, { method: "POST", token }),

  // The journal: text or spoken, sealed on private plans.
  addJournal: (uid: string, text: string, token: string) =>
    req<{ id: string; vaulted: boolean }>(
      `/journal/${uid}`, { method: "POST", body: { text }, token }),
  journal: (uid: string, token: string) =>
    req<JournalRow[]>(`/journal/${uid}`, { token }),

  // Guided wellness: calm protocols, workout plans, meal plans.
  calmCatalog: () =>
    req<{ sessions: { kind: string; title: string; minutes: number; what: string }[] }>("/calm"),
  startCalm: (uid: string, kind: string, token: string) =>
    req<CalmSession>(`/calm/${uid}/${kind}`, { method: "POST", token }),
  workoutPlan: (uid: string, body: { minutes: number; level: string; focus: string }, token: string) =>
    req<WorkoutPlan>(`/fitness/${uid}/plan`, { method: "POST", body, token }),
  mealPlan: (uid: string, body: { goal: string; preferences: string[]; days: number }, token: string) =>
    req<MealPlan>(`/nutrition/${uid}/plan`, { method: "POST", body, token }),

  // The vigil: the alarm that fires when the signals stop.
  getVigil: (uid: string, token: string) =>
    req<VigilStatus>(`/vigil/${uid}`, { token }),
  armVigil: (uid: string, token: string, body: { steward_name: string;
             steward_channel: string; quiet_days: number; note?: string }) =>
    req<VigilStatus>(`/vigil/${uid}`, { method: "PUT", body, token }),
  disarmVigil: (uid: string, token: string) =>
    req<VigilStatus>(`/vigil/${uid}`, { method: "DELETE", token }),
  sweepVigil: (uid: string, token: string) =>
    req<VigilStatus>(`/vigil/${uid}/sweep`, { method: "POST", token }),
  resolveVigil: (uid: string, token: string) =>
    req<VigilStatus>(`/vigil/${uid}/resolve`, { method: "POST", token }),

  // The Apple Watch bridge: a Shortcuts automation drips readings at a
  // tokened URL; the Health app's export seeds the baseline from history.
  getWatchChannel: (uid: string, token: string) =>
    req<WatchChannel>(`/watch/channel/${uid}`, { token }),
  rotateWatchChannel: (uid: string, token: string) =>
    req<WatchChannel>(`/watch/channel/${uid}/rotate`, { method: "POST", token }),
  seedWatchExport: async (uid: string, token: string, file: File) => {
    // The export.zip goes up as raw bytes — req() would JSON-encode it.
    const res = await fetch(getBase() + `/watch/seed/${uid}`, {
      method: "POST",
      headers: { authorization: `Bearer ${token}` },
      body: file,
    });
    const text = await res.text();
    let data: unknown = null;
    try { data = text ? JSON.parse(text) : null; } catch { data = null; }
    if (!res.ok) {
      const body = data as { detail?: unknown } | null;
      const d = (body && body.detail) || text.trim() || res.statusText;
      throw new Error(typeof d === "string" ? d : JSON.stringify(d));
    }
    return data as SeedReport;
  },

  // Mail settings: what makes verification emails real instead of a line in
  // a log file. The password goes up; it never comes back down.
  getMailSettings: () =>
    req<{ transport: "smtp" | "console"; source: string; host: string | null;
          port: number; username: string | null; sender: string | null;
          public_url: string; password_set: boolean }>("/settings/mail"),
  saveMailSettings: (body: { host: string; port: number; username?: string;
                             password?: string; sender?: string; public_url?: string }) =>
    req<{ transport: string }>("/settings/mail", { method: "PUT", body }),
  clearMailSettings: () =>
    req<{ transport: string }>("/settings/mail", { method: "DELETE" }),
  testMailSettings: (to: string) =>
    req<{ sent: boolean; to: string }>("/settings/mail/test",
      { method: "POST", body: { to } }),
  requestReset: (email: string) =>
    req<{ email: string; code_delivery: string }>(
      "/password/reset/request", { method: "POST", body: { email } }),
  resetPassword: (body: { email: string; code: string; new_password: string }) =>
    req<{ email: string; reset: boolean }>(
      "/password/reset", { method: "POST", body }),
  monitor: (uid: string, body: { heart_rate: number; respiration?: number; stress_level?: number }, token: string) =>
    req<MonitorResult>(`/monitor/${uid}`, { method: "POST", body, token }),
  // Spec [0039]: whether the guidance actually worked. "No" escalates toward
  // a live person and comes back with the humans reachable right now.
  answerFollowup: (uid: string, body: { helped: boolean; note?: string }, token: string) =>
    req<FollowupResult>(`/followup/${uid}`, { method: "POST", body, token }),
  checkin: (uid: string, body: { mood: number; energy: number; stress?: number; note?: string }, token: string) =>
    req<CheckinResult>(`/checkin/${uid}`, { method: "POST", body, token }),
  coach: (uid: string, body: { area: string; message: string }, token: string) =>
    req<Guidance>(`/coach/${uid}`, { method: "POST", body, token }),
  baseline: (uid: string, token: string) =>
    req<BaselineMetric[]>(`/baseline/${uid}`, { token }),
};
