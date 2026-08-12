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
    onError(e.error === "not-allowed"
      ? "no microphone available — check the app's microphone permission"
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

/** Listen to the microphone and hand back what was said.
 *
 *  Which path listens is decided by what is configured, not by hope: a
 *  deployment with a transcription key records and sends, because that
 *  works the same in a packaged desktop app as in a browser; one without
 *  uses the recogniser the device already ships — the fallback this
 *  module's header always promised and, until a field report caught it,
 *  this function never actually had.
 */
export async function listen(
  onText: (text: string) => void,
  onError: (message: string) => void,
): Promise<Listener> {
  let hasService = false;
  try {
    const s = await api.getVoiceSettings();
    hasService = s.provider !== "device" && s.key_set;
  } catch { /* an unreachable settings read never blocks listening */ }

  if (!hasService || preferDevice) {
    const dev = deviceListener(onText, onError);
    if (dev) return dev;
    // No recogniser either: record anyway, so the server's own honest
    // refusal is what the person reads rather than a guess made here.
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
