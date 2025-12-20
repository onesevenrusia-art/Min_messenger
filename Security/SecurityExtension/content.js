// from my frontend
window.addEventListener("message", event => {
    if (!event.data || typeof event.data !== "object") return;
    // detect crypto application
    if (event.data.type === "ping_CryptoExtension") {
        window.postMessage({
            type: "isCryptoExtension",
            success: true
        }, "*");
    }
    // send on background.js
    if (event.data.type === "check_native" || event.data.type === "crypto") {
        chrome.runtime.sendMessage({
            type: event.data.type,
            cmd: event.data.cmd,
            data: event.data.data,
            id: event.data.id
        });
    }
});

// recive from background.js
chrome.runtime.onMessage.addListener((message) => {
    // send on frontend
    if (message.type === "check_native" || message.type === "crypto") {
        window.postMessage({
            type: message.type,
            msg: message.msg,
            id: message.id
        }, "*");
    }
    if (message.type === "native_missing") {
        window.postMessage({
            type: message.type,
            msg: "error",
            id: message.id
        }, "*");
    }
});