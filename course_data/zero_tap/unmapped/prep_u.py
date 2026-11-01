"""pathroute (v1 + v2) feature caches for the unmapped tiers: the perception scene's golf layer as an OSM-style fc.

    python course_data/zero_tap/unmapped/prep_u.py --out CU [--split all] [--g-min 0] [--t-min 0] [--extra-tees]

Writes CU/<slug>.pkl in the merged format run2.load() produces (v1 dict + hX2/tpp/tpX, hX widened); dev rows
carry truth labels (training only), test rows none.
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import time
import traceback
from multiprocessing import Pool

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(ZT))
sys.path[:0] = [HERE, os.path.join(ZT, "pathroute_v2"), os.path.join(ZT, "pathroute"), ZT]
import bench as B  # noqa: E402
import scene as S  # noqa: E402
import features as F  # noqa: E402
import features2 as F2  # noqa: E402
import prep as P1  # noqa: E402
import prep2 as P2  # noqa: E402
import scene_fc as SF  # noqa: E402


def build(row, kw):
    x = B.inputs(row, "unmapped_nocard")
    seg = x.get("segment") if kw.get("extra_tees") else None
    pads = x.get("pads") if kw.get("extra_tees") else None
    fc = SF.unmapped_fc(x["fc"], x["scene"], pads=pads, seg=seg, **kw)
    sc = S.Scene(fc, x["course"])
    hp, hX = F.hole_feats(sc)
    tp, tX = F.trans_feats(sc)
    cT, cG = F.club_feats(sc)
    lab = P1.labels(sc, B.truth(row["slug"])) if row["split"] == "dev" else None
    d = dict(slug=row["slug"], split=row["split"], kind=row["kind"], hp=hp, hX=hX, tp=tp, tX=tX, cT=cT, cG=cG,
             lab=lab, club_src=sc.club_src, n_nodes=len(sc.nodes),
             greens=[dict(id=g["id"], ll=sc.pj.inv(*g["c"]), r=g["r"]) for g in sc.greens],
             tees=[dict(id=tt["id"], ll=sc.pj.inv(*tt["c"]), c=tt["c"], ax=tt["ax"], L=tt["L"]) for tt in sc.tees],
             gc=sc.gc, tc=sc.tc, club=sc.club)
    pr = P2._props(fc, sc)
    hX2 = F2.hole2_feats(sc, d["hp"], pr)
    pp, pX = F2.tee_pairs(sc, pr)
    d.update(hX2=hX2, tpp=pp, tpX=pX)
    if lab:
        th = lab["tee_h"]
        d["tpy"] = [int(bool(th[a] & th[b])) for a, b in pp]
    d["hX"] = np.c_[d["hX"], hX2]
    # perception confidences per scene element (for features / gating later)
    d["green_props"] = pr["greens"]
    d["tee_props"] = pr["tees"]
    return d


def one(args):
    row, out, kw = args
    o = os.path.join(out, row["slug"] + ".pkl")
    if os.path.exists(o):
        return row["slug"], "cached"
    t0 = time.time()
    try:
        d = build(row, kw)
        st = f"ok {time.time() - t0:.1f}s g={len(d['greens'])} t={len(d['tees'])}"
    except Exception as e:
        d = dict(slug=row["slug"], split=row["split"], kind=row["kind"], error=repr(e))
        st = "ERR " + traceback.format_exc().splitlines()[-1]
    pickle.dump(d, open(o, "wb"))
    return row["slug"], st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--split", default="all")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--g-min", type=float, default=0.0)
    ap.add_argument("--t-min", type=float, default=0.0)
    ap.add_argument("--f-min", type=float, default=0.0)
    ap.add_argument("--extra-tees", action="store_true")
    ap.add_argument("--tee-mode", default="boxes", choices=("boxes", "complex"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    kw = dict(g_min=a.g_min, t_min=a.t_min, f_min=a.f_min, extra_tees=a.extra_tees, tee_mode=a.tee_mode)
    json.dump(kw, open(os.path.join(a.out, "_config.json"), "w"))
    rows = B.courses(None if a.split == "all" else a.split, tier="unmapped_card")
    with Pool(a.jobs) as p:
        for slug, st in p.imap_unordered(one, [(r, a.out, kw) for r in rows]):
            print(slug, st, flush=True)


if __name__ == "__main__":
    main()
