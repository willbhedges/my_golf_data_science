// Offline tests of the page's golfer confirm and typed card (no browser):
//   node course_data/app/test_confirm.js
// 1. typed_card.js against the cases of course_data/platform/test_typed_card.py (same codes).
// 2. confirm_engine.js on every pool (course_data/app/pools/*.json: the app's courses; fixtures/confirm_pools/*.json:
//    held-out generalize test courses): the golf_confirm/1 payload, yes / no / locate / undo / replay semantics.
// 3. The oracle golfer (fixtures/confirm_truth/<slug>.json, the hidden OSM hole ways) answers the page's questions
//    until every hole is right; taps are compared with confirm.Session's full routing_v2 re-solve on the same course
//    (generalize/eval_v2.json confirm_test_osm, or the truth file's `reference`). Writes out/confirm_sim.json.
const fs = require("fs");
const path = require("path");
const TC = require("./typed_card.js");
const E = require("./confirm_engine.js");

let fails = 0, passes = 0;
const ok = (c, msg) => { if (c) passes++; else { fails++; console.log("FAIL", msg); } };
const codes = (iss, lvl = "error") => iss.filter(i => i.level === lvl).map(i => i.code);

/* ------------------------------------------------------------------ 1. typed card */
const Y18 = [391, 175, 520, 402, 365, 148, 430, 510, 388, 405, 160, 545, 372, 410, 190, 498, 355, 420];
const P18 = [4, 3, 5, 4, 4, 3, 4, 5, 4, 4, 3, 5, 4, 4, 3, 5, 4, 4];
const sum = a => a.reduce((s, x) => s + x, 0);
{
  let [card, iss] = TC.parseTypedCard(Y18.join(" "), {pars: P18.join(","), tee: "White"});
  ok(card && !codes(iss).length, "plain list");
  const ch = E.cardHoles(card, 18);
  ok(ch.every((h, i) => h.par === P18[i] && h.yards[0] === Y18[i]), "card_holes reads a typed card");
  const out = sum(Y18.slice(0, 9)), inn = sum(Y18.slice(9));
  [card, iss] = TC.parseTypedCard(Y18.slice(0, 9).join(", ") + ` OUT ${out}\n` + Y18.slice(9).join(" / ") + ` IN ${inn} ${out + inn}`);
  ok(card && JSON.stringify(card.tee_sets.Typed.yards) === JSON.stringify(Y18) && !codes(iss).length, "separators and subtotals");
  [card] = TC.parseTypedCard(Y18.slice(0, 9).map((y, i) => `${i + 1}: ${y}`).reverse().join("  "));
  ok(card && JSON.stringify(card.tee_sets.Typed.yards) === JSON.stringify(Y18.slice(0, 9)), "hole: value pairs in any order");
  [, iss] = TC.parseTypedCard(Y18.slice(0, 17).join(" ")); ok(codes(iss).includes("count"), "count");
  [, iss] = TC.parseTypedCard(Y18.slice(0, 3).concat([3912]).concat(Y18.slice(5)).join(" "));
  ok(codes(iss).includes("joined") && iss[iss.length - 1].hole === 4, "joined values point at hole 4");
  [, iss] = TC.parseTypedCard(Y18.join(" "), {pars: P18.slice(0, 17).concat([7]).join(" ")}); ok(codes(iss).includes("par_range"), "par_range");
  [, iss] = TC.parseTypedCard(Y18.join(" "), {pars: P18.slice(0, 9).join(" ")}); ok(codes(iss).includes("par_count"), "par_count");
  [, iss] = TC.parseTypedCard("391 17S 520 402 365 148 430 510 388"); ok(codes(iss).includes("not_a_number"), "not_a_number");
  [, iss] = TC.parseTypedCard(Y18.join(" "), {total: sum(Y18) + 10}); ok(codes(iss).includes("total"), "total");
  [, iss] = TC.parseTypedCard(Array(27).fill("400").join(" ")); ok(codes(iss).includes("too_many_holes"), "too_many_holes");
  const y = Y18.slice(); y[1] = 375;
  [card, iss] = TC.parseTypedCard(y.join(" "), {pars: P18.join("")});
  ok(card && JSON.stringify(card.par) === JSON.stringify(P18) && codes(iss, "warning").includes("par_fit"), "digit-run pars + par_fit warning");
  [card] = TC.parseTypedCard(Y18.map(v => Math.floor(v * 0.9144)).join(" "), {unit: "m"});
  ok(card && card.tee_sets.Typed.yards.every((v, i) => Math.abs(v - Y18[i]) <= 2), "metres");
  [, iss] = TC.parseTypedCard(Y18.join(" "), {pars: Array(18).fill(6).join(" ")}); ok(codes(iss).includes("par_total"), "par_total");
  [, iss] = TC.parseTypedCard(Y18.slice(0, 5).concat([30]).concat(Y18.slice(6)).join(" ")); ok(codes(iss).includes("range"), "range");
  [card, iss] = TC.parseTypedCard(Y18.slice(0, 9).concat(Y18.slice(0, 9)).join(" ")); ok(card && codes(iss, "warning").includes("repeat_nine"), "repeat_nine");
  [, iss] = TC.parseTypedCard(""); ok(codes(iss).includes("empty"), "empty");
}

