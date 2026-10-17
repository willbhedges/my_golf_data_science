// Headless check of the "I'm playing course X from tees Y" flow on auto-mapped courses, at 400 px and 1280 px:
//   NODE_PATH=$(npm root -g) node course_data/app/test_confirm_ui.js [out/aim_caddie.html] [shots dir]
// Runs the artifact-format copy wrapped the way the host wraps it. Per width and per auto course with a confirm pool:
//   pick the course and a tee set -> "Check the hole map" -> (no card online: a wrong typed card shows its error,
//   then the real card is typed) -> a simulated golfer answers every question from the hidden truth
//   (fixtures/confirm_truth/<slug>.json: the OSM hole ways the routing never saw) by clicking Yes / No or tapping
//   the true tee and green on the map, until every hole is right (it presses "Keep checking" when the stop rule
//   ends early). Reports taps to 100 % and the stop rule's taps / wrong holes, and checks they equal the node
//   simulation of the same engine (test_confirm.js). Then "This isn't hole n" on a hole, re-located from the hole
//   screen, and a screenshot of every hole of one course with its plan (no NaN, no horizontal scroll, the hole map
//   agrees with the plan). Fails on any page error.
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");
const TIMEOUT = 8000;
const E = require("./confirm_engine.js");

const art = path.resolve(process.argv[2] || path.join(__dirname, "out", "aim_caddie.html"));
const shots = path.resolve(process.argv[3] || path.join(__dirname, "out", "test_confirm"));
fs.mkdirSync(shots, { recursive: true });
for (const f of fs.readdirSync(shots)) if (/\.png$/.test(f)) fs.unlinkSync(path.join(shots, f));
const html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>t</title></head><body>' +
  fs.readFileSync(art, "utf8") + "</body></html>";
const wrapped = path.join(shots, "wrapped.html");
fs.writeFileSync(wrapped, html);
const URL0 = "file://" + wrapped;
const TRUTH = path.join(__dirname, "fixtures", "confirm_truth");
const MAX_TAPS = 30;
const SHOT_COURSE = process.env.SHOT_COURSE || "coldwater";

