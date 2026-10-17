"""REPORT.md for the second-shot plan (rendered from output/approach.json by build.py)."""

EVIDENCE = """\
## Evidence used

| Topic | Number used | Source |
|---|---|---|
| Approach dispersion, 5 hcp | lateral sigma 7.0 yd at 100, 9.4 at 150, 13.4 at 200 (about 6-7% of distance); depth sigma 1.5x lateral | Fitted so the mean proximity from the fairway is ~33 ft at 100, ~45 ft at 150 and ~64 ft at 200 (model output). Anchors: Broadie (fairway, 150 yd, half of shots within): best pros 21 ft, average pros 23 ft, 80-shooters 42 ft, 90-shooters 56 ft. Stagner/Arccos: scratch ~37 ft from 150. A 5 index from ~100 yd matches scratch from 150. Golf Digest: scratch 80+ ft from 200-225 ([golfdigest](https://www.golfdigest.com/story/statistics-pros-better-than-scratch-golfers-how-do-you-compare), [practical-golf](https://practical-golf.com/golf-iron-distances), research.md section 2). |
| Pattern shape | Depth = 1.5x width, unbiased centre | Broadie, via [golfcoursewiki](https://golfcoursewiki.substack.com/p/how-to-bake-a-dispersion-pattern-from-scratch): 90-shooters' 150-yd pattern is 50% longer than it is wide, with the centre ~13 yd short. The plan assumes you club to the middle of the box, i.e. no short bias. If you do come up short, play one more club. |
| Lie effect | Lateral x / depth x: first cut 1.08 / 1.12, rough 1.2 / 1.35, fairway sand 1.4 / 1.5; reach 265 fw, 260 cut, 235 rough, 190 sand | Stagner: "scratch 90 fw = 67 rough; 10 hcp 160 fw = 140 rough", and fairway beats rough by 0.09-0.18 at every lay-up yardage (Arccos par-5 study); Shot Scope proximity 60-100 yd: 40 ft fw / 46 rough / 56 sand (research.md). |
| DECADE green targets | Card number (60 yd: 3 ... 150: 8 ... 250: 13, i.e. ~distance/20) in from each edge; +3 water/OB, +2 trees/long grass, +1 bunker; wind -1/0/+1/+2/+3; worse side keeps its full cushion when both don't fit | `mozingo/yardage_book.py` (DECADE card, as on the par 3s). A USGA-hosted DECADE summary gives the same ~5% of the yardage from the nearest edge (160 yd -> 8 yd): [USGA PDF](https://championships.usga.org/content/dam/championships/usndp/images/2025-images/grant-management-center-/Picking-Targets-Into-Greens.pdf). Fawcett: aim between the middle and the pin, "aggressive off the tee, conservative into greens" ([Golf Digest](https://www.golfdigest.com/story/scott-fawcectt-golf-iq-target-aiming-strategy-advice)). Here the card number is scaled by the lie multiplier (from the rough the cushions grow 20-35%). Beyond 250 yd it continues at distance/20. |
| Lay-up distance | No "favourite wedge" bonus in the model; closer is better unless trouble says otherwise | Arccos par-5 study (1.34 M par-5 holes, 18,285 golfers): strokes to finish rise in a straight line the farther back you lay up, ~0.22 strokes from 60 to 100 yd, and there is no sweet spot. Going for the green beat laying back at every handicap ([MyGolfSpy](https://mygolfspy.com/news-opinion/the-par-5-lay-up-debate-is-over-we-have-the-data/)). Arccos proximity: every bracket is closer from 60-80 than from 100-120 (0-5 hcp: only ~7 ft apart) ([Arccos](https://www.arccosgolf.com/blogs/community/course-management-101-what-layup-yardage-is-your-sweet-spot)). Tested as a sensitivity: a 0.05-stroke penalty on 45-85 yd partial wedges. |
| Scoring after the shot | PGA Tour tables (Broadie): putts by feet, short game 2-40 yd by lie, `tee_strategy.BASELINE` beyond; sensitivity with 5-hcp offsets (+0.06 putting, +0.15 short game, `HCP_BASELINE` long) | Same baseline choice as `final_decision.py`. The modelled 5-hcp approach from 115-120 yd in the fairway comes out about 3.2 strokes, tour about 2.83, i.e. +0.35-0.40, in line with research.md's inference for a 5 index. |
| Bag | 2-wood off the deck ~255/265, 4-wood ~248/258, 4-iron 210 carry, then about 12 yd per club: 5i 198, 6i 186, 7i 174, 8i 162, 9i 150, PW 138, GW 126, SW 113, LW 100 | Your numbers plus typical gapping. A typical 5 hcp is ~23 yd shorter (Arccos 0-5 index: 4i 187 ... PW 119), so your irons scale with your 275 driver carry. Club names in the tables are only a guide: use your own numbers. |
"""

