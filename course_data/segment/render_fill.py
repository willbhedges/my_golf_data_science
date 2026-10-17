"""Draw a package's segment gap-fill zones (filled) over NAIP with the package's other zones (outlines).

    python3 course_data/segment/render_fill.py <package.json> <naip 4-band tif> <out.jpg> [--holes 1,3,5]
"""
import json
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore", category=DeprecationWarning)
COL = {"fairway": (120, 255, 60), "sand": (255, 230, 100), "water": (40, 140, 255), "green": (0, 160, 0)}


def main():
    import rasterio
    from PIL import Image, ImageDraw
    from pyproj import Transformer
    pkg_path, naip, out = sys.argv[1:4]
    holes = sys.argv[5].split(",") if len(sys.argv) > 5 else None
    pkg = json.load(open(pkg_path))
    with rasterio.open(naip) as s:
        img = s.read([1, 2, 3])
        T, crs = s.transform, s.crs
    tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    sc = min(1.0, 2400 / max(img.shape[1:]))
    im = Image.fromarray(np.moveaxis(img, 0, -1)).convert("RGB")
    im = im.resize((int(im.width * sc), int(im.height * sc)))
    d = ImageDraw.Draw(im, "RGBA")
    inv = ~T

    def px(ring):
        xs, ys = tr.transform([p[0] for p in ring], [p[1] for p in ring])
        return [tuple(np.multiply(inv * (x, y), sc)) for x, y in zip(xs, ys)]
    seen = set()
    for k, h in pkg["holes"].items():
        if holes and k not in holes:
            continue
        for z in h.get("zones_ll") or []:
            key = (z["lie"], tuple(z["poly"][0]), len(z["poly"]))
            if key in seen or z["lie"] not in COL:
                continue
            seen.add(key)
            c = COL[z["lie"]]
            if z.get("gapfill"):
                d.polygon(px(z["poly"]), fill=c + (150,), outline=(255, 0, 0, 255))
            else:
                d.line(px(z["poly"]) + px(z["poly"][:1]), fill=c + (255,), width=2)
        if h.get("hole_line_ll"):
            d.line(px(h["hole_line_ll"]), fill=(255, 255, 255, 200), width=2)
            x, y = px(h["hole_line_ll"][:1])[0]
            d.text((x + 4, y), k, fill=(255, 255, 255, 255))
        for t in h.get("tee_candidates_ll") or []:
            x, y = px([t["tee_ll"]])[0]
            d.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(255, 0, 255, 255), width=2)
    im.save(out, quality=85)
    print(out)


if __name__ == "__main__":
    main()
