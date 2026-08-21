// The screen, actually watched.
//
// `monitors.py` has promised since it was written that the screen monitor
// can "see what is on your screen while you work", holding nothing —
// "what it notices is offered and dropped". A field report read the roster
// against a house where nothing was connected and named the gap: every row
// said sensing, and nothing was sensing anything. For the wearables the
// missing half is hardware. For this one it was never hardware at all: the
// browser has had `getDisplayMedia` for years and this console had never
// called it.
//
//     asked     may JIM see this screen
//     mattered  has it ever been shown one
//
// ## The share picker is the consent
//
// Nothing here asks for a permission of its own, and nothing here can start
// without the person choosing a window in the browser's own chooser — the
// one dialog every operating system draws the same way, that names exactly
// what will be shared and cannot be pre-answered. That is a better consent
// gesture than any switch this product could draw, so the switch is not
// drawn twice: `plug_in` records the decision, and this asks the browser.
//
// Ending is the same in reverse. Stopping the track — from here, or from
// the browser's own "stop sharing" bar, which the person can always reach —
// ends the watching, and `onended` is wired so the two cannot disagree
// about whether it is still going.
//
// ## What leaves this machine
//
// One frame at a time, at a slow interval, on its way to being described.
// Not a stream, not a recording, and never more than one in flight: a
// sample that is still being described when the next one comes due is a
// queue nobody asked for, and on a slow line it would become a permanent
// backlog of stale pictures of somebody's screen.
import { api } from "./api";

/** How often a frame is taken. Twenty seconds is a working pace: often
 *  enough that a companion notices what somebody is doing, rare enough
 *  that it is nothing like a recording, and far enough apart that each
 *  frame is described and gone before the next is due. */
export const EVERY_MS = 20_000;

/** The longest edge a frame is scaled to before it leaves. A description
 *  does not need a retina screenshot, and a smaller frame is a smaller
 *  thing to send about somebody's private screen. */
export const WIDEST = 1024;

export interface Watching {
  /** Stop watching — the same end the browser's own stop-sharing gives. */
  stop: () => void;
}

/** Begin watching this screen, and hand each described moment back.
 *
 *  Resolves once the person has chosen what to share; rejects if they
 *  cancel the chooser, which is a person saying no and not an error to
 *  dress up. `onSaw` is called with each sentence the guardian got back,
 *  and `onTrouble` with anything that went wrong — a refusal from the
 *  server included, so a deployment with no eyes configured says so on
 *  the screen instead of looking like it is working.
 */
export async function watchScreen(
  uid: string,
  token: string,
  onSaw: (words: string) => void,
  onTrouble: (message: string) => void,
): Promise<Watching> {
  const media = navigator.mediaDevices as MediaDevices & {
    getDisplayMedia?: (c: object) => Promise<MediaStream>;
  };
  if (!media?.getDisplayMedia) {
    throw new Error(
      "this browser cannot share a screen — try Chrome or Edge on a "
      + "computer, or Chrome on Android");
  }
  // `audio: false` said out loud: a screen share that also grabs the
  // system's sound is a different capture with a different consent, and
  // the screen monitor's promise is about what is *on* the screen.
  const stream = await media.getDisplayMedia({ video: true, audio: false });
  const track = stream.getVideoTracks()[0];
  let stopped = false;
  let looking = false;
  let timer = 0;

  const stop = () => {
    if (stopped) return;
    stopped = true;
    if (timer) { window.clearInterval(timer); timer = 0; }
    stream.getTracks().forEach((t) => t.stop());
  };
  // The browser's own stop-sharing bar is always reachable and always wins.
  // Without this the console would go on believing it was watching a screen
  // the person had already taken back.
  track.addEventListener("ended", stop);

  // Drawn through a canvas rather than an ImageCapture: canvas is
  // everywhere getDisplayMedia is, and this needs one still frame, not a
  // photographic pipeline.
  const video = document.createElement("video");
  video.srcObject = stream;
  video.muted = true;
  await video.play().catch(() => { /* a paused element still yields frames */ });

  const takeOne = async () => {
    // One in flight, ever. See the header: a backlog of stale pictures of
    // somebody's screen is the failure mode worth designing out.
    if (stopped || looking) return;
    const w = video.videoWidth, h = video.videoHeight;
    if (!w || !h) return;                       // not yet painting
    looking = true;
    try {
      const scale = Math.min(1, WIDEST / Math.max(w, h));
      const canvas = document.createElement("canvas");
      canvas.width = Math.round(w * scale);
      canvas.height = Math.round(h * scale);
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const frame = canvas.toDataURL("image/jpeg", 0.7).split(",")[1] || "";
      if (!frame) return;
      const moment = await api.monitorSaw(
        uid, "screen", token, frame,
        "how the person at this screen seems to be doing");
      // `described`, never `kept`: the screen monitor keeps nothing, and
      // what comes back is the offer this console shows once and lets go.
      if (!stopped && moment.described) onSaw(moment.described);
    } catch (e) {
      // Reported, not fatal: a screen that could not be described this
      // minute is still a screen worth watching next minute, and the one
      // failure worth stopping for — the person ending the share — comes
      // through `ended` rather than through here.
      if (!stopped) onTrouble((e as Error).message);
    } finally {
      looking = false;
    }
  };

  timer = window.setInterval(() => { void takeOne(); }, EVERY_MS);
  void takeOne();                               // the first one now, not in 20s
  return { stop };
}
