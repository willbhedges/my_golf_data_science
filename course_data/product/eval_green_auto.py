"""Leave-one-course-out evaluation of green_auto.py (automatic greens) against OSM greens, and the shipped fit.

  python3 course_data/product/eval_green_auto.py extract [--root R] [--work W]   # training rows per course
  python3 course_data/product/eval_green_auto.py loco    [--work W]              # one model per held-out course
  python3 course_data/product/eval_green_auto.py eval    [--root R] [--work W]   # detect on each held-out course
  python3 course_data/product/eval_green_auto.py report  [--work W]              # -> EVAL_green_auto.md / .json
  python3 course_data/product/eval_green_auto.py fit     [--work W]              # green_auto_model/ (all courses)
  python3 course_data/product/eval_green_auto.py plan    [--root R] [--work W]   # par-3 plan effect (page planner)

Courses: every committed package with NAIP imagery and >= 9 OSM greens (Old Works has none; Spirit Hollow's
package has no imagery). The OSM greens (raw/osm.geojson golf=green, practice greens included) are only the labels
of the training courses and the truth of the held-out one: the detector reads the imagery, the DEM, the lidar HAG
and a prior point, never an OSM green. Priors per hole:
  line_end   the OSM hole line's last point, as the build would use it (on these courses mappers end the hole way
             on the green, so this prior is already close: median 1.3 yds)
  moved      the line end moved MOVE_YD (uniform, seeded per hole) in a random direction: what the estimate can be
             on a course with no greens (tier C / D: routed lines, ways ending short of / past the green)
Metrics per hole: found (a detection with score >= the threshold), centroid error (yds, detection vs the OSM green
centroid), IoU, on-green (the detected centre inside the OSM green); the baseline is the assumed 24-yd round
green at the prior. Pixel model and features: green_auto.py. Work files go to --work (default the scratchpad
directory in $GREEN_WORK, else /tmp/green_auto_work), never into the repo.
"""
from __future__ import annotations

import argparse
import copy
import glob
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path.insert(0, HERE)
import green_auto as GA  # noqa: E402

OUT_MD = os.path.join(HERE, "EVAL_green_auto.md")
OUT_JSON = os.path.join(HERE, "eval_green_auto.json")
MOVE_YD = (10.0, 25.0)
MIN_GREENS = 9
SKIP = ("spirit_hollow", "old_works")
N_POS, N_HARD, N_EASY = 300, 300, 300
HARD_M = 25.0
PARAMS = dict(objective="binary", learning_rate=0.08, num_leaves=31, min_data_in_leaf=100, feature_fraction=0.8,
              bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0, verbose=-1, num_threads=1, seed=7, max_bin=63)
ROUNDS = 200
KEEP = 0.5              # share of each course's sampled rows a fit uses (shared box: one thread per fit)
YD = GA.YD


def data_root(root=None):
    """--root, else the checkout with the most packages with imagery (a sparse worktree has few)."""
    if root:
        return root
    cands = [(len(glob.glob(os.path.join(r, "course_data", "packages", "*", "imagery", "naip_rgb.tif"))), r)
             for r in (ROOT, "/home/user/my_golf_data_science")]
    n, r = max(cands)
    if not n:
        raise SystemExit("no packages with imagery under --root")
    return r


def courses(root):
    out = []
    for p in sorted(glob.glob(os.path.join(root, "course_data", "packages", "*", "package.json"))):
        slug = os.path.basename(os.path.dirname(p))
        if slug in SKIP or "rgb" not in GA.sources(slug, root):
            continue
        try:
            pkg = json.load(open(p))
        except ValueError:
            continue
        hs = pkg.get("holes")
        if not isinstance(hs, dict):
            continue
        n = sum(1 for h in hs.values() if truth_poly(h) and h.get("hole_line_ll"))
        if n >= MIN_GREENS:
            out.append(slug)
    return out


def truth_poly(h):
    if str((h.get("provenance") or {}).get("green", "")).startswith("osm") and h.get("green_polygon_ll") and \
            len(h["green_polygon_ll"]) >= 3:
        return h["green_polygon_ll"]
    return None


