// v3 checks: the course library, shared confirmations, "report a problem with this hole", the hole screen's
// sticky arrows and "plays like" breakdowns, at 400 px and 1280 px.
//   node course_data/app/test_library.js [out/index.html] [shots dir]
// (playwright from the global node_modules; chromium at /opt/pw-browsers/chromium)
//  1. library: search by name / city / state, status + state filters, every hand-checked course links to its
//     wind page, every app course opens (tees + hole 1 + a par 3), no horizontal scroll / NaN / console errors;
//  2. local mode (no window.claude, as file:// or a saved copy): confirm -> save -> reload -> the confirmed map is
//     shown; report -> listed (hole, course, library) and still there after a reload;
//  3. shared mode (window.claude.use("db") backed by one in-memory database for two browser contexts = two
//     golfers): golfer A confirms holes, golfer B on a fresh device gets A's confirmed map; B reports a problem,
//     A sees it live; a view-only golfer's answers stay on their device and the page says so.
const path = require("path");
const fs = require("fs");
let pw; try { pw = require("playwright"); } catch (e) { pw = require("/opt/node22/lib/node_modules/playwright"); }
const { chromium } = pw;
const M = require("./mock_db.js");

const page_path = path.resolve(process.argv[2] || path.join(__dirname, "out", "index.html"));
const shots = path.resolve(process.argv[3] || path.join(__dirname, "out", "test_v3"));
fs.mkdirSync(shots, { recursive: true });
const url = "file://" + page_path;
const WIND = {
  blue_hills: "https://claude.ai/artifact/HKvWb1BjemS8rfomZTWRY6", eagle_knoll: "https://claude.ai/artifact/QQkFta99SEstd6Dv8wzgf8",
  gateway_national: "https://claude.ai/artifact/PCn2RTEcicJs2LrEC2ZBLb", pine_dunes: "https://claude.ai/artifact/6aCeobGkESNQXPiZefXFVq",
  national_kc: "https://claude.ai/artifact/X9Kn1MzX1CAgST63WpEuMP", hot_springs_arlington: "https://claude.ai/artifact/PzgE7wAjaMXRn8AeewEAeQ",
  spirit_hollow: "https://claude.ai/artifact/NroPJCYdEmhdN1osK23x4E"};

const problems = [], errors = [], log = [];
const say = s => { log.push(s); console.log(s); };
const expect = (c, msg) => { if (!c) problems.push(msg); };

function watch(page, tag) {
  page.on("console", m => { const u = (m.location() || {}).url || ""; if (m.type() === "error" && !/fonts\.(googleapis|gstatic)|ERR_CERT|ERR_NAME|ERR_INTERNET/.test(m.text() + " " + u)) errors.push(`${tag} console: ${m.text()}`); });
  page.on("pageerror", e => errors.push(`${tag} pageerror: ${e.message}`));
}
async function check(page, what) {
  const r = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
    nan: /NaN|undefined|\[object Object\]/.test(document.getElementById("app").innerText) }));
  if (r.sw > r.cw + 1) problems.push(`${what}: horizontal scroll ${r.sw} > ${r.cw}`);
  if (r.nan) problems.push(`${what}: NaN/undefined in the page`);
}
/* every "plays like" breakdown adds up: base + parts = total */
async function checkAdj(page, what) {
  const rows = await page.$$eval("[data-adj]", els => els.map(e => [...e.querySelectorAll("span")].map(s => s.textContent)));
  for (const r of rows) {
    const n = t => { const m = /^([=+−±]?)\s*(\d+)/.exec(t.replace("= ", "=")); if (!m) return NaN; return (m[1] === "−" ? -1 : 1) * +m[2]; };
    const base = n(r[0]), total = n(r[r.length - 1]), parts = r.slice(1, -1).map(n);
    if (!(base + parts.reduce((a, b) => a + b, 0) === total)) problems.push(`${what}: breakdown does not add up: ${r.join(" ")}`);
  }
  return rows.length;
}
async function pinned(page) { return page.$$eval("#hstrip .hchip.ok", e => e.length); }
async function answer(page, k, how) {                   /* answer up to k questions on the confirm screen */
  let n = 0;
  for (let i = 0; i < k; i++) {
    if (await page.locator("#cDone [data-cmore]").count()) await page.click("#cDone [data-cmore]");   /* all placed: keep checking */
    const yes = page.locator("#qYes");
    if (await yes.count()) { await (how && how(i) === "no" ? page.click("#qNo") : yes.click()); await page.waitForTimeout(60); n++; continue; }
    /* a 2-tap locate: tap the hole's drawn tee, then its green (as a golfer would on the aerial map) */
    let done = true;
    for (const which of ["tee_ll", "green_ll"]) {
      const p = await page.evaluate(w => {
        const C = cur(), S = sess(C), q = nextQuestion(C, S); if (!q || q.kind !== "locate") return null;
        const H = S.holes[q.ref], svg = document.getElementById("cmap"); if (!H[w]) return null;
        svg.scrollIntoView({block: "center"});
        const m = svg.getScreenCTM(), px = ovPx(C, H[w]), sp = svg.createSVGPoint(); sp.x = px[0]; sp.y = px[1];
        const r = sp.matrixTransform(m); return [r.x, r.y];
      }, which);
      if (!p) { done = false; break; }
      await page.mouse.click(p[0], p[1]); await page.waitForTimeout(80);
    }
    if (!done) break;
    n++;
  }
  return n;
}
/* window.claude for a viewer whose db lives in node (one MockServer per test = one artifact database) */
async function sharedContext(browser, server, uid, viewport) {
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1 });
  await ctx.exposeFunction("__mockdb", async (op, args) => { try { return { ok: await server[op](...args) }; } catch (e) { return { err: e.code || String(e) }; } });
  await ctx.addInitScript({ content: fs.readFileSync(path.join(__dirname, "mock_db.js"), "utf8") + `
    (function(){ const subs = new Set();
      const call = op => async (...a) => { const r = await window.__mockdb(op, a); if (r.err) throw {code: r.err, message: r.err}; return r.ok; };
      const remote = {get: call("get"), set: call("set"), update: call("update"), list: call("list"), subs, docs: new Map()};
      setInterval(() => subs.forEach(f => f()), 250);
      window.claude = MockDB.mockClaude(remote, ${JSON.stringify(uid)}); })();` });
  return ctx;
}

