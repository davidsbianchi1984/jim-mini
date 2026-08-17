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


/** Honest looseness. See the note over the block of bindings at the bottom of
 *  this file: where a response is a large nested catalogue the screen reads a
 *  few fields from, it is typed permissively rather than precisely, because a
 *  loose type that is true beats a narrow one that is a guess. */
export type Row = Record<string, unknown>;
export type Body = Record<string, unknown>;

// --- shapes read off a running backend -------------------------------------
// Everything below was driven, not inferred. Where the server names a closed
// set of values in its own 422 body, that set is written out as a union: a
// wrong literal fails the build, where a wrong string fails a user.

/** The seven areas a goal can belong to. The server rejects anything else. */
export type GoalArea =
  | "mental_health" | "health_fitness" | "nutrition" | "career"
  | "finance" | "relationships" | "personal_growth";

/** The eight conditions JIM will take on. Also a closed set, also enforced. */
export type ConditionName =
  | "anxiety" | "depression" | "stress" | "phobia"
  | "financial_stress" | "relationship" | "physical_distress"
  | "physical_injury";

export type GoalRow = {
  id: string; user_id?: string; area: GoalArea; title: string;
  target?: string | null; progress: number; status: string;
  created_at?: string; updated_at?: string;
};

/** `POST /habits` answers with the short form — id, name, streak — and the
 *  listing with the long one. Optional fields are the difference. */
export type HabitRow = {
  id: string; name: string; streak: number;
  user_id?: string; created_at?: string;
};

export type BudgetLine = {
  category: string; monthly_limit: number; spent: number; share: number;
  standing: string; days_left: number; month: string;
};

/** The board wraps the lines — `budgets` is where they live. */
export type BudgetBoard = {
  month: string; days_left: number; budgets: BudgetLine[];
};

export type ActivityResult = {
  activity: string; proactive: boolean; watching: boolean;
  intervention?: { content?: string } | null;
};

export type ChildRow = {
  child_id: string; display_name: string; age?: number; oversight?: string;
  relationship?: string; light?: string; critical_24h?: number;
  escalations_24h?: number; paused?: boolean; quiet_hours?: string | null;
};

export type ChildDetail = {
  child_id: string; display_name: string; age: number; oversight: string;
  relationship: string; sensitivity: string; critical_events: number;
  events: { type: string; condition?: string | null;
            severity?: string | null; created_at: string }[];
  privacy_note?: string | null;
};

export type ChildControls = {
  child_id: string; paused: boolean;
  quiet_start?: string | null; quiet_end?: string | null; note: string;
};

export type GuardianWatch = {
  guardian_id: string; children: ChildRow[]; haptic?: unknown;
};

/** `GET /access-log` is an **object**, not the array its name suggests — the
 *  entries are one field of it, and the other three are the answer to
 *  "is anything even being recorded". Driving this is what found it. */
export type AccessLog = {
  vaulted: boolean; access_record_kept: boolean; entries: Row[]; note: string;
};

/** `GET /audit/{uid}` — the hash-chained record of what was *done*, beside
 *  the access log's record of what was *read*.
 *
 *  `integrity` is not decoration. A list of acts nobody can check is a list,
 *  and it is the half of this answer that makes the other half mean anything,
 *  so it is typed and shown rather than dropped. `catalogue` is what would be
 *  recorded: without it an empty `trail` reads as "nothing is watched" when
 *  what it means is "nothing happened".
 *
 *  Not `entries` and not `chain` — both names are already spoken for in this
 *  API by other types, and the wire-name guard is what said so. */
export type AuditEntry = {
  seq: number; user_id: string | null; action: string; category: string;
  ref: string | null; at: string; prev_hash: string; hash: string;
};
export type AuditAction = {
  action: string; category: string; description: string;
};
export type AuditLog = {
  trail: AuditEntry[]; count: number;
  integrity: { intact: boolean; hashed: number; broken_at_seq: number | null };
  catalogue: AuditAction[]; retention: string;
};

export type EscalationPolicy = {
  sensitivity: string; ladder: string[];
  by_severity: Record<string, string>;
  safety_floors: Record<string, string>;
  ceilings: Record<string, string>;
};

export type WaiverOffer = {
  id?: string; kind: string; terms: string[]; language?: string;
  signature?: string; signed?: boolean;
};

export type SessionRow = {
  id: string; device?: string | null; prior_sessions: number;
  memory?: unknown; continuity?: unknown;
};

export type SpecialistRow = {
  condition: string; mode: string; label: string;
  qrme_profile_id?: string | null;
};

export type MedicalIdCode = {
  token: string; view_url: string; qr_svg_url: string;
};

export type RobotModel = {
  model: string; label: string; maker: string; kind: string;
  capabilities: string[]; llm_capable: boolean; first_aid: string;
};

export type RelayChannel = {
  configured: boolean; signed: boolean; envelope: string; note?: string;
};

export type RelayRoster = {
  configured: boolean; roster: string[]; ceiling: string; note?: string;
};

export type RelayRota = {
  configured: boolean; timezone: string; timezone_valid: boolean;
  evaluated_at: string; on_now: string[]; escalation_order: string[];
  anybody_on_shift: boolean; shifts: Row[]; note?: string;
};

export type LanguageOption = {
  code: string; label: string; safety_content_translated: boolean;
};

export type ImproveBoard = {
  mine: Row[]; tally: Record<string, number>; total: number;
  categories: string[];
};

export type CloudStatus = {
  cloud: boolean; model?: string | null; fallback: string;
  contribution: string;
};

/**
 * What is left of the speaking allowance.
 *
 * `used` is what has been spent — the provider calls it `character_count`,
 * which reads like a balance and is not one. `left` is the subtraction
 * already done, floored at zero, because a spent account reports a count
 * above its limit and a screen doing its own arithmetic would print a
 * negative number.
 */
export type VoiceQuota = {
  provider: string; tier?: string | null; status?: string | null;
  used: number; limit: number; left: number; exhausted: boolean;
  resets_at?: string | null;
};

/**
 * The verdict on a saved speaking key.
 *
 * `verdict` is the key, not the sentence: it travels on the wire so each
 * client renders it from its own table. `detail` is the English behind it,
 * for a client that has no row for a verdict added later.
 */
export type VoiceKeyCheck = {
  provider: string; ok: boolean; checked: boolean;
  verdict: string; detail: string;
};

export type DockState = {
  user_id: string; corner: string; state: string; face: string;
  faces: string[]; set: boolean; wanted: string; forced: boolean;
  why?: string | null;
};

export type SocialBeacon = {
  connection: string; platform: string; handle?: string | null;
  presence_url?: string | null; qr_svg: string;
};

export type PlacedCodeCard = {
  beacon: string; first_name: string; watched: boolean; note: string;
  call_first: string; badge: string; alarm_url: string;
  status?: string | null; location?: string | null;
};

export type DockCatalog = {
  faces: Record<string, string>;
  corners: Record<string, string>;
  states: Record<string, string>;
};

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
// The deployment invite key: a published deployment sets JIM_SIGNUP_KEY and
// refuses account creation without it. Stored on this device once typed,
// sent as x-signup-key on every request — the backend reads it only on the
// routes it gates.
export function getSignupKey(): string { return localStorage.getItem("jim.signupKey") || ""; }
export function setSignupKey(key: string) {
  if (key.trim()) localStorage.setItem("jim.signupKey", key.trim());
  else localStorage.removeItem("jim.signupKey");
}
export function setLlmKey(key: string) {
  if (key.trim()) localStorage.setItem("jim.llmKey", key.trim());
  else localStorage.removeItem("jim.llmKey");
}

/** For routes that answer **markup**, not JSON.
 *
 *  `req` parses the body as JSON and falls back to `null` when it is not —
 *  which is right for a crashed server answering "Internal Server Error", and
 *  wrong for a route whose whole job is to return a page. `GET /c/{bid}`
 *  serves the HTML a phone camera lands on and `…/qr.svg` serves an SVG;
 *  bound through `req` both came back as `null`, silently, and the console
 *  would have rendered the word "null" where a printable code belonged.
 *
 *  Driving them is what showed this. A route's content type is part of its
 *  shape and is not visible in its signature. */
async function reqText(path: string, opts: { token?: string } = {}): Promise<string> {
  const headers: Record<string, string> = {};
  if (opts.token) headers["authorization"] = `Bearer ${opts.token}`;
  let res: Response;
  try {
    res = await fetch(getBase() + path, { headers });
  } catch {
    recordProblem("GET", path, 0);
    throw new Error(
      `Can't reach the Guardian backend at ${getBase()}. ` +
      `Start it with "python -m jim serve", or set the backend URL in Settings.`,
    );
  }
  const text = await res.text();
  if (!res.ok) {
    recordProblem("GET", path, res.status);
    throw new Error(`That didn't work (${res.status}).`);
  }
  return text;
}

async function req<T>(path: string, opts: { method?: string; body?: unknown; token?: string } = {}): Promise<T> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (opts.token) headers["authorization"] = `Bearer ${opts.token}`;
  const llmKey = getLlmKey();
  if (llmKey) headers["x-llm-api-key"] = llmKey;
  const signupKey = getSignupKey();
  if (signupKey) headers["x-signup-key"] = signupKey;
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
    // The sentence first. A 422's `detail` is pydantic's list of rows, and
    // `JSON.stringify` on a list is exactly what the person used to read:
    // `[{"type":"missing","loc":["body","display_name"],...}]`. Every other
    // refusal carries a string `detail` and still comes through below.
    const said = body && typeof body.message === "string" && body.message
      ? body.message : null;
    const d = said ?? ((body && (body.detail || body.message)) || text.trim()
      || res.statusText);
    throw new Error(typeof d === "string" ? d : JSON.stringify(d));
  }
  return data as T;
}

