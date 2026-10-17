"""Score course_data/segment/<slug>/segment.geojson against OSM, the Spirit Hollow hand map, and tee truth.

    python3 course_data/segment/evaluate.py            # every course with a segment.geojson -> eval.json / eval.md

Light (rasterising polygons on the 0.6 m NAIP grid, one process); runs in the sandbox or on Actions.

1. vs OSM, inside the course boundary: exclusive label maps painted fairway < tee < green < bunker < water
   for both OSM and the model polygons; pixel IoU, precision and recall per class. OSM is incomplete (tees,
   water), so "precision" against it is a lower bound. Object metrics: green recall/precision at IoU >= 0.5,
   bunker recall/precision by overlap, tee recall/precision with centroids within 10 yds.
2. vs the hand-checked Spirit Hollow map (spirit_hollow/hand_zones_ll.json; inside each hole's screenshot
   footprint, zones painted in order so later zones win; fairway = fairway + first_cut, sand, water). OSM is
   scored the same way as a reference.
3. Tees: Spirit Hollow screenshot tee per hole (hand_zones tee_ll) -> distance to the nearest OSM box, U-Net
   tee polygon and lidar pad; tee placement (tees/eval_tees.py truth) with U-Net tees as extra candidates;
   on every course the U-Net tees that match no OSM box (unmapped-tee candidates) and how many a lidar pad
   corroborates.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)

CLASSES = ["green", "tee", "fairway", "bunker", "water"]
PAINT = ["fairway", "tee", "green", "bunker", "water"]          # later wins
CODE = {c: i + 1 for i, c in enumerate(CLASSES)}
WATER_GOLF = {"water_hazard", "lateral_water_hazard"}
TEE_MATCH_YD = 10.0


def osm_class(p):
    g = p.get("golf")
    if g in ("green", "tee", "fairway", "bunker"):
        return g
    if g in WATER_GOLF or p.get("natural") == "water" or p.get("water") or p.get("landuse") in ("reservoir", "basin"):
        return "water"
    return None


def course_info(slug):
    meta = json.load(open(os.path.join(HERE, slug, "meta.json")))
    req = json.load(open(os.path.join(ROOT, meta["request"])))
    pkg_path = os.path.join(ROOT, req.get("package") or "")
    pkg = json.load(open(pkg_path)) if req.get("package") and os.path.exists(pkg_path) else None
    pdir = os.path.dirname(pkg_path) if pkg else None
    return meta, req, pkg, pdir


def load_seg(slug):
    fc = json.load(open(os.path.join(HERE, slug, "segment.geojson")))
    return fc["features"]


def load_osm_features(pdir):
    fc = json.load(open(os.path.join(pdir, "raw", "osm.geojson")))
    out = []
    for f in fc["features"]:
        if f["geometry"]["type"] not in ("Polygon", "MultiPolygon"):
            continue
        c = osm_class(f["properties"])
        if c:
            out.append(dict(f, properties=dict(f["properties"], **{"class": c})))
    return out


class Grid:
    def __init__(self, probs_path):
        import rasterio
        from pyproj import Transformer
        with rasterio.open(probs_path) as s:
            self.T, self.crs, self.shape = s.transform, s.crs, (s.height, s.width)
        self.fwd = Transformer.from_crs("EPSG:4326", self.crs, always_xy=True).transform

    def proj(self, geom):
        from shapely.geometry import shape
        from shapely.ops import transform
        g = geom if hasattr(geom, "geom_type") else shape(geom)
        return transform(self.fwd, g)

    def raster(self, geoms_vals, fill=0):
        import rasterio.features
        gv = [(g, v) for g, v in geoms_vals if g is not None and not g.is_empty]
        if not gv:
            return np.full(self.shape, fill, np.uint8)
        return rasterio.features.rasterize(gv, out_shape=self.shape, transform=self.T, fill=fill, dtype="uint8")

    def label_map(self, feats, classes=PAINT):
        lab = np.zeros(self.shape, np.uint8)
        for c in classes:
            gs = [self.proj(f["geometry"]).buffer(0) for f in feats if f["properties"]["class"] == c]
            m = self.raster([(g, 1) for g in gs])
            lab[m > 0] = CODE[c]
        return lab


def iou_table(pred, ref, region):
    out = {}
    for c in CLASSES:
        p, r = (pred == CODE[c]) & region, (ref == CODE[c]) & region
        inter, uni = int((p & r).sum()), int((p | r).sum())
        out[c] = dict(iou=round(inter / uni, 3) if uni else None,
                      precision=round(inter / p.sum(), 3) if p.sum() else None,
                      recall=round(inter / r.sum(), 3) if r.sum() else None,
                      pred_m2=round(float(p.sum()) * 0.36), ref_m2=round(float(r.sum()) * 0.36))
    return out


def object_metrics(seg, osm, grid):
    from shapely.strtree import STRtree
    res = {}
    P = {c: [grid.proj(f["geometry"]).buffer(0) for f in seg if f["properties"]["class"] == c
             and f["properties"]["src"].startswith("segment:ariadgolf")] for c in CLASSES}
    R = {c: [grid.proj(f["geometry"]).buffer(0) for f in osm if f["properties"]["class"] == c] for c in CLASSES}

    def best_iou(a, bs, tree):
        best = 0.0
        for i in tree.query(a):
            b = bs[i]
            u = a.union(b).area
            best = max(best, a.intersection(b).area / u if u else 0)
        return best

    g_ref = [g for g in R["green"] if g.area >= 100]
    if g_ref and P["green"]:
        tp, tr = STRtree(P["green"]), STRtree(g_ref)
        ious = [best_iou(g, P["green"], tp) for g in g_ref]
        prec = [best_iou(g, g_ref, tr) >= 0.5 for g in P["green"]]
        res["green"] = dict(osm=len(g_ref), model=len(P["green"]), recall_iou50=round(np.mean([i >= 0.5 for i in ious]), 3),
                            precision_iou50=round(float(np.mean(prec)), 3), mean_best_iou=round(float(np.mean(ious)), 3))
    for c in ("bunker", "fairway"):
        if R[c] and P[c]:
            tp, tr = STRtree(P[c]), STRtree(R[c])
            rec = [any(P[c][i].intersection(a).area > 0.25 * min(a.area, 20) for i in tp.query(a)) for a in R[c]]
            pre = [any(R[c][i].intersection(a).area > 0.25 * min(a.area, 20) for i in tr.query(a)) for a in P[c]]
            res[c] = dict(osm=len(R[c]), model=len(P[c]), recall_overlap=round(float(np.mean(rec)), 3),
                          precision_overlap=round(float(np.mean(pre)), 3))
    if R["tee"] and P["tee"]:
        rc = np.array([(g.centroid.x, g.centroid.y) for g in R["tee"]])
        pc = np.array([(g.centroid.x, g.centroid.y) for g in P["tee"]])
        d = np.hypot(pc[:, None, 0] - rc[None, :, 0], pc[:, None, 1] - rc[None, :, 1]) / 0.9144
        res["tee"] = dict(osm=len(rc), model=len(pc), match_yd=TEE_MATCH_YD,
                          recall=round(float((d.min(0) <= TEE_MATCH_YD).mean()), 3),
                          precision=round(float((d.min(1) <= TEE_MATCH_YD).mean()), 3))
    return res


def boundary_region(pkg, grid):
    from shapely.geometry import shape
    b = (pkg or {}).get("course", {}).get("boundary")
    if not b:
        return np.ones(grid.shape, bool)
    g = shape(b) if isinstance(b, dict) else shape({"type": "Polygon", "coordinates": [b]})
    return grid.raster([(grid.proj(g).buffer(20), 1)]) > 0


def hand_eval(grid, sources):
    """{source: {class: iou...}} inside the hand map footprints of Spirit Hollow (sources = {name: label map})."""
    from shapely.geometry import Polygon
    hz = json.load(open(os.path.join(CD, "spirit_hollow", "hand_zones_ll.json")))["holes"]
    lie_cls = {"fairway": "fairway", "first_cut": "fairway", "sand": "bunker", "water": "water"}
    HC = ("fairway", "fairway_only", "bunker", "water")
    acc = {s: {c: [0, 0, 0, 0] for c in HC} for s in sources}   # inter, union, pred, ref
    per_hole = {}
    for k, h in hz.items():
        fp = grid.raster([(grid.proj(Polygon(h["footprint_ll"])), 1)]) > 0
        hand = np.zeros(grid.shape, np.uint8)
        fonly = np.zeros(grid.shape, bool)
        for z in h["zones"]:
            m = grid.raster([(grid.proj(Polygon(z["poly_ll"])).buffer(0), 1)]) > 0
            hand[m] = CODE.get(lie_cls.get(z["lie"]), 0)
            fonly[m] = z["lie"] == "fairway"
        per_hole[k] = {}
        for s, lab in sources.items():
            ph = {}
            for c in HC:
                cc = "fairway" if c == "fairway_only" else c
                p = (lab == CODE[cc]) & fp
                r = (fonly if c == "fairway_only" else (hand == CODE[c])) & fp
                i, u = int((p & r).sum()), int((p | r).sum())
                a = acc[s][c]
                a[0] += i; a[1] += u; a[2] += int(p.sum()); a[3] += int(r.sum())
                ph[c] = round(i / u, 3) if u else None
            per_hole[k][s] = ph
    tot = {s: {c: dict(iou=round(a[0] / a[1], 3) if a[1] else None, precision=round(a[0] / a[2], 3) if a[2] else None,
                       recall=round(a[0] / a[3], 3) if a[3] else None) for c, a in v.items()} for s, v in acc.items()}
    return dict(total=tot, per_hole=per_hole)


def unet_tees(seg):
    from shapely.geometry import shape
    out = []
    for i, f in enumerate(seg):
        if f["properties"]["class"] == "tee" and f["properties"]["src"].startswith("segment:ariadgolf"):
            g = shape(f["geometry"])
            gs = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
            ring = max(gs, key=lambda x: x.area).exterior.coords
            c = g.centroid
            out.append(dict(id=f"unet:{i}", coords=[(y, x) for x, y in ring], centroid=(c.y, c.x),
                            source="unet", p=f["properties"]["p"], area_m2=f["properties"]["area_m2"]))
    return out


def tee_eval(slug, pkg_slug, seg):
    """Tee findings: unmapped-tee candidates on every course; Spirit Hollow truth and placement."""
    sys.path[:0] = [os.path.join(CD, "tees")]
    import eval_tees as E
    import lidar_pads
    import place_tee as pt
    c = E.COURSES[pkg_slug]
    lines, tees, greens = E.load_osm(os.path.join(ROOT, c["osm"]))
    ut = unet_tees(seg)
    gc = [pt.centroid_ll(g["coords"]) for g in greens if len(g["coords"]) >= 3]
    ut = [t for t in ut if not gc or min(pt.haversine_yd(t["centroid"], g) for g in gc) > 20]   # greens look like tees
    near = {id(t) for ts in pt.assign_tees_to_holes(lines, ut).values() for t in ts}
    ut_near = [t for t in ut if id(t) in near]
    oc = [pt.centroid_ll(t["coords"]) for t in tees if t["coords"]]
    dem = os.path.join(ROOT, c["dem"])
    pads = lidar_pads.detect_pads(dem, greens=greens, lines=lines) if os.path.exists(dem) else []
    unm = [t for t in ut_near if not oc or min(pt.haversine_yd(t["centroid"], o) for o in oc) > TEE_MATCH_YD]
    corr = [t for t in unm if pads and min(pt.haversine_yd(t["centroid"], p["centroid"]) for p in pads) <= TEE_MATCH_YD]
    res = dict(unet_tees=len(ut), unet_tees_near_first_leg=len(ut_near), osm_boxes=len(oc),
               matched_osm=len(ut_near) - len(unm), unmapped_candidates=len(unm), corroborated_by_lidar_pad=len(corr),
               lidar_pads=len(pads),
               unmapped=[dict(lat=round(t["centroid"][0], 6), lon=round(t["centroid"][1], 6), p=t["p"],
                              area_m2=t["area_m2"], lidar=t in corr) for t in unm])
    yards = {r: v for r, v in E.cards(pkg_slug).items() if r in lines}
    meth = {"joint": pt.place_course_sets(lines, tees, yards, greens=greens),
            "joint+lidar": pt.place_course_sets(lines, tees, yards, greens=greens, pads=pads),
            "joint+unet": pt.place_course_sets(lines, tees, yards, greens=greens, pads=ut_near),
            "joint+lidar+unet": pt.place_course_sets(lines, tees, yards, greens=greens, pads=pads + ut_near)}
    res["placement"] = {m: dict(internal=E.internal(lines, greens, yards, p)) for m, p in meth.items()}
    if pkg_slug == "spirit_hollow":
        for m, p in meth.items():
            s = E.spirit_hollow_truth(lines, greens, p)
            res["placement"][m]["screenshot_set"] = {k: v for k, v in s.items()}
        hz = json.load(open(os.path.join(CD, "spirit_hollow", "hand_zones_ll.json")))["holes"]
        rows = []
        for k, h in hz.items():
            T = (h["tee_ll"][1], h["tee_ll"][0])

            def nearest(cands, key):
                ds = [pt.haversine_yd(T, key(x)) for x in cands]
                return round(min(ds), 1) if ds else None
            rows.append(dict(key=k, osm_box=nearest(tees, lambda t: pt.centroid_ll(t["coords"])),
                             unet=nearest(ut, lambda t: t["centroid"]), lidar=nearest(pads, lambda t: t["centroid"])))
        res["screenshot_tees"] = rows
    return res


def evaluate(slug):
    meta, req, pkg, pdir = course_info(slug)
    pkg_slug = os.path.basename(pdir) if pdir else None
    grid = Grid(os.path.join(HERE, slug, "probs.tif"))
    seg = load_seg(slug)
    out = dict(slug=slug, package=pkg_slug, naip=meta["naip"], model_sha=meta["model_sha"])
    lab_u = grid.label_map(seg)                                  # U-Net classes + NIR-rule water
    raw_water = None
    try:
        import rasterio
        with rasterio.open(os.path.join(HERE, slug, "probs.tif")) as s_:
            q = s_.read().astype(np.float32)
        am = np.concatenate([250 - q.sum(0, keepdims=True), q]).argmax(0)
        raw_water = np.where(am == 5, CODE["water"], 0).astype(np.uint8)   # the U-Net's own water class
    except Exception:  # noqa: BLE001
        pass
    if pdir:
        osm = load_osm_features(pdir)
        lab_o = grid.label_map(osm)
        region = boundary_region(pkg, grid)
        out["vs_osm"] = {"segment": iou_table(lab_u, lab_o, region)}
        if raw_water is not None:
            out["vs_osm"]["unet_water_class"] = iou_table(raw_water, lab_o, region)["water"]
        out["objects_vs_osm"] = object_metrics(seg, osm, grid)
        out["osm_counts"] = {c: sum(f["properties"]["class"] == c for f in osm) for c in CLASSES}
        if pkg_slug == "spirit_hollow":
            out["vs_hand"] = hand_eval(grid, {"segment": lab_u, "osm": lab_o})
        try:
            out["tees"] = tee_eval(slug, pkg_slug, seg)
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            out["tees"] = {"error": repr(e)}
    return out


def fmt(x):
    return "-" if x is None else f"{x:.2f}"


def md(res):
    L = ["# NAIP golf segmentation (ariadgolf U-Net) vs OSM and the Spirit Hollow hand map", "",
         "Generated by `course_data/segment/evaluate.py`. Pixel metrics on the 0.6 m NAIP grid inside the OSM "
         "course boundary (+20 m). Label maps painted fairway < tee < green < bunker < water. OSM is the reference, "
         "so features OSM lacks count against the model's precision.", "",
         "## Pixel IoU vs OSM (precision / recall in brackets)", "",
         "water = NAIP NIR rule (model.nir_water); the U-Net's own water class is in the last column.", "",
         "| course | NAIP | " + " | ".join(CLASSES) + " | U-Net water class |", "|---|---|" + "---|" * (len(CLASSES) + 1)]
    for r in res:
        if "vs_osm" not in r:
            continue
        u = r["vs_osm"]["segment"]
        cells = [f"{fmt(u[c]['iou'])} ({fmt(u[c]['precision'])}/{fmt(u[c]['recall'])})" for c in CLASSES]
        w = r["vs_osm"].get("unet_water_class") or {}
        cells.append(f"{fmt(w.get('iou'))} ({fmt(w.get('precision'))}/{fmt(w.get('recall'))})")
        L.append(f"| {r['slug']} | {os.path.basename(r['naip'])} | " + " | ".join(cells) + " |")
    L += ["", "## Objects vs OSM", "",
          "| course | greens: recall@IoU.5 / precision / mean best IoU | bunkers: recall / precision (overlap) | "
          "fairways: recall / precision (overlap) | tees: recall / precision (10 yds) |", "|---|---|---|---|---|"]
    for r in res:
        o = r.get("objects_vs_osm")
        if not o:
            continue
        g, b, f, t = (o.get(k, {}) for k in ("green", "bunker", "fairway", "tee"))
        L.append(f"| {r['slug']} | {fmt(g.get('recall_iou50'))} / {fmt(g.get('precision_iou50'))} / "
                 f"{fmt(g.get('mean_best_iou'))} ({g.get('osm')} OSM, {g.get('model')} model) | "
                 f"{fmt(b.get('recall_overlap'))} / {fmt(b.get('precision_overlap'))} ({b.get('osm')}/{b.get('model')}) | "
                 f"{fmt(f.get('recall_overlap'))} / {fmt(f.get('precision_overlap'))} ({f.get('osm')}/{f.get('model')}) | "
                 f"{fmt(t.get('recall'))} / {fmt(t.get('precision'))} ({t.get('osm')}/{t.get('model')}) |")
    for r in res:
        if "vs_hand" not in r:
            continue
        L += ["", f"## Spirit Hollow hand map ({r['slug']}, inside the 16 screenshot footprints)", "",
              "fairway = hand fairway + first_cut (OSM convention); fairway only = hand fairway without first_cut; "
              "bunker = sand. IoU (precision / recall). OSM scored the same way as the reference.", "",
              "| source | fairway | fairway only | bunker | water |", "|---|---|---|---|---|"]
        for s, v in r["vs_hand"]["total"].items():
            L.append(f"| {s} | " + " | ".join(f"{fmt(v[c]['iou'])} ({fmt(v[c]['precision'])}/{fmt(v[c]['recall'])})"
                                             for c in ("fairway", "fairway_only", "bunker", "water")) + " |")
    L += ["", "## Tees", "",
          "U-Net tee polygons near a hole's first leg (OSM hole lines; > 20 yds from a green). *unmapped* = no OSM "
          "box centroid within 10 yds; *lidar* = a tees/lidar_pads.py pad within 10 yds.", "",
          "| course | U-Net tees near a first leg | OSM boxes | matching an OSM box | unmapped candidates | of which lidar-corroborated |",
          "|---|---|---|---|---|---|"]
    for r in res:
        t = r.get("tees")
        if not t or "error" in t:
            continue
        L.append(f"| {r['slug']} | {t['unet_tees_near_first_leg']} | {t['osm_boxes']} | {t['matched_osm']} | "
                 f"{t['unmapped_candidates']} | {t['corroborated_by_lidar_pad']} |")
    L += ["", "Tee placement (tees/place_tee.place_course_sets) with U-Net tees as extra candidates (like lidar pads):", "",
          "| course | method | measured within 5 yds of card | walk-backs | SH screenshot tee <= 10 yds | SH median tee err |",
          "|---|---|---|---|---|---|"]
    for r in res:
        t = r.get("tees")
        if not t or "placement" not in t:
            continue
        for m, v in t["placement"].items():
            s = v.get("screenshot_set")
            L.append(f"| {r['slug']} | {m} | {v['internal']['card_within_5']:.0%} | {v['internal']['walkbacks']} | "
                     + (f"{s['tee_within_10']:.0%} | {s['median_tee_err']} |" if s else "- | - |"))
    for r in res:
        t = r.get("tees") or {}
        if t.get("screenshot_tees"):
            L += ["", f"Spirit Hollow screenshot tees ({r['slug']}): yds to the nearest candidate", "",
                  "| hole | OSM box | U-Net tee | lidar pad |", "|---|---|---|---|"]
            for x in t["screenshot_tees"]:
                L.append(f"| {x['key']} | {x['osm_box']} | {x['unet']} | {x['lidar']} |")
    return "\n".join(L) + "\n"


def main():
    sys.path[:0] = [HERE]
    slugs = sys.argv[1:] or sorted(d for d in os.listdir(HERE)
                                   if os.path.exists(os.path.join(HERE, d, "segment.geojson")))
    res = []
    for s in slugs:
        print("==", s, flush=True)
        res.append(evaluate(s))
    json.dump(res, open(os.path.join(HERE, "eval.json"), "w"), indent=1)
    open(os.path.join(HERE, "eval.md"), "w").write(md(res))
    print(md(res))


if __name__ == "__main__":
    main()
