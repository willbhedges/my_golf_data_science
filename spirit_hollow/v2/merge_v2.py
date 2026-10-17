"""Merge the v2 Actions parts (plan_spirit_hollow_v2.yml) into spirit_hollow/v2/output/.

  python3 spirit_hollow/v2/merge_v2.py PARTS_DIR
    v2dec_*.json  -> output/v2_decisions.json
    v2wind_*.json -> output/wind_grid.json / wind_grid_back<+N>.json
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["1", "2B", "2F", "4", "5", "6", "8", "9B", "9F", "10", "11", "13", "14", "16", "17", "18"]


def main(parts):
    out = os.path.join(HERE, "output")
    os.makedirs(out, exist_ok=True)
    dec = {}
    for p in sorted(glob.glob(os.path.join(parts, "**", "v2dec_*.json"), recursive=True)):
        dec.update(json.load(open(p)))
    if dec:
        dec = {k: dec[k] for k in ORDER if k in dec}
        json.dump(dec, open(os.path.join(out, "v2_decisions.json"), "w"), indent=1)
        print("v2_decisions:", len(dec), "holes")
    grids = {}
    for p in sorted(glob.glob(os.path.join(parts, "**", "v2wind_*.json"), recursive=True)):
        d = json.load(open(p))
        g = grids.setdefault(d["back"], dict(speeds=d["speeds"], dirs=d["dirs"], temps=[], bearings={}, holes={},
                                             par3={}, tee_back=d["back"], model="v2"))
        g["temps"] = sorted(set(g["temps"]) | set(d.get("temps", [])))
        for h, byT in d["holes"].items():
            g["holes"].setdefault(h, {}).update(byT)
        g["bearings"].update(d["bearings"])
        g["par3"].update(d["par3"])
    for b, g in grids.items():
        name = "wind_grid.json" if not b else f"wind_grid_back{b:+.0f}.json"
        json.dump(g, open(os.path.join(out, name), "w"))
        print(name, len(g["holes"]), "holes")


if __name__ == "__main__":
    main(sys.argv[1])
