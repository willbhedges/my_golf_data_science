/* ------------------------------------------------------------------ library courses: play (golf_lib_play/1)
   Every built library page (course_data/library/<slug>/page.html) has a compact play record, published next to this
   page as lib/<slug>.json (build_library_play.py) and fetched by relative URL when a golfer opens the course:
   holes, the solved tee sets, greens and par-3 target boxes, the calm-day pick and aim per set, and a wind table per
   hole (pick, aim, landing distance and drift at 0 / 10 / 20 mph from 8 directions relative to the tee line).
   The page interpolates the table for the hole's forecast wind (or a custom one), draws the aim on a small aerial
   picture, shows the hole's PASS / CHECK result, and asks "Is this hole N?": the answer is saved geo-anchored
   (a locate / reject of the hole's tee and green, golf_shared/1) in the shared map doc maps/<slug>, so every golfer
   after sees which holes golfers confirmed. Reports use the shared reports collection, like the app courses. */
const LIBD = {}, LIBERR = {};
const libEntry = slug => LIB.find(e => e.lib && e.id === slug) || null;
function libLoad(slug){
  const e = libEntry(slug); if (!e) return null;
  if (LIBD[slug] || LIBERR[slug]) return LIBD[slug] || null;          /* loaded, loading, or failed (retry clears it) */
  LIBERR[slug] = "loading";
  const inl = window.AIM_LIB_INLINE && window.AIM_LIB_INLINE[slug];
  (inl ? Promise.resolve(inl) : fetch(e.lib).then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); }))
    .then(d => { if (!d || d.schema !== "golf_lib_play/1" || !Array.isArray(d.holes)) throw new Error("not a course record");
      LIBD[slug] = d; delete LIBERR[slug]; LSTAT = null; softRender(); },
      err => { LIBERR[slug] = String(err && err.message || err); softRender(); });
  return null;
}
function LP(){ if (!st.lp || typeof st.lp !== "object") st.lp = {slug: null};
  for (const k of ["set", "idx", "src", "hour", "mine"]) if (!st.lp[k] || typeof st.lp[k] !== "object") st.lp[k] = {};
  if (!st.lp.custom) st.lp.custom = {from: 180, mph: 10, temp: 65};
  return st.lp; }
function lpSet(L){ const s = LP().set[L.id]; return L.sets.some(x => x.name === s) ? s : L.sets[0].name; }
function lpIdx(L){ const lp = LP();
  if (lp.want && lp.want.slug === L.id) { const k = L.holes.findIndex(H => H.no === lp.want.h); if (k >= 0) lp.idx[L.id] = k; delete lp.want; }
  const i = lp.idx[L.id] || 0; return i < L.holes.length ? i : 0; }
