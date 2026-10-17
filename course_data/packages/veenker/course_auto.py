"""Course module for Veenker Memorial Golf Course (Blue tees), generated from package.json by
course_data/platform/package.py on 2026-10-17T00:46:59Z. Do not edit; rebuild with

  python course_data/platform/package.py build course_data/requests/package_veenker.json

Same API as spirit_hollow/course.py (HOLES, PAR3, NOTES, AIM_AT, ORDER, LABELS, APP, GREEN_SIDE) in each
hole's 920 x 2000 pixel frame (px = tee_px + ppy * yard-frame point), so mozingo/tee_strategy.py and
mozingo/yardage_book.use_course() take it unchanged:

  yb.use_course(NAME, DIR, PREFIX, HOLES, PAR3, NOTES, AIM_AT, ORDER, LABELS)
"""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(DIR, "package.json")) as _fh:
    PACKAGE = json.load(_fh)
NAME = PACKAGE["course"]["name"]
PREFIX = "Veenker_Auto"
TEE_SET = PACKAGE["tee_set"]


def _key(k):
    return int(k) if str(k).isdigit() else k


def _px(h, p):
    ppy, (tx, ty) = h["pixel"]["ppy"], h["pixel"]["tee_px"]
    return (round(tx + ppy * p[0], 1), round(ty + ppy * p[1], 1))


HOLES, PAR3, NOTES, AIM_AT = {}, {}, {}, {}
for _k, _h in PACKAGE["holes"].items():
    _z = [(n, [_px(_h, p) for p in poly]) for n, poly in _h["zones"]]
    _hole = dict(par=_h["par"], image=_h.get("image"), length=_h["length"], tee=_px(_h, (0, 0)),
                 dot270=_px(_h, (0, -270)), green=_px(_h, _h["green"]), zones=_z, aim_min=-60, aim_max=60,
                 px_per_yd=_h["pixel"]["ppy"], hole_line=[_px(_h, p) for p in _h["hole_line"]],
                 tee_ll=_h["tee_ll"], aim_ll=_h["aim_ll"], green_ll=_h["green_ll"], bearing_deg=_h["bearing_deg"],
                 auto=_h["confidence"], elevation=_h.get("elevation"))
    NOTES[_key(_k)] = _h.get("note", "Auto-built.")
    _p3 = _h.get("par3")
    if _p3:
        PAR3[_key(_k)] = dict(_p3, image=_h.get("image"), tee=_px(_h, _p3["tee"]), flag=_px(_h, _p3["flag"]),
                              green=[tuple(q) for q in _p3["green"]], zones=_z, auto=_h["confidence"])
    else:
        HOLES[_key(_k)] = _hole
        AIM_AT[_key(_k)] = "Centre of the fairway"

ORDER = sorted(set(HOLES) | set(PAR3), key=lambda k: (str(k).rstrip("BF").zfill(3), str(k)))
LABELS = {}
APP, GREEN_SIDE = {}, {}
