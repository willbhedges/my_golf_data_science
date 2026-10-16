"""Auto-built course (OpenStreetMap -> course_data/geometry/build_holes.py). Do not edit by hand:
re-run  python course_data/geometry/build_holes.py course_data/spirit_hollow

Same format as spirit_hollow/course.py: HOLES (par 4/5, plus par 3s without a mapped green) with tee,
dot270, green, length, par, zones in a 920 x 2000 screen frame; PAR3 with the green outline in yds.
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "auto_holes.json")) as _fh:
    _RAW = json.load(_fh)["holes"]


def _key(k):
    return int(k) if str(k).isdigit() else k


HOLES, PAR3 = {}, {}
for _k, _h in _RAW.items():
    _h = dict(_h)
    _h["tee"], _h["dot270"], _h["green"] = tuple(_h["tee"]), tuple(_h["dot270"]), tuple(_h["green"])
    _h["zones"] = [(n, [tuple(p) for p in poly]) for n, poly in _h["zones"]]
    _h.setdefault("aim_min", -40)
    _h.setdefault("aim_max", 40)
    _p3 = _h.pop("par3", None)
    if _p3:
        _p3 = dict(_p3, tee=tuple(_p3["tee"]), flag=tuple(_p3["flag"]), green=[tuple(p) for p in _p3["green"]])
        _p3["zones"] = _h["zones"]
        PAR3[_key(_k)] = _p3
    else:
        HOLES[_key(_k)] = _h

ORDER = sorted(set(HOLES) | set(PAR3), key=lambda k: (str(k).rstrip("BF").zfill(3), str(k)))
NOTES = {k: "Auto-built from OpenStreetMap ({}).".format(h.get("tee_choice", "")) for k, h in HOLES.items()}
AIM_AT = {k: "Centre of the fairway" for k in HOLES}
LABELS = {}
