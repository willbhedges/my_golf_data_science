"""Cardless scorecard: tee SETS, per-hole yardage per set and PAR from geometry alone (no web card, no paid API).

    from cardless import infer_card
    card = infer_card(holes, tees, pads=())      # -> scorecard/1-shaped dict (tee_sets "Back", "2nd", ..., par)

Inputs (holes already routed): holes = [{"ref": 1, "line": [(lat, lon), ...] tee -> green (dog-leg vertices kept),
"green": (lat, lon) green centre, "green_r_yd": equal-area radius or None}], tees = OSM golf=tee boxes
[{"id", "coords": [(lat, lon), ...]}], pads = lidar / texture pads (same shape) used only on holes where OSM has no box.

Method (CARDLESS.md has the evaluation):
1. Tee complex per hole. Every box goes to the hole whose first leg it sits beside (place_tee.assign_tees_to_holes).
   Each box is measured the USGA way along the hole line through the dog-leg points to the green centre
   (place_tee.LineOfPlay): d_front, d_back, d_centroid, length = d_back - d_front. Boxes whose centroid yardages are
   within MERGE_YD are one marker position (side-by-side split boxes). A box longer than LONG_YD offers two marker
   slots (back and front: d_back - f*len and d_front + f*len, f = SLOT_F); a shorter box one (its centroid).
2. Number of sets S: a learned table from the upper quantile of the per-hole slot count, clipped to [S_MIN, S_MAX]
   (MODEL["s_table"]); cards with 4-5 sets dominate, so sparse mapping falls back to the prior.
3. Assignment, jointly over holes (coordinate descent): set s has a course-wide ratio r_s to the back set
   (r_1 = 1, initialised from MODEL["ratios"][S]). Per hole an exact DP maps sets back -> front onto the slots
   (non-increasing: a later set never longer than an earlier one; sets may share a slot when the hole has fewer slots
   than sets) or OFF a box at r_s * back (forward tees on the fairway that OSM does not map) at cost OFF_COST.
   Cost of set s at yardage y on a hole whose back is B: |y - r_s B| (+ GAP_W per yd the gap to the previous set
   is below MIN_GAP for distinct slots). Then r_s <- median over holes of y_s / y_1, repeat. The back set takes
   the farthest slot unless that slot is an outlier (> TIPS_YD beyond the 2nd slot on most holes is still kept:
   cards do list tips).
4. Par: a softmax classifier on (back yards, 2nd-set yards, green radius, dog-leg) fitted on the dev split
   (MODEL["par"]), then a course-level DP maximising sum log p(par_h) + log prior(course par, # par 3s, # par 5s)
   (18 holes: par 70-72, typically 4 par 3s / 4 par 5s; 9 holes: 34-36).
5. Sets named "Back", "2nd", "3rd", ... with totals.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE] if HERE not in sys.path else []
import place_tee as pt  # noqa: E402

VERSION = "tees/cardless v1"
MODEL_PATH = os.path.join(HERE, "cardless_model.json")

PARAMS = dict(
    merge_yd=5.0,       # boxes whose centroid yardages differ by less are one marker position
    long_yd=30.0,       # a box at least this long (along the line) hosts two markers
    slot_f=0.1,         # long-box markers stand this fraction of the box length in from each end
    short_a=0.9,        # a short box's marker: this fraction of its length from the front (0.5 = centroid)
    line_start=True,
    mode="interval",    # "interval": a set stands anywhere inside a box (clamped to its target); "point": on slots
    same_gap=4.0,       # two sets inside one box stand at least this far apart
    ratio_upd=0.5,    # the routed line's start is a tee position too (when behind every box)
    off_cost=25.0,      # cost of placing a set off any box (unmapped forward tee) at r_s * back
    min_gap=8.0, gap_w=0.5,
    iters=4,
    s_quantile=0.75,
)

# defaults; eval_cardless.py --fit rewrites cardless_model.json from the dev split
DEFAULT_MODEL = {
    "s_table": {"0": 4, "1": 4, "2": 4, "3": 4, "4": 4, "5": 5, "6": 5, "7": 6},
    "ratios": {"1": [1.0], "2": [1.0, 0.91], "3": [1.0, 0.93, 0.84], "4": [1.0, 0.94, 0.87, 0.77],
               "5": [1.0, 0.95, 0.89, 0.82, 0.72], "6": [1.0, 0.96, 0.91, 0.85, 0.78, 0.69]},
    "par": None,
    "par_prior": None,
}


def load_model(path=MODEL_PATH):
    m = json.loads(json.dumps(DEFAULT_MODEL))
    try:
        with open(path) as fh:
            m.update(json.load(fh))
    except (OSError, ValueError):
        pass
    return m


# ----------------------------------------------------------------------------- 1. tee complexes
def _ring(fr, coords):
    ring = [fr.fwd(*p) for p in coords]
    if len(ring) > 1 and ring[0] == ring[-1]:
        ring = ring[:-1]
    return ring


def hole_geometry(hole):
    """Frame, LineOfPlay and shape features of one routed hole."""
    line = [tuple(p) for p in hole["line"]]
    fr, lop = pt._hole_frame(line, hole.get("green"))
    pts = lop.pts
    straight = math.hypot(pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1]) or 1.0
    # dog-leg: angle between the first leg and the direct tee -> green bearing
    d = (pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1])
    cosang = (d[0] * lop.u0[0] + d[1] * lop.u0[1]) / straight
    return fr, lop, dict(line_yd=lop.length, dogleg_deg=math.degrees(math.acos(max(-1.0, min(1.0, cosang)))),
                         bend=lop.length / straight)


def measure_boxes(hole, boxes, source="osm"):
    """[{d_front, d_back, d_centroid, len, offset, source, ids}] for the boxes of one hole, merged and sorted
    back -> front."""
    fr, lop, _ = hole_geometry(hole)
    out = []
    for b in boxes:
        ring = _ring(fr, b["coords"])
        if not ring:
            continue
        c = pt.polygon_centroid(ring) if len(ring) >= 3 else ring[0]
        m = pt._tee_metrics(lop, ring, c)
        along, off = lop.first_leg_coords(c)
        out.append(dict(d_front=m["d_front"], d_back=m["d_back"], d_centroid=m["d_centroid"],
                        offset=off, source=b.get("source", source), ids=[b.get("id")]))
    out.sort(key=lambda x: -x["d_centroid"])
    merged = []
    for b in out:
        if merged and merged[-1]["d_centroid"] - b["d_centroid"] < PARAMS["merge_yd"]:
            m = merged[-1]
            m["d_front"], m["d_back"] = min(m["d_front"], b["d_front"]), max(m["d_back"], b["d_back"])
            m["d_centroid"] = 0.5 * (m["d_centroid"] + b["d_centroid"])
            m["ids"] += b["ids"]
            continue
        merged.append(dict(b))
    for b in merged:
        b["len"] = b["d_back"] - b["d_front"]
    return merged


def slots(boxes, P=None):
    """Marker positions (yards to the green), back -> front."""
    P = dict(PARAMS, **(P or {}))
    out = []
    for b in boxes:
        if b["len"] >= P["long_yd"]:
            out += [b["d_back"] - P["slot_f"] * b["len"], b["d_front"] + P["slot_f"] * b["len"]]
        else:
            out.append(b["d_front"] + P["short_a"] * b["len"])
    return sorted(out, reverse=True)


def tee_complexes(holes, tees, pads=()):
    """ref -> merged boxes. OSM boxes first; pads only for holes with no OSM box."""
    lines = {str(h["ref"]) + "#" + str(i): [tuple(p) for p in h["line"][:-1]] + [tuple(h.get("green") or h["line"][-1])]
             for i, h in enumerate(holes)}
    keys = list(lines)
    by = pt.assign_tees_to_holes(lines, [dict(t, source=t.get("source", "osm")) for t in tees])
    byp = pt.assign_tees_to_holes(lines, [dict(p, source=p.get("source", "lidar")) for p in pads]) if pads else {}
    out = []
    for k, h in zip(keys, holes):
        bx = measure_boxes(h, by.get(k, []))
        if not bx and byp.get(k):
            bx = measure_boxes(h, byp[k], source="lidar")
        out.append(bx)
    return out


def with_line_start(sl, line_yd, P=None):
    """Add the routed line's start (a tee the router chose) as a slot when it lies behind every box."""
    P = dict(PARAMS, **(P or {}))
    if not sl or line_yd > sl[0] + P["merge_yd"]:
        return sorted(list(sl) + [line_yd], reverse=True)
    return list(sl)