def osm_greens(root, slug):
    fc = json.load(open(os.path.join(root, "course_data", "packages", slug, "raw", "osm.geojson")))
    out = []
    for f in fc.get("features", []):
        if (f.get("properties") or {}).get("golf") != "green":
            continue
        g = f["geometry"]
        if g["type"] == "Polygon":
            out.append(g["coordinates"][0])
        elif g["type"] == "MultiPolygon":
            out += [q[0] for q in g["coordinates"]]
    return out


def label_grid(co, w, rings):
    """1 on the feature grid cells inside any OSM green ring."""
    from matplotlib.path import Path
    xy = GA.grid_xy(w)
    lab = np.zeros(len(xy), bool)
    for r in rings:
        q = co.fwd([p[:2] for p in r])
        if np.abs(q.mean(0) - xy.mean(0)).max() > GA.WIN_M + 80:
            continue
        lab |= Path(q).contains_points(xy)
    k = int(math.sqrt(len(xy)))
    return lab.reshape(k, k)


def moved_prior(slug, ref, end_ll, co):
    import zlib
    rng = np.random.default_rng(zlib.crc32(f"{slug}:{ref}".encode()))
    d = rng.uniform(*MOVE_YD) * YD
    a = rng.uniform(0, 2 * np.pi)
    xy = co.fwd([end_ll])[0] + d * np.array([math.cos(a), math.sin(a)])
    return co.back([xy])[0].tolist()


# ----------------------------------------------------------------------------- extract
def extract_one(args):
    root, work, slug = args
    out = os.path.join(work, "rows", f"{slug}.npz")
    if os.path.exists(out):
        return slug, "cached"
    pkg = json.load(open(os.path.join(root, "course_data", "packages", slug, "package.json")))
    co = GA.Course(GA.sources(slug, root, pkg))
    rings = osm_greens(root, slug)
    X, y, H = [], [], []
    rng = np.random.default_rng(11)
    from scipy.ndimage import distance_transform_edt
    for ref, h in pkg["holes"].items():
        if not truth_poly(h) or not h.get("hole_line_ll"):
            continue
        e = co.fwd([h["hole_line_ll"][-1][:2]])[0]
        w = co.window(e[0], e[1])
        F = GA.features(w)
        lab = label_grid(co, w, rings)
        dist = distance_transform_edt(~lab) * GA.RES_M * GA.STEP
        f2, l2, d2 = F.reshape(-1, F.shape[-1]), lab.ravel(), dist.ravel()
        pos = np.nonzero(l2)[0]
        hard = np.nonzero(~l2 & (d2 <= HARD_M))[0]
        easy = np.nonzero(~l2 & (d2 > HARD_M))[0]
        take = np.r_[rng.choice(pos, min(N_POS, len(pos)), replace=False) if len(pos) else [],
                     rng.choice(hard, min(N_HARD, len(hard)), replace=False) if len(hard) else [],
                     rng.choice(easy, min(N_EASY, len(easy)), replace=False) if len(easy) else []].astype(int)
        X.append(f2[take])
        y.append(l2[take])
        H += [ref] * len(take)
    co.close()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    np.savez_compressed(out, X=np.concatenate(X).astype(np.float32), y=np.concatenate(y), hole=np.array(H))
    return slug, f"{len(H)} rows"


def cmd_extract(a):
    root = data_root(a.root)
    cs = courses(root)
    print(f"{len(cs)} courses: {', '.join(cs)}", flush=True)
    with Pool(a.workers) as pool:
        for slug, msg in pool.imap_unordered(extract_one, [(root, a.work, s) for s in cs]):
            print(f"  {slug}: {msg}", flush=True)


# ----------------------------------------------------------------------------- loco / fit
def load_rows(work):
    D = {}
    for f in sorted(glob.glob(os.path.join(work, "rows", "*.npz"))):
        z = np.load(f)
        D[os.path.basename(f)[:-4]] = (z["X"], z["y"])
    return D


