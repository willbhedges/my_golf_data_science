"""Eagle Knoll par 3s: the expected-strokes-optimal target for an unknown pin (OPTIMIZE.md section 13, Nov 6 2026).

  OMP_NUM_THREADS=1 python3 course_data/courses/eagle_knoll/opt/par3_target.py solve   [--sets Back,Eagle,Middle]
  OMP_NUM_THREADS=1 python3 course_data/courses/eagle_knoll/opt/par3_target.py robust  [--sets Back]

`solve` writes opt/results/par3_target.json (full: surfaces, clubs, SEs) and the page file
course_data/courses/eagle_knoll/par3_targets.json (config "par3_targets"; read by course_data/courses/par3_targets.py).
`robust` writes opt/results/par3_robust.json.

Model (each piece is the engine's or the repo's existing model unless marked ASSUMED):
  * Ball: spirit_hollow/v2/model.shots at the central world: lateral sigma = 95 % width / 4 x 70/65, carry sigma =
    depth window x 1.25 / 4, rho 0.1, kappa 0.08, 12 % slight mishits (92-95 % carry, x1.15 lateral), 2.5 % heavy
    (65-85 %, x1.5), temperature carry x (1 - 0.00075 (70 - T)). Clubs: Long iron 210 / Mid iron 185 / 8-iron 162
    are the engine's; 5-, 7-, 9-iron, PW, GW are ASSUMED from the Spirit Hollow approach bag (~12-yd gaps,
    spirit_hollow/approach/REPORT.md), width and depth window scaled with carry like the engine's 8-iron.
  * Wind: spirit_hollow/wind.adjust per club (carry, width, depth incl. gust turbulence). The aim is the landing
    point, so the mean drift is aimed off (not a miss); only its scatter counts.
  * Terrain: each ball lands where its flight meets the 3DEP 1 m DEM: x = flat carry + K (z_tee - z(x)),
    K = 0.839 yd per yd of drop (the page's elevation factor: meta dz / green drop). Then it rolls the club's stated
    roll (total - carry, +/-25 %) along the line, x0.3 once in rough, stopping in sand / trees / water.
  * After the shot: pin-averaged expected strokes on a 0.5-yd raster. Pins uniform over the green polygon (truth
    map), at least 4 yds inside the edge (USGA guidance ~4-5 paces). Putting: Broadie by feet + 0.06 (5-hcp), plus
    a green-slope term from the DEM plane fit: +0.02 strokes per 1 % of downhill grade along the putt (ASSUMED
    size, full from 15 ft, 0 at 3 ft; uphill the same with the sign reversed). Off the green within 40 yds: short
    game by lie + 0.15 (5-hcp), beyond: the engine's amateur table. Trees: Broadie recovery row. Water: 1 + rough
    from the drop (pin distance, at least 10). OB: 1 + 3.2.
  * Statistics: common random numbers across aims and clubs; every margin is a paired per-swing mean with its SE.
"""
import argparse
import json
import os
import sys

import numpy as np
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
EK = os.path.dirname(HERE)
CD = os.path.dirname(os.path.dirname(EK))
ROOT = os.path.dirname(CD)
sys.path[:0] = [os.path.join(CD, "courses"), os.path.join(ROOT, "mozingo")]
OUT = os.path.join(HERE, "results")
PAGE = os.path.join(EK, "par3_targets.json")

SETS = {"Back": "truth", "Eagle": "truth_eagle", "Middle": "truth_middle"}
HOLES3 = (2, 6, 12, 16)
K_DROP = 0.839
RES = 0.5
LAT0, LAT1, DEP0, DEP1 = -70.0, 70.0, -90.0, 70.0

# (carry, total, width95, depth95) at 70 F on the flat; engine's: Long iron, Mid iron, 8-iron
BAG = {
    "Long iron": (210, 220, 40, 20), "5-iron": (198, 206, 37, 19), "Mid iron": (185, 192, 34, 18),
    "7-iron": (174, 180, 32, 17), "8-iron": (162, 167, 30, 16), "9-iron": (150, 154, 28, 15),
    "PW": (138, 141, 26, 14), "GW": (126, 128, 24, 13),
}
SHORT_NAME = {"Long iron": "4-iron", "Mid iron": "6-iron"}

