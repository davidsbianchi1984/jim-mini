import { useCallback, useEffect, useState } from "react";
import {
  api, type MailboxPosture, type MailMessage, type MailThread,
} from "../api";
import { t as tr, visitorLang, type Lang } from "../l10n";
import { useSession } from "../store";

/**
 * The moderated mailbox — the coach agent's correspondence, held at the send.
 *
 * The coach reads what comes in and drafts a reply, but **nothing is sent
 * until a person approves it**: every outbound message is a draft in a
 * moderation queue, and only Approve carries it out — over SMTP when the
 * deployment has a mail server, and *staged* (composed and held) otherwise.
 * The whole loop is here — take a message in, have the coach draft a reply,
 * edit it, approve or discard it, or write to someone new — and every word of
 * chrome runs through the console's ten-language table. The message bodies and
 * addresses are the server's, and render verbatim.
 */
export function Mail() {
  const { session } = useSession();
  const lang = visitorLang();
  const uid = session.userId;
  const token = session.userToken;

  const [posture, setPosture] = useState<MailboxPosture | null>(null);
  const [threads, setThreads] = useState<MailThread[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [edits, setEdits] = useState<Record<string, string>>({});

  // The take-a-message-in form.
  const [rFrom, setRFrom] = useState("");
  const [rSubject, setRSubject] = useState("");
  const [rBody, setRBody] = useState("");
  // The write-to-someone form.
  const [cTo, setCTo] = useState("");
  const [cSubject, setCSubject] = useState("");
  const [cObjective, setCObjective] = useState("");

  const load = useCallback(() => {
    if (!uid || !token) return;
    setError(null);
    api.mailPosture(uid, token).then(setPosture).catch(() => setPosture(null));
    api.mailInbox(uid, token).then(setThreads).catch(() => setThreads([]));
  }, [uid, token]);
  useEffect(load, [load]);

  async function run(action: () => Promise<unknown>) {
    setBusy(true); setError(null);
    try {
      await action();
      load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (!uid || !token) return <p>{tr("mail.signin", lang)}</p>;

  const drafted = (t: MailThread) =>
    t.messages.some((m) => m.state === "draft");

  return (
    <section className="screen">
      <h2>{tr("mail.title", lang)}</h2>
      <p className="muted">{tr("mail.pitch", lang)}</p>
      {error && <p className="error">{error}</p>}

      <div className="card">
        <p><strong>{tr("mail.posture.moderated", lang)}</strong></p>
        {posture && (
          <p className="muted small">
            {posture.outbound_ready
              ? tr("mail.posture.smtp", lang)
              : tr("mail.posture.staged", lang)}
            {" "}{tr("mail.posture.inbound", lang)}
          </p>
        )}
      </div>

      <h3>{tr("mail.receive", lang)}</h3>
      <div className="card">
        <div className="row">
          <input value={rFrom} placeholder={tr("mail.receive.from", lang)}
            onChange={(e) => setRFrom(e.target.value)} />
          <input value={rSubject} placeholder={tr("mail.receive.subject", lang)}
            onChange={(e) => setRSubject(e.target.value)} />
        </div>
        <textarea value={rBody} placeholder={tr("mail.receive.body", lang)}
          onChange={(e) => setRBody(e.target.value)} />
        <button className="primary" disabled={busy || !rFrom.trim() || !rBody.trim()}
          onClick={() => run(async () => {
            await api.mailReceive(uid, {
              from_addr: rFrom.trim(), subject: rSubject.trim(),
              body: rBody.trim(),
            }, token);
            setRFrom(""); setRSubject(""); setRBody("");
          })}>
          {tr("mail.receive.go", lang)}
        </button>
      </div>

      <h3>{tr("mail.compose", lang)}</h3>
      <div className="card">
        <div className="row">
          <input value={cTo} placeholder={tr("mail.compose.to", lang)}
            onChange={(e) => setCTo(e.target.value)} />
          <input value={cSubject} placeholder={tr("mail.compose.subject", lang)}
            onChange={(e) => setCSubject(e.target.value)} />
        </div>
        <textarea value={cObjective} placeholder={tr("mail.compose.objective", lang)}
          onChange={(e) => setCObjective(e.target.value)} />
        <button className="primary"
          disabled={busy || !cTo.trim() || !cObjective.trim()}
          onClick={() => run(async () => {
            await api.mailCompose(uid, {
              to: cTo.trim(), subject: cSubject.trim(),
              objective: cObjective.trim(),
            }, token);
            setCTo(""); setCSubject(""); setCObjective("");
          })}>
          {tr("mail.compose.go", lang)}
        </button>
      </div>

      <h3>{tr("mail.threads", lang)}</h3>
      {threads.length === 0 && <p className="muted">{tr("mail.none", lang)}</p>}
      {threads.map((t) => (
        <div key={t.id} className="card">
          <div className="row">
            <strong>{t.correspondent}</strong>
            <span className="muted">{t.subject}</span>
            {t.held_drafts > 0 && <span className="pill">{tr("mail.held", lang)
              .replace("{n}", String(t.held_drafts))}</span>}
          </div>
          {t.messages.map((m) => (
            <MessageRow key={m.id} m={m} lang={lang} busy={busy}
              edit={edits[m.id]}
              onEditChange={(v) => setEdits((s) => ({ ...s, [m.id]: v }))}
              onDraft={() => run(() => api.mailDraft(uid, m.id, token))}
              onApprove={() => run(() =>
                api.mailModerate(uid, m.id, { action: "approve" }, token))}
              onSaveEdit={() => run(() => api.mailModerate(uid, m.id,
                { action: "edit", edited: (edits[m.id] ?? m.body).trim() }, token))}
              onDiscard={() => run(() =>
                api.mailModerate(uid, m.id, { action: "discard" }, token))} />
          ))}
          {!drafted(t) && t.messages.some((m) => m.direction === "inbound") && (
            <p className="muted small">{tr("mail.draftreply.hint", lang)}</p>
          )}
        </div>
      ))}
    </section>
  );
}

function MessageRow({ m, lang, busy, edit, onEditChange, onDraft, onApprove,
                      onSaveEdit, onDiscard }: {
  m: MailMessage; lang: Lang; busy: boolean; edit?: string;
  onEditChange: (v: string) => void; onDraft: () => void; onApprove: () => void;
  onSaveEdit: () => void; onDiscard: () => void;
}) {
  return (
    <div className="card" style={{ marginTop: "6px" }}>
      <div className="row">
        <span className="pill">{tr(`mail.dir.${m.direction}`, lang)}</span>
        <span className="muted">{tr(`mail.state.${m.state}`, lang)}</span>
        {m.created_at && <span className="muted">
          {m.created_at.slice(0, 16).replace("T", " ")}</span>}
      </div>
      {m.state === "draft"
        ? (
          <>
            <textarea value={edit ?? m.body}
              onChange={(e) => onEditChange(e.target.value)}
              aria-label={tr("mail.edit.aria", lang)} />
            <div className="row">
              <button className="primary" disabled={busy} onClick={onApprove}>
                {tr("mail.approve", lang)}
              </button>
              <button disabled={busy} onClick={onSaveEdit}>
                {tr("mail.saveedit", lang)}
              </button>
              <button disabled={busy} onClick={onDiscard}>
                {tr("mail.discard", lang)}
              </button>
            </div>
          </>
        )
        : (
          <>
            <p>{m.body}</p>
            {m.direction === "inbound" && (
              <button disabled={busy} onClick={onDraft}>
                {tr("mail.draftreply", lang)}
              </button>
            )}
          </>
        )}
    </div>
  );
}
