// Thin typed client for the JIM-mini / Guardian API.
import { recordProblem } from "./errors";
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
    // Never reached a server. Recorded as status 0, which is a different
    // failure from anything the backend answered and worth telling apart.
    recordProblem(opts.method || "GET", path, 0);
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
    // The status and the operation, never the detail below: that string
    // carries whatever the user typed.
    recordProblem(opts.method || "GET", path, res.status);
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
export interface CommunityRoom {
  id: string; topic: string; channel: string; participants: number;
  url: string | null;
}
export interface CommunityView {
  qrme_url: string | null; language: string;
  rooms: CommunityRoom[];
  places: { locality: string; listings: number }[];
  note: string;
  posture: { mirrored_here: boolean; posts_on_your_behalf: boolean;
             health_data_shared: boolean };
}
// Claim 11's user-specific model, derived from this user's own history.
export interface AdaptationProfile {
  built: boolean; note?: string; version?: number;
  evidence_items?: number; confidence?: number; vaulted?: boolean;
  rebuilt_at?: string;
  profile?: {
    known_conditions: string[];
    what_helps: Record<string, { helped: number; did_not: number;
                                 answered: number; hit_rate: number | null }>;
    areas_brought: Record<string, number>;
    checkins: { count: number; avg_mood?: number | null;
                avg_stress?: number | null };
    tone: string | null; explain_level: string | null;
    beliefs_posture: string; occupation: string | null;
    method: string;
  } | null;
  sealed_key?: string | null;
}
// Spec [0031]: what anonymity keeps and what it costs.
export interface AnonymityPosture {
  anonymous: boolean; known_as?: string; legal_name_on_record: boolean;
  keeps: string[]; costs: string[];
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

// ---------------------------------------------------------------------
// Shapes for the doors below. Every field here was read off a live response
// rather than inferred from the handler, because a field name guessed from
// the Python side is exactly the kind of thing that compiles and then finds
// nothing at runtime.
// ---------------------------------------------------------------------

/** An alarm raised by a beacon scan or by the crash watch. */
export type AlarmRow = {
  id: string;
  state: string;
  tier: string;
  beacon_id?: string | null;
  accepted_by?: string | null;
  created_at?: string;
  cleared_at?: string | null;
  messages?: { from?: string; text?: string; at?: string }[];
};

/** What accept / escalate / clear answer with. The three differ, so the
 *  fields they do not share are optional rather than invented. */
export type AlarmAction = {
  state?: string;
  id?: string;
  alarm?: Record<string, unknown>;
  accepted_by?: string | null;
  note?: string;
};

export type IncidentRow = {
  id?: string;
  kind?: string;
  at?: string;
  detail?: string;
  [key: string]: unknown;
};

export type PageRow = {
  id?: string;
  to?: string;
  sent_at?: string;
  delivered?: boolean;
  [key: string]: unknown;
};

export type BeaconRow = {
  id: string;
  user_id: string;
  label: string;
  placement?: string | null;
  kind: string;
  active: boolean;
  scans: number;
  scan_url: string;
  qr_svg: string;
  created_at: string;
};

export type CloudContribution = {
  opted_in: boolean;
  contributed: number;
  policy?: string;
  preview_next?: unknown;
  preview_note?: string;
};


/** A device on the account. A microphone can only be attached to one of these. */
export type DeviceRow = {
  id: string;
  user_id: string;
  name: string;
  kind: string;
  transport?: string | null;
  has_llm: boolean;
  linked_to?: string | null;
  created_at: string;
};

/** Which microphones may become channel 2, and why the ambient ones may not. */
export type MicTypes = {
  personal: string[];
  ambient: string[];
  rule: string;
};

/** Gain is not volume. Every level is the owner at a different distance, and
 *  `reaches_others` says plainly whether anyone else falls inside it. */
export type MicGains = {
  levels: { gain: string; reaches_others: boolean; describes: string }[];
  default: string;
  capped_during: string[];
  voice_focus: boolean;
  rule: string;
};

/** Channel 2's current state. `capped` means a call is in progress and the
 *  agent has narrowed itself regardless of the owner's setting. */
export type MicState = {
  listening: boolean;
  attached?: boolean;
  device?: string | null;
  mic_type?: string | null;
  gain?: string | null;
  effective_gain?: string | null;
  capped?: boolean;
  hears?: string;
  because?: string;
  reason?: string | null;
  route?: string | null;
  since?: string | null;
  note?: string;
  channel?: number;
  voice_focus?: boolean;
  describes?: string;
  id?: string;
};

export type MicEvent = {
  id: string;
  device: string;
  mic_type: string;
  gain: string;
  reason?: string | null;
  route?: string | null;
  live: boolean;
  started_at: string;
  ended_at?: string | null;
  ended_because?: string | null;
};

/** The server describes the whole capture form: what may be photographed,
 *  which of those sites are intimate, and how big a file may be. */
export type CaptureVocabulary = {
  kinds: Record<string, string>;
  sites: Record<string, string>;
  provenance: Record<string, string>;
  intimate: string[];
  minors?: string;
  agent_sees?: string;
  agent_never_sees?: string;
  vault_required: boolean;
  max_bytes: number;
};

export type CaptureRow = {
  id: string;
  kind: string;
  site: string;
  provenance: string;
  note?: string | null;
  condition?: string | null;
  intimate?: boolean;
  sealed?: boolean;
  created_at?: string;
  [key: string]: unknown;
};

export type CaptureAttachResult = {
  attached?: string[];
  explicit?: string[];
  [key: string]: unknown;
};

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
  signup: (body: { email: string; password: string; display_name: string; birthdate: string; terms_consent: boolean;
                   anonymous?: boolean; legal_name?: string }) =>
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
  // FIG. 2 boxes 222-226: the community door. Rooms and places come from
  // QRME through the tandem; nothing is mirrored into JIM.
  community: (uid: string, token: string, locality?: string) =>
    req<CommunityView>(`/community/${uid}` + (locality ? `?locality=${encodeURIComponent(locality)}` : ""), { token }),
  communityVisit: (uid: string, room_id: string, token: string) =>
    req<{ noted: boolean; room_id: string; stored: string }>(
      `/community/${uid}/visits`, { method: "POST", body: { room_id }, token }),
  // Claim 11: the user-specific model, derived and (with a tandem) sealed.
  adaptation: (uid: string, token: string) =>
    req<AdaptationProfile>(`/adaptation/${uid}`, { token }),
  rebuildAdaptation: (uid: string, token: string) =>
    req<AdaptationProfile>(`/adaptation/${uid}`, { method: "POST", token }),
  anonymity: (uid: string, token: string) =>
    req<AnonymityPosture>(`/anonymity/${uid}`, { token }),
  checkin: (uid: string, body: { mood: number; energy: number; stress?: number; note?: string }, token: string) =>
    req<CheckinResult>(`/checkin/${uid}`, { method: "POST", body, token }),
  coach: (uid: string, body: { area: string; message: string }, token: string) =>
    req<Guidance>(`/coach/${uid}`, { method: "POST", body, token }),
  baseline: (uid: string, token: string) =>
    req<BaselineMetric[]>(`/baseline/${uid}`, { token }),