PUTT_FT = np.array([1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 90], float)
PUTTS = np.array([1.00, 1.01, 1.04, 1.13, 1.23, 1.34, 1.50, 1.61, 1.78, 1.87, 1.98, 2.06, 2.14, 2.21, 2.40])
SHORT_D = np.array([2, 5, 10, 15, 20, 30, 40], float)
SHORT = {"fairway": [1.95, 2.05, 2.18, 2.30, 2.40, 2.52, 2.60], "rough": [2.10, 2.20, 2.34, 2.47, 2.59, 2.70, 2.78],
         "sand": [2.30, 2.37, 2.43, 2.48, 2.53, 2.66, 2.82], "recovery": [3.00, 3.10, 3.20, 3.30, 3.40, 3.48, 3.55],
         "native": [2.70, 2.80, 2.90, 3.00, 3.10, 3.20, 3.30]}
HCP_PUTT, HCP_SHORT = 0.06, 0.15
OB_COST = 1.0 + 3.2
LIES = ["rough", "fairway", "green", "sand", "recovery", "native", "water", "ob"]
C = {k: i for i, k in enumerate(LIES)}
STOP = np.array([False, False, False, True, True, True, True, True])


def opts(**over):
    o = dict(width_mult=1.0, depth_mult=1.0, carry_shift=0.0, roll_mult=1.0, slope_beta=0.02, tree_cost=1.0,
             pin_inset=4.0, mishits=True, green_roll=1.0)
    o.update(over)
    return o


# ------------------------------------------------------------------ geometry (truth map, page frame, DEM)
def load_holes(which, base_set):
    """{hole: dict(p, green, zones, decade plan, tee z, z sampler)} in the page's green frame (yds right, yds past
    the green centre along tee -> flag)."""
    import v2_course as vc
    import yardage_book as yb
    cfg = vc.config("eagle_knoll")
    PK = vc.product_pk()
    pp = PK._platform_pkg()
    dem_f = os.path.join(CD, "packages", "eagle_knoll", "imagery", "dem.tif")
    dem = pp.dem_sampler(dem_f)
    got = {}
    orig = PK._par3

    def cap(fr, green_ll, gpoly, zones, length, k):
        p = orig(fr, green_ll, gpoly, zones, length, k)
        tee = np.array(PK.TEE_PX, float)
        flag = fr.ll_to_px([green_ll])[0]
        v = (flag - tee) / np.linalg.norm(flag - tee)
        right = np.array([-v[1], v[0]])
        ppy = PK.PPY
        zz = []
        for lie, poly in zones:
            q = (np.asarray(poly, float) - flag) / ppy
            zz.append((lie, np.c_[q @ right, q @ v]))

        def z_at(lat, dep, fr=fr, flag=flag, v=v, right=right, ppy=ppy):
            lat, dep = np.asarray(lat, float), np.asarray(dep, float)
            px = flag[None, :] + (lat.ravel()[:, None] * right[None, :] + dep.ravel()[:, None] * v[None, :]) * ppy
            return (dem(fr.px_to_ll(px)) / 0.9144).reshape(lat.shape)      # yds
        zt = float(dem(fr.px_to_ll(tee[None, :]))[0] / 0.9144)
        dist_px = float(np.linalg.norm(flag - tee) / ppy)
        got[k] = dict(p=p, zones=zz, z_at=z_at, z_tee=zt, tee_to_flag=dist_px)
        return p
    PK._par3 = cap
    try:
        PK.load(os.path.join(ROOT, cfg["truth_package"]), base_set)
    finally:
        PK._par3 = orig
    plan = vc.floored_plan(yb.par3_plan)
    yb.WIND_NOW = 0
    for k, g in got.items():
        g["plan"] = plan(g["p"])
    return {k: got[k] for k in HOLES3 if k in got}


