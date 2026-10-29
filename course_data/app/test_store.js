// Shared confirmations (golf_shared/1): canonical answers, merging golfers, the two storage backends.
//   node course_data/app/test_store.js
// 1. canonical answers ("yes" -> a pin of the shown green + tee, "no" -> a reject of them) replay to exactly the
//    same hole map as the raw answers, on every app pool and the confirm test pools (an oracle golfer from the
//    hidden truth answers 10 questions);
// 2. two golfers' logs replay to the same pinned holes in either order;
// 3. the shared store over a mock db: golfer A confirms, golfer B (fresh device) sees A's map, both write at
//    once without losing each other's answers, a view-only golfer falls back to this device;
// 4. the localStorage store survives a reload; reports are listed; untrusted documents are cleaned.
const fs = require("fs");
const path = require("path");
const E = require("./confirm_engine.js");
const SS = require("./shared_store.js");
const M = require("./mock_db.js");

let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else { fail++; console.log("FAIL " + msg); } };
const sameMap = (a, b) => Object.keys(a.holes).every(r => a.holes[r].key === b.holes[r].key && a.holes[r].fixed === b.holes[r].fixed);
const memLS = () => { const m = new Map(); return {getItem: k => m.has(k) ? m.get(k) : null, setItem: (k, v) => m.set(k, String(v)), _m: m}; };

function oracle(S, truth, k) {             /* answer k questions truthfully; returns [raw actions] */
  const raw = [];
  for (let i = 0; i < k && !S.done(); i++) {
    const q = S.questions(1)[0]; if (!q) break;
    const T = truth.holes[q.ref];
    let a;
    if (q.kind === "confirm") a = {question: q.id, kind: "confirm", ref: q.ref, answer: !T || E.holeOk(S.holes[q.ref], T) ? "yes" : "no"};
    else a = {question: q.id, kind: "locate", ref: q.ref, answer: {tee_ll: T ? T.tee_ll : S.holes[q.ref].tee_ll, green_ll: T ? T.green_ll : S.holes[q.ref].green_ll}};
    raw.push(a); S.act(a);
  }
  return raw;
}

