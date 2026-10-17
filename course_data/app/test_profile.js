// Headless check of the "Your game" panel (player profile) at phone (400 px) and desktop (1280 px) width.
//   NODE_PATH=$(npm root -g) node course_data/app/test_profile.js [out/aim_caddie.html] [shots dir]
// Runs the artifact-format copy wrapped the way the host wraps it. Per width: every hole of every course and
// tee set renders; a typed 85-yd driver pattern switches the width-sensitive Spirit Hollow picks exactly as
// the page's width_rule data says (and changes 13, 16, 18), widens the drawn pattern; the sample Garmin R10 CSV
// uploads and moves the profile; a pasted tee-shot log is read; the profile survives a reload (localStorage).
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const art = path.resolve(process.argv[2] || path.join(__dirname, "out", "aim_caddie.html"));
const shots = path.resolve(process.argv[3] || path.join(__dirname, "out", "test_profile"));
const sample = path.join(__dirname, "fixtures", "r10_sample.csv");
const teeLog = path.join(__dirname, "..", "personal", "examples", "tee_shots.csv");
fs.mkdirSync(shots, { recursive: true });
const html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>t</title></head><body>' +
  fs.readFileSync(art, "utf8") + "</body></html>";
const wrapped = path.join(shots, "wrapped.html");
fs.writeFileSync(wrapped, html);
const URL0 = "file://" + wrapped;
const CALM = JSON.stringify({ src: { spirit_hollow: "custom" }, custom: { from: 180, mph: 0, temp: 70 } });

