// background.js

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    const tabId = sender.tab.id || null; // нужна вкладка, чтобы отправить обратно

    if (!tabId) return; // если нет вкладки — игнорируем

    // 1️⃣ Проверка native приложения
    if (message.type === "check_native") {
        // Например, проверка наличия native-app
        const nativeAvailable = false; // временно, под реальную проверку

        chrome.tabs.sendMessage(tabId, {
            type: nativeAvailable ? "check_native" : "native_missing",
            msg: nativeAvailable ? "ok" : "error",
            id: message.id
        });
    }

    // 2️⃣ Криптозапросы (подпись, расшифровка и т.д.)
    else if (message.type === "crypto") {
        // Здесь должен быть вызов native-app через chrome.runtime.connectNative
        // Пока просто эмуляция ответа
        const fakeResult = { signed: "FAKE_SIGNATURE" };

        chrome.tabs.sendMessage(tabId, {
            type: "crypto",
            msg: fakeResult,
            id: message.id
        });
    }
});