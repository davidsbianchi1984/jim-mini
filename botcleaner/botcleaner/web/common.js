// Shared helpers for the three pages.
const store = {
  get(k) { try { return localStorage.getItem(k); } catch (_) { return null; } },
  set(k, v) { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (_) {} },
};

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function toast(msg, ms = 3200) {
  document.querySelectorAll(".toast").forEach(x => x.remove());
  const t = document.createElement("div");
  t.className = "toast";
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), ms);
}

async function api(path, { method = "GET", body, headers = {}, form, raw } = {}) {
  const opts = { method, headers: { ...headers } };
  if (form) opts.body = form;
  else if (body !== undefined) { opts.body = JSON.stringify(body); opts.headers["Content-Type"] = "application/json"; }
  const r = await fetch(path, opts);
  if (raw) return r;
  const text = await r.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch (_) { data = text; }
  if (!r.ok) {
    let msg = data && data.detail ? data.detail : `Request failed (${r.status})`;
    if (Array.isArray(msg)) msg = msg.map(d => d.msg).join("; ");
    throw new Error(msg);
  }
  return data;
}

function avatar(name, seed) {
  const s = String(seed || name || "?");
  let h = 0;
  for (const ch of s) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  const initials = (name || "?").replace(/^@/, "").split(/\s+/).map(w => w[0]).join("").slice(0, 2).toUpperCase() || "?";
  return `<div class="avatar" style="background:hsl(${h % 360} 45% 45%)">${esc(initials)}</div>`;
}

function fmtDate(s) {
  if (!s) return "—";
  const d = new Date(s);
  return isNaN(d) ? s : d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

const LABELS = { likely_bot: "Likely bot", suspicious: "Suspicious", low_confidence: "Low confidence", looks_real: "Looks real" };
const PLATFORM_NAMES = { x: "X", facebook: "Facebook", instagram: "Instagram", tiktok: "TikTok", linkedin: "LinkedIn" };
const ACTION_NAMES = { unfriend: "Unfriend", remove_follower: "Remove follower", unfollow: "Unfollow" };
const PLATFORM_ACTIONS = {
  x: ["remove_follower", "unfollow"], facebook: ["unfriend", "remove_follower", "unfollow"],
  instagram: ["remove_follower", "unfollow"], tiktok: ["remove_follower", "unfollow"], linkedin: ["unfriend", "unfollow"],
};
