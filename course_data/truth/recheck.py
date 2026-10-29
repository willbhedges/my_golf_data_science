"""Re-check a hand truth map on a sharper / newer photo (display year): tee boxes, landing tree lines, doglegs, par-3 greens.

  python3 course_data/truth/recheck.py --slug eagle_knoll --img /tmp/disp_eagle_knoll [--sets Back,Eagle,Middle]
        [--out course_data/truth/eagle_knoll/recheck] [--holes 1,3]

Reads course_data/truth/<slug>/holes_truth.json (tees per set, green, hole line), hand_zones_ll.json (corridor zones,
any frame: drawn from their WGS84 rings), render/frames.json (the trace frame of every tee shot), the package OSM
(tee pads) and vision_any/<slug>/raw/hag.tif (lidar canopy). The photo is --img (a fetch_imagery.py folder:
naip_rgb.tif, naip_nir.tif, georef.json); the package photo is drawn beside it for comparison.

Per hole, JPEGs in --out:
  hNN_tees.jpg     tee area in the first set's frame (tee -> its 250-yd aim): every set's tee (dot + label: card yds and
                   measured - card, measured = tee -> hole line -> green as platform/tee_line.py), the OSM tee pads,
                   5-yd grid labelled in yds along from that set's tee (+ = toward the green)
  hNN_hole.jpg     whole hole: hole line (magenta), each set's 250-yd tee line and aim point, the hand zones, green
  hNN_land.jpg     par 4 / 5: the trace frame 130-440 yds x +/-75: new photo + zones + lidar 2.5 m edge (cyan) + aim
                   points | new CIR + zones | package photo + zones
  hNN_green.jpg    par 3: the green and its surround with the truth green outline and centre
Also summary.json: per hole and set, card, measured, measured - card, aim offsets (yds right of the set's own tee line
of the hole line's 250-yd point: the engine searches +/-40 around the tee line).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path.insert(0, os.path.join(CD, "imagery"))
sys.path.insert(0, HERE)
import render as R                      # noqa: E402
import corridor as CO                   # noqa: E402

COL = {k: tuple(int(c) for c in v) for k, v in CO.COL.items()}
SETCOL = [(255, 60, 60), (60, 140, 255), (255, 255, 255), (255, 210, 0), (255, 0, 255), (0, 255, 255)]


def _k(lat):
    lat0 = math.radians(lat)
    return np.array([math.cos(lat0) * 111320 / 0.9144, 111320 / 0.9144])


def measure(tee, line, green):
    """tee -> nearest point of the hole line -> along it -> green centre (yds), and the tee's distance off the line."""
    tee = np.asarray(tee[:2], float)
    k = _k(tee[1])
    P = (np.array([p[:2] for p in (line or [])] + [list(green[:2])], float) - tee) * k
    if len(P) < 2:
        return float(np.linalg.norm(P[-1])), 0.0
    best = None
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        d = b - a
        u = float(np.clip(-(a @ d) / max(float(d @ d), 1e-9), 0, 1))
        dist = float(np.linalg.norm(a + u * d))
        if best is None or dist < best[0]:
            best = (dist, i, u)
    _, i, u = best
    pts = [P[i] + u * (P[i + 1] - P[i])] + list(P[i + 1:])
    return float(np.linalg.norm(pts[0])) + sum(float(np.linalg.norm(b - a)) for a, b in zip(pts[:-1], pts[1:])), best[0]


