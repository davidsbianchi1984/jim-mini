// What went wrong, recorded without recording anything private.
//
// Every failed request passes through `req()`, so one call there catches the
// lot. The hard part is not the catching — it is deciding what a failure may
// say about itself, because the obvious answer is wrong.
//
// The backends put user input straight into their error messages:
//
//     no device called 'Pixel Buds' on this account
//     unknown site 'knee'; one of scalp, face, eye, mouth…
//     unknown language 'xx'
//
// Those are good messages — they tell the person exactly what to fix. They are
// also device names, body sites and, in JIM, potentially health content. A
// report that carried them would quietly undo the promise every other screen in
// these products makes. So the message is shown to the user, who owns it, and
// is never written to this log.
//
// The same reasoning rules out the path. `/profiles/prf_0de08e794ed0/chat`
// identifies a person; `POST /profiles/{id}/chat` identifies a *bug*. Only the
// second is recorded, and the redaction happens here rather than at the send
// step, so a private value never enters storage in the first place — there is
// no moment at which the buffer holds something that would have to be scrubbed.
//
// ── Sending ───────────────────────────────────────────────────────────────
//
// The buffer is sent once at launch, to a gateway whose address is compiled
// into the build (`__PROBLEM_COLLECTOR__`). A build with no address has
// nowhere to send and no code path that could acquire one at runtime beyond a
// key the user sets themselves — which is a stronger "off by default" than a
// flag, because it cannot be flipped by a mistake in a later release.
//
// Counts are sent as *deltas*, not totals. Each row remembers how much of it
// has already been reported, so relaunching an app twenty times does not turn
// one broken screen into twenty. Nothing is deleted after a send: the row is
// the user's own history and stays until they clear it.
//
// The send is fire-and-forget and swallows every failure. A diagnostic that
// can delay a launch, or produce an error of its own, has stopped being worth
// having.

const KEY = "app.problems";
const COLLECTOR_KEY = "app.problems.collector";
const SEND_KEY = "app.problems.send";
const LIMIT = 50;

/** One failure, with nothing in it that belongs to anybody. */
export interface Problem {
  /** `POST /profiles/{id}/chat` — the operation, not the instance. */
  op: string;
  /** HTTP status, or 0 when the request never reached a server. */
  status: number;
  /** How many times this exact operation+status has happened. */
  count: number;
  /** ISO date only. A timestamp to the second is a movement record. */
  day: string;
  /** Stable across occurrences, so duplicates group without a message. */
  fingerprint: string;
  /**
   * How much of `count` has already been reported.
   *
   * A number, never a flag: a row goes on accumulating after it is sent, and
   * the next report owes the difference. Absent on rows written by an older
   * build, which read as zero and are reported once in full.
   */
  sent?: number;
}

// Which product this console is, and where its reports go. Injected at build
// time (vite.config.ts) — the source because a file that is byte-identical in
// three repos cannot know which one it is in, and the collector because the
// address is a decision made when the installer is built, not one a user
// should have to hold an opinion about.
declare const __APP_SOURCE__: string;
declare const __PROBLEM_COLLECTOR__: string;
declare const __PROBLEM_TOKEN__: string;
// Not a product name. A repo whose vite.config.ts forgot the define would
// otherwise file its reports under whichever product this fallback named, and
// nothing would ever look wrong — the aggregate would just quietly attribute
// one app's bugs to another. "unknown" is a source the gateway refuses, so the
// mistake surfaces as a 422 on the first report instead.
const SOURCE: string =
  typeof __APP_SOURCE__ !== "undefined" ? __APP_SOURCE__ : "unknown";
const BUILT_COLLECTOR: string =
  typeof __PROBLEM_COLLECTOR__ !== "undefined" ? __PROBLEM_COLLECTOR__ : "";
const BUILT_TOKEN: string =
  typeof __PROBLEM_TOKEN__ !== "undefined" ? __PROBLEM_TOKEN__ : "";

// A segment that identifies a *thing* rather than naming a route. The id
// formats these products mint (`prf_0de08e794ed0`, `usr_…`, `dev_…`) are the
// common case; the rest catch UUIDs, numeric ids, and anything long enough to
// be a token or an encoded value.
const ID_LIKE = [
  // `prf_0de08e794ed0`, but also `cap_9f2` and `usr_1`. The suffix length is
  // deliberately unbounded: an id minted short is still an id, and requiring
  // six hex characters let three of the first eight real paths through.
  // Nothing in these route tables uses `word_word` as a literal segment —
  // they spell those with hyphens (`skill-grants`, `live-person`) — which is
  // what makes the pattern safe to widen.
  /^[a-z]{2,8}_[0-9a-z]+$/i,
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i,
  /^\d+$/,
  /^[A-Za-z0-9_-]{24,}$/,
];

/**
 * A path with every identifying segment replaced by `{id}`.
 *
 * Deliberately aggressive: a segment that *might* identify something is
 * replaced. Over-redacting costs a little precision in the report; under-
 * redacting costs somebody their privacy, and only one of those is recoverable.
 */
export function redactPath(path: string): string {
  const noQuery = path.split("?")[0];
  return noQuery
    .split("/")
    .map((seg) => (seg && ID_LIKE.some((re) => re.test(seg)) ? "{id}" : seg))
    .join("/");
}

/** Non-reversible by construction — its input already carries nothing private. */
function fingerprintOf(op: string, status: number): string {
  let h = 2166136261;
  for (const ch of `${op}|${status}`) {
    h ^= ch.charCodeAt(0);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0).toString(16).padStart(8, "0");
}

