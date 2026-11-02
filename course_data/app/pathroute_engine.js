/* pathroute v2 confirm-and-resolve in the browser: a line-for-line port of course_data/zero_tap/pathroute_v2
   decode2.decode2 (constrained tour beam: tee complexes, crossing / reuse penalties, pins, hole-1 tee), run2.decode_course
   (min-marginals), confidence.hole_conf_feats + fix_feats and the logistic calibrator (pathroute_calib/1 or /2), and
   resolve2.Session, over the per-course decoder inputs build_library_play.py exports (pathroute_decoder/1, SCHEMA.md
   "Card-blind routing in the browser").

     const S = new PathRoute.Session(R)        // R = record.route (pathroute_decoder/1)
     S.confirmPair(number, tee, green)         // "hole N is this tee + green" (number null = pair only)
     S.rejectPair(tee, green)                  // "no": that tee's complex never plays to this green
     S.notAHole(green)                         // a practice green
     S.holeOne(tee)                            // "this tee is hole 1"
     const {holes, conf} = S.solve()           // holes [{number, g, t, boxes, L, loop}] + calibrated pair confidence
     S.ask(thr)                                // index of the lowest-confidence unconfirmed hole below thr, or null

   Parity: course_data/app/test_pathroute.js decodes the exported benchmark fixtures with and without facts and
   compares with the Python decode written next to them (fixtures/pathroute/<slug>.json). Floating point follows
   numpy's operation order (costs are sums of exported doubles; penalties are multiples of 0.5, exact in float32). */
