/* A golfer-typed scorecard: 9 / 18 yardages and optionally the pars, strictly validated.
   JS port of course_data/platform/typed_card.py (same accepted input, same error / warning codes):
     parseTypedCard(yards, {pars, tee, unit, total, out_total, in_total}) -> [card (scorecard/1) | null, issues]
   issues: [{level: "error" | "warning", code, msg, hole?}]. An error returns card null (the app re-asks). */
(function (root) {
  "use strict";
  const YARD_MIN = 50, YARD_MAX = 720;
  const PAR_FIT = {3: [0, 270], 4: [230, 520], 5: [400, 720], 6: [520, 900]};
  const SEP = /[\s,;/|\t]+/;
  const PAIR = () => /(?:hole\s*)?#?(\d{1,2})\s*[:=\-)]\s*(\d+)/gi;
  const issue = (level, code, msg, hole) => (hole == null ? {level, code, msg} : {level, code, msg, hole});
  const sum = a => a.reduce((s, x) => s + (x || 0), 0);
  const isErr = a => a.some(i => i.level === "error");

  /* text -> [[values as digit strings, hole order], issues] (strings: "443545344" must survive as digits) */
  function tokens(text) {
    if (Array.isArray(text)) text = text.join(" ");
    text = String(text == null ? "" : text).trim();
    const issues = [];
    if (!text) return [[], [issue("error", "empty", "nothing typed")]];
    const pairs = [...text.matchAll(PAIR())];
    const rest = text.replace(PAIR(), " ").replace(/^[ ,;/|\t\n]+|[ ,;/|\t\n]+$/g, "");
    if (pairs.length && !/\d/.test(rest)) {
      const by = {};
      for (const m of pairs) {
        const h = parseInt(m[1], 10);
        if (h in by) issues.push(issue("error", "duplicate_hole", `hole ${h} typed twice`, h));
        by[h] = m[2];
      }
      const n = Math.max(...Object.keys(by).map(Number));
      const missing = [];
      for (let h = 1; h <= n; h++) if (!(h in by)) missing.push(h);
      if (missing.length) issues.push(issue("error", "missing_hole", `no value for hole(s) ${missing.join(", ")}`, missing[0]));
      const out = [];
      for (let h = 1; h <= n; h++) out.push(h in by ? by[h] : null);
      return [out, issues];
    }
    const vals = [];
    for (let tok of text.split(SEP).filter(t => t)) {
      tok = tok.replace(/^\.+|\.+$/g, "");
      if (/^\d+$/.test(tok)) vals.push(tok);
      else if (/^(out|in|tot|total|front|back)$/i.test(tok)) continue;
      else issues.push(issue("error", "not_a_number", `'${tok}' is not a number (value ${vals.length + 1})`, vals.length + 1));
    }
    return [vals, issues];
  }

  /* remove OUT / IN / TOT columns when they equal the sums they stand for -> [holes, subtotals] */
  function stripSubtotals(vals) {
    let v = vals.slice();
    const sub = {};
    if ((v.length === 10 || v.length === 11) && v[9] === sum(v.slice(0, 9))) {
      sub.out = v[9];
      v = v.slice(0, 9).concat(v.slice(10));
      if (v.length === 10 && v[9] === sub.out) v = v.slice(0, 9);
    } else if ((v.length === 20 || v.length === 21) && v[9] === sum(v.slice(0, 9)) && v[19] === sum(v.slice(10, 19))) {
      sub.out = v[9]; sub.in = v[19];
      const tot = v.length === 21 ? v[20] : null;
      v = v.slice(0, 9).concat(v.slice(10, 19));
      if (tot != null) sub.total = tot;
    } else if (v.length === 19 && v[18] === sum(v.slice(0, 18))) {
      sub.total = v[18];
      v = v.slice(0, 18);
    }
    return [v, sub];
  }

  function checkCount(vals, what) {
    const n = vals.length;
    if (n === 9 || n === 18) return [];
    if (n === 27 || n === 36) return [issue("error", "too_many_holes", `${n} ${what} - a ${n}-hole facility: type the ${n === 27 ? "nine" : "eighteen"}s you are playing (18 values)`)];
    const near = Math.abs(n - 9) < Math.abs(n - 18) ? 9 : 18;
    const off = n === near - 1 ? "one missing" : n === near + 1 ? "one extra" : `${Math.abs(n - near)} off`;
    return [issue("error", "count", `${n} ${what} typed, expected 9 or 18 (${off})`)];
  }

  function parseTypedCard(yards, opt) {
    opt = opt || {};
    const tee = opt.tee || "Typed", unit = opt.unit || "yd", source = opt.source || "typed by golfer";
    let total = opt.total ?? null, outT = opt.out_total ?? null, inT = opt.in_total ?? null;
    const issues = [];
    let [ys, iss] = tokens(yards);
    issues.push(...iss);
    let yv = ys.map(s => (s == null ? null : Number(s))), sub = {};
    if (!isErr(iss)) [yv, sub] = stripSubtotals(yv.filter(y => y != null));
    outT = outT || sub.out || null; inT = inT || sub.in || null; total = total || sub.total || null;
    issues.push(...checkCount(yv, "yardages"));
    if (unit === "m") yv = yv.map(y => (y == null ? null : Math.round(y / 0.9144)));
    yv.forEach((y, i) => {
      if (y == null) return;
      if (y > 999) issues.push(issue("error", "joined", `hole ${i + 1}: ${y} looks like two values typed together`, i + 1));
      else if (!(YARD_MIN <= y && y <= YARD_MAX)) issues.push(issue("error", "range", `hole ${i + 1}: ${y} yds is outside ${YARD_MIN}-${YARD_MAX}`, i + 1));
    });
    let pv = null;
    const pars = opt.pars;
    if (pars != null && !["", "[]"].includes(String(pars).trim())) {
      let ps, piss;
      [ps, piss] = tokens(pars);
      issues.push(...piss.map(i => Object.assign({}, i, {msg: "pars: " + i.msg})));
      if (ps.length === 1 && ps[0] != null && (ps[0].length === 9 || ps[0].length === 18)) ps = ps[0].split("");   /* "443545344" */
      pv = ps.map(s => (s == null ? null : Number(s)));
      if (!isErr(piss)) pv = stripSubtotals(pv)[0];
      if (pv.length !== yv.length) issues.push(issue("error", "par_count", `${pv.length} pars for ${yv.length} yardages`));
      pv.forEach((p, i) => { if (p != null && !(3 <= p && p <= 6)) issues.push(issue("error", "par_range", `hole ${i + 1}: par ${p}`, i + 1)); });
      const tp = sum(pv.filter(p => p)), [lo, hi] = pv.length === 9 ? [27, 38] : [54, 76];
      if ((pv.length === 9 || pv.length === 18) && !(lo <= tp && tp <= hi)) issues.push(issue("error", "par_total", `pars add up to ${tp}, expected ${lo}-${hi}`));
    }
    if (isErr(issues)) return [null, issues];
    const n = yv.length;
    if (total != null && sum(yv) !== +total) issues.push(issue("error", "total", `yardages add up to ${sum(yv)}, the card says ${total}`));
    if (outT != null && n === 18 && sum(yv.slice(0, 9)) !== +outT) issues.push(issue("warning", "out_total", `front nine adds up to ${sum(yv.slice(0, 9))}, OUT says ${outT}`));
    if (inT != null && n === 18 && sum(yv.slice(9)) !== +inT) issues.push(issue("warning", "in_total", `back nine adds up to ${sum(yv.slice(9))}, IN says ${inT}`));
    if (isErr(issues)) return [null, issues];
    if (pv) yv.forEach((y, i) => { const [lo, hi] = PAR_FIT[pv[i]] || [0, 999];
      if (!(lo <= y && y <= hi)) issues.push(issue("warning", "par_fit", `hole ${i + 1}: ${y} yds for a par ${pv[i]} - check this hole`, i + 1)); });
    if (n === 18 && yv.slice(0, 9).every((y, i) => y === yv[9 + i])) issues.push(issue("warning", "repeat_nine", "the same nine twice (a 9-hole course played twice?)"));
    const card = {schema: "scorecard/1", source, par: pv ? pv.slice() : null, handicap: null,
      tee_sets: {[tee]: {colour: tee.toLowerCase(), aliases: [tee.toLowerCase()], yards: yv.slice(), total: sum(yv), source}},
      typed: {unit, subtotals: Object.keys(sub).length ? sub : null}};
    return [card, issues];
  }

  const api = {parseTypedCard, tokens, stripSubtotals, PAR_FIT, YARD_MIN, YARD_MAX};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.TypedCard = api;
})(typeof window !== "undefined" ? window : this);
