"""Which geometry corrections (geom.py) change a pick or aim? Central world, each fix alone and all.

  python3 spirit_hollow/v2/geometry_check.py   -> spirit_hollow/v2/output/geometry_check.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import decide as D                              # noqa: E402
import geom                                     # noqa: E402
import model as M                               # noqa: E402

CONFIGS = [("course.py as is", ""), ("ground yards", "scale"), ("Black-tee elevation", "elev"),
           ("OSM green", "green"), ("all three", "scale,elev,green")]


def main():
    n = int(os.environ.get("GEOM_SWINGS", 5000))
    out = {"summary": {k: {kk: (vv if not hasattr(vv, "item") else vv.item()) for kk, vv in v.items()}
                       for k, v in geom.summary().items()}}
    for name, flags in CONFIGS:
        geom.set_geometry(flags)
        res = {}
        for h in M.HOLES:
            r = D.solve_world(h, D.central(h), n)
            res[str(h)] = dict(pick=r["pick"], aim=r["aim"], margin=round(r["margin"], 4), runner=r["runner"])
        out[name] = res
        print(name, {h: f"{v['pick']} {v['aim']:+.1f}" for h, v in res.items()}, flush=True)
    geom.set_geometry("")
    os.makedirs(os.path.join(HERE, "output"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "output", "geometry_check.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
