"""Gateway National par 3s: the DECADE edge rule as a hard constraint on the page target (PAR3.md section 0).

  OMP_NUM_THREADS=1 python3 course_data/courses/gateway_national/opt/par3_decade.py solve [--sets Back,...] [--holes 4,7]
  python3 course_data/courses/gateway_national/opt/par3_decade.py page      (rewrite par3_targets.json from results)
  python3 course_data/courses/gateway_national/opt/par3_decade.py table     (markdown tables for PAR3.md)

The rule (the golfer's statement of Scott Fawcett's DECADE approach rule, 2026-11-13):
  * base margin = 5 % of the plays-like distance, in yards, from EVERY part of the green edge (160 -> 8);
  * +3 where a penalty edge lies beyond that part of the green (water, OB, tall native = penalty area at Gateway);
  * +2 where trees do (the repo's earlier DECADE book, yardage_book.ADD; the golfer's statement does not name trees);
  * +2 for a greenside bunker (sand within 5 yds of the edge), +1 for a bunker 5-10 yds off; mown ground = base;
  * a hazard counts in full for a part of the edge when it begins within FULL = 5 yds of it, not at all from
    NEAR = 10 yds, linearly in between (penalty and trees; a bunker steps +2 / +1 / 0 at 5 and 10 yds);
  * lesser of two evils: when the margins do not all fit, the penalty margins are met first (the target moves away
    from the penalty edge even if that takes it inside the bunker / tree / plain margins; two penalty edges that
    conflict share the shortfall equally); then the worst shortfall on the other edges is made as small as it can
    be (the leftover room is centred between them, the bunker / tree side keeping its extra yards), except that
    expected strokes may buy shortfall back at TRADE = 0.01 strokes a yard (so the leftover leans toward the
    cheaper miss only where that is worth more than a hundredth of a stroke per yard given up);
  * among the points that satisfy the rule, the page target is the one with the best expected strokes (the par-3
    model of opt/par3_target.py, with penalty balls priced where they crossed the edge).
Checked on the green outline of opt/par3_green_check.json (the solve's outline cut back to the putting surface seen
on the 2023 photo: the smaller of the two on every side). The target is the centre of the blue box = the landing spot.

Writes opt/results/par3_decade.json and par3_targets.json (same shape as before; boxes are the target +/- 2 yds).
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

os.environ.setdefault("P3_FEATURES", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
GW = os.path.dirname(HERE)
_spec = importlib.util.spec_from_file_location("gw_par3", os.path.join(HERE, "par3_target.py"))
G = importlib.util.module_from_spec(_spec)
sys.modules["gw_par3"] = G
_spec.loader.exec_module(G)
E = G.E
RES = os.path.join(HERE, "results", "par3_decade.json")
PLAYS = os.path.join(HERE, "results", "par3_plays_forecast.json")
CHECK = os.path.join(HERE, "par3_green_check.json")
OLD = os.path.join(HERE, "results", "par3_targets_before_decade.json")

PCT = 0.05
NEAR = 10.0      # a hazard further than this from the green edge adds nothing
FULL = 5.0       # a hazard within this of the green edge adds its full modifier (linear in between)
ADD = {"penalty": 3.0, "trees": 2.0, "bunker2": 2.0, "bunker1": 1.0, "plain": 0.0}
RANK = ["penalty", "trees", "bunker", "plain"]          # lesser of two evils: satisfied in this order
# One target for every wind class of the page: the base margin already grows with the plays-like number. (The old
# DECADE book added 1 / 2 / 3 yds to every edge at 10-20 / 20-30 / 30+ mph; on these greens that does not fit, and the
# forecast is 4-9 mph.)
WIND_ADD = {-1: 0.0, 0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}
BOX_HALF = 2.0
TRADE = 0.01     # lesser of two evils: a yard of extra shortfall on the other edges is worth this many strokes
FLOOR = 4.0      # lesser of two evils never takes the target closer than this to any edge (the pin inset)
STEP = 0.5
WORD = {"penalty": "penalty", "trees": "trees", "bunker2": "bunker (greenside)", "bunker1": "bunker", "plain": "mown"}


def seg_dist(pts, a, b):
    ab = b - a
    u = np.clip(((pts - a) @ ab) / max(ab @ ab, 1e-9), 0, 1)
    return np.hypot(*(pts - (a + u[:, None] * ab)).T)


def boundary(poly, step=0.5):
    out = []
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        n = max(int(np.ceil(np.hypot(*(b - a)) / step)), 1)
        out.append(a + (b - a) * np.linspace(0, 1, n, endpoint=False)[:, None])
    return np.vstack(out)


def check_green(g, k):
    """The DECADE-check outline in this set's frame (yds right, yds past the centre)."""
    ll = np.asarray(json.load(open(CHECK))["holes"][str(k)]["polygon_ll"], float)
    o = np.asarray(g["to_ll"]([0.0, 1.0, 0.0], [0.0, 0.0, 1.0]), float)[:, :2]
    A = np.c_[o[1] - o[0], o[2] - o[0]]
    return np.linalg.solve(A, (ll - o[0]).T).T


