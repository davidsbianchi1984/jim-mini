# Brag Plan: JIM-mini, in tandem with QRME

## What is this app?
JIM-mini is a personal health guardian for anyone, at any age: it learns what
is normal *for one person*, notices when something drifts, asks before it
assumes, and only escalates when readings collapse or the questions go
unanswered. Standalone it answers with its own guidance engine and an offline
coach. **In tandem with QRME** it hands the pulse itself to a specialist
synthetic profile, lets the person who asks reach one too (only if they say
so), and takes stacked concerns to the household's own QRME care team, which
writes a joint plan back. Patent pending (US 2025/0246290 A1). 409 routes,
131 tables, 3,371 tests, 45 screens, ten languages, three native shells and a
watch.

## The angle
A launch trailer for the handover: a guardian that watches one person, and a
city of specialists it can reach without ever letting go. Every crossing is a
choice, every crossing is on the record, and the emergency ladder never waits
on anybody. Green is the Guardian, violet is QRME; the video is the moment the
two colours touch.

## Hook (first 2-3 seconds)
**"A guardian for one person."** at full scale on the console's navy, then the
product's own four words under it: *monitor → predict → guide → escalate*.

## Key moments (the middle)
- **Watching.** The real *Live Monitoring* card: heart rate 110, respiration
  22, stress 0.8 typed in, **Send to Guardian** pressed; the detection lands
  as the code words it — *acute anxiety / panic · guidance · heart rate 110
  bpm (50 over resting)* — against the person's own band.
- **The handover.** The Guardian's message crosses to QRME word for word
  (`[Guardian monitoring] The user shows signs of acute anxiety / panic (heart
  rate 110 bpm (50 over resting)). Please offer brief, supportive guidance.`)
  with the readings riding along as biometrics; **Dr. Lena Whitcomb**, the
  QRME starter clinical psychologist, answers; the exchange seals into the
  vault under a `jim/…/tandem/…` key.
- **The person who asks.** The real Coach screen: *mental_health*, "I've been
  feeling stressed about work.", **Ask the coach**; the reply carries the offer
  verbatim — *a specialist covers this area. Nothing has been sent — asking
  them shares the message you just wrote with a profile outside JIM, and only
  happens if you say so.* — and the person presses **Ask them**.
- **The care team.** *Linked to a care team.* The stacking rule fires the goal
  the code composes — *heart_rate is drifting outside the personal band while
  medication adherence is slipping (metformin at 57% over the last week).
  Coordinate a gentle plan…* — and the joint plan lands back, sealed.
- **The scale.** 409 routes · 131 tables · 3,371 tests · 45 screens · 10
  languages, on the beat.

## Outro / punchline
Two spheres — the Guardian's and QRME's orb — and the wordmark **JIM-mini ✕
QRME**. Under it: *A guardian, in tandem.* and *Patent pending · US
2025/0246290 A1*. The bed fades.

## User flow worth showing
A reading arrives → the Guardian detects → the specialist answers on the pulse
→ the person brings their own words and chooses to ask → the care team writes
the plan. Entry → key action → result, and every surface exists at
`docs/screens/03`, `07`, `18`, `01`.

## Tone
- Preset: cinematic
- Creative direction: a launch trailer for the handover between two products
- Interpretation: short declarative lines, one claim per scene, full-bleed
  type; UI recreations large and clean; the two palettes meet on screen and
  the wire itself is a character. No jokes — consent lines are read straight.

## Format: landscape — 1920x1080
## Duration: 25 seconds

## Visual identity (from the project)
- Background: radial-gradient(120% 100% at 20% 0%, #10203a 0%, #0a1120 60%, #070b16 100%)
- Surface / card: #182238 (card2 #1f2b45), line #26314e, field #0c1424
- Text: #eef1f7; secondary #8a94ad; tertiary #626d88
- Accent: brand green #43e08a (brand2 #2fd27a), blue #3aa0ff, violet #a78bfa (QRME), amber #f7b731, red #ff4d5e
- Display font: the console's system stack (SF Pro Display / Segoe UI / Roboto) — rendered as Inter, heavy weight, tight tracking
- Body font: same; IBM Plex Mono for labels, keys and numbers
- Strongest visual element: the green primary button on a navy card; the violet
  edge that marks anything that came from QRME; the Overview's blue-violet
  sphere for the outro

## Share copy (draft)
JIM-mini. A personal health guardian for one person — and, in tandem with
QRME, a city of specialists it can reach without letting go. The pulse crosses
as biometrics, the person's own words cross only when they say so, and the
household's care team writes the plan back. Every crossing on the record.

## Audio direction
- Role: cinematic support — a confident bed under big type, accents matched to real UI motion
- Music: `happy-beats-business-moves-vol-11-by-ende-dot-app.mp3` (114.84 BPM)
- Music treatment: starts at 0 under the hook at a moderate level, holds through the UI scenes, fades over the last ~1.5s under the logo hold
- Music cue guidance: preset `assets/music/…vol-11….music-cues.json`; beat grid every ~0.525s from 1.60s; strong cues 1.60, 3.70, 5.80, 6.34, 8.96, 9.50, 12.65, 17.91, 22.65, 24.23. Locks: the detection lands on 5.80, the packet launches on 8.96 and the specialist card lands on 9.50, the coach scene cuts on 12.65, the joint plan lands on 17.91, the tiles ride 20.02 / 20.54 / 21.07 / 21.59 / 22.12, the wordmark slams on 22.65.
- Audio-reactive treatment: subtle; the green and violet glows breathe with RMS. No waveforms or bars.
- SFX posture: moderate, motion-matched, low high-frequency risk
- Audio-coupled moments: typed text (key ticks), the four button presses, the cards that land, the packet's landing, tiles on the grid, one bell on the wordmark
- Restraint rule: no sound on text that is merely fading in; nothing brighter than the bell; never more than one SFX per beat

## Storyboard

### Scene 1 — Hook — 3.2s (0.00–3.18)
Full-bleed navy. "A guardian for one person." rises in heavy type; under it,
smaller, in mono: monitor → predict → guide → escalate. Green rule above.
Sequential/interaction: none
Audio intent: the bed opens; nothing else
Music: bed starts at 0
Transition mood: dramatic → Scene 2

### Scene 2 — Watching — 4.7s (3.18–7.91)
The *Live Monitoring* card, large: "Submit a biometric sample", heart rate,
respiration, stress; a cursor types 110, 22, 0.8 and presses **Send to
Guardian** (green lights). On the strong cue at 5.80 the detection card lands
beneath: **acute anxiety / panic** · guidance · "heart rate 110 bpm (50 over
resting)" · your band 52–78 bpm. Headline left: "It learns what is normal for
you." Sub: "Drift raises a question. Collapse escalates. Never population
averages."
Sequential/interaction: yes — three typed fields, a click, a landing card
Audio intent: the product waking up
Audio-coupled idea: key ticks, one click, one card sound on the detection
Music: bed holds
Transition mood: clean → Scene 3