def train(D, held=None, rounds=ROUNDS):
    import lightgbm as lgb
    Xs, ys, ws = [], [], []
    rng = np.random.default_rng(5)
    for s, (X, y) in D.items():
        if s == held:
            continue
        i = rng.choice(len(y), int(len(y) * KEEP), replace=False)
        Xs.append(X[i])
        ys.append(y[i])
        ws.append(np.full(len(i), 1.0 / len(i)))
    X, y, wt = np.concatenate(Xs), np.concatenate(ys), np.concatenate(ws)
    wt = wt / wt.mean()
    ds = lgb.Dataset(X, y.astype(int), weight=wt, feature_name=GA.FEATURES, free_raw_data=True,
                     params=dict(max_bin=PARAMS["max_bin"]))
    return lgb.train(PARAMS, ds, rounds)


def _fold(args):
    work, s = args
    p = os.path.join(work, "loco", f"{s}.txt")
    if not os.path.exists(p):
        train(load_rows(work), s).save_model(p)
    return s


def cmd_loco(a):
    D = load_rows(a.work)
    os.makedirs(os.path.join(a.work, "loco"), exist_ok=True)
    with Pool(a.workers) as pool:
        for s in pool.imap_unordered(_fold, [(a.work, s) for s in D]):
            print(f"  fold {s}", flush=True)


def cmd_fit(a):
    D = load_rows(a.work)
    b = train(D)
    os.makedirs(os.path.dirname(GA.MODEL_TXT), exist_ok=True)
    b.save_model(GA.MODEL_TXT)
    res = json.load(open(OUT_JSON)) if os.path.exists(OUT_JSON) else {}
    imp = dict(zip(GA.FEATURES, [int(v) for v in b.feature_importance("gain")]))
    meta = dict(schema="green_auto_model/1", courses=sorted(D), rows=int(sum(len(y) for _, y in D.values())),
                params=PARAMS, rounds=ROUNDS, features=GA.FEATURES, score_thr=res.get("score_thr", GA.SCORE_THR),
                gain=dict(sorted(imp.items(), key=lambda kv: -kv[1])),
                doc="LightGBM pixel model of green_auto.py fit on every evaluation course (eval_green_auto.py fit); "
                    "score_thr = the leave-one-course-out calibrated pick threshold")
    json.dump(meta, open(GA.MODEL_JSON, "w"), indent=1)
    print("->", os.path.relpath(GA.MODEL_TXT, ROOT), f"({meta['rows']} rows, {len(D)} courses)")


# ----------------------------------------------------------------------------- eval
def metrics(co, det_ring_ll, det_c_ll, truth_ll):
    from shapely.geometry import Point, Polygon
    T = Polygon(co.fwd([p[:2] for p in truth_ll])).buffer(0)
    c = co.fwd([det_c_ll])[0]
    err = math.hypot(c[0] - T.centroid.x, c[1] - T.centroid.y) / YD
    if det_ring_ll is None:
        D = Point(c).buffer(12 * YD)
    else:
        D = Polygon(co.fwd(det_ring_ll)).buffer(0)
    inter = D.intersection(T).area
    iou = inter / max(D.union(T).area, 1e-6)
    return dict(err_yd=round(err, 2), iou=round(iou, 3), on=bool(T.contains(Point(c))),
                truth_yd2=round(T.area / YD / YD), det_yd2=round(D.area / YD / YD))


