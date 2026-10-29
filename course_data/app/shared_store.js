/* Aim Caddie shared course state (golf_shared/1): golfer-confirmed hole maps and "problem with this hole" reports.
 *
 * One interface, two backends:
 *   * "shared": the artifact's shared database (window.claude.use("db")), so a course confirmed once is confirmed
 *     for everyone who opens the page after;
 *   * "local": this browser's localStorage (file://, a saved copy, a viewer without the db grant, a signed-out
 *     visitor). Same documents, same code paths, seen by this browser only.
 *
 * Documents (SCHEMA.md, "Shared confirmations"):
 *   maps/<course id>   {schema: "golf_shared_map/1", course, card, card_by, card_at,
 *                       logs: {<golfer id>: {log: [Action], at, taps}}}
 *     Each golfer writes only their own entry under `logs` (an update merges that key alone), so two golfers
 *     confirming at once do not overwrite each other. Actions are canonical (geo-anchored, not "yes to whatever
 *     hole 7 was on my screen"): they replay onto the same pool in any order.
 *   reports/<auto id>  {schema: "golf_report/1", course, hole, kind, text, tee, at, by}
 *
 * Everything read back is untrusted (anyone at Contributor level writes it): cleanAction / cleanReport drop
 * anything off-shape, and the page escapes every string it shows.
 */
