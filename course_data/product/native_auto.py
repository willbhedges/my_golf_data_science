"""Automatic native (long, unmown) grass per hole side: no mapper agent, no golfer tap.

Why (platform/ERROR_BUDGET.md, mapper/EVAL_BLIND.md): long grass is 25 % of the wrong plans and 64 % of the regret,
and the auto build has no long-grass layer because every pixel classifier (vision_any v2 / v3, the S2 pixel layer)
put native on mown parkland rough. What moves the plan is the yes / no per side of the landing area, not the exact
edge (EVAL_BLIND round 3 follow-up: a band at the photo mowing line and the truth's 10-yd convention score the same).
So this module classifies hole SIDES, not pixels, and draws native_confirm's "yes" band on the sides it is sure of.

Per side (corridor frame of the hole, mapper/common.py: x = yds right of the tee line, 150-345 yds along), from the
cached rasters of vision_any/<slug>/raw (3DEP HAG, Meta CHM, two NAIP years with NIR) + the Sentinel-2 native P
(vision_any/s2/native_model.py: the leave-one-course-out grid for a training course, the full model otherwise) + the
package (fairway / first cut / green, trees, water, sand, OB of every hole), label-free:
  regions   F = this hole's fairway / first cut / green; N = open ground 1-6 yds off it (the mown-rough reference);
            O = open ground 10-40 yds off it (where native would catch a tee shot; O2 6-20, O3 20-50); "open" = not
            any hole's mown area, not a package hazard / tree zone, lidar HAG < 2.5 m and CHM < 3 m
  s2        mean P and share of P >= 0.5 in O / O2 / O3
  hag       share of HAG >= 0.25 m (>= 0.5 m, mean) in O minus the same in F (and minus N)
  naip      per NAIP year: 5x5 / 9x9 local std of grey and NIR (texture), NDVI, ExG, grey in O minus N (minus F);
            mean of the two years and the "both years agree" extreme
  geo       share of the side band (10-40 yds off) that is open / trees / hazards
  ctx       course-level means of the side features (is this a prairie course?) and the side's z-score within the
            course (label-free, the course's own reference)
Model: logistic regression on the standardised features (median imputation, L2 with C = 0.6 on mean-1 weights,
every course the same total weight, classes balanced). Trained and scored leave-one-course-out on the hand-truth courses by
mapper/eval_native_auto.py (labels = eval_native_confirm.truth_answers: >= 300 sq yds of truth native within 30
yds of the package fairway, 150-345 along); native_auto_model.json is the same fit on all of them, for new courses.
Decision rule: a side gets native when p >= the model's threshold (chosen on the training courses only: the lowest
t whose pooled leave-one-course-out side precision is >= PREC). The band = native_confirm.set_side (beyond 10 yds of
the fairway, 130-400 along, out to 65 yds; trees, water, sand, OB and fairway stay on top). Nothing is erased.

    import native_auto as NA
    rows = NA.side_features(slug, pkg, frames)            # frames = mapper/common.make_frames(pkg, tee_set)
    p = NA.predict(NA.load_model(), rows)                 # {ref: {"L": p, "R": p}}
    m = NA.load_model()
    if NA.course_usable(rows) and NA.course_fires(p, m["thr"]):   # S2 present + the course gate (COURSE_GATE)
        pkg2 = NA.apply_sides(pkg, frames, NA.sides_from_p(p, m["thr"]), p)
    pri = NA.confirm_priors(p)                            # priors for native_confirm.select (the <= 2 tap combo)

Course gate (COURSE_GATE): native only on a course where >= 25 % of the sides reach thr; isolated confident sides
on an otherwise mown course are drought-tan parkland rough (Ellis 2 / 7). No S2 stack -> nothing (course_usable).
Status: adopted (ENABLED); held-out plan scores in mapper/EVAL_BLIND.md "Automatic native sides" and
mapper/EVAL_native_auto.md. Product step: build_layer(slug, pkg) -> (package, info); CLI:
    python3 course_data/product/native_auto.py <slug> [--package P] [--out P]
"""
from __future__ import annotations

