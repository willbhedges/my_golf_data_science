"""Long grass at a P(native) threshold, rebuilt into the packages, for the error budget (v2_longgrass_eb.md).

  python3 course_data/vision_any/v2_longgrass_eb_build.py <repo root> <out dir> 0.04,0.3,0.5 blue_hills,ellis
  -> <out dir>/t<thr>/<slug>/package.json (+ <out dir>/control/<slug>/package.json: same rebuild, no long grass)

P(native) = band 2 of the committed course_data/vision_any/<slug>/layers_v2.tif (the product model, trained on the
Spirit Hollow + Mozingo hand maps only, so out of sample on every other course). Eligible = cells the product
scored (course outline minus OSM fairway / green / tee / bunker / roads / bright pixels) minus the committed trees
and water (band 1), i.e. v2_model.infer's strict mode with dmin 0, gate 0; then v2_model.native_mask. The package
is the committed one with its vision zones replaced (v2_calibrate.rebuild_package, OB re-inferred). Needs no raw2.
Experiment only: nothing here writes into course_data/packages or vision_any/<slug>."""
import os, sys, json, copy
os.environ.setdefault("OMP_NUM_THREADS", "1")
WT = sys.argv[1]; OUT = sys.argv[2]; thrs = [float(x) for x in sys.argv[3].split(",")]
slugs = sys.argv[4].split(",")
VA = os.path.join(WT, "course_data", "vision_any")
sys.path.insert(0, VA)
import numpy as np, rasterio
import layers as L
import v2_model as V
import v2_calibrate as C
for slug in slugs:
    d = os.path.join(VA, slug)
    with rasterio.open(os.path.join(d, "layers_v2.tif")) as r:
        cls, p8 = r.read(1), r.read(2)
        S = L.Stack(); S.crs = r.crs.to_string(); S.transform = r.transform; S.res = r.res[0]; S.H, S.W = r.shape
    p = p8.astype(np.float32) / 255.0
    el = (p8 > 0) & (cls != 2) & (cls != 3)          # region (course, eligible) & ~trees (strict) & ~water
    fc0 = json.load(open(os.path.join(d, "vision_any.geojson")))
    assert not any(f["properties"]["lie"] == "native" for f in fc0["features"])
    for thr in thrs:
        nat = V.native_mask(p, el, thr, S.res)
        from scipy import ndimage
        lab, nl = ndimage.label(nat)
        means = ndimage.mean(p, lab, np.arange(1, nl + 1)) if nl else []
        feats = []
        from shapely.geometry import mapping
        from shapely.ops import transform
        S.ll_to_rc([[0, 0]])
        for g in L.mask_to_polys(S, nat, min_yd2=150, simplify_yd=2.0):
            gm = transform(lambda x, y: S._fwd.transform(x, y), g)
            feats.append(dict(type="Feature", geometry=mapping(g), properties=dict(
                lie="native", src="vision2:lgbm_naip_multiyear+lidar", p=0.5, area_yd2=round(gm.area / 0.9144 ** 2),
                model="vision_any/2")))
        fc = copy.deepcopy(fc0)
        fc["features"] = feats + fc["features"]
        fc["properties"]["native_how"] = f"EXPERIMENT thr {thr} strict on committed layers_v2 band 2"
        pk = C.rebuild_package(slug, fc)
        od = os.path.join(OUT, f"t{thr}", slug); os.makedirs(od, exist_ok=True)
        json.dump(pk, open(os.path.join(od, "package.json"), "w"))
        print(slug, thr, "native px share of region", round(nat.sum() / max(el.sum(), 1), 4), "polys", len(feats), flush=True)
    pk = C.rebuild_package(slug, fc0)
    od = os.path.join(OUT, "control", slug); os.makedirs(od, exist_ok=True)
    json.dump(pk, open(os.path.join(od, "package.json"), "w"))
