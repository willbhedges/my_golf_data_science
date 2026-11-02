"""Sentinel-2 seasonal features on the 10 m grid, per-course fairway reference, 1 m <-> 10 m mapping."""
import os, warnings, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
S2DIR = os.environ.get("S2DIR", os.path.join(HERE, "s2"))
COURSES = ["gateway_national", "spirit_hollow", "coldwater", "ellis", "mozingo", "eagle_knoll", "veenker",
           "pine_dunes", "hot_springs_arlington", "blue_hills", "national_kc", "annbriar", "amana_colonies",
           # 2026-11-02 enlarged set (s2_longgrass.md 'Enlarged native set'): 5 no-native truth_sets_v2 courses + 5 KS native
           "tomahawk_hills", "la_nickell", "gustin", "rivercut", "osage_national",
           "sand_creek_station", "eagle_bend", "prairie_dunes", "mariah_hills", "buffalo_dunes"]
NATIVE, ROUGH, FC = 4, 0, 1
CTX = ["c_fairway", "c_mown", "c_canopy", "c_elig", "c_dfw_min", "c_dfw_mean", "c_canopy_nb"]


def _nm(f, a, axis=0):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return f(a, axis=axis)


def load_stack(slug):
    z = np.load(os.path.join(S2DIR, slug, "s2_stack.npz"), allow_pickle=False)
    return {k: z[k] for k in z.files}


def load_g10(slug):
    z = np.load(os.path.join(HERE, f"g10_{slug}.npz"))
    return {k: z[k] for k in z.files}


def s2_features(st):
    """-> {name: (H, W) float32} seasonal features (raw, not yet relative)."""
    months = [str(m) for m in st["months"]]
    I = st["idx"].astype(np.float32); I[I == -128] = np.nan; I /= 100.0
    names = [str(n) for n in st["inames"]]
    k = {n: i for i, n in enumerate(names)}
    years = sorted({m[:4] for m in months})
    F = {}
    per = {}
    for y in years:
        def mo(ms, band):
            j = [months.index(f"{y}-{m:02d}") for m in ms if f"{y}-{m:02d}" in months]
            return I[j, k[band]] if j else np.full((1,) + I.shape[2:], np.nan, np.float32)
        nd_sp = _nm(np.nanmax, mo([4, 5], "ndvi"))
        nd_jun = _nm(np.nanmax, mo([5, 6], "ndvi"))
        nd_smin = _nm(np.nanmin, mo([7, 8, 9], "ndvi"))
        nd_smed = _nm(np.nanmedian, mo([7, 8, 9], "ndvi"))
        nd_oct = _nm(np.nanmax, mo([10, 11], "ndvi"))
        d = dict(nd_spring=nd_sp, nd_jun=nd_jun, nd_summin=nd_smin, nd_summed=nd_smed, nd_fall=nd_oct,
                 nd_drop=nd_jun - nd_smin, nd_rebound=nd_oct - nd_smin, nd_march=_nm(np.nanmax, mo([3], "ndvi")),
                 re_sum=_nm(np.nanmedian, mo([7, 8], "ndre")), re_summin=_nm(np.nanmin, mo([7, 8, 9], "ndre")),
                 re_drop=_nm(np.nanmax, mo([5, 6], "ndre")) - _nm(np.nanmin, mo([7, 8, 9], "ndre")),
                 mi_summin=_nm(np.nanmin, mo([7, 8, 9], "ndmi")), mi_sum=_nm(np.nanmedian, mo([7, 8], "ndmi")),
                 mi_drop=_nm(np.nanmax, mo([5, 6], "ndmi")) - _nm(np.nanmin, mo([7, 8, 9], "ndmi")),
                 ps_summax=_nm(np.nanmax, mo([7, 8, 9], "psri")), ps_fall=_nm(np.nanmax, mo([10, 11], "psri")),
                 nb_sum=_nm(np.nanmedian, mo([7, 8, 9], "nbr2")))
        for n, a in d.items():
            per.setdefault(n, []).append(a)
    for n, L in per.items():
        A = np.stack(L)
        F[n] = _nm(np.nanmean, A)
        if n in ("nd_summin", "nd_drop", "mi_summin", "re_summin"):
            F[n + "_worst"] = _nm(np.nanmin if "min" in n else np.nanmax, A)
    # per-scene NDVI: variance and low quantile over the growing season
    O = st["ndvi_obs"].astype(np.float32); O[O == -128] = np.nan; O /= 100.0
    dates = [str(d) for d in st["dates"]]
    gs = np.array([4 <= int(d[5:7]) <= 10 for d in dates])
    sm = np.array([6 <= int(d[5:7]) <= 9 for d in dates])
    F["nd_std"] = _nm(np.nanstd, O[gs])
    F["nd_q10_sum"] = _nm(lambda a, axis: np.nanpercentile(a, 10, axis=axis), O[sm])
    F["nd_mean_gs"] = _nm(np.nanmean, O[gs])
    B = st["summer"].astype(np.float32) / 10000.0
    bn = [str(b) for b in st["bands"]]
    for b in ("B03", "B04", "B05", "B06", "B07", "B8A", "B11", "B12"):
        F["r_" + b] = B[bn.index(b)]
    with np.errstate(all="ignore"):
        F["r_re_ratio"] = B[bn.index("B07")] / np.maximum(B[bn.index("B05")], 1e-3)
        F["r_swir_ratio"] = B[bn.index("B11")] / np.maximum(B[bn.index("B8A")], 1e-3)
    return {n: a.astype(np.float32) for n, a in F.items()}


