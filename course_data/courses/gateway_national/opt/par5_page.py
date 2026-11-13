"""Gateway par 5s: the page's "Second shot" block from the solver results (opt/results/par5_second_<set>.json,
written by par5_second.py solve + describe). Writes course_data/courses/gateway_national/par5_second.json
(config "par5_second"; read by v2_course.build_page, shown by the template under the club table).

  python3 course_data/courses/gateway_national/opt/par5_page.py [--md]

No hazard words in any text: targets are given by distance and side only.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GW = os.path.dirname(HERE)
OUT = os.path.join(HERE, "results")
PAGE = os.path.join(GW, "par5_second.json")
SETS = ["The Tips", "Champions", "Back", "Middle", "Forward"]
BASE = {"Back": "Back", "The Tips": "Back", "Champions": "Back", "Middle": "Middle", "Forward": "Middle"}
PAR5 = (3, 6, 13, 18)
NAME = {"Long iron": "long iron", "Mid iron": "mid iron"}      # wedges stay PW / GW / SW
LEVEL = 0.03


def nm(c):
    return NAME.get(c, c)


def side(x, unit="yds"):
    return f"{abs(round(x))} {unit} {'left' if x < 0 else 'right'}"


def go_aim(o):
    x = o["aim_at_green"]
    return "at the middle of the green" if abs(x) < 2.5 else f"at a spot {side(x)} of the middle of the green"


def fw_words(o):
    fw, tl = o.get("fw"), o["target"][1]
    if not fw or fw[1] - fw[0] < 8:
        return f"{side(tl)} of the tee line" if abs(tl) >= 2.5 else "on the tee line"
    f = (tl - fw[0]) / (fw[1] - fw[0])
    return ("the left half of the fairway" if f < 0.38 else "the right half of the fairway" if f > 0.62 else "the middle of the fairway")


def share(p):
    n = round(p * 10)
    return "almost every ball carries" if n >= 10 else "almost none carry" if n <= 0 else f"{n} in 10 carry"


def cost(d):
    return f"{abs(d):.2f}" if abs(d) < 0.095 else f"{abs(d):.1f}"


def option_line(kind, o, first, d, other):
    """One line for an option; d = its strokes minus the other option's (None when it is the only one)."""
    if kind == "go":
        if o["reach_total"] >= 0.5:
            t = f"Go: {nm(o['club'])} {go_aim(o)}; {share(o['reach_carry'])} to the front edge"
        else:
            t = f"Get close: {nm(o['club'])} {go_aim(o)}, a solid one finishes about {round(o['leave'])} short of the middle"
    else:
        t = f"Lay up: {nm(o['club'])} ({round(o['stock'])} total) to {fw_words(o)}, leaves about {round(o['leave'] / 5) * 5}"
    if d is None:
        return t + "."
    if abs(d) < 0.02:
        return t + (". About the same as " + other + "." if not first else ".")
    return t + (f". Gains {cost(d)} strokes on {other}." if first else f". Costs {cost(d)}.")


def best_of(v):
    opts = [(k, v[k]) for k in ("go", "lay") if v.get(k)]
    return sorted(opts, key=lambda t: t[1]["ev"])


def short(kind, o):
    if kind == "go" and o["reach_total"] >= 0.5:
        return f"{nm(o['club'])} at the green"
    if kind == "go":
        return f"{nm(o['club'])}, leaves about {round(o['leave'] / 5) * 5}"
    return f"lay up with the {nm(o['club'])}, leaves about {round(o['leave'] / 5) * 5}"


