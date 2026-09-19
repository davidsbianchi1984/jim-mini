# Brag video: JIM-mini in tandem with QRME

A 25-second launch-style trailer of the tandem: the Guardian's detection, the
pulse crossing to a QRME specialist as biometrics, the coach's consented ask,
and the care team's joint plan.

- `brag.mp4` — the render (1920x1080, 25s, poster baked as frame 0)
- `brag.jpg` — the poster frame
- `share-copy.txt` — the caption
- `brag-plan.md`, `composition-brief.md` — the storyboard and the handoff brief
- `build_index.py` — regenerates `composition/index.html`; every timestamp,
  typed string and sound cue is computed there
- `composition/` — the editable Hyperframes project

## Regenerate

The music track is not committed (its licence is documented beside the brag
plugin's assets, not here). Copy
`happy-beats-business-moves-vol-11-by-ende-dot-app.mp3` from the brag plugin's
`assets/music/` into `composition/assets/music/`, then:

```bash
cd brag-output
python3 build_index.py
cd composition
npx -y hyperframes@0.8.50 check
npx -y hyperframes@0.8.50 render --quality delivery --output ../brag.mp4
```

Every wire string, label and consent sentence in the video is lifted from the
code (`jim/guardian.py`, `jim/specialists.py`, `jim/careteam.py`,
`jim/conditions.py`) or the console's string table. The specialist's reply and
the three plan lines are illustrative.
