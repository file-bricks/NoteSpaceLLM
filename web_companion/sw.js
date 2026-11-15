const CACHE_NAME = "notespacellm-companion-v4";
// Inhalts-Hash aller ASSETS-Dateien inkl. Manifest und Icons (web_companion/tests/sw_asset_hash.test.mjs prueft ihn):
// aendert sich eine davon, CACHE_NAME erhoehen, sonst behalten installierte PWAs den alten Code.
const ASSET_HASH = '37fb40ab6f8a'; // eslint-disable-line no-unused-vars
const ASSETS = [
  "./",
  "./index.html",
  "./app.css",
  "./app.js",
  "./library.js",
  "./manifest.webmanifest",
  "./icons/Icon-192.png",
  "./icons/Icon-512.png",
  "./icons/Icon-maskable-192.png",
  "./icons/Icon-maskable-512.png",
  "./icons/apple-touch-icon-180.png"
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      ).then(() => self.clients.claim())
    )
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request, { ignoreSearch: true }).then((cached) => cached || fetch(event.request))
  );
});
