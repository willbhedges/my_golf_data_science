"""Blue Hills CC hand truth per hole -> holes_truth.json (the format course_data/courses/score_auto.py reads).

  python3 course_data/truth/blue_hills/holes_truth.py

Spec: holes_spec.json (green = OSM green id, line = OSM golf=hole way [tee area, corners...] with corners checked /
moved onto the fairway by hand, pads = OSM tee pads (map/features.json T ids), card = golfify / AllSquare).
Per hole and set the tee is placed by hand on a pad (PADS below, read off the tee-area zooms: NAIP 2021 0.6 m +
CIR, NAIP 2023, OSM pad outlines): on that pad, the tee is the point on the pad's centre line toward the first
corner (or the green) whose measured length (tee -> corners -> green centre) equals the card; when the card
position falls outside the pad (more than EDGE yds beyond its front / back), the tee is put on the pad's edge and
the remaining difference is reported; |measured - card| > 5 yds is flagged 'estimated'.
Combination sets (Blue/White, White/Gold, Gold/Red) play from one of their two parents' boxes on each hole: the
parent whose card yardage they share (checked: every combo hole equals one parent's yardage).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TR = os.path.dirname(HERE)
CD = os.path.dirname(TR)
ROOT = os.path.dirname(CD)
sys.path.insert(0, os.path.join(CD, "imagery"))
import render as R  # noqa: E402

EDGE = 2.0
FLAG = 5.0
PURE = ["Black", "Blue", "White", "Gold", "Red (M)"]
COMBO = {"Blue/White": ("Blue", "White"), "White/Gold": ("White", "Gold"), "Gold/Red": ("Gold", "Red (M)")}
# hand pad assignment per hole: set -> OSM tee pad id (map/features.json), read off the tee zooms
PADS = {}


def frame(ll0):
    return R.Frame(ll0, [ll0[0], ll0[1] + 0.001], ppy=1.0, proj="utm")


def length(fr, pts):
    xy = fr.ll_to_yds(np.asarray(pts, float))
    return float(np.sum(np.linalg.norm(np.diff(xy, axis=0), axis=1)))


PKG = os.path.join(CD, "courses", "blue_hills", "auto", "package_v0_no_vision.json")


def place(F, pad, corners, g, card, pkg_tee=None):
    """-> (tee_ll, measured, how) for a set on `pad` (an OSM id, [lon, lat] for a hand point, or "pkg": the blind
    package's tee for that set, kept after checking it on the zoom: a box the OSM pads miss)."""
    if pad == "pkg":
        fr = frame(g)
        m = length(fr, [pkg_tee] + corners + [g])
        how = f"blind package tee kept (checked on the zoom; no OSM pad), measured {m:.0f} vs card {card}"
        return pkg_tee, m, ("estimated: " + how) if abs(m - card) > FLAG else how
    if not isinstance(pad, str):
        fr = frame(g)
        t = [float(pad[0]), float(pad[1])]
        return t, length(fr, [t] + corners + [g]), "hand point"
    P = F[pad]
    c = np.asarray(P["center_ll"], float)
    pf = frame(list(c))
    tgt = np.asarray((corners or [g])[0], float)
    a, b = pf.ll_to_yds([c])[0], pf.ll_to_yds([tgt])[0]
    u = (b - a) / np.linalg.norm(b - a)
    proj = (pf.ll_to_yds(np.asarray(P["poly_ll"], float)) - a) @ u
    tmin, tmax = float(proj.min()), float(proj.max())
    fr = frame(g)
    L0 = length(fr, [list(c)] + corners + [g])
    t = L0 - card                                   # + t = forward (toward the green): shorter
    tc = float(np.clip(t, tmin + EDGE, tmax - EDGE)) if tmax - tmin > 2 * EDGE else 0.5 * (tmin + tmax)
    q = pf.yds_to_ll([a + u * tc])[0]
    q = [round(float(q[0]), 7), round(float(q[1]), 7)]
    m = length(fr, [q] + corners + [g])
    how = f"pad {pad} ({tmax - tmin:.0f} yds long), measured {m:.0f} vs card {card}"
    if abs(m - card) > FLAG:
        how = f"estimated: card spot {t - tc:+.0f} yds {'ahead of' if t > tc else 'behind'} pad {pad}; " + how
    return q, m, how


def main():
    spec = json.load(open(os.path.join(HERE, "holes_spec.json")))
    F = json.load(open(os.path.join(ROOT, spec["features"])))["features"]
    card = spec["card"]
    ll = lambda v: F[v]["center_ll"] if isinstance(v, str) else [float(v[0]), float(v[1])]   # noqa: E731
    pk = json.load(open(PKG))["holes"]
    out = {}
    for ref, hs in sorted(spec["holes"].items(), key=lambda kv: int(kv[0])):
        i = int(ref) - 1
        g = ll(hs["green"])
        gpoly = F[hs["green"]]["poly_ll"] if isinstance(hs["green"], str) else None
        corners = [ll(p) for p in hs.get("line", [])[1:]]
        pads = dict(hs.get("tees") or {})
        tees, how, meas = {}, {}, {}
        for s in PURE:
            if s not in pads:
                continue
            tees[s], meas[s], how[s] = place(F, pads[s], corners, g, card["sets"][s][i],
                                             (pk[ref]["tees"].get(s) or {}).get("tee_ll"))
        for s, (p1, p2) in COMBO.items():
            y = card["sets"][s][i]
            src = p1 if card["sets"][p1][i] == y else p2 if card["sets"][p2][i] == y else None
            if src and src in tees:
                tees[s], meas[s], how[s] = tees[src], meas[src], f"= {src} box ({y} on both cards)"
            else:
                # combo yardage matches neither parent: placed on the parent pad nearest to its yardage
                near = min((p1, p2), key=lambda p: abs(card["sets"][p][i] - y))
                tees[s], meas[s], how[s] = place(F, pads[near], corners, g, y)
        line = [tees["Black"]] + corners + [g]
        out[ref] = dict(par=card["par"][i], card={s: v[i] for s, v in card["sets"].items()}, tees=tees, tee_how=how,
                        measured={s: round(v, 1) for s, v in meas.items()}, green_ll=g, green_poly_ll=gpoly,
                        hole_line_ll=line, note=hs.get("note", ""), extra_zones=hs.get("extra_zones", []))
    doc = dict(schema="holes_truth/1", course="Blue Hills Country Club", slug="blue_hills",
               likely_set="Black", key_sets=["Black", "Blue"], sets=list(card["sets"]), card_source=card["source"],
               source="course_data/truth/blue_hills/holes_spec.json + holes_truth.py",
               method=__doc__.strip().split("\n\n", 1)[1], holes=out)
    json.dump(doc, open(os.path.join(HERE, "holes_truth.json"), "w"), indent=1)
    for ref, h in out.items():
        print(ref, h["par"], "  ".join(f"{s[:5]} {h['card'][s]}/{h['measured'][s]:.0f}{'*' if 'estimated' in h['tee_how'][s] else ''}"
                                      for s in PURE if s in h["measured"]))


if __name__ == "__main__":
    main()
