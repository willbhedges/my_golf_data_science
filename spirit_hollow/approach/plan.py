"""Approach targets (DECADE green boxes, any distance and lie) and par-5 go / lay-up decisions.

Everything is in the hole's ground frame (geom.Hole: yards east/north of the OSM green centroid).
"""
import json
import os
import sys

import numpy as np

import geom
import shots as S

SH = geom.SH
sys.path.insert(0, SH)
import course                                   # noqa: E402
import tee_strategy as t                        # noqa: E402
import yardage_book as yb                       # noqa: E402

FINAL = os.path.join(SH, "output", "final_decision.json")
SEV_NAME = {"water": "water", "ob": "ob", "recovery": "trees", "native": "native", "sand": "bunker"}
BAND = 12.0            # yds beyond each green edge searched for trouble
BAND_PENAL = 20.0      # ... for water / OB (a penalty further off still sets the side)
ROWS, ROW_HITS = 11, 2  # rays per side; rays that must hit a hazard for it to set the side
WIND_MODS = (-1, 0, 1, 2, 3)


# ------------------------------------------------------------------ tee shot finishing spots
def tee_pick(key):
    fd = json.load(open(FINAL))[str(key)]
    return fd["pick"], float(fd["aim"]), bool(fd.get("tie"))


def tee_finishes(hole, n=4000, seed=21):
    """Finishing spots of the calm-day tee pick (final_decision.json) under the prior-mean settings the
    wind page uses (wind_grid.set_prior_means): (xy yds, lie names, club, aim)."""
    import wind_grid as WG                       # sets t.HOLES = course.HOLES
    t.HOLES = course.HOLES
    saved = (dict(t.CLUBS), dict(t.IRONS), t.TREE_SEVERITY, t.NATIVE_LOST, dict(t.MISHIT_RATE))
    WG.set_prior_means()
    try:
        club, aim, _ = tee_pick(hole.key)
        z = S.z_draws(n, seed)
        pts = t.simulate(hole.key, club, aim, z=z)[0]
    finally:
        t.CLUBS, t.IRONS, t.TREE_SEVERITY, t.NATIVE_LOST, t.MISHIT_RATE = saved
    xy = hole.px_to_xy(pts)
    return xy, club, aim


# ------------------------------------------------------------------ DECADE box, any distance
def decade_base(dist):
    """DECADE baseline yds in from an edge: the card table 60-250 (yardage_book.TARGET), 3 inside 60,
    distance / 20 beyond 250 (the card's own slope)."""
    if dist > 250:
        return round(dist / 20.0)
    return yb.baseline_target(max(dist, 60))


def frame(hole, start):
    fwd = hole.green_c - np.asarray(start, float)
    fwd = fwd / np.linalg.norm(fwd)
    return fwd, geom.right_of(fwd)


def to_ld(hole, xy, fwd, right):
    rel = np.atleast_2d(xy) - hole.green_c
    return np.c_[rel @ right, rel @ fwd]


def from_ld(hole, ld, fwd, right):
    ld = np.atleast_2d(np.asarray(ld, float))
    return hole.green_c + ld[:, :1] * right + ld[:, 1:2] * fwd


