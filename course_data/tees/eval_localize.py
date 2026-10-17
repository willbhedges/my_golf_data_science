"""Tee-set localizer v2 (tees/localize.py) before / after, offline.

    python3 course_data/tees/eval_localize.py              # -> eval_localize.json + eval_localize.md
    python3 course_data/tees/eval_localize.py --split test # also score the held-out generalize test split (once)

before = the as-built S2 (tees/place_tee.place_course_sets: OSM boxes, + lidar pads where a set has no box;
         for Spirit Hollow the committed package's tee, which is that method).
after  = tees/localize.py on the same holes with every candidate source available offline.

A. Spirit Hollow vs the hand map (the scoreboard's tee truth): the 18Birdies screenshot tee
   (course_data/spirit_hollow/hand_zones_ll.json tee_ll) moved up its tee -> 270-dot line by
   spirit_hollow/course.BLACK_TEE_FORWARD (the real Black box); 2B / 9B are Gold. Error = distance to the placed
   tee of that set, split into along (+ = placed tee nearer the green) / across that line.
B. Mozingo Lake (App set = the GPS app's yardages): no georeferenced tee, so the check is the measured length of
   the placed tee vs the app's length (|measured - card|) and how often the tee is on a pad.
C. OSM tees hidden (the any-course case: most courses have hole lines but no or few golf=tee polygons): the truth
   proxy is the OSM box a set lands on with all OSM boxes present (before-method, box error <= 3 yds, a box no
   other set shares); before/after then run without any OSM tee. Courses: the five package courses
   (Spirit Hollow, Mozingo, Veenker, Coldwater, Wakonda) and the generalize *train* split
   (course_data/generalize/validation_set.json; the test split is never used to choose anything and is only
   scored with --split test).
Uncertainty calibration: share of truth errors within 1 / 2 sigma_yd.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path[:0] = [HERE]
import eval_tees as E  # noqa: E402
import lidar_pads as lp  # noqa: E402
import localize as LZ  # noqa: E402
import place_tee as pt  # noqa: E402

CACHE = os.path.join(HERE, "cache")
PKG_COURSES = {
    "spirit_hollow": dict(osm="course_data/packages/spirit_hollow/raw/osm.geojson",
                          img="course_data/imagery/spirit_hollow", seg="course_data/segment/spirit_hollow/segment.geojson"),
    "mozingo_lake": dict(osm="course_data/packages/mozingo_lake/raw/osm.geojson",
                         img="course_data/packages/mozingo_lake/imagery", seg="course_data/segment/mozingo_lake/segment.geojson"),
    "veenker": dict(osm="course_data/packages/veenker/raw/osm.geojson",
                    img="course_data/packages/veenker/imagery", seg="course_data/segment/veenker/segment.geojson"),
    "coldwater": dict(osm="course_data/packages/coldwater/raw/osm.geojson", img="course_data/packages/coldwater/imagery"),
    "wakonda": dict(osm="course_data/packages/wakonda/raw/osm.geojson", img="course_data/packages/wakonda/imagery"),
}


def P(*a):
    return os.path.join(ROOT, *a)


def q(xs, f):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * f
    lo, hi = math.floor(k), math.ceil(k)
    return round(xs[lo] + (xs[hi] - xs[lo]) * (k - lo), 1)


def stats(errs, sig=None):
    e = [x for x in errs if x is not None]
    out = dict(n=len(e), median=q(e, 0.5), p90=q(e, 0.9), within10=sum(x <= 10 for x in e))
    if sig:
        pairs = [(x, s) for x, s in zip(errs, sig) if x is not None and s]
        if pairs:
            out.update(cal1=round(sum(x <= s for x, s in pairs) / len(pairs), 2),
                       cal2=round(sum(x <= 2 * s for x, s in pairs) / len(pairs), 2))
    return out


# ----------------------------------------------------------------------------- course inputs
def pkg_inputs(slug):
    c = PKG_COURSES[slug]
    lines, tees, greens = E.load_osm(P(c["osm"]))
    pk = json.load(open(P("course_data/packages", slug, "package.json")))
    if slug == "spirit_hollow":
        yards = E.cards(slug)
    else:
        yards = {k: {n: y for n, y in (h.get("yards") or {}).items() if y} for k, h in pk["holes"].items()}
    yards = {r: v for r, v in yards.items() if r in lines}
    dem = P(c["img"], "dem.tif")
    pads = cached(f"lidar_{slug}", lambda: lp.detect_pads(dem, greens=greens, lines=lines)) if os.path.exists(dem) else []
    tex = cached(f"texture_{slug}", lambda: LZ.texture_pads(dem, P(c["img"], "naip_nir.tif"), P(c["img"], "naip_rgb.tif"),
                                                          greens=greens, lines=lines)) if os.path.exists(dem) else []
    seg = P(c["seg"]) if c.get("seg") and os.path.exists(P(c["seg"])) else None
    return dict(slug=slug, lines=lines, tees=tees, greens=greens, yards=yards, pads=pads, texture=tex, segment=seg, package=pk)


def cached(name, fn):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, name + ".json")
    if os.path.exists(f):
        return [dict(p, coords=[tuple(c) for c in p["coords"]]) for p in json.load(open(f))]
    r = fn()
    json.dump(r, open(f, "w"))
    return r


def gen_inputs(slug):
    d = P("course_data/generalize/courses", slug)
    fc = json.load(open(os.path.join(d, "osm_golf.geojson")))
    lines, tees, greens = {}, [], []
    dup = set()
    for f in fc["features"]:
        p, g = f["properties"], f["geometry"]
        if p.get("golf") == "hole" and g["type"] == "LineString" and p.get("ref"):
            r = str(p["ref"])
            if r in lines:
                dup.add(r)
            lines[r] = [(c[1], c[0]) for c in g["coordinates"]]
        elif p.get("golf") == "tee" and g["type"] in ("Polygon", "Point"):
            cs = g["coordinates"][0] if g["type"] == "Polygon" else [g["coordinates"]]
            tees.append(dict(id=p.get("osm_id"), coords=[(c[1], c[0]) for c in cs], tags=p))
        elif p.get("golf") == "green" and g["type"] == "Polygon":
            greens.append(dict(id=p.get("osm_id"), coords=[(c[1], c[0]) for c in g["coordinates"][0]]))
    for r in dup:
        lines.pop(r, None)
    sc = json.load(open(os.path.join(d, "scorecard.json"))) if os.path.exists(os.path.join(d, "scorecard.json")) else {}
    cards = sc.get("cards") or []
    card = next((c["card"] for c in cards if c.get("source") == sc.get("chosen")), None) or (cards[0]["card"] if cards else None)
    yards = {}
    if card:
        seen = set()
        for n, s in (card.get("tee_sets") or {}).items():
            ys = s.get("yards") or []
            if "(L)" in n or "/" in n or "combo" in n.lower() or len(ys) < 9 or tuple(ys) in seen:
                continue
            seen.add(tuple(ys))
            for i, y in enumerate(ys):
                if y and str(i + 1) in lines:
                    yards.setdefault(str(i + 1), {})[n] = float(y)
    pads = []
    if os.path.exists(os.path.join(d, "pads.json")):
        pads = [dict(p, coords=[tuple(c) for c in p["coords"]], source="lidar") for p in json.load(open(os.path.join(d, "pads.json")))]
    seg = os.path.join(d, "segment.geojson") if os.path.exists(os.path.join(d, "segment.geojson")) else None
    return dict(slug=slug, lines=lines, tees=tees, greens=greens, yards=yards, pads=pads, texture=[], segment=seg)


# ----------------------------------------------------------------------------- methods
def before(inp, hide_osm=False):
    tees = [] if hide_osm else inp["tees"]
    return pt.place_course_sets(inp["lines"], tees, inp["yards"], greens=inp["greens"], pads=inp["pads"])


def after(inp, hide_osm=False, use=("osm", "segment", "lidar", "texture"), params=None):
    use = tuple(u for u in use if not (hide_osm and u == "osm"))
    cands = LZ.gather(osm_tees=inp["tees"], segment=inp["segment"], pads=inp["pads"], texture=inp["texture"], use=use)
    return LZ.localize_course(inp["lines"], inp["greens"], inp["yards"], cands, params)


# ----------------------------------------------------------------------------- A: Spirit Hollow truth
def sh_truth():
    sys.path.insert(0, P("spirit_hollow"))
    import course                                                     # noqa: E402  (read only)
    hz = json.load(open(P("course_data/spirit_hollow/hand_zones_ll.json")))["holes"]
    shots = {k: v["set"] for k, v in json.load(open(P("course_data/spirit_hollow/screenshot_tee_sets.json")))["holes"].items()}
    fwd = {str(k): float(v) for k, v in course.BLACK_TEE_FORWARD.items()}
    out = {}
    for k, h in hz.items():
        st = "Black" if k in fwd else shots.get(k, "Black")
        T, D = h["tee_ll"], h["dot270_ll"]
        fr = pt.Frame(T[1], T[0])
        d = fr.fwd(D[1], D[0])
        n = math.hypot(*d)
        u = (d[0] / n, d[1] / n)
        m = fwd.get(k, 0.0)
        lat, lon = fr.inv(u[0] * m, u[1] * m)
        out[k] = dict(set=st, ref=k.rstrip("BF"), lat=lat, lon=lon, u=u)
    return out


def sh_errors(truth, placed_ll):
    """placed_ll {key: (lat, lon) or None} -> rows with err / along / lateral."""
    rows = []
    for k, t in truth.items():
        p = placed_ll.get(k)
        if p is None:
            continue
        fr = pt.Frame(t["lat"], t["lon"])
        x, y = fr.fwd(p[0], p[1])
        along = x * t["u"][0] + y * t["u"][1]
        lat = x * t["u"][1] - y * t["u"][0]
        rows.append(dict(key=k, set=t["set"], err=round(math.hypot(x, y), 1), along=round(along, 1), lateral=round(lat, 1),
                         sigma=p[2] if len(p) > 2 else None, tee_id=p[3] if len(p) > 3 else None))
    return rows


def run_sh(inp):
    truth = sh_truth()
    pk = inp["package"]
    base = {k: (pk["holes"][t["ref"]]["tees"][t["set"]]["tee_ll"][1], pk["holes"][t["ref"]]["tees"][t["set"]]["tee_ll"][0])
            for k, t in truth.items()}
    out = dict(before=sh_errors(truth, base))
    res = {}
    for lab, use in (("after", ("osm", "segment", "lidar", "texture")), ("after_osm_lidar", ("osm", "lidar"))):
        placed = after(inp, use=use)
        res[lab] = placed
        out[lab] = sh_errors(truth, {k: (placed[t["ref"]]["tees"][t["set"]]["lat"], placed[t["ref"]]["tees"][t["set"]]["lon"],
                                         placed[t["ref"]]["tees"][t["set"]]["sigma_yd"], placed[t["ref"]]["tees"][t["set"]]["tee_id"])
                                     for k, t in truth.items()})
    # is the truth point on a pad at all? (distance to the nearest OSM box ring; 0 inside)
    for k, t in truth.items():
        fr = pt.Frame(t["lat"], t["lon"])
        best = None
        for tb in inp["tees"]:
            ring = [fr.fwd(*c) for c in tb["coords"]]
            if len(ring) >= 3 and pt._point_in_ring((0.0, 0.0), ring):
                best = 0.0
                break
            d = min(math.hypot(*c) for c in ring)
            best = d if best is None else min(best, d)
        t["off_pad_yd"] = round(best, 1)
    out["truth_off_pad"] = {k: t["off_pad_yd"] for k, t in truth.items()}
    out["summary"] = {m: dict(stats([r["err"] for r in rows], [r.get("sigma") for r in rows]),
                              median_abs_along=q([abs(r["along"]) for r in rows], 0.5),
                              median_abs_lateral=q([abs(r["lateral"]) for r in rows], 0.5))
                      for m, rows in out.items() if m not in ("summary", "truth_off_pad")}
    return out, res


# ----------------------------------------------------------------------------- B / C
def length_check(inp, placed, sets=None):
    errs, pads = [], 0
    for ref, hp in placed.items():
        g = pt.green_for_line(inp["lines"][ref], inp["greens"])
        for s, r in hp["tees"].items():
            if sets and s not in sets:
                continue
            L = E.measure(inp["lines"][ref], g, r["lat"], r["lon"])
            errs.append(abs(L - inp["yards"][ref][s]))
            pads += r["method"] != "walkback"
    return dict(stats(errs), on_pad=pads)


def proxy_truth(inp):
    """{(ref, set): (lat, lon)} from the before-method with every OSM box: unshared boxes, box error <= 3."""
    full = pt.place_course_sets(inp["lines"], inp["tees"], inp["yards"], greens=inp["greens"])
    out = {}
    for ref, hp in full.items():
        for s, r in hp["tees"].items():
            if r["method"] in ("tee_axis", "tee_centroid") and (r["error_yd"] or 0) <= 3 and not r.get("shared_with") \
                    and not r.get("borrowed"):
                out[(ref, s)] = (r["lat"], r["lon"])
    return out


def hidden_eval(inp, params=None):
    tr = proxy_truth(inp)
    if not tr:
        return None
    res = {}
    for lab, placed in (("before", before(inp, hide_osm=True)), ("after", after(inp, hide_osm=True, params=params))):
        errs, sig = [], []
        for (ref, s), t in tr.items():
            r = placed.get(ref, {}).get("tees", {}).get(s)
            if r is None:
                continue
            errs.append(pt.haversine_yd(t, (r["lat"], r["lon"])))
            sig.append(r.get("sigma_yd"))
        res[lab] = dict(errs=[round(e, 1) for e in errs], sig=sig if lab == "after" else None)
    return res


def gen_courses(split):
    V = json.load(open(P("course_data/generalize/validation_set.json")))
    cs = V["courses"]
    cs = cs if isinstance(cs, list) else [dict(slug=k, **v) for k, v in cs.items()]
    return [c["slug"] for c in cs if c["split"] == split and os.path.isdir(P("course_data/generalize/courses", c["slug"]))]


def run(splits=("train",), params=None, verbose=True):
    t0 = time.time()
    R = {}
    sh = pkg_inputs("spirit_hollow")
    R["spirit_hollow_truth"], sh_res = run_sh(sh)
    mz = pkg_inputs("mozingo_lake")
    R["mozingo_length"] = dict(before=length_check(mz, before(mz)), after=length_check(mz, after(mz)))
    hid = {}
    for slug in PKG_COURSES:
        inp = sh if slug == "spirit_hollow" else mz if slug == "mozingo_lake" else pkg_inputs(slug)
        h = hidden_eval(inp, params)
        if h:
            hid[slug] = h
    R["hidden_packages"] = summarise(hid)
    for split in splits:
        hg = {}
        for slug in gen_courses(split):
            inp = gen_inputs(slug)
            if not inp["yards"] or not inp["tees"]:
                continue
            h = hidden_eval(inp, params)
            if h:
                hg[slug] = h
            if verbose:
                print(f"  {split} {slug}: {len((h or {}).get('before', {}).get('errs', []))} placements", flush=True)
        R[f"hidden_generalize_{split}"] = summarise(hg)
    R["seconds"] = round(time.time() - t0, 1)
    return R, sh_res


def summarise(hid):
    out = dict(courses={}, all={})
    pooled = {"before": [], "after": [], "sig": []}
    for slug, h in hid.items():
        out["courses"][slug] = {m: stats(v["errs"], v.get("sig")) for m, v in h.items()}
        pooled["before"] += h["before"]["errs"]
        pooled["after"] += h["after"]["errs"]
        pooled["sig"] += h["after"]["sig"]
    out["all"] = dict(before=stats(pooled["before"]), after=stats(pooled["after"], pooled["sig"]))
    return out


# ----------------------------------------------------------------------------- report
def md(R):
    L = ["# Tee-set localizer v2: before / after", "",
         "Generated by `course_data/tees/eval_localize.py` (offline). *before* = the as-built S2 "
         "(`place_tee.place_course_sets`, OSM boxes + lidar pads where a set has no box); *after* = `tees/localize.py` "
         "(merged OSM / segment-model / lidar / DEM+NAIP texture pads, joint chain assignment, sum-product "
         "uncertainty sigma_yd). Weights chosen on the generalize train split only. Errors in yards.", ""]
    S = R["spirit_hollow_truth"]
    L += ["## A. Spirit Hollow vs the hand map (scoreboard tee truth, 16 tee shots)", "",
          "| method | median | p90 | <= 10 yds | median abs along | median abs across | within 1 / 2 sigma |", "|---|---|---|---|---|---|---|"]
    for m, s in S["summary"].items():
        L.append(f"| {m} | {s['median']} | {s['p90']} | {s['within10']}/{s['n']} | {s['median_abs_along']} | "
                 f"{s['median_abs_lateral']} | {s.get('cal1', '-')} / {s.get('cal2', '-')} |")
    L += ["", "*after_osm_lidar* = the localizer with only the sources the as-built S2 has (OSM + lidar pads). "
          "Along: + = the placed tee is nearer the green than the truth.", "",
          "| key | set | before err (along / across) | after err (along / across) | after sigma | after pad | truth: yds outside the nearest OSM box |",
          "|---|---|---|---|---|---|---|"]
    for a, b in zip(S["before"], S["after"]):
        L.append(f"| {a['key']} | {a['set']} | {a['err']} ({a['along']:+.0f} / {a['lateral']:+.0f}) | "
                 f"{b['err']} ({b['along']:+.0f} / {b['lateral']:+.0f}) | {b['sigma']} | {b['tee_id']} | "
                 f"{S['truth_off_pad'].get(a['key'])} |")
    M = R["mozingo_length"]
    L += ["", "## B. Mozingo Lake (App yardages): |measured length - app length|", "",
          "| method | median | p90 | <= 10 yds | on a pad |", "|---|---|---|---|---|"]
    for m, s in M.items():
        L.append(f"| {m} | {s['median']} | {s['p90']} | {s['within10']}/{s['n']} | {s['on_pad']}/{s['n']} |")
    for key, title in (("hidden_packages", "C1. OSM tees hidden, package courses"),
                       ("hidden_generalize_train", "C2. OSM tees hidden, generalize train split"),
                       ("hidden_generalize_test", "C3. OSM tees hidden, generalize TEST split (held out, report only)")):
        if key not in R:
            continue
        H = R[key]
        L += ["", f"## {title}", "", "Truth proxy: the OSM box each set lands on with all OSM boxes present (unshared, box error <= 3 yds).", "",
              "| course | n | before median / p90 | after median / p90 | before <= 10 | after <= 10 | after within 1 / 2 sigma |",
              "|---|---|---|---|---|---|---|"]
        rows = list(H["courses"].items()) + [("**all**", H["all"])]
        for slug, v in rows:
            b, a = v["before"], v["after"]
            L.append(f"| {slug} | {b['n']} | {b['median']} / {b['p90']} | {a['median']} / {a['p90']} | {b['within10']} | "
                     f"{a['within10']} | {a.get('cal1', '-')} / {a.get('cal2', '-')} |")
    L += ["", "## Notes", "",
          "* course_data/truth/ (Coldwater, Veenker): the hand corridors are framed on the package's own Blue tee "
          "(NOTES.md), so they hold no independent tee truth; both courses are scored in C1 instead.",
          "* Spirit Hollow truth = the 18Birdies tee moved straight up the app's line by BLACK_TEE_FORWARD. On the "
          "five worst keys (1, 2B, 14, 16, 17) the error is across the line (21-29 yds), not along it, and on 1 / 14 / "
          "17 the truth point is 6-16 yds outside every OSM tee box (trees / bank): the real Black box is beside "
          "the app's line, so no pad-based method can get closer there; both methods put Black on the same box.",
          "* sigma_yd is the 1-sigma radial uncertainty (assignment spread + within-pad + source); 'within 1 / 2 "
          "sigma' is the share of truth errors inside it."]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", action="append", default=None)
    a = ap.parse_args()
    splits = ["train"] + [s for s in (a.split or []) if s != "train"]
    R, _ = run(splits)
    json.dump(R, open(os.path.join(HERE, "eval_localize.json"), "w"), indent=1)
    open(os.path.join(HERE, "eval_localize.md"), "w").write(md(R))
    print(md(R))


if __name__ == "__main__":
    main()
