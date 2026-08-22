// When the page is put away — a tab switched, a phone locked, a window
// minimised — and what a microphone owes the person at that moment.
//
// A backgrounded page is not paused politely. The browser throttles its
// timers, suspends its audio, and ends its speech recogniser; a frozen tab
// stops running altogether. None of that arrives as an error. The console
// simply stops hearing, and every part of the screen that says it is
// listening goes on saying it, because nothing told it otherwise.
//
//     asked     does the console stop listening when it is put away
//     mattered  does it stop *saying* it is listening
//
// The first half happened already, without being asked and without being
// reported. The second half is the defect: silence and deafness look
// identical on screen and are opposite facts — one means nobody spoke, the
// other means nobody could be heard. A field report of exactly this: tabs
// dropping into the background mid-conversation, and the microphone never
// coming back.
//
// So this module exists to make the suspension say its own name. Every ear
// in the console asks it the same two questions — *am I away now* and *tell
// me when that changes* — and the relight loops that used to restart a
// recogniser into a sleeping tab, forever and to no effect, ask before they
// restart.

/** True while the page is put away. False in any environment with no
 *  document at all (tests, a packaged shell mid-boot), because a console
 *  that cannot ask is not entitled to assume the worst about a person's
 *  microphone. */
export function putAway(): boolean {
  if (typeof document === "undefined") return false;
  return document.visibilityState === "hidden";
}

/** Call `left` when the page is put away and `back` when it returns.
 *
 *  Returns the release. Callers hold it for exactly as long as the ear it
 *  guards is standing — an unreleased listener is the same headless loop
 *  the unmount teardowns were written to end, one layer down.
 *
 *  `visibilitychange` is the whole subscription on purpose. Chrome's
 *  `freeze` is the event that names the real suspension, but hidden always
 *  precedes frozen, so the earlier signal covers the later one and there is
 *  no second code path to keep honest. */
export function whenPutAway(left: () => void, back?: () => void): () => void {
  if (typeof document === "undefined") return () => {};
  const turn = () => { if (putAway()) left(); else back?.(); };
  document.addEventListener("visibilitychange", turn);
  return () => document.removeEventListener("visibilitychange", turn);
}
