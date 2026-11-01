"""pathroute on the zero-tap benchmark.

    python course_data/zero_tap/pathroute/prep.py --cache C --split all
    python course_data/zero_tap/pathroute/run.py dev  --cache C [--out results_dir]   # 5-fold out-of-fold on dev
    python course_data/zero_tap/pathroute/run.py test --cache C --out results_dir     # fit on all dev, run test once

Dev numbers are out-of-fold (each dev course decoded by models fitted on the other 4/5 of dev courses).
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [HERE, ZT]
import bench as B  # noqa: E402
import decode as DC  # noqa: E402
from model import Models  # noqa: E402

METHOD = "pathroute"
W = dict(trans=0.5, club=1.0)


def load(cache, split):
    out = []
    for r in B.courses(split):
        p = os.path.join(cache, r["slug"] + ".pkl")
        out.append(pickle.load(open(p, "rb")) if os.path.exists(p) else dict(slug=r["slug"], error="no cache"))
    return out


def _version():
    try:
        return subprocess.check_output(["git", "-C", HERE, "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "dev"


def result(d, M, tier, w=W, card=None, cuts=(225.0, 450.0)):
    base = dict(schema="zero_tap_result/1", method=METHOD, version=_version(), tier=tier, slug=d["slug"],
                card_kind="none" if tier == "nocard" else "card")
    if d.get("error"):
        return dict(base, certain=False, confidence=0.0, holes=[], error=d["error"])
    pr = M.predict(d)
    cy, cpar = card_arrays(card)
    holes, conf = DC.decode(d, pr, dict(w, card=w.get("card", 1.0)) if cy else w, card_y=cy)
    hs = []
    names = "ABCD"
    multi = d["kind"] in (27, 36)
    for h in holes:
        pos = h["loop"] * (9 if d["kind"] in (9, 27) else 18) + h["number"] - 1
        par = (cpar[pos] if pos < len(cpar) else cpar[h["number"] - 1]) if cpar else None
        hs.append(dict(number=h["number"], par=par or DC.par_from_len(h["L"], *cuts),
                       green_ll=d["greens"][h["g"]]["ll"], tee_ll=d["tees"][h["t"]]["ll"],
                       tee_boxes_ll=[d["tees"][b]["ll"] for b in h["boxes"]],
                       green_id=d["greens"][h["g"]]["id"], tee_id=d["tees"][h["t"]]["id"], confidence=conf,
                       length_yd=round(h["L"], 1), **({"course": names[h["loop"]]} if multi else {})))
    return dict(base, certain=False, confidence=conf, holes=hs, error=None if hs else "decode failed",
                extra=dict(club_src=d.get("club_src")))


def card_arrays(card):
    """(back-tee yards per hole, pars) of a scorecard/1, or (None, None)."""
    if not card:
        return None, None
    ys = [ts.get("yards") for ts in (card.get("tee_sets") or {}).values() if ts.get("yards")]
    n = max((len(y) for y in ys), default=0)
    ys = [y for y in ys if len(y) == n]
    cy = [max((y[i] or 0) for y in ys) for i in range(n)] if ys else None
    if cy and min(cy) <= 0:
        cy = None
    return cy, card.get("par")


def folds(ds, k=5):
    good = [d for d in ds if not d.get("error")]
    idx = {d["slug"]: i % k for i, d in enumerate(sorted(good, key=lambda d: d["slug"]))}
    return idx


def _cards(split):
    return {r["slug"]: B.card_for(r) for r in B.courses(split)}


def run_dev(cache, tier="nocard", w=W, k=5, out=None, models=None):
    ds = load(cache, "dev")
    cards = _cards("dev") if tier == "osm_card" else {}
    fi = folds(ds, k)
    res = []
    ms = models or {}
    for f in range(k):
        if f not in ms:
            ms[f] = Models().fit([d for d in ds if fi.get(d["slug"], -1) not in (-1, f)])
        for d in ds:
            if fi.get(d["slug"], 0) == f:
                c = cards.get(d["slug"])
                res.append(result(d, ms[f], tier, w, card=c[0] if c else None))
    if out:
        for r in res:
            B.write_result(r, os.path.join(out, tier))
    return res, ms


def summary(res, split):
    s = B.score(res, split)
    a = s[split]
    return dict(formed=a["formed_acc"], number=a["hole_number_acc"], par=a["par_acc"],
                holes_right=a["courses_holes_right"], fully=a["courses_fully_right"],
                fails=a["course_failures"], by_kind={k: (v["formed_acc"], v["hole_number_acc"], v["courses_holes_right"])
                                                     for k, v in a["by_kind"].items()}), s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("split", choices=["dev", "test"])
    ap.add_argument("--cache", required=True)
    ap.add_argument("--out")
    ap.add_argument("--tiers", default="nocard")
    a = ap.parse_args()
    for tier in a.tiers.split(","):
        if a.split == "dev":
            res, _ = run_dev(a.cache, tier, out=a.out)
        else:
            M = Models().fit([d for d in load(a.cache, "dev") if not d.get("error")])
            cards = _cards("test") if tier == "osm_card" else {}
            res = [result(d, M, tier, card=(cards.get(d["slug"]) or (None,))[0]) for d in load(a.cache, "test")]
            if a.out:
                for r in res:
                    B.write_result(r, os.path.join(a.out, tier))
        sm, _ = summary(res, a.split)
        print(tier, a.split, json.dumps(sm))


if __name__ == "__main__":
    main()
