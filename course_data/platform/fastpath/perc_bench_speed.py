"""perc_bench.py with the U-Net probabilities cached under a separate root, for the accuracy gate of U-Net speed
changes (fastc/perception/unet_amx.py, unet_fast.py; fastc/perception/README.md "U-Net speed").

    python3 perc_bench_speed.py ROOT probs test d0+yall [--stride 384] [--impl amx|fp32|ref] [slug ...]
    python3 perc_bench_speed.py ROOT eval  test d0+yall --tag T [slug ...]

ROOT: a directory name under cache/heldout/ (e.g. probs_amx384) used in place of cache/heldout/probs. --stride:
the U-Net tile stride (the TEST reference probabilities, cache/heldout/probs, were computed at 384). --impl: the
forward pass (amx: AMX bf16; fp32: the float32 implicit-GEMM C pass; ref: unet.py's numpy / OpenBLAS pass).
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fastscene as FS  # noqa: E402
import heldout as HO  # noqa: E402
import perc_bench as PB  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("cmd", choices=["probs", "eval"])
    ap.add_argument("which")
    ap.add_argument("variant")
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--stride", type=int)
    ap.add_argument("--impl", default="auto")
    ap.add_argument("--tag")
    a = ap.parse_args()
    PB.PROBS = os.path.join(HO.ROOT, a.root)
    if a.impl != "auto":
        os.environ["FASTPERC_IMPL"] = a.impl
    if a.stride:
        _up = FS.unet_probs

        def unet_probs(*args, **kw):
            if kw.get("stride") is None:              # perc_bench passes stride=None explicitly
                kw["stride"] = a.stride
            return _up(*args, **kw)
        FS.unet_probs = unet_probs
    if a.cmd == "probs":
        for e in PB.entries(a.which, a.slugs):
            vs = a.variant.split("+")
            if "yall" in vs:
                yd = os.path.join(e["dir"], "years")
                ys = sorted(os.listdir(yd)) if os.path.isdir(yd) else []
                vs = [v for v in vs if v != "yall"] + [f"y{y}" for y in ys]
            for v in vs:
                try:
                    print(e["slug"], v, PB.compute_probs(e, v), flush=True)
                except Exception as ex:                              # noqa: BLE001
                    print(e["slug"], v, "FAILED", repr(ex)[:300], flush=True)
    else:
        PB.evaluate(a.which, a.variant, tag=a.tag, slugs=a.slugs)