class Hole:
    def __init__(self, g, o):
        self.g, self.o = g, o
        p = g["p"]
        self.center = float(p["center"])
        self.green = np.array(p["green"], float)
        self.gpath = Path(self.green)
        la = np.arange(LAT0, LAT1 + 1e-9, RES)
        de = np.arange(DEP0, DEP1 + 1e-9, RES)
        self.la, self.de = la, de
        L, Dg = np.meshgrid(la, de, indexing="ij")
        pts = np.c_[L.ravel(), Dg.ravel()]
        lie = np.zeros(len(pts), int)
        pri = ["fairway", "recovery", "native", "sand", "ob", "water"]
        for name in pri:
            for nm, poly in g["zones"]:
                nm = "fairway" if nm == "first_cut" else nm
                if nm == name:
                    lie[Path(poly).contains_points(pts)] = C[name]
        on = self.gpath.contains_points(pts)
        lie[on] = C["green"]
        self.lie = lie.reshape(L.shape)
        self.z = g["z_at"](L, Dg)
        self.z_tee = g["z_tee"]
        # green plane: z = a + b lat + c dep (yds / yd)
        zg = self.z.ravel()[on]
        A = np.c_[np.ones(on.sum()), pts[on]]
        coef, *_ = np.linalg.lstsq(A, zg, rcond=None)
        self.grad = coef[1:]                                   # dz/dlat, dz/ddep
        self.plane_resid = float(np.std(zg - A @ coef) * 3)    # ft
        self.z_centre = float(g["z_at"](np.array([0.0]), np.array([0.0]))[0])
        self.pins = self._pins(o["pin_inset"])
        self.S = self._strokes_field()

    def _pins(self, inset):
        g = self.green
        lo, hi = g.min(0), g.max(0)
        xs, ys = np.meshgrid(np.arange(lo[0], hi[0], 1.0) + 0.5, np.arange(lo[1], hi[1], 1.0) + 0.5)
        cand = np.c_[xs.ravel(), ys.ravel()]
        cand = cand[self.gpath.contains_points(cand)]
        a, b = g, np.roll(g, -1, axis=0)
        d = np.full(len(cand), np.inf)
        for p0, p1 in zip(a, b):
            ab = p1 - p0
            u = np.clip(((cand - p0) @ ab) / max(ab @ ab, 1e-9), 0, 1)
            d = np.minimum(d, np.hypot(*(cand - (p0 + u[:, None] * ab)).T))
        pool = cand[d >= inset]
        return pool if len(pool) >= 12 else cand[np.argsort(-d)[:12]]

    def _strokes_field(self):
        """Pin-averaged expected strokes to hole out from every raster cell."""
        import model as M
        P = M.central()
        o = self.o
        L, Dg = np.meshgrid(self.la, self.de, indexing="ij")
        pts = np.c_[L.ravel(), Dg.ravel()]
        lie = self.lie.ravel()
        out = np.zeros(len(pts))
        pins = self.pins
        gx, gy = self.grad
        for i0 in range(0, len(pts), 4000):
            q = pts[i0:i0 + 4000]
            lq = lie[i0:i0 + 4000]
            dx = pins[None, :, 0] - q[:, None, 0]
            dy = pins[None, :, 1] - q[:, None, 1]
            d = np.hypot(dx, dy)
            res = np.zeros(len(q))
            m = lq == C["green"]
            if m.any():
                ft = np.clip(d[m] * 3.0, 1, 90)
                base = np.interp(ft, PUTT_FT, PUTTS) + HCP_PUTT
                # downhill grade along the putt (fraction): z(ball) - z(pin) over the distance
                s = -(gx * dx[m] + gy * dy[m]) / np.maximum(d[m], 1e-6)
                w = np.clip((ft - 3.0) / 12.0, 0, 1)
                res[m] = (base + o["slope_beta"] * 100.0 * s * w).mean(1)
            for name in ("rough", "fairway", "sand", "recovery", "native"):
                mm = lq == C[name]
                if not mm.any():
                    continue
                dd = d[mm]
                row = np.array(SHORT[name]) + HCP_SHORT
                if name == "recovery":
                    row = np.array(SHORT["rough"]) + HCP_SHORT + o["tree_cost"] * (np.array(SHORT["recovery"]) - np.array(SHORT["rough"]))
                v = np.interp(dd, SHORT_D, row)
                far = dd > 40
                if far.any():
                    kind = {"recovery": "rough", "native": "rough"}.get(name, name)
                    v[far] = row[-1] + (M.table(kind, dd[far], P) - M.table(kind, np.full(far.sum(), 40.0), P))
                res[mm] = v.mean(1)
            mm = lq == C["water"]
            if mm.any():
                res[mm] = 1.0 + np.interp(np.maximum(d[mm], 10), SHORT_D, np.array(SHORT["rough"]) + HCP_SHORT).mean(1)
            mm = lq == C["ob"]
            res[mm] = OB_COST
            out[i0:i0 + 4000] = res
        return out.reshape(L.shape)

    # raster lookups
    def idx(self, lat, dep):
        i = np.clip(np.rint((lat - LAT0) / RES).astype(int), 0, len(self.la) - 1)
        j = np.clip(np.rint((dep - DEP0) / RES).astype(int), 0, len(self.de) - 1)
        return i, j

    def land(self, lat, flat):
        """Landing depth (rel. to the green centre) of balls with flat-ground distance `flat` (from the tee)."""
        x = flat - self.center
        for _ in range(4):
            i, j = self.idx(lat, x)
            x = flat - self.center + K_DROP * (self.z_tee - self.z[i, j])
        return x

    def finish(self, lat, dep, roll):
        i, j = self.idx(lat, dep)
        lie = self.lie[i, j]
        left = np.where(STOP[lie], 0.0, roll)
        left = np.where(lie == C["rough"], left * 0.3, left)
        d = dep.copy()
        while True:
            mv = left > 1e-9
            if not mv.any():
                break
            st = np.minimum(left, 1.0) * mv
            d = d + st
            left = left - st
            i, j = self.idx(lat, d)
            new = self.lie[i, j]
            left = np.where(mv & (new == C["rough"]) & (lie != C["rough"]), left * 0.3, left)
            left = np.where(STOP[new], 0.0, left)
            lie = np.where(mv, new, lie)
        i, j = self.idx(lat, d)
        return d, self.S[i, j], self.lie[i, j]


