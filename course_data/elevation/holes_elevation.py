"""Per-hole elevation analysis of the Spirit Hollow tee shots on the USGS 3DEP 1 m DEM.

  python course_data/elevation/holes_elevation.py [--out course_data/elevation/spirit_hollow_holes.json]

Every hole in spirit_hollow/course.py is drawn in its GPS-app screenshot's own 920x2000 frame (the app
rotates the hole to point up the screen), so we first need where the tee and the tee line are on the
ground. Two independent estimates per hole:

  "anchor"  (geometric, used by default)
      tee   = the OSM/scorecard tee (course_data/tees/tee_positions.json) whose distance to the green
              best matches the screenshot's tee->green distance (from the app's three "Center" numbers,
              course.green_from_app); for par 3s the Black tee (the golfer's tee).
      green = centroid of the OSM green polygon at the end of the OSM hole line.
      line  = the tee->green bearing rotated back by the green's angle off the tee line in the
              screenshot, atan2(lateral, along). The 270-yd point is 270 yds along that bearing.
  "ecc"     image registration of the screenshot onto NAIP (course_data/imagery/traced_align.py,
            run for every hole into course_data/elevation/spirit_hollow/registration.json); reported
            for comparison (bearing and tee offset vs the anchor), used only with --geometry ecc.

Elevations are bilinear samples of the DEM (metres NAVD88, reported in feet and metres):
  tee        mean over a 6 x 6 yd box round the tee
  landing    at 240/270/300 yds along the line, mean over +-10 yds laterally (2-yd steps), +-3 yds along
  green      mean of the DEM inside the OSM green polygon
  slope      least-squares plane over the 240-320 yd x +-15 yd landing box: along-line grade (% , + =
             uphill away from the tee), cross grade (%, + = ground rises to the golfer's right, so the
             ball kicks left), magnitude and the fall-line direction (deg clockwise from the tee line)
  profile    every 10 yds from the tee to the green's along-line distance: centre line (m, ft_rel_tee)
             and the +-10 yd lateral mean (band_ft_rel_tee, what adjust.py flies the ball onto)
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "spirit_hollow"), ROOT]

YD = 0.9144
FT = 0.3048
DEM_DIRS = [os.path.join(HERE, "spirit_hollow"), os.path.join(ROOT, "course_data", "imagery", "spirit_hollow")]
OSM = os.path.join(ROOT, "course_data", "spirit_hollow", "osm.geojson")
TEES = os.path.join(ROOT, "course_data", "tees", "tee_positions.json")
REG = [os.path.join(ROOT, "course_data", "imagery", "spirit_hollow", "traced_registration.json"),
       os.path.join(HERE, "spirit_hollow", "registration.json")]
PAR3_TEE = "Black"


# --------------------------------------------------------------------------- DEM
class Dem:
    def __init__(self, path=None):
        import rasterio
        from pyproj import Transformer
        if path is None:
            path = next(os.path.join(d, "dem.tif") for d in DEM_DIRS if os.path.exists(os.path.join(d, "dem.tif")))
        self.path = path
        with rasterio.open(path) as src:
            self.z = src.read(1).astype(np.float64)
            self.tr = src.transform
            self.epsg = src.crs.to_epsg()
        self.inv = ~self.tr
        self._fwd = Transformer.from_crs("EPSG:4326", f"EPSG:{self.epsg}", always_xy=True)
        self._back = Transformer.from_crs(f"EPSG:{self.epsg}", "EPSG:4326", always_xy=True)
        self.res = abs(self.tr.a)

    def xy(self, lonlat):
        ll = np.atleast_2d(np.asarray(lonlat, float))
        x, y = self._fwd.transform(ll[:, 0], ll[:, 1])
        return np.c_[x, y]

    def ll(self, xy):
        xy = np.atleast_2d(np.asarray(xy, float))
        lon, lat = self._back.transform(xy[:, 0], xy[:, 1])
        return np.c_[lon, lat]

    def sample(self, xy):
        """Bilinear elevation (m) at projected points (N, 2)."""
        xy = np.atleast_2d(np.asarray(xy, float))
        c, r = self.inv * (xy[:, 0], xy[:, 1])
        c, r = np.asarray(c) - 0.5, np.asarray(r) - 0.5
        c0, r0 = np.floor(c).astype(int), np.floor(r).astype(int)
        fc, fr = c - c0, r - r0
        H, W = self.z.shape
        ok = (c0 >= 0) & (r0 >= 0) & (c0 + 1 < W) & (r0 + 1 < H)
        c0, r0 = np.clip(c0, 0, W - 2), np.clip(r0, 0, H - 2)
        z = (self.z[r0, c0] * (1 - fc) * (1 - fr) + self.z[r0, c0 + 1] * fc * (1 - fr)
             + self.z[r0 + 1, c0] * (1 - fc) * fr + self.z[r0 + 1, c0 + 1] * fc * fr)
        return np.where(ok, z, np.nan)


# --------------------------------------------------------------------------- geometry helpers
def bearing_of(u):
    """Compass bearing (deg true, approx: grid north of UTM differs by < 1 deg here) of (east, north)."""
    return math.degrees(math.atan2(u[0], u[1])) % 360


def unit_from_bearing(b):
    return np.array([math.sin(math.radians(b)), math.cos(math.radians(b))])


def grid_convergence(dem, lonlat):
    """Angle (deg) from true north to grid north at a point: true bearing = grid bearing + this."""
    p = dem.xy(lonlat)[0]
    n = dem.xy([lonlat[0], lonlat[1] + 0.001])[0] - p
    return -math.degrees(math.atan2(n[0], n[1]))


def poly_centroid(P):
    P = np.asarray(P, float)
    x, y = P[:, 0], P[:, 1]
    a = x * np.roll(y, -1) - np.roll(x, -1) * y
    A = a.sum() / 2
    return np.array([((x + np.roll(x, -1)) * a).sum() / (6 * A), ((y + np.roll(y, -1)) * a).sum() / (6 * A)])


def osm_layers():
    fc = json.load(open(OSM))
    lines = {str(f["properties"].get("ref")): f["geometry"]["coordinates"] for f in fc["features"]
             if f["properties"].get("golf") == "hole" and f["geometry"]["type"] == "LineString"}
    greens = [f["geometry"]["coordinates"][0] for f in fc["features"]
              if f["properties"].get("golf") == "green" and f["geometry"]["type"] == "Polygon"]
    teeboxes = [(f["properties"].get("osm_id"), f["geometry"]["coordinates"][0]) for f in fc["features"]
                if f["properties"].get("golf") == "tee" and f["geometry"]["type"] == "Polygon"]
    return lines, greens, teeboxes


def green_poly_xy(dem, line_ll, greens):
    """Projected polygon of the OSM green nearest the end of the hole line."""
    from matplotlib.path import Path
    end = dem.xy(line_ll[-1])[0]
    best = None
    for g in greens:
        P = dem.xy(g)
        d = 0.0 if Path(P).contains_point(end) else float(np.min(np.linalg.norm(P - end, axis=1)))
        if best is None or d < best[0]:
            best = (d, P)
    return best[1], best[0]


def ref_of(k):
    return str(k)[:-1] if isinstance(k, str) else str(k)


def screenshot_green(course, k):
    """Green centre in the screenshot's tee-line frame: (yds along, yds right)."""
    if k in course.PAR3:
        return float(course.PAR3[k]["center"]), 0.0
    if course.GREEN_SIDE[k] == 0:
        return 270.0 + course.APP[k][1], 0.0
    a, l = course.green_from_app(*course.APP[k], course.GREEN_SIDE[k])
    return float(a), float(l)


