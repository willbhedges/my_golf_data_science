"""Gateway National par 3s: the expected-strokes-optimal aim box for an unknown pin, and the plays-like number to it
(PAR3.md; the same model as course_data/courses/eagle_knoll/opt/par3_target.py, OPTIMIZE.md section 13, reused
here by import; only the course wiring, the bag ends and the forecast are Gateway's).

  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/par3_target.py solve  [--sets Back] [--fast]
  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/par3_target.py robust [--sets Back]
  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/par3_target.py mapvar [--sets Back]
  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/par3_target.py numbers
  python3 course_data/courses/gateway_national/opt/par3_target.py page     (rewrite par3_targets.json from results)

`solve` writes opt/results/par3_target_<set>.json (surfaces, clubs, SEs) and the page file
course_data/courses/gateway_national/par3_targets.json (config "par3_targets", read by course_data/courses/par3_targets.py).
`robust` writes opt/results/par3_robust.json (dispersion, temperature 35-65 F, single-direction wind, carry, roll,
slope, trees, pins, mishits) and opt/results/par3_numbers.json (plays-like carry to the box by temperature and wind).

Gateway-specific pieces:
  * Geometry: the truth package (course_data/courses/gateway_national/truth/package.json) loaded per tee set through
    the page's own loader (product/package.py, PK.load(path, set)), so every set has its own tee, line and frame.
    DEM: the page's 3DEP 1 m DEM (course_data/packages/gateway_national/imagery/dem.tif); the 2014 Madison Co. lidar
    DTM (vision_any raw/dtm.tif, 2 m) is the cross-check. K = 0.839 yd per yd of drop = 1 / tan 50 deg, the page's
    elevation factor (v2_course meta dz).
  * Bag: the engine's Long iron 210 / Mid iron 185 / 4-wood 255 (Will's numbers: long iron 210, mid iron ~184,
    4-wood 255); 8-iron 162 (assumed by the brief); 5-, 7-, 9-iron, PW 138, GW 126 ASSUMED as at Eagle Knoll (Spirit
    Hollow approach bag, ~12-yd gaps); SW 113 / LW 100 ASSUMED (Eagle Knoll section 13's suggestion) for the Forward
    and Middle 12. No club between 210 and 255 (the engine's 'Hybrid ~235' is marked not in the bag).
  * Forecast: course_data/weather/forecast_gateway_national.json at each hole's time (9:00 shotgun on 1, 14 min a
    hole, as the engine's model.hole time), Sat Nov 14 and Sun Nov 15.
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GW = os.path.dirname(HERE)
CD = os.path.dirname(os.path.dirname(GW))
ROOT = os.path.dirname(CD)
sys.path[:0] = [os.path.join(CD, "courses"), os.path.join(ROOT, "mozingo")]
OUT = os.path.join(HERE, "results")
PAGE = os.path.join(GW, "par3_targets.json")
SLUG = "gateway_national"
SETS = ["Back", "The Tips", "Champions", "Middle", "Forward"]
HOLES3 = (4, 7, 12, 14, 17)
DEM = os.path.join(CD, "packages", SLUG, "imagery", "dem.tif")
DTM_LIDAR = os.path.join(CD, "vision_any", SLUG, "raw", "dtm.tif")
FORECAST = os.path.join(CD, "weather", "forecast_gateway_national.json")
TEE_HOUR, MIN_PER_HOLE = 9.0, 14.0

_spec = importlib.util.spec_from_file_location("ek_par3", os.path.join(CD, "courses", "eagle_knoll", "opt", "par3_target.py"))
E = importlib.util.module_from_spec(_spec)
sys.modules["ek_par3"] = E
_spec.loader.exec_module(E)

# the Eagle Knoll bag plus Will's 4-wood (engine) and two ASSUMED wedges for the short Forward / Middle 12
E.BAG = dict(E.BAG)
E.BAG.update({"4-wood": (255, 270, 50, 24), "SW": (113, 115, 22, 12), "LW": (100, 101, 20, 11)})
E.HOLES3 = HOLES3
E.OUT = OUT
WIND_NAME = {"Long iron": "Long iron", "Mid iron": "Mid iron", "4-wood": "4-wood"}


# ------------------------------------------------------------------ course wiring
def load_holes(set_name):
    """{hole: g} for one tee set, in that set's own green frame (yds right, yds past the green centre)."""
    import v2_course as vc
    import yardage_book as yb
    cfg = vc.config(SLUG)
    PK = vc.product_pk()
    pp = PK._platform_pkg()
    dem = pp.dem_sampler(DEM)
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
            return (dem(fr.px_to_ll(px)) / 0.9144).reshape(lat.shape)

        def to_ll(lat, dep, fr=fr, flag=flag, v=v, right=right, ppy=ppy):
            lat, dep = np.atleast_1d(np.asarray(lat, float)), np.atleast_1d(np.asarray(dep, float))
            px = flag[None, :] + (lat[:, None] * right[None, :] + dep[:, None] * v[None, :]) * ppy
            return fr.px_to_ll(px)
        zt = float(dem(fr.px_to_ll(tee[None, :]))[0] / 0.9144)
        got[k] = dict(p=p, zones=zz, z_at=z_at, z_tee=zt, to_ll=to_ll, tee_ll=fr.px_to_ll(tee[None, :])[0].tolist())
        return p
    PK._par3 = cap
    try:
        PK.load(os.path.join(ROOT, cfg["truth_package"]), set_name)
    finally:
        PK._par3 = orig
    plan = vc.floored_plan(yb.par3_plan)
    yb.WIND_NOW = 0
    for k, g in got.items():
        g["plan"] = plan(g["p"])
    return {k: got[k] for k in HOLES3 if k in got}


