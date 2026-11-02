// Native-grass check cards on a library course (build_library_play.native_cards -> lib_play.js), playwright.
//   node course_data/app/test_lib_native.js [out dir] [shots dir] [slug]
// The record out/lib/<slug>.json (default eagle_bend) is used as built when it has `checks`; otherwise the checks of
// fixtures/lib_native/<slug>.json (a local course_page.py native run) are laid on it. Inlined via AIM_LIB_INLINE, no
// shared db (this-device answers). At 400 px and 1280 px:
//  1. every hole with a card shows "Native grass along this hole's landing area?" with Left / Right / Both / None and
//     each answer's outcome; holes without a card show none; no NaN, no horizontal scroll, no console errors;
//  2. on a card's set, an answer whose outcome re-plans the hole changes the club or the aim shown (and the strip),
//     says "Re-planned from your answer" and draws the band on the photo; a "No change" answer keeps the plan;
//     tapping the same answer again clears it and the plan comes back;
//  3. the answer survives a reload (localStorage); on another tee set the card says it was computed for its set.
const path = require("path"), fs = require("fs"), http = require("http");
let pw; try { pw = require("playwright"); } catch (e) { pw = require("/opt/node22/lib/node_modules/playwright"); }
const { chromium } = pw;
const outDir = path.resolve(process.argv[2] || path.join(__dirname, "out"));
const shots = path.resolve(process.argv[3] || path.join(outDir, "test_lib_native"));
const SLUG = process.argv[4] || "eagle_bend";
fs.mkdirSync(shots, { recursive: true });
const rec = JSON.parse(fs.readFileSync(path.join(outDir, "lib", SLUG + ".json")));
if (!(rec.checks || []).length) rec.checks = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures", "lib_native", SLUG + ".json"))).checks;
const cards = rec.checks.filter(c => c.type === "native");
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
async function open(page, base) {
  await page.goto(base + "aim_caddie.html");
  if (!(await page.$("#q"))) await page.click('[data-go="pick"]');
  await page.fill("#q", rec.name);
  await page.waitForSelector(`[data-libplay="${SLUG}"]`, { timeout: 5000 });
  await page.click(`[data-libplay="${SLUG}"]`);
  await page.waitForSelector("#lpPlay", { timeout: 20000 });
}
const holeNo = page => page.$eval(".holeno", el => +el.textContent.replace(/\D/g, ""));
async function goHole(page, n) {
  for (let k = 0; k < 40 && (await holeNo(page)) !== n; k++) { await page.click("#lnext"); await page.waitForSelector("#lpPlay", { timeout: 5000 }).catch(() => {}); }
  expect((await holeNo(page)) === n, `could not reach hole ${n}`);
}
const playTxt = page => page.$eval("#lpPlay", el => el.innerText.replace(/\s+/g, " ").trim());
const chip = (page, n) => page.$eval(`#lpStrip [aria-label="Hole ${n}"]`, el => el.innerText.replace(/\s+/g, " ").trim()).catch(() => "");
async function setPick(page, name) { const b = await page.$(`#lpSets [data-lpset="${name}"]`); if (b) { await b.click(); await page.waitForSelector("#lpPlay"); } }
async function shot(page, name) { await page.screenshot({ path: path.join(shots, name + ".jpg"), type: "jpeg", quality: 60, fullPage: true }); }