def seg_dist(P, A, B):
    d = B - A
    t = np.clip(((P - A) @ d) / max(d @ d, 1e-9), 0, 1)
    return np.linalg.norm(P - (A + t * d))


def tee_candidates(dem, k, line, teeboxes, tees):
    """Scorecard tees (tee_positions.json) + every OSM tee-box centroid within 35 m of the hole line's
    first leg (or of its start), as (label, projected xy, method, confidence)."""
    out = []
    for c, t in tees["holes"][ref_of(k)]["tees"].items():
        out.append((c, dem.xy([t["lon"], t["lat"]])[0], t.get("method"), t.get("confidence")))
    L = dem.xy(line)
    for oid, poly in teeboxes:
        c = poly_centroid(dem.xy(poly))
        if min(seg_dist(c, L[0], L[1]), np.linalg.norm(c - L[0])) < 35:
            out.append((f"osm_tee_{oid}", c, "osm_tee_centroid", "n/a"))
    return out


def anchor_geometry(dem, course, k, lines, greens, tees, teeboxes=()):
    """Tee (projected m), unit tee-line vector (grid east/north), method notes."""
    line = lines[ref_of(k)]
    gpoly, gdist = green_poly_xy(dem, line, greens)
    g_xy = poly_centroid(gpoly)
    along, lat = screenshot_green(course, k)
    d_app = math.hypot(along, lat)
    cand = tee_candidates(dem, k, line, teeboxes, tees)
    if k in course.PAR3:
        colour, tee_xy, tmeth, tconf = next(c for c in cand if c[0] == PAR3_TEE)
    else:
        colour, tee_xy, tmeth, tconf = min(cand, key=lambda c: abs(np.linalg.norm(c[1] - g_xy) / YD - d_app))
    v = g_xy - tee_xy
    d_world = np.linalg.norm(v) / YD
    phi = math.atan2(lat, along)                       # green is phi clockwise of the tee line
    b_green = math.degrees(math.atan2(v[0], v[1]))
    u = unit_from_bearing(b_green - math.degrees(phi))
    return dict(tee_xy=tee_xy, u=u, green_poly=gpoly, green_xy=g_xy,
                notes=dict(method="anchor", tee=colour, tee_method=tmeth,
                           tee_confidence=tconf, green_offset_from_line_end_m=round(gdist, 1),
                           app_tee_to_green_yd=round(d_app, 1), map_tee_to_green_yd=round(d_world, 1),
                           green_angle_off_line_deg=round(math.degrees(phi), 1)))