# ------------------------------------------------------------------ shots
def club_tuple(carry70):
    """An ideal club for any carry: width and depth window interpolated on the bag (engine 8-iron scaling)."""
    cs = sorted(BAG.values())
    xs = [c[0] for c in cs]
    roll = np.interp(carry70, xs, [c[1] - c[0] for c in cs])
    w = np.interp(carry70, xs, [c[2] for c in cs])
    dpt = np.interp(carry70, xs, [c[3] for c in cs])
    return (float(carry70), float(carry70 + roll), float(w), float(dpt))


def draws(n, seed):
    import model as M
    return M.draws_z(n, seed)


def shot_set(tup, cond, o, z, name="Mid iron"):
    """(carry_flat, dev, roll) per swing for a club tuple at 70 F, in conditions cond (temp, mph, rel, gust)."""
    import model as M
    import wind as W
    M.CLUBS["_p3"] = tup
    over = dict(temp_f=cond["temp"], width={"_p3": tup[2] * 70 / 65 * o["width_mult"]},
                depth_mult=1.25 * o["depth_mult"])
    if not o["mishits"]:
        over.update(mis_slight=0.0, mis_heavy=0.0)
    P = M.central(**over)
    base = M.club_numbers({}, "_p3", P)
    wf = (1.0, 1.0, 1.0)
    if cond["mph"] > 0 or cond.get("gust"):
        c0, t0, w0, d0 = base[0], base[0] + base[1], tup[2], tup[3]
        a = W.adjust((c0, t0, w0, d0), cond["mph"], cond["rel"], club_name=name, gust_mph=cond.get("gust"))
        wf = (a[0] / c0, a[2] / w0, a[3] / d0)

    def wind(carry, roll, sl, sc):
        return carry * wf[0], roll, sl * wf[1], sc * wf[2], 0.0
    car, dev, roll = M.shots({}, "_p3", P, z, wind=wind)
    return car + o["carry_shift"], dev, roll * o["roll_mult"], base[0] * wf[0]


def carry_needed(H, dep, cond, o):
    """70-F flat carry that lands (solid strike) at depth dep on the green line in these conditions."""
    import model as M
    import wind as W
    i, j = H.idx(np.array([0.0]), np.array([dep]))
    flat = H.center + dep - K_DROP * (H.z_tee - H.z[i, j][0])
    tf = 1.0 - 0.00075 * (70.0 - cond["temp"])
    c70 = flat / tf
    if cond["mph"] > 0:
        for _ in range(3):
            tup = club_tuple(c70)
            a = W.adjust((c70 * tf, c70 * tf + tup[1] - tup[0], tup[2], tup[3]), cond["mph"], cond["rel"],
                         club_name="Mid iron")
            c70 = flat / (tf * a[0] / (c70 * tf))
    return c70


def ev_surface(H, cond, o, z, lats, deps):
    """EV (incl. the tee shot) per (lat aim, dep aim) for the ideal club at each depth; per-swing values kept."""
    vals = np.zeros((len(lats), len(deps), z.shape[1]), np.float32)
    for jd, dep in enumerate(deps):
        c70 = carry_needed(H, dep, cond, o)
        car, dev, roll, cmean = shot_set(club_tuple(c70), cond, o, z)
        # solid-strike landing at the aim: shift so that the stock carry lands at dep
        lat = dev[:, None] + lats[None, :]
        flat = car[:, None] + 0 * lats[None, :]
        # land() expects flat distance from the tee; the club's stock flat carry is cmean (temp+wind)
        dl = H.land(lat, flat)
        _, s, _ = H.finish(lat, dl, np.broadcast_to(roll[:, None], lat.shape))
        vals[:, jd, :] = (1.0 + s).T
    return vals


