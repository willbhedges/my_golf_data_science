"""Gateway National hole 10 (271 Back / 251 Middle): the LAY-UP, club by club (second_pass/HOLE10_LAYUP.md), and the
lay-up grid the page's "Lay up" mode reads (gateway_national/layup10.json, config "layup_grid").

  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/layup10.py study --which truth
  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/layup10.py study --which truth_middle
  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/layup10.py grid          (both bases, one process each)
  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/layup10.py picture --which truth

A lay-up = an aim whose FINISHING LINE (aim + wind drift, yds right of the tee line) is inside the lay-up window:
the right fairway, never the green. WINDOW below, from the map (the green is 9-29 yds left of the tee line at 249-290
from the Back tee, the channel beside it 5-15 left; the right fairway runs from 28 left at 150 to 40 right at 270).
Irons cannot reach the green, so their window starts at 5 left; the woods' starts at 5 right so that a "lay-up" is
never a ball that is meant to spill onto the green.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import par5_second as P5                                   # noqa: E402

GW = os.path.dirname(HERE)
OUT = os.path.join(HERE, "results")
PAGE = os.path.join(GW, "layup10.json")
H = 10
WINDOW = {"wood": (5.0, 45.0), "iron": (-5.0, 45.0)}
WOODS = ("Driver", "2-wood", "4-wood")
SET_OF = {"truth": "Back", "truth_middle": "Middle"}
# part swings for the explicit second shot (ASSUMED: width and depth in proportion to the SW's, floors 10 / 8 yds)
PITCH = {f"pitch {c}": (c, c + 2, max(10.0, 22.0 * c / 113.0), max(8.0, 12.0 * c / 113.0), "8-iron")
         for c in (30, 40, 50, 60, 70, 80, 90, 100)}


def window(club):
    return WINDOW["wood" if club in WOODS or club.startswith("Hybrid") else "iron"]


def hook_of(Wd, club, mph, rel):
    return Wd.WG2.wind_hook(club, mph, rel) if mph > 0 else None


def lay_solve(Wd, hd, R, S, P, z, club, mph, rel, restrict=True):
    """Best aim of `club` with the finishing line inside the lay-up window (restrict) or anywhere (the engine's)."""
    M, D = Wd.M, Wd.D
    hook = hook_of(Wd, club, mph, rel)
    c, r, sl, sc = M.club_numbers(hd, club, P)
    dr = 0.0
    if hook:
        c, r, sl, sc, dr = hook(c, r, sl, sc)
    L = float(D.AIM_LIMIT)
    aims = np.arange(-(L + 35.0), L + 35.01, 0.5)
    ev, (a, l, lie, s) = M.ev_curve(R, S, hd, club, P, z, aims, wind=hook)
    lo, hi = (window(club)[0] - dr, window(club)[1] - dr) if restrict else (-L - dr, L - dr)
    ra = D.robust_aim(aims, ev, lo=lo, hi=hi)
    j = int(np.argmin(np.abs(aims - ra["aim"])))
    zl, zh = ra["window"]
    return dict(club=club, aim=float(ra["aim"]), ev=float(ra["ev"]), zone=[float(max(zl, lo)), float(min(zh, hi))],
                drift=float(dr), carry=float(c), total=float(c + r), hook=hook, at_bound=bool(ra["at_bound"]),
                a=a[:, j], l=l[:, j], lie=lie[:, j], s=s[:, j])


def shares(Wd, R, F, o, sand_box):
    M = Wd.M
    lie, a, l = o["lie"], o["a"], o["l"]
    on = F.ongreen[F.R.idx(a, l)]
    pen = np.isin(lie, [M.CODE["water"], M.CODE["native"], M.CODE["ob"]])
    sand = lie == M.CODE["sand"]
    fw = np.isin(lie, [M.CODE["fairway"], M.CODE["first_cut"]]) & ~on
    d = np.hypot(a - F.green[0], l - F.green[1])
    ok = ~pen
    a0, a1, l0, l1, _end = sand_box
    fs = sand & (a >= a0) & (a <= a1) & (l >= l0) & (l <= l1)
    solid = np.abs(a - np.median(a)) < 25
    return dict(fairway=float(fw.mean()), rough=float(((lie == M.CODE["rough"]) & ~on).mean()),
                sand=float(sand.mean()), fairway_sand=float(fs.mean()), green=float(on.mean()), lost=float(pen.mean()),
                trees=float((lie == M.CODE["recovery"]).mean()), leave=float(np.median(d[ok])),
                finish=[float(np.median(a[solid])), float(np.median(l[solid]))],
                finish_10_90=[float(np.percentile(a, 10)), float(np.percentile(a, 90))],
                past_fairway_end=float(((a > sand_box[4]) & ~on).mean()))


def explicit_values(Wd, F, P, wx, bearing, balls, n_grid=400, step=6.0):
    """{lie: interpolator of the explicit next-shot value} on a lattice over the balls (fairway / rough / sand)."""
    from scipy.interpolate import RegularGridInterpolator
    from scipy import ndimage
    M = Wd.M
    z = M.draws_z(n_grid, 9)
    A = np.concatenate([b[0] for b in balls])
    L = np.concatenate([b[1] for b in balls])
    ga = np.arange(np.floor(A.min() / step) * step, A.max() + step, step)
    gl = np.arange(np.floor(L.min() / step) * step, L.max() + step, step)
    occ = np.zeros((len(ga), len(gl)), bool)
    occ[np.clip(np.rint((A - ga[0]) / step).astype(int), 0, len(ga) - 1),
        np.clip(np.rint((L - gl[0]) / step).astype(int), 0, len(gl) - 1)] = True
    occ = ndimage.binary_dilation(occ, iterations=1)
    V = {lie: np.full(occ.shape, np.nan) for lie in P5.LIE}
    for i, a0 in enumerate(ga):
        for j, l0 in enumerate(gl):
            if not occ[i, j]:
                continue
            d = float(np.hypot(a0 - F.green[0], l0 - F.green[1]))
            for lie in P5.LIE:
                clubs = [c for c in P5.DECK if P5.DECK[c][1] <= d + 25 and (c in PITCH or c in P5.deck_clubs(lie))]
                res = P5.play(Wd, F, P, z, float(a0), float(l0), lie, wx, bearing, clubs=clubs or ["pitch 30"])
                V[lie][i, j] = min(float(o["ev"].min()) for o in res["opts"])
    return {lie: RegularGridInterpolator((ga, gl), np.where(np.isnan(v), np.nanmean(v), v), bounds_error=False, fill_value=None)
            for lie, v in V.items()}


def explicit_ev(Wd, F, P, o, VI, near=30.0):
    """The club's strokes with the next shot played out (balls 30+ yds from the middle of the green on fairway,
    rough or sand); the engine's value elsewhere (on / by the green, penalty, trees)."""
    M = Wd.M
    a, l, lie = o["a"], o["l"], o["lie"]
    tot = 1.0 + o["s"].copy()
    d = np.hypot(a - F.green[0], l - F.green[1])
    for lname, codes in (("fairway", ("fairway", "first_cut")), ("rough", ("rough",)), ("sand", ("sand",))):
        m = np.isin(lie, [M.CODE[c] for c in codes]) & (d > near) & ~F.ongreen[F.R.idx(a, l)]
        if m.any():
            tot[m] = 1.0 + VI[lname](np.column_stack([a[m], l[m]]))
    return float(tot.mean())


def geometry(Wd, hd, R):
    """Sand patches and the right fairway's end, in yds from this tee."""
    from scipy import ndimage
    M = Wd.M
    lab, n = ndimage.label(R.lie == M.CODE["sand"])
    pats = []
    for k in range(1, n + 1):
        ia, il = np.nonzero(lab == k)
        if len(ia) < 8:
            continue
        pats.append(dict(a=[float(R.a[ia.min()]), float(R.a[ia.max()])], l=[float(R.l[il.min()]), float(R.l[il.max()])]))
    fwm = np.isin(R.lie, [M.CODE["fairway"], M.CODE["first_cut"]])
    cols = (R.l >= 5) & (R.l <= 40)
    rows = np.nonzero(fwm[:, cols].any(1) & (R.a > 150))[0]
    end = float(R.a[rows.max()])
    for p in pats:                                             # the green's own sand is not the fairway's end
        pass
    fs = [p for p in pats if p["l"][0] > -10 and 150 < p["a"][0] < 240]
    # the right fairway's far end on each lateral line
    ends = {}
    for x in (0, 10, 20, 30, 40):
        col = fwm[:, int(np.argmin(np.abs(R.l - x)))] & (R.a > 150) & (R.a < 300)
        ends[str(x)] = float(R.a[np.nonzero(col)[0].max()]) if col.any() else None
    return dict(sand=pats, fairway_sand=fs, fairway_end=ends)


def study(a):
    Wd = P5.World(a.which)
    M = Wd.M
    for nm, tup in PITCH.items():
        P5.DECK[nm] = tup
        M.CLUBS["deck:" + nm] = tuple(float(x) for x in tup[:4])
    hd = Wd.course.HOLES[H]
    bearing = float(Wd.course.BEARINGS[H])
    R = M.Raster(hd)
    _, Rb = Wd.big(hd)
    geo = geometry(Wd, hd, R)
    fs = geo["fairway_sand"][0] if geo["fairway_sand"] else dict(a=[190, 205], l=[0, 15])
    end = max(v for v in geo["fairway_end"].values() if v)
    box = (fs["a"][0] - 1, fs["a"][1] + 1, fs["l"][0] - 1, fs["l"][1] + 1, end)
    z = M.draws_z(12000, 77)
    conds = {"calm45": dict(temp=45.0, mph=0.0, frm=0.0)}
    for day in ("sat", "sun"):
        conds[day] = Wd.wx(H, P5.DAYS[day])
    cases = [("calm45", 1.0, True), ("sat", 1.0, True), ("sun", 1.0, True), ("sat", 1.25, False), ("sat", 1.5, False),
             ("sun", 1.25, False)]
    if a.fast:
        cases = [(c, r, False) for c, r, _ in cases]
    out = dict(which=a.which, set=SET_OF[a.which], length=hd["length"], green=[float(x) for x in R.green], geometry=geo,
               window=WINDOW, cases={})
    clubs = list(M.REAL_CLUBS)
    for cname, rollx, explicit in cases:
        wx = conds[cname]
        P = M.central(temp_f=wx["temp"], roll_mult=rollx)
        S = R.strokes(P, hd["length"])
        F = P5.Field(Wd, hd, P, Rb)
        rel = (wx["frm"] - bearing) % 360
        rows, go = {}, {}
        for c in clubs:
            rows[c] = lay_solve(Wd, hd, R, S, P, z, c, wx["mph"], rel, True)
        for c in WOODS:
            go[c] = lay_solve(Wd, hd, R, S, P, z, c, wx["mph"], rel, False)
        VI = None
        if explicit:
            balls = [(o["a"][m], o["l"][m]) for o in list(rows.values()) + list(go.values())
                     for m in [np.isin(o["lie"], [M.CODE[k] for k in ("fairway", "first_cut", "rough", "sand")])
                               & (np.hypot(o["a"] - F.green[0], o["l"] - F.green[1]) > 30)]]
            VI = explicit_values(Wd, F, P, wx, bearing, balls)
        res = dict(wx={k: round(float(v), 1) for k, v in wx.items()}, roll=rollx, lay={}, go={})
        for kind, dd in (("lay", rows), ("go", go)):
            for c, o in dd.items():
                r = dict(aim=o["aim"], drift=round(o["drift"], 1), line=round(o["aim"] + o["drift"], 1), ev=round(o["ev"], 4),
                         carry=round(o["carry"], 1), total=round(o["total"], 1), at_bound=o["at_bound"],
                         se=round(float(o["s"].std(ddof=1) / np.sqrt(len(o["s"]))), 4), **shares(Wd, R, F, o, box))
                if VI is not None:
                    r["ev_explicit"] = round(explicit_ev(Wd, F, P, o, VI), 4)
                res[kind][c] = r
        out["cases"][f"{cname}|x{rollx:g}"] = res
        bl = min(res["lay"], key=lambda c: res["lay"][c]["ev"])
        bg = min(res["go"], key=lambda c: res["go"][c]["ev"])
        print(a.which, cname, rollx, "best lay-up", bl, res["lay"][bl]["ev"], "go", bg, res["go"][bg]["ev"], flush=True)
        json.dump(out, open(os.path.join(OUT, f"layup10_{SET_OF[a.which]}.json"), "w"), indent=0)


def grid_one(a):
    """The page's lay-up grid for one base: the wind grid's cells and temperatures, each club at its best lay-up aim."""
    Wd = P5.World(a.which)
    M, WG2, W = Wd.M, Wd.WG2, Wd.W
    hd = Wd.course.HOLES[H]
    R = M.Raster(hd)
    z = M.draws_z(8192, 32)
    main = json.load(open(os.path.join(GW, a.which, "v2", "wind_grid.json")))
    out = {}
    for T in main["temps"]:
        P = M.central(temp_f=float(T))
        S = R.strokes(P, hd["length"])
        g = {}
        for sp in main["speeds"]:
            for rel in ([0] if sp == 0 else main["dirs"]):
                cl = {}
                for c in M.ALL_CLUBS:
                    o = lay_solve(Wd, hd, R, S, P, z, c, sp, rel, True)
                    carry0, total0, width0, depth0 = M.CLUBS[c]            # page numbers as wind_grid_v2.solve: no elevation
                    carry = carry0 * (1.0 - P["temp_k"] * (70.0 - P["temp_f"]))
                    tup = (carry, carry + (total0 - carry0) * P["roll_mult"], P["width"][c], depth0 * P["depth_mult"])
                    c2, t2, w2, d2, drift = W.adjust(tup, sp, rel, club_name=c) if sp else tup + (0.0,)
                    cl[c] = dict(aim=o["aim"], ev=round(o["ev"], 5), zone=[round(x, 2) for x in o["zone"]], carry=round(float(c2), 2),
                                 total=round(float(t2), 2), width=round(float(w2), 2), drift=round(float(drift), 2))
                g[f"{sp}_{rel}"] = dict(clubs=cl)
        out[f"{float(T):g}"] = g
        print(a.which, T, "done", {c: (v["aim"], v["ev"]) for c, v in g["0_0"]["clubs"].items()}, flush=True)
    json.dump(out, open(os.path.join(OUT, f"layup10_grid_{SET_OF[a.which]}.json"), "w"))


PAGE_CLUBS = ("4-wood", "Long iron", "Mid iron", "8-iron")     # Driver / 2-wood lay-ups lose 25-60 % of balls: study only


def grid(a):
    if not a.fast:                                             # --fast: only re-assemble the page file
        ps = [subprocess.Popen([sys.executable, os.path.abspath(__file__), "grid_one", "--which", w]) for w in SET_OF]
        assert all(p.wait() == 0 for p in ps)
    page = dict(source="opt/layup10.py grid (second_pass/HOLE10_LAYUP.md)", window=WINDOW, hole=str(H), sets={})
    for w, s in SET_OF.items():
        g = json.load(open(os.path.join(OUT, f"layup10_grid_{s}.json")))
        page["sets"][s] = {T: {k: dict(clubs={c: v["clubs"][c] for c in PAGE_CLUBS}) for k, v in cells.items()} for T, cells in g.items()}
    json.dump(page, open(PAGE, "w"), separators=(",", ":"))
    print("wrote", PAGE, os.path.getsize(PAGE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--which", default="truth")
    ap.add_argument("--fast", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    {"study": study, "grid": grid, "grid_one": grid_one}[a.cmd](a)


if __name__ == "__main__":
    main()
