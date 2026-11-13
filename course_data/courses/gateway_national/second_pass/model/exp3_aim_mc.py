"""Aim search and Monte Carlo soundness, central world, Back.  python3 exp3_aim_mc.py out.json [holes]
 (a) aim-curve shape at the optimum: cost of +/-3 / +/-5 / +/-10 yds, the 0.005 window, which side is steeper;
 (b) grid: 0.5-yd grid + 1-yd smoothing + spline  vs  a 0.25-yd grid on 60,000 swings without smoothing;
 (c) aim as a rotation of the whole pattern about the tee (the engine translates it sideways);
 (d) selection bias: 8 independent swing sets; in-sample EV of the chosen club/aim vs its EV on fresh swings;
     how often the pick changes; spread of the aim."""
import json, sys, time
from harness import *

out = sys.argv[1]
holes = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else HOLES
NB = 40000


def big_curve(h, c, aims, P, seed=901, rot=False):
    hd = M.HOLES[h]
    R = raster(h)
    S = R.strokes(P, hd["length"])
    z = zz(NB, seed)
    ev = np.zeros(len(aims))
    se = np.zeros(len(aims))
    car, dev, roll = M.shots(hd, c, P, z)
    tot = float(np.median(car + roll))
    cols = []
    for i in range(0, len(aims), 16):
        am = aims[i:i + 16]
        if rot:
            th = np.arcsin(np.clip(am / tot, -0.9, 0.9))[None, :]
            a0 = car[:, None] * np.cos(th) - dev[:, None] * np.sin(th)
            l0 = car[:, None] * np.sin(th) + dev[:, None] * np.cos(th)
            # the aim point is `am` yds right at the club's total: carry + roll along the rotated line
            a, l, lie = M.finish(R, a0, l0, roll[:, None], P["rough_roll"])
        else:
            a, l, lie = M.finish(R, car[:, None], dev[:, None] + am[None, :], roll[:, None], P["rough_roll"])
        s = 1.0 + S[R.idx(a, l)]
        cols.append(s.astype(np.float32))
    s = np.hstack(cols)
    return s.mean(0), s


res = {}
for h in holes:
    t0 = time.time()
    P = D.central(h)
    base = solve(h, P)
    top = base["order"][:3]
    r = dict(base=dict(pick=base["pick"], aim=base["aim"], margin=base["margin"], se=base["se"], clubs=base["clubs"]))
    # (a) + (b): fine curve, pick and runner
    fine = {}
    for c in top:
        a0 = base["clubs"][c]["aim"]
        aims = np.arange(a0 - 12, a0 + 12.001, 0.25)
        ev, s = big_curve(h, c, aims, P)
        j = int(np.argmin(ev))
        # paired SE of ev(aim) - ev(best) for a few offsets
        def cost(dx):
            k = int(np.argmin(np.abs(aims - (aims[j] + dx))))
            d = s[:, k] - s[:, j]
            return [float(d.mean()), float(d.std(ddof=1) / np.sqrt(len(d)))]
        ok = ev <= ev[j] + 0.005
        a, b = j, j
        while a > 0 and ok[a - 1]:
            a -= 1
        while b < len(aims) - 1 and ok[b + 1]:
            b += 1
        # parabola fit +/-6 yds: curvature (strokes per yd^2) and its vertex
        m = np.abs(aims - aims[j]) <= 6
        p2 = np.polyfit(aims[m], ev[m], 2)
        fine[c] = dict(engine_aim=a0, fine_aim=float(aims[j]), ev=float(ev[j]), ev_at_engine_aim=float(np.interp(a0, aims, ev)),
                       window=[float(aims[a]), float(aims[b])], vertex=float(-p2[1] / (2 * p2[0])), curv=float(p2[0]),
                       cost={str(dx): cost(dx) for dx in (-10, -5, -3, 3, 5, 10)})
        if c == base["pick"] or c == base["runner"]:
            evr, sr = big_curve(h, c, aims, P, rot=True)
            jr = int(np.argmin(evr))
            fine[c]["rot"] = dict(aim=float(aims[jr]), ev=float(evr[jr]), ev_at_fine_aim=float(evr[j]))
    r["fine"] = fine
    d = fine[base["runner"]]["ev"] - fine[base["pick"]]["ev"]
    r["fine_margin"] = d
    if "rot" in fine[base["runner"]]:
        r["rot_margin"] = fine[base["runner"]]["rot"]["ev"] - fine[base["pick"]]["rot"]["ev"]
    # (d) selection bias over independent swing sets (the page's wind-grid style: 3000 coarse + 16000 refine)
    reps = []
    for k in range(6):
        rr = solve(h, P, seed1=100 + k, seed2=200 + k)
        fresh = solve(h, P, seed2=300 + k, aim_fix={c: rr["clubs"][c]["aim"] for c in rr["clubs"]}, keep=True)
        reps.append(dict(pick=rr["pick"], aim=rr["aim"], ev_in=rr["clubs"][rr["pick"]]["ev"],
                         ev_fresh=fresh["clubs"][rr["pick"]]["ev"], margin_in=rr["margin"],
                         margin_fresh=fresh["clubs"][rr["runner"]]["ev"] - fresh["clubs"][rr["pick"]]["ev"]))
    r["reps"] = reps
    res[h] = r
    f = fine[base["pick"]]
    print(h, short(base), "| fine aim %+.2f window %s vertex %+.1f curv %.5f cost-5 %.4f +5 %.4f | rot aim %+.2f dEV %.4f | picks %s aim sd %.2f bias %.4f margin in %.4f fresh %.4f  %.0fs" % (
        f["fine_aim"], f["window"], f["vertex"], f["curv"], f["cost"]["-5"][0], f["cost"]["5"][0],
        f["rot"]["aim"], f["rot"]["ev"] - f["ev"],
        "".join(x["pick"][0] for x in reps), np.std([x["aim"] for x in reps]),
        np.mean([x["ev_fresh"] - x["ev_in"] for x in reps]), np.mean([x["margin_in"] for x in reps]),
        np.mean([x["margin_fresh"] for x in reps]), time.time() - t0), flush=True)
    json.dump({str(a): b for a, b in res.items()}, open(out, "w"), indent=0, default=float)