def club_eval(H, cond, o, z, lats, clubs=None):
    """Each real club at its stock carry: landing depth set by the conditions, lateral aim optimised."""
    out = {}
    for c, tup in BAG.items():
        if clubs and c not in clubs:
            continue
        car, dev, roll, cmean = shot_set(tup, cond, o, z, name=c if c in ("Long iron", "Mid iron", "8-iron") else "Mid iron")
        lat = dev[:, None] + lats[None, :]
        dl = H.land(lat, np.broadcast_to(car[:, None], lat.shape))
        _, s, lie = H.finish(lat, dl, np.broadcast_to(roll[:, None], lat.shape))
        v = 1.0 + s                                    # swings x lats
        m = v.mean(0)
        k = int(m.argmin())
        dep_solid = float(H.land(np.array([lats[k]]), np.array([cmean]))[0])
        out[c] = dict(ev=float(m[k]), lat=float(lats[k]), dep=dep_solid, per=v[:, k],
                      green=float(np.mean(lie[:, k] == C["green"])), water=float(np.mean(lie[:, k] == C["water"])),
                      trees=float(np.mean(lie[:, k] == C["recovery"])), sand=float(np.mean(lie[:, k] == C["sand"])))
    return out


def paired(a, b):
    d = np.asarray(a, float) - np.asarray(b, float)
    return float(d.mean()), float(d.std(ddof=1) / np.sqrt(len(d)))


# ------------------------------------------------------------------ solve
def conditions(hole, bearing):
    """Representative conditions: page wind modifiers (any direction) and the two forecast days."""
    rel_sw = ((225.0 - bearing) % 360 + 360) % 360
    return {
        "calm50": dict(temp=50.0, mph=0.0, rel=0.0),
        "sat": dict(temp=47.0, mph=1.5, rel=((350.0 - bearing) % 360), gust=2.0),
        "sun": dict(temp=54.0, mph=5.5, rel=rel_sw, gust=12.0),
    }


def mod_conds(mod):
    """Page DECADE wind modifier classes -> (mph, gust) representative; direction averaged over 4."""
    return {-1: None, 0: (7.0, 12.0), 1: (14.0, 20.0), 2: (24.0, 32.0), 3: (32.0, 40.0)}[mod]


def solve_surface(H, cond, o, seed, lats, deps, n):
    z = draws(n, seed)
    if cond.get("dirs"):
        acc = None
        for rel in cond["dirs"]:
            c2 = dict(cond, rel=rel)
            v = ev_surface(H, c2, o, z, lats, deps)
            acc = v if acc is None else acc + v
        return acc / len(cond["dirs"])
    return ev_surface(H, cond, o, z, lats, deps)


def best_of(vals, lats, deps):
    m = vals.mean(2)
    i, j = np.unravel_index(int(m.argmin()), m.shape)
    return i, j, m


def refine(H, cond, o, seed, centre, n, half=4.0, step=0.5):
    lats = np.arange(centre[0] - half, centre[0] + half + 1e-9, step)
    deps = np.arange(centre[1] - half, centre[1] + half + 1e-9, step)
    v = solve_surface(H, cond, o, seed, lats, deps, n)
    i, j, m = best_of(v, lats, deps)
    return lats, deps, v, (float(lats[i]), float(deps[j]))


def box_from(m, lats, deps, best, tol=0.02, min_w=4.0):
    """Aim box: the extent, through the best aim, of aims within `tol` strokes of the best (>= min_w yds)."""
    i = int(np.argmin(np.abs(lats - best[0])))
    j = int(np.argmin(np.abs(deps - best[1])))
    e0 = m[i, j]
    row = m[:, j] <= e0 + tol
    col = m[i, :] <= e0 + tol

    def ext(mask, ax, k):
        lo = k
        while lo - 1 >= 0 and mask[lo - 1]:
            lo -= 1
        hi = k
        while hi + 1 < len(mask) and mask[hi + 1]:
            hi += 1
        a, b = float(ax[lo]), float(ax[hi])
        if b - a < min_w:
            c = (a + b) / 2
            a, b = c - min_w / 2, c + min_w / 2
        return [round(a, 1), round(b, 1)]
    return ext(row, lats, i), ext(col, deps, j)


