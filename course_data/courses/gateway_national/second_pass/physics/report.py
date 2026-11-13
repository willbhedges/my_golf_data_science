"""Markdown tables for ../PHYSICS.md from results/compare.json and results/reference.json (python3 report.py)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(HERE, "results", "compare.json")))
REF = json.load(open(os.path.join(HERE, "results", "reference.json")))
TEE = ["Driver", "2-wood", "4-wood", "Long iron", "Mid iron", "8-iron"]


def calib():
    print("| club | 70 F carry | ball speed mph | launch deg | spin rpm | apex yds | landing angle | landing speed mph | spin at landing | flight s |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for c, d in REF["fit"]["clubs"].items():
        print(f"| {c} | {d['carry']:.0f} | {d['ball_mph']:.0f} | {d['launch']} | {d['spin']} | {d['apex_yds']:.0f} | {d['land_deg']:.0f} | "
              f"{d['v_land_mph']:.0f} | {d['spin_land']} | {d['time']:.1f} |")


def temp():
    print("| club | engine 45 F (k 0.00075) | ref air only: fit / linear / smits | ref air + ball at 45 F (ball k 0.0002 .. 0.0007) | engine 35 F | ref air+ball 35 F |")
    print("|---|---|---|---|---|---|")
    for c in TEE:
        e, r = C["generic"][c]["engine"], C["generic"][c]["ref"]
        t = r["temp"]["45"]
        print(f"| {c} | {e['temp']['45']:+.1f} | {t['air']['fit']:+.1f} / {t['air']['linear']:+.1f} / {t['air']['smits']:+.1f} | "
              f"**{t['air_ball']:+.1f}** ({t['ball_lo']:+.1f} .. {t['ball_hi']:+.1f}) | {e['temp']['35']:+.1f} | {r['temp']['35']['air_ball']:+.1f} |")


def wind():
    for s in ("5", "10", "15"):
        print(f"\n**{s} mph** (carry yds: head / tail; drift yds for a pure crosswind)\n")
        print("| club | engine head / tail | ref fit, 10 m log profile | ref fit, uniform | linear / smits (log) head | engine drift | ref drift: fit log / fit uniform / linear / smits |")
        print("|---|---|---|---|---|---|---|")
        for c in TEE:
            e, r = C["generic"][c]["engine"]["wind"][s], C["generic"][c]["ref"]["wind"][s]
            print(f"| {c} | {e['head']:+.1f} / {e['tail']:+.1f} | {r['fit']['head']:+.1f} / {r['fit']['tail']:+.1f} | "
                  f"{r['uniform']['head']:+.1f} / {r['uniform']['tail']:+.1f} | {r['linear']['head']:+.1f} / {r['smits']['head']:+.1f} | "
                  f"{e['drift']:.1f} | **{r['fit']['drift']:.1f}** / {r['uniform']['drift']:.1f} / {r['linear']['drift']:.1f} / {r['smits']['drift']:.1f} |")


def par3():
    print("| hole (card) | day | at the tee | head / cross mph | page now (elev / wind / temp) | patched, warm ball | patched, ball at air temp | **+ pressure** | change | reference model (warm / cold / cold + pressure) | drift: page / patched / reference |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for h, p in C["par3"].items():
        for d, v in p["days"].items():
            pp = v["page_parts"]
            print(f"| {h} ({p['card']}) | {d} | {v['temp']:.0f} F, {v['mph']:.1f} mph from {v['wind_from']:.0f} | {v['head']:+.1f} / {v['cross']:+.1f} | "
                  f"{v['page']:.0f} ({pp['elev']:+.1f} / {pp['wind']:+.1f} / {pp['temp']:+.1f}) | {v['patched_warm']:.0f} | {v['patched_cold']:.0f} | "
                  f"**{v['patched_cold_pressure']:.0f}** | {v['patched_cold_pressure'] - v['page']:+.1f} | {v['ref_warm']:.0f} / {v['ref_cold']:.0f} / {v['ref_cold_pressure']:.0f} | "
                  f"{v['page_drift']:+.1f} / {v['patched_drift']:+.1f} / {v['ref_drift']:+.1f} |")


def tee(club="Driver"):
    print(f"| hole | day | F | head / cross mph | engine carry / total / drift | patched (cold ball + pressure) | change carry / drift | reference carry / drift |")
    print("|---|---|---|---|---|---|---|---|")
    for h, p in C["tee"].items():
        for d, v in p["days"].items():
            k = v["clubs"][club]
            e, q, r = k["engine"], k["patched_cold_pressure"], k["ref_cold_pressure"]
            print(f"| {h} | {d} | {v['temp']:.0f} | {v['head']:+.1f} / {v['cross']:+.1f} | {e['carry']:.0f} / {e['total']:.0f} / {e['drift']:+.1f} | "
                  f"{q['carry']:.0f} / {q['total']:.0f} / {q['drift']:+.1f} | {q['carry'] - e['carry']:+.1f} / {abs(q['drift']) - abs(e['drift']):+.1f} | "
                  f"{r['carry']:.0f} / {r['drift']:+.1f} |")


def tee_summary():
    print("| club | patched - engine carry: mean (min .. max) | patched - engine drift, yds further: mean (max) | reference - engine carry | reference - patched carry |")
    print("|---|---|---|---|---|")
    for c in TEE:
        a, b, e, dd = [], [], [], []
        for h, p in C["tee"].items():
            for d, v in p["days"].items():
                k = v["clubs"][c]
                a.append(k["ref_cold_pressure"]["carry"] - k["engine"]["carry"])
                b.append(k["ref_cold_pressure"]["carry"] - k["patched_cold_pressure"]["carry"])
                e.append(k["patched_cold_pressure"]["carry"] - k["engine"]["carry"])
                dd.append(abs(k["patched_cold_pressure"]["drift"]) - abs(k["engine"]["drift"]))
        m = lambda x: sum(x) / len(x)
        print(f"| {c} | {m(e):+.1f} ({min(e):+.1f} .. {max(e):+.1f}) | {m(dd):+.1f} ({max(dd):+.1f}) | {m(a):+.1f} ({min(a):+.1f} .. {max(a):+.1f}) | {m(b):+.1f} ({min(b):+.1f} .. {max(b):+.1f}) |")


def misc():
    print("| club | 10 ft drop / rise: ref carry | 5 mph head: landing angle, curvature x | 10 mph head / tail landing angle | curvature x at 10 mph head / tail (engine width x) | roll model: firm / normal / soft at 70 F | same at 45 F |")
    print("|---|---|---|---|---|---|---|")
    for c in TEE:
        e, r = C["generic"][c]["engine"], C["generic"][c]["ref"]
        w5, w10 = r["wind"]["5"], r["wind"]["10"]
        print(f"| {c} | {r['elev']['10']:+.1f} / {r['elev']['-10']:+.1f} | {w5['head_land']:.0f} deg, x{w5['curve_head']:.2f} | {w10['head_land']:.0f} / {w10['tail_land']:.0f} "
              f"(calm {r['calm70']['land']:.0f}) | x{w10['curve_head']:.2f} / x{w10['curve_tail']:.2f} (x{e['wind']['10']['head_width']:.2f} / x{e['wind']['10']['tail_width']:.2f}) | "
              f"{r['turf']['fairway_firm']:.0f} / {r['turf']['fairway_normal']:.0f} / {r['turf']['fairway_soft']:.0f} | "
              f"{r['turf45']['fairway_firm']:.0f} / {r['turf45']['fairway_normal']:.0f} / {r['turf45']['fairway_soft']:.0f} |")


if __name__ == "__main__":
    for f in (calib, temp, wind, par3, tee, tee_summary, misc):
        print(f"\n<!-- {f.__name__} -->\n")
        f()
