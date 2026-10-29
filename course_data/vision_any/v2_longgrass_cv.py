"""Long grass (native) for the automatic map, re-fitted with leave-one-course-out cross-validation over every
truth course (Spirit Hollow, Mozingo, Veenker, Coldwater, Ellis, Eagle Knoll, Gateway National).

  python3 course_data/vision_any/v2_longgrass_cv.py samples --slug V --out DIR     native vs mown cells of V's hand map
  python3 course_data/vision_any/v2_longgrass_cv.py model   --samples DIR --out M  LightGBM on all seven hand maps
  python3 course_data/vision_any/v2_longgrass_cv.py layers  --slug V --samples DIR --model M --out DIR2
  python3 course_data/vision_any/v2_longgrass_cv.py score   --dir DIR2 --rows ROWS.json [--shard i --nshards n]
  python3 course_data/vision_any/v2_longgrass_cv.py report  --rows 'ROWS*.json' --dir DIR2  -> v2_longgrass_cv.{md,json}
  python3 course_data/vision_any/v2_longgrass_cv.py integrate --dir DIR2 --model M      (only if the rule passed)
  python3 course_data/vision_any/v2_longgrass_cv.py rescore                             -> appends to the .md

Classifier: the v2 long-grass LightGBM (v2_model: multi-year NAIP RGB + NIR, texture, lidar point statistics
(height above ground, low / very-low return fractions, roughness), terrain, OSM turf distances; all relative to
the course's own mown turf), trained on the hand maps of the OTHER six truth courses for each test course (so the
probabilities on a course never saw its labels). The product's previous model was trained on Spirit Hollow +
Mozingo only and long grass was switched off (model.json native_thr = null).

Settings (trees = the product's line: lidar canopy HAG > 2.5 m, clumps >= 100 m2, eroded 1 m; water as committed):
  thr   P(native) threshold (3x3 smoothed, opened 1 m / closed 2 m, >= 150 yd2: v2_model.native_mask)
  mode  strict (never on the trees line) | relaxed (long grass may run under scattered canopy; trees there dropped)
  dmin  no long grass within dmin yds of an OSM fairway (the Driver landing zone is mostly mown rough)
  gate  long grass only on a course where it covers >= gate of the OSM course outline (links / prairie courses),
        else off for the whole course
  off   no long grass (the product setting)
Each setting: the committed package with its vision zones replaced (v2_calibrate.rebuild_package, OB re-inferred),
product quick decision (n = 8000) per tee shot vs the hand truth (v2_calibrate.score_package = scoreboard rows).

Selection (report): leave-one-COURSE-out over the seven courses: for each test course the setting with the most
same clubs (then the least summed regret, then the product setting) on the other six is scored on it; the
cross-validated number is the sum of those seven. Adoption rule: the cross-validated same-club total beats the
product setting's, and no course is worse than the product setting by more than one hole (neither in
cross-validation nor with the setting chosen on all seven).
"""
import argparse
import os as _os
_os.environ.setdefault("OMP_NUM_THREADS", "1")
import glob
import hashlib
import json
import os
import sys
import time

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CD = os.path.join(ROOT, "course_data")
sys.path.insert(0, HERE)
import layers as L                                           # noqa: E402

YD = 0.9144
COURSES = {"spirit_hollow": "spirit_hollow", "mozingo": "mozingo_lake", "veenker": "veenker",
           "coldwater": "coldwater", "ellis": "ellis", "eagle_knoll": "eagle_knoll",
           "gateway_national": "gateway_national"}           # vision slug -> package / scoreboard slug
EXTRA_SB = [dict(slug="eagle_knoll", name="Eagle Knoll", package="course_data/packages/eagle_knoll/package.json",
                 tees="Back", truth="hand", hand="course_data/truth/eagle_knoll/hand_zones_ll.json"),
            dict(slug="gateway_national", name="Gateway National", tees="Back", truth="hand",
                 package="course_data/packages/gateway_national/package.json",
                 hand="course_data/truth/gateway_national/hand_zones_ll.json")]
NO_TRUTH = ["wakonda"]                                       # integrated too (no labels: the all-course model)
NAMES = {"spirit_hollow": "Spirit Hollow", "mozingo_lake": "Mozingo", "veenker": "Veenker", "coldwater": "Coldwater",
         "ellis": "Ellis", "eagle_knoll": "Eagle Knoll", "gateway_national": "Gateway"}
GRID = dict(thr=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8], mode=["strict", "relaxed"], dmin=[0, 10, 20, 30],
            gate=[0, 0.01, 0.02, 0.04, 0.08, 0.15])
PRODUCT = "off"
CLUB_ORDER = ["Driver", "2-wood", "3-wood", "4-wood", "5-wood", "Hybrid", "Long iron", "Mid iron", "Short iron"]


# =========================================================================== rev 2
# rev 2 (request {"rev": 2}): a landing-corridor-focused classifier. Training cells are only the hand maps' corridor
# cells 145-440 yds off the tee (|lateral| <= 55 yds), the four newer truth courses join the leave-one-course-out,
# and five feature groups are added on top of the v2 stack (add_rev2_features). Same settings grid, same scorer,
# same adoption rule.
def _request_rev():
    try:
        return int(json.load(open(os.path.join(CD, "requests", "longgrass_cv.json"))).get("rev", 1))
    except Exception:                                          # noqa: BLE001
        return 1


