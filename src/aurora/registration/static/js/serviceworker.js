const staticCacheName = 'aurora-pwa';

let responseObj = { slug: null }

function retrieveSlug() {
  return fetch("/get_pwa_enabled/")
    .then((response) => response.json())
    .then(data => {
      responseObj.slug = data.slug;
    })
    .catch(error => {
        console.error(error);
    });
};

retrieveSlug(() => console.log("Slug retrieved"));

self.addEventListener('install', function(event) {
  console.log("slug", responseObj.slug)

  let urlToCache = null
  if (responseObj.slug) {
    urlToCache = `/register/${responseObj.slug}`;
  }

  event.waitUntil(
    caches.open(staticCacheName).then(function(cache) {
      let urls = [
          "/registrations",
          "/"
      ];
      if (urlToCache) {
        urls.push(urlToCache);
      }
      return cache.addAll(urls);
    })
  );
});


self.addEventListener('fetch', function(event) {
  var requestUrl = new URL(event.request.url);
    if (requestUrl.origin === location.origin) {
      console.log(requestUrl.pathname);
      if (requestUrl.pathname === '/registrations') {
        console.log("jestem tutaj i nie działam")
        event.respondWith(caches.match('/registrations'));
        return;
      } else if (requestUrl.pathname === '/') {
        console.log("jestem tutaj i działam!!!!!")
        event.respondWith(caches.match('/'));
        return;
    }
    event.respondWith(
      caches.match(event.request).then(function(response) {
        return response || fetch(event.request);
      })
    );
}});
