"""Fairway layer quality per landing corridor, against the hand truth (error-budget set + truth_sets_v2).

    python3 course_data/platform/fairway_quality.py [--auto-dir DIR] [--out fairway_quality.json] [--courses a,b]

Corridor = the truth tee shot's landing zone, 180-330 yds along the truth tee line (truth tee -> the truth
package's aim point), +/-50 yds (inside every hand footprint). Fairway = the visible fairway + first_cut lies
(error_budget.ZONE_LAYERS["fairway"]) of the auto stack (the build as numbered to the truth routing) and of the
truth stack (auto stack + hand corridor map; error_budget.truth_stack). Per corridor:

  truth / auto / inter / missing / extra   sq yds          iou
  width_err   (auto - truth) / 150 yds: mean width difference, yds (- = auto narrower)
  shift       lateral offset of the auto fairway centroid from the truth's, yds (+ = right)
  src         'osm' | 'segment' | 'band' | 'vision' | 'none' (src of the auto fairway zones in the corridor)
  best_buf    the outward buffer of the auto fairway (yds, -6..+20) with the best IoU against the truth
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path.insert(0, HERE)
import error_budget as E  # noqa: E402

A0, A1, HALF = 180.0, 330.0, 50.0
V2 = [dict(slug="tomahawk_hills", tees="Blue", kind="v2"), dict(slug="wakonda", tees="Blue", kind="v2")]
BUFS = list(range(-6, 21))


def truth_holes_v2(cfg):
    S = cfg["tees"]
    d = os.path.join(CD, "truth_sets_v2", cfg["slug"])
    T = E.rj(os.path.join(d, "holes_truth.json"))
    HZ = (E.rj(os.path.join(d, "hand_zones_ll.json")) or {}).get("holes", {})
    out = {}
    for ref, th in T["holes"].items():
        m = HZ.get(ref)
        out[ref] = dict(par=int(th["par"]), yards=dict(th.get("card") or {}), line=th.get("hole_line_ll"),
                        green_ll=th["green_ll"], green_poly=th.get("green_poly_ll"),
                        tee_ll=(th.get("tees") or {}).get(S),
                        hand=dict(footprint=m["footprint_ll"], zones=m["zones"]) if m else None,
                        extra=th.get("extra_zones") or [])
    return out


def all_courses():
    return [c for c in E.COURSES] + V2


def pkg_path(cfg, auto_dir=None):
    if auto_dir and os.path.exists(os.path.join(auto_dir, cfg["slug"], "package.json")):
        return os.path.join(auto_dir, cfg["slug"], "package.json")
    return os.path.join(ROOT, cfg.get("package") or f"course_data/packages/{cfg['slug']}/package.json")


def course_stacks(cfg, auto_pkg):
    """(truth, {ref: auto stack R}, {ref: truth stack}, {ref: (truth tee_ll, truth aim_ll)}, base_r) for the
    hand-mapped tee shots (holes with a hand corridor or whole-hole truth layers)."""
    S = cfg["tees"]
    base = E.prepare(auto_pkg, S)
    truth = truth_holes_v2(cfg) if cfg["kind"] == "v2" else E.truth_holes(cfg)
    base_r, _ = E.renumber(base, truth, S)
    P = E.PK()
    ast, tst = {}, {}
    for ref, td in truth.items():
        h = base_r["holes"].get(ref)
        if h is None:
            continue
        ent = E.tee_entry(h, S, base_r.get("tee_set"))
        ref_ll = P._ll(ent.get("tee_ll")) or P._ll(h.get("tee_ll")) or td.get("tee_ll")
        if ref_ll is None:
            continue
        ast[ref] = E.auto_stack(base_r, h, ref_ll)
        tst[ref] = E.truth_stack(ast[ref], td)
    pk = E.apply_layers(base_r, truth, S, set(E.LAYERS), tst)
    C, holes = E.load_models(pk, S, f"fq_{cfg['slug']}")
    frames = {str(k): (C.frames[k]["tee_ll"], C.frames[k]["aim_ll"]) for k in holes
              if str(k) in tst and (truth[str(k)].get("hand") or truth[str(k)].get("known_full"))}
    return truth, ast, tst, frames, base_r


def corridor_frame(tee_ll, aim_ll):
    """(to-yards fn, T0, fwd, right, corridor polygon) in a local east-north yard frame."""
    from shapely.geometry import Polygon
    f = E._to_yd_fn(tee_ll[1], tee_ll[0])
    T0 = np.array(f(tee_ll[0], tee_ll[1]), float)
    A = np.array(f(aim_ll[0], aim_ll[1]), float) - T0
    fwd = A / np.linalg.norm(A)
    right = np.array([fwd[1], -fwd[0]])
    corr = Polygon([T0 + fwd * a + right * l for a, l in ((A0, -HALF), (A1, -HALF), (A1, HALF), (A0, HALF))])
    return f, T0, fwd, right, corr


def to_yd(f, g):
    from shapely import transform as _tr
    return _tr(g, lambda xy: np.c_[f(xy[:, 0], xy[:, 1])])


def lie_region(stack, lies, f):
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    eff = E.effective(stack)
    gs = [to_yd(f, eff[l]) for l in lies if l in eff]
    return unary_union(gs) if gs else Polygon()


def src_of(h, corr_ll):
    """Sources of the hole's auto fairway zones that reach the corridor."""
    out = set()
    for z in h.get("zones_ll") or []:
        if not isinstance(z, dict) or z.get("lie") not in ("fairway", "first_cut"):
            continue
        g = E._geom([tuple(p) for p in (z.get("poly") or z.get("poly_ll") or [])])
        if g is not None and not g.is_empty and g.intersects(corr_ll):
            s = str(z.get("src", "osm"))
            out.add("segment" if "segment" in s else "band" if "band" in s else "vision" if "vision" in s else "osm")
    return out


