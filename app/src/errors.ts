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
// Nothing is transmitted. The buffer is local, capped, and readable by the
// person it belongs to; getting a report to a developer is a copy and a paste
// they choose to make.

const KEY = "app.problems";
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
}

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
  write([{ op, status, count: 1, day, fingerprint }, ...rows]);
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
 * Exactly what a copied report contains — the same object the screen shows.
 *
 * One function rather than two so the preview cannot drift from the payload.
 * A screen that showed one thing and copied another would be worse than no
 * preview at all, because it would look like a promise.
 */
export function problemReport(appVersion: string): Record<string, unknown> {
  return {
    app_version: appVersion,
    platform: typeof navigator === "undefined" ? "unknown" : navigator.platform,
    language: typeof navigator === "undefined" ? "unknown" : navigator.language,
    problems: read(),
  };
}