def edge_classes(H, bpts):
    """Per boundary point: the hazard class beyond it and the distance to each hazard kind (yds)."""
    from scipy import ndimage as ndi
    C = E.C
    lie = H.lie
    d = {}
    for nm, codes in (("penalty", [C["native"], C["water"], C["ob"]]), ("trees", [C["recovery"]]), ("sand", [C["sand"]])):
        m = np.isin(lie, codes)
        d[nm] = ndi.distance_transform_edt(~m) * E.RES if m.any() else np.full(lie.shape, 999.0)
    i, j = H.idx(bpts[:, 0], bpts[:, 1])
    dp, dt, ds = d["penalty"][i, j], d["trees"][i, j], d["sand"][i, j]
    taper = lambda d: np.clip((NEAR - d) / (NEAR - FULL), 0.0, 1.0)      # noqa: E731
    add = np.maximum.reduce([ADD["penalty"] * taper(dp), ADD["trees"] * taper(dt),
                             np.where(ds <= FULL, ADD["bunker2"], np.where(ds <= NEAR, ADD["bunker1"], 0.0))])
    # the class names the hazard that sets the modifier; a penalty / tree edge is ranked as such from half its modifier
    cls = np.where(taper(dp) >= 0.5, "penalty", np.where(taper(dt) >= 0.5, "trees", np.where(ds <= FULL, "bunker2",
                   np.where(ds <= NEAR, "bunker1", "plain"))))
    return cls, dp, dt, ds, add


def rule(H, gc, base, wind_add=0.0):
    """Slack and per-class shortfall of every 0.5-yd grid point inside the check green."""
    from matplotlib.path import Path
    b = boundary(gc)
    cls, dp, dt, ds, add = edge_classes(H, b)
    req = base + wind_add + add
    lo, hi = gc.min(0), gc.max(0)
    la = np.arange(np.floor(lo[0]), np.ceil(hi[0]) + 1e-9, STEP)
    de = np.arange(np.floor(lo[1]), np.ceil(hi[1]) + 1e-9, STEP)
    L, D = np.meshgrid(la, de, indexing="ij")
    pts = np.c_[L.ravel(), D.ravel()]
    ins = Path(gc).contains_points(pts)
    dist = np.hypot(pts[:, None, 0] - b[None, :, 0], pts[:, None, 1] - b[None, :, 1])
    sl = dist - req[None, :]
    short = {}
    for r in RANK:
        m = np.array([c.startswith(r) for c in cls])
        short[r] = np.maximum(-sl[:, m].min(1), 0.0) if m.any() else np.zeros(len(pts))
    return dict(pts=pts, inside=ins, slack=sl.min(1), edge=dist.min(1), req_min=float(req.min()), short=short, b=b, cls=cls, req=req, dp=dp, dt=dt, ds=ds, la=la, de=de)