def eval_one(args):
    root, work, slug = args
    out = os.path.join(work, "eval", f"{slug}.json")
    if os.path.exists(out):
        return slug, "cached"
    import lightgbm as lgb
    model = dict(booster=lgb.Booster(model_file=os.path.join(work, "loco", f"{slug}.txt")))
    pkg = json.load(open(os.path.join(root, "course_data", "packages", slug, "package.json")))
    co = GA.Course(GA.sources(slug, root, pkg))
    rows = []
    for ref, h in pkg["holes"].items():
        T = truth_poly(h)
        if not T or not h.get("hole_line_ll"):
            continue
        end = [float(v) for v in h["hole_line_ll"][-1][:2]]
        for kind, pr in (("line_end", end), ("moved", moved_prior(slug, ref, end, co))):
            base = metrics(co, None, pr, T)
            d = GA.detect_hole(co, model, pr)
            r = dict(slug=slug, hole=ref, par=h.get("par"), prior=kind, prior_ll=pr, base=base, has_hag="hag" in co.ds)
            if d is not None:
                r["det"] = dict(metrics(co, d["poly_ll"], d["green_ll"], T), score=d["score"], p=d["p"],
                                moved_yd=d["moved_yd"], poly_ll=d["poly_ll"], green_ll=d["green_ll"])
            rows.append(r)
    co.close()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(rows, open(out, "w"))
    return slug, f"{len(rows)} rows"


def cmd_eval(a):
    root = data_root(a.root)
    cs = [os.path.basename(p)[:-4] for p in sorted(glob.glob(os.path.join(a.work, "loco", "*.txt")))]
    with Pool(a.workers) as pool:
        for slug, msg in pool.imap_unordered(eval_one, [(root, a.work, s) for s in cs]):
            print(f"  {slug}: {msg}", flush=True)


# ----------------------------------------------------------------------------- report
CAP = dict(line_end=GA.MAX_MOVE_YD["osm"], moved=GA.MAX_MOVE_YD["routed"])


def summary(rows, thr, kind):
    R = [r for r in rows if r["prior"] == kind]
    n = len(R)
    used = [r for r in R if r.get("det") and r["det"]["score"] >= thr and r["det"]["moved_yd"] <= CAP[kind]]
    final = [(r["det"] if r in used else r["base"]) for r in R]
    e_det = np.array([r["det"]["err_yd"] for r in used]) if used else np.array([np.nan])
    e_base = np.array([r["base"]["err_yd"] for r in R])
    e_fin = np.array([f["err_yd"] for f in final])
    pct = lambda e, q: round(float(np.nanpercentile(e, q)), 1) if np.isfinite(e).any() else None   # noqa: E731
    return dict(prior=kind, holes=n, found=len(used), found_share=round(len(used) / max(n, 1), 3),
                on_green=round(sum(r["det"]["on"] for r in used) / max(len(used), 1), 3),
                det_err_med=pct(e_det, 50), det_err_p75=pct(e_det, 75), det_err_p90=pct(e_det, 90),
                det_le5=round(float(np.mean(e_det <= 5)), 3) if used else None,
                det_iou_med=round(float(np.median([r["det"]["iou"] for r in used])), 3) if used else None,
                base_err_med=pct(e_base, 50), base_err_p90=pct(e_base, 90), base_le5=round(float(np.mean(e_base <= 5)), 3),
                base_iou_med=round(float(np.median([r["base"]["iou"] for r in R])), 3),
                final_err_med=pct(e_fin, 50), final_err_p90=pct(e_fin, 90), final_le5=round(float(np.mean(e_fin <= 5)), 3),
                final_iou_med=round(float(np.median([f["iou"] for f in final])), 3),
                det_area_ratio_med=round(float(np.median([r["det"]["det_yd2"] / max(r["det"]["truth_yd2"], 1) for r in used])), 2)
                if used else None)


def pick_thr(rows, want=0.8):
    """Lowest score threshold whose detections (both priors pooled) have centroid error <= 5 yds for >= want."""
    det = [r["det"] for r in rows if r.get("det")]
    for t in np.round(np.arange(0.05, 0.95, 0.025), 3):
        u = [d for d in det if d["score"] >= t]
        if len(u) >= 20 and np.mean([d["err_yd"] <= 5 for d in u]) >= want:
            return float(t)
    return 0.95


def pc(v):
    return "-" if v is None else f"{100 * v:.0f} %"


