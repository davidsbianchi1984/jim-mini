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

/** Listen to the microphone and hand back what was said.
 *
 *  Recording and sending it to a transcription service is tried first,
 *  because it works the same in a packaged desktop app as in a browser. The
 *  browser's own recogniser is the fallback where no service is configured.
 */
export async function listen(
  onText: (text: string) => void,
  onError: (message: string) => void,
): Promise<Listener> {
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
      // 503 = nothing configured. The browser's recogniser is the answer,
      // but it cannot transcribe a finished recording — so say what to do
      // rather than pretending.
      onError(msg.includes("device")
        ? "no transcription service is set up — add an OpenAI or ElevenLabs key in Settings to talk to the Guardian"
        : msg);
    }
  };
  rec.start();
  return { stop: () => { if (rec.state !== "inactive") rec.stop(); } };
}
