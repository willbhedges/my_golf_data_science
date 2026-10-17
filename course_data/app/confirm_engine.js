/* Golfer confirm in the browser: golf_confirm/1 (course_data/platform/confirm.py, CONFIRM_UX.md) over a
   precomputed routing pool (golf_confirm_pool/1, course_data/app/confirm_pool.py).

     const S = new ConfirmSession(pool, {card})   // card: a typed scorecard/1 (TypedCard.parseTypedCard) or null
     S.payload()                                  // golf_confirm/1: holes, summary, questions (best first)
     S.answer({question: "c7", answer: "yes"})    // "no", or {tee_ll: [lon, lat], green_ll: [lon, lat]} for a locate
     S.notHole(7)                                 // "this isn't hole 7" during the round = a confirm answered "no"

   Re-solve: every answer is a constraint on the pool (a pin on hole n's key = green + tee complex, or an
   exclusion of a green with any box within 45 yds of the shown tee). The routing is the cheapest pooled routing
   that meets every constraint; p_hole is its key's Boltzmann share (temperature tau) over those routings,
   exactly as confirm.Session.marginals does over routing_v2's top routings. When no pooled routing meets every
   constraint, the routings with the fewest broken ones stand in (a pin whose green the routing has under another
   tee complex counts half) and the pinned holes are drawn where the golfer put them.
   Questions: max expected bits per tap (confirm.Session.questions, policy "eig"). Stops when every unconfirmed
   hole has p_hole >= p_stop; "this isn't hole n" stays available all round (the stop rule leaves ~1.4 wrong
   holes per course on the test split). */
