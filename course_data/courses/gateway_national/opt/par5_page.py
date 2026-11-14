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
SUF = "_lost" if os.environ.get("P5_TALL_GRASS") == "lost" else ""     # the page's second rule set (par5_second.py)
OUT = os.path.join(HERE, "results" + SUF)
PAGE = os.path.join(GW, f"par5_second{SUF}.json")
SETS = ["The Tips", "Champions", "Back", "Middle", "Forward"]
BASE = {"Back": "Back", "The Tips": "Back", "Champions": "Back", "Middle": "Middle", "Forward": "Middle"}
PAR5 = (3, 6, 13, 18)
NAME = {"Long iron": "long iron", "Mid iron": "mid iron"}      # wedges stay PW / GW / SW
LEVEL = 0.03
# in-between shots (par5_second.GAP): not stock clubs; the first line that names one says what it is
GAP_WHAT = {"220 shot": "220 shot (a long iron hit hard)", "230 shot": "230 shot (a hybrid, not in your bag)",
            "240 shot": "240 shot (an easy 4-wood)"}


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
    c = GAP_WHAT.get(o["club"], nm(o["club"]))
    if kind == "go":
        if o["reach_total"] >= 0.5:
            t = f"Go: {c} {go_aim(o)}; {share(o['reach_carry'])} to the front edge"
        else:
            t = f"Get close: {c} {go_aim(o)}, a solid one finishes about {round(o['leave'])} short of the middle"
    else:
        t = f"Lay up: {c} ({round(o['stock'])} total) to {fw_words(o)}, leaves about {round(o['leave'] / 5) * 5}"
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
    ordinary = False
    # the best shot is an in-between one: the best with a club he carries, and what it costs
    bag_line = None
    if opts and opts[0][1]["club"] in GAP_WHAT:
        bo = sorted([(k, v.get(k + "_bag") or v[k]) for k in ("go", "lay") if v.get(k)], key=lambda t: t[1]["ev"])
        bo = [t for t in bo if t[1]["club"] not in GAP_WHAT]
        if bo:
            k, o = bo[0]
            d = o["ev"] - opts[0][1]["ev"]
            bag_line = f"With a club you carry: {short(k, o)}. " + ("About the same." if d < 0.02 else f"Costs {cost(d)}.")
            lines.insert(1, bag_line)
    # an ordinary approach (an iron reaches comfortably): the lay-up line says nothing
    # (0.75, was 0.9: since the Nov 14 anisotropic pattern more irons finish short, and 0.9 no longer held for a mid iron
    # from 186; with 0.75 the same spots are ordinary approaches as before)
    if go and go["reach_total"] >= 0.75 and go["club"] != "4-wood" and lay and lay["ev"] - go["ev"] > 0.2:
        lines = [option_line("go", go, True, None, None)] + ([bag_line] if bag_line else [])
        lay = None
        ordinary = True
    # the full-wedge lay-up, when the best lay-up leaves a part swing
    if lay and lay["leave"] < 72:
        cands = [x for x in v["by_club"] if x["kind"] == "lay" and x["club"] not in GAP_WHAT and 82 <= x["leave"] <= 112 and x["target_lie"] in ("fairway", "first_cut")]
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
    out = dict(club=pick, head=head, lines=lines, _ordinary=ordinary, _reach=bool(go),
               **{"from": [round(v["start"][0] - base_back, 1), v["start"][1]]})
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


MENU = os.path.join(GW, f"par5_menu{SUF}.json")
GAPS = tuple(GAP_WHAT)


