// Pick which model answers — as tiles you click, not a dropdown.
//
// Each mark is drawn here rather than fetched: an installer that reaches out
// to six vendors' CDNs for logo files is one that leaks which product you
// opened and breaks when a URL moves. These are simple original glyphs in
// each brand's own colour, which is what a picker needs — recognisable at a
// glance, and honest about being our drawing rather than their trademark.
import type { CSSProperties } from "react";

export interface ProviderInfo {
  name: string;          // registry key: anthropic | openai | grok | …
  label: string;
  configured: boolean;
  model: string;
  network: boolean;
}

const MARKS: Record<string, { color: string; glyph: JSX.Element; blurb: string }> = {
  anthropic: {
    color: "#d97757",
    blurb: "Claude — the default here",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M6.2 17.5 10.9 6h2.3l4.7 11.5h-2.4l-1-2.6H9.6l-1 2.6H6.2Zm4.1-4.5h3.5L12 8.4 10.3 13Z"
              fill="currentColor" />
      </svg>
    ),
  },
  openai: {
    color: "#10a37f",
    blurb: "ChatGPT",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M12 3.2 19 7.3v8.2L12 19.6 5 15.5V7.3l7-4.1Zm0 2.3L7 8.4v6.2l5 2.9 5-2.9V8.4l-5-2.9Zm0 2.6 3 1.7v3.4l-3 1.7-3-1.7V9.8l3-1.7Z"
              fill="currentColor" />
      </svg>
    ),
  },
  grok: {
    color: "#e7e9ea",
    blurb: "Grok (xAI)",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M5 19 12.6 5h2.6L7.6 19H5Zm7.6 0 2.3-4.2h2.6L15.2 19h-2.6ZM14.9 10l2.3-4.2h2.6L17.5 10h-2.6Z"
              fill="currentColor" />
      </svg>
    ),
  },
  perplexity: {
    color: "#20a5b8",
    blurb: "Perplexity — answers with sources",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M11.2 3.6v5.2L6.6 5.4v5.1H4.2v7.9h2.4v2.9l4.6-3.4v3.4h1.6v-3.4l4.6 3.4v-2.9h2.4v-7.9h-2.4V5.4l-4.6 3.4V3.6h-1.6Zm-3 4.3 3 2.2-3 2.2V7.9Zm7.6 0v4.4l-3-2.2 3-2.2Z"
              fill="currentColor" />
      </svg>
    ),
  },
  gemini: {
    color: "#4285f4",
    blurb: "Gemini (Google)",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M12 3c.4 4.6 4.4 8.6 9 9-4.6.4-8.6 4.4-9 9-.4-4.6-4.4-8.6-9-9 4.6-.4 8.6-4.4 9-9Z"
              fill="currentColor" />
      </svg>
    ),
  },
  stub: {
    color: "#8b949e",
    blurb: "Offline — no network, no key, deterministic",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M5 7h14v10H5V7Zm2 2v6h10V9H7Zm2 2h2v2H9v-2Zm4 0h2v2h-2v-2Z"
              fill="currentColor" />
      </svg>
    ),
  },
  auto: {
    color: "#7ee787",
    blurb: "Let the app choose the best configured one",
    glyph: (
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden>
        <path d="M12 4l1.9 4.3 4.7.5-3.5 3.1 1 4.6L12 14.2 7.9 16.5l1-4.6L5.4 8.8l4.7-.5L12 4Z"
              fill="currentColor" />
      </svg>
    ),
  },
};

export function ProviderTiles(props: {
  providers: ProviderInfo[];
  chosen: string;                 // "auto" or a registry key
  effective?: string;             // what it actually resolves to
  onPick: (name: string) => void;
  busy?: boolean;
}) {
  const tiles = [
    { name: "auto", label: "Automatic", configured: true, model: "", network: false },
    ...props.providers,
  ];
  return (
    <div className="provider-tiles">
      {tiles.map((p) => {
        const mark = MARKS[p.name] || MARKS.stub;
        const active = props.chosen === p.name;
        const style: CSSProperties = { color: mark.color };
        return (
          <button key={p.name} type="button" disabled={props.busy}
                  className={`provider-tile${active ? " active" : ""}`}
                  style={active ? { ...style, borderColor: mark.color } : style}
                  onClick={() => props.onPick(p.name)}>
            <span className="provider-glyph">{mark.glyph}</span>
            <span className="provider-name">{p.label || p.name}</span>
            <span className="provider-note">
              {p.name === "auto"
                ? mark.blurb
                : p.configured
                  ? (p.model || mark.blurb)
                  : "needs a key — add one above"}
            </span>
            {active && <span className="provider-check">✓</span>}
          </button>
        );
      })}
    </div>
  );
}