def block(r, base_back):
    pick = r["tee_pick_engine"]
    v = r["second"].get(pick + "|fairway")
    if not v:
        return None
    opts = best_of(v)
    lines = []
    for i, (kind, o) in enumerate(opts):
        if len(opts) == 1:
            lines.append(option_line(kind, o, True, None, None))
        else:
            ok, oo = opts[1 - i]
            other = ("laying up" if ok == "lay" else "going") if (ok == "lay" or oo["reach_total"] >= 0.5) else "the longer club"
            lines.append(option_line(kind, o, i == 0, o["ev"] - oo["ev"], other))
    go, lay = v.get("go"), v.get("lay")
    # an ordinary approach (an iron reaches comfortably): the lay-up line says nothing
    if go and go["reach_total"] >= 0.9 and go["club"] != "4-wood" and lay and lay["ev"] - go["ev"] > 0.2:
        lines = [option_line("go", go, True, None, None)]
        lay = None
    # the full-wedge lay-up, when the best lay-up leaves a part swing
    if lay and lay["leave"] < 72:
        cands = [x for x in v["by_club"] if x["kind"] == "lay" and 82 <= x["leave"] <= 112 and x["target_lie"] in ("fairway", "first_cut")]
        if cands:
            x = min(cands, key=lambda q: abs(q["leave"] - 95))
            lines.append(f"Full-wedge lay-up: {nm(x['club'])} ({round(x['stock'])}) to {fw_words(x)}, leaves about {round(x['leave'] / 5) * 5}. "
                         f"Costs {cost(x['ev'] - lay['ev'])} more.")
    vr = r["second"].get(pick + "|rough")
    if vr:
        k, o = best_of(vr)[0]
        lines.append(f"From the rough there: {short(k, o)}.")
    alt = None
    if pick == "Driver" and r["second"].get("2-wood|fairway"):
        w = r["second"]["2-wood|fairway"]
        k, o = best_of(w)[0]
        gap = round(v["start"][0] - w["start"][0])
        lines.append(f"After a 2-wood ({gap} yds further back, {round(w['d_ctr'])} to the middle): {short(k, o)}.")
        alt = [round(w["start"][0] - base_back, 1), w["start"][1]]
    head = f"from the {pick}'s spot, about {round(v['d_ctr'])} to the middle of the green ({round(v['d_front'])} to the front edge):"
    out = dict(club=pick, head=head, lines=lines, **{"from": [round(v["start"][0] - base_back, 1), v["start"][1]]})
    if lay:
        out["lay"] = [round(lay["target"][0] - base_back, 1), lay["target"][1]]
    if go and go["reach_total"] >= 0.5:
        # the marker = the aim point beside the middle of the green (a solid 4-wood can finish past it)
        g, st = r["green"], v["start"]
        ux, uy = (g[0] - st[0]) / v["d_ctr"], (g[1] - st[1]) / v["d_ctr"]
        out["go"] = [round(g[0] - uy * go["aim_at_green"] - base_back, 1), round(g[1] + ux * go["aim_at_green"], 1)]
    if alt:
        out["alt"], out["alt_label"] = alt, "2-WOOD"
    return out


def pill(ts):
    """The tee clubs under 'always lay up': level -> a pill."""
    if not ts:
        return None
    lay = ts["lay"]
    d2, d4 = lay["2-wood"]["vs_driver"], lay["4-wood"]["vs_driver"]
    lv = [c for c, d in (("2-wood", d2), ("4-wood", d4)) if d <= LEVEL]
    if not lv:
        return None
    same = abs(lay[lv[0]]["aim"] - lay["Driver"]["aim"]) <= 4
    who = "the 2-wood and 4-wood are" if len(lv) == 2 else f"the {lv[0]} is"
    return f"Laying up regardless: {who} just as good off the tee" + (", same line" if same and len(lv) == 1 else "")


def main():
    holes = {}
    for s in SETS:
        p = os.path.join(OUT, f"par5_second_{s.replace(' ', '_')}.json")
        if not os.path.exists(p):
            continue
        res = json.load(open(p))
        for h in PAR5:
            for day, key in (("sat", "d0"), ("sun", "d1")):
                r = res.get(f"{h}|{day}")
                if not r:
                    continue
                b = block(r, r["back"])
                if not b:
                    continue
                ts = (res.get(f"{h}|sat") or {}).get("two_stage")
                pl = pill(ts) if b["club"] == "Driver" and b.get("lay") else None
                if pl:
                    b["pill"] = pl
                holes.setdefault(str(h), {}).setdefault(s, {"base": BASE[s]})[key] = b
    json.dump(dict(source="opt/par5_second.py + opt/par5_page.py (PAR5.md)", holes=holes), open(PAGE, "w"), indent=1)
    for h, v in holes.items():
        for s, d in v.items():
            for k in ("d0", "d1"):
                if k in d:
                    print(f"--- {h} {s} {k}: {d[k]['head']}")
                    for ln in d[k]["lines"]:
                        print("    " + ln)
                    if d[k].get("pill"):
                        print("    PILL: " + d[k]["pill"])


if __name__ == "__main__":
    main()
