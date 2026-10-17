"""Geometry corrections for v2 (parity engineer's findings; course.py itself is not changed).

  scale : the hand map is in APP yards (tee -> 270 dot = 270). Measured on the GPS registration
          (course_data/spirit_hollow/hand_zones_ll.json) the 270 dot is 262-277 ground yds out
          (hole 6 x0.968, 16 x1.024). v2 converts each hole's frame to ground yards, so a 275 carry
          lands where 275 real yards are.
  elev  : DEM carry/roll per club measured along the moved Black-tee line (course.py measured it from
          the screenshot tee, up to 25 yds back on 1, 2F, 5, 6, 10, 11, 14, 16, 17), with the same
          soft-course cap (roll factor 0.7-1.3, no side kick).
  green : green centre = OSM green (registered to NAIP). On 6 and 10 the app-trilaterated centre sits
          14 / 11 yds from it, on the front edge of the green in the 2023 NAIP photo.

  set_geometry("scale,elev,green")   # in place on course.HOLES (= model.HOLES); "" = course.py as is
"""
import copy
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.dirname(HERE)
ROOT = os.path.dirname(SH)
sys.path[:0] = [SH, os.path.join(ROOT, "mozingo")]

import course                                   # noqa: E402

ALL = ("scale", "elev", "green")
_ORIG = copy.deepcopy(course.HOLES)
_CACHE = {}


def _hav_yd(a, b):
    R = 6371008.8
    l1, p1 = map(math.radians, a)
    l2, p2 = map(math.radians, b)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin((l2 - l1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h)) / 0.9144


def _geo():
    if "G" not in _CACHE:
        import geo_zones as GZ
        _CACHE["G"] = GZ.transforms_from_json()
        _CACHE["osm"] = json.load(open(os.path.join(ROOT, "course_data", "spirit_hollow", "holes_osm.json")))["holes"]
    return _CACHE["G"], _CACHE["osm"]


def ref(k):
    return int(str(k).rstrip("FB"))


def ground_scale(k, hd):
    G, _ = _geo()
    g = G[k]
    tl, dl = g.px_to_ll([hd["tee"]])[0], g.px_to_ll([hd["dot270"]])[0]
    return _hav_yd(tl, dl) / 270.0


def osm_green_px(k):
    G, O = _geo()
    return tuple(float(x) for x in G[k].ll_to_px([O[str(ref(k))]["green_ll"]])[0])


def black_elev(k, hd):
    key = ("elev", k, tuple(np.round(hd["tee"], 2)))
    if key in _CACHE:
        return _CACHE[key]
    import tee_sets as TS
    G, _ = _geo()
    if "PK" not in _CACHE:
        _CACHE["PK"] = TS.package_holes()
    g = G[k]
    tl, dl = g.px_to_ll([hd["tee"]])[0], g.px_to_ll([hd["dot270"]])[0]
    adj = TS.elevation_along(ref(k), tl, dl, _CACHE["PK"][ref(k)]["green_polygon_ll"], hd["par"])
    lo, hi = course.SOFT_ROLL
    out = {c: (float(v["carry_delta_yds"]), float(min(max(v["roll_factor"], lo), hi)), 0.0)
           for c, v in adj["clubs"].items()}
    _CACHE[key] = out
    return out


def corrected(k, hd, flags):
    hd = copy.deepcopy(hd)
    flags = set(flags)
    if "green" in flags:
        hd["green_hand"] = hd["green"]
        hd["green"] = osm_green_px(k)
    if "elev" in flags and "elev" in hd:
        try:
            hd["elev_screenshot_tee"] = hd["elev"]
            hd["elev"] = black_elev(k, hd)
        except Exception as ex:                       # DEM missing: keep course.py's numbers
            hd["elev_error"] = str(ex)
    if "scale" in flags:
        s = ground_scale(k, hd)
        hd["ground_scale"] = s
        hd["length"] = hd["length"] * s
    return hd


def set_geometry(flags=ALL):
    """Apply the corrections in place on course.HOLES (shared by model.HOLES and wind_grid)."""
    if isinstance(flags, str):
        flags = [f for f in flags.split(",") if f]
    import model as M
    for k in list(course.HOLES):
        new = corrected(k, _ORIG[k], flags)
        course.HOLES[k].clear()
        course.HOLES[k].update(new)
    M._hybrid_elevation()
    return flags


def summary():
    rows = {}
    for k, hd in _ORIG.items():
        try:
            e = black_elev(k, hd)
        except Exception:
            e = {}
        rows[str(k)] = dict(scale=round(ground_scale(k, hd), 4),
                            green_shift_yd=round(float(np.linalg.norm(np.subtract(osm_green_px(k), hd["green"])))
                                                 / (np.linalg.norm(np.subtract(hd["dot270"], hd["tee"])) / 270), 1),
                            drv_carry_delta=[round(hd.get("elev", {}).get("Driver", (0,))[0], 1),
                                             round(e.get("Driver", (0,))[0], 1)],
                            tee_moved=hd.get("tee_moved", 0))
    return rows
