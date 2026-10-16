"""Compare a plan's tee-shot picks with the hand-traced Spirit Hollow decision (spirit_hollow/output/final_decision.json).

  python3 course_data/product/compare_golden.py <out dir> [--golden spirit_hollow/output/final_decision.json]

Hole keys: the hand map has two boxes on 2 and 9 ("2F"/"9F" = Black, "2B"/"9B" = Gold); the auto plan's
2 / 9 are matched to the box of the plan's tee set (Black -> F, Gold -> B). Aims are compared only loosely:
the hand map's line is the GPS app's line, the auto plan's is tee -> the hole line's first turn.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def compare(out_dir, golden=os.path.join(ROOT, "spirit_hollow", "output", "final_decision.json")):
    plan = json.load(open(os.path.join(out_dir, "plan.json")))
    gold = json.load(open(golden))
    box = "B" if str(plan.get("tee_set", "")).lower() == "gold" else "F"
    rows, same, n = [], 0, 0
    for k, p in plan["picks"].items():
        g = gold.get(k) or gold.get(k + box)
        if g is None:
            rows.append((k, p["club"], "-", "-", "not in the hand map"))
            continue
        n += 1
        ok = p["club"] == g["pick"]
        tie_ok = ok or p["tie"] or g.get("tie")
        same += ok
        rows.append((k, f"{p['club']}{' (tie)' if p['tie'] else ''} {p['aim']:+.0f}",
                     f"{g['pick']}{' (tie)' if g.get('tie') else ''} {g['aim']:+.0f}",
                     "same" if ok else ("differs, but a tie" if tie_ok else "DIFFERS"), ""))
    agree_or_tie = sum(1 for r in rows if r[3] in ("same", "differs, but a tie"))
    md = [f"# {plan['course']} ({plan['tee_set']}, {plan['mode']}) vs the hand-traced final decision", "",
          f"Same club on {same}/{n} tee shots ({same / max(n, 1):.0%}); same or a tie on either side: "
          f"{agree_or_tie}/{n}.", "",
          "| Hole | Auto plan (club, aim) | Hand map final_decision (club, aim) | Club | Note |",
          "|---|---|---|---|---|"]
    md += [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows]
    md += ["", "Aims are not comparable one-to-one: the hand map's aims are off the GPS app's line, the auto "
           "plan's off the tee line (tee to the hole line ~250 yds out)."]
    path = os.path.join(out_dir, "compare_final_decision.md")
    with open(path, "w") as fh:
        fh.write("\n".join(md) + "\n")
    return dict(same=same, n=n, agree_or_tie=agree_or_tie, path=path, rows=rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--golden", default=os.path.join(ROOT, "spirit_hollow", "output", "final_decision.json"))
    a = ap.parse_args()
    r = compare(a.out, a.golden)
    print(open(r["path"]).read())
