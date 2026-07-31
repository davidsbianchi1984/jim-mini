# JIM-mini v0.20.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.20.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.20.0 — the native shells record what breaks, and the route guard
stopped inventing work.**

## Failures from the phone and the desktop shell

The consoles have recorded failures content-free since 0.19.0 — the operation
and the status, never the message, never the path as it was typed. That is the
governing constraint: a crash report is worth having only if nothing private
travels in it, and the safest way to guarantee that is to have nothing private
to send.

The web console has done it since 0.19.0; **iOS, Android and the desktop shell
had not**, so a failure that happened only on a phone happened only in silence.
All three now record on the same terms and post to the same gateway.

`docs/cloud-model.md` — byte-identical across the three repositories — gains
the gateway's container deploy path. The gateway lives in QRME's tree, but
every product's console posts to it, so the instructions belong wherever
somebody is reading about the contract.

## A guard that invented work

Every earlier defect in `clientpaths.py` made it too **lenient**: a truncated
path, a verb read off a neighbouring call, a route table read flat instead of
recursed. Those are the failures you expect from a checker.

This one was the other kind. A template literal may nest another inside an
interpolation, and the extraction pattern's backtick alternative stopped at the
*inner* opening backtick — so a call normalised to a path no route matches, and
a route with a working door was reported as having none.

Nothing failed. The suite stayed green. The route sat on the backlog looking
like work, and a door-building round was aimed at it before anybody noticed the
door was already there. **A checker that invents work fails more quietly than
one that misses some:** a miss is found by the bug it let through, while an
invention is found only by somebody going to do the work and finding it done.

Interpolations are now matched by counting braces, so a nested one passes
through intact.
