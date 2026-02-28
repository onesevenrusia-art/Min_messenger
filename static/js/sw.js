self.addEventListener('install', event => {
    console.log('Service Worker installed');
    self.skipWaiting(); // активировать сразу
});

self.addEventListener('activate', event => {
    console.log('Service Worker activated');
});

self.addEventListener('fetch', event => {
    // Можно перехватывать запросы
    event.respondWith(fetch(event.request));
});

self.addEventListener('push', event => {
    const data = event.data ? event.data.text() : 'No payload';
    event.waitUntil(
        self.registration.showNotification('Push Received', {
            body: data,
            icon: '/icon.png'
        })
    );
});