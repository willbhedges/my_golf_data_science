"""Grading sheets for the blind loop: every hole of a built course on independent NAIP imagery, with what the page
believes drawn on it (tee, green, hole line, zones, the calm-day pick), plus a tee zoom, a green zoom and a course
overview. Looked at hole by hole by the grader (BLIND_LOOP.md "Grading").

  python3 blind20_sheets.py --course-dir course_data/library/gate/gate_b20_x --img DIR_WITH_naip_rgb.tif --out DIR

Runs on Actions (.github/workflows/blind_sheets.yml: the NAIP fetch needs the network) or locally where a package has
its imagery on disk. Output: overview.jpg, holes_01.jpg ... (3 holes per sheet), sheets.json.
"""
import argparse
import json
import math
import os

import cv2
import numpy as np

YD = 0.9144
COL = {"fairway": (120, 255, 120), "recovery": (0, 140, 255), "trees": (0, 140, 255), "water": (255, 160, 0),
       "sand": (120, 255, 255), "ob": (0, 0, 255), "native": (255, 0, 255), "green": (255, 255, 255)}  # BGR


def rj(p, d=None):
    try:
        return json.load(open(p))
    except Exception:                                               # noqa: BLE001
        return d


class Img:
    def __init__(self, d):
        import rasterio
        from pyproj import Transformer
        p = os.path.join(d, "naip_rgb.tif")
        with rasterio.open(p) as ds:
            self.a = np.ascontiguousarray(np.transpose(ds.read([1, 2, 3]), (1, 2, 0))[:, :, ::-1])   # BGR
            self.inv = ~ds.transform
            self.fw = ds.transform
            self.res = abs(ds.transform.a)
            self.tr = Transformer.from_crs("EPSG:4326", ds.crs, always_xy=True)
        g = rj(os.path.join(d, "georef.json")) or {}
        im = g.get("imagery") or {}
        self.date = im.get("acquired") or im.get("naip_date") or im.get("year")

    def xy(self, ll):
        return np.array(self.tr.transform(ll[0], ll[1]))

    def px(self, xy):
        c, r = self.inv * (xy[0], xy[1])
        return np.array([c, r])


class Frame:
    """hole frame: yards (x right, a along) about the tee, a axis towards `to`"""

    def __init__(self, im, tee_ll, to_ll):
        self.im = im
        self.t = im.xy(tee_ll)
        v = im.xy(to_ll) - self.t
        self.len = float(np.hypot(*v)) / YD
        self.f = v / max(np.hypot(*v), 1e-6)
        self.r = np.array([self.f[1], -self.f[0]])

    def yd(self, ll):
        d = (self.im.xy(ll) - self.t) / YD
        return float(d @ self.r), float(d @ self.f)

    def crop(self, x0, x1, a0, a1, ppy):
        """image of the box x0..x1 (right), a0..a1 (along), a up; -> (bgr, fn(x, a) -> pixel)"""
        w, h = int(round((x1 - x0) * ppy)), int(round((a1 - a0) * ppy))
        src = np.float32([self.im.px(self.t + YD * (x * self.r + a * self.f)) for x, a in ((x0, a1), (x1, a1), (x0, a0))])
        dst = np.float32([[0, 0], [w, 0], [0, h]])
        M = cv2.getAffineTransform(src, dst)
        out = cv2.warpAffine(self.im.a, M, (w, h), flags=cv2.INTER_AREA if ppy * YD * self.im.res < 1 else cv2.INTER_LINEAR,
                             borderValue=(40, 40, 40))
        return out, (lambda x, a: (int(round((x - x0) * ppy)), int(round((a1 - a) * ppy))))


def poly(img, to, pts, col, th=1, closed=True):
    if len(pts) < 2:
        return
    p = np.int32([to(x, a) for x, a in pts]).reshape(-1, 1, 2)
    cv2.polylines(img, [p], closed, col, th, cv2.LINE_AA)


def text(img, s, org, sc=0.45, col=(255, 255, 255), th=1):
    cv2.putText(img, s, org, cv2.FONT_HERSHEY_SIMPLEX, sc, (0, 0, 0), th + 2, cv2.LINE_AA)
    cv2.putText(img, s, org, cv2.FONT_HERSHEY_SIMPLEX, sc, col, th, cv2.LINE_AA)


