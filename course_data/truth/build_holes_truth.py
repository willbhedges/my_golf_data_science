"""Hand routing spec -> holes_truth.json (the format course_data/courses/score_auto.py reads), for any course.

  python3 course_data/truth/build_holes_truth.py --slug national_kc

Spec: course_data/truth/<slug>/holes_spec.json, written by hand after checking the whole-course routing map
(course_data/truth/course_map.py: features.json ids G<n> green / T<n> tee pad) and the whole-hole sheets
(course_data/truth/hole_sheet.py):
  {"card": {"source": "...", "sets": {"Black": [358, ...18], ...}, "par": [4, 5, ...]},
   "features": "course_data/truth/<slug>/map/features.json",
   "holes": {"1": {"green": "G12" | [lon, lat], "line": [[lon, lat], ...] (tee area -> corner(s); optional),
                   "pads": ["T7", "T8", ...] | [[lon, lat], ...], "tees": {"Black": "T7" | [lon, lat]} (optional),
                   "note": "..."}}}
Per set, the tee is (in order): the spec's explicit tee; else the pad whose measured length (tee -> line corners ->
green centre) is closest to the card, when within TOL yds; else the nearest-length pad moved along the tee line by
(card - measured), flagged "estimated". Green outline = the OSM polygon of a G id (else none).
Writes holes_truth.json {holes: {ref: {par, card, tees {set: ll}, tee_method {set: ...}, green_ll, green_poly_ll,
hole_line_ll, measured {set: yds}, note}}} and prints the table.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path.insert(0, os.path.join(CD, "imagery"))
import render as R  # noqa: E402

TOL = 10.0


def frame(ll0):
    return R.Frame(ll0, [ll0[0], ll0[1] + 0.001], ppy=1.0, proj="utm")


def length(fr, pts):
    xy = fr.ll_to_yds(np.asarray(pts, float))
    return float(np.sum(np.linalg.norm(np.diff(xy, axis=0), axis=1)))


def build(slug):
    spec = json.load(open(os.path.join(HERE, slug, "holes_spec.json")))
    F = json.load(open(os.path.join(ROOT, spec["features"])))["features"] if spec.get("features") else {}

    def ll(v):
        if isinstance(v, str):
            return F[v]["center_ll"]
        return [float(v[0]), float(v[1])]
    card = spec["card"]
    out = {}
    for ref, hs in sorted(spec["holes"].items(), key=lambda kv: int(kv[0])):
        i = int(ref) - 1
        g = ll(hs["green"])
        gpoly = F[hs["green"]]["poly_ll"] if isinstance(hs["green"], str) else hs.get("green_poly_ll")
        pads = [ll(p) for p in hs.get("pads", [])]
        corners = [ll(p) for p in hs.get("line", [])[1:]]   # line[0] = the tee area (replaced by each tee)
        if not pads and hs.get("line"):
            pads = [ll(hs["line"][0])]                       # no tee pad mapped: the line's start (OSM hole tee)
        fr = frame(g)
        tees, how, meas = {}, {}, {}
        for s, ys in card["sets"].items():
            y = ys[i]
            if not y:
                continue
            if s in hs.get("tees", {}):
                t = ll(hs["tees"][s])
                tees[s], how[s] = t, "hand"
            elif pads:
                L = [length(fr, [p] + corners + [g]) for p in pads]
                k = int(np.argmin([abs(v - y) for v in L]))
                if abs(L[k] - y) <= TOL:
                    tees[s], how[s] = pads[k], f"pad (measured {L[k]:.0f})"
                else:
                    # move the closest pad along its tee line (toward the first corner / the green) by card - measured
                    p, tgt = np.asarray(pads[k]), np.asarray((corners or [g])[0])
                    pf = frame(pads[k])
                    a, b = pf.ll_to_yds([p])[0], pf.ll_to_yds([tgt])[0]
                    u = (b - a) / np.linalg.norm(b - a)
                    q = pf.yds_to_ll([a - u * (y - L[k])])[0]
                    tees[s], how[s] = [round(float(q[0]), 7), round(float(q[1]), 7)], \
                        f"estimated: pad (measured {L[k]:.0f}) moved {y - L[k]:+.0f} yds along the line"
            else:
                continue
            meas[s] = round(length(fr, [tees[s]] + corners + [g]), 1)
        back = max(tees, key=lambda s: card["sets"][s][i]) if tees else None
        line = [tees[back]] + corners + [g] if back else None
        out[ref] = dict(par=card["par"][i], card={s: v[i] for s, v in card["sets"].items()}, tees=tees, tee_method=how,
                        measured=meas, green_ll=g, green_poly_ll=gpoly, hole_line_ll=line, note=hs.get("note", ""),
                        extra_zones=hs.get("extra_zones", []))
    res = dict(slug=slug, source=spec.get("source", ""), card_source=card.get("source"), holes=out)
    json.dump(res, open(os.path.join(HERE, slug, "holes_truth.json"), "w"), indent=1)
    for ref, h in out.items():
        print(ref, h["par"], "  ".join(f"{s} {h['card'][s]}/{h['measured'].get(s, '-')}{'*' if 'estimated' in h['tee_method'].get(s, '') else ''}"
                                      for s in card["sets"]))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    build(ap.parse_args().slug)
