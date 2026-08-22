// The standing ear — while a sound monitor is plugged in and this console
// is open, the device's own recogniser keeps listening, and everything it
// hears goes through the monitor door the roster already gates.
//
// What it deliberately is not: a keyword spotter. The cue vocabulary —
// the calls for help, the speech that comes out wrong, the hurt and the
// lost — lives in jim/cues.py and is matched server-side when the sensed text
// arrives. A copy of that list here would drift from the one that
// decides, and a client that only sends the words it recognises has
// quietly become the judge of what counts as a call for help. (A guard
// holds this line: no phrase from that vocabulary may appear in this
// file, comments included.)
//
//     asked     does the console hear the words the cues know
//     mattered  who decides what a call for help sounds like
//
// Consent is the door's job too: the text is submitted through
// `POST /monitors/{uid}/{name}/sensed`, so a monitor that is off, or one
// that catches other people before they have been told, is refused by
// the server however long this ear has been standing. This module brings
// sound to the door; nothing about what survives is decided on this side.
import { api } from "./api";
import { deviceRecogniser, speakingNow, type DeviceRecognition }
  from "./speech";
import { putAway, whenPutAway } from "./away";

/** What the pill can honestly say. `norecogniser` is a platform with no
 *  recogniser to stand (some packaged webviews); `refused` is the person
 *  or the platform saying no to the microphone — tapping the pill again
 *  will not change either, and the label says which it is.
 *
 *  `asleep` is the state this list was missing. A backgrounded tab has its
 *  recogniser ended by the browser, and the restart below stood a new one
 *  every 400ms into a page that could not hear — all night, if the tab was
 *  left that way, with the pill reading "listening for the words that call
 *  for help" the whole time. An ear for a person who might be calling for
 *  help is the last place a lit light may mean nothing. */
export type EarState =
  "off" | "listening" | "norecogniser" | "refused" | "asleep";

export interface Ear { stop: () => void }

/** True where the platform ships a recogniser at all — the pill uses this
 *  to say "this browser cannot listen" instead of pretending a toggle. */
export function earAvailable(): boolean {
  return deviceRecogniser() !== null;
}

/** Stand the ear: listen continuously and hand everything heard to the
 *  named monitor's door. Recognisers end themselves on their own schedule
 *  (silence timeouts, service hiccups), so a standing ear is a restarting
 *  one — `onend` re-arms unless `stop()` was the reason it ended. */
export function standEar(
  uid: string, token: string, monitor: string,
  onState: (state: EarState) => void,
): Ear {
  const SR = deviceRecogniser();
  if (SR === null) {
    onState("norecogniser");
    return { stop: () => {} };
  }
  let stopped = false;
  // Put away, not switched off. The person's decision has not changed, so
  // the ear stands itself back up the moment the page comes back — but
  // while it is down it says so, and nothing restarts into a sleeping tab.
  let dozing = false;
  let rec: DeviceRecognition | null = null;
  const start = () => {
    if (stopped) return;
    if (putAway()) { doze(); return; }
    const r = new SR();
    rec = r;
    r.lang = navigator.language || "en";
    r.interimResults = false;
    r.continuous = true;
    // Continuous mode accumulates results; only what arrived since the
    // last event is new, and only the new part is sensed.
    let seen = 0;
    r.onresult = (e) => {
      const parts: string[] = [];
      for (let i = seen; i < e.results.length; i++) {
        parts.push(e.results[i][0].transcript);
      }
      seen = e.results.length;
      const text = parts.join(" ").trim();
      // The Guardian's own replies come out of the same speaker this
      // microphone faces. A voice must not testify about itself — a
      // coach's advice about when to ring for an ambulance is advice,
      // and sensed back through the door it would read as a cue.
      if (!text || speakingNow()) return;
      api.monitorSensed(uid, monitor, token, text).catch(() => {
        // The door said no (unplugged mid-listen, consent withdrawn) or
        // the network blinked. Either way the ear keeps standing: the
        // next sound tries the door again, and the door keeps deciding.
      });
    };
    r.onerror = (e) => {
      // Only a refusal ends the ear: the person said no to the microphone,
      // or the platform withholds the service. Everything else —
      // `no-speech`, a network blip — ends this recogniser and the
      // restart in `onend` stands the next one.
      if (e.error === "not-allowed" || e.error === "service-not-allowed") {
        stopped = true;
        onState("refused");
      }
    };
    r.onend = () => {
      if (stopped || dozing) return;
      window.setTimeout(start, 400);
    };
    try {
      r.start();
      onState("listening");
    } catch {
      // An engine that refuses start() (already running, mid-teardown)
      // fires onend, and onend re-arms.
    }
  };
  const doze = () => {
    if (stopped || dozing) return;
    dozing = true;
    onState("asleep");
    try { rec?.stop(); } catch { /* already stopped is stopped */ }
  };
  const wake = () => {
    if (stopped || !dozing) return;
    dozing = false;
    start();
  };
  const release = whenPutAway(doze, wake);
  start();
  return {
    stop: () => {
      stopped = true;
      release();
      onState("off");
      try { rec?.stop(); } catch { /* already stopped is stopped */ }
    },
  };
}
