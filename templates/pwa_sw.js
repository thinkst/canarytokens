const CACHE_NAME = `pwa-token-v0.9`;
    
// Use the install event to pre-cache all initial resources.
self.addEventListener('install', event => {
  event.waitUntil((async () => {
    // const cache = await caches.open(CACHE_NAME);
    // cache.addAll([
    //   'https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css'
    // ]);
  })());
});

self.addEventListener('fetch', event => {
  event.respondWith((async () => {
    // don't use the cache for tokens calls
    // if (event.request.url.startsWith('{{scheme}}://{{domain}}')) {
    try {
      const fetchResponse = await fetch(event.request);
      return fetchResponse;
    } catch (e) {
      // The network failed
    }
    // } else {
    //   const cache = await caches.open(CACHE_NAME);
    //   // Get the resource from the cache.
    //   const cachedResponse = await cache.match(event.request);
    //   if (cachedResponse) {
    //     return cachedResponse;
    //   } else {
    //       try {
    //         // If the resource was not in the cache, try the network.
    //         const fetchResponse = await fetch(event.request);
      
    //         // Save the resource in the cache and return it.
    //         cache.put(event.request, fetchResponse.clone());
    //         return fetchResponse;
    //       } catch (e) {
    //         // The network failed
    //       }
    //   }
    // }
  })());
}); 