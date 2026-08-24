// A conversation that keeps going while you move about the console.
//
// `{tab === "coach" && <Coach/>}` — the screen unmounts on every tab change,
// and the voice with it. There is an unmount teardown on all five voice
// screens for exactly that reason: navigating away mid-reply used to leave a
// headless loop, the guardian talking on under a screen that no longer
// exists. That teardown is right for navigating away and wrong for walking
// away on purpose, which is the same event to React and the opposite event
// to the person: one means they left the conversation, the other means they
// took it with them.
//
//     asked     did the screen unmount
//     mattered  did the person mean to end the conversation
//
// So the conversation moves above the tab switch when — and only when — it
// is asked to. Nothing here starts on its own, and the five teardowns stay
// exactly as they were: an ear that survives a screen has to be one somebody
// pressed a button to keep.
//
// ## What this does not do
//
// It does not survive the page being put away. `away.ts` says why in its own
// words: a backgrounded page has its timers throttled, its audio suspended
// and its recogniser ended by the browser, and no amount of state above a
// tab switch changes that. Walking is inside this application. Minimising
// the browser and keeping the microphone is a native shell's job, and
// belongs where a foreground service and its notification can be honest
// about it.

export type Walking = {
  /** What it is called on screen — the strip names the conversation the way
   *  the screen it came from named it. */
  shownName: string;
  /** The voice the reply is read in, so walking sounds like the screen. */
  lang: string;
  /** How this conversation takes a turn.
   *
   * A callback rather than the ids to build one from, because the surfaces
   * that can be carried do not share a wire: the front door asks the coach
   * with `area: "general"` and the coach screen asks it with whichever area
   * the person picked, and across the estate QRME's two answer through a
   * profile chat and an authoring turn. Holding the ids here would mean the
   * strip knowing every one of them, and a new surface meaning a new branch
   * inside it.
   *
   *     asked     can the strip carry this conversation
   *     mattered  does the strip have to know what kind it is
   *
   * The screen that started the walk already knows how to take its own
   * turn. It hands that over and the strip stays ignorant, which is what
   * lets it be one component instead of one per screen.
   */
  take: (message: string) => Promise<string>;
};

let current: Walking | null = null;
const listeners = new Set<(w: Walking | null) => void>();

export function walking(): Walking | null {
  return current;
}

/** Take the conversation with you. Called from a button, never from an
 *  effect: an ear that outlives its screen without a press is the headless
 *  microphone the five unmount teardowns exist to prevent. */
export function startWalking(w: Walking): void {
  current = w;
  listeners.forEach((f) => f(current));
}

export function stopWalking(): void {
  current = null;
  listeners.forEach((f) => f(current));
}

/** Subscribe. Returns the release — held for as long as the subscriber is
 *  mounted, for the same reason `whenPutAway` returns one. */
export function onWalk(f: (w: Walking | null) => void): () => void {
  listeners.add(f);
  return () => { listeners.delete(f); };
}
