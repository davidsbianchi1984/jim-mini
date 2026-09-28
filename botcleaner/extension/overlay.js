// Content script: shows the removal steps over a flagged profile.
//
// SAFETY RULE: this file only draws its own panel. It never clicks, types into,
// submits, or reads anything on the platform's page. The person clicks Remove /
// Unfollow themselves; automated clicking breaks Meta, LinkedIn and TikTok terms
// and can get their account restricted. A test enforces this.

(function () {
  const ACTIONS = { unfriend: "Unfriend", remove_follower: "Remove follower", unfollow: "Unfollow" };

  // The tab can finish loading a moment before the worker saves its task, so ask a few times.
  let tries = 0;
  (function ask() {
    chrome.runtime.sendMessage({ type: "task" }, res => {
      if (res && res.ok && res.task) return render(res.task);
      if (++tries < 4) setTimeout(ask, 700);
    });
  })();

  function el(tag, attrs = {}, text) {
    const e = document.createElement(tag);
    Object.assign(e, attrs);
    if (text != null) e.textContent = text;
    return e;
  }

  function render(task) {
    const host = el("div");
    host.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:2147483647;";
    const root = host.attachShadow({ mode: "open" });
    root.appendChild(el("style", {}, `
      .p{font:14px/1.45 system-ui,sans-serif;width:320px;max-width:calc(100vw - 32px);background:#fff;color:#16181d;border:1px solid #d6dae1;border-radius:12px;padding:14px;box-shadow:0 6px 24px rgba(0,0,0,.18)}
      @media (prefers-color-scheme: dark){.p{background:#171a21;color:#e8eaef;border-color:#2a2f3a}}
      h3{margin:0 0 6px;font-size:15px} ol{padding-left:18px;margin:6px 0} .m{opacity:.75;font-size:12.5px}
      .r{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px} button{font:inherit;border-radius:8px;border:1px solid #c9ced6;background:transparent;color:inherit;padding:5px 10px;cursor:pointer}
      button.pr{background:#2856d8;border-color:#2856d8;color:#fff;font-weight:600} button:disabled{opacity:.5;cursor:default}`));
    const p = el("div", { className: "p" });
    p.appendChild(el("h3", {}, `${ACTIONS[task.action] || task.action}: ${task.name}`));
    const ol = el("ol");
    task.steps.forEach(s => ol.appendChild(el("li", {}, s)));
    p.appendChild(ol);
    p.appendChild(el("div", { className: "m" }, "You click the button on the page yourself. Then tell us how it went."));
    const row = el("div", { className: "r" });
    const done = el("button", { className: "pr" }, "I removed them");
    const skip = el("button", {}, "Skip");
    const fail = el("button", {}, "Couldn't");
    [done, skip, fail].forEach(b => row.appendChild(b));
    p.appendChild(row);
    const status = el("div", { className: "m" });
    p.appendChild(status);
    root.appendChild(p);
    document.documentElement.appendChild(host);

    const confirm = outcome => {
      [done, skip, fail].forEach(b => (b.disabled = true));
      chrome.runtime.sendMessage({ type: "confirm", outcome }, res => {
        if (!res || !res.ok) { status.textContent = (res && res.error) || "Couldn't reach the server."; [done, skip, fail].forEach(b => (b.disabled = false)); return; }
        row.replaceChildren();
        const next = el("button", { className: "pr" }, "Open next profile");
        row.appendChild(next);
        next.onclick = () => openNext(next, status);
        status.textContent = "Saved.";
      });
    };
    done.onclick = () => confirm("done");
    skip.onclick = () => confirm("skipped");
    fail.onclick = () => confirm("failed");
  }

  function openNext(btn, status) {
    btn.disabled = true;
    chrome.runtime.sendMessage({ type: "next" }, res => {
      if (!res || !res.ok) { status.textContent = (res && res.error) || "Couldn't reach the server."; btn.disabled = false; return; }
      const r = res.result;
      if (r.state === "waiting") {
        // Human pace: count down, then let the person press again.
        let left = Math.ceil(r.wait_seconds);
        const tick = () => {
          if (left <= 0) { btn.disabled = false; btn.textContent = "Open next profile"; return; }
          btn.textContent = `Next in ${left}s`; left -= 1; setTimeout(tick, 1000);
        };
        tick();
      } else if (r.state !== "open") {
        status.textContent = r.state === "empty" ? "All done — every profile in this batch has been opened." : `Job is ${r.state}.`;
      }
    });
  }
})();
