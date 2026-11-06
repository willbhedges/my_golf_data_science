"""Back 14 (265, drivable): 4-wood at the green vs lay-up, with explicit crown ricochets and lidar escape shots.

Reuses the engine's swings (M.shots / M.finish) and its lidar crown path-length stop model (the same exponential
draw per swing). Every ball the engine stops in a crown is instead deflected off a branch (cylinder collision,
random branch axis and impact parameter: forward-biased scatter), flies on with drag through the crowns (further
contacts at the same extinction k), lands on the lidar DTM, bounces and rolls on the DTM slope with lie friction,
and finishes: pond / under the trees / rough / green. Balls finishing in tree cells, or on grass under a crown with
no clean line, take a lidar escape shot (36 directions, low punch, crown base, trunks, understory) scored with the
engine's own strokes grid (short game + putting), plus unplayable / lost-in-leaves probabilities.
"""
import os, sys, json, math, time, argparse
import numpy as np
from scipy import ndimage
from matplotlib.path import Path

WT = '/home/user/my_golf_data_science'
sys.path.insert(0, os.path.join(WT, 'course_data', 'courses'))
import v2_course as vc

Y = 0.9144
G_ACC = 9.81

course, meta, M, D = vc.activate('eagle_knoll', 'truth')
h = 14 if 14 in M.HOLES else '14'
hd = M.HOLES[h]
R = M.Raster(hd)
P = D.central(h)
S = R.strokes(P, hd['length'])
O = M._lidar_opts
CAN = M._engine_opts['_canopy_of'](hd)
DROP = M._engine_opts['_drop_of'](hd)
ga, gl, TOP, BASE = CAN
CODE = M.CODE
INV = {v: k for k, v in CODE.items()}
GREEN_POLY = Path(np.asarray(hd['green_poly'], float))
HOLE = R.green

# ---------------------------------------------------------------- local 1-yd grids (tee frame): DTM, raw HAG
sys.path.insert(0, os.path.join(vc.CD, 'imagery'))
import render as RD
fr = RD.Frame.from_json(course.FRAMES[h])
tee, fwd, right, ppy = M.frame(hd)
RAW = os.path.join(WT, 'course_data/vision_any/eagle_knoll/raw')
AG = np.arange(120.0, 341.0, 1.0)
LG = np.arange(-100.0, 101.0, 1.0)
AA, LL = np.meshgrid(AG, LG, indexing='ij')
pts = tee + (AA.ravel()[:, None] * fwd + LL.ravel()[:, None] * right) * ppy
ll = fr.px_to_ll(pts)


def bilinear_sampler(path):
    import rasterio
    from pyproj import Transformer
    src = rasterio.open(path)
    z = src.read(1).astype(float)
    inv = ~src.transform
    to = Transformer.from_crs('EPSG:4326', src.crs.to_string(), always_xy=True)
    x, y = to.transform(ll[:, 0], ll[:, 1])
    c = inv.a * x + inv.b * y + inv.c - 0.5
    r = inv.d * x + inv.e * y + inv.f - 0.5
    return ndimage.map_coordinates(z, [r, c], order=1, mode='nearest')


DTM = bilinear_sampler(os.path.join(RAW, 'dtm.tif')).reshape(AA.shape) / Y          # yds
if not np.all(np.isfinite(DTM)):
    DTM = np.where(np.isfinite(DTM), DTM, np.nanmedian(DTM))
DTMs = ndimage.gaussian_filter(DTM, 1.0)
GZA, GZL = np.gradient(DTMs, 1.0, 1.0)                                            # dz/da, dz/dl (yd/yd)
HAG = vc._raster_nearest(os.path.join(RAW, 'hag.tif'))(ll).reshape(AA.shape)
HAG[~np.isfinite(HAG) | (HAG == 255)] = 0
HAG_M = HAG * 0.25
UNDER = (HAG_M >= 1.0) & (HAG_M < O['min_tree_m'])                                 # understory / shrubs 1-4 m


