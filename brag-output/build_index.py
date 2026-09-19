#!/usr/bin/env python3
"""Emit brag-output/composition/index.html for the JIM-mini ✕ QRME brag.

One place computes every timestamp — the typed text, the clicks, the packet
crossing the wire, the beat-locked tiles, the SFX that ride them — so the HTML
and the sound agree. Re-run after any timing change: python3 build_index.py
"""
from __future__ import annotations

import functools
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).parent
COMP = HERE / "composition"
OUT = COMP / "index.html"
AUDIO = json.load(open(COMP / "assets/audio-data.json"))
MUSIC = "assets/music/happy-beats-business-moves-vol-11-by-ende-dot-app.mp3"

FPS = 30
TOTAL = 25.0

# ---- scene clock (vol-11: 114.84 BPM, beat grid every ~0.525s from 1.60) --
S1, S2, S3, S4, S5, S6, S7 = 0.0, 3.18, 7.91, 12.65, 16.86, 20.02, 22.65
DETECT_IN = 5.80            # strong cue — the detection lands
PACKET_GO = 8.96            # strong cue — the packet leaves JIM
PACKET_LAND = 9.50          # strong cue — the QRME card lands
PLAN_IN = 17.91             # strong cue — the joint plan lands
BEATS = [20.02, 20.54, 21.07, 21.59, 22.12]   # stat tiles     // beat-grid
LOGO_BEAT = 22.65                              # wordmark slam  // beat-locked

CHAR = 0.06   # seconds per typed character (numbers)
CHAR_T = 0.04  # seconds per typed character (the sentence)

# ---- typing schedule -----------------------------------------------------
TYPE_HR = ("110", S2 + 0.55, CHAR)
TYPE_RR = ("22", S2 + 1.05, CHAR)
TYPE_ST = ("0.8", S2 + 1.50, CHAR)
TYPE_ASK = ("I've been feeling stressed about work.", S4 + 0.50, CHAR_T)


def type_end(spec):
    text, start, per = spec
    return round(start + len(text) * per, 3)


# ---- sound schedule ------------------------------------------------------
sfx: list[tuple[float, str, float]] = []   # (time, path, volume)
KEYS = [f"assets/sfx/keyboard/keypress-00{i}.wav" for i in range(1, 7)]


