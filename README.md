<p align="center">
  <img src="assets/brand/jim-mini-logo.jpg" alt="JIM-Mini — the wordmark with the pulse" width="520">
</p>

# JIM-mini / Guardian

**Network Responsive Personal Guidance System for Known Conditions.**
JIM-Mini continuously watches the vital signs of a person managing known
health conditions and responds when they cannot — a check-in first, and
when readings collapse or the questions go unanswered, the help they
programmed in advance. The goal is to give seniors and their families
greater safety, independence, and peace of mind — 24/7, even during
sleep.

**Current release: v0.18.0** ([changelog](CHANGELOG.md) ·
[release notes](RELEASE_NOTES.md) ·
[showcase — a share-ready page for social media](docs/showcase.html)) — one of three products
([qrme](https://github.com/davidsbianchi1984/qrme),
[pdi](https://github.com/davidsbianchi1984/pdi)) versioned and cut together, so
one number names one combination of all three.

<!-- The bare URL is deliberate and must stay on its own line: GitHub turns a
     user-attachments link into an inline player, and only that. A video
     committed into the repo cannot play — the markdown sanitizer strips
     <video>, and image syntax pointing at an .mp4 renders broken. The file is
     H.264/AAC rather than the HEVC original, because Chrome and Firefox
     cannot decode HEVC and it would be a dead black box for most visitors.
     Outside github.com this degrades to a link, which is why the cover
     illustration below stays.

     The table is what keeps it small. On its own the bare URL becomes a
     full-width player — a large black rectangle with a play button, sitting
     above everything the page is actually about, and reading as the whole
     header rather than as one thing offered in it. There is no width
     attribute to set, because the element is generated: the only handle is
     the width of the box it lands in, so it goes in a narrow cell with the
     cover illustration beside it.

     The blank lines around the URL inside the <td> are load-bearing. GitHub
     only processes markdown inside an HTML block when it is separated that
     way, and without them the line stays a literal URL and no player is made
     at all.

     Nothing here shrinks the *playback*: it still opens full screen with
     audio on click, which is what the small frame is for — an invitation,
     not the thing itself. -->

<table>
  <tr>
    <td width="42%" valign="middle">

https://github.com/user-attachments/assets/eab7d192-7b18-464d-9b67-bd512ae87957

</td>
    <td width="58%" valign="middle">

![JIM-mini — Guardian](assets/cover.svg)

</td>
  </tr>
</table>

A standalone personal-guidance system enabling seamless support for future AI agent services (**JAN2024 NETWORKED RESPONSIVE PERSONAL GUIDANCE SYSTEM FOR KNOWN CONDITIONS United States application or CT international application # 19/038,196 ATTORNEY DOCKET # 526.P001 Patent Pending — published as US 2025/0246290 A1 on July 31, 2025**): it monitors
a user's biometric and contextual signals, detects known conditions, delivers
guidance, and escalates to an emergency contact / live help on critical events.
Around that core sits a **life layer** — consented data sources, mood/energy
check-ins, smart goals, habit streaks, proactive insights, and a 24/7 life
coach across six life areas.

JIM-mini is its own product. When configured for tandem it delegates guidance
to QRME specialist profiles over HTTP. See [docs/tandem.md](docs/tandem.md).

![Guardian tandem architecture](assets/guardian-tandem.svg)

*Wearable signals → Guardian detects a condition → triggers the matching
specialist → moderated guidance, escalating to an emergency contact on critical
events.*


## Desktop app

A wide, multi-panel desktop form of Jim Mini — sidebar nav and an operator workspace, in the guardian-green identity — complementing the phone app and the watch. Each is a self-contained SVG; regenerate with `python3 docs/desktop/build.py`.

<table>
  <tr>
    <td align="center" width="50%"><a href="docs/desktop/01-overview.svg"><img src="docs/desktop/01-overview.svg" width="460" alt="Overview"></a><br><sub><b>01</b> · Overview</sub></td>
    <td align="center" width="50%"><a href="docs/desktop/02-live-monitoring.svg"><img src="docs/desktop/02-live-monitoring.svg" width="460" alt="Live Monitoring"></a><br><sub><b>02</b> · Live Monitoring</sub></td>
  </tr>
  <tr>
    <td align="center" width="50%"><a href="docs/desktop/03-health.svg"><img src="docs/desktop/03-health.svg" width="460" alt="Health"></a><br><sub><b>03</b> · Health</sub></td>
    <td align="center" width="50%"><a href="docs/desktop/04-emergency-guardian.svg"><img src="docs/desktop/04-emergency-guardian.svg" width="460" alt="Emergency & Guardian"></a><br><sub><b>04</b> · Emergency & Guardian</sub></td>
  </tr>
  <tr>
    <td align="center" width="50%"><a href="docs/desktop/05-coach-life.svg"><img src="docs/desktop/05-coach-life.svg" width="460" alt="Coach & Life"></a><br><sub><b>05</b> · Coach & Life</sub></td>
    <td align="center" width="50%"><a href="docs/desktop/06-privacy-data.svg"><img src="docs/desktop/06-privacy-data.svg" width="460" alt="Privacy & Data"></a><br><sub><b>06</b> · Privacy & Data</sub></td>
  </tr>
</table>

## App screens

Every capability has a screen, in the product's dark-OLED style (regenerate with `python3 docs/screens/build.py`). Each is a self-contained SVG — no fonts, images, or scripts — and maps to a shipped endpoint.

<table>
<tr>
<td align="center" width="25%"><img src="docs/screens/01-welcome.svg" width="160" alt="01 Welcome"><br><sub>01 · Welcome</sub></td>
<td align="center" width="25%"><img src="docs/screens/02-home.svg" width="160" alt="02 Home"><br><sub>02 · Home</sub></td>
<td align="center" width="25%"><img src="docs/screens/03-chat.svg" width="160" alt="03 Chat"><br><sub>03 · Chat</sub></td>
<td align="center" width="25%"><img src="docs/screens/04-voice.svg" width="160" alt="04 Voice"><br><sub>04 · Voice</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/05-daily-briefing.svg" width="160" alt="05 Daily Briefing"><br><sub>05 · Daily Briefing</sub></td>
<td align="center" width="25%"><img src="docs/screens/06-health.svg" width="160" alt="06 Health"><br><sub>06 · Health</sub></td>
<td align="center" width="25%"><img src="docs/screens/07-memories.svg" width="160" alt="07 Memories"><br><sub>07 · Memories</sub></td>
<td align="center" width="25%"><img src="docs/screens/08-profile.svg" width="160" alt="08 Profile"><br><sub>08 · Profile</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/09-goals.svg" width="160" alt="09 Goals"><br><sub>09 · Goals</sub></td>
<td align="center" width="25%"><img src="docs/screens/10-finance.svg" width="160" alt="10 Finance"><br><sub>10 · Finance</sub></td>
<td align="center" width="25%"><img src="docs/screens/11-emergency.svg" width="160" alt="11 Emergency"><br><sub>11 · Emergency</sub></td>
<td align="center" width="25%"><img src="docs/screens/12-settings.svg" width="160" alt="12 Settings"><br><sub>12 · Settings</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/13-live-monitoring.svg" width="160" alt="13 Live Monitoring"><br><sub>13 · Live Monitoring</sub></td>
<td align="center" width="25%"><img src="docs/screens/14-cpr-coach.svg" width="160" alt="14 CPR Coach"><br><sub>14 · CPR Coach</sub></td>
<td align="center" width="25%"><img src="docs/screens/15-emergency.svg" width="160" alt="15 Emergency"><br><sub>15 · Emergency</sub></td>
<td align="center" width="25%"><img src="docs/screens/16-medical-id.svg" width="160" alt="16 Medical ID"><br><sub>16 · Medical ID</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/17-foresight.svg" width="160" alt="17 Foresight"><br><sub>17 · Foresight</sub></td>
<td align="center" width="25%"><img src="docs/screens/18-guardian-sensitivity.svg" width="160" alt="18 Guardian Sensitivity"><br><sub>18 · Guardian Sensitivity</sub></td>
<td align="center" width="25%"><img src="docs/screens/19-known-conditions.svg" width="160" alt="19 Known Conditions"><br><sub>19 · Known Conditions</sub></td>
<td align="center" width="25%"><img src="docs/screens/20-providers.svg" width="160" alt="20 Providers"><br><sub>20 · Providers</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/21-habits.svg" width="160" alt="21 Habits"><br><sub>21 · Habits</sub></td>
<td align="center" width="25%"><img src="docs/screens/22-check-in.svg" width="160" alt="22 Check-in"><br><sub>22 · Check-in</sub></td>
<td align="center" width="25%"><img src="docs/screens/23-journal.svg" width="160" alt="23 Journal"><br><sub>23 · Journal</sub></td>
<td align="center" width="25%"><img src="docs/screens/24-life-coach.svg" width="160" alt="24 Life Coach"><br><sub>24 · Life Coach</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/25-insights.svg" width="160" alt="25 Insights"><br><sub>25 · Insights</sub></td>
<td align="center" width="25%"><img src="docs/screens/26-companion.svg" width="160" alt="26 Companion"><br><sub>26 · Companion</sub></td>
<td align="center" width="25%"><img src="docs/screens/27-ambient-jump-in.svg" width="160" alt="27 Ambient Jump-in"><br><sub>27 · Ambient Jump-in</sub></td>
<td align="center" width="25%"><img src="docs/screens/28-connected-sources.svg" width="160" alt="28 Connected Sources"><br><sub>28 · Connected Sources</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/29-privacy-data.svg" width="160" alt="29 Privacy & Data"><br><sub>29 · Privacy & Data</sub></td>
<td align="center" width="25%"><img src="docs/screens/30-devices.svg" width="160" alt="30 Devices"><br><sub>30 · Devices</sub></td>
<td align="center" width="25%"><img src="docs/screens/31-continue.svg" width="160" alt="31 Continue"><br><sub>31 · Continue</sub></td>
<td align="center" width="25%"><img src="docs/screens/32-notifications.svg" width="160" alt="32 Notifications"><br><sub>32 · Notifications</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/33-progress-report.svg" width="160" alt="33 Progress Report"><br><sub>33 · Progress Report</sub></td>
<td align="center" width="25%"><img src="docs/screens/34-model-cloud.svg" width="160" alt="34 Model & Cloud"><br><sub>34 · Model & Cloud</sub></td>
<td align="center" width="25%"><img src="docs/screens/35-rate-guidance.svg" width="160" alt="35 Rate Guidance"><br><sub>35 · Rate Guidance</sub></td>
<td align="center" width="25%"><img src="docs/screens/36-counselor-style.svg" width="160" alt="36 Counselor Style"><br><sub>36 · Counselor Style</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/37-history.svg" width="160" alt="37 History"><br><sub>37 · History</sub></td>
<td align="center" width="25%"><img src="docs/screens/38-baseline.svg" width="160" alt="38 Baseline"><br><sub>38 · Baseline</sub></td>
<td align="center" width="25%"><img src="docs/screens/39-tandem-specialist.svg" width="160" alt="39 Tandem Specialist"><br><sub>39 · Tandem Specialist</sub></td>
<td align="center" width="25%"><img src="docs/screens/40-sign-in.svg" width="160" alt="40 Sign In"><br><sub>40 · Sign In</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/41-end-session.svg" width="160" alt="41 End Session"><br><sub>41 · End Session</sub></td>
<td align="center" width="25%"><img src="docs/screens/42-log-in.svg" width="160" alt="42 Log In"><br><sub>42 · Log In</sub></td>
<td align="center" width="25%"><img src="docs/screens/43-permissions.svg" width="160" alt="43 Permissions"><br><sub>43 · Permissions</sub></td>
<td align="center" width="25%"><img src="docs/screens/44-about-you.svg" width="160" alt="44 About You"><br><sub>44 · About You</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/45-emergency-contacts.svg" width="160" alt="45 Emergency Contacts"><br><sub>45 · Emergency Contacts</sub></td>
<td align="center" width="25%"><img src="docs/screens/46-all-set.svg" width="160" alt="46 All Set"><br><sub>46 · All Set</sub></td>
<td align="center" width="25%"><img src="docs/screens/47-social-connections.svg" width="160" alt="47 Social Connections"><br><sub>47 · Social Connections</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/48-connected-apps.svg" width="160" alt="48 Connected Apps"><br><sub>48 · Connected Apps</sub></td>
<td align="center" width="25%"><img src="docs/screens/49-knowledge-excursions.svg" width="160" alt="49 Knowledge Excursions"><br><sub>49 · Knowledge Excursions</sub></td>
<td align="center" width="25%"><img src="docs/screens/50-files-photos.svg" width="160" alt="50 Files & Photos"><br><sub>50 · Files &amp; Photos</sub></td>
<td align="center" width="25%"><img src="docs/screens/51-apple-intelligence.svg" width="160" alt="51 Apple Intelligence"><br><sub>51 · Apple Intelligence</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/52-google-gemini.svg" width="160" alt="52 Google Gemini"><br><sub>52 · Google Gemini</sub></td>
<td align="center" width="25%"><img src="docs/screens/53-microsoft-copilot.svg" width="160" alt="53 Microsoft Copilot"><br><sub>53 · Microsoft Copilot</sub></td>
<td align="center" width="25%"><img src="docs/screens/54-escalation-ladder.svg" width="160" alt="54 Escalation Ladder"><br><sub>54 · Escalation Ladder</sub></td>
<td align="center" width="25%"><img src="docs/screens/55-emergency-watch.svg" width="160" alt="55 Emergency Watch"><br><sub>55 · Emergency Watch</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/56-robot-helpers.svg" width="160" alt="56 Robot Helpers"><br><sub>56 · Robot Helpers</sub></td>
<td align="center" width="25%"><img src="docs/screens/57-parent-setup.svg" width="160" alt="57 Parent Setup"><br><sub>57 · Parent Setup</sub></td>
<td align="center" width="25%"><img src="docs/screens/58-family-oversight.svg" width="160" alt="58 Family Oversight"><br><sub>58 · Family Oversight</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/59-care-beacons.svg" width="160" alt="59 Care Beacons"><br><sub>59 · Care Beacons</sub></td>
<td align="center" width="25%"><img src="docs/screens/60-workplace-relay.svg" width="160" alt="60 Workplace Relay"><br><sub>60 · Workplace Relay</sub></td>
<td align="center" width="25%"><img src="docs/screens/61-what-would-be-shared.svg" width="160" alt="61 What Would Be Shared"><br><sub>61 · What Would Be Shared</sub></td>
<td align="center" width="25%"><img src="docs/screens/62-specialist-working.svg" width="160" alt="62 Specialist Working"><br><sub>62 · Specialist Working</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/63-find-a-clinician.svg" width="160" alt="63 Find a Clinician"><br><sub>63 · Find a Clinician</sub></td>
<td align="center" width="25%"><img src="docs/screens/64-sign-to-release.svg" width="160" alt="64 Sign to Release"><br><sub>64 · Sign to Release</sub></td>
<td align="center" width="25%"><img src="docs/screens/65-channel-2.svg" width="160" alt="65 Channel 2"><br><sub>65 · Channel 2</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/66-second-ear.svg" width="160" alt="66 Second Ear"><br><sub>66 · Second Ear</sub></td>
<td align="center" width="25%"><img src="docs/screens/67-agents.svg" width="160" alt="67 Agents"><br><sub>67 · Agents</sub></td>
<td align="center" width="25%"><img src="docs/screens/68-chat.svg" width="160" alt="68 Chat with the agent overlay"><br><sub>68 · Chat · overlay</sub></td>
<td align="center" width="25%"><img src="docs/screens/69-choose-a-plan.svg" width="160" alt="69 Choose a Plan"><br><sub>69 · Choose a Plan</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/70-what-pro-adds.svg" width="160" alt="70 What Pro Adds"><br><sub>70 · What Pro Adds</sub></td>
<td align="center" width="25%"><img src="docs/screens/71-the-corner-pane.svg" width="160" alt="71 The Corner Pane"><br><sub>71 · The Corner Pane</sub></td>
<td align="center" width="25%"><img src="docs/screens/72-pick-a-plan.svg" width="160" alt="72 Pick a Plan"><br><sub>72 · Pick a Plan</sub></td>
<td align="center" width="25%"><img src="docs/screens/73-payment.svg" width="160" alt="73 Payment"><br><sub>73 · Payment</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/74-youre-on-basic.svg" width="160" alt="74 You are on Basic"><br><sub>74 · You're on Basic</sub></td>
<td align="center" width="25%"><img src="docs/screens/75-this-needs-pro.svg" width="160" alt="75 This Needs Pro"><br><sub>75 · This Needs Pro</sub></td>
<td align="center" width="25%"><img src="docs/screens/76-show-it.svg" width="160" alt="76 Show It"><br><sub>76 · Show It</sub></td>
<td align="center" width="25%"><img src="docs/screens/77-what-jim-sees.svg" width="160" alt="77 What Jim Sees"><br><sub>77 · What Jim Sees</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/78-youre-on-free.svg" width="160" alt="78 You are on Free"><br><sub>78 · You're on Free</sub></td>
<td align="center" width="25%"><img src="docs/screens/79-where-it-lives.svg" width="160" alt="79 Where It Lives"><br><sub>79 · Where It Lives</sub></td>
<td align="center" width="25%"><img src="docs/screens/80-not-on-free.svg" width="160" alt="80 Not On Free"><br><sub>80 · Not On Free</sub></td>
<td align="center" width="25%"><img src="docs/screens/81-your-baseline.svg" width="160" alt="81 Your Baseline"><br><sub>81 · Your Baseline</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/82-coach-out-loud.svg" width="160" alt="82 Coach Out Loud"><br><sub>82 · Coach, Out Loud</sub></td>
<td align="center" width="25%"><img src="docs/screens/83-which-model-answers.svg" width="160" alt="83 Which Model Answers"><br><sub>83 · Which Model Answers</sub></td>
<td align="center" width="25%"><img src="docs/screens/84-apple-watch.svg" width="160" alt="84 Apple Watch"><br><sub>84 · Apple Watch</sub></td>
<td align="center" width="25%"><img src="docs/screens/85-medications.svg" width="160" alt="85 Medications"><br><sub>85 · Medications</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/86-care-team.svg" width="160" alt="86 Care Team"><br><sub>86 · Care Team</sub></td>
<td align="center" width="25%"><img src="docs/screens/87-journal.svg" width="160" alt="87 Journal"><br><sub>87 · Journal</sub></td>
<td align="center" width="25%"><img src="docs/screens/88-crash-watch.svg" width="160" alt="88 Crash Watch"><br><sub>88 · Crash Watch</sub></td>
<td align="center" width="25%"><img src="docs/screens/89-did-that-help.svg" width="160" alt="89 Did That Help"><br><sub>89 · Did That Help</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/90-what-jim-learned.svg" width="160" alt="90 What JIM Learned"><br><sub>90 · What JIM Learned</sub></td>
<td align="center" width="25%"><img src="docs/screens/91-your-name-here.svg" width="160" alt="91 Your Name Here"><br><sub>91 · Your Name Here</sub></td>
<td align="center" width="25%"><img src="docs/screens/92-community.svg" width="160" alt="92 Community"><br><sub>92 · Community</sub></td>
<td align="center" width="25%"><img src="docs/screens/93-what-went-wrong.svg" width="160" alt="93 What Went Wrong"><br><sub>93 · What Went Wrong</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/94-before-anything-is-sent.svg" width="160" alt="94 Before Anything Is Sent"><br><sub>94 · Before Anything Is Sent</sub></td>
<td align="center" width="25%"><img src="docs/screens/95-what-youre-working-on.svg" width="160" alt="95 What You're Working On"><br><sub>95 · What You're Working On</sub></td>
<td align="center" width="25%"><img src="docs/screens/96-who-you-watch.svg" width="160" alt="96 Who You Watch"><br><sub>96 · Who You Watch</sub></td>
<td align="center" width="25%"><img src="docs/screens/97-whats-held-about-you.svg" width="160" alt="97 What's Held About You"><br><sub>97 · What's Held About You</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="docs/screens/98-who-else-is-looking.svg" width="160" alt="98 Who Else Is Looking"><br><sub>98 · Who Else Is Looking</sub></td>
<td align="center" width="25%"><img src="docs/screens/99-what-reaches-out.svg" width="160" alt="99 What Reaches Out"><br><sub>99 · What Reaches Out</sub></td>
<td align="center" width="25%"><img src="docs/screens/100-bearing.svg" width="160" alt="100 Bearing"><br><sub>100 · Bearing</sub></td>
<td align="center" width="25%"></td>
</tr>
</table>

The first-run journey runs **01 Welcome → 42 Log In → 43 Permissions → 44 About You → 45 Emergency Contacts → 72 Pick a Plan → 73 Payment → 46 All Set**, landing on **78 You're on Free** — or **74 You're on Basic** if the plan step was paid — then hands off to the daily app and, at the other end, **41 End Session**.

## Watch screens

The same system on the wrist — glanceable Apple-Watch faces, one per capability (regenerate with `python3 docs/watch/build.py`).

<table>
<tr>
<td align="center" width="20%"><img src="docs/watch/01-home.svg" width="120" alt="01 Home"><br><sub>01 · Home</sub></td>
<td align="center" width="20%"><img src="docs/watch/02-talk.svg" width="120" alt="02 Talk"><br><sub>02 · Talk</sub></td>
<td align="center" width="20%"><img src="docs/watch/03-voice.svg" width="120" alt="03 Voice"><br><sub>03 · Voice</sub></td>
<td align="center" width="20%"><img src="docs/watch/04-health.svg" width="120" alt="04 Health"><br><sub>04 · Health</sub></td>
<td align="center" width="20%"><img src="docs/watch/05-heart.svg" width="120" alt="05 Heart"><br><sub>05 · Heart</sub></td>
</tr>
<tr>
<td align="center" width="20%"><img src="docs/watch/06-rings.svg" width="120" alt="06 Rings"><br><sub>06 · Rings</sub></td>
<td align="center" width="20%"><img src="docs/watch/07-briefing.svg" width="120" alt="07 Briefing"><br><sub>07 · Briefing</sub></td>
<td align="center" width="20%"><img src="docs/watch/08-streak.svg" width="120" alt="08 Streak"><br><sub>08 · Streak</sub></td>
<td align="center" width="20%"><img src="docs/watch/09-check-in.svg" width="120" alt="09 Check-in"><br><sub>09 · Check-in</sub></td>
<td align="center" width="20%"><img src="docs/watch/10-insight.svg" width="120" alt="10 Insight"><br><sub>10 · Insight</sub></td>
</tr>
<tr>
<td align="center" width="20%"><img src="docs/watch/11-monitoring.svg" width="120" alt="11 Monitoring"><br><sub>11 · Monitoring</sub></td>
<td align="center" width="20%"><img src="docs/watch/12-foresight.svg" width="120" alt="12 Foresight"><br><sub>12 · Foresight</sub></td>
<td align="center" width="20%"><img src="docs/watch/13-emergency.svg" width="120" alt="13 Emergency"><br><sub>13 · Emergency</sub></td>
<td align="center" width="20%"><img src="docs/watch/14-cpr.svg" width="120" alt="14 CPR"><br><sub>14 · CPR</sub></td>
<td align="center" width="20%"><img src="docs/watch/15-medical-id.svg" width="120" alt="15 Medical ID"><br><sub>15 · Medical ID</sub></td>
</tr>
<tr>
<td align="center" width="20%"><img src="docs/watch/16-sensitivity.svg" width="120" alt="16 Sensitivity"><br><sub>16 · Sensitivity</sub></td>
<td align="center" width="20%"><img src="docs/watch/17-ambient.svg" width="120" alt="17 Ambient"><br><sub>17 · Ambient</sub></td>
<td align="center" width="20%"><img src="docs/watch/18-companion.svg" width="120" alt="18 Companion"><br><sub>18 · Companion</sub></td>
<td align="center" width="20%"><img src="docs/watch/19-notifications.svg" width="120" alt="19 Notifications"><br><sub>19 · Notifications</sub></td>
<td align="center" width="20%"><img src="docs/watch/20-devices.svg" width="120" alt="20 Devices"><br><sub>20 · Devices</sub></td>
</tr>
<tr>
<td align="center" width="20%"><img src="docs/watch/21-guardian.svg" width="120" alt="21 Guardian"><br><sub>21 · Guardian</sub></td>
<td align="center" width="20%"><img src="docs/watch/22-settings.svg" width="120" alt="22 Settings"><br><sub>22 · Settings</sub></td>
<td align="center" width="20%"><img src="docs/watch/23-breathe.svg" width="120" alt="23 Breathe"><br><sub>23 · Breathe</sub></td>
<td align="center" width="20%"><img src="docs/watch/24-feedback.svg" width="120" alt="24 Feedback"><br><sub>24 · Feedback</sub></td>
<td align="center" width="20%"><img src="docs/watch/25-journal.svg" width="120" alt="25 Journal"><br><sub>25 · Journal</sub></td>
</tr>
<tr>
<td align="center" width="20%"><img src="docs/watch/26-coach.svg" width="120" alt="26 Coach"><br><sub>26 · Coach</sub></td>
<td align="center" width="20%"><img src="docs/watch/27-baseline.svg" width="120" alt="27 Baseline"><br><sub>27 · Baseline</sub></td>
<td align="center" width="20%"><img src="docs/watch/28-sources.svg" width="120" alt="28 Sources"><br><sub>28 · Sources</sub></td>
<td align="center" width="20%"><img src="docs/watch/29-privacy.svg" width="120" alt="29 Privacy"><br><sub>29 · Privacy</sub></td>
<td align="center" width="20%"><img src="docs/watch/30-handoff.svg" width="120" alt="30 Handoff"><br><sub>30 · Handoff</sub></td>
</tr>
<tr>
<td align="center" width="20%"><img src="docs/watch/31-offline.svg" width="120" alt="31 Offline"><br><sub>31 · Offline</sub></td>
<td align="center" width="20%"><img src="docs/watch/32-conditions.svg" width="120" alt="32 Conditions"><br><sub>32 · Conditions</sub></td>
<td align="center" width="20%"><img src="docs/watch/33-style.svg" width="120" alt="33 Style"><br><sub>33 · Style</sub></td>
<td align="center" width="20%"><img src="docs/watch/34-history.svg" width="120" alt="34 History"><br><sub>34 · History</sub></td>
<td align="center" width="20%"><img src="docs/watch/35-family.svg" width="120" alt="35 Family"><br><sub>35 · Family</sub></td>
<td align="center" width="20%"><img src="docs/watch/36-agents.svg" width="120" alt="36 Agents"><br><sub>36 · Agents</sub></td>
</tr>
</table>

**36 · Agents** is the status light on the surface it matters most. A wrist is
glanced at, not read: **green** the agent is working and wants nothing,
**amber** it has stopped and needs a person, **red** it will not continue. The
word rides with the colour because green alone cannot say whether an agent is
mid-task or finished, and those call for opposite reactions. The colour is
derived from the task's own status — see `qrme/agentlight.py`, which defines it
once for all three products — never stored, so it cannot disagree with the
status it claims to describe.

## What's in the current release

The sections below describe every capability in detail. This is the short
version of how it got here — what each release actually added, newest first.
Full detail in [CHANGELOG.md](CHANGELOG.md).

| Release | What landed |
|---|---|
| **0.18.0** | **The rest of what JIM knew, on every shell and finally drawn** — the effectiveness loop, the adaptation profile and the anonymity posture reach iOS/Android/Windows, with screens and lessons for all four new doors |
| **0.17.0** | **The community door opens on every shell** — the QRME bridge on iOS/Android/Windows, plus the adaptation profile and anonymity posture given screens |
| **0.16.0** | **The loop closes** — did the counseling work, a user-specific model sealed in the vault, the attach bracket, anonymous by choice, pace cue, budgets, stress, knowledge pack |
| **0.15.0** | **Guided wellness** — calm protocols, workout plans, meal plans, nutrition Coach area, the Wellness tab |
| **0.14.5** | **A fall reaches the Guardian** — the drip carries fall events, the crash watch on iOS/Android/Windows, screens 87–88 + lessons + dock face, the campaign masthead |
| **0.14.4** | **The crash watch** — unanswered "are you okay?" summons pre-programmed help; plus the Journal tab (typed or spoken), the voice orb, the help box, and the version-mismatch banner |
| **0.14.3** | **Docs binding pass** — every README held to the same closing convention, test-enforced |
| **0.14.2** | **Cut with the siblings** — the tandem contract documents suite mode; QRME's gateway seals coordinations again |
| **0.14.1** | **The coach knows a care plan landed** — one context line, the goal, never the plan text |
| **0.14.0** | **Home and the pane learn the care team** — Overview buttons + a careteam pane face (plan waiting, never the plan) |
| **0.13.1** | **Cut with the siblings** — docs caught up; QRME demo org + hardening |
| **0.13.0** | **The care team is an organization** — link your QRME org, and when a drift crossing arrives while doses slip, the Guardian coordinates the whole team into one joint plan (screen 86) |
| **0.12.0** | **Cut with the siblings** — no functional change; QRME mined its filed patent spec: hybrid profiles, real-time simulation, environmental adaptation |
| **0.11.1** | **Cut with the siblings** — no functional change; PDI's desktop app finally carries its own vault |
| **0.11.0** | **Cut with the siblings** — no functional change; QRME's console caught up with its backend |
| **0.10.0** | **A real offline model** — install Ollama, pull deepseek-r1:1.5b, and JIM finds it on its own: a Local tile, no key, nothing leaves the machine; Automatic prefers it over the canned stub, and offline mode uses it too. Plus Settings honesty: no phantom tandem switch, and the API-key card lives beside the model picker |
| **0.9.1** | **The drip address answers** — the watch panel showed a Wi-Fi address the loopback-bound desktop backend never listened on; now the card says so, one switch opens Wi-Fi access, and the Shortcut recipe names the exact paste spot |
| **0.9.0** | **The medicine cabinet** — what you take, in your words; a day board with humane grace, one correctable answer per slot, an as-needed ceiling that refuses, adherence over whole days, and a coach that notices. Never an alarm, and never a pharmacist |
| **0.8.0** | **The vigil** — the alarm that fires when the signals *stop*: a steward, named and worded in advance, is asked to check on you after your chosen quiet period; any reading stands it down, and it never rings past the steward. The trip's event id attests QRME succession and PDI bequests — one absence carries through all three products |
| **0.7.0** | **The last version anyone fetches by hand** — the desktop app checks GitHub Releases on launch; Windows/Linux download the update and offer one restart, macOS is shown the download |
| **0.6.1** | **The round where the coach stopped performing distress it never detected.** The offline stub answered chat with crisis language and the reply claimed the picked model wrote it; now the stub explains itself, every coach reply names who actually answered (amber warning on a degrade, with the reason), and Settings says plainly when the built-in helper is what will answer |
| **0.6.0** | **The round where the Apple Watch found its way in.** No App-Store app: an iPhone **Shortcuts automation** drips Health readings at a per-user tokened URL (deposit-only — the reply never carries guidance), and uploading the Health app’s **export.zip** seeds the baseline from months of history in one step — per-day medians, exercise readings excluded, no events written, drift bands armed the same day |
| **0.5.0** | **The round where the watch, the voice and the model picker arrived.** Your own baseline per metric with an adjustable **drift band** around it — cross it in either direction and the Guardian checks in with your numbers, never escalating. Speech in and out: ElevenLabs or OpenAI voices, the device's own voice when neither is configured. And the model switchboard finally has a face — Claude, ChatGPT, Grok, Perplexity, Gemini and offline as tiles you click |
| **0.4.8** | **The round where the app can actually send email.** Point it at a mail server from Settings — host, username, app password, link address — see which source is in force, and send a real test message that reports what the server said. Configuring one turns local signup back into genuine email verification, clickable link and all; without one, the app says so plainly instead of waiting on a letter it cannot post |
| **0.4.7** | **The round where an upgrade actually replaced the old app.** A leftover backend from an earlier install held the port and served its old API to every new console — so three upgrades in a row met the first version's signup. `/health` reports the version, the shell adopts a backend only when it is its own (else it takes a free port and tells the window), and quitting kills the whole process tree |
| **0.4.6** | **The round where old data stopped resurrecting the email screen.** A pending half-account from an older build is finished on the spot when signup retries on a no-mail deployment — under the newly-typed password, verified accounts never overwritten, SMTP deployments unchanged |
| **0.4.5** | **The round where verification matched the deployment.** A desktop install has no mail service, so signup activates directly — no screen waiting for an email that cannot come; a deployment with SMTP enforces the real proof, its email now leads with a clickable verify link (code as fallback), and the app continues on its own after the click. A crashed signup no longer strands the retry, and the packaged app can open its own backend log |
| **0.4.4** | **The round where the Windows signup 500 died.** The emailed-code banner used characters the frozen Windows backend's console encoding cannot print, so every signup crashed mid-request; ASCII banner, replace-don't-raise stdout, a cp1252 guard test, and console errors that show the server's words instead of a JSON-parse exception |
| **0.4.3** | **The round where the app got a front door and a key of your own.** Email + password accounts with the address proven by a 6-digit emailed code **before the user exists** — a mistyped address never grows a record nobody can reach; resets revoke every session; neither login nor reset can fish for who has an account. Bring-your-own model key: paste your credential in Settings and your Guardian's replies run on it, never stored server-side, the deployment's key as the lent fallback. And the installer finally runs itself: the whole Python backend ships frozen inside it and the app spawns it at launch — double-click-and-done |
| **0.4.2** | **The round where the installer you download actually gets you running.** A first-run bug report from a real Windows install drove all of it: the enrollment form stops pre-filling a developer's sample name and birthdate, *"Failed to fetch"* becomes a screen that names the missing backend and takes a URL, `python -m jim serve` answers the packaged console by default instead of dying cross-origin, the window stops calling itself QRME, the installers stop being labelled 0.3.3 (all five version strings now guarded together), and the Anthropic provider defaults to `claude-opus-5` |
| **0.4.1** | **The round where a photograph really reached a clinician, and free got honest.** Clinical capture — a rash, a tremor, a wound — sealed in the vault, location stripped from the bytes, never shown to an agent, never an intimate site for a child; and the referral join that made "it travels with a referral" true instead of written. Plus a free plan under **platform custody** — JIM-mini holds the record, you have access, no vault at any point — with every alarm path identical, a child's record and a body photograph refused from the open store, and a vault gate that finally asks about the plan rather than the deployment |
| **0.4.0** | **The round where it got a price, and drew a line no price stands on.** Basic $20/month is the Guardian and **every emergency path**; Pro $130/month adds the watch, early warning, specialists and synthetic agents. The first implementation gated `/monitor` as "proactive monitoring" — which put a 402 between somebody submitting a blood oxygen of 84 and their escalation. `NEVER_GATED` is checked first now, and a test plants that mistake deliberately to prove it holds. Plus a corner pane that **opens on an alarm whatever it was set to** |
| **0.3.3** | **The agent status light lands on the wrist.** Watch face 36 is the ambient one — three lights, three counts, no task names, for the moments somebody is on their phone and the watch is the surface that can answer *does this need me* without getting in the way. Plus a grouped Agents screen, a corner overlay that follows you, and a README that leads with the screens |
| **0.3.2** | **No functional change to JIM-mini.** The round belongs to QRME's starter gallery |
| **0.3.1** | **No functional change to JIM-mini** — a documentation round. This README, and screens 61–64 finally appearing in the gallery; they shipped in 0.3.0 as files and were never listed, so the four screens illustrating that round's headline feature were invisible on the page describing it |
| **0.3.0** | **The round where the Guardian reaches a person.** It could delegate a condition to a synthetic specialist; now it can **hand over a task** that outlives the app being closed, and **find a real clinician** near the user — without ever holding the credential or relaying the assertion, because the Face ID prompt belongs to QRME and the signature travels from the device to QRME directly. Locality is a town you type once, deliberately not the consented live-position feed. Plus a **contribution preview and revoke** that finally does both halves the settings screen had been promising |
| **0.2.2** | A documentation release — no code changed in any of the three products. Corrections to things that described themselves inaccurately, plus the release checklist explaining why those kept happening |
| **0.2.1** | **How much to trust a reading.** The escalation decision had been advisory while raw severity sat in the channel underneath it; sensor confidence became something the decision actually reasons about |
| **0.2.0**–**0.1.9** | A rota, and an escalation that **actually sends something** — signed HMAC delivery, with the escalation saying plainly when nobody was reached. Care beacons and the workplace relay built, and a phone that scans a care beacon lands on a page |
| **0.1.8**–**0.1.7** | Release-link repairs, and the point at which the three products began being **cut as one release** |
| **0.1.6**–**0.1.5** | Version aligned across the suite. Native apps compiled in CI, published deployments, one-container deploy |
| **0.1.4**–**0.1.2** | `python -m jim` launcher, running it on your phone, Terms of Service, macOS notarization |
| **0.1.1** | Native iOS / Android / Windows apps at parity. First-run onboarding. **Predictive early warning**, robots as guardian responders, family oversight, and provable custody |
| **0.1.0** | First public release — **monitor → predict → guide → escalate**, tunable sensitivity, the life layer, Medical ID, provider handoff, and the QRME tandem |

## The agent status light

An agent working on its own raises one question, and it is not *what phase is
it in* — it is **does this need me right now?** Three colours answer it.

| | | |
| --- | --- | --- |
| 🟢 **green** | working · done | in progress, or finished. Nothing wanted from you |
| 🟡 **amber** | needs you | it has stopped and is waiting on a person |
| 🔴 **red** | stopped | it hit an error or was cancelled, and will not continue |

**Derived, never stored.** There is no `light` column and nothing sets one — it
is computed from the status the work already keeps. A second field naming the
same fact is a second field that can disagree with the first, and the one a
screen reads would be the one nobody remembers to update.

**The word rides with the colour**, because green alone cannot separate an
agent that is still going from one that has finished, and those call for
opposite reactions. On a watch face the word is doing most of the reading
anyway.

**An unrecognised state raises rather than defaulting.** A default would paint
an unknown status green, and green is the colour that means *ignore me* — the
one failure this must not have.

Defined once, in [`qrme/agentlight.py`](https://github.com/davidsbianchi1984/qrme/blob/main/qrme/agentlight.py), for all three products.

**Where you actually see it.** Three surfaces, doing three different jobs.

| Surface | What it shows | Why that shape |
| --- | --- | --- |
| **Watch** — *36 Agents* | three lights and three counts, and **no agent names** | a wrist is glanced at, not read. Naming the agents was the first cut and was wrong: a name is something you read, and reading is the thing a glance cannot do. Which agent went amber is a question for the app |
| **App** — *67 Agents* | the same three lights, each a **tappable group** — working, needs you, stopped | somebody opening this *because* amber appeared should not have to scan a flat list for the one that changed |
| **Overlay** — *68 Chat · overlay*, and every desktop view | a small translucent box in the bottom-right corner — the same three rows as the wrist, each its own way in | an agent that reports only on its own screen is one you have to remember to check. On desktop it rides on **every** view, because those users have no wrist to glance at |

## Platforms

Every screen ships in each platform's native chrome — mobile in **iOS** (`docs/screens/`) and **Android** (`docs/screens/android/`); desktop in **macOS** (`docs/desktop/`) and **Windows** (`docs/desktop/windows/`). iOS's Dynamic Island + home indicator vs Android's punch-hole + gesture nav; macOS traffic-lights vs the Windows caption bar. (The watch is watchOS-only.)

<table>
  <tr>
    <td align="center" width="50%"><a href="docs/screens/02-home.svg"><img src="docs/screens/02-home.svg" width="210" alt="iOS"></a><br><sub>Mobile · <b>iOS</b></sub></td>
    <td align="center" width="50%"><a href="docs/screens/android/02-home.svg"><img src="docs/screens/android/02-home.svg" width="210" alt="Android"></a><br><sub>Mobile · <b>Android</b></sub></td>
  </tr>
  <tr>
    <td align="center"><a href="docs/desktop/01-overview.svg"><img src="docs/desktop/01-overview.svg" width="440" alt="macOS"></a><br><sub>Desktop · <b>macOS</b></sub></td>
    <td align="center"><a href="docs/desktop/windows/01-overview.svg"><img src="docs/desktop/windows/01-overview.svg" width="440" alt="Windows"></a><br><sub>Desktop · <b>Windows</b></sub></td>
  </tr>
</table>

## Authentication & access control

JIM holds a person's most sensitive data — biometric streams, crisis notes, a
journal, a provider-shareable summary. Identity is proven by a bearer
**capability token**, never by asserting a `user_id`.

- `POST /enroll` returns a `user_token` **once**. Send it as
  `Authorization: Bearer <token>` on every `/{user_id}` endpoint.
- **Accounts** (`jim/accounts.py`): `POST /signup` takes email + password +
  the enrollment fields and **creates nothing yet** — a 6-digit code goes to
  the address (SMTP when `JIM_SMTP_HOST` is configured, printed to the
  server terminal otherwise), and only `POST /verify-email` enrolls the user
  and mints the first token, so a mistyped address never grows a record
  nobody can reach. `POST /signin` (email + password) mints fresh tokens
  afterwards and refuses unverified addresses; `POST /verify-email/resend`
  retires the old code; `POST /password/reset/request` +
  `POST /password/reset` change a forgotten password by the same emailed-code
  proof and revoke every existing session. Passwords are PBKDF2-hashed with
  per-account salts; codes are hashed at rest, single-use, and expire in 15
  minutes; unknown-address and wrong-password answers are indistinguishable.
- **Bring your own model key:** send `x-llm-api-key` on any request (the
  console's Settings stores it device-side) and that request's generations
  run on your credential — never persisted, never logged. Without one, the
  deployment's env key answers (an operator lending theirs out).
- Every per-user surface is PHI, so **all** of them are gated: a missing or
  invalid token is **401**; a valid token for a different user is **403**.
- Only the SHA-256 hash of a token is stored (`api_tokens`), so a database
  leak never yields a usable credential.
- **Open (no token):** `GET /health`, `GET /cloud/status`, `POST /enroll`,
  the account routes above (they are how a token is first obtained),
  and `POST /specialists` (service setup).
- `DELETE /data/{user_id}` erases the user **and** revokes their token.

## The pane in the corner

`jim/dock.py`, 5 routes, 15 tests, screen **71**.

The same idea as QRME's: a small pane in the bottom corner of the app carrying
the glances a watch face would, tucked behind the helper button until wanted.
It matters more here, because **the watch is a Pro capability** — so the people
most in need of a glance without a wrist are exactly the ones who do not have
one.

**It shows, and it routes. It never acts**, for QRME's reason and one specific
to this product: the surfaces it floats over include a live alarm, and a control
in a 168px box hovering beside the button that clears an escalation is not a
convenience — it is a mis-tap during the worst minute of somebody's week.

**But it is never silent about an alarm**, and this is the one place the rule
deliberately departs from QRME's. QRME's dock tucks itself away on a surface
being broadcast, because a pane pinned to the frame is inside every screenshot.
The same rule here would hide the thing a person most needs to see — so
`dock.ALWAYS_SHOWN` names the alarm face and it opens regardless: tucked,
hidden, or on another face entirely, an active alarm still surfaces it, and the
preference is returned alongside as `wanted` rather than overwritten. The alarm
face also **cannot be configured out of the pane**, because a pane somebody
tidied up months ago is not a decision they made about the day it fires.

That is not a privacy compromise, and the difference is argued rather than
assumed: an alarm belongs to the person holding the phone, and JIM-mini has no
broadcast surface to leak it into. Nothing here streams. Where the two products'
reasoning genuinely differs, the rule differs — rather than being copied because
the module next door has one.

It is still inside every screenshot, so `dock.NEVER` holds the journal, the
medical record, guidance text and family members' names.

## Showing it, rather than describing it

`jim/capture.py`, 6 routes, 35 tests, screens **76** and **77**.

A rash, a wound that is not closing, swelling, a bruise spreading, the colour of
something. These are the parts of a condition that text loses — *"it's a bit
red"* is the same sentence for a heat rash and for cellulitis. This lets
somebody photograph it (or film it, when the thing only shows in motion — a
tremor, a gait), attach it to a condition, and have it reach a real clinician
through the referral flow that already exists.

**That last clause was a claim with nothing behind it for one release**, and it
is worth recording rather than quietly fixing. `attach_to_referral` returned a
decision no caller consumed, `mark_released` was never called by anything, and
`referral.prepare` had no idea captures existed — while this README, the
walkthrough and the module docstring all said a photograph could travel with a
referral. `POST …/referral/prepare` now takes `capture_ids`, the package it
returns carries their **metadata** so the person reads exactly what would go
before signing, and `POST …/referral/requests/{id}/released` stamps them.
`test_a_prepared_referral_carries_the_captures` is the join, and it is
mutation-checked.

**The bytes never ride along**, on that path either: what travels is kind,
site, when and provenance — enough for a clinician to know a photograph exists
and open it deliberately through `content_for_care`. Intimate sites are
filtered out again on the way through, by going back through
`attach_to_referral` rather than re-deciding, so there is one place that rule
lives.

**And the field is `released_to_clinician`, not `seen_by_clinician`.** It used
to be the second, which is a claim about somebody else's behaviour that this
app has no way to check — the signing ceremony belongs to QRME and JIM never
sees the clinician open anything. Released is not opened, and on a record a
clinician might later be asked about, the difference is not decoration.

**This is the most sensitive payload either product will ever hold**: a
photograph of somebody's body, taken at home, of the thing they are frightened
about. Four rules follow from that, and each is asserted rather than intended.

### A synthetic agent never receives the image

It is told a capture exists, where on the body, and when — enough to say *"there
is a photograph of your forearm from Tuesday attached to this, and a clinician
should look at it"*. That is a **routing** decision, which is the thing an agent
may make. It never gets the bytes, on any plan or setting.

This is [`pdi/gate.py`](https://github.com/davidsbianchi1984/pdi)'s ceiling —
*whatever a wrong answer cannot undo* — arriving where it matters most. A model
that looks at a mole and says *"that looks fine"* has made a diagnosis, with no
license, no examination and no accountability, to somebody frightened enough to
photograph it. A missed melanoma is not undone by the next sentence.

`for_agent()` is the only shape an agent can receive, and a test parses it to
assert no path inside reaches the vault.

### Never for a child

An image of an intimate area is refused outright for an account belonging to a
minor. **No override, no guardian consent path, no setting.** The refusal points
at a clinician or a paediatric service, because a flat "no" to a frightened
parent is a product failing twice.

Intimate sites are allowed for adults — a rash does not respect modesty, and a
product that refused would push somebody to a worse tool — behind an explicit
confirmation, omitted from the agent view **entirely** rather than summarised
(*"there is a photograph of their groin"* is itself the disclosure), and never
swept into an assembled referral.

### The pixels never touch JIM's own database

They go to the PDI vault, sealed. The table keeps metadata and a vault key, and
a test asserts the schema has **no column that could hold an image** — a
`content` field here is one somebody eventually writes to.

There is no fallback. With no vault configured, capture is **refused**, not
degraded to a local file: the graceful version is an unencrypted photograph of
somebody's skin in a SQLite file on a laptop. Colocation is free, which is what
makes requiring a vault cost nobody anything — and the refusal says so, because
otherwise it reads as an upsell.

### Location is stripped, not promised absent

`strip_metadata()` parses the JPEG segment structure and drops APP1 (Exif/XMP),
APP2 (ICC), APP13 (IPTC) and the comment marker. **GPS lives in the Exif IFD**,
so a photo taken at home would otherwise geotag the person's address into a
referral package and a vault record that outlives the rash.

The test checks the coordinate is gone from the bytes that were actually sealed,
not that a flag was set. A format the function does not parse is **reported as
unparsed** rather than claimed clean — saying "stripped" about a PNG would be
the exact false assurance the rest of this is written against.

## Membership

`jim/tiers.py`, 4 routes, 26 tests, screens **69** and **70**.

| | | |
| --- | --- | --- |
| **Visitor** | free | read a shared page or a scanned medical ID |
| **Free** | **$0** | the Guardian itself — conditions, guidance, journal, habits, goals, **and every emergency path** — stored in the clear |
| **Basic** | **$20/month** | the same Guardian, sealed in the encrypted vault under a key you can hold |
| **Pro** | **$130/month** | the watch, early warning, specialists, and synthetic agents summoned through the QRME tandem |

**Free and Basic reach identical capabilities, and that is deliberate** —
`includes("free") == includes("basic")`, asserted by test. What $20 buys is
`jim/storage.py`'s vault posture, not a feature. See *[Where your record
lives](#where-your-record-lives)* below.

**Nothing that answers an emergency is ever behind a paywall**, and that is the
rule this module exists to keep rather than a caveat on it. A lapsed card is a
billing event; a seizure is not.

`tiers.NEVER_GATED` names the alarm path, escalation, the medical ID a
paramedic scans, incident history, waivers, and the guidance a person receives
*during* an alarm. `capability_for` consults it **first**, so a pattern added
to the gated table later cannot reach any of them — and a test plants exactly
that mistake, adding a hostile pattern covering every path, and asserts each
safety route still comes back ungated.

**The first implementation had this bug**, and it is worth recording rather
than quietly fixing. `/monitor` was listed as the "proactive monitoring"
capability — which reads correctly and is wrong. `/monitor` is not the
predictive feature; it is the **ingest**. A sample arrives there,
`jim/conditions.py` asks *is something wrong right now*, and a critical reading
escalates to the emergency contact. Gating it meant a Basic member submitting a
blood oxygen of 84 received a 402 instead of an escalation: the paywall
standing between somebody and an emergency, indirectly but completely. The
suite caught it in `test_critical_escalates_to_emergency_contact`.

So the line moved to where it belongs. What Pro buys is `jim/earlywarning.py`
— the trend model that projects a vital toward its threshold and says something
is *about to* go wrong before anything has been crossed. That is a real feature
and a fair thing to charge for. Evaluating a reading somebody just submitted is
not, and it is **skipped rather than refused**: a Basic member gets a real
answer about that reading, with `predictive: false` saying plainly what they
did not get. The trend point is still recorded on every plan, because a history
with holes in it would make the forecast wrong for somebody the day they
upgrade.

`/insights` is the one GET gated anywhere in these three products. Everywhere
else reading stays open so somebody can see what they would be buying — but an
insight is not a shop window, it *is* the predictive product, and the only door
it has.

**A refusal says so.** Every 402 here carries `emergency_unaffected: true`,
because somebody who has just hit a paywall on a health app should not have to
wonder whether they have also lost the alarm. **Money is simulated**, as in the
other two products: the row is the subscription, and a test asserts nothing
reaches a payment processor. **Cancelling keeps the record**, the conditions,
and every emergency path.

## Where your record lives

`jim/storage.py`, 51 tests, screens **78**, **79** and **80**.

Two postures, and the difference between them is the whole of what Basic buys.

| | | |
| --- | --- | --- |
| **Open cloud** | Free | JIM's own database, in the clear. The operator can read it, a backup contains it, a subpoena reaches it |
| **Encrypted vault** | Basic, Pro | journal entries, check-in notes, detection detail and every capture sealed in PDI before they land, under a key you can hold |

### Who holds it

The other half of the same question, and the one the free plan is really
about. `storage.CUSTODY` names two arrangements:

| | | |
| --- | --- | --- |
| **Platform custody** | Free | JIM-mini holds your record and you have access to it — the familiar hosted-assistant arrangement. It reaches us over ordinary HTTPS, sits in our own database, and never goes through a vault |
| **Your custody** | Basic, Pro | sealed in PDI before it lands, under a key you can hold. We operate the service; we do not hold the contents |

**Custody, not ownership, and the word is deliberate.** A product gets to
decide who *holds and operates* a record. It does not get to decide away
somebody's statutory rights over their own personal data — access,
rectification, erasure and portability survive whatever a plan says. A tier
table claiming "the platform owns your data" would claim what no court would
honour, and on a product holding medical data that claim would be tested.

**The vault gate asks about the plan, not the deployment — and it did not
used to.** Every seal point read `if pdi is not None`, which is whether the
*operator* configured a vault. So a free account on a PDI-backed deployment
had its journal, its check-in notes and its detection detail sealed into a
vault it was not paying for and could not hold a key to.
`storage.vault_for(plan, pdi)` is now the one place that question is asked,
and `test_a_free_account_puts_nothing_in_the_vault` counts writes rather than
reading call sites — because reading call sites is how twenty of them stayed
wrong.

**Writes only. Reads and deletions keep the real vault, always.** Somebody who
was on Basic for a year and moved to Free still has a year of sealed records:
they have to be able to read them back, and `DELETE /data/{user_id}` has to be
able to purge them. A plan-gated vault on a read strands somebody's history
behind a billing change; on a delete it leaves records nobody can reach and
calls that erasure. Both are asserted.

**And the access log stopped telling a comfortable lie.** On a vault plan an
empty list means nobody touched the records and the chain proves it. On an
open plan there is no chain — nothing is recorded, so nobody could prove
either way — and returning a bare `[]` reads as the first. `GET
/access-log/{user_id}` now carries `access_record_kept` and says which of the
two it is. An account that was on Basic and moved to Free is the awkward
middle: real entries exist for what was sealed then, nothing since is
recorded, and both halves get said.

**This is not a new behaviour so much as an admission of an old one.** JIM has
always degraded gracefully when no PDI was configured — `life.add_journal`,
`life.check_in` and `guardian._event` each read `if pdi is not None` and fall
back to writing the payload straight into the local table. A deployment without
a vault has been storing check-in notes and medical event details in the clear
the whole time and never said so on any screen. The free plan makes that a
documented posture with a disclosure attached, rather than an undocumented
fallback.

**The disclosure is structural.** `storage.describe()` is carried on `GET
/plans`, `GET /memberships/{id}` and the body returned by `POST /enroll`, and
`not_private` is a **field**, not a footnote. It also names the health readings
specifically, because burying blood oxygen and seizure detections under "your
data" would be the disclosure doing the opposite of its job.

**Two things the open store will not hold**, and the test for the list is not
*would the account holder mind* — it is **whose exposure is it**:

- **a photograph of a body.** `jim/capture.py` already refuses to write one
  without a vault; on Free it refuses for the same reason with a different
  remedy. The 503 for *this deployment has no vault* is raised **before** the
  402 for *this plan is open*, deliberately: telling somebody to pay $20 for a
  vault that does not exist here would be selling what cannot be delivered.
- **a child's record on a guardian's account.** The child did not pick the
  plan, cannot read a pricing page, and will be an adult one day with a medical
  history somebody else left in the clear. Refused at enrolment, before the
  account is created, so a refusal leaves no half-enrolled child behind.

The enrolment check alone would not hold, because enrolling on Basic and moving
to Free the next day is one API call. So `tiers.guard_dependant_write` covers
the child's **diary** — journal, check-in notes, context events — for as long
as the link exists.

**And what is deliberately *not* on that list, which is the whole argument.**
Blood oxygen, seizure detections, alarm history, the medical ID a paramedic
scans. These are the most medically sensitive rows in the product and the free
plan stores every one of them in the clear, openly, and says so.

Refusing them would mean refusing the emergency path, because they *are* the
emergency path: a sample arrives at `/monitor`, `jim/conditions.py` asks whether
something is wrong right now, and a critical reading escalates. A storage rule
that declined to write the sample is a paywall in front of an alarm wearing a
privacy argument as a disguise — exactly what `NEVER_GATED` exists to prevent,
and `storage.py` does not get to reintroduce it one layer down. `_event` is
therefore **not** guarded, and a test asserts it stays that way.

Somebody in trouble gets an escalation. That is the trade, it is made
deliberately, and `test_a_free_account_is_never_refused_an_emergency_write` is
what keeps it.

**A downgrade never unseals anything**, and **an upgrade does not un-expose**
what was already open — the same two rules as QRME, for the same reason: a
billing event that declassified a year of somebody's medical history would be
the worst thing this module could do.

## Your data promise

**On Basic and Pro, no raw user data ever leaves your vault.** On the free
plan there is no vault at all, and the section above says exactly what that
means — this promise is what $20 buys.

- Biometric samples, crisis notes, journal entries, and consented context are
  sealed in your on-prem PDI vault (AES-256-GCM, tenant-isolated,
  tamper-evident audit) — JIM's own database keeps only key references.
  Never a third party.
- **You can see every access**: `GET /access-log/{user_id}` lists each time
  your sealed records were stored, read, or erased — your namespace only,
  verifiable against the audit chain.
- Prediction runs on bare local numbers (a metric name and a value); the
  payloads stay in the vault. Cloud contribution is opt-in and carries only
  anonymized guidance outcomes — condition, severity, rating. Never ids or
  notes.
- The provider portal opens only with your consent, shows condition-level
  facts only, and every handoff is revocable.
- Delete anything, anytime: `DELETE /data/{user_id}` erases every local
  trace, purges your vault records, and revokes your token.

## Condition detection (`jim/conditions.py`)

Transparent rules over a biometric sample — heart rate vs. the user's resting
baseline, respiratory rate, SpO₂, blood pressure (hypertensive-crisis
thresholds), heart-rate variability, body temperature, activity level,
movement (fall / collapse / immobility), and speech (slurred / incoherent) — plus free-text and crisis
cues, returning a condition domain and `info` / `guidance` / `critical`
severity. Domains: anxiety/panic, depression, stress management, phobias,
financial stress, relationship distress, physical distress, and physical
injury (first-aid counseling with a clear call-for-help threshold).

Two things shape detection per user:

- **Declared known conditions** lower the heart-rate threshold, so episodes
  are caught earlier for users known to be prone to them.
- **Predictive early warning** (`conditions.forecast`): a steady heart-rate
  climb that hasn't crossed a threshold yet produces a `forecast` event and a
  "may be building" insight — identifying a potential abnormality before it
  manifests. Prior samples are read back from the PDI vault when tandem
  storage is on.

## Guidance

- **Standalone** (`jim/guidance.py`): JIM generates condition-specific guidance
  through its own LLM provider, with a minimal safety check. Every reply
  carries a **factual basis** (`references`, e.g. Red Cross first-aid steps,
  NHS breathing techniques), is shaped by the user's declared conditions and
  personality preferences (a user-specific adaptation of the model), keeps
  **continuity with prior sessions** via remembered interaction state, and
  reports its **delivery channel** (`delivered_via`: the user's smart watch or
  linked device when one is paired).
- **Tandem** (`jim/qrme_client.py`): delegates to a QRME specialist profile over
  HTTP; the reply is subject to QRME's moderation and stored in QRME's per-user
  memory. If a tandem specialist is registered but no QRME endpoint is
  configured, JIM falls back to standalone guidance and says so.

## PDI tandem — medical data in the encrypted vault (`jim/pdi_client.py`)

With `JIM_PDI_URL` + `JIM_PDI_TOKEN` set (or a `PDIClient` injected), JIM's
most sensitive payloads never touch its own database in the clear:

- **medical** — raw biometric samples (`/monitor`), detection details
  (readings + signals), and check-in notes go to PDI under
  `jim/{user}/medical/…`, sealed with AES-256-GCM by PDI
- **context** — payloads from consented sources (spending, health, calendar,
  messages, …) go under `jim/{user}/context/…`
- **tandem custody** — when both tandems are configured, every exchange with a
  QRME specialist profile (the Guardian's message and the specialist's reply)
  is sealed under `jim/{user}/tandem/{qrme_profile_id}/…`; the guidance
  carries a `custody` block with the vault key, and PDI's provenance
  attributes the record to JIM Guardian. A vault outage never costs the user
  their guidance — sealing failure is reported in `custody`, not raised

JIM's SQLite keeps only `{"vaulted": true, "pdi_key": …}` references; insight
and detection rules run on the payload in memory before it is sealed, so
behavior is identical either way. Every vaulted key is tracked locally so
`DELETE /data/{user_id}` purges the PDI records too, and every vault access
lands in PDI's tamper-evident audit chain. Without PDI configured, JIM stores
data locally exactly as before. QRME runs the same pattern on its side,
vaulting profile source material — see [docs/tandem.md](docs/tandem.md).

## Cloud model — use a greater model, and contribute to it

With a [Cloud Model Gateway](docs/cloud-model.md) configured, guidance and
coaching route to the hosted tier (e.g. `claude-fable-5`) with automatic
local fallback. Users who opt in at enrollment (`cloud_contribution`)
contribute **anonymized guidance outcomes only** — condition domain,
severity, and their rating; never ids, notes, or biometrics — and can revoke
anytime. `GET /cloud/status` reports the tier.

**See exactly what would leave, and undo what did.** `GET
/users/{id}/cloud-contribution` returns `preview_next` — the actual payload,
built by the same function that builds the real send, so it cannot drift into
describing something the send does not do — alongside every item ever
contributed, verbatim. `POST …/cloud-contribution/revoke` turns it off *and*
asks the gateway to delete what already went, by each item's random `ref`. The
response reports the local and gateway halves separately: a gateway that
cannot be reached must not make the button fail, and must not let JIM claim a
deletion that never happened.

## Reaching a real clinician

The tandem hands a condition to a *synthetic* specialist. This reaches a
person. `GET /users/{id}/referral/clinicians?condition=…` maps the condition to
a care area and finds real clinicians near you; `POST …/referral/prepare` asks
QRME to assemble the summary and raise the signature that would release it
(`jim/referral.py`).

**Nothing is released by preparing.** The response carries the package — so you
read exactly what would go — and a challenge your device signs. **JIM never
holds the credential and never relays the assertion**: the signature is against
*QRME's* relying party, so the Face ID prompt belongs to QRME and the assertion
travels from your device to QRME directly. A guardian standing in the middle of
the exchange that proves you were present would defeat the point of collecting
it. JIM stores a handle, not the summary, the signature, or the link.

**Locality is a town, not a position.** `PUT /users/{id}/locality` takes a place
name you type once. The consented live-location source is deliberately not what
this reads — position is a stream, and matching a clinic needs a place.

Expertise filters and geography only ranks: a nearer clinician is never
substituted for the right one.

## Handing a specialist a task

Tandem guidance sends one message and gets one reply. For work with several
steps — *"read what we have, draft the summary, hold it until somebody
confirms"* — `POST /users/{id}/specialist-tasks` hands a QRME specialist a
**workflow** instead (`jim/handoff.py`), advanced with `…/{task}/advance` and
readable later with `GET …/specialist-tasks/{task}`.

Deliberately **not on the emergency path**: escalation decides in one call and
must keep doing so, so nothing here is reachable from `monitor`. Starting one
is explicit — a detection can warrant a handoff, a person starts it. JIM keeps
the task's **status only**; the drafts stay in QRME under its own moderation
and your capability token. A specialist whose owner has not enabled delegation
answers plainly rather than failing, and a narrower policy narrows the plan
rather than refusing it.

## Physical embodiments & sessions

![JIM-mini physical embodiments](assets/embodiments.svg)

## Life layer (`jim/life.py`, `jim/coach.py`)

![JIM-mini life layer](assets/life-layer.svg)

The guardrail is consent: context only flows from sources the user has
switched on, and `DELETE /data/{user_id}` erases everything on request.
Insight rules are deliberately transparent (a spending threshold, sleep-hours
bands, calendar keywords, mood ≤ 2, streak milestones) rather than opaque
scoring. The coach shares Guardian's LLM provider and safety net, and check-in
notes feed the same crisis detection as biometric monitoring.

## Out of scope for v1

Live device streaming/pairing, real bank/brokerage connections (spending
events are ingested, (non-auto and auto-investing), voice mode, AR visualizations,
image insights, community challenges, real emergency-services dispatch, and a
specialist knowledge-pack marketplace — represented structurally, not as live
integrations.

**Not built** for [care beacons](docs/beacons.md): a transport of JIM's own
— it posts a signed envelope to `JIM_NOTIFY_URL` and stops, so the SMS gateway
or pager behind it is the deployment's — and a scheduling product.
`jim/rota.py` knows people, days, hours and the site's timezone; it does not
know leave, swaps or fairness.

## Related projects

Three separate products, each standalone, interoperating only over HTTP —
see [docs/tandem.md](docs/tandem.md) for the full architecture:

- [**qrme**](https://github.com/davidsbianchi1984/qrme) — AI synthetic
  profiles: relationship-aware, remembered, moderated.
- [**jim-mini**](https://github.com/davidsbianchi1984/jim-mini) — Guardian
  personal guidance: monitor, predict, guide, escalate; can delegate
  specialist guidance to QRME.
- [**pdi**](https://github.com/davidsbianchi1984/pdi) — Private Data
  Infrastructure: the encrypted vault both AI systems can run on top of.

## Reference

Everything below is lookup material — how to run it, what to configure, what
the endpoints are. It is at the bottom on purpose: if you see a command in one
of the screens above and want to know what it does, this is where to find it.

### Run

```bash
pip install -e .[dev]
uvicorn jim.api:app            # standalone
JIM_QRME_URL=http://localhost:8000 uvicorn jim.api:app   # tandem with QRME
JIM_PDI_URL=http://localhost:8100 JIM_PDI_TOKEN=pdi_... uvicorn jim.api:app  # + PDI vault
```

`JIM_DB` sets the SQLite path (default `jim.db`). Set `ANTHROPIC_API_KEY` for
real `claude-opus-5` guidance; otherwise (or with `JIM_LLM=stub`) a
deterministic stub answers offline. `JIM_MODEL` overrides the model.

### Run it on your phone

The console is a web app, so a phone on the same Wi-Fi runs it straight from
this backend — no app store, no second server, nothing to configure on the
phone.

```bash
python -m jim          # the launcher menu: choose your device
python -m jim phone    # straight to the phone flow
```

Bare `python -m jim` prints the launcher menu — every way to run the
Guardian, one command each, so you pick per device: **phone** (this
section), **desktop** (`python -m jim desktop`, the Electron app on this
PC), **packaged installer** (`.dmg`/`.exe`/`.AppImage` from the releases
page — no toolchain needed), or **headless API** (`python -m jim serve`).
Same backend, same data, same token checks in every form.

The packaged installer is **double-click-and-done**: it ships the whole
Python backend as a frozen binary (`packaging/backend_entry.py`, built by
PyInstaller in the release workflow) and the app spawns it at launch when no
backend is already answering — no Python install, no terminal, data under
the app's own user-data directory, and the spawned backend dies with the
window. A backend you already run yourself is left alone.

`python -m jim phone` builds the console if it's missing (first run installs the
npm dependencies too), prints the phone URL **with a QR code right in the
terminal**, and starts the API on the network — scan, Add to Home Screen,
done. Flags: `--port`, `--rebuild`, `--no-build`, `--print-only`.

The manual equivalent, if you prefer the steps separately:

```bash
npm --prefix app install && npm --prefix app run build   # build the console once
uvicorn jim.api:app --host 0.0.0.0                       # listen on the network
curl localhost:8000/pair                                 # what to open on the phone
```

`GET /pair` answers with the console's URL on your local network (and
`GET /pair/qr.svg` is the same URL as a QR code — the Privacy screen shows
both, so you can scan it off the laptop). Open that URL on the phone, then
**Add to Home Screen**: it installs as a standalone app with its own icon,
runs full-screen, and keeps working through a brief drop in connectivity.

Why it needs no setup: the API serves the console at `/app`, so the UI and
the API share one origin — the console simply calls the address it was loaded
from. The phone layout follows: the sidebar becomes a thumb-reachable bottom
tab bar, inputs stay at 16px so iOS doesn't zoom, and the layout respects the
notch and home indicator.

#### Published deployments

The same code serves a laptop on Wi-Fi and an instance you host for
yourself and colleagues to reach from anywhere — useful for troubleshooting
from a phone when you are not on the same network:

<table>
<tr><th align="left"><sub>Variable</sub></th><th align="left"><sub>Effect</sub></th></tr>
<tr><td valign="top"><sub><code>JIM_PUBLIC_URL</code></sub></td><td valign="top"><sub><code>GET /pair</code> advertises this address (QR included) instead of a LAN one, so the phone flow works over the internet. <b>Serve it over HTTPS</b> — user tokens travel in headers and this is health data.</sub></td></tr>
<tr><td valign="top"><sub><code>JIM_SIGNUP_KEY</code></sub></td><td valign="top"><sub>Enrolling requires this key as the <code>x-signup-key</code> header, so a published instance stays yours rather than open registration. Unset = open, the right default on a LAN.</sub></td></tr>
</table>

The key gates *creating an account here*: anyone already enrolled keeps
working, and a parent adding a child is authorized by their own token.

The `Dockerfile` packages the console and the API into one image so a hosted
instance serves both from the same origin, exactly like the phone flow does:

```bash
docker build -t jim-mini .
docker run -p 8200:8200 -v jim-data:/data \
  -e JIM_PUBLIC_URL=https://guardian.example.com \
  -e JIM_SIGNUP_KEY="$(openssl rand -base64 24)" jim-mini
```

[docs/hosting.md](docs/hosting.md) covers the rest — TLS (browsers refuse
geolocation without it, so escalation needs it), what mounting `/data`
protects, and what holding other people's health data commits you to.

Without `JIM_PUBLIC_URL`, the address is local-network only and deliberately
not reachable from the internet — your health data stays on your own
network. Everything still
requires your bearer token; a phone on the LAN is exactly as authorized as a
laptop on the LAN. If `/pair` reports `reachable: false`, it could only find
loopback (which on a phone means the phone itself): set `JIM_LAN_HOST` to
this machine's address and restart.

### API

<table>
<tr><th align="left"><sub>Endpoint</sub></th><th align="left"><sub>Purpose</sub></th></tr>
<tr><td valign="top"><sub><code>GET /health</code></sub></td><td valign="top"><sub>Status + whether tandem is configured</sub></td></tr>
<tr><td valign="top"><sub><code>POST /enroll</code></sub></td><td valign="top"><sub>Enroll a user: terms/guardian consent, emergency contact (+ consent), devices, resting-HR baseline, goals, declared known conditions. <code>anonymous: true</code> enrolls under a <b>pseudonym</b> and the typed name is discarded — the app never learns it (spec [0031] / FIG. 2 box 212). An optional <code>legal_name</code> is then used <i>only</i> in an emergency briefing; without one the briefing says no legal name is on record rather than passing a pseudonym off as an identity</sub></td></tr>
<tr><td valign="top"><sub><code>GET /community/{user_id}</code>, <code>POST</code>/<code>GET …/visits</code></sub></td><td valign="top"><sub>The <b>community door</b> — FIG. 2 boxes 222–226 and [0020]'s "chat engines, your local events, and forums in all languages". All of it lives in <b>QRME</b>, where the moderation, the rooms and the languages already are, so JIM shows the door rather than growing a second social network inside a private health guardian: QRME's active rooms (topic, channel, heads, an openable URL) and the places its listings actually claim, filtered by <code>?locality=</code>, in the language this user reads. Nothing is mirrored here, nothing is posted on your behalf, and no health data crosses over — the reply says so in its own <code>posture</code> block. Opening a door records <b>the fact only</b> on your timeline, never anything from inside the room. 409 without <code>JIM_QRME_URL</code>; an unreachable QRME is a quiet screen. Console: the <b>Community</b> tab</sub></td></tr>
<tr><td valign="top"><sub><code>GET /anonymity/{user_id}</code></sub></td><td valign="top"><sub>What anonymity keeps (every emergency path, your own history and vault records) and what it costs (a legal name for responders, unless you left one) — so the checkbox is an informed choice, not a surprise</sub></td></tr>
<tr><td valign="top"><sub><code>POST /guardians/{gid}/children</code>, <code>GET …/children</code>, <code>GET</code>/<code>DELETE …/children/{cid}</code></sub></td><td valign="top"><sub><b>Family</b> (<code>jim/family.py</code>): a verified-adult guardian enrolls their child — consent recorded as a relationship (who, as what, when, on the child's timeline), protective defaults (cautious sensitivity, the guardian as consented emergency contact, cloud/provider sharing hard-off), and the child's device token shown once. Oversight is sized by age: <b>full</b> under 13 (condition-level timeline, never raw notes), <b>alerts-only</b> 13–17 (escalations reach the parent; a teen's check-ins and everyday guidance stay private), and it <b>ends by itself at 18</b>. The autonomous-resuscitation waiver can never be signed for a minor — not by the minor and not by a guardian</sub></td></tr>
<tr><td valign="top"><sub><code>PUT …/children/{cid}/controls</code>, <code>GET /guardians/{gid}/watch</code></sub></td><td valign="top"><sub><b>Family controls & the parent's wrist</b>: pause and quiet hours (HH:MM, midnight-wrapping) hold <i>everyday</i> guidance only — detection, crisis escalation, and the emergency path never pause, and a held delivery is an audited <code>guidance_held</code> event. The guardian watch face shows one light per child from the last 24h of alert-level events (green quiet · orange escalated · red critical) with <code>haptic: alert</code> when a child needs someone — alert-level only, so teen privacy holds by construction. With a PDI vault configured, the guardian-consent record is sealed there (<code>jim/{child}/family/consent/…</code>) for provable custody</sub></td></tr>
<tr><td valign="top"><sub><code>POST /conditions/{user_id}</code></sub></td><td valign="top"><sub>Declare a known condition after enrollment ("receiving an indication of a known condition"); detection is sensitized for it</sub></td></tr>
<tr><td valign="top"><sub><code>PUT /personality/{user_id}</code></sub></td><td valign="top"><sub>Adapt the counselor from user input — tone and free-text preferences shape every guidance and coach prompt. Plus the two dials spec [0019] asks for: <code>beliefs_posture</code> (<code>neutral</code>, the default and always stated, or <code>sensitive</code> with the user's own declared <code>beliefs</code> — never inferred) and <code>explain_level</code> (<code>plain</code> / <code>standard</code> / <code>technical</code>, for "a user's general intelligence or ability to quickly grasp and apply guidance"). The coach also refines tone <b>autonomously</b>: "keep it short" in a prompt is remembered as a preference from that turn on, and the reply says what it learned (<code>adapted_tone</code>)</sub></td></tr>
<tr><td valign="top"><sub><code>GET /followup/{user_id}</code>, <code>POST /followup/{user_id}</code></sub></td><td valign="top"><sub><b>Did the counseling work?</b> — spec [0039]'s closing edge. Every delivered guidance opens a follow-up; answering <code>helped: true</code> records it and monitoring resumes, and <code>helped: false</code> re-runs the escalation ladder with the <b>ineffective-guidance rung</b> (one tier up, floored at <code>check_in</code>) and names the humans reachable now — the deployment's own support person, the crisis line for a psychological condition, whoever is on shift, and the emergency contact. A rung and not a jump: an unhelped breathing exercise must reach a person, and must not dispatch an ambulance on its own; an unhelped <i>critical</i> event, already at <code>notify_contact</code>, goes to emergency services</sub></td></tr>
<tr><td valign="top"><sub><code>POST /adaptation/{user_id}</code>, <code>GET /adaptation/{user_id}</code></sub></td><td valign="top"><sub>The <b>user-specific model</b> of claim 11: an offline pass derives an adaptation profile from this user's own stored history — declared conditions, check-in trend, the areas they actually bring, the tone they asked for, and <b>which guidance actually helped them</b> from the follow-up record — then seals it in the PDI vault when a tandem is configured (the claim's "secure, decentralized methods"; nothing goes to a model vendor). Confidence is earned from evidence volume, never from fluency, and the profile conditions prompts only where the evidence supports it — three answered follow-ups before "this works for you" is a claim. Honest in its own <code>method</code> field that the transformer's weights are the vendor's and are not modified here</sub></td></tr>
<tr><td valign="top"><sub><code>PUT /sensitivity/{user_id}</code></sub></td><td valign="top"><sub>Tune escalation readiness: <code>cautious</code> (lower HR thresholds; a declared condition reaches the emergency contact even at guidance level) / <code>balanced</code> (default) / <code>assertive</code> (stronger signals required)</sub></td></tr>
<tr><td valign="top"><sub><code>GET /baseline/{user_id}</code></sub></td><td valign="top"><sub>The user's rolling per-metric EMA baselines; each is provisional until enough resting samples accrue</sub></td></tr>
<tr><td valign="top"><sub><code>POST /specialists</code></sub></td><td valign="top"><sub>Register a condition specialist — <code>local</code> (JIM's own guidance) or <code>tandem</code> (a QRME <code>qrme_profile_id</code>)</sub></td></tr>
<tr><td valign="top"><sub><code>GET /specialists</code>, <code>POST /specialists/seed</code></sub></td><td valign="top"><sub>List the registry, or seed the <b>starter specialists</b> — a named domain expert for every condition (<code>jim/seed.py</code>, also <code>python -m jim.seed</code>), so guidance carries a <code>specialist</code> attribution from day one. Idempotent: covered conditions are skipped, operator overrides survive re-seeding</sub></td></tr>
<tr><td valign="top"><sub><code>POST /specialists/seed/tandem</code></sub></td><td valign="top"><sub>The <b>tandem hookup</b>: wire starter specialists to their QRME Starter Collection counterparts (<code>financial_stress</code> → <code>@marcus_bell</code>, <code>physical_distress</code> → <code>@dr_amara_osei</code>, <code>anxiety</code> → <code>@dr_lena_whitcomb</code>, <code>depression</code> → <code>@dr_marcus_adeyemi</code>, <code>relationship</code> → <code>@dr_priya_nair</code>), resolving each @handle live against the connected QRME deployment — ids differ per deployment, handles are the stable cross-product names. Existing tandem links are kept; unresolved handles stay local; crisis escalation always runs through JIM's own tree regardless of routing; 409 without <code>JIM_QRME_URL</code>. <code>python -m jim.seed</code> runs it automatically when <code>JIM_QRME_URL</code> is set</sub></td></tr>
<tr><td valign="top"><sub><code>GET /specialists/catalog</code></sub></td><td valign="top"><sub>The <b>attach bracket</b>'s stock: every condition beside its current attachment, plus the QRME <b>Starter Collection</b> discovery cards (faces, industries, blurbs — each starter already carries its industry's knowledge pack profile-side) so the Care Team tab can offer click-to-attach per condition. 409 without <code>JIM_QRME_URL</code>; an unreachable marketplace yields an empty shelf, never an error page</sub></td></tr>
<tr><td valign="top"><sub><code>POST /monitor/{user_id}</code></sub></td><td valign="top"><sub>Ingest a biometric/context sample (optionally tagged with its <code>source_device</code> — smart watch, stationary system, neural sensor, gesture interface); runs detect → guide → escalate, with predictive early warning when nothing has manifested yet. Physical emergencies carry <b>step-by-step first aid</b>: CPR with the proper pace (30:2, 110/min, cued by green/red lights + a metronome tick), AED guidance on a fibrillation rhythm, the low-blood-oxygen playbook (breathe deeply, fresh air, medical attention), environmental hazards (smoke/CO — leave now), and ergonomic-strain nudges; critical escalations dispatch alerts to every registered connected device</sub></td></tr>
<tr><td valign="top"><sub><code>GET /watch/channel/{user_id}</code>, <code>POST …/rotate</code>, <code>POST /watch/drip/{token}</code>, <code>POST /watch/seed/{user_id}</code></sub></td><td valign="top"><sub>The <b>Apple Watch bridge</b> — readings reach JIM without an App-Store app. The setup card carries a tokened <b>drip URL</b> an iPhone <b>Shortcuts automation</b> POSTs Health samples to (forgiving payload: <code>heartRate</code>, <code>"72 count/min"</code>, SpO₂ as a fraction all understood); every drip runs the full detect → drift → escalate pipeline, and the reply is deposit-only — counts, never guidance, since the token rides in a URL. <code>seed</code> takes the Health app’s <b>export.zip</b> and folds per-day medians into the baselines — months of watch history become an established baseline on day one, writing no events and raising no check-ins (exercise heart-rate records are excluded by motion context). Rotating the token retires a leaked URL in one tap</sub></td></tr>
<tr><td valign="top"><sub><code>GET|POST /meds/{user_id}</code>, <code>PUT|DELETE …/{med_id}</code>, <code>POST …/{med_id}/log</code>, <code>GET …/adherence</code></sub></td><td valign="top"><sub>The <b>medicine cabinet</b> — what the user takes, in their own words (“the little white one, 10 mg” is a valid name and dose). The day's board knows done, due, and missed with humane grace (9:07 is not “missed” for the 8:00 pill); one slot has one correctable answer (skipped → taken happens: people find the pill in their pocket); an as-needed ceiling <b>refuses to log past itself</b> and points at the prescriber. A missed dose — even one marked critical — is a check-in and a line in the coach's context, never an alarm: this module has no path into the escalation ladder. Every dose logged is a sign of life the vigil counts. And JIM is not a pharmacist: no interaction checker, and the board says so on its face</sub></td></tr>
<tr><td valign="top"><sub><code>PUT|GET|DELETE /users/{user_id}/care-team</code>, <code>POST …/care-team/coordinate</code>, <code>GET …/care-team/plans</code></sub></td><td valign="top"><sub>The <b>care team is an organization</b> (QRME's operational ecosystem, tandem mode) — the user links their own QRME org and names the desk that speaks for the Guardian, pasting <i>their own</i> owner token knowingly (QRME's org routes are owner-only and JIM never sneaks around that; unlinking deletes the credential). When concerns <b>stack</b> — a drift-band crossing arriving while a medication's adherence is below 75% — the Guardian takes the situation to the whole team as one coordination goal and the joint plan lands back as a care plan. Summaries cross, never raw readings; at most once a day; calm path only — anything <code>conditions.detect</code> flags is already on the escalation ladder, which no coordination replaces</sub></td></tr>
<tr><td valign="top"><sub><code>POST /sessions/{user_id}</code>, <code>POST …/{session_id}/end</code></sub></td><td valign="top"><sub>Login sessions per device; starting one returns the remembered interaction state, so any device resumes the same conversational thread and counseling routes to the session's device. <b>Cross-product continuity</b>: if the user already has a thread with a QRME specialist, the session's <code>continuity</code> block carries its recent turns (read back with the stored QRME interactor token) — a chat begun in QRME picks up on any JIM embodiment, same thread, same memory</sub></td></tr>
<tr><td valign="top"><sub><code>POST</code>/<code>GET /devices/{user_id}</code></sub></td><td valign="top"><sub>Physical embodiments: wearables, stationary systems, and networked autonomous devices — transport (e.g. Bluetooth, relayed through a linked device) and an optional on-device LLM; guidance reports how and where it was delivered</sub></td></tr>
<tr><td valign="top"><sub><code>GET /custody/{user_id}</code>, <code>GET …/provenance?key=</code></sub></td><td valign="top"><sub>The <b>custody viewer</b>: list the user's sealed tandem exchanges (QRME specialist chats sealed in the PDI vault) with the audit-chain status, and read PDI's full provenance trail for any one of them — origin, seal details, audit history. Scoped strictly to the user's own <code>jim/{user}/tandem/…</code> records; 409 without a PDI vault configured</sub></td></tr>
<tr><td valign="top"><sub><code>POST /emergency/{user_id}</code></sub></td><td valign="top"><sub><b>Emergency mode</b> — one coordinated response (the watch's Emergency screen): reach <b>emergency services</b>, <b>share location</b> with family and responders, <b>contact family</b> (the registered emergency contact), surface the <b>Medical ID</b> (age, known conditions, resting-HR baseline, recent detections, contact — condition-level facts only), deliver step-by-step <b>AI first aid</b> from an optional live <code>sample</code>/<code>situation</code> (CPR/AED/low-oxygen playbooks), and <b>alert every connected device</b>. Logged to the event timeline</sub></td></tr>
<tr><td valign="top"><sub><code>POST</code>/<code>DELETE /medical-id/qr/{user_id}</code></sub></td><td valign="top"><sub><b>Shareable Medical ID QR</b>: mint (or rotate) a printable / lock-screen QR, or revoke it. Returns the card token + its <code>view_url</code> and <code>qr_svg_url</code></sub></td></tr>
<tr><td valign="top"><sub><code>GET /medical-id/{token}</code>, <code>GET …/{token}/qr.svg</code></sub></td><td valign="top"><sub><b>Scan-to-view</b> (public): a first responder scans the code and reads the Medical ID with <b>no auth token</b> — the phone is locked in an emergency, so the card itself is the credential. Condition-level facts only; the token is opaque, rotatable, revocable, and stored only as a hash</sub></td></tr>
<tr><td valign="top"><sub><code>POST</code>/<code>GET /users/{id}/beacons</code>, <code>DELETE /beacons/{id}</code></sub></td><td valign="top"><sub><b>Care beacons</b> (<a href="docs/beacons.md">docs/beacons.md</a>): a printed QR on the <i>things around</i> a watched person — a fridge door, a wristband, a walker. Distinct from the Medical ID above, which travels with the person and is <i>read</i>; a beacon stays with a place and is <b>rung</b>. A minor's is guardian-issued only</sub></td></tr>
<tr><td valign="top"><sub><code>GET /c/{id}</code>, <code>GET …/qr.svg</code></sub></td><td valign="top"><sub><b>Stage one</b> (public): a first name, one sentence, and a button. <b>Never</b> how the person is and never where they are — <i>is this person OK right now</i> is precisely what a stalker is asking, so a beacon reports watch status and never subject status</sub></td></tr>
<tr><td valign="top"><sub><code>POST /c/{id}/alarm</code></sub></td><td valign="top"><sub><b>The bell</b> (public). Raising the alarm is what turns a passer-by into a responder, and <b>that</b> is what earns them the Medical ID — the order QRME's desk beacon runs in reverse, because health is not a shop sign. Capped at <code>notify_contact</code>: a stranger's tap must never dispatch an ambulance. Inside the cooldown a second finder <b>joins</b> the open alarm rather than being dropped. A minor's beacon never opens the clinical stage, to anyone</sub></td></tr>
<tr><td valign="top"><sub><code>GET /users/{id}/alarms</code>, <code>POST …/clear</code></sub></td><td valign="top"><sub>Who rang while they were away — their token only</sub></td></tr>
<tr><td valign="top"><sub><code>GET /relay/roster</code>, <code>GET /users/{id}/incidents</code></sub></td><td valign="top"><sub><b>Workplace relay</b> for lone and remote workers: <code>notify_contact</code> assumes a contact who answers, which at 2am on a single-staffed site may be nobody. Incidents are <b>incident scope, never person scope</b> — the employer bought the deployment, which does not entitle them to what is inside it</sub></td></tr>
<tr><td valign="top"><sub><code>POST …/alarms/{id}/escalate</code>, <code>…/accept</code></sub></td><td valign="top"><sub>Works the rota — <b>whoever is on shift first</b> — and confirms a human <b>accepted</b>; accepting means attending, not resolved. Actually sends the page, and when it did not land says <code>reached_somebody: false</code> and <code>escalate_again_now</code> rather than waiting on an acceptance that cannot come. Rota exhausted is reported, not silent, and still no dispatch</sub></td></tr>
<tr><td valign="top"><sub><code>GET /relay/rota</code>, <code>GET /relay/channel</code>, <code>GET /users/{id}/pages</code></sub></td><td valign="top"><sub>Who would be paged <b>right now</b>, whether a page can go out at all, and which pages never landed. Shifts crossing midnight belong to the day they started — the 18:00–06:00 case the flat roster always got wrong</sub></td></tr>
<tr><td valign="top"><sub><code>POST /alarms/{id}/guidance</code></sub></td><td valign="top"><sub>What to tell whoever is waiting — routed to a QRME first-aid specialist when tandem is configured, else the one instruction that never depends on a model being reachable. <b>Public, and the reason is the whole design</b>: <i>the person standing over a colleague has no account and needs an answer in ninety seconds</i>. Its door is therefore <b>the scanned beacon page</b> rather than a console screen — that reader is holding a phone they pointed at a sticker. Offered whether or not the Medical ID opened, so a minor's beacon, which never opens the clinical stage to anybody, still tells the finder what to do</sub></td></tr>
<tr><td valign="top"><sub><code>POST /activity/{user_id}</code></sub></td><td valign="top"><sub><b>Ambient observation</b> (the "Jiminy Cricket" jump-in): report what the user is <i>doing</i> — activity + signals (<code>retries</code>/<code>errors</code>, <code>idle_seconds</code>, <code>duration_min</code>) + what they said — and JIM offers help <b>proactively</b> when a struggle is building, before being asked. Crisis language still escalates; a calm signal is logged but never interrupts</sub></td></tr>
<tr><td valign="top"><sub><code>GET /events/{user_id}</code></sub></td><td valign="top"><sub>Event timeline (biometric/activity → detection → guidance → escalation)</sub></td></tr>
<tr><td valign="top"><sub><code>GET</code>/<code>PUT /sources/{user_id}</code></sub></td><td valign="top"><sub>Per-source consent (wearable, health, calendar, spending, bank, messages, location) — nothing is read from a source the user hasn't allowed</sub></td></tr>
<tr><td valign="top"><sub><code>POST /context/{user_id}</code></sub></td><td valign="top"><sub>Ingest an event from a consented source (403 otherwise); transparent rules turn it into insights</sub></td></tr>
<tr><td valign="top"><sub><code>POST /checkin/{user_id}</code></sub></td><td valign="top"><sub>Mood & energy check-in; a worrying note still runs the full Guardian detect → escalate pipeline</sub></td></tr>
<tr><td valign="top"><sub><code>GET</code>/<code>POST /goals/{user_id}</code>, <code>PATCH /goals/{user_id}/{goal_id}</code></sub></td><td valign="top"><sub>Smart goals with progress; completion earns a praise insight</sub></td></tr>
<tr><td valign="top"><sub><code>GET</code>/<code>POST /habits/{user_id}</code>, <code>POST …/{habit_id}/log</code></sub></td><td valign="top"><sub>Habit tracking with streaks; milestones (7/30/100 days) earn insights</sub></td></tr>
<tr><td valign="top"><sub><code>POST</code>/<code>GET /coach/{user_id}</code></sub></td><td valign="top"><sub>24/7 life coach across <code>mental_health</code>, <code>health_fitness</code>, <code>career</code>, <code>finance</code>, <code>relationships</code>, <code>personal_growth</code>, grounded in recent check-ins and active goals</sub></td></tr>
<tr><td valign="top"><sub><code>POST /companion/{user_id}</code></sub></td><td valign="top"><sub>Ambient companion check-in: the coach reaches out first, grounded in the latest mood, goals, and personality preferences — invoked explicitly, never on a hidden schedule</sub></td></tr>
<tr><td valign="top"><sub><code>GET /insights/{user_id}</code></sub></td><td valign="top"><sub>Proactive nudges: spending alerts, sleep praise, interview prep, mindful-break suggestions, milestones</sub></td></tr>
<tr><td valign="top"><sub><code>POST</code>/<code>GET /journal/{user_id}</code></sub></td><td valign="top"><sub>Journaling; entries are vaulted under PDI tandem and run the same crisis pipeline as check-in notes</sub></td></tr>
<tr><td valign="top"><sub><code>POST /feedback/{user_id}</code></sub></td><td valign="top"><sub>Continuous-improvement loop: rate guidance up/down with an optional note</sub></td></tr>
<tr><td valign="top"><sub><code>POST</code>/<code>GET /improve</code></sub></td><td valign="top"><sub><b>Help us improve</b>: product feedback on the app itself (idea/improvement/bug/praise + optional 1–5 rating), open to anyone; a submitter sees only their own words plus the public per-category tally</sub></td></tr>
<tr><td valign="top"><sub><code>GET /report/{user_id}</code></sub></td><td valign="top"><sub>Progress report & insights: mood/energy averages, goals, streaks, detection counts, feedback tallies</sub></td></tr>
<tr><td valign="top"><sub><code>GET /access-log/{user_id}</code></sub></td><td valign="top"><sub><b>See who accessed my data</b>: every access to the user's sealed vault records (stored/read/erased + scope + time), filtered to their own <code>jim/{user}/…</code> namespace and verifiable against PDI's tamper-evident audit chain; says so plainly when no vault is configured (data local-only)</sub></td></tr>
<tr><td valign="top"><sub><code>GET /provider/{user_id}</code></sub></td><td valign="top"><sub>Consent-gated provider portal: condition-level summary only (declared conditions, detection history, escalations) — never notes or raw biometrics</sub></td></tr>
<tr><td valign="top"><sub><code>DELETE /data/{user_id}</code></sub></td><td valign="top"><sub>Delete anything, anytime — erases every trace of the user</sub></td></tr>
</table>

### Configuration

<table>
<tr><th align="left"><sub>Variable</sub></th><th align="left"><sub>Default</sub></th><th align="left"><sub>Purpose</sub></th></tr>
<tr><td valign="top"><sub><code>JIM_DB</code></sub></td><td valign="top"><sub><code>jim.db</code></sub></td><td valign="top"><sub>SQLite database path</sub></td></tr>
<tr><td valign="top"><sub><code>JIM_LLM</code></sub></td><td valign="top"><sub>auto</sub></td><td valign="top"><sub><code>stub</code> forces the offline deterministic provider; <code>anthropic</code> forces the SDK</sub></td></tr>
<tr><td valign="top"><sub><code>JIM_MODEL</code></sub></td><td valign="top"><sub><code>claude-opus-5</code></sub></td><td valign="top"><sub>Model used for guidance and coaching</sub></td></tr>
<tr><td valign="top"><sub><code>ANTHROPIC_API_KEY</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Enables real model replies</sub></td></tr>
<tr><td valign="top"><sub><code>JIM_QRME_URL</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>QRME tandem: delegate specialist guidance over HTTP</sub></td></tr>
<tr><td valign="top"><sub><code>JIM_PDI_URL</code> / <code>JIM_PDI_TOKEN</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>PDI tandem: seal medical, <b>financial</b> and context payloads in the encrypted vault — every consented source goes through one namespace and one gate (<a href="docs/tandem.md#qrme--jim-mini--pdi">docs/tandem.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>JIM_CLOUD_URL</code> / <code>JIM_CLOUD_TOKEN</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Cloud Model Gateway: greater-model guidance with local fallback + opt-in contribution (<a href="docs/cloud-model.md">docs/cloud-model.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>JIM_SITE_ROTA</code> / <code>JIM_SITE_TZ</code></sub></td><td valign="top"><sub>— / <code>UTC</code></sub></td><td valign="top"><sub>Workplace relay: who is on shift, in JSON, evaluated in the site's own timezone (<a href="docs/beacons.md#who-is-on-and-reaching-them">docs/beacons.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>JIM_SITE_ROSTER</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>The older, flat form — plain names, always on. Still supported</sub></td></tr>
<tr><td valign="top"><sub><code>JIM_NOTIFY_URL</code> / <code>JIM_NOTIFY_SECRET</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Where an escalation is actually delivered; signed HMAC-SHA256. Unset = queued, and the escalation says nobody was reached</sub></td></tr>
</table>

### Test

```bash
pytest jim/tests
```

Covers standalone detection/guidance/escalation and a real in-process tandem
run against a separate QRME instance (reached only through the HTTP client).

## License

MIT © 2026 David Bianchi — see [LICENSE](LICENSE).

---

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
