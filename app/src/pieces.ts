// The reply, cut where the voice can breathe.
//
// Field report, twice in one week: "still a long delay while waiting for
// a response." The delay had two legs — the model writing the whole
// answer, and then the voice service synthesising the whole answer —
// and the second leg was being paid in full before a single word was
// heard. Cutting the reply at sentence ends lets the first piece be
// synthesised alone, which is small and therefore fast, while the rest
// is fetched behind the piece already playing.
//
//     asked     when does the answer start being heard
//     mattered  does the wait grow with the length of the answer
//
// No imports on purpose: the guard suite transpiles this one file and
// runs the real function through node, instead of pinning a regex to an
// implementation it cannot execute.

// Short titles whose trailing period ends a word, not a sentence. "Dr.
// Smith said" must not put "Dr." on the wire as a whole utterance.
const ABBREV = /\b(?:mr|mrs|ms|dr|st|no|vs|etc|e\.g|i\.e)\.$/i;

/** Every piece is spoken by one request to the voice service. The first
 *  sentence rides alone — it is the one somebody is waiting on — and the
 *  rest are grouped so a long answer is a few requests, not thirty. */
export const PIECE_CHARS = 240;

export function spokenPieces(text: string): string[] {
  const t = text.trim();
  if (!t) return [];
  const sentences: string[] = [];
  let start = 0;
  // A sentence ends at closing punctuation (plus any quote or bracket
  // riding it) followed by whitespace — but only when what follows could
  // begin a sentence, so "2.5 seconds" and "e.g. lowercase" stay whole.
  const boundary = /[.!?…]+["')\]]*\s+/g;
  let m: RegExpExecArray | null;
  while ((m = boundary.exec(t)) !== null) {
    const end = m.index + m[0].length;
    const head = t.slice(start, end).trimEnd();
    if (ABBREV.test(head)) continue;
    if (!/["'(]?[A-Z0-9]/.test(t.slice(end, end + 2))) continue;
    sentences.push(head);
    start = end;
  }
  if (start < t.length) sentences.push(t.slice(start).trimEnd());
  if (sentences.length === 0) return [t];
  const pieces = [sentences[0]];
  let group = "";
  for (const s of sentences.slice(1)) {
    group = group ? group + " " + s : s;
    if (group.length >= PIECE_CHARS) { pieces.push(group); group = ""; }
  }
  if (group) pieces.push(group);
  return pieces;
}
