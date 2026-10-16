"""Render georeferenced overhead imagery into a hole's 920 x 2000 "screen frame".

The screen frame is the one spirit_hollow/screenshots and mozingo/yardage_book.py use: the tee near the
bottom, the tee line pointing straight up the screen, `ppy` pixels per yard, `draw_image` shows it with
extent (0, 920, 2000, 0). A Frame maps screen px <-> WGS84 exactly, so tee, dot270, zones and the image
always line up.

  # CLI: any tee / target pair
  python3 course_data/imagery/render.py --imagery course_data/imagery/spirit_hollow \
      --tee 40.76066,-91.15143 --target 40.7640,-91.1521 [--ppy 3.4 --tee-px 460,1900] --out hole.png
  # every hole of a geometry build (course_data/<slug>/auto_holes.json, frames reproduced exactly)
  python3 course_data/imagery/render.py --imagery course_data/imagery/spirit_hollow \
      --auto course_data/spirit_hollow --holes 5,17 --out-dir course_data/imagery/spirit_hollow/images

Python:
  fr = Frame.from_ll(tee_ll=(lon, lat), aim_ll=(lon, lat))           # ARCHITECTURE.md virtual frame
  img, info = render(fr, Imagery("course_data/imagery/spirit_hollow"))
  info["tee_px"], info["dot270_px"], fr.ll_to_px([[lon, lat], ...]), fr.px_to_ll(...)

Two planar projections are supported, because the two frame conventions in the repo differ by the UTM
grid convergence (~1.2 deg at Burlington, ~6 yds lateral at 300 yds):
  proj="enu"  equirectangular about the tee (ARCHITECTURE.md section 2, osm_to_model.Frame)
  proj="utm"  WGS84 UTM zone of the tee, in yards (course_data/geometry/build_holes.py)
"""
import argparse
import json
import math
import os

import numpy as np