def tee_line():
    import importlib.util
    spec = importlib.util.spec_from_file_location("cdp_tee_line", os.path.join(CD, "platform", "tee_line.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def frame(tee_ll, aim_ll, ppy, a0, a1, lat):
    return R.Frame(tee_ll, aim_ll, ppy=ppy, tee_px=(lat * ppy, a1 * ppy), proj="utm",
                   size=(int(round(2 * lat * ppy)), int(round((a1 - a0) * ppy))))


def u8(a):
    a = np.nan_to_num(np.asarray(a, float), nan=40.0)
    return np.clip(a, 0, 255).astype(np.uint8)


def grid(img, a0, a1, lat, ppy, step=10, label=20, font=0.35):
    import cv2
    img = img.copy()
    for a in np.arange(math.ceil(a0 / step) * step, a1 + 1e-6, step):
        y = int(round((a1 - a) * ppy))
        cv2.line(img, (0, y), (img.shape[1], y), (255, 255, 255) if a % label == 0 else (170, 170, 170), 1)
        if a % label == 0:
            cv2.putText(img, f"{a:.0f}", (2, y - 2), cv2.FONT_HERSHEY_SIMPLEX, font, (0, 0, 0), 3)
            cv2.putText(img, f"{a:.0f}", (2, y - 2), cv2.FONT_HERSHEY_SIMPLEX, font, (255, 255, 0), 1)
    for x in np.arange(-math.floor(lat / step) * step, lat + 1e-6, step):
        px = int(round((x + lat) * ppy))
        cv2.line(img, (px, 0), (px, img.shape[0]), (255, 255, 255) if x == 0 else (150, 150, 150), 1)
        if x % label == 0 and x != 0:
            cv2.putText(img, f"{x:+.0f}", (px + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, font, (0, 0, 0), 3)
            cv2.putText(img, f"{x:+.0f}", (px + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, font, (255, 255, 0), 1)
    return img


def text(img, s, p, col=(255, 255, 255), font=0.4):
    import cv2
    p = (int(p[0]), int(p[1]))
    cv2.putText(img, s, p, cv2.FONT_HERSHEY_SIMPLEX, font, (0, 0, 0), 3)
    cv2.putText(img, s, p, cv2.FONT_HERSHEY_SIMPLEX, font, col, 1)


def poly_px(fr, ring_ll):
    return np.round(fr.ll_to_px(np.asarray(ring_ll, float)[:, :2]) * 8).astype(np.int32)


def draw_zones(img, fr, zones, width=1):
    import cv2
    for z in zones:
        if z["lie"] in ("rough",):
            continue
        p = poly_px(fr, z["poly_ll"])
        cv2.polylines(img, [p], True, (0, 0, 0), width + 2, shift=3)
        cv2.polylines(img, [p], True, COL.get(z["lie"], (255, 255, 255)), width, shift=3)
    return img


def lidar_edge(img, hag, thr=2.5):
    import cv2
    m = (np.nan_to_num(hag, nan=0.0) > thr).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img, cs, -1, (0, 255, 255), 1)
    return img


def cir(nir, rgb):
    a = np.dstack([nir[..., 0], rgb[..., 0], rgb[..., 1]]).astype(float)
    lo, hi = np.nanpercentile(a, 1), np.nanpercentile(a, 99.5)
    return u8((a - lo) / max(hi - lo, 1) * 255)


def stack(panels):
    h = max(p.shape[0] for p in panels)
    out = [np.pad(p, ((0, h - p.shape[0]), (0, 4), (0, 0)), constant_values=255) for p in panels]
    return np.concatenate(out, 1)


def title(img, s):
    bar = np.full((18, img.shape[1], 3), 255, np.uint8)
    import cv2
    cv2.putText(bar, s, (3, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1)
    return np.concatenate([bar, img], 0)


def save(path, img, q=82):
    from PIL import Image
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(img).save(path, "JPEG", quality=q, optimize=True)


def main():
    import cv2
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--img", required=True, help="display imagery folder (naip_rgb.tif [, naip_nir.tif], georef.json)")
    ap.add_argument("--sets", default="")
    ap.add_argument("--out")
    ap.add_argument("--holes", default="")
    a = ap.parse_args()
    S = a.slug
    TL = tee_line()
    T = json.load(open(os.path.join(HERE, S, "holes_truth.json")))
    hzp = os.path.join(HERE, S, "hand_zones_ll.json")
    HZ = json.load(open(hzp))["holes"] if os.path.exists(hzp) else {}
    FJ = json.load(open(os.path.join(HERE, S, "render", "frames.json")))
    sets = [s for s in a.sets.split(",") if s] or list(T.get("sets") or [])
    out = a.out or os.path.join(HERE, S, "recheck")
    want = set(h for h in a.holes.split(",") if h)
    geo = json.load(open(os.path.join(a.img, "georef.json")))
    yr = (geo.get("imagery") or {}).get("year")
    gsd = (geo.get("imagery") or {}).get("resolution_m")
    NEW = CO.Raster(os.path.join(a.img, "naip_rgb.tif"), label=f"NAIP {yr} {gsd} m")
    NIR = CO.Raster(os.path.join(a.img, "naip_nir.tif")) if os.path.exists(os.path.join(a.img, "naip_nir.tif")) else None
    pk = os.path.join(CD, "packages", S, "imagery")
    OLD = CO.Raster(os.path.join(pk, "naip_rgb.tif"), label=f"package NAIP {CO._year(pk)}")
    hp = os.path.join(CD, "vision_any", S, "raw", "hag.tif")
    HAG = CO.Raster(hp) if os.path.exists(hp) else None
    osm = os.path.join(CD, "packages", S, "raw", "osm.geojson")
    pads = []
    if os.path.exists(osm):
        for f in json.load(open(osm))["features"]:
            if (f.get("properties") or {}).get("golf") == "tee" and f["geometry"]["type"] == "Polygon":
                pads.append(f["geometry"]["coordinates"][0])
    summ = dict(slug=S, imagery=dict(year=yr, resolution_m=gsd, acquired=(geo.get("imagery") or {}).get("acquired")),
                sets=sets, holes={})
    for ref, h in sorted(T["holes"].items(), key=lambda kv: int(kv[0])):
        if want and ref not in want:
            continue
        par = int(h["par"])
        tees = {s: h["tees"][s] for s in sets if s in (h.get("tees") or {})}
        if not tees:
            continue
        line, green = h.get("hole_line_ll"), h["green_ll"]
        rec = {}
        aims = {}
        for s, t in tees.items():
            m, off = measure(t, line, green)
            aim, how = TL.aim_point(t, line, green, h["card"].get(s), par)
            aims[s] = aim
            rec[s] = dict(card=h["card"].get(s), measured=round(m, 1), delta=round(m - h["card"].get(s, m), 1),
                          off_line=round(off, 1), how=h.get("tee_how", {}).get(s, ""))
        s0 = sets[0] if sets[0] in tees else next(iter(tees))
        t0 = tees[s0]
        a0_ll = aims[s0] if par > 3 else green
        # ---- tees: every set in s0's frame
        fr1 = R.Frame(t0, a0_ll, ppy=1.0, proj="utm")
        al = {s: -float(fr1.ll_to_yds([t])[0][1]) for s, t in tees.items()}
        xs = {s: float(fr1.ll_to_yds([t])[0][0]) for s, t in tees.items()}
        lo, hi = min(al.values()) - 22, max(al.values()) + 22
        lat = max(30.0, max(abs(v) for v in xs.values()) + 15)
        ppy = 6.0
        fr = frame(t0, a0_ll, ppy, lo, hi, lat)
        img = u8(NEW.warp(fr)[..., :3])
        for p in pads:
            cv2.polylines(img, [poly_px(fr, p)], True, (255, 255, 255), 1, shift=3)
        img = grid(img, lo, hi, lat, ppy, step=5, label=10)
        for i, (s, t) in enumerate(tees.items()):
            p = fr.ll_to_px([t])[0]
            c = SETCOL[i % len(SETCOL)]
            cv2.circle(img, (int(p[0]), int(p[1])), 5, (0, 0, 0), -1)
            cv2.circle(img, (int(p[0]), int(p[1])), 4, c, -1)
            r = rec[s]
            text(img, f"{s} {r['card']} ({r['delta']:+.0f})", (p[0] + 7, p[1] + 4), c, 0.42)
        old = u8(OLD.warp(fr)[..., :3])
        old = grid(old, lo, hi, lat, ppy, step=5, label=10)
        save(os.path.join(out, f"h{int(ref):02d}_tees.jpg"),
             stack([title(img, f"{S} {ref} tees on NAIP {yr} ({s0} frame; yds along from {s0})"),
                    title(old, OLD.label)]))
        # ---- whole hole
        L = max(rec[s0]["measured"], 150) + 30
        ppy = 1.6
        lat = 110.0
        fr = frame(t0, a0_ll if par > 3 else green, ppy, min(lo, -10), L, lat)
        img = u8(NEW.warp(fr)[..., :3])
        if ref in HZ:
            draw_zones(img, fr, HZ[ref]["zones"])
            cv2.polylines(img, [poly_px(fr, HZ[ref]["footprint_ll"])], True, (255, 255, 0), 1, shift=3)
        if line:
            cv2.polylines(img, [poly_px(fr, list(line) + [green])], False, (255, 0, 255), 2, shift=3)
        if h.get("green_poly_ll"):
            cv2.polylines(img, [poly_px(fr, h["green_poly_ll"])], True, (255, 255, 255), 1, shift=3)
        img = grid(img, min(lo, -10), L, lat, ppy, step=50, label=50)
        for i, (s, t) in enumerate(tees.items()):
            c = SETCOL[i % len(SETCOL)]
            p = fr.ll_to_px([t])[0]
            q = fr.ll_to_px([aims[s]])[0]
            if par > 3:
                cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), c, 1)
                cv2.circle(img, (int(q[0]), int(q[1])), 4, c, -1)
            cv2.circle(img, (int(p[0]), int(p[1])), 3, c, -1)
            text(img, s, (p[0] + 5, p[1] - 3 - 10 * i), c, 0.35)
        save(os.path.join(out, f"h{int(ref):02d}_hole.jpg"),
             title(img, f"{ref} par {par}: hole line (magenta), 250-yd tee lines per set, zones, NAIP {yr}"))
        # ---- landing zone or green
        if par > 3 and ref in FJ:
            f0 = FJ[ref]["frame"]
            a0, a1, lat, ppy = 130.0, 440.0, 75.0, 3.0
            fr = frame(f0["tee_ll"], f0["aim_ll"], ppy, a0, a1, lat)
            rgb = NEW.warp(fr)[..., :3]
            P1 = u8(rgb)
            if HAG is not None:
                P1 = lidar_edge(P1, HAG.warp(fr)[..., 0])
            zs = HZ.get(ref, {}).get("zones", [])
            P1 = draw_zones(P1, fr, zs)
            for i, (s, t) in enumerate(tees.items()):
                q = fr.ll_to_px([aims[s]])[0]
                c = SETCOL[i % len(SETCOL)]
                cv2.circle(img if False else P1, (int(q[0]), int(q[1])), 4, c, -1)
                d = -float(fr.ll_to_yds([t])[0][1])
                text(P1, f"{s} tee {d:+.0f}", (4, 30 + 13 * i), c, 0.38)
            P1 = grid(P1, a0, a1, lat, ppy)
            P = [title(P1, f"{ref}: NAIP {yr} + zones + lidar 2.5 m edge (cyan); along from {FJ[ref].get('set')} tee")]
            if NIR is not None:
                P2 = draw_zones(cir(NIR.warp(fr), rgb), fr, zs)
                P.append(title(grid(P2, a0, a1, lat, ppy), f"CIR {yr}"))
            P3 = draw_zones(u8(OLD.warp(fr)[..., :3]), fr, zs)
            P.append(title(grid(P3, a0, a1, lat, ppy), OLD.label))
            save(os.path.join(out, f"h{int(ref):02d}_land.jpg"), stack(P))
        elif par == 3:
            Lg = rec[s0]["measured"]
            a0, a1, lat, ppy = Lg - 45, Lg + 30, 40.0, 5.0
            fr = frame(t0, green, ppy, a0, a1, lat)
            P1 = u8(NEW.warp(fr)[..., :3])
            if h.get("green_poly_ll"):
                cv2.polylines(P1, [poly_px(fr, h["green_poly_ll"])], True, (255, 0, 255), 1, shift=3)
            g = fr.ll_to_px([green])[0]
            cv2.circle(P1, (int(g[0]), int(g[1])), 4, (255, 0, 255), -1)
            P1 = grid(P1, a0, a1, lat, ppy, step=5, label=10)
            P2 = grid(u8(OLD.warp(fr)[..., :3]), a0, a1, lat, ppy, step=5, label=10)
            save(os.path.join(out, f"h{int(ref):02d}_green.jpg"),
                 stack([title(P1, f"{ref} par 3 green (truth outline magenta), NAIP {yr}"), title(P2, OLD.label)]))
        # aim offsets: the 250-yd hole-line point relative to each set's own tee line (it IS the tee line: 0), and
        # relative to the base set's tee line, for a quick look at how far another set's line swings
        summ["holes"][ref] = dict(par=par, tees=rec)
        print(ref, " | ".join(f"{s} {r['card']} {r['delta']:+.1f}" for s, r in rec.items()), flush=True)
    json.dump(summ, open(os.path.join(out, "summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