(async () => {
  const H = __dirname, pools = [];
  for (const s of ["coldwater", "mozingo_lake", "veenker", "wakonda"]) pools.push([s, path.join(H, "pools", s + ".json"), path.join(H, "fixtures", "confirm_truth", s + ".json")]);
  for (const f of fs.readdirSync(path.join(H, "fixtures", "confirm_pools")).sort()) pools.push([f.replace(".json", ""), path.join(H, "fixtures", "confirm_pools", f), path.join(H, "fixtures", "confirm_truth", f)]);
  for (const [slug, pf, tf] of pools) {
    if (!fs.existsSync(pf) || !fs.existsSync(tf)) continue;
    const pool = JSON.parse(fs.readFileSync(pf)); delete pool.overview;
    const truth = JSON.parse(fs.readFileSync(tf));
    // 1. raw vs canonical
    const S0 = new E.ConfirmSession(pool), raw = oracle(S0, truth, 10);
    const S1 = new E.ConfirmSession(pool), canon = [];
    for (const a of raw) { const c = S1.canonical(a); canon.push(c); S1.act(c); }
    ok(sameMap(S0, S1), `${slug}: canonical answers give the same map as the raw ones`);
    const cl = SS.cleanLog(JSON.parse(JSON.stringify(canon)));
    ok(cl.length === canon.length, `${slug}: canonical log survives cleaning (${cl.length}/${canon.length})`);
    const S2 = new E.ConfirmSession(pool); S2.restore({log: cl});
    ok(sameMap(S0, S2), `${slug}: the cleaned, stored log restores the same map`);
    ok(S2.taps === S0.taps, `${slug}: taps carried (${S2.taps} vs ${S0.taps})`);
    // 2. two golfers, either order
    const half = Math.ceil(cl.length / 2), A = cl.slice(0, half), B = cl.slice(half);
    const doc = {logs: {ga: {log: A, at: "2026-10-01T10:00:00Z"}, gb: {log: B, at: "2026-10-02T10:00:00Z"}}};
    const ab = new E.ConfirmSession(pool); ab.restore({log: SS.replayLog(doc, "nobody", [])});
    const ba = new E.ConfirmSession(pool); ba.restore({log: SS.replayLog(doc, "ga", A)});   /* ga on their own device: theirs last */
    const pins = S => Object.values(S.holes).filter(h => h.fixed).map(h => h.ref + ":" + h.key).sort().join(",");
    ok(pins(ab) === pins(S0) && pins(ba) === pins(S0), `${slug}: two golfers' answers pin the same holes in either order`);
    ok(sameMap(ab, S0), `${slug}: merged map equals one golfer answering everything`);
    // reject replays like the "no" it came from
    const r = S0.questions(1).find(q => q.kind === "confirm");
    if (r) { const Sx = new E.ConfirmSession(pool), Sy = new E.ConfirmSession(pool); Sx.restore({log: cl}); Sy.restore({log: cl});
      Sx.act({question: r.id, kind: "confirm", ref: r.ref, answer: "no"}); Sy.act(Sy.canonical({question: r.id, kind: "confirm", ref: r.ref, answer: "no"}));
      ok(sameMap(Sx, Sy), `${slug}: canonical reject == raw "no"`);
      const Sz = new E.ConfirmSession(pool); Sz.restore({log: cl}); Sz.act(Sz.canonical({not: r.ref})); ok(sameMap(Sx, Sz), `${slug}: "this isn't hole n" == "no"`); }
  }
  // 4a. cleaning untrusted documents
  ok(SS.cleanAction({kind: "locate", ref: "7", answer: {tee_ll: [1, 2], green_ll: [3, 4]}}) !== null, "clean: a good locate passes");
  ok(SS.cleanAction({kind: "locate", ref: "7<script>", answer: {tee_ll: [1, 2], green_ll: [3, 4]}}) === null, "clean: bad ref dropped");
  ok(SS.cleanAction({kind: "locate", ref: "7", answer: {tee_ll: ["x", 2], green_ll: [3, 4]}}) === null, "clean: bad coordinate dropped");
  ok(SS.cleanAction({kind: "eval", ref: "7", answer: {green_ll: [3, 4]}}) === null, "clean: unknown kind dropped");
  ok(SS.cleanLog(new Array(500).fill({kind: "reject", ref: "1", answer: {green_ll: [3, 4]}})).length === 120, "clean: log capped");
  const cm = SS.cleanMap({logs: {g1: {log: [{kind: "locate", ref: "3", answer: {green_ll: [3, 4]}}, "junk"], at: "2026-10-01T00:00:00Z"}, g2: "junk"}, card: {tee_sets: {T: {yards: [400, "x"]}}}}, "c");
  ok(Object.keys(cm.logs).length === 1 && cm.logs.g1.log.length === 1 && cm.card === null, "clean: map doc cleaned");
  ok(SS.cleanReport({course: "coldwater", hole: 7, kind: "<b>", text: "x".repeat(900)}).text.length === 500, "clean: report text capped");
  ok(SS.cleanReport({course: "Bad Course!", hole: 7}) === null, "clean: bad course id dropped");

  // 3. shared store over a mock db
  const server = new M.MockServer();
  const lsA = memLS(), lsB = memLS(), lsC = memLS();
  const A = SS.createStore({localStorage: lsA, claude: M.mockClaude(server, "user-a")});
  const B = SS.createStore({localStorage: lsB, claude: M.mockClaude(server, "user-b")});
  ok(await A.ready === "shared" && await B.ready === "shared", "shared: both golfers get shared storage");
  ok(A.gid === "user-a", "shared: golfer id from the user capability");
  const la = [{question: "l1", kind: "locate", ref: "1", answer: {tee_ll: [-93.6, 42.0], green_ll: [-93.61, 42.01]}, taps: 1}];
  const lb = [{question: "r2", kind: "reject", ref: "2", answer: {tee_ll: [-93.62, 42.0], green_ll: [-93.63, 42.01]}, taps: 1}];
  ok(await A.saveLog("coldwater", la, {taps: 1}) === "shared", "shared: A's answer saved for everyone");
  await new Promise(r => setTimeout(r, 20));
  const mb = B.map("coldwater");
  ok(mb && mb.logs["user-a"] && mb.logs["user-a"].log.length === 1, "shared: B (another device) sees A's answer");
  ok(SS.replayLog(mb, "user-b", []).length === 1, "shared: B replays A's answer");
  // both write at once: neither loses the other's entry (update merges only the writer's key)
  await Promise.all([A.saveLog("coldwater", la.concat(lb), {taps: 2}), B.saveLog("coldwater", lb, {taps: 1})]);
  const doc = server.get("maps/coldwater");
  ok(doc.logs["user-a"].log.length === 2 && doc.logs["user-b"].log.length === 1, "shared: concurrent writes keep both golfers' answers");
  await B.saveLog("coldwater", [], {taps: 0});
  ok(!server.get("maps/coldwater").logs["user-b"] && server.get("maps/coldwater").logs["user-a"], "shared: undoing all of B's answers removes only B's entry");
  await A.saveLog("coldwater", la, {taps: 1, card: {tee_sets: {Typed: {yards: [400, 150]}}}});
  ok(server.get("maps/coldwater").card.tee_sets.Typed.total === 550, "shared: a typed card is shared");
  ok(await A.addReport({course: "coldwater", hole: 4, kind: "green", text: "green moved", tee: "Blue"}) === "shared", "shared: report saved");
  await new Promise(r => setTimeout(r, 20));
  ok(B.reports("coldwater").length === 1 && B.reports("coldwater")[0].kind === "green", "shared: B lists A's report");
  // a view-only golfer: writes refused -> kept on this device, said so
  const view = new M.MockServer(); view.failWrites = true;
  const V = SS.createStore({localStorage: lsC, claude: M.mockClaude(view, "user-v")});
  await V.ready;
  ok(await V.saveLog("veenker", la, {taps: 1}) === "local", "view-only: answer kept on this device");
  ok(V.canWrite === false, "view-only: store knows it cannot write");
  // 4b. no claude at all: local store, survives a reload
  const lsL = memLS();
  const L1 = SS.createStore({localStorage: lsL});
  ok(await L1.ready === "local", "local: no window.claude -> local");
  await L1.saveLog("wakonda", la, {taps: 1});
  await L1.addReport({course: "wakonda", hole: 9, kind: "hazard", text: "pond missing"});
  const L2 = SS.createStore({localStorage: lsL});
  await L2.ready;
  ok(L2.gid === L1.gid, "local: same golfer id after reload");
  ok(L2.map("wakonda").logs[L2.gid].log.length === 1, "local: answers survive a reload");
  ok(L2.reports("wakonda").length === 1 && L2.reports("wakonda")[0].mine, "local: report listed after reload");
  // 4c. a db that never answers falls back
  const T0 = Date.now();
  const N = SS.createStore({localStorage: memLS(), claude: {use: () => new Promise(() => {})}, timeoutMs: 200});
  ok(await N.ready === "local" && Date.now() - T0 < 2000, "timeout: a host that never answers -> local");
  // a local-only device later gets shared storage: its earlier answers go up once
  const srv2 = new M.MockServer(), lsU = memLS();
  const U1 = SS.createStore({localStorage: lsU}); await U1.ready; await U1.saveLog("mozingo_lake", la, {taps: 1});
  const U2 = SS.createStore({localStorage: lsU, claude: M.mockClaude(srv2, "user-u")}); await U2.ready;
  await new Promise(r => setTimeout(r, 30));
  ok(srv2.get("maps/mozingo_lake") && srv2.get("maps/mozingo_lake").logs["user-u"], "upgrade: local-only answers pushed to the shared map");
  console.log(`${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})();
