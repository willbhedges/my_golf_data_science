// Card-blind routing confirm in the app (lib_play.js "card-blind routing" + pathroute_engine.js), playwright.
//   node course_data/app/test_route_ui.js [out dir] [shots dir]
// The library record of tomahawk_hills (out/lib) gets the card-blind route of fixtures/lib_route/tomahawk_hills.json
// (built by build_library_play.py --route-cardblind: OSM hole ways ignored) through window.AIM_LIB_INLINE. The test
// raises the route's ask target (policy target 0.99999: P(all pairs right) never reaches it, so every hole below the
// policy cap 0.999 is asked) so that the questions show.
// At 400 px and 1280 px, golfer A (shared mock db):
//  1. hole 1 shows the plan (club / aim on the photo), "Is this hole 1?" with Yes / No / Pick the right green, and
//     "Which tee is hole 1?"; no NaN, no horizontal scroll, no console errors;
//  2. "Yes" -> hole 1 confirmed (no re-solve); the hole-1 tee answer hides that question;
//  3. "No" on hole 2 -> re-solve -> hole 2's pairing changes; a hole without a precomputed plan shows "plan pending"
//     (sketch, no club) and a golf_replan/1 request lands in requests/;
//  4. "Pick the right green" on hole 3 -> letters on the sketch -> picking one confirms hole 3 with that green;
//  5. golfer B (fresh device, same db) opens the course and starts from A's facts: same strip, hole 1 confirmed.
const path = require("path"), fs = require("fs"), http = require("http");
let pw; try { pw = require("playwright"); } catch (e) { pw = require("/opt/node22/lib/node_modules/playwright"); }
const { chromium } = pw;
const M = require("./mock_db.js");
const outDir = path.resolve(process.argv[2] || path.join(__dirname, "out"));
const shots = path.resolve(process.argv[3] || path.join(outDir, "test_route"));
fs.mkdirSync(shots, { recursive: true });
const SLUG = "tomahawk_hills";
const rec = JSON.parse(fs.readFileSync(path.join(outDir, "lib", SLUG + ".json")));
rec.route = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures", "lib_route", SLUG + ".json"))).route;
rec.route.conf_ok = 0.999;
rec.route.policy = Object.assign({}, rec.route.policy || {}, { target: 0.99999 });
const problems = [], errors = [];
const expect = (c, msg) => { if (!c) problems.push(msg); };

function serve() {
  return new Promise(res => {
    const srv = http.createServer((q, r) => {
      const u = decodeURIComponent(q.url.split("?")[0].split("#")[0]), f = path.join(outDir, u === "/" ? "index.html" : u);
      if (!f.startsWith(outDir) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end("not found"); }
      r.writeHead(200, { "content-type": f.endsWith(".json") ? "application/json" : "text/html; charset=utf-8" });
      fs.createReadStream(f).pipe(r);
    });
    srv.listen(0, "127.0.0.1", () => res(srv));
  });
}
function watch(page, tag) {
  page.on("console", m => { const u = (m.location() || {}).url || ""; if (m.type() === "error" && !/fonts\.(googleapis|gstatic)|ERR_CERT|ERR_NAME|ERR_INTERNET|404/.test(m.text() + " " + u)) errors.push(`${tag} console: ${m.text()}`); });
  page.on("pageerror", e => errors.push(`${tag} pageerror: ${e.message}`));
}
async function check(page, what) {
  const r = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
    nan: /NaN|undefined|\[object Object\]|Infinity/.test(document.getElementById("app").innerText) }));
  if (r.sw > r.cw + 1) problems.push(`${what}: horizontal scroll ${r.sw} > ${r.cw}`);
  if (r.nan) problems.push(`${what}: NaN/undefined in the page`);
}
async function context(browser, server, uid, viewport) {
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1 });
  await ctx.exposeFunction("__mockdb", async (op, args) => { try { return { ok: await server[op](...args) }; } catch (e) { return { err: e.code || String(e) }; } });
  await ctx.addInitScript({ content: `window.AIM_LIB_INLINE = {${JSON.stringify(SLUG)}: ${JSON.stringify(rec)}};\n` + fs.readFileSync(path.join(__dirname, "mock_db.js"), "utf8") + `
    (function(){ const subs = new Set();
      const call = op => async (...a) => { const r = await window.__mockdb(op, a); if (r.err) throw {code: r.err, message: r.err}; return r.ok; };
      const remote = {get: call("get"), set: call("set"), update: call("update"), list: call("list"), subs, docs: new Map()};
      setInterval(() => subs.forEach(f => f()), 250);
      window.claude = MockDB.mockClaude(remote, ${JSON.stringify(uid)}); })();` });
  return ctx;
}
async function open(page, base) {
  await page.goto(base + "aim_caddie.html");
  if (!(await page.$("#q"))) await page.click('[data-go="pick"]');
  await page.fill("#q", rec.name);
  await page.waitForSelector(`[data-libplay="${SLUG}"]`, { timeout: 5000 });
  await page.click(`[data-libplay="${SLUG}"]`);
  await page.waitForSelector("#rtBox", { timeout: 15000 });
  await settle(page);
}
/* wait until the re-solve has filled in the confidences (no "Re-solving" line) */
async function settle(page) {
  await page.waitForFunction(() => { const b = document.getElementById("rtBox"); return b && !/Re-solving/.test(b.innerText); }, null, { timeout: 30000 })
    .catch(() => problems.push("re-solve did not finish in 30 s"));
}
const strip = page => page.$eval("#lpStrip", el => el.innerText.replace(/\s+/g, " "));
async function goHole(page, n) { await page.click(`#lpStrip [aria-label="Hole ${n}"]`); await settle(page); }
async function shot(page, name) { await page.evaluate(() => window.scrollTo(0, 0)); await page.screenshot({ path: path.join(shots, name + ".jpg"), type: "jpeg", quality: 60, fullPage: true }); }