def hole_panel(im, ref, h, base, qa, H=760):
    tees = h.get("tees") or {}
    t = tees.get(base) or (next(iter(tees.values())) if tees else None)
    tee_ll = (t or {}).get("tee_ll") or h.get("tee_ll")
    g_ll = h.get("green_ll")
    if not tee_ll or not g_ll:
        p = np.full((H, 300, 3), 40, np.uint8)
        text(p, f"H{ref}: no tee / green", (8, 30))
        return p, {}
    fr = Frame(im, tee_ll, g_ll)
    line = [fr.yd(p) for p in (h.get("hole_line_ll") or [tee_ll, g_ll])]
    gp = [fr.yd(p) for p in (h.get("green_polygon_ll") or [])]
    zones = [(z.get("lie"), [fr.yd(p) for p in z.get("poly") or []]) for z in (h.get("zones_ll") or [])]
    xs = [x for x, _ in line] + [0]
    x0, x1 = min(min(xs) - 75, -85), max(max(xs) + 75, 85)
    a0, a1 = -35, max(fr.len, max(a for _, a in line)) + 45
    ppy = min(1.6, (H - 30) / (a1 - a0), 330 / (x1 - x0))
    main, to = fr.crop(x0, x1, a0, a1, ppy)
    for lie, pts in zones:
        poly(main, to, pts, COL.get(lie, (200, 200, 200)), 1)
    poly(main, to, gp, COL["green"], 1)
    poly(main, to, line, (255, 255, 0), 1, closed=False)
    for k in range(100, int(a1), 100):
        cv2.line(main, to(x0, k), to(x0 + 12, k), (255, 255, 255), 1)
        text(main, str(k), (to(x0 + 14, k)[0], to(x0, k)[1] + 4), 0.35)
    for n, v in tees.items():
        if v.get("tee_ll"):
            cv2.circle(main, to(*fr.yd(v["tee_ll"])), 3, (0, 255, 255) if n == base else (200, 200, 200), -1, cv2.LINE_AA)
    cv2.drawMarker(main, to(*fr.yd(g_ll)), (255, 255, 255), cv2.MARKER_TILTED_CROSS, 8, 1)
    pick = (qa or {}).get("pick") or {}
    if pick.get("along") and t and t.get("aim_ll"):
        fa = Frame(im, tee_ll, t["aim_ll"])
        P = fa.t + YD * (pick["along"] * fa.f + (pick.get("aim") or 0) * fa.r)
        d = (P - fr.t) / YD
        c = to(float(d @ fr.r), float(d @ fr.f))
        cv2.line(main, to(0, 0), c, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.ellipse(main, c, (int(15 * ppy), int(30 * ppy)), 0, 0, 360, (0, 0, 255), 1, cv2.LINE_AA)
    # zooms: tee (70 yds square, 3.6 px / yd) and green (90 yds square, 2.8 px / yd)
    tz, tt = fr.crop(-35, 35, -30, 40, 3.6)
    for lie, pts in zones:
        poly(tz, tt, pts, COL.get(lie, (200, 200, 200)), 1)
    for n, v in tees.items():
        if v.get("tee_ll"):
            cv2.drawMarker(tz, tt(*fr.yd(v["tee_ll"])), (0, 255, 255) if n == base else (220, 220, 220), cv2.MARKER_CROSS, 12, 1)
            text(tz, n[:6], (tt(*fr.yd(v["tee_ll"]))[0] + 6, tt(*fr.yd(v["tee_ll"]))[1] - 4), 0.33)
    cv2.circle(tz, tt(0, 0), int(10 * 3.6), (0, 255, 255), 1, cv2.LINE_AA)        # 10-yd ring round the graded tee
    text(tz, "tee (ring = 10 yds)", (4, 12), 0.38)
    gx, ga = fr.yd(g_ll)
    gz, gt = fr.crop(gx - 45, gx + 45, ga - 45, ga + 45, 2.8)
    poly(gz, gt, gp, COL["green"], 1)
    cv2.drawMarker(gz, gt(gx, ga), (255, 255, 255), cv2.MARKER_TILTED_CROSS, 8, 1)
    for lie, pts in zones:
        if lie in ("water", "sand", "ob"):
            poly(gz, gt, pts, COL[lie], 1)
    text(gz, "green", (4, 12), 0.38)
    side = np.full((max(main.shape[0], tz.shape[0] + gz.shape[0] + 6), max(tz.shape[1], gz.shape[1]), 3), 40, np.uint8)
    side[:tz.shape[0], :tz.shape[1]] = tz
    side[tz.shape[0] + 6:tz.shape[0] + 6 + gz.shape[0], :gz.shape[1]] = gz
    hh = max(main.shape[0], side.shape[0]) + 46
    out = np.full((hh, main.shape[1] + side.shape[1] + 6, 3), 40, np.uint8)
    out[46:46 + main.shape[0], :main.shape[1]] = main
    out[46:46 + side.shape[0], main.shape[1] + 6:] = side
    card = (h.get("yards") or {}).get(base) if isinstance(h.get("yards"), dict) else None
    meas = (t or {}).get("measured_yards") or h.get("measured_length")
    st = (qa or {}).get("status") or ""
    text(out, f"H{ref} par {h.get('par')} card {card} meas {meas} [{base}] {st}", (4, 16), 0.5, (0, 255, 255) if st == "PASS" else (80, 180, 255))
    text(out, f"{pick.get('club', '-')} aim {pick.get('aim', '-')} lands {pick.get('along', '-')} {pick.get('lie', '')} | tee {(t or {}).get('method', '?')} green {(h.get('provenance') or {}).get('green', '?')}"[:100], (4, 34), 0.4)
    info = dict(ref=ref, par=h.get("par"), card=card, measured=meas, status=st, reasons=(qa or {}).get("reasons"),
                tee=(t or {}).get("method"), green=(h.get("provenance") or {}).get("green"), pick=pick,
                zones={k: sum(1 for l, _ in zones if l == k) for k in {l for l, _ in zones}})
    return out, info


def overview(im, pkg, base, W=1500):
    holes = pkg.get("holes") or {}
    pts = []
    for h in holes.values():
        for p in (h.get("hole_line_ll") or []) + [h.get("green_ll"), h.get("tee_ll")]:
            if p:
                pts.append(im.px(im.xy(p)))
    b = (pkg.get("course") or {}).get("bbox")
    if b:
        pts += [im.px(im.xy((b[0], b[1]))), im.px(im.xy((b[2], b[3])))]
    if not pts:
        pts = [np.array([0, 0]), np.array([im.a.shape[1], im.a.shape[0]])]
    pts = np.array(pts)
    m = 80 / im.res
    c0, r0 = np.maximum(pts.min(0) - m, 0).astype(int)
    c1, r1 = np.minimum(pts.max(0) + m, [im.a.shape[1], im.a.shape[0]]).astype(int)
    k = min(1.0, W / max(c1 - c0, 1), W / max(r1 - r0, 1))
    o = cv2.resize(im.a[r0:r1, c0:c1], None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    P = lambda ll: tuple(int(v) for v in ((im.px(im.xy(ll)) - [c0, r0]) * k))
    bd = (pkg.get("course") or {}).get("boundary_geojson") or {}
    for ring in (bd.get("coordinates") or [])[:1] if bd.get("type") == "Polygon" else []:
        cv2.polylines(o, [np.int32([P(p) for p in ring]).reshape(-1, 1, 2)], True, (0, 0, 255), 1, cv2.LINE_AA)
    for ref, h in holes.items():
        t = (h.get("tees") or {}).get(base) or {}
        tee = t.get("tee_ll") or h.get("tee_ll")
        line = h.get("hole_line_ll") or [tee, h.get("green_ll")]
        line = [p for p in line if p]
        if tee and line:
            line = [tee] + line[1:]
        if len(line) >= 2:
            cv2.polylines(o, [np.int32([P(p) for p in line]).reshape(-1, 1, 2)], False, (0, 255, 255), 2, cv2.LINE_AA)
        if h.get("green_polygon_ll"):
            cv2.polylines(o, [np.int32([P(p) for p in h["green_polygon_ll"]]).reshape(-1, 1, 2)], True, (255, 255, 255), 1, cv2.LINE_AA)
        if tee:
            cv2.circle(o, P(tee), 4, (0, 0, 255), -1)
            text(o, str(ref), (P(tee)[0] + 5, P(tee)[1] - 5), 0.6, (0, 255, 255), 2)
        if h.get("green_ll"):
            text(o, str(ref), (P(h["green_ll"])[0] + 5, P(h["green_ll"])[1] + 5), 0.45, (255, 255, 255), 1)
    return o


def build(course_dir, img_dir, out):
    os.makedirs(out, exist_ok=True)
    pkg = rj(os.path.join(course_dir, "package.json"))
    if not pkg:
        raise SystemExit(f"no package.json in {course_dir}")
    qa = rj(os.path.join(course_dir, "qa.json")) or {}
    auto = ((qa.get("checks") or {}).get("auto") or {})
    base = auto.get("set") or pkg.get("tee_set")
    im = Img(img_dir)
    cv2.imwrite(os.path.join(out, "overview.jpg"), overview(im, pkg, base), [cv2.IMWRITE_JPEG_QUALITY, 72])
    holes = pkg.get("holes") or {}
    refs = sorted(holes, key=lambda r: (int("".join(c for c in r if c.isdigit()) or 0), r))
    infos, panels = [], []
    for r in refs:
        p, info = hole_panel(im, r, holes[r], base, (auto.get("holes") or {}).get(r))
        panels.append(p)
        infos.append(info)
    n = 0
    for i in range(0, len(panels), 3):
        grp = panels[i:i + 3]
        hh = max(p.shape[0] for p in grp)
        sheet = np.full((hh, sum(p.shape[1] for p in grp) + 10 * (len(grp) - 1), 3), 255, np.uint8)
        x = 0
        for p in grp:
            sheet[:p.shape[0], x:x + p.shape[1]] = p
            x += p.shape[1] + 10
        n += 1
        cv2.imwrite(os.path.join(out, f"holes_{n:02d}.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 70])
    json.dump(dict(course=(pkg.get("course") or {}).get("name"), base=base, imagery=im.date, holes=infos,
                   legend="yellow dot/cross = graded tee (grey = other sets), white = green outline + centre, cyan = hole line, "
                          "red line + oval = calm pick (30 x 60 yd nominal oval), light green = fairway, orange = trees, blue = water, "
                          "yellow = sand, red = OB, magenta = native"),
              open(os.path.join(out, "sheets.json"), "w"), indent=1)
    print(out, n, "sheets", "imagery", im.date)


def bbox(course_dir, pad_m=140):
    """S,W,N,E round every hole (and the course outline), padded: fetch_imagery.py --bbox"""
    pkg = rj(os.path.join(course_dir, "package.json")) or {}
    pts = []
    for h in (pkg.get("holes") or {}).values():
        pts += [p for p in (h.get("hole_line_ll") or []) + [h.get("green_ll"), h.get("tee_ll")] if p]
        pts += [v["tee_ll"] for v in (h.get("tees") or {}).values() if v.get("tee_ll")]
    b = (pkg.get("course") or {}).get("bbox")
    if b and (not pts or (b[2] - b[0]) < 0.06 and (b[3] - b[1]) < 0.05):      # a resort-wide outline is not fetched
        pts += [(b[0], b[1]), (b[2], b[3])]
    lon, lat = [p[0] for p in pts], [p[1] for p in pts]
    dy = pad_m / 111320.0
    dx = dy / math.cos(math.radians(sum(lat) / len(lat)))
    return f"{min(lat) - dy:.6f},{min(lon) - dx:.6f},{max(lat) + dy:.6f},{max(lon) + dx:.6f}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--course-dir", required=True)
    ap.add_argument("--img")
    ap.add_argument("--out")
    ap.add_argument("--bbox", action="store_true")
    a = ap.parse_args(argv)
    if a.bbox:
        print(bbox(a.course_dir))
        return
    build(a.course_dir, a.img, a.out)


if __name__ == "__main__":
    main()