/* the hole's set record: the chosen set, else the first solved set that has this hole */
function lpV(L, H){ const s = lpSet(L); return H.sets[s] ? [s, H.sets[s]] : Object.entries(H.sets)[0]; }
function lpSrc(L){ const s = LP().src[L.id]; return s === "custom" || !L.days.length ? "custom" : (L.days.some(d => d.key === s) ? s : L.days[0].key); }
const lpHour = L => LP().hour[L.id] ?? L.tee_hour ?? 9;
function lpWind(L, H){
  const src = lpSrc(L);
  if (src === "custom") { const c = LP().custom; return {from: c.from, mph: c.mph, temp: c.temp, custom: true}; }
  const di = L.days.findIndex(d => d.key === src), t = lpHour(L) + (H.no - 1) * 14 / 60, h0 = Math.floor(t), w = t - h0;
  const row = h => L.hourly.find(r => r[0] === di && r[1] === h);
  const a = row(h0) || row(Math.max(...L.hourly.filter(r => r[0] === di).map(r => r[1]))), b = row(h0 + 1) || a;
  if (!a) return {from: 180, mph: 0, temp: 65, t};
  const vec = r => { const d = r[3] * Math.PI / 180; return [r[2] * Math.sin(d), r[2] * Math.cos(d)]; };
  const [ax, ay] = vec(a), [bx, by] = vec(b), x = ax + (bx - ax) * w, y = ay + (by - ay) * w;
  return {mph: Math.hypot(x, y), from: (Math.atan2(x, y) * 180 / Math.PI + 360) % 360, temp: a[4] + (b[4] - a[4]) * w, t};
}
/* bilinear over (0 / 10 / 20 mph) x (8 directions, 45 deg): table index of (speed i, direction j) */
function lpCorners(L, W, V){
  const rel = ((W.from - V.bearing) % 360 + 360) % 360, mph = Math.max(0, Math.min(W.mph, 20));
  const si = mph >= 10 ? 1 : 0, ws = (mph - si * 10) / 10, d0 = Math.floor(rel / 45) % 8, d1 = (d0 + 1) % 8, wd = (rel - d0 * 45) / 45;
  const ix = (s, d) => s === 0 ? 0 : 1 + (s - 1) * 8 + d;
  return {rel, mph, cs: [[ix(si, d0), (1 - ws) * (1 - wd)], [ix(si, d1), (1 - ws) * wd], [ix(si + 1, d0), ws * (1 - wd)], [ix(si + 1, d1), ws * wd]]};
}
function lpSolve(L, H, W){
  const [setName, V] = lpV(L, H), k = lpCorners(L, W, V);
  if (V.kind === "tee") {
    const wt = {}; for (const [i, w] of k.cs) { const c = V.wind[i][0]; wt[c] = (wt[c] || 0) + w; }
    const pc = +Object.keys(wt).sort((a, b) => wt[b] - wt[a])[0];
    let aim = 0, tot = 0, dr = 0, ww = 0;
    for (const [i, w] of k.cs) { const e = V.wind[i]; if (e[0] !== pc || w <= 0) continue; aim += w * e[1]; tot += w * e[2]; dr += w * e[3]; ww += w; }
    if (!ww) { const e = V.wind[k.cs[0][0]]; aim = e[1]; tot = e[2]; dr = e[3]; ww = 1; }
    return {setName, V, rel: k.rel, kind: "tee", club: L.clubs[pc], aim: aim / ww, total: tot / ww, drift: dr / ww, split: wt[pc] < 0.75};
  }
  let plays = 0; for (const [i, w] of k.cs) plays += w * V.plays[i];
  const box = V.boxes[String(windMod(W.mph))] || V.boxes["0"];
  return {setName, V, rel: k.rel, kind: "par3", plays, box, play: box.play * plays / V.center};
}
const lpShort = c => SHORT[c] || (/hybrid/i.test(c) ? "Hy" : c.split(" ")[0]);
/* golfers' answers for the course: per hole ref, the last answer anyone gave (others oldest first, then mine) */
function lpMine(slug){ const m = LP().mine[slug]; if (Array.isArray(m)) return m;
  const doc = STORE.map(slug), e = doc && doc.logs[STORE.gid]; return (LP().mine[slug] = e ? e.log.slice() : []); }
