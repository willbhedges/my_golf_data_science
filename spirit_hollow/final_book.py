"""Final strategy book: picks and aims from the Bayesian run (output/final_decision.json).

  python3 spirit_hollow/final_book.py
    -> output/Spirit_Hollow_Final.pdf (book) and output/Spirit_Hollow_Final_Aim_Sheets.pdf

final_decision.json is the single source of truth for club and aim. The page numbers (fairway %,
trouble %, approach) are simulated at the prior means of that run (driver pattern 70 yds, depth
x1.25) at exactly that aim, so they describe the play printed on the page. Confidence = share of
the 64 what-if worlds (cross-fitted) in which the pick is the best club; the notes add when to
switch clubs if your pattern is wider or tighter than 70 yds.
"""
import copy
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "mozingo"), HERE]

import course                                  # noqa: E402
import tee_strategy as t                       # noqa: E402
import yardage_book as yb                      # noqa: E402
from interim_book import LIE_WORDS, aim_words  # noqa: E402

FINAL = json.load(open(os.path.join(HERE, "output", "final_decision.json")))


def key(h):
    return str(h)


def set_prior_means():
    s = 70.0 / 65.0
    t.CLUBS = {k: (c, tot, w * s, d * 1.25) for k, (c, tot, w, d) in copy.deepcopy(t.CLUBS).items()}
    t.IRONS = {k: (c, tot, w * s, d * 1.25) for k, (c, tot, w, d) in copy.deepcopy(t.IRONS).items()}


def tee_plan(h):
    fd = FINAL[key(h)]
    res = {}
    for c, v in fd["clubs"].items():
        r = t.best_aim(h, c, aims=np.array([v["aim"]]))
        r["ev"] = v["ev"]                                  # the Bayesian expected strokes
        res[c] = r
    best = fd["pick"]
    lo = t.HOLES[h].get("aim_min", -20)
    aims = np.arange(lo, t.HOLES[h].get("aim_max", 20) + 0.1, 2.5)
    curve = np.array([t.simulate(h, best, a)[3].mean() for a in aims])
    ok = aims[curve <= curve.min() + yb.ZONE_TOL]
    ok = np.append(ok, fd["aim"])
    return res, best, (ok.min(), ok.max())


def describe(h, res, best):
    fd = FINAL[key(h)]
    r = res[best]
    p = fd["p_best_crossfit"].get(best, 0.0)
    lead = (f"Tie with {fd['runner']} ({fd['margin']:.3f} strokes); either is fine, play the one you trust today."
            if fd["tie"] else f"{best} by {fd['margin']:.2f} strokes over {fd['runner']}; best club in {p:.0%} of "
            f"what-if worlds.")
    flips = fd.get("width_flips") or []
    sw = " ".join(f"If your driver pattern is {'wider' if f['to'] != 'Driver' else 'tighter'} than "
                  f"{f['width']:.0f} yds, {f['to']} instead of {f['frm']}." for f in flips
                  if f["frm"] == best or f["to"] == best)
    trouble = sorted(((r["share"].get(k_, 0.0), w) for k_, w in LIE_WORDS.items()), reverse=True)
    trouble = [f"{w} {q:.0%}" for q, w in trouble if q >= 0.02]
    parts = [lead, sw, f"With {best}: fairway {r['share']['fairway']:.0%}, first cut "
             f"{r['share'].get('first_cut', 0.0):.0%}" + (", " + ", ".join(trouble) if trouble else "")
             + f", about {r['approach']:.0f} yds in."]
    el = course.HOLES[h].get("elev", {}).get(best)
    if el and abs(el[0]) >= 3:
        parts.append(f"Elevation: {'+' if el[0] > 0 else ''}{el[0]:.0f} yds carry "
                     f"({'downhill' if el[0] > 0 else 'uphill'}), roll x{el[1]:.2f}.")
    return " ".join(x for x in parts if x)


def main():
    set_prior_means()
    notes, aim_at = {}, {}
    yb.use_course("Spirit Hollow GC", HERE, "Spirit_Hollow", course.HOLES, course.PAR3, notes, aim_at,
                  course.ORDER, course.LABELS)
    yb.tee_plan = tee_plan
    for h in course.HOLES:
        res, best, zone = tee_plan(h)
        notes[h] = describe(h, res, best)
        aim_at[h] = aim_words(h, res, best)
        print(h, best, notes[h], flush=True)
    yb.STRATEGY_NAME = "Spirit_Hollow_Final.pdf"
    yb.PREFIX = "Spirit_Hollow_Final"
    yb.confidence = lambda: {(int(k) if k.isdigit() else k): round(100 * v["p_best_crossfit"].get(v["pick"], 0))
                             for k, v in FINAL.items()}
    yb.build()


if __name__ == "__main__":
    main()
