# Hosting JIM-mini

Run it yourself, or let someone run it for you. This document covers the
second case honestly — what changes when a deployment is reachable from
outside your own network, and what an operator holding other people's health
data has to settle first.

For the local flow (laptop, phone on the same Wi-Fi), see **Run it on your
phone** in the [README](../README.md); nothing here is needed for that.

## The two postures

| | Local | Published |
|---|---|---|
| Reached by | this machine and the LAN | anyone with the URL |
| Pairing advertises | the machine's LAN address | `JIM_PUBLIC_URL` |
| Who can enroll | anyone who can reach it | holders of `JIM_SIGNUP_KEY` |
| Transport | plain HTTP is fine on your own wire | **HTTPS, always** |

The local defaults are deliberate: on your own network, reaching the API
already means being in the house. Publishing changes that, so publishing
requires the two variables below.

## The three-product beta is a different page

This page is about running JIM-mini on its own. The live beta is four
containers on one box — JIM-mini, its two sibling products and the shared
gateway behind one reverse proxy — and it is documented once, in QRME, at
`docs/beta-deploy.md`, beside the compose file it describes.

Once rather than three times, deliberately: it is one machine. Three copies
of a page about one box is the drift this estate keeps finding in itself, and
the copies would disagree the first time somebody fixed only the one they had
open. What belongs here is the pointer, so an operator standing in this
repository can find it.

Its § 7 is the one to read at the end of a release: all three repositories are
pulled and rebuilt every time, even for a release that changed only one of
them, because each console's version guard compares itself against whatever
backend answers its port.


## Deploying

The `Dockerfile` builds the console and the API into one image, so the UI is
served from the same origin as the API — that's what lets a phone use it with
nothing to configure.

```bash
docker build -t jim-mini .
docker run -p 8200:8200 -v jim-data:/data \
  -e JIM_PUBLIC_URL=https://guardian.example.com \
  -e JIM_SIGNUP_KEY="$(openssl rand -base64 24)" \
  jim-mini
```

It honours `$PORT`, so container platforms that assign one work unchanged.
The database lives on the `/data` volume — **mount it**, or a restart is a
data-loss event, and here the data is someone's health history and baseline.
The container runs as a non-root user and reports health at `/health`.

Shared cPanel-style hosting (the kind sold for PHP sites) is a poor fit: this
is a long-running ASGI process, not a request-per-script runtime. A small VPS
or any container platform is the right shape.

### Required when published

| Variable | Why |
|---|---|
| `JIM_PUBLIC_URL` | `GET /pair` advertises this address, so the QR a phone scans points somewhere it can actually reach. |
| `JIM_SIGNUP_KEY` | Without it, anyone who finds the URL can enroll on your deployment. Give the key to the people who should have accounts — it gates *creating* one, so anyone already enrolled keeps working and a parent adding a child is authorized by their own token. |

### TLS is not optional

User tokens travel in the `Authorization` header, and what they unlock is
biometrics, medications, and a medical ID. Terminate TLS at a reverse proxy or
at the platform — the app does not do it. Over plain HTTP on a network you
don't control, a token is readable in transit and a stolen token is that
person's health record.

## Escalation still has to work

A published deployment is not just a copy of the local one — the parts of the
Guardian that matter most are the parts that reach outward:

- **Emergency contacts and services.** `POST /emergency` is what makes this a
  guardian rather than a dashboard. Exercise it on your deployment, with a
  real contact, before anyone relies on it.
- **Location.** The escalation payload carries location supplied by the
  client. A phone on a hosted origin over HTTPS can provide it; over plain
  HTTP browsers refuse the geolocation API outright — another reason TLS is
  not optional here.
- **Crisis routing stays local.** The mental-health trio escalates through the
  local path by design; hosting does not move that decision onto a network
  hop that can fail.

## If you host for other people

Running Guardian accounts that belong to someone else is a different
undertaking from running your own:

- **The Terms of Service** ([docs/terms.md](terms.md)) are written for the
  operator relationship — not a medical device, call 911 first, assumption of
  risk, the robot-resuscitation boundary, warranty disclaimer, liability cap.
  Have counsel review them before you take someone else's health data, and set
  the governing-law placeholder.
- **This is health data, and the law may say so.** If you host for a covered
  entity, [docs/hipaa-baa.md](hipaa-baa.md) is the starting point and a signed
  BAA is not optional. Hosting for a household is a different posture from
  hosting for a clinic; know which one you're in before you take the data.
- **Encryption at rest belongs to PDI.** JIM's own database is not encrypted;
  sealing medical and context payloads requires the PDI tandem
  (`JIM_PDI_URL` + `JIM_PDI_TOKEN`). If you hold other people's records, read
  PDI's key-custody table in its `docs/operations.md` — particularly that the
  KMS/HSM provider is an integration seam, not a finished control.
- **Erasure has to actually work.** `DELETE /data/{user_id}` erases every
  local table, purges the user's vault records, and revokes their token. Test
  it on your deployment before promising it.
- **Children's accounts raise the stakes.** Parent oversight ends at 18 by
  design, consent is recorded, and a minor can never have a resuscitation
  waiver signed for them. Hosting those accounts means being the party that
  has to honour all of it.

## What this does not give you

Stated plainly, so nobody infers otherwise:

- **No multi-tenancy.** One deployment is one trust boundary; accounts on it
  are isolated by bearer token, not by tenant. Separate customers means
  separate deployments.
- **No rate limiting or abuse controls.** Put them at the proxy.
- **No backups.** Snapshot the `/data` volume on whatever schedule your
  promises to users require — and remember that a lost baseline is a Guardian
  that has to learn the person again from scratch.
- **No uptime guarantee, from us or from the code.** A guardian that is down
  is not guarding. If people are relying on escalation, monitor `/health` and
  mean it.
