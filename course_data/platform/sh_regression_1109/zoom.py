import sys, json, numpy as np, rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
ROOT = "/home/user/my_golf_data_science"
pkg = json.load(open(sys.argv[1])); key = sys.argv[2]; outdir = sys.argv[3]; year = sys.argv[4] if len(sys.argv) > 4 else "2023"
hz = json.load(open(f"{ROOT}/course_data/spirit_hollow/hand_zones_ll.json"))["holes"][key]
R = rasterio.open(f"{ROOT}/course_data/vision_any/spirit_hollow/raw/naip_{year}.tif")
T = Transformer.from_crs("EPSG:4326", R.crs, always_xy=True)
def xy(poly):
    p = np.asarray(poly, float)[:, :2]
    lon, lat = (p[:, 0], p[:, 1]) if abs(p[0, 0]) > 60 else (p[:, 1], p[:, 0])
    x, y = T.transform(lon, lat); return np.c_[x, y]
t = xy([hz["tee_ll"]])[0]; d = xy([hz["dot270_ll"]])[0]
u = (d - t) / np.linalg.norm(d - t)
c = t + u * 270 * 0.9144; half = 110
win = from_bounds(c[0] - half, c[1] - half, c[0] + half, c[1] + half, R.transform)
img = R.read([1, 2, 3], window=win, boundless=True).transpose(1, 2, 0)
ext = (c[0] - half, c[0] + half, c[1] - half, c[1] + half)
fig, axs = plt.subplots(1, 2, figsize=(20, 10))
for ax, zones, tt in ((axs[0], [(z["lie"], z["poly_ll"], "") for z in hz["zones"]], "hand"),
                      (axs[1], [(z["lie"], z["poly"], z.get("src", "")) for z in pkg["holes"][key.rstrip("BF")]["zones_ll"]], "package")):
    ax.imshow(img, extent=ext)
    for lie, poly, src in zones:
        if lie in ("native", "fairway", "water", "ob") and len(poly) >= 3:
            ax.add_patch(Polygon(xy(poly), fill=False, ec={"native": "magenta", "fairway": "white", "water": "cyan", "ob": "red"}[lie], lw=1.5,
                                 ls="--" if "native_side" in src else "-"))
    for dd in (225, 250, 275, 300, 325):
        ang = np.linspace(0, 2 * np.pi, 400); r = dd * 0.9144
        ax.plot(t[0] + r * np.cos(ang), t[1] + r * np.sin(ang), color="orange", lw=0.5)
    ax.set_xlim(ext[:2]); ax.set_ylim(ext[2:]); ax.set_title(f"{key} {tt} NAIP {year} (rings 225..325 yd)"); ax.set_xticks([]); ax.set_yticks([])
fig.tight_layout(); fig.savefig(f"{outdir}/zoom_{key}_{year}.jpg", dpi=60); plt.close(fig)
