const CACHE_NAME = 'casa-afriqa-menu-v5';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/admin.html',
  '/styles.css',
  '/script.js',
  '/images/koya_logo_loco.png',
];

// Install event - cache assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS_TO_CACHE).catch(() => {
        // Some assets might fail during install, that's okay
        return Promise.resolve();
      });
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// --- Enhanced Fetch Event: Daily 5am Menu Cache Refresh & Optimizations ---
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // --- 1. Skip caching for admin API calls ---
  if (url.pathname.includes('/api/admin/')) {
    event.respondWith(fetch(request));
    return;
  }

  // --- 2. Cache-first for static assets (with WebP/AVIF support) ---
  if (request.method === 'GET' && (url.pathname.match(/\.(?:png|jpe?g|webp|avif|gif)$/) || url.pathname.includes('style') || url.pathname.includes('.js'))) {
    event.respondWith(
      caches.match(request).then(response => {
        return response || fetch(request).then(fetchResponse => {
          if (fetchResponse.status === 200) {
            caches.open(CACHE_NAME).then(c => c.put(request, fetchResponse.clone()));
          }
          return fetchResponse;
        });
      }).catch(() => caches.match(request))
    );
    return;
  }

  // --- 3. Stale-while-revalidate for menu API + daily 5am hard refresh ---
  if (request.method === 'GET' && url.pathname.includes('/api/menu')) {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      const cached = await cache.match(request);

      // Read last refresh timestamp from meta cache
      const META_KEY = 'casa-afriqa-last-menu-refresh';
      let lastRefresh = 0;
      try {
        const metaCache = await caches.open('casa-afriqa-meta');
        const metaRes = await metaCache.match(META_KEY);
        if (metaRes) lastRefresh = parseInt(await metaRes.text(), 10);
      } catch {}

      const now = Date.now();
      const today5am = (() => { const d = new Date(); d.setHours(5,0,0,0); return d.getTime(); })();
      const needsHardRefresh = now >= today5am && lastRefresh < today5am;

      // If no cache at all, must wait for network (first visit)
      if (!cached) {
        const fresh = await fetch(request);
        if (fresh.status === 200) {
          cache.put(request, fresh.clone());
          const metaCache = await caches.open('casa-afriqa-meta');
          metaCache.put(META_KEY, new Response(now.toString()));
        }
        return fresh;
      }

      // STALE-WHILE-REVALIDATE: return cache instantly, refresh in background
      const backgroundRefresh = (async () => {
        try {
          const fresh = await fetch(request);
          if (fresh.status === 200) {
            cache.put(request, fresh.clone());
            const metaCache = await caches.open('casa-afriqa-meta');
            metaCache.put(META_KEY, new Response(now.toString()));
            // If it was a 5am hard refresh, notify all open tabs to reload menu
            if (needsHardRefresh) {
              const clients = await self.clients.matchAll({ type: 'window' });
              clients.forEach(c => c.postMessage({ type: 'MENU_UPDATED' }));
            }
          }
        } catch {}
      })();

      // Only block on network for the 5am hard refresh (once per day)
      if (needsHardRefresh) {
        await backgroundRefresh;
        return (await cache.match(request)) || cached;
      }

      // Otherwise return cached instantly, refresh silently in background
      event.waitUntil(backgroundRefresh);
      return cached;
    })());
    return;
  }

  // --- 4. Network only for admin/write operations ---
  if (request.method !== 'GET') {
    event.respondWith(fetch(request));
    return;
  }

  // --- 5. Default: network first, fallback to cache ---
  event.respondWith(
    fetch(request)
      .then(response => response)
      .catch(() => caches.match(request))
  );
});