def solve_hole(H, bearing, o, n_grid=6000, n_ref=40000, seed=11, clubs_for=("sat", "sun", "calm50"), fast=False):
    """fast: mod 1-3 boxes copied from mod 0 and calm50 from mod-1 (on Back they differ by <= 0.5 yd)."""
    lats = np.arange(-16.0, 16.0 + 1e-9, 1.0)
    deps = np.arange(-20.0, 16.0 + 1e-9, 1.0)
    out = dict(center=H.center, grad_pct=[round(100 * x, 2) for x in H.grad], plane_resid_ft=round(H.plane_resid, 2),
               z_drop_ft=round((H.z_tee - H.z_centre) * 3, 1), n_pins=int(len(H.pins)))
    plan = H.g["plan"]
    out["decade"] = dict(aim=[round(float(x), 2) for x in plan["aim"]], lat=[float(x) for x in plan["lat"]],
                         dep=[float(x) for x in plan["dep"]])
    conds = conditions(None, bearing)
    out["conds"] = {k: {kk: (round(vv, 1) if isinstance(vv, float) else vv) for kk, vv in c.items()} for k, c in conds.items()}
    res = {}
    # page wind classes: -1 = calm (50 F); 0..3 = that strength from any of 4 directions
    allc = {"mod-1": dict(temp=50.0, mph=0.0, rel=0.0)}
    for mod in (0, 1, 2, 3):
        mph, gust = mod_conds(mod)
        allc[f"mod{mod}"] = dict(temp=50.0, mph=mph, rel=0.0, gust=gust, dirs=[0.0, 90.0, 180.0, 270.0])
    allc.update(conds)
    for name, cond in allc.items():
        if fast and name in ("mod1", "mod2", "mod3", "calm50"):
            continue
        v = solve_surface(H, cond, o, seed, lats, deps, n_grid)
        i, j, m = best_of(v, lats, deps)
        rl, rd, rv, best = refine(H, cond, o, seed + 1, (lats[i], deps[j]), n_ref)
        mref = rv.mean(2)
        bi, bj = int(np.argmin(np.abs(rl - best[0]))), int(np.argmin(np.abs(rd - best[1])))
        # centre and DECADE aims on the same fresh swings
        pts = {"centre": (0.0, 0.0), "decade": (float(plan["aim"][0]), float(plan["aim"][1]))}
        z2 = draws(n_ref, seed + 1)
        ref_vals = {}
        for nm, (al, ad) in pts.items():
            vv = solve_surface_pt(H, cond, o, z2, al, ad)
            ref_vals[nm] = vv
        bestv = rv[bi, bj, :]
        r = dict(best=[best[0], best[1]], ev_best=round(float(bestv.mean()), 4),
                 coarse_best=[float(lats[i]), float(deps[j])])
        for nm, vv in ref_vals.items():
            d, se = paired(bestv, vv)
            r[f"ev_{nm}"] = round(float(vv.mean()), 4)
            r[f"gain_vs_{nm}"] = [round(-d, 4), round(se, 4)]
        r["box_lat"], r["box_dep"] = box_from(m, lats, deps, (lats[i], deps[j]))
        # fine box edges from the refine window where it reaches
        r["surface"] = dict(lats=lats.tolist(), deps=deps.tolist(), ev=np.round(m, 4).tolist())
        r["surface_fine"] = dict(lats=rl.tolist(), deps=rd.tolist(), ev=np.round(mref, 4).tolist())
        r["carry70_at_best"] = round(float(carry_needed(H, best[1], cond, o)), 1) if not cond.get("dirs") else None
        res[name] = r
        print(f"  {name}: best {best} ev {r['ev_best']} gain vs centre {r['gain_vs_centre']} vs decade "
              f"{r['gain_vs_decade']} box lat {r['box_lat']} dep {r['box_dep']}", file=sys.stderr, flush=True)
    if fast:
        for m in ("mod1", "mod2", "mod3"):
            res[m] = dict(res["mod0"], copied_from="mod0")
        res["calm50"] = dict(res["mod-1"], copied_from="mod-1")
    out["aims"] = res
    # clubs at stock carry
    lats_c = np.arange(-12.0, 12.0 + 1e-9, 0.5)
    clubs = {}
    for name in clubs_for:
        cond = allc[name]
        z = draws(n_ref, seed + 7)
        ce = club_eval(H, cond, o, z, lats_c)
        order = sorted(ce, key=lambda c: ce[c]["ev"])
        b, r2 = order[0], order[1]
        d, se = paired(ce[r2]["per"], ce[b]["per"])
        tie = (d < 2 * se) or (d < 0.01)
        ideal = res[name]["ev_best"]
        clubs[name] = dict(pick=b, runner=r2, margin=[round(d, 4), round(se, 4)], tie=bool(tie),
                           order=[(c, round(ce[c]["ev"], 4), round(ce[c]["dep"], 1), ce[c]["lat"],
                                   round(ce[c]["green"], 3), round(ce[c]["water"], 3), round(ce[c]["trees"], 3))
                                  for c in order[:4]],
                           ideal_ev=ideal)
        print(f"  clubs {name}: {b} (lands {ce[b]['dep']:+.1f}, ev {ce[b]['ev']:.4f}) over {r2} by {d:.4f} +/- {se:.4f}"
              f"{' TIE' if tie else ''}; ideal {ideal}", file=sys.stderr, flush=True)
    out["clubs"] = clubs
    return out


