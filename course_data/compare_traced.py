"""Compare the OSM-derived hole maps with the hand-traced spirit_hollow/course.py maps.

  python course_data/compare_traced.py [course_data/spirit_hollow]

For each traced hole, picks the OSM tee box whose playing length best matches the traced
length, converts OSM to the model frame (osm_to_model.convert) and compares the lie the
model would see on a landing-zone grid (200-320 yds along, +/-45 yds lateral, 5-yd step).
Prints per-hole agreement and the confusion of traced vs OSM lies.
"""
import os
import sys
import json
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "spirit_hollow"), os.path.join(HERE, "..", "mozingo")]
import osm_to_model as om                                   # noqa: E402
import course                                               # noqa: E402
import tee_strategy as t                                    # noqa: E402


def grid():
    a, l = np.meshgrid(np.arange(200, 321, 5), np.arange(-45, 46, 5))
    return a.ravel(), l.ravel()


def traced_lies(h, along, lat):
    tee, f, r, ppy = t.hole_frame(h)
    pts = tee + (along[:, None] * f + lat[:, None] * r) * ppy
    return t.lie_at(h, pts)


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "spirit_hollow")
    fc = json.load(open(os.path.join(d, "osm.geojson")))
    along, lat = grid()
    conf, rows = Counter(), []
    for k, h in course.HOLES.items():
        ref = str(k).rstrip("BF")
        osm = om.convert(fc, lengths={ref: h["length"]})[int(ref)]
        o = t.lie_at(osm, np.c_[lat, -along].astype(float))
        tr = traced_lies(h, along, lat)
        agree = float(np.mean(o == tr))
        conf.update(zip(tr, o))
        rows.append((k, h["length"], osm["length"], osm["tee_choice"], agree,
                     dict(Counter(tr)), dict(Counter(o))))
    for r in rows:
        print(f"{str(r[0]):>3}  traced {r[1]:>3}  osm {r[2]:>3}  agree {r[4]:.2f}  traced {r[5]}  osm {r[6]}")
    print("mean agreement", round(np.mean([r[4] for r in rows]), 3))
    labs = sorted({a for a, _ in conf} | {b for _, b in conf})
    print("confusion (rows traced, cols OSM):", labs)
    for a in labs:
        print(f"{a:>9}", [conf[(a, b)] for b in labs])


if __name__ == "__main__":
    main()
