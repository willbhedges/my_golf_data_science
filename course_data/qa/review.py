"""Visual review: each auto-built hole's landing zone on NAIP with the package's zones drawn.

  python3 course_data/qa/review.py                       # every package on disk
  python3 course_data/qa/review.py --slug spirit_hollow --holes 1,4,8

Writes course_data/qa/review/<slug>/<hole>.jpg: left = the whole hole (tee line up, 0-480 yds), right =
the landing zone (150-360 yds along, +/-90 yds) at 2x. Zones are outlined in their lie colour, the
ARCHITECTURE landing grid (220-340, +/-45) is a dashed white box, the tee line is a thin white line and
the Driver best-aim landing (tee_strategy, 1,000 swings) is a yellow star with its balls coloured by lie.
Look for: trees/long grass/water in the photo with no outline, outlines over plain grass, a tee not on a
tee box, a green not on the green, a tee line not along the hole.
Also writes review/<slug>/index.json (per hole: lie shares of the Driver landing, no-imagery fraction).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

QA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QA)
import packages as P                                     # noqa: E402

COL = {"fairway": (124, 252, 0), "recovery": (255, 85, 0), "sand": (255, 255, 255), "native": (255, 208, 0),
       "water": (0, 191, 255), "ob": (255, 0, 255), "rough": (200, 200, 200), "first_cut": (190, 240, 140),
       "green": (0, 120, 0)}
PPY = 4.0
TEE_PX = (460.0, 1940.0)


def find_imagery(pkg):
    """Directory with georef.json (+ naip tifs/jpgs) for the package's course."""
    cands = [os.path.join(P.CD, "imagery", pkg.slug), os.path.join(pkg.dir, "imagery"), pkg.dir,
             os.path.join(P.CD, pkg.slug, "imagery"), os.path.join(P.CD, pkg.slug)]
    cands += sorted(glob.glob(os.path.join(P.CD, "*", pkg.slug, "imagery"))) + \
        sorted(glob.glob(os.path.join(P.CD, "*", pkg.slug)))
    for d in cands:
        if os.path.exists(os.path.join(d, "georef.json")):
            return d
    return None