import copy
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
for _p in (os.path.join(CD, "mapper"), os.path.join(CD, "vision_any", "s2"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import common as M  # noqa: E402
import native_confirm as NC  # noqa: E402

MODEL_JSON = os.path.join(HERE, "native_auto_model.json")
SRC = "auto:native_side"
# Adopted 2026-11-03 behind the course gate (mapper/EVAL_BLIND.md "Automatic native sides": held out on 18 truth
# courses 167 -> 186 matches / 250 tee shots, regret 8.79 -> 4.34, no parkland control broken). build_layer reads it;
# the package build does not call build_layer yet.
ENABLED = True
COURSE_GATE = 0.25             # a course gets automatic native only when >= this share of its sides reach thr
PREC = 0.9                     # threshold rule: lowest t with pooled LOCO side precision >= PREC on the training courses
C_L2 = 0.6                     # L2 strength (weights have mean 1; = sklearn C 0.3 on weights that sum to 2n)
ALONG = (150.0, 345.0)
REACH = 65.0
TREE_HAG, TREE_CHM = 2.5, 3.0
HAZ_LIES = ("water", "sand", "bunker", "ob", "recovery", "trees")
MOWN_LIES = ("fairway", "first_cut", "green")
REGIONS = {"O": (10, 40), "N": (1, 6), "O2": (6, 20), "O3": (20, 50)}
NAIP_KEYS = ("ndvi", "gray", "tex", "ntex", "tex9", "exg")

FEATURES = [
    # s2
    "s2_O", "s2ge5_O", "s2_O2", "s2_O3",
    # hag
    "d_hag_OF", "d_hag_ON", "d_hag50_OF", "d_hagm_OF", "d_hag_O2F",
    # naip
    "d_tex_ON", "d_ntex_ON", "d_tex9_ON", "d_ndvi_ON", "d_gray_ON", "d_exg_ON", "d_tex_OF", "d_ndvi_OF",
    "m_tex_ON", "m_ndvi_ON",
    # geo
    "open_O", "tree_O", "haz_O",
    # ctx
    "c_s2ge5_O", "c_d_hag_OF", "c_d_tex_ON", "c_d_ndvi_ON", "z_s2ge5_O", "z_d_hag_OF",
]


# ----------------------------------------------------------------------------- rasters
def _read(path):
    import rasterio
    with rasterio.open(path) as r:
        return r.read(), r.transform, str(r.crs)


def _lstd(x, k):
    from scipy import ndimage
    m = ndimage.uniform_filter(x, k)
    m2 = ndimage.uniform_filter(x * x, k)
    return np.sqrt(np.maximum(m2 - m * m, 0))


def course_rasters(slug, raw_dir=None, s2=True):
    """The cached rasters of one course: {"crs", "hag": (m, affine), "chm": ..., "naip": [{year, t, <NAIP_KEYS>}],
    "s2": (P, affine)} (missing layers are left out)."""
    raw = raw_dir or os.path.join(CD, "vision_any", slug, "raw")
    out = {"naip": []}
    a, t, crs = _read(os.path.join(raw, "hag.tif"))       # uint8, 0.25 m units, 255 = no data (vision_any/fetch_any.py)
    h = a[0].astype(np.float32) * 0.25
    h[a[0] == 255] = np.nan
    out["hag"], out["crs"] = (h, t), crs
    p = os.path.join(raw, "chm_meta.tif")
    if os.path.exists(p):
        a, t, _ = _read(p)
        c = a[0].astype(np.float32)
        c[a[0] == 255] = np.nan
        out["chm"] = (c, t)
    for f in sorted(f for f in os.listdir(raw) if f.startswith("naip_") and f.endswith(".tif"))[-2:]:
        a, t, _ = _read(os.path.join(raw, f))
        a = a.astype(np.float32)
        if a.shape[0] < 4:
            continue
        r_, g_, b_, n_ = a[0], a[1], a[2], a[3]
        gray = (r_ + g_ + b_) / 3
        out["naip"].append(dict(year=f[5:9], t=t, ndvi=(n_ - r_) / np.maximum(n_ + r_, 1), gray=gray,
                                tex=_lstd(gray, 5), ntex=_lstd(n_, 5), tex9=_lstd(gray, 9),
                                exg=(2 * g_ - r_ - b_) / np.maximum(r_ + g_ + b_, 1)))
    if s2:
        try:
            import native_model as NM
            from affine import Affine
            g = NM.p_grid(slug)
            if g is not None:
                out["s2"] = (g["p"], Affine(*g["transform"]))
                out["s2_source"] = g["source"]
        except Exception as e:                           # noqa: BLE001  (no S2 stack / model: the S2 features are NaN)
            out["s2_error"] = f"{type(e).__name__}: {e}"
    return out


def _sample(grid, E, N):
    a, t = grid
    i = ~t
    c, r = i.a * E + i.b * N + i.c, i.d * E + i.e * N + i.f
    r, c = np.floor(r).astype(int), np.floor(c).astype(int)
    ok = (r >= 0) & (r < a.shape[0]) & (c >= 0) & (c < a.shape[1])
    return np.where(ok, a[np.where(ok, r, 0), np.where(ok, c, 0)], np.nan)


def _union(fj, pkg, lies):
    from shapely.ops import unary_union
    gs = [M._poly(z["xy"]) for h in pkg["holes"].values() for z in M.auto_zones_xy(fj, h, lies)]
    return unary_union(gs).buffer(0) if gs else None


# ----------------------------------------------------------------------------- features
def _mean(a, m, nmin=20):
    v = a[m]
    v = v[np.isfinite(v)]
    return float(np.mean(v)) if len(v) >= nmin else float("nan")


def _median(a, m, nmin=20):
    v = a[m]
    v = v[np.isfinite(v)]
    return float(np.median(v)) if len(v) >= nmin else float("nan")


def side_features(slug, pkg, frames, rs=None, step=1.0):
    """[{slug, hole, side, <raw features>}] for every framed hole (two rows per hole)."""
    import shapely
    from pyproj import Transformer
    rs = rs or course_rasters(slug)
    tr = Transformer.from_crs("EPSG:4326", rs["crs"], always_xy=True)
    XX, YY = np.meshgrid(np.arange(-REACH, REACH + 1e-6, step), np.arange(ALONG[0], ALONG[1] + 1e-6, step))
    xy = np.c_[XX.ravel(), YY.ravel()]
    rows = []
    for ref, fj in frames.items():
        h = pkg["holes"].get(ref)
        if h is None:
            continue
        ll = M.xy_to_ll(fj, xy)
        E, N = tr.transform(ll[:, 0], ll[:, 1])
        mown = NC.mown_xy(fj, h)
        if mown is not None and not mown.is_empty:
            d = shapely.distance(mown, shapely.points(xy))
        else:                                            # no fairway mapped: a 30-yd strip along the tee line
            d = np.abs(xy[:, 0]) - 15.0
        inside = d <= 0
        allmown, haz = _union(fj, pkg, MOWN_LIES), _union(fj, pkg, HAZ_LIES)
        other = shapely.contains_xy(allmown, xy[:, 0], xy[:, 1]) if allmown is not None else np.zeros(len(xy), bool)
        inhaz = shapely.contains_xy(haz, xy[:, 0], xy[:, 1]) if haz is not None else np.zeros(len(xy), bool)
        hag = _sample(rs["hag"], E, N)
        tree = hag >= TREE_HAG
        if "chm" in rs:
            tree |= np.nan_to_num(_sample(rs["chm"], E, N)) >= TREE_CHM
        s2 = _sample(rs["s2"], E, N) if "s2" in rs else np.full(len(xy), np.nan)
        nai = [{k: _sample((nd[k], nd["t"]), E, N) for k in NAIP_KEYS} for nd in rs["naip"]]
        open_ = ~other & ~inhaz & ~tree
        fin = np.isfinite(hag)
        for side in NC.SIDES:
            sm = xy[:, 0] < 0 if side == "L" else xy[:, 0] > 0
            reg = {"F": inside & sm & ~tree}
            for k, (d0, d1) in REGIONS.items():
                reg[k] = sm & open_ & (d >= d0) & ((d < d1) if k in ("N", "O2") else (d <= d1))
            band = sm & (d >= REGIONS["O"][0]) & (d <= REGIONS["O"][1])
            nb = max(int(band.sum()), 1)
            f = dict(slug=slug, hole=str(ref), side=side, n_O=int(reg["O"].sum()), n_N=int(reg["N"].sum()),
                     n_F=int(reg["F"].sum()), open_O=float(reg["O"].sum() / nb),
                     tree_O=float((band & tree).sum() / nb), haz_O=float((band & inhaz).sum() / nb))
            for nm in ("O", "N", "F", "O2", "O3"):
                m = reg[nm]
                f[f"hag_ge25_{nm}"] = _mean(np.where(fin, (hag >= 0.25).astype(float), np.nan), m)
                f[f"hag_ge50_{nm}"] = _mean(np.where(fin, (hag >= 0.5).astype(float), np.nan), m)
                f[f"hag_mean_{nm}"] = _mean(np.clip(hag, 0, 2.5), m)
                f[f"s2_{nm}"] = _mean(s2, m)
                f[f"s2ge5_{nm}"] = _mean(np.where(np.isfinite(s2), (s2 >= 0.5).astype(float), np.nan), m)
                for i, nd in enumerate(nai):
                    for k in NAIP_KEYS:
                        f[f"y{i}_{k}_{nm}"] = _median(nd[k], m)
            rows.append(f)
    return rows


def _num(v):
    return float("nan") if v is None else float(v)


def derive(rows):
    """Adds the relative (O vs F / N, two NAIP years) and course-context features to rows (in place) -> rows."""
    import warnings
    by = {}
    for r in rows:
        by.setdefault(r["slug"], []).append(r)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for rs in by.values():
            for r in rs:
                g = lambda k: _num(r.get(k))            # noqa: E731
                r["d_hag_OF"] = g("hag_ge25_O") - g("hag_ge25_F")
                r["d_hag_ON"] = g("hag_ge25_O") - g("hag_ge25_N")
                r["d_hag50_OF"] = g("hag_ge50_O") - g("hag_ge50_F")
                r["d_hagm_OF"] = g("hag_mean_O") - g("hag_mean_F")
                r["d_hag_O2F"] = g("hag_ge25_O2") - g("hag_ge25_F")
                for k in NAIP_KEYS:
                    vn = np.array([g(f"y{i}_{k}_O") - g(f"y{i}_{k}_N") for i in (0, 1)])
                    vf = np.array([g(f"y{i}_{k}_O") - g(f"y{i}_{k}_F") for i in (0, 1)])
                    has_n, has_f = np.isfinite(vn).any(), np.isfinite(vf).any()
                    r[f"d_{k}_ON"] = float(np.nanmean(vn)) if has_n else float("nan")
                    r[f"d_{k}_OF"] = float(np.nanmean(vf)) if has_f else float("nan")
                    r[f"m_{k}_ON"] = (float(np.nanmin(vn) if k in ("tex", "ntex", "tex9") else np.nanmax(vn))
                                      if has_n else float("nan"))
            for k in ("s2ge5_O", "d_hag_OF", "d_tex_ON", "d_ndvi_ON"):
                v = np.array([_num(r.get(k)) for r in rs], float)
                fin = np.isfinite(v)
                mu = float(np.nanmean(v)) if fin.any() else float("nan")
                sd = float(np.nanstd(v)) if fin.sum() > 2 else float("nan")
                for r in rs:
                    r[f"c_{k}"] = mu
                    x = _num(r.get(k))
                    r[f"z_{k}"] = (x - mu) / sd if np.isfinite(sd) and sd > 1e-6 and np.isfinite(x) else 0.0
    return rows


def matrix(rows, names=FEATURES):
    return np.array([[_num(r.get(n)) for n in names] for r in rows], float)


# ----------------------------------------------------------------------------- model (numpy logistic regression)
def balanced_weights(slugs, y):
    """Every course the same total weight, then the two classes the same total weight (mean weight 1)."""
    slugs, y = np.asarray(slugs), np.asarray(y, float)
    w = np.ones(len(y))
    for c in set(slugs.tolist()):
        w[slugs == c] = 1.0 / (slugs == c).sum()
    pos, neg = (w * y).sum(), (w * (1 - y)).sum()
    if pos > 0 and neg > 0:
        w = np.where(y == 1, w / pos, w / neg)
    return w * len(w) / w.sum()


def _lr(Z, y, w, C, iters=100):
    """min 0.5 |beta|^2 + C sum w_i logloss_i (intercept not penalised), Newton steps (sklearn's objective)."""
    n, k = Z.shape
    A = np.c_[Z, np.ones(n)]
    b = np.zeros(k + 1)
    R = np.eye(k + 1)
    R[-1, -1] = 0.0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(A @ b, -35, 35)))
        g = C * A.T @ (w * (p - y)) + R @ b
        H = C * (A * (w * p * (1 - p))[:, None]).T @ A + R + 1e-9 * np.eye(k + 1)
        step = np.linalg.solve(H, g)
        b -= step
        if np.abs(step).max() < 1e-10:
            break
    return b[:-1], float(b[-1])


