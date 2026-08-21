// Saying it aloud, and hearing it back.
//
// Two layers, and the fallback is the point: a deployment with an
// ElevenLabs or OpenAI key gets those voices; one without still speaks and
// still listens, using what the operating system already ships. An app that
// goes mute because an API key is missing has chosen the wrong failure.
import { api, getBase } from "./api";

let current: HTMLAudioElement | null = null;

/** Stop whatever is being said right now. */
export function hush() {
  if (current) { current.pause(); current = null; }
  if (typeof speechSynthesis !== "undefined") speechSynthesis.cancel();
}

/** True while this module is saying something aloud. The standing ear
 *  reads this so that nothing the Guardian says is ever submitted as
 *  something a monitor heard — a voice must not testify about itself. */
export function speakingNow(): boolean {
  return current !== null
    || (typeof speechSynthesis !== "undefined" && speechSynthesis.speaking);
}

/** Say `text` aloud — the configured voice when there is one, the device's
 *  own otherwise. Resolves when the speaking ENDS (hush() counts as an
 *  end), not when it starts: the purple orb is bound to this promise, and
 *  a field report caught it vanishing the moment the reply began — the
 *  orb was supposed to stay for the whole answer, and "when did the
 *  speaking finish" is a fact only this module can see. */
export async function say(text: string): Promise<"service" | "device"> {
  hush();
  try {
    const res = await fetch(getBase() + "/voice/speak", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (res.ok) {
      const blob = await res.blob();
      const audio = new Audio(URL.createObjectURL(blob));
      current = audio;
      // The reply goes to the earbud somebody already connected, where the
      // platform lets a page choose. Where it does not (iOS), the
      // microphone request below is the lever that moves the session.
      const sink = await connectedEar("audiooutput");
      if (sink && "setSinkId" in audio) {
        await (audio as HTMLAudioElement & {
          setSinkId(id: string): Promise<void>;
        }).setSinkId(sink).catch(() => { /* the default route stands */ });
      }
      await audio.play();
      await new Promise<void>((resolve) => {
        // `pause` fires for hush(); `ended` for a played-out reply;
        // `error` for a decode that dies mid-utterance. Any of them is
        // the speaking being over.
        audio.addEventListener("ended", () => resolve(), { once: true });
        audio.addEventListener("pause", () => resolve(), { once: true });
        audio.addEventListener("error", () => resolve(), { once: true });
      });
      // A reply that played out is no longer "speaking now" — without this,
      // `speakingNow()` reads true until the next say() or hush(), and the
      // standing ear would stay deaf between replies.
      if (current === audio) current = null;
      return "service";
    }
  } catch { /* fall through to the device's own voice */ }
  if (typeof speechSynthesis !== "undefined") {
    const utter = new SpeechSynthesisUtterance(text);
    // Prefer a male voice when the platform has one, since that is what this
    // product is usually asked for; the user's own choice still wins if the
    // OS has one set.
    const preferred = speechSynthesis.getVoices().find((v) =>
      /david|daniel|alex|fred|george|male/i.test(v.name));
    if (preferred) utter.voice = preferred;
    await new Promise<void>((resolve) => {
      utter.onend = () => resolve();
      utter.onerror = () => resolve();
      speechSynthesis.speak(utter);
      // `hush()` cancels the queue, and a cancelled utterance fires
      // onend/onerror per spec — but not on every engine. The watcher is
      // the belt for those braces: once nothing is speaking, it is over.
      const watch = window.setInterval(() => {
        if (!speechSynthesis.speaking) {
          window.clearInterval(watch);
          resolve();
        }
      }, 250);
    });
  }
  return "device";
}

export interface Listener { stop: () => void }

// -- following the device that is already connected ------------------------
//
// Field report: an earbud connected to the phone, and the conversation came
// out of the phone's own speaker while the built-in microphone listened —
// the person had to disconnect the earbud to hear their guardian. A page
// cannot re-route the operating system, but it can *ask by name*: request
// the connected headset's microphone in getUserMedia (on iOS that request
// is also what flips the whole audio session to the headset), and on the
// platforms that expose setSinkId, point the reply at the headset speaker.
// Device labels are readable only after a microphone permission has been
// granted once, so the first-ever listen uses the defaults and every one
// after it follows the earbud.
const EXTERNAL_EAR =
  /airpod|earbud|\bbuds?\b|headset|headphone|bluetooth|hands-?free|wireless|jabra|\bwf-|\bwh-/i;

async function connectedEar(
  kind: "audioinput" | "audiooutput",
): Promise<string | null> {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const ext = devices.find(
      (d) => d.kind === kind && EXTERNAL_EAR.test(d.label));
    return ext ? ext.deviceId : null;
  } catch {
    // No enumeration (old webview, permission withheld): the defaults are
    // what the person had before this existed, not a failure.
    return null;
  }
}

