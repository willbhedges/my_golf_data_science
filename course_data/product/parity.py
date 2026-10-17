"""Decision parity: the product's decision path vs the hand pipeline on the SAME hand-checked geometry.

  python3 course_data/product/parity.py [--n 8000] [--holes 1,2,11] [--ladder] [--out <dir>]
  (Actions: .github/workflows/parity.yml, request file course_data/requests/parity_<name>.json)

Two ways into the strategy model (mozingo/tee_strategy.simulate via product/decide.quick_hole, the same prior-mean
settings, N and seed in both, so every difference is an INPUT difference):

  hand     spirit_hollow/course.py HOLES (screenshot px; tees on the real Black box, BLACK_TEE_FORWARD; the app line
           toward the 270 dot; zones in the traced order incl. AUDIT_FIXES / landing QA / first_cut; elevation
           elev_registered.json along the registered screenshot line; irons on 11 and 13; aims +/-40)
  product  the Spirit Hollow package with the hand map put in (verify_hand_truth.hand_package: hand_zones_ll.json
           zones + the Black-box tee) -> product/package.load (product frame, its zone order, its tee line,
           its elevation, its irons rule) -> the generated HOLES

Step 1 (geometry, per tee hole): tee (yds apart, WGS84), tee-line bearing, the frame's yards per app yard (the
hand map is scaled by the app's 270 dot, the product by the ground), length, green, effective lie IoU per lie
in the landing corridor (100-340 yds x +/-60, 2-yd grid: what tee_strategy.lie_at returns in each frame), the
share of that corridor whose lie changes with the zone ORDER, first-cut share, elevation per club, irons, aims.
Step 2 (decision): pick / aim (yds right of the HAND tee line at the club's carry) / EV per club on both.
Step 3 (--ladder): attribution. Every hand input is also mapped into the product frame (screenshot px ->
WGS84 via the hand registration -> product px), so each factor can be switched from product to hand one at a
time (and all together: the "all hand" row must reproduce the hand pick; it checks the mapping itself).

Factors: tee, line (bearing), scale (app vs ground yards), zones (hand polygons in hand order), order (the
package's own zones in the order given), elev, green, irons, aims (search range), guard (the line-of-play
guard: hand holes have no play_line).

Writes <out>/parity.json and parity.md (default course_data/packages/spirit_hollow/out/review/).
"""
import argparse
import contextlib
import copy
import importlib.util
import io
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
for _p in (HERE, os.path.join(CD, "imagery"), os.path.join(ROOT, "mozingo")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import package as PK                                # noqa: E402
import render as R                                  # noqa: E402

HAND_LL = os.path.join(CD, "spirit_hollow", "hand_zones_ll.json")
SH_COURSE = os.path.join(ROOT, "spirit_hollow", "course.py")
SH_PACKAGE = os.path.join(CD, "packages", "spirit_hollow", "package.json")
OUT = os.path.join(CD, "packages", "spirit_hollow", "out", "review")
FACTORS = ["tee", "line", "scale", "zones", "order", "elev", "green", "irons", "aims", "guard"]
LIES = ("fairway", "first_cut", "rough", "sand", "recovery", "native", "water", "ob")
ALONG = np.arange(100, 340.1, 2.0)
LAT = np.arange(-60, 60.1, 2.0)
AIM_TOL = 2.5


def log(*a):
    print(*a, flush=True)


# ----------------------------------------------------------------------------- loading
def load_hand_course():
    """spirit_hollow/course.py as a fresh module (Black boxes)."""
    os.environ.pop("SH_SCREENSHOT_TEES", None)
    sp = os.path.join(ROOT, "spirit_hollow")
    if sp not in sys.path:
        sys.path.insert(0, sp)
    spec = importlib.util.spec_from_file_location("parity_sh_course", SH_COURSE)
    mod = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    return mod


class ShotGeo:
    """Screenshot px <-> WGS84 for one hand-traced hole (spirit_hollow/geo_zones.ShotGeo, no cv2)."""

    def __init__(self, hh):
        self.frame = R.Frame.from_json(hh["frame"])
        self.warp = np.asarray(hh["warp"], float)
        self.inv = np.linalg.inv(np.vstack([self.warp, [0, 0, 1]]))[:2]

    def px_to_ll(self, px):
        p = np.atleast_2d(np.asarray(px, float))
        return self.frame.px_to_ll(p @ self.warp[:, :2].T + self.warp[:, 2])

    def ll_to_px(self, ll):
        q = self.frame.ll_to_px(np.atleast_2d(np.asarray(ll, float)))
        return q @ self.inv[:, :2].T + self.inv[:, 2]


def hand_key(k, tee_set="Black"):
    box = "B" if tee_set.lower() == "gold" else "F"
    return str(k) if str(k) not in ("2", "9") else f"{k}{box}"


def course_key(hk):
    return int(hk) if str(hk).isdigit() else hk


def product_course(pkg_path=SH_PACKAGE, tee_set="Black", hand=None):
    """The product path on the hand map: package with hand zones + Black-box tees -> package.load -> Course."""
    import tempfile
    import verify_hand_truth as VH
    hand = hand or json.load(open(HAND_LL))
    pkg = json.load(open(pkg_path))
    new = VH.hand_package(pkg, hand, tee_set)
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "package.json")
        with open(p, "w") as fh:
            json.dump(new, fh)
        C = PK.load(p, tee_set)
    return C, new


