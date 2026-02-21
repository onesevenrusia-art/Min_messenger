class UNsentMessageStore {
    constructor(dbName = "chatDB", version = 2) {
        this.dbName = dbName;
        this.version = version;
        this.db = null;
    }

    /* ---------- INIT ---------- */

    async open() {
        if (this.db) return this.db;