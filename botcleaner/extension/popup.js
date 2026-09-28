const $ = id => document.getElementById(id);
const PLATFORMS = { x: "X", facebook: "Facebook", instagram: "Instagram", tiktok: "TikTok", linkedin: "LinkedIn" };
const send = msg => new Promise(res => chrome.runtime.sendMessage(msg, res));

async function init() {
  const { server, token } = await chrome.storage.local.get(["server", "token"]);
  $("server").value = server || "";
  $("token").value = token || "";
  if (server && token) showRun();
}

$("save").onclick = async () => {
  let server = $("server").value.trim().replace(/\/$/, "");
  if (!/^https:\/\/|^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?/.test(server)) { $("msg").textContent = "Use an https:// server address."; return; }
  // Ask for access to just this server.
  const granted = await chrome.permissions.request({ origins: [server + "/*"] });
  if (!granted) { $("msg").textContent = "Permission to reach the server is needed."; return; }
  await chrome.storage.local.set({ server, token: $("token").value.trim() });
  showRun();
};

$("reset").onclick = () => { $("setup").hidden = false; $("run").hidden = true; };

async function showRun() {
  $("setup").hidden = true; $("run").hidden = false;
  const r = await send({ type: "jobs" });
  if (!r || !r.ok) { $("msg").textContent = (r && r.error) || "Couldn't reach the server."; return; }
  const jobs = r.jobs.filter(j => j.state === "running" && j.mode !== "guided");
  $("job").innerHTML = "";
  jobs.forEach(j => {
    const o = document.createElement("option");
    o.value = j.id; o.textContent = `${PLATFORMS[j.platform] || j.platform} · ${new Date(j.created_at).toLocaleString()}`;
    $("job").appendChild(o);
  });
  $("start").disabled = !jobs.length;
  $("msg").textContent = jobs.length ? "Pick a job and open the first profile." : "No assisted removal jobs yet. Select accounts in the web app and choose Assisted.";
}

$("start").onclick = async () => {
  const r = await send({ type: "start", jobId: $("job").value });
  if (!r || !r.ok) { $("msg").textContent = (r && r.error) || "Something went wrong."; return; }
  const s = r.result.state;
  $("msg").textContent = s === "open" ? "Opened. Follow the steps on the page." : s === "waiting" ? `Short pause — try again in ${Math.ceil(r.result.wait_seconds)}s.` : `Job is ${s}.`;
};

init();