YD = 0.9144
W, H = 920, 2000
HERE = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------- frame
class Frame:
    """screen px (x right, y down) <-> planar yards <-> WGS84 [lon, lat]."""

    def __init__(self, tee_ll, aim_ll, ppy=3.4, tee_px=(460.0, 1900.0), proj="enu", size=(W, H)):
        self.tee_ll = (float(tee_ll[0]), float(tee_ll[1]))
        self.aim_ll = (float(aim_ll[0]), float(aim_ll[1]))
        self.ppy = float(ppy)
        self.tee_px = np.array(tee_px, float)
        self.proj = proj
        self.size = tuple(size)
        lon0, lat0 = self.tee_ll
        if proj == "enu":
            self.k = math.cos(math.radians(lat0))
        elif proj == "utm":
            from pyproj import Transformer
            epsg = (32600 if lat0 >= 0 else 32700) + int((lon0 + 180) // 6) + 1
            self.epsg = epsg
            self._fwd_tr = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
            self._inv_tr = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
        else:
            raise ValueError(proj)
        self.t0 = self._to_yd(np.array([self.tee_ll]))[0]
        d = self._to_yd(np.array([self.aim_ll]))[0] - self.t0
        self.f = d / np.linalg.norm(d)                        # forward (east, north)
        self.r = np.array([self.f[1], -self.f[0]])            # golfer's right

    @classmethod
    def from_ll(cls, tee_ll, aim_ll, **kw):
        return cls(tee_ll, aim_ll, **kw)

    # planar yards (east, north)
    def _to_yd(self, ll):
        ll = np.atleast_2d(np.asarray(ll, float))
        if self.proj == "enu":
            lon0, lat0 = self.tee_ll
            return np.c_[(ll[:, 0] - lon0) * self.k, ll[:, 1] - lat0] * 111320.0 / YD
        x, y = self._fwd_tr.transform(ll[:, 0], ll[:, 1])
        return np.c_[x, y] / YD

    def _from_yd(self, en):
        en = np.atleast_2d(en)
        if self.proj == "enu":
            lon0, lat0 = self.tee_ll
            m = en * YD / 111320.0
            return np.c_[lon0 + m[:, 0] / self.k, lat0 + m[:, 1]]
        lon, lat = self._inv_tr.transform(en[:, 0] * YD, en[:, 1] * YD)
        return np.c_[lon, lat]

    # model yard frame (x = yds right, y = -yds along), as ARCHITECTURE.md
    def ll_to_yds(self, ll):
        d = self._to_yd(ll) - self.t0
        return np.c_[d @ self.r, -(d @ self.f)]

    def yds_to_ll(self, xy):
        xy = np.atleast_2d(np.asarray(xy, float))
        en = self.t0 + xy[:, :1] * self.r - xy[:, 1:2] * self.f
        return self._from_yd(en)

    def ll_to_px(self, ll):
        return self.tee_px + self.ll_to_yds(ll) * self.ppy

    def px_to_ll(self, px):
        return self.yds_to_ll((np.atleast_2d(np.asarray(px, float)) - self.tee_px) / self.ppy)

    def point_px(self, along, right=0.0):
        """Screen px of the point `along` yds up the tee line and `right` yds right of it."""
        return self.tee_px + np.array([right, -along]) * self.ppy

    def to_json(self):
        return dict(tee_ll=list(self.tee_ll), aim_ll=list(self.aim_ll), ppy=self.ppy,
                    tee_px=[float(v) for v in self.tee_px], proj=self.proj, size=list(self.size),
                    dot270_px=[float(v) for v in self.point_px(270)])

    @classmethod
    def from_json(cls, d):
        return cls(d["tee_ll"], d["aim_ll"], d["ppy"], d["tee_px"], d.get("proj", "enu"), d.get("size", (W, H)))


# --------------------------------------------------------------------------- imagery
class Imagery:
    """A georeferenced image: the COG(s) via rasterio, or the plain JPEGs + georef.json."""

    def __init__(self, path, prefer="cog"):
        self.dir = path if os.path.isdir(path) else os.path.dirname(path)
        gj = os.path.join(self.dir, "georef.json")
        self.meta = json.load(open(gj)) if os.path.exists(gj) else {}
        im = self.meta.get("imagery", {})
        self.date = ",".join(im.get("acquired", [])) or None
        self.source = im.get("source")
        self._rio = None
        files = im.get("files", {})
        rgb_tif = os.path.join(self.dir, files.get("rgb", "naip_rgb.tif"))
        if os.path.isfile(path) and path.endswith(".tif"):
            rgb_tif = path
        use_cog = prefer == "cog" and os.path.exists(rgb_tif)
        if use_cog:
            try:
                import rasterio
                self._rio = rasterio
            except ImportError:
                use_cog = False
        if use_cog:
            self.rgb_path = rgb_tif
            nir = os.path.join(self.dir, files.get("nir", "naip_nir.tif"))
            self.nir_path = nir if os.path.exists(nir) else None
            with rasterio.open(rgb_tif) as src:
                self.crs = src.crs.to_string()
                self.transform = list(src.transform)[:6]
                self.width, self.height = src.width, src.height
            self.kind = "cog"
        else:
            lo = im["lo"]
            from PIL import Image
            Image.MAX_IMAGE_PIXELS = None
            self.rgb = np.asarray(Image.open(os.path.join(self.dir, lo["files"]["rgb"])).convert("RGB"))
            nf = lo["files"].get("nir")
            self.nir = np.asarray(Image.open(os.path.join(self.dir, nf))) if nf else None
            self.crs = im["crs"]
            self.transform = lo["transform"]
            self.height, self.width = self.rgb.shape[:2]
            self.kind = "jpeg"
        a, b, c, d, e, f = self.transform
        self.res = math.hypot(a, d)
        from pyproj import Transformer
        self._ll2crs = Transformer.from_crs("EPSG:4326", self.crs, always_xy=True)

    def ll_to_colrow(self, ll):
        ll = np.atleast_2d(ll)
        x, y = self._ll2crs.transform(ll[:, 0], ll[:, 1])
        a, b, c, d, e, f = self.transform
        det = a * e - b * d
        dx, dy = np.asarray(x) - c, np.asarray(y) - f
        return np.c_[(e * dx - b * dy) / det, (-d * dx + a * dy) / det]   # pixel-corner coords

    def read_window(self, c0, r0, c1, r1, nir=False):
        """uint8 (h, w, bands) for the integer window [c0,c1) x [r0,r1), zero outside the raster."""
        c0, r0, c1, r1 = int(c0), int(r0), int(c1), int(r1)
        out = np.zeros((r1 - r0, c1 - c0, 4 if nir else 3), np.uint8)
        cc0, rr0 = max(c0, 0), max(r0, 0)
        cc1, rr1 = min(c1, self.width), min(r1, self.height)
        if cc1 <= cc0 or rr1 <= rr0:
            return out
        if self.kind == "cog":
            from rasterio.windows import Window
            win = Window(cc0, rr0, cc1 - cc0, rr1 - rr0)
            with self._rio.open(self.rgb_path) as src:
                rgb = np.moveaxis(src.read([1, 2, 3], window=win), 0, -1)
            out[rr0 - r0:rr1 - r0, cc0 - c0:cc1 - c0, :3] = rgb
            if nir and self.nir_path:
                with self._rio.open(self.nir_path) as src:
                    out[rr0 - r0:rr1 - r0, cc0 - c0:cc1 - c0, 3] = src.read(1, window=win)
        else:
            out[rr0 - r0:rr1 - r0, cc0 - c0:cc1 - c0, :3] = self.rgb[rr0:rr1, cc0:cc1]
            if nir and self.nir is not None:
                out[rr0 - r0:rr1 - r0, cc0 - c0:cc1 - c0, 3] = self.nir[rr0:rr1, cc0:cc1]
        return out


# --------------------------------------------------------------------------- render
def sample_maps(fr, img, step=8):
    """Source (col, row) pixel-centre coords for every screen pixel (exact on a grid, bilinear between)."""
    Wd, Hd = fr.size
    gx = np.arange(0, Wd + step, step, dtype=float)
    gy = np.arange(0, Hd + step, step, dtype=float)
    GX, GY = np.meshgrid(gx, gy)
    ll = fr.px_to_ll(np.c_[GX.ravel() + 0.5, GY.ravel() + 0.5])
    cr = img.ll_to_colrow(ll) - 0.5                            # -> pixel-centre index space
    import cv2
    cg = cr[:, 0].reshape(GX.shape).astype(np.float32)
    rg = cr[:, 1].reshape(GX.shape).astype(np.float32)
    # the map is affine to < 1e-4 px over a hole; upsample the grid linearly
    big = (int(len(gx) - 1) * step + 1, int(len(gy) - 1) * step + 1)
    cm = cv2.resize(cg, big, interpolation=cv2.INTER_LINEAR)[:Hd, :Wd]
    rm = cv2.resize(rg, big, interpolation=cv2.INTER_LINEAR)[:Hd, :Wd]
    return cm, rm


def render(fr, img, nir=False, pad=4):
    """-> (H x W x 3|4 uint8 screen image, info dict)."""
    import cv2
    cm, rm = sample_maps(fr, img)
    c0, c1 = math.floor(cm.min()) - pad, math.ceil(cm.max()) + pad
    r0, r1 = math.floor(rm.min()) - pad, math.ceil(rm.max()) + pad
    src = img.read_window(c0, r0, c1, r1, nir=nir)
    src_per_out = img.res / (YD / fr.ppy)                      # source px per screen px
    if src_per_out > 1.4:                                      # downsampling: pre-blur against aliasing
        s = 0.5 * src_per_out
        src = cv2.GaussianBlur(src, (0, 0), s)
    out = cv2.remap(src, cm - c0, rm - r0, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    valid = (cm >= -0.5) & (cm <= img.width - 0.5) & (rm >= -0.5) & (rm <= img.height - 0.5)
    info = dict(frame=fr.to_json(), tee_px=[float(v) for v in fr.tee_px],
                dot270_px=[float(v) for v in fr.point_px(270)],
                yds_per_px=1 / fr.ppy, source_res_m=img.res, imagery_date=img.date,
                imagery_source=img.source, no_imagery_frac=round(float(1 - valid.mean()), 4))
    return out, info


# --------------------------------------------------------------------------- frames from repo data
def _osm_holes(course_dir):
    fc = json.load(open(os.path.join(course_dir, "osm.geojson")))
    return {str(f["properties"].get("ref")): f["geometry"]["coordinates"] for f in fc["features"]
            if f["properties"].get("golf") == "hole" and f["geometry"]["type"] == "LineString"}


def aim_point(tee_ll, line_ll, proj="utm", min_leg=60.0):
    """First hole-line node >= min_leg yds from the tee (the ARCHITECTURE.md / build_holes aim rule)."""
    fr = Frame(tee_ll, line_ll[-1], proj=proj)
    dist = np.linalg.norm(fr._to_yd(line_ll) - fr.t0, axis=1)
    for p, d in zip(line_ll, dist):
        if d >= min_leg:
            return tuple(p)
    return tuple(line_ll[-1])


def frame_for_auto_hole(hole, osm_line):
    """Reproduce course_data/geometry/build_holes.py's frame for one auto_holes.json hole."""
    tee_ll = hole["lonlat_tee"]
    aim = aim_point(tee_ll, osm_line, proj="utm")
    return Frame(tee_ll, aim, ppy=hole["px_per_yd"], tee_px=hole["tee"], proj="utm")


def frame_for_spec_hole(hole):
    """ARCHITECTURE.md hole dict (tee_ll, aim_ll) -> the virtual pixel frame (ppy 3.4, tee (460, 1900))."""
    return Frame(hole["tee_ll"], hole["aim_ll"], ppy=3.4, tee_px=(460, 1900), proj="enu")


def render_hole(course_dir, hole, out_png, frame=None, imagery=None, nir=False):
    """S5 entry point. `hole`: a dict with tee_ll/aim_ll (spec) or an auto_holes.json hole (+ 'ref')."""
    from PIL import Image
    if frame is None:
        if "tee_ll" in hole:
            frame = frame_for_spec_hole(hole)
        else:
            frame = frame_for_auto_hole(hole, _osm_holes(course_dir)[str(hole["ref"])])
    elif isinstance(frame, dict):
        frame = Frame.from_json(frame)
    slug = os.path.basename(os.path.normpath(course_dir))
    img = imagery or Imagery(os.path.join(HERE, slug))
    out, info = render(frame, img, nir=nir)
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    Image.fromarray(out[..., :3]).save(out_png, optimize=True)
    if nir:
        Image.fromarray(out[..., 3]).save(out_png.replace(".png", "_nir.png"), optimize=True)
    info["image"] = os.path.basename(out_png)
    return info


# --------------------------------------------------------------------------- CLI
def _ll(s):
    lat, lon = map(float, s.split(","))
    return (lon, lat)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--imagery", default=os.path.join(HERE, "spirit_hollow"))
    ap.add_argument("--tee", type=_ll, help="lat,lon")
    ap.add_argument("--target", type=_ll, help="lat,lon of the aim point / green")
    ap.add_argument("--ppy", type=float, default=None, help="px per yd (default: fit the target, 2.5-5)")
    ap.add_argument("--tee-px", default="460,1900")
    ap.add_argument("--proj", default="enu", choices=["enu", "utm"])
    ap.add_argument("--auto", help="course dir with auto_holes.json + osm.geojson")
    ap.add_argument("--holes", help="comma list of refs (with --auto)")
    ap.add_argument("--nir", action="store_true")
    ap.add_argument("--out", default="hole.png")
    ap.add_argument("--out-dir")
    a = ap.parse_args()
    img = Imagery(a.imagery)
    from PIL import Image
    if a.auto:
        holes = json.load(open(os.path.join(a.auto, "auto_holes.json")))["holes"]
        lines = _osm_holes(a.auto)
        refs = a.holes.split(",") if a.holes else list(holes)
        out_dir = a.out_dir or os.path.join(a.imagery, "images")
        index = {}
        for ref in refs:
            fr = frame_for_auto_hole(holes[ref], lines[ref])
            out, info = render(fr, img, nir=a.nir)
            p = os.path.join(out_dir, f"hole{int(ref):02d}.png")
            os.makedirs(out_dir, exist_ok=True)
            Image.fromarray(out[..., :3]).save(p, optimize=True)
            index[ref] = info
            print(ref, p, info["tee_px"], info["dot270_px"], info["no_imagery_frac"])
        with open(os.path.join(out_dir, "index.json"), "w") as fh:
            json.dump(index, fh, indent=1)
        return
    tx, ty = map(float, a.tee_px.split(","))
    ppy = a.ppy
    if ppy is None:
        d = np.linalg.norm(Frame(a.tee, a.target, proj=a.proj).ll_to_yds([a.target]))
        ppy = float(np.clip((ty - 600) / max(d, 1), 2.5, 5.0))
    fr = Frame(a.tee, a.target, ppy=ppy, tee_px=(tx, ty), proj=a.proj)
    out, info = render(fr, img, nir=a.nir)
    Image.fromarray(out[..., :3]).save(a.out, optimize=True)
    info["target_px"] = [float(v) for v in fr.ll_to_px([a.target])[0]]
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
