self.addEventListener("message", (event) => {
    if (event.data.type === "notify") {
        self.registration.showNotification(event.data.title, {
            body: event.data.body,
            data: event.data.data,
            icon: "/static/images/favicon.ico",
            badge: "/static/images/favicon.ico"
        });
    }
});