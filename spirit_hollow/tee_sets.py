"""Spirit Hollow holes for any tee set, built on the hand-checked hazard maps.

  python3 spirit_hollow/tee_sets.py [--sets Gold,Black,White,Rust] [--check]

  import tee_sets
  HOLES, PAR3, images = tee_sets.holes_for("White")
  tee_strategy.HOLES = HOLES                           # best_aim / yardage_book work unchanged

Per hole and tee set:
  * tee   = the set's tee box from the platform package (course_data/packages/spirit_hollow/package.json,
            tees[set].tee_ll, from course_data/tees/place_tee.py).
  * line  = tee -> the point on the OSM hole line 250 yds from that tee (so a forward tee looks at the
            same landing area further up the hole, a back tee at the one behind it). dot270 = 270 yds up
            that line, as in the app frames.
  * frame = a 920 x 2000 render.Frame (proj "enu"), tee at y = 1900, scale chosen so the green (or
            420 yds) fits; image = NAIP 2023 rendered into it (spirit_hollow/tee_sets/<set>/holeNN.jpg).
  * zones = the hand-checked zones (course_data/spirit_hollow/hand_zones_ll.json, made by geo_zones.py)
            projected into the frame, in their original order. On 2 and 9, which have two screenshots,
            the one shot from that set is primary (Gold: 2B / 9B; the rest: 2F / 9F, the Black-tee shots,
            course.LABELS); the other fills in outside the
            primary's footprint. Outside every hand-checked footprint the package's OSM + vision zones
            fill in (flagged in zone_src / coverage).
  * green = OSM green centroid; length = scorecard yards for the set; elevation = USGS 3DEP
            adjustments (course_data/elevation adjust.py) re-run along this frame's tee line.
  Par 3s: tee from the package, flag = OSM green centroid, the hand-traced green outline (yds about the
  flag) turned to the new tee line, and haz / notes carried over; center = card yards (center_measured
  = tee-to-flag on the ground).
"""
import argparse
import copy
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
for _p in (HERE, os.path.join(ROOT, "course_data", "imagery"), os.path.join(ROOT, "mozingo")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import render as R                                         # noqa: E402

PACKAGE = os.path.join(ROOT, "course_data", "packages", "spirit_hollow", "package.json")
SCORECARD = os.path.join(ROOT, "course_data", "tees", "scorecard.json")
HAND = os.path.join(ROOT, "course_data", "spirit_hollow", "hand_zones_ll.json")
NAIP_DIR = os.path.join(ROOT, "course_data", "imagery", "spirit_hollow")
OUT_DIR = os.path.join(HERE, "tee_sets")
SETS = ("Gold", "Black", "White", "Rust")
AIM_ALONG = 250.0
TEE_PX_Y = 1900.0
TOP_Y = 580.0
SOURCES = {2: ("2F", "2B"), 9: ("9F", "9B")}             # holes with two hand-checked screenshots


def _load(path):
    with open(path) as fh:
        return json.load(fh)


def package_holes():
    hs = _load(PACKAGE)["holes"]
    return {int(k): v for k, v in hs.items()} if isinstance(hs, dict) else {int(h["ref"]): h for h in hs}


def card(tee_set):
    sc = _load(SCORECARD)
    ts = sc["tee_sets"][tee_set]
    return {i + 1: y for i, y in enumerate(ts["yards"])}, {i + 1: p for i, p in enumerate(sc["par"])}


# --------------------------------------------------------------------------- geometry helpers
def point_along_line(tee_ll, line_ll, dist=AIM_ALONG):
    """The first point of the hole line (extended back past its start) `dist` yds from the tee,
    beyond the tee's own projection onto the line. Falls back to the line's end."""
    fr = R.Frame(tee_ll, line_ll[-1], proj="enu")
    P = fr._to_yd(np.asarray(line_ll, float)) - fr.t0          # tee at the origin
    u0 = P[1] - P[0]
    u0 /= np.linalg.norm(u0)
    P = np.r_[[P[0] - 400 * u0], P]                            # extend the line back 400 yds
    seg = np.diff(P, axis=0)
    L = np.linalg.norm(seg, axis=1)
    s = np.r_[0, np.cumsum(L)]
    t = np.arange(0, s[-1], 1.0)
    pts = np.c_[np.interp(t, s, P[:, 0]), np.interp(t, s, P[:, 1])]
    d = np.linalg.norm(pts, axis=1)
    i0 = int(np.argmin(d))
    after = np.flatnonzero((d >= dist) & (np.arange(len(d)) > i0))
    q = pts[after[0]] if len(after) else P[-1]
    return tuple(fr._from_yd(fr.t0 + q)[0])


def make_frame(tee_ll, aim_ll, green_ll):
    """920 x 2000 frame: tee at y 1900, the green (capped at 420 yds) inside the top at y 580."""
    fr0 = R.Frame(tee_ll, aim_ll, proj="enu")
    gx, gy = fr0.ll_to_yds([green_ll])[0]                       # x right, y = -along
    need = float(np.clip(-gy + 20, 300, 420))
    ppy = float(np.clip((TEE_PX_Y - TOP_Y) / need, 2.6, 4.4))
    # shift the tee sideways so the green and the landing area (+/- 60 at 250) stay on screen
    lat_lo, lat_hi = min(gx - 25, -60), max(gx + 25, 60)
    x = 460 - 0.5 * (lat_lo + lat_hi) * ppy
    x = float(np.clip(x, 140, 780))
    return R.Frame(tee_ll, aim_ll, ppy=ppy, tee_px=(x, TEE_PX_Y), proj="enu")


def _simple_parts(geom, depth=0):
    """Shapely (Multi)Polygon -> list of hole-free polygons (exterior rings tee_strategy can use)."""
    from shapely.geometry import LineString, Polygon
    from shapely.ops import split
    if geom.is_empty:
        return []
    if geom.geom_type in ("MultiPolygon", "GeometryCollection"):
        return [p for g in geom.geoms for p in _simple_parts(g, depth)]
    if geom.geom_type != "Polygon":
        return []
    if not geom.interiors or depth > 6:
        return [Polygon(geom.exterior)] if geom.area > 0 else []
    c = Polygon(geom.interiors[0]).centroid
    x0, y0, x1, y1 = geom.bounds
    cut = LineString([(c.x, y0 - 1), (c.x, y1 + 1)])
    return [p for g in split(geom, cut).geoms for p in _simple_parts(g, depth + 1)]


def _poly_px(fr, ring_ll):
    return [tuple(map(float, p)) for p in fr.ll_to_px(np.asarray(ring_ll, float))]


# --------------------------------------------------------------------------- elevation
_DEM = []


def elevation_along(ref, tee_ll, toward_ll, green_poly_ll, par):
    """course_data/elevation analysis + adjust.py along THIS frame's tee line (the package's per-set
    numbers are along its own tee -> aim line, which can differ by 15+ deg). -> adjust.adjustments dict."""
    edir = os.path.join(ROOT, "course_data", "elevation")
    if edir not in sys.path:
        sys.path.insert(0, edir)
    import adjust as A
    import course
    import holes_elevation as HE
    if not _DEM:
        _DEM.append(HE.Dem())
    dem = _DEM[0]
    t, a = dem.xy([tee_ll])[0], dem.xy([toward_ll])[0]
    gp = dem.xy(np.asarray(green_poly_ll, float))
    geo = dict(tee_xy=t, u=(a - t) / np.linalg.norm(a - t), green_poly=gp, green_xy=HE.poly_centroid(gp))
    out = HE.analyse(dem, course, ref, geo)
    out["par"] = par
    return A.adjustments(str(ref), holes={str(ref): out})


# --------------------------------------------------------------------------- build
def tee_hole(ref, tee_set, pk, hand, yards, par, course, tee_source="package"):
    """One tee-shot hole in the tee_strategy dict format.

    tee_source "app": tee and line = the app screenshot's own (hand_zones tee_ll -> dot270_ll) for the
    screenshot taken from this set (2F / 9F = Black, 2B / 9B = Gold); a check of the conversion."""
    from shapely.geometry import Polygon
    from shapely.validation import make_valid
    tee = pk["tees"][tee_set]
    tee_ll = tuple(tee["tee_ll"])
    aim_ll = point_along_line(tee_ll, pk["hole_line_ll"])
    if tee_source == "app":
        k0 = {2: "2B" if tee_set == "Gold" else "2F", 9: "9B" if tee_set == "Gold" else "9F"}.get(ref, str(ref))
        tee_ll, aim_ll = tuple(hand[k0]["tee_ll"]), tuple(hand[k0]["dot270_ll"])
    green_ll = tuple(pk["green_ll"])
    fr = make_frame(tee_ll, aim_ll, green_ll)
    keys = list(SOURCES.get(ref, (str(ref),)))
    if len(keys) == 2 and tee_set == "Gold":                    # 2B / 9B were shot from the Gold tee
        keys = keys[::-1]
    primary = hand[keys[0]]
    foot = [Polygon(_poly_px(fr, hand[k]["footprint_ll"])) for k in keys]
    zones, src = [], []
    covered = foot[0]
    # package OSM + vision zones outside every hand-checked footprint (lowest priority)
    union = foot[0]
    for f in foot[1:]:
        union = union.union(f)
    for z in pk.get("zones_ll", []):
        try:
            g = make_valid(Polygon(_poly_px(fr, z["poly"]))).difference(union)
        except Exception:
            continue
        for p in _simple_parts(g):
            zones.append((z["lie"], [tuple(c) for c in list(p.exterior.coords)[:-1]]))
            src.append("package")
    # secondary screenshot outside the primary's footprint
    for k in keys[1:]:
        for z in hand[k]["zones"]:
            g = make_valid(Polygon(_poly_px(fr, z["poly_ll"]))).difference(covered)
            for p in _simple_parts(g):
                zones.append((z["lie"], [tuple(c) for c in list(p.exterior.coords)[:-1]]))
                src.append(f"hand:{k}")
        covered = covered.union(foot[1])
    for z in primary["zones"]:
        zones.append((z["lie"], _poly_px(fr, z["poly_ll"])))
        src.append(f"hand:{keys[0]}")
    ck = int(keys[0]) if keys[0].isdigit() else keys[0]
    ch = course.HOLES[ck]
    h = dict(par=par, length=int(yards), tee=tuple(map(float, fr.tee_px)),
             dot270=tuple(map(float, fr.point_px(270))), green=tuple(map(float, fr.ll_to_px([green_ll])[0])),
             zones=zones, zone_src=src, aim_min=ch.get("aim_min", -40), aim_max=ch.get("aim_max", 40),
             tee_set=tee_set, ref=ref, source_key=keys[0], sources=keys, frame=fr.to_json(),
             tee_ll=list(tee_ll), aim_ll=list(aim_ll), green_ll=list(green_ll),
             tee_method=tee.get("method"), measured_yards=tee.get("measured_yards"))
    for k_ in ("irons", "extra_roll"):
        if k_ in ch:
            h[k_] = ch[k_]
    try:
        adj, esrc = elevation_along(ref, tee_ll, fr.px_to_ll([fr.point_px(270)])[0],
                                    pk["green_polygon_ll"], par), "dem:frame_line"
    except Exception as ex:                                      # DEM missing: the package's numbers
        adj, esrc = (tee.get("elevation") or {}).get("adjustments") or {}, f"package:{tee_set} ({ex})"
    if adj.get("clubs"):
        h["elev"] = {c: (v["carry_delta_yds"], v["roll_factor"], v["lateral_kick_yds"])
                     for c, v in adj["clubs"].items()}
        h["elev_info"] = dict(bearing=adj.get("bearing_deg_true"), source=esrc)
    h["coverage"] = landing_coverage(h, covered)
    return h, fr


def landing_coverage(h, covered, alongs=range(190, 341, 10), lats=range(-50, 51, 5)):
    """Share of the landing area (190-340 yds x +/-50) inside the hand-checked footprint(s)."""
    from shapely.geometry import Point
    tee = np.array(h["tee"])
    d = np.array(h["dot270"]) - tee
    ppy = np.linalg.norm(d) / 270
    f = d / np.linalg.norm(d)
    r = np.array([-f[1], f[0]])
    pts = [tee + (a * f + lt * r) * ppy for a in alongs for lt in lats]
    return float(np.mean([covered.contains(Point(*p)) for p in pts]))


def par3_hole(ref, tee_set, pk, yards, course, black_tee_ll):
    p0 = course.PAR3[ref]
    tee_ll = tuple(pk["tees"][tee_set]["tee_ll"])
    flag_ll = tuple(pk["green_ll"])
    fr0 = R.Frame(tee_ll, flag_ll, proj="enu")
    dist = float(np.linalg.norm(fr0.ll_to_yds([flag_ll])[0]))
    ppy = float(np.clip((TEE_PX_Y - 760) / dist, 3.0, 7.0))
    fr = R.Frame(tee_ll, flag_ll, ppy=ppy, tee_px=(460, TEE_PX_Y), proj="enu")
    # the traced green is in (right, along) yds of the screenshot's line (taken from about the Black
    # tee): turn it into the new line's axes on the ground
    old = R.Frame(black_tee_ll, flag_ll, proj="enu")
    G = []
    for lat, dep in p0["green"]:
        en = lat * old.r + dep * old.f
        G.append((float(en @ fr.r), float(en @ fr.f)))
    deps = [d for _, d in G]
    p = copy.deepcopy({k: v for k, v in p0.items() if k not in ("image", "tee", "flag")})
    p.update(tee=tuple(map(float, fr.tee_px)), flag=tuple(map(float, fr.ll_to_px([flag_ll])[0])),
             center=int(yards), center_measured=round(dist, 1), front=round(yards + min(deps)),
             back=round(yards + max(deps)), green=G, tee_set=tee_set, ref=ref, frame=fr.to_json(),
             tee_ll=list(tee_ll), flag_ll=list(flag_ll))
    try:
        adj = elevation_along(ref, tee_ll, flag_ll, pk["green_polygon_ll"], 3)
    except Exception:
        adj = (pk["tees"][tee_set].get("elevation") or {}).get("adjustments") or {}
    if "plays_like_delta_yds" in adj:
        p["plays_like_delta"] = float(adj["plays_like_delta_yds"])
        p["bearing"] = adj.get("bearing_deg_true")
    return p, fr


def render_image(fr, path, img=None):
    from PIL import Image
    if os.path.exists(path) and img is None:
        return path
    out, _ = R.render(fr, img or R.Imagery(NAIP_DIR))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(out[..., :3]).save(path, quality=88, optimize=True)
    return path


def holes_for(tee_set, render=True, force_render=False, out_dir=OUT_DIR, tee_source="package"):
    """-> (HOLES, PAR3, images) for 'Gold' | 'Black' | 'White' | 'Rust'.

    HOLES / PAR3 use the course.HOLES / course.PAR3 dict formats (keys = hole numbers 1-18) with
    'image' = the absolute path of the NAIP render, so tee_strategy and yardage_book take them as
    they are. images = {hole: path}."""
    import course
    tee_set = tee_set.capitalize()
    if tee_set not in SETS:
        raise ValueError(f"tee set {tee_set!r} not in {SETS}")
    pk = package_holes()
    hand = _load(HAND)["holes"]
    yards, par = card(tee_set)
    holes, par3, images = {}, {}, {}
    img = R.Imagery(NAIP_DIR) if (render and force_render) else None
    for ref in range(1, 19):
        p = pk[ref]
        path = os.path.join(out_dir, tee_set, f"hole{ref:02d}.jpg")
        if ref in course.PAR3:
            d, fr = par3_hole(ref, tee_set, p, yards[ref], course, p["tees"]["Black"]["tee_ll"])
            par3[ref] = d
        else:
            d, fr = tee_hole(ref, tee_set, p, hand, yards[ref], par[ref], course, tee_source)
            holes[ref] = d
        d["image"] = path
        images[ref] = path
        if render:
            if force_render or not os.path.exists(path):
                img = img or R.Imagery(NAIP_DIR)
                render_image(fr, path, img)
    return holes, par3, images


# --------------------------------------------------------------------------- checks
def _picks(t, holes, refs, z):
    out = {}
    saved = t.HOLES
    try:
        t.HOLES = holes
        for ref in refs:
            res = {c: t.best_aim(ref, c, z=z) for c in t.clubs_for(ref)}
            pick = min(res, key=lambda c: res[c]["ev"])
            evs = sorted(r["ev"] for r in res.values())
            out[ref] = dict(pick=pick, aim=float(res[pick]["aim"]), margin=float(evs[1] - evs[0]),
                            ev={c: float(r["ev"]) for c, r in res.items()},
                            aims={c: float(r["aim"]) for c, r in res.items()})
    finally:
        t.HOLES = saved
    return out


def compare_black(n=3000):
    """Black tee: best_aim picks (same swings, the default tee_strategy model) for
      screen    course.HOLES in the screenshot frames (the reference geometry),
      app_geo   the hand zones via WGS84 in a NAIP frame from the app's own tee and line (tests
                the coordinate conversion alone),
      package   holes_for("Black") as shipped (package tee box, line to the 250-yd point),
    and the published pick in spirit_hollow/output/final_decision.json (Bayesian prior over
    dispersion, so ties can flip against any single-model run)."""
    import course
    import tee_strategy as t
    fd = _load(os.path.join(HERE, "output", "final_decision.json"))
    rng = np.random.default_rng(2027)
    z = np.vstack([rng.standard_normal((2, n)), rng.random((2, n))])
    pkg, _, _ = holes_for("Black", render=False)
    app, _, _ = holes_for("Black", render=False, tee_source="app")
    keys = {ref: h["source_key"] for ref, h in pkg.items()}
    keys[2], keys[9] = "2F", "9F"
    scr = {ref: course.HOLES[int(k) if k.isdigit() else k] for ref, k in keys.items()}
    P = dict(screen=_picks(t, scr, list(scr), z), app_geo=_picks(t, app, list(app), z),
             package=_picks(t, pkg, list(pkg), z))
    rows = []
    for ref in pkg:
        f = fd.get(keys[ref], {})
        rows.append(dict(ref=ref, key=keys[ref], final=f.get("pick"), final_aim=f.get("aim"),
                         final_tie=f.get("tie"), coverage=pkg[ref]["coverage"],
                         **{v: P[v][ref] for v in P}))
    return rows


def qa_overlays(tee_set, out_dir=os.path.join(HERE, "qa_geo", "tee_sets")):
    """Zones drawn on each NAIP render (half size): spirit_hollow/qa_geo/tee_sets/<set>_holeNN.jpg."""
    from PIL import Image, ImageDraw
    import geo_zones as GZ
    holes, par3, images = holes_for(tee_set)
    os.makedirs(out_dir, exist_ok=True)
    for k, path in images.items():
        rgb = np.asarray(Image.open(path).convert("RGB"))
        if k in holes:
            h = holes[k]
            im = Image.fromarray(GZ.draw_zones(rgb, h["zones"]))
            d = ImageDraw.Draw(im)
            for p_, col in ((h["tee"], (255, 0, 0)), (h["dot270"], (255, 255, 255)), (h["green"], (255, 255, 0))):
                d.ellipse([p_[0] - 10, p_[1] - 10, p_[0] + 10, p_[1] + 10], outline=col, width=4)
            d.line([tuple(h["tee"]), tuple(h["dot270"])], fill=(255, 255, 255), width=2)
            lab = f"{tee_set} {k}: {h['length']} yds, hand map {h['source_key']}, landing coverage {h['coverage']:.0%}"
        else:
            p = holes_p = par3[k]
            fr = R.Frame.from_json(p["frame"])
            ppy = fr.ppy
            flag = np.array(p["flag"])
            g = [tuple(flag + np.array([lat, -dep]) * ppy) for lat, dep in holes_p["green"]]
            im = Image.fromarray(rgb)
            d = ImageDraw.Draw(im)
            d.line(g + [g[0]], fill=(255, 255, 255), width=3)
            d.ellipse([p["tee"][0] - 10, p["tee"][1] - 10, p["tee"][0] + 10, p["tee"][1] + 10], outline=(255, 0, 0),
                      width=4)
            lab = f"{tee_set} {k}: par 3, card {p['center']} (ground {p['center_measured']}), haz {p['haz']}"
        d.rectangle([0, 0, 920, 40], fill=(0, 0, 0))
        d.text((10, 14), lab, fill=(255, 255, 255))
        im.resize((460, 1000), Image.LANCZOS).save(os.path.join(out_dir, f"{tee_set}_hole{k:02d}.jpg"),
                                                    quality=85)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default=",".join(SETS))
    ap.add_argument("--force", action="store_true", help="re-render the images")
    ap.add_argument("--check", action="store_true", help="Black best_aim vs final_decision.json")
    ap.add_argument("--qa", action="store_true", help="zone overlays in spirit_hollow/qa_geo/tee_sets/")
    a = ap.parse_args()
    summary = {}
    for s in a.sets.split(","):
        holes, par3, images = holes_for(s, force_render=a.force)
        summary[s] = {str(k): dict(length=h["length"], measured=h["measured_yards"], source=h["source_key"],
                                   coverage=round(h["coverage"], 2),
                                   n_package_zones=sum(1 for x in h["zone_src"] if x == "package"))
                      for k, h in holes.items()}
        summary[s].update({str(k): dict(center=p["center"], measured=p["center_measured"])
                           for k, p in par3.items()})
        print(s, json.dumps(summary[s]), flush=True)
        if a.qa:
            qa_overlays(s)
    with open(os.path.join(OUT_DIR, "index.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    if a.check:
        rows = compare_black()
        n = {v: 0 for v in ("screen", "app_geo", "package")}
        sc = {v: 0 for v in ("app_geo", "package")}
        for r in rows:
            cells = []
            for v in ("screen", "app_geo", "package"):
                n[v] += r[v]["pick"] == r["final"]
                if v != "screen":
                    sc[v] += r[v]["pick"] == r["screen"]["pick"]
                cells.append(f"{v} {r[v]['pick']:<9} {r[v]['aim']:+5.1f} ({r[v]['margin']:.3f})")
            print(f"{r['ref']:>2} {r['key']:>3} | final {r['final']:<9} {r['final_aim']:+5.1f}"
                  f"{' tie' if r['final_tie'] else '    '} | " + " | ".join(cells), flush=True)
        print("agree with final_decision:", n, " agree with screen-frame run:", sc)
        with open(os.path.join(OUT_DIR, "black_check.json"), "w") as fh:
            json.dump(rows, fh, indent=1, default=float)


if __name__ == "__main__":
    main()
