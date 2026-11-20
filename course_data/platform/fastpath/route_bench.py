"""Routing bench for unmapped courses: the validation set simulated as unmapped (every OSM golf feature hidden), routed
on a detected scene + the web card, scored against the hidden OSM hole ways, and the show / block gate measured.

  python3 route_bench.py scenes --split test [--limit N]     fetch NAIP / DEM / canopy for the validation courses
                                                             and build the fastscene scene (cached per detector version)
  python3 route_bench.py eval --scene fast|oracle|perc --split train|test [--router v0|v1] [--out f.json]
  python3 route_bench.py gate --split train ...              precision / coverage curve of the gate

Scenes:
  fast    fastscene.build on the course's NAIP + 3DEP DEM + Meta canopy, OSM golf features hidden from it (its
          negative mask reads only non-golf OSM). Cached at cache/val/scenes/<detector version>/<slug>.json, the
          imagery at cache/val/<slug>/ (shared with the detection side: NOTES_ROUTING.md).
  oracle  the OSM truth objects as detections with realistic noise (seeded): 15 % of hole greens and 30 % of tee
          complexes dropped, false greens / tees added, polygons jittered. Separates routing from detection errors.
  perc    the slow pipeline's perception scene (zero_tap bench files), for reference.

Scoring: routing.score (green within 20 yd of the true line's end, tee within 40 yd of its first 60 %, same number),
the validation-set convention of PIPELINE.md. Card: the web card only (courses without one are reported apart).
Tune on train only; test is read for reporting.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(HERE)
CD = os.path.dirname(PLAT)
ROOT = os.path.dirname(CD)
GEN = os.path.join(CD, "generalize")
VAL = os.path.join(os.environ.get("FASTPATH_CACHE") or os.path.join(HERE, "cache"), "val")
sys.path[:0] = [HERE, PLAT]


def log(*a):
    print(*a, flush=True)


# ----------------------------------------------------------------------------- courses
def courses(split=None):
    """validation-set rows of a split (train / test / all); 'big' = TRAIN-BIG (route_big.py), 'train+big' both"""
    v = json.load(open(os.path.join(GEN, "validation_set.json")))["courses"]
    if split and "big" in split.split("+"):
        import route_big
        v = v + route_big.kept_courses()
    sp = set((split or "all").split("+"))
    return [c for c in v if "all" in sp or c["split"] in sp]


def is_big(slug):
    return slug.startswith("tb_")


def big_dir(*p):
    import route_big
    return os.path.join(route_big.BIG, *p)


def rd(p):
    import gzip
    if not os.path.exists(p):
        return None
    with (gzip.open if p.endswith(".gz") else open)(p, "rt") as fh:
        return json.load(fh)


def course_files(slug):
    if is_big(slug):
        d = big_dir("courses", slug)
        return rd(os.path.join(d, "osm_golf.geojson.gz")), rd(os.path.join(d, "course.json")) or {}, \
            rd(os.path.join(d, "scorecard.json"))
    d = os.path.join(GEN, "courses", slug)
    return rd(os.path.join(d, "osm_golf.geojson")), rd(os.path.join(d, "course.json")) or {}, \
        rd(os.path.join(d, "scorecard.json"))


def strip_golf(fc):
    return dict(fc, features=[f for f in fc.get("features", []) if not (f.get("properties") or {}).get("golf")])


# ----------------------------------------------------------------------------- detector version + scene cache
DET_PATHS = ["course_data/platform/fastpath/fastscene.py", "course_data/platform/fastpath/fastscene_model",
             "course_data/platform/fastc/perception", "course_data/perception", "course_data/segment/models"]


def detector_version():
    """The last commit touching the detector's files (+ '-dirty' and a hash of the diff when they have local edits)."""
    h = subprocess.run(["git", "log", "-1", "--format=%h", "--"] + DET_PATHS, cwd=ROOT, capture_output=True,
                       text=True).stdout.strip() or "nogit"
    diff = subprocess.run(["git", "diff", "HEAD", "--"] + DET_PATHS, cwd=ROOT, capture_output=True, text=True).stdout
    if diff:
        h += "-dirty" + hashlib.sha1(diff.encode()).hexdigest()[:6]
    return h


HELDOUT = os.path.join(os.environ.get("FASTPATH_CACHE") or os.path.join(HERE, "cache"), "heldout")
PROBS = os.environ.get("ROUTE_BENCH_PROBS", "d0")      # the detection side's cached U-Net probabilities (perc_bench.py)


def bench_probs(slug, combo=None):
    """the cached U-Net probabilities of a course as uint8 [6, H, W]: one variant ('d0'), or the mean of several
    ('d0+yall': d0 and every cached extra NAIP year y<year>.npz, as perc_bench.load_combo; a course without extra
    years gives d0). None when missing."""
    combo = combo or PROBS
    if is_big(slug):                 # TRAIN-BIG: production's multi-year probabilities, one file
        q = big_dir("probs", slug, "d0+yall.npz")
        return np.load(q)["p"] if os.path.exists(q) else None
    d = os.path.join(HELDOUT, "probs", slug)
    vs = combo.split("+")
    if "yall" in vs:
        ys = sorted(f[:-4] for f in os.listdir(d) if f.startswith("y") and "_" not in f) if os.path.isdir(d) else []
        vs = [v for v in vs if v != "yall"] + ys
    ps = [np.load(os.path.join(d, v + ".npz"))["p"].astype(np.float32) for v in vs
          if os.path.exists(os.path.join(d, v + ".npz"))]
    if not ps or not os.path.exists(os.path.join(d, vs[0] + ".npz")):
        return None
    return np.clip(np.round(np.mean(ps, 0)), 0, 255).astype(np.uint8)


