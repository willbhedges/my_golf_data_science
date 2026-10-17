"""Second-shot model: reach, dispersion by distance and lie, and expected strokes to hole out after it.

Bag (calm carry / finishing yds on a soft course, the golfer's numbers + typical 12-yd gapping from a
210-carry 4-iron; see REPORT.md "Evidence"): 2-wood off the deck ~255/265, 4-wood ~248/258, 4-iron 210,
5i 198, 6i 186, 7i 174, 8i 162, 9i 150, PW 138, GW 126, SW 113, LW 100 (full wedges ~100-130).
The model doesn't pick a named club per shot: any distance up to the lie's reach can be played, with the
dispersion of that distance. Clubs are named in the report from CLUB_FOR.

Dispersion (95% pattern = +/- 2 sigma, as the tee model): lateral sigma by shot distance from the
fairway, fitted so the mean proximity matches a 5-handicap (Broadie / Stagner / Arccos anchors:
~35 ft from 100 yds, ~45 ft from 150, ~65 ft from 200); depth sigma = 1.5 x lateral (Broadie: amateur
approach patterns are ~50% longer than wide). First cut, rough and fairway sand widen it.
Long clubs (over 200 yds) mishit 15% of the time and finish 75-92% of the intended distance.

Expected strokes after the shot: PGA Tour tables (Broadie; same choice as final_decision.py): putting by
feet, short game 2-40 yds by lie, tee_strategy.BASELINE beyond. HCP=True adds 5-handicap offsets.
"""
import numpy as np

import geom
import tee_strategy as t

# finishing distance the lie lets you reach (yds)
REACH = {"fairway": 265.0, "first_cut": 260.0, "rough": 235.0, "sand": 190.0, "green": 265.0}
CLUB_FOR = [(258, "2-wood"), (245, "4-wood"), (222, "4-wood (smooth) / driving iron"), (214, "4-iron"),
            (202, "5-iron"), (190, "6-iron"), (178, "7-iron"), (166, "8-iron"), (154, "9-iron"),
            (141, "PW"), (128, "GW"), (115, "SW"), (102, "LW"), (0, "LW (partial)")]

SIG_D = np.array([30, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275], float)
SIG_LAT = np.array([3.5, 4.5, 5.8, 7.0, 8.2, 9.4, 11.2, 13.4, 15.8, 18.5, 21.0])
DEPTH_RATIO = 1.5
# (lateral, depth) multipliers on the fairway pattern
LIE_MULT = {"fairway": (1.0, 1.0), "green": (1.0, 1.0), "first_cut": (1.08, 1.12),
            "rough": (1.2, 1.35), "sand": (1.4, 1.5)}
MISHIT_FROM, MISHIT_RATE, MISHIT_RANGE = 200.0, 0.15, (0.75, 0.92)
TARGETABLE = ("fairway", "first_cut", "rough", "sand", "green")

PUTT_FT = np.array([1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 50, 60, 90], float)
PUTTS = np.array([1.00, 1.01, 1.04, 1.13, 1.23, 1.34, 1.50, 1.61, 1.78, 1.87, 1.98, 2.06, 2.14, 2.21, 2.40])
SHORT_D = np.array([2, 5, 10, 15, 20, 30, 40], float)
SHORT = {"fairway": [1.95, 2.05, 2.18, 2.30, 2.40, 2.52, 2.60],
         "first_cut": [2.00, 2.10, 2.23, 2.36, 2.47, 2.58, 2.66],
         "rough": [2.10, 2.20, 2.34, 2.47, 2.59, 2.70, 2.78],
         "sand": [2.30, 2.37, 2.43, 2.48, 2.53, 2.66, 2.82],
         "recovery": [3.00, 3.10, 3.20, 3.30, 3.40, 3.48, 3.55]}
HCP = False                        # True: approximate 5-handicap offsets (research.md section 2)
HCP_PUTT, HCP_SHORT = 0.06, 0.15
PARTIAL_WEDGE = 0.0                # sensitivity: extra strokes for a 45-85 yd partial wedge (0 = none)


def sigma(dist, lie="fairway"):
    lat = np.interp(dist, SIG_D, SIG_LAT)
    ml, md = LIE_MULT.get(lie, (1.0, 1.0))
    return lat * ml, lat * DEPTH_RATIO * md


def club_for(dist):
    for d, name in CLUB_FOR:
        if dist >= d:
            return name
    return CLUB_FOR[-1][1]


# ------------------------------------------------------------------ baselines
def putts(ft):
    e = np.interp(np.clip(ft, 1, 90), PUTT_FT, PUTTS) + np.maximum(np.asarray(ft) - 90, 0) * 0.005
    return e + (HCP_PUTT if HCP else 0.0)


