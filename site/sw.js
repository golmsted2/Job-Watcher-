const CACHE = "fda-job-watcher-v10";
const SHELL = ["./", "./index.html", "./browse.html", "./job.html", "./compare.html", "./companies.html", "./workspace.html", "./market.html", "./styles.css?v=market-interactive", "./app.js?v=market-interactive", "./manifest.webmanifest", "./assets/finance-career-hero.png", "./assets/market-network.png", "./assets/logos/edward-jones.png", "./assets/logos/stifel.png", "./assets/logos/jpmorgan-chase.png", "./assets/logos/bank-of-america.png", "./assets/logos/citi.png", "./assets/logos/wells-fargo.png", "./assets/logos/goldman-sachs.png", "./assets/logos/morgan-stanley.png", "./assets/logos/pnc.png", "./assets/logos/us-bank.png", "./assets/logos/state-street.png", "./assets/logos/bny.png", "./assets/logos/american-express.png", "./assets/logos/capital-one.png", "./assets/logos/northern-trust.png"];
self.addEventListener("install", (event) => event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener("activate", (event) => event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))).then(() => self.clients.claim())));
self.addEventListener("fetch", (event) => {
  if (event.request.url.includes("/data/")) {
    event.respondWith(fetch(event.request).then((response) => { const copy = response.clone(); caches.open(CACHE).then((cache) => cache.put(event.request, copy)); return response; }).catch(() => caches.match(event.request)));
  } else {
    event.respondWith(fetch(event.request).then((response) => { const copy = response.clone(); caches.open(CACHE).then((cache) => cache.put(event.request, copy)); return response; }).catch(() => caches.match(event.request)));
  }
});