def scene_path(slug, ver=None):
    if is_big(slug):
        return big_dir("scenes", slug + ".json.gz")
    return os.path.join(VAL, "scenes", ver or scene_version(), slug + ".json")


def scene_version():
    return detector_version() + "_" + PROBS


def build_scene(slug, ver=None):
    """The fastscene scene of a validation course from the detection side's simulated-unmapped package
    (cache/heldout/<slug>: NAIP / DEM / canopy + OSM, golf features never read by the detector) and its cached U-Net
    probabilities (cache/heldout/probs/<slug>/<PROBS>.npz) when present; nothing is written into their folders."""
    ver = ver or scene_version()
    p = scene_path(slug, ver)
    if os.path.exists(p):
        return rd(p), dict(cached=True)
    d = os.path.join(HELDOUT, slug)
    if not os.path.exists(os.path.join(d, "imagery", "naip_rgb.tif")):
        raise FileNotFoundError("no heldout package for " + slug + " (heldout.py fetch)")
    import fastscene as FS
    P, T = None, {}
    P = bench_probs(slug)
    if P is not None:
        P = P.astype(np.float32) / 255.0
        T["probs"] = "cached " + PROBS
    t = time.time()
    sc, info = FS.build(d, out=False, P=P) if P is not None else FS.build(d, out=False)
    T["scene"] = round(time.time() - t, 1)
    sc["route_bench"] = dict(version=ver, probs=T.get("probs", "computed"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(sc, open(p + ".tmp", "w"), separators=(",", ":"))
    os.replace(p + ".tmp", p)
    return sc, T


def cmd_scenes(a):
    ver = a.ver or scene_version()
    log("detector version", ver)
    cs = courses(a.split)
    if a.slugs:
        cs = [c for c in cs if c["slug"] in a.slugs.split(",")]
    done = 0
    for c in cs[:a.limit or None]:
        if os.path.exists(scene_path(c["slug"], ver)):
            continue
        if a.probs_only and not os.path.exists(os.path.join(HELDOUT, "probs", c["slug"], PROBS + ".npz")):
            continue
        t = time.time()
        try:
            sc, T = build_scene(c["slug"], ver)
            log(c["slug"], c["split"], "ok", round(time.time() - t, 1), "s", T,
                "greens", len(sc.get("greens") or []), "tees", len(sc.get("tee_complexes") or []))
        except Exception as e:                                       # noqa: BLE001
            log(c["slug"], "FAIL", repr(e)[:300])
        done += 1
    log("done", done)


# ----------------------------------------------------------------------------- oracle scene
def _ring_of(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return [c[0]]
    if t == "MultiPolygon":
        return [q[0] for q in c]
    return []


def _centroid(ring):
    a = np.asarray(ring, float)
    return [float(a[:, 0].mean()), float(a[:, 1].mean())]


def _area_m2(ring):
    a = np.asarray(ring, float)
    k = math.cos(math.radians(a[:, 1].mean()))
    x, y = a[:, 0] * k * 111320.0, a[:, 1] * 111320.0
    return float(abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))) / 2)


def _jit(ll, rng, m):
    k = math.cos(math.radians(ll[1]))
    return [ll[0] + rng.normal(0, m) / (111320.0 * k), ll[1] + rng.normal(0, m) / 111320.0]


def _shift_ring(ring, dx, dy):
    return [[q[0] + dx, q[1] + dy] for q in ring]


ORACLE = dict(drop_green=0.15, drop_tee=0.30, drop_fair=0.2, false_green=0.12, false_tee=0.25, jitter_m=3.0)
ORACLE.update(json.loads(os.environ.get("ORACLE_NOISE") or "{}"))      # e.g. '{"drop_tee": 0}' for ablations


