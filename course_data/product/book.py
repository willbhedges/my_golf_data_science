"""Strategy book + phone aim sheets for any course, via mozingo/yardage_book.use_course(...) + build().

The book code is used unchanged; three hooks adapt it to a generated course:
  * tee_plan -> the decision from decide.py (quick or full) instead of the book's own point estimate,
  * the "GPS app line" wording -> "tee line" (an auto course has no GPS app; the line runs from the tee
    to the point on the hole line ~250 yds out, package.TEE_LINE),
  * the confidence line: P(best) from the full run, or "quick mode" when it was not computed.
"""
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if os.path.join(ROOT, "mozingo") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "mozingo"))

import tee_strategy as t                            # noqa: E402
import yardage_book as yb                           # noqa: E402

import decide                                       # noqa: E402

_text_block, _side = yb.text_block, yb.side


def _words(s):
    return (s.replace("on the tee line of the app line", "on the tee line")
             .replace("of the app line", "of the tee line").replace("app line", "tee line")
             .replace("Aims are yards left/right of the GPS app's tee line.",
                      "Aims are yards left/right of the tee line (tee to the hole line ~250 yds out).")
             .replace("best club in ?% of what-if worlds", "not computed (quick mode)")
             .replace("100 'what if my inputs are off' scenarios", "the Bayesian prior's what-if worlds")
             .replace("Green (app):", "Green (map):").replace("the green as traced", "the green as mapped")
             .replace("20,000 simulated tee shots per club", SIM_WORDS[0]))


SIM_WORDS = ["8,000 simulated tee shots per club and aim"]


def _text_block_hook(fig, x, y, lines, *a, **k):
    return _text_block(fig, x, y, [_words(ln) for ln in lines], *a, **k)


def _side_hook(yds):
    return _words(_side(yds))


def side(yds):
    return _side_hook(yds)


def stats_report(results, labels, path):
    """yardage_book.confidence() reads '| key | **club** | ... | NN% |' rows."""
    rows = ["| Hole | Pick | Margin | P(best) |", "|---|---|---|---|"]
    for k, r in results.items():
        if r.get("conf") is not None:
            rows.append(f"| {k} | **{r['pick']}** | {r['margin']:.3f} | {r['conf']}% |")
    with open(path, "w") as fh:
        fh.write("\n".join(rows) + "\n")


def build(mod, out_dir, prefix, results, log=print):
    """Write <out>/<prefix>_Strategy.pdf and <prefix>_Aim_Sheets.pdf. Images in <out>/screenshots/."""
    r0 = next(iter(results.values()))
    SIM_WORDS[0] = (f"{r0.get('n', 8000):,} simulated tee shots per club and aim (quick mode)" if r0.get("mode") == "quick"
                    else f"{r0.get('S')} prior draws x {r0.get('N'):,} simulated tee shots per club and aim")
    yb.use_course(mod.NAME, out_dir, prefix, mod.HOLES, mod.PAR3, mod.NOTES, mod.AIM_AT, mod.ORDER, mod.LABELS)
    decide.bind(mod.HOLES)
    decide.set_prior_means()                    # the drawn 95% pattern = the one the decision used

    def tee_plan(h):
        r = results[h]
        res = {c: dict(v) for c, v in r["clubs"].items()}
        return res, r["pick"], tuple(r["zone"])
    tee_plan.cache_clear = lambda: None
    yb.tee_plan = tee_plan
    yb.text_block, yb.side = _text_block_hook, _side_hook
    os.makedirs(os.path.join(out_dir, "output"), exist_ok=True)
    stats_report(results, mod.LABELS, os.path.join(out_dir, "output", "stats_report.md"))
    try:
        rows = yb.build()
    finally:
        yb.text_block, yb.side = _text_block, _side
    files = []
    for name in (f"{prefix}_Strategy.pdf", f"{prefix}_Aim_Sheets.pdf"):
        src = os.path.join(out_dir, "output", name)
        shutil.move(src, os.path.join(out_dir, name))
        files.append(name)
    shutil.rmtree(os.path.join(out_dir, "output"), ignore_errors=True)
    return rows, files


# ----------------------------------------------------------------------------- words for the page
def notes_and_aims(mod_holes, par3, results, flags, labels=None):
    """NOTES / AIM_AT for a generated course from the decision and the package's data flags."""
    notes, aim_at = {}, {}
    names = {"recovery": "trees", "native": "long grass", "water": "water", "ob": "OB", "sand": "sand"}
    for k, r in results.items():
        c = r["clubs"][r["pick"]]
        sh = c["share"]
        risk = sorted(((sh.get(x, 0) + (sh.get("ob", 0) if x == "water" else 0), names[x])
                       for x in ("water", "recovery", "native", "sand")), reverse=True)
        risk = [f"{n} {v:.0%}" for v, n in risk if v >= 0.03]
        s = f"{r['pick']} by {r['margin']:.3f} over {r['runner']}"
        s += " (a tie: either is fine)." if r.get("tie") else "."
        s += f" Fairway {sh['fairway'] + sh.get('first_cut', 0):.0%}"
        s += (", " + ", ".join(risk)) if risk else ""
        s += f"; ~{c['approach']:.0f} yds in."
        if r.get("width_flips"):
            s += " Switches " + "; ".join(f"{f['frm']}->{f['to']} if your pattern is wider than {f['width']:.0f} yds"
                                          for f in r["width_flips"]) + "."
        fl = [f for f in flags.get(k, []) if not f.startswith("tee:")]
        if fl:
            s += " Data check: " + "; ".join(fl[:2]) + "."
        notes[k] = s
        zone = r["zone"]
        aim_at[k] = (f"{side(r['aim'])} of the tee line (good from {side(zone[0])} to {side(zone[1])})"
                     .replace("on the tee line of the tee line", "on the tee line"))
    for k, p in par3.items():
        notes[k] = p.get("note", "")
    return notes, aim_at
