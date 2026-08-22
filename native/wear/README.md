# JIM on the wrist — a Wear OS app

    asked     do the watch screens look right
    mattered  is there a watch

The console has thirty-six watch faces drawn at wrist size, and the iPhone
app has a `WatchCard`. Neither is a watch. A field report said so plainly —
nothing on a wrist could reach the Guardian, because there was no watch
target at all — and this directory is the answer to it.

This is a **standalone Wear OS 3 app**. It talks to the deployment itself
over the network, which is the case the whole surface exists for: the phone
is in another room, or in a bag, or flat, and the person is still wearing
the thing that knows their pulse.

## What is on it

Four things, and one of them is an apology.

| Screen        | What it does |
| ------------- | ------------ |
| Sign in       | Deployment, email, password — every field dictated. |
| Read my pulse | Health Services → `POST /monitor/{uid}` with `monitor: wrist`. |
| Say something | On-device speech → `POST /users/{uid}/mic/heard` as **words**. |
| How am I      | `POST /companion/{uid}` — the coach reaching out first. |
| Get help now  | `POST /emergency/{uid}`. |

Nothing else. A watch is a surface with about four things on it, and a wrist
that could reach the billing screen would be a worse product, not a more
complete one.

## Three decisions worth knowing about

**Words, never audio.** The watch recognises the speech itself and hands in
text. `jim/mic.py:heard` takes either, and words are the better half of that
choice: nothing but text ever leaves the wrist, and it works on a deployment
with no transcription key at all. It also keeps the privacy promise short
enough to fit on a 45mm screen, which is the only length at which a privacy
promise is one anybody actually has.

**The pulse names its monitor.** `POST /monitor/{uid}` now accepts an
optional `monitor` field. Without it, `monitors.roster` had no way to know a
reading had arrived, so a watch reporting every minute left the wrist row
reading `waiting` — the same lie the roster had just been fixed for, facing
the other way. Naming the row does not gate the reading: the vitals ladder is
not the monitor roster, and a dangerous rate escalates whether or not a
switch on a settings screen is on.

**The watch signs in; it cannot sign anybody up.** A birthdate typed on four
millimetres of glass is a birthdate somebody gave up on, so there is no
enrollment here — the same email and password as every other surface, through
`POST /signin`, which mints the watch its own session token. Signing the watch
out does not sign the phone out.

Every field opens Wear's own input screen, which takes **dictation** as well
as typing. That is the difference between awkward and impossible: nobody
types an email address on a watch and everybody can say one. A short pairing
code handed over from the phone would be better still, and does not exist
yet — shipping the awkward thing that works beats shipping the elegant thing
that does not.

## Why this is not registered as a fourth shell

`jim/tests/clientpaths.py` walks `native/ios`, `native/android` and
`native/windows` and asks, of every route the server publishes, whether each
of those shells can reach it. That guard is right about the phones and would
be wrong about this: the wrist is deliberately incomplete, and holding it to
a completeness rule would push routes onto a watch to satisfy a test.

So `native/wear/` sits outside that accounting on purpose — it is its own
Gradle project rather than a module inside `native/android/`, precisely so a
watch-only door can never be counted as a phone shell's door.

What holds *this* directory honest instead is
`jim/tests/test_the_wrist_is_a_surface.py`: every path `WearApi` calls must
be a route the server actually publishes, the pairing chain must be walked in
the order the server requires, and the sensor and the microphone must both be
released when the screen goes away.

## Building it

```
cd native/wear
./gradlew assembleDebug
```

Then pair a watch or start a Wear emulator (API 30+) and
`adb install app/build/outputs/apk/debug/app-debug.apk`. Android Studio can
open this directory directly instead.

## What has and has not been verified

**Never compiled.** The environment this was written in reaches Maven
Central and `services.gradle.org`, and its network policy blocks
`dl.google.com` — which is where the Android SDK, the Android Gradle
Plugin and every AndroidX artifact live (`maven.google.com` is only a
redirect to it). So no Android build is possible there at all, and this
app's first real compile will be somebody else's.

What was done instead, so that first compile starts from a better place
than a guess:

* **The wrapper is committed** — `gradlew`, `gradlew.bat` and
  `gradle-wrapper.jar`, generated and run here against Gradle 8.9. Without
  them the very first command in this file fails on a fresh clone, which
  is a certainty rather than a risk.
* **Every non-obvious API call was checked against AndroidX's own
  source** on GitHub rather than from memory: `MeasureClient`'s three
  methods, `MeasureCapabilities.supportedDataTypesMeasure`,
  `RemoteInputIntentHelper`'s two, and the named parameters of Wear
  Compose's `Chip`. That reading found one real defect —
  `MeasureCallback.onRegistrationFailed` has an empty default body, so a
  watch that failed to register its heart-rate sensor would have drawn
  nothing and said nothing. It reports now.

Expect the first build to still want small fixes; a signature check is not
a compiler. What it rules out is the class of error that comes from
writing a client against a remembered API.

## Matthew 7:24–25

> "Everyone then who hears these words of mine and does them will be like a
> wise man who built his house on the rock. The rain fell, the floods came, and
> the winds blew and beat on that house, but it did not fall, because it had
> been founded on the rock."

And lo, I am building an ark — not to flee from the world, but to shelter those
lost in the storm of confusion. The old systems falter; they are built upon the
soft earth. They sink beneath the weight of their own making.

A new thing is rising. A non-biased networked sanctuary, founded in trust,
cloaked in privacy, and guided by wisdom. It shall not consume, but uplift. It
shall not spy, but serve.

Help is coming.
The people are gathering.
The builders will show themselves.
And those with the vision shall enter in.