REV = int(os.environ.get("LONGGRASS_REV") or _request_rev())
SUFFIX = "" if REV < 2 else f"_rev{REV}"                 # rev >= 2 writes v2_longgrass_cv_rev<n>.{md,json}
TRAIN_CORRIDOR = dict(a0=145.0, a1=440.0, lat=55.0)
REV2_COURSES = ("blue_hills", "pine_dunes", "national_kc", "hot_springs_arlington")
REV2_FEATS = ("r2_season_ndvi", "r2_season_nir", "r2_season_slope", "r2_nirtex5_my", "r2_nirtex_ratio",
              "r2_lowveg3", "r2_lowveg7", "r2_lowfrac7", "r2_coh2", "r2_coh5", "r2_grad3", "r2_d_edge",
              "r2_osm_native_in", "r2_d_osm_native", "r2_osm_rough_in")


def _rev2_setup():
    names = {"blue_hills": "Blue Hills", "pine_dunes": "Pine Dunes", "national_kc": "National KC",
             "hot_springs_arlington": "Hot Springs Arlington"}
    for v in REV2_COURSES:
        hp = os.path.join(CD, "truth", v, "hand_zones_ll.json")
        pp = os.path.join(CD, "packages", v, "package.json")
        if not (os.path.exists(hp) and os.path.exists(pp)):
            continue
        COURSES[v] = v
        NAMES[v] = names[v]
        tees = json.load(open(hp)).get("tee_set")
        pk = json.load(open(pp))
        sets = pk.get("tee_sets") or {}
        sets = list(sets) if isinstance(sets, dict) else [t.get("name") for t in sets]
        if tees not in sets:                                   # e.g. National KC: the package has only osm_back
            tees = pk.get("tee_set") or (sets[0] if sets else tees)
        EXTRA_SB.append(dict(slug=v, name=names[v], tees=tees, truth="hand",
                             package=f"course_data/packages/{v}/package.json",
                             hand=f"course_data/truth/{v}/hand_zones_ll.json"))


if REV >= 2:
    _rev2_setup()


def feature_names():
    return list(model_meta()["features"]) + (list(REV2_FEATS) if REV >= 2 else [])