(async () => {
  const browser = await chromium.launch({ executablePath: fs.existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined });
  // ------------------------------------------------------------------ 1. library + every course, both widths
  for (const W of [400, 1280]) {
    const ctx = await browser.newContext({ viewport: { width: W, height: 900 }, deviceScaleFactor: 1 });
    const page = await ctx.newPage(); watch(page, `w${W}`);
    await page.goto(url); await page.evaluate(() => localStorage.clear()); await page.goto(url);
    const info = await page.evaluate(() => ({ n: D.library.entries.length, app: D.courses.map(c => ({ id: c.id, holes: c.holes.map(h => h.no), par3: (c.holes.find(h => h.par === 3) || {}).no })) }));
    await page.screenshot({ path: path.join(shots, `lib_${W}.png`) }); await check(page, `library ${W}`);
    const cnt = async () => page.$$eval("#list [data-lib]", e => e.length);
    const total = await page.evaluate(() => +document.querySelector('[data-lf="all"] .counts').textContent);
    expect(total === info.n, `library ${W}: All count ${total} != ${info.n} entries`);
    // search by city, by name, by state
    await page.fill("#q", "ames"); await page.waitForTimeout(40);
    const ames = await page.$$eval("#list [data-lib] .name", e => e.map(x => x.textContent));
    expect(ames.some(x => /Coldwater/.test(x)) && ames.some(x => /Veenker/.test(x)), `search "ames" (city): ${ames.join(", ")}`);
    await page.screenshot({ path: path.join(shots, `lib_search_ames_${W}.png`) }); await check(page, `search ${W}`);
    await page.fill("#q", "hot springs"); await page.waitForTimeout(40);
    const hs = await page.$$eval("#list [data-lib] .name", e => e.map(x => x.textContent));
    expect(hs.some(x => /Arlington/.test(x)), `search "hot springs": ${hs.join(", ")}`);
    await page.fill("#q", "tx"); await page.waitForTimeout(40);
    const tx = await page.$$eval("#list [data-lib] .name", e => e.map(x => x.textContent));
    expect(tx.some(x => /Pine Dunes/.test(x)), `search "tx" (state): ${tx.join(", ")}`);
    await page.fill("#q", ""); await page.waitForTimeout(40);
    // status filters
    const byStatus = {};
    for (const k of ["app", "hand", "auto", "confirm", "none"]) {
      await page.click(`[data-lf="${k}"]`);
      byStatus[k] = await page.evaluate(() => +document.querySelector('[aria-pressed="true"][data-lf] .counts').textContent);
      const st = await page.$$eval("#list [data-lib]", e => e.map(x => x.dataset.status));
      if (k !== "app") expect(st.every(s => s === k), `filter ${k}: got statuses ${[...new Set(st)].join(",")}`);
      if (k === "hand") {
        const links = await page.$$eval("#list a[href]", e => e.map(a => [a.dataset.link, a.getAttribute("href"), a.target]));
        for (const [id, u] of Object.entries(WIND)) expect(links.some(l => l[0] === id && l[1] === u && l[2] === "_blank"), `hand-checked ${id}: wind page link ${u} missing`);
        await page.screenshot({ path: path.join(shots, `lib_hand_${W}.png`), fullPage: true }); await check(page, `hand ${W}`);
      }
    }
    say(`w${W}: library ${info.n} courses; filter counts ${JSON.stringify(byStatus)}`);
    expect(byStatus.hand === 7, `hand-checked count ${byStatus.hand} (want 7: Spirit Hollow + 6 tournament courses)`);
    await page.click('[data-lf="all"]');
    await page.selectOption("#fState", "MO"); await page.waitForTimeout(40);
    const mo = await page.$$eval("#list [data-lib] .sub", e => e.map(x => x.textContent));
    expect(mo.length && mo.every(x => /, MO/.test(x) || !/, [A-Z]{2}/.test(x)), `state filter MO`);
    await page.selectOption("#fState", "all");
    if (await page.locator("[data-libmore]").count()) { const a = await cnt(); await page.click("[data-libmore]"); expect(await cnt() > a, "show more"); }
    // every app course: tees, hole 1, a par 3, sticky arrows
    for (const C of info.app) {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.click('[data-go="pick"]').catch(() => {});
      await page.click(`[data-course="${C.id}"]`);
      await check(page, `${C.id} tees ${W}`);
      await page.screenshot({ path: path.join(shots, `tees_${C.id}_${W}.png`), fullPage: true });
      await page.click('[data-go="hole"]');
      await check(page, `${C.id} hole 1 ${W}`);
      let nAdj = await checkAdj(page, `${C.id} hole 1 ${W}`);
      await page.screenshot({ path: path.join(shots, `hole1_${C.id}_${W}.png`) });
      await page.evaluate(() => window.scrollTo(0, 700)); await page.waitForTimeout(30);
      const top = await page.evaluate(() => { const r = document.getElementById("next").getBoundingClientRect(); return [r.top, r.height]; });
      expect(top[0] >= 0 && top[0] < 140 && top[1] >= 52, `${C.id} ${W}: hole arrows not at the top after scrolling (${top})`);
      await page.click("#next"); await check(page, `${C.id} next ${W}`);
      const no = await page.evaluate(() => document.querySelector(".holeno").textContent);
      expect(no === "Hole " + C.holes[1], `${C.id} ${W}: next went to ${no}`);
      if (C.par3) { await page.click(`.chip[data-i="${C.holes.indexOf(C.par3)}"]`); await check(page, `${C.id} par 3 ${W}`);
        nAdj += await checkAdj(page, `${C.id} par 3 ${W}`);
        const has = await page.evaluate(() => /plays like/.test(document.querySelector("[data-adj]").textContent));
        expect(has, `${C.id} ${W}: par 3 has no plays-like breakdown`);
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.screenshot({ path: path.join(shots, `par3_${C.id}_${W}.png`) }); }
      if (await page.locator('[data-view="appr"]').count()) { await page.click('[data-view="appr"]'); nAdj += await checkAdj(page, `${C.id} approach ${W}`); await page.click('[data-view="land"]'); }
      expect(nAdj >= 2, `${C.id} ${W}: ${nAdj} plays-like breakdowns`);
      const wind = await page.$$eval(".cond .windico svg", e => e.length);
      expect(wind >= 1, `${C.id} ${W}: no wind arrow next to the conditions`);
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.click('[data-go="pick"]');
    }
    await ctx.close();
  }

  // ------------------------------------------------------------------ 2. local mode: confirm -> save -> reload; report
  {
    const ctx = await browser.newContext({ viewport: { width: 400, height: 900 }, deviceScaleFactor: 1 });
    const page = await ctx.newPage(); watch(page, "local");
    await page.goto(url); await page.evaluate(() => localStorage.clear()); await page.goto(url);
    await page.click('[data-course="coldwater"]'); await page.click("#goConfirm");
    const n0 = await pinned(page);
    const taps = await answer(page, 4);
    const n1 = await pinned(page);
    const sync = await page.textContent("#syncLine");
    await page.screenshot({ path: path.join(shots, "local_confirm_answered.png"), fullPage: true });
    expect(n1 > n0, `local: answering ${taps} questions pinned no hole (${n0} -> ${n1})`);
    expect(/this device/.test(sync), `local: sync line says "${sync}"`);
    const ref = await page.evaluate(() => [...document.querySelectorAll("#hstrip .hchip.ok b")].map(b => b.textContent).join(","));
    await page.reload(); await page.waitForTimeout(200);
    await page.click('[data-go="pick"]').catch(() => {});
    await page.click('[data-course="coldwater"]'); await page.click("#goConfirm");
    const ref2 = await page.evaluate(() => [...document.querySelectorAll("#hstrip .hchip.ok b")].map(b => b.textContent).join(","));
    say(`local: ${taps} answers pinned holes [${ref}]; after reload [${ref2}]`);
    expect(ref === ref2 && ref.length, `local: confirmed map after reload [${ref2}] != before [${ref}]`);
    await page.screenshot({ path: path.join(shots, "local_confirm_after_reload.png"), fullPage: true });
    // undo my last answer
    await page.click("[data-cundo]"); const n2 = await pinned(page);
    expect(n2 <= n1, "local: undo"); await page.reload();
    // report a problem on hole 4
    await page.goto(url + "#c=coldwater&t=Blue&h=4"); await page.waitForTimeout(100);
    await page.click("#reportBtn"); await page.click('[data-rkind="green"]'); await page.fill("#rText", "Green is 20 yds left of the drawn one");
    await page.screenshot({ path: path.join(shots, "local_report_form.png"), fullPage: true });
    await page.click("#reportSend"); await page.waitForTimeout(100);
    const listed = await page.$$eval("#holeReports li", e => e.map(x => x.textContent));
    expect(listed.length === 1 && /Green is 20 yds/.test(listed[0]), `local report: hole list ${JSON.stringify(listed)}`);
    await page.reload(); await page.waitForTimeout(100);
    const listed2 = await page.$$eval("#holeReports li", e => e.map(x => x.textContent));
    expect(listed2.length === 1, `local report after reload: ${JSON.stringify(listed2)}`);
    await page.screenshot({ path: path.join(shots, "local_report_listed.png"), fullPage: true });
    await page.click('[data-go="tees"]');
    const cr = await page.$$eval("#courseReports li", e => e.map(x => x.textContent));
    expect(cr.length === 1 && /Hole 4/.test(cr[0]), `local report: course list ${JSON.stringify(cr)}`);
    await page.click('[data-go="pick"]');
    const badge = await page.textContent('[data-lib] .badge.check').catch(() => "");
    expect(/1 problem reported/.test(badge), `local report: library badge "${badge}"`);
    say(`local: report listed on the hole (${listed2.length}), the course (${cr.length}) and the library card ("${badge}")`);
    await ctx.close();
  }

  // ------------------------------------------------------------------ 3. shared mode: two golfers, one database
  {
    const server = new M.MockServer();
    const vp = { width: 400, height: 900 };
    const ctxA = await sharedContext(browser, server, "golfer-a", vp), A = await ctxA.newPage(); watch(A, "shared A");
    await A.goto(url); await A.waitForTimeout(300);
    const modeA = await A.evaluate(() => STORE.mode);
    expect(modeA === "shared", `shared A: store mode ${modeA}`);
    await A.click('[data-course="coldwater"]'); await A.click("#goConfirm");
    const tA = await answer(A, 6, i => (i === 2 ? "no" : "yes"));
    await A.waitForTimeout(400);
    const pinsA = await A.evaluate(() => [...document.querySelectorAll("#hstrip .hchip.ok b")].map(b => b.textContent).join(","));
    const syncA = await A.textContent("#syncLine");
    await A.screenshot({ path: path.join(shots, "shared_A_confirmed.png"), fullPage: true });
    const doc = server.get("maps/coldwater");
    expect(doc && doc.logs && doc.logs["golfer-a"] && doc.logs["golfer-a"].log.length === tA, `shared: A's ${tA} answers not in the database (${JSON.stringify(doc && doc.logs && Object.keys(doc.logs))})`);
    expect(/Shared/.test(syncA), `shared A: sync line "${syncA}"`);
    // golfer B: a fresh device
    const ctxB = await sharedContext(browser, server, "golfer-b", { width: 1280, height: 900 }), B = await ctxB.newPage(); watch(B, "shared B");
    await B.goto(url); await B.waitForTimeout(500);
    await B.screenshot({ path: path.join(shots, "shared_B_library.png") });
    const card = await B.textContent('[data-lib] .badge.shared').catch(() => "");
    expect(/confirmed by 1 golfer/.test(card), `shared B: library card badge "${card}"`);
    await B.click('[data-course="coldwater"]');
    const panel = await B.textContent("#mapPanel");
    expect(/other golfer/.test(panel), `shared B: tee screen does not mention A's answers: ${panel.slice(0, 200)}`);
    await B.click("#goConfirm");
    const pinsB = await B.evaluate(() => [...document.querySelectorAll("#hstrip .hchip.ok b")].map(b => b.textContent).join(","));
    say(`shared: A answered ${tA} (pinned [${pinsA}]); B on a fresh device sees pinned [${pinsB}]`);
    expect(pinsA === pinsB && pinsA.length, `shared: B's confirmed map [${pinsB}] != A's [${pinsA}]`);
    await B.screenshot({ path: path.join(shots, "shared_B_gets_map.png"), fullPage: true });
    // B adds answers; A (live listener) gets them without a reload
    const tB = await answer(B, 2);
    await B.waitForTimeout(400);
    const pinsB2 = await B.evaluate(() => [...document.querySelectorAll("#hstrip .hchip.ok b")].map(b => b.textContent).join(","));
    await A.waitForTimeout(900);
    const pinsA2 = await A.evaluate(() => [...document.querySelectorAll("#hstrip .hchip.ok b")].map(b => b.textContent).join(","));
    say(`shared: B answered ${tB} more -> B [${pinsB2}], A live [${pinsA2}]`);
    expect(pinsA2 === pinsB2, `shared: A did not get B's answers live (${pinsA2} vs ${pinsB2})`);
    const d2 = server.get("maps/coldwater");
    expect(Object.keys(d2.logs).sort().join() === "golfer-a,golfer-b", `shared: database logs ${Object.keys(d2.logs)}`);
    // B reports a problem on hole 3; A sees it
    await B.goto(url + "#c=coldwater&t=Blue&h=3"); await B.reload(); await B.waitForTimeout(400);
    await B.click("#reportBtn"); await B.click('[data-rkind="hazard"]'); await B.fill("#rText", "Pond short right is not drawn");
    await B.click("#reportSend"); await B.waitForTimeout(300);
    const msg = await B.textContent("#reportMsg");
    expect(/for everyone/.test(msg), `shared report: "${msg}"`);
    await B.screenshot({ path: path.join(shots, "shared_B_reported.png"), fullPage: true });
    await A.goto(url + "#c=coldwater&t=Blue"); await A.reload(); await A.waitForTimeout(600);
    const crA = await A.$$eval("#courseReports li", e => e.map(x => x.textContent));
    expect(crA.length === 1 && /Pond short right/.test(crA[0]), `shared report: A's course list ${JSON.stringify(crA)}`);
    await A.screenshot({ path: path.join(shots, "shared_A_sees_report.png"), fullPage: true });
    say(`shared: B's report listed for A: ${JSON.stringify(crA)}`);
    // a view-only golfer: their answers stay on their device
    const vserver = new M.MockServer(); for (const [k, v] of server.docs) vserver.docs.set(k, v); vserver.failWrites = true;
    const ctxV = await sharedContext(browser, vserver, "golfer-v", vp), V = await ctxV.newPage(); watch(V, "view-only");
    await V.goto(url + "#c=coldwater&t=Blue"); await V.reload(); await V.waitForTimeout(400);
    await V.click("#goConfirm");
    const pv0 = await pinned(V);
    expect(pv0 >= pinsB2.split(",").length, `view-only: does not see the shared map (${pv0})`);
    await answer(V, 1); await V.waitForTimeout(300);
    const sv = await V.textContent("#syncLine");
    expect(/this device only/.test(sv), `view-only: sync line "${sv}"`);
    say(`view-only: sees ${pv0} confirmed holes; own answer -> "${sv.replace(/\s+/g, " ").slice(0, 90)}"`);
    await V.screenshot({ path: path.join(shots, "viewonly_saved_locally.png"), fullPage: true });
    await ctxA.close(); await ctxB.close(); await ctxV.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(shots, "summary.txt"), log.concat([`errors ${errors.length}`, ...errors, `problems ${problems.length}`, ...problems]).join("\n") + "\n");
  console.log(`console/page errors: ${errors.length}`); errors.slice(0, 20).forEach(e => console.log("  " + e));
  console.log(`problems: ${problems.length}`); problems.slice(0, 30).forEach(e => console.log("  " + e));
  process.exit(errors.length || problems.length ? 1 : 0);
})();