(function (root) {
  "use strict";
  const LKEY = "aimcaddie_shared1", GKEY = "aimcaddie_gid";
  const MAX_LOG = 120, MAX_GOLFERS = 60, MAX_REPORTS = 500, MAX_TEXT = 500;
  const KINDS = ["wrong_hole", "tee", "green", "hazard", "advice", "other"];

  const num = x => typeof x === "number" && isFinite(x);
  const ll = p => Array.isArray(p) && p.length === 2 && num(p[0]) && num(p[1]) && Math.abs(p[0]) <= 180 && Math.abs(p[1]) <= 90
    ? [+p[0].toFixed(7), +p[1].toFixed(7)] : null;
  const ref = r => { const s = String(r == null ? "" : r); return /^\d{1,2}$/.test(s) ? s : null; };
  const iso = s => typeof s === "string" && s.length <= 40 && !isNaN(Date.parse(s)) ? s : null;

  /* one canonical action: {question, kind: "locate"|"reject", ref, answer: {tee_ll, green_ll}, taps} */
  function cleanAction(a) {
    if (!a || typeof a !== "object") return null;
    const r = ref(a.ref);
    if (!r || (a.kind !== "locate" && a.kind !== "reject")) return null;
    const ans = a.answer || {}, t = ans.tee_ll == null ? null : ll(ans.tee_ll), g = ans.green_ll == null ? null : ll(ans.green_ll);
    if (!g && !t) return null;
    if ((ans.tee_ll != null && !t) || (ans.green_ll != null && !g)) return null;
    const taps = a.taps === 1 || a.taps === 2 ? a.taps : (a.kind === "locate" ? 2 : 1);
    return {question: (a.kind === "locate" ? "l" : "r") + r, kind: a.kind, ref: r, answer: {tee_ll: t, green_ll: g}, taps};
  }
  function cleanLog(log) {
    if (!Array.isArray(log)) return [];
    const out = [];
    for (const a of log.slice(-MAX_LOG)) { const c = cleanAction(a); if (c) out.push(c); }
    return out;
  }
  /* a typed scorecard as typed_card.js builds it: {tee_sets: {name: {yards[], total}}, par[]?} */
  function cleanCard(c) {
    if (!c || typeof c !== "object" || !c.tee_sets || typeof c.tee_sets !== "object") return null;
    const sets = {};
    for (const [k, v] of Object.entries(c.tee_sets).slice(0, 4)) {
      if (typeof k !== "string" || k.length > 24 || !v || !Array.isArray(v.yards) || v.yards.length > 27) continue;
      if (!v.yards.every(y => num(y) && y > 0 && y < 1000)) continue;
      sets[k] = {yards: v.yards.slice(), total: v.yards.reduce((s, y) => s + y, 0)};
    }
    if (!Object.keys(sets).length) return null;
    const out = Object.assign({}, c, {tee_sets: sets});
    if (c.par != null) out.par = Array.isArray(c.par) && c.par.length <= 27 && c.par.every(p => p === 3 || p === 4 || p === 5 || p === 6) ? c.par.slice() : null;
    for (const k of Object.keys(out)) if (!["tee_sets", "par", "source", "name", "holes", "unit"].includes(k)) delete out[k];
    if (out.source != null && typeof out.source !== "string") delete out.source;
    if (out.name != null && typeof out.name !== "string") delete out.name;
    if (out.unit != null && typeof out.unit !== "string") delete out.unit;
    if (out.holes != null && !num(out.holes)) delete out.holes;
    return out;
  }
  function cleanMap(d, course) {
    if (!d || typeof d !== "object") return null;
    const logs = {};
    const ents = Object.entries(d.logs && typeof d.logs === "object" ? d.logs : {})
      .filter(([g, e]) => typeof g === "string" && g.length <= 128 && e && typeof e === "object")
      .map(([g, e]) => [g, {log: cleanLog(e.log), at: iso(e.at) || "1970-01-01T00:00:00Z", taps: num(e.taps) ? Math.max(0, Math.min(999, Math.round(e.taps))) : 0}])
      .filter(([, e]) => e.log.length)
      .sort((a, b) => a[1].at < b[1].at ? 1 : -1).slice(0, MAX_GOLFERS);
    for (const [g, e] of ents) logs[g] = e;
    return {schema: "golf_shared_map/1", course: course || (typeof d.course === "string" ? d.course : null),
            card: d.card === null ? null : cleanCard(d.card), card_at: iso(d.card_at), logs};
  }
  function cleanReport(r, id) {
    if (!r || typeof r !== "object") return null;
    const course = typeof r.course === "string" && /^[a-z0-9_.-]{1,64}$/.test(r.course) ? r.course : null;
    const hole = ref(r.hole);
    if (!course || !hole) return null;
    return {id: typeof id === "string" ? id.slice(0, 64) : (typeof r.id === "string" ? r.id.slice(0, 64) : null),
            course, hole: +hole, kind: KINDS.includes(r.kind) ? r.kind : "other",
            text: typeof r.text === "string" ? r.text.slice(0, MAX_TEXT) : "",
            tee: typeof r.tee === "string" ? r.tee.slice(0, 24) : null, at: iso(r.at) || "1970-01-01T00:00:00Z",
            mine: false, by: typeof r.by === "string" ? r.by.slice(0, 128) : null};
  }

  /* every golfer's log but `me`'s, oldest contribution first, then `mine` (this golfer's, from this device) */
  function replayLog(doc, me, mine) {
    const ents = Object.entries((doc && doc.logs) || {}).filter(([g]) => g !== me).sort((a, b) => a[1].at < b[1].at ? -1 : 1);
    const out = [];
    for (const [, e] of ents) out.push(...e.log);
    return out.concat(cleanLog(mine || []));
  }
  function golferCount(doc, me, mineLen) {
    const g = new Set(Object.keys((doc && doc.logs) || {}).filter(k => k !== me));
    if (mineLen) g.add(me);
    return g.size;
  }

  /* ------------------------------------------------------------------ the store */
  function readLocal(ls) {
    try { const s = JSON.parse(ls.getItem(LKEY) || "null"); if (s && typeof s === "object") return {maps: s.maps || {}, reports: Array.isArray(s.reports) ? s.reports : []}; } catch (e) {}
    return {maps: {}, reports: []};
  }
  function writeLocal(ls, s) { try { ls.setItem(LKEY, JSON.stringify(s)); return true; } catch (e) { return false; } }
  function localGid(ls) {
    try { let g = ls.getItem(GKEY); if (!g) { g = "local-" + Math.random().toString(36).slice(2, 12); ls.setItem(GKEY, g); } return g; } catch (e) { return "local-anon"; }
  }

  /**
   * createStore({localStorage, claude, timeoutMs}) -> store
   *   store.mode          "connecting" | "shared" | "local"
   *   store.why           why it is local (text for the page)
   *   store.gid           this golfer's id (user.id() when shared, a random per-browser id otherwise)
   *   store.map(course)   cleaned maps/<course> doc or null (cache; kept live by a snapshot listener when shared)
   *   store.reports(course?) cleaned reports, newest first
   *   store.saveLog(course, log, opts)  write this golfer's log (+ opts.card when they typed one) -> Promise<"shared"|"local">
   *   store.addReport(r)  -> Promise<"shared"|"local">
   *   store.onChange(fn)  fn(kind) after every cache change ("maps" | "reports" | "mode")
   *   store.ready         Promise resolving once the mode is settled
   */
  function createStore(opt) {
    opt = opt || {};
    const ls = opt.localStorage || {getItem: () => null, setItem: () => {}};
    const fns = [];
    const localG = localGid(ls);
    const S = {mode: "connecting", why: "", gid: localG, canWrite: null};
    let local = readLocal(ls), shared = {maps: {}, reports: []}, db = null;
    const emit = k => { for (const f of fns) { try { f(k); } catch (e) { if (typeof console !== "undefined") console.warn(e); } } };
    S.onChange = f => { fns.push(f); };
    S.map = course => {
      const src = S.mode === "shared" ? shared.maps : local.maps;
      return src[course] ? cleanMap(src[course], course) : null;
    };
    S.reports = course => {
      const arr = S.mode === "shared" ? shared.reports : local.reports.map(r => Object.assign(cleanReport(r) || {}, {mine: true}));
      const mineIds = new Set(local.reports.map(r => r.id));
      return arr.filter(r => r && r.course && (!course || r.course === course))
        .map(r => Object.assign({}, r, {mine: r.mine || mineIds.has(r.id) || (r.by && r.by === S.gid)}))
        .sort((a, b) => a.at < b.at ? 1 : -1);
    };
    function localSave(course, log, o) {
      const d = local.maps[course] || {schema: "golf_shared_map/1", course, logs: {}};
      d.logs = d.logs || {};
      if (log && log.length) d.logs[S.gid] = {log, at: new Date().toISOString(), taps: o.taps || 0}; else delete d.logs[S.gid];
      if (o.card !== undefined) { d.card = o.card; d.card_at = new Date().toISOString(); }
      local.maps[course] = d;
      writeLocal(ls, local);
    }
    let chain = Promise.resolve();                       /* one write at a time (the db asks for it per document) */
    S.saveLog = (course, log, o) => {
      o = o || {};
      log = cleanLog(log);
      const card = o.card === undefined ? undefined : (o.card === null ? null : cleanCard(o.card));
      localSave(course, log, {taps: o.taps, card});
      if (S.mode !== "shared" || !db) { emit("maps"); return Promise.resolve("local"); }
      const at = new Date().toISOString();
      const mine = log.length ? {log, at, taps: o.taps || 0} : null;
      const run = async () => {
        const ref = db.doc("maps/" + course);
        const snap = await ref.get();
        if (!snap.exists) {
          const body = {schema: "golf_shared_map/1", course, logs: mine ? {[S.gid]: mine} : {}};
          if (card !== undefined) { body.card = card; body.card_at = at; }
          await ref.set(body);
        } else {
          const cur = snap.data() || {}, logs = Object.assign({}, cur.logs || {});
          if (mine) logs[S.gid] = mine; else delete logs[S.gid];
          /* `update` merges nested objects key by key: send only this golfer's entry (others' writes survive);
             removing an entry needs the whole map, so that case replaces `logs` from the fresh read */
          const patch = mine ? {logs: {[S.gid]: mine}} : {logs};
          if (card !== undefined) { patch.card = card; patch.card_at = at; }
          if (mine) await ref.update(patch); else await ref.set(Object.assign({}, cur, patch));
        }
        shared.maps[course] = Object.assign({}, shared.maps[course] || {}, {logs: Object.assign({}, (shared.maps[course] || {}).logs || {}, mine ? {[S.gid]: mine} : {})});
        if (!mine && shared.maps[course]) delete shared.maps[course].logs[S.gid];
        if (card !== undefined) shared.maps[course].card = card;
        return "shared";
      };
      const p = chain.then(run, run).catch(e => { S.lastError = (e && e.code) || String(e); if (e && e.code === "invalid_argument") S.canWrite = false; return "local"; });
      chain = p;
      return p.then(r => { emit("maps"); return r; });
    };
    S.addReport = r => {
      const body = {schema: "golf_report/1", course: r.course, hole: +r.hole, kind: r.kind, text: String(r.text || "").slice(0, MAX_TEXT),
                    tee: r.tee || null, at: new Date().toISOString(), by: S.gid};
      const c = cleanReport(body);
      if (!c) return Promise.reject(new Error("bad report"));
      c.id = "r" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
      local.reports = [c].concat(local.reports).slice(0, MAX_REPORTS);
      writeLocal(ls, local);
      if (S.mode !== "shared" || !db) { emit("reports"); return Promise.resolve("local"); }
      return db.collection("reports").doc(c.id).set(Object.assign({}, body)).then(() => {
        if (!shared.reports.some(x => x.id === c.id)) shared.reports = [Object.assign({}, c)].concat(shared.reports);
        emit("reports"); return "shared";
      }, e => { S.lastError = (e && e.code) || String(e); if (e && e.code === "invalid_argument") S.canWrite = false; emit("reports"); return "local"; });
    };
    function goLocal(why) { S.mode = "local"; S.why = why; db = null; emit("mode"); }
    S.ready = (async () => {
      const C = opt.claude;
      if (!C || typeof C.use !== "function") { goLocal("no shared storage on this page (opened outside claude.ai)"); return S.mode; }
      let to;
      const timeout = new Promise(res => { to = setTimeout(() => res(null), opt.timeoutMs || 12000); });
      try {
        const [d, u] = await Promise.race([Promise.all([C.use("db"), C.use("user").catch(() => null)]), timeout.then(() => [null, null])]);
        clearTimeout(to);
        if (!d) { goLocal("shared storage is not available to this view (signed out, or not granted)"); return S.mode; }
        db = d;
        if (u) {
          try { const id = await u.id(); if (id) S.gid = String(id); } catch (e) {}
          try { const w = await u.can("data.write"); S.canWrite = w; } catch (e) {}
        }
        S.mode = "shared"; S.why = "";
        /* two listeners for the whole page: every course's map doc, and the newest reports */
        db.collection("maps").onSnapshot(snap => {
          const m = {}; for (const x of snap.docs) m[x.id] = x.data();
          shared.maps = m; emit("maps");
        }, e => { S.lastError = e && e.code; });
        db.collection("reports").orderBy("at", "desc").limit(MAX_REPORTS).onSnapshot(snap => {
          shared.reports = snap.docs.map(x => cleanReport(x.data(), x.id)).filter(Boolean); emit("reports");
        }, e => { S.lastError = e && e.code; });
        /* this browser's own earlier local-only work goes up once shared storage is there */
        for (const [course, d0] of Object.entries(local.maps)) {
          const mine = d0 && d0.logs && (d0.logs[localG] || d0.logs[S.gid]);
          if (mine && mine.log && mine.log.length && !d0.pushed) { d0.pushed = true; writeLocal(ls, local); S.saveLog(course, mine.log, {taps: mine.taps, card: d0.card === undefined ? undefined : d0.card}); }
        }
        emit("mode");
      } catch (e) { clearTimeout(to); goLocal("shared storage failed to start (" + ((e && e.code) || e) + ")"); }
      return S.mode;
    })();
    return S;
  }

  const api = {createStore, cleanAction, cleanLog, cleanCard, cleanMap, cleanReport, replayLog, golferCount, KINDS, LKEY};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.SharedStore = api;
})(typeof window !== "undefined" ? window : this);