def solve_surface_pt(H, cond, o, z, al, ad):
    return solve_surface_z(H, cond, o, z, np.array([al]), np.array([ad]))[0, 0, :]


def solve_surface_z(H, cond, o, z, lats, deps):
    if cond.get("dirs"):
        acc = None
        for rel in cond["dirs"]:
            v = ev_surface(H, dict(cond, rel=rel), o, z, lats, deps)
            acc = v if acc is None else acc + v
        return acc / len(cond["dirs"])
    return ev_surface(H, cond, o, z, lats, deps)


def setup_engine():
    import v2_course as vc
    course, meta, M, D = vc.activate("eagle_knoll", "truth")
    sys.path.insert(0, os.path.join(ROOT, "spirit_hollow"))
    import wind as W
    for c in BAG:
        W.SENSITIVITY.setdefault(c, 1.3)
    W.SENSITIVITY["_p3"] = 1.0
    return M


def bearings(which):
    import v2_course as vc
    mod = vc._load(vc.cdir("eagle_knoll", which, "course.py"), "course_" + which)
    return mod.BEARINGS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["solve", "robust"])
    ap.add_argument("--sets", default="Back,Eagle,Middle")
    ap.add_argument("--holes", default="2,6,12,16")
    ap.add_argument("--n-grid", type=int, default=6000)
    ap.add_argument("--n-ref", type=int, default=40000)
    ap.add_argument("--variants", default="")
    ap.add_argument("--fast", action="store_true")
    a = ap.parse_args()
    setup_engine()
    os.makedirs(OUT, exist_ok=True)
    holes = [int(x) for x in a.holes.split(",")]
    if a.cmd == "solve":
        for s in a.sets.split(","):
            path = os.path.join(OUT, f"par3_target_{s}.json")
            res = json.load(open(path)) if os.path.exists(path) else {}
            G = load_holes(SETS[s], s)
            B = bearings(SETS[s])
            for k in holes:
                print(s, k, file=sys.stderr, flush=True)
                H = Hole(G[k], opts())
                res[f"{s} {k}"] = solve_hole(H, B[k], opts(), a.n_grid, a.n_ref, fast=a.fast)
                res[f"{s} {k}"]["bearing"] = B[k]
                json.dump(res, open(path, "w"), indent=1)
        write_page()
    else:
        robust(a)


def all_results():
    res = {}
    for s in SETS:
        p = os.path.join(OUT, f"par3_target_{s}.json")
        if os.path.exists(p):
            res.update(json.load(open(p)))
    return res


def write_page():
    """Compact page data: per set / hole, the box (lat, dep) for each DECADE wind class, the aim, and the club."""
    res = all_results()
    page = {"source": "course_data/courses/eagle_knoll/opt/par3_target.py (OPTIMIZE.md section 13)", "sets": {}}
    for key, r in sorted(res.items()):
        s, k = key.split()
        boxes = {}
        for mod in (-1, 0, 1, 2, 3):
            a = r["aims"][f"mod{mod}"]
            boxes[str(mod)] = dict(aim=a["best"], lat=a["box_lat"], dep=a["box_dep"])
        cl = {}
        for nm, c in r["clubs"].items():
            cl[nm] = dict(pick=SHORT_NAME.get(c["pick"], c["pick"]), runner=SHORT_NAME.get(c["runner"], c["runner"]),
                          tie=c["tie"], margin=c["margin"][0])
        page["sets"].setdefault(s, {})[k] = dict(boxes=boxes, clubs=cl,
                                                 gain_vs_centre=r["aims"]["mod-1"]["gain_vs_centre"],
                                                 gain_vs_decade=r["aims"]["mod-1"]["gain_vs_decade"])
    json.dump(page, open(PAGE, "w"), indent=1)
    print("wrote", PAGE, file=sys.stderr)