def review_hole(q, img, out_path, z):
    import tee_strategy as t
    from PIL import Image, ImageDraw, ImageFont
    R = P._render()
    fr = R.Frame(q.tee_ll, q.aim_ll, ppy=PPY, tee_px=TEE_PX, proj="utm", size=(920, 2000))
    arr, info = R.render(fr, img)
    im = Image.fromarray(arr[..., :3].copy())
    d = ImageDraw.Draw(im)
    for lie, poly in q.zones_ll:
        px = fr.ll_to_px(np.array(poly, float)[:, :2])
        d.line([tuple(p) for p in px] + [tuple(px[0])], fill=COL.get(lie, (255, 0, 0)), width=3)
    if q.green_poly_ll:
        g = fr.ll_to_px(np.array(q.green_poly_ll, float)[:, :2])
        d.line([tuple(p) for p in g] + [tuple(g[0])], fill=(0, 90, 0), width=3)
    tee = fr.ll_to_px([q.tee_ll])[0]
    d.line([tuple(tee), tuple(fr.point_px(480))], fill=(255, 255, 255), width=1)
    if q.hole_line_ll:
        hl = fr.ll_to_px(np.array(q.hole_line_ll, float)[:, :2])
        d.line([tuple(p) for p in hl], fill=(255, 255, 0), width=1)
    for a in range(100, 481, 50):
        p = fr.point_px(a)
        d.line([(p[0] - 8, p[1]), (p[0] + 8, p[1])], fill=(255, 255, 255), width=2)
        d.text((p[0] + 10, p[1] - 6), str(a), fill=(255, 255, 255))
    c = [fr.point_px(220, -45), fr.point_px(220, 45), fr.point_px(340, 45), fr.point_px(340, -45)]
    for a, b in zip(c, c[1:] + c[:1]):
        n = 12
        for i in range(n):
            if i % 2 == 0:
                d.line([tuple(a + (b - a) * i / n), tuple(a + (b - a) * (i + 1) / n)], fill=(255, 255, 255), width=2)
    gr = fr.ll_to_px([q.green_ll])[0]
    d.ellipse([gr[0] - 7, gr[1] - 7, gr[0] + 7, gr[1] + 7], outline=(255, 0, 0), width=3)
    d.ellipse([tee[0] - 7, tee[1] - 7, tee[0] + 7, tee[1] + 7], outline=(0, 255, 255), width=3)
    stats = dict(no_imagery=info["no_imagery_frac"])
    if q.model is not None and (q.par or 4) > 3:
        saved = t.HOLES
        t.HOLES = {q.ref: q.model}
        try:
            r = t.best_aim(q.ref, "Driver", z=z)
            pts, lie, *_ = t.simulate(q.ref, "Driver", r["aim"], z=z[:, :300])
        finally:
            t.HOLES = saved
        # model px (package frame) -> ll -> review px
        mt, mf, mr, mppy = t.hole_frame(q.model)
        if q.frame is not None:
            ll = q.frame.px_to_ll(pts)
            rp = fr.ll_to_px(ll)
            for (x, y), l in zip(rp, lie):
                d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=COL.get(l, (255, 0, 0)), outline=(0, 0, 0))
        carry, total = t.CLUBS["Driver"][:2]
        s = fr.ll_to_px(q.frame.px_to_ll(np.array([mt + (total * mf + r["aim"] * mr) * mppy])))[0] if q.frame else fr.point_px(total, r["aim"])
        d.regular_polygon((s[0], s[1], 14), 5, fill=(255, 214, 10), outline=(0, 0, 0))
        stats.update(aim=float(r["aim"]), ev=round(float(r["ev"]), 3), share={k: round(v, 3) for k, v in r["share"].items() if v})
    # compose: full hole (scaled to 0.3) | landing crop (150-360 yds, +/-90) at 1x
    full = im.resize((276, 600))
    y0, y1 = fr.point_px(365)[1], fr.point_px(145)[1]
    x0, x1 = fr.point_px(0, -95)[0], fr.point_px(0, 95)[0]
    crop = im.crop((int(x0), int(y0), int(x1), int(y1))).resize((int((x1 - x0) * 0.78), int((y1 - y0) * 0.78)))
    W = full.width + crop.width + 6
    H = max(full.height, crop.height) + 26
    out = Image.new("RGB", (W, H), (20, 20, 20))
    out.paste(full, (0, 26))
    out.paste(crop, (full.width + 6, 26))
    dd = ImageDraw.Draw(out)
    font = ImageFont.load_default(size=14)
    sh = stats.get("share", {})
    txt = f"{q.ref} par {q.par} {q.length} yds (card {q.card}) brg {q.bearing:.0f}  " + \
        " ".join(f"{k[:4]} {v:.0%}" for k, v in sh.items())
    dd.text((4, 5), txt, fill=(255, 255, 255), font=font)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    out.save(out_path, quality=72, optimize=True)
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--holes")
    ap.add_argument("--kind", help="package.json or holes.json (default: package.json if present, else holes.json)")
    a = ap.parse_args()
    R = P._render()
    rng = np.random.default_rng(5)
    z = np.vstack([rng.standard_normal((2, 1000)), rng.random((2, 1000))])
    pk_all = [p for p in P.find_packages() if not a.slug or a.slug in p.slug]
    by = {}
    for p in pk_all:                                     # one package per slug: prefer package.json
        if p.slug not in by or (p.kind == "package.json" and by[p.slug].kind != "package.json") or p.kind == a.kind:
            by[p.slug] = p
    for slug, pk in by.items():
        idir = find_imagery(pk)
        if not idir:
            print(f"{slug}: no imagery (georef.json) found -> no review images")
            continue
        img = R.Imagery(idir)
        idx = {}
        for ref, q in pk.holes.items():
            if a.holes and ref not in a.holes.split(","):
                continue
            if not (q.tee_ll and q.aim_ll and q.green_ll):
                idx[ref] = dict(error="no tee/aim/green")
                continue
            try:
                idx[ref] = review_hole(q, img, os.path.join(QA, "review", slug, f"{ref}.jpg"), z)
            except Exception as e:                                 # noqa: BLE001
                idx[ref] = dict(error=f"{type(e).__name__}: {e}")
            print(slug, ref, idx[ref], flush=True)
        idx["_package"] = os.path.relpath(pk.path, P.ROOT)
        with open(os.path.join(QA, "review", slug, "index.json"), "w") as fh:
            json.dump(idx, fh, indent=1)


if __name__ == "__main__":
    main()
