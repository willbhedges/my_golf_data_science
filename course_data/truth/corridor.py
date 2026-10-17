"""Hand-checked landing-corridor truth maps: evidence renders, tracing frame, review renders, hand_zones_ll.json.

  python3 course_data/truth/corridor.py panels --slug veenker [--holes 1,7]    # evidence renders (Actions or local)
  python3 course_data/truth/corridor.py review --slug veenker [--holes 1,7]    # side-by-side review of trace.py
  python3 course_data/truth/corridor.py build  --slug veenker                  # -> hand_zones_ll.json
  python3 course_data/truth/corridor.py edges  --slug veenker [--holes 1]      # edge table, 2nd pass (<= 10 yds)
  python3 course_data/truth/corridor.py zoom   --slug veenker --holes 1 --box 200,260,-40,0 [--which hag]

Every tee shot (par 4 / 5, the card set in SETS) gets ONE planar corridor frame (course_data/imagery/render.Frame,
UTM, tee = the package's tee of that set, aim = the package's aim point): x = yds right of the tee line,
`along` = yds out along it. All renders of a hole share that frame, so a point read off the grid of any panel
is the same ground point. The trace (course_data/truth/<slug>/trace.py) is written by hand in those
(x, along) yards after looking at the renders, and converted to WGS84 by the same frame (build).

Evidence (none of it is a vision layer or a model output):
  photo     USDA NAIP 2023 0.3 m RGB (the package imagery), 5 px / yd, 10-yd grid
  CIR       NAIP NIR-R-G false colour (mown turf vs unmown grass / canopy separate better in NIR)
  years     every other NAIP year available (vision_any raw/ 0.6 m; raw2/ 1 m multi-year when present):
            unmown long grass stays tan / textured across years, mown rough does not
  canopy    USGS 3DEP lidar height above ground (vision_any raw/hag.tif)
  low veg   share of lidar returns 0.3-1.5 m above ground (raw2 lidar_v2 n_low / n_all): tall grass / shrubs

Outputs in course_data/truth/<slug>/: render/hNN_photo.png, render/hNN_evidence.png, render/hNN_overview.png,
render/frames.json, review/hNN.png, hand_zones_ll.json (schema of course_data/spirit_hollow/hand_zones_ll.json).
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path.insert(0, os.path.join(CD, "imagery"))
import render as R                                         # noqa: E402

YD = 0.9144
A0, A1, LAT = 140.0, 350.0, 70.0       # rendered corridor (yds); the mapped footprint is FOOT
FOOT = dict(a0=145.0, a1=345.0, lat=65.0)
CORE = dict(a0=150.0, a1=340.0, lat=60.0)   # the corridor the task asks for (every zone traced inside it)
PPY_PHOTO, PPY_EV = 5.0, 2.5
# card tee set per course (the back or middle set from the card; = the scoreboard's tee set)
SETS = {"veenker": "Blue", "coldwater": "Blue", "ellis": "Blue"}
LIES = ["rough", "first_cut", "fairway", "recovery", "native", "water", "sand", "ob"]
COL = {"fairway": (40, 230, 60), "first_cut": (170, 255, 120), "rough": (255, 255, 255), "recovery": (20, 110, 20),
       "native": (230, 190, 60), "water": (40, 120, 255), "sand": (255, 240, 200), "ob": (255, 40, 40)}


def log(*a):
    print(*a, flush=True)


def tdir(slug, *p):
    return os.path.join(HERE, slug, *p)


# =========================================================================== course + frames
def package(slug):
    return json.load(open(os.path.join(CD, "packages", slug, "package.json")))


def tee_set(slug, pkg=None):
    pkg = pkg or package(slug)
    s = SETS.get(slug) or pkg.get("tee_set")
    if s not in pkg["tee_sets"]:
        raise SystemExit(f"{slug}: tee set {s} not on the card {list(pkg['tee_sets'])}")
    return s


def tee_holes(slug, pkg=None):
    """{ref: dict(par, yards, tee_ll, aim_ll, green_ll)} for the par 4 / 5 holes of the chosen set."""
    pkg = pkg or package(slug)
    st = tee_set(slug, pkg)
    out = {}
    for ref, h in sorted(pkg["holes"].items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 99):
        if int(h.get("par") or 0) < 4:
            continue
        t = (h.get("tees") or {}).get(st) or {}
        tee = t.get("tee_ll") or h.get("tee_ll")
        aim = t.get("aim_ll") or h.get("aim_ll")
        if not tee or not aim:
            log(f"  ! {slug} {ref}: no tee / aim for {st}")
            continue
        out[ref] = dict(ref=ref, par=int(h["par"]), yards=(h.get("yards") or {}).get(st), tee_ll=tee, aim_ll=aim,
                        green_ll=h.get("green_ll"), tee_method=t.get("method"), tee_conf=t.get("confidence"),
                        measured=t.get("measured_yards"))
    return out


def corridor_frame(tee_ll, aim_ll, ppy, a0=A0, a1=A1, lat=LAT):
    return R.Frame(tee_ll, aim_ll, ppy=ppy, tee_px=(lat * ppy, a1 * ppy), proj="utm",
                   size=(int(round(2 * lat * ppy)), int(round((a1 - a0) * ppy))))


def frames(slug):
    """{ref: dict(..., frame)}: the trace frame of every tee shot (render/frames.json, written by `panels`)."""
    p = tdir(slug, "render", "frames.json")
    if os.path.exists(p):
        return json.load(open(p))
    st = tee_set(slug)
    return {ref: dict(h, set=st, frame=corridor_frame(h["tee_ll"], h["aim_ll"], 1.0).to_json())
            for ref, h in tee_holes(slug).items()}


def frame_of(fj, ppy, **kw):
    f = fj["frame"]
    return corridor_frame(f["tee_ll"], f["aim_ll"], ppy, **kw)


# =========================================================================== rasters
class Raster:
    """Any GeoTIFF warped into a Frame (bilinear or nearest)."""

    def __init__(self, path, bands=None, label=None):
        import rasterio
        self.path = path
        self.label = label or os.path.basename(path)
        with rasterio.open(path) as s:
            self.crs = s.crs.to_string()
            self.T = s.transform
            self.W, self.H = s.width, s.height
            self.nodata = s.nodata
            self.count = s.count
            self.res = abs(s.transform.a)
        self.bands = bands or list(range(1, self.count + 1))
        from pyproj import Transformer
        self._tr = Transformer.from_crs("EPSG:4326", self.crs, always_xy=True)
        self._cache = None

    def data(self):
        if self._cache is None:
            import rasterio
            with rasterio.open(self.path) as s:
                self._cache = s.read(self.bands)
        return self._cache

    def warp(self, fr, nearest=False):
        import cv2
        Wd, Hd = fr.size
        step = 8
        gx = np.arange(0, Wd + step, step, dtype=float)
        gy = np.arange(0, Hd + step, step, dtype=float)
        GX, GY = np.meshgrid(gx, gy)
        ll = fr.px_to_ll(np.c_[GX.ravel() + 0.5, GY.ravel() + 0.5])
        x, y = self._tr.transform(ll[:, 0], ll[:, 1])
        inv = ~self.T
        c, r = inv * (np.asarray(x), np.asarray(y))
        cg = (np.asarray(c) - 0.5).reshape(GX.shape).astype(np.float32)
        rg = (np.asarray(r) - 0.5).reshape(GX.shape).astype(np.float32)
        big = ((len(gx) - 1) * step + 1, (len(gy) - 1) * step + 1)
        cm = cv2.resize(cg, big, interpolation=cv2.INTER_LINEAR)[:Hd, :Wd]
        rm = cv2.resize(rg, big, interpolation=cv2.INTER_LINEAR)[:Hd, :Wd]
        out = []
        for b in self.data():
            src = b.astype(np.float32)
            spo = self.res / (YD / fr.ppy)
            if spo > 1.4 and not nearest:
                src = cv2.GaussianBlur(src, (0, 0), 0.5 * spo)
            out.append(cv2.remap(src, cm, rm, cv2.INTER_NEAREST if nearest else cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=float("nan")))
        return np.stack(out, -1)


def sources(slug):
    """dict name -> Raster for whatever evidence exists locally."""
    S = {}
    pk = os.path.join(CD, "packages", slug, "imagery")
    if os.path.exists(os.path.join(pk, "naip_rgb.tif")):
        S["photo"] = Raster(os.path.join(pk, "naip_rgb.tif"), label="NAIP %s 0.3 m" % _year(pk))
    if os.path.exists(os.path.join(pk, "naip_nir.tif")):
        S["nir"] = Raster(os.path.join(pk, "naip_nir.tif"))
    years = {}
    for d in (os.path.join(CD, "vision_any", slug, "raw"), os.path.join(CD, "vision_any", slug, "raw2")):
        for f in sorted(glob.glob(os.path.join(d, "naip_*.tif"))):
            yr = os.path.basename(f)[5:9]
            if yr.isdigit() and (yr not in years or "/raw/" in years[yr]):
                years[yr] = f
    for yr, f in sorted(years.items(), reverse=True):
        S[f"naip_{yr}"] = Raster(f, label=f"NAIP {yr}")
    d = os.path.join(CD, "vision_any", slug, "raw")
    if os.path.exists(os.path.join(d, "hag.tif")):
        S["hag"] = Raster(os.path.join(d, "hag.tif"), label="lidar HAG")
    p = os.path.join(CD, "vision_any", slug, "raw2", "lidar_v2.tif")
    if os.path.exists(p):
        S["lidar_v2"] = Raster(p, label="lidar v2")
    return S


def _year(d):
    try:
        return json.load(open(os.path.join(d, "georef.json")))["imagery"]["year"]
    except Exception:                                          # noqa: BLE001
        return "?"


def _u8(a):
    return np.clip(np.nan_to_num(a, nan=0), 0, 255).astype(np.uint8)


def hag_rgb(h):
    """lidar height above ground (m) -> colour: < 0.5 grey, 0.5-2.5 yellow, 2.5-8 green, > 8 dark green."""
    out = np.full(h.shape + (3,), 30, np.uint8)
    v = np.isfinite(h)
    out[v] = (80, 80, 80)
    out[v & (h >= 0.5)] = (220, 210, 60)
    out[v & (h >= 2.5)] = (60, 200, 60)
    out[v & (h >= 8)] = (10, 110, 10)
    out[v & (h >= 16)] = (0, 60, 0)
    return out


def lowveg_rgb(frac):
    import matplotlib.cm as cm
    f = np.clip(np.nan_to_num(frac, nan=0) / 0.3, 0, 1)
    return (cm.magma(f)[..., :3] * 255).astype(np.uint8)


def hag_m(S, fr):
    h = S["hag"].warp(fr, nearest=True)[..., 0]
    return np.where(h >= 255, np.nan, h * 0.25)


def lidar_contour(img, S, fr, thr=2.5, color=(0, 255, 255)):
    """Draw the lidar canopy edge (HAG > thr m) on an image of frame fr: separates crowns from cast shadows."""
    import cv2
    if "hag" not in S:
        return img
    h = hag_m(S, fr)
    m = (np.nan_to_num(h, nan=0) > thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    out = img.copy()
    cv2.drawContours(out, cs, -1, color, 1)
    return out


def shadow_dir(fj):
    """Unit (x, along) direction of north-west in the hole frame (NAIP shadows fall roughly NW, late-morning sun)."""
    fr = frame_of(fj, 1.0)
    t = np.asarray(fj["frame"]["tee_ll"], float)
    p = fr.ll_to_yds([t + np.array([-0.0005, 0.0004])])[0]
    v = np.array([p[0], -p[1]])
    return v / np.linalg.norm(v)


def cir(S, fr, rgb=None):
    rgb = S["photo"].warp(fr) if rgb is None else rgb
    return _u8(np.dstack([S["nir"].warp(fr)[..., 0], rgb[..., 0], rgb[..., 1]]))


# =========================================================================== drawing
def grid(img, fr, a0=A0, a1=A1, lat=LAT, step=10, label_every=20, font=0.4):
    import cv2
    out = img.copy()
    ppy = fr.ppy
    ov = out.copy()
    for a in np.arange(math.ceil(a0 / step) * step, a1 + 0.1, step):
        y = int(round((a1 - a) * ppy))
        cv2.line(ov, (0, y), (out.shape[1], y), (255, 255, 255) if a % 50 else (255, 255, 0), 1)
    for x_ in np.arange(-lat, lat + 0.1, step):
        x = int(round((x_ + lat) * ppy))
        cv2.line(ov, (x, 0), (x, out.shape[0]), (255, 255, 255) if x_ else (255, 0, 255), 1)
    out = cv2.addWeighted(ov, 0.35, out, 0.65, 0)
    for a in np.arange(math.ceil(a0 / label_every) * label_every, a1 + 0.1, label_every):
        y = int(round((a1 - a) * ppy))
        for xx in (2, out.shape[1] // 2 + 3):
            cv2.putText(out, f"{int(a)}", (xx, y - 2), cv2.FONT_HERSHEY_SIMPLEX, font, (0, 0, 0), 3)
            cv2.putText(out, f"{int(a)}", (xx, y - 2), cv2.FONT_HERSHEY_SIMPLEX, font, (255, 255, 0), 1)
    for x_ in np.arange(-lat, lat + 0.1, label_every):
        x = int(round((x_ + lat) * ppy))
        t = f"{int(x_):+d}" if x_ else "0"
        for yy in (30, out.shape[0] - 4):
            cv2.putText(out, t, (x + 2, yy), cv2.FONT_HERSHEY_SIMPLEX, font, (0, 0, 0), 3)
            cv2.putText(out, t, (x + 2, yy), cv2.FONT_HERSHEY_SIMPLEX, font, (255, 255, 255), 1)
    return out


def title(img, text, font=0.5):
    import cv2
    out = img.copy()
    cv2.rectangle(out, (0, 0), (out.shape[1], 18), (0, 0, 0), -1)
    cv2.putText(out, text, (4, 13), cv2.FONT_HERSHEY_SIMPLEX, font, (255, 255, 255), 1)
    return out


def stack(panels, cols):
    rows = []
    h = max(p.shape[0] for p in panels)
    w = max(p.shape[1] for p in panels)
    pad = lambda p: np.pad(p, ((0, h - p.shape[0]), (0, w - p.shape[1]), (0, 0)))       # noqa: E731
    panels = [pad(p) for p in panels]
    while len(panels) % cols:
        panels.append(np.zeros_like(panels[0]))
    for i in range(0, len(panels), cols):
        rows.append(np.concatenate([np.pad(p, ((2, 2), (2, 2), (0, 0)), constant_values=255) for p in panels[i:i + cols]], 1))
    return np.concatenate(rows, 0)


def save(path, rgb):
    from PIL import Image
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(rgb).save(path, optimize=True)


def yd_to_px(fr, xy, a1=A1, lat=LAT):
    xy = np.asarray(xy, float)
    return np.c_[(xy[:, 0] + lat) * fr.ppy, (a1 - xy[:, 1]) * fr.ppy]


def draw_zones(img, fr, zones, fill=True, width=2, labels=False, a1=A1, lat=LAT):
    import cv2
    out = img.copy()
    ov = out.copy()
    for z in zones:
        p = np.round(yd_to_px(fr, z["xy"], a1, lat) * 8).astype(np.int32)
        if fill and z["lie"] != "rough":
            cv2.fillPoly(ov, [p], COL[z["lie"]], shift=3)
    if fill:
        out = cv2.addWeighted(ov, 0.30, out, 0.70, 0)
    for i, z in enumerate(zones):
        p = np.round(yd_to_px(fr, z["xy"], a1, lat) * 8).astype(np.int32)
        c = COL[z["lie"]]
        cv2.polylines(out, [p], True, (0, 0, 0), width + 2, shift=3)
        cv2.polylines(out, [p], True, c, width, shift=3)
        if labels:
            m = yd_to_px(fr, z["xy"], a1, lat).mean(0).astype(int)
            cv2.putText(out, f"{i}{z['lie'][:3]}", tuple(int(v) for v in m), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 2)
            cv2.putText(out, f"{i}{z['lie'][:3]}", tuple(int(v) for v in m), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    return out


def lie_grid(zones, step=1.0, a0=A0, a1=A1, lat=LAT):
    """lie name per cell of the (along, x) grid, later zones win, unzoned = rough."""
    from matplotlib.path import Path
    A = np.arange(a0, a1 + 1e-6, step)
    X = np.arange(-lat, lat + 1e-6, step)
    XX, AA = np.meshgrid(X, A)
    pts = np.c_[XX.ravel(), AA.ravel()]
    lie = np.array(["rough"] * len(pts), dtype=object)
    for z in zones:
        if len(z["xy"]) >= 3:
            lie[Path(np.asarray(z["xy"], float)).contains_points(pts)] = z["lie"]
    return A, X, lie.reshape(AA.shape)


# =========================================================================== panels
def evidence_panels(S, fj, ppy=PPY_EV):
    fr = frame_of(fj, ppy)
    P = []
    if "photo" in S and "nir" in S:
        P.append(title(grid(cir(S, fr), fr, font=0.3), "NAIP 2023 CIR (NIR,R,G)"))
    for k in sorted([k for k in S if k.startswith("naip_")], reverse=True):
        a = S[k].warp(fr)
        if np.isnan(a).mean() > 0.5 or np.nanmax(a) == 0:
            continue
        P.append(title(grid(_u8(a[..., :3]), fr, font=0.3), S[k].label + f" ({S[k].res:.1f} m)"))
    if "hag" in S:
        P.append(title(grid(hag_rgb(hag_m(S, fr)), fr, font=0.3), "lidar HAG: grey<0.5 yel<2.5 grn<8 dk>8 m"))
    if "lidar_v2" in S:
        import rasterio
        with rasterio.open(S["lidar_v2"].path) as s:
            names = list(s.descriptions)
        if "n_low" in names and "n_all" in names:
            lv = Raster(S["lidar_v2"].path, bands=[names.index("n_low") + 1, names.index("n_all") + 1])
            a = lv.warp(fr, nearest=True)
            frac = a[..., 0] / np.maximum(a[..., 1], 1)
            P.append(title(grid(lowveg_rgb(frac), fr, font=0.3), "lidar returns 0.3-1.5 m share (0-0.3)"))
    return P


def overview(S, fj, pkg_hole):
    """Whole hole (tee -> green) at 1.6 px / yd: tee boxes of every set, green, card yards; checks the frame."""
    import cv2
    L = max(float(fj.get("yards") or 400), 300) + 40
    ppy = 1.6
    fr = corridor_frame(fj["frame"]["tee_ll"], fj["frame"]["aim_ll"], ppy, a0=-30, a1=L, lat=90)
    img = _u8(S["photo"].warp(fr))
    img = grid(img, fr, a0=-30, a1=L, lat=90, step=50, label_every=50, font=0.35)
    for sname, t in (pkg_hole.get("tees") or {}).items():
        if t.get("tee_ll"):
            p = fr.ll_to_px([t["tee_ll"]])[0]
            p = (int(p[0]), int(p[1]))
            cv2.circle(img, p, 4, (255, 0, 0) if sname == fj.get("set") else (255, 255, 255), -1)
            cv2.putText(img, sname, (p[0] + 5, p[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    if fj.get("green_ll"):
        p = fr.ll_to_px([fj["green_ll"]])[0]
        cv2.circle(img, (int(p[0]), int(p[1])), 6, (255, 0, 255), 2)
    y0, y1 = int((L - CORE["a1"]) * ppy), int((L - CORE["a0"]) * ppy)
    x0, x1 = int((90 - CORE["lat"]) * ppy), int((90 + CORE["lat"]) * ppy)
    cv2.rectangle(img, (x0, y0), (x1, y1), (0, 255, 255), 1)
    return title(img, f"hole {fj['ref']} par {fj['par']} {fj.get('set')} {fj.get('yards')} yds (tee {fj.get('tee_method')})", 0.4)


def stage_panels(slug, holes=None):
    pkg = package(slug)
    st = tee_set(slug, pkg)
    S = sources(slug)
    log(f"[{slug}] tee set {st}; sources: " + ", ".join(f"{k}={v.label}" for k, v in S.items()))
    fpath = tdir(slug, "render", "frames.json")
    FJ = json.load(open(fpath)) if os.path.exists(fpath) else {}
    for ref, h in tee_holes(slug, pkg).items():
        if ref not in FJ:
            FJ[ref] = dict(h, set=st, frame=corridor_frame(h["tee_ll"], h["aim_ll"], 1.0).to_json())
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    json.dump(dict(sorted(FJ.items(), key=lambda kv: int(kv[0]))), open(fpath, "w"), indent=1)
    for ref, fj in FJ.items():
        if holes and ref not in holes:
            continue
        fr = frame_of(fj, PPY_PHOTO)
        photo = _u8(S["photo"].warp(fr))
        save(tdir(slug, "render", f"h{int(ref):02d}_photo.png"),
             title(grid(photo, fr), f"{slug} {ref} par {fj['par']} ({fj['set']} {fj.get('yards')}): NAIP 2023 0.3 m, "
                                    f"x = yds right of tee line, along = yds from tee", 0.42))
        P = evidence_panels(S, fj)
        save(tdir(slug, "render", f"h{int(ref):02d}_evidence.png"), stack(P, 4))
        save(tdir(slug, "render", f"h{int(ref):02d}_overview.png"), overview(S, fj, pkg["holes"][ref]))
        log(f"  {ref}: {len(P)} evidence panels")


# =========================================================================== trace -> review / build
def trace(slug):
    """The hand trace: course_data/truth/<slug>/trace.py (TRACE dict, written with the shape helpers below)."""
    import importlib.util
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    p = tdir(slug, "trace.py")
    spec = importlib.util.spec_from_file_location(f"truth_trace_{slug}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.TRACE


# ---- shape helpers for trace.py: every coordinate is (x yds right of the tee line, yds along it)
def band(left, right):
    """Polygon between a left and a right edge, each [(along, x), ...] (any order)."""
    L_ = sorted(left)
    R_ = sorted(right, reverse=True)
    return [[float(x), float(a)] for a, x in L_] + [[float(x), float(a)] for a, x in R_]


def ell(cx, ca, rx, ra, n=16):
    """Ellipse centred (cx, ca) with half-widths rx (lateral) / ra (along): one tree crown."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return [[round(float(cx + rx * np.cos(v)), 2), round(float(ca + ra * np.sin(v)), 2)] for v in t]