def _enu(ll, ref):
    ll = np.atleast_2d(np.asarray(ll, float))
    k = np.array([111320.0 * math.cos(math.radians(ref[1])), 110540.0]) / 0.9144
    return (ll - np.asarray(ref, float)) * k


def _bearing(a, b):
    return PK.bearing_deg(a, b)


def frame_vectors(hd):
    tee = np.array(hd["tee"], float)
    v = np.array(hd["dot270"], float) - tee
    ppy = np.linalg.norm(v) / 270.0
    f = v / np.linalg.norm(v)
    return tee, f, np.array([-f[1], f[0]]), ppy


def lie_grid(hd, to_px):
    """Effective lie (tee_strategy.lie_at) on WGS84 points mapped into this hole's px."""
    from matplotlib.path import Path
    pts = to_px
    lie = np.array(["rough"] * len(pts), dtype=object)
    for name, poly in hd["zones"]:
        if len(poly) >= 3:
            lie[Path(np.asarray(poly, float)).contains_points(pts)] = name
    return lie


# ----------------------------------------------------------------------------- hand inputs in the product frame
def hand_in_product(hd, geo, fr):
    """Every hand input of one hole mapped into the product frame (screenshot px -> WGS84 -> product px)."""
    def m(pts):
        return fr.ll_to_px(geo.px_to_ll(np.asarray(pts, float)))
    out = dict(tee=tuple(m([hd["tee"]])[0]), dot270=tuple(m([hd["dot270"]])[0]), green=tuple(m([hd["green"]])[0]),
               zones=[(n, [tuple(q) for q in m(p)]) for n, p in hd["zones"] if len(p) >= 3],
               elev=copy.deepcopy(hd.get("elev")), irons=bool(hd.get("irons")),
               aim_min=hd.get("aim_min", -40), aim_max=hd.get("aim_max", 40), extra_roll=hd.get("extra_roll"))
    return out


def variant(P, H, factors, given_order_zones=None):
    """A product hole dict with `factors` switched to the hand's version (H = hand_in_product)."""
    v = copy.deepcopy(P)
    f = set(factors)
    tee0, fw0, _, ppy0 = frame_vectors(P)
    tee = np.array(H["tee"] if "tee" in f else P["tee"], float)
    if "line" in f:
        d = np.array(H["dot270"], float) - np.array(H["tee"], float)
        fwd = d / np.linalg.norm(d)
        dist = (np.linalg.norm(d) / PK.PPY) if "scale" in f else 270.0   # ground yds to the hand's dot
    else:
        fwd, dist = fw0, 270.0
    ppy = PK.PPY * (270.0 / dist) if "scale" in f else PK.PPY
    # tee_strategy's yards come from |dot270 - tee| / 270, so the dot carries the scale
    v["tee"] = tuple(tee)
    v["dot270"] = tuple(tee + fwd * 270.0 * ppy)
    if "zones" in f:
        v["zones"] = copy.deepcopy(H["zones"])
    elif "order" in f and given_order_zones is not None:
        v["zones"] = copy.deepcopy(given_order_zones)
    if "elev" in f:
        if H["elev"]:
            v["elev"] = copy.deepcopy(H["elev"])
        else:
            v.pop("elev", None)
    if "green" in f:
        v["green"] = H["green"]
    if "irons" in f:
        if H["irons"]:
            v["irons"] = True
        else:
            v.pop("irons", None)
    if "aims" in f:
        v["aim_min"], v["aim_max"] = H["aim_min"], H["aim_max"]
    if "guard" in f:
        v.pop("play_line", None)
    if H.get("extra_roll") and "zones" in f:
        v["extra_roll"] = H["extra_roll"]
    return v


