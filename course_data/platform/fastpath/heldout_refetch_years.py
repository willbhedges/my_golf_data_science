"""Re-fetch the extra NAIP years of a heldout.py set whose GeoTIFFs were deleted to save disk (cache/heldout/
clean_years.py keeps only years/<year>/georef.json once the probabilities are cached). Same request as
fast_imagery.fetch_years (the package's padded box, 0.6 m, that year), so the U-Net sees the same imagery.

    python3 heldout_refetch_years.py test [--workers 4] [slug ...]
    python3 heldout_refetch_years.py test --clean        # delete the tifs again (keeps georef.json)
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fast_imagery as fim  # noqa: E402
import heldout as HO  # noqa: E402


def refetch(e, y):
    o = os.path.join(e["dir"], "years", str(y))
    if os.path.exists(os.path.join(o, "naip_rgb.tif")) and os.path.exists(os.path.join(o, "naip_nir.tif")):
        return "have"
    g = json.load(open(os.path.join(e["dir"], "imagery", "georef.json")))
    keep = json.load(open(os.path.join(o, "georef.json")))
    im = fim.fetch_naip(tuple(g["padded_bbox_wgs84_snwe"]), o, 0.6, year=str(y))
    for junk in ("naip_rgb_lo.jpg", "naip_nir_lo.jpg"):
        if os.path.exists(os.path.join(o, junk)):
            os.remove(os.path.join(o, junk))
    if "nir" not in im.get("files", {}):
        raise RuntimeError("no NIR band")
    if sorted(im.get("items") or []) != sorted((keep.get("imagery") or {}).get("items") or []):
        print(e["slug"], y, "items differ from the cached georef", flush=True)
    json.dump(dict(imagery=im), open(os.path.join(o, "georef.json"), "w"), indent=1)
    fim.to_06(o)
    return "fetched"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("which")
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--clean", action="store_true")
    a = ap.parse_args()
    es = [x for x in HO.sets()[a.which] if (not a.slugs or x["slug"] in a.slugs) and HO.ok(x)]
    if a.clean:
        n = 0
        for e in es:
            for f in glob.glob(os.path.join(e["dir"], "years", "*", "*.tif")):
                n += os.path.getsize(f)
                os.remove(f)
        print(round(n / 1e6), "MB freed")
        sys.exit(0)
    jobs = [(e, int(y)) for e in es for y in (sorted(os.listdir(os.path.join(e["dir"], "years")))
                                               if os.path.isdir(os.path.join(e["dir"], "years")) else [])]

    def run(j):
        try:
            return j[0]["slug"], j[1], refetch(*j)
        except Exception as ex:                                      # noqa: BLE001
            return j[0]["slug"], j[1], "FAILED " + repr(ex)[:200]
    with ThreadPoolExecutor(a.workers) as ex:
        for r in ex.map(run, jobs):
            print(*r, flush=True)
