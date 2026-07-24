# JIM-mini (Guardian) Terms of Service

*Version 1.0 — effective 2026-07-24. Served by the API at `GET /terms`;
acceptance is required to enroll and is recorded (version + timestamp) on
the account. This is a template maintained with the product — have counsel
review and localize it before commercial launch.*

**By enrolling in or using JIM-mini (the "Service"), you agree to these
Terms. If you do not agree, do not use the Service.**

## 1. Not a medical device — the most important section

1.1 The Service is a **wellness and personal-guidance tool**. It is **not a
medical device**, is not FDA-cleared or -approved, and does not diagnose,
treat, cure, or prevent any disease or condition. Its monitoring,
predictions, guidance, coaching, and first-aid playbooks are **educational
support, not medical advice**, and no doctor–patient or
therapist–client relationship is formed.

1.2 **In an emergency, call your local emergency number (911 in the US)
immediately — before, or instead of, anything in this app.** In mental
health crisis, call or text **988** (US). The Service's escalation features
are a best-effort supplement to — never a substitute for — emergency
services, and may fail due to connectivity, device, sensor, or service
conditions.

1.3 Detection can be wrong in both directions: the Service may miss a real
event (false negative) or flag a non-event (false positive). Baselines,
thresholds, and sensitivity settings are heuristics, not guarantees. Do not
delay seeking professional care because of anything the Service says or
does not say.

## 2. Assumption of risk and release (waiver)

2.1 **You knowingly and voluntarily assume all risks** of using the
Service, including reliance on AI-generated guidance, biometric monitoring
inaccuracy, notification or escalation failure, interactions with tandem
AI specialists, and the operation of connected devices and robot
responders within their command allowlists.

2.2 To the maximum extent permitted by law, you **release, waive, and
discharge** the Service operator, its owners, employees, and licensors
(the "Released Parties") from any and all claims arising out of or related
to your use of the Service — including guidance content, missed or false
detections, escalation outcomes, first-aid coaching, and robot-assisted
response — except where caused by the Released Parties' gross negligence
or willful misconduct, or where such a release is not permitted by law.

2.3 **Robot-assisted resuscitation.** Confirm-gated robot first aid
(fetching an AED, coaching a playbook, compressions only after a person on
scene confirms) operates under this Section. **Fully autonomous
resuscitation (automatic CPR start, fully automatic AED operation) never
operates under these Terms alone** — it requires the separate, signed
autonomous-resuscitation waiver (`GET /waivers/{user}`), which can never
be signed for a minor. A robot never delivers a defibrillation shock; the
AED analyzes and a human presses the button.

## 3. Parents, guardians, and minors

A parent/guardian who enrolls a child accepts these Terms on the child's
behalf, confirms their authority to do so, and accepts the documented
oversight model (age-scaled visibility that ends at 18; safety monitoring
that never pauses). Minors' accounts always run with protective defaults.

## 4. Your responsibilities

Provide accurate enrollment information (age, conditions, emergency
contacts); keep your device charged, connected, and worn as directed if
you rely on monitoring; keep emergency-contact details current; and do not
use the Service for anyone without their (or their guardian's) consent.

## 5. Health data & privacy

Your health data is handled as described in the HIPAA posture document
(docs/hipaa-baa.md): sealed at rest in the PDI vault when configured,
access-logged, user-visible, and erasable. You may delete everything at
any time (`DELETE /data/{user}`); erasure also revokes your token.

## 6. Disclaimer of warranties

THE SERVICE IS PROVIDED **"AS IS" AND "AS AVAILABLE"** WITHOUT WARRANTIES
OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE, ACCURACY, OR UNINTERRUPTED OR ERROR-FREE OPERATION.

## 7. Limitation of liability

TO THE MAXIMUM EXTENT PERMITTED BY LAW, THE RELEASED PARTIES SHALL NOT BE
LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, EXEMPLARY, OR
PUNITIVE DAMAGES, OR FOR PERSONAL INJURY OR DEATH TO THE EXTENT ARISING
FROM RELIANCE ON THE SERVICE IN LIEU OF EMERGENCY OR PROFESSIONAL CARE.
THE RELEASED PARTIES' AGGREGATE LIABILITY FOR ALL CLAIMS SHALL NOT EXCEED
THE GREATER OF (A) AMOUNTS YOU PAID FOR THE SERVICE IN THE TWELVE MONTHS
BEFORE THE CLAIM OR (B) US $100. Some jurisdictions do not allow certain
limitations; these apply to the fullest extent permitted.

## 8. Indemnification

You will defend, indemnify, and hold harmless the Released Parties from
claims arising out of your misuse of the Service, enrollment of another
person without authority, or breach of these Terms.

## 9. Termination; changes

We may suspend or terminate access for breach, and may update these Terms
by publishing a new version at `GET /terms`; continued use after the
effective date is acceptance.

## 10. Governing law; disputes

`[GOVERNING LAW / VENUE / ARBITRATION CLAUSE — set by counsel]`

---

*Related: the autonomous-resuscitation waiver (a separate signed
instrument, per §2.3), the HIPAA posture (docs/hipaa-baa.md), and the
safety architecture — crisis escalation that never pauses, hand-translated
safety content, provenance-cited guidance — documented in the README.*
