"""Workstream B: turn probe runs into hole_evidence/1 files and score each source against OSM hole lines.

  python course_data/zero_tap/evidence/evaluate.py --run runs/<run> [--run runs/<run2> ...]

Writes:
  course_data/zero_tap/evidence/courses/<slug>.json   hole_evidence/1 (see README.md)
  course_data/zero_tap/evidence/results.json          coverage x accuracy per source, per split

Truth: OSM golf=hole ways (ref = hole number, first vertex = tee, last vertex = green), the same truth the
generalize validation set uses. The evidence itself never reads the hole lines: it is built from the probe
record (website images registered to NAIP, OCR) or from OSM green/tee/pin features' own `ref` tags.
"""
import argparse
import glob
import json
import math
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GEN = os.path.join(ROOT, "course_data", "generalize")

MATCH_RADIUS_M = 60.0          # an evidence point counts for the nearest truth hole within this distance
MIN_INLIERS = 12


def jload(p, d=None):
    try:
        with open(p) as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001
        return d


def m_per_deg(lat):
    return 111_320.0 * math.cos(math.radians(lat)), 110_540.0


def dist_m(a, b):
    kx, ky = m_per_deg((a[1] + b[1]) / 2)
    return math.hypot((a[0] - b[0]) * kx, (a[1] - b[1]) * ky)


def seg_dist_m(p, a, b):
    kx, ky = m_per_deg(p[1])
    px, py = 0.0, 0.0
    ax, ay = (a[0] - p[0]) * kx, (a[1] - p[1]) * ky
    bx, by = (b[0] - p[0]) * kx, (b[1] - p[1]) * ky
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(ax + t * dx - px, ay + t * dy - py)


def centroid(geom):
    t = geom["type"]
    if t == "Point":
        return geom["coordinates"]
    ring = geom["coordinates"][0] if t == "Polygon" else geom["coordinates"][0][0] if t == "MultiPolygon" \
        else geom["coordinates"]
    xs = [c[0] for c in ring]
    ys = [c[1] for c in ring]
    return [sum(xs) / len(xs), sum(ys) / len(ys)]


def ref_num(v):
    m = re.match(r"^\s*(\d{1,2})\s*$", str(v or ""))
    return int(m.group(1)) if m else None


# ----------------------------------------------------------------------------- truth
def truth_holes(slug):
    g = jload(os.path.join(GEN, "courses", slug, "osm_golf.geojson"), {}) or {}
    holes = {}
    for f in g.get("features", []):
        p = f["properties"]
        if p.get("golf") != "hole" or f["geometry"]["type"] != "LineString":
            continue
        n = ref_num(p.get("ref"))
        if n and n not in holes:
            cs = f["geometry"]["coordinates"]
            holes[n] = dict(line=cs, tee=cs[0], green=cs[-1])
    return holes


def nearest_hole(pt, holes, what="line"):
    best = (None, 1e9)
    for n, h in holes.items():
        if what == "line":
            d = min(seg_dist_m(pt, a, b) for a, b in zip(h["line"][:-1], h["line"][1:]))
        else:
            d = dist_m(pt, h[what])
        if d < best[1]:
            best = (n, d)
    return best


def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1:
            inside = not inside
    return inside


def line_frac_inside(line, poly, k=20):
    pts = []
    for a, b in zip(line[:-1], line[1:]):
        for i in range(k):
            t = i / k
            pts.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    pts.append(tuple(line[-1]))
    return sum(point_in_poly(p, poly) for p in pts) / len(pts)


# ----------------------------------------------------------------------------- sources
def ev_osm_ref(slug):
    """Evidence from OSM green / tee / pin features that carry their own `ref` (not the hole lines)."""
    g = jload(os.path.join(GEN, "courses", slug, "osm_golf.geojson"), {}) or {}
    out = []
    for f in g.get("features", []):
        p = f["properties"]
        kind = p.get("golf")
        if kind not in ("green", "tee", "pin"):
            continue
        n = ref_num(p.get("ref"))
        if not n or n > 18:
            continue
        out.append(dict(hole=n, role="green" if kind in ("green", "pin") else "tee", point=centroid(f["geometry"]),
                        source="osm_feature_ref", url=f"https://www.openstreetmap.org/{p['osm_type']}/{p['osm_id']}",
                        confidence=0.95))
    return out


def px_to_lonlat(naip):
    from pyproj import Transformer
    a, b, c, d, e, f = naip["lo"]["transform"]
    tr = Transformer.from_crs(naip["crs"], "EPSG:4326", always_xy=True)

    def fn(x, y):
        return list(tr.transform(a * x + b * y + c, d * x + e * y + f))
    return fn


