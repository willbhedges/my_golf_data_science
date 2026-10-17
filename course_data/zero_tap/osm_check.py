"""How good is OSM as truth? Hand checks against NAIP + an automatic scorecard consistency check.

  python course_data/zero_tap/osm_check.py pick                 -> osm_check/picks.json (30 seeded courses)
  python course_data/zero_tap/osm_check.py render <slug> ...    (Actions: NAIP fetch) -> osm_check/sheets/<slug>_*.jpg
  python course_data/zero_tap/osm_check.py cardcheck            -> osm_check/card_check.json (offline, every course)
  python course_data/zero_tap/osm_check.py apply                -> verdicts.json -> truth/<slug>.json hand_check
  python course_data/zero_tap/osm_check.py report               -> OSM_CHECK.md

Sheets: an overview (NAIP, every OSM hole line numbered at the tee and green end, OSM greens in yellow, tees in
cyan) and a per-hole tile sheet (each hole's line + 45 m, north up). A hole is judged (verdicts.json, by eye):
  ok           the line runs from a tee complex to the green of one hole, and the number fits the sequence
               (green n near tee n + 1)
  tee_short    the line starts in front of the back tee complex (> ~40 yds ahead; still the right hole)
  green_wrong  the line ends on no green / the wrong green (or the OSM green polygon is misplaced)
  tee_wrong    the line starts at another hole's tee or nowhere near a tee
  number       the line is a real hole but the sequence says its number is wrong
  unclear      imagery cannot tell (trees, old imagery, construction)
Card check (no eyes): per hole, OSM line length vs the web card's longest tee yardage (> 15 % off and > 30 yds =
`length`) and OSM par vs card par.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [HERE]
import bench as B  # noqa: E402
import truth as TR  # noqa: E402

OUT = os.path.join(HERE, "osm_check")
SEED = 20261020


def pick(n=30):
    rows = sorted(B.courses(), key=lambda r: r["slug"])
    p = random.Random(SEED).sample(rows, n)
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(seed=SEED, n=n, slugs=[r["slug"] for r in p]), open(os.path.join(OUT, "picks.json"), "w"), indent=1)
    print([r["slug"] for r in p])


def render(slug, work):
    import subprocess
    import numpy as np
    import rasterio
    from PIL import Image, ImageDraw
    from pyproj import Transformer
    row = next(r for r in B.manifest()["courses"] if r["slug"] == slug)
    t = B.truth(slug)
    fc = B._rd(row["files"]["osm"])
    pts = [q for h in t["holes"] for q in h["line"]]
    lo = [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]
    d = os.path.join(work, slug)
    if not os.path.exists(os.path.join(d, "naip_rgb.tif")):
        subprocess.run([sys.executable, os.path.join(CD, "imagery", "fetch_imagery.py"), "--bbox",
                        f"{lo[1]},{lo[0]},{lo[3]},{lo[2]}", "--margin", "120", "--no-dem", "--max-mb", "40",
                        "--out", d], check=True, timeout=1800)
    meta = json.load(open(os.path.join(d, "georef.json")))
    with rasterio.open(os.path.join(d, "naip_rgb.tif")) as s:
        f = max(1, int(round(1.0 / abs(s.transform.a))))         # ~1 m overview grid for the sheet
        H, W = s.height // f, s.width // f
        img = s.read(out_shape=(3, H, W))
        T = s.transform * s.transform.scale(s.width / W, s.height / H)
        tr = Transformer.from_crs("EPSG:4326", s.crs, always_xy=True)
    inv = ~T

    def px(ll):
        x, y = tr.transform(ll[0], ll[1])
        c, r = inv * (x, y)
        return (c, r)
    base = Image.fromarray(np.transpose(img, (1, 2, 0)).astype("uint8"))
    ov = base.copy()
    dr = ImageDraw.Draw(ov)
    for fid, ring, c in TR.features(fc, "green"):
        if ring:
            dr.polygon([px(q) for q in ring], outline=(255, 230, 0))
    for fid, ring, c in TR.features(fc, "tee"):
        if ring:
            dr.polygon([px(q) for q in ring], outline=(0, 230, 255))
        else:
            x, y = px(c)
            dr.ellipse([x - 3, y - 3, x + 3, y + 3], outline=(0, 230, 255))
    for h in t["holes"]:
        line = [px(q) for q in h["line"]]
        dr.line(line, fill=(255, 40, 40), width=2)
        for (x, y), lab, col in ((line[0], f"T{h['ref']}", (255, 255, 255)), (line[-1], f"G{h['ref']}", (255, 230, 0))):
            dr.rectangle([x - 1, y - 1, x + 7 * len(lab), y + 11], fill=(0, 0, 0))
            dr.text((x + 1, y), lab, fill=col)
    os.makedirs(os.path.join(OUT, "sheets"), exist_ok=True)
    sc = min(1.0, 1800 / max(ov.size))
    ov.resize((int(ov.size[0] * sc), int(ov.size[1] * sc))).save(
        os.path.join(OUT, "sheets", f"{slug}_overview.jpg"), quality=72)
    tiles = []
    for h in t["holes"]:
        line = [px(q) for q in h["line"]]
        xs, ys = [p[0] for p in line], [p[1] for p in line]
        m = 45 / f
        box = [max(0, min(xs) - m), max(0, min(ys) - m), min(W, max(xs) + m), min(H, max(ys) + m)]
        tile = ov.crop(tuple(int(v) for v in box))
        k = 340 / max(tile.size)
        tile = tile.resize((max(1, int(tile.size[0] * k)), max(1, int(tile.size[1] * k))))
        tiles.append((h, tile))
    cols = 6
    rows_n = math.ceil(len(tiles) / cols)
    sheet = Image.new("RGB", (cols * 345, rows_n * 360), (20, 20, 20))
    sd = ImageDraw.Draw(sheet)
    for i, (h, tile) in enumerate(tiles):
        x0, y0 = (i % cols) * 345, (i // cols) * 360
        sheet.paste(tile, (x0, y0 + 18))
        sd.text((x0 + 4, y0 + 3), f"hole {h['ref']} par {h['par']} {h['length_yd']:.0f} yds", fill=(255, 255, 255))
    sheet.save(os.path.join(OUT, "sheets", f"{slug}_holes.jpg"), quality=72)
    im = meta.get("imagery") or {}
    return dict(slug=slug, imagery=dict(source=im.get("source"), year=im.get("year"), gsd_m=im.get("gsd_m")))


def cardcheck():
    out = {}
    for r in B.courses():
        if not (r.get("card") and r["card"].get("fits")) or r["kind"] not in (9, 18):
            continue
        card, src = B.card_for(r)
        t = B.truth(r["slug"])
        sets = [s.get("yards") for s in (card.get("tee_sets") or {}).values() if s.get("yards")]
        sets = [s for s in sets if len(s) == r["kind"]]
        back = [max((s[i] or 0) for s in sets) for i in range(r["kind"])] if sets else None
        pars = card.get("par") or []
        per = {}
        for h in t["holes"]:
            i = h["ref"] - 1
            e = []
            if back and back[i]:
                d = h["length_yd"] - back[i]
                if abs(d) > 30 and abs(d) > 0.15 * back[i]:
                    e.append(f"length {h['length_yd']:.0f} vs card {back[i]}")
            if h.get("par_osm") is not None:
                e.append(f"par {h['par_osm']} vs card {pars[i]}")
            if e:
                per[h["ref"]] = e
        out[r["slug"]] = dict(card=src, holes=r["kind"], flagged=per, split=r["split"])
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "card_check.json"), "w"), indent=1)
    nh = sum(v["holes"] for v in out.values())
    nf = sum(len(v["flagged"]) for v in out.values())
    print(len(out), "courses with a fitting card;", nh, "holes;", nf, "flagged",
          sum(1 for v in out.values() if v["flagged"]), "courses with >= 1 flag")
    return out


def apply():
    """verdicts.json {slug: {"holes": {ref: verdict}, "course": "ok"|"bad", "note": ".."}} -> truth hand_check."""
    v = json.load(open(os.path.join(OUT, "verdicts.json")))
    for slug, e in v.items():
        p = os.path.join(HERE, "truth", slug + ".json")
        t = json.load(open(p))
        t["hand_check"] = dict(verdict=e.get("course", "ok"), holes=e["holes"], note=e.get("note"),
                               method="NAIP overlay sheets, osm_check.py")
        json.dump(t, open(p, "w"), separators=(",", ":"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["pick", "render", "cardcheck", "apply"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--work", default=os.path.join(HERE, "work", "naip"))
    a = ap.parse_args()
    if a.cmd == "pick":
        pick()
    elif a.cmd == "render":
        slugs = a.args or json.load(open(os.path.join(OUT, "picks.json")))["slugs"]
        meta = {}
        for s in slugs:
            try:
                meta[s] = render(s, a.work)
            except Exception as e:                                # noqa: BLE001
                import traceback
                traceback.print_exc()
                meta[s] = dict(error=repr(e)[:300])
            print(s, meta[s], flush=True)
        os.makedirs(os.path.join(OUT, "sheets"), exist_ok=True)
        json.dump(meta, open(os.path.join(OUT, "sheets", f"meta_{slugs[0]}.json"), "w"), indent=1)
    elif a.cmd == "cardcheck":
        cardcheck()
    else:
        apply()


if __name__ == "__main__":
    main()
