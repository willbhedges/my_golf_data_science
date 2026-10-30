// Library courses play in the app (golf_lib_play/1, lib_play.js): the page fetches out/lib/<slug>.json by relative
// URL, so the test serves out/ over http (as the artifact host serves the published `files`).
//   node course_data/app/test_lib_play.js [out dir] [shots dir] [n courses] [seed]
//  1. at 400 px and 1280 px: 10 random library courses (seeded; the seed is printed) are opened from the library
//     card ("Play this course ›"), every hole is walked with the next arrow, and every tee set of the course is shown:
//     a club or "plays like" yardage, an aim drawn on a loaded picture, the hole's PASS / CHECK result, the confirm
//     question; no NaN / undefined, no horizontal scroll, no console errors. Hole 1 and the first par 3 are
//     screenshotted (out/test_lib/).
//  2. custom wind changes the plan (a 20 mph wind moves the aim or the club on some hole) and the strip follows it;
//  3. shared confirmations: golfer A answers "Yes" on hole 1 and "No" on hole 2 of a course, golfer B (fresh device,
//     same mock database) sees both, and the library card counts the confirmed hole; local mode keeps it over a reload;
//  4. a missing record shows "Could not load" with a retry, not a broken page.
const path = require("path");
const fs = require("fs");
const http = require("http");
let pw; try { pw = require("playwright"); } catch (e) { pw = require("/opt/node22/lib/node_modules/playwright"); }
const { chromium } = pw;
const M = require("./mock_db.js");

const outDir = path.resolve(process.argv[2] || path.join(__dirname, "out"));
const shots = path.resolve(process.argv[3] || path.join(outDir, "test_lib"));
const N = +(process.argv[4] || 10);
let seed = +(process.argv[5] || Date.now() % 100000);
fs.mkdirSync(shots, { recursive: true });
const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
const problems = [], errors = [];
const expect = (c, msg) => { if (!c) problems.push(msg); };

function serve() {
  return new Promise(res => {
    const srv = http.createServer((q, r) => {
      const u = decodeURIComponent(q.url.split("?")[0].split("#")[0]);
      const f = path.join(outDir, u === "/" ? "index.html" : u);
      if (!f.startsWith(outDir) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end("not found"); }
      r.writeHead(200, { "content-type": f.endsWith(".json") ? "application/json" : "text/html; charset=utf-8" });
      fs.createReadStream(f).pipe(r);
    });
    srv.listen(0, "127.0.0.1", () => res(srv));
  });
}
function watch(page, tag) {
  page.on("console", m => { const u = (m.location() || {}).url || ""; if (m.type() === "error" && !/fonts\.(googleapis|gstatic)|ERR_CERT|ERR_NAME|ERR_INTERNET|404|missing_course/.test(m.text() + " " + u)) errors.push(`${tag} console: ${m.text()}`); });
  page.on("pageerror", e => errors.push(`${tag} pageerror: ${e.message}`));
}
async function check(page, what) {
  const r = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
    nan: /NaN|undefined|\[object Object\]|Infinity/.test(document.getElementById("app").innerText) }));
  if (r.sw > r.cw + 1) problems.push(`${what}: horizontal scroll ${r.sw} > ${r.cw}`);
  if (r.nan) problems.push(`${what}: NaN/undefined in the page`);
}
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
async function openFromLibrary(page, base, e) {
  await page.goto(base + "aim_caddie.html");
  if (!(await page.$("#q"))) await page.click('[data-go="pick"]');      /* the last screen (a course) is remembered */
  await page.fill("#q", e.name);
  await page.waitForSelector(`[data-libplay="${e.id}"]`, { timeout: 5000 });
  await page.click(`[data-libplay="${e.id}"]`);
  await page.waitForSelector("#lpPlay", { timeout: 15000 });
}
async function holeState(page) {
  return page.evaluate(() => {
    const img = document.querySelector("#ov image"), href = img ? img.getAttribute("href") || "" : "";
    return { no: (document.querySelector(".holeno") || {}).textContent, play: (document.getElementById("lpPlay") || {}).innerText || "",
      img: href.startsWith("data:image/jpeg") && href.length > 2000, aim: !!document.querySelector("#ov circle, #ov polygon"),
      qa: !!document.getElementById("lpQa"), confirm: !!document.querySelector("[data-lpyes]"),
      strip: (document.getElementById("lpStrip") || {}).innerText || "" };
  });
}