def gidx(a, l, A, L):
    ia = np.clip(np.rint((a - A[0])).astype(np.int32), 0, len(A) - 1)
    il = np.clip(np.rint((l - L[0])).astype(np.int32), 0, len(L) - 1)
    return ia, il


def top_base(a, l):
    ia, il = gidx(a, l, ga, gl)
    return TOP[ia, il], BASE[ia, il]


def ground(a, l):
    ia, il = gidx(a, l, AG, LG)
    return DTMs[ia, il]


def lie_at(a, l):
    return R.lie_at(a, l)


def on_green(a, l):
    return GREEN_POLY.contains_points(np.column_stack([np.ravel(a), np.ravel(l)])).reshape(np.shape(a))


# ---------------------------------------------------------------- crown map near the green
def crown_report():
    ia0, il0 = gidx(np.array([200.0]), np.array([-60.0]), ga, gl)
    out = {}
    lie = R.lie_at(AA, LL)
    t, b = top_base(AA, LL)
    zones = {'left of green / pond (a 225-280, l -60..-12)': (AA >= 225) & (AA <= 280) & (LL >= -60) & (LL <= -12),
             'right of green / pond (a 230-280, l +18..+60)': (AA >= 230) & (AA <= 280) & (LL >= 18) & (LL <= 60),
             'behind green (a 276-310, l -25..+25)': (AA >= 276) & (AA <= 310) & (LL >= -25) & (LL <= 25)}
    for name, m in zones.items():
        cr = m & (t > 0)
        d = {'cells_yd2': int(m.sum()), 'crown_cover': round(float(cr.sum() / m.sum()), 3),
             'top_yds_p50': round(float(np.median(t[cr])), 1), 'top_yds_p90': round(float(np.percentile(t[cr], 90)), 1),
             'base_yds_p50': round(float(np.median(b[cr])), 1),
             'understory_1_4m_share': round(float((UNDER & m).sum() / m.sum()), 3),
             'map_tree_share': round(float((m & (lie == CODE['recovery'])).sum() / m.sum()), 3)}
        # density: share of 1-m lidar cells >= 4 m within 5 yds of a crown cell (closed canopy ~1, open-grown ~0.5)
        dens = ndimage.uniform_filter((HAG_M >= O['min_tree_m']).astype(float), 11)
        d['local_canopy_density_p50'] = round(float(np.median(dens[cr])), 2)
        gz = np.hypot(GZA, GZL)
        d['ground_slope_pct_p50'] = round(float(np.median(gz[m]) * 100), 1)
        d['ground_slope_pct_p90'] = round(float(np.percentile(gz[m], 90) * 100), 1)
        out[name] = d
    # the bank: ground slope in the 6 yds next to the pond, and the drop from the tree line to the water
    water = lie == CODE['water']
    near = ndimage.binary_dilation(water, iterations=6) & ~water
    gz = np.hypot(GZA, GZL)
    out['pond bank (6 yds round the water)'] = {
        'slope_pct_p50': round(float(np.median(gz[near]) * 100), 1),
        'slope_pct_p90': round(float(np.percentile(gz[near], 90) * 100), 1),
        'water_level_yds_rel_green': round(float(np.median(DTMs[water]) - np.median(DTMs[on_green(AA, LL)])), 2),
        'tree_ground_above_water_yds_p50': round(float(np.median(DTMs[(lie == CODE['recovery']) & ndimage.binary_dilation(water, iterations=15) & ~water]) - np.median(DTMs[water])), 2)}
    return out