def side_hazards(hole, raster, fwd, right, band=BAND_PENAL, band_near=BAND):
    """What sits off each edge of the green, seen from this direction: left/right/short/long ->
    DECADE category (water, ob, trees, native, bunker, rough). Rays leave the edge from ROWS lines
    spread across the green; a category counts for a side when it is hit within BAND yds of the edge
    (BAND_PENAL for water/OB) on at least ROW_HITS of them; the worst counting category wins.
    Also returns, per side, the share of rays that hit each category."""
    from matplotlib.path import Path
    g = to_ld(hole, hole.green, fwd, right)
    path = Path(g)
    lo, hi = g.min(axis=0), g.max(axis=0)
    span = np.arange(-60, 60.01, 0.5)
    ks = np.arange(1.0, band + 0.01, 1.0)
    out = {}
    for side in ("left", "right", "short", "long"):
        ax = 0 if side in ("left", "right") else 1          # coordinate that moves off the edge
        other = 1 - ax
        w = hi[other] - lo[other]
        rows = np.linspace(lo[other] + 0.1 * w, hi[other] - 0.1 * w, ROWS)
        hits = []
        for r in rows:
            pts = np.zeros((len(span), 2))
            pts[:, ax], pts[:, other] = span, r
            ins = span[path.contains_points(pts)]
            if not len(ins):
                continue
            edge = ins.min() if side in ("left", "short") else ins.max()
            sgn = -1 if side in ("left", "short") else 1
            q = np.zeros((len(ks), 2))
            q[:, ax], q[:, other] = edge + sgn * ks, r
            names = [SEV_NAME.get(geom.LIES[i], "rough") for i in raster.lie_id(from_ld(hole, q, fwd, right))]
            hit = {c for c, k in zip(names, ks) if c in ("water", "ob") or (k <= band_near and c != "rough")}
            hits.append(hit)
        share = {c: round(sum(c in h for h in hits) / len(hits), 2)
                 for c in ("water", "ob", "trees", "native", "bunker")} if hits else {}
        cats = [c for c in share if share[c] * len(hits) >= ROW_HITS]
        worst = max(cats, key=lambda c: yb.SEVERITY[c]) if cats else "rough"
        out[side] = (worst, {c: v for c, v in share.items() if v})
    return out


def decade_box(hole, raster, start, lie="fairway", wind=0, dist=None, step=0.25):
    """The DECADE edge rule (yardage_book.par3_plan) generalised to any approach: cushion = the card
    number for the distance x the lie's dispersion multiplier, + 3 water/OB, + 2 trees/long grass,
    + 1 bunker, + the wind modifier, in from each edge of the real green as seen from `start`."""
    from matplotlib.path import Path
    start = np.asarray(start, float)
    fwd, right = frame(hole, start)
    dist = float(np.linalg.norm(hole.green_c - start)) if dist is None else float(dist)
    g = to_ld(hole, hole.green, fwd, right)
    path = Path(g)
    haz = side_hazards(hole, raster, fwd, right)
    base = decade_base(dist)
    ml, md = S.LIE_MULT.get(lie, (1.0, 1.0))
    mult = {"left": ml, "right": ml, "short": md, "long": md}
    off = {k: max(base * mult[k] + yb.ADD[v[0]] + wind, 0.0) for k, v in haz.items()}
    sev = {k: yb.SEVERITY[v[0]] for k, v in haz.items()}

    def extent(axis, at):
        span = np.arange(-60, 60 + step, step)
        pts = np.c_[span, np.full_like(span, at)] if axis == 0 else np.c_[np.full_like(span, at), span]
        inside = span[path.contains_points(pts)]
        return (inside.min(), inside.max()) if len(inside) else (0.0, 0.0)

    lat_c = (g[:, 0].min() + g[:, 0].max()) / 2
    dep_c = (g[:, 1].min() + g[:, 1].max()) / 2
    for _ in range(3):
        f, b_ = extent(1, lat_c)
        d0, d1, how_d = yb._axis(f, b_, off["short"], off["long"], sev["short"], sev["long"])
        dep_c = (d0 + d1) / 2
        l, r = extent(0, dep_c)
        l0, l1, how_l = yb._axis(l, r, off["left"], off["right"], sev["left"], sev["right"])
        lat_c = (l0 + l1) / 2
    bl0, bl1, bd0, bd1 = l0, l1, d0, d1
    if bl1 - bl0 < 2:
        bl0, bl1 = lat_c - 1, lat_c + 1
    if bd1 - bd0 < 2:
        bd0, bd1 = dep_c - 1, dep_c + 1
    corners = np.array([(bl0, bd0), (bl1, bd0), (bl1, bd1), (bl0, bd1)])
    shape = clip_to_rect(g, bl0, bl1, bd0, bd1)      # the box, trimmed to the putting surface
    if len(shape) < 3:
        shape = corners
    return dict(dist=dist, lie=lie, wind=wind, base=float(base), haz={k: v[0] for k, v in haz.items()},
                haz_share={k: v[1] for k, v in haz.items()}, off=off, lat=(float(l0), float(l1)),
                dep=(float(d0), float(d1)), how_lat=how_l, how_dep=how_d, edges_lat=(float(l), float(r)),
                edges_dep=(float(f), float(b_)), aim_ld=(float(lat_c), float(dep_c)),
                aim_xy=from_ld(hole, [(lat_c, dep_c)], fwd, right)[0],
                box_xy=from_ld(hole, corners, fwd, right), shape_ld=shape,
                shape_xy=from_ld(hole, shape, fwd, right), green_ld=g, fwd=fwd, right=right)