export interface FirstAid {
  kind: string; title?: string; steps: string[];
  pace?: { compressions_per_minute: number; compression_to_breath_ratio: string;
           cue: { light: string; audio: string } };
}
export interface SpecialistOffer {
  available: boolean; label: string; qrme_profile_id: string;
  sent: boolean; note: string;
}
export interface SpecialistAnswer {
  delivered: boolean; area?: string; content?: string | null;
  reason?: string; note?: string;
  specialist?: { label: string; qrme_profile_id: string };
  held_for_owner_approval?: boolean;
  provenance?: { method: string; shared: string };
}
export interface Guidance { delivered: boolean; source?: string; content: string; references?: string[];
  first_aid?: FirstAid | null;
  specialist_offer?: SpecialistOffer | null;
  provenance?: { generated_by?: string; degraded?: boolean; degraded_reason?: string | null } }
// The offline coach's store and syllabus (jim/pipeline.py): what it can
// draw on, what JIM should study next, and what one press of study did.
export interface CoachStoreEntry { topic: string; lesson: string;
  source: string; model: string | null; area?: string }
export interface CoachStore { pack: number; excursions: CoachStoreEntry[];
  deposits: CoachStoreEntry[] }
export interface CoachSuggestion { area: string; topic: string; why: string }
export interface CoachCurriculum { suggested: CoachSuggestion[]; note: string }
export interface CoachStudied { studied: string; area: string | null;
  folded: boolean; left_host: boolean; excursion_id: string; note: string }

// -- an aid on the call, and the notice that goes first (jim/oncall.py) --
//
// `say` is a script, not a message: each part is the support-line notice in a
// language the far side might actually speak, picked from the dialling code
// and given more than once where the mix is known. `language_from` is the
// clue it was picked on, because a guess presented as knowledge is worse
// than a guess.
export interface CallNotice { language: string; words: string }

export interface AssistedCall {
  id: string;
  listening: boolean;
  route: string;
  recording: boolean;
  notices: CallNotice[];
  said: string;
  spoken_in: string[];
  language_from: string;
  note: string;
}

export interface CallRow {
  id: string; route: string; recording: boolean; said: string;
  spoken_in: string[]; language_from: string;
  announced_at: string | null; listened: boolean;
  opened_at: string; ended_at: string | null; ended_because: string | null;
}

// -- beside somebody while they write (jim/alongside.py) -----------------
//
// One remark on a draft. `because` is the evidence — a goal of theirs, an
// entry in the coach's store and where that entry came from — because "you
// forgot about this" with nothing under it is a guess wearing a suggestion's
// clothes. `door` is set only on an offer, and only ever names a screen this
// product has.
export interface Remark {
  kind: "forgot" | "angle" | "offer";
  says: string;
  because: string[];
  door?: string;
}

// `quiet_because` carries the reason there is nothing: an empty list on its
// own leaves a person unable to tell "nothing to add" from "it did not run".
export interface Alongside {
  remarks: Remark[];
  quiet_because: string | null;
}

// -- the unattended study pass (jim/errands.py) --------------------------
//
// One errand: a topic the offline coach could not answer, gone and studied,
// with the monitor that asked for it written on the row. `why` is the half
// worth reading — *it studied sleep* is a fact about the guardian, *it
// studied sleep because your sleep band has a learned baseline* is a fact
// about the person.
export interface Errand {
  id: string; topic: string; area: string; why: string;
  excursion_id: string; redactions: number; left_host: boolean;
  opened_at: string;
}

// `due` sits beside `studied` deliberately: an empty ledger has three
// different causes — nothing worth studying, nothing left to spend today, or
// nobody ever allowed it — and a person is entitled to tell them apart.
// `errands`, not `studied`: the study route's `studied` is the name of one
// topic, and one wire name carries one type.
export interface ErrandLedger {
  errands: Errand[]; due: CoachSuggestion[]; spent_today: number;
  daily: number; permitted: boolean;
}

export interface ErrandsRun {
  errands: Errand[]; remaining_today: number; nothing_to_study: boolean;
}

// -- engaged sessions (jim/engaged.py) -----------------------------------
//
// `reversible` and `irreversible_because` are carried separately rather than
// derived from one another, because the honest third state is a row that
// acted and can no longer be taken back — already undone, or one whose way
// back the backend could not build. A screen that renders `!reversible` as
// "irreversible" would tell somebody their journal entry left the app.
export interface EngagedTool {
  name: string; says: string; acts: boolean; reversible: boolean;
  irreversible_because: string | null;
  // The group this tool belongs to (jim/permits.py), null for a read — reads
  // are governed by nothing there, on purpose. `permitted` appears only on
  // the signed-in read: the accountless catalogue is what the product can do,
  // not what it may do for somebody who does not have an account yet.
  area: string | null; permitted?: boolean;
}
export interface EngagedReach {
  can: EngagedTool[]; tools_per_turn: number; acts_per_session: number;
  watch_ceiling: number;
}
export interface EngagedPermitArea {
  area: string; says: string; standing: "opened" | "asked";
  granted: boolean; decided_at: string | null; tools: string[];
}
export interface EngagedPermits {
  // `groups`, not `areas` — the presence already sends an `areas` and it is
  // a map of life areas, not a list of permit groups.
  user_id: string; groups: EngagedPermitArea[]; note: string;
  can: EngagedTool[];
}
export interface EngagedStep {
  tool: string | null; answered?: number | null; says?: string;
  acts?: boolean; reversible?: boolean;
  irreversible_because?: string | null; refused?: string;
}
export interface EngagedAct {
  id: string; tool: string; says: string; answered: number;
  created_at: string; undone_at: string | null; reversible: boolean;
  irreversible_because: string | null;
}
export interface StandingWatch {
  id: string; topic: string; area: string | null; created_at: string;
  cleared_at: string | null; engagement_id: string | null;
}
export interface EngagedSessionTurn {
  role: "user" | "assistant"; content: string; created_at: string;
}
export interface EngagedSession {
  engaged: boolean; id: string | null; area: string | null;
  opened_at: string | null;
  turns: EngagedSessionTurn[]; acted: EngagedAct[];
  watches: StandingWatch[];
}
export interface EngagedTurn {
  engagement_id: string; reply: string; did: EngagedStep[];
  stopped: string | null; engaged: boolean; watches: StandingWatch[];
  provenance: { generated_by: string; degraded: boolean;
    degraded_reason: string | null };
}
export interface EngagedSignOff {
  engagement_id: string; signed_off: boolean; deposited: number;
  watches: StandingWatch[]; acted: EngagedAct[];
}
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
export interface ContinuityState {
  built: boolean;
  note?: string;
  carries: string;
  version?: number;
  observations?: number;
  conditioning?: boolean;
  vector?: Record<string, number>;
  meanings?: Record<string, string>;
  method?: string;
  updated_at?: string;
}

export interface Finetune {
  build: number;
  backend: string;
  examples: number;
  helped: number;
  did_not_help: number;
  weights: number[];
  vocab: Record<string, number>;
  final_loss: number;
  first_loss: number;
  method: string;
  digest: string;
  trained_at: string;
  active?: boolean;
}

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
  device: string; devices: { key: string; name: string }[];
  steps: string[]; shortcut: string[]; seed_hint: string;
}
export interface SeedReport {
  seeded: Record<string, { days: number; baseline: number; provisional: boolean }>;
}

/** One QRME profile the attach bracket found, in the same shape a starter
 *  card arrives in — so a client renders both with the same code.
 *
 *  `attachable` and `standing` are two fields rather than one for the same
 *  reason the undo trail keeps `reversible` separate from
 *  `irreversible_because`: an age-restricted profile *is* attachable and
 *  still carries a caveat somebody needs to read, and collapsing the pair
 *  would either hide the caveat or refuse a profile that works. */
