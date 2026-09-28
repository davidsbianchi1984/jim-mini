# Bot Account Cleaner

Flags bots, fake accounts and cloned impersonators in your **friends, followers and following** lists on X, Facebook, Instagram, TikTok and LinkedIn, then helps you remove them. It never asks for your social media password. A separate **Platform Purge Console** lets platform owners purge bots from their whole service. Every action there is reversible, sends the user a notice, and can be appealed.

This is a standalone app inside this repository. It shares no code with JIM-mini.

## Run it

```bash
cd botcleaner
pip install -e .[dev]
python -m botcleaner --port 8000        # http://localhost:8000  (Personal Cleaner)
                                        # http://localhost:8000/console  (Purge Console)
pytest -q                               # 66 tests, including the accuracy gates (+5 browser tests with BOTCLEANER_UI_TESTS=1)
python -m botcleaner.evaluation         # print the §7 validation gates on seeded networks
```

| Environment variable | Purpose |
|---|---|
| `BOTCLEANER_DB` | SQLite path (default `botcleaner.sqlite3`) |
| `BOTCLEANER_SECRET` | Key used to encrypt OAuth tokens at rest and sign appeal links. **Set this in production.** Without it, a key file `.botcleaner.key` is generated |
| `BOTCLEANER_ADMIN_TOKEN` | Needed to moderate community instructions and to create Purge Console tenants |
| `X_CLIENT_ID`, `X_REDIRECT_URI` | X OAuth 2.0 (PKCE) app credentials, used for one-click removal |
| `BOTCLEANER_WORKER` / `BOTCLEANER_TICK_SECONDS` | Background worker (one-click queue, purge batches, 24h raw-data purge, scheduled rescans) |

## Module A — Personal Cleaner

1. **Connect or import.** Connect X through OAuth, or upload the data export (zip or single file) for Instagram, Facebook, TikTok, LinkedIn or an X archive. The app shows the export steps for each platform. `botcleaner/importers.py` turns every source into one schema.
2. **Scan.** Every connection gets a 0–100 score with its top 3 reasons written in plain words (`botcleaner/scoring.py`).
3. **Review.** You can filter by direction (friends, followers, following) and by tab: Likely bot, Suspicious, Clones, Low confidence, Whitelisted, Pending, Removed. You can also sort, filter by reason, preview a profile, or open the real one.
4. **Remove** (`botcleaner/removal.py`). There are three modes:
   - **One-click** (X only): official API calls, paced under X's limits. If X's API tier refuses block/unblock, the item switches to Assisted mode instead of failing.
   - **Assisted:** the app opens each profile in your own logged-in browser at a human pace, and **you** click. It never clicks for you.
   - **Guided:** a checklist with steps for your platform and device (web, iOS, Android).
5. **Re-check.** Items you tick off are marked *Pending*. On your next import, anyone missing from the new export is marked *Removed* and anyone still there is marked *Failed*.

Also included:
- "Real person" / "Definitely a bot" feedback, which retrains your personal model
- Clone alerts with links to report impersonation
- A user instruction editor with versions, moderation and "outdated" flags. Community steps that link to login or password pages are rejected
- Weekly or monthly rescans
- A CSV export and undo log ("I re-added them" whitelists that person permanently)
- One-tap deletion of all your data
- Parent/guardian sign-up that requires the teen's consent

## Module B — Platform Purge Console

1. **Connect data.** Send accounts through the REST API (`POST /api/purge/accounts`) or upload a CSV/JSON export.
2. **Scan.** Scoring uses signals only a platform can see (`botcleaner/purge/signals.py`):
   - signup velocity per IP, subnet, ASN or device fingerprint
   - disposable or sequentially numbered emails
   - CAPTCHA solve timing, headless-browser markers, honeypot fields and links
   - posts built from the same template across accounts
   - logins from data-centre IPs, and inhumanly fast or regular action timing

   Accounts are then grouped into **rings**.
3. **Review.** An explorer (filter by score, reason, ring, state or signup date), a ring view, and stratified spot-check samples.
4. **Dry run.** Shows exactly who each rule would hit, and why. The batch then carries out **that plan** and skips any account that changed in the meantime.
5. **Act in tiers**, in chunks you can pause, with full rollback:

   | Tier | Default trigger | Action |
   |---|---|---|
   | 1 | score 60–79 | challenge (CAPTCHA, email/phone re-check) |
   | 2 | score 80–94 | restrict posting, messaging and following |
   | 3 | 95+ or a confirmed ring | suspend, with a notice and an appeal link |
   | 4 | appeal window closed, no appeal won | permanent removal and data deletion. Needs a reviewer's sign-off; rules can't trigger it |

6. **Appeals.** The public portal at `/appeal/<signed token>` explains the action and the reasons. The user submits an appeal, and a reviewer queue works through appeals with deadlines. An approved appeal restores the account automatically and exempts it from future automated action.
7. **Everything else:**
   - an owner rules builder
   - a real-time signup gate (`POST /api/purge/gate` → allow, challenge or block)
   - an enforcement feed and webhook your platform applies
   - reports (appeal and overturn rates, trends, top reasons)
   - a hash-chained **append-only audit log**: database triggers refuse edits and deletes, and `GET /api/purge/audit/verify` detects tampering
   - separate owner and reviewer keys, and tenant isolation

