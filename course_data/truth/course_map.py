"""Whole-course routing map for hand truth: NAIP of the package bbox with every OSM green (G<n>), tee pad (T<n>) and
golf=hole line drawn and numbered, plus the package's own holes (tee -> green, labelled with its hole number).

  python3 course_data/truth/course_map.py --slug national_kc [--out DIR] [--mpp 1.0] [--tiles 2x2]
      -> DIR/map.jpg (or map_r<i>c<j>.jpg tiles), DIR/features.json {G<n>: centroid + polygon, T<n>: ...}

features.json is what a holes_truth.py reads to snap a hole's green / tees to the mapped OSM shapes by id
(course_data/truth/<slug>/holes_truth.py). A UTM grid every --grid m (100) (labels = metres from the map's SW corner)
lets an unmapped tee or green be read off the map: features.json carries the grid origin and UTM zone.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)


def main():
    import cv2
    import rasterio
    from pyproj import Transformer
    from rasterio.warp import Resampling, reproject
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--out")
    ap.add_argument("--mpp", type=float, default=1.0)
    ap.add_argument("--tiles", default="1x1")
    ap.add_argument("--bbox", help="lon0,lat0,lon1,lat1 (default: the package imagery)")
    ap.add_argument("--grid", type=float, default=100.0, help="grid step (m); labels every 2 steps")
    a = ap.parse_args()
    pk = os.path.join(CD, "packages", a.slug)
    out = a.out or os.path.join(HERE, a.slug, "map")
    os.makedirs(out, exist_ok=True)
    src = rasterio.open(os.path.join(pk, "imagery", "naip_rgb.tif"))
    to_ll = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)
    b = src.bounds
    if a.bbox:
        lon0, lat0, lon1, lat1 = map(float, a.bbox.split(","))
    else:
        (lon0, lon1), (lat0, lat1) = [sorted(v) for v in zip(*[to_ll.transform(x, y) for x, y in
                                                               ((b.left, b.bottom), (b.right, b.top))])]
    zone = int((lon0 + lon1) / 2 // 6 + 31)
    utm = f"EPSG:{32600 + zone}"
    fw = Transformer.from_crs("EPSG:4326", utm, always_xy=True)
    bw = Transformer.from_crs(utm, "EPSG:4326", always_xy=True)
    x0, y0 = fw.transform(lon0, lat0)
    x1, y1 = fw.transform(lon1, lat1)
    W, H = int((x1 - x0) / a.mpp), int((y1 - y0) / a.mpp)
    from rasterio.transform import from_origin
    T = from_origin(x0, y1, a.mpp, a.mpp)
    img = np.zeros((3, H, W), np.uint8)
    for i in range(3):
        reproject(src.read(i + 1), img[i], src_transform=src.transform, src_crs=src.crs, dst_transform=T,
                  dst_crs=utm, resampling=Resampling.average if a.mpp > 0.6 else Resampling.bilinear)
    img = np.ascontiguousarray(img.transpose(1, 2, 0)[..., ::-1])   # BGR for cv2

    def px(ll):
        ll = np.asarray(ll, float)
        x, y = fw.transform(ll[:, 0], ll[:, 1])
        return np.c_[(np.asarray(x) - x0) / a.mpp, (y1 - np.asarray(y)) / a.mpp]

    ov = img.copy()
    for gx in np.arange(0, x1 - x0, a.grid):
        cv2.line(ov, (int(gx / a.mpp), 0), (int(gx / a.mpp), H), (255, 255, 255), 1)
    for gy in np.arange(0, y1 - y0, a.grid):
        cv2.line(ov, (0, int(H - gy / a.mpp)), (W, int(H - gy / a.mpp)), (255, 255, 255), 1)
    img = cv2.addWeighted(ov, 0.3, img, 0.7, 0)
    for gx in np.arange(0, x1 - x0, 2 * a.grid):
        cv2.putText(img, f"{int(gx)}", (int(gx / a.mpp) + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    for gy in np.arange(0, y1 - y0, 2 * a.grid):
        cv2.putText(img, f"{int(gy)}", (2, int(H - gy / a.mpp) - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    fc = json.load(open(os.path.join(pk, "raw", "osm.geojson")))
    feats, ng, nt = {}, 0, 0

    def rings(g):
        if g["type"] == "Polygon":
            return [g["coordinates"][0]]
        if g["type"] == "MultiPolygon":
            return [p[0] for p in g["coordinates"]]
        return []

    def label(t, p, col):
        cv2.putText(img, t, (int(p[0]) + 3, int(p[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 3)
        cv2.putText(img, t, (int(p[0]) + 3, int(p[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.42, col, 1)
    for f in fc["features"]:
        p, g = f["properties"], f["geometry"]
        kind = p.get("golf")
        if kind in ("green", "tee"):
            for r in rings(g):
                r = np.asarray(r, float)[:, :2]
                q = px(r)
                if (q[:, 0].max() < 0) or (q[:, 1].max() < 0) or q[:, 0].min() > W or q[:, 1].min() > H:
                    continue
                c = r.mean(0)
                if kind == "green":
                    ng += 1
                    k, col = f"G{ng}", (255, 0, 255)
                else:
                    nt += 1
                    k, col = f"T{nt}", (0, 255, 255)
                feats[k] = dict(kind=kind, center_ll=[round(float(c[0]), 7), round(float(c[1]), 7)],
                                poly_ll=[[round(float(x), 7), round(float(y), 7)] for x, y in r], osm=p.get("osm_id"))
                cv2.polylines(img, [np.round(q * 8).astype(np.int32)], True, col, 1, shift=3)
                label(k, q.mean(0), col)
        elif kind == "hole" and g["type"] == "LineString":
            q = px(np.asarray(g["coordinates"], float)[:, :2])
            cv2.polylines(img, [np.round(q * 8).astype(np.int32)], False, (0, 165, 255), 1, shift=3)
            label(f"osm{p.get('ref')}", q[0], (0, 165, 255))
    pj = os.path.join(pk, "package.json")
    if os.path.exists(pj):
        pkg = json.load(open(pj))
        for ref, h in pkg["holes"].items():
            if h.get("tee_ll") and h.get("green_ll"):
                q = px([h["tee_ll"], h["green_ll"]])
                cv2.arrowedLine(img, tuple(int(v) for v in q[0]), tuple(int(v) for v in q[1]), (0, 0, 255), 1,
                                tipLength=0.04)
                label(f"P{ref}", (q[0] + q[1]) / 2, (80, 80, 255))
    ty, tx = (int(v) for v in a.tiles.split("x"))
    paths = []
    for i in range(ty):
        for j in range(tx):
            r0, r1 = H * i // ty, H * (i + 1) // ty
            c0, c1 = W * j // tx, W * (j + 1) // tx
            name = "map.jpg" if ty * tx == 1 else f"map_r{i}c{j}.jpg"
            cv2.imwrite(os.path.join(out, name), img[max(0, r0 - 40):r1 + 40, max(0, c0 - 40):c1 + 40],
                        [cv2.IMWRITE_JPEG_QUALITY, 82])
            paths.append(name)
    json.dump(dict(slug=a.slug, utm=utm, origin_utm=[x0, y0], mpp=a.mpp, size=[W, H], tiles=a.tiles,
                   note="grid labels = metres east / north of origin_utm (map SW corner)", features=feats),
              open(os.path.join(out, "features.json"), "w"), indent=1)
    print(out, paths, ng, "greens", nt, "tees")


def grid_to_ll(features_json, e, n):
    """(metres east, metres north of the map's SW corner) read off the grid -> [lon, lat]."""
    from pyproj import Transformer
    F = json.load(open(features_json))
    bw = Transformer.from_crs(F["utm"], "EPSG:4326", always_xy=True)
    lon, lat = bw.transform(F["origin_utm"][0] + e, F["origin_utm"][1] + n)
    return [round(lon, 7), round(lat, 7)]


if __name__ == "__main__":
    main()
