"""TRAIN-BIG: more routing training courses, simulated unmapped, through the normal fast-path fetch + perception.

    python3 route_big.py pick [--n 320]        seeded draw of fully mapped survey courses -> cache/big/manifest.json
    python3 route_big.py build [--max N]       fetch + perceive the next courses of the manifest (resumable)
    python3 route_big.py list                  status counts

Population: the generalize state surveys (surveys/survey_*.json, 12 states), tier "full" (OSM golf=hole ways),
18 or 9 hole ways, minus every validation-set course (train and test), the blind-loop list (blind20.json, which
holds the TEST-40 b20 courses), the perception stacks_meta pool (TRAIN of the object models) and the U-Net's training
index (heldout.py's leak check), and anything within 1.5 km of one of them (other courses of the same facility).

Per course (cache/big/, the work package deleted after extraction; about 2-3 MB a course):
  courses/<slug>/osm_golf.geojson.gz   raw/osm.geojson of the OSM API fetch (the hidden truth: golf=hole ways)
  courses/<slug>/course.json, scorecard.json  (scorecard_web.json; `chosen` = package.pick_scorecard on the OSM
                                       without golf features, what an unmapped course gets)
  probs/<slug>/d0+yall.npz             fastscene's U-Net probabilities (package year + 2 other NAIP years averaged,
                                       production's default), uint8 [6, H, W]; only green / tee kept
  scenes/<slug>.json.gz                  fastscene.build's scene (the detector never reads OSM golf features)
  maps/<slug>.npz                      route_learn corridor maps (fair / turf / water / bunker / tree)
Simulated unmapped as heldout.py does it: NAIP year "latest", OSM golf features only read by the scorer. The web
card search does see the OSM hole lengths (fetch_package's plausibility check), as the validation set's cards did.
route_bench reads these courses as split "big" (route_bench.courses / course_files / bench_probs / scene_path).
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import math
import os
import random
import shutil
import sys
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(HERE)
CD = os.path.dirname(PLAT)
sys.path[:0] = [HERE, PLAT, os.path.join(CD, "generalize")]
os.environ.setdefault("FASTPATH_TILE_CACHE", "off")        # the shared COG block cache is not grown by this batch
BIG = os.environ.get("ROUTE_BIG_DIR") or os.path.join(os.environ.get("FASTPATH_CACHE") or os.path.join(HERE, "cache"),
                                                        "big")
MANIFEST = os.path.join(BIG, "manifest.json")
SEED = 20261116
MIN_FREE_GB = 1.3
CAP_MB = 800.0
PROBS_NAME = "d0+yall"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def _hav_m(a, b):
    k = math.cos(math.radians((a[1] + b[1]) / 2))
    return math.hypot((a[0] - b[0]) * k, a[1] - b[1]) * 111320.0


def excluded():
    """(osm ids, centres [lon, lat]) of every course that must not be in TRAIN-BIG"""
    ids, cen = set(), []
    vs = json.load(open(os.path.join(CD, "generalize", "validation_set.json")))["courses"]
    for c in vs:
        ids.add(c["osm"])
        p = os.path.join(os.path.dirname(CD), c["dir"], "course.json")
        if os.path.exists(p):
            cc = json.load(open(p))
            if cc.get("center"):
                cen.append(cc["center"])
    for c in json.load(open(os.path.join(PLAT, "blind20", "blind20.json")))["courses"]:
        ids.add(c["osm"])
        cen.append([c["lon"], c["lat"]])
    for p in glob.glob(os.path.join(CD, "perception", "stacks_meta", "*.json")):
        m = json.load(open(p))
        c = m.get("course") or {}
        o = c.get("osm")
        if isinstance(o, dict):
            ids.add(f"{o.get('type')}/{o.get('id')}")
        if c.get("center"):
            cen.append(c["center"])
    import heldout
    ids |= heldout._unet_train_ids()
    return ids, cen


def cmd_pick(n):
    import sample as SM
    import platform_common as pc
    ids, cen = excluded()
    pop = []
    for p in sorted(glob.glob(os.path.join(CD, "generalize", "surveys", "survey_*.json"))):
        for r in json.load(open(p))["courses"]:
            h, g = r["counts"].get("hole", 0), r["counts"].get("green", 0)
            if r["tier"] != "full" or not SM.eligible(r) or r["osm"] in ids or r["osm"].startswith("node/"):
                continue
            if not (h == 18 or (h == 9 and g < 14)) or r["area_ha"] < 15:
                continue
            if any(_hav_m(r["center"], c) < 1500 for c in cen):
                continue
            pop.append(r)
    pop.sort(key=lambda r: r["osm"])
    random.Random(SEED).shuffle(pop)
    used, out = set(), []
    for r in pop[:n]:
        s = "tb_" + SM.slug_for(r, used)
        out.append(dict(slug=s, name=r["name"], state=r["state"], osm=r["osm"], lon=r["center"][0],
                        lat=r["center"][1], osm_holes=r["counts"].get("hole"), area_ha=r["area_ha"]))
    os.makedirs(BIG, exist_ok=True)
    json.dump(dict(schema="route_big/1", seed=SEED, population=len(pop), courses=out), open(MANIFEST, "w"), indent=0)
    log("population", len(pop), "picked", len(out))


# ----------------------------------------------------------------------------- one course
def status_path(slug):
    return os.path.join(BIG, "status", slug + ".json")


def done(slug):
    return os.path.exists(status_path(slug))


def set_status(slug, **kw):
    os.makedirs(os.path.dirname(status_path(slug)), exist_ok=True)
    json.dump(dict(slug=slug, **kw), open(status_path(slug), "w"))


def big_mb():
    t = 0
    for d in ("courses", "probs", "scenes", "maps"):
        for root, _, fs in os.walk(os.path.join(BIG, d)):
            t += sum(os.path.getsize(os.path.join(root, f)) for f in fs)
    return t / 1e6


def free_gb():
    s = os.statvfs(BIG)
    return s.f_bavail * s.f_frsize / 1e9


def fetch_stage(c):
    """OSM + truth check + card search, then (only for usable courses) NAIP latest + 2 other years + DEM + canopy.
    -> dict(ok, why, pkg, card ...)"""
    import osm_api
    import routing as R
    import route_bench as RB
    import fetch_package as fp
    import package as pk
    import platform_common as pc
    slug = c["slug"]
    pkg = os.path.join(BIG, "work", slug)
    raw = os.path.join(pkg, "raw")
    ocache = os.path.join(pkg, "_osm")
    os.makedirs(raw, exist_ok=True)
    T = {}
    t = time.time()
    row = dict(c, city=None)
    course = osm_api.course_from_row(row, ocache)
    if course["status"] != "ok":
        return dict(ok=False, why="course " + str(course.get("closed") or course["status"]))
    pc.write_json(os.path.join(raw, "course.json"), course)
    req = dict(schema="request/1", kind="package", course=c["name"], state=c["state"], slug=slug, tees="Black",
               allow_substitute=True, builder="fastpath", town=None, osm=c["osm"], near=f"{c['lat']:.5f},{c['lon']:.5f}")
    fc, summ = osm_api.features(course, raw, ocache, req)
    T["osm"] = round(time.time() - t, 1)
    truth = {k: v for k, v in R.truth_from_fc(fc).items() if int(k) <= 18}
    refs = sorted(int(k) for k in truth)
    if refs not in (list(range(1, 10)), list(range(1, 19))):
        return dict(ok=False, why=f"truth refs {refs[:3]}..{refs[-3:]} ({len(refs)})", T=T)
    t = time.time()
    f = Future()
    f.set_result(summ)
    try:
        fp.fetch_scorecards(req, course, f, raw, parallel=True)
    except Exception as e:                                           # noqa: BLE001
        return dict(ok=False, why="card search crashed " + repr(e)[:120], T=T)
    T["card"] = round(time.time() - t, 1)
    card, info = pk.pick_scorecard(req, raw, RB.strip_golf(fc))
    if not card or not card.get("tee_sets"):
        return dict(ok=False, why="no card", T=T)
    ny = max(len(s.get("yards") or []) for s in card["tee_sets"].values())
    if ny not in (9, 18) or (ny == 9 and len(refs) == 18 and False):
        return dict(ok=False, why=f"card holes {ny}", T=T)
    if free_gb() < MIN_FREE_GB or big_mb() > CAP_MB:
        return dict(ok=False, why="disk", stop=True, T=T)
    t = time.time()
    import fast_imagery as fim
    fim.fetch(course["bbox"], os.path.join(pkg, "imagery"), None, "latest", label=course.get("name"))
    fim.to_06(os.path.join(pkg, "imagery"))
    T["imagery"] = round(time.time() - t, 1)
    t = time.time()
    try:
        fim.fetch_years(os.path.join(pkg, "imagery"), 2)
    except Exception as e:                                           # noqa: BLE001
        T["years_err"] = repr(e)[:120]
    T["years"] = round(time.time() - t, 1)
    t = time.time()
    import canopy
    canopy.fetch(course["bbox"], os.path.join(pkg, "canopy"))
    T["canopy"] = round(time.time() - t, 1)
    web = json.load(open(os.path.join(raw, "scorecard_web.json")))
    return dict(ok=True, pkg=pkg, course=course, card=card, info=info, web=web, T=T, n_truth=len(refs))


def perceive_stage(c, F):
    """fastscene.build on the work package (U-Net on 3 NAIP years) -> the files routing needs; the package is deleted"""
    import fastscene as FS
    import route_learn as RL
    slug, pkg = c["slug"], F["pkg"]
    t = time.time()
    sc, info = FS.build(pkg, out=False)
    T = dict(F["T"], scene=round(time.time() - t, 1), fastscene=sc.get("fastscene", {}).get("seconds"))
    P = info["P"]
    Pu = np.clip(np.round(P * 255), 0, 255).astype(np.uint8)
    cdir = os.path.join(BIG, "courses", slug)
    os.makedirs(cdir, exist_ok=True)
    with open(os.path.join(pkg, "raw", "osm.geojson"), "rb") as fi, gzip.open(os.path.join(cdir, "osm_golf.geojson.gz"),
                                                                              "wb") as fo:
        shutil.copyfileobj(fi, fo)
    json.dump(F["course"], open(os.path.join(cdir, "course.json"), "w"))
    web = F["web"]
    chosen = (F["info"] or {}).get("source") or (F["info"] or {}).get("url")
    srcs = [x.get("source") for x in web.get("cards", [])]
    if chosen not in srcs:
        web["cards"] = [dict(source="picked", card=F["card"])] + list(web.get("cards", []))
        chosen = "picked"
    web["chosen"] = chosen
    json.dump(web, open(os.path.join(cdir, "scorecard.json"), "w"))
    os.makedirs(os.path.join(BIG, "probs", slug), exist_ok=True)
    Pz = Pu.copy()                    # routing reads P(green) / P(tee) from here, the other classes from maps/
    Pz[[0, 3, 4, 5]] = 0
    np.savez_compressed(os.path.join(BIG, "probs", slug, PROBS_NAME + ".npz"), p=Pz)
    sc["route_bench"] = dict(version="big", probs=PROBS_NAME, years=T.get("fastscene", {}).get("unet_years"))
    os.makedirs(os.path.join(BIG, "scenes"), exist_ok=True)
    with gzip.open(os.path.join(BIG, "scenes", slug + ".json.gz"), "wt") as fh:
        json.dump(sc, fh, separators=(",", ":"))
    cp = os.path.join(pkg, "canopy", "chm_meta.tif")
    chm = RL.warp_chm(cp, sc["grid"]) if os.path.exists(cp) else None
    m = RL.corridor_maps(Pu, sc["grid"], chm=chm)
    os.makedirs(os.path.join(BIG, "maps"), exist_ok=True)
    np.savez_compressed(os.path.join(BIG, "maps", slug + ".npz"), fair=m.fair, turf=m.turf, water=m.water,
                        bunker=m.bunker, tree=m.tree)
    return T


def cleanup(slug):
    shutil.rmtree(os.path.join(BIG, "work", slug), ignore_errors=True)


def cmd_build(mx, workers=4):
    cs = [c for c in json.load(open(MANIFEST))["courses"] if not done(c["slug"])]
    if mx:
        cs = cs[:mx]
    log("to do", len(cs), "free GB", round(free_gb(), 2), "big MB", round(big_mb(), 1))
    stop = threading.Event()
    sem = threading.Semaphore(3)              # at most 3 fetched packages waiting for the U-Net (disk)

    def fetch(c):
        sem.acquire()
        if stop.is_set():
            return c, dict(ok=False, why="stopped", stop=True)
        try:
            return c, fetch_stage(c)
        except Exception as e:                                       # noqa: BLE001
            import traceback
            return c, dict(ok=False, why="fetch crashed " + repr(e)[:200], tb=traceback.format_exc()[-600:])
    kept = 0
    with ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(fetch, c) for c in cs]
        for fu in futs:
            c, F = fu.result()
            try:
                if F.get("stop"):
                    stop.set()
                    log(c["slug"], "STOP", F.get("why"), "free GB", round(free_gb(), 2), "big MB", round(big_mb(), 1))
                    continue
                if not F["ok"]:
                    set_status(c["slug"], ok=False, why=F["why"], T=F.get("T"))
                    log(c["slug"], "skip", F["why"], F.get("T"))
                    continue
                try:
                    T = perceive_stage(c, F)
                    set_status(c["slug"], ok=True, T=T, n=F["n_truth"])
                    kept += 1
                    log(c["slug"], "ok", kept, T, "free GB", round(free_gb(), 2), "big MB", round(big_mb(), 1))
                except Exception as e:                               # noqa: BLE001
                    import traceback
                    set_status(c["slug"], ok=False, why="perceive crashed " + repr(e)[:200],
                               tb=traceback.format_exc()[-600:])
                    log(c["slug"], "perceive FAIL", repr(e)[:200])
            finally:
                cleanup(c["slug"])
                sem.release()
    log("kept", kept)


def kept_courses():
    """manifest rows of the courses built ok (route_bench split 'big')"""
    if not os.path.exists(MANIFEST):
        return []
    out = []
    for c in json.load(open(MANIFEST))["courses"]:
        p = status_path(c["slug"])
        if os.path.exists(p) and json.load(open(p)).get("ok"):
            out.append(dict(slug=c["slug"], name=c["name"], state=c["state"], osm=c["osm"], split="big", card=True,
                            status="ok", big=True))
    return out


def cmd_list():
    cs = json.load(open(MANIFEST))["courses"]
    from collections import Counter
    st = Counter()
    for c in cs:
        p = status_path(c["slug"])
        if not os.path.exists(p):
            st["todo"] += 1
            continue
        s = json.load(open(p))
        st["ok" if s.get("ok") else s.get("why", "?").split(" ")[0] + " " + " ".join(s.get("why", "").split(" ")[1:2])] += 1
    print(dict(st), "big MB", round(big_mb(), 1), "free GB", round(free_gb(), 2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["pick", "build", "list"])
    ap.add_argument("--n", type=int, default=320)
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.cmd == "pick":
        cmd_pick(a.n)
    elif a.cmd == "build":
        cmd_build(a.max, a.workers)
    else:
        cmd_list()
