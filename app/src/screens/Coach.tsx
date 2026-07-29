import { useRef, useState } from "react";
import { api, type Guidance } from "../api";
import { hush, listen, say, type Listener } from "../speech";
import { useSession } from "../store";

const AREAS = ["mental_health", "health_fitness", "career", "relationships"];

export function Coach() {
  const { session } = useSession();
  const [area, setArea] = useState("mental_health");
  const [message, setMessage] = useState("I've been feeling stressed about work.");
  const [reply, setReply] = useState<Guidance | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const recorder = useRef<Listener | null>(null);

  async function ask(text?: string) {
    const said = (text ?? message).trim();
    if (!session.userId || !session.userToken || !said) return;
    setBusy(true); setError(null);
    try {
      const r = await api.coach(session.userId, { area, message: said },
                                session.userToken);
      setReply(r);
      // Talking to it should mean being answered out loud — a spoken
      // question answered only in text is half a conversation.
      if (r?.content && (text !== undefined || speaking)) {
        setSpeaking(true);
        say(r.content).finally(() => setSpeaking(false));
      }
    }
    catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  async function toggleMic() {
    if (listening) {
      recorder.current?.stop();
      recorder.current = null;
      setListening(false);
      return;
    }
    setError(null);
    setListening(true);
    recorder.current = await listen(
      (text) => { setListening(false); setMessage(text); ask(text); },
      (msg) => { setListening(false); setError(msg); },
    );
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Coach</h2>
        <span className="muted small">24/7 across your life</span>
      </header>
      <div className="card">
        <label>Area
          <select value={area} onChange={(e) => setArea(e.target.value)}>
            {AREAS.map((a) => <option key={a}>{a}</option>)}
          </select>
        </label>
        <label>What's on your mind?
          <textarea rows={3} value={message} onChange={(e) => setMessage(e.target.value)} />
        </label>
        <div className="voice-row">
          <button className="primary" onClick={() => ask()} disabled={busy || listening}>
            {busy ? "Thinking…" : "Ask the coach"}
          </button>
          <button className={listening ? "mic listening" : "mic"} onClick={toggleMic}
                  disabled={busy}>
            {listening ? "◉ Listening — tap to send" : "🎙 Talk to it"}
          </button>
          {reply?.content && (
            <button onClick={() => { if (speaking) { hush(); setSpeaking(false); }
                                     else { setSpeaking(true); say(reply.content).finally(() => setSpeaking(false)); } }}>
              {speaking ? "■ Stop" : "🔊 Read it aloud"}
            </button>
          )}
        </div>
        {error && <div className="error">⚠ {error}</div>}
      </div>
      {reply?.content && (
        <div className="card guidance">
          <div className="guidance-src">{area.replace("_", " ")} · guidance</div>
          <p>{reply.content}</p>
        </div>
      )}
    </div>
  );
}