def cmd_report(a):
    rows = []
    for f in sorted(glob.glob(os.path.join(a.work, "eval", "*.json"))):
        rows += json.load(open(f))
    thr = a.thr if a.thr is not None else GA.SCORE_THR
    S = {k: summary(rows, thr, k) for k in ("line_end", "moved")}
    per = {}
    for s in sorted({r["slug"] for r in rows}):
        per[s] = {k: summary([r for r in rows if r["slug"] == s], thr, k) for k in ("line_end", "moved")}
    par3 = {k: summary([r for r in rows if r["par"] == 3], thr, k) for k in ("line_end", "moved")}
    nohag = {k: summary([r for r in rows if not r["has_hag"]], thr, k) for k in ("line_end", "moved")}
    curve = []
    for t in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
        s = summary(rows, t, "moved")
        curve.append(dict(thr=t, found=s["found_share"], le5=s["det_le5"], med=s["det_err_med"], p90=s["det_err_p90"]))
    res = dict(score_thr=thr, courses=sorted(per), summary=S, par3=par3, no_lidar=nohag, per_course=per, curve=curve,
               move_yd=MOVE_YD)
    json.dump(res, open(OUT_JSON, "w"), indent=1)
    L = ["# Automatic greens (green_auto.py): leave-one-course-out vs OSM greens", "",
         f"{len(per)} courses, {S['line_end']['holes']} holes with an OSM green (the detector never reads an OSM "
         f"green: they are the labels of the other courses and this course's truth). Pick threshold {thr:.2f} and "
         f"move cap {CAP['line_end']:g} yds (line_end) / {CAP['moved']:g} yds (moved): green_auto.SCORE_THR / "
         f"MAX_MOVE_YD, read off the pooled held-out curve below (two scalars chosen on held-out results). Priors: `line_end` = the OSM hole line's end (what the build uses), `moved` = "
         f"moved {MOVE_YD[0]:g}-{MOVE_YD[1]:g} yds in a random direction (a greenless course's estimate).", "",
         "| prior | holes | found | on the green | centroid err med / p75 / p90 (yds) | <= 5 yds | IoU med | "
         "baseline 24-yd circle: err med / p90, <= 5 yds, IoU | page green (found -> detected, else circle): err med / p90, <= 5, IoU |",
         "|---|---|---|---|---|---|---|---|---|"]
    for k, s in list(S.items()) + [(f"{k} (par 3s)", v) for k, v in par3.items()] + [(f"{k} (no lidar)", v) for k, v in nohag.items()]:
        L.append(f"| {k} | {s['holes']} | {s['found']} ({100 * s['found_share']:.0f} %) | {100 * s['on_green']:.0f} % | "
                 f"{s['det_err_med']} / {s['det_err_p75']} / {s['det_err_p90']} | "
                 f"{pc(s['det_le5'])} | {s['det_iou_med']} | "
                 f"{s['base_err_med']} / {s['base_err_p90']}, {100 * s['base_le5']:.0f} %, {s['base_iou_med']} | "
                 f"{s['final_err_med']} / {s['final_err_p90']}, {100 * s['final_le5']:.0f} %, {s['final_iou_med']} |")
    L += ["", "Threshold curve (moved prior): " + "; ".join(
        f"{c['thr']:.1f}: found {100 * c['found']:.0f} %, <= 5 yds {pc(c['le5'])}, "
        f"med {c['med']}, p90 {c['p90']}" for c in curve), "",
          "## Per course (moved prior)", "", "| course | holes | found | <= 5 yds | err med | IoU med | baseline err med |",
          "|---|---|---|---|---|---|---|"]
    for s, v in per.items():
        m = v["moved"]
        L.append(f"| {s} | {m['holes']} | {m['found']} | {pc(m['det_le5'])} | "
                 f"{m['det_err_med']} | {m['det_iou_med']} | {m['base_err_med']} |")
    open(OUT_MD, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:14]))


