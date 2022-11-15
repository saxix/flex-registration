const cacheName = "v1";


function cleanResponse(response) {
  const clonedResponse = response.clone();

  const bodyPromise = 'body' in clonedResponse ?
    Promise.resolve(clonedResponse.body) :
    clonedResponse.blob();

  return bodyPromise.then((body) => {
    return new Response(body, {
      headers: clonedResponse.headers,
      status: clonedResponse.status,
      statusText: clonedResponse.statusText,
    });
  });
}


const addResourcesToCache = async (resources) => {
  const cache = await caches.open(cacheName);
  await cache.addAll(resources);
};


self.addEventListener("install", (event) => {
  event.waitUntil(
    addResourcesToCache([
      "/",
      "/registrations/",
      "/serviceworker.js"
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
  return event.respondWith(cacheFirst(event.request));
});