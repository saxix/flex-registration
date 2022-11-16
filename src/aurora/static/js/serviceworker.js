const cacheName = "v1";


const addResourcesToCache = async (resources) => {
  const cache = await caches.open(cacheName);
  await cache.addAll(resources);
};


self.addEventListener("install", (event) => {
  event.waitUntil(
    addResourcesToCache([
      "/",
      "/registrations/",
      // "/i18n/en-us/",
      "/serviceworker.js",
      // "/static/admin/debug.css",
      "/static/registration/auth.js",
      "/static/page.min.js",
      "/static/edit.min.js",
      "/static/i18n/i18n_edit.js",
      "/static/smart.js",
      "/static/registration/survey.min.js",
      "/static/admin/js/vendor/jquery/jquery.js",
      "/static/base.css",
      "/static/staff-toolbar.css",
      // "/static/hope1.webp",
      "https://code.jquery.com/jquery-3.6.0.min.js",
      "/api/project/",
    ])
  );
});


const cacheFirst = async (request) => {
  const responseFromCache = await caches.match(request);
  // const responseClone = responseFromCache.clone();

  console.log("responseFromCache", responseFromCache);
  if (responseFromCache) {
    return responseFromCache;
  }
  return fetch(request, { mode: 'no-cors'}).then(response => {
    caches.open(cacheName).then(cache => {
      cache.put(request, response.clone());
    })
  });
};


self.addEventListener("fetch", (event) => {
    if (navigator.onLine) {
        console.log("Fetching from SERVER");
        return fetch(event.request);
    } else {
        console.log(`Fetching from service worker url=${event.request.url}`);
        return event.respondWith(cacheFirst(event.request));
    }

});