def fit(rows, y, slugs=None, names=FEATURES, C=C_L2):
    X = matrix(rows, names)
    y = np.asarray(y, float)
    w = balanced_weights(slugs if slugs is not None else [r["slug"] for r in rows], y)
    med = np.nanmedian(np.where(np.isfinite(X), X, np.nan), 0) if len(X) else np.zeros(len(names))
    med = np.where(np.isfinite(med), med, 0.0)
    A = np.where(np.isfinite(X), X, med)
    mu, sd = A.mean(0), A.std(0) + 1e-9
    coef, b0 = _lr((A - mu) / sd, y, w, C)
    return dict(schema="native_auto_model/1", features=list(names), median=med.tolist(), mu=mu.tolist(),
                sd=sd.tolist(), coef=coef.tolist(), intercept=b0, C=C)


def predict_rows(model, rows):
    X = matrix(rows, model["features"])
    med, mu, sd = (np.asarray(model[k]) for k in ("median", "mu", "sd"))
    A = np.where(np.isfinite(X), X, med)
    z = ((A - mu) / sd) @ np.asarray(model["coef"]) + model["intercept"]
    return 1 / (1 + np.exp(-np.clip(z, -35, 35)))


def predict(model, rows, derived=False):
    """rows from side_features (one course) -> {ref: {"L": p, "R": p}}."""
    rows = rows if derived else derive([dict(r) for r in rows])
    out = {}
    for r, p in zip(rows, predict_rows(model, rows)):
        out.setdefault(str(r["hole"]), {})[r["side"]] = round(float(p), 4)
    return out