# ----------------------------------------------------------------------------- 2. number of sets
def estimate_S(slot_counts, model=None, P=None):
    P = dict(PARAMS, **(P or {}))
    model = model or load_model()
    cs = sorted(slot_counts)
    if not cs:
        return int(model["s_table"]["0"])
    q = cs[min(len(cs) - 1, int(round(P["s_quantile"] * (len(cs) - 1))))]
    tab = model["s_table"]
    q = min(int(q), max(int(k) for k in tab))
    return int(tab[str(q)])


# ----------------------------------------------------------------------------- 3. joint assignment
def _hole_dp(iv, r, B, P):
    """Exact (beam-pruned) DP: sets 0..S-1 back -> front onto marker options iv = [(lo, hi)] (descending; a point
    slot has lo == hi, a box interval its extent) or off any box. A set on option k stands at its target r_s * B
    clamped into [lo, hi], never longer than the previous set (non-increasing). Returns (cost, [yards])."""
    S = len(r)
    INF = float("inf")
    best = {(-1, None): (0.0, [])}          # (last option idx, last yardage) -> (cost, path)
    for s in range(S):
        tgt = r[s] * B
        nb = {}
        for (j, ly), (c, path) in best.items():
            cands = []
            for k in range(max(j, 0), len(iv)):
                lo, hi = iv[k]
                cap = hi if ly is None else min(hi, ly - (P["same_gap"] if k == j and hi > lo else 0.0))
                if cap < lo - 1e-6:
                    if ly is not None and lo > ly + 1e-6 or k != j:
                        continue
                    cap = lo
                y = min(max(tgt, lo), cap)
                if ly is not None and y > ly + 1e-6:
                    continue
                cost = abs(y - tgt)
                if ly is not None and k != j and ly - y < P["min_gap"]:
                    cost += P["gap_w"] * (P["min_gap"] - (ly - y))
                cands.append((k, y, cost))
            y = tgt if ly is None else min(tgt, ly)
            cands.append((j, y, P["off_cost"] + abs(y - tgt)))
            for k, y, cost in cands:
                key = (k, round(y, 1))
                v = (c + cost, path + [y])
                if key not in nb or v[0] < nb[key][0]:
                    nb[key] = v
        best = dict(sorted(nb.items(), key=lambda kv: kv[1][0])[:60])
    return min(best.values(), key=lambda v: v[0]) if best else (INF, [])


