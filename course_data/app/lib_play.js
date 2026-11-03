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
  for (const k of ["set", "idx", "src", "hour", "mine", "replan", "h1skip"]) if (!st.lp[k] || typeof st.lp[k] !== "object") st.lp[k] = {};
  if (!st.lp.custom) st.lp.custom = {from: 180, mph: 10, temp: 65};
  return st.lp; }
function lpSet(L){ const s = LP().set[L.id]; return L.sets.some(x => x.name === s) ? s : L.sets[0].name; }
/* golfer-facing set names (the page's D.set_labels / D.tee_labels, e.g. "Back tees (from the map)" for a no-card
   page's "osm_back" set); the set name stays the key for lookups, answers and the stored pick */
const lpSetObj = (L, s) => L.sets.find(x => x.name === s) || {name: s};
const lpTeesLabel = (L, s) => { const o = lpSetObj(L, s); return o.tee_label ? o.tee_label + " tees" : o.label || s + " tees"; };
function lpIdx(L){ const lp = LP(), LS = lpList(L);
  if (lp.want && lp.want.slug === L.id) { const k = LS.findIndex(H => H.no === lp.want.h); if (k >= 0) lp.idx[L.id] = k; delete lp.want; }
  const i = lp.idx[L.id] || 0; return i < LS.length ? i : 0; }
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
/* golfer check cards of a library course (native grass along the landing area: build_library_play.native_cards);
   answers live in st.answers["lib:<slug>"] on this device, like an app course's pre-round check */