def rect(x0, x1, a0, a1):
    return [[x0, a0], [x1, a0], [x1, a1], [x0, a1]]


def poly(*pts):
    """[(x, along), ...] as written."""
    return [[float(x), float(a)] for x, a in pts]


def Z(lie, xy, note=None):
    assert lie in LIES, lie
    z = dict(lie=lie, xy=xy)
    if note:
        z["note"] = note
    return z


def stage_review(slug, holes=None):
    """photo + trace | outlines on the photo | other NAIP year | lidar canopy | CIR | an older year."""
    S = sources(slug)
    FJ = frames(slug)
    T = trace(slug)
    for ref, th in T["holes"].items():
        if holes and ref not in holes:
            continue
        zones = th["zones"]
        fr = frame_of(FJ[ref], 3.5)
        rgb = S["photo"].warp(fr)
        photo = _u8(rgb)
        P = [title(grid(draw_zones(photo, fr, zones, labels=True), fr, font=0.3), f"{slug} {ref}: trace on NAIP 2023", 0.4),
             title(grid(draw_zones(lidar_contour(photo, S, fr), fr, zones, fill=False, width=1), fr, font=0.3),
                   "outlines + lidar canopy edge (cyan); NW = (%+.1f, %+.1f)" % tuple(shadow_dir(FJ[ref])), 0.4)]
        other = sorted([k for k in S if k.startswith("naip_") and k != "naip_2023"], reverse=True)
        if other:
            P.append(title(grid(draw_zones(_u8(S[other[0]].warp(fr)[..., :3]), fr, zones, fill=False, width=1), fr,
                                font=0.3), S[other[0]].label, 0.4))
        if "hag" in S:
            P.append(title(grid(draw_zones(hag_rgb(hag_m(S, fr)), fr, zones, fill=False, width=1), fr, font=0.3),
                           "lidar canopy", 0.4))
        if "nir" in S:
            P.append(title(grid(draw_zones(cir(S, fr, rgb), fr, zones, fill=False, width=1), fr, font=0.3), "CIR", 0.4))
        if len(other) > 1:
            k = other[min(2, len(other) - 1)]
            P.append(title(grid(draw_zones(_u8(S[k].warp(fr)[..., :3]), fr, zones, fill=False, width=1), fr, font=0.3),
                           S[k].label, 0.4))
        save(tdir(slug, "review", f"h{int(ref):02d}.png"), stack(P[:6], 3))
        log(f"  review {ref}: {len(zones)} zones")