def given_order_zones(pkg_hole, fr):
    """The package's own zones_ll in the order given (no precedence sort), product px."""
    out = []
    for z in pkg_hole.get("zones_ll") or []:
        lie = PK.LIE_MAP.get(z["lie"], z["lie"])
        if lie not in PK.MODEL_LIES or len(z.get("poly") or []) < 3:
            continue
        q = fr.ll_to_px(np.array(z["poly"], float)[:, :2])
        out.append((lie, [(float(x), float(y)) for x, y in q]))
    return out


# ----------------------------------------------------------------------------- decision
def decide_one(hd, key="h", n=8000, seed=31):
    import decide
    import tee_strategy as t
    decide.bind({key: hd})
    t.HOLES = copy.deepcopy(decide.BASE["holes"])
    r = decide.quick_hole(key, n=n, seed=seed)
    return r


def aim_in_hand(hd, club, aim, to_hand_px, hand_hd):
    """Yards right of the HAND tee line of a result's aim point at the club's carry."""
    import decide
    tee, f, r, ppy = frame_vectors(hd)
    pt = tee + (decide._carry(club) * f + float(aim) * r) * ppy
    q = to_hand_px(pt[None, :])[0]
    ht, hf, hr, hp = frame_vectors(hand_hd)
    return float((q - ht) @ hr / hp)


def summary(r):
    return dict(pick=r["pick"], aim=round(float(r["aim"]), 1), tie=bool(r["tie"]), runner=r["runner"],
                margin=round(float(r["margin"]), 4),
                ev={c: round(float(v["ev"]), 4) for c, v in r["clubs"].items()},
                aims={c: round(float(v["aim"]), 1) for c, v in r["clubs"].items()}, check=r.get("check") or [])


def same_or_tie(a, b):
    return a["pick"] == b["pick"] or (a["tie"] and a["runner"] == b["pick"]) or (b["tie"] and b["runner"] == a["pick"])


