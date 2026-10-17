"""Merge per-hole Actions outputs (plan_spirit_hollow.yml) into the files the book and page read.

  python3 spirit_hollow/merge_parts.py PARTS_DIR
    final_*.json            -> output/final_decision.json (+ .md)
    wind_<back>_<hole>.json -> output/wind_grid.json (back 0) / output/wind_grid_back<+N>.json
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "mozingo"), HERE]


def main(parts):
    out = os.path.join(HERE, "output")
    fd = {}
    for p in sorted(glob.glob(os.path.join(parts, "**", "final_*.json"), recursive=True)):
        fd.update(json.load(open(p)))
    if fd:
        import course
        import final_decision as F
        order = [str(h) for h in course.HOLES]
        fd = {k: fd[k] for k in order if k in fd}
        json.dump(fd, open(os.path.join(out, "final_decision.json"), "w"), indent=1, default=float)
        F.write_md(fd)
        print("final_decision:", len(fd), "holes")
    grids = {}
    for p in sorted(glob.glob(os.path.join(parts, "**", "wind_*.json"), recursive=True)):
        d = json.load(open(p))
        g = grids.setdefault(d["back"], dict(speeds=[0, 5, 10, 15, 20, 25], dirs=list(range(0, 360, 30)),
                                             bearings={}, holes={}, par3={}, tee_back=d["back"]))
        g["holes"].update(d["holes"])
        g["bearings"].update(d["bearings"])
        g["par3"].update(d["par3"])
    for b, g in grids.items():
        name = "wind_grid.json" if not b else f"wind_grid_back{b:+.0f}.json"
        json.dump(g, open(os.path.join(out, name), "w"))
        print(name, len(g["holes"]), "holes")


if __name__ == "__main__":
    main(sys.argv[1])
