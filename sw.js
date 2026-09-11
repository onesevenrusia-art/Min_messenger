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
    if (!event.data) return;

    const data = event.data.json();

    const chatId = data.chat_id || 0;
    const tag = "chat_" + chatId;

    event.waitUntil(
        self.registration.getNotifications({ tag: tag })
            .then(notifications => {

                // Уже есть уведомление этого чата
                if (notifications.length > 0) {
                    return;
                }

                return self.registration.showNotification(
                    data.title || "Новое сообщение",
                    {
                        body: data.body || "Новое сообщение",
                        icon: data.avatar || "/static/images/Uniknown.png",
                        badge: "/static/images/logo.png",
                        tag: tag,
                        renotify: false,
                        vibrate: [200, 100, 200],
                        data: {
                            chat_id: chatId
                        }
                    }
                );
            })
    );
});