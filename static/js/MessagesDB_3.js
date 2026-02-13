class MessageStore {
    constructor(dbName = "chatDB_3", version = 1) {
        this.dbName = dbName;
        this.version = version;
        this.db = null;
    }

    /* ---------- INIT ---------- */
    async open() {
        if (this.db) return this.db;

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);

            request.onupgradeneeded = (e) => {
                const db = e.target.result;

                if (!db.objectStoreNames.contains("messages")) {
                    const store = db.createObjectStore("messages", {
                        keyPath: "id",      // глобальный ID
                        autoIncrement: true
                    });

                    // индекс по чату
                    store.createIndex("chat_id", "chat_id", { unique: false });

                    // индекс для пагинации по глобальному id
                    store.createIndex("chat_global", ["chat_id", "id"], { unique: false });

                    // можно добавить индекс по времени
                    store.createIndex("chat_time", ["chat_id", "created_at"], { unique: false });
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
    async _store(mode = "readonly") {
        if (!this.db) await this.open();
        return this.db.transaction("messages", mode).objectStore("messages");
    }

    /* ---------- SAVE / UPDATE ---------- */
    async save(message) {
        const store = await this._store("readwrite");
        return new Promise((resolve, reject) => {
            const req = store.put(message);
            req.onsuccess = () => resolve(req.result); // вернёт глобальный id
            req.onerror = () => reject(req.error);
        });
    }

    async updateById(id, patch) {
        const old = await this.getById(id);
        if (!old) return false;
        const updated = { ...old, ...patch };
        return this.save(updated);
    }

    /* ---------- DELETE ---------- */
    async deleteById(id) {
        const store = await this._store("readwrite");
        return new Promise((resolve, reject) => {
            const req = store.delete(id);
            req.onsuccess = () => resolve(true);
            req.onerror = () => reject(req.error);
        });
    }

    async deleteByChat(chatId) {
        const store = await this._store("readwrite");
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
        const store = await this._store();
        return new Promise((resolve, reject) => {
            const req = store.get(id);
            req.onsuccess = () => resolve(req.result || null);
            req.onerror = () => reject(req.error);
        });
    }

    /* ---------- PAGINATION: OLDER MESSAGES ---------- */
    async loadOlderMessages(chatId, fromGlobalId, limit = 30) {
        const store = await this._store();
        const index = store.index("chat_global");
        console.log(chatId, fromGlobalId, limit )
        const range = IDBKeyRange.upperBound([chatId, fromGlobalId], true);

        const result = [];

        return new Promise((resolve, reject) => {
            const req = index.openCursor(range, "prev"); // идём назад
            req.onsuccess = (e) => {
                const cursor = e.target.result;
                if (cursor && result.length < limit) {
                    result.push(cursor.value);
                    cursor.continue();
                } else {
                    resolve(result.reverse()); // чтобы от старого к новому
                }
            };
            req.onerror = () => reject(req.error);
        });
    }

    /* ---------- PAGINATION: NEWER MESSAGES ---------- */
    async loadNewerMessages(chatId, afterGlobalId) {
        const store = await this._store();
        const index = store.index("chat_global");

        const range = IDBKeyRange.lowerBound([chatId, afterGlobalId], true);

        const result = [];

        return new Promise((resolve, reject) => {
            const req = index.openCursor(range); // идём вперёд
            req.onsuccess = (e) => {
                const cursor = e.target.result;
                if (cursor) {
                    result.push(cursor.value);
                    cursor.continue();
                } else {
                    resolve(result);
                }
            };
            req.onerror = () => reject(req.error);
        });
    }

    async getChatMessages(chatId, limit = 30, beforeGlobalId = Infinity) {
        const store = await this._store();
        const index = store.index("chat_global"); // индекс ["chat_id", "id"]
    
        // Диапазон: все сообщения меньше beforeGlobalId
        const range = IDBKeyRange.upperBound([chatId, beforeGlobalId], true);
    
        const result = [];
    
        return new Promise((resolve, reject) => {
            // Курсор идёт "назад", от больших id к меньшим
            const req = index.openCursor(range, "prev");
    
            req.onsuccess = (e) => {
                const cursor = e.target.result;
    
                if (cursor && result.length < limit) {
                    result.push(cursor.value); // собираем сообщения
                    cursor.continue();
                } else {
                    // возвращаем от старого к новому
                    resolve(result.reverse());
                }
            };
    
            req.onerror = () => reject(req.error);
        });
    }

    /* ---------- CLEAR DB (опционально) ---------- */
    async deleteDB() {
        this.db = null;
        return new Promise((resolve, reject) => {
            const req = indexedDB.deleteDatabase(this.dbName);
            req.onsuccess = () => resolve(true);
            req.onerror = () => reject(req.error);
        });
    }
}