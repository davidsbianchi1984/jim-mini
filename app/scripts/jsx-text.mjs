/**
 * Every piece of English a `.tsx` file puts in front of a person.
 *
 * ## Why this is not a regex
 *
 * `tests/test_the_stranger_has_a_language_too.py` used to find untranslated
 * copy by matching `>([^<>{}]+)<` over the source. Three things were wrong
 * with that, and each of them hid real text:
 *
 * 1. **Any chunk containing an interpolation was skipped entirely**, because
 *    `{` and `}` were excluded from the character class. So
 *    `Also present on: {surfaces.join(", ")}.` was invisible, and the
 *    sentences that *were* reported — "from this moment. It was" — were only
 *    the brace-free scraps of sentences whose interpolated middles the
 *    pattern could not cross.
 * 2. **TypeScript generics look exactly like tags.** `useState<Row | null>`
 *    opens a "tag" the scanner then reads out of, which is why the check
 *    grew a rule dropping any line containing `=`, `;`, `()` or `=>`.
 * 3. **That rule then swallowed real prose**, because a paragraph adjacent
 *    to an `onChange={(e) => ...}` ends up in the same bleeding region as
 *    the handler. `MarkPane`'s entire explanatory paragraph was being
 *    dropped as "code punctuation".
 *
 * Every one of those is the same mistake this audit keeps finding: a checker
 * answering a question slightly to the left of the one that matters. Here the
 * question asked was *what does this source look like*, and the one that
 * matters is *what does this screen say*.
 *
 * TypeScript's own parser answers the second exactly. `JsxText` is a node
 * kind in the grammar; there is no guessing left to do.
 *
 * ## What counts as user-visible
 *
 * - `JsxText` nodes — the literal text between tags.
 * - String literals in attributes a person reads: `placeholder`, `title`,
 *   `alt`, `aria-label`. A `className` is not read by anybody.
 *
 * Deliberately *not* included: string literals anywhere else. A component
 * that builds a sentence in a variable would slip past this, and that is a
 * known limit rather than an oversight — the alternative is reporting every
 * id, key and CSS class in the file.
 *
 * Usage: `node scripts/jsx-text.mjs <file.tsx> [...]` → JSON on stdout,
 * `{ "<path>": ["<text>", ...] }`.
 */
import { readFileSync } from "node:fs";
import ts from "typescript";

/** Attributes whose string value a person reads. */
const VISIBLE_ATTRS = new Set(["placeholder", "title", "alt", "aria-label"]);

function textsIn(path) {
  const source = ts.createSourceFile(
    path, readFileSync(path, "utf8"), ts.ScriptTarget.Latest, true,
    ts.ScriptKind.TSX);

  const found = [];
  const walk = (node) => {
    if (ts.isJsxText(node)) {
      // JSX collapses runs of whitespace and drops lines that are only
      // whitespace, so a paragraph split across four source lines is one
      // sentence to the reader and must be one entry here.
      const text = node.text.replace(/\s+/g, " ").trim();
      if (text) found.push(text);
    } else if (ts.isJsxAttribute(node) && node.initializer) {
      const name = node.name.getText();
      const init = node.initializer;
      if (VISIBLE_ATTRS.has(name) && ts.isStringLiteral(init)) {
        found.push(init.text);
      }
    }
    ts.forEachChild(node, walk);
  };
  walk(source);
  return found;
}

const out = {};
for (const path of process.argv.slice(2)) out[path] = textsIn(path);
process.stdout.write(JSON.stringify(out, null, 2) + "\n");