def keys_for(spec, every=2):
    text, start, per = spec
    for i, ch in enumerate(text):
        if i % every == 0 and ch != " ":
            sfx.append((round(start + i * per, 3), KEYS[(i // every) % len(KEYS)], 0.32))


for spec in (TYPE_HR, TYPE_RR, TYPE_ST, TYPE_ASK):
    keys_for(spec)

CLICK_HR = S2 + 0.45
CLICK_RR = S2 + 0.95
CLICK_ST = S2 + 1.40
CLICK_SEND = S2 + 2.15
# DETECT_IN lands the detection card (5.80)

MSG_IN = S3 + 0.50
REPLY_IN = PACKET_LAND + 0.45
CUSTODY_IN = PACKET_LAND + 1.25

CLICK_ASK = type_end(TYPE_ASK) + 0.20
REPLY4_IN = CLICK_ASK + 0.30
CLICK_THEM = S4 + 3.35
SENT_IN = CLICK_THEM + 0.20

GOAL_IN = S5 + 0.40
# PLAN_IN lands the joint plan (17.91)

for t in (CLICK_HR, CLICK_RR, CLICK_ST):
    sfx.append((t, "assets/sfx/interface/click_003.ogg", 0.5))
sfx.append((CLICK_SEND, "assets/sfx/interface/click_002.ogg", 0.55))
sfx.append((DETECT_IN, "assets/sfx/casino/card-slide-1.ogg", 0.4))
sfx.append((PACKET_LAND, "assets/sfx/impact/impactSoft_medium_001.ogg", 0.5))
sfx.append((PACKET_LAND + 0.05, "assets/sfx/casino/card-slide-1.ogg", 0.3))
sfx.append((CLICK_ASK, "assets/sfx/interface/click_002.ogg", 0.55))
sfx.append((REPLY4_IN, "assets/sfx/casino/card-slide-1.ogg", 0.4))
sfx.append((CLICK_THEM, "assets/sfx/interface/click_002.ogg", 0.55))
sfx.append((GOAL_IN, "assets/sfx/casino/card-slide-1.ogg", 0.35))
sfx.append((PLAN_IN, "assets/sfx/impact/impactSoft_medium_002.ogg", 0.5))
sfx.append((S6, "assets/sfx/impact/impactSoft_medium_004.ogg", 0.5))
for i, t in enumerate(BEATS):
    if i == 0:
        continue  # S6 already carries the first hit
    sfx.append((t, f"assets/sfx/impact/impactSoft_medium_00{[1, 2, 4, 1, 2][i]}.ogg", 0.45))
sfx.append((LOGO_BEAT, "assets/sfx/impact/impactBell_heavy_000.ogg", 0.6))
sfx.sort()

# ---- audio-reactive data: rms per frame for the first TOTAL seconds -------
frames = AUDIO["frames"][: int(TOTAL * FPS) + 2]
RMS = [round(f["rms"], 3) for f in frames]


@functools.lru_cache(maxsize=None)
def media_len(path: str) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(COMP / path)], capture_output=True, text=True).stdout
    return round(float(out.strip() or 1.0), 3)


def audio_tags() -> str:
    tags = [
        f'<audio id="music" src="{MUSIC}"'
        f' data-start="0" data-duration="{TOTAL}" data-track-index="1" data-volume="0.55"'
        ' data-automation=\'{"version":1,"lanes":[{"target":"volume","points":['
        '{"t":0,"v":0},{"t":0.6,"v":0.55},{"t":23.4,"v":0.55},{"t":24.9,"v":0}]}]}\'></audio>'
    ]
    for i, (t, path, vol) in enumerate(sfx):
        tags.append(
            f'<audio id="sfx{i:02d}" src="{path}" data-start="{t}" data-duration="{media_len(path)}"'
            f' data-track-index="{2 + i % 6}" data-volume="{vol}"></audio>'
        )
    return "\n      ".join(tags)


TILE_LINES = "\n      ".join(
    f'tl.fromTo("#t{i+1}", {{ opacity: 0, y: 60, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "power4.out" }}, {t}); // beat-grid {t}s'
    for i, t in enumerate(BEATS))

GUARDIAN_MSG = ("[Guardian monitoring] The user shows signs of acute anxiety / panic "
                "(heart rate 110 bpm (50 over resting), respiratory rate 22/min). "
                "Please offer brief, supportive guidance.")
OFFER_NOTE = ("a specialist covers this area. Nothing has been sent — asking them shares the "
              "message you just wrote with a profile outside JIM, and only happens if you say so.")
GOAL = ("heart_rate is drifting outside the personal band while medication adherence is "
        "slipping (metformin at 57% over the last week). Coordinate a gentle plan: what each "
        "desk should do this week, and what to watch for.")

HTML = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>JIM-mini ✕ QRME — brag</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #0a1120; }}
      body {{ font-family: Inter, sans-serif; color: #eef1f7; -webkit-font-smoothing: antialiased; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden;
        background: radial-gradient(120% 100% at 20% 0%, #10203a 0%, #0a1120 60%, #070b16 100%); }}
      .mono {{ font-family: "IBM Plex Mono", monospace; }}

      /* ---- background: the console's navy, two glows breathing with the bed ---- */
      #bg {{ position: absolute; inset: 0; overflow: hidden; --pulse: 0; }}
      .glow {{ position: absolute; border-radius: 50%; will-change: transform, opacity; }}
      #glow1 {{ width: 1400px; height: 1400px; left: -320px; top: -720px;
        background: radial-gradient(circle, rgba(67,224,138,0.22) 0%, rgba(67,224,138,0) 62%);
        transform: scale(calc(1 + var(--pulse) * 0.16)); }}
      #glow2 {{ width: 1200px; height: 1200px; right: -420px; bottom: -600px;
        background: radial-gradient(circle, rgba(167,139,250,0.22) 0%, rgba(167,139,250,0) 62%);
        transform: scale(calc(1 + var(--pulse) * 0.12)); }}
      #grid {{ position: absolute; inset: 0; opacity: 0.14;
        background-image: linear-gradient(rgba(138,148,173,0.35) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(138,148,173,0.35) 1px, transparent 1px);
        background-size: 120px 120px; }}
      #ghost {{ position: absolute; left: 60px; bottom: -50px; font-size: 440px; font-weight: 800;
        letter-spacing: -0.06em; color: rgba(67,224,138,0.07); white-space: nowrap; }}

      .scene {{ position: absolute; inset: 0; overflow: hidden; will-change: transform, opacity, filter; }}
      #scene2, #scene3, #scene4, #scene5, #scene6, #scene7 {{ opacity: 0; }}

      .label {{ position: absolute; left: 120px; top: 96px; font-size: 22px; letter-spacing: 0.18em;
        color: #a6afc7; }}
      .label b {{ color: #f7b731; font-weight: 700; }}
      .rule {{ position: absolute; left: 120px; height: 4px; width: 220px; background: #43e08a;
        transform-origin: left center; }}
      .head {{ position: absolute; left: 120px; top: 300px; width: 800px; font-size: 76px; font-weight: 800;
        line-height: 1.02; letter-spacing: -0.035em; }}
      .sub {{ position: absolute; left: 124px; width: 760px; font-size: 36px; font-weight: 400;
        line-height: 1.32; color: #b9c0d4; }}

      /* ---- scene 1 ---- */
      #s1-head {{ position: absolute; left: 120px; top: 300px; width: 1600px; font-size: 156px;
        font-weight: 800; line-height: 0.98; letter-spacing: -0.045em; }}
      #s1-head span {{ display: inline-block; margin-right: 0.22em; }}
      #s1-sub {{ position: absolute; left: 124px; top: 700px; font-size: 40px; color: #b9c0d4;
        letter-spacing: 0.02em; }}
      #s1-sub em {{ font-style: normal; color: #43e08a; }}

      /* ---- shared card look (the console's cards, scaled for video) ---- */
      .card {{ position: absolute; background: #182238; border: 2px solid #26314e; border-radius: 26px;
        box-shadow: 0 30px 80px rgba(0,0,0,0.45); }}
      .card.jim {{ border-left: 8px solid #43e08a; }}
      .card.qrme {{ border-left: 8px solid #a78bfa; }}
      .card h3 {{ font-size: 38px; font-weight: 800; letter-spacing: -0.02em; }}
      .flabel {{ font-size: 24px; color: #8a94ad; margin: 0 0 10px; }}
      .field {{ position: relative; height: 84px; border-radius: 18px; background: #0c1424;
        border: 2px solid #26314e; padding: 0 26px; display: flex; align-items: center;
        font-size: 32px; color: #8a94ad; overflow: hidden; white-space: nowrap; }}
      .field .typed {{ color: #eef1f7; }}
      .caret {{ display: inline-block; width: 3px; height: 38px; background: #43e08a; margin-left: 4px;
        vertical-align: middle; opacity: 0; }}
      .btn {{ position: relative; overflow: hidden; height: 88px; border-radius: 20px; background: #1f2b45;
        border: 2px solid #2c3a5c; display: flex; align-items: center; justify-content: center;
        font-size: 32px; font-weight: 800; color: #eef1f7; }}
      .btn .lit {{ position: absolute; inset: 0; border-radius: 18px; background: #43e08a; opacity: 0; }}
      .btn.violet .lit {{ background: #a78bfa; }}
      .btn span {{ position: relative; }}
      .btn.primary {{ background: #43e08a; border-color: #43e08a; color: #07110c; }}
      .pill {{ position: absolute; height: 68px; padding: 0 30px; border-radius: 34px; background: #f7b731;
        color: #0c1424; font-size: 26px; font-weight: 800; display: flex; align-items: center;
        white-space: nowrap; opacity: 0; }}
      .pill.green {{ background: #43e08a; color: #07110c; }}
      .pill.violet {{ background: #a78bfa; color: #120b2a; }}

      /* ---- scene 2: watching ---- */
      #s2-card {{ left: 1000px; top: 130px; width: 800px; padding: 40px 44px 40px; }}
      #s2-card h3 {{ margin-bottom: 26px; }}
      .row2 {{ display: flex; gap: 24px; margin-bottom: 22px; }}
      .row2 > div {{ flex: 1; }}
      #s2-send {{ margin-top: 8px; width: 420px; }}
      #s2-det {{ left: 1000px; top: 660px; width: 800px; padding: 30px 40px 30px 36px; opacity: 0; }}
      #s2-det .kind {{ font-size: 30px; font-weight: 800; color: #f7b731; }}
      #s2-det .kind small {{ font-family: "IBM Plex Mono", monospace; font-size: 20px; color: #8a94ad;
        font-weight: 400; margin-left: 16px; letter-spacing: 0.08em; }}
      #s2-det .why {{ font-size: 26px; color: #eef1f7; margin-top: 10px; line-height: 1.35; }}
      #s2-det .band {{ font-family: "IBM Plex Mono", monospace; font-size: 22px; color: #8a94ad; margin-top: 12px; }}
      #s2-det .band b {{ color: #43e08a; font-weight: 700; }}
      #s2-head {{ top: 260px; }}
      #s2-sub {{ top: 520px; }}

      /* ---- scene 3: the handover ---- */
      #s3-head {{ top: 150px; width: 1700px; font-size: 72px; }}
      #s3-sub {{ top: 262px; width: 1500px; }}
      #s3-jim {{ left: 120px; top: 420px; width: 760px; height: 540px; padding: 34px 40px 34px 40px; }}
      #s3-qrme {{ left: 1040px; top: 420px; width: 760px; height: 540px; padding: 34px 40px 34px 40px; opacity: 0; }}
      .who {{ display: flex; align-items: center; gap: 22px; }}
      .who .tag {{ font-family: "IBM Plex Mono", monospace; font-size: 20px; letter-spacing: 0.16em;
        color: #8a94ad; }}
      .who .tag b {{ color: #43e08a; font-weight: 700; }}
      #s3-qrme .who .tag b {{ color: #a78bfa; }}
      #s3-msg {{ font-size: 25px; line-height: 1.45; color: #eef1f7; margin-top: 22px; opacity: 0; }}
      #s3-msg i {{ font-style: normal; color: #8a94ad; }}
      .chips {{ display: flex; gap: 14px; margin-top: 26px; flex-wrap: wrap; }}
      .chip {{ font-family: "IBM Plex Mono", monospace; font-size: 21px; padding: 10px 16px; border-radius: 14px;
        background: #0c1424; border: 1px solid #26314e; color: #b9c0d4; opacity: 0; }}
      .chip b {{ color: #43e08a; font-weight: 700; }}
      #s3-wire {{ position: absolute; left: 884px; top: 690px; width: 152px; height: 4px;
        background: repeating-linear-gradient(90deg, #3a4a70 0 12px, transparent 12px 22px); }}
      #s3-wirelit {{ position: absolute; left: 884px; top: 690px; width: 152px; height: 4px;
        background: linear-gradient(90deg, #43e08a, #a78bfa); transform-origin: left center; opacity: 0; }}
      #s3-packet {{ position: absolute; left: 700px; top: 646px; height: 52px; padding: 0 20px; border-radius: 26px;
        background: #0c1424; border: 2px solid #43e08a; color: #eef1f7; font-family: "IBM Plex Mono", monospace;
        font-size: 19px; display: flex; align-items: center; white-space: nowrap; opacity: 0; z-index: 5;
        box-shadow: 0 0 30px rgba(67,224,138,0.35); }}
      #s3-packet b {{ color: #43e08a; font-weight: 700; margin-right: 12px; }}
      #s3-spec {{ display: flex; align-items: center; gap: 22px; margin-top: 22px; }}
      #s3-face {{ width: 108px; height: 108px; border-radius: 22px; border: 2px solid #26314e; flex: 0 0 108px;
        object-fit: cover; background: #0c1424; }}
      #s3-spec h4 {{ font-size: 32px; font-weight: 800; letter-spacing: -0.02em; }}
      #s3-spec p {{ font-size: 23px; color: #8a94ad; margin-top: 6px; }}
      #s3-spec p b {{ color: #a78bfa; font-weight: 700; }}
      #s3-reply {{ font-size: 25px; line-height: 1.45; color: #eef1f7; margin-top: 22px; opacity: 0; }}
      #s3-custody {{ font-family: "IBM Plex Mono", monospace; font-size: 20px; color: #8a94ad; margin-top: 22px;
        opacity: 0; line-height: 1.5; }}
      #s3-custody b {{ color: #43e08a; font-weight: 700; }}

      /* ---- scene 4: the person who asks ---- */
      #s4-card {{ left: 1000px; top: 110px; width: 800px; padding: 36px 44px 36px; }}
      #s4-card h3 {{ margin-bottom: 20px; }}
      #s4-area {{ margin-bottom: 18px; height: 78px; font-size: 30px; color: #eef1f7; justify-content: space-between; }}
      #s4-area small {{ font-size: 22px; color: #8a94ad; }}
      #s4-box {{ height: 150px; align-items: flex-start; padding-top: 20px; white-space: normal; font-size: 30px; }}
      #s4-ask {{ margin-top: 20px; width: 320px; height: 80px; font-size: 30px; }}
      #s4-offer {{ margin-top: 22px; padding: 22px 24px; border-radius: 20px; background: #0c1424;
        border: 2px solid #26314e; display: flex; align-items: center; gap: 22px; opacity: 0; position: relative;
        overflow: hidden; }}
      #s4-offer .olit {{ position: absolute; inset: 0; background: rgba(167,139,250,0.16); opacity: 0; }}
      #s4-offer > div {{ position: relative; flex: 1; }}
      #s4-offer b {{ font-size: 25px; font-weight: 800; display: block; }}
      #s4-offer p {{ font-size: 19px; line-height: 1.4; color: #8a94ad; margin-top: 6px; }}
      #s4-them {{ position: relative; flex: 0 0 180px; height: 74px; font-size: 26px; }}
      #s4-sent {{ left: 1000px; top: 972px; }}
      #s4-head {{ top: 260px; }}
      #s4-sub {{ top: 500px; }}

      /* ---- scene 5: the care team ---- */
      #s5-head {{ top: 220px; font-size: 68px; }}
      #s5-sub {{ top: 520px; }}
      #s5-status {{ position: absolute; left: 1000px; top: 130px; display: flex; align-items: center; gap: 16px;
        font-size: 30px; font-weight: 700; color: #eef1f7; opacity: 0; }}
      #s5-status i {{ width: 18px; height: 18px; border-radius: 50%; background: #43e08a; display: inline-block; }}
      #s5-goal {{ left: 1000px; top: 200px; width: 800px; padding: 28px 36px 28px 34px; opacity: 0; }}
      #s5-goal .tag, #s5-plan .tag {{ font-family: "IBM Plex Mono", monospace; font-size: 19px; letter-spacing: 0.16em;
        color: #8a94ad; margin-bottom: 12px; }}
      #s5-goal .tag b {{ color: #43e08a; font-weight: 700; }}
      #s5-plan .tag b {{ color: #a78bfa; font-weight: 700; }}
      #s5-goal p {{ font-size: 24px; line-height: 1.45; color: #eef1f7; }}
      #s5-plan {{ left: 1000px; top: 520px; width: 800px; padding: 28px 36px 28px 34px; opacity: 0; }}
      #s5-plan h4 {{ font-size: 30px; font-weight: 800; margin-bottom: 14px; }}
      #s5-plan li {{ list-style: none; font-size: 23px; line-height: 1.4; color: #eef1f7; padding: 8px 0;
        border-top: 1px solid #26314e; }}
      #s5-plan li b {{ color: #a78bfa; font-weight: 700; margin-right: 10px; }}
      #s5-plan .sealed {{ font-family: "IBM Plex Mono", monospace; font-size: 20px; color: #43e08a; margin-top: 14px; }}

      /* ---- scene 6: the scale ---- */
      #s6-label {{ top: 260px; }}
      .tile {{ position: absolute; top: 380px; width: 320px; height: 300px; border-radius: 26px; background: #182238;
        border: 2px solid #26314e; padding: 34px 30px; opacity: 0; }}
      .tile b {{ display: block; font-size: 86px; font-weight: 800; letter-spacing: -0.05em; line-height: 1;
        font-variant-numeric: tabular-nums; }}
      .tile span {{ display: block; margin-top: 22px; font-family: "IBM Plex Mono", monospace; font-size: 26px;
        color: #b9c0d4; }}
      #t1 {{ left: 120px; }} #t2 {{ left: 460px; }} #t3 {{ left: 800px; }} #t4 {{ left: 1140px; }} #t5 {{ left: 1480px; }}
      #s6-foot {{ position: absolute; left: 120px; top: 760px; width: 1700px; font-size: 42px; font-weight: 700;
        line-height: 1.3; color: #b9c0d4; opacity: 0; }}
      #s6-foot em {{ font-style: normal; color: #eef1f7; }}

      /* ---- scene 7: outro ---- */
      #orb-jim {{ position: absolute; left: 420px; top: 400px; width: 220px; height: 220px; border-radius: 50%;
        background: radial-gradient(circle at 32% 28%, #cfe3ff 0%, #a78bfa 35%, #3aa0ff 70%, #143a8a 100%);
        box-shadow: 0 0 120px rgba(58,160,255,0.5); opacity: 0; }}
      #orb-qrme {{ position: absolute; left: 600px; top: 440px; width: 180px; height: 180px; border-radius: 50%;
        background: radial-gradient(circle at 32% 28%, #cfc2ff 0%, #9d7bff 38%, #4a35c7 75%, #2a1f6e 100%);
        box-shadow: 0 0 100px rgba(123,92,255,0.55); opacity: 0; }}
      #wordmark {{ position: absolute; left: 840px; top: 392px; font-size: 112px; font-weight: 800;
        letter-spacing: -0.05em; line-height: 1; opacity: 0; white-space: nowrap; }}
      #wordmark em {{ font-style: normal; color: #43e08a; }}
      #wordmark i {{ font-style: normal; color: #626d88; font-weight: 400; margin: 0 22px; font-size: 76px;
        vertical-align: middle; }}
      #wordmark u {{ text-decoration: none; color: #a78bfa; }}
      #s7-tag {{ position: absolute; left: 846px; top: 540px; font-size: 44px; font-weight: 700; color: #b9c0d4;
        opacity: 0; }}
      #s7-patent {{ position: absolute; left: 846px; top: 620px; font-size: 22px; letter-spacing: 0.12em;
        color: #8a94ad; opacity: 0; }}

      /* ---- overlays ---- */
      #cursor {{ position: absolute; left: 0; top: 0; width: 40px; height: 48px; opacity: 0; z-index: 40;
        filter: drop-shadow(0 6px 10px rgba(0,0,0,0.6)); }}
      #flash {{ position: absolute; inset: 0; background: #43e08a; opacity: 0; z-index: 50; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="{TOTAL}">
      <div id="bg" data-layout-ignore>
        <div id="glow1" class="glow"></div>
        <div id="glow2" class="glow"></div>
        <div id="grid"></div>
        <div id="ghost">JIM</div>
      </div>

      <!-- scene 1: the hook -->
      <div id="scene1" class="scene">
        <div class="label mono" id="s1-label">JIM-MINI · <b>3.4.0</b> · GUARDIAN</div>
        <div class="rule" id="s1-rule" style="top: 260px"></div>
        <h1 id="s1-head"><span>A</span><span>guardian</span><span>for</span><span>one</span><span>person.</span></h1>
        <p id="s1-sub" class="mono">monitor <em>→</em> predict <em>→</em> guide <em>→</em> escalate</p>
      </div>

      <!-- scene 2: watching -->
      <div id="scene2" class="scene">
        <div class="label mono" id="s2-label">LIVE MONITORING · <b>01</b> · DETECT → GUIDE → ESCALATE</div>
        <h2 class="head" id="s2-head">It learns what is normal for you.</h2>
        <p class="sub" id="s2-sub">Drift raises a question. Collapse escalates. Never population averages.</p>
        <div class="card jim" id="s2-card">
          <h3>Submit a biometric sample</h3>
          <div class="row2">
            <div><div class="flabel">Heart rate (bpm)</div>
              <div class="field" id="s2-f1"><span class="typed" id="s2-t1"></span><span class="ph" id="s2-p1">—</span><span class="caret" id="s2-c1"></span></div></div>
            <div><div class="flabel">Respiration (/min)</div>
              <div class="field" id="s2-f2"><span class="typed" id="s2-t2"></span><span class="ph" id="s2-p2">—</span><span class="caret" id="s2-c2"></span></div></div>
          </div>
          <div class="flabel">Stress (0–1)</div>
          <div class="field" id="s2-f3"><span class="typed" id="s2-t3"></span><span class="ph" id="s2-p3">—</span><span class="caret" id="s2-c3"></span></div>
          <div class="btn" id="s2-send"><div class="lit" id="s2-lit"></div><span>Send to Guardian</span></div>
        </div>
        <div class="card jim" id="s2-det">
          <div class="kind">acute anxiety / panic<small>GUIDANCE</small></div>
          <div class="why">heart rate 110 bpm (50 over resting), respiratory rate 22/min</div>
          <div class="band">your band <b>52–78 bpm</b> · learned from your own calm samples</div>
        </div>
      </div>

      <!-- scene 3: the handover -->
      <div id="scene3" class="scene">
        <div class="label mono" id="s3-label">THE TANDEM · <b>02</b> · GUARDIAN → QRME</div>
        <h2 class="head" id="s3-head">In tandem, the pulse itself reaches a specialist.</h2>
        <p class="sub" id="s3-sub">Over public HTTP. Never imported. Sealed in the vault on the way back.</p>
        <div class="card jim" id="s3-jim">
          <div class="who"><div class="tag"><b>JIM-MINI</b> · guardian._deliver</div></div>
          <div id="s3-msg"><i>message</i> &nbsp;{GUARDIAN_MSG}</div>
          <div class="chips">
            <div class="chip" id="chip1"><b>heart_rate</b> 110</div>
            <div class="chip" id="chip2"><b>respiratory_rate</b> 22</div>
            <div class="chip" id="chip3"><b>stress</b> 0.8</div>
            <div class="chip" id="chip4"><b>biometrics</b> the readings that triggered it</div>
          </div>
        </div>
        <div id="s3-wire"></div>
        <div id="s3-wirelit"></div>
        <div id="s3-packet"><b>POST</b>/profiles/{{id}}/chat · biometrics</div>
        <div class="card qrme" id="s3-qrme">
          <div class="who"><div class="tag"><b>QRME</b> · specialist profile</div></div>
          <div id="s3-spec">
            <img id="s3-face" src="assets/portraits/dr_lena_whitcomb.webp" alt="" />
            <div><h4>Dr. Lena Whitcomb</h4><p>clinical psychologist · <b>✦ AI</b> · persona, moderation, memory — QRME's own</p></div>
          </div>
          <div id="s3-reply">Your heart has been running fast for a while now. Let's slow the breath before anything else: in for four, out for six, three times. I'm here while you do it.</div>
          <div id="s3-custody"><b>sealed</b> · jim/u_7f3a/tandem/dr_lena_whitcomb/txc_91c2 · AES-256-GCM · hash-chained</div>
        </div>
      </div>

      <!-- scene 4: the person who asks -->
      <div id="scene4" class="scene">
        <div class="label mono" id="s4-label">COACH · <b>03</b> · THE PERSON WHO ASKS</div>
        <h2 class="head" id="s4-head">The person who asks reaches one too.</h2>
        <p class="sub" id="s4-sub">An offer, not a send. Your words cross only when you press it.</p>
        <div class="card jim" id="s4-card">
          <h3>Coach</h3>
          <div class="flabel">Area</div>
          <div class="field" id="s4-area"><span>mental_health</span><small>▾</small></div>
          <div class="flabel">What's on your mind?</div>
          <div class="field" id="s4-box"><span class="typed" id="s4-t1"></span><span class="ph" id="s4-p1"></span><span class="caret" id="s4-c1"></span></div>
          <div class="btn primary" id="s4-ask"><span>Ask the coach</span></div>
          <div id="s4-offer">
            <div class="olit" id="s4-olit"></div>
            <div><b>Dr. Lena Whitcomb — clinical psychologist</b><p>{OFFER_NOTE}</p></div>
            <div class="btn violet" id="s4-them"><div class="lit" id="s4-tlit"></div><span>Ask them</span></div>
          </div>
        </div>
        <div class="pill violet" id="s4-sent">Sent · your words, your choice · answered in the same thread</div>
      </div>

      <!-- scene 5: the care team -->
      <div id="scene5" class="scene">
        <div class="label mono" id="s5-label">CARE TEAM · <b>04</b> · YOUR OWN QRME ORGANIZATION</div>
        <h2 class="head" id="s5-head">When concerns stack, the whole care team writes the plan.</h2>
        <p class="sub" id="s5-sub">Summaries cross, never raw readings. Once a day. Never on the emergency path.</p>
        <div id="s5-status"><i></i>Linked to a care team.</div>
        <div class="card jim" id="s5-goal">
          <div class="tag"><b>GOAL</b> · drift + adherence below 75%</div>
          <p>{GOAL}</p>
        </div>
        <div class="card qrme" id="s5-plan">
          <div class="tag"><b>JOINT PLAN</b> · POST /organizations/{{id}}/coordinate</div>
          <h4>What each desk does this week</h4>
          <ul>
            <li><b>Meds desk</b>evening dose moved beside the kettle; a two-day check-in</li>
            <li><b>Mental-health desk</b>a short walk after the dose, not a lecture about it</li>
            <li><b>Guardian desk</b>watch the band for four calm evenings before saying more</li>
          </ul>
          <div class="sealed">✓ sealed in the vault · GET /users/{{id}}/care-team/plans</div>
        </div>
      </div>

      <!-- scene 6: the scale -->
      <div id="scene6" class="scene">
        <div class="label mono" id="s6-label">SHIPPED · <b>05</b> · RELEASE 3.4.0</div>
        <div class="tile" id="t1"><b>409</b><span>routes</span></div>
        <div class="tile" id="t2"><b>131</b><span>tables</span></div>
        <div class="tile" id="t3"><b>3,371</b><span>tests</span></div>
        <div class="tile" id="t4"><b>45</b><span>screens</span></div>
        <div class="tile" id="t5"><b>10</b><span>languages</span></div>
        <p id="s6-foot">Offline is enforced, not promised — <em>one gate every socket passes,</em> and the ladder never waits on anybody.</p>
      </div>

      <!-- scene 7: outro -->
      <div id="scene7" class="scene">
        <div id="orb-jim"></div>
        <div id="orb-qrme"></div>
        <div id="wordmark">JIM<em>-mini</em><i>✕</i><u>QRME</u></div>
        <div id="s7-tag">A guardian, in tandem.</div>
        <div id="s7-patent" class="mono">PATENT PENDING · US 2025/0246290 A1</div>
      </div>

      <svg id="cursor" viewBox="0 0 40 48" aria-hidden="true">
        <path d="M4 2 L36 26 L21 28 L30 44 L23 47 L15 31 L4 42 Z" fill="#eef1f7" stroke="#0c1424" stroke-width="2.5" stroke-linejoin="round"/>
      </svg>
      <div id="flash" data-layout-ignore></div>

      {audio_tags()}
    </div>

    <script>
      const RMS = {json.dumps(RMS)};
      const FPS = {FPS};
      const T = {{ s2: {S2}, s3: {S3}, s4: {S4}, s5: {S5}, s6: {S6}, s7: {S7}, total: {TOTAL} }};

      const $ = (id) => document.getElementById(id);
      const tl = gsap.timeline({{ paused: true }});

      // ---- global clock: audio-reactive glow + carets, a pure function of time ----
      const clock = {{ t: 0 }};
      const bg = $("bg");
      const carets = ["s2-c1", "s2-c2", "s2-c3", "s4-c1"].map($);
      tl.fromTo(clock, {{ t: 0 }}, {{ t: T.total, duration: T.total, ease: "none",
        onUpdate() {{
          const f = Math.min(RMS.length - 1, Math.max(0, Math.floor(clock.t * FPS)));
          bg.style.setProperty("--pulse", RMS[f].toFixed(3));
          const on = (clock.t % 1.0) < 0.5 ? 1 : 0;
          for (const c of carets) c.style.opacity = c.dataset.live === "1" ? on : 0;
        }} }}, 0);

      // ---- typing, seek-safe: the visible slice is a function of the tween value ----
      function typeInto(fieldId, typedId, phId, caretId, text, start, per, color) {{
        const p = {{ n: 0 }};
        const typed = $(typedId), ph = $(phId), caret = $(caretId), field = $(fieldId);
        const dur = text.length * per;
        tl.fromTo(p, {{ n: 0 }}, {{ n: text.length, duration: dur, ease: "none",
          onUpdate() {{
            const k = Math.round(p.n);
            typed.textContent = text.slice(0, k);
            ph.style.opacity = k === 0 ? 1 : 0;
          }} }}, start);
        tl.set(field, {{ borderColor: color }}, start - 0.1);
        tl.set(caret, {{ attr: {{ "data-live": "1" }} }}, start - 0.1);
        tl.set(caret, {{ attr: {{ "data-live": "0" }} }}, start + dur + 0.5);
        tl.set(field, {{ borderColor: "#26314e" }}, start + dur + 0.5);
      }}

      // ---- cursor: move, then a small press ----
      const cur = $("cursor");
      function moveCursor(x, y, at, dur) {{
        tl.to(cur, {{ x, y, duration: dur, ease: "power2.inOut" }}, at);
      }}
      function press(at) {{
        tl.fromTo(cur, {{ scale: 1 }}, {{ scale: 0.82, duration: 0.08, ease: "power2.in", immediateRender: false }}, at);
        tl.to(cur, {{ scale: 1, duration: 0.12, ease: "power2.out" }}, at + 0.08);
      }}
      function light(litId, at) {{
        tl.fromTo($(litId), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.18, ease: "power2.out" }}, at);
      }}
      function fadeUp(sel, at, dur = 0.5, y = 24) {{
        tl.fromTo(sel, {{ opacity: 0, y }}, {{ opacity: 1, y: 0, duration: dur, ease: "power3.out" }}, at);
      }}
      function landCard(sel, at) {{
        tl.fromTo(sel, {{ opacity: 0, y: 40, scale: 0.97 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "power4.out" }}, at);
      }}
      function blurCross(outSel, inSel, at) {{
        tl.to(outSel, {{ filter: "blur(10px)", scale: 1.03, opacity: 0, duration: 0.5, ease: "power2.inOut" }}, at);
        tl.fromTo(inSel, {{ filter: "blur(10px)", scale: 0.97, opacity: 0 }},
          {{ filter: "blur(0px)", scale: 1, opacity: 1, duration: 0.5, ease: "power2.inOut" }}, at + 0.1);
      }}

      // =====================================================================
      // scene 1 — hook (0 → {S2})
      // =====================================================================
      fadeUp("#s1-label", 0.1, 0.5, -16);
      tl.fromTo("#s1-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power3.out" }}, 0.15);
      tl.fromTo("#s1-head span", {{ y: 90, opacity: 0, rotation: 2 }},
        {{ y: 0, opacity: 1, rotation: 0, duration: 0.7, ease: "power4.out", stagger: 0.08 }}, 0.2);
      fadeUp("#s1-sub", 1.2, 0.6);
      tl.fromTo("#s1-head", {{ scale: 1 }}, {{ scale: 1.03, duration: 2.9, ease: "none" }}, 0.2);

      // transition 1 — zoom through (dramatic)
      tl.to("#scene1", {{ scale: 2.2, opacity: 0, filter: "blur(10px)", duration: 0.45, ease: "power3.in" }}, T.s2);
      tl.fromTo("#scene2", {{ scale: 0.72, opacity: 0, filter: "blur(10px)" }},
        {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.5, ease: "power3.out" }}, T.s2 + 0.12);

      // =====================================================================
      // scene 2 — watching ({S2} → {S3})
      // =====================================================================
      fadeUp("#s2-label", T.s2 + 0.25, 0.5, -16);
      tl.fromTo("#s2-head", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.7, ease: "power4.out" }}, T.s2 + 0.2);
      fadeUp("#s2-sub", T.s2 + 0.45, 0.6);
      tl.fromTo("#s2-card", {{ opacity: 0, x: 90, rotation: 1.5 }}, {{ opacity: 1, x: 0, rotation: 0, duration: 0.7, ease: "power4.out" }}, T.s2 + 0.15);

      tl.fromTo(cur, {{ x: 1300, y: 640, opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, T.s2 + 0.25);
      moveCursor(1180, 318, T.s2 + 0.25, 0.22);
      press({CLICK_HR});
      typeInto("s2-f1", "s2-t1", "s2-p1", "s2-c1", {json.dumps(TYPE_HR[0])}, {TYPE_HR[1]}, {CHAR}, "#43e08a");
      moveCursor(1560, 318, {CLICK_RR} - 0.22, 0.2);
      press({CLICK_RR});
      typeInto("s2-f2", "s2-t2", "s2-p2", "s2-c2", {json.dumps(TYPE_RR[0])}, {TYPE_RR[1]}, {CHAR}, "#43e08a");
      moveCursor(1180, 468, {CLICK_ST} - 0.24, 0.22);
      press({CLICK_ST});
      typeInto("s2-f3", "s2-t3", "s2-p3", "s2-c3", {json.dumps(TYPE_ST[0])}, {TYPE_ST[1]}, {CHAR}, "#43e08a");
      moveCursor(1250, 590, {CLICK_SEND} - 0.3, 0.28);
      press({CLICK_SEND});
      light("s2-lit", {CLICK_SEND});
      tl.set("#s2-send span", {{ color: "#07110c" }}, {CLICK_SEND} + 0.05);
      landCard("#s2-det", {DETECT_IN}); // beat-locked {DETECT_IN}s
      tl.to(cur, {{ opacity: 0, duration: 0.2 }}, T.s3 - 0.3);

      // transition 2 — blur crossfade
      blurCross("#scene2", "#scene3", T.s3);

      // =====================================================================
      // scene 3 — the handover ({S3} → {S4})
      // =====================================================================
      fadeUp("#s3-label", T.s3 + 0.25, 0.5, -16);
      tl.fromTo("#s3-head", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.7, ease: "power4.out" }}, T.s3 + 0.2);
      fadeUp("#s3-sub", T.s3 + 0.45, 0.6);
      tl.fromTo("#s3-jim", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.6, ease: "power4.out" }}, T.s3 + 0.15);
      fadeUp("#s3-msg", {MSG_IN}, 0.45, 14);
      tl.fromTo(".chip", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out", stagger: 0.08 }}, {MSG_IN} + 0.35);
      // the packet: leaves JIM on the strong cue, lands as the QRME card arrives
      tl.fromTo("#s3-packet", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.14, ease: "power2.out" }}, {PACKET_GO} - 0.15);
      tl.to("#s3-packet", {{ x: 460, duration: {PACKET_LAND} - {PACKET_GO}, ease: "power2.inOut" }}, {PACKET_GO}); // beat-locked {PACKET_GO}s
      tl.fromTo("#s3-wirelit", {{ scaleX: 0, opacity: 0 }}, {{ scaleX: 1, opacity: 1, duration: {PACKET_LAND} - {PACKET_GO}, ease: "power2.inOut" }}, {PACKET_GO});
      tl.to("#s3-packet", {{ opacity: 0, scale: 0.8, duration: 0.2, ease: "power2.in" }}, {PACKET_LAND});
      tl.fromTo("#s3-qrme", {{ opacity: 0, x: 60, scale: 0.97 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.5, ease: "power4.out" }}, {PACKET_LAND}); // beat-locked {PACKET_LAND}s
      fadeUp("#s3-reply", {REPLY_IN}, 0.5, 14);
      fadeUp("#s3-custody", {CUSTODY_IN}, 0.45, 10);

      // transition 3 — blur crossfade on the strong cue
      blurCross("#scene3", "#scene4", T.s4);

      // =====================================================================
      // scene 4 — the person who asks ({S4} → {S5})
      // =====================================================================
      fadeUp("#s4-label", T.s4 + 0.25, 0.5, -16);
      tl.fromTo("#s4-head", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.7, ease: "power4.out" }}, T.s4 + 0.2);
      fadeUp("#s4-sub", T.s4 + 0.45, 0.6);
      tl.fromTo("#s4-card", {{ opacity: 0, x: 90, rotation: 1.5 }}, {{ opacity: 1, x: 0, rotation: 0, duration: 0.7, ease: "power4.out" }}, T.s4 + 0.15);
      tl.fromTo(cur, {{ x: 1300, y: 760, opacity: 0 }}, {{ opacity: 1, duration: 0.2, immediateRender: false }}, T.s4 + 0.25);
      moveCursor(1200, 420, T.s4 + 0.25, 0.22);
      press({TYPE_ASK[1]} - 0.08);
      typeInto("s4-box", "s4-t1", "s4-p1", "s4-c1", {json.dumps(TYPE_ASK[0])}, {TYPE_ASK[1]}, {CHAR_T}, "#43e08a");
      moveCursor(1190, 600, {CLICK_ASK} - 0.26, 0.24);
      press({CLICK_ASK});
      tl.fromTo("#s4-ask", {{ scale: 1 }}, {{ scale: 0.97, duration: 0.08, yoyo: true, repeat: 1, ease: "power2.inOut" }}, {CLICK_ASK});
      landCard("#s4-offer", {REPLY4_IN});
      moveCursor(1640, 728, {CLICK_THEM} - 0.34, 0.32);
      press({CLICK_THEM});
      light("s4-tlit", {CLICK_THEM});
      tl.set("#s4-them span", {{ color: "#120b2a" }}, {CLICK_THEM} + 0.05);
      light("s4-olit", {CLICK_THEM} + 0.05);
      fadeUp("#s4-sent", {SENT_IN}, 0.45, 20);
      tl.to(cur, {{ opacity: 0, duration: 0.2 }}, T.s5 - 0.3);

      // transition 4 — blur crossfade
      blurCross("#scene4", "#scene5", T.s5);

      // =====================================================================
      // scene 5 — the care team ({S5} → {S6})
      // =====================================================================
      fadeUp("#s5-label", T.s5 + 0.25, 0.5, -16);
      tl.fromTo("#s5-head", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.7, ease: "power4.out" }}, T.s5 + 0.2);
      fadeUp("#s5-sub", T.s5 + 0.45, 0.6);
      fadeUp("#s5-status", T.s5 + 0.2, 0.4, 10);
      landCard("#s5-goal", {GOAL_IN});
      landCard("#s5-plan", {PLAN_IN}); // beat-locked {PLAN_IN}s

      // transition 5 — hard cut with a green flash, on the beat
      tl.set("#scene5", {{ opacity: 0 }}, T.s6);
      tl.set("#scene6", {{ opacity: 1 }}, T.s6);
      tl.fromTo("#flash", {{ opacity: 0 }}, {{ opacity: 0.45, duration: 0.05, ease: "none" }}, T.s6);
      tl.to("#flash", {{ opacity: 0, duration: 0.3, ease: "power2.out" }}, T.s6 + 0.05);

      // =====================================================================
      // scene 6 — the scale ({S6} → {S7}), tiles on the beat grid
      // =====================================================================
      fadeUp("#s6-label", T.s6 + 0.05, 0.4, -16);
      {TILE_LINES}
      fadeUp("#s6-foot", {BEATS[-1]} + 0.25, 0.45, 20);

      // transition 6 — zoom through into the outro
      tl.to("#scene6", {{ scale: 1.6, opacity: 0, filter: "blur(8px)", duration: 0.4, ease: "power3.in" }}, T.s7 - 0.1);
      tl.fromTo("#scene7", {{ scale: 0.8, opacity: 0, filter: "blur(8px)" }},
        {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.45, ease: "power3.out" }}, T.s7 - 0.05);

      // =====================================================================
      // scene 7 — outro ({S7} → {TOTAL})
      // =====================================================================
      tl.fromTo("#orb-jim", {{ opacity: 0, y: 60, scale: 0.7 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "power3.out" }}, T.s7);
      tl.fromTo("#orb-qrme", {{ opacity: 0, y: 60, scale: 0.7 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "power3.out" }}, T.s7 + 0.1);
      tl.fromTo("#wordmark", {{ opacity: 0, scale: 1.45 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "power4.out" }}, {LOGO_BEAT} - 0.06); // beat-locked {LOGO_BEAT}s
      fadeUp("#s7-tag", {LOGO_BEAT} + 0.4, 0.4, 18);
      tl.fromTo("#s7-patent", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {LOGO_BEAT} + 0.75);
      tl.fromTo("#orb-jim", {{ y: 0 }}, {{ y: -10, duration: 1.2, ease: "sine.inOut", immediateRender: false }}, T.s7 + 0.8);
      tl.fromTo("#orb-qrme", {{ y: 0 }}, {{ y: 8, duration: 1.2, ease: "sine.inOut", immediateRender: false }}, T.s7 + 0.8);

      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""

OUT.write_text(HTML, encoding="utf-8")
print(f"wrote {OUT} ({len(HTML)} bytes); {len(sfx)} sfx; rms frames {len(RMS)}")
print("typing ends:", type_end(TYPE_HR), type_end(TYPE_RR), type_end(TYPE_ST), type_end(TYPE_ASK),
      "| click ask", CLICK_ASK, "| ask them", CLICK_THEM)
