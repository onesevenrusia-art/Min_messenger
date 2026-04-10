class ChunkStore {
    constructor(dbName = "chunkdb", version = 1) {
        this.dbName = dbName;
        this.version = version;
        this.db = null;
    }

    // ---------- OPEN ----------
    async open() {
        if (this.db) return this.db;

        return new Promise((resolve, reject) => {

            const request = indexedDB.open(this.dbName, this.version);

            request.onupgradeneeded = (e) => {
                const db = e.target.result;
            
                if (!db.objectStoreNames.contains("chunks")) {
                    const store = db.createObjectStore("chunks", {
                        keyPath: "id",
                        autoIncrement: true
                    });
                    store.createIndex("msg_id", "msg_id", { unique: false });
                    store.createIndex("msg_chunk", ["msg_id", "chunk_id"], { unique: false });
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

    // ---------- SAVE CHUNK ----------
    async saveChunk(msg_id, chunk_id, chunk) {
        const store = await this._store("readwrite");
        return new Promise((resolve, reject) => {
            const req = store.put({
                msg_id,
                chunk_id,
                chunk
            });
            req.onsuccess = () => resolve(true);
            req.onerror = () => reject(req.error);
        });
    }

    // ---------- GET ONE CHUNK ----------
    async getChunk(msg_id, chunk_id) {

        const store = await this._store("readonly");
        const index = store.index("msg_chunk");
    
        return new Promise((resolve, reject) => {
    
            const req = index.get([msg_id, chunk_id]);
    
            req.onsuccess = () => resolve(req.result || null);
            req.onerror = () => reject(req.error);
        });
    }

    // ---------- GET ALL CHUNKS BY MSG ----------
    async getChunksByMsgId(msg_id) {

        const store = await this._store();
        const index = store.index("msg_id");

        return new Promise((resolve, reject) => {

            const req = index.getAll(msg_id);

            req.onsuccess = () => {

                const result = req.result || [];

                result.sort((a, b) => a.chunk_id - b.chunk_id);

                resolve(result);
            };

            req.onerror = () => reject(req.error);

        });
    }

    // ---------- DELETE ALL CHUNKS ----------
    async deleteByMsgId(msg_id) {

        const store = await this._store("readwrite");
        const index = store.index("msg_id");

        return new Promise((resolve, reject) => {

            const req = index.openCursor(IDBKeyRange.only(msg_id));

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

    // ---------- CHECK IF EXISTS ----------
    async hasChunk(msg_id, chunk_id) {

        const store = await this._store();

        return new Promise((resolve, reject) => {

            const req = store.get([msg_id, chunk_id]);

            req.onsuccess = () => resolve(!!req.result);
            req.onerror = () => reject(req.error);

        });
    }

    // ---------- DELETE DB ----------
    async deleteDB() {
        this.db = null;

        return new Promise((resolve, reject) => {

            const req = indexedDB.deleteDatabase(this.dbName);

            req.onsuccess = () => resolve(true);
            req.onerror = () => reject(req.error);

        });
    }
}