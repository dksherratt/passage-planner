// Grampian Passage Planner — offline support.
// The app itself is cached on install so it opens at sea with no signal.
// Fonts are cached the first time they load. Live tide and wind requests
// always go to the network; the app keeps their last results itself.

const VERSION = 'v1';
const APP_CACHE = 'planner-app-' + VERSION;
const FONT_CACHE = 'planner-fonts';
const APP_FILES = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/apple-touch-icon.png'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(APP_CACHE).then(c => c.addAll(APP_FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('planner-app-') && k !== APP_CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET') return;

  // Google Fonts: serve from cache, refresh in the background.
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    event.respondWith(caches.open(FONT_CACHE).then(async cache => {
      const hit = await cache.match(event.request);
      const live = fetch(event.request).then(res => { if (res.ok || res.type === 'opaque') cache.put(event.request, res.clone()); return res; }).catch(() => hit);
      return hit || live;
    }));
    return;
  }

  // The app's own files: network first so updates arrive, cache when offline.
  if (url.origin === self.location.origin) {
    event.respondWith(
      fetch(event.request)
        .then(res => { const copy = res.clone(); caches.open(APP_CACHE).then(c => c.put(event.request, copy)); return res; })
        .catch(() => caches.match(event.request).then(hit => hit || caches.match('./index.html')))
    );
  }
  // Everything else (Admiralty, Open-Meteo) goes straight to the network.
});