def ecc_geometry(dem, k):
    """Tee + tee line from the NAIP image registration (screenshot tee / 270 dot -> lon/lat)."""
    import course
    sys.path.insert(0, os.path.join(ROOT, "course_data", "imagery"))
    import traced_align as T
    for p in REG:
        if os.path.exists(p):
            reg = json.load(open(p)).get(str(k))
            if reg and reg.get("warp"):
                h = course.HOLES[k]
                ll = T.screenshot_px_to_ll(reg, [h["tee"], h["dot270"]])
                a, b = dem.xy(ll)
                return dict(tee_xy=a, u=(b - a) / np.linalg.norm(b - a),
                            scale_270_yd=float(np.linalg.norm(b - a) / YD),
                            quality=dict(corr=reg.get("corr"), ecc=reg.get("ecc"), source=os.path.relpath(p, ROOT)))
    return None


# --------------------------------------------------------------------------- measurements
def pts(tee_xy, u, along_yd, lat_yd):
    r = np.array([u[1], -u[0]])                        # golfer's right
    A, L = np.meshgrid(np.atleast_1d(along_yd), np.atleast_1d(lat_yd), indexing="ij")
    P = tee_xy + (A.reshape(-1, 1) * u + L.reshape(-1, 1) * r) * YD
    return P, A.ravel(), L.ravel()


