"""Clean overhead image per hole: NAIP re-projected into the hole's virtual pixel frame (920 x 2000).

Uses course_data/imagery/render.py (exact WGS84 <-> screen mapping), so the only things drawn on the
book pages and the wind page are our own aim marks. JPEG keeps the outputs small.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "imagery"))

import render as R                                  # noqa: E402

QUALITY = 82


def render_all(C, out_dir, quality=QUALITY, log=print):
    """Render every hole of Course C into out_dir/<image>. Returns {key: info} (also out_dir/index.json)."""
    from PIL import Image
    os.makedirs(out_dir, exist_ok=True)
    if not C.imagery_dir:
        raise SystemExit("no imagery for this course: run the imagery fetch (imagery_fetch.yml) first; "
                         "the package's sources.imagery.dir must point at a folder with naip_rgb.tif")
    img = R.Imagery(C.imagery_dir)
    index = {}
    for k in C.order:
        hd = C.holes.get(k) or C.par3[k]
        fr = R.Frame.from_json(C.frames[k])
        out, info = R.render(fr, img)
        path = os.path.join(out_dir, hd["image"])
        Image.fromarray(out[..., :3]).save(path, "JPEG", quality=quality, optimize=True, progressive=True)
        info["image"] = hd["image"]
        info["bytes"] = os.path.getsize(path)
        index[str(k)] = info
        if info["no_imagery_frac"] > 0.05:
            log(f"  ! hole {k}: {info['no_imagery_frac']:.0%} of the frame has no imagery")
    with open(os.path.join(out_dir, "index.json"), "w") as fh:
        json.dump(index, fh, indent=1, default=float)
    return index


def check_alignment(C):
    """Max px error of the tee and green when mapped WGS84 -> frame -> WGS84 -> frame (sanity check)."""
    err = 0.0
    for k, fj in C.frames.items():
        fr = R.Frame.from_json(fj)
        p = np.array([fr.tee_px, fr.point_px(270)])
        err = max(err, float(np.abs(fr.ll_to_px(fr.px_to_ll(p)) - p).max()))
    return err