  // ---------------------------------------------------------------------
  // Doors the backend had been holding open with nobody on the other side.
  // Everything below reaches a route that has existed for versions and was
  // called by no client at all — the console, the shells, or anything else.
  // ---------------------------------------------------------------------

  // The crash watch can raise an alarm; until now nothing could answer one.
  // `open_only` is the view that matters on arrival: what still needs a human.
  alarms: (uid: string, token: string, openOnly = false) =>
    req<AlarmRow[]>(`/users/${uid}/alarms` + (openOnly ? "?open_only=true" : ""),
      { token }),
  acceptAlarm: (uid: string, alarmId: string, responder: string, token: string) =>
    req<AlarmAction>(`/users/${uid}/alarms/${alarmId}/accept`,
      { method: "POST", body: { responder }, token }),
  clearAlarm: (uid: string, alarmId: string, token: string) =>
    req<AlarmAction>(`/users/${uid}/alarms/${alarmId}/clear`,
      { method: "POST", token }),
  escalateAlarm: (uid: string, alarmId: string, token: string) =>
    req<AlarmAction>(`/users/${uid}/alarms/${alarmId}/escalate`,
      { method: "POST", token }),
  incidents: (uid: string, token: string) =>
    req<IncidentRow[]>(`/users/${uid}/incidents`, { token }),
  pages: (uid: string, token: string, undeliveredOnly = false) =>
    req<PageRow[]>(`/users/${uid}/pages`
      + (undeliveredOnly ? "?undelivered_only=true" : ""), { token }),
  beacons: (uid: string, token: string) =>
    req<BeaconRow[]>(`/users/${uid}/beacons`, { token }),
  placeBeacon: (uid: string, body: { label: string; placement?: string;
    kind?: "personal" | "site" }, token: string) =>
    req<BeaconRow>(`/users/${uid}/beacons`, { method: "POST", body, token }),