def loco(rows, y, names=FEATURES, C=C_L2):
    """Leave-one-course-out p (each course predicted by the fit on the others)."""
    s = np.array([r["slug"] for r in rows])
    y = np.asarray(y, float)
    p = np.zeros(len(rows))
    for c in sorted(set(s.tolist())):
        tr = s != c
        m = fit([r for r, t in zip(rows, tr) if t], y[tr], s[tr], names, C)
        p[~tr] = predict_rows(m, [r for r, t in zip(rows, tr) if not t])
    return p


def pick_threshold(p, y, prec=PREC, grid=None):
    """The lowest t whose pooled side precision (p >= t) is >= prec (the top of the grid when none)."""
    grid = np.round(np.arange(0.3, 0.96, 0.025), 3) if grid is None else grid
    p, y = np.asarray(p), np.asarray(y)
    for t in grid:
        sel = p >= t
        if sel.sum() and y[sel].mean() >= prec:
            return float(t)
    return float(grid[-1])


def load_model(path=MODEL_JSON):
    return json.load(open(path)) if os.path.exists(path) else None


# ----------------------------------------------------------------------------- map
def course_share(p, thr):
    """Share of the course's framed hole sides with p >= thr."""
    v = [float(x.get(s) or 0.0) for x in p.values() for s in NC.SIDES]
    return float(np.mean([x >= thr for x in v])) if v else 0.0


