"""Detection benchmark on simulated-unmapped courses (heldout.py sets): U-Net probabilities cached per course and
variant, then perception + object scoring from the cache (seconds per course instead of a minute).

    python3 perc_bench.py probs test|val|train VARIANT [--max N] [slug ...]    # -> cache/heldout/probs/<slug>/<VARIANT>.npz
    python3 perc_bench.py eval  test|val COMBO [--tag T] [slug ...]             # -> cache/heldout/eval/<set>_<T>.json

VARIANT: d0 (plain U-Net) .. d7 (one dihedral TTA view: rot90 x k, flip), or y<YEAR>[_dK] (another NAIP year,
heldout.py fetch_years). COMBO: '+'-joined variants whose probabilities are averaged (d0+d1+d2+d3 = 4-view TTA).
Scores: perception/evaluate.py through evaluate_scene.score_course; pooled precision / recall over the eligible
courses. TEST is reported, never tuned on; VAL is for choices.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fastscene as FS  # noqa: E402
import heldout as HO  # noqa: E402

PROBS = os.path.join(HO.ROOT, "probs")
EVAL = os.path.join(HO.ROOT, "eval")
KEYS = ("greens_hole", "greens_any", "tee_complexes", "tee_boxes", "fairways", "bunkers", "water")


def entries(which, slugs=()):
    e = [x for x in HO.sets()[which] if (not slugs or x["slug"] in slugs) and HO.ok(x)]
    return e


def variant_opts(v):
    """'d3' -> dict(augs=[3]); 'y2019_d1' -> dict(augs=[1], naip=(...2019 files))"""
    o = {}
    for part in v.split("_"):
        if part.startswith("d"):
            o["augs"] = [int(part[1:])]
        elif part.startswith("y"):
            o["year"] = int(part[1:])
    return o


def probs_path(slug, v):
    return os.path.join(PROBS, slug, v + ".npz")


def compute_probs(e, v):
    p = probs_path(e["slug"], v)
    if os.path.exists(p):
        return None
    o = variant_opts(v)
    st = FS.grid_stack(e["dir"])
    keep = FS.course_mask(st) & ~FS.osm_negative_mask(st, e["dir"])
    naip = None
    if "year" in o:
        yd = os.path.join(e["dir"], "years", str(o["year"]))
        naip = (os.path.join(yd, "naip_rgb.tif"), os.path.join(yd, "naip_nir.tif"))
        if not os.path.exists(naip[0]):
            return "no year " + str(o["year"])
    t = time.time()
    P = FS.unet_probs(e["dir"], st, FS.unet_weights(), keep, augs=o.get("augs"), naip=naip)
    dt = time.time() - t
    os.makedirs(os.path.dirname(p), exist_ok=True)
    q = np.clip(np.round(P * 255), 0, 255).astype(np.uint8)
    np.savez_compressed(p + ".tmp.npz", p=q, seconds=dt)
    os.replace(p + ".tmp.npz", p)
    return round(dt, 1)


def load_combo(slug, combo):
    ps = []
    for v in combo.split("+"):
        p = probs_path(slug, v)
        if not os.path.exists(p):
            if v.startswith("y"):           # a year this course does not have: skip that view
                continue
            raise FileNotFoundError(p)
        ps.append(np.load(p)["p"].astype(np.float32) / 255.0)
    if not ps:
        raise FileNotFoundError(slug + " " + combo)
    return np.mean(ps, 0)


def pooled(res, key):
    tp_p = n_p = tp_t = n_t = n = 0
    for r in res.values():
        v = r.get(key) or {}
        if not v.get("eligible"):
            continue
        n += 1
        tp_p += v.get("tp_pred") or 0
        n_p += v.get("n_pred") or 0
        tp_t += v.get("tp_true") or 0
        n_t += v.get("n_true") or 0
    return dict(courses=n, precision=round(tp_p / max(n_p, 1), 3), recall=round(tp_t / max(n_t, 1), 3),
                n_pred=n_p, n_true=n_t)


def evaluate(which, combo, tag=None, slugs=(), log=print, post=None):
    """post(st, D, P, e): an optional hook run on the detections before scoring (second-stage models)"""
    import evaluate_scene as ES
    res = {}
    for e in entries(which, slugs):
        try:
            P = load_combo(e["slug"], combo)
        except FileNotFoundError as ex:
            log(e["slug"], "missing", ex)
            continue
        t = time.time()
        r = ES.score_course(e["dir"], P=P)
        r["seconds_eval"] = round(time.time() - t, 1)
        res[e["slug"]] = {k: v for k, v in r.items() if not k.startswith("_")}
        log(e["slug"], " ".join(f"{k}={(r.get(k) or {}).get('precision')}/{(r.get(k) or {}).get('recall')}"
                                for k in ("greens_hole", "tee_complexes", "fairways", "bunkers", "water")), flush=True)
    pool = {k: pooled(res, k) for k in KEYS}
    os.makedirs(EVAL, exist_ok=True)
    out = os.path.join(EVAL, f"{which}_{tag or combo}.json")
    json.dump(dict(set=which, combo=combo, courses=res, pooled=pool), open(out, "w"), indent=1, default=float)
    for k in KEYS:
        log(k, pool[k])
    return pool


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["probs", "eval"])
    ap.add_argument("which")
    ap.add_argument("variant")
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--tag")
    a = ap.parse_args()
    if a.cmd == "probs":
        es = entries(a.which, a.slugs)
        if a.max:
            es = es[:a.max]
        for e in es:
            vs = a.variant.split("+")
            if "yall" in vs:                     # every extra NAIP year fetched for this course (heldout.py years)
                yd = os.path.join(e["dir"], "years")
                ys = sorted(os.listdir(yd)) if os.path.isdir(yd) else []
                vs = [v for v in vs if v != "yall"] + [f"y{y}" for y in ys]
            for v in vs:
                try:
                    print(e["slug"], v, compute_probs(e, v), flush=True)
                except Exception as ex:                              # noqa: BLE001
                    print(e["slug"], v, "FAILED", repr(ex)[:300], flush=True)
    else:
        evaluate(a.which, a.variant, a.tag, a.slugs)