# ---------------------------------------------------------------- engine flight + stop record (copy of the loop)
def trace(club, z, aims):
    car, dev, roll = M.shots(hd, club, P, z)
    a, l, lie = M.finish(R, car[:, None], dev[:, None] + aims[None, :], roll[:, None], P['rough_roll'],
                         P.get('v1_roll', False))
    k = float(O['k_per_yd'])
    kind = 'wood' if club in M.WOODS else 'iron'
    cm = float(np.median(car))
    n = max(4, int(np.ceil((1.0 - O['f0']) * cm / O['step_yds'])))
    F = np.linspace(O['f0'], 1.0, n + 1)[:-1] + 0.5 * (1.0 - O['f0']) / n
    y = vc.flight_heights(F, kind, cm)
    xs = np.linspace(0, 1, 401)
    dydx = np.gradient(vc.flight_heights(xs, kind, cm), np.linspace(0, cm, 401))
    slope = np.interp(F, xs, dydx)
    dga, dgl, dg = DROP

    def drop(pa, pl):
        ia = np.clip(np.rint((pa - dga[0]) / vc.DROP_STEP).astype(np.int32), 0, len(dga) - 1)
        il = np.clip(np.rint((pl - dgl[0]) / vc.DROP_STEP).astype(np.int32), 0, len(dgl) - 1)
        return dg[ia, il]
    u = np.random.default_rng(int(z.shape[1]) * 7919 + 17).random(z.shape[1])
    need = (-np.log1p(-np.minimum(u, 1 - 1e-12)) / k).astype(np.float32)
    shp = a.shape
    lat0 = (dev[:, None] + aims[None, :]).ravel()
    car1 = np.broadcast_to(car[:, None], shp).ravel()
    need1 = np.broadcast_to(need[:, None], shp).ravel()
    d_land = drop(car1, lat0)
    tmax = float(TOP.max())
    dmin = float(dg.min())
    acc = np.zeros(car1.shape, np.float32)
    stop = np.zeros(car1.shape, bool)
    ha, hl, hc, hs = (np.zeros(car1.shape) for _ in range(4))
    for f, yf, sl in zip(F, y, slope):
        c = np.flatnonzero((yf - f * d_land + dmin < tmax) & ~stop & (car1 * f >= O['min_along']))
        if not c.size:
            continue
        pa, pl = car1[c] * f, lat0[c] * f
        clear = yf - f * d_land[c] + drop(pa, pl)
        ia = np.clip(np.rint((pa - ga[0]) / vc.CANOPY_STEP).astype(np.int32), 0, len(ga) - 1)
        il = np.clip(np.rint((pl - gl[0]) / vc.CANOPY_STEP).astype(np.int32), 0, len(gl) - 1)
        ins = (clear < TOP[ia, il]) & (clear > BASE[ia, il])
        if not ins.any():
            continue
        c, pa, pl, clear = c[ins], pa[ins], pl[ins], clear[ins]
        acc[c] += (car1[c] * (1.0 - O['f0']) / n * math.sqrt(1.0 + sl * sl)).astype(np.float32)
        s = acc[c] >= need1[c]
        c, pa, pl, clear = c[s], pa[s], pl[s], clear[s]
        ha[c], hl[c], hc[c], hs[c] = pa, pl, clear, sl
        stop[c] = True
    eng_a = np.where(stop.reshape(shp), ha.reshape(shp), a)
    eng_l = np.where(stop.reshape(shp), hl.reshape(shp), l)
    eng_lie = R.lie_at(eng_a, eng_l)
    eng_s = S[R.idx(eng_a, eng_l)]
    return dict(a=a, l=l, lie=lie, stop=stop.reshape(shp), ha=ha.reshape(shp), hl=hl.reshape(shp),
                hc=hc.reshape(shp), hs=hs.reshape(shp), car=np.broadcast_to(car[:, None], shp),
                lat0=lat0.reshape(shp), eng_a=eng_a, eng_l=eng_l, eng_lie=eng_lie, eng_s=eng_s, kind=kind)


# ---------------------------------------------------------------- ricochet physics
PHYS = dict(e_n=0.40, e_t=0.70, scatter='central', v_land_wood=22.0, v_land_iron=20.0, vt=32.0, k=O['k_per_yd'],
            mu={'green': 0.06, 'fairway': 0.09, 'rough': 0.30, 'trees': 0.45}, bounce_h=0.55, max_hits=8)


def impact_param(rng, n, scatter):
    u = rng.random(n)
    s = np.where(rng.random(n) < 0.5, -1.0, 1.0)
    if scatter == 'low':          # glancing contacts only: |b| in 0.5..1, mostly forward
        b = 1 - 0.5 * u
    elif scatter == 'high':       # weighted to head-on (more back-scatter)
        b = u ** 2
    else:
        b = u
    return s * b