CAVEATS = """\
## Caveats

- **Green and hazards:** the green outlines are the OSM polygons. They match the NAIP photo on every hole (QA close-ups) and sit 1-14 yd from course.py's trilaterated centres (6: 14 yd, 10: 10 yd). Bunkers and water are from OSM. Trees are lidar canopy (+5 m). Long grass is the hand map near the greens; the vision2 long grass is ignored within 40 yd of a green, where it flagged mown rough. Hazard sides are read from rays out of each edge: 12 yd for sand/trees/long grass, 20 yd for water/OB.
- **No pin:** boxes are pin-free, as on the par 3s. The strokes-gained check averages 16 pins spread over the green, at least 4 yd from the edge.
- **Not modelled:** elevation, green slope, wind on the approach (the DECADE wind modifier only widens the cushions; plays-like yardage is the wind page's job) and firmness (soft: ~1-2 yd of release on approaches).
- **Lay-up target values** are the third shot's expected strokes, played to the DECADE box of this green from where the lay-up finishes, on a 5-yd value grid. A full Monte Carlo would read a little better than the grid. The best lay-up per tee ball is the minimum over ~170 targets, which flatters laying up by about 0.01 (winner's curse).
- **Tee shot:** the calm-day pick and aim from `final_decision.json`, at the wind page's prior means (driver width 70 yd, carry depth x1.25, 15% slight mishits). The Gold-tee rows (2B, 9B) are for reference: you play the Black tees.
"""


def _lies(share):
    order = ("fairway", "first_cut", "rough", "sand", "green", "recovery", "native", "water", "ob")
    short = {"fairway": "fw", "first_cut": "cut", "rough": "rgh", "sand": "sand", "green": "grn",
             "recovery": "trees", "native": "long gr.", "water": "water", "ob": "OB"}
    return " / ".join(f"{short[k]} {share[k]:.0%}" for k in order if share.get(k, 0) >= 0.005)


def _trouble(b):
    return ", ".join(f"{s} {v}" for s, v in b["haz"].items() if v != "rough") or "none within 12 yd"


def _box(b):
    w = b["lat"][1] - b["lat"][0]
    d = b["dep"][1] - b["dep"][0]
    size = f"{max(w, 0):.0f} x {max(d, 0):.0f} yd" if w >= 2 and d >= 2 else (
        "single line" if w < 2 and d < 2 else f"{max(w, 0):.0f} x {max(d, 0):.0f} yd")
    return f"play **{b['play']:.0f}** ({b['lo']:.0f}-{b['hi']:.0f}), aim {b['aim_text']} of centre; box {size}"


