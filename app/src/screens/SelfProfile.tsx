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

  const consented = status?.consented ?? [];
  const brief = preview?.brief ?? {};

  return (
    <div className="screen">
      <h2>{tr("self.title", lang)}</h2>
      <p className="lead">
        {tr("self.lead", lang)}
      </p>

      {!status?.linked && (
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