def collide(v, rng, ph):
    n = len(v)
    w = rng.normal(size=(n, 3))
    w /= np.linalg.norm(w, axis=1, keepdims=True)                               # branch axis, isotropic
    vperp = v - (np.sum(v * w, 1, keepdims=True)) * w
    vp = np.linalg.norm(vperp, axis=1, keepdims=True)
    vh = vperp / np.maximum(vp, 1e-9)
    b = impact_param(rng, n, ph['scatter'])[:, None]
    nrm = -np.sqrt(1 - b ** 2) * vh + b * np.cross(w, vh)                       # outward normal at the contact
    vn = np.sum(v * nrm, 1, keepdims=True)
    vn = np.minimum(vn, 0.0)
    vnv = vn * nrm
    vt = v - vnv
    return ph['e_t'] * vt - ph['e_n'] * vnv


def ricochet(st, idx, rng, ph):
    """idx: flat indices of stopped balls. Returns final (a, l, kind) with kind in {'water', 'land'}; a, l in yds."""
    a0 = st['ha'].ravel()[idx]; l0 = st['hl'].ravel()[idx]
    clear = st['hc'].ravel()[idx]; sl = st['hs'].ravel()[idx]
    car = st['car'].ravel()[idx]; lat = st['lat0'].ravel()[idx]
    vland = ph['v_land_wood'] if st['kind'] == 'wood' else ph['v_land_iron']
    frac = a0 / np.maximum(car, 1)
    speed = vland * (1 + 0.5 * np.clip((1 - frac) / 0.4, 0, 1))                    # faster higher up the descent
    uh = np.column_stack([car, lat]); uh /= np.linalg.norm(uh, axis=1, keepdims=True)
    th = np.arctan(sl)                                                           # negative: descending
    v = np.column_stack([uh * np.cos(th)[:, None], np.sin(th)]) * speed[:, None]  # m/s, (a, l, up)
    pos = np.column_stack([a0, l0, ground(a0, l0) + clear]) * Y                  # m
    v = collide(v, rng, ph)
    n = len(idx)
    need = rng.exponential(1.0 / ph['k'], n) * Y                                  # m of crown to the next contact
    acc = np.zeros(n)
    hits = np.ones(n, int)
    alive = np.ones(n, bool)
    land_v = np.zeros((n, 3))
    dt = 0.01
    kd = G_ACC / ph['vt'] ** 2
    for _ in range(800):
        if not alive.any():
            break
        c = np.flatnonzero(alive)
        vv = v[c]
        sp = np.linalg.norm(vv, axis=1, keepdims=True)
        acc_v = -kd * sp * vv; acc_v[:, 2] -= G_ACC
        vv = vv + acc_v * dt
        p = pos[c] + vv * dt
        a_y, l_y, z_y = p[:, 0] / Y, p[:, 1] / Y, p[:, 2] / Y
        gz = ground(a_y, l_y)
        hgt = z_y - gz
        t, b = top_base(a_y, l_y)
        inc = (hgt < t) & (hgt > b) & (hits[c] < ph['max_hits'])
        acc[c] += np.where(inc, np.linalg.norm(vv, axis=1) * dt, 0)
        hit = inc & (acc[c] >= need[c])
        if hit.any():
            hc = c[hit]
            vv[hit] = collide(vv[hit], rng, ph)
            hits[hc] += 1
            acc[hc] = 0
            need[hc] = rng.exponential(1.0 / ph['k'], len(hc)) * Y
        landed = hgt <= 0
        p[landed, 2] = gz[landed] * Y
        pos[c] = p
        v[c] = vv
        if landed.any():
            land_v[c[landed]] = vv[landed]
            alive[c[landed]] = False
    # roll on the DTM
    a = pos[:, 0] / Y; l = pos[:, 1] / Y
    vh = land_v[:, :2] * ph['bounce_h']                                           # m/s, first bounce on soft ground
    out = np.zeros(n, '<U5'); out[:] = 'land'
    lie = lie_at(a, l)
    wet = lie == CODE['water']
    out[wet] = 'water'
    moving = ~wet
    mu_of = np.full(len(M.LIES), ph['mu']['rough'])
    mu_of[CODE['fairway']] = ph['mu']['fairway']; mu_of[CODE['first_cut']] = ph['mu']['fairway'] * 1.5
    mu_of[CODE['recovery']] = ph['mu']['trees']; mu_of[CODE['native']] = ph['mu']['trees']
    mu_of[CODE['sand']] = 1.0
    dt = 0.02
    for _ in range(1500):
        c = np.flatnonzero(moving)
        if not c.size:
            break
        ac, lc = a[c], l[c]
        lie = lie_at(ac, lc)
        mu = mu_of[lie]
        mu = np.where(on_green(ac, lc) & (lie != CODE['water']), ph['mu']['green'], mu)
        ia, il = gidx(ac, lc, AG, LG)
        gxa, gxl = GZA[ia, il], GZL[ia, il]
        vv = vh[c]
        sp = np.linalg.norm(vv, axis=1)
        grav = -G_ACC * np.column_stack([gxa, gxl])                               # small-slope approximation
        fr_ = -mu[:, None] * G_ACC * vv / np.maximum(sp, 1e-6)[:, None]
        slope = np.hypot(gxa, gxl)
        stuck = (sp < 0.15) & (slope < mu)
        vv = np.where(stuck[:, None], 0.0, vv + (grav + fr_) * dt)
        vh[c] = vv
        a[c] += vv[:, 0] * dt / Y; l[c] += vv[:, 1] * dt / Y
        stopnow = stuck
        wetn = lie_at(a[c], l[c]) == CODE['water']
        out[c[wetn]] = 'water'
        moving[c[stopnow | wetn]] = False
    return a, l, out