def robust(a):
    """Back: does the calm best aim hold under carry +/-5, dispersion +/-10 %, wind +/-3 mph, roll, slope, trees?"""
    base = all_results()
    out = {}
    s = "Back"
    G = load_holes(SETS[s], s)
    B = bearings(SETS[s])
    lats = np.arange(-16.0, 16.0 + 1e-9, 1.0)
    deps = np.arange(-24.0, 16.0 + 1e-9, 1.0)
    variants = {
        "carry+5": dict(o=dict(carry_shift=5.0)), "carry-5": dict(o=dict(carry_shift=-5.0)),
        "disp+10": dict(o=dict(width_mult=1.1, depth_mult=1.1)), "disp-10": dict(o=dict(width_mult=0.9, depth_mult=0.9)),
        "wind+3": dict(c=dict(mph=3.0, gust=6.0, dirs=[0.0, 90.0, 180.0, 270.0])),
        "sun+3": dict(c="sun", dmph=3.0), "sun-3": dict(c="sun", dmph=-3.0),
        "roll0.5": dict(o=dict(roll_mult=0.5)), "no-slope": dict(o=dict(slope_beta=0.0)),
        "slope x2": dict(o=dict(slope_beta=0.04)), "trees half": dict(o=dict(tree_cost=0.5)),
        "no mishits": dict(o=dict(mishits=False)), "pins 3 in": dict(o=dict(pin_inset=3.0)),
        "pins 6 in": dict(o=dict(pin_inset=6.0)),
        "depth x2 (amateur finish pattern)": dict(o=dict(depth_mult=2.0)),
    }
    if a.variants:
        variants = {k: v for k, v in variants.items() if k in a.variants.split("|")}
    for k in [int(x) for x in a.holes.split(",")]:
        r0 = base[f"{s} {k}"]["aims"]["mod-1"]
        best0 = tuple(r0["best"])
        conds = conditions(None, B[k])
        res = {}
        for name, v in variants.items():
            o = opts(**v.get("o", {}))
            H = Hole(G[k], o)
            cond = dict(temp=50.0, mph=0.0, rel=0.0)
            ref = best0
            if isinstance(v.get("c"), dict):
                cond.update(v["c"])
            elif v.get("c") == "sun":
                cond = dict(conds["sun"])
                cond["mph"] = max(cond["mph"] + v["dmph"], 0.0)
                cond["gust"] = max(cond["gust"] + v["dmph"], 0.0)
                ref = tuple(base[f"{s} {k}"]["aims"]["sun"]["best"])
            z = draws(a.n_grid, 21)
            vals = solve_surface_z(H, cond, o, z, lats, deps)
            i, j, m = best_of(vals, lats, deps)
            nb = (float(lats[i]), float(deps[j]))
            z2 = draws(a.n_ref, 22)
            pts = solve_surface_z(H, cond, o, z2, np.array(sorted({nb[0], ref[0], 0.0})), np.array(sorted({nb[1], ref[1], 0.0})))
            L2 = sorted({nb[0], ref[0], 0.0})
            D2 = sorted({nb[1], ref[1], 0.0})

            def at(p):
                return pts[L2.index(p[0]), D2.index(p[1]), :]
            keep, se1 = paired(at(nb), at(ref))         # best-under-variant minus central aim (<= 0)
            cen, se2 = paired(at(ref), at((0.0, 0.0)))  # central aim minus centre aim (< 0 = still better)
            res[name] = dict(best=list(nb), regret_of_central_aim=[round(-keep, 4), round(se1, 4)],
                             central_aim_vs_centre=[round(cen, 4), round(se2, 4)])
            print(s, k, name, json.dumps(res[name]), file=sys.stderr, flush=True)
        out[f"{s} {k}"] = res
    rp = os.path.join(OUT, "par3_robust.json")
    old = json.load(open(rp)) if os.path.exists(rp) else {}
    for k, v in out.items():
        old.setdefault(k, {}).update(v)
    json.dump(old, open(rp, "w"), indent=1)


if __name__ == "__main__":
    main()
