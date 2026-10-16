"""Landing-zone review sheet: photo + traced outlines + star + 95% oval + every simulated ball
coloured by the lie the model gives it. Review EVERY hole with this before trusting a pick:
  python3 spirit_hollow/review.py out.png 1 2B 4 ...
Look for balls coloured fairway/rough that sit on tan grass, trees or water in the photo."""
import sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "mozingo"), HERE]
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tee_strategy as t, course as c, yardage_book as yb
t.HOLES = c.HOLES
out = sys.argv[1]
col = {"fairway": (124, 252, 0), "recovery": (255, 85, 0), "sand": (255, 255, 255), "native": (255, 208, 0),
       "water": (0, 191, 255), "ob": (255, 0, 255), "rough": (200, 200, 200)}
k = 1206 / 920
font = ImageFont.load_default(size=22)
tiles = []
for h in [x if not x.isdigit() else int(x) for x in sys.argv[2:]]:
    hd = c.HOLES[h]
    res = {kk: t.best_aim(h, kk, aims=t.AIMS_WIDE if kk in t.IRONS else t.AIMS) for kk in t.clubs_for(h)}
    b = min(res, key=lambda kk: res[kk]["ev"]); aim = res[b]["aim"]
    im = Image.open(f"{HERE}/screenshots/{hd['image']}").convert("RGB")
    d = ImageDraw.Draw(im)
    for name, poly in hd["zones"]:
        d.line([(x * k, y * k) for x, y in poly + [poly[0]]], fill=col[name], width=3)
    fr = yb.frame(hd["tee"], hd["dot270"], 270)
    carry, total, width, depth = {**t.CLUBS, **t.IRONS}[b]
    total += hd.get("extra_roll", 0)
    ell = [tuple(yb.px(fr, total + depth / 2 * np.sin(a), aim + width / 2 * np.cos(a)) * k) for a in np.linspace(0, 2 * np.pi, 60)]
    d.line(ell + [ell[0]], fill=(255, 214, 10), width=2)
    pts, lie, *_ = t.simulate(h, b, aim, n=500)
    for (x, y), l in zip(pts, lie):
        d.ellipse([x * k - 3, y * k - 3, x * k + 3, y * k + 3], fill=col.get(l, (255, 0, 0)), outline=(0, 0, 0))
    sx, sy = yb.px(fr, total, aim) * k
    d.regular_polygon((sx, sy, 16), 5, fill=(255, 214, 10), outline=(0, 0, 0))
    lo, hi = yb.px(fr, total - 60, aim) * k, yb.px(fr, total + 40, aim) * k
    cx = (lo[0] + hi[0]) / 2
    half = 320
    box = (int(cx - half), int(min(lo[1], hi[1]) - 40), int(cx + half), int(max(lo[1], hi[1]) + 40))
    tile = im.crop(box)
    tile = tile.resize((520, int(tile.height * 520 / tile.width)))
    dd = ImageDraw.Draw(tile)
    sh = res[b]["share"]
    dd.rectangle([0, 0, 520, 30], fill=(0, 0, 0))
    dd.text((6, 4), f"{h} {b} aim {aim:+.1f}  fw {sh['fairway']:.0%} rgh {sh['rough']:.0%} tree {sh['recovery']:.0%} "
            f"nat {sh['native']:.0%} wat {sh['water']+sh['ob']:.0%} sand {sh['sand']:.0%}", fill=(255, 255, 255), font=ImageFont.load_default(size=15))
    tiles.append(tile)
H = max(tl.height for tl in tiles)
o = Image.new("RGB", (530 * len(tiles), H), "white")
for i, tl in enumerate(tiles):
    o.paste(tl, (i * 530, 0))
o.save(out)