def baseline(lie, dist):
    """Expected strokes to hole out from a lie at `dist` yds (no geometry)."""
    dist = np.asarray(dist, float)
    if lie == "green":
        return putts(dist * 3.0)
    long = t.expected_strokes(lie, np.maximum(dist, 20))
    if lie in SHORT:
        short = np.interp(np.clip(dist, 2, 40), SHORT_D, SHORT[lie]) + (HCP_SHORT if HCP else 0.0)
        out = np.where(dist < 40, short, long)
    else:
        out = long
    if PARTIAL_WEDGE and lie in ("fairway", "first_cut", "rough"):
        out = out + PARTIAL_WEDGE * ((dist >= 45) & (dist <= 85))
    return out


# ------------------------------------------------------------------ pins
def pins(hole, k=16, inset=4.0, seed=3):
    """k pin positions spread over the green, at least `inset` yds from the edge (fixed seed)."""
    g = hole.green
    lo, hi = g.min(axis=0), g.max(axis=0)
    xs, ys = np.meshgrid(np.arange(lo[0], hi[0], 1.0), np.arange(lo[1], hi[1], 1.0))
    cand = np.c_[xs.ravel(), ys.ravel()]
    cand = cand[hole.green_path.contains_points(cand)]
    seg_a, seg_b = g, np.roll(g, -1, axis=0)
    d = np.full(len(cand), np.inf)
    for a, b in zip(seg_a, seg_b):
        ab = b - a
        u = np.clip(((cand - a) @ ab) / (ab @ ab), 0, 1)
        d = np.minimum(d, np.hypot(*(cand - (a + u[:, None] * ab)).T))
    pool = cand[d >= inset]
    if len(pool) < k:
        pool = cand[np.argsort(-d)[:max(k, 1)]]
    rng = np.random.default_rng(seed)
    return pool[rng.choice(len(pool), size=min(k, len(pool)), replace=False)]


# ------------------------------------------------------------------ outcome scoring
def score_outcomes(hole, raster, fin, start_e, pin_pts):
    """Expected strokes to hole out from each finishing point (pin-averaged).

    fin: (..., 2) yds; start_e: expected strokes from where the shot was played (for OB / lost ball:
    stroke and distance), broadcastable to fin[..., 0]."""
    ids = raster.lie_id(fin)
    flat = fin.reshape(-1, 2)
    fid = ids.ravel()
    se = np.broadcast_to(np.asarray(start_e, float), ids.shape).ravel()
    dp = np.hypot(flat[:, None, 0] - pin_pts[None, :, 0], flat[:, None, 1] - pin_pts[None, :, 1])   # N x K
    dc = np.hypot(*(flat - hole.green_c).T)
    out = np.empty(len(flat))
    L = geom.LIE_ID
    m = fid == L["green"]
    out[m] = putts(dp[m] * 3.0).mean(axis=1)
    for lie in ("fairway", "first_cut", "rough", "sand"):
        m = fid == L[lie]
        if m.any():
            near = dc[m] < 45
            v = baseline(lie, dc[m])
            if near.any():
                v[near] = baseline(lie, dp[m][near]).mean(axis=1)
            out[m] = v
    m = fid == L["recovery"]
    out[m] = t.TREE_SEVERITY * baseline("recovery", np.maximum(dc[m], 2)) + \
        (1 - t.TREE_SEVERITY) * baseline("rough", np.maximum(dc[m], 2))
    m = fid == L["water"]                       # penalty drop near where it went in
    out[m] = 1.0 + baseline("rough", np.maximum(dc[m], 10))
    m = fid == L["ob"]                          # stroke and distance
    out[m] = 1.0 + se[m]
    m = fid == L["native"]                      # lost = stroke and distance, else hack out
    out[m] = t.NATIVE_LOST * (1.0 + se[m]) + (1 - t.NATIVE_LOST) * baseline("recovery", np.maximum(dc[m], 2))
    return out.reshape(ids.shape), ids


def shot(start, aim, lie, z, reach=None):
    """Finishing points of shots from `start` (2,) aimed at `aim` (2,) from `lie`.
    z: (4, n) standard normals (rows 0-1) and uniforms (rows 2-3) - common random numbers."""
    start, aim = np.asarray(start, float), np.asarray(aim, float)
    v = aim - start
    d_aim = float(np.linalg.norm(v))
    u = v / max(d_aim, 1e-9)
    r = geom.right_of(u)
    reach = REACH.get(lie, 0.0) if reach is None else reach
    d = min(d_aim, reach)
    sl, sd = sigma(d, lie)
    along = d + sd * z[0]
    if d > MISHIT_FROM:
        mis = z[2] < MISHIT_RATE
        lo, hi = MISHIT_RANGE
        along = np.where(mis, d * (lo + (hi - lo) * z[3]), along)
    lat = sl * z[1]
    return start + along[:, None] * u + lat[:, None] * r, d


def z_draws(n, seed=0):
    rng = np.random.default_rng(seed)
    return np.vstack([rng.standard_normal((2, n)), rng.random((2, n))])
