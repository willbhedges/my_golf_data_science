"""Tee placement before/after (Q2/Q3 of course_data/research/auto_course_lookup.md), offline, seconds.

    python3 course_data/tees/eval_tees.py            # -> course_data/tees/eval_tees.json + eval_tees.md

Methods compared on the same OSM data (packages/<slug>/raw/osm.geojson) and cards:
  independent   the old S2 (package.place_tees / place_course.py): place_tee per set, borrow a neighbour's
                box within 10 yds, distances to the hole line's last vertex
  joint         place_tee.place_course_sets: all sets together, back-to-front order, green centroid
  joint+lidar   joint + lidar flat-pad candidates (lidar_pads.py) on holes where a set has no OSM box

Every placed tee is measured the same way (tee -> hole-line turning points -> OSM green centroid).

Spirit Hollow vs the screenshots (Q1 truth, spirit_hollow/screenshot_tee_sets.json):
  tee <= 10       placed tee of the screenshot's set within 10 yds of the screenshot tee georeferenced on
                  NAIP (hand_zones_ll.json tee_ll; '2B' is matched from 2F, treat with care)
  length <= 5     |measured length of that tee - the screenshot's measured length| <= 5
  ...golfer set   the same with Black on every hole (what the as-built package was scored on)
All courses, internal: share of hole x set placements whose measured length is within 5 yds of the card,
walk-backs, order violations (a longer set in front of a shorter one), sets forced onto one box.
"""
from __future__ import annotations

import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path[:0] = [HERE]
import place_tee as pt  # noqa: E402
import screenshot_sets  # noqa: E402

COURSES = {
    "spirit_hollow": dict(osm="course_data/packages/spirit_hollow/raw/osm.geojson",
                          dem="course_data/imagery/spirit_hollow/dem.tif"),
    "veenker": dict(osm="course_data/packages/veenker/raw/osm.geojson",
                    dem="course_data/packages/veenker/imagery/dem.tif"),
    "mozingo_lake": dict(osm="course_data/packages/mozingo_lake/raw/osm.geojson",
                         dem="course_data/packages/mozingo_lake/imagery/dem.tif"),
}


def load_osm(path):
    fc = json.load(open(path))
    lines, tees, greens = {}, [], []
    for f in fc["features"]:
        p, g = f["properties"], f["geometry"]
        if p.get("golf") == "hole" and g["type"] == "LineString" and p.get("ref"):
            lines[str(p["ref"])] = [(c[1], c[0]) for c in g["coordinates"]]
        elif p.get("golf") == "tee" and g["type"] in ("Polygon", "Point"):
            cs = g["coordinates"][0] if g["type"] == "Polygon" else [g["coordinates"]]
            tees.append(dict(id=p.get("osm_id"), coords=[(c[1], c[0]) for c in cs], tags=p))
        elif p.get("golf") == "green" and g["type"] == "Polygon":
            greens.append(dict(id=p.get("osm_id"), coords=[(c[1], c[0]) for c in g["coordinates"][0]]))
    return lines, tees, greens


def cards(slug):
    """{ref: {set: yards}} for the course's card in the repo."""
    if slug == "spirit_hollow":
        c = json.load(open(os.path.join(HERE, "scorecard.json")))
        return {str(i + 1): {n: s["yards"][i] for n, s in c["tee_sets"].items()} for i in range(18)}
    pkg = json.load(open(os.path.join(CD, "packages", slug, "package.json")))
    return {k: {n: y for n, y in (h.get("yards") or {}).items() if y} for k, h in pkg["holes"].items()}


def independent(lines, tees, yards):
    """The pre-Q2 S2: platform/package.py place_tees + place_course.py's borrow rule, per set."""
    by_hole = pt.assign_tees_to_holes(lines, tees)
    out = {}
    for ref, line in lines.items():
        res = {}
        for n, y in (yards.get(ref) or {}).items():
            r = pt.place_tee(line, by_hole.get(ref, []), float(y))
            if r["error_yd"] is None or r["error_yd"] > 10 or r["method"] == "walkback":
                alt = pt.place_tee(line, tees, float(y))
                if alt["method"] != "walkback" and alt["error_yd"] is not None and alt["error_yd"] <= 10:
                    alt["borrowed"] = True
                    r = alt
            res[n] = r
        for n, r in res.items():
            r["shared_with"] = sorted(m for m, o in res.items() if m != n and r["tee_id"] and o["tee_id"] == r["tee_id"])
        out[ref] = dict(tees=res)
    return out


def measure(line, green, lat, lon):
    fr, lop = pt._hole_frame(line, green)
    return lop.dist_to_green(fr.fwd(lat, lon))


def internal(lines, greens, yards, placed):
    n = within5 = walk = viol = shared = 0
    for ref, hp in placed.items():
        g = pt.green_for_line(lines[ref], greens)
        ts = hp["tees"]
        order = sorted(ts, key=lambda s: -float(yards[ref][s]))
        d = {s: measure(lines[ref], g, ts[s]["lat"], ts[s]["lon"]) for s in ts}
        for i, s in enumerate(order):
            n += 1
            within5 += abs(d[s] - yards[ref][s]) <= 5
            walk += ts[s]["method"] == "walkback"
            viol += any(d[s] + 2 < d[m] for m in order[i + 1:])
            shared += bool(ts[s].get("shared_with"))
    return dict(placements=n, card_within_5=round(within5 / max(n, 1), 3), walkbacks=walk,
                order_violations=viol, on_a_shared_box=shared)