def clip_to_rect(poly, x0, x1, y0, y1):
    """Sutherland-Hodgman: the part of polygon `poly` (N x 2) inside the axis-aligned rectangle."""
    out = [tuple(p) for p in np.asarray(poly, float)]
    for axis, val, keep_ge in ((0, x0, True), (0, x1, False), (1, y0, True), (1, y1, False)):
        if not out:
            break
        inp, out = out, []
        inside = (lambda p: p[axis] >= val) if keep_ge else (lambda p: p[axis] <= val)  # noqa: E731
        for i, cur in enumerate(inp):
            prev = inp[i - 1]
            if inside(cur):
                if not inside(prev):
                    out.append(_cross(prev, cur, axis, val))
                out.append(cur)
            elif inside(prev):
                out.append(_cross(prev, cur, axis, val))
    return np.array(out) if out else np.zeros((0, 2))


def _cross(a, b, axis, val):
    tt = (val - a[axis]) / (b[axis] - a[axis])
    return (a[0] + tt * (b[0] - a[0]), a[1] + tt * (b[1] - a[1]))


# ------------------------------------------------------------------ approach values
class Approach:
    """Expected strokes for approach shots into one green, aimed at the DECADE box centre."""

    def __init__(self, hole, raster=None, n_pins=16, m=150, seed=5):
        self.h = hole
        self.r = raster or geom.Raster(hole)
        self.pins = S.pins(hole, n_pins)
        self.z = S.z_draws(m, seed)
        self.grid = None

    def start_e(self, lie, dist):
        return S.baseline(lie if lie in S.SHORT or lie == "green" else "rough", np.maximum(dist, 2))

    def value(self, start, lie, aim=None, z=None):
        """Expected strokes from `start` in `lie` (incl. this shot), aiming at `aim` (default: the
        DECADE box centre for this start and lie). Non-targetable lies use the baselines."""
        start = np.asarray(start, float)
        dist = float(np.linalg.norm(start - self.h.green_c))
        if lie not in S.TARGETABLE:
            return float(self.after(start[None], np.zeros(1), lie_override=lie)[0])
        if lie == "green" or dist < 45:
            return float(self.after(start[None], np.zeros(1), lie_override=lie)[0])
        if aim is None:
            aim = decade_box(self.h, self.r, start, lie)["aim_xy"]
        fin, _ = S.shot(start, aim, lie, self.z if z is None else z)
        e0 = self.start_e(lie, dist)
        sc, _ = S.score_outcomes(self.h, self.r, fin, e0, self.pins)
        return 1.0 + float(sc.mean())

    def after(self, fin, start_e, lie_override=None):
        """Expected strokes to hole out from finishing points (third-shot values from the grid when
        the ball is a full shot away in a playable lie)."""
        fin = np.atleast_2d(fin)
        if lie_override is not None:
            ids = np.full(len(fin), geom.LIE_ID[lie_override], np.int8)
            lie = lie_override
            dc = np.hypot(*(fin - self.h.green_c).T)
            dp = np.hypot(fin[:, None, 0] - self.pins[None, :, 0], fin[:, None, 1] - self.pins[None, :, 1])
            if lie == "green":
                return S.putts(dp * 3).mean(axis=1)
            if lie in S.SHORT:
                v = S.baseline(lie, dc)
                near = dc < 45
                v[near] = S.baseline(lie, dp[near]).mean(axis=1)
                return v
            if lie == "native":
                return t.NATIVE_LOST * (1 + np.asarray(start_e, float)) + (1 - t.NATIVE_LOST) * S.baseline("recovery", dc)
            if lie == "water":
                return 1 + S.baseline("rough", np.maximum(dc, 10))
            if lie == "ob":
                return 1 + np.asarray(start_e, float)
            return S.baseline(lie, dc)
        sc, ids = S.score_outcomes(self.h, self.r, fin, start_e, self.pins)
        if self.grid is not None:
            dc = np.hypot(*(fin - self.h.green_c).T)
            for lie in ("fairway", "first_cut", "rough", "sand"):
                m = (ids == geom.LIE_ID[lie]) & (dc >= 45)
                if m.any():
                    v = self.interp(fin[m], lie)
                    ok = np.isfinite(v)
                    sub = sc[m]
                    sub[ok] = v[ok]
                    sc[m] = sub
        return sc

    # value grid (third shots after a lay-up)
    def build_grid(self, spacing=5.0, rmax=290.0, corridor=90.0):
        h = self.h
        lo = np.minimum(h.line.min(axis=0), h.green_c) - corridor
        hi = np.maximum(h.line.max(axis=0), h.green_c) + corridor
        xs = np.arange(lo[0], hi[0] + spacing, spacing)
        ys = np.arange(lo[1], hi[1] + spacing, spacing)
        V = {lie: np.full((len(ys), len(xs)), np.nan) for lie in ("fairway", "first_cut", "rough", "sand")}
        X, Y = np.meshgrid(xs, ys)
        P = np.c_[X.ravel(), Y.ravel()]
        dc = np.hypot(*(P - h.green_c).T)
        line = np.vstack([h.line[:-1], h.green_c])
        dline = np.full(len(P), np.inf)
        for a, b in zip(line[:-1], line[1:]):
            ab = b - a
            u = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
            dline = np.minimum(dline, np.hypot(*(P - (a + u[:, None] * ab)).T))
        use = (dc >= 40) & (dc <= rmax) & (dline <= corridor)
        aims = {}
        for idx in np.flatnonzero(use):
            p = P[idx]
            for lie in V:
                key = (round(float(dc[idx]) / 10), lie)
                b = decade_box(h, self.r, p, lie)          # aim depends on direction: per cell
                aims[key] = b
                V[lie].flat[idx] = self.value(p, lie, aim=b["aim_xy"])
        self.grid = dict(xs=xs, ys=ys, V=V)
        return self.grid

    def interp(self, pts, lie):
        g = self.grid
        xs, ys, V = g["xs"], g["ys"], g["V"][lie]
        fx = (pts[:, 0] - xs[0]) / (xs[1] - xs[0])
        fy = (pts[:, 1] - ys[0]) / (ys[1] - ys[0])
        i0 = np.clip(np.floor(fy).astype(int), 0, len(ys) - 2)
        j0 = np.clip(np.floor(fx).astype(int), 0, len(xs) - 2)
        ty, tx = np.clip(fy - i0, 0, 1), np.clip(fx - j0, 0, 1)
        v00, v01 = V[i0, j0], V[i0, j0 + 1]
        v10, v11 = V[i0 + 1, j0], V[i0 + 1, j0 + 1]
        w = np.stack([(1 - ty) * (1 - tx), (1 - ty) * tx, ty * (1 - tx), ty * tx])
        vals = np.stack([v00, v01, v10, v11])
        ok = np.isfinite(vals)
        wsum = (w * ok).sum(axis=0)
        out = np.where(wsum > 0.5, np.nansum(np.where(ok, vals, 0) * w, axis=0) / np.maximum(wsum, 1e-9), np.nan)
        inside = (fx >= 0) & (fx <= len(xs) - 1) & (fy >= 0) & (fy <= len(ys) - 1)
        return np.where(inside, out, np.nan)