/** How long a standing conversation keeps re-opening the microphone with
 *  nothing heard before it bows out on its own. The reviewer's number:
 *  "at least two minutes would be enough" — long enough to think, or to
 *  step away and come back, short enough that a conversation nobody is in
 *  does not hold the microphone open all afternoon. Shared by Coach and
 *  Talk so the two rooms cannot drift apart. */
export const CONVERSATION_IDLE_MS = 120_000;

/** True when a listen ended only because nothing was said — quiet, not a
 *  refusal. A standing conversation reads this and opens the microphone
 *  again; every other message is a real failure and ends it. */
export function heardNothing(message: string): boolean {
  return message === "nothing was heard in that"
    || message === "nothing was recorded";
}

/** The minimal face of the platform's own recogniser. Typed here because
 *  the DOM lib does not ship one, and `any` would hide the contract.
 *  Exported for the standing ear (ear.ts), which listens continuously
 *  through the same recogniser this module borrows one phrase at a time. */
export interface DeviceRecognition {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  onresult:
    ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void)
    | null;
  onerror: ((e: { error?: string }) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
}

export function deviceRecogniser(): (new () => DeviceRecognition) | null {
  const w = window as unknown as Record<string, unknown>;
  const SR = w.SpeechRecognition ?? w.webkitSpeechRecognition;
  return typeof SR === "function"
    ? (SR as new () => DeviceRecognition) : null;
}

/** Listen with the device's own recogniser — live, free, and no account.
 *  Returns null where the platform ships none (some packaged webviews),
 *  which is what the record-and-send path below exists for. */
function deviceListener(
  onText: (text: string) => void,
  onError: (message: string) => void,
): Listener | null {
  const SR = deviceRecogniser();
  if (SR === null) return null;
  const rec = new SR();
  rec.lang = navigator.language || "en";
  rec.interimResults = false;
  rec.continuous = false;
  let heard = "";
  let failed = false;
  rec.onresult = (e) => {
    heard = Array.from({ length: e.results.length },
      (_, i) => e.results[i][0].transcript).join(" ").trim();
  };
  rec.onerror = (e) => {
    failed = true;
    // `not-allowed` is the person refusing the microphone: the browser asked
    // and was told no. `service-not-allowed` is the *platform* refusing —
    // nobody was asked, and no prompt will appear however many times the mic
    // is tapped. Printing the raw code named the failure and left its owner
    // with nothing to do about it, which is the same defect as a verdict
    // reading "bad key" for an account with an unpaid invoice.
    onError(e.error === "not-allowed"
      ? "no microphone available — check the app's microphone permission"
      : e.error === "service-not-allowed"
      ? platformRefusal()
      : `the device's recogniser could not hear that (${e.error || "unknown"})`);
  };
  rec.onend = () => {
    if (failed) return;
    if (heard) onText(heard);
    else onError("nothing was heard in that");
  };
  rec.start();
  return { stop: () => rec.stop() };
}

