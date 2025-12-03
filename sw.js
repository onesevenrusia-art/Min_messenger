self.addEventListener("message", (event) => {
    if (event.data.type === "notify") {
        self.registration.showNotification(event.data.title, {
            body: event.data.body,
            data: event.data.data,
            icon: "/icon.png",
            badge: "/badge.png"
        });
    }
});