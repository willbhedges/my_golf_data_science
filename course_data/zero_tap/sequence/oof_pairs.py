"""Out-of-fold hole_pairs/1 for the benchmark's DEV courses (workstream C's gate needs honest per-pair certainty).

Workstream A's committed formation/hole_pairs/ were made with model.pkl, which was trained on every dev-state course,
so on D's dev split (all 77 courses are A training courses) p and p_corridor are in-sample (formed 91-94 % vs 82-87 %
on test). A certainty gate fitted on those would trust p_corridor more than it deserves on new courses. This script
refits A's model per state fold exactly as formation.cv does (6 folds by state, stage 1 on the other folds' training
rows, stage 2 on the stage-1 out-of-fold logits of the other folds' courses; the Sinkhorn temperature / slack `cal` is
A's own, itself fitted on out-of-fold predictions) and writes, for every dev benchmark course and tier, hole_pairs/1
from the model that never saw that course's state.

    ZT_FORMATION_CACHE=/tmp/zfc python course_data/zero_tap/formation/formation.py build --procs 4
    ZT_FORMATION_CACHE=/tmp/zfc python course_data/zero_tap/sequence/oof_pairs.py models --out /tmp/oofm
    python course_data/zero_tap/sequence/oof_pairs.py pairs --models /tmp/oofm --tier nocard --out hp_oof

Test courses keep A's committed files (A's model never saw them).
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
FDIR = os.path.join(ZT, "formation")
sys.path[:0] = [FDIR, ZT]


def models(out):
    import formation as FM
    rows = FM.load_cache()
    tr = [r for r in rows if r["split"] == "train"]
    fs = FM.folds({r["state"] for r in tr}, 6)
    cal = pickle.load(open(FM.MODEL, "rb"))["cal"]
    os.makedirs(out, exist_ok=True)
    clfs, oof1 = [], {}
    for i, f in enumerate(fs):
        clf = FM.fit_model(FM.train_rows([r for r in tr if r["state"] not in f]))
        clfs.append(clf)
        for r in tr:
            if r["state"] in f:
                oof1[id(r)] = (r, FM.pair_logit(clf, r))
        print("stage 1 fold", i, sorted(f), flush=True)
    index = {}
    for i, f in enumerate(fs):
        c2 = FM.fit_stage2([oof1[id(r)] for r in tr if r["state"] not in f]) if FM.STAGES >= 2 else None
        p = os.path.join(out, f"model_fold{i}.pkl")
        pickle.dump(dict(clf=clfs[i], clf2=c2, cal=cal, fold=i, states=sorted(f),
                         trained_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + f"-oof{i}"), open(p, "wb"))
        for s in f:
            index[s] = p
        print("stage 2 fold", i, flush=True)
    json.dump(index, open(os.path.join(out, "index.json"), "w"), indent=1)


def pairs(models_dir, tier, out):
    import bench as B
    import data as D
    import hole_pairs as HP
    import scene as S
    index = json.load(open(os.path.join(models_dir, "index.json")))
    od = os.path.join(out, tier)
    os.makedirs(od, exist_ok=True)
    n = 0
    for row in B.courses("dev"):
        try:
            mp = index[row["state"]]
            inp = B.inputs(row, tier)
            if tier.startswith("unmapped"):
                obj = inp.get("scene") or D.perception_scene_obj(row["slug"])
                if not obj:
                    continue
                sc = S.scene_from_perception(obj)
            else:
                sc = S.scene_from_osm(inp["fc"], (inp.get("course") or {}).get("boundary"))
            aux = os.path.join(D.INPUTS, row["slug"], "aux.npz")
            hp = HP.hole_pairs(sc, inp.get("card"), aux if os.path.exists(aux) else None, model_path=mp, slug=row["slug"])
            hp.update(tier=tier, oof=dict(model=os.path.basename(mp), state=row["state"]))
            json.dump(hp, open(os.path.join(od, row["slug"] + ".json"), "w"), separators=(",", ":"))
            n += 1
        except Exception:                                            # noqa: BLE001
            traceback.print_exc()
    print(tier, n, "dev courses (out-of-fold)", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["models", "pairs"])
    ap.add_argument("--models")
    ap.add_argument("--tier")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.what == "models":
        models(a.out)
    else:
        pairs(a.models, a.tier, a.out)


if __name__ == "__main__":
    main()
