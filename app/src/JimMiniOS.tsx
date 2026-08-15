/**
 * The jim-mini OS lockup — the whole thing, as the ABRACADABRA menu button.
 *
 * Three stacked parts, in the proportions of the artwork it reproduces: the
 * neon wordmark, the amulet triangle with ABRACADABRA descending eleven rows,
 * and the OS plate.
 *
 *     asked     is the mark on the button
 *     mattered  is the whole mark on the button, big enough to read as itself
 *
 * A first pass shipped the triangle alone, sized so the word inside it could
 * be read — 60px, which is where ABRACADABRA stops being mush. The lockup
 * replaced it, and the brief changed with it: the word inside the triangle no
 * longer has to be legible, the *lockup* does. Rendered at 60, 72, 84 and 96
 * and looked at: the wordmark is cramped at 60, fine at 72, and all three
 * parts read cleanly at 84. So the menu icon is 84px, and every other icon
 * grew to match — a mark that dwarfs its neighbours is not a menu, it is one
 * button that got away.
 *
 * **The neon wordmark is stroked, not filled.** A neon tube is a thin line of
 * even width, and an outline reads that way whichever face the renderer
 * substitutes underneath — which matters, because a script font cannot be
 * assumed. The stack asks for one and degrades to a glowing italic word
 * rather than to something that looks broken.
 *
 * **Every glyph in the triangle is placed at a computed x** rather than left
 * to the renderer's tracking. `textLength` is honoured inconsistently across
 * rasterizers, and a mark that is one width in Chrome and another in cairo is
 * not one mark.
 *
 * Kept identical to `assets/brand/jim-mini-os.svg`, the same drawing as a file
 * for surfaces that take one.
 */

const WORD = "ABRACADABRA";
/** Triangle, in the proportions of the source artwork. */
const TRI = { left: 29.5, right: 71.5, top: 25, apexY: 62, apexX: 50.5 };
/** Per-character advance and size: row one spans 35 of the 39 available. */
const ADV = 3.3;
const FS = 3.0;
/** The letters stop above the apex, as they do on the amulet. */
const TEXT_TOP = 26.2;
const TEXT_BOTTOM = 54.5;
/** The white OS plate: x, y, width, height. */
const PLATE = { x: 9.4, y: 63, w: 81.8, h: 21.3 };

const SCRIPT = "'Brush Script MT','Segoe Script','Bradley Hand'," +
  "'Apple Chancery','Lucida Handwriting',cursive";
const HEAVY = "'Arial Black','Helvetica Neue',Helvetica,Arial,sans-serif";

function rows(): { y: number; glyphs: { x: number; ch: string }[] }[] {
  const step = (TEXT_BOTTOM - TEXT_TOP) / WORD.length;
  return Array.from({ length: WORD.length }, (_, i) => {
    const text = WORD.slice(0, WORD.length - i);
    const first = TRI.apexX - ((text.length - 1) * ADV) / 2;
    return {
      // The baseline, computed rather than left to `dominant-baseline` —
      // that is the attribute renderers disagree about most.
      y: TEXT_TOP + (i + 0.5) * step + FS * 0.34,
      glyphs: [...text].map((ch, j) => ({ x: first + j * ADV, ch })),
    };
  });
}

export function JimMiniOS({ size = 84 }: { size?: number }) {
  return (
    <svg viewBox="0 0 100 100" width={size} height={size}
      role="img" aria-label="jim-mini OS">
      <defs>
        <linearGradient id="jm-edge" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#dfe94b" />
          <stop offset=".5" stopColor="#f2c230" />
          <stop offset="1" stopColor="#b8861f" />
        </linearGradient>
        <filter id="jm-neon" x="-40%" y="-60%" width="180%" height="260%">
          <feGaussianBlur stdDeviation="1.6" result="glow" />
          <feMerge>
            <feMergeNode in="glow" />
            <feMergeNode in="glow" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <rect width="100" height="100" fill="#000" />
      <text x="50" y="21" fontFamily={SCRIPT} fontSize="15" fontStyle="italic"
        textAnchor="middle" fill="none" stroke="#e9f04e" strokeWidth="0.55"
        strokeLinejoin="round" filter="url(#jm-neon)">jim-mini</text>
      <path d={`M${TRI.left} ${TRI.top} H${TRI.right} L${TRI.apexX} ${TRI.apexY} Z`}
        fill="#15120a" stroke="url(#jm-edge)" strokeWidth="2.1"
        strokeLinejoin="round" />
      <g fontFamily="Georgia,'Times New Roman',serif" fontSize={FS}
        fill="#f4efdc" textAnchor="middle">
        {rows().map((row, i) =>
          row.glyphs.map((g, j) => (
            <text key={`${i}-${j}`} x={g.x} y={row.y}>{g.ch}</text>
          )))}
      </g>
      <rect x={PLATE.x} y={PLATE.y} width={PLATE.w} height={PLATE.h} fill="#fff" />
      <text x="50" y={PLATE.y + PLATE.h * 0.78} fontFamily={HEAVY} fontSize="19"
        fontWeight={900} textAnchor="middle" fill="#000"
        letterSpacing="-0.5">OS</text>
    </svg>
  );
}
