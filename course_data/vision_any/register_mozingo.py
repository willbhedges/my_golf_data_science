"""Georeference the hand-traced Mozingo Lake holes (mozingo/tee_strategy.HOLES, screenshot px) for validation.

  python3 course_data/vision_any/register_mozingo.py

There is no NAIP registration of the Mozingo screenshots, so each traced hole is fitted to the OSM-built
hole (pipeline.build_course with the traced lengths as the card, geometry's frame) by acceptance.py's
rigid lie-raster fit on fairway / water / sand (never trees or native, so the tree / native evaluation stays
independent). The chain traced px -> auto yards -> auto px -> WGS84 is summarised as a 2x3 affine
(px -> lon, lat; residual < 0.05 yd over the screen) in course_data/vision_any/mozingo/traced_registration.json
with the fit's dice score.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "course_data"), os.path.join(ROOT, "spirit_hollow"), os.path.join(ROOT, "mozingo")]


def main():
    import pipeline as P
    import tee_strategy as t
    import acceptance as A
    lens = {str(k): float(h["length"]) for k, h in t.HOLES.items()}
    m = P.build_course("Mozingo Lake", "white", lens, render=False, quiet=True, tee_stage=False)
    A.CDIR = os.path.join(ROOT, "course_data", "mozingo")
    out = {}
    gx, gy = np.meshgrid(np.linspace(0, 920, 12), np.linspace(400, 2000, 20))
    G = np.c_[gx.ravel(), gy.ravel()]
    for k, h in t.HOLES.items():
        a = A.as_model_hole(m["holes"][str(k)])
        T, reg = A.raster_transform(h, a)
        if T is None:
            continue
        fa = A.auto_frame(a, str(k))
        ll = fa.px_to_ll(A.yds_to_px(a, T(G)))
        X = np.c_[G, np.ones(len(G))]
        coef, *_ = np.linalg.lstsq(X, ll, rcond=None)
        res = ll - X @ coef
        res_yd = float(np.abs(res * [111320 * np.cos(np.radians(ll[:, 1].mean())), 111320]).max() / 0.9144)
        out[str(k)] = dict(key=str(k), affine_px_to_ll=coef.T.tolist(), residual_yd=round(res_yd, 3),
                           dice=reg["dice"], rot_deg=reg["rot_deg"], shift_yd=reg["shift"], classes=reg["classes"],
                           auto_tee_ll=list(a["tee_ll"]), auto_aim_ll=list(a["aim_ll"]),
                           method="acceptance.raster_transform onto the OSM-built hole (fairway/water/sand)")
        print(k, reg, "affine residual", round(res_yd, 3), "yd")
    p = os.path.join(HERE, "mozingo", "traced_registration.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(out, open(p, "w"), indent=1)
    print("wrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