def spirit_hollow_truth(lines, greens, placed, golfer=False):
    sys.path.insert(0, os.path.join(ROOT, "spirit_hollow"))
    import course                                                  # noqa: E402  (read only)
    hz = json.load(open(os.path.join(CD, "spirit_hollow", "hand_zones_ll.json")))["holes"]
    sets = screenshot_sets.load()
    rows = []
    for k, set_ in sets.items():
        kk = int(k) if k.isdigit() else k
        h = course.HOLES.get(kk)
        if h is None:
            continue
        ref = k.rstrip("BF")
        s = screenshot_sets.GOLFER_SET if golfer else set_
        r = placed[ref]["tees"].get(s)
        if r is None:
            continue
        g = pt.green_for_line(lines[ref], greens)
        L = measure(lines[ref], g, r["lat"], r["lon"])
        T = hz[k]["tee_ll"]
        e = pt.haversine_yd((T[1], T[0]), (r["lat"], r["lon"]))
        rows.append(dict(key=k, set=s, method=r["method"], tee_err=round(e, 1), measured=round(L, 1),
                         traced=h["length"], len_err=round(L - h["length"], 1)))
    n = len(rows)
    return dict(n=n, tee_within_10=round(sum(r["tee_err"] <= 10 for r in rows) / n, 3),
                length_within_5=round(sum(abs(r["len_err"]) <= 5 for r in rows) / n, 3),
                median_tee_err=statistics.median(r["tee_err"] for r in rows),
                median_abs_len_err=statistics.median(abs(r["len_err"]) for r in rows), rows=rows)


def run(slugs=None, lidar=True):
    res = {}
    for slug, c in COURSES.items():
        if slugs and slug not in slugs:
            continue
        lines, tees, greens = load_osm(os.path.join(ROOT, c["osm"]))
        yards = {r: v for r, v in cards(slug).items() if r in lines}
        meth = {"independent": independent(lines, tees, yards),
                "joint": pt.place_course_sets(lines, tees, yards, greens=greens)}
        if lidar and os.path.exists(os.path.join(ROOT, c["dem"])):
            import lidar_pads
            pads = lidar_pads.detect_pads(os.path.join(ROOT, c["dem"]), greens=greens, lines=lines)
            meth["joint+lidar"] = pt.place_course_sets(lines, tees, yards, greens=greens, pads=pads)
            res.setdefault(slug, {})["lidar_pads"] = len(pads)
        out = res.setdefault(slug, {})
        for m, placed in meth.items():
            out[m] = dict(internal=internal(lines, greens, yards, placed))
            if slug == "spirit_hollow":
                out[m]["screenshot_set"] = spirit_hollow_truth(lines, greens, placed)
                out[m]["golfer_set"] = spirit_hollow_truth(lines, greens, placed, golfer=True)
    return res


def md(res):
    L = ["# Tee placement before / after (Q2 joint assignment, Q3 lidar pads)", "",
         "Generated by `course_data/tees/eval_tees.py` (offline). *independent* = the S2 before this change; "
         "*joint* = ordered joint assignment to the green centroid; *joint+lidar* = plus lidar flat-pad candidates.", ""]
    sh = res.get("spirit_hollow")
    if sh:
        L += ["## Spirit Hollow vs the screenshots (Q1 truth)", "",
              "| method | scored on | tee <= 10 yds | length <= 5 yds | median tee err | median abs len err |",
              "|---|---|---|---|---|---|"]
        for m, v in sh.items():
            if not isinstance(v, dict):
                continue
            for lab, key in (("screenshot's set", "screenshot_set"), ("Black everywhere", "golfer_set")):
                s = v[key]
                L.append(f"| {m} | {lab} | {s['tee_within_10']:.0%} ({sum(r['tee_err'] <= 10 for r in s['rows'])}/{s['n']}) | "
                         f"{s['length_within_5']:.0%} ({sum(abs(r['len_err']) <= 5 for r in s['rows'])}/{s['n']}) | "
                         f"{s['median_tee_err']} | {s['median_abs_len_err']} |")
        L += ["", "Per hole (screenshot's set): tee error yds / measured - screenshot length", "",
              "| key | set | " + " | ".join(m for m in sh if isinstance(sh[m], dict)) + " |",
              "|---|---|" + "---|" * sum(isinstance(sh[m], dict) for m in sh)]
        ms = [m for m in sh if isinstance(sh[m], dict)]
        for i, r in enumerate(sh[ms[0]]["screenshot_set"]["rows"]):
            cells = []
            for m in ms:
                q = sh[m]["screenshot_set"]["rows"][i]
                cells.append(f"{q['tee_err']} / {q['len_err']:+.0f} ({q['method']})")
            L.append(f"| {r['key']} | {r['set']} | " + " | ".join(cells) + " |")
        L.append("")
    L += ["## Internal consistency, every course x every set", "",
          "| course | method | placements | measured within 5 yds of card | walk-backs | order violations | on a shared box |",
          "|---|---|---|---|---|---|---|"]
    for slug, v in res.items():
        for m, x in v.items():
            if not isinstance(x, dict):
                continue
            i = x["internal"]
            L.append(f"| {slug} | {m} | {i['placements']} | {i['card_within_5']:.0%} | {i['walkbacks']} | "
                     f"{i['order_violations']} | {i['on_a_shared_box']} |")
    return "\n".join(L) + "\n"


def main():
    res = run(sys.argv[1:] or None)
    json.dump(res, open(os.path.join(HERE, "eval_tees.json"), "w"), indent=1)
    open(os.path.join(HERE, "eval_tees.md"), "w").write(md(res))
    print(md(res))


if __name__ == "__main__":
    main()
