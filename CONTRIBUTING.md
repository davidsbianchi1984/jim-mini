# Contributing to JIM-mini

Thanks for your interest! JIM-mini (Guardian) is one of three interoperating
products (with [qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)); see
[docs/tandem.md](docs/tandem.md) for how they fit together.

## Development setup

```bash
pip install -e .[dev]      # backend + test deps
pytest                     # run the suite (offline stub provider, no API key needed)
uvicorn jim.api:app --reload
```

For the guardian console:

```bash
cd app
npm ci
npm run dev                # renderer in the browser
npm run electron:dev       # renderer inside Electron
```

The backend runs fully offline by default — the deterministic stub provider
answers when no `ANTHROPIC_API_KEY` is set, so tests and local dev need no
network or credentials.

## Guidelines

- **Tests pass, and cover new behavior.** Run `pytest` before opening a PR;
  add tests for any new endpoint or detection rule. The console must still
  build (`cd app && npm run build`) — CI checks both.
- **This is health data.** Everything under `/{user_id}` is PHI: guard it with
  the per-user token, never log it, and seal anything sensitive in the PDI
  vault rather than local plaintext.
- **Keep the products decoupled.** Cross-product calls go over HTTP at the
  client seam (see the QRME and PDI clients), never direct imports of another
  product's internals.
- **Match the surrounding style.** Standard-library-first Python; keep comments
  at the density of the file you're editing.

## Pull requests

1. Branch off `main`.
2. Make the change with tests; keep commits focused.
3. Open a PR describing the what and why. CI runs `pytest` and the console
   smoke build.

By contributing you agree that your contributions are licensed under the
project's [MIT License](LICENSE).
