import { useCallback, useLayoutEffect, useRef, useState } from "react";
import { GuardianLights } from "./GuardianLights";
import { Help } from "./Help";
import { Underway } from "./Underway";
import { t as tr, visitorLang } from "./l10n";

/**
 * The edge dock: every control the shell floats over the screens, as one
 * stack of tabs on the right edge of the glass.
 *
 *     asked     "Jim-mini still has all the circle running lights, the
 *               help tabs and the count — needs to be tabs off to the
 *               side, just like QRME"
 *     mattered  four fixed things in four corners, and a phone has no
 *               empty corner
 *
 * The help bubble sat bottom-right, the Guardian's lights bottom-left,
 * the task window pinned beside them, the footsteps count in a corner of
 * its own. Each was a `position: fixed` widget that had never been told
 * what any screen underneath it had put there, and each carried its own
 * minimize-to-a-dot so a person could move it out of the way — which is
 * the tell: four controls that each needed an escape hatch were four
 * controls in the way.
 *
 * QRME solved this in 3.1.2 and this is that solution, carried over
 * rather than re-invented, so the two consoles are learned once. Each
 * control is a tab protruding from the right side of the window;
 * pressing a tab opens its panel beside it, pressing again (or another
 * tab) closes it; the whole stack slides up or down by its grip, and the
 * position is remembered per device. A person who finds it in the way
 * moves it once, and it stays moved.
 *
 * Three tabs, where QRME has two. The help box and the Guardian's lights
 * are the shared pair. The third is this product's own: the task window,
 * which answers *what is my guardian doing* where the lights answer *is
 * anything wrong* — two questions with different answers, which is why
 * they stayed two panels rather than becoming one crowded one.
 *
 * The footsteps count is gone, as it went from QRME: a number beside a
 * glyph, in a corner, saying how many people are enrolled, was never
 * worth a fixed position on a phone.
 *
 * Only one panel is open at a time — the dock owns that, so the panels
 * cannot open over each other the way independent widgets could.
 */

const Y_KEY = "jim.dock.y";
//: Where the dock's top sits, as a share of the window's height. Low on
//: the glass by default, under anything a screen puts at its middle.
const Y_DEFAULT = 72;
const Y_MIN = 4;
//: The ceiling is measured, not written. QRME can use a flat 90 because its
//: navigation is a drawer opened from the top-left; here the sidebar becomes
//: the bottom tab bar on a phone, and a stack dragged to 90% of a short
//: screen ends up over the tabs — which is the exact defect
//: `test_the_light_sat_on_the_menu.py` exists for, re-introduced in a new
//: shape. So the floor of the stack is kept above the bar, using the height
//: the bar publishes about itself rather than a guess about how tall it is.
const Y_MAX_CEILING = 90;
const BAR_VAR = "--tabbar-h";
//: A press that travels less than this is a press, not a move.
const SLOP_PX = 4;

export type DockTab = "help" | "lights" | "underway";

function remembered(): number {
  try {
    const v = Number(localStorage.getItem(Y_KEY));
    if (Number.isFinite(v) && v >= Y_MIN && v <= Y_MAX_CEILING) return v;
  } catch { /* a browser that blocks storage keeps the default */ }
  return Y_DEFAULT;
}

//: How much of the window the stack and the bar under it occupy, as a
//: percentage, so the dock's top can be held above both.
function reservedPct(stack: number): number {
  const declared = getComputedStyle(document.documentElement)
    .getPropertyValue(BAR_VAR).trim();
  const bar = declared.endsWith("px") ? parseFloat(declared) : 0;
  const h = window.innerHeight || 1;
  return ((stack + (Number.isFinite(bar) ? bar : 0) + 12) / h) * 100;
}

function clamp(v: number, ceiling: number): number {
  return Math.min(ceiling, Math.max(Y_MIN, v));
}

export function EdgeDock() {
  const lang = visitorLang();
  const [y, setY] = useState(remembered);
  const [open, setOpen] = useState<DockTab | null>(null);
  const [ceiling, setCeiling] = useState(Y_MAX_CEILING);
  const stack = useRef<HTMLDivElement | null>(null);
  const drag = useRef<{ startY: number; startPct: number; moved: boolean }
                      | null>(null);

  // Measured after layout and again on resize, because the bar is as tall as
  // its labels and every label here is translated into ten languages — the
  // number that was wrong the first time this defect appeared was a guess
  // about that height written into the stylesheet.
  const measure = useCallback(() => {
    const el = stack.current;
    if (!el) return;
    const top = Math.min(Y_MAX_CEILING,
                         100 - reservedPct(el.offsetHeight));
    const limit = Math.max(Y_MIN, top);
    setCeiling(limit);
    setY((cur) => Math.min(cur, limit));
  }, []);

  useLayoutEffect(() => {
    measure();
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, [measure]);

  const toggle = (tab: DockTab) => setOpen((cur) => (cur === tab ? null : tab));

  function remember(pct: number) {
    try { localStorage.setItem(Y_KEY, String(Math.round(pct))); }
    catch { /* not remembered, still moved */ }
  }

  // The grip is the one thing that moves the stack. The tabs only press:
  // a control that is both a button and a handle answers a slow thumb
  // with the wrong one of the two, and the report that shaped this was
  // about things being in the way, not about reaching them faster.
  function down(e: React.PointerEvent<HTMLButtonElement>) {
    drag.current = { startY: e.clientY, startPct: y, moved: false };
    e.currentTarget.setPointerCapture(e.pointerId);
  }
  function move(e: React.PointerEvent<HTMLButtonElement>) {
    const d = drag.current;
    if (!d) return;
    const dy = e.clientY - d.startY;
    if (!d.moved && Math.abs(dy) < SLOP_PX) return;
    d.moved = true;
    setY(clamp(d.startPct + (dy / window.innerHeight) * 100, ceiling));
  }
  function up(e: React.PointerEvent<HTMLButtonElement>) {
    const d = drag.current;
    drag.current = null;
    if (!d) return;
    e.currentTarget.releasePointerCapture(e.pointerId);
    if (d.moved) remember(clamp(d.startPct + ((e.clientY - d.startY)
                                       / window.innerHeight) * 100, ceiling));
  }
  // The same move from a keyboard: the grip is a button, and a button
  // that only answers a pointer is a control half the room cannot use.
  function key(e: React.KeyboardEvent<HTMLButtonElement>) {
    const step = e.key === "ArrowUp" ? -5 : e.key === "ArrowDown" ? 5 : 0;
    if (!step) return;
    e.preventDefault();
    const next = clamp(y + step, ceiling);
    setY(next);
    remember(next);
  }

  // A panel hangs off the dock's top edge while the dock is high on the
  // glass, and off its bottom edge once it is low — so the panel opens
  // toward the room there is, never off the bottom of a phone.
  const low = y > 50;
  return (
    <div ref={stack} className={"edge-dock" + (low ? " low" : "") + (open ? " open" : "")}
         style={{ top: `${y}%`, ["--dock-y" as string]: `${y}vh` }}
         data-dock-y={Math.round(y)}>
      <button className="edge-grip" type="button"
              aria-label={tr("dock.move", lang)} title={tr("dock.move", lang)}
              onPointerDown={down} onPointerMove={move}
              onPointerUp={up} onPointerCancel={up} onKeyDown={key}>
        <span aria-hidden="true">⋮</span>
      </button>
      <Help open={open === "help"} onToggle={() => toggle("help")} />
      <GuardianLights open={open === "lights"}
                      onToggle={() => toggle("lights")} />
      <Underway open={open === "underway"}
                onToggle={() => toggle("underway")} />
    </div>
  );
}
