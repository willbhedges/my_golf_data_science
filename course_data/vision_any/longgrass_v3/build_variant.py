"""LOCO model -> full-grid P(native) on the held-out course -> variant packages.
python3 build_variant.py <wt> <featset> <outdir> <thr,...> <gate> slug...
Gate: if predicted share (P>=thr) of the course-wide eligible sample < gate, the course gets no long grass."""
import os, sys, json, copy, numpy as np
os.environ.setdefault("OMP_NUM_THREADS", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
WT, FS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
thrs = [float(t) for t in sys.argv[4].split(",")]; gate = float(sys.argv[5]); slugs = sys.argv[6:]
sys.path.insert(0, HERE)
from common import *
import model_lib as ML
sys.path.insert(0, os.path.join(WT, "course_data/vision_any"))
import v2_longgrass_cv as CV
CV.install_truth_labels()
import v2_model as VM, v2_calibrate as C, layers as L
from shapely.geometry import mapping
from shapely.ops import transform
PK = {"mozingo": "mozingo_lake"}
for slug in slugs:
    clf, N = ML.fit_loco(FS, slug)
    D = VM.prepare(slug); S, F = D["S"], D["F"]
    el = D["elig_rel"] & ~D["water0"] & D["course"]
    idx = np.flatnonzero(el.ravel())
    p = np.zeros(S.H * S.W, np.float32)
    for i in range(0, len(idx), 400000):
        j = idx[i:i + 400000]; p[j] = clf.predict_proba(ML.features_for_grid(FS, slug, F, j))[:, 1]
    p = p.reshape(S.H, S.W)
    np.save(os.path.join(OUT, f"p_{FS}_{slug}.npy"), (p * 255).astype(np.uint8))
    vd = os.path.join(WT, "course_data/vision_any", slug)
    fc0 = json.load(open(os.path.join(vd, "vision_any.geojson")))
    fc0["features"] = [f for f in fc0["features"] if f["properties"]["lie"] != "native"]
    # strict eligibility against the committed trees (same as v2_longgrass_eb_build)
    import rasterio
    with rasterio.open(os.path.join(vd, "layers_v2.tif")) as r:
        cls = r.read(1)
    elS = D["elig"] & ~D["water0"] & D["course"] & (cls != 2) & (cls != 3)
    for thr in thrs:
        nat = VM.native_mask(p, elS, thr, S.res)
        share = nat.sum() / max(elS.sum(), 1)
        feats = []
        if share >= gate:
            S.ll_to_rc([[0, 0]])
            for g in L.mask_to_polys(S, nat, min_yd2=150, simplify_yd=2.0):
                gm = transform(lambda x, y: S._fwd.transform(x, y), g)
                feats.append(dict(type="Feature", geometry=mapping(g), properties=dict(
                    lie="native", src="vision3:loco_experiment", p=0.5, area_yd2=round(gm.area / 0.9144 ** 2), model="experiment")))
        fc = copy.deepcopy(fc0); fc["features"] = feats + fc["features"]
        pk = C.rebuild_package(PK.get(slug, slug), fc)
        od = os.path.join(OUT, f"{FS}_t{thr}_g{gate}", PK.get(slug, slug)); os.makedirs(od, exist_ok=True)
        json.dump(pk, open(os.path.join(od, "package.json"), "w"))
        print(slug, thr, "share %.4f" % share, "polys", len(feats), flush=True)
