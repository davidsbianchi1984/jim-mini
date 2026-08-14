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

/** Say `text` aloud — the configured voice when there is one, the device's
 *  own otherwise. Resolves when the speaking starts, not when it ends. */
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
      current = new Audio(URL.createObjectURL(blob));
      await current.play();
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
    speechSynthesis.speak(utter);
  }
  return "device";
}

export interface Listener { stop: () => void }

/** The minimal face of the platform's own recogniser. Typed here because
 *  the DOM lib does not ship one, and `any` would hide the contract. */
interface DeviceRecognition {
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

function deviceRecogniser(): (new () => DeviceRecognition) | null {
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
      ? "the operating system refused the device's recogniser — on iPhone "
        + "and iPad that is Dictation being switched off: Settings › "
        + "General › Keyboard › Enable Dictation"
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
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch {
    onError("no microphone available — check the app's microphone permission");
    return { stop: () => {} };
  }
  const chunks: BlobPart[] = [];
  const rec = new MediaRecorder(stream);
  rec.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
  rec.onstop = async () => {
    stream.getTracks().forEach((t) => t.stop());
    const blob = new Blob(chunks, { type: "audio/webm" });
    if (!blob.size) { onError("nothing was recorded"); return; }
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