def context(g):
    from scipy import ndimage
    can = np.nan_to_num(g["canopy"])
    return dict(c_fairway=np.nan_to_num(g["fairway"]), c_mown=np.nan_to_num(g["mown"]), c_canopy=can,
                c_elig=np.nan_to_num(g["elig"]), c_dfw_min=g["dfw_min"], c_dfw_mean=g["dfw_mean"],
                c_canopy_nb=ndimage.uniform_filter(can, 5))


def relative(F, g):
    """Per-course references: OSM fairway cells (fairway share >= 0.7) and mown-rough cells next to them
    (no fairway / canopy, 5-25 m from the fairway). Returns {fw_<n>, rf_<n>} = feature - reference median."""
    fw = np.nan_to_num(g["fairway"]) >= 0.7
    rf = (np.nan_to_num(g["mown"]) == 0) & (np.nan_to_num(g["canopy"]) < 0.05) & (g["dfw_mean"] >= 5) & (g["dfw_mean"] <= 25) \
        & (np.nan_to_num(g["water"]) == 0)
    out = {}
    for n, a in F.items():
        for tag, m in (("fw_", fw), ("rf_", rf)):
            v = a[m]; v = v[np.isfinite(v)]
            med = np.median(v) if len(v) >= 30 else np.nan
            out[tag + n] = a - med
    return out


def course_grid(slug, featset):
    st = load_stack(slug); g = load_g10(slug)
    H, W = int(g["H"]), int(g["W"])
    assert tuple(st["shape"]) == (H, W), (slug, st["shape"], H, W)
    F = s2_features(st); C = context(g)
    R = relative(F, g)
    cols = {}
    if featset in ("s2", "s2raw", "fused"):
        cols.update(R)
    if featset == "s2raw":
        cols.update(F)
    if featset in ("s2fw",):
        cols.update({k: v for k, v in R.items() if k.startswith("fw_")})
    if featset in ("s2", "s2raw", "ctx", "s2fw", "fused"):
        cols.update(C)
    if featset == "s2only":
        cols.update(R)
    names = sorted(cols)
    return names, np.stack([cols[n] for n in names], -1).reshape(H * W, len(names)), g


def map_1m(idx, g):
    W1 = int(g["W1"]); r1 = idx // W1; c1 = idx % W1
    return ((r1 + int(g["ro"])) // 10) * int(g["W"]) + (c1 + int(g["co"])) // 10
