"""Tables of gateway_national/second_pass/HOLESOLVE.md from results/*.json (prints markdown).

  python3 course_data/courses/holesolve/report.py tee [--set Back] [--tall drop]
  python3 course_data/courses/holesolve/report.py flat
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
SHORT = {"Driver": "Driver", "2-wood": "2-wood", "4-wood": "4-wood", "Long iron": "long iron", "Mid iron": "mid iron",
         "8-iron": "8-iron"}


def load_tee(set_name="Back", tall="drop", tag=""):
    holes = {}
    for p in sorted(glob.glob(os.path.join(OUT, f"tee_{set_name}_{tall}{tag or '_*'}.json"))):
        if not tag and any(x in os.path.basename(p) for x in ("_eased", "_spread", "_time", "_level", "_check")):
            continue
        holes.update(json.load(open(p))["holes"])
    return dict(sorted(holes.items(), key=lambda kv: int(kv[0])))


def side(a):
    return f"{abs(a):.1f} {'L' if a < 0 else 'R'}" if abs(a) >= 0.25 else "line"


def tee(set_name="Back", tall="drop", tag=""):
    H = load_tee(set_name, tall, tag)
    print("| hole | published book (forecast temp) | table, calm 45 F | margin | DP, calm 45 F | margin | DP - table, "
          "strokes | margin change | raw DP | margin |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for h, o in H.items():
        t, d, r, p = o["tee"]["table"], o["tee"]["dp"], o["tee"]["dp_raw"], o.get("published")
        ps = f"{p['pick']} {side(p['aim'])}, {p['margin']:.3f} ({p['temp_f']:.0f} F)" if p else "-"
        flag = "**" if d["pick"] != t["pick"] else ""
        print(f"| {h} ({o['length']:.0f}) | {ps} | {t['pick']} {side(t['aim'])}, {t['ev']:.3f} | {t['margin']:.3f} vs {SHORT[t['runner']]} | "
              f"{flag}{d['pick']} {side(d['aim'])}{flag}, {d['ev']:.3f} | {d['margin']:.3f} vs {SHORT[d['runner']]} | "
              f"{d['clubs'][d['pick']]['ev'] - t['clubs'][t['pick']]['ev']:+.3f} | "
              f"{(d['margin'] - t['margin']) if d['pick'] == t['pick'] else float('nan'):+.3f} | "
              f"{r['pick']} {side(r['aim'])}, {r['ev']:.3f} | {r['margin']:.3f} vs {SHORT[r['runner']]} |")
    L = load_tee(set_name, tall, "_level*") if not tag else {}
    if L:
        print("\nLevel-only calibration (one constant per lie; the model's own value of distance):\n")
        print("| hole | table | margin | calibrated DP | margin | level-only DP | margin | raw DP | margin |")
        print("|---|---|---|---|---|---|---|---|---|")
        for h, o in H.items():
            if h not in L:
                continue
            cells = []
            for v in (o["tee"]["table"], o["tee"]["dp"], L[h]["tee"]["dp_level"], o["tee"]["dp_raw"]):
                cells.append(f"{v['pick']} {side(v['aim'])} | {v['margin']:.3f} vs {SHORT[v['runner']]}")
            print(f"| {h} | " + " | ".join(cells) + " |")
    print("\nEvery club, strokes behind the valuation's best (table / DP / raw DP):\n")
    clubs = ["Driver", "2-wood", "4-wood", "Long iron", "Mid iron", "8-iron"]
    print("| hole | " + " | ".join(clubs) + " |")
    print("|---|" + "---|" * len(clubs))
    for h, o in H.items():
        cells = []
        for c in clubs:
            x = []
            for k in ("table", "dp", "dp_raw"):
                v = o["tee"][k]
                x.append(f"{v['clubs'][c]['ev'] - v['ev']:.3f}" if c in v["clubs"] else "-")
            cells.append(" / ".join(x))
        print(f"| {h} | " + " | ".join(cells) + " |")
    print("\nThe table's pick at the table's aim, scored on the DP (same 16,000 swings):\n")
    print("| hole | penalty balls | dry balls: DP - table (left 10+ / middle / right 10+ of the pattern) | penalty balls: DP - table | all: DP - table | this hole's fairway, DP - table by yds to the hole |")
    print("|---|---|---|---|---|---|")
    for h, o in H.items():
        q = o["pick_at_table_aim"]
        fd = o["fairway_delta"]["dp"]
        fds = ", ".join(f"{k}: {v[1]:+.2f}" for k, v in fd.items() if v[0] >= 20)
        pd = f"{q['pen_delta']:+.3f}" if q["pen_delta"] is not None else "-"
        bs = q.get("dry_delta_by_side") or {}
        bss = " (" + " / ".join(f"{bs[k]:+.3f}" if bs.get(k) is not None else "-" for k in ("left 10+", "middle", "right 10+")) + ")" if bs else ""
        print(f"| {h} | {q['penalty_share']:.1%} | {q['dry_delta']:+.3f}{bss} | {pd} | {q['ev']['dp'] - q['ev']['table']:+.3f} | {fds} |")
    print("\n| hole | states | calibrated DP, s | raw DP, s | sweeps |")
    print("|---|---|---|---|---|")
    for h, o in H.items():
        print(f"| {h} | {o['states']} | {o['secs']['dp']} | {o['secs']['dp_raw']} | {o['sweeps']} |")


def flat():
    d = json.load(open(os.path.join(OUT, "flat.json")))
    for name in ("raw", "calibrated"):
        print(f"\n{name}: {d[name]['states']} states, {d[name]['secs']} s; every state within 60 yds of the line: {d[name]['all_states']}")
        print("| yds | fairway: table | DP | gap | rough: table | DP | gap | sand: table | DP | gap |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for r in d[name]["rows"]:
            f, ro, sa = r["fairway@0"], r.get("rough@25"), r["sand@0"]
            rs = f"{ro[0]:.2f} | {ro[1]:.2f} | {ro[2]:+.3f}" if ro else " | | "
            print(f"| {r['d']} | {f[0]:.2f} | {f[1]:.2f} | {f[2]:+.3f} | {rs} | {sa[0]:.2f} | {sa[1]:.2f} | {sa[2]:+.3f} |")
    import numpy as np
    c, dd = np.array(d["cal"]["c"]), np.array(d["cal"]["d"])
    print("\n| yds | c fairway | c rough | c sand |")
    print("|---|---|---|---|")
    for x in (30, 40, 50, 60, 80, 100, 125, 150, 175, 200, 225, 250, 275, 300, 350, 400, 450, 500, 550, 600):
        i = int(np.argmin(np.abs(dd - x)))
        print(f"| {x} | {c[0, i]:+.3f} | {c[1, i]:+.3f} | {c[2, i]:+.3f} |")


if __name__ == "__main__":
    a = sys.argv[1:]
    kw = {}
    for k in ("--set", "--tall", "--tag"):
        if k in a:
            kw[{"--set": "set_name", "--tall": "tall", "--tag": "tag"}[k]] = a[a.index(k) + 1]
    if a[0] == "tee":
        tee(**kw)
    else:
        flat()