def course_usable(rows):
    """The classifier needs the S2 native P (its strongest input, s2_longgrass.md): a course with no S2 stack, or
    with S2 on fewer than half of its sides, gets no automatic native (the other features alone were not scored)."""
    v = [r.get("s2_O") for r in rows]
    return bool(v) and float(np.mean([x is not None and np.isfinite(x) for x in v])) >= 0.5


def course_fires(p, thr, gate=COURSE_GATE):
    """The course gate: isolated confident sides on a course that otherwise looks mown (Ellis 2 / 7: drought-tan
    parkland rough, 2 of 28 sides) are not trusted; a native / prairie course fires on most of its sides."""
    return course_share(p, thr) >= gate


def sides_from_p(p, thr):
    """{ref: {"L": p, "R": p}} -> {ref: ["L", "R"] sides with p >= thr}."""
    return {r: [s for s in NC.SIDES if (v.get(s) or 0.0) >= thr] for r, v in p.items()}


def apply_sides(pkg, frames, sides, p=None):
    """Native band (native_confirm.set_side, beyond 10 yds of the fairway) on each listed side -> new package (input
    untouched). Nothing is erased; zones carry src SRC and the side's p."""
    out = copy.deepcopy(pkg)
    for ref, ss in sides.items():
        if ref not in out["holes"] or ref not in frames or not ss:
            continue
        h = out["holes"][ref]
        n0 = len(h.get("zones_ll") or [])
        for s in ss:
            NC.set_side(h, frames[ref], s, True, None, tag="auto")
        for z in h["zones_ll"][n0:]:
            z.update(src=SRC, verified="auto", p=(p or {}).get(ref, {}).get(z.get("side"), z.get("p")))
        h.setdefault("verification", {})["native_auto"] = dict(sides=NC.answer_of({s: s in ss for s in NC.SIDES}),
                                                               p=(p or {}).get(ref))
    return out


