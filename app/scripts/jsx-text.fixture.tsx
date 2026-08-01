/**
 * What `jsx-text.mjs` is supposed to find, and what it is supposed to ignore.
 *
 * Not a screen and never rendered. It exists so the extractor can be checked
 * against a known answer that does not move when product copy does — pointing
 * the guard at a real screen means the guard's expectations drift every time
 * somebody edits a sentence, and a guard nobody can trust gets relaxed.
 *
 * The expected result is asserted in
 * `tests/test_the_stranger_has_a_language_too.py`.
 *
 * Every awkward case that has actually broken a version of this check lives
 * here: a generic that looks like a tag, a handler with an arrow in it, a
 * sentence wrapped around an interpolation, and a paragraph split over
 * several source lines.
 */
import { useState } from "react";

/* A comment containing a sentence that must never be reported. */
export function Fixture({ count }: { count: number }) {
  // Nor this one.
  const [value, setValue] = useState<string | null>(null);
  return (
    <div className="not-user-visible">
      <h3>A heading</h3>
      <p>
        A paragraph that runs across several lines of source and is
        nonetheless one sentence to whoever reads it.
      </p>
      <p>Wrapped around {count} an interpolated value.</p>
      <input placeholder="a placeholder" title="a title"
             value={value ?? ""} onChange={(e) => setValue(e.target.value)} />
      <button aria-label="an aria label" onClick={() => setValue(null)}>
        A button
      </button>
    </div>
  );
}
