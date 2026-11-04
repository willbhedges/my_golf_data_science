"""Tree canopy edge bias: the auto tree layer against the hand tree polygons in the landing corridors.

    python3 course_data/platform/tree_edge_bias.py --auto-dir A1 --auto-dir2 A2 [--out tree_edge_bias.json]
        (A1: v1 auto packages, A2: v2; as error_budget.py --auto-dir; omitted = the committed packages)

For every scored par-4/5 tee shot of the error budget's truth courses (error_budget --set v1 + v2, National KC and
Colbert Hills left out: no card / no hand trees) the hole's lie stacks are built exactly as error_budget.py builds
them (auto renumbered to the truth routing; truth = auto + the hand footprint + the hand zones). Inside the hand
footprint and the landing corridor (CORR_YD along the truth tee -> aim line, +/- LAT_YD), on the course's 1 m
vision_any grid:

  edge offset   for every truth crown-edge cell (not on the footprint / corridor cut) the signed distance to the
                auto tree edge, yds: + = the auto canopy stops short (inside the real crown), - = it reaches past it.
                Cells further than MATCH_YD from any auto canopy belong to missed crowns, not to an edge.
  crowns        connected truth tree pieces in the corridor; missed when the auto layer covers < MISS_COVER of it.
  missing cells truth tree cells the auto layer lacks, split by what the data says there: lidar HAG (3x3 median,
                as layers.tree_mask) over the canopy threshold (lost to the buffer / clump / building rule), 1 m to
                the threshold (low canopy edge), < 1 m with the Meta CHM over the threshold (Meta sees a crown the
                lidar does not: a lidar gap or a crown grown since the flight), < 1 m and NAIP tree-like (NDVI >
                NDVI_TREE in the newest NAIP: young or planted trees, or a hand line drawn wide), or nothing.
  sources       the auto zones' src (vision2 lidar HAG rule, the older vision lidar layer, OSM wood) of the auto cell
                nearest each truth edge cell; lidar year (canopy_recency.lidar_year) vs the NAIP years.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys

import warnings

import numpy as np
from scipy import ndimage

warnings.filterwarnings("ignore", category=RuntimeWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
YD = 0.9144
CORR_YD = (120.0, 345.0)
LAT_YD = 50.0
MATCH_YD = 15.0
MISS_COVER = 0.2
NDVI_TREE = 0.3
SKIP = ("national_kc", "colbert_hills")
TREE_SPEC = None        # --rule '{"k": -1}': also split the missing cells by the step of that tree rule that lost them


def src_class(src):
    s = str(src or "")
    if s.startswith("vision2:lidar"):
        return "lidar HAG rule (vision_any/2)"
    if s.startswith("vision:lidar"):
        return "older vision lidar layer"
    if s.startswith("osm"):
        return "OSM wood / tree row"
    return "other"


def _stack(vslug):
    vd = os.path.join(CD, "vision_any")
    if vd not in sys.path:
        sys.path.insert(0, vd)
    import layers as L
    import run_any as RA
    with contextlib.redirect_stdout(io.StringIO()):
        S = L.Stack.load(vslug, RA.course_dir_for(vslug))
    S.ll_to_rc([[0, 0]])
    return S


def _raster(S, geoms, win):
    """bool grid of shapely lon/lat geometries on the window (r0, c0, h, w) of the stack grid"""
    from rasterio import features
    from affine import Affine
    from shapely.ops import transform
    r0, c0, h, w = win
    tr = S.transform * Affine.translation(c0, r0)
    gs = [transform(lambda x, y: S._fwd.transform(x, y), g) for g in geoms if g is not None and not g.is_empty]
    if not gs:
        return np.zeros((h, w), bool)
    return features.rasterize([(g, 1) for g in gs], out_shape=(h, w), transform=tr, fill=0, dtype="uint8").astype(bool)


def hole_cells(S, tee_ll, aim_ll, pad_m=8.0):
    """(window, corridor mask) for the landing corridor of one tee shot on the stack grid"""
    from shapely.geometry import Polygon
    rc = S.ll_to_rc([tee_ll, aim_ll])
    x, y = S._fwd.transform([tee_ll[0], aim_ll[0]], [tee_ll[1], aim_ll[1]])
    t, a = np.array([x[0], y[0]]), np.array([x[1], y[1]])
    f = (a - t) / np.linalg.norm(a - t)
    r = np.array([f[1], -f[0]])
    d0, d1, lat = CORR_YD[0] * YD, CORR_YD[1] * YD, LAT_YD * YD
    corners = [t + f * d + r * l for d, l in ((d0, -lat), (d1, -lat), (d1, lat), (d0, lat))]
    xs, ys = [c[0] for c in corners], [c[1] for c in corners]
    inv = ~S.transform
    cs, rs = zip(*[inv * (xx, yy) for xx, yy in zip(xs, ys)])
    r0, r1 = int(max(0, min(rs) - pad_m)), int(min(S.H, max(rs) + pad_m))
    c0, c1 = int(max(0, min(cs) - pad_m)), int(min(S.W, max(cs) + pad_m))
    if r1 <= r0 or c1 <= c0:
        return None, None
    win = (r0, c0, r1 - r0, c1 - c0)
    from rasterio import features
    from affine import Affine
    tr = S.transform * Affine.translation(c0, r0)
    m = features.rasterize([(Polygon(corners), 1)], out_shape=(win[2], win[3]), transform=tr, fill=0,
                           dtype="uint8").astype(bool)
    del rc
    return win, m


def measure_hole(S, auto_by_src, truth_tree, footprint, tee_ll, aim_ll, ctx, auto_eff=None):
    from shapely.ops import unary_union
    win, corr = hole_cells(S, tee_ll, aim_ll)
    if win is None:
        return None
    r0, c0, h, w = win
    F = _raster(S, [footprint], win)
    D = F & corr
    if D.sum() < 100:
        return None
    T = _raster(S, [truth_tree], win) if truth_tree is not None else np.zeros((h, w), bool)
    lab = np.zeros((h, w), np.int16)                 # auto source label, later wins
    names = sorted(auto_by_src)
    for i, s in enumerate(names, 1):
        g = unary_union(auto_by_src[s]) if auto_by_src[s] else None
        if g is not None:
            lab[_raster(S, [g], win)] = i
    A = lab > 0
    # signed edge offset at truth crown edges inside D, away from the footprint / corridor cut
    Tin = T & D
    edge = Tin & ~ndimage.binary_erosion(T, np.ones((3, 3), bool), border_value=0)
    edge &= ndimage.binary_erosion(D, np.ones((5, 5), bool), border_value=0)
    d_out, idx = ndimage.distance_transform_edt(~A, return_indices=True)
    d_in = ndimage.distance_transform_edt(A)
    off_m = np.where(A, -(d_in - 0.5), d_out - 0.5)        # cell centre to edge
    e_off = off_m[edge] / YD
    near_src = lab[idx[0], idx[1]][edge]
    # crowns
    cl, nc = ndimage.label(Tin, np.ones((3, 3), bool))
    crowns = []
    for i in range(1, nc + 1):
        c = cl == i
        a = c.sum()
        if a * 1.0 / YD ** 2 < 20:
            continue
        crowns.append(dict(area_yd2=round(a / YD ** 2), cover=round(float((c & A).sum() / a), 3)))
    # missing / extra cells and what the data says there
    miss = Tin & ~A
    extra = A & ~T & D
    sl = (slice(r0, r0 + h), slice(c0, c0 + w))
    hm, chm = ctx["hm"][sl], ctx["chm"][sl]
    nd = ctx["ndvi"][sl] if ctx["ndvi"] is not None else np.zeros((h, w))
    thr = ctx["thr"]
    cats = {}
    for name, m in (("lidar over threshold", hm > thr), ("lidar 1 m to threshold", (hm > 1.0) & (hm <= thr)),
                    ("Meta CHM only", (hm <= 1.0) & (chm > thr)),
                    ("NAIP tree-like only", (hm <= 1.0) & ~(chm > thr) & (nd > NDVI_TREE))):
        cats[name] = int((miss & m).sum())
    cats["nothing"] = int(miss.sum()) - sum(cats.values())
    lost = {}
    if ctx.get("canopy") is not None:
        cm, rule = ctx["canopy"][sl], ctx["rule"][sl]
        lost = {"not in the canopy mask (HAG over threshold: building / NDVI / opening mask)": int((miss & (hm > thr) & ~cm).sum()),
                "canopy mask, cut by the clump size / buffer rule": int((miss & cm & ~rule).sum()),
                "in the tree rule, not in the visible auto layer": int((miss & rule).sum())}
    covered = {}
    if auto_eff:                      # what the auto map shows on the missing cells (the lie drawn over the canopy)
        rest = miss.copy()
        for lie, g in auto_eff.items():
            if lie == "recovery":
                continue
            c = _raster(S, [g], win) & rest
            if c.any():
                covered[lie] = int(c.sum())
                rest &= ~c
        covered["no zone (rough)"] = int(rest.sum())
    if ctx.get("canopy") is not None:
        cm = ctx["canopy"][sl]
        hi = miss & (hm > thr) & ~cm
        lost.update({"  of which building (lclass 6 / OSM, 2 m dilated)": int((hi & ctx["bld"][sl]).sum()),
                     "  of which NDVI < 0.05 (tall, not green)": int((hi & ~ctx["bld"][sl] & ctx["lowndvi"][sl]).sum())})
        rule = ctx["rule"][sl]
        lost["  rule cells under: " + ", ".join(f"{k} {round(v / YD ** 2)}" for k, v in sorted(
            {lie: int((_raster(S, [g], win) & miss & rule).sum()) for lie, g in (auto_eff or {}).items()
             if lie != "recovery"}.items(), key=lambda kv: -kv[1])[:4])] = int((miss & rule).sum())
    dist = d_out[miss]
    return dict(
        corridor_yd2=round(D.sum() / YD ** 2), truth_yd2=round(Tin.sum() / YD ** 2), auto_yd2=round((A & D).sum() / YD ** 2),
        missing_yd2=round(miss.sum() / YD ** 2), extra_yd2=round(extra.sum() / YD ** 2),
        edge_off_yd=[round(float(v), 2) for v in e_off], edge_src=[names[i - 1] if i > 0 else None for i in near_src],
        crowns=crowns, missing_by_data={k: round(v / YD ** 2) for k, v in cats.items()},
        missing_lost_at={k: round(v / YD ** 2) for k, v in lost.items() if not k.startswith("  rule cells under")},
        missing_covered_by={k: round(v / YD ** 2) for k, v in covered.items()},
        missing_band={"0-3 yd from auto": round(float((dist <= 3 * YD).sum()) / YD ** 2),
                      "3-8 yd": round(float(((dist > 3 * YD) & (dist <= 8 * YD)).sum()) / YD ** 2),
                      "> 8 yd": round(float((dist > 8 * YD).sum()) / YD ** 2)},
        extra_lidar_low=round(float((extra & (hm <= thr)).sum()) / YD ** 2))


def course_ctx(S):
    vd = os.path.join(CD, "vision_any")
    sys.path.insert(0, vd)
    import layers as L
    import canopy_recency as CR
    tb = json.load(open(os.path.join(vd, "model_v2", "model.json")))["settings"]["trees"]
    h = S.layers.get("hag")
    hh = np.nan_to_num(h.copy() if h is not None else np.zeros((S.H, S.W), np.float32), nan=0.0)
    chm = np.nan_to_num(S.layers.get("chm_meta", np.zeros((S.H, S.W), np.float32)), nan=0.0)
    hm = ndimage.median_filter(hh, 3)
    years = sorted(y for y, _ in S.naip)
    nd = L.ndvi(dict(S.naip)[years[-1]]) if years else None
    canopy = rule = None
    if TREE_SPEC is not None and h is not None:
        import v2_model as VM
        M, _ = L.osm_masks(S, json.load(open(os.path.join(S.course_dir, "osm.geojson"))))
        canopy = L.tree_mask(S, M, hag_min=TREE_SPEC.get("hag", tb["hag"]), min_area_m2=10.0)[0]
        rule = VM.tree_rule(canopy, TREE_SPEC.get("k", tb["k_m"]), TREE_SPEC.get("min_area", tb["min_area_m2"]), S.res)
        bld = np.zeros((S.H, S.W), bool)
        if "lclass" in S.layers:
            bld |= S.layers["lclass"] == 6
        bld |= M.get("building", np.zeros_like(bld))
        bld = ndimage.binary_dilation(bld, L.disk(2))
        lowndvi = (ndimage.uniform_filter(L.ndvi(S.naip[0][1]), 5) < 0.05) if S.naip else np.zeros_like(bld)
    return dict(hm=hm, chm=ndimage.median_filter(chm, 3), ndvi=nd, thr=tb["hag"], lidar_year=CR.lidar_year(S),
                canopy=canopy, rule=rule, bld=None if canopy is None else bld, lowndvi=None if canopy is None else lowndvi,
                naip_years=years, meta=("chm_meta" in S.layers))


def course(cfg, auto_dir):
    sys.path.insert(0, HERE)
    import error_budget as E
    S_ = cfg["tees"]
    pkg_path = os.path.join(ROOT, cfg.get("package") or f"course_data/packages/{cfg['slug']}/package.json")
    if auto_dir and os.path.exists(os.path.join(auto_dir, cfg["slug"], "package.json")):
        pkg_path = os.path.join(auto_dir, cfg["slug"], "package.json")
    base = E.prepare(E.rj(pkg_path), S_)
    truth = E.truth_holes(cfg)
    base_r, _ = E.renumber(base, truth, S_)
    P = E.PK()
    auto_st, truth_st, zsrc = {}, {}, {}
    for ref, td in truth.items():
        h = base_r["holes"].get(ref)
        if h is None or not td.get("hand"):
            continue
        ent = E.tee_entry(h, S_, base_r.get("tee_set"))
        ref_ll = P._ll(ent.get("tee_ll")) or P._ll(h.get("tee_ll")) or td.get("tee_ll")
        if ref_ll is None:
            continue
        auto_st[ref] = E.auto_stack(base_r, h, ref_ll)
        truth_st[ref] = E.truth_stack(auto_st[ref], td)
        zsrc[ref] = [str(z.get("src", "")) for z in (h.get("zones_ll") or []) if isinstance(z, dict)
                     and E.model_lie(z.get("lie")) == "recovery"]
    if not truth_st:
        return None
    stacks = {ref: E.mixed_stack(auto_st[ref], truth_st[ref], set(E.LAYERS), {}) for ref in truth_st}
    pk = E.apply_layers(base_r, truth, S_, set(E.LAYERS), stacks)
    Ct, Ht = E.load_models(pk, S_, f"teb_{cfg['slug']}")
    vslug = "mozingo" if cfg["slug"] == "mozingo_lake" else cfg["slug"]
    S = _stack(vslug)
    ctx = course_ctx(S)
    rows = {}
    from shapely.geometry import Polygon
    for k in Ht:
        ref = str(k)
        if ref not in truth_st:
            continue
        fr = Ct.frames[k]
        ea, et = E.effective(auto_st[ref]), E.effective(truth_st[ref])
        # auto trees by source: the raw recovery zones of the hole, clipped to the visible recovery region
        vis = ea.get("recovery")
        by = {}
        h = base_r["holes"][ref]
        for z in h.get("zones_ll") or []:
            if not isinstance(z, dict) or E.model_lie(z.get("lie")) != "recovery":
                continue
            poly = z.get("poly") or z.get("poly_ll")
            if not poly or len(poly) < 3 or vis is None:
                continue
            g = E._geom(E._ring(poly))
            if g is None or g.is_empty:
                continue
            by.setdefault(src_class(z.get("src")), []).append(g.intersection(vis))
        foot = Polygon(E._ring(truth[ref]["hand"]["footprint"]))
        if not foot.is_valid:
            foot = foot.buffer(0)
        m = measure_hole(S, by, et.get("recovery"), foot, fr["tee_ll"], fr["aim_ll"], ctx, ea)
        if m:
            rows[ref] = m
    return dict(slug=cfg["slug"], lidar_year=ctx["lidar_year"], naip_years=ctx["naip_years"], meta_chm=ctx["meta"],
                holes=rows)


def summarise(courses):
    def stats(v):
        v = np.asarray(v, float)
        if not len(v):
            return None
        return dict(n=int(len(v)), median=round(float(np.median(v)), 2), mean=round(float(v.mean()), 2),
                    p25=round(float(np.percentile(v, 25)), 2), p75=round(float(np.percentile(v, 75)), 2),
                    short_share=round(float((v > 0).mean()), 3))
    allv, by_src, by_course, by_age = [], {}, {}, {}
    crowns, cats, bands, lost, cov = [], {}, {}, {}, {}
    tot = dict(truth=0, missing=0, extra=0)
    for c in courses:
        age = None if c["lidar_year"] is None or not c["naip_years"] else c["naip_years"][-1] - c["lidar_year"]
        akey = "unknown" if age is None else ("0-2 yrs" if age <= 2 else "3-5 yrs" if age <= 5 else "6+ yrs")
        cv = []
        for ref, m in c["holes"].items():
            v = [o for o in m["edge_off_yd"] if abs(o) <= MATCH_YD]
            s = [s for o, s in zip(m["edge_off_yd"], m["edge_src"]) if abs(o) <= MATCH_YD]
            cv += v
            for o, ss in zip(v, s):
                by_src.setdefault(ss or "none", []).append(o)
            by_age.setdefault(akey, []).extend(v)
            crowns += [dict(slug=c["slug"], hole=ref, **cr) for cr in m["crowns"]]
            for k, x in m["missing_by_data"].items():
                cats[k] = cats.get(k, 0) + x
            for k, x in (m.get("missing_lost_at") or {}).items():
                lost[k] = lost.get(k, 0) + x
            for k, x in (m.get("missing_covered_by") or {}).items():
                cov[k] = cov.get(k, 0) + x
            for k, x in m["missing_band"].items():
                bands[k] = bands.get(k, 0) + x
            tot["truth"] += m["truth_yd2"]
            tot["missing"] += m["missing_yd2"]
            tot["extra"] += m["extra_yd2"]
        allv += cv
        by_course[c["slug"]] = dict(edge=stats(cv), lidar_year=c["lidar_year"], naip=c["naip_years"], age=age,
                                    missing_yd2=sum(m["missing_yd2"] for m in c["holes"].values()),
                                    extra_yd2=sum(m["extra_yd2"] for m in c["holes"].values()),
                                    truth_yd2=sum(m["truth_yd2"] for m in c["holes"].values()))
    big = [c for c in crowns if c["area_yd2"] >= 100]
    missed = [c for c in big if c["cover"] < MISS_COVER]
    return dict(edge_all=stats(allv), edge_by_src={k: stats(v) for k, v in by_src.items()},
                edge_by_lidar_age={k: stats(v) for k, v in by_age.items()}, by_course=by_course,
                crowns=dict(n=len(big), missed=len(missed), missed_share=round(len(missed) / max(1, len(big)), 3),
                            missed_area_yd2=sum(c["area_yd2"] for c in missed),
                            missed_median_yd2=float(np.median([c["area_yd2"] for c in missed])) if missed else None,
                            missed_list=sorted(missed, key=lambda c: -c["area_yd2"])[:40]),
                missing_by_data=cats, missing_lost_at=lost, missing_covered_by=cov, missing_band=bands, totals=tot)


def compact(c):
    """a course record without the per-cell edge lists (for the committed json)"""
    holes = {}
    for ref, m in c["holes"].items():
        v = [o for o in m["edge_off_yd"] if abs(o) <= MATCH_YD]
        h = {k: x for k, x in m.items() if k not in ("edge_off_yd", "edge_src", "crowns")}
        h["edge_median_yd"] = round(float(np.median(v)), 2) if v else None
        h["crowns_missed"] = sum(1 for x in m["crowns"] if x["area_yd2"] >= 100 and x["cover"] < MISS_COVER)
        holes[ref] = h
    return dict(c, holes=holes)


def main():
    sys.path.insert(0, HERE)
    import error_budget as E
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto-dir")
    ap.add_argument("--auto-dir2")
    ap.add_argument("--courses")
    ap.add_argument("--out", default=os.path.join(HERE, "tree_edge_bias.json"))
    ap.add_argument("--rule", help='tree rule of the auto layer, e.g. {"k": -1}: split the missing cells by step')
    a = ap.parse_args()
    global TREE_SPEC
    TREE_SPEC = json.loads(a.rule) if a.rule else None
    want = set(a.courses.split(",")) if a.courses else None
    out = []
    for sv, d in (("v1", a.auto_dir), ("v2", a.auto_dir2 or a.auto_dir)):
        for cfg in E.SETS[sv]():
            if cfg["slug"] in SKIP or (want and cfg["slug"] not in want):
                continue
            r = course(cfg, d)
            if r:
                out.append(r)
                s = summarise([r])
                print(cfg["slug"], json.dumps(s["edge_all"]), s["totals"], flush=True)
    res = dict(summary=summarise(out), courses=[compact(c) for c in out])
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res["summary"].items() if k not in ("by_course",)}, indent=1)[:6000])


if __name__ == "__main__":
    main()
