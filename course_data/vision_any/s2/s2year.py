"""Per-year Sentinel-2 features + year-consistency drought gate (s2_longgrass.md 'Enlarged set + drought gate').
features_year(st, y) -> {name: (H, W)} the s2lib seasonal features for ONE season (no multi-year mean, no worst-year);
course_grid_years(slug) -> names, {year: (H*W, F) relative + context}, g, drought {year: index}.
Drought index of a season (label-free, the course's own unirrigated reference): median Jul-Sep minimum NDVI of the
mown-rough band (unmown, canopy-free, 5-25 m off the OSM fairway) minus that of the OSM fairway cells, relative to the
course's least-browned season. A season whose rough band browned >= DROUGHT_D more than its best season is a drought
season for that course and is left out of the year aggregation (when another season remains)."""
import numpy as np, warnings
import s2lib as S2
_nm = S2._nm


def years_of(st):
    return sorted({str(m)[:4] for m in st["months"]})


def features_year(st, y):
    months = [str(m) for m in st["months"]]
    I = st["idx"].astype(np.float32); I[I == -128] = np.nan; I /= 100.0
    k = {str(n): i for i, n in enumerate(st["inames"])}

    def mo(ms, band):
        j = [months.index(f"{y}-{m:02d}") for m in ms if f"{y}-{m:02d}" in months]
        return I[j, k[band]] if j else np.full((1,) + I.shape[2:], np.nan, np.float32)
    nd_jun = _nm(np.nanmax, mo([5, 6], "ndvi")); nd_smin = _nm(np.nanmin, mo([7, 8, 9], "ndvi"))
    nd_oct = _nm(np.nanmax, mo([10, 11], "ndvi"))
    F = dict(nd_spring=_nm(np.nanmax, mo([4, 5], "ndvi")), nd_jun=nd_jun, nd_summin=nd_smin,
             nd_summed=_nm(np.nanmedian, mo([7, 8, 9], "ndvi")), nd_fall=nd_oct, nd_drop=nd_jun - nd_smin,
             nd_rebound=nd_oct - nd_smin, nd_march=_nm(np.nanmax, mo([3], "ndvi")),
             re_sum=_nm(np.nanmedian, mo([7, 8], "ndre")), re_summin=_nm(np.nanmin, mo([7, 8, 9], "ndre")),
             re_drop=_nm(np.nanmax, mo([5, 6], "ndre")) - _nm(np.nanmin, mo([7, 8, 9], "ndre")),
             mi_summin=_nm(np.nanmin, mo([7, 8, 9], "ndmi")), mi_sum=_nm(np.nanmedian, mo([7, 8], "ndmi")),
             mi_drop=_nm(np.nanmax, mo([5, 6], "ndmi")) - _nm(np.nanmin, mo([7, 8, 9], "ndmi")),
             ps_summax=_nm(np.nanmax, mo([7, 8, 9], "psri")), ps_fall=_nm(np.nanmax, mo([10, 11], "psri")),
             nb_sum=_nm(np.nanmedian, mo([7, 8, 9], "nbr2")))
    O = st["ndvi_obs"].astype(np.float32); O[O == -128] = np.nan; O /= 100.0
    dates = [str(d) for d in st["dates"]]
    gs = np.array([d[:4] == y and 4 <= int(d[5:7]) <= 10 for d in dates])
    sm = np.array([d[:4] == y and 6 <= int(d[5:7]) <= 9 for d in dates])
    F["nd_std"] = _nm(np.nanstd, O[gs]) if gs.sum() >= 3 else np.full(O.shape[1:], np.nan, np.float32)
    F["nd_q10_sum"] = _nm(lambda a, axis: np.nanpercentile(a, 10, axis=axis), O[sm]) if sm.sum() >= 3 else np.full(O.shape[1:], np.nan, np.float32)
    F["nd_mean_gs"] = _nm(np.nanmean, O[gs]) if gs.sum() else np.full(O.shape[1:], np.nan, np.float32)
    B = st["summer"].astype(np.float32) / 10000.0
    bn = [str(b) for b in st["bands"]]
    for b in ("B03", "B04", "B05", "B06", "B07", "B8A", "B11", "B12"):
        F["r_" + b] = B[bn.index(b)]
    with np.errstate(all="ignore"):
        F["r_re_ratio"] = B[bn.index("B07")] / np.maximum(B[bn.index("B05")], 1e-3)
        F["r_swir_ratio"] = B[bn.index("B11")] / np.maximum(B[bn.index("B8A")], 1e-3)
    return {n: np.asarray(a, np.float32) for n, a in F.items()}


def drought_index(F, g):
    fw = np.nan_to_num(g["fairway"]) >= 0.7
    rf = (np.nan_to_num(g["mown"]) == 0) & (np.nan_to_num(g["canopy"]) < 0.05) & (g["dfw_mean"] >= 5) & \
        (g["dfw_mean"] <= 25) & (np.nan_to_num(g["water"]) == 0)
    a = F["nd_summin"]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return float(np.nanmedian(a[rf]) - np.nanmedian(a[fw])) if fw.sum() >= 30 and rf.sum() >= 30 else np.nan


def course_grid_years(slug, ctx=True):
    st = S2.load_stack(slug); g = S2.load_g10(slug)
    H, W = int(g["H"]), int(g["W"])
    C = S2.context(g)
    out, di = {}, {}
    names = None
    for y in years_of(st):
        F = features_year(st, y)
        di[y] = drought_index(F, g)
        cols = S2.relative(F, g)
        if ctx:
            cols.update(C)
        names = sorted(cols)
        out[y] = np.stack([cols[n] for n in names], -1).reshape(H * W, len(names))
    return names, out, g, di
