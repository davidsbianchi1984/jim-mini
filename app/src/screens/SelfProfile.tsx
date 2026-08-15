import { useEffect, useState } from "react";
import { api, SelfProfileStatus, SelfProfilePreview } from "../api";
import { useSession } from "../store";
import { t as tr, visitorLang } from "../l10n";

// The one QRME profile that is this person.
//
// Every other tandem surface in this console reaches somebody else's profile —
// a clinician's specialist, the care team's org. This reaches their own: the
// `self` profile that speaks *as* them, and that answers strangers.
//
// The screen is built around the preview rather than around the switches,
// because the switches are not the decision. `docs/tandem.md` says what may
// cross and why; this shows exactly what would, in the strings that would go,
// before anything does.

const ORDER = ["language", "wellbeing", "conditions", "medication",
               "continuity"];

export function SelfProfile() {
  const { session } = useSession();
  const userId = session.userId;
  const token = session.userToken;
  const lang = visitorLang();
  const [status, setStatus] = useState<SelfProfileStatus | null>(null);
  const [preview, setPreview] = useState<SelfProfilePreview | null>(null);
  const [profileId, setProfileId] = useState("");
  const [ownerToken, setOwnerToken] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  // Signing in to QRME. Neither of these leaves this component except as the
  // body of one request, and neither is stored on either side of it.
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [choices, setChoices] = useState<
    { profile_id: string; shown_as?: string; kind?: string }[]>([]);
  //: The paste-it form, for somebody who does hold an id and a token. Still
  //  the right door for them; no longer the only one.
  const [pasting, setPasting] = useState(false);

  async function refresh() {
    if (!userId || !token) return;
    setStatus(await api.selfProfile(userId, token));
    setPreview(await api.selfProfilePreview(userId, token));
  }

  useEffect(() => { refresh(); }, [userId, token]);

  if (!userId || !token) return <p>{tr("self.signin", lang)}</p>;

  async function run(work: () => Promise<unknown>, said: string) {
    setBusy(true); setNote(null);
    try { await work(); setNote(said); await refresh(); }
    catch (e) { setNote(e instanceof Error ? e.message : String(e)); }
    finally { setBusy(false); }
  }

  /// Sign in to QRME and link, or come back with the choice to make.
  ///
  /// One `self` profile links straight away. Several returns `choose` and
  /// nothing has happened yet — the password is still in the form, so the
  /// second call costs the person no retyping and needs no ticket held
  /// anywhere between the two.
  async function signIn(chosen?: string) {
    if (!userId || !token) return;
    setBusy(true); setNote(null);
    try {
      const r = await api.selfProfileSignIn(userId, token, {
        email: email.trim(), password,
        ...(chosen ? { profile_id: chosen } : {}) });
      if (r.linked) {
        setChoices([]); setPassword("");
        setNote(tr("self.linked_note", lang));
        await refresh();
      } else {
        setChoices(r.choose ?? []);
      }
    } catch (e) {
      setNote(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const consented = status?.consented ?? [];
  const brief = preview?.brief ?? {};

  return (
    <div className="screen">
      <h2>{tr("self.title", lang)}</h2>
      <p className="lead">
        {tr("self.lead", lang)}
      </p>

      {/* Signing in comes first; the paste-it form is behind a link now.
          The screen used to lead with a `prf_…` id and an owner token, and a
          field report said the honest thing about that: *how do I get a
          token?* There was no answer — it is minted once, in QRME's create
          response, and handed to whichever client did the creating.

              asked     how do I get a token
              mattered  the screen was asking for something unfindable

          Neither field below is stored. JIM signs in to QRME, mints the
          owner token itself, and keeps only that — the same value the form
          underneath was asking the person to go and find. */}
      {!status?.linked && (
        <section className="card">
          <h3>{tr("self.signin.title", lang)}</h3>
          <p>{tr("self.signin.pitch", lang)}</p>
          <input value={email} placeholder={tr("self.signin.email", lang)}
                 type="email" autoComplete="username"
                 onChange={(e) => setEmail(e.target.value)} />
          <input value={password}
                 placeholder={tr("self.signin.password", lang)}
                 type="password" autoComplete="current-password"
                 onChange={(e) => setPassword(e.target.value)} />
          <button disabled={busy || !email.trim() || !password}
                  onClick={() => signIn()}>
            {tr("self.signin.button", lang)}
          </button>

          {choices.length > 0 && (
            <>
              <p className="small">{tr("self.signin.choose", lang)}</p>
              {choices.map((c) => (
                <button key={c.profile_id} disabled={busy}
                        onClick={() => signIn(c.profile_id)}>
                  {c.shown_as || c.profile_id}
                </button>
              ))}
            </>
          )}

          <button className="linkish" disabled={busy}
                  onClick={() => setPasting(!pasting)}>
            {tr("self.signin.paste_instead", lang)}
          </button>
        </section>
      )}

      {!status?.linked && pasting && (
        <section className="card">
          <h3>{tr("self.link", lang)}</h3>
          <p>
            {tr("self.paste", lang)}
          </p>
          <input value={profileId} placeholder={tr("self.profile_id", lang)}
                 onChange={(e) => setProfileId(e.target.value)} />
          <input value={ownerToken} placeholder={tr("self.owner_token", lang)} type="password"
                 onChange={(e) => setOwnerToken(e.target.value)} />
          <button disabled={busy || !profileId.trim() || !ownerToken.trim()}
                  onClick={() => run(
                    () => api.selfProfileLink(userId, token, {
                      profile_id: profileId.trim(),
                      owner_token: ownerToken.trim() }),
                    tr("self.linked_note", lang))}>
            {tr("self.link_button", lang)}
          </button>
        </section>
      )}

      {status?.linked && (
        <>
          <section className="card">
            <h3>{tr("self.may_know", lang)}</h3>
            <p>{tr("self.until_tick", lang)}</p>
            {ORDER.filter((k) => status.categories[k]).map((key) => (
              <label key={key} className="row">
                <input type="checkbox" checked={consented.includes(key)}
                       disabled={busy}
                       onChange={(e) => {
                         const next = e.target.checked
                           ? [...consented, key]
                           : consented.filter((c) => c !== key);
                         run(() => api.selfProfileConsent(userId, token, next),
                             tr("self.saved", lang));
                       }} />
                <span>{`${key} — ${status.categories[key]}`}</span>
              </label>
            ))}
          </section>

          <section className="card">
            <h3>{tr("self.exactly", lang)}</h3>
            {preview?.empty ? (
              <p>{tr("self.nothing_ticked", lang)}</p>
            ) : (
              <pre className="brief">{JSON.stringify(brief, null, 2)}</pre>
            )}
            <p className="small">
              {tr("self.message_itself", lang)}
            </p>
            <button disabled={busy || preview?.empty}
                    onClick={() => run(
                      () => api.selfProfileBrief(userId, token),
                      tr("self.sent", lang))}>
              {tr("self.send", lang)}
            </button>
          </section>

          <section className="card">
            <h3>{tr("self.stop", lang)}</h3>
            <p>
              {tr("self.unlink_note", lang)}
            </p>
            <button className="danger" disabled={busy}
                    onClick={() => run(
                      () => api.selfProfileUnlink(userId, token),
                      tr("self.unlinked", lang))}>
              {tr("self.unlink", lang)}
            </button>
          </section>
        </>
      )}

      {note && <p className="note">{note}</p>}
    </div>
  );
}