  // What left this device for the shared model, and the button that stops it.
  cloudContribution: (uid: string, token: string) =>
    req<CloudContribution>(`/users/${uid}/cloud-contribution`, { token }),
  revokeCloudContribution: (uid: string, token: string) =>
    req<CloudContribution>(`/users/${uid}/cloud-contribution/revoke`,
      { method: "POST", token }),
  setLocality: (uid: string, locality: string | null, token: string) =>
    req<{ locality: string | null }>(`/users/${uid}/locality`,
      { method: "PUT", body: { locality }, token }),

  // Devices come first because channel 2 depends on them: a microphone
  // attaches to a device the account already knows, never to a typed name.
  devices: (uid: string, token: string) =>
    req<DeviceRow[]>(`/devices/${uid}`, { token }),
  registerDevice: (uid: string, body: { name: string; kind: string;
    transport?: string; has_llm?: boolean }, token: string) =>
    req<DeviceRow>(`/devices/${uid}`, { method: "POST", body, token }),

  // Channel 2 — the microphone JIM listens through. Both vocabularies come
  // from the server so the picker cannot offer a value the handler refuses,
  // and so the rules travel with the options rather than being retyped here.
  micTypes: () => req<MicTypes>(`/mic/types`),
  micGains: () => req<MicGains>(`/mic/gains`),
  micState: (uid: string, token: string) =>
    req<MicState>(`/users/${uid}/mic`, { token }),
  attachMic: (uid: string, body: { device_name: string; mic_type: string },
    token: string) =>
    req<MicState>(`/users/${uid}/mic`, { method: "PUT", body, token }),
  detachMic: (uid: string, token: string) =>
    req<MicState>(`/users/${uid}/mic`, { method: "DELETE", token }),
  setMicGain: (uid: string, gain: string, token: string) =>
    req<MicState>(`/users/${uid}/mic/gain`,
      { method: "PUT", body: { gain }, token }),
  handOverMic: (uid: string, body: { reason: string; route: string;
    others_present?: boolean; primary_device?: string }, token: string) =>
    req<MicState>(`/users/${uid}/mic/handover`, { method: "POST", body, token }),
  releaseMic: (uid: string, token: string) =>
    req<MicState>(`/users/${uid}/mic/release`, { method: "POST", token }),
  micHistory: (uid: string, token: string) =>
    req<MicEvent[]>(`/users/${uid}/mic/history`, { token }),

  // Clinical capture. The vocabulary is the form: 21 sites, three kinds, and
  // the list of which sites count as intimate — read rather than duplicated,
  // because a site list that drifts out of step is a 422 at the worst moment.
  captureVocabulary: () => req<CaptureVocabulary>(`/captures/vocabulary`),
  captures: (uid: string, token: string, condition?: string) =>
    req<CaptureRow[]>(`/users/${uid}/captures`
      + (condition ? `?condition=${encodeURIComponent(condition)}` : ""),
      { token }),
  takeCapture: (uid: string, body: { kind?: string; site: string;
    content: string; provenance?: string; note?: string; condition?: string;
    intimate_consent?: boolean }, token: string) =>
    req<CaptureRow>(`/users/${uid}/captures`, { method: "POST", body, token }),
  captureImage: (uid: string, captureId: string, token: string) =>
    req<{ content: string; kind: string }>(
      `/users/${uid}/captures/${captureId}/image`, { token }),
  attachCaptures: (uid: string, capture_ids: string[], token: string) =>
    req<CaptureAttachResult>(`/users/${uid}/captures/attach`,
      { method: "POST", body: { capture_ids }, token }),
  deleteCapture: (uid: string, captureId: string, token: string) =>
    req<{ withdrawn: boolean }>(`/users/${uid}/captures/${captureId}`,
      { method: "DELETE", token }),
};
