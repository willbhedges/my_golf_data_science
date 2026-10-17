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


def width_ranges(fd):
    """'Driver pattern up to 60 yds: X; 60-80: Y; over 80: Z' from the fixed-width sweep."""
    flips = sorted(fd.get("width_flips") or [], key=lambda f: f["width"])
    if not flips:
        return "Same club for any driver pattern from 55 to 90 yds."
    parts, lo = [], None
    for f in flips:
        parts.append(f"{'up to' if lo is None else f'{lo:.0f}-'}{'' if lo is None else ''}"
                     f"{' ' if lo is None else ''}{f['width']:.0f} yds: {f['frm']}")
        lo = f["width"]
    parts.append(f"over {lo:.0f} yds: {flips[-1]['to']}")
    at70 = next((w["pick"] for w in fd.get("width_sweep", []) if w["width"] == 70), fd["pick"])
    extra = ("" if at70 == fd["pick"] else
             f" (At exactly 70 yds {at70} edges it; {fd['pick']} wins once the other unknowns are "
             f"averaged in, so treat it as a near tie.)")
    return "By driver pattern width: " + "; ".join(parts) + "." + extra


def describe(h, res, best):
    fd = FINAL[key(h)]
    r = res[best]
    p = fd["p_best_crossfit"].get(best, 0.0)
    lead = (f"Tie with {fd['runner']} ({fd['margin']:.3f} strokes); either is fine, play the one you trust today."
            if fd["tie"] else f"{best} by {fd['margin']:.2f} strokes over {fd['runner']}; best club in {p:.0%} of "
            f"what-if worlds.")
    sw = width_ranges(fd)
    trouble = sorted(((r["share"].get(k_, 0.0), w) for k_, w in LIE_WORDS.items()), reverse=True)
    trouble = [f"{w} {q:.0%}" for q, w in trouble if q >= 0.02]
    parts = [lead, sw, f"With {best}: fairway {r['share']['fairway']:.0%}, first cut "
             f"{r['share'].get('first_cut', 0.0):.0%}" + (", " + ", ".join(trouble) if trouble else "")
             + f", about {r['approach']:.0f} yds in."]
    el = course.HOLES[h].get("elev", {}).get(best)
    if el and abs(el[0]) >= 3:
        parts.append(f"Elevation: {'+' if el[0] > 0 else ''}{el[0]:.0f} yds carry "
                     f"({'downhill' if el[0] > 0 else 'uphill'}), roll x{el[1]:.2f}.")
    mv = course.HOLES[h].get("tee_moved")
    if mv:
        parts.append(f"Tee: planned from the Black box, {mv} yds ahead of the app's tee marker "
                     "(18Birdies puts its marker on a box further back on this hole).")
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
    with open(os.path.join(HERE, "output", "final_notes.json"), "w") as fh:   # also feeds the wind page
        json.dump({str(k): dict(note=notes[k], aim_at=aim_at[k]) for k in notes}, fh, indent=1)
    if os.environ.get("NOTES_ONLY"):
        return
    # write somewhere git never touches, then move into place when complete (other agents' git
    # pull --autostash once reverted a half-written PDF in output/)
    out_dir = os.environ.get("BOOK_TMP")
    yb.STRATEGY_NAME = os.path.join(out_dir, "Spirit_Hollow_Final.pdf") if out_dir else "Spirit_Hollow_Final.pdf"
    yb.PREFIX = os.path.join(out_dir, "Spirit_Hollow_Final") if out_dir else "Spirit_Hollow_Final"
    yb.confidence = lambda: {(int(k) if k.isdigit() else k): round(100 * v["p_best_crossfit"].get(v["pick"], 0))
                             for k, v in FINAL.items()}
    yb.build()


if __name__ == "__main__":
    main()