# ------------------------------------------------------------------ SG check of the DECADE aim
def sg_aim_check(ap, starts, lies, m=60, step=2.0, seed=9):
    """Pin-averaged expected strokes of the DECADE box centre vs every aim point on the green (2-yd
    grid), over the given approach starts (playable lies). Returns the best aim and the gap."""
    h = ap.h
    z = S.z_draws(m, seed)
    keep = np.isin(lies, S.TARGETABLE) & (np.hypot(*(starts - h.green_c).T) >= 45)
    starts, lies = starts[keep], lies[keep]
    if not len(starts):
        return None
    lo, hi = h.green.min(axis=0), h.green.max(axis=0)
    gx, gy = np.meshgrid(np.arange(lo[0], hi[0], step), np.arange(lo[1], hi[1], step))
    cand = np.c_[gx.ravel(), gy.ravel()]
    cand = cand[h.green_path.contains_points(cand)]
    e0 = np.array([ap.start_e(l, np.linalg.norm(s - h.green_c)) for s, l in zip(starts, lies)])

    def ev(aim_of):
        tot = 0.0
        for s, l, e in zip(starts, lies, e0):
            fin, _ = S.shot(s, aim_of(s, l), l, z)
            sc, _ = S.score_outcomes(h, ap.r, fin, e, ap.pins)
            tot += sc.mean()
        return 1 + tot / len(starts)

    boxes = {}

    def decade_aim(s, l):
        k = (tuple(np.round(s, 1)), l)
        if k not in boxes:
            boxes[k] = decade_box(h, ap.r, s, l)["aim_xy"]
        return boxes[k]

    e_decade = ev(decade_aim)
    e_centre = ev(lambda s, l: h.green_c)
    evs = np.array([ev(lambda s, l, a=a: a) for a in cand])
    i = int(evs.argmin())
    return dict(e_decade=e_decade, e_centre=e_centre, e_best=float(evs[i]), best_xy=cand[i],
                n_starts=int(len(starts)), aims=cand, evs=evs)


