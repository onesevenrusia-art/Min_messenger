self.addEventListener('install', event => {
    console.log('Service Worker installed');
    self.skipWaiting(); // активировать сразу
});

self.addEventListener('activate', event => {
    console.log('Service Worker activated');
});

self.addEventListener('fetch', event => {
    event.respondWith(fetch(event.request));
});

self.addEventListener("push", event => {

    if (!event.data) return
    const data = event.data.json()
    console.log(data)
    const options = {
        body: data.body || "Новое сообщение",
        icon: data.avatar || "/static/default.png",
        badge: "/static/images/logo.png",
        tag: "chat_" + data.chat_id || 0,
        renotify: true,
        vibrate: [200, 100, 200, 100, 200],
        data: {
            chat_id: data.chat_id || 0
        }
    }
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    )
    
})