### Scene 3 — The handover — 4.7s (7.91–12.65)
Two cards. Left, green-edged, JIM: the message the code composes, word for
word, and three biometric chips (heart_rate 110 · respiration 22 · stress
0.8). A packet — `POST /profiles/{id}/chat · biometrics` — leaves the JIM card
on 8.96 along a dashed wire and lands on 9.50 as the right, violet-edged QRME
card arrives: Dr. Lena Whitcomb · clinical psychologist · ✦ AI, a short reply,
and the custody line `sealed · jim/u_7f3a/tandem/dr_lena_whitcomb/txc_91c2`.
Headline: "In tandem, the pulse itself reaches a specialist." Sub: "Over
public HTTP. Never imported. Sealed in the vault on the way back."
Sequential/interaction: yes — a packet crossing, a card landing, two reveals
Audio intent: the wire
Audio-coupled idea: a soft impact when the packet lands, a card sound on the QRME card
Music: bed holds
Transition mood: clean → Scene 4

### Scene 4 — The person who asks — 4.2s (12.65–16.86)
The real Coach card: Area *mental_health*, "What's on your mind?", the cursor
types "I've been feeling stressed about work." and presses **Ask the coach**.
The reply lands with the offer row verbatim: **Dr. Lena Whitcomb — clinical
psychologist**, "a specialist covers this area. Nothing has been sent — asking
them shares the message you just wrote with a profile outside JIM, and only
happens if you say so." and the button **Ask them**, which the cursor presses;
the row lights violet. Headline: "The person who asks reaches one too." Sub:
"An offer, not a send. Your words cross only when you press it."
Sequential/interaction: yes — typed text, two clicks, a reveal
Audio intent: consent, played straight
Audio-coupled idea: key ticks, two clicks, one card sound on the offer
Music: bed holds
Transition mood: clean → Scene 5

### Scene 5 — The care team — 3.2s (16.86–20.02)
"Linked to a care team." The goal card composes itself from the stacking rule
— heart_rate drifting while metformin adherence sits at 57% — and on 17.91 the
joint plan lands, violet-edged, with a line per desk and "sealed in the vault".
Headline: "When concerns stack, the whole care team writes the plan." Sub:
"Summaries cross, never raw readings. Once a day. Never on the emergency
path."
Sequential/interaction: yes — a goal, a landing plan
Audio intent: things clicking into place
Audio-coupled idea: one card sound on the plan
Music: bed holds
Transition mood: hard → Scene 6

### Scene 6 — The scale — 2.6s (20.02–22.65)
Five tiles on the beat grid: 409 routes · 131 tables · 3,371 tests · 45
screens · 10 languages. Foot: "Offline is enforced, not promised — one gate
every socket passes."
Sequential/interaction: yes — five tiles, one per beat
Audio intent: momentum
Audio-coupled idea: soft impacts on the grid
Music: bed at full presence
Transition mood: hard → Scene 7

### Scene 7 — Outro — 2.4s (22.65–25.00)
The Guardian's blue-violet sphere and QRME's orb; **JIM-mini ✕ QRME** slams on
22.65; "A guardian, in tandem."; the smallest line: "Patent pending · US
2025/0246290 A1". Hold; the bed fades.
Sequential/interaction: none
Audio intent: arrival
Audio-coupled idea: one bell on the wordmark; music fades over the final 1.5s
Music: fade out
Transition mood: hold to end

**Music mood for this video:** cinematic-confident (upbeat business bed played straight)
**Audio summary:** the bed opens under the hook, carries the reading, the wire, the ask and the plan with motion-matched clicks and card sounds, lands the tiles on the grid, and rings one bell on the wordmark before fading under the patent line.