def choose(R, ev_at):
    """The DECADE target: feasible points -> best EV; otherwise lesser of two evils, then best EV."""
    cand = R["inside"].copy()
    how = "fits"
    extra = 0.0
    if not (cand & (R["slack"] >= -1e-9)).any():
        # the margins do not all fit. The penalty margins keep priority (shared equally where two penalty edges
        # conflict); the room left among the other edges is settled by expected strokes ("weighted toward the
        # cheaper miss"), never closer than FLOOR yds to any edge
        s = R["short"]["penalty"]
        best = s[cand].min()
        cand &= s <= best + 0.5
        o = np.maximum.reduce([R["short"][r] for r in RANK[1:]])
        worst = o[cand].min()
        if (cand & (R["edge"] >= FLOOR)).any():
            cand &= R["edge"] >= FLOOR
        extra = TRADE * np.maximum(o - worst, 0.0)
        how = "lesser of two evils: penalty margins " + ("met" if best <= 0.05 else f"short by {best:.1f} (two penalty edges)") + \
              f", the other edges short by {worst:.1f} at best"
    else:
        cand &= R["slack"] >= -1e-9
    ev = ev_at(R["pts"]) + (extra if how != "fits" else 0.0)
    ev = np.where(cand, ev, np.inf)
    i = int(ev.argmin())
    return R["pts"][i], how, i


def four_sides(R, t):
    """Edge distance left / right / short / long of the point (along its row and column), what is beyond, required."""
    from matplotlib.path import Path
    b, cls, req = R["b"], R["cls"], R["req"]
    out = {}
    for side, (ax, sg) in dict(left=(0, -1), right=(0, 1), short=(1, -1), long=(1, 1)).items():
        other = 1 - ax
        m = (np.abs(b[:, other] - t[other]) <= 0.6) & (sg * (b[:, ax] - t[ax]) > 0)
        if not m.any():
            out[side] = None
            continue
        idx = np.where(m)[0]
        j = idx[np.argmax(sg * (b[idx, ax] - t[ax]))]
        hz = cls[j]
        dh = {"penalty": R["dp"][j], "trees": R["dt"][j], "bunker2": R["ds"][j], "bunker1": R["ds"][j]}.get(hz)
        out[side] = dict(edge=round(float(abs(b[j, ax] - t[ax])), 1), beyond=hz, req=round(float(req[j]), 1),
                         hazard_off_edge=None if dh is None else round(float(dh), 1))
    d = np.hypot(*(b - t).T)
    j = int(np.argmin(d - req))
    k = int(np.argmin(d))
    out["tightest"] = dict(edge=round(float(d[j]), 1), req=round(float(req[j]), 1), beyond=cls[j],
                           at=[round(float(x), 1) for x in b[j]], slack=round(float(d[j] - req[j]), 1))
    out["nearest"] = dict(edge=round(float(d[k]), 1), req=round(float(req[k]), 1), beyond=cls[k],
                          at=[round(float(x), 1) for x in b[k]])
    return out