# ----------------------------------------------------------------------------- per hole
def compare_hole(k, hk, hd_hand, P, C, hand_ll, pkg_hole, n, ladder, log=log):
    hh = hand_ll["holes"][hk]
    geo = ShotGeo(hh)
    fr = R.Frame.from_json(C.frames[k])
    H = hand_in_product(hd_hand, geo, fr)
    tee_h_ll = geo.px_to_ll([hd_hand["tee"]])[0]
    dot_h_ll = geo.px_to_ll([hd_hand["dot270"]])[0]
    tee_p_ll = fr.px_to_ll([P["tee"]])[0]
    aim_p_ll = fr.px_to_ll([P["dot270"]])[0]
    ref = tee_h_ll
    tee_err = float(np.linalg.norm(_enu([tee_p_ll], ref)[0]))
    b_h, b_p = _bearing(tee_h_ll, dot_h_ll), _bearing(tee_p_ll, aim_p_ll)
    dbear = (b_p - b_h + 180) % 360 - 180
    app_scale = float(np.linalg.norm(_enu([dot_h_ll], ref)[0]) / 270.0)    # ground yds per app yd
    g_h = geo.px_to_ll([hd_hand["green"]])[0]
    g_p = fr.px_to_ll([P["green"]])[0]
    green_err = float(np.linalg.norm(_enu([g_p], g_h)[0]))
    # effective lies on a WGS84 grid along the hand tee line
    ht, hf, hr, hp = frame_vectors(hd_hand)
    A, L = np.meshgrid(ALONG, LAT)
    grid_hpx = ht + (A.ravel()[:, None] * hf + L.ravel()[:, None] * hr) * hp
    grid_ll = geo.px_to_ll(grid_hpx)
    grid_ppx = fr.ll_to_px(grid_ll)
    inside = np.ones(len(grid_hpx), bool)
    if hh.get("footprint_ll"):
        from matplotlib.path import Path
        inside = Path(np.asarray(hh["footprint_ll"], float)).contains_points(grid_ll)
    lh = lie_grid(hd_hand, grid_hpx)[inside]
    lp = lie_grid(P, grid_ppx)[inside]
    lg = lie_grid(dict(zones=given_order_zones(pkg_hole, fr)), grid_ppx)[inside]
    iou = {}
    for lie in LIES:
        a, b = lh == lie, lp == lie
        u = (a | b).sum()
        if u:
            iou[lie] = dict(iou=round(float((a & b).sum() / u), 3), hand=round(float(a.mean()), 3), product=round(float(b.mean()), 3))
    geom = dict(tee_err_yd=round(tee_err, 1), bearing_hand=round(b_h, 1), bearing_product=round(b_p, 1),
                dbearing_deg=round(dbear, 1), ground_yd_per_app_yd=round(app_scale, 4),
                length_hand=hd_hand["length"], length_product=P["length"], green_err_yd=round(green_err, 1),
                lie_agree=round(float((lh == lp).mean()), 3), lie_agree_given_order=round(float((lh == lg).mean()), 3),
                order_changes=round(float((lg != lp).mean()), 3), iou=iou,
                n_zones_hand=len(hd_hand["zones"]), n_zones_product=len(P["zones"]),
                zone_order_hand=[z[0] for z in hd_hand["zones"]], zone_order_product=[z[0] for z in P["zones"]],
                elev_hand=hd_hand.get("elev"), elev_product=P.get("elev"),
                irons_hand=bool(hd_hand.get("irons")), irons_product=bool(P.get("irons")),
                aims_hand=[hd_hand.get("aim_min"), hd_hand.get("aim_max")], aims_product=[P.get("aim_min"), P.get("aim_max")],
                play_line_product=bool(P.get("play_line")), extra_roll=[hd_hand.get("extra_roll"), P.get("extra_roll")])
    to_hand_px = (lambda pts: geo.ll_to_px(fr.px_to_ll(pts)))
    ident = (lambda pts: pts)
    t0 = time.time()
    rh = decide_one(hd_hand, hk, n)
    rp = decide_one(P, k, n)
    res = dict(hand=summary(rh), product=summary(rp))
    res["hand"]["aim_hand_line"] = round(aim_in_hand(hd_hand, rh["pick"], rh["aim"], ident, hd_hand), 1)
    res["product"]["aim_hand_line"] = round(aim_in_hand(P, rp["pick"], rp["aim"], to_hand_px, hd_hand), 1)
    rows = {}
    if ladder:
        gz = given_order_zones(pkg_hole, fr)
        steps = [("all hand", FACTORS)] + [(f"only {f}", [f] + (["line"] if f == "scale" else [])) for f in FACTORS] \
            + [(f"all but {f}", [g for g in FACTORS if g != f and not (f == "line" and g == "scale")]) for f in FACTORS]
        for name, fs in steps:
            hd = variant(P, H, fs, gz)
            r = decide_one(hd, k, n)
            s = summary(r)
            s["aim_hand_line"] = round(aim_in_hand(hd, r["pick"], r["aim"], to_hand_px, hd_hand), 1)
            rows[name] = s
    res["ladder"] = rows
    res["secs"] = round(time.time() - t0, 1)
    log(f"  {hk}: hand {rh['pick']} {res['hand']['aim_hand_line']:+.1f} | product {rp['pick']} "
        f"{res['product']['aim_hand_line']:+.1f} | tee {tee_err:.1f} yd, bearing {dbear:+.1f} deg, "
        f"lies agree {geom['lie_agree']:.0%} (given order {geom['lie_agree_given_order']:.0%}) [{res['secs']}s]")
    return dict(geometry=geom, **res)


def attribute(res):
    """Which factors explain a disagreement: switching it alone to hand fixes it, or leaving it alone at the
    product's value (all others hand) breaks it."""
    lad = res.get("ladder") or {}
    hand = res["hand"]
    out = []
    for f in FACTORS:
        only, but = lad.get(f"only {f}"), lad.get(f"all but {f}")
        fixes = only is not None and only["pick"] == hand["pick"] and res["product"]["pick"] != hand["pick"]
        breaks = but is not None and but["pick"] != hand["pick"]
        if fixes or breaks:
            out.append(f + (" (alone fixes)" if fixes else "") + (" (needed)" if breaks else ""))
    return out