function read(): Problem[] {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || "[]");
    return Array.isArray(raw) ? (raw as Problem[]) : [];
  } catch {
    return [];
  }
}

function write(rows: Problem[]): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(rows.slice(0, LIMIT)));
  } catch {
    // A full or disabled localStorage is not worth an error of its own. The
    // diagnostic is the least important thing in the app; it must never be the
    // reason something else fails.
  }
}

/**
 * Record a failure. Takes the method and raw path, never the message.
 *
 * The signature is the safeguard: there is no parameter for the detail string,
 * so a future caller cannot pass one by accident.
 */
export function recordProblem(method: string, path: string,
                              status: number): void {
  const op = `${method.toUpperCase()} ${redactPath(path)}`;
  const fingerprint = fingerprintOf(op, status);
  const day = new Date().toISOString().slice(0, 10);
  const rows = read();
  const hit = rows.find((r) => r.fingerprint === fingerprint);
  if (hit) {
    hit.count += 1;
    hit.day = day;
    write([hit, ...rows.filter((r) => r !== hit)]);
    return;
  }
  write([{ op, status, count: 1, day, fingerprint, sent: 0 }, ...rows]);
}

export function problems(): Problem[] {
  return read();
}

export function clearProblems(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* nothing to do, and nothing worth saying */
  }
}

/**
 * Where reports go, or "" for nowhere.
 *
 * The stored key wins over the built-in address so a self-hoster can point
 * their own install at their own gateway — and so anyone can point it at
 * nothing by setting it empty, without waiting for a release.
 */
export function collectorUrl(): string {
  try {
    const stored = localStorage.getItem(COLLECTOR_KEY);
    if (stored !== null) return stored.trim().replace(/\/+$/, "");
  } catch {
    /* fall through to the built-in */
  }
  return BUILT_COLLECTOR.trim().replace(/\/+$/, "");
}

export function setCollectorUrl(url: string | null): void {
  try {
    if (url === null) localStorage.removeItem(COLLECTOR_KEY);
    else localStorage.setItem(COLLECTOR_KEY, url.trim());
  } catch {
    /* the switch below still works; this one just will not persist */
  }
}

/** Sending is on where a collector exists, and off the moment anyone says so. */
export function sendingEnabled(): boolean {
  try {
    return localStorage.getItem(SEND_KEY) !== "off";
  } catch {
    return true;
  }
}

export function setSending(on: boolean): void {
  try {
    if (on) localStorage.removeItem(SEND_KEY);
    else localStorage.setItem(SEND_KEY, "off");
  } catch {
    /* nothing to do */
  }
}

/**
 * Exactly what a report contains — shown on screen, copied by the button, and
 * posted by the sender, all from here.
 *
 * One function rather than three so the preview cannot drift from the payload.
 * A screen that showed one thing and sent another would be worse than no
 * preview at all, because it would look like a promise.
 *
 * `count` is the unreported remainder, and rows with nothing left to report
 * are absent. So this is not a view of the log — it is the message, and after
 * a successful send it is legitimately empty.
 */
export function problemReport(appVersion: string): Record<string, unknown> {
  const unsent = read()
    .map((r) => ({
      op: r.op,
      status: r.status,
      count: r.count - (r.sent || 0),
      day: r.day,
      fingerprint: r.fingerprint,
    }))
    .filter((r) => r.count > 0);
  return {
    source: SOURCE,
    app_version: appVersion,
    platform: typeof navigator === "undefined" ? "unknown" : navigator.platform,
    language: typeof navigator === "undefined" ? "unknown" : navigator.language,
    problems: unsent,
  };
}

/** Move the watermark up by what a report just carried. */
function markReported(report: Record<string, unknown>): void {
  const carried = new Map<string, number>();
  for (const p of (report.problems as Problem[]) || []) {
    carried.set(p.fingerprint, p.count);
  }
  write(read().map((r) => {
    const n = carried.get(r.fingerprint);
    // `(r.sent || 0) + n` rather than `r.count`: the row may have grown while
    // the request was in flight, and that growth has not been reported.
    return n === undefined ? r : { ...r, sent: (r.sent || 0) + n };
  }));
}

export type SendOutcome =
  | "sent" | "nothing-to-send" | "turned-off" | "no-collector" | "failed";

/**
 * Post the unreported failures. Never throws, never blocks anything.
 *
 * The gateway answers 422 when a report does not have exactly the shape it
 * expects — which would mean this build's redaction has stopped working. That
 * is a refusal, not a retry: the watermark stays put, nothing is marked sent,
 * and the next launch tries again with whatever the fix ships.
 *
 * Raw `fetch`, not `req()`, and that is not laziness. `req()` calls
 * `recordProblem` when it fails, so routing the send through it would make a
 * failing collector write a new row every launch — a log that fills up with
 * the story of its own delivery and nothing else.
 */
export async function sendProblems(appVersion: string): Promise<SendOutcome> {
  const base = collectorUrl();
  if (!base) return "no-collector";
  if (!sendingEnabled()) return "turned-off";
  const report = problemReport(appVersion);
  if (!(report.problems as unknown[]).length) return "nothing-to-send";
  try {
    const headers: Record<string, string> = {
      "content-type": "application/json",
    };
    if (BUILT_TOKEN) headers.authorization = `Bearer ${BUILT_TOKEN}`;
    const res = await fetch(`${base}/v1/problems`, {
      method: "POST", headers, body: JSON.stringify(report),
    });
    if (!res.ok) return "failed";
  } catch {
    return "failed";
  }
  markReported(report);
  return "sent";
}