(async () => {
  const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
  const problems = [], results = [];
  for (const vp of [{ width: 400, height: 860, tag: "400" }, { width: 1280, height: 900, tag: "1280" }]) {
    const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
    const page = await ctx.newPage();
    page.setDefaultTimeout(TIMEOUT);
    const errs = [];
    page.on("pageerror", e => errs.push("pageerror: " + e.message));
    page.on("console", m => { if (m.type() === "error" && !/fonts\.(googleapis|gstatic)|ERR_NAME_NOT_RESOLVED|net::/.test(m.text())) errs.push("console: " + m.text()); });
    await page.goto(URL0);
    await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
    await page.goto(URL0);
    const courses = await page.evaluate(() => D.courses.filter(c => c.confirm).map(c => ({ id: c.id, sets: c.tee_sets.filter(t => t.computed !== "missing").map(t => t.name), card_known: c.confirm.card_known, n: c.holes.length })));
    const layout = async (what) => {
      const r = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
        nan: /NaN|undefined/.test(document.getElementById("app").innerText) }));
      if (r.sw > r.cw + 1) problems.push(`${vp.tag} ${what}: horizontal scroll ${r.sw} > ${r.cw}`);
      if (r.nan) problems.push(`${vp.tag} ${what}: NaN/undefined in the page`);
    };
    const routed = id => page.evaluate(id => { const S = SESS[id]; return Object.fromEntries(Object.entries(S.holes).map(([r, h]) => [r, { tee_ll: h.tee_ll, green_ll: h.green_ll, fixed: h.fixed }])); }, id);
    const wrongOf = (R, T) => Object.keys(T.holes).filter(r => !E.holeOk(R[r], T.holes[r]));
    const tapLL = async (ll) => {
      const xy = await page.evaluate(ll => { const C = cur(), svg = document.getElementById("cmap"); svg.scrollIntoView({block: "center"});
        const m = svg.getScreenCTM(), p = ovPx(C, ll);
        if (p[0] < 0 || p[1] < 0 || p[0] > C.confirm.overview.w || p[1] > C.confirm.overview.h) throw new Error("point off the map " + ll);
        const q = svg.createSVGPoint(); q.x = p[0]; q.y = p[1]; const s = q.matrixTransform(m); return [s.x, s.y]; }, ll);
      await page.mouse.click(xy[0], xy[1]);
    };
    for (const C of courses) { try {
      const tf = path.join(TRUTH, C.id + ".json");
      if (!fs.existsSync(tf)) { problems.push(`${C.id}: no truth fixture`); continue; }
      const T = JSON.parse(fs.readFileSync(tf, "utf8"));
      await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} for (const k in SESS) delete SESS[k];
        Object.assign(st, {confirm: {}, cfocus: {}, creturn: {}, cmore: {}, cskipcard: {}, ctyped: {}, cstep: null, screen: "pick"}); render(); });
      await page.click(`[data-course="${C.id}"]`);
      await page.click(`[data-set="${C.sets[C.sets.length - 1]}"]`);      // a non-default tee set
      await page.click(`[data-set="${C.sets[0]}"]`);
      await layout(`${C.id} tees`);
      await page.click("#goConfirm");
      let typed = null;
      if (!C.card_known) {                                                   // the typed-card path
        if (!(await page.locator("#typedCard").count())) problems.push(`${C.id}: no typed-card panel`);
        const ys = Object.values(T.card.tee_sets)[0].yards, pars = T.card.par || Object.values(T.holes).map(h => h.par);
        await page.fill("#tcYards", ys.slice(0, 17).join(" "));
        await page.click('[data-tc="use"]');
        const err = await page.locator("#tcIssues .tc-err").innerText().catch(() => "");
        if (!/17 yardages typed, expected 9 or 18 \(one missing\)/.test(err)) problems.push(`${C.id}: 17 values not rejected (${err})`);
        const sm = a => a.reduce((x, y) => x + y, 0);                       // typed the way the card reads: OUT / IN columns
        await page.fill("#tcYards", ys.slice(0, 9).join(", ") + " OUT " + sm(ys.slice(0, 9)) + "\n" + ys.slice(9).join(" ") + " IN " + sm(ys.slice(9)));
        await page.fill("#tcPars", pars.join(""));
        await page.click('[data-tc="use"]');
        typed = await page.locator("#tcOk").innerText().catch(() => "");
        if (!/Using your card: 18 holes/.test(typed)) problems.push(`${vp.tag} ${C.id}: typed card not accepted (${typed}; ${await page.locator("#typedCard").innerText().catch(() => "")})`);
        await page.screenshot({ path: path.join(shots, `${vp.tag}_${C.id}_typed.png`), fullPage: false });
      }
      await page.screenshot({ path: path.join(shots, `${vp.tag}_${C.id}_confirm0.png`), fullPage: true });
      await layout(`${C.id} confirm`);
      const R0 = await routed(C.id);
      const right0 = Object.keys(T.holes).length - wrongOf(R0, T).length;
      let stop = null, taps = 0, n = 0, shotQ = 0;
      for (;;) {
        const R = await routed(C.id), wrong = wrongOf(R, T);
        taps = await page.evaluate(id => SESS[id].taps, C.id);
        const done = await page.locator("#cDone").count();
        if (done && stop === null) { stop = { taps, wrong: wrong.length }; await page.screenshot({ path: path.join(shots, `${vp.tag}_${C.id}_done.png`), fullPage: true }); }
        if (!wrong.length || taps >= MAX_TAPS) break;
        if (done) { await page.click("[data-cmore]"); continue; }
        const q = (await page.locator(".qcard").count()) ? await page.getAttribute(".qcard", "data-q") : null;
        if (!q) { problems.push(`${vp.tag} ${C.id}: no question while ${wrong.length} holes are wrong: ${(await page.locator("#app").innerText()).slice(0, 300)}`);
          await page.screenshot({ path: path.join(shots, `${vp.tag}_${C.id}_stuck.png`), fullPage: true }); break; }
        const ref = q.slice(1);
        if (shotQ < 2) { await page.screenshot({ path: path.join(shots, `${vp.tag}_${C.id}_q${n}_${q}.png`), fullPage: false }); shotQ++; }
        if (q[0] === "c") await page.click(E.holeOk(R[ref], T.holes[ref]) ? "#qYes" : "#qNo");
        else { await tapLL(T.holes[ref].tee_ll); await tapLL(T.holes[ref].green_ll); }
        n++;
      }
      const Rf = await routed(C.id), left = wrongOf(Rf, T).length;
      if (stop === null) stop = { taps, wrong: left };                  // as route_eval: the stop rule had not fired yet
      // the same oracle on the same engine in node must give the same taps
      const P = await page.evaluate(id => { const S = SESS[id]; return { pool: S.pool, card: S.card }; }, C.id);
      const sim = E.simulate(P.pool, T, { card: P.card, max_taps: MAX_TAPS });
      const row = { width: vp.tag, course: C.id, card: C.card_known ? "card" : "typed card", holes: Object.keys(T.holes).length, right_at_start: right0,
        taps_to_correct: left ? null : taps, questions: n, stop_rule_taps: stop ? stop.taps : null, stop_rule_wrong: stop ? stop.wrong : null,
        node_sim_taps: sim.taps, python_taps: ((T.reference || {}).card || {}).taps ?? null, python_stop_rule: ((T.reference || {}).card || {}).stop_rule_taps ?? null };
      results.push(row);
      if (left) problems.push(`${vp.tag} ${C.id}: ${left} holes still wrong after ${taps} taps`);
      if (sim.taps !== row.taps_to_correct) problems.push(`${vp.tag} ${C.id}: page ${row.taps_to_correct} taps vs node sim ${sim.taps}`);
      // "This isn't hole n" from the hole screen: the golfer re-locates it and is back on the hole
      await page.click("[data-go=hole]").catch(async () => { await page.click('[data-go="tees"]'); await page.click('[data-go="hole"]'); });
      const hn = Object.keys(T.holes)[4];
      await page.click(`.chip[data-i="${+hn - 1}"]`);
      await page.click("#notHole");
      const q2 = (await page.locator(".qcard").count()) ? await page.getAttribute(".qcard", "data-q") : null;
      if (q2 !== "l" + hn) problems.push(`${vp.tag} ${C.id}: "This isn't hole ${hn}" asked ${q2}`);
      await page.screenshot({ path: path.join(shots, `${vp.tag}_${C.id}_nothole.png`), fullPage: false });
      await tapLL(T.holes[hn].tee_ll); await tapLL(T.holes[hn].green_ll);
      const scr = await page.evaluate(() => st.screen), R2 = await routed(C.id);
      if (scr !== "hole") problems.push(`${vp.tag} ${C.id}: not back on the hole after re-locating (${scr})`);
      if (!E.holeOk(R2[hn], T.holes[hn]) || !R2[hn].fixed) problems.push(`${vp.tag} ${C.id}: hole ${hn} not fixed by the re-locate`);
      const strip = await page.locator("#routeStrip").innerText().catch(() => "");
      if (!new RegExp(`Hole ${hn} confirmed`).test(strip)) problems.push(`${vp.tag} ${C.id}: hole strip says "${strip.slice(0, 60)}"`);
      await layout(`${C.id} hole after not-hole`);
      // every hole of one course: the plan renders, and the confirmed map agrees with it
      if (C.id === SHOT_COURSE || (!courses.some(c => c.id === SHOT_COURSE) && C === courses[0])) {
        for (let i = 0; i < C.n; i++) {
          await page.click(`.chip[data-i="${i}"]`);
          await layout(`${C.id} hole ${i + 1}`);
          const s = await page.locator("#routeStrip").innerText();
          if (/somewhere other than/.test(s)) problems.push(`${vp.tag} ${C.id} hole ${i + 1}: map and plan disagree after the confirm`);
          const svg = await page.locator("#ov").count();
          if (!svg) problems.push(`${vp.tag} ${C.id} hole ${i + 1}: no plan map`);
          await page.locator(".app").screenshot({ path: path.join(shots, `${vp.tag}_${C.id}_hole${String(i + 1).padStart(2, "0")}.png`) });
        }
      }
      // reload keeps the answers (localStorage), on the same routing
      const keys0 = await page.evaluate(id => Object.values(SESS[id].holes).map(h => h.key).join(","), C.id);
      await page.reload();
      const keys1 = await page.evaluate(id => { sess(D.courses.find(c => c.id === id)); return Object.values(SESS[id].holes).map(h => h.key).join(","); }, C.id);
      if (keys0 !== keys1) problems.push(`${vp.tag} ${C.id}: routing changed after reload`);
    } catch (e) {
      problems.push(`${vp.tag} ${C.id}: ${String(e.message || e).split("\n")[0]} (screen ${await page.evaluate(() => st.screen).catch(() => "?")})`);
      await page.screenshot({ path: path.join(shots, `${vp.tag}_${C.id}_error.png`), fullPage: true }).catch(() => {});
    } }
    problems.push(...errs.map(e => `${vp.tag} ${e}`));
    await ctx.close();
  }
  await browser.close();
  const pad = (v, n) => String(v == null ? "-" : v).padStart(n);
  console.log("width course         card        holes right@0 taps→100%  node  python  stop@ wrong@stop");
  for (const r of results) console.log(`${r.width.padEnd(5)} ${r.course.padEnd(14)} ${r.card.padEnd(11)} ${pad(r.holes, 5)} ${pad(r.right_at_start, 7)} ${pad(r.taps_to_correct, 9)} ${pad(r.node_sim_taps, 5)} ${pad(r.python_taps, 7)} ${pad(r.stop_rule_taps, 6)} ${pad(r.stop_rule_wrong, 10)}`);
  fs.writeFileSync(path.join(__dirname, "out", "confirm_ui_summary.json"), JSON.stringify({ schema: "confirm_ui/1", results, problems }, null, 1));
  if (problems.length) { console.log("\nPROBLEMS:\n" + problems.join("\n")); process.exit(1); }
  console.log(`\nOK: ${results.length} confirm runs, no problems`);
})().catch(e => { console.error(e); process.exit(1); });
