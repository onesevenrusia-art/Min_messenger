self.addEventListener("push", function(event){
    console.log("push event")
    
    event.waitUntil(
        self.registration.showNotification("TEST PUSH",{
            body: "push received"
        })
    )
})

self.addEventListener("notificationclick", function(event){
    event.notification.close()
    event.waitUntil(
        clients.openWindow("/")
    )

})