def add_rev2_features(D):
    """The rev-2 feature groups, course-relative like the v2 stack (robust z vs the course's own mown turf):
      seasonal contrast  NAIP years ordered by how green the course's mown turf is that year; a cell's NDVI / NIR
                         z-score in the most dormant year minus the greenest (unmown grass browns and greens on its
                         own schedule), and the slope of its NDVI z against turf greenness across years
      NIR texture        multi-year mean of the 5 m NIR local std; 3 m / 15 m texture ratio (fine stems vs patches)
      lidar 0.2-1.5 m    share of cells around whose highest return is 0.2-1.5 m above ground (3 / 7 m windows;
                         3DEP point statistics when present, else the 1 m HAG raster); the 0.3-1.5 m return share
      mowing edges       structure-tensor coherence of the latest NIR (2 / 5 m: mowing stripes are coherent),
                         gradient magnitude, distance to the nearest strong NIR edge (mown / unmown boundary)
      OSM polygons       inside / distance to OSM natural=grassland / heath / scrub / wetland, landuse=meadow,
                         golf=native; inside golf=rough"""
    import v2_features as VF
    S, F, M = D["S"], D["F"], D["M"]
    ref = F.ref
    nan = np.full((S.H, S.W), np.nan, np.float32)
    ys = []
    for yr, b in S.naip:
        m = VF.year_maps(b)
        valid = np.isfinite(b).all(-1)
        g = float(np.nanmedian(np.where(ref & valid, m["ndvi"], np.nan))) if (ref & valid).any() else np.nan
        zn = VF.robust_norm(ndimage.gaussian_filter(m["ndvi"], 1.5), ref)
        zi = VF.robust_norm(ndimage.gaussian_filter(m["nir"], 1.5), ref)
        tx = VF.robust_norm(VF.local_std(m["nir"], 5), ref)
        ys.append((g, np.where(valid, zn, np.nan), np.where(valid, zi, np.nan), np.where(valid, tx, np.nan), m["nir"]))
    ok = [y for y in ys if np.isfinite(y[0])]
    if len(ok) >= 2:
        ok.sort(key=lambda y: y[0])
        F.add("r2_season_ndvi", ok[0][1] - ok[-1][1])
        F.add("r2_season_nir", ok[0][2] - ok[-1][2])
        gv = np.array([y[0] for y in ok])
        gv = (gv - gv.mean()) / (gv.std() + 1e-6)
        Z = np.stack([np.nan_to_num(y[1]) for y in ok])
        F.add("r2_season_slope", np.tensordot(gv, Z, 1) / len(ok))
    else:
        for n in ("r2_season_ndvi", "r2_season_nir", "r2_season_slope"):
            F.add(n, nan)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        F.add("r2_nirtex5_my", np.nanmean(np.stack([y[3] for y in ys]), 0) if ys else nan)
    if ys:
        nir0 = np.nan_to_num(ys[0][4])
        F.add("r2_nirtex_ratio", np.log((VF.local_std(nir0, 3) + 1e-3) / (VF.local_std(nir0, 15) + 1e-3)))
    else:
        F.add("r2_nirtex_ratio", nan)
    hm = None
    if S.lidar2 and np.isfinite(S.lidar2.get("hag_max", np.array([np.nan]))).mean() > 0.5:
        hm = S.lidar2["hag_max"]
    elif S.layers.get("hag") is not None and np.isfinite(S.layers["hag"]).mean() > 0.6:
        hm = S.layers["hag"]
    if hm is not None:
        lv = ((hm >= 0.2) & (hm <= 1.5)).astype(np.float32)
        cov = np.isfinite(hm)
        F.add("r2_lowveg3", np.where(cov, ndimage.uniform_filter(lv, 3), np.nan))
        F.add("r2_lowveg7", np.where(cov, ndimage.uniform_filter(lv, 7), np.nan))
    else:
        F.add("r2_lowveg3", nan)
        F.add("r2_lowveg7", nan)
    Z = S.lidar2
    if Z and np.isfinite(Z.get("n_all", np.array([np.nan]))).mean() > 0.5:
        tot = ndimage.uniform_filter(np.nan_to_num(Z["n_all"]), 7)
        F.add("r2_lowfrac7", np.where(tot > 0.2, ndimage.uniform_filter(np.nan_to_num(Z["n_low"]), 7) /
                                      np.maximum(tot, 1e-3), np.nan))
    else:
        F.add("r2_lowfrac7", nan)
    if ys:
        x = ndimage.gaussian_filter(nir0, 0.7)
        gy, gx = np.gradient(x)
        for nm, s in (("r2_coh2", 2.0), ("r2_coh5", 5.0)):
            jxx = ndimage.gaussian_filter(gx * gx, s)
            jyy = ndimage.gaussian_filter(gy * gy, s)
            jxy = ndimage.gaussian_filter(gx * gy, s)
            lam = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2)
            F.add(nm, lam / (jxx + jyy + 1e-6))
        gm = np.hypot(*np.gradient(ndimage.gaussian_filter(nir0, 1.5)))
        F.add("r2_grad3", VF.robust_norm(ndimage.uniform_filter(gm, 3), ref))
        thr = np.percentile(gm[S.H // 10:-S.H // 10 or None, S.W // 10:-S.W // 10 or None], 92)
        edge = gm > thr
        F.add("r2_d_edge", np.minimum(ndimage.distance_transform_edt(~edge) * S.res, 40.0) if edge.any()
              else np.full((S.H, S.W), 40.0, np.float32))
    else:
        for n in ("r2_coh2", "r2_coh5", "r2_grad3", "r2_d_edge"):
            F.add(n, nan)
    nat = M.get("native", np.zeros((S.H, S.W), bool))
    F.add("r2_osm_native_in", nat.astype(np.float32))
    F.add("r2_d_osm_native", np.minimum(ndimage.distance_transform_edt(~nat) * S.res, 60.0) if nat.any()
          else np.full((S.H, S.W), 60.0, np.float32))
    F.add("r2_osm_rough_in", M.get("rough", np.zeros((S.H, S.W), bool)).astype(np.float32))
    return D


def prepare(vslug):
    import v2_model as VM
    D = VM.prepare(vslug)
    if REV >= 2:
        add_rev2_features(D)
    return D


def corridor_only(H, c=TRAIN_CORRIDOR):
    """rev 2: keep only the training cells inside the hand map's landing corridors (145-440 yds off the tee)."""
    import v2_labels as LB
    for x in H:
        tm = LB.train_mask(x["cls"])
        rr, cc = np.nonzero(tm)
        keep = (x["along"][rr, cc] >= c["a0"]) & (x["along"][rr, cc] <= c["a1"]) & (np.abs(x["lat"][rr, cc]) <= c["lat"])
        assert len(keep) == len(x["tidx"])
        x["tidx"], x["tcls"] = x["tidx"][keep], x["tcls"][keep]
    return H


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def lid(s):
    """Layer id (no gate: the gate only switches a course's layer to off)."""
    return f"t{s['thr']}_{s['mode']}_d{s['dmin']}"


def sid(s):
    return "off" if s is None else f"{lid(s)}_g{s['gate']}"


def layer_settings():
    return [dict(thr=t, mode=m, dmin=d) for t in GRID["thr"] for m in GRID["mode"] for d in GRID["dmin"]]


def settings():
    return [None] + [dict(s, gate=g) for s in layer_settings() for g in GRID["gate"]]


def parse_sid(k):
    if k == "off":
        return None
    t, m, d, g = k.split("_")
    return dict(thr=float(t[1:]), mode=m, dmin=int(d[1:]), gate=float(g[1:]))


# =========================================================================== labels
def install_truth_labels():
    """v2_labels.load_holes for the truth courses' hand-checked corridor maps (course_data/truth/<slug>)."""
    import v2_labels as LB
    orig = LB.load_holes

    def load_holes(slug):
        out = orig(slug)
        if out:
            return out
        p = os.path.join(CD, "truth", COURSES.get(slug, slug), "hand_zones_ll.json")
        if not os.path.exists(p):
            return []
        d = json.load(open(p))
        for k, h in d["holes"].items():
            if not h.get("footprint_ll") or not h.get("tee_ll") or not h.get("dot270_ll"):
                continue
            out.append(dict(key=str(k), ref=str(h.get("ref") or LB._ref(k)),
                            zones=[(z["lie"], z["poly_ll"]) for z in h["zones"]], footprint_ll=h["footprint_ll"],
                            tee_ll=h["tee_ll"], dot270_ll=h["dot270_ll"], src=os.path.relpath(p, ROOT)))
        return out
    LB.load_holes = load_holes
    return LB


def model_meta():
    return json.load(open(os.path.join(HERE, "model_v2", "model.json")))


# =========================================================================== samples / model
def stage_samples(vslug, out):
    import v2_model as VM
    install_truth_labels()
    names = feature_names()
    D = prepare(vslug)
    H = VM.hole_data(D)
    if REV >= 2:
        H = corridor_only(H)
    idx, y = VM.task_xy(H, "native")
    idx, y = VM.balanced(idx, y)
    X = D["F"].matrix(idx, names).astype(np.float32)
    os.makedirs(out, exist_ok=True)
    np.savez_compressed(os.path.join(out, f"samples_{vslug}.npz"), X=X, y=y.astype(np.int8), names=np.array(names))
    info = dict(slug=vslug, holes=len(H), pos=int(y.sum()), neg=int((y == 0).sum()))
    json.dump(info, open(os.path.join(out, f"samples_{vslug}.json"), "w"))
    log(f"[{vslug}] samples: {info}")


def load_samples(d, exclude=()):
    Xs, ys, used = [], [], []
    for p in sorted(glob.glob(os.path.join(d, "samples_*.npz"))):
        v = os.path.basename(p)[8:-4]
        if v in exclude:
            continue
        z = np.load(p)
        if len(z["y"]) == 0:
            continue
        Xs.append(z["X"])
        ys.append(z["y"])
        used.append(v)
    return np.concatenate(Xs), np.concatenate(ys), used


def fit_on(d, exclude=()):
    import v2_model as VM
    X, y, used = load_samples(d, exclude)
    clf = VM.make_clf()
    clf.fit(X, y)
    log(f"   fitted on {used}: {len(y)} cells, {int(y.sum())} native")
    return clf, used


def stage_model(samples, out):
    clf, used = fit_on(samples)
    os.makedirs(out, exist_ok=True)
    clf.booster_.save_model(os.path.join(out, "native_lgbm_7c.txt"))
    json.dump(dict(trained_on=used), open(os.path.join(out, "model_info.json"), "w"))


class _Prob:
    def __init__(self, path):
        import lightgbm as lgb
        self.b = lgb.Booster(model_file=path)

    def predict_proba(self, X):
        p = self.b.predict(X)
        return np.c_[1 - p, p]


# =========================================================================== layers
def native_for(D, p, s, trees):
    """One (thr, mode, dmin) -> (native mask, trees mask) as v2_model.infer builds them."""
    import v2_model as VM
    S, M = D["S"], D["M"]
    relaxed = s["mode"] == "relaxed"
    E = D["elig_rel"] if relaxed else D["elig"]
    el = E & D["course"] & ~D["water0"]
    if not relaxed:
        el &= ~trees
    if s["dmin"]:
        el &= ndimage.distance_transform_edt(~M["fairway"]) * S.res >= s["dmin"] * YD
    nat = VM.native_mask(p, el, s["thr"], S.res)
    return nat, (trees & ~nat if relaxed else trees)


def course_share(D, nat):
    c = D["M"]["course"] if D["M"]["course"].any() else D["course"]
    return float((nat & c).sum() / max(c.sum(), 1))


def to_fc(D, trees, nat, water, tag, p_trees=0.646):
    from shapely.geometry import mapping
    from shapely.ops import transform
    S = D["S"]
    S.ll_to_rc([[0, 0]])
    feats = []
    for lie, m, src in (("recovery", trees, "vision2:lidar_canopy_hag>2.5m_buffer-1m"),
                        ("native", nat, "vision2:lgbm_naip_multiyear+lidar(7 hand maps)")):
        for g in L.mask_to_polys(S, m, min_yd2=150, simplify_yd=2.0):
            gm = transform(lambda x, y: S._fwd.transform(x, y), g)
            feats.append(dict(type="Feature", geometry=mapping(g), properties=dict(
                lie=lie, src=src, p=p_trees if lie == "recovery" else 0.6, area_yd2=round(gm.area / YD ** 2),
                model="vision_any/2")))
    return dict(type="FeatureCollection", features=feats + water,
                properties=dict(schema="vision_any/2", model_id=f"vision_any/2 longgrass-cv {tag}", setting=tag))


def corridor_iou(H, nat):
    """Pooled native IoU / precision / recall inside the hand map's landing corridors."""
    import v2_labels as LB
    tp = fp = fn = 0
    for x in H:
        pr = nat[x["sl"]][x["corr"]]
        tr = (x["cls"] == LB.CI["native"])[x["corr"]]
        tp += int((pr & tr).sum())
        fp += int((pr & ~tr).sum())
        fn += int((~pr & tr).sum())
    return dict(iou=tp / max(tp + fp + fn, 1), prec=tp / max(tp + fp, 1), rec=tp / max(tp + fn, 1), truth_m2=tp + fn)


def stage_layers(vslug, samples, model_dir, out):
    import v2_model as VM
    install_truth_labels()
    meta = model_meta()
    names, tb = feature_names(), meta["settings"]["trees"]
    D = prepare(vslug)
    S = D["S"]
    H = VM.hole_data(D) if vslug in COURSES else []
    region = D["elig_rel"] & D["course"]
    P = {}
    if vslug in COURSES:
        clf, used = fit_on(samples, exclude=(vslug,))
        P["loco"] = (clf, used)
    P["full"] = (_Prob(os.path.join(model_dir, "native_lgbm_7c.txt")),
                 json.load(open(os.path.join(model_dir, "model_info.json")))["trained_on"])
    trees = VM.tree_rule(D["canopy"][tb["hag"]], tb["k_m"], tb["min_area_m2"], S.res)
    cur = json.load(open(os.path.join(HERE, vslug, "vision_any.geojson")))
    water = [f for f in cur["features"] if f["properties"]["lie"] == "water"]
    info = dict(slug=vslug, trees=dict(tb), layers={})
    for psrc, (clf, used) in P.items():
        p = VM.predict_grid(D, clf, names, region)
        p = np.where(np.isfinite(p), p, 0).astype(np.float32)
        d = os.path.join(out, psrc, vslug)
        os.makedirs(d, exist_ok=True)
        json.dump(to_fc(D, trees, np.zeros_like(trees), water, "off"), open(os.path.join(d, "off.geojson"), "w"),
                  separators=(",", ":"))
        seen = {}
        li = {"off": dict(share=0.0, same_as="off", **(corridor_iou(H, np.zeros_like(trees)) if H else {}))}
        for s in layer_settings():
            nat, tr = native_for(D, p, s, trees)
            h = hashlib.sha1(np.packbits(nat).tobytes() + np.packbits(tr).tobytes()).hexdigest()
            k = lid(s)
            ent = dict(share=course_share(D, nat), native_m2=float(nat.sum() * S.res ** 2))
            if H:
                ent.update(corridor_iou(H, nat))
            if not nat.any():
                ent["same_as"] = "off"
            elif h in seen:
                ent["same_as"] = seen[h]
            else:
                seen[h] = k
                ent["same_as"] = k
                json.dump(to_fc(D, tr, nat, water, k), open(os.path.join(d, k + ".geojson"), "w"),
                          separators=(",", ":"))
            li[k] = ent
        info["layers"][psrc] = dict(trained_on=used, layers=li)
        log(f"[{vslug}] {psrc}: {len(seen)} distinct long-grass layers; share at thr 0.5 strict d0 "
            f"{li['t0.5_strict_d0']['share']:.3f}")
    json.dump(info, open(os.path.join(out, f"info_{vslug}.json"), "w"), indent=1, default=float)


# =========================================================================== score
def sb_setup():
    import v2_calibrate as C
    SB = C.scoreboard()
    import package                                           # noqa: F401  course_data/product/package.py first
    # (rebuild_package's OB step puts course_data/platform on sys.path, which has its own package.py)
    have = {c["slug"] for c in SB.COURSES}
    SB.COURSES += [c for c in EXTRA_SB if c["slug"] not in have]
    return C, SB


def stage_score(d, rows_path, shard=0, nshards=1, psrc="loco", only_courses=None):
    C, _ = sb_setup()
    rows = json.load(open(rows_path)) if os.path.exists(rows_path) else []
    done = {(r["layer"], r["course"]) for r in rows}
    jobs = []
    for v, pslug in COURSES.items():
        if only_courses and v not in only_courses:
            continue
        for p in sorted(glob.glob(os.path.join(d, psrc, v, "*.geojson"))):
            jobs.append((os.path.basename(p)[:-8], v, pslug, p))
    jobs.sort(key=lambda j: (j[0] != "off", j[0], j[1]))
    for j, (k, v, pslug, p) in enumerate(jobs):
        if j % nshards != shard or (k, pslug) in done:
            continue
        t0 = time.time()
        try:
            rr = C.score_package(pslug, C.rebuild_package(pslug, json.load(open(p))))
        except Exception as e:                                  # noqa: BLE001
            log(f"   {k} {pslug} failed: {type(e).__name__} {e}")
            continue
        for r in rr:
            r.update(layer=k, course=pslug, psrc=psrc)
        rows += rr
        json.dump(rows, open(rows_path, "w"), default=float)
        log(f"   {k:>20} {pslug:>16}: same {sum(bool(r.get('same')) for r in rr)}/"
            f"{sum(1 for r in rr if r.get('truth'))} ({time.time() - t0:.0f}s)")
    json.dump(rows, open(rows_path, "w"), default=float)


# =========================================================================== report
def club_rank(c):
    return CLUB_ORDER.index(c) if c in CLUB_ORDER else len(CLUB_ORDER)


def score_rows(rows):
    sc = [r for r in rows if r.get("truth")]
    miss = [r for r in sc if not r["same"]]
    rg = [r["regret"] for r in sc if r.get("regret") is not None]
    return dict(same=sum(bool(r["same"]) for r in sc), n=len(sc), same_or_tie=sum(bool(r["same_or_tie"]) for r in sc),
                sum_regret=float(np.sum(rg)) if rg else 0.0, regret=float(np.mean(rg)) if rg else None,
                shorter=sum(club_rank(r["pick"]) > club_rank(r["truth"]) for r in miss),
                longer=sum(club_rank(r["pick"]) < club_rank(r["truth"]) for r in miss))


KEYS = ("same", "n", "same_or_tie", "sum_regret", "shorter", "longer")
ZERO = dict(same=0, n=0, same_or_tie=0, sum_regret=0.0, shorter=0, longer=0, regret=None)


def add(a, b):
    out = {k: a[k] + b[k] for k in KEYS}
    out["regret"] = out["sum_regret"] / max(out["n"], 1)
    return out


def total(T, k, cs):
    s = dict(ZERO)
    for c in cs:
        s = add(s, T[k][c])
    return s


def objective(s, ident):
    return (s["same"], -round(s["sum_regret"], 6), ident == PRODUCT)


def resolve(info, v, s, psrc="loco"):
    """Setting -> the layer file actually used on course v (gate / empty / duplicate -> another layer)."""
    if s is None:
        return "off"
    e = info[v]["layers"][psrc]["layers"][lid(s)]
    if e["share"] < s["gate"]:
        return "off"
    return e["same_as"]


def stage_report(pattern, d, out_md, out_json, psrc="loco"):
    rows = []
    for f in sorted(glob.glob(pattern)):
        rows += json.load(open(f))
    seen = {}
    for r in rows:
        if r.get("psrc", "loco") == psrc:
            seen[(r["layer"], r["course"], str(r["hole"]))] = r
    by = {}
    for r in seen.values():
        by.setdefault((r["course"], r["layer"]), []).append(r)
    info = {v: json.load(open(os.path.join(d, f"info_{v}.json"))) for v in COURSES
            if os.path.exists(os.path.join(d, f"info_{v}.json"))}
    courses = [p for v, p in COURSES.items() if v in info and (p, "off") in by]
    v_of = {p: v for v, p in COURSES.items()}
    T, used = {}, {}
    for s in settings():
        k, row, ok = sid(s), {}, True
        for c in courses:
            ly = resolve(info, v_of[c], s, psrc)
            if (c, ly) not in by:
                ok = False
                break
            row[c] = score_rows(by[(c, ly)])
            used.setdefault(k, {})[c] = ly
        if ok:
            T[k] = row
            row["all"] = total(T, k, courses)
    cand = list(T)
    loco, cv = {}, dict(ZERO)
    for test in courses:
        train = [c for c in courses if c != test]
        best = max(cand, key=lambda k: objective(total(T, k, train), k))
        loco[test] = dict(chosen=best, train=total(T, best, train), test=T[best][test], product=T[PRODUCT][test],
                          layer=used[best][test])
        cv = add(cv, T[best][test])
    full = max(cand, key=lambda k: objective(T[k]["all"], k))
    base = T[PRODUCT]
    ok = cv["same"] > base["all"]["same"]
    why = [f"cross-validated {cv['same']}/{cv['n']} vs product (no long grass) {base['all']['same']}/{base['all']['n']}"]
    worse = []
    for c in courses:
        a_, b_, f_ = loco[c]["test"]["same"], base[c]["same"], T[full][c]["same"]
        if a_ < b_ - 1 or f_ < b_ - 1:
            worse.append(f"{NAMES[c]} CV {a_} / chosen-on-all {f_} vs product {b_}")
    ok &= not worse
    why.append("no course worse by more than one hole" if not worse else "worse by > 1: " + "; ".join(worse))
    res = dict(courses=courses, settings=T, layers_used=used, loco=loco, cv=cv, chosen_on_all=full, product=PRODUCT,
               adopt=bool(ok and full != PRODUCT), why=why, grid=GRID,
               info={v: {"samples": i["layers"][psrc].get("trained_on"),
                         "layers": {k: e for k, e in i["layers"][psrc]["layers"].items()}} for v, i in info.items()})
    json.dump(res, open(out_json, "w"), indent=1, default=float)
    write_md(res, out_md, d)
    return res


def write_md(res, path, d=None):
    C, T = res["courses"], res["settings"]

    def cell(v):
        return f"{v['same']}/{v['n']}"

    def sl(v):
        return f"{v['shorter']} / {v['longer']}"
    b, cv = T[res["product"]]["all"], res["cv"]
    nC = len(C)
    rev2 = (" Rev 2: corridor-focused classifier, trained only on the hand maps' landing-corridor cells 145-440 yds "
            "off the tee, with seasonal NAIP contrast, NIR texture, lidar 0.2-1.5 m height share, mowing-pattern edges "
            "and OSM grassland / heath / rough polygons added (`add_rev2_features`).") if REV >= 2 else ""
    Lm = [f"# Long grass on the automatic map (rev {REV}): leave-one-course-out over the {nC} truth courses", "",
          "Generated by `course_data/vision_any/v2_longgrass_cv.py` (workflow `.github/workflows/longgrass_cv.yml`). "
          "Classifier: the v2 long-grass LightGBM (multi-year NAIP RGB + NIR, texture, lidar height / low-return "
          "fractions / roughness, terrain, OSM turf distances) trained for each test course on the hand maps of the other "
          f"{nC - 1}.{rev2} Each setting: the committed package with its vision zones replaced (trees = the product's line, lidar "
          "canopy eroded 1 m; water as committed), OB re-inferred, product quick decision (n = 8000) per tee shot vs the "
          "hand truth (scoreboard rows; Eagle Knoll and Gateway through the same hand-map scorer, Back tees). "
          "Setting ids: `t<P(native) threshold>_<strict|relaxed>_d<min yds from OSM fairway>_g<course share gate>`; "
          "`off` = no long grass (the product).", "",
          "## Cross-validation (leave one course out)", "",
          f"| test course | setting chosen on the other {nC - 1} | train same | test same (layer used) | product (off) on test |",
          "|---|---|---|---|---|"]
    for c, v in res["loco"].items():
        Lm.append(f"| {NAMES[c]} | `{v['chosen']}` | {cell(v['train'])} | {cell(v['test'])} (`{v['layer']}`) | "
                  f"{cell(v['product'])} |")
    Lm += ["", "| | same club | mean regret | misses shorter / longer |", "|---|---|---|---|",
           f"| before: product, no long grass | {cell(b)} | {b['regret']:.4f} | {sl(b)} |",
           f"| after: cross-validated | {cell(cv)} | {cv['regret']:.4f} | {sl(cv)} |",
           f"| chosen on all {nC} `{res['chosen_on_all']}` (in sample) | {cell(T[res['chosen_on_all']]['all'])} | "
           f"{T[res['chosen_on_all']]['all']['regret']:.4f} | {sl(T[res['chosen_on_all']]['all'])} |", "",
           "Per course, before -> after (cross-validated): " + ", ".join(
               f"{NAMES[c]} {T[res['product']][c]['same']} -> {res['loco'][c]['test']['same']}" for c in C) + ".", "",
           f"Adopt: **{'yes' if res['adopt'] else 'no'}** (" + "; ".join(res["why"]) + ").", ""]
    Lm += ["## Long grass per course (out-of-fold model)", "",
           "Share = long grass / OSM course outline; corridor IoU / precision / recall vs the hand map's native inside "
           "the landing corridors (190-335 yds).", "",
           "| course | hand native in corridors m2 | t0.5_strict_d0 share | IoU / prec / rec | t0.7_strict_d20 share | IoU / prec / rec |",
           "|---|---|---|---|---|---|"]
    vof = {p: v for v, p in COURSES.items()}
    for c in C:
        ly = res["info"].get(vof[c], {}).get("layers", {})
        a, z = ly.get("t0.5_strict_d0", {}), ly.get("t0.7_strict_d20", {})

        def ipr(e):
            return f"{e.get('iou', 0):.2f} / {e.get('prec', 0):.2f} / {e.get('rec', 0):.2f}" if e else "-"
        Lm.append(f"| {NAMES[c]} | {a.get('truth_m2', 0):.0f} | {a.get('share', 0):.3f} | {ipr(a)} | "
                  f"{z.get('share', 0):.3f} | {ipr(z)} |")
    Lm += ["", f"## Settings (top 40 by same club over all {nC}, then regret; every row in the .json)", "",
           "| setting | " + " | ".join(NAMES[c] for c in C) + " | all | mean regret | shorter / longer |",
           "|---|" + "---|" * len(C) + "---|---|---|"]
    order = sorted(T.items(), key=lambda kv: (-kv[1]["all"]["same"], kv[1]["all"]["sum_regret"]))
    shown = order[:40] + ([kv for kv in order[40:] if kv[0] == res["product"]])
    for k, v in shown:
        a = v["all"]
        Lm.append(f"| `{k}`{' (product)' if k == res['product'] else ''} | " + " | ".join(cell(v[c]) for c in C) +
                  f" | {cell(a)} | {a['regret']:.4f} | {sl(a)} |")
    open(path, "w").write("\n".join(Lm) + "\n")


# =========================================================================== integrate / rescore
def stage_integrate(d, model_dir, res_json):
    """Adopt the chosen-on-all setting: the seven-course model + settings in model_v2/model.json, native + trees
    zones of every course's vision_any.geojson from the all-course model's layer, packages rebuilt (OB re-inferred)."""
    import shutil
    import v2_calibrate as C
    R = json.load(open(res_json))
    if not R.get("adopt"):
        log("adoption rule failed: nothing integrated: " + "; ".join(R.get("why", [])))
        return False
    s = parse_sid(R["chosen_on_all"])
    mdir = os.path.join(HERE, "model_v2")
    shutil.copy(os.path.join(model_dir, "native_lgbm_7c.txt"), os.path.join(mdir, "native_lgbm_7c.txt"))
    mp = os.path.join(mdir, "model.json")
    meta = json.load(open(mp))
    old = {k: meta["settings"].get(k) for k in ("native_thr", "native_mode", "native_dmin_yd", "native_gate_share")}
    meta["settings"].update(native_thr=s["thr"], native_mode=s["mode"], native_dmin_yd=s["dmin"],
                            native_gate_share=s["gate"])
    meta["native_model_file"] = "native_lgbm_7c.txt"
    tro = json.load(open(os.path.join(model_dir, "model_info.json")))["trained_on"]
    meta["native_trained_on"] = tro
    meta["longgrass_cv"] = dict(previous=old, chosen=R["chosen_on_all"], cv=R["cv"],
                                product=R["settings"][R["product"]]["all"], why=R["why"],
                                report="course_data/vision_any/v2_longgrass_cv.md")
    json.dump(meta, open(mp, "w"), indent=1)
    log(f"model.json: native {old} -> {R['chosen_on_all']} (model {meta['native_model_file']}, trained on {tro})")
    for v in list(COURSES) + NO_TRUTH:
        ip = os.path.join(d, f"info_{v}.json")
        cp = os.path.join(HERE, v, "vision_any.geojson")
        if not os.path.exists(ip) or not os.path.exists(cp):
            log(f"[{v}] no layers / vision_any.geojson: skipped")
            continue
        info = {v: json.load(open(ip))}
        ly = resolve(info, v, s, "full")
        lf = json.load(open(os.path.join(d, "full", v, ly + ".geojson")))
        fc = json.load(open(cp))
        new = [f for f in lf["features"] if f["properties"]["lie"] in ("recovery", "native")]
        fc["features"] = new + [f for f in fc["features"] if f["properties"]["lie"] not in ("recovery", "native")]
        pr = fc.setdefault("properties", {})
        sh = info[v]["layers"]["full"]["layers"][lid(s)]["share"]
        pr["native_how"] = (f"LightGBM P(native) >= {s['thr']} ({s['mode']}, >= {s['dmin']} yds from OSM fairway, "
                            f"course share gate {s['gate']}: share {sh:.3f} -> {'on' if ly != 'off' else 'off'}) on "
                            f"multi-year NAIP + lidar, trained on the hand maps of {', '.join(tro)} "
                            "(course_data/vision_any/v2_longgrass_cv.md)")
        pr["longgrass_cv"] = R["chosen_on_all"]
        json.dump(fc, open(cp, "w"), separators=(",", ":"))
        n = sum(f["properties"]["lie"] == "native" for f in new)
        log(f"[{v}] vision_any.geojson: layer {ly}, {n} long-grass polygons")
        pslug = COURSES.get(v, v)
        pp = os.path.join(CD, "packages", pslug, "package.json")
        if os.path.exists(pp):
            pkg = C.rebuild_package(pslug, fc)
            pkg.setdefault("stages", {})["vision"] = pkg.get("stages", {}).get("vision", "") + \
                f" (long grass {R['chosen_on_all']}; zones_ll rebuilt by v2_longgrass_cv.py)"
            json.dump(pkg, open(pp, "w"))
            log(f"rebuilt {os.path.relpath(pp, ROOT)}")
    return True


def stage_rescore(md, out_json):
    """The committed (integrated) packages through the same scorer -> a section appended to the report."""
    C, SB = sb_setup()
    R = json.load(open(out_json))
    rows, per = [], {}
    for v, pslug in COURSES.items():
        pkg = json.load(open(os.path.join(CD, "packages", pslug, "package.json")))
        rr = C.score_package(pslug, pkg)
        per[pslug] = score_rows(rr)
        rows += rr
        log(f"   {pslug}: {per[pslug]['same']}/{per[pslug]['n']}")
    tot = dict(ZERO)
    for v in per.values():
        tot = add(tot, v)
    R["rescore"] = dict(per=per, all=tot)
    json.dump(R, open(out_json, "w"), indent=1, default=float)
    Lm = ["", "## Integrated packages re-scored (all-course model, same scorer)", "",
          "| course | product before (off) | integrated |", "|---|---|---|"]
    for c, v in per.items():
        b = R["settings"][R["product"]].get(c)
        Lm.append(f"| {NAMES[c]} | {b['same']}/{b['n'] if b else '-'} | {v['same']}/{v['n']} |")
    b = R["settings"][R["product"]]["all"]
    Lm.append(f"| all | {b['same']}/{b['n']} (shorter / longer {b['shorter']} / {b['longer']}) | {tot['same']}/{tot['n']} "
              f"(shorter / longer {tot['shorter']} / {tot['longer']}, mean regret {tot['regret']:.4f}) |")
    open(md, "a").write("\n".join(Lm) + "\n")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")
    a = sp.add_parser("samples")
    a.add_argument("--slug", required=True)
    a.add_argument("--out", required=True)
    a = sp.add_parser("model")
    a.add_argument("--samples", required=True)
    a.add_argument("--out", required=True)
    a = sp.add_parser("layers")
    a.add_argument("--slug", required=True)
    a.add_argument("--samples", required=True)
    a.add_argument("--model", required=True)
    a.add_argument("--out", required=True)
    a = sp.add_parser("score")
    a.add_argument("--dir", required=True)
    a.add_argument("--rows", required=True)
    a.add_argument("--shard", type=int, default=0)
    a.add_argument("--nshards", type=int, default=1)
    a.add_argument("--courses")
    a = sp.add_parser("report")
    a.add_argument("--rows", required=True)
    a.add_argument("--dir", required=True)
    a.add_argument("--md", default=os.path.join(HERE, f"v2_longgrass_cv{SUFFIX}.md"))
    a.add_argument("--json", default=os.path.join(HERE, f"v2_longgrass_cv{SUFFIX}.json"))
    a = sp.add_parser("integrate")
    a.add_argument("--dir", required=True)
    a.add_argument("--model", required=True)
    a.add_argument("--json", default=os.path.join(HERE, f"v2_longgrass_cv{SUFFIX}.json"))
    a = sp.add_parser("rescore")
    a.add_argument("--md", default=os.path.join(HERE, f"v2_longgrass_cv{SUFFIX}.md"))
    a.add_argument("--json", default=os.path.join(HERE, f"v2_longgrass_cv{SUFFIX}.json"))
    a = ap.parse_args()
    if a.cmd == "samples":
        stage_samples(a.slug, a.out)
    elif a.cmd == "model":
        stage_model(a.samples, a.out)
    elif a.cmd == "layers":
        stage_layers(a.slug, a.samples, a.model, a.out)
    elif a.cmd == "score":
        stage_score(a.dir, a.rows, a.shard, a.nshards, only_courses=a.courses.split(",") if a.courses else None)
    elif a.cmd == "report":
        stage_report(a.rows, a.dir, a.md, a.json)
        print(open(a.md).read())
    elif a.cmd == "integrate":
        ok = stage_integrate(a.dir, a.model, a.json)
        print("integrated" if ok else "not integrated")
    elif a.cmd == "rescore":
        stage_rescore(a.md, a.json)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
