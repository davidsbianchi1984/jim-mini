// Telling a person apart from the speaker on the table.
//
// Field report from a coach conversation: "when I'm in the chat sphere
// with coach while it's talking, it's listening at the same time, but it
// seems to be picking up its own voice and triggering itself and not
// letting it finish." The microphone is open while she speaks — that is
// what makes interrupting a turn — and on a phone speaker, echo
// cancellation thins her voice without silencing it. What came back
// through was transcribed and submitted as the person's turn, so the
// reply hushed itself mid-sentence and answered a sentence it had just
// said.
//
//     asked     did somebody interrupt
//     mattered  was it a person, or the speaker on the table
//
// The standing ear already knew this rule — it never submits anything
// while the Guardian is speaking. A conversation cannot borrow that
// rule wholesale, because going deaf while she talks is exactly the
// interruption we promised to keep. So the question is not "are we
// speaking" but "are these OUR words".
//
// No imports on purpose: the guard suite transpiles this one file and
// runs the real function, instead of pinning a regex to a rule it
// cannot execute.

function words(s: string): string[] {
  return s.toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, " ")
    .split(/\s+/).filter(Boolean);
}

/** Fewer words than this is never called an echo, however well it
 *  matches: "yes", "no", "stop", "wait", "hang on" are exactly the
 *  interruptions worth having, and a person answering "yes" to a
 *  paragraph containing the word yes must not be mistaken for the room. */
export const SHORTEST_ECHO = 3;

/** How much of what was heard has to be made of what was just said. Not
 *  1.0: a transcriber mishears an occasional word, and the microphone
 *  catches the room around the speaker too. */
export const ECHO_SHARE = 0.7;

/** True when `heard` is the Guardian's own `said` voice coming back.
 *
 *  The cost of a wrong call is small and asymmetric, which is why the
 *  bar sits where it does: a missed echo derails the whole answer (the
 *  defect), while a false echo drops one short turn and re-opens the
 *  microphone — which reads as "she didn't hear me", and saying it again
 *  fixes it. */
export function isEcho(heard: string, said: string): boolean {
  const mine = words(said);
  if (mine.length === 0) return false;
  const got = words(heard);
  if (got.length < SHORTEST_ECHO) return false;
  const bag = new Set(mine);
  const shared = got.filter((w) => bag.has(w)).length;
  return shared / got.length >= ECHO_SHARE;
}
