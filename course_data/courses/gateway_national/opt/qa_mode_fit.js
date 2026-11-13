// QA_TALL=1: the same with "Tall grass: Lost ball" switched on (also: the tag must be on the card).
// fit.js <page> <out>: at 375 and 430 px, every th's right edge <= the hole section's right edge, in Second shot mode
// on 3, 6, 13, 18 (several starts) and in Lay up mode on 10; also the top-bar club on one line. Screenshots at 375.
let pw; try { pw = require("playwright"); } catch (e) { pw = require("/opt/node22/lib/node_modules/playwright"); }
const { chromium } = pw; const path = require("path"), fs = require("fs");
(async () => {
  const [pp, out] = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
  const lines = []; let bad = 0;
  for (const W of [375, 430]) {
    const page = await (await b.newContext({ viewport: { width: W, height: 800 }, deviceScaleFactor: 2 })).newPage();
    const errs = []; page.on("pageerror", e => errs.push(String(e)));
    await page.goto("file://" + path.resolve(pp));
    await page.waitForFunction(() => typeof D !== "undefined" && D && D.holes, null, { timeout: 15000 });
    if (process.env.QA_TALL === "1") { await page.evaluate(() => document.querySelector('#tall button[data-v="1"]').click()); await page.waitForTimeout(100); }   // the second rule set on
    const measure = () => page.evaluate(() => {
      const sec = document.querySelector("section.hole").getBoundingClientRect();
      const ths = [...document.querySelectorAll("#hTable th")].map(t => [t.textContent, Math.round(t.getBoundingClientRect().right)]);
      const tds = [...document.querySelectorAll("#hTable tbody tr")].map(r => Math.round(r.lastElementChild.getBoundingClientRect().right));
      const tc = document.getElementById("topClub"); const lh = parseFloat(getComputedStyle(tc).lineHeight) || 40;
      return { secRight: Math.round(sec.right), ths, maxTd: Math.max(...tds), topLines: Math.round(tc.getBoundingClientRect().height / lh), top: tc.textContent,
               key: document.getElementById("topKey").textContent, doc: document.documentElement.scrollWidth, win: window.innerWidth };
    });
    const check = async (label) => {
      const m = await measure();
      const worst = Math.max(...m.ths.map(t => t[1]), m.maxTd);
      const tagOk = process.env.QA_TALL !== "1" || await page.evaluate(() => { const e = document.getElementById("tallTag"); return !!e && !e.hidden && e.getBoundingClientRect().right <= document.querySelector("section.hole").getBoundingClientRect().right; });
      const ok = worst <= m.secRight && m.topLines <= 1 && m.doc <= m.win + 1 && tagOk;
      if (!ok) bad++;
      lines.push(`${W}px ${label}: section right ${m.secRight}; th right edges ${m.ths.map(t => t[0] + " " + t[1]).join(", ")}; last td ${m.maxTd}; top bar "${m.top}" ${m.topLines} line(s) · "${m.key}" => ${ok ? "OK" : "FAIL"}`);
    };
    for (const [set, k, cases] of [["Back", "13", [240, 270, "D", "240R"]], ["Back", "6", ["D", 270]], ["Back", "18", ["D", "W"]], ["Back", "3", [300]], ["Middle", "13", ["D"]]]) {
      await page.evaluate(([set, k]) => { st.set = set; st.src = "d0"; st.start = 1; st.adj = {}; st.club = {}; st.view = "hole"; useSet(); st.idx = D.holes.findIndex(h => h.key === k); render(); }, [set, k]);
      await page.click("#altBtn"); await page.waitForTimeout(80);
      for (const c of cases) {
        await page.evaluate((c) => { if (c === "D" || c === "W") { SS.start = c; SS.lie = "F"; } else { SS.start = parseInt(c); SS.lie = String(c).endsWith("R") ? "R" : "F"; } SS.row = null; render(); }, c);
        await page.waitForTimeout(60);
        await check(`${set} ${k} second-shot ${c}`);
        if (W === 375 && k === "13" && set === "Back" && (c === 240 || c === 270))
          await (await page.$("section.hole")).screenshot({ path: `${out}/fit375_Back_h13_${c}.jpg`, type: "jpeg", quality: 75 });
      }
      await page.click("#altBtn");
    }
    for (const set of ["Back", "Middle"]) {
      await page.evaluate((set) => { st.set = set; st.src = "d0"; st.start = 1; st.adj = {}; st.club = {}; st.view = "hole"; useSet(); st.idx = D.holes.findIndex(h => h.key === "10"); render(); }, set);
      await page.click("#altBtn"); await page.waitForTimeout(80);
      await check(`${set} 10 lay-up`);
      if (W === 375 && set === "Back") await (await page.$("section.hole")).screenshot({ path: `${out}/fit375_Back_h10_layup.jpg`, type: "jpeg", quality: 75 });
      await page.click("#altBtn");
    }
    if (errs.length) { bad++; lines.push("page errors: " + errs.join(" | ")); }
  }
  await b.close();
  lines.push(bad ? `FAILED: ${bad}` : "all fit");
  fs.writeFileSync(out + "/fit.txt", lines.join("\n")); console.log(lines.join("\n"));
})();
