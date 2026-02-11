class MessageStore {
    constructor(dbName = "chatDB", version = 2) {
        this.dbName = dbName;
        this.version = version;
        this.db = null;
    }

    /* ---------- INIT ---------- */

    async open() {
        if (this.db) return this.db;

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);
            indexedDB.deleteDatabase(this.dbName)
            request.onupgradeneeded = (e) => {
                const db = e.target.result;

                if (!db.objectStoreNames.contains("messages")) {
                    const store = db.createObjectStore("messages", {
                        keyPath: "id",
                        autoIncrement: true // primary key
                    });

                    store.createIndex("chat_id", "chat_id", { unique: false });
                    store.createIndex(
                        "chat_internal",
                        ["chat_id", "internal_id"],
                        { unique: false }
                    );
                }
            };

            request.onsuccess = () => {
                this.db = request.result;
                resolve(this.db);
            };

            request.onerror = () => reject(request.error);
        });
    }

    /* ---------- INTERNAL ---------- */

    _store(mode = "readonly") {
        return this.db.transaction("messages", mode).objectStore("messages");
    }

    /* ---------- SAVE / UPDATE ---------- */

    async save(message) {
        const db = await this.open();
        return new Promise((resolve, reject) => {
            const req = this._store("readwrite").put(message);
            req.onsuccess = () => resolve(true);
            req.onerror = () => reject(req.error);
        });
    }

    async updateById(id, patch) {
        const old = await this.getById(id);
        if (!old) return false;

        const updated = { ...old, ...patch };
        return new Promise((resolve, reject) => {
            const req = this._store("readwrite").put(updated);
            req.onsuccess = () => resolve(true);
            req.onerror = () => reject(req.error);
        });
    }

    /* ---------- DELETE ---------- */

    async deleteById(id) {
        return new Promise((resolve, reject) => {
            const req = this._store("readwrite").delete(id);
            req.onsuccess = () => resolve(true);
            req.onerror = () => reject(req.error);
        });
    }

    async deleteByChat(chatId) {
        const store = this._store("readwrite");
        const index = store.index("chat_id");

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
        return new Promise((resolve, reject) => {
            const req = this._store().get(id);
            req.onsuccess = () => resolve(req.result || null);
            req.onerror = () => reject(req.error);
        });
    }

    async getByInternalId(chatId, internalId) {
        const store = this._store();
        const index = store.index("chat_internal");
        return new Promise((resolve, reject) => {
            const req = index.get([chatId, internalId]);
            req.onsuccess = () => resolve(req.result || null);
            req.onerror = () => reject(req.error);
        });
    }

    async getChatMessages(chatId, limit = 50, beforeInternalId = Infinity) {
        const store = this._store();
        const index = store.index("chat_internal");

        const range = IDBKeyRange.bound(
            [chatId, 0],
            [chatId, beforeInternalId],
            false,
            true
        );
        const result = [];
                return new Promise((resolve, reject) => {
                    const req = index.openCursor(range, "prev");
                    req.onsuccess = (e) => {
                        const cursor = e.target.result;
                        if (cursor && result.length < limit) {
                            result.push(cursor.value);
                            cursor.continue();
                        } else {
                            resolve(result.reverse());
                        }
                    };
                    req.onerror = () => reject(req.error);
                });
            }
        }