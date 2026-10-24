// Hole-by-hole browser check of a course wind page (Playwright, chromium at /opt/pw-browsers/chromium).
//   node course_data/courses/qa_page.js course_data/courses/<slug>/wind_page/index.html <out_dir> [tee set]
// For each hole (top next arrow, 400 px phone and 1280 px desktop): a JPEG screenshot of the hole panel and a
// record {hole, par line, play, aim text, table rows, elevation line, note, badges, problems}. Problems: console
// errors, NaN / undefined / Infinity in the text, empty play, image missing, table without rows, page wider than
// the viewport (horizontal scroll), hole number not advancing. Also: tee picker / start picker / day buttons.
let pw; try { pw = require("playwright"); } catch (e) { pw = require("/opt/node22/lib/node_modules/playwright"); }
const { chromium } = pw;
const fs = require("fs");
const path = require("path");

(async () => {
  const [page_path, out, set0] = process.argv.slice(2);     // optional set0: check every hole from that tee set
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
  const report = { page: page_path, views: {} };
  for (const [name, vp] of [["phone", { width: 400, height: 860 }], ["desktop", { width: 1280, height: 900 }]]) {
    const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    const errors = [];
    page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
    page.on("pageerror", e => errors.push(String(e)));
    await page.goto("file://" + path.resolve(page_path));
    await page.waitForTimeout(400);
    if (set0) { await page.click(`#set button[data-v="${set0}"]`); await page.waitForTimeout(150); }
    const D = await page.evaluate(() => ({ n: D.holes.length, sets: D.sets, days: D.days, keys: D.holes.map(h => h.key) }));
    const holes = [];
    for (let i = 0; i < D.n; i++) {
      const rec = await page.evaluate(() => {
        const t = id => (document.getElementById(id) || {}).textContent || "";
        const rows = [...document.querySelectorAll("#hTable tbody tr")].map(r => [...r.children].map(c => c.textContent.trim()));
        const img = document.querySelector("#ov image");
        return { hole: t("hNo"), top: t("topNo"), par: t("hPar"), play: t("hPlay"), aim: t("hAim"), elev: t("hElev"),
                 note: t("hNote"), badges: t("hBadges"), rows, wind: t("windLbl"), adj: t("hAdj"),
                 img: !!(img && img.getAttribute("href") && img.getAttribute("href").length > 1000),
                 wide: document.documentElement.scrollWidth > window.innerWidth + 1 };
      });
      const probs = [];
      const all = JSON.stringify(rec);
      if (/NaN|undefined|Infinity|null yds/.test(all)) probs.push("bad number in text");
      if (!rec.play.trim()) probs.push("empty play");
      if (!rec.img) probs.push("no hole image");
      if (!rec.rows.length) probs.push("empty table");
      if (rec.wide) probs.push("horizontal scroll");
      if (i > 0 && rec.hole === holes[i - 1].hole) probs.push("hole did not advance");
      rec.problems = probs;
      const panel = await page.$("section.hole");
      await panel.screenshot({ path: path.join(out, `${name}_${String(i + 1).padStart(2, "0")}.jpg`), type: "jpeg", quality: 55 });
      holes.push(rec);
      await page.click("#nextTop");
      await page.waitForTimeout(120);
    }
    // controls: every tee set, day 2, a starting hole, custom wind
    const ctl = [];
    for (const s of (await page.isVisible("#setRow")) ? D.sets : []) {
      await page.click(`#set button[data-v="${s}"]`);
      await page.waitForTimeout(80);
      ctl.push({ set: s, par: await page.textContent("#hPar"), play: await page.textContent("#hPlay") });
    }
    if (await page.$('#src button[data-v="d1"]')) await page.click('#src button[data-v="d1"]');   // one-day events
    await page.selectOption("#start", "10");
    await page.waitForTimeout(100);
    ctl.push({ day2_start10: await page.textContent("#windLbl"), hole: await page.textContent("#hNo") });
    report.views[name] = { holes, controls: ctl, errors };
    await page.screenshot({ path: path.join(out, `${name}_full.jpg`), type: "jpeg", quality: 50, fullPage: true });
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(out, "qa.json"), JSON.stringify(report, null, 1));
  let bad = 0;
  for (const [v, r] of Object.entries(report.views)) {
    for (const h of r.holes) if (h.problems.length) { bad++; console.log(v, h.hole, h.problems.join("; ")); }
    if (r.errors.length) console.log(v, "console errors:", r.errors.slice(0, 5));
  }
  console.log("holes checked:", report.views.phone.holes.length, "problems:", bad);
})();
