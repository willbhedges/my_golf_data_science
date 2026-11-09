"""joint routing: build and cache per-course candidates, geometry, features and (for fitting / scoring) labels.

    python course_data/zero_tap/joint/prep.py --source scene|truth|osm --out CACHE [--split all] [--procs 3]

One pickle per course: CACHE/<source>/<slug>.pkl = dict(row, co, geo, hp, hx, wp, wx, W, lab, card, card_kind).
"""
from __future__ import annotations

import argparse
import os
import pickle
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [HERE, ZT]
import bench as B  # noqa: E402
import cands as C  # noqa: E402
import feats as F  # noqa: E402


def build(row, source):
    tier = "unmapped_card" if source == "scene" else "osm_card"
    x = B.inputs(row, tier)
    t = B.truth(row["slug"])
    if source == "scene":
        co = C.from_scene(x["scene"], x["fc"])
    elif source == "truth":
        co = C.from_truth(t, x["fc"], seed=len(row["slug"]))
    else:
        co = C.from_osm(x["fc"])
    geo = F.geometry(co)
    hp, hx = F.hole_features(co, geo)
    wp, wx, W = F.walk_features(co, geo)
    card = x["card"] if x["card_kind"].startswith("web") else None       # an OSM-derived card is the truth: never used
    return dict(row=row, co=co, geo=geo, hp=hp, hx=hx, wp=wp, wx=wx, W=W, lab=C.label(co, t), card=card,
                card_kind=x["card_kind"], kind=row["kind"])


def _one(a):
    row, source, out = a
    p = os.path.join(out, source, row["slug"] + ".pkl")
    if os.path.exists(p):
        return row["slug"], None
    try:
        d = build(row, source)
    except Exception as e:
        return row["slug"], repr(e)
    pickle.dump(d, open(p, "wb"))
    return row["slug"], None


def load(cache, source, split=None, version=None):
    out = []
    tier = "unmapped_card" if source == "scene" else "osm_card"
    for r in B.courses(split, tier, version=version):
        p = os.path.join(cache, source, r["slug"] + ".pkl")
        if os.path.exists(p):
            out.append(pickle.load(open(p, "rb")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--split", default="all")
    ap.add_argument("--procs", type=int, default=3)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, a.source), exist_ok=True)
    tier = "unmapped_card" if a.source == "scene" else "osm_card"
    rows = B.courses(a.split, tier)
    with Pool(a.procs) as pool:
        for slug, err in pool.imap_unordered(_one, [(r, a.source, a.out) for r in rows]):
            if err:
                print("FAIL", slug, err, flush=True)
    print("done", len(rows))


if __name__ == "__main__":
    main()