# ---------------------------------------------------------------- escape-shot value grid (lidar line of sight)
ESC = dict(delta=0.05, trunk=0.015, under=0.10, crown_k=O['k_per_yd'], sd0=2.0, sd_rel=0.20, punch_h=3.0,
           p_unp=0.03, p_lost=0.02)


def escape_grid(esc):
    lie = R.lie_at(AA, LL)
    t, b = top_base(AA, LL)
    trees = lie == CODE['recovery']
    underc = (t > 0) & ~trees & (lie != CODE['water'])
    need = trees | underc
    ia, il = np.nonzero(need)
    a0, l0 = AG[ia], LG[il]
    Sg = S[R.idx(AA, LL)]
    water = lie == CODE['water']
    openl = ~trees & ~water & (lie != CODE['ob']) & (lie != CODE['native'])
    th = np.deg2rad(np.arange(0, 360, 10.0))
    # always include the exact direction to the hole
    dirs = [(np.cos(x) * np.ones_like(a0), np.sin(x) * np.ones_like(a0)) for x in th]
    dh = np.hypot(HOLE[0] - a0, HOLE[1] - l0)
    dirs.append(((HOLE[0] - a0) / np.maximum(dh, 1e-6), (HOLE[1] - l0) / np.maximum(dh, 1e-6)))
    s_steps = np.arange(1.0, 71.0, 1.0)
    best_V, best_p = [], []
    hole_p = None
    for j, (ua, ul) in enumerate(dirs):
        haz = np.zeros(len(a0)); blocked_water = np.zeros(len(a0), bool)
        Vs = np.full(len(a0), np.inf); ps = np.zeros(len(a0))
        prof = []
        for s in s_steps:
            pa, pl = a0 + ua * s, l0 + ul * s
            ja, jl = gidx(pa, pl, AG, LG)
            hh = np.minimum(esc['punch_h'], 0.35 * s)                            # low punch: up at ~19 deg, then flat
            tt, bb = t[ja, jl], b[ja, jl]
            in_crown = (tt > 0) & (hh > bb)
            in_tree = trees[ja, jl] | ((tt > 0) & (hh <= bb))
            haz += np.where(in_crown, esc['crown_k'], 0) + np.where(in_tree, esc['trunk'], 0) \
                + np.where(UNDER[ja, jl], esc['under'], 0)
            blocked_water |= water[ja, jl]
            prof.append((pa, pl, np.exp(-haz), blocked_water.copy()))
        # aim at spot s: land around s with sd, value = 1 + mean S over that spread (along the ray)
        for i, s in enumerate(s_steps):
            pa, pl, pcl, bw = prof[i]
            ja, jl = gidx(pa, pl, AG, LG)
            ok = openl[ja, jl] & ~bw
            if not ok.any():
                continue
            sd = esc['sd0'] + esc['sd_rel'] * s
            vals = 0.0
            for q, wq in ((-1.5, 0.067), (-0.75, 0.24), (0.0, 0.386), (0.75, 0.24), (1.5, 0.067)):
                pq_a, pq_l = pa + ua * q * sd, pl + ul * q * sd
                qa, ql = gidx(pq_a, pq_l, AG, LG)
                vals = vals + wq * Sg[qa, ql]          # spread into the trees: the engine's punch-out value there
            # a landing spread into the trees / water: crude, back in the trees (2 more) or the water score
            vals = np.where(vals > 50, np.nan, vals)
            V = 1.0 + vals + esc['delta']
            V = np.where(ok & np.isfinite(V), V, np.inf)
            better = V < Vs
            Vs = np.where(better, V, Vs); ps = np.where(better, pcl, ps)
        best_V.append(Vs); best_p.append(ps)
    # lofted pitch (wedge) toward the hole and +/-10, 20 deg: may carry water, must stay under the crown base
    hdir = np.arctan2(HOLE[1] - l0, HOLE[0] - a0)
    for dth in np.deg2rad([0, -10, 10, -20, 20]):
        ua, ul = np.cos(hdir + dth), np.sin(hdir + dth)
        Vs = np.full(len(a0), np.inf); ps = np.zeros(len(a0))
        for C in np.arange(4.0, 46.0, 1.0):
            Hp = min(0.22 * C, 9.0)
            haz = np.zeros(len(a0))
            for x in np.arange(0.5, C, 1.0):
                pa, pl = a0 + ua * x, l0 + ul * x
                ja, jl = gidx(pa, pl, AG, LG)
                hh = 4 * Hp * (x / C) * (1 - x / C)
                tt, bb = t[ja, jl], b[ja, jl]
                haz += np.where((tt > 0) & (hh > bb) & (hh < tt), esc['crown_k'], 0) \
                    + np.where((trees[ja, jl] | (tt > 0)) & (hh <= bb) & (hh < 2.0), esc['trunk'], 0) \
                    + np.where(UNDER[ja, jl] & (hh < 4.4), esc['under'], 0)
            pa, pl = a0 + ua * C, l0 + ul * C
            sd = esc['sd0'] + 1.5 * esc['sd_rel'] * C                              # pitch from a tree lie: wider
            vals = 0.0
            for q, wq in ((-1.5, 0.067), (-0.75, 0.24), (0.0, 0.386), (0.75, 0.24), (1.5, 0.067)):
                qa, ql = gidx(pa + ua * q * sd, pl + ul * q * sd, AG, LG)
                vals = vals + wq * Sg[qa, ql]
            ja, jl = gidx(pa, pl, AG, LG)
            V = np.where(openl[ja, jl], 1.0 + vals + 2 * esc['delta'], np.inf)
            pcl = np.exp(-haz)
            better = V < Vs
            Vs = np.where(better, V, Vs); ps = np.where(better, pcl, ps)
        best_V.insert(-1, Vs); best_p.insert(-1, ps)
    best_V = np.array(best_V); best_p = np.array(best_p)
    # E = min_r p V + (1 - p)(1 + E): ball that hits wood stays about where it was
    E = np.nanmin(np.where(np.isfinite(best_V), best_V, 9.0), axis=0) + 1.0
    for _ in range(20):
        cand = best_p * best_V + (1 - best_p) * (1 + E[None, :])
        cand = np.where(np.isfinite(best_V), cand, np.inf)
        E = np.min(cand, axis=0)
    E = np.where(np.isfinite(E), E, 6.0)
    # unplayable (penalty drop nearby, same escape) and lost in the leaf litter (stroke and distance)
    sd_cost = 1.0 + M.tee_value(hd['length'], P)
    Et = (1 - esc['p_unp'] - esc['p_lost']) * E + esc['p_unp'] * (1 + E) + esc['p_lost'] * sd_cost
    # grass under a crown edge: the escape only if it beats the engine's value with a clean line to the hole
    p_hole = best_p[-1]
    eng = Sg[ia, il]
    is_tree = trees[ia, il]
    val = np.where(is_tree, Et, np.where(p_hole >= 0.8, eng, np.maximum(eng, E)))
    grid = np.full(AA.shape, np.nan)
    grid[ia, il] = val
    hp = np.full(AA.shape, np.nan); hp[ia, il] = p_hole
    return grid, hp