def solve(a):
    G.setup_engine()
    plays = json.load(open(PLAYS))
    old = json.load(open(OLD))["sets"]
    prev = json.load(open(RES)) if os.path.exists(RES) else {}
    res = {}
    lats = np.arange(-11.0, 11.0 + 1e-9, STEP)
    deps = np.arange(-15.0, 11.0 + 1e-9, STEP)
    cond = dict(temp=50.0, mph=0.0, rel=0.0)
    for s in a.sets.split(","):
        holes = G.load_holes(s)
        B = G.bearings(s)
        for k in [int(x) for x in a.holes.split(",")]:
            g = holes[k]
            H = E.Hole(g, E.opts())
            gc = check_green(g, k)
            z = E.draws(a.n, 31)
            cf = os.path.join(a.cache, f"surf_{s}_{k}_{a.n}.npy".replace(" ", "_")) if a.cache else None
            if cf and os.path.exists(cf):
                m = np.load(cf)
            else:
                m = E.solve_surface_z(H, cond, E.opts(), z, lats, deps).mean(2)        # lats x deps
                if cf:
                    np.save(cf, m)

            def ij(p):
                return int(round((p[0] - lats[0]) / STEP)), int(round((p[1] - deps[0]) / STEP))

            def ev_at(pts, m=m):
                i = np.clip(np.rint((pts[:, 0] - lats[0]) / STEP).astype(int), 0, len(lats) - 1)
                j = np.clip(np.rint((pts[:, 1] - deps[0]) / STEP).astype(int), 0, len(deps) - 1)
                return m[i, j]
            iu, ju = np.unravel_index(int(m.argmin()), m.shape)
            uncon = [float(lats[iu]), float(deps[ju])]
            pc = plays[s][str(k)]                      # plays-like to the green centre, worst forecast state
            o_aim = old[s][str(k)]["boxes"]["0"]["aim"]
            out = dict(card=G.card(s)[k], map_center=H.center, plays_centre=pc, old=o_aim, uncon=uncon, mods={})
            for mod in (0,):
                # the base margin follows the target depth (plays-like to the target = to the centre + depth)
                t = np.array(o_aim, float)
                for _ in range(3):
                    base = PCT * (pc["max"] + t[1])
                    R = rule(H, gc, base, WIND_ADD[mod])
                    t, how, _i = choose(R, ev_at)
                fs = four_sides(R, t)
                d = dict(target=[float(t[0]), float(t[1])], how=how, base=round(base, 2), sides=fs,
                         feasible_area=round(float((R["inside"] & (R["slack"] >= 0)).sum() * STEP * STEP), 1))
                if mod == 0:
                    Ro = rule(H, gc, PCT * (pc["max"] + o_aim[1]), 0.0)
                    out["old_sides"] = four_sides(Ro, np.array(o_aim, float))
                    out["old_base"] = round(PCT * (pc["max"] + o_aim[1]), 2)
                    Ru = rule(H, gc, PCT * (pc["max"] + uncon[1]), 0.0)
                    out["uncon_sides"] = four_sides(Ru, np.array(uncon, float))
                    io, iuu, it = ij(o_aim), (iu, ju), ij(t)
                    L2, D2 = sorted({o_aim[0], uncon[0], float(t[0])}), sorted({o_aim[1], uncon[1], float(t[1])})
                    v = E.solve_surface_z(H, cond, E.opts(), z, np.array(L2), np.array(D2))
                    pair = lambda p, q: [round(x, 4) for x in E.paired(v[L2.index(lats[p[0]]), D2.index(deps[p[1]]), :],   # noqa: E731
                                                                       v[L2.index(lats[q[0]]), D2.index(deps[q[1]]), :])]
                    out["ev"] = dict(old=round(float(m[io]), 4), uncon=round(float(m[iuu]), 4), decade=round(float(m[it]), 4),
                                     centre=round(float(m[ij((0.0, 0.0))]), 4),
                                     decade_minus_uncon=pair(it, iuu), decade_minus_old=pair(it, io), old_minus_uncon=pair(io, iuu))
                    # the old pricing (penalty at the ball's own distance) on the same swings, for the "why"
                    os.environ["P3_PENALTY"] = "ball"
                    H0 = E.Hole(g, E.opts())
                    del os.environ["P3_PENALTY"]
                    v0 = E.solve_surface_z(H0, cond, E.opts(), z, np.array(L2), np.array(D2))
                    at0 = lambda p: v0[L2.index(p[0]), D2.index(p[1]), :]      # noqa: E731
                    out["ev_old_pricing"] = dict(old=round(float(at0(o_aim).mean()), 4), uncon=round(float(at0(uncon).mean()), 4),
                                                 decade=round(float(at0([float(t[0]), float(t[1])]).mean()), 4))
                    out["green_check"] = dict(lat=[round(float(gc[:, 0].min()), 1), round(float(gc[:, 0].max()), 1)],
                                              dep=[round(float(gc[:, 1].min()), 1), round(float(gc[:, 1].max()), 1)])
                    # clubs at stock carry for the forecast days (the page's fallback club line; the ladder is live)
                    if a.cache and (prev.get(f"{s} {k}") or {}).get("clubs"):
                        out["clubs"] = prev[f"{s} {k}"]["clubs"]
                    else:
                        G.CUR["hole"] = k
                        conds = G.conditions(None, B[k])
                        cl = {}
                        for nm, c in conds.items():
                            ce = G.club_eval(H, c, E.opts(), E.draws(8000, 18), np.arange(-12.0, 12.0 + 1e-9, 1.0))
                            order = sorted(ce, key=lambda c_: ce[c_]["ev"])
                            dd, se = E.paired(ce[order[1]]["per"], ce[order[0]]["per"])
                            cl[nm] = dict(pick=E.SHORT_NAME.get(order[0], order[0]), runner=E.SHORT_NAME.get(order[1], order[1]),
                                          tie=bool(dd < 2 * se or dd < 0.01), margin=round(float(dd), 4))
                        out["clubs"] = cl
                out["mods"][str(mod)] = d
            for mod in (-1, 1, 2, 3):
                out["mods"][str(mod)] = out["mods"]["0"]
            out["green_check"]["poly"] = [[round(float(x), 1), round(float(y), 1)] for x, y in gc]
            res[f"{s} {k}"] = out
            m0 = out["mods"]["0"]
            print(s, k, "old", o_aim, "uncon", uncon, "decade", m0["target"], m0["how"], "base", m0["base"],
                  "cost", out["ev"]["decade_minus_uncon"], "tight", m0["sides"]["tightest"], file=sys.stderr, flush=True)
            G.merge_json(RES, {f"{s} {k}": out})
    write_page()


