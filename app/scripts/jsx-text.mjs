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
 * - String literals inside a **child expression** — `{ok ? "answering" :
 *   "degraded"}`. The browser lays these out as text exactly like `JsxText`;
 *   the only difference is that the choice is made at runtime.
 *
 *   Added after a field report: the vault light said *vault answering* in
 *   English on a console that translates everything else, and this reader
 *   saw nothing in the file. `VaultLight.tsx` imports the translator, so the
 *   guard forbidding a half-translated screen was already watching it —
 *   watching, and reading zero strings.
 *
 *       asked     what text does this file place between tags
 *       mattered  what words does this screen put on the glass
 *
 * Deliberately *not* included: string literals anywhere else — attribute
 * values beyond the four above, object properties, ids, keys, class names.
 * The rule is position rather than content: a literal counts when it sits
 * where children go, because that is where a browser draws it.
 *
 * Usage: `node scripts/jsx-text.mjs <file.tsx> [...]` → JSON on stdout,
 * `{ "<path>": ["<text>", ...] }`.
 */
import { readFileSync } from "node:fs";
import ts from "typescript";

/** Attributes whose string value a person reads. */
const VISIBLE_ATTRS = new Set(["placeholder", "title", "alt", "aria-label"]);

/**
 * The string literals a child expression can put on the glass.
 *
 * Walks only the shapes that *are* the rendered value — a literal on its
 * own, either branch of a ternary, either side of `&&` / `??`, and the
 * pieces of a concatenation. It deliberately does not descend into calls:
 * `t("vl.title", lang)` renders a translation, and its key is not a word
 * anybody reads.
 */
function literalsDrawnBy(expr) {
  if (ts.isStringLiteral(expr)) return [expr.text];
  if (ts.isParenthesizedExpression(expr)) return literalsDrawnBy(expr.expression);
  if (ts.isConditionalExpression(expr)) {
    return [...literalsDrawnBy(expr.whenTrue), ...literalsDrawnBy(expr.whenFalse)];
  }
  if (ts.isBinaryExpression(expr)) {
    const op = expr.operatorToken.kind;
    if (op === ts.SyntaxKind.AmpersandAmpersandToken
        || op === ts.SyntaxKind.BarBarToken
        || op === ts.SyntaxKind.QuestionQuestionToken
        || op === ts.SyntaxKind.PlusToken) {
      return [...literalsDrawnBy(expr.left), ...literalsDrawnBy(expr.right)];
    }
  }
  return [];
}

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
    } else if (ts.isJsxExpression(node) && node.expression
               && node.parent && (ts.isJsxElement(node.parent)
                                  || ts.isJsxFragment(node.parent))) {
      // A child expression: whatever string it can evaluate to is drawn
      // between the tags. Only literals that are the expression itself or a
      // branch of it are read — a literal buried in a call argument is that
      // call's business, not the layout's.
      //
      // A literal with no letter in it is skipped: the empty string, a
      // spacer, ` · `, an emoji. Those are drawn, but they are not words,
      // and a reader of this list is deciding what to translate.
      for (const literal of literalsDrawnBy(node.expression)) {
        // Collapsed and trimmed exactly like `JsxText` above: the spaces
        // around a phrase are spacing between elements, not part of the
        // words, and a record of these strings is read back line by line.
        const text = literal.replace(/\s+/g, " ").trim();
        if (text && /\p{Letter}/u.test(text)) found.push(text);
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
