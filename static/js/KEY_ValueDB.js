class SettingsDB {
    constructor(dbName = "settingsDB", version = 1) {
        this.dbName = dbName;
        this.version = version;
        this.db = null;
    }

    async open() {
        if (this.db) return this.db;

        return new Promise((resolve, reject) => {
            const req = indexedDB.open(this.dbName, this.version);

            req.onupgradeneeded = () => {
                const db = req.result;

                if (!db.objectStoreNames.contains("settings")) {
                    db.createObjectStore("settings");
                }
            };

            req.onsuccess = () => {
                this.db = req.result;
                resolve(this.db);
            };

            req.onerror = () => reject(req.error);
        });
    }

    async set(key, value) {
        const db = await this.open();

        return new Promise((resolve, reject) => {
            const tx = db.transaction("settings", "readwrite");

            tx.objectStore("settings").put(value, key);

            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });
    }

    async get(key) {
        const db = await this.open();

        return new Promise((resolve, reject) => {
            const tx = db.transaction("settings", "readonly");
            const req = tx.objectStore("settings").get(key);

            req.onsuccess = () => resolve(req.result);
            req.onerror = () => reject(req.error);
        });
    }

    async delete(key) {
        const db = await this.open();

        return new Promise((resolve, reject) => {
            const tx = db.transaction("settings", "readwrite");

            tx.objectStore("settings").delete(key);

            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });
    }
}