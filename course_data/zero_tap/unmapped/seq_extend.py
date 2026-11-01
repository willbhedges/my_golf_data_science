"""Extend sequence_v3's unmapped-tier results to courses added to the unmapped tiers after its Actions run.

    # solve (same settings as zero_tap_seqv3.yml request zt_seqv3_v3: form_w 3, chosen card variant c2, c0 for no-card)
    ZT_PAIRS_FORM_W=3 ZT_STRUCT_FALLBACK=1 ZT_CARD_W=0 python course_data/zero_tap/sequence/run_bench.py solve \
        --tiers unmapped_nocard --slugs <new> --pairs-root course_data/zero_tap/formation/hole_pairs --out zb_c0.json
    ZT_PAIRS_FORM_W=3 ZT_STRUCT_FALLBACK=1 ZT_CARD_W=2 ZT_CARD_NEST=1 python ... --tiers unmapped_card ... --out zb_c2.json
    python course_data/zero_tap/unmapped/seq_extend.py zb_c0*.json zb_c2*.json

The certainty gate is NOT refitted: the committed v3 gate (sequence/results/v3/gate_params.json, fitted on dev in the
original run) is applied as-is, exactly like gate2 applies it to test courses. Caveat for DEV rows only: the
original run read out-of-fold hole_pairs for dev (artifact zt-hp-oof, not downloadable here), these use the
committed (in-sample for formation) hole_pairs, so dev numbers of the added courses are optimistic.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [ZT]
import bench as B  # noqa: E402  (zero_tap/bench.py; sequence/ has its own bench.py, so it goes on the path after)
sys.path.insert(1, os.path.join(ZT, "sequence"))
import gate as GT  # noqa: E402

METHOD = "sequence_v3"


def main(paths):
    gp = json.load(open(os.path.join(ZT, "sequence", "results", "v3", "gate_params.json")))
    n = 0
    for p in paths:
        for r in GT._read(p):
            res, dg = r["result"], r.get("diag") or {}
            if dg:
                s = float(GT.score(gp["model"], GT.features(dg, gp["feats"])[None])[0])
                ok = GT.hard_ok(dg)
                conf = float(GT.iso_apply(gp["iso"]["x"], gp["iso"]["v"], [s])[0])
                certain = bool(ok and s >= gp["threshold_score"])
            else:
                s, ok, conf, certain = None, False, 0.0, False
            res.update(method=METHOD, version="v3", certain=certain, confidence=round(conf if ok else min(conf, 0.5), 4),
                       gate=dict(score=None if s is None else round(s, 4), threshold=gp["threshold_score"], hard_ok=ok,
                                 version=gp["schema"], dev_scores="committed v3 gate applied (unmapped/seq_extend.py)"),
                       pairs_note=None if r["split"] == "test" else "dev: committed hole_pairs (not out-of-fold)")
            B.write_result(res, os.path.join(ZT, "results", METHOD, r["tier"]))
            n += 1
    print(n, "results written")


if __name__ == "__main__":
    main(sys.argv[1:])