def bearings(set_name):
    P = json.load(open(os.path.join(ROOT, "course_data/courses/gateway_national/truth/package.json")))
    return {int(k): P["holes"][str(k)]["tees"][set_name]["bearing_deg"] for k in HOLES3}


def card(set_name):
    P = json.load(open(os.path.join(ROOT, "course_data/courses/gateway_national/truth/package.json")))
    return {int(k): P["holes"][str(k)]["yards"][set_name] for k in HOLES3}


def wx(day, hour):
    """Forecast at a fractional hour, interpolated."""
    f = json.load(open(FORECAST))
    rows = [r for r in f["hourly"] if r["date"] == day]
    hh = np.array([r["hour"] for r in rows], float)

    def it(key):
        return float(np.interp(hour, hh, [r[key] for r in rows]))
    ang = np.radians([r["wind_from_deg"] for r in rows])
    s, c = np.interp(hour, hh, np.sin(ang)), np.interp(hour, hh, np.cos(ang))
    return dict(temp=it("temp_f"), mph=it("wind_mph"), gust=it("gust_mph"), frm=float(np.degrees(np.arctan2(s, c)) % 360))


CUR = {"hole": 4}


def conditions(_hole, bearing):
    k = CUR["hole"]
    hr = TEE_HOUR + (k - 1) * MIN_PER_HOLE / 60.0
    out = {"calm50": dict(temp=50.0, mph=0.0, rel=0.0)}
    for nm, day in (("sat", "2026-11-14"), ("sun", "2026-11-15")):
        w = wx(day, hr)
        out[nm] = dict(temp=round(w["temp"], 1), mph=round(w["mph"], 1), rel=round((w["frm"] - bearing) % 360, 1),
                       gust=round(w["gust"], 1), frm=round(w["frm"]), hour=round(hr, 2))
    return out


E.conditions = conditions


