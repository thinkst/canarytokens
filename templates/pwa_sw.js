

self.addEventListener('install', event => {
  event.waitUntil((async () => {
  })());
});

self.addEventListener('fetch', event => {
  event.respondWith((async () => {
    try {
      const fetchResponse = await fetch(event.request);
      return fetchResponse;
    } catch (e) {
      // The network failed
    }
  })());
}); 