import json, os, sys, pickle, warnings
warnings.filterwarnings("ignore")
import numpy as np
WT = "/home/user/my_golf_data_science"; CD = os.path.join(WT, "course_data")
for p in ("mapper", "product", "platform"): sys.path.insert(0, os.path.join(CD, p))
import common as M, mowing_line as ML, error_budget as E, mow_self as MS
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import rasterio
from pyproj import Transformer
slug, ref, OUT, x0, x1, a0, a1 = sys.argv[1:8]; x0, x1, a0, a1 = map(float, (x0, x1, a0, a1))
G = pickle.load(open(f"mow/{slug}.pkl", "rb")); g = G["holes"][ref]
cfgs = {c["slug"]: (c, "v1") for c in E.SETS["v1"]()}; cfgs.update({c["slug"]: (c, "v2") for c in E.SETS["v2"]()})
cfg, sv = cfgs[slug]; pkg = M.rj(f"an_{sv}/{slug}/package.json"); S = cfg["tees"]
frames = M.make_frames(pkg, M.tee_set_of(pkg, S) if any(k.lower() == S.lower() for k in pkg.get("tee_sets") or {}) else M.tee_set_of(pkg)); fj = frames[ref]
raw = os.path.join(CD, "vision_any", slug, "raw"); fs = sorted(x for x in os.listdir(raw) if x.startswith("naip_"))
xs = np.arange(x0, x1, 0.5); as_ = np.arange(a0, a1, 0.5); XX, YY = np.meshgrid(xs, as_); ll = M.xy_to_ll(fj, np.c_[XX.ravel(), YY.ravel()])
fig, ax = plt.subplots(1, len(fs), figsize=(9 * len(fs), 9 * (a1 - a0) / (x1 - x0) + 0.6))
ft, m = ML.features(g); sh = g["shape"]
for k, f in enumerate(fs):
    with rasterio.open(os.path.join(raw, f)) as r:
        tr = Transformer.from_crs("EPSG:4326", r.crs, always_xy=True); Eg, Ng = tr.transform(ll[:, 0], ll[:, 1])
        a = r.read(); inv = ~r.transform; c, rw = inv * (np.asarray(Eg), np.asarray(Ng)); c = np.clip(c.astype(int), 0, a.shape[2] - 1); rw = np.clip(rw.astype(int), 0, a.shape[1] - 1)
        rgb = np.stack([a[i][rw, c] for i in range(3)], -1).reshape(XX.shape + (3,)).astype(float)
    rgb = np.clip(rgb / np.percentile(rgb, 99.8), 0, 1) ** 0.8
    A = ax[k] if len(fs) > 1 else ax
    A.imshow(rgb, extent=[x0, x1, a0, a1], origin="lower")
    A.contour(ML.XS, ML.AS, m["d"], levels=[0.01], colors="white", linewidths=1.2)
    A.contour(ML.XS, ML.AS, m["d"], levels=[10], colors="cyan", linewidths=1, linestyles="dashed")
    if "t_native" in g:
        A.contour(ML.XS, ML.AS, g["t_native"].reshape(sh).astype(float), levels=[0.5], colors="yellow", linewidths=1.5)
        A.contour(ML.XS, ML.AS, g["t_fairway"].reshape(sh).astype(float), levels=[0.5], colors="lime", linewidths=1, linestyles="dotted")
    for s in ("L", "R"):
        p = MS.side_score(g, ft, m, s); ln = ML.detect(g, p, s, m); mk = ML.band_mask(g, ln, s)
        if mk.any(): A.contour(ML.XS, ML.AS, mk.astype(float), levels=[0.5], colors="red", linewidths=1.5)
    A.set_xlim(x0, x1); A.set_ylim(a0, a1); A.set_title(f"{slug} {ref} {f}: yellow hand native, lime dotted hand fairway, white pkg fairway, cyan +10, red detected")
fig.tight_layout(); fig.savefig(OUT, dpi=80)