const lpAK = L => "lib:" + L.id;
function lpCards(L, H){ return (L.checks || []).filter(c => String(c.hole) === String(H.ref)); }
/* the answered card whose outcome re-plans this hole on this set: {card, o} or null */
function lpNat(L, H, setName){
  const A = st.answers[lpAK(L)] || {};
  for (const card of lpCards(L, H)) { const a = A[card.id]; if (!a || card.tee_set !== setName) continue;
    const o = card.options.find(x => x.answer === a); if (o) return {card, o}; }
  return null;
}
function lpSolve(L, H, W){
  const [setName, V] = lpV(L, H), k = lpCorners(L, W, V);
  if (V.kind === "tee") {
    const nat = lpNat(L, H, setName), tab = nat && nat.o.outcome && nat.o.outcome.wind || V.wind;
    const wt = {}; for (const [i, w] of k.cs) { const c = tab[i][0]; wt[c] = (wt[c] || 0) + w; }
    const pc = +Object.keys(wt).sort((a, b) => wt[b] - wt[a])[0];
    let aim = 0, tot = 0, dr = 0, ww = 0;
    for (const [i, w] of k.cs) { const e = tab[i]; if (e[0] !== pc || w <= 0) continue; aim += w * e[1]; tot += w * e[2]; dr += w * e[3]; ww += w; }
    if (!ww) { const e = tab[k.cs[0][0]]; aim = e[1]; tot = e[2]; dr = e[3]; ww = 1; }
    return {setName, V, rel: k.rel, kind: "tee", club: L.clubs[pc], aim: aim / ww, total: tot / ww, drift: dr / ww, split: wt[pc] < 0.75,
            nat, replanned: !!(nat && nat.o.outcome && nat.o.outcome.wind)};
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
  for (const a of log) if (a.kind !== "first") out[a.ref] = a.kind === "locate" ? "yes" : "no";
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
  const L = LIBD[e.id], RT = L && L.route ? lpRoute(L) : null;
  if (RT) return {k: RT.low.length ? "confirm" : "auto", fixed: RT.view.filter(v => v.fixed).length, golfers: lpAnswers(e.id).golfers, n: RT.view.length, lib: true};
  const ans = lpAnswers(e.id), chk = e.checks || [], yes = chk.filter(h => ans.by[String(h)] === "yes").length;
  const k = e.status === "auto" ? "auto" : chk.length && yes >= chk.length ? "auto" : e.status === "none" ? "none" : "confirm";
  return {k, fixed: Object.values(ans.by).filter(v => v === "yes").length, golfers: ans.golfers, n: e.holes || 18, lib: true};
}
/* the tee shot's landing pattern, [along, lateral] yds: the club's tee-frame pattern on this set when the record has it
   (V.pat[club index] = [dA, dL, long, short, left, right, tilt]: course_data/library/landing_pattern.py, centre relative
   to the landing point the page computes), else a generic 60 x 28 yd oval at the landing point */
const LP_FALLBACK = [0, 0, 14, 14, 30, 30, 0];
function lpPattern(V, ci, r, n = 48){
  const q = (V.pat && V.pat[ci]) || LP_FALLBACK, al = r.total + q[0], lat = r.aim + r.drift + q[1], out = [];
  for (let k = 0; k < n; k++) { const a = k / n * 2 * Math.PI, c = Math.cos(a), s = Math.sin(a), x = s * (s >= 0 ? q[5] : q[4]);
    out.push([al + c * (c >= 0 ? q[2] : q[3]) + q[6] * x, lat + x]); }
  return out;
}
function lpDraw(L, H, r, W){
  const V = r.V, img = L.images[V.img], P = (a, l) => [V.tee[0] + (a * V.f[0] + l * V.r[0]) * V.ppy, V.tee[1] + (a * V.f[1] + l * V.r[1]) * V.ppy];
  const f1 = p => p[0].toFixed(1) + "," + p[1].toFixed(1);
  let g = `<image href="${img}" x="0" y="0" width="${V.w}" height="${V.h}"/>`, vb = [0, 0, V.w, V.h];
  if (r.kind === "tee" && r.nat && r.nat.card.band) {         /* the native the answer says is there, as the plan assumed it */
    const a = r.nat.o.answer, sides = a === "both" ? ["L", "R"] : a === "L" || a === "R" ? [a] : [];
    for (const sd of sides) for (const poly of r.nat.card.band[sd] || [])
      g += `<polygon data-native="${sd}" points="${poly.map(([al, l]) => f1(P(al, l))).join(" ")}" fill="rgba(255,210,63,.24)" stroke="rgba(255,210,63,.8)" stroke-width="${V.w / 300}"/>`;
  }
  if (r.kind === "tee") {
    const tee = P(0, 0), aim = P(r.total, r.aim), land = P(r.total, r.aim + r.drift), sw = V.w / 300;
    const ell = lpPattern(V, L.clubs.indexOf(r.club), r).map(([al, l]) => f1(P(al, l)));
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
  const RT = lpRoute(L), LS = lpList(L), i = lpIdx(L), lv = LS[i];
  if (RT && !lv.plan) return lpPending(L, RT, i, lv);
  const H = lv.plan.no === lv.no ? lv.plan : Object.assign({}, lv.plan, {no: lv.no}), PN = lv.plan.no;   /* PN: the plan's own number */
  const W = lpWind(L, H), r = lpSolve(L, H, W), V = r.V, src = lpSrc(L), ans = lpAnswers(slug), a = ans.by[String(H.no)];
  const qa = V.qa || ["", []], chk = (L.check_holes || []).includes(PN) || qa[0] === "CHECK";
  const play = r.kind === "tee"
    ? `<div class="spread"><span class="label">Tee shot</span><span class="sub">${r.split ? "close call in this wind" : ""}</span></div><div class="playrow" id="lpPlay"><span class="play ${cls(r.club)}">${esc(r.club)}</span><span class="sub" style="padding-bottom:5px">aim ${yds(r.aim)}</span></div><div class="sub">Finishes about ${Math.round(r.total)} yds out${Math.abs(r.drift) > 2 ? `, the wind moves it ${Math.abs(r.drift).toFixed(0)} yds ${r.drift < 0 ? "left" : "right"}` : ""}${V.green_al ? ` · ${Math.round(Math.hypot(V.green_al[0] - r.total, V.green_al[1] - r.aim - r.drift))} yds left to the green` : ""}. Calm day: ${esc(V.calm.pick || "")}${V.calm.aim != null ? `, aim ${yds(V.calm.aim)}` : ""}.</div>${r.replanned ? `<div class="sub" id="lpReplan"><b>Re-planned from your answer</b> (native grass: ${esc(r.nat.o.label)}): calm day ${esc(r.nat.o.outcome.pick)}, aim ${yds(r.nat.o.outcome.aim)}.</div>` : ""}`
    : `<div class="spread"><span class="label">Par 3</span></div><div class="playrow" id="lpPlay"><span class="play">${Math.round(r.play)} yds</span><span class="sub" style="padding-bottom:5px">plays like</span></div><div class="sub">Card ${V.yds} yds to the centre (${V.center}); target box ${r.box.lo}–${r.box.hi} yds. ${esc(V.short || "")}</div>`;
  const conf = RT ? `<section class="conf ${chk ? "check" : "auto"}" id="lpQa"><div class="row">${chk ? badge("check") : `<span class="badge auto">PASS</span>`}<b>${chk ? "Auto-map CHECK: look before you trust this hole" : "Passed the picture checks"}</b></div>${qa[1].length ? qa[1].map(x => `<div class="sub">${esc(x)}</div>`).join("") : ""}</section>${lpRouteBox(L, RT, lv)}`
    : `<section class="conf ${chk ? "check" : "auto"}" id="lpQa"><div class="row">${chk ? badge("check") : `<span class="badge auto">PASS</span>`}<b>${chk ? "Auto-map CHECK: look before you trust this hole" : "Passed the picture checks"}</b></div>
      ${qa[1].length ? qa[1].map(x => `<div class="sub">${esc(x)}</div>`).join("") : ""}
      <div class="row" id="lpConfirm"><span>Is this hole ${H.no} as drawn (tee and green)?</span><button class="btn${a === "yes" ? " primary" : ""}" data-lpyes="1" aria-pressed="${a === "yes"}">Yes, that's it</button><button class="btn${a === "no" ? " primary" : ""}" data-lpno="1" aria-pressed="${a === "no"}">No, it's wrong</button></div>
      <div class="sub" id="lpAns">${a === "yes" ? "✓ Golfers confirmed this hole." : a === "no" ? "Golfers say this hole is drawn wrong: treat the aim with care." : "Not confirmed yet."} ${ans.n ? `${ans.n} answer${ans.n === 1 ? "" : "s"} from ${ans.golfers} golfer${ans.golfers === 1 ? "" : "s"} on this course.` : ""}</div>
      ${syncLine({id: slug}, null)}</section>`;
  const relTxt = relWords(r.rel, W.mph);
  const cond = W.custom ? `Your wind: <b>${Math.round(W.mph)} mph</b> from the ${compass(W.from)}` : `At about <b>${clock(W.t)}</b> · <b>${Math.round(W.mph)} mph</b> from the ${compass(W.from)} · ${Math.round(W.temp)}°F`;
  const strip = RT ? lpStripRoute(L, RT, i) : L.holes.map((Hh, k) => { const rr = lpSolve(L, Hh, lpWind(L, Hh)), c = (L.check_holes || []).includes(Hh.no) || (rr.V.qa || [])[0] === "CHECK";
    return `<button class="chip" data-lpi="${k}" aria-current="${k === i}" aria-label="Hole ${Hh.no}">${c ? "<i>⚠</i>" : ""}<b>${Hh.no}</b><span class="${rr.kind === "tee" ? cls(rr.club) : ""}">${rr.kind === "tee" ? esc(lpShort(rr.club)) : Math.round(rr.play)}</span></button>`; }).join("");
  const FC = {id: slug, confirm: null};
  return `<div class="hhead" id="hhead">${top(`<span class="sub">${esc(lpTeesLabel(L, r.setName))} · library course</span>`)}
    <div class="holehead"><button class="navbtn" id="lprev" data-lpnav="-1" aria-label="Previous hole">‹</button>
      <div style="text-align:center;min-width:0"><div class="holeno">Hole ${H.no}</div><div class="sub">Par ${H.par} · ${V.yds} yds</div>
      <div class="row" style="justify-content:center;margin-top:4px">${chk ? badge("check") : `<span class="badge auto">PASS</span>`}${STORE.reports(slug).some(x => x.hole === H.no) ? `<span class="badge check">reported</span>` : ""}</div></div>
      <button class="navbtn" id="lnext" data-lpnav="1" aria-label="Next hole">›</button></div></div>
    <div class="seg" id="lpSets" role="group" aria-label="Tee set">${L.sets.map(s => `<button data-lpset="${esc(s.name)}" aria-pressed="${s.name === r.setName}">${esc(s.label || s.name)}${s.total ? " " + Number(s.total).toLocaleString() : ""}</button>`).join("")}</div>
    ${reviewBanner(L.review)}${L.review && L.review.holes && L.review.holes[String(PN)] ? `<div class="review bad" id="lpHoleReview">Reviewer, hole ${PN}: ${esc(L.review.holes[String(PN)][0])}${L.review.holes[String(PN)][1] ? ` — ${esc(L.review.holes[String(PN)][1])}` : ""}</div>` : ""}
    ${lpDraw(L, H, r, W)}
    <section class="panel stack">${play}<div class="cond"><span>${cond}</span><span class="windico">${windIcon(r.rel, W.mph)}${esc(relTxt)}</span></div>
      ${W.mph > 20 ? `<p class="sub">Picks use the 20 mph table: stronger wind plays even more so.</p>` : ""}</section>
    ${lpCards(L, lv.plan).length ? `<section class="stack" id="lpChecks">${lpCards(L, lv.plan).map(c => checkCard({id: lpAK(L)}, c, {img: false, set: r.setName})).join("")}</section>` : ""}
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
  if (L.route && lpRouteClick(L, d)) return true;
  const lp = LP(), LS = lpList(L), H = Object.assign({}, LS[lpIdx(L)].plan || {}, {no: LS[lpIdx(L)].no});
  if (d.lpnav) { lp.idx[slug] = (lpIdx(L) + (+d.lpnav) + LS.length) % LS.length; st.report = null; lp.rpick = null; lp.rask = null; return true; }
  if (d.lpi !== undefined) { lp.idx[slug] = +d.lpi; st.report = null; return true; }
  if (d.lpset) { lp.set[slug] = d.lpset; return true; }
  if (d.lpsrc) { if (d.lpsrc === "custom") { const W = lpWind(L, H); lp.custom = {from: Math.round(W.from / 5) * 5 % 360, mph: Math.round(W.mph), temp: Math.round(W.temp || 65)}; } lp.src[slug] = d.lpsrc; return true; }
  if (d.lpyes || d.lpno) { lpAnswer(L, H, !!d.lpyes); return true; }
  if (d.card && d.ans) { const A = st.answers[lpAK(L)] = st.answers[lpAK(L)] || {};
    if (A[d.card] === d.ans) delete A[d.card]; else A[d.card] = d.ans; save(); return true; }
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

/* ------------------------------------------------------------------ card-blind routing: confirm taps + re-solve
   A record with `route` (pathroute_decoder/1, pathroute_engine.js) was routed without hole ways: tee <-> green
   pairing and order come from pathroute v2 with a calibrated confidence per hole. The hole list is the decoded
   route; each decoded hole shows the precomputed plan whose tee and green it matches (green within 25 yds, a tee
   within 40 yds), else "plan pending" (geometry only; a golf_replan/1 request is recorded). Golfers' answers are the
   same geo-anchored actions as above (maps/<slug>): locate = "hole N is this tee + green", reject = "no" (or a
   practice green when only the green is set), first = "this tee is hole 1". The confirm-tap policy is the engine's
   (PathRoute.POLICY = resolve2.POLICY, zero_tap PATHROUTE.md "Fully right"): on a 9 / 18-hole course "Which tee is
   hole 1?" comes first (Session.needHole1, shown above the hole question until answered or "Not now"); every answer
   (yes / correction / "no" / not a hole / hole-1 tee) re-solves the whole route in the browser (the same decode as
   zero_tap/pathroute_v2; POLICY yes / not_hole "solve"); the holes to ask are Session.need(): lowest confidence first
   until P(every pair right) reaches the policy target. The answer log is replayed answer by answer into one Session (kept across answers: a new answer
   only applies itself). */
const LPR = {}, RT_SNAP = 25;
const llYd = (a, b) => { const kx = 111320 * Math.cos(a[1] * Math.PI / 180) / 0.9144; return Math.hypot((a[0] - b[0]) * kx, (a[1] - b[1]) * 110950 / 0.9144); };
function lpFactsFromIds(R, f){
  if (!f) return null;
  const ti = {}, gi = {}; R.tees.forEach((t, i) => { ti[t.id] = i; }); R.greens.forEach((g, i) => { gi[g.id] = i; });
  return {pairs: (f.pairs || []).filter(p => p[1] in ti && p[2] in gi).map(p => [p[0], ti[p[1]], gi[p[2]]]),
          not_green: (f.not_green || []).filter(g => g in gi).map(g => gi[g]), first_tee: f.first_tee in ti ? ti[f.first_tee] : null,
          reject: (f.reject || []).filter(p => p[0] in ti && p[1] in gi).map(p => [ti[p[0]], gi[p[1]]])};
}
/* one answer into the session (the engine's policy) -> true when the route must be re-solved */
function lpRouteApply(S, a, single){
  const t = a.answer.tee_ll ? S.nearest("tee", a.answer.tee_ll, RT_SNAP) : null, g = a.answer.green_ll ? S.nearest("green", a.answer.green_ll, RT_SNAP) : null;
  const num = single ? +a.ref : null, at = g == null ? -1 : S.holes.findIndex(h => h.g === g);
  if (a.kind === "first") { if (t == null) return false; S.holeOne(t); return true; }
  if (a.kind === "locate") {
    if (t == null || g == null) return false;
    if (at >= 0) return S.answer(at, t, num, false);
    S.confirmPair(num, t, g); return true;
  }
  if (g == null) return false;
  if (t != null) { S.rejectPair(t, g); return true; }
  if (at >= 0) return S.answer(at, null, null, true);
  S.notAHole(g); return true;
}
function lpRoute(L){
  if (!L.route || typeof PathRoute === "undefined") return null;
  const log = SharedStore.replayLog(STORE.map(L.id), STORE.gid, lpMine(L.id)), key = JSON.stringify(log);
  const c = LPR[L.id]; if (c && c.key === key) return c.none ? null : c;
  const single = L.route.kind === 9 || L.route.kind === 18, t0 = Date.now(), prev = c && !c.pending && !c.none ? c : null;
  /* the cached session when the log only grew (the usual case: this golfer's new answer), else a replay from scratch;
     a re-solving answer decodes the route at once (begin), the confidences are computed for the last decode only */
  const grow = c && !c.none && c.log.length <= log.length && JSON.stringify(log.slice(0, c.log.length)) === JSON.stringify(c.log);
  let S, todo;
  try {
    if (grow) { S = c.S; todo = log.slice(c.log.length); }
    else { S = new PathRoute.Session(L.route, lpFactsFromIds(L.route, L.route.facts)); S.begin(); todo = log; }
    for (const a of todo) if (lpRouteApply(S, a, single)) S.begin();
  } catch (e) { if (typeof console !== "undefined") console.warn(e); return null; }
  /* no round decodes from this map (e.g. OSM has fewer greens than holes): the course plays as the record's own holes
     with the plain "Is this hole N as drawn?" confirm instead of an empty routing view */
  if (!S.holes.length) { LPR[L.id] = {key, log, none: true}; return null; }
  const out = (LPR[L.id] = {key, log, S, pending: !!S.job, ms: 0, thr: L.route.conf_ok || 0.95, target: S.policy.target, n: log.length});
  lpRouteFill(L, out, prev);
  if (!out.pending) return out;
  /* the pairing shows at once; the confidences (one re-decode per hole) fill in over the next frames */
  const tick = () => {
    if (LPR[L.id] !== out) return;
    const t1 = Date.now();
    let done = false;
    try { while (!done && Date.now() - t1 < 40) done = S.step(); } catch (e) { done = true; if (typeof console !== "undefined") console.warn(e); }
    if (!done) return void setTimeout(tick, 0);
    out.pending = false; out.ms = Date.now() - t0;
    lpRouteFill(L, out, null);
    if (out.n && out.pend.length) {                /* golfers' answers re-paired holes the server never planned */
      const sig = JSON.stringify(out.pend.map(v => [v.no, v.h.t, v.h.g]));
      if (sig !== (LP().replan[L.id] || "")) { LP().replan[L.id] = sig; save();
        STORE.addReplan(L.id, out.pend.map(v => ({no: v.no, tee_ll: L.route.tees[v.h.t].ll, green_ll: L.route.greens[v.h.g].ll, yds: v.h.L})), S.toIds()); }
    }
    LSTAT = null; softRender();
  };
  setTimeout(tick, 0);
  return out;
}
/* the view of a (partly) solved session; while the confidences are pending, a hole keeps its previous confidence when
   its pair is unchanged, else it reads 0 ("checking") and is not asked yet */
function lpRouteFill(L, out, prev){
  const S = out.S, conf = S.conf, fp = S.fixedPairs(), pc = {};
  if (prev) prev.view.forEach(v => { pc[v.h.t + "," + v.h.g] = v.conf; });
  S.conf = conf || S.holes.map(h => fp.has(h.t + "," + h.g) ? 1 : (pc[h.t + "," + h.g] ?? 0));
  const need = new Set(S.need(out.target));
  out.pall = S.pAll();
  out.view = lpRouteView(L, S);
  if (!conf) { S.conf = null; out.view.forEach(v => { v.checking = !v.fixed && !((v.h.t + "," + v.h.g) in pc); }); }
  out.view.forEach(v => { v.ask = need.has(v.i) && !v.checking; });
  out.pend = out.view.filter(v => !v.plan);
  out.low = out.view.filter(v => v.ask);
}
function lpRouteView(L, S){
  const R = L.route, fp = S.fixedPairs();
  const out = S.holes.map((h, i) => ({i, no: S.holeRef(h), h, conf: S.conf[i], fixed: fp.has(h.t + "," + h.g), plan: null, par: S.par(h)}));
  const cand = [];
  out.forEach((v, vi) => {
    const G = R.greens[v.h.g].ll, Ts = [v.h.t].concat(v.h.boxes).map(t => R.tees[t].ll);
    L.holes.forEach((H, hi) => {
      if (!H.green_ll) return;
      const dg = llYd(G, H.green_ll); if (dg > 25) return;
      const tl = Object.values(H.sets).map(V => V.tee_ll).filter(Boolean);
      let dt = Infinity; for (const a of tl) for (const b of Ts) dt = Math.min(dt, llYd(a, b));
      if (dt <= 40) cand.push([dg + dt / 4, vi, hi]);
    });
  });
  cand.sort((a, b) => a[0] - b[0]);
  const uv = new Set(), uh = new Set();
  for (const [, vi, hi] of cand) if (!uv.has(vi) && !uh.has(hi)) { uv.add(vi); uh.add(hi); out[vi].plan = L.holes[hi]; }
  return out.sort((a, b) => a.no - b.no);
}
/* the hole list the screen walks: the decoded route (route records) or the record's holes */
function lpList(L){ const RT = lpRoute(L); return RT ? RT.view : L.holes.map(H => ({no: H.no, plan: H, fixed: false, conf: 1})); }
/* a sketch of the whole course in route yds: every decoded hole's line, greens, and the labelled choices */
function lpSchem(L, RT, v, pick){
  const R = L.route, xs = R.tc.concat(R.gc).map(p => p[0]), ys = R.tc.concat(R.gc).map(p => p[1]);
  const x0 = Math.min(...xs) - 30, x1 = Math.max(...xs) + 30, y0 = Math.min(...ys) - 30, y1 = Math.max(...ys) + 30;
  const W = x1 - x0, Hh = y1 - y0, P = p => [(p[0] - x0).toFixed(1), (y1 - p[1]).toFixed(1)], sw = Math.max(W, Hh) / 300;
  let g = "";
  for (const u of RT.view) { const a = P(R.tc[u.h.t]), b = P(R.gc[u.h.g]), cur = v && u.no === v.no;
    g += `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="${cur ? "#ffc928" : u.fixed ? "#5cc48d" : "rgba(255,255,255,.45)"}" stroke-width="${(cur ? 3.2 : 1.4) * sw}"${u.ask && !cur ? ` stroke-dasharray="${4 * sw} ${3 * sw}"` : ""}/>`
      + `<text x="${a[0]}" y="${a[1]}" dy="${-4 * sw}" font-size="${11 * sw}" fill="#fff" text-anchor="middle" font-weight="700">${u.no}</text>`; }
  R.gc.forEach((p, i) => { const q = P(p); g += `<circle cx="${q[0]}" cy="${q[1]}" r="${5 * sw}" fill="#3fae5a" stroke="#0b130e" stroke-width="${sw}"/>`; void i; });
  R.tc.forEach(p => { const q = P(p); g += `<rect x="${(+q[0] - 2 * sw).toFixed(1)}" y="${(+q[1] - 2 * sw).toFixed(1)}" width="${4 * sw}" height="${4 * sw}" fill="#d8e6dc"/>`; });
  for (const [lab, kind, i] of pick || []) { const q = P(kind === "g" ? R.gc[i] : R.tc[i]);
    g += `<circle cx="${q[0]}" cy="${q[1]}" r="${9 * sw}" fill="#ff3b30" stroke="#fff" stroke-width="${1.4 * sw}"/><text x="${q[0]}" y="${q[1]}" dy="${4 * sw}" font-size="${11 * sw}" fill="#fff" text-anchor="middle" font-weight="700">${lab}</text>`; }
  return `<div class="mapbox" id="rtMap"><svg viewBox="0 0 ${W.toFixed(0)} ${Hh.toFixed(0)}" style="max-height:60vh;width:100%;background:#26352c" role="img" aria-label="Sketch of the course routing${v ? ", hole " + v.no + " highlighted" : ""}">${g}</svg></div>`;
}
const LETTERS = "ABCDEFGH";
/* greens the golfer may mean for this hole's tee: the 6 cheapest by hole cost (not this one) */
function lpGreenChoices(L, RT, v){
  const S = RT.S, M = S.M, t = v.h.t, gs = [];
  for (let g = 0; g < M.ng; g++) if (g !== v.h.g) gs.push([M.H[t * M.ng + g], g]);
  gs.sort((a, b) => a[0] - b[0]);
  return gs.slice(0, 6).map(([, g], k) => [LETTERS[k], "g", g]);
}
/* tee complexes the round may start from: the 5 likeliest starts, one tee per complex */
function lpStartChoices(L, RT){
  const R = L.route, seen = new Set(), out = [], o = R.S.map((s, i) => [s, i]).sort((a, b) => a[0] - b[0]);
  const h1 = RT.view.find(u => u.no === 1);
  if (h1) { out.push(h1.h.t); seen.add(R.comp[h1.h.t]); }
  for (const [, t] of o) { if (out.length >= 5) break; if (!seen.has(R.comp[t])) { seen.add(R.comp[t]); out.push(t); } }
  return out.map((t, k) => [LETTERS[k], "t", t]);
}
function lpRouteAct(L, kind, ref, tee, green){
  const R = L.route;
  const a = SharedStore.cleanAction({kind, ref: String(ref), answer: {tee_ll: tee == null ? null : R.tees[tee].ll, green_ll: green == null ? null : R.greens[green].ll}, taps: 1});
  if (!a) return;
  const m = lpMine(L.id); m.push(a); if (m.length > 100) m.splice(0, m.length - 100);
  SYNC[L.id] = "saving"; LSTAT = null; LP().rpick = null; save();
  STORE.saveLog(L.id, m, {taps: m.length}).then(r => { SYNC[L.id] = r; softRender(); });
}
const pctTxt = c => (c >= 0.995 ? ">99" : Math.round(c * 100)) + " %";
function lpRouteBox(L, RT, v){
  const S = RT.S, lp = LP(), pick = lp.rpick && lp.rpick.slug === L.id && lp.rpick.no === v.no ? lp.rpick.kind : null;
  let h1 = "";
  if (S.fix.first_tee == null && !lp.h1skip[L.id] && ((S.needHole1 && S.needHole1()) || RT.low.length)) {
    const ch = lpStartChoices(L, RT);
    h1 = `<section class="conf check stack" id="rtHole1"><b>First: which tee is hole 1?</b><span class="sub">One tap fixes the numbering of every hole. The red letters on the sketch are the likeliest first tees (A = the one shown as hole 1 now).</span>
      ${lp.rpick && lp.rpick.slug === L.id && lp.rpick.kind === "h1" ? lpSchem(L, RT, null, ch) : ""}
      <div class="row">${ch.map(([lab, , t]) => `<button class="btn" data-rth1="${t}">${lab}${lab === "A" && RT.view.some(u => u.no === 1 && u.h.t === t) ? " (shown as 1)" : ""}</button>`).join("")}
      <button class="btn ghost" data-rth1map="1">${lp.rpick && lp.rpick.kind === "h1" ? "Hide the sketch" : "Show on the sketch"}</button><button class="btn ghost" data-rth1skip="1">Not now</button></div></section>`;
  }
  const lowTxt = RT.pending ? `<div class="sub" id="rtLow">Re-solving…</div>` : RT.low.length ? `<div class="sub" id="rtLow">${RT.low.length} hole${RT.low.length === 1 ? "" : "s"} still need a look: ${RT.low.map(u => `<button class="chip" data-rtgo="${u.no}" aria-label="Go to hole ${u.no}"><b>${u.no}</b></button>`).join(" ")}</div>`
    : `<div class="sub" id="rtLow">Routing is ${pctTxt(RT.pall)} sure every hole is right (golfers' answers included).</div>`;
  let q;
  if (v.fixed) q = `<div class="row"><span class="badge auto">✓</span><b>Golfers confirmed hole ${v.no} (tee → green).</b></div>`;
  else if (RT.pending && v.checking) q = `<div class="row" id="rtWait"><b>Re-solving the routing…</b><span class="sub">re-checking how sure each hole is</span></div>`;
  else if (!v.ask && !pick && !(lp.rask && lp.rask === L.id + "|" + v.no))
    q = `<div class="row"><span class="badge auto">${pctTxt(v.conf)}</span><b>Routing is ${pctTxt(v.conf)} sure this is hole ${v.no}.</b><button class="btn ghost" data-rtask="1">Not right?</button></div>`;
  else {
    const ch = pick === "green" ? lpGreenChoices(L, RT, v) : null;
    q = `<div class="stack" id="rtAsk"><div><b>Is this hole ${v.no}?</b> <span class="sub">(tee → green on the ${v.plan ? "photo" : "sketch"}; routing is ${pctTxt(v.conf)} sure)</span></div>
      <div class="row"><button class="btn" data-rtyes="1">Yes</button><button class="btn" data-rtno="1">No</button><button class="btn${pick ? " primary" : ""}" data-rtpick="1" aria-pressed="${!!pick}">Pick the right green</button></div>
      ${ch ? `<span class="sub">Tap the letter of hole ${v.no}'s green on the sketch (red); the yellow line is what the routing has now.</span>${lpSchem(L, RT, v, ch)}
        <div class="row">${ch.map(([lab, , g]) => `<button class="btn" data-rtg="${g}">${lab}</button>`).join("")}<button class="btn ghost" data-rtnot="1">This green is a practice green</button></div>` : ""}</div>`;
  }
  return `${h1}<section class="conf ${v.fixed || !v.ask ? "auto" : "check"} stack" id="rtBox">${q}${lowTxt}
    <div class="sub" id="rtNote">Hole pairing from the course map, no scorecard (card-blind routing). Every answer re-solves every hole${RT.ms ? ` (${RT.ms} ms)` : ""}; every answer is shared with the next golfer.</div>${syncLine({id: L.id}, null)}</section>`;
}
/* a decoded hole with no precomputed plan: geometry only */
function lpPending(L, RT, i, v){
  const e = libEntry(L.id), R = L.route;
  const top = `<div class="topbar"><button class="btn ghost" data-go="pick" aria-label="All courses">‹ Courses</button><div class="ttl"><b>${esc(e ? e.name : L.id)}</b><span class="sub">library course · card-blind routing</span></div><span></span></div>`;
  const strip = lpStripRoute(L, RT, i);
  return `<div class="hhead" id="hhead">${top}<div class="holehead"><button class="navbtn" id="lprev" data-lpnav="-1" aria-label="Previous hole">‹</button>
    <div style="text-align:center;min-width:0"><div class="holeno">Hole ${v.no}</div><div class="sub">Par ${v.par} (from the length) · ${Math.round(v.h.L)} yds tee to green</div>
    <div class="row" style="justify-content:center;margin-top:4px"><span class="badge check">plan pending</span></div></div>
    <button class="navbtn" id="lnext" data-lpnav="1" aria-label="Next hole">›</button></div></div>
    ${lpSchem(L, RT, v, null)}
    <section class="panel stack" id="rtPending"><b>Plan pending for this hole</b><p class="sub">The routing now pairs this tee with this green (${Math.round(v.h.L)} yds, yellow line), but no club and aim were precomputed for that pair: they need a server rebuild of the course. ${RT.key !== "[]" ? "A rebuild request was recorded with golfers' answers." : ""} Play it from what you see.</p></section>
    ${lpRouteBox(L, RT, v)}
    <section class="panel stack"><div class="label">All holes</div><div class="strip" id="lpStrip">${strip}</div></section>`;
}
function lpStripRoute(L, RT, i){
  return RT.view.map((u, k) => { let txt = "…";
    if (u.plan) { const H = Object.assign({}, u.plan, {no: u.no}), rr = lpSolve(L, H, lpWind(L, H)); txt = rr.kind === "tee" ? `<span class="${cls(rr.club)}">${esc(lpShort(rr.club))}</span>` : `<span>${Math.round(rr.play)}</span>`; }
    else txt = `<span>plan?</span>`;
    return `<button class="chip" data-lpi="${k}" aria-current="${k === i}" aria-label="Hole ${u.no}">${u.ask ? "<i>?</i>" : ""}<b>${u.no}</b>${txt}</button>`; }).join("");
}
function lpRouteClick(L, d){
  const RT = lpRoute(L); if (!RT) return false;
  const lp = LP(), LS = RT.view, v = LS[lpIdx(L)];
  if (d.rtgo) { const k = LS.findIndex(u => u.no === +d.rtgo); if (k >= 0) lp.idx[L.id] = k; lp.rpick = null; return true; }
  if (d.rth1skip) { lp.h1skip[L.id] = 1; return true; }
  if (d.rth1map) { lp.rpick = lp.rpick && lp.rpick.kind === "h1" ? null : {slug: L.id, kind: "h1"}; return true; }
  if (d.rth1 !== undefined) { lpRouteAct(L, "first", 1, +d.rth1, null); return true; }
  if (!v) return false;
  if (d.rtask) { lp.rask = L.id + "|" + v.no; return true; }
  if (d.rtyes) { lp.rask = null; lpRouteAct(L, "locate", v.no, v.h.t, v.h.g); return true; }
  if (d.rtno) { lp.rask = null; lpRouteAct(L, "reject", v.no, v.h.t, v.h.g); return true; }
  if (d.rtpick) { lp.rpick = lp.rpick && lp.rpick.no === v.no ? null : {slug: L.id, no: v.no, kind: "green"}; return true; }
  if (d.rtg !== undefined) { lp.rask = null; lpRouteAct(L, "locate", v.no, v.h.t, +d.rtg); return true; }
  if (d.rtnot) { lp.rask = null; lpRouteAct(L, "reject", v.no, null, v.h.g); return true; }
  return false;
}
