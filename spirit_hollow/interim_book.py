"""Current-best strategy book while the final Bayesian run finishes.

  python3 spirit_hollow/interim_book.py
    -> output/Spirit_Hollow_Targets.pdf (book) and output/Spirit_Hollow_Targets_Aim_Sheets.pdf

Uses the full current model (audited map, OSM mown fairway widths + first cut, stroke-and-distance
for lost balls in long grass, USGS DEM elevation, corrected greens) at Fawcett's 65/60/50-yd
patterns. Notes are generated from these results, not the older hand-written ones (which quote
numbers from earlier runs). No confidence column: the old one was computed on the outdated map.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "mozingo"), HERE]

import course                                  # noqa: E402
import tee_strategy as t                       # noqa: E402
import yardage_book as yb                      # noqa: E402

LIE_WORDS = {"recovery": "trees", "native": "long grass", "water": "water", "ob": "out of bounds", "sand": "sand"}


def describe(h, res, best):
    r = res[best]
    others = sorted((c for c in res if c != best), key=lambda c: res[c]["ev"])
    trouble = sorted(((r["share"].get(k, 0.0), w) for k, w in LIE_WORDS.items()), reverse=True)
    trouble = [f"{w} {p:.0%}" for p, w in trouble if p >= 0.02]
    margin = res[others[0]]["ev"] - r["ev"]
    lead = (f"Tie with {others[0]} (within {margin:.3f}); either is fine." if margin < 0.01
            else f"{best} by {margin:.2f} strokes over {others[0]}.")
    fw = r["share"]["fairway"]
    fc = r["share"].get("first_cut", 0.0)
    parts = [lead, f"With {best}: fairway {fw:.0%}, first cut {fc:.0%}"
             + (", " + ", ".join(trouble) if trouble else "") + f", about {r['approach']:.0f} yds in."]
    el = course.HOLES[h].get("elev", {}).get(best)
    if el and abs(el[0]) >= 3:
        parts.append(f"Elevation: {'+' if el[0] > 0 else ''}{el[0]:.0f} yds carry "
                     f"({'downhill' if el[0] > 0 else 'uphill'}), roll x{el[1]:.2f}.")
    return " ".join(parts)


def aim_words(h, res, best):
    r = res[best]
    trouble = sorted(((r["share"].get(k, 0.0), w) for k, w in LIE_WORDS.items()), reverse=True)
    main = [w for p, w in trouble if p >= 0.03][:2]
    return (f"Main trouble: {' and '.join(main)}." if main else "Open landing area.")


def main():
    notes, aim_at = {}, {}
    yb.use_course("Spirit Hollow GC", HERE, "Spirit_Hollow", course.HOLES, course.PAR3, notes, aim_at,
                  course.ORDER, course.LABELS)
    for h in course.HOLES:
        res, best, zone = yb.tee_plan(h)
        notes[h] = describe(h, res, best)
        aim_at[h] = aim_words(h, res, best)
        print(h, best, notes[h], flush=True)
    yb.STRATEGY_NAME = "Spirit_Hollow_Targets.pdf"
    yb.PREFIX = "Spirit_Hollow_Targets"
    yb.confidence = lambda: {}                       # no stale confidence numbers
    yb.build()


if __name__ == "__main__":
    main()
