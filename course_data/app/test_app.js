// Headless check of the app prototype at phone width (420 px).
//   NODE_PATH=$(npm root -g) PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node course_data/app/test_app.js [out/index.html] [shots dir]
// Walks every course, tee set and hole; taps every club on tee shots; switches tees, views, wind source and
// answers a check; fails on any console error, page error, horizontal scroll or NaN in the page.
// Writes per-hole screenshots of the map + a contact sheet per course (contact_<course>.png).
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const page_path = path.resolve(process.argv[2] || path.join(__dirname, "out", "index.html"));
const shots = path.resolve(process.argv[3] || path.join(__dirname, "out", "test"));
fs.mkdirSync(shots, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 420, height: 900 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const errors = [];
  page.on("console", m => { const u = (m.location() || {}).url || ""; if (m.type() === "error" && !/fonts\.(googleapis|gstatic)/.test(m.text() + " " + u)) errors.push("console: " + m.text() + " " + u); });
  page.on("pageerror", e => errors.push("pageerror: " + e.message));
  page.on("requestfailed", r => { if (!/fonts\.(googleapis|gstatic)/.test(r.url())) errors.push("request failed: " + r.url()); });
  const url = "file://" + page_path;
  await page.goto(url);
  await page.evaluate(() => localStorage.clear());
  await page.goto(url);
  const D = await page.evaluate(() => ({ courses: D.courses.map(c => ({ id: c.id, sets: c.tee_sets.filter(t => t.computed !== "missing").map(t => t.name), holes: c.holes.map(h => h.no), checks: c.checks.length })) }));
  const problems = [];
  const check = async (what) => {
    const r = await page.evaluate(() => ({
      sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
      nan: /NaN|undefined/.test(document.getElementById("app").innerText),
      svgnan: /NaN|undefined/.test(((document.getElementById("ov") || {}).innerHTML || "").replace(/href="[^"]*"/g, "")),
    }));
    if (r.sw > r.cw + 1) problems.push(`${what}: horizontal scroll ${r.sw} > ${r.cw}`);
    if (r.nan || r.svgnan) problems.push(`${what}: NaN/undefined in the page`);
  };
  // 1. course list + search
  await page.screenshot({ path: path.join(shots, "00_pick.png"), fullPage: true });
  await check("pick");
  await page.fill("#q", "ames");
  await page.waitForTimeout(50);
  const soon = await page.locator(".soon").count();
  await page.screenshot({ path: path.join(shots, "01_search.png"), fullPage: true });
  await check("search");
  await page.fill("#q", "");
  let nHoles = 0, nClubs = 0;
  const summary = [];
  for (const C of D.courses) {
    await page.click(`[data-course="${C.id}"]`);
    await page.screenshot({ path: path.join(shots, `10_tees_${C.id}.png`), fullPage: true });
    await check(`${C.id} tees`);
    if (C.checks) {                                         // answer the first red check (and undo it)
      const b = page.locator(".chk.red [data-ans]").nth(1);
      if (await b.count()) { await b.click(); await check(`${C.id} answer`); await page.screenshot({ path: path.join(shots, `11_answered_${C.id}.png`), fullPage: true }); }
    }
    for (const S of C.sets) {
      await page.click(`[data-set="${S}"]`);
      await page.click(`[data-go="hole"]`);
      for (let i = 0; i < C.holes.length; i++) {
        await page.click(`.chip[data-i="${i}"]`);
        const tag = `${C.id}_${S}_${String(C.holes[i]).padStart(2, "0")}`;
        await check(tag);
        const info = await page.evaluate(() => {
          const play = document.querySelector(".play"); const svg = document.getElementById("ov");
          return { play: play && play.textContent, clubs: [...document.querySelectorAll("tr[data-club]")].map(t => t.dataset.club),
                   badge: (document.querySelector(".holehead .badge") || {}).textContent, vb: svg.getAttribute("viewBox") };
        });
        summary.push(`${tag}: ${info.play} [${info.badge}]`);
        nHoles++;
        if (S === C.sets[0]) {
          await page.locator(".mapbox").screenshot({ path: path.join(shots, `h_${tag}.png`) });
          for (const club of info.clubs) {                   // club override: every club draws its own aim + pattern
            await page.click(`tr[data-club="${club}"]`);
            await check(`${tag} ${club}`);
            nClubs++;
          }
          if (info.clubs.length) {
            await page.click(`tr[data-club="${info.clubs[1]}"]`);
            await page.locator(".mapbox").screenshot({ path: path.join(shots, `hc_${tag}.png`) });
            await page.click(`tr[data-club="${info.clubs[0]}"]`);   // tap the best club (first row) to go back
            await page.click(`[data-view="hole"]`);
            await check(`${tag} whole`);
            await page.locator(".mapbox").screenshot({ path: path.join(shots, `hw_${tag}.png`) });
            await page.click(`[data-view="land"]`);
          }
        }
      }
      // the tee move slider, if this course has offset grids
      if (await page.locator("#adj").count()) {
        const mx = await page.locator("#adj").getAttribute("max"); await page.locator("#adj").fill(mx); await check(`${C.id} adj`);
        await page.locator("#adj").fill("0");
      }
      await page.screenshot({ path: path.join(shots, `20_hole_${C.id}_${S}.png`), fullPage: true });
      await page.click(`[data-go="tees"]`);
    }
    // custom wind: open the panel and move speed + temperature
    await page.click(`[data-go="hole"]`);
    if (!(await page.evaluate(() => document.getElementById("windPanel").open))) await page.click("#windPanel summary");
    await page.locator("#mph").fill("20");
    await page.locator("#temp").fill("45");
    await check(`${C.id} custom wind`);
    await page.screenshot({ path: path.join(shots, `30_custom_${C.id}.png`), fullPage: true });
    await page.click(`[data-src]`);                           // back to the first forecast day
    await page.click(`[data-go="pick"]`);
  }
  // contact sheets: every hole map of each course's first tee set, 6 across
  for (const C of D.courses) {
    const S = C.sets[0];
    const files = C.holes.map(n => `h_${C.id}_${S}_${String(n).padStart(2, "0")}.png`).filter(f => fs.existsSync(path.join(shots, f)));
    const html = `<body style="margin:0;background:#111;display:grid;grid-template-columns:repeat(6,260px);gap:6px;padding:6px;font:14px sans-serif;color:#fff">` +
      files.map(f => `<div><div>${f.replace(/^h_|\.png$/g, "")}</div><img src="data:image/png;base64,${fs.readFileSync(path.join(shots, f)).toString("base64")}" style="width:260px;max-height:420px;object-fit:contain;background:#000"></div>`).join("") + `</body>`;
    const p2 = await ctx.newPage();
    await p2.setViewportSize({ width: 6 * 266 + 6, height: 900 });
    await p2.setContent(html, { waitUntil: "load" });
    await p2.screenshot({ path: path.join(shots, `contact_${C.id}.png`), fullPage: true });
    await p2.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(shots, "summary.txt"), summary.join("\n") + "\n");
  console.log(`courses ${D.courses.length}, hole views ${nHoles}, club taps ${nClubs}, coming-soon matches for "ames": ${soon}`);
  console.log(`console/page errors: ${errors.length}`); errors.slice(0, 20).forEach(e => console.log("  " + e));
  console.log(`layout/NaN problems: ${problems.length}`); problems.slice(0, 20).forEach(e => console.log("  " + e));
  process.exit(errors.length || problems.length ? 1 : 0);
})();
