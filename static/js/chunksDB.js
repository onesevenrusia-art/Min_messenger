
class ChunkStore {
    constructor(dbName = "chunkdb", version = 1) {
        this.dbName = dbName;
        this.version = version;
        this.db = null;
    }


    async open() {
        if (this.db) return this.db;

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);
            request.onupgradeneeded = (e) => {
                const db = e.target.result;
                if (!db.objectStoreNames.contains("chunks")) {
                    const store = db.createObjectStore("chunks", {
                        keyPath: "id",  // глобальный ID
                        autoIncrement: true // сам ставит id
                    });
                    store.createIndex("msg_id", "msg_id", { unique: false });
                }
            };
            request.onsuccess = () => {
                this.db = request.result;
                resolve(this.db);
            };
            request.onerror = () => reject(request.error);
        });
    }

    async _store(mode = "readonly") {
        if (!this.db) await this.open();
        return this.db.transaction("chunks", mode).objectStore("chunks");
    }

    async save(message) {
        if (!this.db) await this.open();
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction("chunks", "readwrite");
            const store = tx.objectStore("chunks");
            const req = store.put(message);
            req.onerror = () => reject(req.error);
            tx.oncomplete = () => resolve(req.result);
            tx.onerror = () => reject(tx.error);
        });
    }

    async deleteBymsg_id(chatId) {
        const store = await this._store("readwrite");
        const index = store.index("msg_id");

        return new Promise((resolve, reject) => {
            const req = index.openCursor(IDBKeyRange.only(chatId));
            req.onsuccess = (e) => {
                const cursor = e.target.result;
                if (cursor) {
                    cursor.delete();
                    cursor.continue();
                } else {
                    resolve(true);
                }
            };
            req.onerror = () => reject(req.error);
        });
    }

    /* ---------- GET ---------- */
    async getById(id) {
        const store = await this._store();
        return new Promise((resolve, reject) => {
            const req = store.get(id);
            req.onsuccess = () => resolve(req.result || null);
            req.onerror = () => reject(req.error);
        });
    }
    async deleteDB() {
        this.db = null;
        return new Promise((resolve, reject) => {
            const req = indexedDB.deleteDatabase(this.dbName);
            req.onsuccess = () => resolve(true);
            req.onerror = () => reject(req.error);
        });
    }


}