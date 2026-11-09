"""Render a hole's photo (package NAIP 2023 0.3 m, its page frame) with the course module's lie map painted on it
(zones in order, later wins), to eye-check map edits. Usage: lie_render.py out_dir holes [which] [a0,a1 yds along]"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "course_data", "imagery"))
import importlib.util
import cv2
import render as R
from PIL import Image, ImageDraw
out, holes = sys.argv[1], sys.argv[2].split(",")
which = sys.argv[3] if len(sys.argv) > 3 else "truth"
spec = importlib.util.spec_from_file_location("c", os.path.join(ROOT, "course_data/courses/gateway_national", which, "course.py"))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
img = R.Imagery(os.path.join(ROOT, "course_data/packages/gateway_national/imagery"))
COL = {"fairway": (40, 230, 60), "first_cut": (170, 255, 120), "rough": (255, 255, 255), "recovery": (20, 110, 20),
       "native": (230, 190, 60), "water": (40, 120, 255), "sand": (255, 240, 200), "ob": (255, 40, 40)}
os.makedirs(out, exist_ok=True)
for k in holes:
    k = int(k)
    fr = R.Frame.from_json(C.FRAMES[k])
    hd = C.HOLES.get(k) or C.PAR3[k]
    a, _ = R.render(fr, img, interp=cv2.INTER_LINEAR)
    base = Image.fromarray(a[..., :3]).convert("RGBA")
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for name, poly in hd["zones"]:
        if len(poly) >= 3 and name in COL:
            d.polygon([tuple(p) for p in poly], fill=COL[name] + (70,), outline=COL[name] + (255,))
    im = Image.alpha_composite(base, lay).convert("RGB")
    dd = ImageDraw.Draw(im)
    tee = hd["tee"]; ppy = fr.ppy
    for yd in range(50, 451, 50):
        y = tee[1] - yd * ppy
        dd.line([(tee[0] - 4, y), (tee[0] + 4, y)], fill=(255, 0, 255), width=2); dd.text((tee[0] + 6, y - 6), str(yd), fill=(255, 0, 255))
    dd.line([tuple(tee), (tee[0], tee[1] - 420 * ppy)], fill=(255, 0, 255), width=1)
    if len(sys.argv) > 4:
        a0, a1 = [float(v) for v in sys.argv[4].split(",")]
        im = im.crop((0, int(tee[1] - a1 * ppy), im.width, int(tee[1] - a0 * ppy)))
    im.save(os.path.join(out, f"lie_{which}_{k:02d}.jpg"), quality=85)
    print("wrote", k)