def settings_table():
    """Model settings of the three hand-pipeline runs vs the product's quick decision (read from the code)."""
    import decide
    import tee_strategy as t
    saved = (copy.deepcopy(t.CLUBS), copy.deepcopy(t.IRONS), t.TREE_SEVERITY, t.NATIVE_LOST, dict(t.MISHIT_RATE), t.HCP_BASELINE)
    decide.set_prior_means()
    q = dict(driver_width=t.CLUBS["Driver"][2], driver_depth=t.CLUBS["Driver"][3], trees=t.TREE_SEVERITY,
             lost=t.NATIVE_LOST, mishit=t.MISHIT_RATE["Driver"], hcp=t.HCP_BASELINE, long_slope=t.LONG_SLOPE,
             first_cut_cost=t.FIRST_CUT_COST)
    t.CLUBS, t.IRONS, t.TREE_SEVERITY, t.NATIVE_LOST, t.MISHIT_RATE, t.HCP_BASELINE = saved
    return [
        ("driver width (yds, 95%)", f"{q['driver_width']:.1f} (65 x 70/65)", "70 (wind_grid.set_prior_means)", "Sobol prior, median 70, 90% to 80"),
        ("carry depth", f"{q['driver_depth']:.1f} (x1.25)", "x1.25", "prior depth / 1.5 x 1.25"),
        ("tree severity / long grass lost", f"{q['trees']} / {q['lost']}", "0.8 / 0.5", "prior draws"),
        ("mishit rate", f"{q['mishit']}", "0.15", "prior draws"),
        ("baselines", "tour" if not q["hcp"] else "5-hcp", "tour (default)", "tour (hcp False)"),
        ("LONG_SLOPE / FIRST_CUT_COST", f"{q['long_slope']} / {q['first_cut_cost']}", "same module", "same module"),
        ("swings, seed", "8000, 31 (decide._z)", "4000, 31 (same draw layout)", "3000 per draw, 128 draws, seed 2027"),
        ("wood aims", f"+/-{decide.AIM_LIMIT} capped by the hole's aim_min/max, 2.5 step, widened past the edge",
         "-30..+30, 2.5 step", "decision.aims_for: hole aim_min/max capped to +/-25"),
        ("iron aims", "-25..+45", "-30..+45", "-25..+45"),
        ("irons offered", "hole['irons'] (product: package irons rule)", "course.HOLES[h]['irons'] (11, 13)", "same"),
        ("absurd-aim guard", "yes (40 yds; aim point lie; play_line)", "no", "no"),
    ]


def run(n=8000, holes=None, ladder=True, out=OUT, pkg_path=SH_PACKAGE, tee_set="Black", log=log):
    hand_ll = json.load(open(HAND_LL))
    course = load_hand_course()
    C, pkg_new = product_course(pkg_path, tee_set, hand_ll)
    result = dict(n=n, tee_set=tee_set, package=os.path.relpath(pkg_path, ROOT), holes={}, settings=settings_table())
    for k in C.holes:
        hk = hand_key(k, tee_set)
        if hk not in hand_ll["holes"] or course_key(hk) not in course.HOLES:
            continue
        if holes and str(k) not in holes and hk not in holes:
            continue
        r = compare_hole(k, hk, course.HOLES[course_key(hk)], C.holes[k], C, hand_ll, pkg_new["holes"][str(k)],
                         n, ladder, log=log)
        r["attribution"] = attribute(r) if r["hand"]["pick"] != r["product"]["pick"] else []
        result["holes"][hk] = r
    H = result["holes"].values()
    result["same_club"] = [sum(r["hand"]["pick"] == r["product"]["pick"] for r in H), len(result["holes"])]
    result["same_or_tie"] = [sum(same_or_tie(r["hand"], r["product"]) for r in H), len(result["holes"])]
    result["aims_within"] = [sum(r["hand"]["pick"] == r["product"]["pick"] and
                                 abs(r["hand"]["aim_hand_line"] - r["product"]["aim_hand_line"]) <= AIM_TOL for r in H),
                             result["same_club"][0]]
    if out:
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "parity.json"), "w") as fh:
            json.dump(result, fh, indent=1, default=float)
        with open(os.path.join(out, "parity.md"), "w") as fh:
            fh.write(report_md(result))
    log(f"parity: same club {result['same_club']}, same or tie {result['same_or_tie']}, aims within "
        f"{AIM_TOL} yds {result['aims_within']}")
    return result