(function (root) {
  "use strict";
  const YD = 0.9144;
  function Proj(lon0, lat0) {
    const kx = 111320.0 * Math.cos(lat0 * Math.PI / 180) / YD, ky = 110950.0 / YD;
    return {fwd: (lon, lat) => [(lon - lon0) * kx, (lat - lat0) * ky], inv: (x, y) => [lon0 + x / kx, lat0 + y / ky]};
  }
  const H2 = p => (p <= 0 || p >= 1) ? 0 : -(p * Math.log2(p) + (1 - p) * Math.log2(1 - p));
  const entropy = ps => { let s = 0; for (const p of ps) if (p > 0) s -= p * Math.log2(p); return s; };
  const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);

  /* routing.length_cost / routing.fingerprint for one (tee, green) pair */
  function lengthCost(D, yards, par, P) {
    if (yards && yards.length) {
      let best = Infinity;
      for (const Y of yards) {
        const z = D >= Y ? (D - Y) / (0.04 * Y + 8) : (Y - D) / (par === 3 ? 0.06 * Y + 10 : 0.12 * Y + 15);
        best = Math.min(best, Math.min(z, 3.2) ** 2);
      }
      return best;
    }
    const [lo, hi] = P.par_ranges[String(par)] || [90, 640];
    const z = D < lo ? (lo - D) / 25 : D > hi ? (D - hi) / 25 : 0;
    return Math.min(z, 3.2) ** 2;
  }
  function fingerprint(boxes, yards, par, P) {
    if (!yards || !yards.length) return 0;
    let tot = 0;
    for (const Y of yards) {
      let zmin = Infinity;
      for (const d of boxes) {
        const dd = d - Y, tol = dd >= 0 ? 0.04 * Y + 8 : (par === 3 ? 0.06 * Y + 10 : 0.12 * Y + 15);
        zmin = Math.min(zmin, Math.abs(dd) / tol);
      }
      tot += Math.min(zmin * zmin, P.fp_cap);
    }
    return tot / yards.length;
  }
  /* card -> per hole {par, yards: [one per tee set]} (routing.card_holes) */
  function cardHoles(card, n) {
    if (!card) return null;
    let pars = card.par;
    const sets = card.tee_sets || {};
    const ys = {};
    for (const [k, v] of Object.entries(sets)) if (v && v.yards) ys[k] = v.yards;
    if (!pars) pars = (Object.values(sets).find(v => v.par) || {}).par || null;
    const out = [];
    for (let i = 0; i < n; i++) {
      const row = [...new Set(Object.values(ys).map(v => v[i]).filter(y => y && y >= 60 && y <= 800).map(Number))].sort((a, b) => a - b);
      const p = pars && pars[i] ? +pars[i] : null;
      out.push({par: p, yards: row});
    }
    return out;
  }

  class ConfirmSession {
    constructor(pool, opt) {
      opt = opt || {};
      this.pool = pool;
      const P = this.P = pool.params;
      this.n = pool.n;
      const pts = pool.greens.map(g => g.ll).concat(pool.tees.map(t => t.ll));
      const lon0 = pts.reduce((s, p) => s + p[0], 0) / pts.length, lat0 = pts.reduce((s, p) => s + p[1], 0) / pts.length;
      this.proj = Proj(lon0, lat0);
      this.gxy = pool.greens.map(g => this.proj.fwd(g.ll[0], g.ll[1]));
      this.txy = pool.tees.map(t => this.proj.fwd(t.ll[0], t.ll[1]));
      /* per hole: pair -> key id (green + tee complex) and green */
      this.keyIds = {}; this.keyNames = [];
      this.pkey = pool.pairs.map(tab => tab.map(([t, g]) => this.keyOf(t, g)));
      this.R = pool.routings.length;
      this.setCard(opt.card || null);
      this.pins = {}; this.excl = []; this.rejected = new Set();
      this.taps = 0; this.history = [];
      this.solve();
    }
    keyOf(t, g) {
      const name = g + "|" + (t >= 0 ? this.pool.tees[t].cx : "none");
      if (!(name in this.keyIds)) { this.keyIds[name] = this.keyNames.length; this.keyNames.push(name); }
      return this.keyIds[name];
    }
    /* a typed card re-scores the pool's length / fingerprint terms (the pool may have been built with another
       card, or none: each pair carries its straight length and its on-line box lengths) */
    setCard(card) {
      const pool = this.pool, P = this.P, n = this.n;
      this.card = card;
      this.cost = Float64Array.from(pool.costs);
      this.valid = new Uint8Array(this.R).fill(1);
      this.cardHoles = card ? cardHoles(card, n) : null;
      if (!card) return;
      const old = pool.holes;
      const delta = pool.pairs.map((tab, h) => tab.map(([t, g, , D, boxes]) => {
        if (t < 0 || g < 0 || D == null) return 0;
        const o = old[h] || {}, c = this.cardHoles[h] || {};
        const lcOld = lengthCost(D, o.yards, o.par, P), fpOld = fingerprint(boxes, o.yards, o.par, P);
        const lcNew = lengthCost(D, c.yards, c.par, P), fpNew = fingerprint(boxes, c.yards, c.par, P);
        return P.w_length * (lcNew - lcOld) + P.w_fingerprint * (fpNew - fpOld);
      }));
      for (let r = 0; r < this.R; r++) {
        const row = pool.routings[r];
        let d = 0;
        for (let h = 0; h < n; h++) d += delta[h][row[h]];
        if (!isFinite(d)) this.valid[r] = 0; else this.cost[r] += d;
      }
      if (!this.valid.some(v => v)) this.valid.fill(1);      /* a card that fits nothing: keep the pool */
    }

    /* ---------------------------------------------------------------- solve */
    violation(r) {
      const row = this.pool.routings[r], pairs = this.pool.pairs;
      let v = 0;
      for (const [hs, pin] of Object.entries(this.pins)) {
        const h = +hs, pr = pairs[h][row[h]];
        if (pin.key != null && this.pkey[h][row[h]] === pin.key) continue;
        if (pin.g >= 0 && pr[1] === pin.g) { v += pin.t >= 0 ? 0.5 : 0; continue; }
        v += 1;
        if (pin.g >= 0) for (let k = 0; k < this.n; k++) if (k !== h && pairs[k][row[k]][1] === pin.g) { v += 0.5; break; }
      }
      for (const e of this.excl) {
        if (this.pins[e.h]) continue;                 /* a located hole: the pin replaces the earlier "no" (as fixed rows in routing_v2) */
        const pr = pairs[e.h][row[e.h]];
        if (e.key != null) { if (this.pkey[e.h][row[e.h]] === e.key) v += 1; continue; }
        if (pr[1] === e.g && pr[0] >= 0 && dist(this.txy[pr[0]], e.xy) < e.r) v += 1;
      }
      return v;
    }
    solve() {
      const R = this.R, n = this.n, pool = this.pool, tau = Math.max(this.P.tau, 1e-6);
      const viol = new Float64Array(R);
      let vmin = Infinity;
      for (let r = 0; r < R; r++) { if (!this.valid[r]) { viol[r] = Infinity; continue; } viol[r] = this.violation(r); if (viol[r] < vmin) vmin = viol[r]; }
      const S = [];
      for (let r = 0; r < R; r++) if (viol[r] <= vmin + 1e-9) S.push(r);
      let cmin = Infinity, best = S[0];
      for (const r of S) if (this.cost[r] < cmin) { cmin = this.cost[r]; best = r; }
      const marg = Array.from({length: n}, () => new Map());
      let Z = 0;
      for (const r of S) {
        const p = Math.exp(-(this.cost[r] - cmin) / tau);
        Z += p;
        const row = pool.routings[r];
        for (let h = 0; h < n; h++) { const k = this.pkey[h][row[h]]; marg[h].set(k, (marg[h].get(k) || 0) + p); }
      }
      for (const m of marg) for (const [k, v] of m) m.set(k, v / Z);
      this.marg = marg; this.best = best; this.vmin = vmin; this.nConsistent = S.length;
      const row = pool.routings[best];
      const holes = {};
      for (let h = 0; h < n; h++) {
        const ref = String(h + 1), pin = this.pins[ref - 1];
        let [t, g, bt, D] = pool.pairs[h][row[h]];
        let key = this.pkey[h][row[h]], custom = null;
        if (pin && (pin.key == null || pin.key !== key)) {          /* soft: draw the hole where the golfer put it */
          custom = {tee_ll: pin.tee_ll, green_ll: pin.green_ll};
          t = pin.t; g = pin.g; bt = pin.t; key = pin.key;
        }
        const pk = key != null ? (marg[h].get(key) || 0) : 0;
        const fixed = !!pin;
        const H = {ref, par: this.parOf(h), card_yards: this.yardsOf(h), t_idx: t, g_idx: g, fixed, p_hole: +pk.toFixed(3)};
        H.tee_ll = custom ? custom.tee_ll : (t >= 0 ? pool.tees[t].ll : null);
        H.green_ll = custom ? custom.green_ll : (g >= 0 ? pool.greens[g].ll : null);
        H.back_tee_ll = custom ? custom.tee_ll : (bt >= 0 ? pool.tees[bt].ll : H.tee_ll);
        H.straight_yd = H.tee_ll && H.green_ll ? +(dist(this.proj.fwd(...H.tee_ll), this.proj.fwd(...H.green_ll))).toFixed(1) : null;
        const flags = [];
        if (!H.green_ll) flags.push("no green found");
        if (!H.tee_ll) flags.push("no tee found");
        if (pk < this.P.p_check && !fixed) flags.push(`ambiguous (${Math.round(pk * 100)}% of the posterior)`);
        H.flags = flags;
        H.status = fixed ? "confirmed" : (flags.length ? "check" : "ok");
        H.key = key;
        holes[ref] = H;
      }
      this.holes = holes;
      return holes;
    }
    parOf(h) { const c = this.cardHoles ? this.cardHoles[h] : this.pool.holes[h]; return c ? c.par : null; }
    yardsOf(h) { const c = this.cardHoles ? this.cardHoles[h] : this.pool.holes[h]; return c ? c.yards : []; }
    done() { return Object.values(this.holes).every(H => H.fixed || H.p_hole >= this.P.p_stop); }

    /* ---------------------------------------------------------------- questions (confirm.Session.questions, "eig") */
    questions(k) {
      const qs = [], DOUBT = this.P.doubt;
      for (const H of Object.values(this.holes)) {
        if (H.fixed) continue;
        const h = +H.ref - 1, d = this.marg[h];
        const p = Math.min(Math.max(H.key != null ? (d.get(H.key) || 0) : 0, 1e-6), 1 - 1e-6);
        const igC = Math.max(H2(p), H2(DOUBT) * (1 - p));
        const vals = [...d.values()], rest = Math.max(0, 1 - vals.reduce((s, x) => s + x, 0));
        let igL = entropy(vals.concat([rest]));
        const line = H.back_tee_ll && H.green_ll ? [H.back_tee_ll, H.green_ll] : null;
        const par = H.par ? ` (par ${H.par})` : "";
        if (!this.rejected.has(H.ref))
          qs.push({id: "c" + H.ref, kind: "confirm", ref: H.ref, taps: 1, bits: +igC.toFixed(3), bits_per_tap: +igC.toFixed(3),
                   p_hole: +p.toFixed(3), prompt: `Is this hole ${H.ref}?${par}`,
                   show: {line, tee_ll: H.tee_ll, green_ll: H.green_ll}, answers: ["yes", "no"]});
        else igL = Math.max(igL, 1.0);
        qs.push({id: "l" + H.ref, kind: "locate", ref: H.ref, taps: 2, bits: +igL.toFixed(3), bits_per_tap: +(igL / 2).toFixed(3),
                 p_hole: +p.toFixed(3), prompt: `Tap hole ${H.ref}'s tee, then its green`,
                 show: {line: null, tee_ll: null, green_ll: null}, answers: [{tee_ll: "[lon, lat]", green_ll: "[lon, lat]"}]});
      }
      qs.sort((a, b) => (b.bits_per_tap - a.bits_per_tap) || (a.taps - b.taps) || (+a.ref - +b.ref));
      this._qs = {};
      for (const q of qs) this._qs[q.id] = q;
      return k == null ? qs : qs.slice(0, k);
    }

    /* ---------------------------------------------------------------- answers */
    snap(kind, ll, tol) {
      const xy = this.proj.fwd(ll[0], ll[1]), arr = kind === "green" ? this.gxy : this.txy;
      let bi = -1, bd = Infinity;
      arr.forEach((p, i) => { const d = dist(p, xy); if (d < bd) { bd = d; bi = i; } });
      return bd <= tol ? bi : -1;
    }
    answer(a) {
      const q = (this._qs && this._qs[a.question]) || {kind: a.kind || "confirm", ref: String(a.ref), id: a.question};
      const ref = String(q.ref), h = +ref - 1, H = this.holes[ref], ans = a.answer;
      if (q.kind === "confirm") {
        this.taps += 1;
        if (ans === "yes" || ans === true) {
          this.pins[h] = {key: H.key, t: H.t_idx, g: H.g_idx, tee_ll: H.tee_ll, green_ll: H.green_ll};
        } else {
          if (H.t_idx >= 0 && H.g_idx >= 0) this.excl.push({h, g: H.g_idx, xy: this.txy[H.t_idx], r: this.P.reject_r});
          else if (H.key != null) this.excl.push({h, key: H.key});
          delete this.pins[h];
          this.rejected.add(ref);
        }
      } else {
        this.taps += 2;
        const gk = ans.green_ll ? this.snap("green", ans.green_ll, this.P.snap_green) : H.g_idx;
        const tk = ans.tee_ll ? this.snap("tee", ans.tee_ll, this.P.snap_tee) : H.t_idx;
        const green_ll = gk >= 0 ? this.pool.greens[gk].ll : ans.green_ll, tee_ll = tk >= 0 ? this.pool.tees[tk].ll : ans.tee_ll;
        const key = gk >= 0 && tk >= 0 ? this.keyOf(tk, gk) : null;
        this.pins[h] = {key, t: tk, g: gk, tee_ll, green_ll};
      }
      this.history.push({question: q.id || null, kind: q.kind, ref, answer: typeof ans === "string" ? ans : "tapped"});
      return this.solve();
    }
    notHole(ref) { this.questions(); return this.answer({question: "c" + ref, kind: "confirm", ref: String(ref), answer: "no"}); }

    payload(course, k) {
      const holes = Object.values(this.holes).sort((a, b) => +a.ref - +b.ref).map(H => ({
        ref: +H.ref, par: H.par, card_yards: H.card_yards,
        tee: H.tee_ll ? {ll: H.tee_ll, src: H.t_idx >= 0 ? this.pool.tees[H.t_idx].src : "golfer"} : null,
        green: H.green_ll ? {ll: H.green_ll, src: H.g_idx >= 0 ? this.pool.greens[H.g_idx].src : "golfer"} : null,
        line: H.back_tee_ll && H.green_ll ? [H.back_tee_ll, H.green_ll] : null, straight_yd: H.straight_yd,
        p_hole: H.p_hole, confirmed: H.fixed, status: H.status, flags: H.flags}));
      const qs = this.done() ? [] : this.questions(k == null ? 3 : k);
      return {schema: "golf_confirm/1", course: course || {name: this.pool.name}, method: "routing/2 (pool)", n_holes: this.n,
              card: !!(this.card || this.pool.card), holes,
              summary: {confirmed: holes.filter(x => x.confirmed).length, to_check: holes.filter(x => x.status === "check").length,
                        taps_so_far: this.taps, done: this.done(), p_stop: this.P.p_stop,
                        expected_correct_holes: +holes.reduce((s, x) => s + (x.p_hole || 0), 0).toFixed(1),
                        consistent_routings: this.nConsistent, broken_constraints: this.vmin},
              questions: qs, history: this.history,
              answer_format: {question: "<questions[].id>", answer: "'yes' | 'no' (confirm) or {'tee_ll': [lon, lat], 'green_ll': [lon, lat]} (locate)"}};
    }
    /* state for localStorage: the answers replay onto the pool */
    save() { return {log: this.log || [], card: this.card}; }
    act(a) { this.log = (this.log || []).concat([a]); return a.not ? this.notHole(a.not) : (this.questions(), this.answer(a)); }
    restore(s) {
      this.pins = {}; this.excl = []; this.rejected = new Set(); this.taps = 0; this.history = []; this.log = [];
      if (s && s.card !== undefined && s.card !== this.card) this.setCard(s.card);
      this.solve();
      for (const a of (s && s.log) || []) { try { this.act(a); } catch (e) { break; } }
    }
    undoLast() { const log = (this.log || []).slice(0, -1); this.restore({log, card: this.card}); }
  }

  /* routing.score for one hole: green within 20 yds of the true green, tee within 40 yds of the true line's first 60 % */
  function holeOk(H, T) {
    if (!H || !H.green_ll || !H.tee_ll) return false;
    const p = Proj(T.green_ll[0], T.green_ll[1]);
    if (Math.hypot(...p.fwd(...H.green_ll)) > 20) return false;
    const line = T.line.map(c => p.fwd(c[0], c[1]));
    const cum = [0];
    for (let i = 1; i < line.length; i++) cum.push(cum[i - 1] + dist(line[i], line[i - 1]));
    let k = 0; const lim = 0.6 * cum[cum.length - 1];
    while (k < cum.length && cum[k] < lim) k++;                       /* np.searchsorted(cum, lim) */
    const first = line.slice(0, Math.max(2, k + 1));
    const q = p.fwd(...H.tee_ll);
    let best = Infinity;
    for (let i = 0; i + 1 < first.length; i++) {
      const a = first[i], b = first[i + 1], ab = [b[0] - a[0], b[1] - a[1]];
      const t = Math.max(0, Math.min(1, ((q[0] - a[0]) * ab[0] + (q[1] - a[1]) * ab[1]) / Math.max(ab[0] ** 2 + ab[1] ** 2, 1e-9)));
      best = Math.min(best, Math.hypot(a[0] + t * ab[0] - q[0], a[1] + t * ab[1] - q[1]));
    }
    return best <= 40;
  }

  /* the oracle golfer of route_eval.simulate_confirm: answers the first question from the hidden truth until
     every hole is right -> {taps, questions, stop_rule_taps, stop_rule_wrong, log} */
  function simulate(pool, truth, opt) {
    opt = opt || {};
    const S = new ConfirmSession(poolFor(pool, opt.typed_pools, opt.card), {card: opt.card || null});
    const maxTaps = opt.max_taps || 30;
    let stop = null;
    for (;;) {
      const wrong = Object.keys(truth.holes).filter(r => +r <= S.n && !holeOk(S.holes[r], truth.holes[r]));
      if (stop === null && S.done()) stop = [S.taps, wrong.length];
      if (!wrong.length || S.taps >= maxTaps) {
        const st = stop || [S.taps, wrong.length];
        return {taps: wrong.length ? null : S.taps, questions: S.history.length, stop_rule_taps: st[0], stop_rule_wrong: st[1],
                wrong_left: wrong.length, log: S.history};
      }
      const qs = S.questions();
      if (!qs.length) return {taps: null, questions: S.history.length, wrong_left: wrong.length, log: S.history};
      const q = qs[0], T = truth.holes[q.ref];
      if (q.kind === "confirm") S.answer({question: q.id, answer: !T || holeOk(S.holes[q.ref], T) ? "yes" : "no"});   /* no truth for this hole: yes (route_eval) */
      else S.answer({question: q.id, answer: T ? {tee_ll: T.tee_ll, green_ll: T.green_ll} : {tee_ll: S.holes[q.ref].tee_ll, green_ll: S.holes[q.ref].green_ll}});
    }
  }

  /* is `pool` (routed with a card) the re-solve for this typed card? Same pars, every typed yardage within 3 yds
     of one of the pool card's sets. The page carries such pools for cards it knows (the package request's card):
     the stand-in for the backend re-solve a typed card would trigger. */
  function cardMatches(pool, card) {
    if (!pool || !pool.card || !card) return false;
    const ch = cardHoles(card, pool.n);
    if (!ch || ch.length !== pool.holes.length) return false;
    return ch.every((c, h) => { const o = pool.holes[h] || {};
      if (c.par && o.par && c.par !== o.par) return false;
      return c.yards.length > 0 && c.yards.every(y => (o.yards || []).some(Y => Math.abs(Y - y) <= 3)); });
  }
  function poolFor(base, typed, card) { return (card && (typed || []).find(p => cardMatches(p, card))) || base; }

  const api = {ConfirmSession, Proj, holeOk, simulate, lengthCost, fingerprint, cardHoles, cardMatches, poolFor};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.ConfirmEngine = api;
})(typeof window !== "undefined" ? window : this);
