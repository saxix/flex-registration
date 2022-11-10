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
      let urls = ["/"];
      if (urlToCache) {
        urls.push(urlToCache);
      }
      return cache.addAll(urls);
    })
  );
});