(async () => {
  const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
  const problems = [], log = [];
  for (const vp of [{ width: 400, height: 860, tag: "400" }, { width: 1280, height: 900, tag: "desktop" }]) {
    const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
    const page = await ctx.newPage();
    const errs = [];
    page.on("pageerror", e => errs.push("pageerror: " + e.message));
    page.on("console", m => { if (m.type() === "error" && !/fonts\.(googleapis|gstatic)|ERR_/.test(m.text())) errs.push("console: " + m.text()); });
    await page.goto(URL0);
    await page.evaluate(c => { localStorage.clear(); localStorage.setItem("aimcaddie1", c); }, CALM);
    const open = async hash => { await page.goto(URL0 + hash); await page.reload(); await page.waitForSelector(hash ? ".holeno" : "#app > *"); };
    const check = async what => {
      const r = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
        nan: /NaN|undefined|Infinity/.test(document.getElementById("app").innerText),
        svg: !document.getElementById("ov") || /NaN|undefined/.test(document.getElementById("ov").innerHTML.replace(/href="[^"]*"/g, "")) }));
      if (r.sw > r.cw + 1) problems.push(`${vp.tag} ${what}: horizontal scroll ${r.sw} > ${r.cw}`);
      if (r.nan) problems.push(`${vp.tag} ${what}: NaN/undefined in the page`);
    };
    // picks on Spirit Hollow (Black, calm) read from the page itself
    const picks = async () => {
      const out = {};
      await open("#c=spirit_hollow&t=Black&h=1");
      const n = await page.locator(".chip").count();
      for (let i = 0; i < n; i++) {
        await page.click(`.chip[data-i="${i}"]`);
        const r = await page.evaluate(() => {
          const ov = document.getElementById("ov"), pg = ov.querySelector('polygon[stroke-dasharray="6 5"]');
          let w = null; if (pg) { const xs = pg.getAttribute("points").trim().split(/\s+/).map(p => p.split(",").map(Number));
            const ax = xs.map(p => p[0]); w = Math.max(...ax) - Math.min(...ax); }
          return { no: document.querySelector(".holeno").textContent.replace("Hole ", ""), play: document.querySelector(".play").textContent, w,
                   pill: (document.querySelector('[data-wr="changed"]') || {}).textContent || "" };
        });
        out[r.no] = r;
      }
      return out;
    };
    // 1. every course / tee set / hole renders at this width (default profile)
    await page.reload();
    await check("pick screen");
    await page.screenshot({ path: path.join(shots, `${vp.tag}_00_pick.png`), fullPage: true });
    const courses = await page.evaluate(() => D.courses.map(c => ({ id: c.id, sets: c.tee_sets.filter(t => t.computed !== "missing").map(t => t.name), n: c.holes.length })));
    let nHoles = 0;
    for (const C of courses) for (const S of C.sets) {
      await open(`#c=${C.id}&t=${encodeURIComponent(S)}&h=1`);
      for (let i = 0; i < C.n; i++) {
        await page.click(`.chip[data-i="${i}"]`);
        const ok = await page.evaluate(() => !!document.querySelector("#ov image") && !!document.querySelector(".play"));
        if (!ok) problems.push(`${vp.tag} ${C.id} ${S} hole ${i + 1}: did not render`);
        await check(`${C.id} ${S} ${i + 1}`); nHoles++;
      }
    }
    const before = await picks();
    // 2. type an 85-yd driver pattern
    await page.goto(URL0); await page.evaluate(() => { st.screen = "pick"; render(); }); await page.click('[data-go="game"]');
    await page.fill('input[data-pf="Driver|width95"]', "85"); await page.locator('input[data-pf="Driver|width95"]').press("Tab");
    await check("game 85");
    await page.screenshot({ path: path.join(shots, `${vp.tag}_10_game_85.png`), fullPage: true });
    const shown = await page.locator('#pfOut tr[data-pfrow="Driver"] b').textContent();
    if (shown.trim() !== "85") problems.push(`${vp.tag}: driver pattern shows ${shown} after typing 85`);
    const after = await picks();
    const expect = await page.evaluate(() => { const C = D.courses.find(c => c.id === "spirit_hollow"), o = {};
      for (const H of C.holes) { const V = H.variants[H.tees.Black.variant]; if (V.width_rule) o[H.no] = [widthPick(V.width_rule, 70), widthPick(V.width_rule, 85)]; } return o; });
    const changed = [];
    for (const [no, [p70, p85]] of Object.entries(expect)) {
      if (before[no].play !== p70) problems.push(`${vp.tag} hole ${no}: shows ${before[no].play} at 70, data says ${p70}`);
      if (after[no].play !== p85) problems.push(`${vp.tag} hole ${no}: shows ${after[no].play} at 85, data says ${p85}`);
      if (before[no].play !== after[no].play) changed.push(`${no}: ${before[no].play} -> ${after[no].play}`);
    }
    for (const no of ["13", "16", "18"]) if (before[no].play === after[no].play || !after[no].pill) problems.push(`${vp.tag} hole ${no}: pick did not change at 85 (${after[no].play})`);
    const h4 = before["4"].w && after["4"].w ? after["4"].w / before["4"].w : 0;      // Driver both times: pattern x 85/70
    if (Math.abs(h4 - 85 / 70) > 0.05) problems.push(`${vp.tag} hole 4: pattern scaled x${h4.toFixed(3)}, expected x${(85 / 70).toFixed(3)}`);
    await open("#c=spirit_hollow&t=Black&h=13");
    await page.screenshot({ path: path.join(shots, `${vp.tag}_20_hole13_85.png`), fullPage: true });
    log.push(`${vp.tag}: ${nHoles} hole views; at 85 yds: ${changed.join(", ")}; hole 4 pattern x${h4.toFixed(3)}`);
    // 3. CSV upload (Garmin R10 sample) after resetting the bag
    await page.goto(URL0); await page.evaluate(() => { st.screen = "pick"; render(); }); await page.click('[data-go="game"]'); await page.click('[data-pfact="reset"]');
    await page.setInputFiles("#pfFile", sample);
    await page.waitForFunction(() => /Added/.test((document.getElementById("pfMsg") || {}).textContent || ""));
    const up = await page.evaluate(() => ({ msg: document.getElementById("pfMsg").textContent, W: POST.clubs.Driver.width95.median,
      ci: POST.clubs.Driver.width95.ci90, n: POST.clubs.Driver.n_shots.launch_monitor, n4: POST.clubs["4-wood"].n_shots.launch_monitor,
      c: POST.clubs.Driver.carry.median }));
    if (up.n !== 12 || up.n4 !== 4 || !/7-iron \(2\)/.test(up.msg)) problems.push(`${vp.tag} upload: ${up.msg}`);
    if (!(up.W > 72 && up.W < 100)) problems.push(`${vp.tag} upload: driver pattern ${up.W} did not move toward the sample's ~110`);
    await check("game upload");
    await page.screenshot({ path: path.join(shots, `${vp.tag}_30_upload.png`), fullPage: true });
    log.push(`${vp.tag}: upload -> ${up.msg} Driver pattern ${up.W.toFixed(1)} (90% ${up.ci[0].toFixed(0)}-${up.ci[1].toFixed(0)}), carry ${up.c.toFixed(1)}`);
    // 4. paste a tee-shot log; 5. it all survives a reload
    await page.fill("#pfPaste", fs.readFileSync(teeLog, "utf8")); await page.click('[data-pfact="paste"]');
    const paste = await page.evaluate(() => ({ msg: document.getElementById("pfMsg").textContent, n: POST.data.on_course, W: POST.clubs.Driver.width95.median }));
    if (!(paste.n > 0)) problems.push(`${vp.tag} paste: ${paste.msg}`);
    log.push(`${vp.tag}: paste -> ${paste.msg} Driver pattern ${paste.W.toFixed(1)}`);
    await page.reload(); await page.waitForSelector("#pfOut");
    const kept = await page.evaluate(() => POST.data.on_course + POST.data.launch_monitor);
    if (kept !== paste.n + 16) problems.push(`${vp.tag}: after reload ${kept} shots kept`);
    await check("game reload");
    if (errs.length) problems.push(...errs.map(e => `${vp.tag} ${e}`));
    await ctx.close();
  }
  await browser.close();
  log.forEach(l => console.log(l));
  console.log(`problems: ${problems.length}`); problems.slice(0, 30).forEach(p => console.log("  " + p));
  process.exit(problems.length ? 1 : 0);
})();