def zoom_render(slug, ref, a0, a1, x0, x1, ppy=8.0, out=None, which="photo"):
    """A zoomed crop (a0-a1 along, x0-x1 lateral) with the trace outlines: the 2nd-pass look at an edge."""
    S = sources(slug)
    fj = frames(slug)[ref]
    zones = trace(slug)["holes"].get(ref, {}).get("zones", []) if os.path.exists(tdir(slug, "trace.py")) else []
    lat = math.ceil(max(abs(x0), abs(x1)) / 10.0) * 10.0          # grid lines on multiples of 5 yds
    fr = corridor_frame(fj["frame"]["tee_ll"], fj["frame"]["aim_ll"], ppy, a0=a0, a1=a1, lat=lat)
    if which == "hag":
        img = hag_rgb(hag_m(S, fr))
    elif which == "cir":
        img = cir(S, fr)
    elif which.startswith("naip_"):
        img = _u8(S[which].warp(fr)[..., :3])
    elif which == "photol":
        img = lidar_contour(_u8(S["photo"].warp(fr)), S, fr)
    elif which == "cirl":
        img = lidar_contour(cir(S, fr), S, fr)
    else:
        img = _u8(S["photo"].warp(fr))
    if zones:
        img = draw_zones(img, fr, zones, fill=False, width=1, a1=a1, lat=lat)
    img = grid(img, fr, a0=a0, a1=a1, lat=lat, step=5, label_every=10, font=0.35)
    img = img[:, int((x0 + lat) * ppy):int((x1 + lat) * ppy)]
    out = out or os.path.join(HERE, slug, "_zoom.png")
    save(out, img)
    return out