def confirm_priors(p, lo=0.03, hi=0.97):
    """Classifier p -> native_confirm.select priors {ref: {side: {p, w}}} (w None = the map's own rough width)."""
    return {r: {s: dict(p=float(min(hi, max(lo, v.get(s) or 0.0))), w=None) for s in NC.SIDES} for r, v in p.items()}


# ----------------------------------------------------------------------------- product step
def build_layer(slug, pkg, frames=None, model=None, rs=None, force=False):
    """The zero-tap step for one course -> (package, info). Adds the native band on the sides the classifier is
    sure of when ENABLED (or force), the course has an S2 stack (course_usable) and the course gate fires; else
    the package comes back unchanged and info["why"] says why. info["p"] = per side p (the confirm-tap priors)."""
    model = model or load_model()
    info = dict(src=SRC, enabled=ENABLED or force)
    if model is None:
        return pkg, dict(info, why="no native_auto_model.json")
    if frames is None:
        frames = M.make_frames(pkg, M.tee_set_of(pkg))
    try:
        rows = side_features(slug, pkg, frames, rs=rs)
    except Exception as e:                               # noqa: BLE001  (no vision_any/<slug>/raw rasters)
        return pkg, dict(info, why=f"no features: {type(e).__name__}: {e}"[:200])
    p = predict(model, rows)
    info.update(p=p, thr=model["thr"], share=round(course_share(p, model["thr"]), 3), usable=course_usable(rows))
    if not info["usable"]:
        return pkg, dict(info, why="no S2 native P for this course (vision_any/s2/<slug>/s2_stack.npz)")
    if not course_fires(p, model["thr"]):
        return pkg, dict(info, why=f"course gate shut: {info['share']:.0%} of sides >= {model['thr']} (< {COURSE_GATE:.0%})")
    sides = sides_from_p(p, model["thr"])
    info["sides"] = {r: NC.answer_of({s: s in v for s in NC.SIDES}) for r, v in sides.items() if v}
    if not info["enabled"]:
        return pkg, dict(info, why="ENABLED is False (dry run: info['sides'] is what it would add)")
    out = apply_sides(pkg, frames, sides, p)
    out.setdefault("stages", {})["native_auto"] = (f"ok: {len(info['sides'])} holes, sides "
                                                   + ", ".join(f"{r} {a}" for r, a in info["sides"].items()))
    return out, dict(info, why="added")


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Automatic native sides for one course (see the module doc).")
    ap.add_argument("slug")
    ap.add_argument("--package", help="package.json (default: the committed one)")
    ap.add_argument("--out", help="write the package with the native band here (default: print only)")
    ap.add_argument("--force", action="store_true", help="apply even when ENABLED is False")
    a = ap.parse_args(argv)
    pkg = M.rj(a.package or M.committed_package_path(a.slug))
    out, info = build_layer(a.slug, pkg, force=a.force)
    print(json.dumps({k: v for k, v in info.items() if k != "p"}, indent=1))
    if a.out and out is not pkg:
        M.wj(a.out, out)
        print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
