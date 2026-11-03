"""One cause per miss and per stroke of regret, from error_budget.py runs with every configuration.

    python3 course_data/platform/error_budget.py --set v1 --auto-dir A1 --out EB1.json      # all configurations
    python3 course_data/platform/error_budget.py --set v2 --auto-dir A2 --out EB2.json
    python3 course_data/platform/budget_causes.py EB1.json EB2.json [--out causes.json]

error_budget.py says, per tee shot, which single truth layer fixes the auto plan (+layer) and which single auto
layer breaks the truth plan (-layer). Shares there can add to more than 100 % (one miss, two fixers). This tool
gives every tee shot ONE cause so the misses and the regret add up:

  regret r      truth-map EV of the auto plan minus the truth plan's EV (strokes; error_budget "regret"; 0 where
                the aim point is on another hole)
  recovery      rec(L) = r(auto) - r(+L): the strokes the truth layer L alone gives back
  miss          cause = the +L that fixes it with the largest recovery; else the L with the largest recovery when
                it is >= max(MIN_REC, r / 2); else the -L whose auto layer breaks the truth plan with the largest
                regret ("(-layer)"); else "interaction" (only a group fixes it) or "unexplained"
  matched hole  its (small) regret goes to the L with the largest recovery when >= MIN_REC, else "no layer"
  near tie      a miss with r < TIE: both plans within TIE strokes on the true map ("same club + aim" counts it)

National KC is left out (no web card: the build numbered the holes itself), as in ERROR_BUDGET.md.
"""
from __future__ import annotations

import argparse
import json

LAYERS = ["card", "routing", "tees", "greens", "fairway", "trees", "water", "ob", "long_grass", "bunkers", "elevation"]
GROUPS = ("frame", "hazards")
MIN_REC = 0.005
TIE = 0.01
COST = 0.02          # proposed M2 rule: a miss counts only when it costs more than this
SKIP = ("national_kc",)


def _cfg(r, name):
    return r["configs"].get(name) or {}


def _reg(r, name="auto"):
    v = _cfg(r, name).get("regret")
    return None if v is None else float(v)


def cause_of(r):
    """(cause, is_miss, regret, {layer: recovery}, [layers whose +L fixes it]) for one error_budget row."""
    r0 = _reg(r) or 0.0
    rec = {}
    for L in LAYERS:
        v = _reg(r, f"+{L}")
        rec[L] = r0 - v if v is not None else 0.0
    miss = not _cfg(r, "auto").get("match")
    fixers = [L for L in LAYERS if _cfg(r, f"+{L}").get("match")]
    if miss:
        cand = fixers or [L for L in LAYERS if rec[L] >= max(MIN_REC, 0.5 * r0)]
        if cand:
            c = max(cand, key=lambda L: rec[L])
        else:
            minus = [L for L in LAYERS if f"-{L}" in r["configs"] and not _cfg(r, f"-{L}").get("match")]
            if minus:
                c = max(minus, key=lambda L: _reg(r, f"-{L}") or 0.0) + " (-layer)"
            elif any(_cfg(r, f"+{g}").get("match") for g in GROUPS):
                c = "interaction"
            else:
                c = "unexplained"
    else:
        best = max(LAYERS, key=lambda L: rec[L])
        c = best if rec[best] >= MIN_REC else "no layer"
    return c, miss, r0, rec, fixers


def rows_of(paths, skip=SKIP):
    out = []
    for p in paths:
        for c in json.load(open(p))["courses"]:
            if c["slug"] in skip or "rows" not in c:
                continue
            out += [(c["slug"], r) for r in c["rows"]]
    return out


def summarise(rows):
    per, holes = {}, {}
    for s, r in rows:
        c, miss, r0, rec, fixers = cause_of(r)
        base = c.replace(" (-layer)", "")
        P = per.setdefault(base, dict(misses=0, near_ties=0, regret=0.0, regret_misses=0.0, holes=[]))
        P["regret"] += r0
        if miss:
            P["misses"] += 1
            P["near_ties"] += r0 < TIE
            P["regret_misses"] += r0
            P["holes"].append(f"{s}:{r['hole']}")
        holes[f"{s}:{r['hole']}"] = dict(cause=c, miss=miss, regret=round(r0, 4), fixers=fixers,
                                         rec={L: round(v, 4) for L, v in rec.items() if abs(v) >= 0.001})
    miss = [_reg(r) or 0.0 for _, r in rows if not _cfg(r, "auto").get("match")]
    n = len(rows)
    out = dict(n=n, match=n - len(miss), regret=round(sum(_reg(r) or 0.0 for _, r in rows), 3),
               near_tie=dict(misses=len(miss), under_tie=sum(x < TIE for x in miss),
                             under_cost=sum(x < COST for x in miss), over_cost=sum(x >= COST for x in miss),
                             regret_over_cost=round(sum(x for x in miss if x >= COST), 3)),
               match_if_cost_counted=n - sum(x >= COST for x in miss),
               per_cause={k: dict(v, regret=round(v["regret"], 3), regret_misses=round(v["regret_misses"], 3))
                          for k, v in sorted(per.items(), key=lambda kv: -kv[1]["regret"])},
               hole_causes=holes)
    for L in LAYERS + list(GROUPS):
        if any(f"+{L}" in r["configs"] for _, r in rows):
            out[f"+{L}"] = dict(match=sum(bool(_cfg(r, f"+{L}").get("match")) for _, r in rows),
                                regret=round(sum(_reg(r, f"+{L}") or 0.0 for _, r in rows), 3))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", help="error_budget.py result jsons (every configuration)")
    ap.add_argument("--out")
    a = ap.parse_args()
    S = summarise(rows_of(a.runs))
    print(json.dumps({k: v for k, v in S.items() if k != "hole_causes"}, indent=1))
    if a.out:
        json.dump(S, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