def club_eval(H, cond, o, z, lats, clubs=None):
    """E.club_eval with the 4-wood's own wind sensitivity (E passes 'Mid iron' for every non-engine club)."""
    out = {}
    for c, tup in E.BAG.items():
        if clubs and c not in clubs:
            continue
        car, dev, roll, cmean = E.shot_set(tup, cond, o, z, name=WIND_NAME.get(c, "Mid iron"))
        lat = dev[:, None] + lats[None, :]
        dl = H.land(lat, np.broadcast_to(car[:, None], lat.shape))
        _, s, lie = H.finish(lat, dl, np.broadcast_to(roll[:, None], lat.shape))
        v = 1.0 + s
        m = v.mean(0)
        k = int(m.argmin())
        dep_solid = float(H.land(np.array([lats[k]]), np.array([cmean]))[0])
        out[c] = dict(ev=float(m[k]), lat=float(lats[k]), dep=dep_solid, per=v[:, k],
                      green=float(np.mean(lie[:, k] == E.C["green"])), water=float(np.mean(lie[:, k] == E.C["water"])),
                      trees=float(np.mean(lie[:, k] == E.C["recovery"])), sand=float(np.mean(lie[:, k] == E.C["sand"])))
    return out


E.club_eval = club_eval


class GHole(E.Hole):
    """E.Hole with the lies painted in package order (later zones win, as the page's lie_at does), not E's fixed
    priority (fairway < recovery < native < sand < ob < water). They differ only where zones overlap: on 7 and 14
    the Nov 9 hand native bands (painted first) overlap the lidar trees, which keep the trees."""

    def _pins(self, inset):
        from matplotlib.path import Path
        L, Dg = np.meshgrid(self.la, self.de, indexing="ij")
        pts = np.c_[L.ravel(), Dg.ravel()]
        lie = np.zeros(len(pts), int)
        for nm, poly in self.g["zones"]:
            nm = "fairway" if nm == "first_cut" else nm
            if nm in E.C:
                lie[Path(poly).contains_points(pts)] = E.C[nm]
        lie[self.gpath.contains_points(pts)] = E.C["green"]
        self.lie = lie.reshape(L.shape)
        return super()._pins(inset)


E.Hole = GHole


def setup_engine():
    import v2_course as vc
    course, meta, M, D = vc.activate(SLUG, "truth")
    sys.path.insert(0, os.path.join(ROOT, "spirit_hollow"))
    import wind as W
    for c in E.BAG:
        W.SENSITIVITY.setdefault(c, 1.3)
    W.SENSITIVITY["_p3"] = 1.0
    return M


# ------------------------------------------------------------------ solve
def solve(a):
    os.makedirs(OUT, exist_ok=True)
    holes = [int(x) for x in a.holes.split(",")]
    for s in a.sets.split(","):
        path = os.path.join(OUT, f"par3_target_{s.replace(' ', '_')}.json")
        G = load_holes(s)
        B = bearings(s)
        cards = card(s)
        for k in holes:
            print(s, k, file=sys.stderr, flush=True)
            CUR["hole"] = k
            H = E.Hole(G[k], E.opts())
            fast = a.fast or s != "Back"
            ng, nr = (a.n_grid, a.n_ref) if s == "Back" else (min(a.n_grid, 3000), min(a.n_ref, 16000))
            r = E.solve_hole(H, B[k], E.opts(), ng, nr, fast=fast)
            r.update(bearing=B[k], card=cards[k], tee_ll=G[k]["tee_ll"], z_tee_ft=round(H.z_tee * 3, 1),
                     z_centre_ft=round(H.z_centre * 3, 1), n_grid=ng, n_ref=nr)
            if s != "Back":                        # keep results small: coarse surfaces for Back only
                for x in r["aims"].values():
                    x.pop("surface", None)
            merge_json(path, {f"{s} {k}": r})
    write_page()