# ------------------------------------------------------------------ par 5 second shots
LAYUP_L = np.arange(30, 171, 10)
LAYUP_OFF = np.arange(-25, 25.1, 5)


def layup_targets(hole):
    out = []
    for L in LAYUP_L:
        p, fwd = hole.along_line_from_green(float(L))
        r = geom.right_of(fwd)
        for o in LAYUP_OFF:
            out.append((float(L), float(o), p + o * r))
    return out


def par5_second(ap, starts, lies, m=100, seed=13, go_slack=20.0):
    """For each tee-shot finish: expected strokes of going for the green (DECADE box centre, max reach
    by lie) and of every lay-up target (hole-line distance L from the green, offset o yds right), each
    incl. the second shot. Returns per-start arrays."""
    h = ap.h
    z = S.z_draws(m, seed)
    targets = layup_targets(h)
    n = len(starts)
    E_go = np.full(n, np.nan)
    E_lay = np.full((n, len(targets)), np.nan)
    E_fixed = np.full(n, np.nan)             # non-playable lies: chip out / drop (baseline)
    dist = np.hypot(*(starts - h.green_c).T)
    for i, (s, lie) in enumerate(zip(starts, lies)):
        e0 = float(ap.start_e(lie, dist[i]))
        if lie not in S.TARGETABLE or lie == "green":
            E_fixed[i] = float(ap.after(s[None], np.array([e0]), lie_override=lie)[0])
            continue
        reach = S.REACH[lie]
        if dist[i] <= reach + go_slack:
            if dist[i] < 45:
                E_go[i] = float(ap.after(s[None], np.zeros(1), lie_override=lie)[0])
            else:
                aim = decade_box(h, ap.r, s, lie)["aim_xy"]
                fin, _ = S.shot(s, aim, lie, z)
                E_go[i] = 1 + float(ap.after(fin, e0).mean())
        for j, (L, o, p) in enumerate(targets):
            d = float(np.linalg.norm(p - s))
            if d > reach or L >= dist[i] - 20:
                continue
            fin, _ = S.shot(s, p, lie, z)
            E_lay[i, j] = 1 + float(ap.after(fin, e0).mean())
    return dict(targets=[(L, o) for L, o, _ in targets], target_xy=np.array([p for *_, p in targets]),
                E_go=E_go, E_lay=E_lay, E_fixed=E_fixed, dist=dist, lies=np.asarray(lies))