def sheet(slug, ref, out, ppy=4.0, with_trace=False):
    """Tracing sheet: NAIP 2023 photo | lidar canopy, same frame, 5-yd grid (10-yd labels)."""
    S = sources(slug)
    fj = frames(slug)[ref]
    fr = frame_of(fj, ppy)
    zones = trace(slug)["holes"].get(ref, {}).get("zones", []) if with_trace else []
    a = _u8(S["photo"].warp(fr))
    b = hag_rgb(hag_m(S, fr))
    if zones:
        a = draw_zones(a, fr, zones, fill=False, width=1)
        b = draw_zones(b, fr, zones, fill=False, width=1)
    P = [title(grid(a, fr, step=5, label_every=10, font=0.33), f"{slug} {ref} par {fj['par']} {fj.get('yards')}: NAIP 2023", 0.4),
         title(grid(b, fr, step=5, label_every=10, font=0.33), "lidar canopy (yel 0.5-2.5, grn 2.5-8, dk > 8 m)", 0.4)]
    save(out, stack(P, 2))
    return out


def sheet4(slug, ref, out, ppy=3.5, with_trace=False, years=("naip_2021",)):
    """4 panels in one row: NAIP 2023 | CIR | an older NAIP year | lidar canopy (5-yd grid)."""
    S = sources(slug)
    fj = frames(slug)[ref]
    fr = frame_of(fj, ppy)
    zones = trace(slug)["holes"].get(ref, {}).get("zones", []) if with_trace else []
    rgb = S["photo"].warp(fr)
    imgs = [(_u8(rgb), f"{slug} {ref} par {fj['par']} {fj.get('yards')}: NAIP 2023"),
            (lidar_contour(cir(S, fr, rgb), S, fr), "CIR 2023 + lidar edge; NW (%+.1f,%+.1f)" % tuple(shadow_dir(fj)))]
    for y in years:
        k = y if y in S else next((k for k in sorted(S, reverse=True) if k.startswith("naip_") and k != "naip_2023"), None)
        if k:
            imgs.append((_u8(S[k].warp(fr)[..., :3]), S[k].label))
    imgs.append((hag_rgb(hag_m(S, fr)), "lidar canopy"))
    P = []
    for im, t in imgs:
        if zones:
            im = draw_zones(im, fr, zones, fill=False, width=1)
        P.append(title(grid(im, fr, step=5, label_every=10, font=0.3), t, 0.38))
    save(out, stack(P, len(P)))
    return out


