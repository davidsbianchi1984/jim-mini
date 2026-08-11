import { useEffect, useState } from "react";
import { api } from "./api";
import { fill, t as tr, visitorLang } from "./l10n";

/**
 * The footsteps in the corner: how many people are enrolled here.
 *
 * The number rides /health — the request every client already makes at
 * launch for the version handshake — so the counter costs no extra door.
 * It is an aggregate, never a roster: the payload carries the count and
 * nothing else about anybody. A deployment old enough to answer /health
 * without the field simply shows no chip, which is honest twice over.
 */
export function Footsteps() {
  const lang = visitorLang();
  const [count, setCount] = useState<number | null>(null);

  useEffect(() => {
    let alive = true;
    api.health()
      .then((h) => {
        if (alive && typeof h.footsteps === "number") setCount(h.footsteps);
      })
      .catch(() => { /* unreachable is the connection panel's story */ });
    return () => { alive = false; };
  }, []);

  if (count === null) return null;

  return (
    <div className="footsteps" title={tr("steps.tip", lang)}>
      <span aria-hidden="true">👣</span>{" "}
      {fill("steps.count", lang, { n: count })}
    </div>
  );
}