def summarize_par5(res):
    E_go, E_lay, E_fixed, dist, lies = res["E_go"], res["E_lay"], res["E_fixed"], res["dist"], res["lies"]
    best_lay = np.nanmin(np.where(np.isfinite(E_lay), E_lay, np.inf), axis=1)
    best_lay[~np.isfinite(best_lay)] = np.nan
    j_best = np.where(np.isfinite(E_lay).any(axis=1), np.nanargmin(np.where(np.isfinite(E_lay), E_lay, np.inf), axis=1), -1)
    playable = np.isnan(E_fixed)
    go_better = playable & np.isfinite(E_go) & ~(best_lay < E_go)
    policy = np.where(~playable, E_fixed, np.where(go_better, E_go, np.fmin(best_lay, E_go)))
    # one book lay-up target: the best average over the starts that lay up (where reachable)
    lay = playable & ~go_better
    fixed_choice = None
    if lay.any():
        sub = E_lay[lay]
        ok = np.isfinite(sub).mean(axis=0) >= 0.9
        if ok.any():
            mean = np.where(ok, np.nanmean(np.where(np.isfinite(sub), sub, np.nan), axis=0), np.inf)
            jj = int(np.argmin(mean))
            fixed_choice = dict(L=res["targets"][jj][0], off=res["targets"][jj][1], j=jj,
                                ev=float(mean[jj]), ev_by_L={})
            for L in sorted(set(x[0] for x in res["targets"])):
                cols = [k for k, x in enumerate(res["targets"]) if x[0] == L and ok[k]]
                if cols:
                    best_k = min(cols, key=lambda k: mean[k])
                    fixed_choice["ev_by_L"][int(L)] = (float(mean[best_k]), res["targets"][best_k][1])
    # go thresholds by lie (largest 10-yd distance bin where going wins at least half the time)
    thresh = {}
    for lie in ("fairway", "first_cut", "rough", "sand"):
        m = playable & (lies == lie) & np.isfinite(E_go)
        if m.sum() < 10:
            continue
        bins = np.arange(150, 300, 10)
        best = None
        for b in bins:
            mm = m & (dist >= b) & (dist < b + 10)
            if mm.sum() >= 5 and go_better[mm].mean() >= 0.5:
                best = int(b + 10)
        thresh[lie] = best
    return dict(p_go=float(go_better.mean()), p_lay=float(lay.mean()), p_fixed=float((~playable).mean()),
                ev_policy=float(np.mean(policy)), go_better=go_better, best_lay=best_lay, j_best=j_best,
                fixed=fixed_choice, go_threshold=thresh,
                ev_go_when_possible=float(np.nanmean(np.where(playable & np.isfinite(E_go), E_go, np.nan)))
                if (playable & np.isfinite(E_go)).any() else None,
                ev_lay_when_possible=float(np.nanmean(np.where(playable & np.isfinite(E_go), best_lay, np.nan)))
                if (playable & np.isfinite(E_go)).any() else None)


def go_sweep(ap, dists=range(150, 301, 10), lies=("fairway", "first_cut", "rough"), m=100, seed=17):
    """Go vs best lay-up from points on the hole line at each distance from the green, per lie:
    rows (dist, lie, E_go or None, E_best_layup or None, best (L, off))."""
    h = ap.h
    z = S.z_draws(m, seed)
    targets = layup_targets(h)
    rows = []
    for d in dists:
        s, _ = h.along_line_from_green(float(d))
        dist = float(np.linalg.norm(s - h.green_c))
        for lie in lies:
            e0 = float(ap.start_e(lie, dist))
            reach = S.REACH[lie]
            e_go = None
            if dist <= reach + 20:
                aim = decade_box(h, ap.r, s, lie)["aim_xy"]
                fin, _ = S.shot(s, aim, lie, z)
                e_go = 1 + float(ap.after(fin, e0).mean())
            best = None
            for L, o, p in targets:
                if np.linalg.norm(p - s) > reach or L >= dist - 20:
                    continue
                fin, _ = S.shot(s, p, lie, z)
                e = 1 + float(ap.after(fin, e0).mean())
                if best is None or e < best[0]:
                    best = (e, L, o)
            rows.append(dict(dist=round(dist, 1), lie=lie, e_go=e_go, e_lay=best[0] if best else None,
                             lay=(best[1], best[2]) if best else None))
    return rows