def ring_ll(fj, xy):
    """yard (x, along) -> WGS84 with the hole's corridor frame."""
    fr = frame_of(fj, 1.0)
    xy = np.asarray(xy, float)
    return fr.yds_to_ll(np.c_[xy[:, 0], -xy[:, 1]])


def stage_build(slug):
    FJ = frames(slug)
    T = trace(slug)
    pkg = package(slug)
    holes = {}
    rnd = lambda a: [[round(float(x), 8), round(float(y), 8)] for x, y in a]      # noqa: E731
    for ref, th in T["holes"].items():
        fj = FJ[ref]
        fr = frame_of(fj, 1.0)
        foot = [(-FOOT["lat"], FOOT["a0"]), (FOOT["lat"], FOOT["a0"]), (FOOT["lat"], FOOT["a1"]), (-FOOT["lat"], FOOT["a1"])]
        holes[ref] = dict(
            key=ref, ref=ref, par=fj["par"], tee_set=fj["set"], card_yards=fj.get("yards"),
            image=f"render/h{int(ref):02d}_photo.png",
            method="hand trace on NAIP 2023 0.3 m + NAIP other years + 3DEP lidar canopy (course_data/truth/corridor.py)",
            frame=dict(fj["frame"], ppy=1.0, tee_px=[0.0, 0.0]),
            tee_ll=rnd([fj["frame"]["tee_ll"]])[0], tee_check=th.get("tee_check", ""),
            dot270_ll=rnd(fr.yds_to_ll([[0.0, -270.0]]))[0],
            green_ll=fj.get("green_ll"),
            footprint_ll=rnd(ring_ll(fj, foot)),
            zones=[dict(lie=z["lie"], poly_ll=rnd(ring_ll(fj, z["xy"])), **({"note": z["note"]} if z.get("note") else {}))
                   for z in th["zones"]],
            note=th.get("note", ""), confidence=th.get("confidence", ""))
    out = dict(doc="Hand-checked landing-corridor zones (par 4 / 5 tee shots of the card set) in WGS84 [lon, lat]. "
                   "Zone order is kept: later zones override earlier ones (tee_strategy.lie_at); unzoned = rough. "
                   "footprint_ll = the mapped corridor (%g-%g yds along the tee line, +/-%g yds): the hand map only "
                   "covers that area. Traced by eye in the corridor frame (frame: render.Frame, UTM, tee / aim of the "
                   "card set from the package; yard frame x right, y = -along) on NAIP 2023 0.3 m with NAIP other years "
                   "and 3DEP lidar canopy; never from a vision layer. Built by course_data/truth/corridor.py build from "
                   "trace.py." % (FOOT["a0"], FOOT["a1"], FOOT["lat"]),
               source=f"course_data/truth/{slug}/trace.py (hand trace; see NOTES.md)",
               course=pkg["course"]["name"], slug=slug, tee_set=tee_set(slug, pkg),
               registration="none needed: traced directly on georeferenced NAIP (the corridor frame is exact)",
               holes=holes, missing=T.get("missing", []))
    json.dump(out, open(tdir(slug, "hand_zones_ll.json"), "w"), indent=1)
    log(f"[{slug}] wrote hand_zones_ll.json: {len(holes)} holes, {sum(len(h['zones']) for h in holes.values())} zones")
    return out