/** What to say when the platform refuses the recogniser outright.
 *
 * The previous wording named one cause and named it as fact: *on iPhone and
 * iPad that is Dictation being switched off*. Reported from the field with a
 * screenshot of Settings showing Dictation **on**. So the sentence sent
 * somebody to a switch that was already thrown, and when it changed nothing
 * the honest conclusion available to them was that the app is broken.
 *
 *     asked     does the refusal name a remedy
 *     mattered  is the remedy the reason
 *
 * That is a worse failure than the raw error code it replaced. A code is
 * unhelpful and admits it; a confident wrong diagnosis spends the person's
 * trust and their time, and it was written by somebody — me — who had no way
 * to tell which of several causes had fired.
 *
 * `service-not-allowed` is WebKit's answer for *the speech service will not
 * serve this page*, and Dictation is only one of the ways to get there.
 * Screen Time can withhold Siri & Dictation entirely; an embedded web view
 * inside another app does not get the recogniser at all however the phone is
 * configured; and the service is a network service, so it can simply be
 * unreachable.
 *
 * Nothing here can read any of that: none of it is exposed to a page. So the
 * sentence now states only what is certain — the platform refused, and
 * tapping again will not help — and lists where to look without claiming to
 * know which one it is. The one thing it *can* detect is the web view, and
 * it says so when it sees it, because that is the case no setting can fix.
 */
export function platformRefusal(): string {
  // The cause the person can actually act on, said first.
  //
  // A second field report, same session: Dictation on, Screen Time
  // restrictions off entirely, still refused. The reporter had already told
  // me the thing that mattered and I had not connected it — *no key is
  // configured for this app*. `listen()` reads that as `knownHasService ===
  // false` and goes straight to the device recogniser, which on iOS answers
  // `service-not-allowed`. So the sentence lectured about iOS settings while
  // the fixable cause sat one branch away.
  //
  //     asked     why did the recogniser refuse
  //     mattered  which of the reasons can this person do something about
  //
  // The honest sentence for that state names the key first and the platform
  // second, because one of the two has a door and the other does not.
  //
  // `no transcription service is set up — add a key` already existed in this
  // file, and was reachable only when `deviceRecogniser()` returned null.
  // On iOS Safari the constructor exists and always fails, so the branch
  // that would have said the useful thing was the branch iOS never takes.
  // The constructor being present is not the service being available —
  // a binding is not a door, in a file that had already learned that once.
  if (knownHasService === false) {
    return "no transcription service is set up for this app — add an OpenAI "
      + "or ElevenLabs key in Settings, and the microphone will work. The "
      + "device's own recogniser was tried instead and this platform "
      + "refused it, which no setting on the phone will change. You can "
      + "type in the meantime — nothing else is blocked.";
  }
  const embedded = typeof navigator !== "undefined"
    // `navigator.standalone` is defined in iOS Safari — `false` in a tab,
    // `true` for a home-screen app — and absent inside another app's web
    // view. It is non-standard and a few in-app browsers do expose it, so
    // this is a hint rather than a proof; it only ever *adds* a sentence
    // that names a real dead end, and never withholds the settings.
    && /iPhone|iPad|iPod/.test(navigator.userAgent)
    && (navigator as unknown as { standalone?: boolean }).standalone
       === undefined;
  return embedded
    ? "this page is running inside another app's browser, which does not get "
      + "the device's recogniser at all. Open jim-mini.com in Safari itself "
      + "and the microphone will work — no setting will fix it here."
    : "the platform refused the recogniser, so tapping again will not help. "
      + "Three things withhold it and this page cannot see which: Dictation "
      + "off (Settings › General › Keyboard › Enable Dictation); Siri & "
      + "Dictation restricted (Settings › Screen Time › Content & Privacy "
      + "Restrictions › Allowed Apps & Features, or Intelligence & Siri on "
      + "newer iOS — not the Speech Recognition row under Privacy, which is "
      + "a different permission and can read Allow while dictation is still "
      + "withheld); or the speech service being unreachable just now. You "
      + "can type instead — nothing else is blocked.";
}