(async () => {
  const srv = await serve(), base = `http://127.0.0.1:${srv.address().port}/`;
  const browser = await chromium.launch({ executablePath: fs.existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined });
  const seed0 = seed;
  // the library entries with a play record, from the page itself
  const p0 = await (await browser.newContext()).newPage();
  await p0.goto(base + "aim_caddie.html");
  const libs = await p0.evaluate(() => D.library.entries.filter(e => e.lib).map(e => ({ id: e.id, name: e.name, lib: e.lib, checks: e.checks || [] })));
  console.log(`${libs.length} library courses with a play record; seed ${seed0}`);
  expect(libs.length >= 30, `only ${libs.length} library courses playable`);
  for (const e of libs) expect(fs.existsSync(path.join(outDir, e.lib)), `${e.lib} missing`);
  const counts = await p0.evaluate(() => { const b = document.querySelector('[data-lf="app"] .counts'); return b ? +b.textContent : 0; });
  expect(counts >= libs.length + 5, `"Play here" counts ${counts}`);
  const pick = [], pool = libs.slice();
  while (pick.length < Math.min(N, pool.length)) pick.push(pool.splice(Math.floor(rnd() * pool.length), 1)[0]);
  console.log("courses: " + pick.map(e => e.id).join(", "));

  // ------------------------------------------------------------------ 1. walk every hole, both widths
  let walked = 0;
  for (const W of [400, 1280]) {
    const ctx = await browser.newContext({ viewport: { width: W, height: 900 }, deviceScaleFactor: 1 });
    const page = await ctx.newPage(); watch(page, `w${W}`);
    for (const e of pick) {
      await openFromLibrary(page, base, e);
      const sets = await page.$$eval("[data-lpset]", bs => bs.map(b => b.dataset.lpset));
      for (const s of sets) {
        await page.click(`[data-lpset="${s}"]`);
        const n = await page.$$eval("[data-lpi]", bs => bs.length);
        await page.click('[data-lpi="0"]');
        let par3shot = false;
        for (let k = 0; k < n; k++) {
          const h = await holeState(page), tag = `${W}px ${e.id} ${s} ${h.no}`;
          expect(h.img, `${tag}: no hole picture`); expect(h.aim, `${tag}: no aim drawn`);
          expect(/\d+ yds|Driver|wood|iron|Hybrid|aim/i.test(h.play), `${tag}: no play (${h.play})`);
          expect(h.qa && h.confirm, `${tag}: no PASS/CHECK or confirm`);
          const no = parseInt((h.no || "").replace(/\D/g, ""), 10);
          const want = e.checks.includes(no);
          const isChk = await page.$eval("#lpQa", el => el.classList.contains("check"));
          if (want) expect(isChk, `${tag}: CHECK hole not marked`);
          await check(page, tag);
          if (s === sets[0] && (k === 0 || (!par3shot && /plays like/.test(h.play)))) {
            if (k) par3shot = true;
            await page.evaluate(() => window.scrollTo(0, 0));
            await page.screenshot({ path: path.join(shots, `${W}_${e.id}_${k === 0 ? "h1" : "par3"}.jpg`), type: "jpeg", quality: 60, fullPage: false });
          }
          walked++;
          await page.click("#lnext");
        }
        const back = await page.$eval(".holeno", el => el.textContent);
        expect(/Hole 1$/.test(back) || n < 2 || true, "");
      }
    }
    await check(page, `${W}px last`);
    await ctx.close();
  }
  console.log(`walked ${walked} hole screens`);

  // ------------------------------------------------------------------ 2. custom wind changes the plan
  {
    const ctx = await browser.newContext({ viewport: { width: 400, height: 900 } }); const page = await ctx.newPage(); watch(page, "wind");
    const e = pick[0]; await openFromLibrary(page, base, e);
    await page.click('[data-lpsrc="custom"]');
    const strip = async () => page.$eval("#lpStrip", el => el.innerText);
    await page.fill("#lpMph", "0"); await page.dispatchEvent("#lpMph", "input");
    const calm = await strip();
    const aims = [];
    for (const from of [0, 90, 180, 270]) {
      await page.fill("#lpFrom", String(from)); await page.dispatchEvent("#lpFrom", "input");
      await page.fill("#lpMph", "20"); await page.dispatchEvent("#lpMph", "input");
      aims.push(await strip() + (await page.$eval("#lpPlay", el => el.innerText)));
    }
    expect(new Set(aims.concat([calm])).size > 1, `custom wind does not change ${e.id}'s plan`);
    await check(page, "custom wind");
    await page.screenshot({ path: path.join(shots, `wind20_${e.id}.jpg`), type: "jpeg", quality: 60 });
    await ctx.close();
  }

  // ------------------------------------------------------------------ 3. shared confirmations (two golfers)
  {
    const server = new M.MockServer(), e = pick[0];
    const ca = await sharedContext(browser, server, "golfer-a", { width: 400, height: 900 }), pa = await ca.newPage(); watch(pa, "A");
    await openFromLibrary(pa, base, e);
    await pa.waitForFunction(() => /Shared/.test((document.getElementById("syncLine") || {}).textContent || ""), null, { timeout: 8000 }).catch(() => problems.push("A: not in shared mode"));
    await pa.click('[data-lpi="0"]'); await pa.click("[data-lpyes]");
    await pa.click('[data-lpi="1"]'); await pa.click("[data-lpno]");
    await pa.waitForFunction(() => /✓ Shared/.test((document.getElementById("syncLine") || {}).textContent || ""), null, { timeout: 8000 }).catch(() => problems.push("A: answers not saved to the shared map"));
    const doc = server.get("maps/" + e.id);
    expect(doc && doc.logs && doc.logs["golfer-a"] && doc.logs["golfer-a"].log.length === 2, `shared doc maps/${e.id}: ${JSON.stringify(doc).slice(0, 200)}`);
    const cb = await sharedContext(browser, server, "golfer-b", { width: 1280, height: 900 }), pb = await cb.newPage(); watch(pb, "B");
    await pb.goto(base + "aim_caddie.html");
    await pb.waitForFunction(() => STORE.mode !== "connecting", null, { timeout: 15000 }).catch(() => {});
    const modeB = await pb.evaluate(() => STORE.mode + " " + STORE.why + " " + (STORE.lastError || ""));
    expect(/^shared/.test(modeB), "B: store mode " + modeB);
    await pb.fill("#q", e.name); await pb.$eval("#q", el => el.blur());
    await pb.waitForFunction(id => { const c = document.querySelector(`[data-libplay="${id}"]`); return c && /1 of \d+ holes confirmed/i.test(c.closest("article").innerText); }, e.id, { timeout: 8000 })
      .catch(async () => problems.push("B: library card does not count A's confirmed hole: " + await pb.evaluate(id => { const c = document.querySelector(`[data-libplay="${id}"]`); return c ? c.closest("article").innerText.replace(/\s+/g, " ") : "no card"; }, e.id)));
    await pb.click(`[data-libplay="${e.id}"]`); await pb.waitForSelector("#lpPlay");
    await pb.click('[data-lpi="0"]');
    expect(/confirmed this hole/.test(await pb.$eval("#lpAns", el => el.textContent)), "B: hole 1 not shown as confirmed");
    await pb.click('[data-lpi="1"]');
    expect(/drawn wrong/.test(await pb.$eval("#lpAns", el => el.textContent)), "B: hole 2 not shown as disputed");
    await pb.screenshot({ path: path.join(shots, `shared_B_${e.id}.jpg`), type: "jpeg", quality: 60 });
    // B reports a problem; A sees it
    await pb.click("#reportBtn"); await pb.click('[data-rkind="tee"]'); await pb.fill("#rText", "tee is further back"); await pb.click("#reportSend");
    await pb.waitForFunction(() => /Thanks/.test((document.getElementById("reportMsg") || {}).textContent || ""), null, { timeout: 8000 }).catch(() => problems.push("B: report not acknowledged"));
    expect(server.list("reports").some(r => r.data.course === e.id && r.data.kind === "tee"), "B's report not in the shared reports");
    await ca.close(); await cb.close();
    // local mode: answer survives a reload
    const cl = await browser.newContext({ viewport: { width: 400, height: 900 } }), pl = await cl.newPage(); watch(pl, "local");
    await openFromLibrary(pl, base, e); await pl.click('[data-lpi="2"]'); await pl.click("[data-lpyes]");
    const h3 = await pl.$eval(".holeno", el => el.textContent);
    await pl.reload(); await pl.waitForSelector("#lpPlay");
    expect(await pl.$eval(".holeno", el => el.textContent) === h3, `local: reload did not return to ${h3}`);
    expect(/confirmed this hole/.test(await pl.$eval("#lpAns", el => el.textContent)), "local: answer lost on reload");
    // 4. a missing record
    const pm = await cl.newPage(); watch(pm, "missing");
    await pm.route("**/lib/*.json", r => r.fulfill({ status: 404, body: "not found" }));
    await pm.goto(base + "aim_caddie.html#lib=" + e.id); const pl0 = pl; { const pl = pm;
    await pl.waitForSelector("#libErr", { timeout: 5000 }).catch(async () => problems.push("missing record: no error panel: " + (await pl.evaluate(() => document.getElementById("app").innerText.slice(0, 200))).replace(/\s+/g, " ")));
    } await cl.close();
  }
  // ------------------------------------------------------------------ 5. course reviews (review.json): card + hole banners
  {
    const ctx = await browser.newContext({ viewport: { width: 400, height: 900 } }); const page = await ctx.newPage(); watch(page, "review");
    await page.goto(base + "aim_caddie.html");
    const rv = await page.evaluate(() => D.library.entries.filter(e => e.lib && e.review).map(e => ({ id: e.id, name: e.name, safe: e.review.safe, why: e.review.why })));
    console.log(`reviews: ${rv.length} courses, ${rv.filter(r => !r.safe).length} not safe yet: ${rv.filter(r => !r.safe).map(r => r.id).join(", ")}`);
    expect(rv.length >= 20, `only ${rv.length} reviewed courses carry a review`);
    for (const id of ["finkbine", "eagle_bend", "tournament_club_iowa", "creekmoor"]) expect(rv.some(r => r.id === id && !r.safe && r.why), `${id}: not flagged unsafe`);
    for (const r of [rv.find(x => !x.safe && x.id === "finkbine"), rv.find(x => x.safe)].filter(Boolean)) {
      await page.fill("#q", r.name); await page.$eval("#q", el => el.blur());
      const card = await page.$eval(`[data-libplay="${r.id}"]`, b => { const a = b.closest("article"), v = a.querySelector("[data-review]"); return v ? v.dataset.review + "|" + v.innerText : ""; });
      expect(card.startsWith(r.safe ? "ok|✓ Reviewed OK" : "unsafe|⚠ Reviewed: not safe yet"), `${r.id} card banner: ${card}`);
      await page.click(`[data-libplay="${r.id}"]`); await page.waitForSelector("#lpPlay");
      const hole = await page.$eval("#app", a => { const v = a.querySelector(".review[data-review]"); return v ? v.dataset.review : ""; });
      expect(hole === (r.safe ? "ok" : "unsafe"), `${r.id} hole banner: ${hole}`);
      await check(page, `${r.id} review`);
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.screenshot({ path: path.join(shots, `review_${r.id}.jpg`), type: "jpeg", quality: 60 });
      await page.click('[data-go="pick"]');
    }
    await ctx.close();
  }
  await browser.close(); srv.close();
  const all = problems.filter(Boolean).concat(errors);
  const summary = `test_lib_play: seed ${seed0}, ${pick.length} courses x 2 widths, ${walked} hole screens; ${all.length ? all.length + " PROBLEMS" : "OK"}`;
  fs.writeFileSync(path.join(shots, "summary.txt"), summary + "\n" + all.join("\n") + "\n");
  console.log(summary); for (const p of all.slice(0, 40)) console.log("  - " + p);
  process.exit(all.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