def merge_json(path, new, deep=False):
    """Read-update-write under a lock (several holes may be solved at once)."""
    import fcntl
    with open(path + ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        res = json.load(open(path)) if os.path.exists(path) else {}
        for k, v in new.items():
            if deep and isinstance(res.get(k), dict):
                res[k].update(v)
            else:
                res[k] = v
        json.dump(res, open(path, "w"), separators=(",", ":"))


def all_results():
    res = {}
    for s in SETS:
        p = os.path.join(OUT, f"par3_target_{s.replace(' ', '_')}.json")
        if os.path.exists(p):
            res.update(json.load(open(p)))
    return res


def write_page():
    res = all_results()
    page = {"source": "course_data/courses/gateway_national/opt/par3_target.py (PAR3.md)", "sets": {}}
    for key, r in sorted(res.items()):
        s, k = key.rsplit(" ", 1)
        boxes = {}
        for mod in (-1, 0, 1, 2, 3):
            x = r["aims"][f"mod{mod}"]
            boxes[str(mod)] = dict(aim=x["best"], lat=x["box_lat"], dep=x["box_dep"])
        cl = {}
        for nm, c in r["clubs"].items():
            cl[nm] = dict(pick=E.SHORT_NAME.get(c["pick"], c["pick"]), runner=E.SHORT_NAME.get(c["runner"], c["runner"]),
                          tie=c["tie"], margin=c["margin"][0])
        page["sets"].setdefault(s, {})[k] = dict(boxes=boxes, clubs=cl,
                                                 gain_vs_centre=r["aims"]["mod-1"]["gain_vs_centre"],
                                                 gain_vs_decade=r["aims"]["mod-1"]["gain_vs_decade"])
    json.dump(page, open(PAGE, "w"), indent=1)
    print("wrote", PAGE, file=sys.stderr)


# ------------------------------------------------------------------ sensitivity and numbers
VARIANTS = {
    "temp 35": dict(c=dict(temp=35.0)), "temp 65": dict(c=dict(temp=65.0)),
    "disp +15%": dict(o=dict(width_mult=1.15, depth_mult=1.15)), "disp -15%": dict(o=dict(width_mult=0.85, depth_mult=0.85)),
    "depth x2": dict(o=dict(depth_mult=2.0)),
    "head 10": dict(c=dict(mph=10.0, gust=16.0, rel=0.0)), "tail 10": dict(c=dict(mph=10.0, gust=16.0, rel=180.0)),
    "from left 10": dict(c=dict(mph=10.0, gust=16.0, rel=270.0)), "from right 10": dict(c=dict(mph=10.0, gust=16.0, rel=90.0)),
    "head 20": dict(c=dict(mph=20.0, gust=28.0, rel=0.0)),
    "carry +5": dict(o=dict(carry_shift=5.0)), "carry -5": dict(o=dict(carry_shift=-5.0)),
    "roll x0.5": dict(o=dict(roll_mult=0.5)), "roll x1.5": dict(o=dict(roll_mult=1.5)),
    "no slope": dict(o=dict(slope_beta=0.0)), "slope x2": dict(o=dict(slope_beta=0.04)),
    "trees half": dict(o=dict(tree_cost=0.5)), "no mishits": dict(o=dict(mishits=False)),
    "pins 3 in": dict(o=dict(pin_inset=3.0)), "pins 6 in": dict(o=dict(pin_inset=6.0)),
}


def robust(a):
    base = all_results()
    lats = np.arange(-16.0, 16.0 + 1e-9, 1.0)
    deps = np.arange(-24.0, 16.0 + 1e-9, 1.0)
    variants = VARIANTS if not a.variants else {k: v for k, v in VARIANTS.items() if k in a.variants.split("|")}
    for s in a.sets.split(","):
        G = load_holes(s)
        for k in [int(x) for x in a.holes.split(",")]:
            ref = tuple(base[f"{s} {k}"]["aims"]["mod-1"]["best"])
            res = {}
            for name, v in variants.items():
                o = E.opts(**v.get("o", {}))
                H = E.Hole(G[k], o)
                cond = dict(temp=50.0, mph=0.0, rel=0.0)
                cond.update(v.get("c", {}))
                z = E.draws(a.n_grid, 21)
                vals = E.solve_surface_z(H, cond, o, z, lats, deps)
                i, j, m = E.best_of(vals, lats, deps)
                nb = (float(lats[i]), float(deps[j]))
                z2 = E.draws(a.n_ref, 22)
                L2, D2 = sorted({nb[0], ref[0], 0.0}), sorted({nb[1], ref[1], 0.0})
                pts = E.solve_surface_z(H, cond, o, z2, np.array(L2), np.array(D2))

                def at(p):
                    return pts[L2.index(p[0]), D2.index(p[1]), :]
                keep, se1 = E.paired(at(nb), at(ref))
                cen, se2 = E.paired(at(ref), at((0.0, 0.0)))
                res[name] = dict(best=list(nb), regret_of_page_aim=[round(-keep, 4), round(se1, 4)],
                                 page_aim_gain_vs_centre=[round(-cen, 4), round(se2, 4)],
                                 carry70_to_page_aim=round(float(E.carry_needed(H, ref[1], cond, o)), 1)
                                 if not cond.get("dirs") else None)
                print(s, k, name, json.dumps(res[name]), file=sys.stderr, flush=True)
            merge_json(os.path.join(OUT, "par3_robust.json"), {f"{s} {k}": res}, deep=True)


def mapvar(a):
    """Map questions near the par-3 greens (PAR3.md): the page aim's regret if the map is wrong.
    4: (a) the smooth 'fairway' lobe left of the green (reviewer A's note) is putting surface, pins there too;
       (b) reviewer A's C4: native 24-54 yds past the centre, beyond the path.
    7: the 2014-lidar 'trees' left-short of the green are rough (they look thinner on NAIP 2023)."""
    import copy
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    base = all_results()
    lats = np.arange(-16.0, 16.0 + 1e-9, 1.0)
    deps = np.arange(-24.0, 16.0 + 1e-9, 1.0)
    for s in a.sets.split(","):
        HH = load_holes(s)
        va = {}
        g0 = HH[4]
        gp = Polygon(np.array(g0["p"]["green"]))
        win = Polygon([(-40, -12), (0, -12), (0, 15), (-40, 15)])       # left of the green, its depth
        lobes = [Polygon(p).buffer(0).intersection(win).difference(gp) for nm, p in g0["zones"]
                 if nm == "fairway" and Polygon(p).buffer(0).distance(gp) < 1.0]
        lobes = [x for x in lobes if x.area > 20]
        if lobes:
            ga = copy.copy(g0)
            ga["p"] = dict(g0["p"])
            u = unary_union([gp] + [x.buffer(0.5) for x in lobes])
            u = max(getattr(u, "geoms", [u]), key=lambda q: q.area)
            print("hole 4 lobe area", round(sum(x.area for x in lobes)), "green", round(gp.area), file=sys.stderr)
            ga["p"]["green"] = [tuple(c) for c in np.array(u.exterior.coords)[:-1]]
            va[(4, "lobe is green")] = ga
        gb = copy.copy(g0)
        gb["zones"] = list(g0["zones"]) + [("native", np.array([[-60, 24], [20, 24], [20, 54], [-60, 54]], float))]
        va[(4, "C4 native long")] = gb
        g7 = HH[7]
        gc = copy.copy(g7)
        gc["zones"] = [(("rough" if nm == "recovery" and np.mean(p[:, 0]) < -10 and np.mean(p[:, 1]) < 10 else nm), p)
                       for nm, p in g7["zones"]]
        va[(7, "left-short trees are rough")] = gc
        res = {}
        for (k, nm), g in va.items():
            ref = tuple(base[f"{s} {k}"]["aims"]["mod-1"]["best"])
            o = E.opts()
            H = E.Hole(g, o)
            cond = dict(temp=50.0, mph=0.0, rel=0.0)
            vals = E.solve_surface_z(H, cond, o, E.draws(a.n_grid, 21), lats, deps)
            i, j, m = E.best_of(vals, lats, deps)
            nb = (float(lats[i]), float(deps[j]))
            L2, D2 = sorted({nb[0], ref[0], 0.0}), sorted({nb[1], ref[1], 0.0})
            pts = E.solve_surface_z(H, cond, o, E.draws(a.n_ref, 22), np.array(L2), np.array(D2))

            def at(p):
                return pts[L2.index(p[0]), D2.index(p[1]), :]
            k1, s1 = E.paired(at(nb), at(ref))
            k2, s2 = E.paired(at(ref), at((0.0, 0.0)))
            res.setdefault(f"{s} {k}", {})[nm] = dict(best=list(nb), regret_of_page_aim=[round(-k1, 4), round(s1, 4)],
                                                      page_aim_gain_vs_centre=[round(-k2, 4), round(s2, 4)],
                                                      n_pins=int(len(H.pins)))
            print(s, k, nm, json.dumps(res[f"{s} {k}"][nm]), file=sys.stderr, flush=True)
        for key, v in res.items():
            merge_json(os.path.join(OUT, "par3_robust.json"), {key: v}, deep=True)


def numbers(a):
    """Plays-like carry (70 F flat-ground equivalent) to the calm box aim and to the centre, by temperature and wind,
    on the model's own geometry (map distance) and on the page's card formula ((card + aim + dz) / temperature)."""
    import v2_course as vc
    import wind_grid as WG
    base = all_results()
    meta = json.load(open(vc.cdir(SLUG, "truth", "meta.json")))
    out = {}
    for s in SETS:
        if not any(k.startswith(s + " ") and k[len(s) + 1:].isdigit() for k in base):
            continue
        G = load_holes(s)
        cards = card(s)
        for k in HOLES3:
            key = f"{s} {k}"
            if key not in base:
                continue
            H = E.Hole(G[k], E.opts())
            r = base[key]
            aim = r["aims"]["mod-1"]["best"][1]
            dz = float(meta["holes"][str(k)]["dz"])
            A = cards[k] + aim
            row = dict(card=cards[k], map_centre=round(H.center, 1), aim_dep=aim, dz_page=dz,
                       z_drop_ft_to_aim=round(3 * (H.z_tee - float(H.z[H.idx(np.array([0.0]), np.array([aim]))][0])), 1))
            for T in (35, 40, 45, 50, 55, 60, 65):
                tf = 1 - 0.00075 * (70 - T)
                row[f"page_{T}F"] = round((A + dz) / tf, 1)
                row[f"model_{T}F"] = round(float(E.carry_needed(H, aim, dict(temp=float(T), mph=0.0, rel=0.0), E.opts())), 1)
                row[f"model_centre_{T}F"] = round(float(E.carry_needed(H, 0.0, dict(temp=float(T), mph=0.0, rel=0.0), E.opts())), 1)
            tf50 = 1 - 0.00075 * 20
            for mph in (5, 10, 15, 20):
                for d, nm in ((0, "head"), (180, "tail"), (90, "cross")):
                    row[f"page_50F_{nm}{mph}"] = round((WG.plays_like(A, mph, d) + dz) / tf50, 1)
            for day in ("sat", "sun"):
                c = r["conds"][day]
                row[day] = dict(c, model=round(float(E.carry_needed(H, r["aims"][day]["best"][1], c, E.opts())), 1),
                                aim=r["aims"][day]["best"])
            out[key] = row
            print(key, json.dumps(row), file=sys.stderr, flush=True)
    json.dump(out, open(os.path.join(OUT, "par3_numbers.json"), "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["solve", "robust", "numbers", "page", "mapvar"])
    ap.add_argument("--sets", default="Back")
    ap.add_argument("--holes", default="4,7,12,14,17")
    ap.add_argument("--n-grid", type=int, default=6000)
    ap.add_argument("--n-ref", type=int, default=40000)
    ap.add_argument("--variants", default="")
    ap.add_argument("--fast", action="store_true")
    a = ap.parse_args()
    setup_engine()
    os.makedirs(OUT, exist_ok=True)
    if a.cmd == "solve":
        solve(a)
    elif a.cmd == "robust":
        robust(a)
    elif a.cmd == "mapvar":
        mapvar(a)
    elif a.cmd == "numbers":
        numbers(a)
    else:
        write_page()


if __name__ == "__main__":
    main()
