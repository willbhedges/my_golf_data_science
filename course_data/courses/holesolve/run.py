"""holesolve validation runs (results/*.json; the tables of gateway_national/second_pass/HOLESOLVE.md).

  python3 course_data/courses/holesolve/run.py flat                         validation 1 (calibration)
  python3 course_data/courses/holesolve/run.py hole10 --which truth         validation 2 (Back; truth_middle = Middle)
  python3 course_data/courses/holesolve/run.py par5 --which truth           validation 3
  python3 course_data/courses/holesolve/run.py tee --which truth            validation 4 (all tee-shot holes)
  ... --tall lost    the lost-ball rule set for the tall grass     ... --tag X   suffix of the results file
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import solver as S                                                        # noqa: E402

OUT = os.path.join(HERE, "results")
SET_OF = {"truth": "Back", "truth_middle": "Middle"}


def dump(name, obj):
    os.makedirs(OUT, exist_ok=True)
    if isinstance(obj, dict):
        obj.setdefault("state", S.state())
    p = os.path.join(OUT, name)
    json.dump(obj, open(p, "w"), indent=1, default=lambda x: x.tolist() if hasattr(x, "tolist") else float(x))
    print("wrote", p)


def make_world(args):
    """--swings N / --grid G: resolution checks. --eased: an eased 4-wood (226 carry, 240 total, the 4-wood's width) joins the bag; --spread X: every shot that
    is not a tee shot X times wider and deeper (PAR5.md's sensitivity cases). The calibration is redone for the bag."""
    cfg = dict(S.CONFIG)
    if args.eased:
        clubs = {}
        for k, v in S.CONFIG["clubs"].items():
            clubs[k] = v
            if k == "4-wood":
                clubs["4-wood eased"] = (226, 240, 50, 24)
        cfg["clubs"] = clubs
    if args.swings:
        cfg["swings"] = args.swings
    if args.grid:
        cfg["grid_yds"] = args.grid
    W = S.World(args.slug, args.which, args.tall, cfg=cfg)
    if args.spread != 1.0:
        W.bag = S.Bag(W.M, W.P, cfg, spread=args.spread)
    return W


def level_cal(cal, lo=40.0, hi=200.0):
    """A level-only calibration: one constant per lie class, the mean of c between 40 and 200 yds. It lifts the
    model player to the table's level per shot without importing the table's value of distance."""
    m = (cal["d"] >= lo) & (cal["d"] <= hi)
    c = np.repeat(cal["c"][:, m].mean(1)[:, None], len(cal["d"]), axis=1)
    return dict(d=cal["d"], c=c)


def valuations(W, args):
    cal = W.calibration()
    allv = {"dp": cal, "dp_raw": None, "dp_level": level_cal(cal)}
    return {k: allv[k] for k in args.vals.split(",")}


# ------------------------------------------------------------------------------------------------ 1. flat hole
def flat(args):
    W = make_world(args)
    t = time.time()
    cal = W.calibration()
    t_cal = time.time() - t
    G = W.flat_ground()
    L = W.cfg["flat"]["length"]
    out = dict(config={k: v for k, v in W.cfg.items() if k != "clubs"}, clubs=W.cfg["clubs"],
               stock={n: [round(float(W.bag.stock[i, c]), 1) for i in range(3)] for c, n in enumerate(W.bag.names)},
               cal=dict(d=cal["d"], c=cal["c"], one_step=cal["one_step"], table=cal["table"]), secs_cal=round(t_cal, 2))
    spots = [("fairway", 0.0), ("rough", 25.0), ("sand", 0.0), ("fairway", 12.0), ("rough", 40.0)]
    ds = [30, 40, 50, 60, 80, 100, 125, 150, 175, 200, 225, 250, 275, 300, 350, 400, 450, 500, 550, 600]
    for name, c in (("raw", None), ("calibrated", cal)):
        hs = S.HoleSolve(G, W.bag, cal=c).solve()
        rows = []
        for d in ds:
            r = dict(d=d)
            for lie, lat in spots:
                if d <= lat + 5:
                    continue
                a = L - np.sqrt(d ** 2 - lat ** 2)
                v = hs.value_at(a, lat, lie)
                T = float(G.table(lie, d))
                r[f"{lie}@{lat:g}"] = [round(T, 3), round(v, 3), round(v - T, 3)]
            rows.append(r)
        # every state against the table
        T = hs.Tn[hs.st[:, 0], hs.st[:, 1], hs.st[:, 2]]
        inside = np.abs(hs.sl_) <= 60
        gap = (hs.V - T)[inside]
        out[name] = dict(rows=rows, states=len(hs.st), secs=round(hs.secs, 2), sweeps=hs.log,
                         all_states=dict(mean=float(gap.mean()), sd=float(gap.std()), min=float(gap.min()),
                                         max=float(gap.max()), p95_abs=float(np.percentile(np.abs(gap), 95))))
        print(f"\n{name}: {len(hs.st)} states, {hs.secs:.1f} s, sweeps {hs.log}")
        print("all states within 60 yds of the line, DP - table:", out[name]["all_states"])
        print("| yds | fairway table | DP | gap | rough table | DP | gap | sand table | DP | gap |")
        for r in rows:
            f, ro, sa = r["fairway@0"], r.get("rough@25"), r["sand@0"]
            rs = f"{ro[0]:.3f} | {ro[1]:.3f} | {ro[2]:+.3f}" if ro else " | | "
            print(f"| {r['d']} | {f[0]:.3f} | {f[1]:.3f} | {f[2]:+.3f} | {rs} | {sa[0]:.3f} | {sa[1]:.3f} | {sa[2]:+.3f} |")
    print("\ncalibration term c (strokes per shot): | yds | fairway | rough | sand |")
    for d in ds:
        i = int(np.argmin(np.abs(cal["d"] - d)))
        print(f"| {d} | {cal['c'][0, i]:+.3f} | {cal['c'][1, i]:+.3f} | {cal['c'][2, i]:+.3f} |")
    dump(f"flat{args.tag}.json", out)


# ------------------------------------------------------------------------------------------------ shared pieces
def tee_tables(W, h, hs_by, clubs=None):
    """The engine's two-stage tee solve on the table and on each DP's values. Returns {valuation: result}."""
    M = W.M
    R0 = next(iter(hs_by.values())).R0
    St = R0.strokes(W.P, M.HOLES[h]["length"])
    res = {"table": (W.tee_solve(h, R0, St, clubs=clubs), St)}
    for k, hs in hs_by.items():
        Sd = hs.tee_values(R0, St)
        res[k] = (W.tee_solve(h, R0, Sd, clubs=clubs), Sd)
    return R0, res


def slim(r):
    return dict(pick=r["pick"], aim=r["aim"], ev=round(r["ev"], 4), runner=r["runner"], margin=round(r["margin"], 4),
                se=round(r["se"], 4), clubs=r["clubs"])


def at_aim(W, h, R, S_by, club, aim, n=16000, seed=77):
    """One club at one aim, scored on several value rasters with the same swings: per-ball finish and values."""
    M = W.M
    z = W._eng["z"][1] if "z" in W._eng else M.draws_z(n, seed)
    out = {}
    for k, Sv in S_by.items():
        ev, (a, l, lie, s) = M.ev_curve(R, Sv, M.HOLES[h], club, W.P, z, np.array([float(aim)]))
        out[k] = dict(ev=float(ev[0]), a=a[:, 0], l=l[:, 0], lie=lie[:, 0], s=np.asarray(s)[:, 0])
    return out


# ------------------------------------------------------------------------------------------------ 2. hole 10
SPOTS10 = {"truth": [("Long iron", 212, 8), ("Mid iron", 184, 0), ("8-iron", 160, -3), ("4-wood", 259, 22)],
           "truth_middle": [("Long iron", 211, 17), ("Mid iron", 183, -2), ("8-iron", 160, -1), ("4-wood", 254, 31)]}


def hole10(args):
    W = make_world(args)
    M, h = W.M, 10
    cal = W.calibration()
    t = time.time()
    hs = {"dp": W.solve_hole(h, cal=cal), "dp_raw": W.solve_hole(h, cal=None)}
    secs = {k: round(v.secs, 1) for k, v in hs.items()}
    R0, res = tee_tables(W, h, hs)
    out = dict(set=SET_OF.get(args.which, args.which), tall=args.tall, temp_f=W.cfg["temp_f"], secs=secs,
               states=len(hs["dp"].st), sweeps=hs["dp"].log, green=hs["dp"].G.green,
               tee={k: slim(v[0]) for k, v in res.items()})
    irons = ("Long iron", "Mid iron", "8-iron")
    print(f"\nHole 10, {out['set']}, tall grass = {args.tall}; DP {secs} s, {out['states']} states")
    print("| valuation | go (best wood, aim) | strokes | " + " | ".join(irons) + " | go minus best lay-up |")
    for k, (r, _) in res.items():
        woods = [c for c in r["order"] if c in ("Driver", "2-wood", "4-wood")]
        go = woods[0]
        lay = min(irons, key=lambda c: r["clubs"][c]["ev"])
        out["tee"][k]["go_minus_layup"] = round(r["clubs"][go]["ev"] - r["clubs"][lay]["ev"], 4)
        out["tee"][k]["best_layup"] = lay
        print(f"| {k} | {go} {r['clubs'][go]['aim']:+.1f} | {r['clubs'][go]['ev']:.3f} | "
              + " | ".join(f"{r['clubs'][c]['ev']:.3f} ({r['clubs'][c]['aim']:+.1f})" for c in irons)
              + f" | {out['tee'][k]['go_minus_layup']:+.3f} ({lay}) |")
    # the lay-up spots of HOLE10_LAYUP.md: table value against the DP
    out["spots"] = []
    print("\n| lay-up ball at | to the hole | table | DP | DP raw | best club (DP) | on green | penalty |")
    for club, a, l in SPOTS10.get(args.which, []):
        q, qr = hs["dp"].query(a, l, "fairway"), hs["dp_raw"].query(a, l, "fairway")
        T = float(M.table("fairway", q["d"], W.P))
        b = q["rows"][0]
        out["spots"].append(dict(tee_club=club, a=a, l=l, d=q["d"], table=round(T, 3), dp=q["value"], dp_raw=qr["value"],
                                 rows=q["rows"][:5], rows_raw=qr["rows"][:5]))
        print(f"| {club} ({a}, {l:+d}) | {q['d']:.0f} | {T:.3f} | {q['value']:.3f} | {qr['value']:.3f} | {b['club']} | "
              f"{b['green']:.0%} | {b['penalty']:.1%} |")
    # dropped balls of the go club at the table's aim: the engine's value against the DP's
    go_r = res["table"][0]
    woods = [c for c in go_r["order"] if c in ("Driver", "2-wood", "4-wood")]
    out["drops"] = {}
    g = hs["dp"].G.green
    for club in woods[:2]:
        aim = go_r["clubs"][club]["aim"]
        b = at_aim(W, h, R0, {k: v[1] for k, v in res.items()}, club, aim)
        lie = b["table"]["lie"]
        a, l = b["table"]["a"], b["table"]["l"]
        pen = np.isin(lie, [M.CODE["water"], M.CODE["native"]])
        # which side of the tee-to-green line the ball finished, and short of the green or level with it
        side = l * g[0] - a * g[1]
        reg = {"right of the green line": pen & (side > 0) & (a > g[0] - 45),
               "left of the green line": pen & (side <= 0) & (a > g[0] - 45),
               "short (45+ yds short of the middle)": pen & (a <= g[0] - 45), "all dropped": pen, "dry": ~pen}
        rows = {}
        print(f"\n{club} at {aim:+.1f}: strokes after the tee shot (incl. the penalty stroke)")
        print("| where | share | engine table | DP | DP raw |")
        for nm, m in reg.items():
            if not m.any():
                continue
            rows[nm] = dict(share=round(float(m.mean()), 4), **{k: round(float(b[k]["s"][m].mean()), 3) for k in b})
            print(f"| {nm} | {m.mean():.1%} | {rows[nm]['table']:.2f} | {rows[nm]['dp']:.2f} | {rows[nm]['dp_raw']:.2f} |")
        out["drops"][club] = dict(aim=aim, rows=rows, ev={k: round(b[k]["ev"], 4) for k in b})
    dump(f"hole10_{out['set']}_{args.tall}{args.tag}.json", out)
    return out

# ------------------------------------------------------------------------------------------------ 3. par 5s
LAY_GAP = 20.0            # PAR5.md: a LAY-UP is a shot whose stock total stops 20+ yds short of the front edge
DRIVER_SPOT = {"truth": {6: (291, 6), 13: (294, 1), 18: (299, 13)}}     # PAR5.md, Back, Saturday


def front(G, a0, l0):
    """yds from (a0, l0) to the first point of the green on the line to its middle, and to the middle."""
    d = float(np.hypot(*(G.green - (a0, l0))))
    s = np.arange(0.0, d + 0.01, 0.25)
    u = (G.green - (a0, l0)) / d
    on = G.ongreen[G.idx(a0 + s * u[0], l0 + s * u[1])]
    return (float(s[np.argmax(on)]) if on.any() else d), d


def fairway_spot(G, d):
    """The middle of the strip of this hole's fairway d yds from the middle of the green (None: no fairway)."""
    C = G.M.CODE
    lo, hi = min(0.0, G.green[1]) - 65.0, max(0.0, G.green[1]) + 65.0   # this hole's corridor, not the next fairway
    m = ((np.abs(G.dist - d) <= 0.5) & (G.lie == C["fairway"]) & (G.R.AA < G.green[0]) & ~G.ongreen
         & (G.R.LL >= lo) & (G.R.LL <= hi))
    ia, il = np.nonzero(m)
    if not len(ia):
        return None
    a, l = G.R.a[ia], G.R.l[il]
    ang = np.degrees(np.arctan2(l - G.green[1], G.green[0] - a))        # bearing from the green back down the hole
    o = np.argsort(ang)
    ang, a, l = ang[o], a[o], l[o]
    gap_deg = np.degrees(2.5 / d)
    cuts = np.nonzero(np.diff(ang) > gap_deg)[0]
    runs = np.split(np.arange(len(ang)), cuts + 1)
    # the strip nearest the line of play (tee line to 270, then straight to the green); a 15-yd strip at least
    g = G.green

    def off_line(x):
        ma, ml = float(a[x].mean()), float(l[x].mean())
        if ma <= 270.0:
            return abs(ml)
        u = (g - (270.0, 0.0)) / np.hypot(*(g - (270.0, 0.0)))
        return abs((ma - 270.0) * u[1] - ml * u[0])
    wide = [x for x in runs if d * np.radians(ang[x[-1]] - ang[x[0]]) >= 15.0] or runs
    r = min(wide, key=off_line)
    mid = 0.5 * (ang[r[0]] + ang[r[-1]])
    j = r[int(np.argmin(np.abs(ang[r] - mid)))]
    return float(a[j]), float(l[j]), float(d * np.radians(ang[r[-1]] - ang[r[0]]))


def go_lay(hs, a, l, lie):
    q = hs.query(a, l, lie, all_clubs=True)
    df, dc = front(hs.G, a, l)
    best = {"go": None, "lay": None}
    for r in q["rows"]:
        r["kind"] = "lay" if r["stock"] <= df - LAY_GAP else "go"
        if best[r["kind"]] is None:
            best[r["kind"]] = r
    return dict(a=round(a, 1), l=round(l, 1), lie=lie, d=round(dc, 1), d_front=round(df, 1), value=q["value"],
                table=round(float(hs.G.table(lie, dc)), 4), go=best["go"], lay=best["lay"], rows=q["rows"])


def fmt_row(r):
    if r is None:
        return "none | | |"
    return f"{r['club']} {r['ang']:+.0f} deg | {r['strokes']:.3f} | leaves {r['leave']:.0f}, green {r['green']:.0%}, pen. {r['penalty']:.0%} |"


def par5(args):
    W = make_world(args)
    cal = W.calibration()
    holes = [int(x) for x in args.holes.split(",")] if args.holes else [6, 13, 18]
    out = dict(set=SET_OF.get(args.which, args.which), tall=args.tall, holes={})
    for h in holes:
        hs = {"dp": W.solve_hole(h, cal=cal), "dp_raw": W.solve_hole(h, cal=None)}
        G = hs["dp"].G
        R0, res = tee_tables(W, h, hs, clubs=["Driver", "2-wood", "4-wood"])
        o = dict(secs={k: round(v.secs, 1) for k, v in hs.items()}, states=len(hs["dp"].st), sweeps=hs["dp"].log,
                 green=G.green, tee={k: slim(v[0]) for k, v in res.items()}, ladder={}, spot={})
        print(f"\n=== hole {h} {out['set']}: {o['states']} states, DP {o['secs']} s")
        print("| valuation | Driver | 2-wood (vs Driver) | 4-wood (vs Driver) |")
        for k, (r, _) in res.items():
            c = r["clubs"]
            print(f"| {k} | {c['Driver']['ev']:.3f}, aim {c['Driver']['aim']:+.1f} | {c['2-wood']['ev']:.3f} "
                  f"({c['2-wood']['ev'] - c['Driver']['ev']:+.3f}) | {c['4-wood']['ev']:.3f} ({c['4-wood']['ev'] - c['Driver']['ev']:+.3f}) |")
        # where the table's Driver finishes (median of the fairway balls) and PAR5.md's spot
        dr = res["table"][0]["raw"]["Driver"]
        fw = dr["lie"] == W.M.CODE["fairway"]
        spots = {"driver_median": (float(np.median(dr["a"][fw])), float(np.median(dr["l"][fw])))}
        if h in DRIVER_SPOT.get(args.which, {}):
            spots["par5_md"] = tuple(float(x) for x in DRIVER_SPOT[args.which][h])
        for nm, (a, l) in spots.items():
            for lie in ("fairway", "rough"):
                for k in hs:
                    o["spot"][f"{nm}:{lie}:{k}"] = go_lay(hs[k], a, l, lie)
        print("\n| from | valuation | to front / middle | table | V | GO | strokes | | LAY-UP | strokes | | go - lay-up |")
        for key, g in o["spot"].items():
            dlt = (g["go"]["strokes"] - g["lay"]["strokes"]) if g["go"] and g["lay"] else float("nan")
            print(f"| {key} ({g['a']:.0f}, {g['l']:+.0f}) | | {g['d_front']:.0f} / {g['d']:.0f} | {g['table']:.3f} | {g['value']:.3f} | "
                  f"{fmt_row(g['go'])} {fmt_row(g['lay'])} {dlt:+.3f} |")
        # the ladder: every 10 yds from 150 to 340 on the fairway's middle, fairway lie and rough
        for lie in ("fairway", "rough"):
            for k in hs:
                rows = []
                for d in range(150, 341, 10):
                    sp = fairway_spot(G, d)
                    if sp is None:
                        continue
                    g = go_lay(hs[k], sp[0], sp[1], lie)
                    g["fairway_width"] = round(sp[2], 1)
                    g["rows"] = g["rows"][:6]
                    rows.append(g)
                o["ladder"][f"{lie}:{k}"] = rows
            print(f"\nladder, {lie} lie (calibrated DP | raw DP): best row, go - best lay-up")
            print("| yds to middle | spot | table | V | best | go - lay-up | lay-up leaves | raw: V | best | go - lay-up | lay-up leaves |")
            for gc, gr in zip(o["ladder"][f"{lie}:dp"], o["ladder"][f"{lie}:dp_raw"]):
                def cell(g):
                    b = g["rows"][0]
                    dl = f"{g['go']['strokes'] - g['lay']['strokes']:+.3f}" if g["go"] and g["lay"] else "no go"
                    lv = f"{g['lay']['club']} {g['lay']['leave']:.0f}" if g["lay"] else "-"
                    return f"{g['value']:.3f} | {b['kind']}: {b['club']} | {dl} | {lv}"
                print(f"| {gc['d']:.0f} | ({gc['a']:.0f}, {gc['l']:+.0f}) | {gc['table']:.3f} | {cell(gc)} | {cell(gr)} |")
        out["holes"][str(h)] = o
    dump(f"par5_{out['set']}_{args.tall}{args.tag}.json", out)


# ------------------------------------------------------------------------------------------------ 4. every tee shot
def tee(args):
    W = make_world(args)
    cals = valuations(W, args)
    k0 = next(iter(cals))
    holes = [int(x) for x in args.holes.split(",")] if args.holes else [k for k in W.course.ORDER if k in W.course.HOLES]
    pub = {}
    try:
        pub = json.load(open(os.path.join(S.COURSES, args.slug, args.which, "v2" if args.tall == "drop" else "v2_lost",
                                          "v2_decisions.json")))
    except Exception:                                                     # noqa: BLE001
        pass
    out = dict(set=SET_OF.get(args.which, args.which), tall=args.tall, temp_f=W.cfg["temp_f"], holes={})
    for h in holes:
        t = time.time()
        hs = {k: W.solve_hole(h, cal=c) for k, c in cals.items()}
        R0, res = tee_tables(W, h, hs)
        G = hs[k0].G
        o = dict(length=W.M.HOLES[h]["length"], secs={k: round(v.secs, 1) for k, v in hs.items()},
                 states=len(hs[k0].st), sweeps=len(hs[k0].log), tee={k: slim(v[0]) for k, v in res.items()},
                 total_secs=round(time.time() - t, 1))
        p = pub.get(str(h))
        if p:
            o["published"] = dict(pick=p["pick"], aim=p["aim"], ev=round(p["ev"], 4), margin=round(p["margin"], 4),
                                  runner=p["runner"], temp_f=round(p.get("temp_f", 0), 1))
        # the table's pick scored on the DP's values at the table's aim, and how the DP differs from the table
        tb = res["table"][0]
        b = at_aim(W, h, R0, {k: v[1] for k, v in res.items()}, tb["pick"], tb["aim"])
        lie = b["table"]["lie"]
        dry = ~np.isin(lie, [W.M.CODE["water"], W.M.CODE["native"], W.M.CODE["ob"]])
        o["pick_at_table_aim"] = dict(
            ev={k: round(b[k]["ev"], 4) for k in b}, penalty_share=round(float((~dry).mean()), 4),
            dry_delta=round(float((b[k0]["s"] - b["table"]["s"])[dry].mean()), 4) if dry.any() else None,
            pen_delta=round(float((b[k0]["s"] - b["table"]["s"])[~dry].mean()), 4) if (~dry).any() else None)
        dry_d = (b[k0]["s"] - b["table"]["s"])
        off = b["table"]["l"] - np.median(b["table"]["l"])
        o["pick_at_table_aim"]["dry_delta_by_side"] = {
            nm: round(float(dry_d[dry & m].mean()), 4) if (dry & m).any() else None
            for nm, m in (("left 10+", off < -10), ("middle", np.abs(off) <= 10), ("right 10+", off > 10))}
        o["delta_range"] = [round(float(hs[k0].delta.min()), 3), round(float(hs[k0].delta.max()), 3)]
        # DP minus table on this hole's own fairway states, by distance to the hole (how far the hole is from flat)
        o["fairway_delta"] = {}
        for k in hs:
            m = hs[k].st[:, 0] == 0
            ia, il = G.idx(hs[k].sa_[m], hs[k].sl_[m])
            own = (G.lie[ia, il] == W.M.CODE["fairway"]) & (np.abs(hs[k].sl_[m] - 0.5 * G.green[1]) <= 65 + 0.5 * abs(G.green[1]))
            d = hs[k].sd[m][own]
            dv = (hs[k].V[m] - hs[k].Tn[0][hs[k].st[m, 1], hs[k].st[m, 2]])[own]
            bins = np.arange(25, 476, 50)
            o["fairway_delta"][k] = {f"{int(b)}-{int(b + 50)}": [int(((d >= b) & (d < b + 50)).sum()),
                                                                round(float(dv[(d >= b) & (d < b + 50)].mean()), 4)]
                                     for b in bins if ((d >= b) & (d < b + 50)).any()}
        out["holes"][str(h)] = o
        r = res["table"][0]
        print(f"hole {h}: table {r['pick']} {r['aim']:+.1f} {r['ev']:.3f} m {r['margin']:.3f} vs {r['runner']} | "
              + " | ".join(f"{k} {res[k][0]['pick']} {res[k][0]['aim']:+.1f} {res[k][0]['ev']:.3f} m {res[k][0]['margin']:.3f} "
                           f"vs {res[k][0]['runner']}" for k in hs) + f" | {o['states']} states {o['secs']} s", flush=True)
        dump(f"tee_{out['set']}_{args.tall}{args.tag}.json", out)


# ------------------------------------------------------------------------------------------------ timings
def timing(args):
    """One calibrated solve per tee-shot hole and the engine's tee solve on it; load average recorded."""
    W = make_world(args)
    t = time.time()
    cal = W.calibration()
    out = dict(threads=os.environ.get("OMP_NUM_THREADS", "all"), cpus=os.cpu_count(), load_before=os.getloadavg()[0],
               calibration_secs=round(time.time() - t, 2), holes={})
    holes = [int(x) for x in args.holes.split(",")] if args.holes else [k for k in W.course.ORDER if k in W.course.HOLES]
    for h in holes:
        t = time.time()
        R0, G = W.ground(h)
        t_ras = time.time() - t
        hs = S.HoleSolve(G, W.bag, cal=cal).solve()
        t = time.time()
        St = R0.strokes(W.P, W.M.HOLES[h]["length"])
        W.tee_solve(h, R0, hs.tee_values(R0, St))
        out["holes"][str(h)] = dict(states=len(hs.st), sweeps=len(hs.log), raster_secs=round(t_ras, 2),
                                    dp_secs=round(hs.secs, 2), tee_solve_secs=round(time.time() - t, 2))
        print(h, out["holes"][str(h)], flush=True)
    out["load_after"] = os.getloadavg()[0]
    dump(f"timing{args.tag}.json", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["flat", "hole10", "par5", "tee", "timing"])
    ap.add_argument("--slug", default="gateway_national")
    ap.add_argument("--which", default="truth")
    ap.add_argument("--tall", default="drop", choices=["drop", "lost"])
    ap.add_argument("--holes", default="")
    ap.add_argument("--tag", default="")
    ap.add_argument("--eased", action="store_true")
    ap.add_argument("--swings", type=int, default=0)     # resolution checks: swings per club, state grid (yds)
    ap.add_argument("--grid", type=float, default=0.0)
    ap.add_argument("--vals", default="dp,dp_raw")       # tee: which valuations (dp, dp_raw, dp_level)
    ap.add_argument("--spread", type=float, default=1.0)
    args = ap.parse_args()
    globals()[args.cmd](args)


if __name__ == "__main__":
    main()