export interface SpecialistFound {
  profile_id: string;
  display_name: string;
  purpose?: string | null;
  blurb?: string | null;
  tags: string[];
  avatar?: string | null;
  avatar_kind?: string | null;
  found_by: "handle" | "id" | "words";
  attachable: boolean;
  standing: string | null;
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
export interface MealRow {
  id: string;
  note?: string | null;
  logged: string;
  described_by: string;      // note | model | photo
  photo_sealed: boolean;
  created_at?: string;
}
export interface JournalRow {
  id: string; text: string; created_at: string; vaulted?: boolean;
}
export interface DrillRow {
  id: string;
  kind: string;
  question: string;
  probes?: string[];
  response?: string | null;
  critique?: string | null;
  described_by?: string | null;   // model | checklist
  created_at?: string;
  answered_at?: string | null;
}
export interface LetterRow {
  id: string;
  week_start: string;
  body: string;
  described_by: string;      // model | digest
  created_at?: string;
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
  days: { day_number: number; meals: { slot: string; name: string }[] }[];
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
  /** "crash_watch" when the row is the tripped crash watch standing in the
   *  same queue; absent on beacon alarms. */
  kind?: string;
  beacon_id?: string | null;
  accepted_by?: string | null;
  created_at?: string;
  cleared_at?: string | null;
  /** Plain strings — a finder's words, or the crash watch's sentence. The
   *  shells decode [String]; one queue, one shape. */
  messages?: string[];
  /** True on every row this queue holds, because JIM cannot place a call at
   *  any tier — a beacon alarm is ceilinged below emergency services, and a
   *  crash watch that reached the top rung issued a dispatch *request*. The
   *  stranger's page has carried this sentence since it shipped; the carer's
   *  queue showed a tier and never said what the tier could not do. */
  call_emergency_services_yourself?: boolean;
  /** Whether a safety floor was cut to reach this tier. */
  clipped_by_ceiling?: boolean;
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

export type MoneyAccount = {
  id: string; kind: string; institution: string; label: string;
  last4?: string | null; credentials: string; balance?: number | null;
};
export type SavingsGoal = { goal: number; note?: string | null;
  reached_at?: string | null };
export type MoneyMandate = { enabled: boolean; cap_per_order: number;
  monthly_cap: number; asset_classes: string[]; scope: string };
export type MoneyOrder = { id: string; asset_class: string; amount: number;
  status: string; rationale?: string | null; created_at?: string };
export type MoneyWarning = { kind: string; message: string;
  doors?: Record<string, unknown> };
export type MoneyObservation = { recorded: boolean;
  warnings: MoneyWarning[]; orders_proposed: MoneyOrder[] };
/** Labels come with the data, in the reader's language. */
export type Appointment = {
  id: string; title: string; whenat: string; whereat?: string | null;
  email_reminder: number; qrme_order_id?: string | null; status: string;
};
export type ScheduleView = {
  appointments: Appointment[];
  email_available: boolean;
  labels: Record<string, string>;
  note: string;
};
export type ShoppingView = {
  shops: { id: string; name: string; seller: string; tag?: string | null;
           offerings: number }[];
  receipts: { id: string; qrme_order_id: string; shop_id: string;
              title: string; amount: number; currency: string;
              status: string; placed_at: string }[];
  labels: Record<string, string>;
  note: string;
};
export type PlacedShopOrder = {
  id: string; shop_id: string; status: string; title?: string;
  amount?: number; currency?: string;
};

export type CirclePerson = { user_id: string; display_name: string | null };
export type CircleTie = { other_id: string; other_name?: string | null;
  state: string };
export type CircleMessage = { id: string; low_id: string; high_id: string;
  sender_id: string; body: string; sent_at: string };
export type CircleThread = { other_id: string; other_name: string | null;
  messages: number; last_at: string };
export type CircleHomepage = {
  user_id: string; display_name: string | null; headline: string;
  about: string; theme: { bg: string; accent: string };
  links: { label: string; url: string }[];
  top_friends: CirclePerson[]; editable: boolean;
};
export type CircleView = {
  features: Record<string, boolean>;
  circle: { contacts: CirclePerson[]; invited_me: CirclePerson[];
            awaiting: CirclePerson[] };
  threads: CircleThread[];
  homepage: CircleHomepage;
  labels: Record<string, string>;
  note: string;
};
export type CircleMailbox = { threads?: CircleThread[]; with?: string;
  messages?: CircleMessage[] };

export interface StatementRow {
  id: string; account_id: string; filename: string;
  line_count: number; total_in: number; total_out: number;
  end_balance: number | null; statement_sealed: boolean; created_at?: string;
}
export interface BankLinkRow {
  id: string; account_id: string; institution: string; aggregator: string;
  status: string; created_at?: string; revoked_at?: string | null;
}
export type MoneyView = {
  accounts: MoneyAccount[]; savings: SavingsGoal | null;
  mandate: MoneyMandate | null; orders: MoneyOrder[];
  doors: Record<string, unknown>; note: string;
  labels: Record<string, string>;
};

// `contributed` is the log itself, not a count of it. Declared as a number,
// the settings line read `${state.contributed} item...` and rendered the
// whole array stringified, with `=== 1` never true — so the singular never
// appeared and the count was the payloads.
export type ContributedItem = {
  ref: string;
  at: string;
  revoked: boolean;
  payload: unknown;
};

export type CloudContribution = {
  opted_in: boolean;
  contributed: ContributedItem[];
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
  paired?: boolean;
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
  agent_sees?: string[];   // the field names, not a sentence about them
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

export interface QrmeFeedItem {
  kind: "video" | "offsite" | "room" | "desk" | "party";
  id: string;
  reason: string;
  at: string;
  /** QRME's, and passed through whole. JIM never recomputes it: the rule that
   *  footage QRME does not hold makes no request until pressed is only safe
   *  when one place decides it. */
  plays: boolean;
  loop?: boolean;
  note?: string;
  src?: string;
  profile?: { profile_id: string; name: string };
  title?: string;
  said?: string;
  facade?: { platform: string; platform_name: string; video_id: string;
             url: string };
  topic?: string;
  channel?: string;
  people?: number;
  entering?: string;
  enter?: string;
  display_name?: string;
  trade?: string;
  location?: string | null;
  blurb?: string | null;
  presence?: string;
  live?: boolean;
  human?: boolean;
  ai?: boolean;
  ringing?: string;
  ring?: string;
  shop?: {
    shop_id: string; name: string; blurb?: string | null;
    offerings: { id: string; kind: string; title: string; price: number;
                 currency: string }[];
    open: string;
  } | null;
  /** party — a QRME watch party whose host chose to be found. Counts and a
   *  facade, passed through whole; joining happens in QRME. */
  video?: { platform: string; platform_name: string; video_id: string;
            url: string } | null;
  profiles?: number;
  playing?: boolean;
  joining?: string;
  join?: string;
}

export interface QrmeFeedView {
  qrme_url: string | null;
  language: string;
  items: QrmeFeedItem[];
  cursor: string | null;
  counts: Record<string, number>;
  rules: Record<string, string>;
  open_in_qrme: string | null;
  note: string;
  posture: {
    mirrored_here: boolean;
    posts_on_your_behalf: boolean;
    can_post_from_jim: boolean;
    health_data_shared: boolean;
    watching_stored_here: boolean;
  };
}

/** What the presence says it is. `boundaries` is the half that matters: a
 *  boundary a screen cannot render is a boundary nobody can be shown. */
export interface PresenceWho {
  name: string; kind: string; says: string; note: string;
  hands_free: boolean; works_offline: boolean;
  areas: string[]; registers: string[];
  boundaries: Record<string, { value: boolean; says: string }>;
}

export interface PresenceBeat {
  speak: boolean; slot: string; register: string; area: string | null;
  line_key: string; slots: Record<string, string | number>;
  because: string[]; english: string; english_is_fallback: boolean;
  initiative: boolean; wants_reply: boolean; offline: boolean;
  deepened: boolean; deepened_line?: string; why_not?: string;
}

export interface PresenceDay {
  beats: PresenceBeat[]; hands_free: boolean; offline: boolean;
}

export interface PresenceBaseline {
  known_areas: number; of: number; needed_network: boolean;
  needed_model: boolean;
  areas: Record<string, { area: string; standing: string; known: boolean;
                          evidence: Record<string, unknown>[] }>;
}

export interface PresenceReach {
  offers: { kind: string; id?: string; who?: string; topic?: string;
            trade?: string; about?: string; warning?: string;
            opens?: string; human?: boolean; ai?: boolean }[];
  posture: Record<string, boolean>;
  note: string;
}

export interface PresenceSurfaces {
  chosen: string; rule: string; glasses_makes: string[];
  surfaces: { surface: string; audio: boolean; visual: boolean;
              private: boolean; note: string; chosen: boolean;
              reads_health_aloud: boolean; withholds: string[] }[];
}

/** A beat plus the room's verdict on it.
 *
 *  The withholding is decided on the server, before anything is synthesised,
 *  because the surface rule spent a whole release as a caption next to a
 *  button — reported by `surfaces()` and read by nothing. */
export interface PresenceSpoken extends PresenceBeat {
  speaks_on: string;
  spoken: boolean;
  shown: boolean;
  withheld: string[];
  why_not_aloud: string;
  surface_is_private: boolean;
  surface_has_audio: boolean;
  due?: boolean;
  slot_from_hour?: string;
}

export interface PresenceBearingView {
  bearing: string; default: string; choices: string[];
  effect: { registers: string[]; asks_about_your_day: boolean;
            keeps_company: boolean; says: string };
  unchanged: Record<string, string>;
  note: string;
}

export interface PresenceGrowth {
  beats_spoken: number; by_register: Record<string, number>;
  areas_i_can_see: number; of: number; what_i_changed: string[];
  about_myself: string; still_synthetic: boolean;
}

export const api = {
  // The help box — written directions about the app itself; no token, so a
  // lost person can ask before they have an account.
  help: (question: string) =>
    req<{ answer: string; ai: boolean; disclosure: string }>(
      "/help", { method: "POST", body: { question } }),

  /** What this deployment can and cannot reach.
   *
   *  Offline mode was settable before this and had nowhere to be read. A
   *  guarantee nobody can see is a guarantee nobody can check. */
  // The failure aggregate this backend keeps (see jim/api.py's
  // /v1/problems pair). Reading is the operator's: JIM_PROBLEMS_KEY as the
  // token, or nothing when asking from the machine the backend runs on.
  problemRows: (key?: string) =>
    req<{ rows: { source: string; app_version: string; platform: string;
                  op: string; status_code: number; day: string; count: number;
                  last_seen: string }[] }>(
      "/v1/problems", key ? { token: key } : {}),
  // The sending half of the same wire, for the screen's own button — the
  // launch-time auto-sender lives in errors.ts and may point at an external
  // collector; this one posts to the backend this console already talks to.
  reportProblems: (body: Record<string, unknown>) =>
    req<{ accepted: boolean; problems: number; failures: number }>(
      "/v1/problems", { method: "POST", body }),
  offlineStatus: () => req<{
    offline: boolean; external_transmission_possible: boolean;
    local_destinations_allowed: string; guarantees: string[];
    cloud_attached?: boolean;
  }>("/offline/status"),
  health: () => req<{ status: string; version?: string; tandem: boolean;
                      console?: boolean; signup_key?: boolean;
                      footsteps?: number }>("/health"),
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
                   anonymous?: boolean; legal_name?: string;
                   // A minor's activation code is delivered here — verified
                   // parental consent, not an asserted checkbox.
                   guardian_consent?: boolean; guardian_email?: string }) =>
    req<{ account_id: string; email: string; verified: boolean; code_delivery?: string;
          verification: "local" | "email";
          code_sent_to?: "guardian" | "account";
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
  // What is left of the speaking allowance. Answers 503 on a deployment
  // with no speaking provider, or one whose provider publishes no balance —
  // the refusal is the information, so the screen catches and shows it.
  voiceQuota: () => req<VoiceQuota>("/voice/quota"),
  // Is the saved key a working key? Saving only ever answered whether the
  // string was written down. 503 when there is nothing to check.
  checkVoiceKey: () =>
    req<VoiceKeyCheck>("/settings/voice/check", { method: "POST" }),
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
  // Anyone on QRME, not only the thirty-four on the shelf. A `@handle` or a
  // `prof_…` id resolves to exactly one profile; anything else is matched
  // against QRME's own public discovery cards. Every row says whether it
  // could actually stand behind a condition — see `guardian.standing`.
  searchSpecialists: (q: string) =>
    req<{ query: string; limit: number; capped: boolean;
          results: SpecialistFound[] }>(
      `/specialists/search?q=${encodeURIComponent(q)}`),
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

  // The one QRME profile that is this person (jim/synthetic_self.py). Every
  // other QRME binding above reaches somebody else's profile; this reaches
  // their own, and the preview is the payload — see docs/tandem.md.
  selfProfile: (uid: string, token: string) =>
    req<SelfProfileStatus>(`/self-profile/${uid}`, { token }),
  selfProfileLink: (uid: string, token: string,
                    body: { profile_id: string; owner_token: string }) =>
    req<SelfProfileStatus>(`/self-profile/${uid}`,
      { method: "POST", body, token }),
  // The same link, asked for the way a person can answer it.
  //
  // `selfProfileLink` above wants a `prf_…` id and an owner token. The token
  // is minted once, in QRME's create response, and there is no second place
  // to read it — so somebody who made the profile elsewhere could not fill
  // that form in at all. This sends the QRME email and password instead;
  // JIM signs in, mints the owner token and stores only that.
  //
  // `choose` comes back when the account holds more than one profile of the
  // person. The caller re-sends the same body with `profile_id` — the form
  // still holds the password, so it costs no extra typing.
  selfProfileSignIn: (uid: string, token: string,
                      body: { email: string; password: string;
                              profile_id?: string }) =>
    req<SelfProfileStatus & {
      choose?: { profile_id: string; shown_as?: string; kind?: string }[] }>(
      `/self-profile/${uid}/sign-in`, { method: "POST", body, token }),
  selfProfileUnlink: (uid: string, token: string) =>
    req<{ linked: boolean; was_linked: boolean }>(`/self-profile/${uid}`,
      { method: "DELETE", token }),
  selfProfileConsent: (uid: string, token: string, categories: string[]) =>
    req<SelfProfileStatus>(`/self-profile/${uid}/consent`,
      { method: "PUT", body: { categories }, token }),
  selfProfilePreview: (uid: string, token: string) =>
    req<SelfProfilePreview>(`/self-profile/${uid}/preview`, { token }),
  selfProfileBrief: (uid: string, token: string) =>
    req<{ sent: boolean; brief: Record<string, unknown> }>(
      `/self-profile/${uid}/brief`, { method: "POST", token }),

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

  // Meals: the photo is the receipt, the note is the log.
  logMeal: (uid: string, note: string, token: string, contentB64?: string) =>
    req<MealRow>(`/users/${uid}/meals`,
      { method: "POST",
        body: contentB64 ? { note, content: contentB64 } : { note }, token }),
  meals: (uid: string, token: string) =>
    req<MealRow[]>(`/users/${uid}/meals`, { token }),

  // Interview drills: the question bank is local; practice works offline.
  startDrill: (uid: string, token: string, kind?: string) =>
    req<DrillRow>(`/users/${uid}/drills`,
      { method: "POST", body: kind ? { kind } : {}, token }),
  answerDrill: (uid: string, drillId: string, answer: string, token: string) =>
    req<DrillRow>(`/users/${uid}/drills/${drillId}/answer`,
      { method: "POST", body: { answer }, token }),
  drills: (uid: string, token: string) =>
    req<DrillRow[]>(`/users/${uid}/drills`, { token }),

  // The weekly letter: what the last seven days actually held, in words.
  writeLetter: (uid: string, token: string) =>
    req<LetterRow>(`/users/${uid}/letters`, { method: "POST", body: {}, token }),
  letters: (uid: string, token: string) =>
    req<LetterRow[]>(`/users/${uid}/letters`, { token }),

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

  // The watch bridge: an automation drips readings at a tokened URL; the
  // wearable's own export seeds the baseline from history. The device
  // argument picks which wearable family the recipe teaches.
  getWatchChannel: (uid: string, token: string, device = "apple_watch") =>
    req<WatchChannel>(
      `/watch/channel/${uid}?device=${encodeURIComponent(device)}`,
      { token }),
  rotateWatchChannel: (uid: string, token: string, device = "apple_watch") =>
    req<WatchChannel>(
      `/watch/channel/${uid}/rotate?device=${encodeURIComponent(device)}`,
      { method: "POST", token }),
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
      const body = data as { detail?: unknown; message?: unknown } | null;
      // The sentence first. A 422's `detail` is pydantic's list of rows, and
      // `JSON.stringify` on a list is exactly what the person used to read:
      // `[{"type":"missing","loc":["body","display_name"],...}]`. Every other
      // refusal carries a string `detail` and still comes through below.
      const said = body && typeof body.message === "string" && body.message
        ? body.message : null;
      const d = said ?? ((body && body.detail) || text.trim() || res.statusText);
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
  // `respiratory_rate` is what BiometricSample calls it. Sent as
  // `respiration`, it was dropped by the model with no error — the
  // console collected a breathing rate and the guardian never saw it.
  monitor: (uid: string, body: { heart_rate: number;
            respiratory_rate?: number; stress_level?: number },
            token: string) =>
    req<MonitorResult>(`/monitor/${uid}`, { method: "POST", body, token }),
  // Spec [0039]: whether the guidance actually worked. "No" escalates toward
  // a live person and comes back with the humans reachable right now.
  answerFollowup: (uid: string, body: { helped: boolean; note?: string }, token: string) =>
    req<FollowupResult>(`/followup/${uid}`, { method: "POST", body, token }),
  // FIG. 2 boxes 222-226: the community door. Rooms and places come from
  // QRME through the tandem; nothing is mirrored into JIM.
  // QRME's public feed, through the same door the rooms use. Read-only by
  // construction — there is no post binding here, because publishing belongs
  // in QRME under the user's own QRME identity.
  // -- the presence (jim/presence.py) --
  //
  // Every read here is answered from rows the backend already holds. The
  // screen may be open on a train with no signal and the day still arrives:
  // that is the point of the module, so it is the point of these bindings.
  presenceWho: () => req<PresenceWho>("/presence"),
  presenceBaseline: (uid: string, token: string) =>
    req<PresenceBaseline>(`/presence/${uid}/baseline`, { token }),
  presenceDay: (uid: string, token: string) =>
    req<PresenceDay>(`/presence/${uid}/day`, { token }),
  presenceBeat: (uid: string, token: string, slot: string) =>
    req<PresenceBeat>(`/presence/${uid}/beat?slot=${encodeURIComponent(slot)}`, { token }),
  presenceDeepen: (uid: string, token: string, slot: string) =>
    req<PresenceBeat>(`/presence/${uid}/deepen?slot=${encodeURIComponent(slot)}`, { token, method: "POST" }),
  presenceReach: (uid: string, token: string) =>
    req<PresenceReach>(`/presence/${uid}/reach`, { token }),
  presenceSurfaces: (uid: string, token: string) =>
    req<PresenceSurfaces>(`/presence/${uid}/surfaces`, { token }),
  presenceChooseSurface: (uid: string, token: string, surface: string) =>
    req<PresenceSurfaces>(`/presence/${uid}/surface`, { token, method: "PUT", body: { speaks_on: surface } }),
  presenceSay: (uid: string, token: string, slot: string) =>
    req<PresenceSpoken>(`/presence/${uid}/say?slot=${encodeURIComponent(slot)}`, { token }),
  // The hands-free question. Deliberately does not record: a device polling
  // every ten minutes must not burn a beat the person never heard.
  presenceDue: (uid: string, token: string) =>
    req<PresenceSpoken>(`/presence/${uid}/due`, { token }),
  presenceBearing: (uid: string, token: string) =>
    req<PresenceBearingView>(`/presence/${uid}/bearing`, { token }),
  // A register, never a capability — the same six areas are watched in both,
  // which is why this reads back the whole posture rather than an ack.
  presenceSetBearing: (uid: string, token: string, bearing: string) =>
    req<PresenceBearingView>(`/presence/${uid}/bearing`, { token, method: "PUT", body: { bearing } }),
  presenceGrowth: (uid: string, token: string) =>
    req<PresenceGrowth>(`/presence/${uid}/growth`, { token }),
  qrmeFeed: (uid: string, token: string, cursor?: string) =>
    req<QrmeFeedView>(`/community/${uid}/feed`
      + (cursor ? `?cursor=${encodeURIComponent(cursor)}` : ""), { token }),
  community: (uid: string, token: string, locality?: string) =>
    req<CommunityView>(`/community/${uid}` + (locality ? `?locality=${encodeURIComponent(locality)}` : ""), { token }),
  communityVisit: (uid: string, room_id: string, token: string) =>
    req<{ noted: boolean; room_id: string; stored: string }>(
      `/community/${uid}/visits`, { method: "POST", body: { room_id }, token }),
  // Claim 11: the user-specific model, derived and (with a tandem) sealed.
  // The offline fine-tune. Beside `adaptation` and not folded into it: that
  // one recomputes a profile that conditions a prompt, this one trains
  // weights. A reader who cannot tell which happened has been told nothing.
  finetune: (uid: string, token: string) =>
    req<Finetune>(`/finetune/${uid}`, { token }),
  runFinetune: (uid: string, token: string) =>
    req<Finetune>(`/finetune/${uid}`, { method: "POST", token }),
  // Training and using are two decisions. Off takes effect on the next reply.
  setFinetuneActive: (uid: string, token: string, active: boolean) =>
    req<{ user_id: string; active: boolean; digest: string; backend: string }>(
      `/finetune/${uid}/active`, { method: "PUT", token, body: { active } }),
  adaptation: (uid: string, token: string) =>
    req<AdaptationProfile>(`/adaptation/${uid}`, { token }),
  rebuildAdaptation: (uid: string, token: string) =>
    req<AdaptationProfile>(`/adaptation/${uid}`, { method: "POST", token }),
  // The state that survives between sessions. Counts and timings only — the
  // vector is derived from tallies and carries nothing anybody wrote.
  continuity: (uid: string, token: string) =>
    req<ContinuityState>(`/continuity/${uid}`, { token }),
  forgetContinuity: (uid: string, token: string) =>
    req<{ forgotten: boolean }>(`/continuity/${uid}`, { method: "DELETE", token }),
  anonymity: (uid: string, token: string) =>
    req<AnonymityPosture>(`/anonymity/${uid}`, { token }),
  checkin: (uid: string, body: { mood: number; energy: number; stress?: number; note?: string }, token: string) =>
    req<CheckinResult>(`/checkin/${uid}`, { method: "POST", body, token }),
  coach: (uid: string, body: { area: string; message: string }, token: string) =>
    req<Guidance>(`/coach/${uid}`, { method: "POST", body, token }),
  // The person's own question to the QRME specialist covering this area.
  // `coach` only *offers*; this is the door they choose, because what crosses
  // is what they wrote.
  coachSpecialist: (uid: string, body: { area: string; message: string }, token: string) =>
    req<SpecialistAnswer>(`/coach/${uid}/specialist`, { method: "POST", body, token }),
  // The store the offline stack predicts from, the syllabus read off the
  // monitored surface, and the one-press study that imports the findings.
  coachStore: (uid: string, token: string) =>
    req<CoachStore>(`/coach/${uid}/store`, { token }),
  coachCurriculum: (uid: string, token: string) =>
    req<CoachCurriculum>(`/coach/${uid}/curriculum`, { token }),
  coachStudy: (uid: string, body: { topic?: string; area?: string }, token: string) =>
    req<CoachStudied>(`/coach/${uid}/study`, { method: "POST", body, token }),
  baseline: (uid: string, token: string) =>
    req<BaselineMetric[]>(`/baseline/${uid}`, { token }),
  // The unattended pass: what the coach missed, gone and learned. Refused
  // without the permit, and refused again once the day's budget is spent —
  // two different refusals, because "not allowed" and "not today" are two
  // different things to be told.
  // Set up an assisted call. It is not listening: what comes back is the
  // notice to play, and `callAnnounced` is the only way out of that state.
  // `number` is read for the language and dropped — it is never stored.
  openCall: (uid: string, body: { route: string; recording?: boolean;
                                  number?: string }, token: string) =>
    req<AssistedCall>(`/calls/${uid}`, { method: "POST", body, token }),
  // Confirmed by whatever played it: the server knows what should have been
  // said, and only the thing holding the audio knows whether it was.
  callAnnounced: (uid: string, callId: string, token: string) =>
    req<{ id: string; listening: boolean; announced_at: string;
          said: string }>(
      `/calls/${uid}/${callId}/announced`, { method: "POST", token }),
  calls: (uid: string, token: string) =>
    req<CallRow[]>(`/calls/${uid}`, { token }),
  endCall: (uid: string, callId: string, token: string) =>
    req<{ id: string; listening: boolean; ended_because: string }>(
      `/calls/${uid}/${callId}`, { method: "DELETE", token }),
  // Every path that hands the agent something heard goes through here, and
  // through `oncall.may_listen` first.
  callHeard: (uid: string, callId: string, token: string) =>
    req<{ listening: boolean; id: string }>(
      `/calls/${uid}/${callId}/heard`, { method: "POST", token }),
  // A draft, read on the device and dropped. Nothing is stored and nothing
  // is edited: remarks come back, and applying one is the person's own act.
  alongside: (uid: string, body: { draft: string; area?: string },
              token: string) =>
    req<Alongside>(`/alongside/${uid}`, { method: "POST", body, token }),
  errands: (uid: string, token: string) =>
    req<ErrandLedger>(`/errands/${uid}`, { token }),
  runErrands: (uid: string, token: string) =>
    req<ErrandsRun>(`/errands/${uid}`, { method: "POST", token }),

  // -- engaged: the online Guardian you leave running ---------------------
  //
  // `coach` above is a turn. These are a session: it stays open until you
  // sign off, it can act on your account while it is open, and everything it
  // does lands on a trail you can take back one row at a time. See
  // jim/engaged.py for what it may touch and why the reach is a written list
  // rather than the token's full authority.
  //
  // `engagedReach` carries no token on purpose — it is how somebody decides
  // whether to open one at all, and a list of what a feature would be
  // allowed to touch is not the feature.
  engagedReach: () => req<EngagedReach>("/engaged/reach"),
  engaged: (uid: string, token: string) =>
    req<EngagedSession>(`/engaged/${uid}`, { token }),
  engage: (uid: string, body: { area: string }, token: string) =>
    req<EngagedSession>(`/engaged/${uid}`, { method: "POST", body, token }),
  engagedTurn: (uid: string, body: { message: string }, token: string) =>
    req<EngagedTurn>(`/engaged/${uid}/turn`, { method: "POST", body, token }),
  engagedSignOff: (uid: string, body: { topics: string[] }, token: string) =>
    req<EngagedSignOff>(`/engaged/${uid}/sign-off`,
      { method: "POST", body, token }),
  engagedActs: (uid: string, token: string) =>
    req<EngagedAct[]>(`/engaged/${uid}/acts`, { token }),
  engagedUndo: (uid: string, actId: string, token: string) =>
    req<Row>(`/engaged/${uid}/acts/${actId}/undo`,
      { method: "POST", token }),
  // The connectors screen, turned around to face this account's own settings.
  // Two calls rather than one shape: the list is a read anybody signed in can
  // make, and a grant is a decision somebody takes one row at a time.
  engagedPermits: (uid: string, token: string) =>
    req<EngagedPermits>(`/engaged/${uid}/permits`, { token }),
  engagedSetPermit: (uid: string, area: string, body: { granted: boolean },
                     token: string) =>
    req<EngagedPermitArea>(`/engaged/${uid}/permits/${area}`,
      { method: "PUT", body, token }),
  engagedWatches: (uid: string, token: string) =>
    req<StandingWatch[]>(`/engaged/${uid}/watches`, { token }),
  engagedWatch: (uid: string, body: { topic: string; area?: string },
                 token: string) =>
    req<StandingWatch>(`/engaged/${uid}/watches`,
      { method: "POST", body, token }),
  engagedClearWatch: (uid: string, watchId: string, token: string) =>
    req<Row>(`/engaged/${uid}/watches/${watchId}`,
      { method: "DELETE", token }),

  // The ways back the undo trail replays, and the doors a person should
  // always have had: until an engaged session needed to take a check-in
  // back, nothing in this product could delete one.
  removeCheckin: (uid: string, checkinId: string, token: string) =>
    req<Row>(`/checkin/${uid}/${checkinId}`, { method: "DELETE", token }),
  removeJournal: (uid: string, entryId: string, token: string) =>
    req<Row>(`/journal/${uid}/${entryId}`, { method: "DELETE", token }),
  removeGoal: (uid: string, goalId: string, token: string) =>
    req<Row>(`/goals/${uid}/${goalId}`, { method: "DELETE", token }),
  removeHabit: (uid: string, habitId: string, token: string) =>
    req<Row>(`/habits/${uid}/${habitId}`, { method: "DELETE", token }),
  unlogHabit: (uid: string, habitId: string, day: string, token: string) =>
    req<Row>(`/habits/${uid}/${habitId}/log/${day}`,
      { method: "DELETE", token }),

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
  // The money guardian. The overview carries its own `labels` in the
  // reader's language — the card renders what the server hands it, because
  // this console has no translation table and its English backlog is a
  // ratchet that only shrinks.
  // The Guardian's calendar. Labels ride the view; reminders live on the
  // proactive ladder's bottom rung, raised by the monitor/observe senses.
  scheduleView: (uid: string, token: string) =>
    req<ScheduleView>(`/schedule/${uid}`, { token }),
  scheduleBook: (uid: string, body: { title: string; when: string;
    where?: string; email_reminder?: boolean; shop_id?: string;
    offering_id?: string }, token: string) =>
    req<Appointment>(`/schedule/${uid}`, { method: "POST", body, token }),
  scheduleCancel: (uid: string, appointmentId: string, token: string) =>
    req<Appointment>(`/schedule/${uid}/${appointmentId}`,
      { method: "DELETE", token }),
  // Shopping through the tandem. The shelf carries its own `labels` in the
  // reader's language for the same reason the money card does; the receipt
  // history lives in JIM, never asked of QRME.
  shoppingView: (uid: string, token: string, tag?: string) =>
    req<ShoppingView>(`/shopping/${uid}${tag ? `?tag=${encodeURIComponent(tag)}` : ""}`,
      { token }),
  shoppingOrder: (uid: string, body: { shop_id: string; offering_id: string;
    quantity?: number }, token: string) =>
    req<PlacedShopOrder>(`/shopping/${uid}/order`,
      { method: "POST", body, token }),
  shoppingCancel: (uid: string, qrmeOrderId: string, token: string) =>
    req<PlacedShopOrder>(`/shopping/${uid}/cancel`,
      { method: "POST", body: { qrme_order_id: qrmeOrderId }, token }),
  // Your circle: contacts by mutual invitation, messages that never leave
  // this deployment, per-user switches, and the homepage sandbox. The view
  // carries its own `labels` in the reader's language, like the shelf above.
  circleView: (uid: string, token: string) =>
    req<CircleView>(`/circle/${uid}`, { token }),
  circleFeature: (uid: string, body: { feature: string; enabled: boolean },
    token: string) =>
    req<Record<string, boolean>>(`/circle/${uid}/features`,
      { method: "PUT", body, token }),
  circleInvite: (uid: string, otherId: string, token: string) =>
    req<CircleTie>(`/circle/${uid}/contacts`,
      { method: "POST", body: { other_id: otherId }, token }),
  circleLeave: (uid: string, otherId: string, token: string) =>
    req<CircleTie>(`/circle/${uid}/contacts/${otherId}`,
      { method: "DELETE", token }),
  circleSend: (uid: string, body: { to: string; body: string },
    token: string) =>
    req<CircleMessage>(`/circle/${uid}/messages`,
      { method: "POST", body, token }),
  circleMessages: (uid: string, token: string, withId?: string) =>
    req<CircleMailbox>(
      `/circle/${uid}/messages${withId ? `?with_id=${encodeURIComponent(withId)}` : ""}`,
      { token }),
  circleHomepage: (uid: string, otherId: string, token: string) =>
    req<CircleHomepage>(`/circle/${uid}/homepage/${otherId}`, { token }),
  circleEditHomepage: (uid: string, body: { headline?: string;
    about?: string; theme?: { bg: string; accent: string };
    links?: { label: string; url: string }[]; top_friends?: string[] },
    token: string) =>
    req<CircleHomepage>(`/circle/${uid}/homepage`,
      { method: "PUT", body, token }),
  moneyView: (uid: string, token: string) =>
    req<MoneyView>(`/money/${uid}`, { token }),
  moneyAddAccount: (uid: string, body: { kind: string; institution: string;
    label?: string; account_number?: string; routing_number?: string;
    api_key?: string }, token: string) =>
    req<MoneyAccount>(`/money/${uid}/accounts`,
      { method: "POST", body, token }),
  moneyObserve: (uid: string, body: { account_id: string; balance?: number;
    note?: string }, token: string) =>
    req<MoneyObservation>(`/money/${uid}/observe`,
      { method: "POST", body, token }),
  // Statements: sealed in the vault, read locally. Links: written
  // aggregator consents whose status never claims data not pulled.
  moneyDropStatement: (uid: string, body: { account_id: string;
      filename?: string; content: string }, token: string) =>
    req<StatementRow>(`/money/${uid}/statements`,
      { method: "POST", body, token }),
  moneyStatements: (uid: string, token: string) =>
    req<StatementRow[]>(`/money/${uid}/statements`, { token }),
  moneyLinkBank: (uid: string, body: { institution: string;
      aggregator: string; kind?: string }, token: string) =>
    req<BankLinkRow>(`/money/${uid}/links`,
      { method: "POST", body, token }),
  moneyLinks: (uid: string, token: string) =>
    req<BankLinkRow[]>(`/money/${uid}/links`, { token }),
  moneySyncBank: (uid: string, linkId: string, token: string) =>
    req<BankLinkRow>(`/money/${uid}/links/${linkId}/sync`,
      { method: "POST", body: {}, token }),
  moneyRevokeLink: (uid: string, linkId: string, token: string) =>
    req<BankLinkRow>(`/money/${uid}/links/${linkId}`,
      { method: "DELETE", token }),
  moneySetSavings: (uid: string, body: { goal: number; note?: string },
    token: string) =>
    req<SavingsGoal>(`/money/${uid}/savings`,
      { method: "PUT", body, token }),
  moneySetMandate: (uid: string, body: { enabled: boolean;
    cap_per_order?: number; monthly_cap?: number; asset_classes?: string[];
    scope?: string }, token: string) =>
    req<MoneyMandate>(`/money/${uid}/mandate`,
      { method: "PUT", body, token }),
  setLocality: (uid: string, locality: string | null, token: string) =>
    req<{ locality: string | null }>(`/users/${uid}/locality`,
      { method: "PUT", body: { locality }, token }),

  // Devices come first because channel 2 depends on them: a microphone
  // attaches to a device the account already knows, never to a typed name.
  devices: (uid: string, token: string) =>
    req<DeviceRow[]>(`/devices/${uid}`, { token }),
  registerDevice: (uid: string, body: { name: string; kind: string;
    transport?: string; has_llm?: boolean; paired?: boolean },
    token: string) =>
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

  // =====================================================================
  // The rest of the API.
  //
  // One hundred and nine routes that the desktop console could not reach on
  // its own. The per-client audit found them: the union guard had been
  // answering *some client can reach this*, and the phone shells could, so
  // the number looked healthy while a desktop user could not do any of it.
  //
  // **On the types below.** The house rule is that shapes are read off a
  // running server rather than off route signatures. These were: a backend
  // was started on 8791 and every family below was called against it.
  //
  // Driving is not a formality. It caught three bindings written from the
  // route table that were wrong about the wire:
  //
  //   * `GET /access-log/{uid}` returns an **object** — `{vaulted,
  //     access_record_kept, entries, note}` — not the array of entries the
  //     name suggests. Typed `Row[]`, the screen would have mapped over an
  //     object and rendered nothing, silently, which is the worst way for a
  //     privacy log to fail.
  //   * `GET /custody/{uid}/provenance` requires a `key` query parameter.
  //     Without it the call is a 422 every time.
  //   * `GET /users/{uid}/referral/clinicians` requires `condition`. Same.
  //
  // It also produced the enums: a goal's `area` and a condition's name are
  // closed sets, and the server names its members in the 422 body. Those are
  // written out below rather than left as `string`, because a typo in a
  // literal union is caught at build time and a typo in a string is caught
  // by a user.
  //
  // Where a response is a large nested document that the screen only reads
  // a few fields from — the plan catalogue, the connector catalogue, the
  // tutorial — it stays `Row`. A loose type that is true is worth more than
  // a narrow one that is a guess: the guess is what put `waiting.length` on
  // a number.
  // =====================================================================

  // -- guardianship: a child's account, and what an adult may see ---------
  children: (guardianId: string, token: string) =>
    req<ChildRow[]>(`/guardians/${guardianId}/children`, { token }),
  child: (guardianId: string, childId: string, token: string) =>
    req<ChildDetail>(`/guardians/${guardianId}/children/${childId}`, { token }),
  // `relationship` is the *adult's* relationship to the child — the server
  // accepts `parent` or `legal_guardian` and nothing else. Naming the child's
  // side of it ("daughter") is a 422.
  addChild: (guardianId: string, body: { display_name: string;
               birthdate: string; relationship?: "parent" | "legal_guardian";
               guardian_phone?: string; resting_heart_rate?: number;
               known_conditions?: string[]; language?: string },
             token: string) =>
    req<Row>(`/guardians/${guardianId}/children`,
      { method: "POST", body, token }),
  removeChild: (guardianId: string, childId: string, token: string) =>
    req<Row>(`/guardians/${guardianId}/children/${childId}`,
      { method: "DELETE", token }),
  setChildControls: (guardianId: string, childId: string,
                     body: { paused?: boolean; quiet_start?: string;
                             quiet_end?: string }, token: string) =>
    req<ChildControls>(`/guardians/${guardianId}/children/${childId}/controls`,
      { method: "PUT", body, token }),
  guardianWatch: (guardianId: string, token: string) =>
    req<GuardianWatch>(`/guardians/${guardianId}/watch`, { token }),

  // -- what somebody is trying to do: goals, habits, budgets, activity ----
  goals: (uid: string, token: string) =>
    req<GoalRow[]>(`/goals/${uid}`, { token }),
  addGoal: (uid: string, body: { area: GoalArea; title: string;
                                 target?: string }, token: string) =>
    req<GoalRow>(`/goals/${uid}`, { method: "POST", body, token }),
  updateGoal: (uid: string, goalId: string,
               body: { progress?: number; status?: string }, token: string) =>
    req<GoalRow>(`/goals/${uid}/${goalId}`, { method: "PATCH", body, token }),
  habits: (uid: string, token: string) =>
    req<HabitRow[]>(`/habits/${uid}`, { token }),
  addHabit: (uid: string, body: { name: string }, token: string) =>
    req<HabitRow>(`/habits/${uid}`, { method: "POST", body, token }),
  logHabit: (uid: string, habitId: string, token: string) =>
    req<HabitRow>(`/habits/${uid}/${habitId}/log`,
      { method: "POST", token }),
  budgets: (uid: string, token: string) =>
    req<BudgetBoard>(`/budgets/${uid}`, { token }),
  setBudget: (uid: string, body: { category?: string;
                                   monthly_limit: number }, token: string) =>
    req<BudgetLine>(`/budgets/${uid}`, { method: "PUT", body, token }),
  clearBudget: (uid: string, category: string, token: string) =>
    req<Row>(`/budgets/${uid}/${category}`, { method: "DELETE", token }),
  logActivity: (uid: string, body: { activity?: string; signals?: Row;
                                     note?: string }, token: string) =>
    req<ActivityResult>(`/activity/${uid}`, { method: "POST", body, token }),

  // -- the guide, and the dock it lives in --------------------------------
  tutorial: () => req<Row>("/tutorial"),
  tutorialStep: (key: string) => req<Row>(`/tutorial/steps/${key}`),
  tutorialForScreen: (screen: number) =>
    req<Row>(`/tutorial/for-screen/${screen}`),
  tutorialProgress: (learnerId: string) =>
    req<Row>(`/tutorial/progress/${learnerId}`),
  startTutorial: (body: Body) =>
    req<Row>("/tutorial/start", { method: "POST", body }),
  finishTutorialStep: (body: Body) =>
    req<Row>("/tutorial/done", { method: "POST", body }),
  helpTopics: () => req<{ topics: string[] }>("/help/topics"),
  dockFaces: () => req<DockCatalog>("/dock/faces"),
  dockWhere: (face: string) => req<Row>(`/dock/where/${face}`),
  dock: (uid: string, token: string, alarmActive?: boolean) =>
    req<DockState>(`/dock/${uid}`
      + (alarmActive ? "?alarm_active=true" : ""), { token }),
  dockFace: (uid: string, name: string, token: string) =>
    req<Row>(`/dock/${uid}/face/${name}`, { token }),
  setDock: (uid: string, body: Body, token: string) =>
    req<Row>(`/dock/${uid}`, { method: "PUT", body, token }),

  // -- social accounts, the codes that reach them, and excursions ---------
  socialAccounts: (uid: string, token: string) =>
    req<Row[]>(`/social/${uid}`, { token }),
  connectSocialAccount: (uid: string, body: Body, token: string) =>
    req<Row>(`/social/${uid}`, { method: "POST", body, token }),
  // Both of these want the owner's token, unlike the placed-code pair above.
  // That asymmetry is right — a care code on a front door is *for* strangers,
  // and the address of somebody's Mastodon account is not — but it is not
  // visible in either signature. Driving them is what produced it.
  socialBeaconCard: (cid: string, token: string) =>
    req<SocialBeacon>(`/social/connection/${cid}/beacon`, { token }),
  socialQr: (cid: string, token: string) =>
    reqText(`/social/connection/${cid}/qr.svg`, { token }),
  collectFromSocial: (cid: string, body: Body, token: string) =>
    req<Row>(`/social/connection/${cid}/collect`,
      { method: "POST", body, token }),
  scrapeSocial: (cid: string, token: string) =>
    req<Row>(`/social/connection/${cid}/scrape`, { method: "POST", token }),
  publishToSocial: (cid: string, body: Body, token: string) =>
    req<Row>(`/social/connection/${cid}/publish`,
      { method: "POST", body, token }),
  disconnectSocialAccount: (cid: string, token: string) =>
    req<Row>(`/social/connection/${cid}`, { method: "DELETE", token }),
  // A placed code. `/c/…` is the scan path a phone camera lands on.
  // The page a phone camera lands on — HTML, not JSON.
  placedCode: (bid: string) => reqText(`/c/${bid}`),
  placedCodeCard: (bid: string) => req<PlacedCodeCard>(`/c/${bid}/card`),
  placedCodeQr: (bid: string) => reqText(`/c/${bid}/qr.svg`),
  raiseFromCode: (bid: string, body: Body) =>
    req<Row>(`/c/${bid}/alarm`, { method: "POST", body }),
  pickUpCode: (bid: string, token: string) =>
    req<Row>(`/beacons/${bid}`, { method: "DELETE", token }),
  excursions: (uid: string, token: string) =>
    req<Row[]>(`/excursions/${uid}`, { token }),
  startExcursion: (uid: string, body: Body, token: string) =>
    req<Row>(`/excursions/${uid}`, { method: "POST", body, token }),
  excursionEntry: (cid: string) => req<Row>(`/excursions/entry/${cid}`),
  learnFromExcursion: (cid: string, token: string) =>
    req<Row>(`/excursions/entry/${cid}/learn`, { method: "POST", token }),

  // -- specialists, referrals, and work handed to one ---------------------
  specialists: () => req<SpecialistRow[]>("/specialists"),
  seedSpecialists: (token: string) =>
    req<Row>("/specialists/seed", { method: "POST", token }),
  seedTandemSpecialists: (token: string) =>
    req<Row>("/specialists/seed/tandem", { method: "POST", token }),
  // An **object**, not the array the name suggests: `{area, locality,
  // clinicians, reason?}`. Typed `Row[]` here, the Attending screen called
  // `.map` on it and threw `clinicians.map is not a function` the moment
  // anybody pressed *who would this reach* — and the `reason` the backend
  // composes for an empty list ("no clinician registered") had never been
  // shown to anybody, because the screen never got that far.
  referralClinicians: (uid: string, condition: string, token: string) =>
    req<{ area: string; locality: string | null; clinicians: Row[];
          reason?: string }>(
      `/users/${uid}/referral/clinicians`
      + `?condition=${encodeURIComponent(condition)}`, { token }),
  referralRequests: (uid: string, token: string) =>
    req<Row[]>(`/users/${uid}/referral/requests`, { token }),
  prepareReferral: (uid: string, body: Body, token: string) =>
    req<Row>(`/users/${uid}/referral/prepare`,
      { method: "POST", body, token }),
  markReferralReleased: (uid: string, requestId: string, body: Body,
                         token: string) =>
    req<Row>(`/users/${uid}/referral/requests/${requestId}/released`,
      { method: "POST", body, token }),
  specialistTasks: (uid: string, token: string) =>
    req<Row[]>(`/users/${uid}/specialist-tasks`, { token }),
  specialistTask: (uid: string, taskId: string, token: string) =>
    req<Row>(`/users/${uid}/specialist-tasks/${taskId}`, { token }),
  handToSpecialist: (uid: string, body: Body, token: string) =>
    req<Row>(`/users/${uid}/specialist-tasks`,
      { method: "POST", body, token }),
  advanceSpecialistTask: (uid: string, taskId: string, token: string) =>
    req<Row>(`/users/${uid}/specialist-tasks/${taskId}/advance`,
      { method: "POST", token }),

  // -- a body to move through the house -----------------------------------
  roboticsCatalog: () => req<{ robots: RobotModel[] }>("/robotics/catalog"),
  robots: (uid: string, token: string) =>
    req<Row[]>(`/robots/${uid}`, { token }),
  bindRobot: (uid: string, body: { model: string; name?: string;
                                   llm_provider?: string }, token: string) =>
    req<Row>(`/robots/${uid}`, { method: "POST", body, token }),
  commandRobot: (uid: string, robotId: string, body: Body, token: string) =>
    req<Row>(`/robots/${uid}/${robotId}/command`,
      { method: "POST", body, token }),
  unbindRobot: (uid: string, robotId: string, token: string) =>
    req<Row>(`/robots/${uid}/${robotId}`, { method: "DELETE", token }),

  // -- the plan, and what is held about you -------------------------------
  plans: () => req<Row>("/plans"),
  membership: (accountId: string, token: string) =>
    req<Row>(`/memberships/${accountId}`, { token }),
  setMembership: (accountId: string, body: Body, token: string) =>
    req<Row>(`/memberships/${accountId}`, { method: "POST", body, token }),
  cancelMembership: (accountId: string, token: string) =>
    req<Row>(`/memberships/${accountId}`, { method: "DELETE", token }),
  waivers: (uid: string, token: string) =>
    req<WaiverOffer>(`/waivers/${uid}`, { token }),
  signWaiver: (uid: string, body: { signature: string; accept?: boolean },
               token: string) =>
    req<WaiverOffer>(`/waivers/${uid}`, { method: "POST", body, token }),
  withdrawWaiver: (uid: string, token: string) =>
    req<Row>(`/waivers/${uid}`, { method: "DELETE", token }),
  custody: (uid: string, token: string) =>
    req<Row>(`/custody/${uid}`, { token }),
  custodyProvenance: (uid: string, key: string, token: string) =>
    req<Row>(`/custody/${uid}/provenance?key=${encodeURIComponent(key)}`,
      { token }),
  // Everything held about a person, as one document — the answer to *what
  // do you have*, which this product had no route for at all while offering
  // the erase below it.
  exportEverything: (uid: string, token: string) =>
    req<{ user: Row | null; tables: Record<string, Row[]>; note: string }>(
      `/data/${uid}`, { token }),
  // Erases everything held about a person. There is no undo, which is the
  // point of it.
  eraseEverything: (uid: string, token: string) =>
    req<Row>(`/data/${uid}`, { method: "DELETE", token }),
  accessLog: (uid: string, token: string) =>
    req<AccessLog>(`/access-log/${uid}`, { token }),
  // The other half of the same question. The access log says who *read*
  // your record; this says what was *done* — and whether the saying of it
  // has been edited since.
  auditLog: (uid: string, token: string) =>
    req<AuditLog>(`/audit/${uid}`, { token }),

  // -- how it speaks, and how it is tuned ---------------------------------
  languages: () => req<{ languages: LanguageOption[] }>("/languages"),
  userLanguage: (uid: string, token: string) =>
    req<Row>(`/language/${uid}`, { token }),
  setUserLanguage: (uid: string, body: Body, token: string) =>
    req<Row>(`/language/${uid}`, { method: "PUT", body, token }),
  translate: (uid: string, body: Body, token: string) =>
    req<Row>(`/translate/${uid}`, { method: "POST", body, token }),
  setPersonality: (uid: string, body: Body, token: string) =>
    req<Row>(`/personality/${uid}`, { method: "PUT", body, token }),
  setSensitivity: (uid: string, body: Body, token: string) =>
    req<Row>(`/sensitivity/${uid}`, { method: "PUT", body, token }),
  providerFor: (uid: string, token: string) =>
    req<Row>(`/provider/${uid}`, { token }),
  clearVoice: (token: string) =>
    req<Row>("/settings/voice", { method: "DELETE", token }),
  connectorsCatalog: () => req<Row>("/connectors/catalog"),
  cloudStatus: () => req<CloudStatus>("/cloud/status"),

  // -- being looked after -------------------------------------------------
  coachHistory: (uid: string, token: string, area?: string) =>
    req<Row[]>(`/coach/${uid}`
      + (area ? `?area=${encodeURIComponent(area)}` : ""), { token }),
  insights: (uid: string, token: string) =>
    req<Row[]>(`/insights/${uid}`, { token }),
  report: (uid: string, token: string) => req<Row>(`/report/${uid}`, { token }),
  events: (uid: string, token: string) =>
    req<Row[]>(`/events/${uid}`, { token }),
  followup: (uid: string, token: string) =>
    req<Row>(`/followup/${uid}`, { token }),
  calmHistory: (uid: string, token: string) =>
    req<Row[]>(`/calm/${uid}/history`, { token }),
  escalationPolicy: (uid: string, token: string) =>
    req<EscalationPolicy>(`/escalation-policy/${uid}`, { token }),
  communityVisits: (uid: string, token: string) =>
    req<Row[]>(`/community/${uid}/visits`, { token }),
  sources: (uid: string, token: string) =>
    req<Row[]>(`/sources/${uid}`, { token }),
  setSources: (uid: string, body: { source: string; consented: boolean },
               token: string) =>
    req<{ source: string; consented: boolean }>(`/sources/${uid}`,
      { method: "PUT", body, token }),
  recordCondition: (uid: string, body: { condition: ConditionName;
                                         note?: string }, token: string) =>
    req<Row>(`/conditions/${uid}`, { method: "POST", body, token }),
  giveContext: (uid: string, body: Body, token: string) =>
    req<Row>(`/context/${uid}`, { method: "POST", body, token }),
  askCompanion: (uid: string, body: Body, token: string) =>
    req<Row>(`/companion/${uid}`, { method: "POST", body, token }),
  updateMed: (uid: string, medId: string, body: Body, token: string) =>
    req<Row>(`/meds/${uid}/${medId}`, { method: "PUT", body, token }),
  // **No token, and that is the route's whole design.** Its docstring says
  // so: "Public: the person standing over a colleague has no account and
  // needs an answer in ninety seconds." This binding sent one anyway, which
  // made a route written for a stranger callable only by an account holder —
  // and the only screen calling it was Attending, which is the Guardian's
  // side of an alarm, not the side of the person kneeling on the floor.
  //
  // The door that matters for that person is not in this console at all: it
  // is the beacon page the server renders at `GET /c/{id}`, which they reach
  // by pointing a camera at a sticker. This binding stays because a Guardian
  // watching an alarm from a desk wants the same answer; it just stops
  // pretending a credential was ever required.
  alarmGuidance: (alarmId: string, body: Body) =>
    req<Row>(`/alarms/${alarmId}/guidance`, { method: "POST", body }),
  // This one **does** take a credential, and the first version of this
  // binding did not — written from the reasonable-sounding premise that an
  // emergency is the moment a person is least able to produce a token.
  // The server disagrees, for a reason that is better than the premise: an
  // uncredentialed `POST /emergency/{uid}` lets anybody raise an emergency
  // against anybody's account, and the tier it reaches is `emergency_services`.
  //
  // The uncredentialed door for a stranger already exists and is a different
  // one: `POST /c/{bid}/alarm`, off a scanned code, capped at
  // `notify_contact`. A bystander wakes the household; only the account
  // holder's own credential reaches an ambulance. That is the right split
  // and it was already built — the binding was wrong about it, not the app.
  raiseEmergency: (uid: string, body: { situation?: string;
                                        location?: string; sample?: Row },
                   token: string) =>
    req<Row>(`/emergency/${uid}`, { method: "POST", body, token }),
  medicalId: (token: string) => req<Row>(`/medical-id/${token}`),
  makeMedicalIdQr: (uid: string, token: string) =>
    req<MedicalIdCode>(`/medical-id/qr/${uid}`, { method: "POST", token }),
  revokeMedicalIdQr: (uid: string, token: string) =>
    req<Row>(`/medical-id/qr/${uid}`, { method: "DELETE", token }),

  // -- the household relay, sessions, and the wrist -----------------------
  relayChannel: (token: string) => req<RelayChannel>("/relay/channel", { token }),
  relayRoster: (token: string) => req<RelayRoster>("/relay/roster", { token }),
  relayRota: (token: string) => req<RelayRota>("/relay/rota", { token }),
  startSession: (uid: string, body: { device?: string }, token: string) =>
    req<SessionRow>(`/sessions/${uid}`, { method: "POST", body, token }),
  endSession: (uid: string, sessionId: string, token: string) =>
    req<Row>(`/sessions/${uid}/${sessionId}/end`, { method: "POST", token }),
  // The watch posts readings against a drip token rather than an account
  // credential, because a watch cannot hold one.
  watchDrip: (dripToken: string, body: Body) =>
    req<Row>(`/watch/drip/${dripToken}`, { method: "POST", body }),

  // -- telling us about the app -------------------------------------------
  improvements: () => req<ImproveBoard>("/improve"),
  suggestImprovement: (body: Body) =>
    req<Row>("/improve", { method: "POST", body }),
  sendFeedback: (uid: string, body: { rating: "up" | "down"; note?: string },
                 token: string) =>
    req<Row>(`/feedback/${uid}`, { method: "POST", body, token }),

  // The accessibility door. The POST is deliberately tokenless — the person
  // it exists for may be the person the enrollment shut out — and the GET
  // takes the *reviewer* token (JIM_ADMIN_TOKEN), never a user's: reports
  // are read by whoever stands for the deployment.
  sendAccessReport: (body: { doing: string; wall: string; help?: string;
                             lang?: string }) =>
    req<{ id: string; status: string; note: string }>(
      "/access/reports", { method: "POST", body }),
  accessReports: (reviewerToken: string) =>
    req<AccessReports>("/access/reports", { token: reviewerToken }),

  // The Studio. `studioLimits` takes no token on purpose — it says what this
  // installation can offer, and somebody deciding whether the Studio is worth
  // an account should not need one to find out.
  studioLimits: () => req<StudioLimits>("/studio/limits"),
  widgets: (uid: string, token: string) =>
    req<{ widgets: Widget[] }>(`/users/${uid}/widgets`, { token }),
  writeWidget: (uid: string, body: { name: string; source: string },
                token: string) =>
    req<Widget>(`/users/${uid}/widgets`, { method: "POST", body, token }),
  readWidget: (uid: string, widgetId: string, token: string) =>
    req<Widget>(`/users/${uid}/widgets/${widgetId}`, { token }),
  reviseWidget: (uid: string, widgetId: string,
                 body: { name: string; source: string }, token: string) =>
    req<Widget>(`/users/${uid}/widgets/${widgetId}`,
                { method: "PUT", body, token }),
  removeWidget: (uid: string, widgetId: string, token: string) =>
    req<Row>(`/users/${uid}/widgets/${widgetId}`,
             { method: "DELETE", token }),
  runWidget: (uid: string, widgetId: string, inputs: unknown, token: string) =>
    req<WidgetRun>(`/users/${uid}/widgets/${widgetId}/run`,
                   { method: "POST", body: { inputs }, token }),
};

/** What the box can do on this deployment, and the honest reason when it
 *  cannot. `unavailable_because` is a refusal *key*, not a sentence — the
 *  screen renders it from `l10n.ts` in the reader's language, like every
 *  other refusal in this product. */
export type StudioLimits = {
  available: boolean;
  unavailable_because: string | null;
  allowances: Record<string, number>;
};

/** A small program somebody wrote for themselves.
 *
 *  `revision` and not `version`: `/health` already answers a `version` and
 *  that one is a semantic version string, while this is a save count. One
 *  wire name, one type. */
export type Widget = {
  id: string;
  name: string;
  source: string;
  revision: number;
  created_at: number;
  updated_at: number;
};

/** What a run answers. A widget that threw is `status: "error"` on a 200 —
 *  the call worked and the code did not, and the person needs the message
 *  beside their editor rather than a status code standing in for it. */
export type WidgetRun = {
  status: "ok" | "error" | "timeout" | "killed" | "refused";
  ms: number;
  widget_id?: string;
  revision?: number;
  value?: unknown;
  truncated?: boolean;
  message?: string;
  detail?: string;
};

/** Accessibility reports, for the deployment's reviewer. Three answers in
 *  the writer's own words and language — never a name, never a diagnosis:
 *  the table they come from has no submitter column to select. */
export type AccessReports = {
  reports: { id: string; lang: string; doing: string; wall: string;
             help: string | null; status: string; pdi_key: string | null;
             created_at: string }[];
  total: number;
};

export type SelfProfileStatus = {
  linked: boolean;
  profile_id?: string;
  consented: string[];
  categories: Record<string, string>;
  created_at?: string;
};

export type SelfProfilePreview = {
  linked: boolean;
  profile_id?: string;
  consented?: string[];
  brief: Record<string, unknown> | null;
  empty?: boolean;
};