(async () => {
  const srv = await serve(), base = `http://127.0.0.1:${srv.address().port}/`;
  const browser = await chromium.launch({ executablePath: fs.existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined });
  let solveMs = [];
  for (const W of [400, 1280]) {
    const server = new M.MockServer();
    const ca = await context(browser, server, "golfer-a", { width: W, height: 900 }), pa = await ca.newPage(); watch(pa, `A${W}`);
    await open(pa, base);
    const tag = `${W}px`;
    // 1. hole 1: plan + questions
    await goHole(pa, 1);
    expect(/Hole 1$/.test(await pa.$eval(".holeno", el => el.textContent)), `${tag}: not on hole 1`);
    expect(await pa.$("#lpPlay"), `${tag}: hole 1 has no plan`);
    expect(await pa.$("#ov image"), `${tag}: hole 1 has no photo`);
    expect(/Is this hole 1\?/.test(await pa.$eval("#rtAsk", el => el.innerText).catch(() => "")), `${tag}: no "Is this hole 1?"`);
    for (const s of ["[data-rtyes]", "[data-rtno]", "[data-rtpick]"]) expect(await pa.$(s), `${tag}: no ${s} button`);
    expect(await pa.$("#rtHole1"), `${tag}: no "Which tee is hole 1?"`);
    await check(pa, `${tag} hole 1`);
    await shot(pa, `${W}_hole1_ask`);
    const s0 = await strip(pa);
    // 2. yes + hole-1 tee
    await pa.click("[data-rtyes]"); await settle(pa);
    expect(/Golfers confirmed hole 1/.test(await pa.$eval("#rtBox", el => el.innerText)), `${tag}: hole 1 not confirmed after Yes`);
    await pa.click('#rtHole1 [data-rth1]'); await settle(pa);
    expect(!(await pa.$("#rtHole1")), `${tag}: "Which tee is hole 1?" still shown after the answer`);
    solveMs.push(await pa.evaluate(s => LPR[s].ms, SLUG));
    // 3. no on hole 2
    await goHole(pa, 2);
    const before = await pa.evaluate(s => { const v = LPR[s].view.find(u => u.no === 2); return v.h.t + "," + v.h.g; }, SLUG);
    await pa.click("[data-rtno]"); await settle(pa);
    const after = await pa.evaluate(s => { const v = LPR[s].view.find(u => u.no === 2); return v ? v.h.t + "," + v.h.g : "none"; }, SLUG);
    expect(before !== after, `${tag}: hole 2 pairing unchanged after No (${before})`);
    const pend = await pa.evaluate(s => LPR[s].view.filter(u => !u.plan).map(u => u.no), SLUG);
    expect(pend.length > 0, `${tag}: no hole without a plan after a wrong "No" (expected one re-paired hole)`);
    if (pend.length) {
      await goHole(pa, pend[0]);
      expect(await pa.$("#rtPending"), `${tag}: hole ${pend[0]} has no plan but no "plan pending" panel`);
      expect(!(await pa.$("#lpPlay")), `${tag}: hole ${pend[0]} shows a club without a plan`);
      expect(await pa.$("#rtMap svg"), `${tag}: no sketch on the pending hole`);
      await check(pa, `${tag} pending hole`);
      await shot(pa, `${W}_plan_pending`);
      await pa.waitForFunction(() => true);
      await new Promise(r => setTimeout(r, 600));
      const req = server.list("requests").filter(r => r.data.schema === "golf_replan/1" && r.data.course === SLUG);
      expect(req.length === 1 && req[0].data.holes.length >= 1, `${tag}: replan request not recorded: ${JSON.stringify(req).slice(0, 200)}`);
    }
    // 4. pick the right green on hole 3
    await goHole(pa, 3);
    if (await pa.$("[data-rtpick]")) {
      await pa.click("[data-rtpick]");
      expect(await pa.$("#rtMap svg"), `${tag}: no sketch for picking a green`);
      const g = await pa.$eval("[data-rtg]", b => +b.dataset.rtg);
      await check(pa, `${tag} pick green`);
      await shot(pa, `${W}_pick_green`);
      await pa.click("[data-rtg]"); await settle(pa);
      const h3 = await pa.evaluate(s => { const v = LPR[s].view.find(u => u.no === 3); return v && v.fixed ? v.h.g : null; }, SLUG);
      expect(h3 === g, `${tag}: hole 3 not confirmed with the picked green ${g} (got ${h3})`);
    } else problems.push(`${tag}: hole 3 has no question`);
    const sA = await strip(pa);
    expect(sA !== s0, `${tag}: strip did not change after the answers`);
    await pa.waitForFunction(() => /✓ Shared/.test((document.getElementById("syncLine") || {}).textContent || ""), null, { timeout: 8000 }).catch(() => problems.push(`${tag}: answers not shared`));
    const doc = server.get("maps/" + SLUG), log = doc && doc.logs && doc.logs["golfer-a"] && doc.logs["golfer-a"].log;
    expect(log && log.length === 4 && log.some(a => a.kind === "first"), `${tag}: shared log ${JSON.stringify(log).slice(0, 300)}`);
    // 5. golfer B starts from A's facts
    const cb = await context(browser, server, "golfer-b", { width: W, height: 900 }), pb = await cb.newPage(); watch(pb, `B${W}`);
    await pb.goto(base + "aim_caddie.html");
    await pb.waitForFunction(() => STORE.mode !== "connecting", null, { timeout: 15000 }).catch(() => {});
    await open(pb, base);
    await pb.waitForFunction(s => LPR[s] && LPR[s].n === 4 && !LPR[s].pending, SLUG, { timeout: 20000 }).catch(() => problems.push(`${tag}: B did not get A's 4 answers`));
    await pb.waitForFunction(a => { const el = document.getElementById("lpStrip"); return el && el.innerText.replace(/\s+/g, " ") === a; }, sA, { timeout: 5000 }).catch(() => {});   // the render after the last step
    expect(await strip(pb) === sA, `${tag}: B's strip differs from A's:\n  A ${sA}\n  B ${await strip(pb)}`);
    await goHole(pb, 1);
    expect(/Golfers confirmed hole 1/.test(await pb.$eval("#rtBox", el => el.innerText)), `${tag}: B does not see hole 1 confirmed`);
    await check(pb, `${tag} B`);
    await shot(pb, `${W}_golfer_B`);
    await ca.close(); await cb.close();
  }
  await browser.close(); srv.close();
  const all = problems.concat(errors);
  const summary = `test_route_ui: ${SLUG} card-blind, 400 + 1280 px; re-solve ${solveMs.join(" / ")} ms; ${all.length ? all.length + " PROBLEMS" : "OK"}`;
  fs.writeFileSync(path.join(shots, "summary.txt"), summary + "\n" + all.join("\n") + "\n");
  console.log(summary); for (const p of all.slice(0, 40)) console.log("  - " + p);
  process.exit(all.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
