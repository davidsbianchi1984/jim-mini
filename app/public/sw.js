/* Service worker for the installed Guardian console.
 *
 * Deliberately narrow: it caches the **app shell only** — the HTML, JS, CSS,
 * and icons under this scope — so the app opens instantly and still opens
 * when the phone is briefly offline.
 *
 * It never caches API responses. Monitoring readings, guidance, escalation
 * state and check-ins must always be live: a stale cached answer in a health
 * app is worse than an error, so anything that isn't a shell asset goes
 * straight to the network, untouched.
 */

const CACHE = "jim-shell-v1";

self.addEventListener("install", (event) => {
  // Take over as soon as the new shell is stored; no stale worker lingering.
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(["./", "./index.html"]))
      .catch(() => undefined)   // a cold/offline install must not fail
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

/** Shell assets are same-origin GETs for the document or its build output. */
function isShellAsset(request, url) {
  if (request.method !== "GET") return false;
  if (url.origin !== self.location.origin) return false;
  if (!url.pathname.startsWith(new URL("./", self.location).pathname)) return false;
  return request.mode === "navigate"
    || /\.(?:js|css|svg|png|ico|webmanifest|woff2?)$/.test(url.pathname);
}

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (!isShellAsset(event.request, url)) return;   // API traffic: untouched

  // Network first, so a rebuilt console is picked up on the next load; the
  // cache is the offline fallback, and navigations fall back to the shell.
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const copy = response.clone();
        caches.open(CACHE).then((cache) => cache.put(event.request, copy))
          .catch(() => undefined);
        return response;
      })
      .catch(() => caches.match(event.request)
        .then((hit) => hit || caches.match("./index.html"))),
  );
});