def measure_corridor(a_fw, t_fw, corr, right, other_auto=None):
    from shapely.geometry import Polygon
    a = a_fw.intersection(corr) if not a_fw.is_empty else Polygon()
    t = t_fw.intersection(corr) if not t_fw.is_empty else Polygon()
    inter = a.intersection(t).area
    uni = a.union(t).area
    r = dict(truth=round(t.area), auto=round(a.area), inter=round(inter), missing=round(t.area - inter),
             extra=round(a.area - inter), iou=round(inter / uni, 3) if uni > 0 else None,
             width_err=round((a.area - t.area) / (A1 - A0), 1))
    if a.area > 1 and t.area > 1:
        r["shift"] = round(float((np.array(a.centroid.coords[0]) - np.array(t.centroid.coords[0])) @ right), 1)
    if not a_fw.is_empty and t.area > 1:
        best = (-1, 0)
        r["iou_by_buf"] = {}
        for b in BUFS:
            g = a_fw.buffer(b, join_style=2) if b else a_fw
            if other_auto is not None and b > 0:
                g = a_fw.union(g.difference(other_auto))
            g = g.intersection(corr)
            u = g.union(t).area
            iou = g.intersection(t).area / u if u > 0 else 0
            r["iou_by_buf"][str(b)] = round(iou, 4)
            if iou > best[0] + 1e-9:
                best = (iou, b)
        r["best_buf"], r["best_iou"] = best[1], round(best[0], 3)
    return r


def measure_course(cfg, auto_dir=None):
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    auto_pkg = E.rj(pkg_path(cfg, auto_dir))
    if auto_pkg is None:
        return []
    truth, ast, tst, frames, base_r = course_stacks(cfg, auto_pkg)
    fw = E.ZONE_LAYERS["fairway"]
    haz = ("recovery", "water", "sand", "native", "ob", "ob_boundary")
    rows = []
    for ref, (tee_ll, aim_ll) in sorted(frames.items(), key=lambda kv: int("".join(c for c in kv[0] if c.isdigit()) or 0)):
        f, T0, fwd, right, corr = corridor_frame(tee_ll, aim_ll)
        a_fw = lie_region(ast[ref], fw, f)
        t_fw = lie_region(tst[ref], fw, f)
        t_fo = lie_region(tst[ref], ("fairway",), f)
        oth = lie_region(ast[ref], haz, f)
        r = dict(course=cfg["slug"], hole=ref, **measure_corridor(a_fw, t_fw, corr, right, oth))
        r["truth_fairway_only"] = round(t_fo.intersection(corr).area)
        # corridor in lon/lat for the source lookup
        kx = np.cos(np.radians(tee_ll[1])) * 111320.0 / 0.9144
        ky = 110574.0 / 0.9144
        corr_ll = Polygon([(x / kx + tee_ll[0], y / ky + tee_ll[1]) for x, y in corr.exterior.coords])
        s = src_of(base_r["holes"][ref], corr_ll)
        r["src"] = "+".join(sorted(s)) if s else "none"
        rows.append(r)
    return rows


def summary(rows, key="src"):
    out = {}
    groups = {}
    for r in rows:
        groups.setdefault(r[key], []).append(r)
    groups["all"] = rows
    for g, rs in groups.items():
        rs = [r for r in rs if r["truth"] > 0 or r["auto"] > 0]
        if not rs:
            continue
        T = sum(r["truth"] for r in rs)
        I = sum(r["inter"] for r in rs)
        A = sum(r["auto"] for r in rs)
        out[g] = dict(n=len(rs), pooled_iou=round(I / (T + A - I), 3) if T + A - I else None,
                      median_iou=float(np.median([r["iou"] for r in rs if r["iou"] is not None])),
                      median_width_err=float(np.median([r["width_err"] for r in rs])),
                      median_missing=float(np.median([r["missing"] for r in rs])),
                      median_extra=float(np.median([r["extra"] for r in rs])),
                      median_best_buf=float(np.median([r["best_buf"] for r in rs if "best_buf" in r])) if any("best_buf" in r for r in rs) else None,
                      wrong_side=sum(1 for r in rs if r.get("iou") is not None and r["iou"] < 0.25 and r["truth"] > 1500 and r["auto"] > 1500))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto-dir")
    ap.add_argument("--courses")
    ap.add_argument("--out", default=os.path.join(HERE, "fairway_quality.json"))
    a = ap.parse_args()
    want = set(a.courses.split(",")) if a.courses else None
    rows = []
    for cfg in all_courses():
        if want and cfg["slug"] not in want:
            continue
        rs = measure_course(cfg, a.auto_dir)
        rows += rs
        s = summary(rs)["all"] if rs else {}
        print(cfg["slug"], len(rs), json.dumps(s), flush=True)
    res = dict(corridor=f"{A0:.0f}-{A1:.0f} yds x +/-{HALF:.0f}", by_src=summary(rows), by_course={
        c: summary([r for r in rows if r["course"] == c])["all"] for c in sorted({r["course"] for r in rows})}, rows=rows)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res["by_src"], indent=1))


if __name__ == "__main__":
    main()