def oracle_scene(fc, seed=0, noise=None):
    """OSM truth objects as a course_scene/1-shaped scene with detection noise. Greens: every OSM golf=green (practice
    greens included: real false candidates), 15 % dropped; tee complexes: OSM tee boxes grouped within 25 m, 30 % of
    complexes dropped; false greens / tees: fairway-interior and rough spots; fairways 20 % dropped."""
    N = dict(ORACLE, **(noise or {}))
    rng = np.random.default_rng(seed)
    feats = fc.get("features", [])
    out = dict(schema="course_scene/1", mode="oracle", greens=[], tee_complexes=[], fairways=[], parking=[],
               clubhouse={}, oracle=N)
    gi = 0
    fair_rings = []
    for f in feats:
        p = f.get("properties") or {}
        if p.get("golf") == "fairway":
            for r in _ring_of(f["geometry"]):
                if len(r) >= 4:
                    fair_rings.append(r)
    for f in feats:
        p = f.get("properties") or {}
        if p.get("golf") != "green" or p.get("inside_course") is False:
            continue
        for r in _ring_of(f["geometry"]):
            if len(r) < 4 or rng.random() < N["drop_green"]:
                continue
            j = _jit(_centroid(r), rng, N["jitter_m"])
            c0 = _centroid(r)
            gi += 1
            out["greens"].append(dict(id="g%d" % gi, p=float(rng.uniform(0.6, 1.0)), p_hole=float(rng.uniform(0.5, 0.97)),
                                      centroid=j, area_m2=_area_m2(r),
                                      polygon=_shift_ring(r, j[0] - c0[0], j[1] - c0[1])))
    # tee boxes -> complexes (single link 25 m between centroids)
    boxes = []
    for f in feats:
        p = f.get("properties") or {}
        if p.get("golf") != "tee" or p.get("inside_course") is False:
            continue
        if f["geometry"]["type"] == "Point":
            c = f["geometry"]["coordinates"]
            boxes.append((list(c[:2]), None))
        for r in _ring_of(f["geometry"]):
            if len(r) >= 4:
                boxes.append((_centroid(r), r))
    par = list(range(len(boxes)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    from shapely.geometry import Point, Polygon
    lat0 = float(np.mean([b[0][1] for b in boxes])) if boxes else 0.0
    kx = math.cos(math.radians(lat0)) * 111320.0

    def shp(b):
        c, r = b
        if r:
            q = Polygon([((v[0] - c[0]) * kx, (v[1] - c[1]) * 111320.0) for v in r]).buffer(0)
            from shapely.affinity import translate
            return translate(q, c[0] * kx, c[1] * 111320.0)
        return Point(c[0] * kx, c[1] * 111320.0).buffer(3.0)
    sh = [shp(b) for b in boxes]
    for i in range(len(boxes)):                  # edge to edge 28 yd, as cands.from_osm groups OSM tee boxes
        for j in range(i + 1, len(boxes)):
            if sh[i].distance(sh[j]) <= 28 * 0.9144:
                par[find(i)] = find(j)
    grp = {}
    for i in range(len(boxes)):
        grp.setdefault(find(i), []).append(i)
    ti = 0
    for mem in grp.values():
        if rng.random() < N["drop_tee"]:
            continue
        ti += 1
        bx = []
        for k, i in enumerate(mem):
            c, r = boxes[i]
            j = _jit(c, rng, N["jitter_m"])
            bx.append(dict(id="t%d.%d" % (ti, k + 1), p=0.8, centroid=j,
                           polygon=_shift_ring(r, j[0] - c[0], j[1] - c[1]) if r else None))
        cc = _centroid([b["centroid"] for b in bx])
        out["tee_complexes"].append(dict(id="t%d" % ti, p=float(rng.uniform(0.5, 0.95)), p_range_tee=0.0, centroid=cc,
                                         boxes=bx, virtual=False))
    for r in fair_rings:
        if rng.random() < N["drop_fair"]:
            continue
        out["fairways"].append(dict(id="f%d" % (len(out["fairways"]) + 1), p=0.9, polygon=r, centroid=_centroid(r),
                                    area_m2=_area_m2(r)))
    # false candidates: green-like blobs inside fairways / at fairway ends, tee-like boxes in the rough beside them
    n_hole = max(1, len(out["greens"]))
    for k in range(int(round(N["false_green"] * n_hole))):
        if not fair_rings:
            break
        r = fair_rings[int(rng.integers(len(fair_rings)))]
        a = np.asarray(r, float)
        c = list(a[int(rng.integers(len(a)))] * 0.6 + a.mean(0) * 0.4)
        out["greens"].append(dict(id="gf%d" % k, p=float(rng.uniform(0.4, 0.8)), p_hole=float(rng.uniform(0.36, 0.75)),
                                  centroid=c, area_m2=float(rng.uniform(250, 600)), polygon=None, false=True))
    n_t = max(1, len(out["tee_complexes"]))
    for k in range(int(round(N["false_tee"] * n_t))):
        if not fair_rings:
            break
        r = fair_rings[int(rng.integers(len(fair_rings)))]
        a = np.asarray(r, float)
        c = _jit(list(a[int(rng.integers(len(a)))]), rng, 25.0)
        out["tee_complexes"].append(dict(id="tf%d" % k, p=float(rng.uniform(0.3, 0.7)), p_range_tee=0.0, centroid=c,
                                         boxes=[dict(id="tf%d.1" % k, p=0.5, centroid=c, polygon=None)], virtual=False,
                                         false=True))
    return out


# ----------------------------------------------------------------------------- one course
def bench_card(scj):
    """-> (source, card) the bench routes a course with. ROUTE_BENCH_CARD=pick (default since 2026-11-20): the card
    production picks for an unmapped course (package.pick_scorecard with no OSM hole ground = scorecard.choose_card
    over the web cards, with its sanity filter and source vote unless CARD_SANITY=0 / CARD_VOTE; (None, None) when
    no card is usable). TRAIN-BIG's 'picked' entry (a card_consensus copy made on the OSM ground) is left out.
    ROUTE_BENCH_CARD=chosen: scorecard.json's `chosen`, the raw card, as before: for TRAIN-BIG that is
    package.pick_scorecard on raw/summary.json, i.e. card_consensus on the OSM hole lengths the bench hides (45 of
    the 643 courses differ from production's pick; NOTES_ROUTING.md 2026-11-20 "card sanity"). The fits in
    route_models/v2 were made with `chosen`; cached prep pickles (ROUTE_BENCH_PREP) keep the card they were made with."""
    cards = [x for x in (scj or {}).get("cards") or [] if x.get("card")]
    if not cards:
        return None, None
    if os.environ.get("ROUTE_BENCH_CARD", "pick") == "pick":
        import scorecard as scm
        pick = scm.choose_card([(x["source"], scm.normalise(x["card"]), x.get("url")) for x in cards
                                if x["source"] != "picked"])
        return (pick[0], pick[1]) if pick else (None, None)
    ch = scj.get("chosen")
    x = next((x for x in cards if x["source"] == ch), cards[0])
    return x["source"], x["card"]


def load_course(c, scene_kind, seed=0, ver=None, router="v1"):
    import platform_common  # noqa: F401
    sys.path.insert(0, GEN)
    import routing as R
    fc, course, scj = course_files(c["slug"])
    truth = {k: v for k, v in R.truth_from_fc(fc).items() if int(k) <= 18}
    card_src, card = bench_card(scj)
    n_card = None
    if card and card.get("tee_sets"):
        n_card = max(len(s.get("yards") or []) for s in card["tee_sets"].values())
    kind = 18 if max(int(k) for k in truth) > 9 else 9
    n = n_card if n_card in (9, 18) else kind
    if scene_kind == "oracle":
        scene = oracle_scene(fc, seed=seed + sum(map(ord, c["slug"])))
    elif scene_kind == "fast":
        p = scene_path(c["slug"], ver)
        scene = rd(p)
        Pb = bench_probs(c["slug"], (ver or scene_version()).split("_", 1)[1]) if router == "v2" else None
        if router == "v2" and scene is not None and Pb is not None:
            import route_learn as RL                     # greens the U-Net map holds but the scene left out
            scene, _ = RL.augment_scene(scene, Pb, n_holes=n)
    elif scene_kind == "perc":
        m = {r["slug"]: r for r in rd(os.path.join(CD, "zero_tap", "benchmark.json"))["courses"]}
        f = (m.get(c["slug"]) or {}).get("files", {}).get("scene")
        scene = rd(os.path.join(ROOT, f)) if f else None
    else:
        raise ValueError(scene_kind)
    return dict(slug=c["slug"], split=c["split"], fc=strip_golf(fc), course=course, card=card, n=n, truth=truth,
                scene=scene, card_src=card_src)


def to_res(feats):
    """golf=hole features -> routing.score's result shape."""
    holes = {}
    for f in feats:
        p, co = f["properties"], f["geometry"]["coordinates"]
        t, g = co[0], co[-1]
        k = math.cos(math.radians(g[1]))
        L = math.hypot((t[0] - g[0]) * k, t[1] - g[1]) * 111320.0 / 0.9144
        holes[str(p["ref"])] = dict(tee_ll=tuple(t), green_ll=tuple(g), straight_yd=L, status="ok")
    return dict(holes=holes)


def line_len_yd(co):
    a = np.asarray(co, float)
    k = math.cos(math.radians(a[:, 1].mean()))
    return float(np.hypot(np.diff(a[:, 0]) * k, np.diff(a[:, 1])).sum() * 111320.0 / 0.9144)


def card_fit(feats, card, n):
    """Per hole |routed play length - card yards| for the course's best-fitting tee set (median residual)."""
    if not card or not card.get("tee_sets") or not feats:
        return None
    L = {int(f["properties"]["ref"]): line_len_yd(f["geometry"]["coordinates"]) for f in feats}
    best = None
    for nm, s in card["tee_sets"].items():
        y = s.get("yards") or []
        if len(y) < n and y and n % len(y) == 0:
            y = list(y) * (n // len(y))
        r = [abs(L[i] - y[i - 1]) for i in L if i - 1 < len(y) and y[i - 1]]
        if r and (best is None or np.median(r) < np.median(best[1])):
            best = (nm, r, {i: L[i] - y[i - 1] for i in L if i - 1 < len(y) and y[i - 1]})
    return best


PREP = os.environ.get("ROUTE_BENCH_PREP") or os.path.join(
    VAL, "prep" if os.environ.get("ROUTE_SPLIT_TEES", "1") == "0" else
    "prep_split" if float(os.environ.get("ROUTE_LEARN_PEAKS", "0.2") or 0) == 0 else "prep_pk20")   # split tees, P(green) peaks


def prep_path(slug, scene_kind, seed, router, ver=None):
    tag = scene_kind + ("_" + (ver or scene_version()) if scene_kind == "fast" else "")
    return os.path.join(PREP, tag, router, "%s_%d.pkl" % (slug, seed))


_PK = {}


def _picks(env="ROUTE_RERANK_PICKS"):
    """ROUTE_RERANK_PICKS: json {slug: [option per position]} (route_rerank out-of-fold picks); ROUTE_TEE_PICKS:
    {slug: {position: [x, y]}} (route_tee out-of-fold tee spots), else {}"""
    p = os.environ.get(env)
    if p and p not in _PK:
        _PK[p] = json.load(open(p))
    return _PK.get(p, {}) if p else {}


def run_one(c, scene_kind, router="v0", seed=0, ver=None, prep=False):
    """route one course and score it. prep=True: cache prepare()'s output (candidates, features, model scores) per
    (course, scene, seed, router) on disk and reuse it (parameter tuning re-solves only)."""
    import pickle
    import routing as R
    pp = prep_path(c["slug"], scene_kind, seed, router, ver)
    x = pd = None
    if prep and os.path.exists(pp):
        import route_scene as RS
        RS._mods()                                   # the pickled Course holds truth.Proj (zero_tap on the path)
        x, pd = pickle.load(open(pp, "rb"))
    if x is None:
        x = load_course(c, scene_kind, seed, ver, router)
        if prep and x["scene"] is not None:
            import route_scene as RS
            try:
                pd = RS.prepare(x["fc"], x["scene"], x["card"], x["n"], version=router)
            except Exception:                                        # noqa: BLE001
                pd = None
            os.makedirs(os.path.dirname(pp), exist_ok=True)
            x = dict(x, fc=None, scene=x["scene"] and {}) if pd is not None else x
            pickle.dump((x, pd), open(pp, "wb"))
    sc_dir = os.environ.get("ROUTE_BENCH_SC")                  # route_learn.py score overrides (ph / pw ...)
    if sc_dir and pd is not None and os.path.exists(os.path.join(sc_dir, x["slug"] + ".pkl")):
        pd = (dict(pd[0], sc=dict(pd[0]["sc"], **pickle.load(open(os.path.join(sc_dir, x["slug"] + ".pkl"), "rb")))),
              pd[1])
    if router == "v2" and pd is not None and pd[0].get("_maps") is None:
        import route_learn as RL                         # the pixel maps (fairway / turf / trees) for v2's tee choice
        sc0 = rd(scene_path(x["slug"], ver))
        if sc0 is not None:
            pv = (ver or scene_version()).split("_", 1)[1]
            pd = (dict(pd[0], _maps=RL.bench_maps(x["slug"], sc0, pv).bind(pd[0]["co"]["pj"])), pd[1])
            Pb = bench_probs(x["slug"], pv)
            if Pb is not None:
                pd[0]["_maps"].green, pd[0]["_maps"].tee = Pb[1], Pb[2]     # P(green) / P(tee): virtual end anchors
            if Pb is not None:                           # detector p / map flag of each candidate (the gate reads them)
                sca, _ = RL.augment_scene(sc0, Pb, n_holes=x["n"])
                pd[0]["_gattr"], pd[0]["_tattr"] = RL.obj_attrs(pd[0], sca, pd[0]["_maps"])
            if json.loads(os.environ.get("ROUTER_PARAMS") or "{}").get("map_fair"):
                pd[0]["co"] = dict(pd[0]["co"], maps=pd[0]["_maps"])
    alt_src = _picks("ROUTE_CARD_PICKS").get(x["slug"])        # route_scene card selection's out-of-fold pick
    if alt_src and pd is not None and x["scene"] is not None:
        _, _, scj0 = course_files(x["slug"])
        alt = next((c["card"] for c in (scj0 or {}).get("cards") or [] if c.get("source") == alt_src and c.get("card")), None)
        fd = os.environ.get("ROUTE_BENCH_FOLDS")                 # route_learn fold models (folds.json + fold_<i>.pkl)
        if alt is not None and fd:
            import route_learn as RL
            fo = json.load(open(os.path.join(fd, "folds.json")))
            sc0 = rd(scene_path(x["slug"], ver))
            pv = (ver or scene_version()).split("_", 1)[1]
            sca, _ = RL.augment_scene(sc0, bench_probs(x["slug"], pv), n_holes=x["n"])
            d = dict(pd[0], card=alt)
            RL.rescore(d, sca, d["_maps"], card=alt, n_holes=x["n"],
                       path=os.path.join(fd, "fold_%d.pkl" % fo[x["slug"]]))
            pd = (d, pd[1])
            x = dict(x, card=alt)
    elif os.environ.get("ROUTE_BENCH_FOLD_RESCORE") == "1" and pd is not None and x["scene"] is not None:
        # every course rescored with its route_learn fold model on its own (bench_card) card: out-of-fold scores
        # without ROUTE_BENCH_SC (whose cached scores were made with scorecard.json's chosen card)
        import route_learn as RL
        fd = os.environ["ROUTE_BENCH_FOLDS"]
        fo = json.load(open(os.path.join(fd, "folds.json")))
        sc0 = rd(scene_path(x["slug"], ver))
        pv = (ver or scene_version()).split("_", 1)[1]
        sca, _ = RL.augment_scene(sc0, bench_probs(x["slug"], pv), n_holes=x["n"])
        d = dict(pd[0], card=x["card"])
        RL.rescore(d, sca, d["_maps"], card=x["card"], n_holes=x["n"],
                   path=os.path.join(fd, "fold_%d.pkl" % fo[x["slug"]]))
        pd = (d, pd[1])
    out = dict(slug=x["slug"], split=x["split"], n=x["n"], n_true=len(x["truth"]), has_card=x["card"] is not None)
    if alt_src:
        out["card_pick"] = alt_src
    out["card_src"] = alt_src or x.get("card_src")
    if x["scene"] is None:
        out.update(error="no scene")
        return out
    if prep and pd is None:
        out.update(error="prepare failed")
        return out
    t = time.time()
    try:
        if router == "v0":
            import route_scene as RS
            r = RS.route(x["fc"], x["scene"], x["card"], x["n"], prepared=pd)
        else:
            import route_scene as RS
            prm = json.loads(os.environ.get("ROUTER_PARAMS") or "{}")
            pk = None if alt_src else _picks().get(x["slug"])   # route_rerank's out-of-fold pick (made for its card)
            if pk is not None:
                prm["fix_seq"] = pk
            tk = None if alt_src else _picks("ROUTE_TEE_PICKS").get(x["slug"])   # route_tee's out-of-fold tee choices
            if tk is not None:
                prm["tee_fix"] = tk
            r = RS.route(x["fc"], x["scene"], x["card"], x["n"], version=router, params=prm, prepared=pd)
    except Exception as e:                                           # noqa: BLE001
        out.update(error=repr(e)[:300], seconds=round(time.time() - t, 2))
        return out
    out["seconds"] = round(time.time() - t, 2)
    _, _, scj = course_files(x["slug"])
    import route_gate as RG
    out["card_conflict"] = bool(scj and x["card"] and RG.card_order_conflict(
        x["card"], [c["card"] for c in scj.get("cards") or [] if c.get("card")], int(x["n"])))
    feats = r.pop("features", [])
    r.pop("_used", None)
    sc = R.score(to_res(feats), x["truth"])
    out["score"] = {k: v for k, v in sc.items() if k != "per_hole"}
    out["hole_ok"] = {k: e["hole_ok"] for k, e in sc["per_hole"].items()}
    out["hole_ok_fwd"] = hole_ok_fwd(feats, x["truth"], sc["per_hole"])
    cf = card_fit(feats, x["card"], x["n"])
    if cf:
        out["card_set"], out["card_resid"] = cf[0], {str(k): round(v, 1) for k, v in cf[2].items()}
    out["route"] = {k: v for k, v in r.items() if not k.startswith("_")}
    out["lines"] = {f["properties"]["ref"]: dict(co=f["geometry"]["coordinates"], tee=f["properties"].get("tee_src"),
                                                 green=f["properties"].get("green_src")) for f in feats}
    out["gate_v0"] = gate_v0(r, feats, x)
    return out


def gate_v0(r, feats, x):
    """The fast.py gate as of 2aea53af7 (without the package-build gates, approximated from the lines): min margin >= 4,
    no virtual hole, every hole routed, <= 3 holes resting on detections, no shared green, card misfit < 3 holes."""
    why = []
    if r.get("min_margin", 0.0) < 4.0 or r.get("n_virtual") or len(r.get("margins") or []) < r.get("n_holes", 0):
        why.append("margin/virtual")
    if len(r.get("detected_holes") or []) > 3:
        why.append("detected>3")
    g = [f["geometry"]["coordinates"][-1] for f in feats]
    for i in range(len(g)):
        for j in range(i + 1, len(g)):
            k = math.cos(math.radians(g[i][1]))
            if math.hypot((g[i][0] - g[j][0]) * k, g[i][1] - g[j][1]) * 111320.0 / 0.9144 <= 15.0:
                why.append("shared green")
    cf = card_fit(feats, x["card"], x["n"])
    if cf and sum(abs(v) > 25 for v in cf[2].values()) >= 3:
        why.append("card misfit")
    return dict(show=not why, why=sorted(set(why)))


def _job(a):
    return run_one(*a)


FWD_BEHIND_YD = 200.0     # hole_ok_fwd: how far behind the OSM way's start a routed tee may sit
FWD_LATERAL_YD = 40.0     # ... and how far off the line of the way's first segment (the scorer's tee tolerance)


def hole_ok_fwd(feats, truth, per):
    """The secondary bench metric (2026-11-20, forward-tee convention): a hole is right as routing.score has it, or
    when its green is right and its routed tee sits behind the OSM way's start, within FWD_LATERAL_YD of the first
    segment's line and up to FWD_BEHIND_YD back (a back box when the mapper started the way at a forward tee: on the
    default 87 such holes on choice, 60 on never-used). The primary metric stays routing.score."""
    from routing import Proj
    lines = {str(f["properties"]["ref"]): f["geometry"]["coordinates"] for f in feats}
    out = {}
    for k, e in per.items():
        ok = bool(e["hole_ok"])
        if not ok and e.get("green_ok") and k in lines and k in truth:
            t = truth[k]
            pr = Proj(*t["green_ll"])
            ln = pr.ring(t["line"])
            a = ln[0]
            b = next((q for q in ln[1:] if np.hypot(*(q - a)) > 1.0), None)
            if b is not None:
                u = (b - a) / np.hypot(*(b - a))
                p = np.asarray(pr.fwd(*lines[k][0])) - a
                along, lat = float(p @ u), abs(float(p[0] * u[1] - p[1] * u[0]))
                ok = -FWD_BEHIND_YD <= along <= 0 and lat <= FWD_LATERAL_YD
        out[k] = ok
    return out


def summarise(rs, gate_key="gate_v0"):
    ok = [r for r in rs if "score" in r]
    H = sum(r["n_true"] for r in rs)
    right = sum(sum(r["hole_ok"].values()) for r in ok)
    allr = [r for r in ok if r["score"]["all_correct"]]
    res = [abs(v) for r in ok for v in (r.get("card_resid") or {}).values()]
    shown = [r for r in ok if (r.get(gate_key) or {}).get("show")]
    Hok = sum(r["n_true"] for r in ok)
    right2 = sum(sum((r.get("hole_ok_fwd") or r["hole_ok"]).values()) for r in ok)
    return dict(courses=len(rs), errors=len(rs) - len(ok), hole_acc=round(right / max(H, 1), 4),
                hole_acc_fwd=round(right2 / max(H, 1), 4),
                hole_acc_routed=round(right / max(Hok, 1), 4),
                all_right=f"{len(allr)}/{len(rs)}", all_right_frac=round(len(allr) / max(len(rs), 1), 4),
                card_err_med=round(float(np.median(res)), 1) if res else None,
                card_err_p90=round(float(np.percentile(res, 90)), 1) if res else None,
                card_within_15pct=None,
                shown=len(shown), shown_right=sum(r["score"]["all_correct"] for r in shown),
                gate_precision=round(sum(r["score"]["all_correct"] for r in shown) / len(shown), 3) if shown else None,
                coverage=round(len(shown) / max(len(rs), 1), 3),
                sec_mean=round(float(np.mean([r.get("seconds", 0) for r in rs])), 2))


def cmd_eval(a):
    cs = courses(a.split)
    if a.slugs:
        cs = [c for c in cs if c["slug"] in a.slugs.split(",")]
    if a.card_only:
        cs = [c for c in cs if c.get("card")]
    ver = a.ver or (scene_version() if a.scene == "fast" else None)
    jobs = [(c, a.scene, a.router, s, ver, a.prep) for s in range(a.seeds) for c in cs]
    t = time.time()
    if a.procs > 1:
        from multiprocessing import Pool
        with Pool(a.procs) as pool:
            rs = pool.map(_job, jobs, chunksize=1)
    else:
        rs = [_job(j) for j in jobs]
    S = summarise(rs)
    S.update(scene=a.scene, router=a.router, split=a.split, seeds=a.seeds, detector=ver, wall=round(time.time() - t, 1))
    log(json.dumps(S))
    if a.verbose:
        for r in rs:
            log(r["slug"], r.get("error") or "", (r.get("score") or {}).get("hole_number_acc"),
                (r.get("route") or {}).get("min_margin"), (r.get("gate_v0") or {}).get("why"))
    if a.out:
        json.dump(dict(summary=S, courses=rs), open(a.out, "w"), indent=0, default=float)


def render(slug, res, out, scene=None):
    """NAIP of the course (detection side's package) with the scene's greens (magenta) / tee boxes (cyan), the hidden
    OSM hole lines (white, number at the tee) and the routed lines (green = right, red = wrong; dashed end = virtual)."""
    import cv2
    import fastscene as FS
    sys.path.insert(0, GEN)
    import routing as R
    d = os.path.join(HELDOUT, slug)
    st = FS.grid_stack(d)
    img = np.transpose(st.a["naip"][:3], (1, 2, 0))[:, :, ::-1].copy()
    img = cv2.convertScaleAbs(img, alpha=1.15, beta=5)

    def px(ll):
        ll = np.asarray(ll, float).reshape(-1, 2)
        r, c = st.ll_to_rc(ll[:, 0], ll[:, 1])
        return np.round(np.c_[c, r]).astype(np.int32)
    for g in (scene or {}).get("greens") or []:
        if g.get("polygon") and len(g["polygon"]) >= 3:
            cv2.polylines(img, [px(g["polygon"]).reshape(-1, 1, 2)], True, (255, 0, 255), 2)
    for t in (scene or {}).get("tee_complexes") or []:
        for b in t.get("boxes") or []:
            if b.get("polygon") and len(b["polygon"]) >= 3:
                cv2.polylines(img, [px(b["polygon"]).reshape(-1, 1, 2)], True, (255, 255, 0), 1)
    fc, _, _ = course_files(slug)
    truth = R.truth_from_fc(fc)
    for ref, t in truth.items():
        q = px(t["line"])
        cv2.polylines(img, [q.reshape(-1, 1, 2)], False, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img, ref, tuple(int(v) for v in q[0] + [-14, 14]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    for ref, ln in (res.get("lines") or {}).items():
        q = px(ln["co"])
        col = (0, 220, 0) if (res.get("hole_ok") or {}).get(ref) else (0, 0, 255)
        cv2.polylines(img, [q.reshape(-1, 1, 2)], False, col, 2, cv2.LINE_AA)
        for end, k in ((q[0], "tee"), (q[-1], "green")):
            cv2.circle(img, tuple(int(v) for v in end), 5 if ln.get(k) == "virtual" else 3, col, 1 if ln.get(k) == "virtual" else -1)
        cv2.putText(img, ref, tuple(int(v) for v in q[0] + [6, -6]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
        cv2.putText(img, ref, tuple(int(v) for v in q[0] + [6, -6]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 1)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    cv2.imwrite(out, img, [cv2.IMWRITE_JPEG_QUALITY, 82])
    return out


def gate_rows(rs):
    """per-course rows for route_gate.fit / curve from eval results (v1 with margins)"""
    out = []
    for r in rs:
        if "score" not in r or not r.get("has_card"):
            continue
        hf = (r.get("route") or {}).get("hole_features") or []
        ok = [bool(r["hole_ok"].get(h["ref"], False)) for h in hf]
        hard = bool((r.get("route") or {}).get("n_miss")) or len(hf) < r["n"] or bool(r.get("card_conflict"))
        out.append(dict(slug=r["slug"], hole_features=hf, hole_ok=ok, all_right=bool(r["score"]["all_correct"]),
                        hard_block=hard))
    return out


def cmd_gate(a):
    """fit route_gate on the train eval file, threshold for precision 1.0 there; curves on train and test"""
    import route_gate as RG
    tr = gate_rows(json.load(open(a.train))["courses"])
    te = gate_rows(json.load(open(a.test))["courses"]) if a.test else []
    w = RG.fit(tr)
    ct, ce = RG.curve(tr, w), RG.curve(te, w)
    thr = RG.pick_threshold(ct, len(tr), min_shown=RG.MIN_SHOWN, min_ratio=RG.MIN_RATIO)
    thr_any = RG.pick_threshold(ct, len(tr), min_shown=RG.MIN_SHOWN)        # without the ratio rule (reported)
    def at(cur, t):
        s = [r for r in cur if r["threshold"] >= t]
        return s[-1] if s else dict(shown=0, right=0, precision=None)
    res = dict(w=w, feats=RG.FEATS, threshold=thr, fitted_on=a.train, train_courses=len(tr), test_courses=len(te),
               train_at_threshold=at(ct, thr), test_at_threshold=at(ce, thr),
               threshold_min_shown_only=thr_any, train_at_min_shown_only=at(ct, thr_any),
               test_at_min_shown_only=at(ce, thr_any), train_curve=ct[:40], test_curve=ce[:40])
    log(json.dumps({k: v for k, v in res.items() if not k.endswith("curve")}))
    if a.write:
        json.dump(res, open(RG.PARAMS, "w"), indent=1)
    return res


# ----------------------------------------------------------------------------- tier C (route_joint) calibration bench
def joint_one(c, mode):
    """tier C simulated on a mapped course: OSM greens / tees kept, golf=hole ways hidden (mode 'osm': route_joint.route)
    or kept without their refs (mode 'lines': route_joint.route_lines). -> per-hole rows for route_gate.fit_joint"""
    import routing as R
    import route_joint as RJ
    fc, _, scj = course_files(c["slug"])
    truth = {k: v for k, v in R.truth_from_fc(fc).items() if int(k) <= 18}
    x = load_course(dict(c), "oracle")                     # only for card / n (the oracle scene is not used)
    card, n = x["card"], x["n"]
    feats = fc.get("features", [])
    if mode == "osm":
        f2 = dict(fc, features=[f for f in feats if (f.get("properties") or {}).get("golf") != "hole"])
        t = time.time()
        r = RJ.route(f2, card, n)
    else:
        f2 = dict(fc, features=[f if (f.get("properties") or {}).get("golf") != "hole" else
                                dict(f, properties={k: v for k, v in f["properties"].items() if k != "ref"}) for f in feats])
        lines = RJ.unnumbered_lines(f2, n)
        if lines is None:
            return None
        t = time.time()
        r = RJ.route_lines(f2, lines, card, n)
    out = dict(slug=c["slug"], split=c["split"], mode=mode, n=n, n_true=len(truth), seconds=round(time.time() - t, 2))
    fs = r.pop("features", [])
    sc = R.score(to_res(fs), truth)
    out["hole_ok"] = {k: e["hole_ok"] for k, e in sc["per_hole"].items()}
    out["route"] = r
    cf = card_fit(fs, card, n)
    out["card_resid"] = {str(k): round(v, 1) for k, v in cf[2].items()} if cf else {}
    out["card_yd"] = {}
    if cf:
        y = (card.get("tee_sets") or {}).get(cf[0], {}).get("yards") or []
        out["card_yd"] = {str(i + 1): v for i, v in enumerate(y[:n])}
    out["refs"] = [f["properties"]["ref"] for f in fs]
    return out


def _job_joint(a):
    try:
        return joint_one(*a)
    except Exception as e:                                           # noqa: BLE001
        return dict(slug=a[0]["slug"], mode=a[1], error=repr(e)[:200])


def cmd_joint(a):
    cs = [c for c in courses(a.split) if c.get("card") and (not a.slugs or c["slug"] in a.slugs.split(","))]
    jobs = [(c, m) for m in ("osm", "lines") for c in cs]
    from multiprocessing import Pool
    with Pool(a.procs) as pool:
        rs = [r for r in pool.map(_job_joint, jobs, chunksize=2) if r]
    for m in ("osm", "lines"):
        x = [r for r in rs if r.get("mode") == m and "hole_ok" in r]
        H = sum(r["n_true"] for r in x)
        ok = sum(sum(r["hole_ok"].values()) for r in x)
        log(m, "courses", len(x), "holes right", round(ok / max(H, 1), 4), "errors", sum(1 for r in rs if r.get("mode") == m and "error" in r))
    if a.out:
        json.dump(dict(courses=rs), open(a.out, "w"), default=float)


def _job_p(a):
    os.environ["ROUTER_PARAMS"] = json.dumps(a[-1])
    return run_one(*a[:-1])


TUNE_GRID = dict(c_vt=[-1.0, 0.5, 2.0, 4.0], c_vg=[-1.0, 0.5, 2.0, 5.0], c_miss=[3.0, 6.0, 9.0], w_c=[0.5, 1.0, 2.0],
                 card_s=[5.0, 9.0, 15.0], w_w=[0.5, 1.0, 2.0], w_h=[0.5, 1.0, 1.5], v1=[25.0, 45.0, 80.0],
                 v_base=[0.0, 0.4, 1.0], w_cov=[0.0, 3.0, 6.0], reuse_cost=[0.5, 1.5, 4.0], w_obr=[0.0, 4.0, 10.0],
                 w_s=[0.5, 1.0, 2.0], walk_miss=[1.0, 3.0, 5.0], w_tree=[0.0, 1.0], w_x=[0.75, 1.5, 3.0],
                 w_dg=[0.0, 0.5, 1.0])


def cmd_tune(a):
    """coordinate descent on the train split (hole accuracy + share of courses with every hole right), one parameter
    at a time over TUNE_GRID, prepared inputs cached; writes the path to --out (json lines)."""
    from multiprocessing import Pool
    cs = [c for c in courses(a.split) if c.get("card") and (not a.slugs or c["slug"] in a.slugs.split(","))]
    assert "test" not in a.split.split("+"), "never tune on test"
    ver = a.ver or (scene_version() if a.scene == "fast" else None)
    cur = json.loads(a.start or "{}")
    cur.setdefault("no_margins", 1)
    cur.setdefault("beam", a.beam)
    pool = Pool(a.procs)

    def score(pp):
        jobs = [(c, a.scene, a.router, s, ver, True, pp) for s in range(a.seeds) for c in cs]
        rs = pool.map(_job_p, jobs, chunksize=1)
        S = summarise(rs)
        return S["hole_acc"] + S["all_right_frac"], S
    best, S = score(cur)
    out = open(a.out, "a") if a.out else None

    def rec(pp, v, S):
        line = json.dumps(dict(params=pp, obj=round(v, 4), hole_acc=S["hole_acc"], all_right=S["all_right"]))
        log(line)
        if out:
            out.write(line + "\n")
            out.flush()
    rec(cur, best, S)
    grid = json.loads(a.grid) if a.grid else TUNE_GRID
    for rnd in range(a.rounds):
        improved = False
        for k, vals in grid.items():
            for v in vals:
                if cur.get(k) == v:
                    continue
                pp = dict(cur, **{k: v})
                val, S = score(pp)
                rec(pp, val, S)
                if val > best + 1e-4:
                    best, cur, improved = val, pp, True
        if not improved:
            break
    log("BEST", json.dumps(cur), best)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--split", default="test")
    ap.add_argument("--slugs", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--scene", default="oracle")
    ap.add_argument("--router", default="v0")
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--ver", default="")
    ap.add_argument("--card-only", action="store_true")
    ap.add_argument("--prep", action="store_true", help="cache / reuse the prepared solver inputs")
    ap.add_argument("--start", default="")
    ap.add_argument("--train", default="")
    ap.add_argument("--beam", type=int, default=1500)
    ap.add_argument("--test", default="")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--probs-only", action="store_true", help="scenes: only courses whose U-Net probabilities are cached")
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--grid", default="", help="tune: json {param: [values]} instead of TUNE_GRID")
    ap.add_argument("--out", default="")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if a.cmd == "scenes":
        cmd_scenes(a)
    elif a.cmd == "eval":
        cmd_eval(a)
    elif a.cmd == "tune":
        cmd_tune(a)
    elif a.cmd == "gate":
        cmd_gate(a)
    elif a.cmd == "joint":                       # joint --split train+big --out joint.json (tier C calibration rows)
        cmd_joint(a)
    elif a.cmd == "render":                      # render --out RESULTS.json --slugs a,b  (eval --out file)
        R0 = {r["slug"]: r for r in json.load(open(a.out))["courses"]}
        for sl in a.slugs.split(","):
            ver = a.ver or scene_version()
            p = render(sl, R0[sl], os.path.join(VAL, "render", sl + ".jpg"), rd(scene_path(sl, ver)))
            log(p)