## Assisted-mode browser extension

`extension/` is a Manifest V3 extension for Chrome and Edge. To try it:
1. Open `chrome://extensions` and turn on developer mode.
2. Choose **Load unpacked** and select `botcleaner/extension`.
3. Open the popup and enter your server address and access key.
4. Pick an Assisted job and open the first profile.

It opens each flagged profile and shows the steps in a small panel beside it. **You** click Remove or Unfollow yourself, then press "I removed them".

Rules the extension follows:
- It never clicks, types, submits or reads anything on the platform's page.
- A test checks the source for any code that could do that, and a browser test confirms the page's Remove button is never clicked.
- It asks for access only to your own server.
- It keeps the server's human pace between profiles.

## Platform SDK and admin-API adapters (Module B)

- **`/static/sdk.js`** adds three things to a signup form:
  - a hidden honeypot field and an invisible bait link
  - headless-browser detection
  - CAPTCHA and form-fill timing

  `BotCleaner.protect(form).collect()` returns those signals. Your server forwards them to `POST /api/purge/gate`.
- **Adapters** (`PUT /api/purge/adapter`, then `POST /api/purge/adapter/sync`) import members and apply each tier on the platform itself:

  | State | Discourse | Discord |
  |---|---|---|
  | Challenged | deactivate | verification role |
  | Restricted | silence | 28-day timeout |
  | Suspended | suspend until the appeal deadline | ban |
  | Removed | delete | ban stays |
  | Active | undo | undo |

  Staff and admins, and Discord bot integrations, arrive tagged as exempt. Credentials are encrypted at rest. Shopify and WordPress remain CSV/REST imports for now.

## Validation (§7)

`botcleaner/evaluation.py` builds seeded test networks with a known mix of real people and bots. Real people include hard cases: new accounts, no photo, birth-year handles. It then checks the PRD's accuracy gates:
- precision for Likely bot / Suspicious
- recall
- false-flag rate
- bias (no group above 2× the overall false-flag rate)
- clone traps (every planted clone must be caught in a single scan)

It also includes shadow-mode comparison and stratified 1% review sampling. The suite fails if any gate fails.

**Red team (§7.5).** Three levels of evasive bots with aged accounts, realistic photos and human names:
- Level 1: recycled posts on a fixed timer. Caught.
- Level 2: human timing, but no mutual friends and a lopsided follow ratio. Caught.
- Level 3: nothing in the data tells them apart from people. Not caught. This level measures the blind spot and is reported, not gated.

**Browser tests (§7.9).** `BOTCLEANER_UI_TESTS=1 pytest tests/test_ui.py` drives Chromium through:
- the guided path at desktop and phone widths, with steps for every platform × device × action
- Assisted mode in the web app and through the extension
- the console, the appeals portal and the audit log

`.github/workflows/botcleaner-weekly.yml` runs these weekly, with the gates and load tests.

**Load tests (§7.10).** `python -m botcleaner.loadtest --module a|b --size N` times a full import and scan. On a 4-core dev box:

| Load | Time |
|---|---|
| 100k connections (Module A) | ~32 s |
| 1M connections (Module A) | ~4.6 min, ~10 GB peak memory (test data generated in the same process) |
| 100k accounts (Module B) | ~33 s |

At 100k connections all four Module A gates pass (0.05% false flags).

**Product metrics (§10).** `GET /api/admin/metrics` (admin token) reports each measure against its target:
- flag confirmation rate
- share of users who complete a removal after their first scan
- median scan-to-clean time
- accounts users report as restricted by a platform
- Module B overturn rate

Users report a restriction with `POST /api/me/restriction-report`.

**These gates run on synthetic data.** Passing them shows the pipeline behaves as designed. It does not show real-world accuracy. Before launch, run them on licensed labelled datasets and in ≥2 weeks of shadow mode, as §7 requires.

## Known limits and open items

- **Instagram, Facebook, TikTok and LinkedIn exports carry only names or handles and dates.** On those platforms most bots reach *Suspicious* (shown for review) rather than *Likely bot* (pre-selected). Scoring prefers precision when evidence is thin.
- **Clones with no photo.** An account with the same name as a friend but no photo is capped at *Suspicious*. Near-identical names need a matching photo. In very large lists, common names are compared by photo only.
- **No native mobile apps yet.** Native iOS and Android clients are not built. The web app works at phone width and shows iOS/Android steps.
- **Module B at 50M accounts** (§7.10) needs a real database and sharded scoring. SQLite and single-process scoring top out around a few million.
- **The X API tier** and whether it still allows block/unblock need confirming (PRD §11).
- **Shopify and WordPress adapters** aren't built.
- **Legal review** of each platform's terms and of the extension, and GDPR/CCPA/DSA review, are still to do.
