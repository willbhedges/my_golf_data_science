"""Whole-hole review sheets for hand verification (every hole, incl. par 3s): tees of EVERY set, green, all zones.

  python3 course_data/truth/hole_sheet.py --slug pine_dunes [--holes 1,7] [--ppy 2.5] [--out DIR] [--trace]

One frame per hole from the package's back-set tee to the green centre (x = yds right of that line, along = yds
from the tee; -40 .. length+40, +/-80). Panels: NAIP photo (package year) with the package's tee boxes per set
(coloured squares + set initial), green outline and zone outlines | CIR | lidar canopy (3DEP HAG) | other NAIP
years when present. With --trace: the hand truth (course_data/truth/<slug>/holes_truth.json: tees per set,
green) drawn in white crosses. Uses course_data/truth/corridor.py's rasters and drawing (UTM planar frame).
Output JPEGs (default the scratchpad-style dir course_data/truth/<slug>/sheets/, git-ignored).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corridor as C                                      # noqa: E402

SETCOL = {"gold": (230, 180, 20), "black": (20, 20, 20), "blue": (40, 90, 255), "white": (250, 250, 250),
          "red": (230, 30, 30), "green": (30, 170, 60), "silver": (190, 190, 190), "purple": (150, 60, 200),
          "orange": (255, 140, 0), "combo": (120, 120, 120), "yellow": (250, 230, 40), "tan": (200, 170, 120)}


def setcol(name, pkg):
    c = ((pkg.get("tee_sets") or {}).get(name) or {}).get("colour") or name
    return SETCOL.get(str(c).lower(), SETCOL.get(str(name).lower().split()[0], (255, 0, 255)))


def back_set(pkg, h):
    ys = h.get("yards") or {}
    return max(ys, key=lambda s: ys[s] or 0) if ys else pkg["tee_set"]


def sheet(slug, ref, out_dir, ppy=2.5, trace=None, years=2):
    import cv2
    pkg = C.package(slug)
    h = pkg["holes"][ref]
    S = C.sources(slug)
    st = back_set(pkg, h)
    tees = h.get("tees") or {}
    tee_ll = (tees.get(st) or {}).get("tee_ll") or h["tee_ll"]
    green_ll = h["green_ll"]
    fr0 = C.R.Frame(tee_ll, green_ll, ppy=1.0, proj="utm")
    L = float(np.linalg.norm(fr0.ll_to_yds([green_ll])[0]))
    a0, a1, lat = -40.0, L + 40.0, 80.0
    fr = C.corridor_frame(tee_ll, green_ll, ppy, a0=a0, a1=a1, lat=lat)

    def px(ll):
        xy = fr.ll_to_yds(np.asarray(ll, float)[:, :2])
        return C.yd_to_px(fr, np.c_[xy[:, 0], -xy[:, 1]], a1, lat)

    rgb = C._u8(S["photo"].warp(fr)[..., :3])
    base = rgb.copy()
    # zones (package), green, tees
    zones = []
    for z in h.get("zones_ll") or []:
        if len(z.get("poly") or []) >= 3:
            lie = {"bunker": "sand", "trees": "recovery", "green": "fairway"}.get(z["lie"], z["lie"])
            if lie in C.COL:
                xy = fr.ll_to_yds(np.asarray(z["poly"], float)[:, :2])
                zones.append(dict(lie=lie, xy=np.c_[xy[:, 0], -xy[:, 1]]))
    ann = C.draw_zones(base, fr, zones, fill=False, width=1, a1=a1, lat=lat)
    gp = h.get("green_polygon_ll")
    if gp:
        p = np.round(px(gp) * 8).astype(np.int32)
        cv2.polylines(ann, [p], True, (255, 0, 255), 2, shift=3)
    for name, t in tees.items():
        if not t.get("tee_ll"):
            continue
        x, y = px([t["tee_ll"]])[0]
        c = setcol(name, pkg)
        cv2.rectangle(ann, (int(x) - 5, int(y) - 5), (int(x) + 5, int(y) + 5), (0, 0, 0), 3)
        cv2.rectangle(ann, (int(x) - 5, int(y) - 5), (int(x) + 5, int(y) + 5), c, -1)
        lab = f"{name[:2]} {(h.get('yards') or {}).get(name, '')}"
        cv2.putText(ann, lab, (int(x) + 8, int(y) + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 0), 3)
        cv2.putText(ann, lab, (int(x) + 8, int(y) + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)
    if trace:
        for name, ll in (trace.get("tees") or {}).items():
            x, y = px([ll])[0]
            cv2.drawMarker(ann, (int(x), int(y)), (255, 255, 255), cv2.MARKER_CROSS, 14, 2)
        if trace.get("green_ll"):
            x, y = px([trace["green_ll"]])[0]
            cv2.drawMarker(ann, (int(x), int(y)), (255, 255, 255), cv2.MARKER_TILTED_CROSS, 16, 2)
    P = [C.title(C.grid(ann, fr, a0=a0, a1=a1, lat=lat, step=10, label_every=50, font=0.35),
                 f"{slug} {ref} par {h.get('par')} {st} {L:.0f}yd: photo {C._year(os.path.join(C.CD, 'packages', slug, 'imagery'))}")]
    if "nir" in S:
        P.append(C.title(C.grid(C.cir(S, fr), fr, a0=a0, a1=a1, lat=lat, step=10, label_every=50, font=0.35), "CIR"))
    if "hag" in S:
        hg = C.hag_rgb(C.hag_m(S, fr))
        P.append(C.title(C.grid(hg, fr, a0=a0, a1=a1, lat=lat, step=10, label_every=50, font=0.35),
                         "lidar HAG gy<.5 ye<2.5 gn<8 dk"))
    for k in sorted([k for k in S if k.startswith("naip_")], reverse=True)[:years]:
        a = S[k].warp(fr)
        if np.isnan(a).mean() > 0.5:
            continue
        P.append(C.title(C.grid(C._u8(a[..., :3]), fr, a0=a0, a1=a1, lat=lat, step=10, label_every=50, font=0.35),
                         S[k].label))
    img = C.stack(P, len(P))
    os.makedirs(out_dir, exist_ok=True)
    from PIL import Image
    p = os.path.join(out_dir, f"h{int(ref):02d}.jpg")
    Image.fromarray(img).save(p, quality=80)
    return p, dict(ref=ref, set=st, length=round(L, 1), frame=fr.to_json(), a0=a0, a1=a1, lat=lat)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--holes", default="")
    ap.add_argument("--ppy", type=float, default=2.5)
    ap.add_argument("--out")
    ap.add_argument("--trace", action="store_true")
    a = ap.parse_args()
    pkg = C.package(a.slug)
    refs = [r for r in pkg["holes"] if not a.holes or r in a.holes.split(",")]
    out = a.out or C.tdir(a.slug, "sheets")
    tr = {}
    tp = C.tdir(a.slug, "holes_truth.json")
    if a.trace and os.path.exists(tp):
        tr = json.load(open(tp)).get("holes", {})
    fj = {}
    for r in sorted(refs, key=int):
        p, f = sheet(a.slug, r, out, a.ppy, tr.get(r))
        fj[r] = f
        print(p)
    json.dump(fj, open(os.path.join(out, "frames.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
