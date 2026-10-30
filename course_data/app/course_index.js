/* Aim Caddie national course index + "Request this course" (us_courses/1 -> course_index/1, course_data/app/SCHEMA.md
 * "National index and requests").
 *
 * Self-contained: build_app.py concatenates this file into the engine script and replaces the data placeholder below
 * with the gzip + base64 compact index (course_index.py). It needs nothing from app_template.html beyond the pick
 * screen's existing DOM (#app[data-screen=pick], #q, #fState, #list, .lcard[data-lib][data-status]) and the page's
 * global D.library.entries. A MutationObserver adds, after each pick-screen render:
 *   * a "More US courses" section: national index rows matching the search that the library does not list, each with
 *     a "Request this course" button;
 *   * a "Request this course" button on library cards that have no page yet (status "none").
 * Requests go to the artifact's shared db, collection "requests" (one doc per golfer per course), else localStorage.
 */
(function (root) {
  "use strict";
  const DATA = /*__COURSE_INDEX__*/null;   /* {n, built, b64}: gzip of "name|city|ST|lat|lon|osm|holes|tier" lines */
  const LKEY = "aimcaddie_requests1", MAX_SHOW = 30;
  const TIER = {A: "OSM maps every hole · scorecard known", B: "OSM maps every hole", C: "OSM maps some holes",
                D: "outline only on OSM"};
  const OSM = {w: "way", r: "relation", n: "node"};

  const norm = s => String(s || "").toLowerCase().replace(/&/g, " and ")
    .replace(/\b(golf|course|club|country|cc|gc|the|links|and|of|at)\b/g, " ").replace(/[^a-z0-9]/g, "");
  /* the request slug (requests_to_batch.py uses the same rule) */
  function slugOf(name) {
    let s = String(name || "").toLowerCase().replace(/&/g, " and ").replace(/['’]/g, "")
      .replace(/\b(golf|course|club|country|and|the|cc|gc)\b/g, " ").replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
    return (s || "course").slice(0, 48);
  }
  const escH = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));

  let rows = null, loading = null, failed = null;
  function parse(text) {
    return text.split("\n").filter(Boolean).map(l => {
      const p = l.split("|");
      return {name: p[0], city: p[1], state: p[2], lat: +p[3], lon: +p[4], osm: p[5] ? OSM[p[5][0]] + "/" + p[5].slice(1) : "",
              holes: +p[6] || 0, tier: p[7] || "D", hay: (p[0] + " " + p[1] + " " + p[2]).toLowerCase(), key: p[2] + "|" + norm(p[0])};
    });
  }
  function load() {
    if (rows || loading) return loading || Promise.resolve(rows);
    if (!DATA || !DATA.b64) { failed = "no national index in this build"; return Promise.resolve(null); }
    loading = (async () => {
      try {
        const bin = Uint8Array.from(atob(DATA.b64), c => c.charCodeAt(0));
        if (typeof DecompressionStream === "undefined") throw new Error("this browser cannot unpack the index");
        const ds = new Blob([bin]).stream().pipeThrough(new DecompressionStream("gzip"));
        rows = parse(await new Response(ds).text());
      } catch (e) { failed = String((e && e.message) || e); rows = null; }
      loading = null; refresh(); return rows;
    })();
    return loading;
  }
  function libKeys() {
    const L = (root.D && root.D.library && root.D.library.entries) || (typeof D !== "undefined" ? D.library.entries : []);
    const k = new Set();
    for (const e of L) k.add((e.state || "") + "|" + norm(e.name));
    return k;
  }
  function search(q, state) {
    if (!rows) return {list: [], n: 0};
    const words = String(q || "").toLowerCase().split(/[\s,]+/).filter(Boolean);
    if (!words.length) return {list: [], n: 0};
    const lk = libKeys(), out = [];
    let n = 0;
    for (const r of rows) {
      if (state && state !== "all" && r.state !== state) continue;
      if (!words.every(w => r.hay.includes(w) || (w.length === 2 && r.state.toLowerCase() === w))) continue;
      if (lk.has(r.key)) continue;
      n++;
      if (out.length < MAX_SHOW) out.push(r);
    }
    out.sort((a, b) => a.tier.localeCompare(b.tier) || a.name.localeCompare(b.name));
    return {list: out, n};
  }
  function byKey(state, name) {
    if (!rows) return null;
    const k = state + "|" + norm(name);
    return rows.find(r => r.key === k) || null;
  }

  /* ---------------------------------------------------------------- requests: shared db "requests", else local */
  const R = {mode: "connecting", db: null, uid: null, counts: {}, mine: new Set()};
  function readLocal() { try { const s = JSON.parse(localStorage.getItem(LKEY) || "[]"); return Array.isArray(s) ? s : []; } catch (e) { return []; } }
  function writeLocal(a) { try { localStorage.setItem(LKEY, JSON.stringify(a.slice(-200))); } catch (e) {} }
  for (const d of readLocal()) R.mine.add(d.slug + "|" + d.state);
  const docId = (slug, state, uid) => (state.toLowerCase() + "_" + slug + "__" + String(uid).replace(/[^A-Za-z0-9_-]/g, "").slice(0, 40)).slice(0, 120);
  (async () => {
    const C = root.claude;
    if (!C || typeof C.use !== "function") { R.mode = "local"; return; }
    try {
      const to = new Promise(res => setTimeout(() => res([null, null]), 12000));
      const [db, u] = await Promise.race([Promise.all([C.use("db"), C.use("user").catch(() => null)]), to]);
      if (!db) { R.mode = "local"; return refresh(); }
      R.db = db; R.mode = "shared";
      if (u) { try { R.uid = String(await u.id()); } catch (e) {} }
      db.collection("requests").onSnapshot(snap => {
        const c = {};
        for (const x of snap.docs) { const d = x.data() || {};
          if (typeof d.slug !== "string" || typeof d.state !== "string") continue;
          const k = d.slug.slice(0, 64) + "|" + d.state.slice(0, 2);
          c[k] = (c[k] || 0) + 1;
          if (R.uid && d.user_id === R.uid) R.mine.add(k); }
        R.counts = c; refresh();
      }, () => {});
      refresh();
    } catch (e) { R.mode = "local"; refresh(); }
  })();
  function uid() {
    if (R.uid) return R.uid;
    try { let g = localStorage.getItem("aimcaddie_gid"); if (!g) { g = "local-" + Math.random().toString(36).slice(2, 12); localStorage.setItem("aimcaddie_gid", g); } return g; } catch (e) { return "local-anon"; }
  }
  async function request(c) {
    const doc = {schema: "golf_request/1", slug: slugOf(c.name), name: String(c.name).slice(0, 120),
                 city: String(c.city || "").slice(0, 80), state: String(c.state || "").slice(0, 2),
                 osm: /^(way|relation|node)\/\d+$/.test(c.osm || "") ? c.osm : null,
                 lat: isFinite(c.lat) ? +(+c.lat).toFixed(5) : null, lon: isFinite(c.lon) ? +(+c.lon).toFixed(5) : null,
                 holes: c.holes || null, requested_at: new Date().toISOString(), user_id: uid()};
    const k = doc.slug + "|" + doc.state;
    R.mine.add(k);
    const loc = readLocal(); loc.push(doc); writeLocal(loc);
    if (R.mode === "shared" && R.db) {
      try { await R.db.collection("requests").doc(docId(doc.slug, doc.state, doc.user_id)).set(doc); R.last = "shared"; }
      catch (e) { R.last = "local"; R.err = (e && e.code) || String(e); }
    } else R.last = "local";
    refresh();
    return R.last;
  }

  /* ---------------------------------------------------------------- UI (added to the pick screen after each render) */
  function reqButton(c, idx) {
    const k = slugOf(c.name) + "|" + c.state, n = R.counts[k] || 0, mine = R.mine.has(k);
    const who = n ? ` · ${n} golfer${n === 1 ? "" : "s"} asked` : "";
    return mine ? `<span class="badge shared" data-nreq="1">Requested${who}</span>${R.mode !== "shared" ? ` <span class="sub">(saved on this device; the shared list needs the published page)</span>` : ""}`
      : `<button class="btn" data-nreq-i="${idx}">Request this course</button>${n ? `<span class="sub">${n} golfer${n === 1 ? "" : "s"} asked</span>` : ""}`;
  }
  let shown = [];
  function section(q, state) {
    const total = DATA && DATA.n ? DATA.n : 0;
    if (!total) return "";
    if (!rows) return `<section class="panel stack" id="natidx" style="gap:6px"><div class="label">More US courses</div><p class="sub">${failed ? "National index unavailable: " + escH(failed) : `Loading the national index (${total.toLocaleString()} courses)…`}</p></section>`;
    const {list, n} = search(q, state);
    shown = list;
    const head = `<div class="spread"><span class="label">More US courses</span><span class="sub">${total.toLocaleString()} in the national index (OpenStreetMap)</span></div>`;
    if (!String(q || "").trim()) return `<section class="panel stack" id="natidx" style="gap:6px">${head}<p class="sub">Search above to find any US course. A course with no page yet can be requested: requests are built in batches.</p></section>`;
    const cards = list.map((c, i) => `<article class="lcard none" data-nat="${i}">
        <div class="spread" style="align-items:flex-start"><h3 class="name">${escH(c.name)}</h3><span class="badge none" title="${escH(TIER[c.tier] || "")}">No page yet</span></div>
        <div class="sub">${escH([c.city, c.state].filter(Boolean).join(", "))}${c.holes ? ` · ${c.holes} holes` : ""} · ${escH(TIER[c.tier] || "")}</div>
        <div class="acts">${reqButton(c, i)}</div></article>`).join("");
    return `<section class="stack" id="natidx" style="gap:8px">${head}
      <p class="sub">${n ? `${n.toLocaleString()} more match${n === 1 ? "es" : ""}${n > list.length ? `, showing ${list.length}: narrow the search` : ""}.` : "No other US course matches."} Courses mapped hole by hole on OpenStreetMap build best.</p>
      <div class="libgrid">${cards}</div></section>`;
  }
  let busy = false;
  function decorate(fromObserver) {
    const app = document.getElementById("app");
    if (!app || app.dataset.screen !== "pick" || busy) return;
    const l0 = document.getElementById("list");
    if (fromObserver && l0 && l0.dataset.nat === "1") return;   /* our own insertion, not a new render */
    busy = true;
    try {
      const list = document.getElementById("list");
      if (!list) return;
      list.dataset.nat = "1";
      if (!rows && !failed) load();
      const q = (document.getElementById("q") || {}).value || "", stv = (document.getElementById("fState") || {}).value || "all";
      let sec = document.getElementById("natidx");
      const html = section(q, stv);
      if (sec) sec.outerHTML = html || "";
      else if (html) list.insertAdjacentHTML("afterend", html);
      /* library cards with no page yet */
      const L = typeof D !== "undefined" ? D.library.entries : [];
      for (const card of list.querySelectorAll('.lcard[data-status="none"]')) {
        const e = L[+card.dataset.lib];
        if (!e) continue;
        let box = card.querySelector(".nreq");
        if (!box) { box = document.createElement("div"); box.className = "acts nreq"; card.appendChild(box); }
        const m = byKey(e.state, e.name) || {name: e.name, city: e.town, state: e.state, holes: e.holes, osm: "", lat: NaN, lon: NaN};
        box.innerHTML = reqButton(m, "L" + card.dataset.lib);
      }
    } finally { busy = false; }
  }
  function refresh(o) { if (typeof document === "undefined") return; try { decorate(o); } catch (e) { if (typeof console !== "undefined") console.warn(e); } }
  if (typeof document !== "undefined") {
    const start = () => {
      const app = document.getElementById("app");
      if (!app) return;
      new MutationObserver(() => { if (!busy) refresh(true); }).observe(app, {childList: true});
      app.addEventListener("click", ev => {
        const b = ev.target.closest && ev.target.closest("button[data-nreq-i]");
        if (!b) return;
        ev.stopPropagation();
        const i = b.dataset.nreqI;
        let c;
        if (i[0] === "L") { const e = D.library.entries[+i.slice(1)]; c = e && (byKey(e.state, e.name) || {name: e.name, city: e.town, state: e.state, holes: e.holes}); }
        else c = shown[+i];
        if (!c) return;
        b.disabled = true; b.textContent = "Requesting…";
        request(c);
      }, true);
      refresh();
    };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else setTimeout(start, 0);
  }
  const api = {load, search, slugOf, norm, parse, request, section, state: R, get rows() { return rows; }};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.CourseIndex = api;
})(typeof window !== "undefined" ? window : this);