def report_md(r):
    L = [f"# Decision parity: product vs hand pipeline on the hand map ({r['tee_set']} tees)", "",
         f"Both through product/decide.quick_hole (n={r['n']}, seed 31, prior-mean settings): every difference is an "
         "input difference. Aims are yds right of the hand (app) tee line at the club's carry.", "",
         f"**Same club {r['same_club'][0]}/{r['same_club'][1]}; same or tie {r['same_or_tie'][0]}/{r['same_or_tie'][1]}; "
         f"aims within {AIM_TOL} yds on {r['aims_within'][0]}/{r['aims_within'][1]} same-club holes.**", "",
         "| hole | hand | product | same | tee err | bearing diff | ground/app yd | green err | lies agree (given order) | causes |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for hk, h in r["holes"].items():
        g, a, b = h["geometry"], h["hand"], h["product"]
        same = "yes" if a["pick"] == b["pick"] else ("tie" if same_or_tie(a, b) else "**no**")
        L.append(f"| {hk} | {a['pick']}{' (tie)' if a['tie'] else ''} {a['aim_hand_line']:+.1f} | "
                 f"{b['pick']}{' (tie)' if b['tie'] else ''} {b['aim_hand_line']:+.1f} | {same} | {g['tee_err_yd']} | "
                 f"{g['dbearing_deg']:+.1f} | {g['ground_yd_per_app_yd']:.3f} | {g['green_err_yd']} | "
                 f"{g['lie_agree']:.0%} ({g['lie_agree_given_order']:.0%}) | {', '.join(h.get('attribution') or []) or '-'} |")
    if any(h.get("ladder") for h in r["holes"].values()):
        L += ["", "## Ladder (pick / aim on the hand line, one factor at a time)", ""]
        names = list(next(h for h in r["holes"].values() if h.get("ladder"))["ladder"])
        L += ["| hole | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
        for hk, h in r["holes"].items():
            if h.get("ladder"):
                L.append(f"| {hk} | " + " | ".join(f"{h['ladder'][x]['pick']} {h['ladder'][x]['aim_hand_line']:+.0f}"
                                                   for x in names) + " |")
    L += ["", "## EV per club (hand / product)", "", "| hole | " + " | ".join(("Driver", "2-wood", "4-wood", "Long iron", "Mid iron")) + " |",
          "|---|---|---|---|---|---|"]
    for hk, h in r["holes"].items():
        L.append(f"| {hk} | " + " | ".join(f"{h['hand']['ev'].get(c, float('nan')):.3f} / {h['product']['ev'].get(c, float('nan')):.3f}"
                                           for c in ("Driver", "2-wood", "4-wood", "Long iron", "Mid iron")) + " |")
    L += ["", "## Inputs per hole", "", "| hole | IoU fairway / first cut / trees / long grass / water / sand / OB | zones hand / product | "
          "irons hand / product | aims hand / product | elev Driver hand / product (carry, roll x, kick) |", "|---|---|---|---|---|---|"]
    for hk, h in r["holes"].items():
        g = h["geometry"]
        io = " / ".join(str(g["iou"].get(x, {}).get("iou", "-")) for x in ("fairway", "first_cut", "recovery", "native", "water", "sand", "ob"))
        eh = (g["elev_hand"] or {}).get("Driver")
        ep = (g["elev_product"] or {}).get("Driver")
        L.append(f"| {hk} | {io} | {g['n_zones_hand']} / {g['n_zones_product']} | {g['irons_hand']} / {g['irons_product']} | "
                 f"{g['aims_hand']} / {g['aims_product']} | {tuple(round(x, 2) for x in eh) if eh else '-'} / "
                 f"{tuple(round(x, 2) for x in ep) if ep else '-'} |")
    L += ["", "## Model settings", "", "| setting | product quick (decide.py) | hand calm cell (wind_grid.py) | hand final (final_decision.py) |",
          "|---|---|---|---|"]
    L += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in r["settings"]]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=8000)
    ap.add_argument("--holes", default=None, help="e.g. 1,2F,11")
    ap.add_argument("--no-ladder", action="store_true")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--package", default=SH_PACKAGE)
    ap.add_argument("--request", default=None, help="request JSON {n, holes, ladder, out}")
    a = ap.parse_args(argv)
    kw = dict(n=a.n, holes=a.holes.split(",") if a.holes else None, ladder=not a.no_ladder, out=a.out,
              pkg_path=a.package)
    if a.request:
        rq = json.load(open(a.request))
        kw.update({k: v for k, v in rq.items() if k in ("n", "holes", "ladder", "out")})
        if rq.get("out"):
            kw["out"] = os.path.join(ROOT, rq["out"])
    run(**kw)


if __name__ == "__main__":
    main()