// Set when the configured service refuses, so the next tap goes straight to
// the recogniser that works instead of failing the same way twice. Never
// set by a transport blip on the settings read — only by the service
// itself saying no.
let preferDevice = false;

// What the settings read said last time. `null` is "never asked" — not
// "no service", which is why this is a tri-state and not a boolean. It
// exists so that a tap does not have to spend a network round trip finding
// out something the screen could have learned while it was being read.
let knownHasService: boolean | null = null;

/** Read the voice settings and remember the answer.
 *
 *  Screens with a microphone call this on mount, so the first tap already
 *  knows which path to take and never has to await inside the gesture. It
 *  never throws and never blocks anything: an unreachable settings read
 *  leaves the previous answer standing. */
export async function primeVoice(): Promise<void> {
  try {
    const s = await api.getVoiceSettings();
    knownHasService = s.provider !== "device" && s.key_set;
  } catch { /* an unreachable settings read never changes what we knew */ }
}

/** Listen to the microphone and hand back what was said.
 *
 *  Which path listens is decided by what is configured, not by hope: a
 *  deployment with a transcription key records and sends, because that
 *  works the same in a packaged desktop app as in a browser; one without
 *  uses the recogniser the device already ships — the fallback this
 *  module's header always promised and, until a field report caught it,
 *  this function never actually had.
 *
 *  Ordering here is load-bearing. Safari permits
 *  `SpeechRecognition.start()` only inside the user gesture that asked for
 *  it, and an async function holds that gesture exactly until its first
 *  suspension point. The settings read used to come first, which spent the
 *  gesture on a fetch and left the recogniser to be refused with
 *  `service-not-allowed` — so the fallback ran on every platform except
 *  the one most people were holding. Worse, `preferDevice` was consulted
 *  *after* that await, which is the flag whose entire job is to make the
 *  second tap avoid the first tap's failure.
 *
 *      asked     is there a device recogniser to fall back to
 *      mattered  is it started while the browser still permits it
 *
 *  So everything decidable without the network is decided before the first
 *  `await`, and the network answer is cached rather than re-fetched.
 */
