const CACHE = "pokestar-shell-v7";
const CORE_PRECACHE = [
  "./manifest.json",
  "./robots.txt",
  "./favicon.ico",
  "./favicon-32.png",
  "./icon-192.png",
  "./icon-512.png",
  "./assets/brand-logo.jpg",
  "./cm-market-cache.json"
];
const OPTIONAL_PRECACHE = [
  "./ebay-sold-cache.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) =>
      Promise.all(CORE_PRECACHE.map(p => c.add(p)))  // core must succeed visibly on error
        .then(() => Promise.all(OPTIONAL_PRECACHE.map(p => c.add(p).catch(() => {/* ebay optional, may be absent in some deploys */}))))
    ).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  if (event.request.mode === "navigate" || url.pathname === "/" || url.pathname.endsWith("/index.html")) {
    event.respondWith(
      fetch(event.request)
        .then((res) => {
          if (res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put("./index.html", copy));
          }
          return res;
        })
        .catch(() => caches.match("./index.html"))
    );
    return;
  }

  if (url.pathname.endsWith("cm-market-cache.json") || url.pathname.endsWith("ebay-sold-cache.json")) {
    event.respondWith(
      fetch(event.request)
        .then((res) => {
          if (res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(event.request, copy));
          }
          return res;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((res) => {
        if (!res.ok) return res;
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(event.request, copy));
        return res;
      }).catch(() => cached);
    })
  );
});
