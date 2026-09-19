# Hyperframes Composition Brief: JIM-mini ✕ QRME

## Objective
Create a short launch-style brag video for JIM-mini running in tandem with
QRME: the Guardian's handover to specialist profiles, the coach's consented
ask, and the care team's joint plan.

## Output
- Composition directory: `brag-output/composition/`
- Rendered video: `brag-output/brag.mp4`
- Format: landscape — 1920x1080
- Duration: 25 seconds

## Source Material
- Project root: `/home/user/jim-mini`
- Primary files read: `README.md` (hero, Features, Architecture, release
  3.4.0), `docs/tandem.md`, `docs/diagrams/tandem-flow.svg`,
  `jim/guardian.py` (`_deliver`, `_tandem_guidance`), `jim/specialists.py`
  (`offer`), `jim/coach.py` (`ask_specialist`), `jim/careteam.py`
  (`consider`), `jim/conditions.py` (labels, the heart-rate reason),
  `jim/seed.py` (`TANDEM_HANDLES`), `app/src/styles.css` (`:root` palette,
  body gradient), `app/src/l10n.ts` (`spec.ask`, care-team copy),
  `docs/screens/01-home.png`, `03-monitor.png`, `07-coach.png`,
  `18-careteam.png`; the specialist's portrait from the QRME repository
  (`qrme/assets/portraits/dr_lena_whitcomb.webp`, the served photograph)
- Product name: JIM-mini (with QRME)
- Tagline / strongest claim: "A personal health guardian for anyone, at any
  age." — and, in tandem, "the readings that trigger a detection cross the
  Guardian→QRME handoff as real biometrics"
- Key UI or visual moment to recreate: the *Live Monitoring* card (Send to
  Guardian), the *Coach* card with the specialist offer row (Ask them), the
  *Care Team* status and plan
- Copy that must appear verbatim:
  - monitor → predict → guide → escalate
  - Submit a biometric sample · Send to Guardian
  - acute anxiety / panic · heart rate 110 bpm (50 over resting), respiratory rate 22/min
  - [Guardian monitoring] The user shows signs of acute anxiety / panic (heart rate 110 bpm (50 over resting), respiratory rate 22/min). Please offer brief, supportive guidance.
  - Ask the coach · Ask them
  - a specialist covers this area. Nothing has been sent — asking them shares the message you just wrote with a profile outside JIM, and only happens if you say so.
  - Linked to a care team.
  - heart_rate is drifting outside the personal band while medication adherence is slipping (metformin at 57% over the last week). Coordinate a gentle plan: what each desk should do this week, and what to watch for.
  - JIM-mini · QRME
  - Patent pending · US 2025/0246290 A1

## Creative Direction
- Tone preset: cinematic
- Creative direction: a launch trailer for the handover between two products
- Interpretation: short declarative lines, one claim per scene, full-bleed
  type; UI recreations large and clean; green is the Guardian, violet is QRME,
  and the wire between them is drawn as a moving packet.
- Angle: a guardian that watches one person and can reach a city of
  specialists without letting go — every crossing a choice, every crossing on
  the record, the emergency ladder never waiting on anybody.
- Hook: "A guardian for one person." at full scale, the four-word loop under it.
- Outro / punchline: two spheres, **JIM-mini ✕ QRME**, "A guardian, in
  tandem.", the patent line, under a fading bed.
- Avoid: generic SaaS language; abstract filler visuals; unrelated redesign;
  any suggestion that the escalation ladder depends on QRME.

## Visual Identity
- Background: radial-gradient(120% 100% at 20% 0%, #10203a 0%, #0a1120 60%, #070b16 100%)
- Text: #eef1f7 (secondary #8a94ad, tertiary #626d88)
- Accent: green #43e08a / #2fd27a (Guardian), violet #a78bfa (QRME), blue #3aa0ff, amber #f7b731, red #ff4d5e
- Surfaces: card #182238, card2 #1f2b45, line #26314e, field #0c1424
- Display font: Inter (standing in for the console's system stack), 800, tracking −0.03em
- Body font: Inter 400–600; IBM Plex Mono for labels, keys and numbers
- Visual references: the green primary button on a navy card (03-monitor); the
  Coach card and its offer row (07-coach); the Care Team status (18-careteam);
  the Overview's blue-violet sphere (01-home)

## Storyboard
Use the storyboard in `brag-output/brag-plan.md` as the creative contract.

Scene summary:
1. Hook — 3.2s — "A guardian for one person." · monitor → predict → guide → escalate
2. Watching — 4.7s — Live Monitoring card typed (110 / 22 / 0.8), Send to Guardian, detection lands on 5.80
3. The handover — 4.7s — JIM card → packet on 8.96 → QRME card on 9.50 (Dr. Lena Whitcomb, reply, custody key)
4. The person who asks — 4.2s — Coach card typed, Ask the coach, offer row verbatim, Ask them
5. The care team — 3.2s — Linked; the goal from the stacking rule; joint plan lands on 17.91
6. The scale — 2.6s — 409 routes · 131 tables · 3,371 tests · 45 screens · 10 languages on 20.02 … 22.12
7. Outro — 2.4s — spheres, JIM-mini ✕ QRME on 22.65, tagline, patent line; bed fades

## Audio
- Audio role: cinematic support
- Music: `assets/music/happy-beats-business-moves-vol-11-by-ende-dot-app.mp3`
- Music treatment: start 0s, volume ~0.55, fade to 0 over the last 1.5s (automation lane)
- Music cue guidance: preset `assets/music/happy-beats-business-moves-vol-11-by-ende-dot-app.music-cues.json`; grid every ~0.525s from 1.60s; strong cues 1.60, 3.70, 5.80, 6.34, 8.96, 9.50, 12.65, 17.91, 22.65, 24.23
- Audio-reactive treatment: subtle; the green and violet glows breathe with RMS (`assets/audio-data.json`)
- Audio-coupled moments: typed text — key ticks; Send to Guardian / Ask the coach / Ask them — clicks; detection, QRME card, offer row, plan — card slides; packet landing and tiles — soft impacts; wordmark — one bell
- SFX selection guidance: impactSoft_medium_*, interface/click_00{2,3}, casino/card-slide-1, keyboard/keypress-00{1..6}
- Audio files: copied into `brag-output/composition/assets/`

## Hyperframes Instructions
Load `hyperframes-core`, `hyperframes-animation`, `hyperframes-creative`,
`hyperframes-keyframes`, `hyperframes-cli`. /brag is its own workflow: do not
enter the `hyperframes` intent interview or its promo workflow.

Requirements:
- Show at least one real UI, copy, or visual element from the source project.
- Keep all text readable in the final render.
- Keep the video within 15-25 seconds.
- Include the planned music/SFX layer.
- Treat `/brag` audio notes as guidance, not a fixed cue sheet; cue metadata as optional timing hints.
- Major reveals may move toward nearby strong cues within about 0.15s; smaller entrances may align to nearby beat points within about 0.10s; use 1-3 strong cue locks.
- Use local assets for audio and any required runtime/media dependencies (GSAP is vendored).
- Run `hyperframes check` before render — it is brag's single gate.