def menu_lines(b, r, v, M, s):
    """The block's lines from the Second shot mode's own menu rows (par5_menu.json: same start, same numbers as the
    mode), leading with the best club he carries; an in-between shot is named second. M = the menu of this hole,
    base and day; None (Forward: no menu) keeps the lines of block()."""
    sp = (M or {}).get("spots", {}).get(s)
    if not sp:
        return
    pick = r["tee_pick_engine"]
    key = {"Driver": "D", "2-wood": "W"}.get(pick)
    if not key or key not in sp:
        return
    E = sp[key]["F"]
    rows = E["rows"]
    best = rows[0]
    bag = next((x for x in rows if x["c"] not in GAPS), None)
    if not bag:
        return
    lay = [x for x in rows if x["k"] == "l" and x["c"] not in GAPS]
    go = [x for x in rows if x["k"] == "g" and x["c"] not in GAPS]

    def aim(x):
        import math
        off = math.tan(math.radians(x["ax"])) * E["d"]
        return ("at the middle of the green" if abs(off) < 3 else f"at the {'left' if off < 0 else 'right'} half of the green"
                if abs(off) <= 14 else f"{round(abs(off))} yds {'left' if off < 0 else 'right'} of the middle of the green")

    def sh(pc):
        n = round(pc / 10)
        return "almost every ball carries" if pc >= 95 else "almost none carry" if pc <= 4 else f"{n} in 10 carry"

    def line(x):
        if x["k"] == "g" and x["rc"] >= 50:
            return f"Go: {nm(x['c'])} {aim(x)}; {sh(x['rc'])} to the front edge"
        if x["k"] == "g":
            return f"Get close: {nm(x['c'])} {aim(x)} ({x['tot']} total), leaves {x['lv']}"
        return f"Lay up: {nm(x['c'])} ({x['tot']} total), leaves {x['lv']}"

    def brief(x):
        return (f"{nm(x['c'])} at the green" if x["k"] == "g" and x["rc"] >= 50 else f"{nm(x['c'])}, leaves {x['lv']}" if x["k"] == "g"
                else f"lay up with the {nm(x['c'])}, leaves {x['lv']}")
    ordinary = b.get("_ordinary")
    other = (lay[0] if bag["k"] == "g" and lay else go[0] if bag["k"] == "l" and go else None)
    lines = [line(bag) + (f". Gains {cost(other['ev'] - bag['ev'])} strokes on {'laying up' if other['k'] == 'l' else 'going'}."
                          if other and not ordinary and other["ev"] - bag["ev"] >= 0.02 else ".")]
    if best["c"] in GAPS:
        d = bag["ev"] - best["ev"]
        lines.append(f"A {GAP_WHAT[best['c']]} would be " + ("about the same." if d < 0.015 else f"{cost(d)} better."))
    if other and not ordinary:
        d = other["ev"] - bag["ev"]
        lines.append(line(other) + (". About the same." if d < 0.02 else f". Costs {cost(d)}."))
    lay0 = lay[0] if lay and not ordinary else None
    if lay0 and lay0["lv"] < 72:                       # the full-wedge lay-up, when the best lay-up leaves a part swing
        c = [x for x in lay if 82 <= x["lv"] <= 112 and x["fw"] + x["ar"] >= 50]
        if c:
            x = min(c, key=lambda q: abs(q["lv"] - 95))
            lines.append(f"Full-wedge lay-up: {nm(x['c'])} ({x['tot']} total), leaves {x['lv']}. Costs {cost(x['ev'] - lay0['ev'])} more.")
    R = sp[key]["R"]["rows"]
    br = next((x for x in R if x["c"] not in GAPS), None)
    if br:
        lines.append(f"From the rough there: {brief(br)}.")
    if pick == "Driver" and "W" in sp:
        W = sp["W"]["F"]
        bw = next((x for x in W["rows"] if x["c"] not in GAPS), None)
        if bw:
            lines.append(f"After a 2-wood ({W['d'] - E['d']} yds further back, {W['d']} to the middle): {brief(bw)}.")
    b["lines"] = lines
    b["head"] = f"from the {pick}'s spot, about {E['d']} to the middle of the green ({E['f']} to the front edge):"
    if lay0:
        b["lay"] = [lay0["t"][0], lay0["t"][1]]
    else:
        b.pop("lay", None)
    b["_reach"] = bool(go) or bag["k"] == "g"


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
    who = "the 2-wood and 4-wood lose" if len(lv) == 2 else f"the {lv[0]} loses"
    return f"Only if you would never go for the green in two: {who} nothing off the tee" + (", same line" if same and len(lv) == 1 else "")


def main():
    holes = {}
    menu = json.load(open(MENU))["holes"] if os.path.exists(MENU) else {}
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
                # one source for the numbers: the Second shot mode's menu rows (Forward has no menu: block() lines)
                menu_lines(b, r, r["second"].get(r["tee_pick_engine"] + "|fairway"), menu.get(str(h), {}).get(BASE[s], {}).get(key), s)
                ts = (res.get(f"{h}|sat") or {}).get("two_stage")
                # the pill only where going for the green is a real option from the Driver's spot (never on hole 3:
                # the green is out of reach there, so "if you lay up anyway" is always true and the table already says it)
                # ... and only for Back and Middle: their tee re-check is re-run on the current pattern (PAR5.md); the
                # other sets' stored re-checks are from the first build
                pl = pill(ts) if b["club"] == "Driver" and b.get("lay") and b.get("_reach") and s in ("Back", "Middle") else None
                b.pop("_ordinary", None)
                b.pop("_reach", None)
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