def plane_fit(dem, tee_xy, u, a0, a1, half_w, step=4.0):
    P, A, L = pts(tee_xy, u, np.arange(a0, a1 + 1e-9, step), np.arange(-half_w, half_w + 1e-9, 2.0))
    z = dem.sample(P)
    ok = np.isfinite(z)
    X = np.c_[np.ones(ok.sum()), A[ok] * YD, L[ok] * YD]
    coef, res, *_ = np.linalg.lstsq(X, z[ok], rcond=None)
    rms = float(np.sqrt(np.mean((X @ coef - z[ok]) ** 2)))
    g_al, g_lat = coef[1] * 100, coef[2] * 100
    mag = math.hypot(g_al, g_lat)
    # downhill direction in (along, right) = -(g_al, g_lat); angle clockwise from the tee line
    fall = math.degrees(math.atan2(-g_lat, -g_al)) % 360 if mag > 0 else 0.0
    return dict(along_pct=round(g_al, 2), cross_pct=round(g_lat, 2), magnitude_pct=round(mag, 2),
                fall_line_deg_cw_from_line=round(fall, 0), residual_rms_m=round(rms, 2),
                box=dict(along_yd=[a0, a1], lateral_yd=[-half_w, half_w]))


def m2(z):
    return dict(m=round(float(z), 2), ft=round(float(z) / FT, 1))