def write_page():
    res = json.load(open(RES))
    page = {"source": "course_data/courses/gateway_national/opt/par3_decade.py (PAR3.md section 0): the DECADE edge "
                      "rule as a constraint, best expected strokes inside it", "sets": {}}
    for key, r in sorted(res.items()):
        s, k = key.rsplit(" ", 1)
        boxes = {}
        for mod in (-1, 0, 1, 2, 3):
            t = r["mods"][str(mod)]["target"]
            sm = r["mods"][str(mod)]["sides"]
            boxes[str(mod)] = dict(aim=t, lat=[t[0] - BOX_HALF, t[0] + BOX_HALF], dep=[t[1] - BOX_HALF, t[1] + BOX_HALF],
                                   m={x: sm[x]["edge"] for x in ("left", "right", "short", "long") if sm[x]})
        sd = r["mods"]["0"]["sides"]
        page["sets"].setdefault(s, {})[k] = dict(
            boxes=boxes, clubs=r["clubs"],
            margins={x: (sd[x]["edge"] if sd[x] else None) for x in ("left", "right", "short", "long")},
            required={x: (sd[x]["req"] if sd[x] else None) for x in ("left", "right", "short", "long")},
            decade=r["mods"]["0"]["how"], cost_vs_unconstrained=r["ev"]["decade_minus_uncon"],
            green=r["green_check"]["poly"])
    json.dump(page, open(G.PAGE, "w"), indent=1)
    print("wrote", G.PAGE, file=sys.stderr)


def table(_a):
    res = json.load(open(RES))
    f = lambda p: f"({p[0]:+.1f}, {p[1]:+.1f})"      # noqa: E731

    def sd(x):
        return "-" if not x else f"{x['edge']:.0f} / {x['req']:.1f} {WORD[x['beyond']]}"
    print("| set | hole | plays (max) | base | old target | old: tightest edge (have / need) | new model's free optimum | DECADE target | left | right | short | long | tightest | how | cost vs free optimum |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s in G.SETS:
        for k in G.HOLES3:
            r = res.get(f"{s} {k}")
            if not r:
                continue
            m = r["mods"]["0"]
            S, o = m["sides"], r["old_sides"]["tightest"]
            c = r["ev"]["decade_minus_uncon"]
            print(f"| {s} | {k} | {r['plays_centre']['max'] + m['target'][1]:.0f} | {m['base']:.1f} | {f(r['old'])} | "
                  f"{o['edge']:.1f} / {o['req']:.1f} {WORD[o['beyond']]} {'ok' if o['slack'] >= 0 else '**FAIL %.1f**' % -o['slack']} | "
                  f"{f(r['uncon'])} | **{f(m['target'])}** | {sd(S['left'])} | {sd(S['right'])} | {sd(S['short'])} | {sd(S['long'])} | "
                  f"{S['tightest']['edge']:.1f} / {S['tightest']['req']:.1f} {WORD[S['tightest']['beyond']]} | {m['how']} | {c[0]:+.3f} +/- {c[1]:.3f} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["solve", "page", "table"])
    ap.add_argument("--sets", default=",".join(G.SETS))
    ap.add_argument("--holes", default="4,7,12,14,17")
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--cache", default="", help="directory for the expected-strokes surfaces (re-runs of the rule)")
    a = ap.parse_args()
    {"solve": solve, "page": lambda _a: write_page(), "table": table}[a.cmd](a)


if __name__ == "__main__":
    main()