def render(data):
    H = data["holes"]
    out = ["# Spirit Hollow: second shots (approach targets and par-5 go / lay-up)", "",
           "Built by `spirit_hollow/approach/build.py` (data: `output/approach.json`). "
           f"Settings: {data['cfg']}.", "",
           "**How to read the boxes.** The DECADE rule (as on the par-3 pages) is applied to each green as seen "
           "from where the tee plan leaves you: the card's cushion for that distance, scaled up from the rough, "
           "+3 water/OB, +2 trees/long grass, +1 bunker. *Play* is the yardage to the box centre, with the box's "
           "front-back in brackets. *Aim* is the box centre relative to the green centre (left/right as you face the "
           "green). All boxes are calm (wind modifier 0); the JSON has -1..+3.", "",
           "## Par 4s and par 5s: the approach", "",
           "| Hole | Par | Tee club (aim) | Approach left: median (10-90%) | Lie after the tee shot | DECADE box from the fairway | Trouble round the green | From the rough | SG check (box / green centre / best aim) |",
           "|---|---|---|---|---|---|---|---|---|"]
    for k, h in H.items():
        a = h["approach"]
        src = h.get("go_boxes") if h["par"] == 5 and h.get("go_boxes") else h["boxes"]
        bx = src["fairway"]["0"]
        br = src["rough"]["0"]
        tee = f"{h['tee']['club']} ({h['tee']['aim']:+.1f}){' tie' if h['tee']['tie'] else ''}"
        if h["par"] == 5:
            dist = f"{a['median']:.0f} ({a['p10']:.0f}-{a['p90']:.0f}) after the tee (box = going for it)"
            if h.get("go_target"):
                gt = h["go_target"]
                dist += f"; SG prefers the apron {gt['L']:.0f} short ({gt['off']:+.0f}), {gt['shot']:.0f} yd"
        else:
            dist = f"{a['median']:.0f} ({a['p10']:.0f}-{a['p90']:.0f}), {a['club']}"
        sg = h.get("sg_check")
        sgs = "-"
        if sg:
            sgs = f"{sg['e_decade']:.3f} / {sg['e_centre']:.3f} / {sg['e_best']:.3f}"
            if sg["recommend"] == "sg":
                lat, dep = sg["best_ld"]
                sgs += (f"; **SG: aim {abs(lat):.0f} {'right' if lat > 0 else 'left'}, {abs(dep):.0f} "
                        f"{'long' if dep > 0 else 'short'} of centre, play {sg['play_sg']:.0f}** (box costs {sg['decade_cost']:.2f})")
            elif not sg["best_in_box"]:
                sgs += f" (best aim just outside the box, {sg['decade_cost']:.3f})"
        out.append(f"| {h['label']} | {h['par']} | {tee} | {dist} | {_lies(a['lie_share'])} | {_box(bx)} | "
                   f"{_trouble(bx)} | play {br['play']:.0f}, aim {br['aim_text']} | {sgs} |")
    p5 = {k: h for k, h in H.items() if h["par"] == 5}
    if p5:
        out += ["", "## Par 5s: go for it or lay up", "",
                "Monte Carlo over the tee ball's finishing spots. For each spot, going for the green (at the "
                "DECADE box, longest club the lie allows) is compared with every lay-up target (20-170 yd short of the "
                "green on the hole line, 25 yd left to 25 yd right), each followed by the third shot into this green. "
                f"A 2nd shot aimed within 40 yd of the green centre (the box, or the apron in front of it) counts as going; "
                "*apron 20 short, +5* = aim 20 yd short of the green centre, 5 yd right of the line. "
                "*Go rule* comes from the same comparison from points on the hole line, by lie: go when the "
                "distance is at or under the number.", "",
                "| Hole | Tee ball | Go (share of tee balls) | When going, aim at | Go rule: fw / cut / rough (go at or inside, yd) | Lay-up target | Lay-up club / where it finishes | Leave a full wedge instead | Go minus lay-up (strokes, go-range balls) | 5-hcp tables / partial-wedge test |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for k, h in p5.items():
            p = h["par5"]
            rule = p.get("go_rule", {})
            gr = " / ".join(_ft(rule.get(l, {}).get("go_up_to")) for l in ("fairway", "first_cut", "rough"))
            gb = " / ".join(_ft(rule.get(l, {}).get("green_box_up_to")) for l in ("fairway", "first_cut", "rough"))
            gr += f"; at the green itself up to {gb}"
            lay = h.get("layup")
            if lay:
                side = "on the line" if abs(lay["off"]) < 1 else f"{abs(lay['off']):.0f} yd {'right' if lay['off'] > 0 else 'left'} of the line"
                lt = f"{lay['L']:.0f} yd short of the green centre, {side}"
                lc = f"{lay['club']} ({lay['shot']:.0f} yd) -> {_lies(lay['lie_share'])}"
                fw = (f"+{lay['full_wedge_cost']:.2f} (leave {lay['full_wedge_L']})"
                      if "full_wedge_cost" in lay else "-")
            else:
                lt = lc = fw = "-"
            mg = p.get("margin_go_minus_lay") or {}
            mgs = f"{mg['mean']:+.3f} ± {mg['se']:.3f} (n {mg['n']})" if mg.get("mean") is not None and mg.get("se") else "-"
            sens = h.get("sensitivity", {})
            ss = "; ".join(
                f"{n.split('_')[0]}: go {v['p_go']:.0%}, lay-up {_ft(v.get('layup_L'))}"
                + (f", fw rule {_ft(v.get('go_rule', {}).get('fairway', {}).get('go_up_to'))}" if v.get("go_rule") else "")
                for n, v in sens.items())
            ga = ", ".join(f"{('the green box' if k == 'green' else 'apron ' + k)} {v:.0%}" for k, v in list(p.get("go_aims", {}).items())[:2]) or "-"
            out.append(f"| {h['label']} | {h['approach']['median']:.0f} ({h['approach']['p10']:.0f}-{h['approach']['p90']:.0f}) | "
                       f"{p['p_go']:.0%} (lay-up {p['p_layup']:.0%}, forced {p['p_forced']:.0%}) | {ga} | {gr} | {lt} | {lc} | {fw} | {mgs} | {ss} |")
        out += ["", "Lay-up EV by distance left (best offset; all strokes incl. the 2nd shot, averaged over the tee balls that lay up):", ""]
        for k, h in p5.items():
            lay = h.get("layup")
            if lay:
                row = ", ".join(f"{L}: {v[0]:.2f}" for L, v in lay["ev_by_L"].items())
                out.append(f"- **{h['label']}**: {row}")
    out += ["", "## Hole notes", ""]
    for k, h in H.items():
        bx = h["boxes"]["fairway"]["0"]
        cush = ", ".join(f"{s} {v:.0f}" for s, v in bx["cushion"].items())
        winds = ", ".join(f"{w}: {b['lo']:.0f}-{b['hi']:.0f}" for w, b in h["boxes"]["fairway"].items())
        g = h["green"]
        line = (f"- **{h['label']}** (par {h['par']}): green {g['width_yd']:.0f} wide x {g['depth_yd']:.0f} deep "
                f"(OSM; {g['trilat_offset_yd']:.0f} yd from the trilaterated centre). From {bx['dist']:.0f} yd: "
                f"cushions {cush} ({bx['how_lat']}/{bx['how_dep']}); box depth by wind modifier {winds}.")
        if h["par"] == 5:
            line = line.replace(f"From {bx['dist']:.0f} yd:", f"Third shot after the lay-up, from {bx['dist']:.0f} yd: {_box(bx)};")
        out.append(line)
    out += ["", EVIDENCE, CAVEATS]
    return "\n".join(out) + "\n"


def _ft(x):
    return "-" if x is None else f"{x:.0f}"
