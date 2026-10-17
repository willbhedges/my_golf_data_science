"""How many product picks change with the tee-set localizer v2 (tees/localize.py), and are they closer to the truth?

    python3 course_data/tees/picks_localize.py [--n 8000] [--workers 4]   # -> picks_localize.json + .md (~15 min)

Each variant re-tees the COMMITTED package (packages/<slug>/package.json: zones, vision / OB / segment layers stay
as built) with a tee_positions dict, recomputes each tee's aim (tee_line rule), measured length and elevation
profile, and re-derives the yard frame with platform/package.reframe(); then the product's quick decision
(qa/scoreboard.product_plan: product/package.load -> decide.run quick, n=8000) picks a club per tee shot.

Variants
  asbuilt      the committed tees, through the same re-tee path (a control: must reproduce the scoreboard)
  v2           tees/localize.py, every candidate source (OSM boxes + lidar + DEM/NAIP texture + segment model)
  hidden       OSM golf=tee boxes removed (the any-course case): the as-built S2 (place_course_sets + lidar pads)
  hidden_v2    OSM boxes removed: tees/localize.py with lidar + texture + segment pads
Truth: Spirit Hollow spirit_hollow/output/final_decision.json (scoreboard keys: Black plan, 2B / 9B from Gold);
Mozingo Lake: the hand map through the same quick decision (qa/scoreboard.json truth_cache); Veenker: none.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
import os
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
for p in (HERE, os.path.join(CD, "qa")):
    if p not in sys.path:
        sys.path.insert(0, p)
import eval_localize as EL  # noqa: E402
import localize as LZ  # noqa: E402
import place_tee as pt  # noqa: E402
import scoreboard  # noqa: E402,F401  (puts product/ on sys.path)
import package as _product_package  # noqa: E402,F401  product/package.py owns the name 'package' (platform's is loaded by path)

COURSES = [dict(slug="spirit_hollow", tees="Black", truth="spirit_hollow"),
           dict(slug="mozingo_lake", tees="App", truth="mozingo"),
           dict(slug="veenker", tees="Blue", truth=None)]


def positions_from_package(pkg):
    out = {}
    for k, h in pkg["holes"].items():
        out[k] = dict(tees={s: dict(lat=t["tee_ll"][1], lon=t["tee_ll"][0], method=t.get("method"), source=t.get("tee_source"),
                                    tee_id=t.get("tee_id")) for s, t in h["tees"].items()})
    return out


_PK = None


def platform_package():
    """platform/package.py under its own module name (product/package.py is also called 'package')."""
    global _PK
    if _PK is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("platform_package_lz", os.path.join(CD, "platform", "package.py"))
        _PK = importlib.util.module_from_spec(spec)
        sys.modules["platform_package_lz"] = _PK
        spec.loader.exec_module(_PK)
    return _PK


def retee(pkg, positions, label):
    """Committed package + {ref: {tees: {set: {lat, lon, method, source, tee_id, sigma_yd...}}}} -> reframed package."""
    PK = platform_package()
    p = copy.deepcopy(pkg)
    sample = PK.dem_sampler(os.path.join(ROOT, p["elevation"]["file"])) if p.get("elevation") else None
    moved = 0
    for k, h in p["holes"].items():
        hp = (positions.get(k) or {}).get("tees") or {}
        line = [(c[1], c[0]) for c in h["hole_line_ll"]]
        g = (h["green_ll"][1], h["green_ll"][0])
        for s, t in h["tees"].items():
            r = hp.get(s)
            if not r:
                continue
            old = (t["tee_ll"][1], t["tee_ll"][0])
            t["tee_ll"] = [round(float(r["lon"]), 7), round(float(r["lat"]), 7)]
            if pt.haversine_yd(old, (r["lat"], r["lon"])) > 0.5:
                moved += 1
                t["measured_yards"] = int(round(EL.E.measure(line, g, r["lat"], r["lon"])))
                t["method"] = r.get("method") or t.get("method")
                t["tee_choice"] = f"tee stage: {s} {t['method']} ({label})"
                t["tee_source"] = r.get("source")
                t["tee_id"] = r.get("tee_id")
            if r.get("sigma_yd") is not None:
                t["uncertainty"] = {kk: r.get(kk) for kk in ("sigma_yd", "sigma_along_yd", "sigma_lat_yd", "p_assign")}
        PK.apply_tee_line(h)
        if sample is not None:
            for s, t in h["tees"].items():
                fr = PK._frame(t["tee_ll"], t["aim_ll"])
                gy = fr.ll_to_yds(np.array([h["green_ll"]]))[0]
                hh = dict(ref=k, par=h["par"], length=t["card_yards"] or t["measured_yards"],
                          measured_length=t["measured_yards"], green=[float(gy[0]), float(gy[1])], bearing_deg=t["bearing_deg"])
                try:
                    t["elevation"] = PK.elevation_for_hole(hh, sample, fr.yds_to_ll)
                except Exception:                                  # noqa: BLE001
                    t["elevation"] = None
    with contextlib.redirect_stdout(io.StringIO()):
        out = PK.reframe(p)
    out.setdefault("stages", {})["tees_variant"] = f"{label}: {moved} tee(s) moved vs the committed package"
    return out, moved


def variants(slug):
    inp = EL.pkg_inputs(slug)
    pkg = inp["package"]
    v = {"asbuilt": positions_from_package(pkg)}
    v["v2"] = EL.after(inp)
    v["hidden"] = EL.before(inp, hide_osm=True)
    v["hidden_v2"] = EL.after(inp, hide_osm=True)
    return pkg, v


def plan(path, slug, tees, keys, n, workers):
    import scoreboard as SB
    cfg = dict(slug=slug, package=path, tees=tees)
    with contextlib.redirect_stdout(io.StringIO()):
        res, C, sec = SB.product_plan(cfg, tees, keys=keys, n=n, workers=workers)
    return {k: dict(pick=r["pick"], aim=round(float(r["aim"]), 1), tie=bool(r.get("tie")), runner=r.get("runner"),
                    margin=r.get("margin")) for k, r in res.items()}, sec


def truth_for(c):
    import scoreboard as SB
    if c["truth"] == "spirit_hollow":
        sets = SB.sh_truth_sets()
        return SB.final_truth(), sets
    if c["truth"] == "mozingo":
        tc = json.load(open(os.path.join(CD, "qa", "scoreboard.json")))["truth_cache"]["mozingo"]["res"]
        return tc, None
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8000)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--courses", default=None)
    a = ap.parse_args()
    import scoreboard as SB
    out = {}
    td = tempfile.mkdtemp(prefix="picks_localize_")
    for c in COURSES:
        if a.courses and c["slug"] not in a.courses.split(","):
            continue
        t0 = time.time()
        pkg, V = variants(c["slug"])
        truth, sets = truth_for(c)
        res = {}
        for lab, pos in V.items():
            P, moved = retee(pkg, pos, lab)
            f = os.path.join(td, f"{c['slug']}_{lab}.json")
            json.dump(P, open(f, "w"))
            picks, _ = plan(f, c["slug"], c["tees"], None, a.n, a.workers)
            if sets:                                               # Spirit Hollow: 2B / 9B play the Gold box
                gk = {k.rstrip("BF") for k, s in sets.items() if s != c["tees"]}
                gp, _ = plan(f, c["slug"], "Gold", gk, a.n, a.workers)
                rows = {}
                for key, s in sets.items():
                    ref = key.rstrip("BF")
                    src = gp if s != c["tees"] else picks
                    if ref in src:
                        rows[key] = src[ref]
                picks = rows
            res[lab] = dict(moved=moved, picks=picks)
            print(f"{c['slug']} {lab}: moved {moved}, {time.time() - t0:.0f} s", flush=True)
        base = res["asbuilt"]["picks"]
        summ = {}
        for lab, r in res.items():
            pk = r["picks"]
            changed = sorted(k for k in pk if k in base and pk[k]["pick"] != base[k]["pick"])
            s = dict(moved=r["moved"], changed_vs_asbuilt=changed)
            if truth:
                keys = [k for k in pk if k in truth]
                s["same_club"] = sum(SB.agree(pk[k], truth[k])[0] for k in keys)
                s["same_or_tie"] = sum(SB.agree(pk[k], truth[k])[1] for k in keys)
                s["n"] = len(keys)
            summ[lab] = s
        out[c["slug"]] = dict(summary=summ, picks={lab: r["picks"] for lab, r in res.items()},
                              truth={k: v["pick"] for k, v in (truth or {}).items()})
    json.dump(out, open(os.path.join(HERE, "picks_localize.json"), "w"), indent=1)
    L = ["# Product picks with the tee-set localizer v2", "",
         "Generated by `course_data/tees/picks_localize.py` (product quick decision, n=%d, on the committed packages "
         "re-teed per variant; see the module docstring)." % a.n, "",
         "| course | variant | tees moved | picks changed vs as-built | same club as truth | same or tie |", "|---|---|---|---|---|---|"]
    for slug, v in out.items():
        for lab, s in v["summary"].items():
            L.append(f"| {slug} | {lab} | {s['moved']} | {len(s['changed_vs_asbuilt'])} "
                     f"({', '.join(s['changed_vs_asbuilt']) or '-'}) | {s.get('same_club', '-')}/{s.get('n', '-')} | "
                     f"{s.get('same_or_tie', '-')}/{s.get('n', '-')} |")
    open(os.path.join(HERE, "picks_localize.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