def analyse(dem, course, k, geo):
    tee_xy, u = geo["tee_xy"], geo["u"]
    out = {}
    P, _, _ = pts(tee_xy, u, np.arange(-3, 3.1, 1.5), np.arange(-3, 3.1, 1.5))
    z_tee = float(np.nanmean(dem.sample(P)))
    tee_ll = dem.ll(tee_xy)[0]
    conv = grid_convergence(dem, tee_ll)
    out["tee_ll"] = [round(tee_ll[0], 7), round(tee_ll[1], 7)]
    out["p270_ll"] = [round(x, 7) for x in dem.ll(tee_xy + 270 * YD * u)[0]]
    out["bearing_deg_true"] = round((bearing_of(u) + conv) % 360, 1)
    out["tee_elev"] = m2(z_tee)
    land = {}
    for d in (240, 270, 300):
        P, _, _ = pts(tee_xy, u, np.arange(d - 3, d + 3.1, 3), np.arange(-10, 10.1, 2))
        z = float(np.nanmean(dem.sample(P)))
        land[str(d)] = dict(m=round(z, 2), ft=round(z / FT, 1), delta_ft=round((z - z_tee) / FT, 1),
                            delta_m=round(z - z_tee, 2))
    from matplotlib.path import Path
    gp = geo["green_poly"]
    x0, y0 = gp.min(axis=0)
    x1, y1 = gp.max(axis=0)
    gx, gy = np.meshgrid(np.arange(x0, x1, 1.0), np.arange(y0, y1, 1.0))
    G = np.c_[gx.ravel(), gy.ravel()]
    G = G[Path(gp).contains_points(G)]
    z_green = float(np.nanmean(dem.sample(G))) if len(G) else float(dem.sample(geo["green_xy"])[0])
    g_rel = geo["green_xy"] - tee_xy
    r = np.array([u[1], -u[0]])
    g_along, g_lat = float(g_rel @ u / YD), float(g_rel @ r / YD)
    out["green"] = dict(m=round(z_green, 2), ft=round(z_green / FT, 1), delta_ft=round((z_green - z_tee) / FT, 1),
                        along_yd=round(g_along, 1), lateral_yd=round(g_lat, 1))
    if k in course.PAR3:
        out["landing"] = None
        out["landing_slope"] = None
        # green surface plane in the tee-line frame
        X = np.c_[np.ones(len(G)), (G - tee_xy) @ u, (G - tee_xy) @ r]
        zg = dem.sample(G)
        c, *_ = np.linalg.lstsq(X, zg, rcond=None)
        out["green_slope"] = dict(along_pct=round(c[1] * 100, 2), cross_pct=round(c[2] * 100, 2))
    else:
        out["landing"] = land
        out["landing_slope"] = plane_fit(dem, tee_xy, u, 240, 320, 15)
        out["slope_by_zone"] = {f"{a}-{a + 40}": plane_fit(dem, tee_xy, u, a, a + 40, 15) for a in (200, 240, 280)}
    end = max(10, int(math.floor(g_along / 10.0)) * 10)
    A = np.arange(0, end + 1, 10)
    P, _, _ = pts(tee_xy, u, A, [0.0])
    z = dem.sample(P)
    lat = np.arange(-10, 10.1, 2)
    Pb, _, _ = pts(tee_xy, u, A, lat)
    zb = np.nanmean(dem.sample(Pb).reshape(len(A), len(lat)), axis=1)
    out["profile"] = [dict(yd=int(a), m=round(float(zz), 2), ft_rel_tee=round(float(zz - z_tee) / FT, 1),
                           band_ft_rel_tee=round(float(bb - z_tee) / FT, 1))
                      for a, zz, bb in zip(A, z, zb)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "spirit_hollow_holes.json"))
    ap.add_argument("--geometry", choices=["anchor", "ecc"], default="anchor")
    ap.add_argument("--dem")
    a = ap.parse_args()
    import course
    dem = Dem(a.dem)
    lines, greens, teeboxes = osm_layers()
    tees = json.load(open(TEES))
    gj = os.path.join(os.path.dirname(dem.path), "georef.json")
    meta = json.load(open(gj)) if os.path.exists(gj) else {}
    dmeta = meta.get("dem", meta)
    res = dict(dem=dict(file=os.path.relpath(dem.path, ROOT), source=dmeta.get("source"),
                        resolution_m=dem.res, epsg=dem.epsg),
               geometry=a.geometry,
               conventions=dict(
                   bearing="compass degrees true of the tee line (tee -> 270-yd point)",
                   delta_ft="elevation minus tee elevation (+ = uphill)",
                   along_pct="+ = ground rises going away from the tee (upslope landing)",
                   cross_pct="+ = ground rises to the golfer's right (ball kicks left)",
                   fall_line="direction of steepest descent, deg clockwise from the tee line "
                             "(0 = straight away, 90 = to the right, 180 = back toward the tee)"),
               holes={})
    keys = list(course.HOLES) + list(course.PAR3)
    for k in keys:
        geo_a = anchor_geometry(dem, course, k, lines, greens, tees, teeboxes)
        geo_e = ecc_geometry(dem, k) if k in course.HOLES else None
        geo = dict(geo_a)
        if a.geometry == "ecc" and geo_e:
            geo.update(tee_xy=geo_e["tee_xy"], u=geo_e["u"])
        rec = dict(par=3 if k in course.PAR3 else course.HOLES[k]["par"],
                   length_yd=int(course.PAR3[k]["center"]) if k in course.PAR3 else int(course.HOLES[k]["length"]))
        rec.update(analyse(dem, course, k, geo))
        rec["geometry"] = geo_a["notes"]
        if geo_e:
            de = geo_e["tee_xy"] - geo_a["tee_xy"]
            db = (bearing_of(geo_e["u"]) - bearing_of(geo_a["u"]) + 180) % 360 - 180
            alt = analyse(dem, course, k, dict(geo_a, tee_xy=geo_e["tee_xy"], u=geo_e["u"]))
            rec["ecc_check"] = dict(tee_offset_yd=round(float(np.linalg.norm(de)) / YD, 1),
                                    bearing_diff_deg=round(db, 1), scale_270_yd=round(geo_e["scale_270_yd"], 1),
                                    landing_270_delta_ft=alt["landing"]["270"]["delta_ft"],
                                    landing_slope_along_pct=alt["landing_slope"]["along_pct"],
                                    landing_slope_cross_pct=alt["landing_slope"]["cross_pct"],
                                    quality=geo_e["quality"])
        res["holes"][str(k)] = rec
        L = rec["landing"]
        print(f"{str(k):>3} par {rec['par']} brg {rec['bearing_deg_true']:6.1f}  tee {rec['tee_elev']['ft']:6.1f} ft"
              + (f"  270 {L['270']['delta_ft']:+6.1f} ft  slope along {rec['landing_slope']['along_pct']:+5.1f}% "
                 f"cross {rec['landing_slope']['cross_pct']:+5.1f}%" if L else "")
              + f"  green {rec['green']['delta_ft']:+6.1f} ft"
              + (f"  [ecc: tee {rec['ecc_check']['tee_offset_yd']:.0f} yd, brg {rec['ecc_check']['bearing_diff_deg']:+.1f}]"
                 if geo_e else ""))
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
