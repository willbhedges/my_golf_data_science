"""Look at a fast-path perception build: NAIP (1 m grid) with OSM greens / tees, detected greens / tee boxes /
fairways / bunkers / water, the routed hole lines and the strategy pick (decision.json).

    python3 render_scene.py <pkg_dir> [--out DIR] [--holes]
    -> DIR/overview.jpg (whole course) and, with --holes, DIR/hole_NN.jpg (one crop per routed hole)

Colours: OSM green white outline, detected green magenta fill edge, detected tee box cyan, OSM tee blue, fairway
(detected) light green outline, bunker yellow, water dark blue, routed hole line red (tee -> green), the pick's aim
point an orange dot with the club written beside the tee.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fastscene as FS  # noqa: E402

COL = dict(osm_green=(255, 255, 255), det_green=(255, 0, 255), det_tee=(255, 255, 0), osm_tee=(255, 80, 0),
           fairway=(120, 255, 120), bunker=(0, 230, 255), water=(255, 60, 0), line=(0, 0, 255), aim=(0, 140, 255))


def _rings(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return [c[0]]
    if t == "MultiPolygon":
        return [p[0] for p in c]
    return []


def render(pkg_dir, out_dir=None, holes=False, scale=1.0):
    import cv2
    out_dir = out_dir or os.path.join(pkg_dir, "render")
    os.makedirs(out_dir, exist_ok=True)
    st = FS.grid_stack(pkg_dir)
    img = np.transpose(st.a["naip"][:3], (1, 2, 0))[:, :, ::-1].copy()          # BGR
    img = cv2.convertScaleAbs(img, alpha=1.15, beta=5)

    def px(ll):
        ll = np.asarray(ll, float).reshape(-1, 2)
        r, c = st.ll_to_rc(ll[:, 0], ll[:, 1])
        return np.round(np.c_[c, r]).astype(np.int32)

    def poly(ring, col, th=1):
        if ring and len(ring) >= 3:
            cv2.polylines(img, [px(ring).reshape(-1, 1, 2)], True, col, th, cv2.LINE_AA)
    sc = json.load(open(os.path.join(pkg_dir, "scene.json"))) if os.path.exists(os.path.join(pkg_dir, "scene.json")) else {}
    fc = json.load(open(os.path.join(pkg_dir, "raw", "osm.geojson")))
    for f in sc.get("fairways") or []:
        poly(f.get("polygon"), COL["fairway"], 1)
    for b in sc.get("bunkers") or []:
        poly(b.get("polygon"), COL["bunker"], 1)
    for w in sc.get("water") or []:
        poly(w.get("polygon"), COL["water"], 2)
    for g in sc.get("greens") or []:
        if g.get("kind") != "practice":
            poly(g.get("polygon"), COL["det_green"], 2)
    for t in sc.get("tee_complexes") or []:
        for b in t.get("boxes") or []:
            poly(b.get("polygon"), COL["det_tee"], 1)
    for f in fc["features"]:
        p = f.get("properties") or {}
        if p.get("origin") == "fastscene" or p.get("golf") not in ("green", "tee"):
            continue
        for r in _rings(f["geometry"]):
            poly(r, COL["osm_green"] if p["golf"] == "green" else COL["osm_tee"], 2)
    pkg = json.load(open(os.path.join(pkg_dir, "package.json"))) if os.path.exists(os.path.join(pkg_dir, "package.json")) else {}
    dec = json.load(open(os.path.join(pkg_dir, "decision.json"))) if os.path.exists(os.path.join(pkg_dir, "decision.json")) else {}
    lines = {}
    for f in fc["features"]:
        p = f.get("properties") or {}
        if p.get("golf") == "hole" and f["geometry"]["type"] == "LineString":
            lines[str(p.get("ref"))] = f["geometry"]["coordinates"]
    for ref, h in (pkg.get("holes") or {}).items():       # the built holes (OSM, joint or the stage selector's)
        ln = h.get("hole_line_ll") or ([h["tee_ll"], h["green_ll"]] if h.get("tee_ll") and h.get("green_ll") else None)
        if ln:
            lines[str(ref)] = ln
    gate = json.load(open(os.path.join(pkg_dir, "gate.json"))) if os.path.exists(os.path.join(pkg_dir, "gate.json")) else {}
    for ref, h in (pkg.get("holes") or {}).items():           # the strategy pick's aim point
        d = (dec.get("holes") or {}).get(str(ref))
        if d and h.get("aim_ll"):
            a = px(h["aim_ll"])[0]
            cv2.circle(img, (int(a[0]), int(a[1])), 5, COL["aim"], -1)
    for ref, ln in lines.items():
        q = px(ln)
        cv2.polylines(img, [q.reshape(-1, 1, 2)], False, COL["line"], 2, cv2.LINE_AA)
        cv2.circle(img, tuple(int(v) for v in q[0]), 4, COL["line"], -1)
        cv2.putText(img, ref, tuple(int(v) for v in q[0] + [6, -6]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(img, ref, tuple(int(v) for v in q[0] + [6, -6]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 1, cv2.LINE_AA)
    picks = {}
    for ref, h in (pkg.get("holes") or {}).items():
        d = (dec.get("holes") or {}).get(str(ref))
        if d and h.get("tee_ll") and h.get("bearing_deg") is not None:
            # aim point: `aim` yds right of the tee line at the pick's carry is not in decision.json; draw the club
            picks[str(ref)] = d
    cv2.imwrite(os.path.join(out_dir, "overview.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    paths = [os.path.join(out_dir, "overview.jpg")]
    if holes:
        H, W = img.shape[:2]
        for ref in sorted(lines, key=lambda r: int(r) if r.isdigit() else 99):
            q = px(lines[ref])
            x0, y0 = q.min(0) - 60
            x1, y1 = q.max(0) + 60
            x0, y0 = max(int(x0), 0), max(int(y0), 0)
            x1, y1 = min(int(x1), W), min(int(y1), H)
            crop = img[y0:y1, x0:x1].copy()
            if crop.size == 0:
                continue
            k = 520.0 / max(crop.shape[:2])
            crop = cv2.resize(crop, None, fx=k, fy=k, interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_LINEAR)
            h = (pkg.get("holes") or {}).get(ref) or {}
            d = picks.get(ref) or {}
            txt = (f"hole {ref}  par {h.get('par')}  card {h.get('length')}  measured {h.get('measured_length')}  "
                   f"pick {d.get('pick', '-')}")
            band = np.zeros((26, crop.shape[1], 3), np.uint8)
            cv2.putText(band, txt[:90], (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
            p = os.path.join(out_dir, f"hole_{int(ref):02d}.jpg" if ref.isdigit() else f"hole_{ref}.jpg")
            cv2.imwrite(p, np.vstack([band, crop]), [cv2.IMWRITE_JPEG_QUALITY, 85])
            paths.append(p)
    return paths, gate


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg_dir")
    ap.add_argument("--out")
    ap.add_argument("--holes", action="store_true")
    a = ap.parse_args()
    paths, gate = render(a.pkg_dir, a.out, a.holes)
    print("\n".join(paths))
    print(json.dumps(gate)[:600])
