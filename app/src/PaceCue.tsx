import { useEffect, useRef, useState } from "react";
import type { FirstAid } from "./api";

/**
 * The CPR pace, cued the way the patent describes it: a light and a sound.
 * The circle flashes green on every compression beat (110/min from the
 * playbook, never invented here) and a short tick sounds with it; the red
 * state is the cue's own vocabulary — shown when the metronome is stopped
 * mid-emergency, because a stopped pace IS off pace. A 30:2 rhythm rides
 * the counter: every thirtieth beat the cue calls for the two rescue
 * breaths.
 */
export function PaceCue({ aid }: { aid: FirstAid }) {
  const pace = aid.pace;
  const [running, setRunning] = useState(false);
  const [flash, setFlash] = useState(false);
  const [beat, setBeat] = useState(0);
  const audio = useRef<AudioContext | null>(null);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => () => {
    if (timer.current) clearInterval(timer.current);
    audio.current?.close().catch(() => {});
  }, []);

  if (!pace) return null;
  const interval = 60000 / pace.compressions_per_minute;

  function tick() {
    setBeat((b) => b + 1);
    setFlash(true);
    setTimeout(() => setFlash(false), Math.min(140, interval / 2));
    try {
      const ctx = (audio.current ??=
        new (window.AudioContext ||
          (window as unknown as { webkitAudioContext: typeof AudioContext })
            .webkitAudioContext)());
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.frequency.value = 880;
      gain.gain.setValueAtTime(0.25, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
      osc.connect(gain).connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.09);
    } catch { /* no audio device — the light still carries the pace */ }
  }

  function toggle() {
    if (running) {
      if (timer.current) clearInterval(timer.current);
      timer.current = null;
      setRunning(false);
      return;
    }
    setBeat(0);
    setRunning(true);
    tick();
    timer.current = setInterval(tick, interval);
  }

  const inCycle = beat % 30;
  const breaths = running && inCycle === 0 && beat > 0;

  return (
    <div className="pace-cue">
      <button className={"pace-light" + (running ? (flash ? " on" : "") : " stopped")}
              onClick={toggle}
              aria-label={running ? "Stop the pace cue" : "Start the pace cue"}>
        {running ? (breaths ? "2 breaths" : inCycle || 30) : "▶ pace"}
      </button>
      <div className="pace-notes">
        <b>{pace.compressions_per_minute}/min · {pace.compression_to_breath_ratio}</b>
        <div className="muted small">{pace.cue.light}</div>
        <div className="muted small">{pace.cue.audio}</div>
        {!running && <div className="pace-red">stopped — a stopped pace is off pace</div>}
      </div>
    </div>
  );
}