# ----------------------------------------------------------------------------- par-3 plan effect
def par3_aims(pkg_path, refs):
    """{ref: dict(aim_ll, dist, box_ll (9x9 points), club)} from the page's par-3 plan (product/package.load ->
    PAR3 entry -> yardage_book.par3_plan, calm), for the par-3 holes asked."""
    import importlib.util
    sys.path.insert(0, os.path.join(ROOT, "mozingo"))
    import yardage_book as yb
    spec = importlib.util.spec_from_file_location("pp_green_eval", os.path.join(HERE, "package.py"))
    PP = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(PP)
    import render as R
    PP.ELEV_ALONG_LINE = False
    C = PP.load(pkg_path)
    yb.WIND_NOW = 0
    out = {}
    for k, p3 in C.par3.items():
        if str(k) not in refs:
            continue
        plan = yb.par3_plan(p3)
        fr = R.Frame.from_json(C.frames[k])
        tee, flag = np.array(p3["tee"], float), np.array(p3["flag"], float)
        v = (flag - tee) / np.linalg.norm(flag - tee)
        right = np.array([-v[1], v[0]])
        to_ll = lambda lat, dep: fr.px_to_ll(flag + (lat * right + dep * v) * PP.PPY)[0]     # noqa: E731
        (l0, l1), (d0, d1) = plan["lat"], plan["dep"]
        box = [to_ll(a, b).tolist() for a in np.linspace(l0, l1, 9) for b in np.linspace(d0, d1, 9)]
        out[str(k)] = dict(aim_ll=to_ll(*plan["aim"]).tolist(), dist=float(p3["center"] + plan["aim"][1]), box_ll=box,
                           how=(plan["how_lat"], plan["how_dep"]))
    return out


def plan_one(args):
    root, work, slug = args
    from shapely.geometry import Point, Polygon
    rows = json.load(open(os.path.join(work, "eval", f"{slug}.json")))
    thr = json.load(open(OUT_JSON))["score_thr"]
    pkg = json.load(open(os.path.join(root, "course_data", "packages", slug, "package.json")))
    p3 = {r["hole"] for r in rows if r["par"] == 3}
    if not p3:
        return slug, []
    co = GA.Course(GA.sources(slug, root, pkg))
    tmp = os.path.join(work, "plan_tmp", slug)
    os.makedirs(tmp, exist_ok=True)
    sys.path.insert(0, os.path.join(CD, "mapper"))
    import apply as AP
    PK = AP.platform_package()
    T = {ref: Polygon(co.fwd([q[:2] for q in pkg["holes"][ref]["green_polygon_ll"]])).buffer(0) for ref in p3}
    variants = {"truth": pkg}
    for kind in ("line_end", "moved"):
        for use in ("assumed", "detected"):
            v = copy.deepcopy(pkg)
            for r in rows:
                if r["prior"] != kind or r["hole"] not in p3:
                    continue
                h = v["holes"][r["hole"]]
                h["green_ll"] = r["prior_ll"]
                h["green_polygon_ll"] = h["green_polygon"] = None
                h["provenance"]["green"] = "hole_line_end"
                d = r.get("det")
                if use == "detected" and d and d["score"] >= thr and d["moved_yd"] <= CAP[kind]:
                    f = dict(type="Feature", properties=dict(op="green"),
                             geometry=dict(type="Polygon", coordinates=[d["poly_ll"] + [d["poly_ll"][0]]]))
                    AP.green_op(h, f, PK, None, src=GA.SRC)
                else:
                    for tt in h["tees"].values():
                        try:
                            tt["measured_yards"] = AP._measure(h, tt["tee_ll"][0], tt["tee_ll"][1])
                        except Exception:                          # noqa: BLE001
                            pass
                    PK.apply_tee_line(h)
            import contextlib
            import io
            with contextlib.redirect_stdout(io.StringIO()):
                variants[f"{kind}:{use}"] = PK.reframe(v)
    aims = {}
    for name, v in variants.items():
        pth = os.path.join(tmp, f"{name.replace(':', '_')}.json")
        json.dump(v, open(pth, "w"))
        aims[name] = par3_aims(pth, p3)
    out = []
    for ref in sorted(p3, key=lambda r: int(r) if r.isdigit() else 99):
        t = aims["truth"].get(ref)
        if not t:
            continue
        row = dict(slug=slug, hole=ref)
        for name in variants:
            a = aims[name].get(ref)
            if not a:
                continue
            q = co.fwd([a["aim_ll"]])[0]
            tq = co.fwd([t["aim_ll"]])[0]
            bx = co.fwd(a["box_ll"])
            row[name] = dict(aim_err_yd=round(math.hypot(*(q - tq)) / YD, 1), dist_err_yd=round(a["dist"] - t["dist"], 1),
                             aim_on_green=bool(T[ref].contains(Point(q))),
                             box_on_green=round(float(np.mean([T[ref].contains(Point(p)) for p in bx])), 2))
        out.append(row)
    co.close()
    return slug, out


