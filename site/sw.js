const CACHE = "fda-job-watcher-v8";
const SHELL = ["./", "./index.html", "./browse.html", "./job.html", "./compare.html", "./companies.html", "./workspace.html", "./market.html", "./styles.css?v=hero-small", "./app.js?v=8c76b40", "./manifest.webmanifest", "./assets/finance-career-hero.png", "./assets/market-network.png"];
self.addEventListener("install", (event) => event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener("activate", (event) => event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))).then(() => self.clients.claim())));
self.addEventListener("fetch", (event) => {
  if (event.request.url.includes("/data/")) {
    event.respondWith(fetch(event.request).then((response) => { const copy = response.clone(); caches.open(CACHE).then((cache) => cache.put(event.request, copy)); return response; }).catch(() => caches.match(event.request)));
  } else {
    event.respondWith(fetch(event.request).then((response) => { const copy = response.clone(); caches.open(CACHE).then((cache) => cache.put(event.request, copy)); return response; }).catch(() => caches.match(event.request)));
  }
});

