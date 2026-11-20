"""Course list for the v3 tee-targeted U-Net fine-tune: v2's draw (pick_v2.py: national index, strict label filter,
every evaluation course excluded with a 1.5 km buffer) with the v2 training courses (v2_courses.json) also excluded,
id and 1.5 km, so v3 only adds courses.

    python course_data/segment/train/pick_v3.py [--per-state 1000 (no cap: v2 took the states it capped)] [--n 3000]
        -> course_data/segment/train/v3_courses.json (build_dataset.py --courses ... --quality --tee-quality)

Label filter as v2 (outline, greens / tees >= holes, fairways >= 0.6 x holes). The tee-label quality filter needs
the real polygons, so it runs in build_dataset.py --tee-quality (tee_quality()). Run locally (needs the TRAIN-BIG
manifest, cache/big/manifest.json, not committed).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pick_v2 as P2                                            # noqa: E402

SEED = 20261120
OUT = os.path.join(HERE, "v3_courses.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-state", type=int, default=1000)
    ap.add_argument("--n", type=int, default=3000)
    a = ap.parse_args()
    base = P2.exclusions

    def exclusions():
        ids, cen, n = base()
        v2 = json.load(open(os.path.join(HERE, "v2_courses.json")))["courses"]
        for c in v2:
            ids.add(c["osm"])
            cen.append([c["lon"], c["lat"]])
        n["v2_courses"] = len(v2)
        return ids, cen, n

    P2.exclusions, P2.SEED, P2.OUT = exclusions, SEED, OUT
    sys.argv = [sys.argv[0], "--per-state", str(a.per_state), "--n", str(a.n)]
    P2.main()
    d = json.load(open(OUT))
    d["schema"] = "segment_v3_courses/1"
    json.dump(d, open(OUT, "w"), indent=0)


if __name__ == "__main__":
    main()