(function (root) {
  "use strict";
  const INF = Infinity;

  /* ---------------------------------------------------------------- inputs -> dense matrices (decode.cost_mats) */
  function mats(R) {
    const nt = R.tees.length, ng = R.greens.length;
    const H = new Float64Array(nt * ng).fill(R.H_default);           // H[t*ng + g]
    for (const [t, g, c] of R.H) H[t * ng + g] = c;
    const T = new Float64Array(ng * nt).fill(R.T_default);           // T[g*nt + t] (walk weight applied)
    for (const [g, t, c] of R.T) T[g * nt + t] = c;
    return {nt, ng, H, T, S: Float64Array.from(R.S), E: Float64Array.from(R.E)};
  }

  function segCross(A, B, C, D) {                                     /* proper intersection of AB and CD */
    const orient = (P, Q, Rr) => (Q[0] - P[0]) * (Rr[1] - P[1]) - (Q[1] - P[1]) * (Rr[0] - P[0]);
    const o1 = orient(A, B, C), o2 = orient(A, B, D), o3 = orient(C, D, A), o4 = orient(C, D, B);
    return (o1 * o2 < 0) && (o3 * o4 < 0);
  }

  /* stable argsort of a numeric array (ties: lower index first; inf last) */
  function argsortStable(v, idx) {
    const o = idx ? idx.slice() : Array.from(v, (_, i) => i);
    o.sort((a, b) => (v[a] < v[b] ? -1 : v[a] > v[b] ? 1 : a - b));
    return o;
  }

  /* candidates: per green the K best tees by hole cost (unavailable -> inf); force_t replaces the K-th slot */
  function candidates(M, H, K, availT, availG, forceT) {
    const {nt, ng} = M;
    K = Math.min(K, nt);
    const top = [], hc = [];
    for (let g = 0; g < ng; g++) {
      const col = new Float64Array(nt);
      for (let t = 0; t < nt; t++) col[t] = (!availT[t] || !availG[g]) ? INF : H[t * ng + g];
      const o = argsortStable(col).slice(0, K);
      if (forceT != null && K >= 2 && !o.includes(forceT)) o[K - 1] = forceT;
      top.push(o);
      hc.push(o.map(t => col[t]));
    }
    return {top, hc, K};
  }

  function pairMats(top, K, tc, gc, comp, boxesOf, cross, reuse, shrink) {
    shrink = shrink == null ? 0.12 : shrink;
    const ng = top.length, P = ng * K, pt = new Int32Array(P), pg = new Int32Array(P);
    const A2 = [], B2 = [];
    for (let g = 0; g < ng; g++) for (let k = 0; k < K; k++) {
      const p = g * K + k, t = top[g][k];
      pt[p] = t; pg[p] = g;
      const A = tc[t], B = gc[g], v = [B[0] - A[0], B[1] - A[1]];
      A2.push([A[0] + shrink * v[0], A[1] + shrink * v[1]]);
      B2.push([B[0] - shrink * v[0], B[1] - shrink * v[1]]);
    }
    const PEN = new Float64Array(P * P);
    for (let a = 0; a < P; a++) for (let b = 0; b < P; b++) {
      if (pg[a] === pg[b]) continue;                                  // X[same_g] = 0, R[same_g] = 0
      const X = segCross(A2[a], B2[a], A2[b], B2[b]) ? 1 : 0;
      let Rr = comp[pt[a]] === comp[pt[b]] ? 1 : 0;
      if (boxesOf) Rr = Math.max(Rr, boxesOf[pt[a]][pt[b]] ? 1 : 0, boxesOf[pt[b]][pt[a]] ? 1 : 0);
      let pen = Math.fround(Math.fround(cross * X) + Math.fround(reuse * Rr));
      if (pt[a] === pt[b]) pen = Math.fround(pen + 50.0);              // one tee box never serves two holes
      PEN[a * P + b] = pen;
    }
    return {PEN, pt, pg, P};
  }

  /* beam_loop2: one loop of n holes. -> [greens, tees, cost, conf] or null */
  function beamLoop2(M, H, n, availG, availT, tc, gc, comp, boxesOf, o) {
    const {nt, ng, T, S, E} = M;
    const K0 = o.K == null ? 6 : o.K, beam = o.beam == null ? 4000 : o.beam, mid = o.mid;
    const cross = o.cross == null ? 1.5 : o.cross, reuse = o.reuse == null ? 4.0 : o.reuse;
    const pins = {};
    for (const [k, v] of Object.entries(o.pins || {})) if (+k >= 1 && +k <= n) pins[+k] = v;
    const first = o.first || null;
    const cd = candidates(M, H, K0, availT, availG, first ? o.firstForce : null), K = cd.K;
    const {PEN, pt, pg, P} = pairMats(cd.top, K, tc, gc, comp, boxesOf, cross, reuse);
    const hcf = new Float64Array(P);
    for (let g = 0; g < ng; g++) for (let k = 0; k < K; k++) hcf[g * K + k] = cd.hc[g][k];
    const Tstep = new Float64Array(ng * P), Tmid = new Float64Array(ng * P);
    for (let g = 0; g < ng; g++) for (let p = 0; p < P; p++) {
      const w = T[g * nt + pt[p]];
      Tstep[g * P + p] = w + hcf[p];
      Tmid[g * P + p] = ((w + S[pt[p]]) + hcf[p]) + E[g];
    }
    const s0 = new Float64Array(P);
    for (let p = 0; p < P; p++) s0[p] = S[pt[p]] + hcf[p];
    const stepOk = {};
    const pinKeys = Object.keys(pins).map(Number);
    if (pinKeys.length || first) {
      const pinP = {};
      for (const k of pinKeys) {
        const [t, g] = pins[k];
        let hit = -1;
        for (let p = 0; p < P; p++) if (pt[p] === t && pg[p] === g) { hit = p; break; }
        if (hit < 0) return null;
        pinP[k] = hit;
      }
      const pinnedG = new Map();
      for (const k of pinKeys) pinnedG.set(pins[k][1], k);
      for (let k = 1; k <= n; k++) {
        const ok = new Uint8Array(P).fill(1);
        if (k in pinP) { ok.fill(0); ok[pinP[k]] = 1; }
        for (const [g, kk] of pinnedG) if (kk !== k) for (let p = 0; p < P; p++) if (pg[p] === g) ok[p] = 0;
        if (k === 1 && first) for (let p = 0; p < P; p++) if (!first.has(pt[p])) ok[p] = 0;
        stepOk[k] = ok;
      }
      if (stepOk[1]) for (let p = 0; p < P; p++) if (!stepOk[1][p]) s0[p] = INF;
    }
    let pLast = [], cost = [];
    for (let p = 0; p < P; p++) if (isFinite(s0[p])) { pLast.push(p); cost.push(s0[p]); }
    let nb = pLast.length;
    let gl = pLast.map(p => pg[p]);
    let used = new Uint8Array(nb * ng);                               // greens used per state (the bitmask)
    for (let b = 0; b < nb; b++) used[b * ng + gl[b]] = 1;
    const numeric = ng <= 46;                                        /* numeric keys while 2^ng * 64 stays exact */
    const pow2 = Array.from({length: ng}, (_, x) => Math.pow(2, x));
    let mask = new Float64Array(nb);
    for (let b = 0; b < nb; b++) mask[b] = pow2[gl[b]];
    let pen = new Float64Array(nb * P);
    for (let b = 0; b < nb; b++) for (let q = 0; q < P; q++) pen[b * P + q] = PEN[pLast[b] * P + q];
    const hist = [[new Int32Array(nb).fill(-1), Int32Array.from(pLast)]];
    for (let k = 2; k <= n; k++) {
      const Ts = (mid && k === mid + 1) ? Tmid : Tstep, ok = stepOk[k];
      const flat = new Float64Array(nb * ng), kbA = new Int32Array(nb * ng);
      for (let b = 0; b < nb; b++) {
        const cb = cost[b], row = gl[b] * P, pr = b * P;
        for (let g = 0; g < ng; g++) {
          let best = INF, kb = 0;
          if (!used[b * ng + g]) {
            for (let kk = 0; kk < K; kk++) {
              const p = g * K + kk;
              if (ok && !ok[p]) continue;
              const c = (cb + Ts[row + p]) + pen[pr + p];
              if (c < best) { best = c; kb = kk; }                   // first minimum (np.argmin)
            }
          }
          flat[b * ng + g] = best; kbA[b * ng + g] = kb;
        }
      }
      let nk = 0;
      for (let i = 0; i < flat.length; i++) if (flat[i] !== INF) nk++;
      const keep = new Int32Array(nk);
      nk = 0;
      for (let i = 0; i < flat.length; i++) if (flat[i] !== INF) keep[nk++] = i;
      if (!keep.length) return null;
      /* the stable cost order of `keep`, but only as deep as needed: sort the entries at or under the m-th smallest
         cost (native numeric sort finds it), dedup, and go deeper only if fewer than `beam` keys came out */
      let order, firstIdx, m = Math.min(keep.length, 2 * beam);
      const vals = new Float64Array(keep.length);
      for (let i = 0; i < keep.length; i++) vals[i] = flat[keep[i]];
      for (;;) {
        const thr = m >= keep.length ? INF : kth(vals, m - 1);
        const sub = m >= keep.length ? Array.from(keep) : Array.from(keep.filter(i => flat[i] <= thr));
        order = argsortStable(flat, sub);
        const seen = new Set();
        firstIdx = [];
        for (let i = 0; i < order.length; i++) {
          const b = Math.floor(order[i] / ng), g = order[i] % ng;
          const key = numeric ? (mask[b] + pow2[g]) * 64 + g : stateKey(used, b, ng, g);   // (greens used, last green)
          if (!seen.has(key)) { seen.add(key); firstIdx.push(i); if (firstIdx.length >= beam) break; }
        }
        if (firstIdx.length >= beam || sub.length >= keep.length) break;
        m = Math.min(keep.length, m * 4);
      }
      /* np.unique(return_index) gives first occurrences; sorted and cut to the beam = the first `beam` distinct keys
         in cost order, which is what the early break above keeps */
      const nb2 = firstIdx.length, par = new Int32Array(nb2), gN = new Int32Array(nb2), pN = new Int32Array(nb2);
      const cost2 = new Float64Array(nb2), used2 = new Uint8Array(nb2 * ng), pen2 = new Float64Array(nb2 * P), mask2 = new Float64Array(nb2);
      for (let j = 0; j < nb2; j++) {
        const oi = order[firstIdx[j]], b = Math.floor(oi / ng), g = oi % ng;
        par[j] = b; gN[j] = g; pN[j] = g * K + kbA[b * ng + g]; cost2[j] = flat[oi];
        for (let x = 0; x < ng; x++) used2[j * ng + x] = used[b * ng + x];
        used2[j * ng + g] = 1;
        mask2[j] = mask[b] + pow2[g];
        const pb = b * P, pp = pN[j] * P, pj = j * P;
        for (let q = 0; q < P; q++) pen2[pj + q] = pen[pb + q] + PEN[pp + q];   // multiples of 0.5: exact as float32
      }
      nb = nb2; cost = cost2; used = used2; pen = pen2; mask = mask2; gl = gN;
      hist.push([par, pN]);
    }
    const fin = Array.from(cost, (c, b) => c + E[gl[b]]);
    const o2 = argsortStable(fin), best = o2[0];
    let z = 0;
    for (const i of o2.slice(0, 500)) z += Math.exp(-(fin[i] - fin[best]));
    const conf = 1.0 / z;
    const seq = [];
    let i = best;
    for (let h = hist.length - 1; h >= 0; h--) { seq.push(hist[h][1][i]); i = hist[h][0][i]; }
    seq.reverse();
    return [seq.map(p => pg[p]), seq.map(p => pt[p]), fin[best], conf];
  }

  /* k-th smallest (0-based) of a Float64Array, in place (Hoare quickselect) */
  function kth(a, k) {
    let lo = 0, hi = a.length - 1;
    while (lo < hi) {
      const piv = a[(lo + hi) >> 1];
      let i = lo, j = hi;
      while (i <= j) {
        while (a[i] < piv) i++;
        while (a[j] > piv) j--;
        if (i <= j) { const t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }
      }
      if (k <= j) hi = j; else if (k >= i) lo = i; else return a[k];
    }
    return a[k];
  }

  function stateKey(used, b, ng, g) {
    let key = "";
    for (let x = 0; x < ng; x++) key += (used[b * ng + x] || x === g) ? "1" : "0";
    return key + ":" + g;
  }

  function boxSets(tc) {
    return tc.map(a => tc.map(b => Math.hypot(a[0] - b[0], a[1] - b[1]) < 45));
  }

  const FIX_BONUS = 30.0;
  /* decode2.apply_fix: golfer facts -> hole-cost matrix */
  function applyFix(M, H0, comp, fix) {
    const {nt, ng} = M, H = Float64Array.from(H0);
    const pairs = (fix && fix.pairs) || [], fixedT = new Set(pairs.map(p => p[1]));
    for (const [, t, g] of pairs) {
      for (let c = 0; c < nt; c++) if (comp[c] === comp[t] && (!fixedT.has(c) || c === t)) for (let x = 0; x < ng; x++) H[c * ng + x] = INF;
      for (let x = 0; x < nt; x++) H[x * ng + g] = INF;
    }
    for (const [, t, g] of pairs) {
      for (let x = 0; x < ng; x++) H[t * ng + x] = INF;
      H[t * ng + g] = Math.min(H0[t * ng + g], M.BIG) - FIX_BONUS;
    }
    for (const g of (fix && fix.not_green) || []) for (let x = 0; x < nt; x++) H[x * ng + g] = INF;
    const fp = new Set(pairs.map(p => p[1] + "," + p[2]));
    for (const [t, g] of (fix && fix.reject) || []) {
      if (fp.has(t + "," + g)) continue;
      for (let c = 0; c < nt; c++) if (comp[c] === comp[t]) H[c * ng + g] = INF;
      H[t * ng + g] = INF;
    }
    for (const [t, g, w] of (fix && fix.sticky) || []) {     /* sticky re-solve: the previous decode's pairs (solver state) */
      if (isFinite(H[t * ng + g])) H[t * ng + g] = H[t * ng + g] - w;
    }
    return H;
  }

  /* decode2.decode2 -> {holes, conf, cost} */
  function decode2(M, R, comp, o) {
    const kind = R.kind, n = (kind === 9 || kind === 27) ? 9 : 18;
    const loops = ({9: 1, 18: 1, 27: 3, 36: 2})[kind] || Math.max(1, Math.round(kind / n));
    const fix = o.fix || null;
    let H = o.H || M.H;
    if (fix) H = applyFix(M, H, comp, fix);
    const pins = {};
    if (loops === 1) for (const [k, t, g] of (fix && fix.pairs) || []) if (k != null) pins[k] = [t, g];
    let first = null;
    if (fix && fix.first_tee != null) {
      const ft = fix.first_tee;
      first = new Set();
      for (let c = 0; c < M.nt; c++) if (comp[c] === comp[ft]) first.add(c);
      first.add(ft);
      if (pins[1]) first.add(pins[1][0]);
    }
    const availG = new Uint8Array(M.ng).fill(1), availT = new Uint8Array(M.nt).fill(1);
    const tc = R.tc, gc = R.gc, bo = M.boxesOf;
    const fixedT = new Uint8Array(M.nt);                       /* confirmed tees are never another hole's box */
    for (const [, t] of (fix && fix.pairs) || []) fixedT[t] = 1;
    const out = [], confs = [], costs = [];
    for (let li = 0; li < loops; li++) {
      const r = beamLoop2(M, H, n, availG, availT, tc, gc, comp, bo, {
        K: o.K, beam: o.beam, mid: n === 18 ? 9 : null, cross: o.cross, reuse: o.reuse,
        pins: li === 0 ? pins : null, first: li === 0 ? first : null, firstForce: (first && li === 0) ? fix.first_tee : null});
      if (!r) break;
      const [gs, ts, c, conf] = r;
      confs.push(conf); costs.push(c);
      for (let k = 0; k < gs.length; k++) {
        const g = gs[k], t = ts[k], gp = gc[g], tp = tc[t];
        const dd = Math.max(Math.hypot(gp[0] - tp[0], gp[1] - tp[1]), 1.0), u = [(gp[0] - tp[0]) / dd, (gp[1] - tp[1]) / dd];
        const box = new Set();
        for (let b = 0; b < M.nt; b++) {
          const rel = [tc[b][0] - tp[0], tc[b][1] - tp[1]];
          const lat = Math.abs(rel[0] * u[1] - rel[1] * u[0]);
          if (Math.hypot(rel[0], rel[1]) < 80 && lat < 22 && availT[b]) box.add(b);
          if (comp[b] === comp[t] && availT[b]) box.add(b);
        }
        box.delete(t);
        const boxes = Array.from(box).filter(b => !fixedT[b]).sort((a, b) => a - b);
        let L = -INF;
        for (const b of boxes.concat([t])) L = Math.max(L, Math.hypot(gp[0] - tc[b][0], gp[1] - tc[b][1]));
        out.push({number: k + 1, g, t, boxes, L, loop: li});
        availG[g] = 0; availT[t] = 0;
        for (const b of boxes) availT[b] = 0;
        for (let c2 = 0; c2 < M.nt; c2++) if (comp[c2] === comp[t] && !fixedT[c2]) availT[c2] = 0;
      }
    }
    let conf = 0, cost = INF;
    if (confs.length) { conf = confs.reduce((a, b) => a * b, 1); cost = costs.reduce((a, b) => a + b, 0); }
    return {holes: out, conf, cost};
  }

  /* confidence.hole_conf_feats + fix_feats (CONF_F2 order) */
  function confFeats(M, holes, routeConf, mm, fix, Hf, freePairs) {
    const {nt, ng, H, T} = M;
    const pairs = (fix && fix.pairs) || [], fixed = new Set(pairs.map(p => p[1] + "," + p[2]));
    const nf = holes.filter(h => fixed.has(h.t + "," + h.g)).length, nn = Math.max(holes.length, 1);
    return holes.map((h, i) => {
      const {t, g} = h, own = new Set([t].concat(h.boxes));
      const colMin = (HH) => { let m = INF; for (let x = 0; x < nt; x++) if (!own.has(x)) m = Math.min(m, HH[x * ng + g]); return m; };
      const rowMin = (HH) => { let m = INF; for (let x = 0; x < ng; x++) if (x !== g) m = Math.min(m, HH[t * ng + x]); return m; };
      const htg = H[t * ng + g];
      const prev = i > 0 && holes[i - 1].loop === h.loop ? T[holes[i - 1].g * nt + t] : NaN;
      const next = i + 1 < holes.length && holes[i + 1].loop === h.loop ? T[g * nt + holes[i + 1].t] : NaN;
      const m = mm[i];
      let nb = 0;
      for (const j of [i - 1, i + 1]) if (j >= 0 && j < holes.length && holes[j].loop === h.loop && fixed.has(holes[j].t + "," + holes[j].g)) nb++;
      const base = isFinite(Hf[t * ng + g]) ? Hf[t * ng + g] : htg;
      return [Math.exp(-htg), Math.min(colMin(H) - htg, 14), Math.min(rowMin(H) - htg, 14),
        isFinite(prev) ? Math.exp(-prev) : 0.5, isFinite(next) ? Math.exp(-next) : 0.5,
        routeConf, Math.min(m, 30.0), Math.min(Math.max(m, 0), 30) > 3 ? 1 : 0, h.L, 0,
        nf / nn, nb, freePairs ? (freePairs.has(t + "," + g) ? 0 : 1) : 0,
        Math.min(colMin(Hf) - base, 14), Math.min(rowMin(Hf) - base, 14)];
    });
  }

  /* calibrator: pathroute_calib/2 (confidence.Calib2) or /1 (confidence.Calib, 9 transformed columns) */
  function calibrate(C, X) {
    return X.map(x => {
      const mm = Math.log1p(Math.max(x[6], 0));
      let z;
      if (C.schema === "pathroute_calib/2") {
        const ff = x[10];
        const v = [x[0], x[1], x[2], x[3], x[4], x[5], mm, x[7], x[8] / 300.0, ff, x[11], x[12],
          Math.min(x[13], 14), Math.min(x[14], 14), mm * ff, x[5] * ff];
        z = C.intercept; for (let i = 0; i < v.length; i++) z += C.coef[i] * v[i];
      } else {
        const v = [x[0], x[1], x[2], x[3], x[4], x[5], mm, x[7], x[8] / 300.0];
        z = C.intercept; for (let i = 0; i < v.length; i++) z += C.coef[i] * v[i];
      }
      return 1.0 / (1.0 + Math.exp(-z));
    });
  }

  function hasFix(fix) {
    return !!(fix && ((fix.pairs && fix.pairs.length) || (fix.not_green && fix.not_green.length) ||
      (fix.reject && fix.reject.length) || fix.first_tee != null));
  }

  /* run2.decode_course: decode + per-hole min-marginals + confidence features. As a job: courseJob() decodes the route,
     each jobStep() adds one hole's min-marginal (one smaller-beam re-decode), jobFinish() builds the features, so a
     page can show the re-solved pairing at once and fill the confidences in over the next frames. */
  function courseJob(M, R, comp, fix, freePairs, mmSkip) {
    const cfg = R.cfg, kw = {K: cfg.K, cross: cfg.cross, reuse: cfg.reuse, fix};
    const d = decode2(M, R, comp, Object.assign({beam: cfg.beam}, kw));
    const fixed = new Set(((fix && fix.pairs) || []).map(p => p[1] + "," + p[2]));
    return {M, R, comp, fix, freePairs, kw, d, mm: [], fixed, skip: mmSkip || new Set()};
  }
  function jobStep(J) {
    const {M, R, comp, d} = J, h = d.holes[J.mm.length];
    if (!h) return true;
    if (J.fixed.has(h.t + "," + h.g) || J.skip.has(h.t + "," + h.g)) J.mm.push(30.0);
    else {
      const H2 = Float64Array.from(M.H);
      for (let c = 0; c < M.nt; c++) if (comp[c] === comp[h.t]) H2[c * M.ng + h.g] = INF;
      H2[h.t * M.ng + h.g] = INF;
      const c2 = decode2(M, R, comp, Object.assign({beam: R.cfg.mm_beam, H: H2}, J.kw)).cost;
      J.mm.push(isFinite(c2) ? c2 - d.cost : 30.0);
    }
    return J.mm.length >= d.holes.length;
  }
  function jobFinish(J) {
    const {M, R, comp, fix, d} = J;
    if (!d.holes.length) return {holes: [], conf: d.conf, X: []};
    const hf = hasFix(fix);
    let freePairs = J.freePairs;
    if (hf && !freePairs) freePairs = new Set(decode2(M, R, comp, {beam: R.cfg.beam, K: R.cfg.K, cross: R.cfg.cross, reuse: R.cfg.reuse}).holes.map(h => h.t + "," + h.g));
    const Hf = hf ? applyFix(M, M.H, comp, fix) : M.H;
    return {holes: d.holes, conf: d.conf, X: confFeats(M, d.holes, d.conf, J.mm, fix, Hf, hf ? freePairs : null)};
  }
  function decodeCourse(M, R, comp, fix, freePairs, mmSkip) {
    const J = courseJob(M, R, comp, fix, freePairs, mmSkip);
    while (!jobStep(J)) { /* every hole's min-marginal */ }
    return jobFinish(J);
  }

  const parFromLen = (L, c3, c4) => L <= (c3 || 225) ? 3 : (L <= (c4 || 450) ? 4 : 5);

  /* resolve2.STICKY / sticky_w: sticky re-solve (the previous solve's unconfirmed pairs get alpha * conf nats, pin_w
     once conf >= pin; a pair that survives keeps its confidence). R.sticky (exported) overrides; null = plain re-solve. */
  const STICKY = {alpha: 0.0, pin: 0.0, pin_w: 30.0, keep: true, cap: 1.0, boxes: false};
  const stickyW = (c, st) => c >= st.pin ? st.pin_w : st.alpha * c;
  /* resolve2.POLICY: the shipped confirm-tap policy (zero_tap PATHROUTE.md "Fully right"): plain full re-solve
     (sticky null; an exported R.sticky is ignored unless R.policy names it) after every answer (yes / not_hole
     "solve"; "keep" / "drop" = no re-solve after a "yes" / "not a hole"), ask the lowest-confidence unconfirmed hole
     (< cap) until P(every pair right) = product of the unconfirmed confidences >= target; h1 "first" = on a 9 / 18-hole
     course "which tee is hole 1?" before any hole (needHole1). R.policy (exported) overrides. */
  const POLICY = {target: 0.9, cap: 0.999, yes: "solve", not_hole: "solve", sticky: null, h1: "first"};

  /* resolve2.Session */
  class Session {
    constructor(R, fix, sticky) {
      if (!R || R.schema !== "pathroute_decoder/1") throw new Error("not a pathroute_decoder/1 record");
      this.R = R;
      this.M = mats(R);
      this.M.BIG = R.BIG;
      this.M.boxesOf = boxSets(R.tc);
      this.comp = R.comp;
      this.fix = {pairs: [], not_green: [], first_tee: null, reject: []};
      if (fix) for (const k of Object.keys(this.fix)) if (fix[k] != null) this.fix[k] = Array.isArray(fix[k]) ? fix[k].map(x => Array.isArray(x) ? x.slice() : x) : fix[k];
      this.holes = []; this.conf = []; this.routeConf = 0; this.free = null;
      this.policy = Object.assign({}, POLICY, R.policy || {});
      this.sticky = sticky !== undefined ? sticky : this.policy.sticky;
      this.prev = new Map();                                         /* "t,g" -> conf of the previous solve's unconfirmed holes */
    }
    confirmPair(number, tee, green) {
      this.fix.pairs = this.fix.pairs.filter(p => p[2] !== green && p[1] !== tee && (number == null || p[0] !== number));
      this.fix.pairs.push([number == null ? null : number, tee, green]);
      this.fix.reject = this.fix.reject.filter(r => !(r[0] === tee && r[1] === green));
    }
    /* resolve2.Session.confirm_yes: "yes, hole i is right as decoded" -> confirmed without a re-solve */
    confirmYes(i, number) {
      const h = this.holes[i];
      this.confirmPair(number == null ? null : number, h.t, h.g);
      if (this.conf) { this.conf = this.conf.slice(); this.conf[i] = 1.0; }
      this.prev.delete(h.t + "," + h.g);
    }
    /* resolve2.Session.drop_hole: "not a hole" for hole i's green without a re-solve (the hole leaves the route) */
    dropHole(i) {
      const h = this.holes[i];
      this.notAHole(h.g);
      this.prev.delete(h.t + "," + h.g);
      this.holes = this.holes.filter((x, k) => k !== i);
      if (this.conf) this.conf = this.conf.filter((x, k) => k !== i);
    }
    rejectPair(tee, green) {
      if (!this.fix.reject.some(r => r[0] === tee && r[1] === green)) this.fix.reject.push([tee, green]);
      this.fix.pairs = this.fix.pairs.filter(p => !(p[1] === tee && p[2] === green));
    }
    notAHole(green) { if (!this.fix.not_green.includes(green)) this.fix.not_green.push(green); this.fix.pairs = this.fix.pairs.filter(p => p[2] !== green); }
    holeOne(tee) { this.fix.first_tee = tee; }
    fixedPairs() { return new Set(this.fix.pairs.map(p => p[1] + "," + p[2])); }
    freePairs() {
      if (!this.free) this.free = new Set(decode2(this.M, this.R, this.comp, {beam: this.R.cfg.beam, K: this.R.cfg.K, cross: this.R.cfg.cross, reuse: this.R.cfg.reuse}).holes.map(h => h.t + "," + h.g));
      return this.free;
    }
    pyFix() {                                                        /* the Python fix dict (decode2.apply_fix) */
      const f = {pairs: this.fix.pairs, not_green: this.fix.not_green, first_tee: this.fix.first_tee};
      if (this.fix.reject.length) f.reject = this.fix.reject;
      return f;
    }
    /* resolve2.Session.solve_fix: the facts + (sticky) the previous solve's unconfirmed pairs */
    solveFix() {
      const f = this.pyFix(), st = this.sticky;
      if (!st || !this.prev.size || !hasFix(f)) return f;
      const fp = this.fixedPairs();
      const sk = Array.from(this.prev.entries()).map(([k, c]) => { const [t, g] = k.split(",").map(Number); return [t, g, c]; })
        .filter(([t, g]) => !fp.has(t + "," + g)).sort((a, b) => a[0] - b[0] || a[1] - b[1])
        .map(([t, g, c]) => [t, g, stickyW(c, st)]).filter(x => x[2] > 0);
      return sk.length ? Object.assign({}, f, {sticky: sk}) : f;
    }
    /* begin(): decode with every fact (holes available at once, conf null); step(): one more min-marginal, true when
       the confidences are in; solve() = begin + steps */
    begin() {
      const fr = this.freePairs(), st = this.sticky;
      this.keep = (st && st.keep && hasFix(this.pyFix())) ? new Map(this.prev) : new Map();
      const skip = new Set(this.keep.keys());
      let J = courseJob(this.M, this.R, this.comp, this.solveFix(), fr, skip);
      if (!J.d.holes.length && this.fix.first_tee != null) { this.fix.first_tee = null; J = courseJob(this.M, this.R, this.comp, this.solveFix(), fr, skip); }
      if (this.keep.size && st.boxes) J.d.holes = this.keepBoxes(J.d.holes, this.keep);
      this.job = J; this.holes = J.d.holes; this.routeConf = J.d.conf; this.conf = null; this.X = null;
      return this.holes;
    }
    /* resolve2.Session.keep_boxes: a kept pair keeps its previous box set, minus tees now used by another hole */
    keepBoxes(holes, keep) {
      const pb = this.prevBoxes || new Map(), tc = this.R.tc, gc = this.R.gc;
      const kept = holes.map(h => keep.has(h.t + "," + h.g) && pb.has(h.t + "," + h.g));
      const taken = new Set(holes.map(h => h.t));
      holes.forEach((h, i) => { if (!kept[i]) for (const b of h.boxes) taken.add(b); });
      return holes.map((h, i) => {
        if (!kept[i]) return h;
        const bx = pb.get(h.t + "," + h.g).filter(b => !taken.has(b)).sort((a, b) => a - b);
        let L = -INF;
        for (const b of bx.concat([h.t])) L = Math.max(L, Math.hypot(gc[h.g][0] - tc[b][0], gc[h.g][1] - tc[b][1]));
        return Object.assign({}, h, {boxes: bx, L});
      });
    }
    step() {
      const J = this.job;
      if (!J) return true;
      if (!jobStep(J)) return false;
      const cal = hasFix(J.fix) && this.R.calib_fix ? this.R.calib_fix : this.R.calib;
      const r = jobFinish(J), c = r.holes.length ? calibrate(cal, r.X) : [], fp = this.fixedPairs();
      this.X = r.X; this.job = null;
      const keep = this.keep || new Map(), st = this.sticky;
      const cap = (st && keep.size) ? (st.cap == null ? 1.0 : st.cap) : 1.0;      /* a pair the re-solve moved: at most cap */
      const cr = r.holes.map((h, i) => { const k = h.t + "," + h.g; return fp.has(k) ? 1.0 : (keep.has(k) ? keep.get(k) : Math.min(c[i], cap)); });
      /* holes answered with "yes" / "not a hole" between begin() and the last step keep their answer (conf 1 / gone) */
      const ck = new Map(r.holes.map((h, i) => [h.t + "," + h.g, cr[i]]));
      this.conf = this.holes.map(h => { const k = h.t + "," + h.g; return fp.has(k) ? 1.0 : (ck.has(k) ? ck.get(k) : 0); });
      this.prev = new Map();
      r.holes.forEach((h, i) => { const k = h.t + "," + h.g; if (!fp.has(k)) this.prev.set(k, cr[i]); });
      this.prevBoxes = new Map(r.holes.map(h => [h.t + "," + h.g, h.boxes.slice()]));
      return true;
    }
    solve() {
      this.begin();
      while (!this.step()) { /* min-marginals */ }
      return {holes: this.holes, conf: this.conf};
    }
    /* resolve2.Session.p_all / need / ask_all / answer: the shipped policy (POLICY) */
    pAll() {
      if (!this.conf || !this.holes.length) return 0;
      const fp = this.fixedPairs();
      let p = 1;
      this.holes.forEach((h, i) => { if (!fp.has(h.t + "," + h.g)) p *= Math.min(1, Math.max(0, this.conf[i])); });
      return p;
    }
    need(target) {
      target = target == null ? this.policy.target : target;
      if (!this.conf) return [];
      const fp = this.fixedPairs(), c = this.conf.map(x => Math.min(1, Math.max(0, x)));
      const order = this.holes.map((h, i) => i).filter(i => !fp.has(this.holes[i].t + "," + this.holes[i].g)).sort((a, b) => c[a] - c[b] || a - b);
      const out = [];
      for (let k = 0; k < order.length; k++) {
        let p = 1; for (let j = k; j < order.length; j++) p *= c[order[j]];
        if (p >= target || c[order[k]] >= this.policy.cap) break;
        out.push(order[k]);
      }
      return out;
    }
    /* resolve2.Session.need_hole1: the hole-1 tee is still to ask (POLICY h1 "first", 9 / 18 holes, none yet) */
    needHole1() { return this.policy.h1 === "first" && (this.R.kind === 9 || this.R.kind === 18) && this.fix.first_tee == null; }
    askAll(target) { const n = this.need(target); return n.length ? n[0] : null; }
    /* the golfer's answer about hole i: notHole, else "hole `number` is `tee` -> this green" (tee null / the decoded
       tee = "yes"). -> true when the route needs a re-solve (the caller runs solve(), or begin() + step()s) */
    answer(i, tee, number, notHole) {
      const h = this.holes[i], pol = this.policy;
      if (notHole) {
        if (pol.not_hole === "drop") { this.dropHole(i); return false; }
        this.notAHole(h.g);
      } else if (tee == null || tee === h.t) {
        if (pol.yes === "keep") { this.confirmYes(i, number); return false; }
        this.confirmPair(number == null ? null : number, h.t, h.g);
      } else this.confirmPair(number == null ? null : number, tee, h.g);
      return true;
    }
    ask(thr) {
      thr = thr == null ? 1.0 : thr;
      if (!this.conf) return null;
      const fp = this.fixedPairs();
      let best = null;
      this.holes.forEach((h, i) => { if (!fp.has(h.t + "," + h.g) && this.conf[i] < thr && (best === null || this.conf[i] < this.conf[best])) best = i; });
      return best;
    }
    holeRef(h) { const n = (this.R.kind === 9 || this.R.kind === 27) ? 9 : 18; return h.loop * n + h.number; }
    par(h) { return parFromLen(h.L, this.R.par_cuts && this.R.par_cuts[0], this.R.par_cuts && this.R.par_cuts[1]); }
    /* facts by OSM id (resolve2.Session.to_ids) */
    toIds() {
      const T = this.R.tees, G = this.R.greens;
      const f = {pairs: this.fix.pairs.map(([n, t, g]) => [n, T[t].id, G[g].id]), not_green: this.fix.not_green.map(g => G[g].id),
                 first_tee: this.fix.first_tee == null ? null : T[this.fix.first_tee].id};
      if (this.fix.reject.length) f.reject = this.fix.reject.map(([t, g]) => [T[t].id, G[g].id]);
      return f;
    }
    /* nearest tee / green (index) to a [lon, lat] within maxYd yds (equirectangular), or null */
    nearest(kind, ll, maxYd) {
      if (!Array.isArray(ll)) return null;
      const arr = kind === "tee" ? this.R.tees : this.R.greens;
      const kx = 111320.0 * Math.cos(ll[1] * Math.PI / 180) / 0.9144, ky = 110950.0 / 0.9144;
      let best = null, bd = maxYd == null ? 30 : maxYd;
      arr.forEach((x, i) => { const dd = Math.hypot((x.ll[0] - ll[0]) * kx, (x.ll[1] - ll[1]) * ky); if (dd <= bd) { bd = dd; best = i; } });
      return best;
    }
  }

  const api = {Session, STICKY, POLICY, stickyW, decode2, decodeCourse, courseJob, jobStep, jobFinish, applyFix, calibrate, mats, boxSets, parFromLen, hasFix};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.PathRoute = api;
})(typeof window !== "undefined" ? window : this);
