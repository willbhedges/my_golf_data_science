"""Which courses / states the perception models may learn from (leakage control, UNMAPPED.md).

The zero-tap benchmark splits courses by state (zero_tap/state_split.json, frozen) with one exception: the 31
generalize validation-set test courses sit in dev states but stay in test. The perception models therefore:

  * train only on courses whose state is a bench **dev** state AND that are not a bench **test** course
    (`role(slug, state) == "pool"`); every bench test course and every course in a bench test state is held out;
  * for dev tuning, the pool's states are split into K state folds (`fold_plan`); fold model k is trained on the
    pool minus fold k's states, and perceive.py uses it for every course in those states (dev courses AND the
    validation-set test courses there), so every scene of a dev-state course is out-of-state;
  * courses in bench test states (and states the bench does not know) are perceived with the final model
    (whole pool), which never saw their state.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.join(os.path.dirname(HERE), "zero_tap")
K_FOLDS = 5


def _load():
    st = json.load(open(os.path.join(ZT, "state_split.json")))["states"]
    bench = {}
    bp = os.path.join(ZT, "benchmark.json")
    if os.path.exists(bp):
        for c in json.load(open(bp))["courses"]:
            bench[c["slug"]] = c.get("split")
    return st, bench


_ST, _BENCH = _load()


def bench_split(slug):
    return _BENCH.get(slug)


def state_split(state):
    return _ST.get(str(state or "").upper())


def role(slug, state):
    """'pool' = may be used to train; 'heldout' = never trained on (bench test course or not a dev state)."""
    if bench_split(slug) == "test" or state_split(state) != "dev":
        return "heldout"
    return "pool"


def fold_plan(pool_courses, k=K_FOLDS):
    """Greedy balanced assignment of the pool's states to k folds by course count (deterministic)."""
    cnt = {}
    for slug, state in pool_courses:
        cnt[str(state).upper()] = cnt.get(str(state).upper(), 0) + 1
    folds = [[] for _ in range(k)]
    load = [0] * k
    for s in sorted(cnt, key=lambda s: (-cnt[s], s)):
        j = min(range(k), key=lambda i: (load[i], i))
        folds[j].append(s)
        load[j] += cnt[s]
    return [sorted(f) for f in folds]


def models_dir_for(state, models_root):
    """The model set perceive.py must use for a course in `state`: the fold that held its state out, else final."""
    fp = os.path.join(models_root, "folds.json")
    if os.path.exists(fp):
        for f in json.load(open(fp))["folds"]:
            if str(state or "").upper() in f["held_out_states"]:
                d = os.path.join(models_root, f["dir"])
                if os.path.isdir(d):
                    return d
    return models_root
