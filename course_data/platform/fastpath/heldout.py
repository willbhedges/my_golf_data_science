"""Detection benchmark sets for unmapped courses (perception side): TEST (held out, never tuned on), VAL (tuning)
and TRAIN (second-stage object models), each course fetched as a fast-path package simulated as unmapped.

    python3 heldout.py list                       # the three sets (slugs, sources), leakage checks
    python3 heldout.py fetch test|val|train [--max N] [slug ...]   # NAIP + DEM + canopy + OSM -> cache/heldout/<slug>

Simulated unmapped: the detector never reads an OSM golf feature (fastscene uses the course outline and non-golf
OSM buildings / roads only); the NAIP year is the newest covering one ("latest", what an unmapped course gets: the
year scoring needs OSM turf). OSM golf polygons are read only by the scorer (evaluate_scene.py).

Sets (`sets()`):
  TEST  the blind-loop tier A / B courses (cache/packages/b20_*, fetched by the blind loop; Pheasant Ridge IA is
        dropped: its OSM id is in the U-Net's training index) + the 31 generalize validation-set test courses
        (bench test courses: no perception model was trained on them; the U-Net trained on IA / MO only)
  VAL   the generalize validation-set train courses (51, perception "pool"), not in the U-Net training index
  TRAIN perception stacks_meta pool courses not in VAL, not in the U-Net training index
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(HERE)
CD = os.path.dirname(PLAT)
ROOT = os.path.join(HERE, "cache", "heldout")
PKGS = os.path.join(HERE, "cache", "packages")
B20 = ["b20_crow_canyon", "b20_chevy_chase", "b20_cedar_glen", "b20_kittansett", "b20_zintel_creek",
       "b20_at_cedar_creek", "b20_falls_village", "b20_maplewood", "b20_twisted_pine"]


def _unet_train_ids():
    p = os.path.join(CD, "segment", "train", "dataset_index.json")
    return set(json.load(open(p))["courses"]) if os.path.exists(p) else set()


def _osm_id(o):
    if isinstance(o, dict):
        return f"{o.get('type')}/{o.get('id')}"
    return str(o)


def sets():
    vs = json.load(open(os.path.join(CD, "generalize", "validation_set.json")))
    bad = _unet_train_ids()
    test = [dict(slug=s, dir=os.path.join(PKGS, s), src="b20") for s in B20]
    val = []
    for c in vs["courses"]:
        if c.get("status") != "ok" or c["osm"] in bad:
            continue
        e = dict(slug=c["slug"], dir=os.path.join(ROOT, c["slug"]), src="generalize", state=c["state"],
                 course=os.path.join(os.path.dirname(CD), c["dir"], "course.json"))
        (test if c["split"] == "test" else val).append(e)
    vslugs = {e["slug"] for e in val} | {e["slug"] for e in test}
    sys.path.insert(0, os.path.join(CD, "perception"))
    import split as SP
    train = []
    for p in sorted(glob.glob(os.path.join(CD, "perception", "stacks_meta", "*.json"))):
        m = json.load(open(p))
        slug = os.path.basename(p)[:-5]
        c = m.get("course") or {}
        if slug in vslugs or SP.role(slug, m.get("state")) != "pool" or _osm_id(c.get("osm")) in bad:
            continue
        if not (c.get("boundary") or m.get("boundary")) or not (c.get("bbox") or m.get("bbox_wsen")):
            continue
        train.append(dict(slug=slug, dir=os.path.join(ROOT, slug), src="stacks_meta", state=m.get("state"),
                          meta=p))
    return dict(test=test, val=val, train=train)


def course_dict(e):
    if e.get("course"):
        return json.load(open(e["course"]))
    m = json.load(open(e["meta"]))
    c = dict(m["course"])
    c.update(schema="course/1", status="ok", slug=e["slug"], state=m.get("state"),
             bbox=c.get("bbox") or m.get("bbox_wsen"), boundary=c.get("boundary") or m.get("boundary"))
    return c


def to_06(img_dir, res=0.6):
    """0.3 m NAIP -> 0.6 m (area average, what fastscene.unet_probs feeds the U-Net anyway; grid_stack averages to
    1 m): a quarter of the disk. Rewritten in place (JPEG COGs as fast_imagery writes them); georef.json notes it."""
    import numpy as np
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.transform import Affine
    from rasterio.warp import reproject
    sys.path.insert(0, HERE)
    import fast_imagery as fim
    gp = os.path.join(img_dir, "georef.json")
    if not os.path.exists(gp):
        return False
    g = json.load(open(gp))
    im = g.get("imagery") or {}
    if not im or im.get("resolution_m", 1.0) > 0.5:
        return False
    for name, q in (("naip_rgb.tif", 90), ("naip_nir.tif", 92)):
        p = os.path.join(img_dir, name)
        if not os.path.exists(p):
            continue
        with rasterio.open(p) as s:
            a, tr, crs = s.read(), s.transform, s.crs
        f = res / abs(tr.a)
        H6, W6 = int(round(a.shape[1] / f)), int(round(a.shape[2] / f))
        tr6 = tr * Affine.scale(a.shape[2] / W6, a.shape[1] / H6)
        o = np.zeros((a.shape[0], H6, W6), np.float32)
        for k in range(a.shape[0]):
            reproject(a[k].astype(np.float32), o[k], src_transform=tr, src_crs=crs, dst_transform=tr6, dst_crs=crs,
                      resampling=Resampling.average)
        fim.write_cog(p, np.clip(np.round(o), 0, 255).astype(np.uint8), crs, tr6, q)
    im.update(resolution_m_fetched=im["resolution_m"], resolution_m=res, note="averaged to 0.6 m by heldout.to_06")
    json.dump(g, open(gp, "w"), indent=1)
    return True


def fetch_one(e, log=print):
    """-> seconds; skips what is already there"""
    sys.path.insert(0, HERE)
    sys.path.insert(0, PLAT)
    import osm_api
    d = e["dir"]
    t0 = time.time()
    raw = os.path.join(d, "raw")
    os.makedirs(raw, exist_ok=True)
    course = course_dict(e)
    if not os.path.exists(os.path.join(raw, "course.json")):
        json.dump(course, open(os.path.join(raw, "course.json"), "w"))
    if not os.path.exists(os.path.join(raw, "osm.geojson")):
        osm_api.features(course, raw, os.path.join(HERE, "cache"))
    if not os.path.exists(os.path.join(d, "imagery", "georef.json")):
        import fast_imagery as fim
        fim.fetch(course["bbox"], os.path.join(d, "imagery"), None, "latest", label=course.get("name"))
    to_06(os.path.join(d, "imagery"))
    if not os.path.exists(os.path.join(d, "canopy", "chm_meta.tif")):
        import canopy
        canopy.fetch(course["bbox"], os.path.join(d, "canopy"))
    for junk in ("naip_rgb_lo.jpg", "naip_nir_lo.jpg"):
        p = os.path.join(d, "imagery", junk)
        if os.path.exists(p):
            os.remove(p)
    for junk in ("osm_raw.json",):
        p = os.path.join(raw, junk)
        if os.path.exists(p):
            os.remove(p)
    return round(time.time() - t0, 1)


def fetch_years(e, k=2, min_year=2012):
    """the k newest other NAIP years (coverage > 0.9, 4 bands) besides the package's own -> years/<year>/naip_*.tif
    (multi-year fusion: different seasons separate greens from fairways differently). -> [years written]"""
    sys.path.insert(0, HERE)
    import fast_imagery as fim
    d = e["dir"]
    g = json.load(open(os.path.join(d, "imagery", "georef.json")))
    have = g.get("imagery", {}).get("year")
    padded = g["padded_bbox_wgs84_snwe"]
    yd = os.path.join(d, "years")
    done = sorted(int(x) for x in os.listdir(yd)) if os.path.isdir(yd) else []
    if len(done) >= k:
        return done
    ys = fim.list_years(tuple(padded))
    ys = [y for y in ys if y["coverage"] > 0.9 and y["year"] != have and y["year"] >= min_year]
    out = []
    for y in reversed(ys):
        if len(out) >= k:
            break
        o = os.path.join(yd, str(y["year"]))
        if not os.path.exists(os.path.join(o, "naip_nir.tif")):
            os.makedirs(o, exist_ok=True)
            try:
                im = fim.fetch_naip(tuple(padded), o, 0.6, year=str(y["year"]))
                json.dump(dict(imagery=im), open(os.path.join(o, "georef.json"), "w"), indent=1)
                to_06(o)
            except Exception as ex:                                  # noqa: BLE001
                print(e["slug"], y["year"], "failed", repr(ex)[:200])
            for junk in ("naip_rgb_lo.jpg", "naip_nir_lo.jpg"):
                if os.path.exists(os.path.join(o, junk)):
                    os.remove(os.path.join(o, junk))
        if os.path.exists(os.path.join(o, "naip_nir.tif")):
            out.append(y["year"])
        else:
            import shutil
            shutil.rmtree(o, ignore_errors=True)
    return out


def ok(e):
    d = e["dir"]
    return all(os.path.exists(os.path.join(d, p)) for p in ("raw/osm.geojson", "imagery/naip_rgb.tif",
                                                            "imagery/naip_nir.tif"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "fetch", "years"])
    ap.add_argument("which", nargs="?", default="test")
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--max", type=int, default=0)
    a = ap.parse_args()
    S = sets()
    if a.cmd == "list":
        for k, v in S.items():
            print(k, len(v), sum(ok(e) for e in v), " ".join(e["slug"] for e in v))
        sys.exit(0)
    todo = [e for e in S[a.which] if (not a.slugs or e["slug"] in a.slugs) and e["src"] != "b20"]
    if a.max:
        todo = todo[:a.max]
    if a.cmd == "years":
        todo = [e for e in S[a.which] if (not a.slugs or e["slug"] in a.slugs) and ok(e)][:a.max or None]
    for e in todo:
        try:
            print(e["slug"], fetch_years(e) if a.cmd == "years" else fetch_one(e), "s", flush=True)
        except Exception as ex:                                      # noqa: BLE001
            print(e["slug"], "FAILED", repr(ex)[:300], flush=True)