def hole_options(boxes, line_yd, P=None):
    """(slot count used for S, DP options [(lo, hi)] descending, back yardage B) for one hole."""
    P = dict(PARAMS, **(P or {}))
    sl = slots(boxes, P)
    if P["line_start"]:
        sl = with_line_start(sl, line_yd, P)
    if P["mode"] == "interval":
        iv = [(b["d_front"], b["d_back"]) for b in boxes]
        if P["line_start"] and (not boxes or line_yd > boxes[0]["d_back"] + P["merge_yd"]):
            iv = [(line_yd, line_yd)] + iv
        if iv:
            lo, hi = iv[0]
            B = lo + P["short_a"] * (hi - lo)
            iv[0] = (lo, B)                  # the back set stands at B: nothing behind it
        else:
            B = line_yd
    else:
        iv = [(y, y) for y in sl]
        B = sl[0] if sl else line_yd
    return len(sl), iv, B


def assign_sets(opts, S, model=None, P=None):
    """opts: per hole (options [(lo, hi)], back yardage B) from hole_options. Returns (yards[h][s], ratios)."""
    P = dict(PARAMS, **(P or {}))
    model = model or load_model()
    rs = model["ratios"].get(str(S)) or [1.0 - 0.07 * i for i in range(S)]
    r = list(rs[:S])
    Y = []
    for _ in range(P["iters"]):
        Y = []
        for iv, B in opts:
            if not iv:
                Y.append([r[s] * B for s in range(S)])
                continue
            Y.append(_hole_dp(iv, r, B, P)[1])
        new = [1.0]
        for s in range(1, S):
            vals = sorted(y[s] / y[0] for y in Y if y and y[0] > 0)
            m = vals[len(vals) // 2] if vals else r[s]
            new.append(min(new[-1], P["ratio_upd"] * m + (1 - P["ratio_upd"]) * rs[s]))   # shrink to the prior
        r = new
    return Y, r


# ----------------------------------------------------------------------------- 4. par
def par_features(back, second, green_r, dogleg, line_yd):
    b = back / 100.0
    s2 = (second if second else back) / 100.0
    g = (green_r or 15.0) / 10.0
    return [1.0, b, b * b, s2, g, dogleg / 45.0, line_yd / 100.0]


def par_probs(x, W):
    if not W:
        b = x[1] * 100
        lp3 = -((max(0.0, b - 230)) / 20) ** 2
        lp5 = -((max(0.0, 480 - b)) / 25) ** 2
        lp4 = -((max(0.0, 250 - b)) / 20) ** 2 - ((max(0.0, b - 470)) / 25) ** 2
        z = [lp3, lp4, lp5]
    else:
        z = [sum(w * xi for w, xi in zip(row, x)) for row in W]
    m = max(z)
    e = [math.exp(v - m) for v in z]
    t = sum(e)
    return [v / t for v in e]


def _prior(n, total, n3, n5, pp):
    """log prior of a course with n holes, par total, n3 par 3s, n5 par 5s."""
    key = str(n)
    if pp and key in pp:
        d = pp[key]
        lt = math.log(d["total"].get(str(total), 0) + 0.5) - math.log(d["N"] + 0.5 * len(d["total"]) + 1)
        l3 = math.log(d["n3"].get(str(n3), 0) + 0.5) - math.log(d["N"] + 10)
        l5 = math.log(d["n5"].get(str(n5), 0) + 0.5) - math.log(d["N"] + 10)
        return lt + 0.5 * (l3 + l5)
    exp = 72 * n / 18.0
    return -abs(total - exp) * (0.7 if n >= 18 else 1.2) - 0.2 * abs(n3 - 4 * n / 18) - 0.2 * abs(n5 - 4 * n / 18)


def infer_pars(probs, model=None, prior_w=1.0):
    """Exact DP over (n3, n5) with the course prior. probs: per hole [p3, p4, p5]."""
    model = model or load_model()
    n = len(probs)
    best = {(0, 0): (0.0, [])}
    for p in probs:
        nb = {}
        for (a, c), (v, path) in best.items():
            for par, k in ((3, (a + 1, c)), (4, (a, c)), (5, (a, c + 1))):
                val = v + math.log(max(p[par - 3], 1e-6))
                if k not in nb or val > nb[k][0]:
                    nb[k] = (val, path + [par])
        best = nb
    out = None
    for (a, c), (v, path) in best.items():
        tot = 3 * a + 5 * c + 4 * (n - a - c)
        sc = v + prior_w * _prior(n, tot, a, c, model.get("par_prior"))
        if out is None or sc > out[0]:
            out = (sc, path)
    return out[1]


# ----------------------------------------------------------------------------- top level
def set_names(S):
    return ["Back", "2nd", "3rd", "4th", "5th", "6th", "7th"][:S]


def infer_card(holes, tees, pads=(), model=None, params=None, S=None):
    """Synthetic scorecard (scorecard/1 shape + diagnostics). holes: see module docstring."""
    P = dict(PARAMS, **(params or {}))
    model = model or load_model()
    geo = [hole_geometry(h)[2] for h in holes]
    boxes = tee_complexes(holes, tees, pads)
    ho = [hole_options(b, g["line_yd"], P) for b, g in zip(boxes, geo)]
    S_est = S or estimate_S([o[0] for o in ho], model, P)
    Y, r = assign_sets([(o[1], o[2]) for o in ho], S_est, model, P)
    probs = [par_probs(par_features(y[0], y[1] if len(y) > 1 else None, h.get("green_r_yd"), g["dogleg_deg"],
                                    g["line_yd"]), model.get("par")) for y, h, g in zip(Y, holes, geo)]
    pars = infer_pars(probs, model)
    names = set_names(S_est)
    tee_sets = {}
    for s, nm in enumerate(names):
        ys = [int(round(y[s])) for y in Y]
        tee_sets[nm] = dict(yards=ys, total=sum(ys), ratio=round(r[s], 3), inferred=True)
    return {"schema": "scorecard/1", "source": VERSION, "inferred": True, "par": pars,
            "tee_sets": tee_sets,
            "diagnostics": dict(S=S_est, slots_per_hole=[o[0] for o in ho],
                                boxes_per_hole=[len(b) for b in boxes],
                                box_sources=[sorted({x["source"] for x in b}) for b in boxes],
                                par_probs=[[round(v, 3) for v in p] for p in probs])}