# =========================================================================== second pass: edges near the fairway
def edges(zones, a0=CORE["a0"], a1=CORE["a1"], step=10.0, near=10.0):
    """Per 10 yds along and side: the fairway edge and the first non-mown lie beyond it, flagged when that lie
    starts within `near` yds of the fairway (the edges the 2nd pass re-checks on zoomed renders)."""
    A, X, lie = lie_grid(zones, step=0.5)
    rows = []
    for a in np.arange(a0, a1 + 0.1, step):
        row = lie[int(round((a - A[0]) / 0.5))]
        fw = np.nonzero(row == "fairway")[0]
        if not len(fw):
            rows.append(dict(along=a, fairway=None))
            continue
        c = int(round(np.median(fw)))
        rec = dict(along=a)
        for side, rng in (("L", range(c, -1, -1)), ("R", range(c, len(X)))):
            edge = haz = None
            for j in rng:
                if edge is None and row[j] != "fairway":
                    edge = X[j]
                if edge is not None and row[j] not in ("fairway", "first_cut", "rough"):
                    haz = (row[j], X[j])
                    break
            gap = None if (haz is None or edge is None) else round(abs(haz[1] - edge), 1)
            rec[side] = dict(fw_edge=None if edge is None else float(edge), hazard=None if haz is None else haz[0],
                             hazard_x=None if haz is None else float(haz[1]), gap=gap,
                             near=bool(gap is not None and gap <= near))
        rows.append(rec)
    return rows


