/* JS vs Python parity of the pathroute v2 confirm-and-resolve decoder (pathroute_engine.js vs decode2 / run2 /
   confidence). Fixtures: fixtures/pathroute/<slug>.json.gz (zero_tap test-split courses, written by
   course_data/zero_tap/pathroute_v2/export_js.py): the exported decoder inputs + Python decodes with no facts,
   two confirmed pairs, a reject + practice green, and a hole-1 tee.

     node course_data/app/test_pathroute.js [fixture dir]
   Pass = every case's holes (number, loop, tee, green, box set) identical, L / route confidence / features /
   calibrated confidence within 1e-9. */
"use strict";
const fs = require("fs"), path = require("path"), zlib = require("zlib");
const PR = require("./pathroute_engine.js");
const dir = process.argv[2] || path.join(__dirname, "fixtures", "pathroute");
const files = fs.readdirSync(dir).filter(f => f.endsWith(".json.gz")).sort();
let nCourse = 0, nCase = 0, nFix = 0, nSess = 0, bad = 0, ms = 0, maxd = 0;
const close = (a, b, tol) => { const d = Math.abs(a - b); maxd = Math.max(maxd, d); return d <= tol * Math.max(1, Math.abs(a)); };
for (const f of files) {
  const doc = JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(dir, f))).toString());
  const R = doc.route;
  const S = new PR.Session(R);
  nCourse++;
  for (const c of doc.cases) {
    const t0 = Date.now();
    const fix = c.fix ? {pairs: c.fix.pairs || [], not_green: c.fix.not_green || [], first_tee: c.fix.first_tee, reject: c.fix.reject || []} : null;
    const free = fix ? S.freePairs() : null;
    const r = PR.decodeCourse(S.M, R, R.comp, fix, free);
    const conf = r.holes.length ? PR.calibrate(PR.hasFix(fix) && R.calib_fix ? R.calib_fix : R.calib, r.X) : [];
    const fp = new Set(((fix && fix.pairs) || []).map(p => p[1] + "," + p[2]));
    const cj = r.holes.map((h, i) => fp.has(h.t + "," + h.g) ? 1.0 : conf[i]);
    ms += Date.now() - t0;
    nCase++; if (fix) nFix++;
    const errs = [];
    if (r.holes.length !== c.holes.length) errs.push(`n holes ${r.holes.length} vs ${c.holes.length}`);
    else {
      r.holes.forEach((h, i) => {
        const [n, loop, t, g, boxes, L] = c.holes[i];
        if (h.number !== n || h.loop !== loop || h.t !== t || h.g !== g || JSON.stringify(h.boxes) !== JSON.stringify(boxes))
          errs.push(`hole ${i}: js ${h.number}/${h.loop} t${h.t} g${h.g} [${h.boxes}] vs py ${n}/${loop} t${t} g${g} [${boxes}]`);
        if (!close(h.L, L, 1e-9)) errs.push(`hole ${i} L ${h.L} vs ${L}`);
        if (!close(cj[i], c.conf[i], 1e-9)) errs.push(`hole ${i} conf ${cj[i]} vs ${c.conf[i]}`);
        r.X[i].forEach((x, k) => { if (!close(x, c.X[i][k], 1e-9)) errs.push(`hole ${i} X[${k}] ${x} vs ${c.X[i][k]}`); });
      });
      if (r.holes.length && !close(r.conf, c.route_conf, 1e-9)) errs.push(`route conf ${r.conf} vs ${c.route_conf}`);
    }
    if (errs.length) { bad++; console.log(`FAIL ${doc.slug} fix=${JSON.stringify(c.fix)}\n  ` + errs.slice(0, 6).join("\n  ")); }
  }
  /* resolve2.Session under the shipped POLICY (Session.answer): yes / correction / not a hole; holes, conf, P(all pairs
     right) and the ask list after each answer, and whether the answer re-solved */
  if (doc.session) {
    const S2 = new PR.Session(R);
    for (const st of doc.session) {
      const a = st.act;
      const t0 = Date.now();
      let solved = true;
      if (a && a[0] === "answer") solved = S2.answer(a[1], a[2], a[3], a[4]);
      if (a && a[0] === "hole1") S2.holeOne(a[1]);
      if (solved) S2.solve();
      if (st.need_h1 !== undefined && S2.needHole1() !== st.need_h1) { bad++; console.log(`FAIL ${doc.slug} needHole1 ${S2.needHole1()} vs ${st.need_h1}`); }
      if (st.solved !== undefined && solved !== st.solved) { bad++; console.log(`FAIL ${doc.slug} answer ${JSON.stringify(a)} re-solve ${solved} vs ${st.solved}`); }
      if (st.p_all !== undefined && !close(S2.pAll(), st.p_all, 1e-9)) { bad++; console.log(`FAIL ${doc.slug} p_all ${S2.pAll()} vs ${st.p_all}`); }
      if (st.need !== undefined && JSON.stringify(S2.need()) !== JSON.stringify(st.need)) { bad++; console.log(`FAIL ${doc.slug} need ${S2.need()} vs ${st.need}`); }
      ms += Date.now() - t0; nCase++; nSess++;
      const errs = [];
      if (S2.holes.length !== st.holes.length) errs.push(`n holes ${S2.holes.length} vs ${st.holes.length}`);
      else S2.holes.forEach((h, i) => {
        const [n, loop, t, g, boxes] = st.holes[i];
        if (h.number !== n || h.loop !== loop || h.t !== t || h.g !== g || JSON.stringify(h.boxes) !== JSON.stringify(boxes))
          errs.push(`hole ${i}: js ${h.number}/${h.loop} t${h.t} g${h.g} vs py ${n}/${loop} t${t} g${g}`);
        if (!close(S2.conf[i], st.conf[i], 1e-9)) errs.push(`hole ${i} conf ${S2.conf[i]} vs ${st.conf[i]}`);
      });
      if (errs.length) { bad++; console.log(`FAIL ${doc.slug} session act=${JSON.stringify(a)}\n  ` + errs.slice(0, 6).join("\n  ")); }
    }
  }
}
console.log(`pathroute parity: ${nCourse} courses, ${nCase} cases (${nFix} with facts, ${nSess} policy session steps), ${bad} failing; max |diff| ${maxd.toExponential(2)}; ${(ms / Math.max(nCase, 1)).toFixed(0)} ms / solve`);
if (nCourse < 1 || bad) process.exit(1);
