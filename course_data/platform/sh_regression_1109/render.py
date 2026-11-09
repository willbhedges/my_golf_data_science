"""Render a SH hole: NAIP 2023 + hand-map zones (left) vs product package zones (right)."""
import sys, json, numpy as np, rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
ROOT = "/home/user/my_golf_data_science"
pkg = json.load(open(sys.argv[1])); keys = sys.argv[2].split(","); outdir = sys.argv[3]
hz = json.load(open(f"{ROOT}/course_data/spirit_hollow/hand_zones_ll.json"))["holes"]
R = rasterio.open(f"{ROOT}/course_data/vision_any/spirit_hollow/raw/naip_2023.tif")
T = Transformer.from_crs("EPSG:4326", R.crs, always_xy=True)
COL = dict(native="#ff00ff", recovery="#00c000", trees="#00c000", water="#00a0ff", sand="#ffff00", ob="#ff0000",
           fairway="#ffffff", first_cut="#bbbbbb", rough="#888888", green="#00ffff")
def xy(poly):  # [lat, lon] or [lon, lat]? detect
    p = np.asarray(poly, float)[:, :2]
    if abs(p[0, 0]) > 60:   # lon first
        lon, lat = p[:, 0], p[:, 1]
    else:
        lat, lon = p[:, 0], p[:, 1]
    x, y = T.transform(lon, lat); return np.c_[x, y]
for key in keys:
    h = hz[key]; ref = key.rstrip("BF")
    ph = pkg["holes"][ref]
    pts = np.vstack([xy([h["tee_ll"]]), xy([h["green_ll"]])])
    cx, cy = pts.mean(0); half = max(np.ptp(pts[:, 0]), np.ptp(pts[:, 1])) / 2 + 120
    win = from_bounds(cx - half, cy - half, cx + half, cy + half, R.transform)
    img = R.read([1, 2, 3], window=win, boundless=True).transpose(1, 2, 0)
    ext = (cx - half, cx + half, cy - half, cy + half)
    fig, axs = plt.subplots(1, 3, figsize=(24, 8.5))
    for ax, title, zones in ((axs[0], "NAIP 2023", []),
                             (axs[1], f"hand map {key}", [(z["lie"], z["poly_ll"], "hand") for z in h["zones"]]),
                             (axs[2], f"package hole {ref}", [(z["lie"], z["poly"], z.get("src", "")) for z in ph["zones_ll"]])):
        ax.imshow(img, extent=ext)
        for lie, poly, src in zones:
            if len(poly) < 3: continue
            c = COL.get(lie, "#ff8800")
            ax.add_patch(Polygon(xy(poly), closed=True, fill=False, ec=c, lw=2.2 if lie == "native" else 1.2,
                                 ls="--" if "native_side" in src else "-"))
        t = xy([h["tee_ll"]])[0]; g = xy([h["green_ll"]])[0]
        ax.plot([t[0], g[0]], [t[1], g[1]], "w:", lw=1)
        # distance rings 250/300 yds from hand tee
        for d in (250, 300):
            ang = np.linspace(0, 2 * np.pi, 200); r = d * 0.9144
            ax.plot(t[0] + r * np.cos(ang), t[1] + r * np.sin(ang), color="orange", lw=0.6)
        ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_title(title); ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout(); fig.savefig(f"{outdir}/hole_{key}.jpg", dpi=70); plt.close(fig)
    print("wrote", key)