# ---------------------------------------------------------------- scoring
def classify(a, l, lie, stopped, wet):
    cls = np.empty(a.shape, '<U24')
    g = on_green(a, l) & (lie != CODE['water'])
    cls[:] = 'rough/short grass'
    cls[g] = 'green'
    tr = lie == CODE['recovery']
    cls[tr & (l < -8)] = 'trees left'
    cls[tr & (l > 8)] = 'trees right'
    cls[tr & (l >= -8) & (l <= 8)] = 'trees behind' if True else ''
    cls[tr & (l >= -8) & (l <= 8) & (a < 240)] = 'trees short'
    w = (lie == CODE['water']) | wet
    cls[w & ~stopped] = 'pond direct'
    cls[w & stopped] = 'pond by ricochet'
    far = (a < 230) & ~w & ~tr
    cls[far & ~g] = 'lay-up grass'
    return cls


def score_club(club, z, aims, ph, esc_grid, seed=11):
    st = trace(club, z, aims)
    a = st['a'].copy(); l = st['l'].copy(); lie = st['lie'].copy()
    stop = st['stop']
    wet = np.zeros(a.shape, bool)
    idx = np.flatnonzero(stop.ravel())
    if idx.size:
        rng = np.random.default_rng(seed)
        fa, fl, kind = ricochet(st, idx, rng, ph)
        af, lf, wf = a.ravel(), l.ravel(), wet.ravel()
        af[idx] = fa; lf[idx] = fl; wf[idx] = kind == 'water'
        a, l, wet = af.reshape(a.shape), lf.reshape(a.shape), wf.reshape(a.shape)
        lie = R.lie_at(a, l)
        lie = np.where(wet, CODE['water'], lie)
    s = S[R.idx(a, l)].copy()
    # water by ricochet: lateral relief beside the crossing ~ back-on-line, take the engine's water value
    ia, il = gidx(a, l, AG, LG)
    inside = (a >= AG[0]) & (a <= AG[-1]) & (l >= LG[0]) & (l <= LG[-1])
    ev = esc_grid[ia, il]
    use = inside & np.isfinite(ev) & (lie != CODE['water'])
    s = np.where(use, ev, s)
    # ricochet balls that end in water cells but the map cell is not water (rolled in): engine water value of
    # the nearest water cell ~ 1 + rough from the entry; use 1 + rough at the distance from the hole
    wfix = wet & (R.lie_at(a, l) != CODE['water'])
    if wfix.any():
        s = np.where(wfix, 1.0 + M.table('rough', np.hypot(a - HOLE[0], l - HOLE[1]), P), s)
    tot = 1.0 + s
    cls = classify(a, l, lie, stop, wet)
    return tot, cls, st


def summarize(tot, cls, j):
    t = tot[:, j]; c = cls[:, j]
    out = {}
    for k in ['green', 'rough/short grass', 'lay-up grass', 'trees left', 'trees right', 'trees behind', 'trees short',
              'pond direct', 'pond by ricochet']:
        m = c == k
        if m.any():
            out[k] = dict(share=round(float(m.mean()), 4), avg=round(float(t[m].mean()), 3))
    return out
