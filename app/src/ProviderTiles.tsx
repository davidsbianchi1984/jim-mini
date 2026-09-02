import type { CSSProperties } from "react";

export interface ProviderInfo {
  name: string;          // registry key: anthropic | openai | grok | …
  label: string;
  configured: boolean;
  model: string;
  network: boolean;
  origin?: string;       // US | CN | FR | CA | local | any
}

/**
 * The tiles a person picks a model from.
 *
 * No company emblems. Every provider is drawn the same way — a generic
 * monogram of its own initial in one accent — because the marks belong to
 * the companies, not to this product, and a menu that borrowed them would be
 * wearing somebody else's badge. The provider's public name is the label;
 * that is the honest, unbranded way to say which one it is. One accent, not
 * a rainbow: the choice is the person's, and the palette stays out of it.
 */
const ACCENT = "var(--accent, #7c5cff)";

function monogram(name: string): string {
  if (name === "auto") return "A";
  if (name === "ollama" || name === "vault") return "⌂";      // on this machine
  if (name === "custom") return "⚙";                          // your own endpoint
  if (name === "stub") return "·";
  return (name[0] || "?").toUpperCase();
}

export function ProviderTiles(props: {
  providers: ProviderInfo[];
  chosen: string;                 // "auto" or a registry key
  effective?: string;             // what it actually resolves to
  onPick: (name: string) => void;
  busy?: boolean;
  autoLabel?: string;             // localized "Automatic"
  needsKey?: string;              // localized "needs a key — add one above"
}) {
  const tiles: ProviderInfo[] = [
    { name: "auto", label: props.autoLabel || "Automatic", configured: true,
      model: "", network: false },
    ...props.providers,
  ];
  return (
    <div className="provider-tiles" data-screen="15">
      {tiles.map((p) => {
        const active = props.chosen === p.name;
        const style: CSSProperties = { color: ACCENT };
        return (
          <button key={p.name} type="button" disabled={props.busy}
                  className={`provider-tile${active ? " active" : ""}`}
                  style={active ? { ...style, borderColor: ACCENT } : style}
                  onClick={() => props.onPick(p.name)}>
            <span className="provider-glyph" aria-hidden
                  style={{ display: "inline-flex", alignItems: "center",
                           justifyContent: "center", width: 26, height: 26,
                           borderRadius: "50%", border: "1.5px solid currentColor",
                           fontWeight: 700, fontSize: 13 }}>
              {monogram(p.name)}
            </span>
            <span className="provider-name">
              {p.label || p.name}
              {p.origin && p.origin !== "any" && p.origin !== "local" && (
                <span className="muted small" style={{ marginLeft: 6 }}>{p.origin}</span>
              )}
            </span>
            <span className="provider-note">
              {p.name === "auto"
                ? ""
                : p.configured
                  ? p.model
                  : (props.needsKey || "")}
            </span>
            {active && <span className="provider-check">✓</span>}
          </button>
        );
      })}
    </div>
  );
}