/* ------------------------------------------------------------------ 2. engine semantics */
const POOLS = [path.join(__dirname, "pools"), path.join(__dirname, "fixtures", "confirm_pools")];
const TYPED = path.join(__dirname, "pools", "typed");     /* pools re-solved with a known card (typed-card stand-in) */
const TRUTH = path.join(__dirname, "fixtures", "confirm_truth");
const pools = [];
for (const d of POOLS) if (fs.existsSync(d)) for (const f of fs.readdirSync(d).sort()) if (/^[a-z0-9_]+\.json$/.test(f))
  pools.push({slug: f.replace(".json", ""), app: d === POOLS[0], file: path.join(d, f)});
ok(pools.length >= 3, "at least 3 pools");
for (const p of pools) {
  const P = JSON.parse(fs.readFileSync(p.file, "utf8"));
  const S = new E.ConfirmSession(P);
  const pl = S.payload({name: P.name});
  ok(pl.schema === "golf_confirm/1" && pl.holes.length === P.n, `${p.slug}: payload`);
  ok(pl.holes.every(h => h.p_hole >= 0 && h.p_hole <= 1), `${p.slug}: p_hole in [0, 1]`);
  const qs = S.questions();
  for (let i = 1; i < qs.length; i++) if (qs[i].bits_per_tap > qs[i - 1].bits_per_tap + 1e-9) { ok(false, `${p.slug}: questions sorted by bits per tap`); break; }
  // yes pins the shown hole
  const q = qs.find(x => x.kind === "confirm");
  if (q) {
    const before = S.holes[q.ref];
    S.act({question: q.id, kind: "confirm", ref: q.ref, answer: "yes"});
    ok(S.holes[q.ref].fixed && S.holes[q.ref].green_ll === before.green_ll && S.holes[q.ref].status === "confirmed", `${p.slug}: yes pins hole ${q.ref}`);
    ok(!S.questions().some(x => x.ref === q.ref), `${p.slug}: no more questions on a confirmed hole`);
    S.undoLast();
    ok(!S.holes[q.ref].fixed && S.taps === 0, `${p.slug}: undo`);
  }
  // no: the shown green (with a box near the shown tee) is ruled out for that hole; only a locate is asked next
  const q2 = S.questions().find(x => x.kind === "confirm");
  if (q2) {
    const g0 = S.holes[q2.ref].g_idx, t0 = S.holes[q2.ref].t_idx;
    S.act({question: q2.id, kind: "confirm", ref: q2.ref, answer: "no"});
    const H = S.holes[q2.ref];
    ok(!(H.g_idx === g0 && H.t_idx === t0) || S.vmin > 0, `${p.slug}: no moves hole ${q2.ref}`);
    ok(!S.questions().some(x => x.ref === q2.ref && x.kind === "confirm"), `${p.slug}: after no, hole ${q2.ref} gets a locate`);
    // replay from the saved log gives the same routing
    const S2 = new E.ConfirmSession(P); S2.restore(S.save());
    ok(JSON.stringify(Object.values(S2.holes).map(h => h.key)) === JSON.stringify(Object.values(S.holes).map(h => h.key)), `${p.slug}: replay`);
    S.undoLast();
  }
  // locate on a detected green / tee snaps to it; a spot far from everything becomes the golfer's own point
  const g = P.greens[0], t = P.tees[0];
  S.act({question: "l1", kind: "locate", ref: "1", answer: {tee_ll: t.ll, green_ll: g.ll}});
  ok(S.holes["1"].fixed && S.holes["1"].g_idx === 0 && S.holes["1"].green_ll === g.ll, `${p.slug}: locate snaps`);
  S.undoLast();
  const far = [g.ll[0] + 0.02, g.ll[1] + 0.02];
  S.act({question: "l2", kind: "locate", ref: "2", answer: {tee_ll: far, green_ll: [far[0] + 0.003, far[1]]}});
  ok(S.holes["2"].fixed && S.holes["2"].g_idx === -1 && S.holes["2"].green_ll[0] === far[0] + 0.003, `${p.slug}: locate on an undetected spot`);
  S.undoLast();
  // "this isn't hole n" during the round
  S.act({not: 3});
  ok(S.rejected.has("3") && S.taps === 1, `${p.slug}: this isn't hole 3`);
}