def stage_edges(slug, holes=None):
    T = trace(slug)
    for ref, th in T["holes"].items():
        if holes and ref not in holes:
            continue
        rows = edges(th["zones"])
        flag = [(r["along"], s, r[s]) for r in rows if "L" in r for s in ("L", "R") if r[s]["near"]]
        log(f"{ref}: " + ("; ".join(f"{int(a)}{s} fw {d['fw_edge']:+.0f} -> {d['hazard']} {d['hazard_x']:+.0f}"
                                    for a, s, d in flag) or "no hazard within 10 yds of the fairway"))


def stage_notes(slug, header):
    """NOTES.md = the hand-written header (notes_header.md) + per hole: confidence, note, zone notes, 2nd-pass edges."""
    T = trace(slug)
    FJ = frames(slug)
    L_ = [open(header).read().rstrip(), "", "## Per tee shot", ""]
    for ref, th in T["holes"].items():
        fj = FJ[ref]
        n = {}
        for z in th["zones"]:
            n[z["lie"]] = n.get(z["lie"], 0) + 1
        L_ += [f"### {ref} (par {fj['par']}, {fj.get('set')} {fj.get('yards')} yds; tee: {fj.get('tee_method')})", "",
               f"Confidence: {th.get('confidence', '?')}. Zones: " + ", ".join(f"{k} {v}" for k, v in n.items()) + ".", "",
               th.get("note", ""), ""]
        zn = [f"{z['lie']}: {z['note']}" for z in th["zones"] if z.get("note")]
        if zn:
            L_ += ["Zone notes: " + "; ".join(zn) + ".", ""]
        rows = edges(th["zones"])
        near = [f"{int(r['along'])}{s_} {r[s_]['hazard']} {r[s_]['gap']:.0f} yds out" for r in rows if "L" in r
                for s_ in ("L", "R") if r[s_]["near"]]
        L_ += [("Edges within 10 yds of the fairway (re-checked on zoomed photo / CIR / lidar renders): "
                + "; ".join(near) + ".") if near else "No hazard within 10 yds of the fairway edge.", "",
               f"Review: `review/h{int(ref):02d}.png`; evidence: `render/h{int(ref):02d}_evidence.png`.", ""]
    open(tdir(slug, "NOTES.md"), "w").write("\n".join(L_) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["panels", "review", "build", "edges", "zoom", "sheet", "sheet4", "notes"])
    ap.add_argument("--slug", required=True)
    ap.add_argument("--holes")
    ap.add_argument("--box", help="zoom: a0,a1,x0,x1")
    ap.add_argument("--which", default="photo")
    ap.add_argument("--ppy", type=float, default=8.0)
    ap.add_argument("--out")
    a = ap.parse_args()
    hs = set(a.holes.split(",")) if a.holes else None
    if a.stage == "panels":
        stage_panels(a.slug, hs)
    elif a.stage == "review":
        stage_review(a.slug, hs)
    elif a.stage == "build":
        stage_build(a.slug)
    elif a.stage == "edges":
        stage_edges(a.slug, hs)
    elif a.stage == "notes":
        stage_notes(a.slug, tdir(a.slug, "notes_header.md"))
    elif a.stage == "sheet":
        print(sheet(a.slug, a.holes, a.out, with_trace=a.which == "trace"))
    elif a.stage == "sheet4":
        print(sheet4(a.slug, a.holes, a.out, with_trace=a.which == "trace"))
    elif a.stage == "zoom":
        a0, a1, x0, x1 = map(float, a.box.split(","))
        print(zoom_render(a.slug, a.holes, a0, a1, x0, x1, ppy=a.ppy, out=a.out, which=a.which))


if __name__ == "__main__":
    main()