def apply_h(H, x, y):
    w = H[2][0] * x + H[2][1] * y + H[2][2]
    return ((H[0][0] * x + H[0][1] * y + H[0][2]) / w, (H[1][0] * x + H[1][1] * y + H[1][2]) / w)


def reg_confidence(m):
    """Registration confidence from inlier count (calibrated in results.json on the train split)."""
    ni = m["inliers"]
    return round(min(0.95, max(0.05, 1 - math.exp(-(ni - MIN_INLIERS) / 25.0))), 3)


def ev_website(rec):
    """Evidence from registered website images: per-hole images -> footprint + tee/green anchors;
    overview maps / PDF pages -> OCR'd hole numbers placed on the ground."""
    out = []
    naip = rec.get("naip")
    if not naip:
        return out
    to_ll = px_to_lonlat(naip)
    for r in rec.get("registrations", []):
        m = r.get("match")
        if not m or not m.get("sane") or m["inliers"] < MIN_INLIERS:
            continue
        H = m["H"]
        w, h = r["wh"]
        conf = reg_confidence(m)
        fp = [to_ll(*xy) for xy in m["footprint_px"]]
        if r.get("kind") == "hole" and r.get("hole"):
            out.append(dict(hole=r["hole"], role="footprint", footprint=fp, source="website_hole_image",
                            url=r["url"], page=r.get("page"), inliers=m["inliers"], confidence=conf,
                            tee=to_ll(*apply_h(H, w / 2, h * 0.9)), green=to_ll(*apply_h(H, w / 2, h * 0.1))))
        for n, x, y, oc in r.get("ocr") or []:
            src = "website_map_ocr" if r.get("kind") != "pdf_page" else "scorecard_pdf_map_ocr"
            out.append(dict(hole=int(n), role="label", point=to_ll(*apply_h(H, x, y)), source=src,
                            url=r["url"], inliers=m["inliers"], ocr_conf=oc,
                            confidence=round(conf * min(1.0, oc / 90.0), 3)))
    return out


def ev_thirdparty(rec):
    """golfify / OpenGolfAPI: per-hole coordinates if the free responses carry any."""
    out = []
    for key in ("golfify", "opengolfapi"):
        r = rec.get(key) or {}
        for pt in r.get("hole_points") or []:
            out.append(dict(hole=pt["hole"], role=pt["role"], point=pt["point"], source=key, url=r.get("url"),
                            confidence=0.9))
    return out