(async () => {
  expect(cards.length > 0 && cards.length <= 4, `${SLUG}: ${cards.length} native cards (want 1-4)`);
  const srv = await serve(), base = `http://127.0.0.1:${srv.address().port}/`;
  const browser = await chromium.launch({ executablePath: fs.existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined });
  const cardHoles = new Set(cards.map(c => String(c.hole)));
  let replans = 0;
  for (const W of [400, 1280]) {
    const ctx = await browser.newContext({ viewport: { width: W, height: 900 }, deviceScaleFactor: 1 });
    await ctx.addInitScript({ content: `window.AIM_LIB_INLINE = {${JSON.stringify(SLUG)}: ${JSON.stringify(rec)}};` });
    const page = await ctx.newPage(); watch(page, `${W}`);
    const tag = `${W}px`;
    await open(page, base);
    // 1. every hole: cards only where expected
    const n = rec.holes.length;
    for (let k = 0; k < n; k++) {
      const no = await holeNo(page), H = rec.holes.find(h => h.no === no);
      const has = !!(await page.$("#lpChecks"));
      expect(has === cardHoles.has(H ? H.ref : "?"), `${tag} hole ${no}: native card shown ${has}, expected ${cardHoles.has(H ? H.ref : "?")}`);
      await check(page, `${tag} hole ${no}`);
      await page.click("#lnext"); await page.waitForSelector("#lpPlay", { timeout: 5000 }).catch(() => {});
    }
    for (const c of cards) {
      const H = rec.holes.find(h => h.ref === String(c.hole)), no = H.no;
      await setPick(page, c.tee_set);
      await goHole(page, no);
      const q = await page.$eval(`#chk-${c.id}`, el => el.innerText).catch(() => "");
      expect(q.includes("Native grass along this hole's landing area?"), `${tag} hole ${no}: no native question`);
      const labels = await page.$$eval(`#chk-${c.id} [data-ans]`, bs => bs.map(b => b.textContent.trim()));
      expect(labels.join(",") === "Left,Right,Both,None", `${tag} hole ${no}: answers ${labels}`);
      for (const o of c.options) expect(q.includes(o.text), `${tag} hole ${no}: outcome of ${o.label} not shown ("${o.text}")`);
      const p0 = await playTxt(page), c0 = await chip(page, no);
      // 2. each answer
      for (const o of c.options) {
        await page.click(`#chk-${c.id} [data-ans="${o.answer}"]`); await page.waitForSelector("#lpPlay");
        const p1 = await playTxt(page), re = !!(await page.$("#lpReplan")), band = (await page.$$("#ov [data-native]")).length;
        const said = await page.$eval(`#chk-${c.id} .out`, el => el.innerText).catch(() => "");
        expect(said.includes(`Your answer: ${o.label}.`), `${tag} hole ${no} ${o.label}: card does not show the answer`);
        if (o.outcome) {
          replans++;
          expect(re, `${tag} hole ${no} ${o.label}: no "Re-planned from your answer"`);
          expect(p1.includes(o.outcome.pick) || p1 !== p0, `${tag} hole ${no} ${o.label}: plan unchanged (${p1})`);
          expect(p1.startsWith(o.outcome.pick) || o.outcome.wind.some(e => rec.clubs[e[0]] !== o.outcome.pick), `${tag} hole ${no} ${o.label}: club ${p1} not ${o.outcome.pick}`);
          if (o.outcome.club_changed) expect((await chip(page, no)) !== c0, `${tag} hole ${no} ${o.label}: strip chip unchanged`);
        } else {
          expect(!re && p1 === p0, `${tag} hole ${no} ${o.label}: "No change" answer changed the plan (${p0} -> ${p1})`);
        }
        const wantBand = o.answer !== "none" && c.band && (c.band[o.answer === "both" ? "L" : o.answer] || []).length;
        expect(!wantBand || band > 0, `${tag} hole ${no} ${o.label}: no band drawn`);
        expect(o.answer !== "none" || band === 0, `${tag} hole ${no} None: band drawn`);
        await check(page, `${tag} hole ${no} ${o.label}`);
        if (o.outcome && o.answer === "both") await shot(page, `${W}_hole${no}_both`);
      }
      // tap again = clear
      const last = c.options[c.options.length - 1];
      await page.click(`#chk-${c.id} [data-ans="${last.answer}"]`); await page.waitForSelector("#lpPlay");
      expect((await playTxt(page)) === p0 && !(await page.$("#lpReplan")), `${tag} hole ${no}: clearing the answer did not restore the plan`);
    }
    // 3. reload keeps an answer; another set says computed for the card's set
    const c = cards.find(x => x.options.some(o => o.outcome)) || cards[0], o = c.options.find(x => x.outcome) || c.options[0];
    const H = rec.holes.find(h => h.ref === String(c.hole));
    await setPick(page, c.tee_set); await goHole(page, H.no);
    await page.click(`#chk-${c.id} [data-ans="${o.answer}"]`); await page.waitForSelector("#lpPlay");
    const pa = await playTxt(page);
    await page.reload(); await page.waitForSelector("#app");
    if (!(await page.$("#lpPlay"))) await open(page, base);
    await setPick(page, c.tee_set); await goHole(page, H.no);
    expect((await playTxt(page)) === pa, `${tag}: answer not kept over a reload`);
    const other = rec.sets.map(s => s.name).find(s => s !== c.tee_set);
    if (other && o.outcome) {
      await setPick(page, other);
      const t = await page.$eval(`#chk-${c.id} .out`, el => el.innerText).catch(() => "");
      expect(t.includes(`Computed for the ${c.tee_set} tees`), `${tag}: on ${other} the card does not say it is for ${c.tee_set}`);
      expect(!(await page.$("#lpReplan")), `${tag}: ${other} tees re-planned from a ${c.tee_set} answer`);
    }
    await ctx.close();
  }
  expect(replans > 0, "no answer re-planned any hole");
  await browser.close(); srv.close();
  const all = problems.concat(errors);
  console.log(`${SLUG}: ${cards.length} native cards (holes ${cards.map(c => c.hole).join(", ")}), ${replans} re-planning answers checked at 400 + 1280 px`);
  if (all.length) { console.log("FAIL\n" + all.slice(0, 40).join("\n")); process.exit(1); }
  console.log("OK");
})().catch(e => { console.error(e); process.exit(1); });