def cmd_plan(a):
    root = data_root(a.root)
    cs = [os.path.basename(p)[:-5] for p in sorted(glob.glob(os.path.join(a.work, "eval", "*.json")))]
    rows = []
    with Pool(a.workers) as pool:
        for slug, r in pool.imap_unordered(plan_one, [(root, a.work, s) for s in cs]):
            rows += r
            print(f"  {slug}: {len(r)} par 3s", flush=True)
    names = ["truth", "line_end:assumed", "line_end:detected", "moved:assumed", "moved:detected"]
    S = {}
    for n in names[1:]:
        R_ = [r[n] for r in rows if n in r]
        e = np.array([x["aim_err_yd"] for x in R_])
        dd = np.abs([x["dist_err_yd"] for x in R_])
        S[n] = dict(holes=len(R_), aim_err_med=round(float(np.median(e)), 1), aim_err_p90=round(float(np.percentile(e, 90)), 1),
                    aim_le5=round(float(np.mean(e <= 5)), 3), dist_le5=round(float(np.mean(dd <= 5)), 3),
                    aim_on_green=round(float(np.mean([x["aim_on_green"] for x in R_])), 3),
                    box_on_green_med=round(float(np.median([x["box_on_green"] for x in R_])), 2),
                    box_ok=round(float(np.mean([x["box_on_green"] >= 0.6 and x["aim_on_green"] for x in R_])), 3))
    res = json.load(open(OUT_JSON))
    res["par3_plan"] = dict(summary=S, rows=rows)
    json.dump(res, open(OUT_JSON, "w"), indent=1)
    L = ["", "## Par-3 plan effect (the page's par-3 plan: product/package.load -> yardage_book.par3_plan, calm)", "",
         "Per par 3 the plan's aim point and target box on the green the variant gives, against the plan on the OSM "
         "green (the truth). `assumed` = the 24-yd round green at the prior; `detected` = the detector's green where "
         "found (score >= the threshold), else the assumed one. Hazards come from the same package zones.", "",
         "| variant | par 3s | aim err med / p90 (yds) | aim <= 5 yds | plays-as distance <= 5 yds | aim on the real green | "
         "box share on the real green (med) | box OK (centre on, >= 60 % on) |", "|---|---|---|---|---|---|---|---|"]
    for n, s in S.items():
        L.append(f"| {n} | {s['holes']} | {s['aim_err_med']} / {s['aim_err_p90']} | {100 * s['aim_le5']:.0f} % | "
                 f"{100 * s['dist_le5']:.0f} % | {100 * s['aim_on_green']:.0f} % | {s['box_on_green_med']} | {100 * s['box_ok']:.0f} % |")
    md = open(OUT_MD).read().split("\n## Par-3 plan effect")[0].rstrip("\n")
    open(OUT_MD, "w").write(md + "\n" + "\n".join(L) + "\n")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("extract", "loco", "eval", "report", "fit", "plan"))
    ap.add_argument("--root")
    ap.add_argument("--work", default=os.environ.get("GREEN_WORK", "/tmp/green_auto_work"))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--thr", type=float)
    a = ap.parse_args()
    dict(extract=cmd_extract, loco=cmd_loco, eval=cmd_eval, report=cmd_report, fit=cmd_fit, plan=cmd_plan)[a.cmd](a)


if __name__ == "__main__":
    main()
