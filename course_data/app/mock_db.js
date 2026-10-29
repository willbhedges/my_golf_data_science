/* In-memory stand-in for the artifact `db` capability (window.claude.use("db")), for tests only: the subset
 * shared_store.js uses (doc get / set / update with nested merge, collection doc / orderBy / limit / onSnapshot).
 * Several "viewers" share one MockServer, like golfers sharing one artifact database. Never embedded in the page. */
(function (root) {
  "use strict";
  const clone = x => JSON.parse(JSON.stringify(x));
  function merge(a, b) {                       /* db.d.ts update(): nested objects merge, anything else replaces */
    const o = Object.assign({}, a);
    for (const [k, v] of Object.entries(b)) o[k] = v && typeof v === "object" && !Array.isArray(v) && o[k] && typeof o[k] === "object" && !Array.isArray(o[k]) ? merge(o[k], v) : v;
    return o;
  }
  class MockServer {
    constructor() { this.docs = new Map(); this.subs = new Set(); this.writes = 0; this.failWrites = false; }
    get(path) { return this.docs.has(path) ? clone(this.docs.get(path)) : null; }
    set(path, data) { this._w(); this.docs.set(path, clone(data)); this._notify(); }
    update(path, data) { this._w(); if (!this.docs.has(path)) throw {code: "invalid_argument", message: "no such document"}; this.docs.set(path, merge(this.docs.get(path), clone(data))); this._notify(); }
    list(coll) { const out = []; for (const [p, d] of this.docs) { const i = p.lastIndexOf("/"); if (p.slice(0, i) === coll) out.push({id: p.slice(i + 1), data: clone(d)}); } return out; }
    _w() { if (this.failWrites) throw {code: "invalid_argument", message: "write refused (view-only)"}; this.writes++; }
    _notify() { for (const f of [...this.subs]) setTimeout(f, 0); }
  }
  function snapOf(id, data) { const d = data == null ? undefined : Object.freeze(data); return {id, exists: data != null, data: () => d, metadata: {fromCache: false, hasPendingWrites: false}}; }
  /* a viewer's `db` namespace over a server; `call` lets a browser page reach a server living in node */
  function mockDb(server) {
    const call = async (op, ...a) => { await Promise.resolve(); return server[op](...a); };
    function query(coll, ord, lim) {
      const run = async () => { let rows = await call("list", coll);
        if (ord) rows.sort((x, y) => (x.data[ord[0]] < y.data[ord[0]] ? -1 : 1) * (ord[1] === "desc" ? -1 : 1));
        if (lim) rows = rows.slice(0, lim);
        const docs = rows.map(r => snapOf(r.id, r.data));
        return {docs, size: docs.length, empty: !docs.length, docChanges: () => [], metadata: {fromCache: false, hasPendingWrites: false}}; };
      return {
        orderBy: (f, dir) => query(coll, [f, dir || "asc"], lim), limit: n => query(coll, ord, n), where: () => query(coll, ord, lim),
        get: run,
        onSnapshot(next, err) { let live = true; const f = () => live && run().then(next, err);
          server.subs.add(f); setTimeout(f, 0); return () => { live = false; server.subs.delete(f); }; },
        doc: id => docRef(coll + "/" + (id || Math.random().toString(36).slice(2))), path: coll,
        add: async data => { const r = docRef(coll + "/" + Math.random().toString(36).slice(2)); await r.set(data); return r; }
      };
    }
    function docRef(path) {
      const id = path.slice(path.lastIndexOf("/") + 1);
      return {id, path, get: async () => snapOf(id, await call("get", path)), set: data => call("set", path, data),
              update: data => call("update", path, data), delete: async () => { server.docs.delete(path); },
              onSnapshot(next) { const f = () => call("get", path).then(d => next(snapOf(id, d))); server.subs.add(f); setTimeout(f, 0); return () => server.subs.delete(f); }};
    }
    return Object.freeze({doc: docRef, collection: c => query(c)});
  }
  function mockClaude(server, uid) {
    const user = Object.freeze({id: async () => uid, can: async () => !server.failWrites, isOwner: () => false, canEdit: () => false});
    const db = mockDb(server);
    return {use: async name => name === "db" ? db : name === "user" ? user : null};
  }
  const api = {MockServer, mockDb, mockClaude, merge};
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.MockDB = api;
})(typeof window !== "undefined" ? window : this);
