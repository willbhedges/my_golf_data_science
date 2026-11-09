"""python3 mow_render.py MOWDIR MODELS.pkl slug ref OUT.png [params json] : RGB / tex / ndvi / p panels with truth native (yellow), d=0 (white), d=10 (cyan), line (red)"""
import json, os, sys, pickle, warnings
warnings.filterwarnings("ignore")
import numpy as np
WT = "/home/user/my_golf_data_science"; CD = os.path.join(WT, "course_data")
for p in ("mapper", "product", "platform"): sys.path.insert(0, os.path.join(CD, p))
import common as M, native_auto as NA, mowing_line as ML, error_budget as E
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import rasterio
from pyproj import Transformer
D, MP, slug, ref, OUT = sys.argv[1:6]
PAR = json.loads(sys.argv[6]) if len(sys.argv) > 6 else {}
G = pickle.load(open(os.path.join(D, slug + ".pkl"), "rb")); g = G["holes"][ref]
A1 = os.environ.get("AN", os.path.dirname(D) + "/an")
cfgs = {c["slug"]: (c, "v1") for c in E.SETS["v1"]()}; cfgs.update({c["slug"]: (c, "v2") for c in E.SETS["v2"]()})
cfg, sv = cfgs[slug]; pkg = M.rj(f"{A1}_{sv}/{slug}/package.json"); S = cfg["tees"]
frames = M.make_frames(pkg, M.tee_set_of(pkg, S) if any(k.lower() == S.lower() for k in pkg.get("tee_sets") or {}) else M.tee_set_of(pkg))
fj = frames[ref]
raw = os.path.join(CD, "vision_any", slug, "raw"); f = sorted(x for x in os.listdir(raw) if x.startswith("naip_"))[-1]
XX, YY = np.meshgrid(ML.XS, ML.AS); ll = M.xy_to_ll(fj, np.c_[XX.ravel(), YY.ravel()])
with rasterio.open(os.path.join(raw, f)) as r:
    tr = Transformer.from_crs("EPSG:4326", r.crs, always_xy=True); Eg, Ng = tr.transform(ll[:, 0], ll[:, 1])
    a = r.read(); inv = ~r.transform; c, rw = inv * (np.asarray(Eg), np.asarray(Ng)); c = np.clip(c.astype(int), 0, a.shape[2] - 1); rw = np.clip(rw.astype(int), 0, a.shape[1] - 1)
    rgb = np.stack([a[i][rw, c] for i in range(3)], -1).reshape(XX.shape + (3,)).astype(float)
rgb = np.clip(rgb / np.percentile(rgb, 99.5), 0, 1)
models = pickle.load(open(MP, "rb"))["models"]; model = models.get(slug, models["_all"]); model = getattr(model, "booster_", model)
ft, m = ML.features(g); p = ML.unmown_p(g, model, ft, m); sh = g["shape"]; d = m["d"]
ext = [ML.XS[0], ML.XS[-1], ML.AS[0], ML.AS[-1]]
fig, ax = plt.subplots(1, 4, figsize=(20, 9))
score = PAR.pop("score", None)
if score == "self":
    import mow_self as MS
    p = MS.self_score(g, ft, m)
panels = [("NAIP " + f[5:9], rgb, None), ("texture (5x5 std grey)", ft["tex"], "magma"), ("NDVI", ft["ndvi"], "RdYlGn"), ("P(unmown)", p, "viridis")]
for k, (ttl, im, cm) in enumerate(panels):
    ax[k].imshow(im, extent=ext, origin="lower", cmap=cm, aspect="equal", vmin=None if cm != "viridis" else 0, vmax=None if cm != "viridis" else 1)
    ax[k].contour(ML.XS, ML.AS, d, levels=[0.01], colors="white", linewidths=1)
    ax[k].contour(ML.XS, ML.AS, d, levels=[10], colors="cyan", linewidths=0.8, linestyles="dashed")
    if "t_native" in g:
        ax[k].contour(ML.XS, ML.AS, g["t_native"].reshape(sh).astype(float), levels=[0.5], colors="yellow", linewidths=1.5)
        ax[k].contour(ML.XS, ML.AS, g["foot"].reshape(sh).astype(float), levels=[0.5], colors="gray", linewidths=0.6)
    for s in ("L", "R"):
        ln = ML.detect(g, p, s, m, PAR); mk = ML.band_mask(g, ln, s)
        if mk.any(): ax[k].contour(ML.XS, ML.AS, mk.astype(float), levels=[0.5], colors="red", linewidths=1.5)
    ax[k].set_title(ttl); ax[k].set_xlabel("yds right of tee line")
ax[0].set_ylabel("yds from tee")
fig.suptitle(f"{slug} {ref}: yellow = hand native, white = package fairway, cyan dashed = +10 yds (today's band edge), red = detected band")
fig.tight_layout(); fig.savefig(OUT, dpi=70)
