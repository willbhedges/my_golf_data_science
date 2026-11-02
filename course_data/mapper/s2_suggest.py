"""Sentinel-2 native suggestions for the mapper: the S2 native probability in each corridor frame, and the
"S2 suggested native" candidate shapes the agent accepts / rejects per side (BRIEF.md "S2 suggestions").

The probability comes from course_data/vision_any/s2/native_model.py (LOCO-safe: a course in the S2 training set
gets the P of the fold model trained without it; any other course the full model). S2 is 10 m: a candidate is a
cluster of 10 m cells with P >= THR, minus the package's fairway / first cut / green / water / sand / trees, split
at the tee line into a left and a right part. It is a hint where to look, never a layer by itself.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as M  # noqa: E402

S2_DIR = os.path.join(M.CD, "vision_any", "s2")
THR = 0.5
MIN_YD2 = 150.0              # smallest candidate (ng_variant / the error budget used the same)
SIMPLIFY_YD = 2.5            # 10 m cells are 11 yds: soften the stair steps a little, the agent traces the real edge
NOT_NATIVE = ("fairway", "first_cut", "green", "water", "sand", "recovery")
DECISIONS = ("accept", "reject", "replace")


def _nm():
    if S2_DIR not in sys.path:
        sys.path.insert(0, S2_DIR)
    import native_model as NM
    return NM


_CACHE = {}


def load(slug, allow_full=True):
    """-> native_model.p_grid(slug) (+ a WGS84 -> grid transformer) or None (no S2 stack)."""
    if slug in _CACHE:
        return _CACHE[slug]
    r = _nm().p_grid(slug, allow_full=allow_full)
    if r is not None:
        from pyproj import Transformer
        r["tr"] = Transformer.from_crs("EPSG:4326", r["crs"], always_xy=True)
    _CACHE[slug] = r
    return r


def sample_ll(pg, ll):
    """P at WGS84 points (nearest 10 m cell; nan outside the grid / no data)."""
    ll = np.asarray(ll, float).reshape(-1, 2)
    X, Y = pg["tr"].transform(ll[:, 0], ll[:, 1])
    a, b, c, d, e, f = pg["transform"]
    col = np.floor((np.asarray(X) - c) / a).astype(int)
    row = np.floor((np.asarray(Y) - f) / e).astype(int)
    H, W = pg["p"].shape
    ok = (row >= 0) & (row < H) & (col >= 0) & (col < W)
    out = np.full(len(ll), np.nan, np.float32)
    out[ok] = pg["p"][row[ok], col[ok]]
    return out


def p_frame(pg, fj, a0, a1, lat, ppy):
    """P on the corridor panel's pixel grid (rows = along a1 -> a0, cols = x -lat -> +lat), pixel centres."""
    nx, ny = int(round(2 * lat * ppy)), int(round((a1 - a0) * ppy))
    xs = -lat + (np.arange(nx) + 0.5) / ppy
    al = a1 - (np.arange(ny) + 0.5) / ppy
    X, A = np.meshgrid(xs, al)
    return sample_ll(pg, M.xy_to_ll(fj, np.c_[X.ravel(), A.ravel()])).reshape(ny, nx)


def _not_native(fj, h):
    from shapely.ops import unary_union
    zs = [M._poly(z["xy"]) for z in M.auto_zones_xy(fj, h, NOT_NATIVE)]
    return unary_union(zs).buffer(0) if zs else None


def candidates(pg, fj, h, ref, thr=THR):
    """-> [{id, side, area_yd2, p_mean, along, x, gap_yd, shape: {"poly": ...}}] for one corridor hole."""
    import rasterio.features as RF
    from affine import Affine
    from shapely.geometry import box, shape as shp
    from shapely.ops import unary_union
    a0, a1, lat = M.WIN["a0"], M.WIN["a1"], M.WIN["lat"]
    P = p_frame(pg, fj, a0, a1, lat, 1.0)
    m = (np.nan_to_num(P, nan=0.0) >= thr).astype(np.uint8)
    if not m.any():
        return []
    tf = Affine(1.0, 0, -lat, 0, -1.0, a1)            # pixel (col, row) -> (x, along)
    g = unary_union([shp(s) for s, v in RF.shapes(m, mask=m.astype(bool), transform=tf) if v == 1]).buffer(0)
    blk = _not_native(fj, h)
    if blk is not None:
        g = g.difference(blk)
    fw = [M._poly(z["xy"]) for z in M.auto_zones_xy(fj, h, ("fairway", "first_cut", "green"))]
    mown = unary_union(fw).buffer(0) if fw else None
    out = []
    for side, bx in (("L", box(-lat, a0, 0, a1)), ("R", box(0, a0, lat, a1))):
        parts = sorted(M.polys_of(g.intersection(bx).simplify(SIMPLIFY_YD).buffer(0), MIN_YD2),
                       key=lambda q: q.bounds[1])
        k = 0
        for p in parts:
            xy = [[int(round(x)), int(round(a))] for x, a in list(p.exterior.coords)[:-1]]
            if len(xy) < 3:
                continue
            k += 1
            inside = RF.rasterize([(p, 1)], out_shape=P.shape, transform=tf).astype(bool)
            pv = P[inside & np.isfinite(P)]
            b = p.bounds
            out.append(dict(id=f"S2-{ref}-{side}{k}", side=side, area_yd2=int(round(p.area)),
                            p=round(float(pv.mean()), 2) if pv.size else None,
                            along=[int(round(b[1])), int(round(b[3]))], x=[int(round(b[0])), int(round(b[2]))],
                            gap_yd=None if mown is None else round(float(p.distance(mown)), 1), shape=dict(poly=xy)))
    return out


def template_entry(cands):
    """The edits.template.json block: per side, every candidate with an empty decision for the agent."""
    out = {}
    for side in ("L", "R"):
        out[side] = [dict(id=c["id"], area_yd2=c["area_yd2"], p=c["p"], along=c["along"], gap_yd=c["gap_yd"],
                          decision="", confidence="", evidence="", shape=c["shape"])
                     for c in cands if c["side"] == side]
    return out


def decisions_to_edits(ref, block, EditError=ValueError):
    """edits.json `s2_suggested` -> (extra add-native edits for accepted candidates, problems, summary rows).
    accept: the candidate's shape becomes `add native` with the agent's confidence + evidence (keep-out applies);
    reject: nothing (evidence = why); replace: nothing here (the agent drew its own native edit in `edits`)."""
    edits, problems, rows = [], [], []
    for side in ("L", "R"):
        for c in (block or {}).get(side) or []:
            d = (c.get("decision") or "").strip().lower()
            cid = c.get("id") or f"S2-{ref}-{side}?"
            rows.append(dict(id=cid, side=side, area_yd2=c.get("area_yd2"), decision=d or "undecided",
                             confidence=c.get("confidence") or "", evidence=c.get("evidence") or ""))
            if not d:
                problems.append(f"hole {ref} {cid}: S2 suggestion undecided (accept / reject / replace it per side)")
                continue
            if d not in DECISIONS:
                raise EditError(f"hole {ref} {cid}: decision {d!r} not in {DECISIONS}")
            if not c.get("evidence"):
                raise EditError(f"hole {ref} {cid}: {d} needs evidence (what the photo shows in both years)")
            if d == "accept":
                if c.get("confidence") not in M.CONF:
                    raise EditError(f"hole {ref} {cid}: accept needs confidence high / medium / low")
                edits.append(dict(op="add", lie="native", shape=c.get("shape"), confidence=c["confidence"],
                                  evidence=f"{cid} accepted: {c['evidence']}", s2=cid))
    return edits, problems, rows
