// Service worker: talks to the Bot Account Cleaner server and remembers which
// flagged profile each tab is showing. It opens pages; it never touches them.

const get = keys => chrome.storage.local.get(keys);

async function api(path, { method = "GET", body } = {}) {
  const { server, token } = await get(["server", "token"]);
  if (!server || !token) throw new Error("Set your server and access key in the extension popup first.");
  const r = await fetch(server.replace(/\/$/, "") + path, {
    method,
    headers: { Authorization: "Bearer " + token, ...(body ? { "Content-Type": "application/json" } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await r.json().catch(() => null);
  if (!r.ok) throw new Error((data && data.detail) || `Request failed (${r.status})`);
  return data;
}

function device() {
  return /Android/.test(navigator.userAgent) ? "android" : "web";
}

// Open (or reuse) one tab for the current job, at the pace the server allows.
async function openNext(jobId) {
  const r = await api(`/api/removals/${jobId}/next?device=${device()}`);
  if (r.state !== "open") return r;
  const { removalTab } = await get("removalTab");
  let tab;
  try {
    tab = removalTab ? await chrome.tabs.update(removalTab, { url: r.item.profile_url, active: true }) : null;
  } catch (_) { tab = null; }
  if (!tab) tab = await chrome.tabs.create({ url: r.item.profile_url, active: true });
  const task = { jobId, idx: r.item.idx, name: r.item.name || r.item.handle || r.item.account_id,
                 action: r.item.action, steps: r.steps.steps, note: r.note, openedAt: Date.now() };
  await chrome.storage.local.set({ removalTab: tab.id, ["task:" + tab.id]: task, activeJob: jobId });
  return r;
}

chrome.runtime.onMessage.addListener((msg, sender, reply) => {
  (async () => {
    try {
      if (msg.type === "jobs") return reply({ ok: true, jobs: await api("/api/removals") });
      if (msg.type === "start") return reply({ ok: true, result: await openNext(msg.jobId) });
      if (msg.type === "task") {
        const key = "task:" + sender.tab.id;
        const t = (await get(key))[key];
        return reply({ ok: true, task: t || null });
      }
      if (msg.type === "confirm") {
        const key = "task:" + sender.tab.id;
        const t = (await get(key))[key];
        if (!t) return reply({ ok: false, error: "No removal task for this tab" });
        await api(`/api/removals/${t.jobId}/items/${t.idx}/confirm`, { method: "POST", body: { outcome: msg.outcome } });
        await chrome.storage.local.remove(key);
        return reply({ ok: true });
      }
      if (msg.type === "next") {
        const { activeJob } = await get("activeJob");
        return reply({ ok: true, result: await openNext(activeJob) });
      }
      reply({ ok: false, error: "unknown message" });
    } catch (e) {
      reply({ ok: false, error: e.message });
    }
  })();
  return true; // async reply
});

chrome.tabs.onRemoved.addListener(tabId => chrome.storage.local.remove("task:" + tabId));