export async function listen(
  onText: (text: string) => void,
  onError: (message: string) => void,
  // The voice's own level, 0..1, a few times a second — the orb's wave.
  // Only the record path has an analyser to read it from; the device
  // recogniser keeps a still orb, which is honest about what it exposes.
  onLevel?: (level: number) => void,
): Promise<Listener> {
  if (preferDevice || knownHasService === false) {
    const dev = deviceListener(onText, onError);
    if (dev) return dev;
  }

  if (knownHasService === null) {
    await primeVoice();
    if (!knownHasService || preferDevice) {
      const dev = deviceListener(onText, onError);
      if (dev) return dev;
      // No recogniser either: record anyway, so the server's own honest
      // refusal is what the person reads rather than a guess made here.
    }
  }

  let stream: MediaStream;
  try {
    // Echo cancellation asked for by name, not assumed: the microphone is
    // open while the reply plays now (interrupting is a turn), and without
    // AEC the speaker's own voice would barge itself in. The connected
    // earbud's microphone is asked for by name too — `ideal`, not `exact`,
    // so an earbud that vanished mid-session degrades to the built-in mic
    // instead of refusing to listen at all.
    const mic = await connectedEar("audioinput");
    stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true,
               ...(mic ? { deviceId: { ideal: mic } } : {}) } });
  } catch {
    onError("no microphone available — check the app's microphone permission");
    return { stop: () => {} };
  }
  const chunks: BlobPart[] = [];
  const rec = new MediaRecorder(stream);
  rec.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
  // Stop by silence, not only by tap. A field report from a coach
  // conversation: the green orb waits for a press however long the
  // question has been over. Quiet ends the listening on its own — long
  // enough for a thinking pause mid-question, short enough that the
  // answer starts when the asking stops. The tap still works, and a
  // platform with no AudioContext simply keeps the old manual behavior.
  //
  // Five seconds first, and the same reviewer sent it back: "still a
  // long delay while waiting for a response — drop it to 2.5". Half the
  // window, and the wait between finishing a sentence and hearing the
  // reply begins is half of what it was.
  const SILENCE_STOP_MS = 2500;
  let watcher = 0;
  let audioCtx: AudioContext | null = null;
  // Whether a voice-level sound was ever heard. Speech models hallucinate
  // words out of silence — a field report watched the specialist answer
  // "thank you" after "thank you" to an empty room, each invented turn
  // resetting the idle clock that should have closed the conversation. A
  // recording the analyser never saw cross the voice threshold reports
  // "nothing was heard" without ever reaching transcription.
  let voiced = false;
  let hadAnalyser = false;
  const stopWatching = () => {
    if (watcher) { window.clearInterval(watcher); watcher = 0; }
    if (audioCtx) { void audioCtx.close().catch(() => {}); audioCtx = null; }
    onLevel?.(0);
  };
  try {
    const AC = (window as unknown as {
      AudioContext?: typeof AudioContext;
      webkitAudioContext?: typeof AudioContext;
    });
    const Ctx = AC.AudioContext ?? AC.webkitAudioContext;
    if (Ctx) {
      audioCtx = new Ctx();
      hadAnalyser = true;
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 1024;
      audioCtx.createMediaStreamSource(stream).connect(analyser);
      const wave = new Uint8Array(analyser.fftSize);
      let lastVoice = Date.now();
      watcher = window.setInterval(() => {
        analyser.getByteTimeDomainData(wave);
        let peak = 0;
        for (let i = 0; i < wave.length; i++) {
          const dev = Math.abs(wave[i] - 128);
          if (dev > peak) peak = dev;
        }
        onLevel?.(Math.min(1, peak / 40));
        // ~5% of full scale: above the hiss of a quiet room, below any
        // spoken word near the microphone.
        if (peak > 6) { voiced = true; lastVoice = Date.now(); }
        else if (Date.now() - lastVoice >= SILENCE_STOP_MS) {
          stopWatching();
          if (rec.state !== "inactive") rec.stop();
        }
      }, 200);
    }
  } catch { /* no analyser — the tap keeps working as before */ }
  rec.onstop = async () => {
    stopWatching();
    stream.getTracks().forEach((t) => t.stop());
    const blob = new Blob(chunks, { type: "audio/webm" });
    if (!blob.size) { onError("nothing was recorded"); return; }
    // The energy gate: silence never reaches the transcriber, so the
    // transcriber can never invent a sentence from it. A platform with
    // no analyser keeps the old behavior — it cannot tell, so it asks.
    if (hadAnalyser && !voiced) { onError("nothing was heard in that"); return; }
    const b64: string = await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(String(reader.result).split(",")[1] || "");
      reader.readAsDataURL(blob);
    });
    try {
      const { text } = await api.transcribe(b64);
      if (text) onText(text);
      else onError("nothing was heard in that");
    } catch (e) {
      const msg = (e as Error).message;
      // The recogniser cannot transcribe a finished recording, so these
      // words are lost either way — but the next tap does not have to
      // fail the same way twice.
      if (deviceRecogniser() !== null) {
        preferDevice = true;
        onError(msg + " — tap the mic again and the device's own recogniser "
          + "will listen instead");
      } else {
        onError(msg.includes("device")
          ? "no transcription service is set up — add an OpenAI or ElevenLabs key in Settings to talk to the Guardian"
          : msg);
      }
    }
  };
  rec.start();
  return { stop: () => { if (rec.state !== "inactive") rec.stop(); } };
}