/* ------------------------------------------------------------------ 3. oracle golfer vs confirm.Session */
let ref = {};
try { const ev = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "generalize", "eval_v2.json"), "utf8"));
  for (const r of ev.confirm_test_osm.rows) ref[r.slug] = r.eig; } catch (e) {}
const rows = [];
for (const p of pools) {
  const tf = path.join(TRUTH, p.slug + ".json");
  if (!fs.existsSync(tf)) continue;
  const P = JSON.parse(fs.readFileSync(p.file, "utf8")), T = JSON.parse(fs.readFileSync(tf, "utf8"));
  const runs = [["card", P.card ? null : undefined]];
  if (!P.card && T.card) runs.push(["typed card", T.card]);
  if (!P.card) runs[0][0] = "no card";
  for (const [kind, card] of runs) {
    const t0 = Date.now();
    const typed = card && fs.existsSync(path.join(TYPED, p.slug + ".json")) ? [JSON.parse(fs.readFileSync(path.join(TYPED, p.slug + ".json"), "utf8"))] : [];
    if (card) ok(typed.length === 0 || E.cardMatches(typed[0], card), `${p.slug}: the typed card matches its re-solved pool`);
    const r = E.simulate(P, T, {card: card || null, max_taps: 30, typed_pools: typed});
    const S0 = new E.ConfirmSession(E.poolFor(P, typed, card), {card: card || null});
    const right0 = Object.keys(T.holes).filter(k => E.holeOk(S0.holes[k], T.holes[k])).length;
    const py = (T.reference && (T.reference[P.card || card ? "card" : "nocard"])) || (P.card ? ref[p.slug] : null) || null;
    rows.push({slug: p.slug, app: p.app, card: kind, holes: Object.keys(T.holes).length, right_at_start: right0, taps: r.taps,
               questions: r.questions, stop_rule_taps: r.stop_rule_taps, stop_rule_wrong: r.stop_rule_wrong,
               python_taps: py ? py.taps : null, python_stop_rule_wrong: py ? py.stop_rule_wrong : null, ms: Date.now() - t0});
  }
}
const fmt = v => v == null ? "-" : String(v);
console.log("\ncourse                 card        holes right@0  taps(JS pool)  taps(Python)  stop@  wrong@stop  ms");
for (const r of rows) console.log(`${r.slug.padEnd(22)} ${r.card.padEnd(11)} ${String(r.holes).padStart(5)} ${String(r.right_at_start).padStart(8)} ${fmt(r.taps).padStart(14)} ${fmt(r.python_taps).padStart(13)} ${fmt(r.stop_rule_taps).padStart(6)} ${fmt(r.stop_rule_wrong).padStart(11)} ${String(r.ms).padStart(4)}`);
const reached = rows.filter(r => r.taps != null), both = rows.filter(r => r.taps != null && r.python_taps != null);
const mean = a => a.length ? +(a.reduce((s, x) => s + x, 0) / a.length).toFixed(2) : null;
const agg = {runs: rows.length, reached_100: +(reached.length / Math.max(1, rows.length)).toFixed(3), mean_taps: mean(reached.map(r => r.taps)),
             mean_stop_rule_wrong: mean(rows.filter(r => r.stop_rule_wrong != null).map(r => r.stop_rule_wrong)),
             paired: both.length, paired_mean_js: mean(both.map(r => r.taps)), paired_mean_python: mean(both.map(r => r.python_taps))};
console.log("\n", JSON.stringify(agg));
fs.mkdirSync(path.join(__dirname, "out"), {recursive: true});
fs.writeFileSync(path.join(__dirname, "out", "confirm_sim.json"), JSON.stringify({schema: "confirm_sim/1", doc: "node course_data/app/test_confirm.js: the oracle golfer (hidden OSM hole ways) answers the page's questions (confirm_engine.js over the pool) until every hole is right; python_taps = confirm.Session (full routing_v2 re-solve per answer) on the same inputs.", agg, rows}, null, 1));
ok(agg.reached_100 >= 0.6, "the oracle reaches 100 % on most courses within 30 taps");
console.log(`\n${passes} passed, ${fails} failed`);
process.exit(fails ? 1 : 0);