# ----------------------------------------------------------------------------- scoring
def score_item(it, holes):
    """-> (scored: bool, correct: bool, detail)"""
    if it["role"] in ("green", "tee", "label"):
        what = "line" if it["role"] == "label" else it["role"]
        n, d = nearest_hole(it["point"], holes, what)
        if n is None or d > MATCH_RADIUS_M:
            return False, False, dict(nearest=n, d=round(d, 1))
        return True, n == it["hole"], dict(nearest=n, d=round(d, 1))
    if it["role"] == "footprint":
        fr = {n: line_frac_inside(h["line"], it["footprint"]) for n, h in holes.items()}
        best = max(fr, key=fr.get) if fr else None
        if best is None or fr[best] < 0.5:
            return False, False, dict(best=best, frac=round(fr.get(best, 0), 2) if best else 0)
        h = holes.get(it["hole"])
        det = dict(best=best, frac=round(fr[best], 2))
        if h:
            det["tee_err_m"] = round(dist_m(it["tee"], h["tee"]), 1)
            det["green_err_m"] = round(dist_m(it["green"], h["green"]), 1)
            det["own_frac"] = round(fr.get(it["hole"], 0), 2)
        return True, best == it["hole"] or fr.get(it["hole"], 0) >= 0.8, det
    return False, False, {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", default=[])
    ap.add_argument("--out", default=os.path.join(HERE, "results.json"))
    a = ap.parse_args()
    val = jload(os.path.join(GEN, "validation_set.json"))
    split = {c["slug"]: c["split"] for c in val["courses"]}
    recs = {}
    for r in a.run:
        d = r if os.path.isabs(r) else os.path.join(HERE, r)
        for f in sorted(glob.glob(os.path.join(d, "*.json"))):
            rec = jload(f)
            if rec and rec.get("slug"):
                recs[rec["slug"]] = rec               # later runs override
    slugs = sorted(set(split) | set(recs))
    os.makedirs(os.path.join(HERE, "courses"), exist_ok=True)
    stats = defaultdict(lambda: defaultdict(Counter))
    site = Counter()
    per_course = {}
    for slug in slugs:
        holes = truth_holes(slug)
        if not holes:
            continue
        rec = recs.get(slug, {})
        items = ev_osm_ref(slug) + (ev_website(rec) + ev_thirdparty(rec) if rec else [])
        sp = split.get(slug, "other")
        srcs = sorted({it["source"] for it in items})
        evid = defaultdict(list)
        for it in items:
            ok_scored, ok, det = score_item(it, holes)
            st = stats[it["source"]][sp]
            st["items"] += 1
            st["scored"] += ok_scored
            st["correct"] += ok_scored and ok
            if it["role"] == "footprint" and "tee_err_m" in det:
                st["tee_err_sum"] += det["tee_err_m"]
                st["green_err_sum"] += det["green_err_m"]
                st["anchor_n"] += 1
                st["tee_within_40m"] += det["tee_err_m"] <= 40
                st["green_within_40m"] += det["green_err_m"] <= 40
            e = {k: v for k, v in it.items() if k != "hole"}
            evid[str(it["hole"])].append(e)
        for s in srcs:
            hs = {it["hole"] for it in items if it["source"] == s}
            stats[s][sp]["courses"] += 1
            stats[s][sp]["holes_covered"] += len(hs & set(holes))
        for sp2 in (sp, "all"):
            stats["_truth"][sp2]["courses"] += 1
            stats["_truth"][sp2]["holes"] += len(holes)
        if rec:
            ss = rec.get("site_summary") or {}
            site["probed"] += 1
            for k in ("has_website", "reachable"):
                site[k] += bool(ss.get(k))
            site["robots_blocked_home"] += ss.get("has_website", False) and ss.get("robots_ok") is False
            site["hole_pages>=9"] += ss.get("hole_pages", 0) >= 9
            site["hole_images>=9"] += ss.get("hole_images", 0) >= 9
            site["any_hole_images"] += ss.get("hole_images", 0) > 0
            site["layout_images"] += ss.get("layout_images", 0) > 0
            site["pdfs"] += ss.get("pdfs", 0) > 0
            site["videos"] += ss.get("videos", 0) > 0
            regs = rec.get("registrations", [])
            site["images_tried"] += len(regs)
            site["images_registered"] += sum(1 for r in regs if (r.get("match") or {}).get("sane")
                                             and r["match"]["inliers"] >= MIN_INLIERS)
            site["courses_with_registered_image"] += any((r.get("match") or {}).get("sane")
                                                         and r["match"]["inliers"] >= MIN_INLIERS for r in regs)
            gf = rec.get("golfify") or {}
            site["golfify_page"] += gf.get("status") == 200
            site["golfify_hole_geo"] += bool(gf.get("hole_geo_keys"))
            og = rec.get("opengolfapi") or {}
            site["opengolfapi_detail"] += og.get("status") == 200
            site["opengolfapi_hole_geo"] += bool([k for k in (og.get("geo_keys") or {}) if "hole" in k.lower()])
        doc = dict(schema="hole_evidence/1", slug=slug, name=rec.get("name"), split=sp,
                   sources=srcs, holes=dict(sorted(evid.items(), key=lambda kv: int(kv[0]))))
        if evid:
            with open(os.path.join(HERE, "courses", f"{slug}.json"), "w") as fh:
                json.dump(doc, fh, indent=1)
        per_course[slug] = dict(split=sp, sources=srcs, n_holes_with_evidence=len(evid))
    # summarise
    table = {}
    for s, bysp in stats.items():
        if s == "_truth":
            continue
        row = {}
        for sp in ("train", "test", "all"):
            c = Counter()
            for k, v in bysp.items():
                if sp == "all" or k == sp:
                    c.update(v)
            n_courses = stats["_truth"][sp]["courses"] if sp != "all" else stats["_truth"]["all"]["courses"]
            row[sp] = dict(courses_with_evidence=c["courses"], courses_total=n_courses,
                           course_coverage=round(c["courses"] / n_courses, 3) if n_courses else None,
                           hole_coverage=round(c["holes_covered"] / max(1, stats["_truth"][sp]["holes"]), 3),
                           items=c["items"], scored=c["scored"], correct=c["correct"],
                           accuracy=round(c["correct"] / c["scored"], 3) if c["scored"] else None)
            if c["anchor_n"]:
                row[sp].update(anchor_n=c["anchor_n"], tee_err_mean_m=round(c["tee_err_sum"] / c["anchor_n"], 1),
                               green_err_mean_m=round(c["green_err_sum"] / c["anchor_n"], 1),
                               tee_within_40m=c["tee_within_40m"], green_within_40m=c["green_within_40m"])
        table[s] = row
    res = dict(schema="hole_evidence_eval/1", runs=a.run, match_radius_m=MATCH_RADIUS_M, min_inliers=MIN_INLIERS,
               truth=dict(courses=stats["_truth"]["all"]["courses"], holes=stats["_truth"]["all"]["holes"]),
               sources=table, website_survey=dict(site), per_course=per_course)
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(dict(sources=table, website_survey=site), indent=1))


if __name__ == "__main__":
    main()