function lpAnswers(slug){
  const doc = STORE.map(slug), log = SharedStore.replayLog(doc, STORE.gid, lpMine(slug)), out = {};
  for (const a of log) out[a.ref] = a.kind === "locate" ? "yes" : "no";
  return {by: out, golfers: SharedStore.golferCount(doc, STORE.gid, lpMine(slug).length), n: log.length};
}
function lpAnswer(L, H, yes){
  const [, V] = lpV(L, H);
  if (!H.green_ll && !V.tee_ll) return;
  const a = SharedStore.cleanAction({kind: yes ? "locate" : "reject", ref: String(H.no), answer: {tee_ll: V.tee_ll || null, green_ll: H.green_ll || null}, taps: 1});
  if (!a) return;
  const m = lpMine(L.id); m.push(a); if (m.length > 100) m.splice(0, m.length - 100);
  SYNC[L.id] = "saving"; LSTAT = null; save();
  STORE.saveLog(L.id, m, {taps: m.length}).then(r => { SYNC[L.id] = r; softRender(); });
}
/* the library card's live status for a course with a play record: confirm until every CHECK hole has a "yes" */
function lpStatus(e){
  const ans = lpAnswers(e.id), chk = e.checks || [], yes = chk.filter(h => ans.by[String(h)] === "yes").length;
  const k = e.status === "auto" ? "auto" : chk.length && yes >= chk.length ? "auto" : e.status === "none" ? "none" : "confirm";
  return {k, fixed: Object.values(ans.by).filter(v => v === "yes").length, golfers: ans.golfers, n: e.holes || 18, lib: true};
}
function lpDraw(L, H, r, W){
  const V = r.V, img = L.images[V.img], P = (a, l) => [V.tee[0] + (a * V.f[0] + l * V.r[0]) * V.ppy, V.tee[1] + (a * V.f[1] + l * V.r[1]) * V.ppy];
  const f1 = p => p[0].toFixed(1) + "," + p[1].toFixed(1);
  let g = `<image href="${img}" x="0" y="0" width="${V.w}" height="${V.h}"/>`, vb = [0, 0, V.w, V.h];
  if (r.kind === "tee") {
    const tee = P(0, 0), aim = P(r.total, r.aim), land = P(r.total, r.aim + r.drift), sw = V.w / 300;
    const ell = []; for (let k = 0; k < 36; k++) { const a = k / 36 * 2 * Math.PI; ell.push(f1(P(r.total + Math.sin(a) * 14, r.aim + r.drift + Math.cos(a) * 30))); }
    g += `<polygon points="${ell.join(" ")}" fill="rgba(255,201,40,.16)" stroke="#ffc928" stroke-width="${1.4 * sw}" stroke-dasharray="4 3"/>`
      + `<line x1="${tee[0]}" y1="${tee[1]}" x2="${aim[0]}" y2="${aim[1]}" stroke="#fff" stroke-width="${1.6 * sw}"/>`
      + (Math.abs(r.drift) > 2 ? `<line x1="${aim[0]}" y1="${aim[1]}" x2="${land[0]}" y2="${land[1]}" stroke="#fff" stroke-width="${1.4 * sw}" stroke-dasharray="3 3"/>` : "")
      + `<g stroke="#ff3b30" stroke-width="${2 * sw}" fill="none"><circle cx="${aim[0]}" cy="${aim[1]}" r="${6 * sw}"/><line x1="${aim[0] - 11 * sw}" y1="${aim[1]}" x2="${aim[0] + 11 * sw}" y2="${aim[1]}"/><line x1="${aim[0]}" y1="${aim[1] - 11 * sw}" x2="${aim[0]}" y2="${aim[1] + 11 * sw}"/></g>`
      + `<circle cx="${tee[0]}" cy="${tee[1]}" r="${5 * sw}" fill="${esc(lpColour(L, r.setName))}" stroke="#000" stroke-width="${1.2 * sw}"/>`;
  } else {
    g += `<polygon points="${V.green.map(f1).join(" ")}" fill="none" stroke="#7CFC00" stroke-width="1.2"/>`
      + `<polygon points="${r.box.poly.map(f1).join(" ")}" fill="rgba(255,59,48,.25)" stroke="#ff3b30" stroke-width="1.6"/>`;
  }
  return `<div class="mapbox"><svg id="ov" viewBox="${vb.join(" ")}" style="max-height:72vh" role="img" aria-label="Aerial view of hole ${H.no} with the aim drawn on it">${g}</svg></div>`;
}
const lpColour = (L, s) => (L.sets.find(x => x.name === s) || {}).colour || "#888";
function renderLib(){
  const slug = LP().slug, e = libEntry(slug);
  const top = t => `<div class="topbar"><button class="btn ghost" data-go="pick" aria-label="All courses">‹ Courses</button><div class="ttl"><b>${esc(e ? e.name : slug)}</b>${t || ""}</div><span></span></div>`;
  if (!e) return top() + `<p class="sub">This course is not in the library.</p>`;
  const L = LIBD[slug] || libLoad(slug);
  if (!L) return top() + (LIBERR[slug] && LIBERR[slug] !== "loading"
    ? `<section class="panel stack" id="libErr"><b>Could not load this course's data</b><p class="sub">${esc(LIBERR[slug])}: the page fetches ${esc(e.lib)} from where it is published.</p><div class="row"><button class="btn" data-lpretry="1">Try again</button></div></section>`
    : `<section class="panel" id="libLoading"><p class="sub">Loading ${esc(e.name)}…</p></section>`);
  const i = lpIdx(L), H = L.holes[i], W = lpWind(L, H), r = lpSolve(L, H, W), V = r.V, src = lpSrc(L), ans = lpAnswers(slug), a = ans.by[String(H.no)];
  const qa = V.qa || ["", []], chk = (L.check_holes || []).includes(H.no) || qa[0] === "CHECK";
  const play = r.kind === "tee"
    ? `<div class="spread"><span class="label">Tee shot</span><span class="sub">${r.split ? "close call in this wind" : ""}</span></div><div class="playrow" id="lpPlay"><span class="play ${cls(r.club)}">${esc(r.club)}</span><span class="sub" style="padding-bottom:5px">aim ${yds(r.aim)}</span></div><div class="sub">Finishes about ${Math.round(r.total)} yds out${Math.abs(r.drift) > 2 ? `, the wind moves it ${Math.abs(r.drift).toFixed(0)} yds ${r.drift < 0 ? "left" : "right"}` : ""}${V.green_al ? ` · ${Math.round(Math.hypot(V.green_al[0] - r.total, V.green_al[1] - r.aim - r.drift))} yds left to the green` : ""}. Calm day: ${esc(V.calm.pick || "")}${V.calm.aim != null ? `, aim ${yds(V.calm.aim)}` : ""}.</div>`
    : `<div class="spread"><span class="label">Par 3</span></div><div class="playrow" id="lpPlay"><span class="play">${Math.round(r.play)} yds</span><span class="sub" style="padding-bottom:5px">plays like</span></div><div class="sub">Card ${V.yds} yds to the centre (${V.center}); target box ${r.box.lo}–${r.box.hi} yds. ${esc(V.short || "")}</div>`;
  const conf = `<section class="conf ${chk ? "check" : "auto"}" id="lpQa"><div class="row">${chk ? badge("check") : `<span class="badge auto">PASS</span>`}<b>${chk ? "Auto-map CHECK: look before you trust this hole" : "Passed the picture checks"}</b></div>
      ${qa[1].length ? qa[1].map(x => `<div class="sub">${esc(x)}</div>`).join("") : ""}
      <div class="row" id="lpConfirm"><span>Is this hole ${H.no} as drawn (tee and green)?</span><button class="btn${a === "yes" ? " primary" : ""}" data-lpyes="1" aria-pressed="${a === "yes"}">Yes, that's it</button><button class="btn${a === "no" ? " primary" : ""}" data-lpno="1" aria-pressed="${a === "no"}">No, it's wrong</button></div>
      <div class="sub" id="lpAns">${a === "yes" ? "✓ Golfers confirmed this hole." : a === "no" ? "Golfers say this hole is drawn wrong: treat the aim with care." : "Not confirmed yet."} ${ans.n ? `${ans.n} answer${ans.n === 1 ? "" : "s"} from ${ans.golfers} golfer${ans.golfers === 1 ? "" : "s"} on this course.` : ""}</div>
      ${syncLine({id: slug}, null)}</section>`;
  const relTxt = relWords(r.rel, W.mph);
  const cond = W.custom ? `Your wind: <b>${Math.round(W.mph)} mph</b> from the ${compass(W.from)}` : `At about <b>${clock(W.t)}</b> · <b>${Math.round(W.mph)} mph</b> from the ${compass(W.from)} · ${Math.round(W.temp)}°F`;
  const strip = L.holes.map((Hh, k) => { const rr = lpSolve(L, Hh, lpWind(L, Hh)), c = (L.check_holes || []).includes(Hh.no) || (rr.V.qa || [])[0] === "CHECK";
    return `<button class="chip" data-lpi="${k}" aria-current="${k === i}" aria-label="Hole ${Hh.no}">${c ? "<i>⚠</i>" : ""}<b>${Hh.no}</b><span class="${rr.kind === "tee" ? cls(rr.club) : ""}">${rr.kind === "tee" ? esc(lpShort(rr.club)) : Math.round(rr.play)}</span></button>`; }).join("");
  const FC = {id: slug, confirm: null};
  return `<div class="hhead" id="hhead">${top(`<span class="sub">${esc(r.setName)} tees · library course</span>`)}
    <div class="holehead"><button class="navbtn" id="lprev" data-lpnav="-1" aria-label="Previous hole">‹</button>
      <div style="text-align:center;min-width:0"><div class="holeno">Hole ${H.no}</div><div class="sub">Par ${H.par} · ${V.yds} yds</div>
      <div class="row" style="justify-content:center;margin-top:4px">${chk ? badge("check") : `<span class="badge auto">PASS</span>`}${STORE.reports(slug).some(x => x.hole === H.no) ? `<span class="badge check">reported</span>` : ""}</div></div>
      <button class="navbtn" id="lnext" data-lpnav="1" aria-label="Next hole">›</button></div></div>
    <div class="seg" id="lpSets" role="group" aria-label="Tee set">${L.sets.map(s => `<button data-lpset="${esc(s.name)}" aria-pressed="${s.name === r.setName}">${esc(s.name)}${s.total ? " " + Number(s.total).toLocaleString() : ""}</button>`).join("")}</div>
    ${lpDraw(L, H, r, W)}
    <section class="panel stack">${play}<div class="cond"><span>${cond}</span><span class="windico">${windIcon(r.rel, W.mph)}${esc(relTxt)}</span></div>
      ${W.mph > 20 ? `<p class="sub">Picks use the 20 mph table: stronger wind plays even more so.</p>` : ""}</section>
    ${conf}
    ${reportBox(FC, {no: H.no}, null)}
    <section class="panel stack"><div class="label">Wind &amp; tee time</div>
      <div class="seg" id="lpSrc">${L.days.map(d => `<button data-lpsrc="${esc(d.key)}" aria-pressed="${src === d.key}">${esc(d.label)}</button>`).join("")}<button data-lpsrc="custom" aria-pressed="${src === "custom"}">Custom</button></div>
      ${src === "custom" ? `<div class="row"><span class="label">From</span><input type="range" id="lpFrom" min="0" max="355" step="5" value="${Math.round(W.from)}" aria-label="Wind from (degrees)"><span class="windread">${compass(W.from)}</span></div>
        <div class="row"><span class="label">Speed</span><input type="range" id="lpMph" min="0" max="25" step="1" value="${Math.round(W.mph)}" aria-label="Wind speed"><span class="windread">${Math.round(W.mph)} mph</span></div>`
      : `<div class="row"><span class="label">Tee time</span><input type="range" id="lpHour" min="7" max="16" step="0.25" value="${lpHour(L)}" aria-label="Tee time"><span class="windread">${clock(lpHour(L))}</span></div>`}
      ${L.placeholder ? `<p class="sub">Climate normals for the event days, not a forecast.</p>` : `<p class="sub">${esc(L.fc_note || "")}</p>`}</section>
    <section class="panel stack"><div class="label">All holes</div><div class="strip" id="lpStrip">${strip}</div><p class="sub">Club per tee shot, “plays like” yards on par 3s; ⚠ = CHECK hole.</p></section>
    ${V.note ? `<section class="panel"><p class="note">${esc(V.note)}</p></section>` : ""}
    <p class="foot">Automatic library page${L.built ? ` built ${esc(L.built.slice(0, 10))}` : ""}. Picks and aims from its wind grids at ${L.temps ? Math.round(L.temps[1]) : 65}°F (0 / 10 / 20 mph from 8 directions, interpolated); calm-day picks from its Bayesian run. Imagery ${esc(L.imagery || "")}. ${esc(L.foot || "")}</p>`;
}
function lpClick(b){
  const d = b.dataset, slug = LP().slug, L = LIBD[slug];
  if (d.lpretry) { delete LIBERR[slug]; return true; }
  if (!L) return false;
  const lp = LP(), H = L.holes[lpIdx(L)];
  if (d.lpnav) { lp.idx[slug] = (lpIdx(L) + (+d.lpnav) + L.holes.length) % L.holes.length; st.report = null; return true; }
  if (d.lpi !== undefined) { lp.idx[slug] = +d.lpi; st.report = null; return true; }
  if (d.lpset) { lp.set[slug] = d.lpset; return true; }
  if (d.lpsrc) { if (d.lpsrc === "custom") { const W = lpWind(L, H); lp.custom = {from: Math.round(W.from / 5) * 5 % 360, mph: Math.round(W.mph), temp: Math.round(W.temp || 65)}; } lp.src[slug] = d.lpsrc; return true; }
  if (d.lpyes || d.lpno) { lpAnswer(L, H, !!d.lpyes); return true; }
  const FC = {id: slug}, k = slug + "|" + H.no;
  if (d.rkind) { st.rdraft = ($("rText") || {}).value || st.rdraft || ""; st.rkind = d.rkind; return true; }
  if (d.report === "open") { st.report = k; st.rmsg = null; return true; }
  if (d.report === "cancel") { st.report = null; st.rdraft = ""; return true; }
  if (d.report === "send") { const text = (($("rText") || {}).value || "").trim().slice(0, 500);
    st.report = null; st.rdraft = ""; st.rmsg = {k, t: "Sending…"};
    STORE.addReport({course: FC.id, hole: H.no, kind: st.rkind, text, tee: lpSet(L)}).then(r => {
      st.rmsg = {k, t: r === "shared" ? "Thanks: reported for everyone. The hole is flagged for a re-check." : "Thanks: saved on this device (shared storage isn't available here)."}; softRender(); },
      () => { st.rmsg = {k, t: "Could not save the report."}; softRender(); });
    return true; }
  return false;
}
function lpInput(t){
  const slug = LP().slug, L = LIBD[slug]; if (!L) return false; const lp = LP();
  if (t.id === "lpHour") { lp.hour[slug] = +t.value; return true; }
  if (t.id === "lpFrom") { lp.custom.from = +t.value; return true; }
  if (t.id === "lpMph") { lp.custom.mph = +t.value; return true; }
  return false;
}
