"""LOCO Sentinel-2 P(native) (10 m grid, held-out course) -> native polygons -> variant packages.
python3 s2_variant.py <wt> <pred.npz> <outdir> <name> <mode pix|ext|none> <thr> slug...
pix: v2_model.native_mask on the 10 m P upsampled to 1 m (strict eligibility).
ext: per package hole and side of the 150-340 yd corridor (|lat| <= 50 yds): native on every strict-eligible cell
     >= N yds from the OSM fairway, N = argmax sum_{cells >= N}(P - thr) over that side (none if <= 0).
none: the control (same rebuild, no long grass)."""
import os, sys, json, copy, numpy as np
os.environ.setdefault("OMP_NUM_THREADS", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
WT, PRED, OUT, NAME, MODE, THR = sys.argv[1:7]; THR = float(THR); slugs = sys.argv[7:]
sys.path.insert(0, HERE)
import s2lib as S2
sys.path.insert(0, os.path.join(WT, "course_data/vision_any"))
import v2_longgrass_cv as CV
LB = CV.install_truth_labels()
import v2_model as VM, v2_calibrate as C, layers as L
from shapely.geometry import mapping
from shapely.ops import transform
PK = {"mozingo": "mozingo_lake"}
YD = 0.9144
P = np.load(PRED) if MODE != "none" else None


def base_fc(slug, pk):
    p = os.path.join(WT, "course_data/vision_any", slug, "vision_any.geojson")
    if os.path.exists(p):
        fc = json.load(open(p))
        fc["features"] = [f for f in fc["features"] if f["properties"]["lie"] != "native"]
        return fc, True
    # truth_sets_v2 courses: no committed vision geojson; rebuild it from the package's own vision zones
    feats = []
    for h in pk["holes"].values():
        for z in h.get("zones_ll") or []:
            if str(z.get("src", "")).startswith("vision") and z["lie"] != "native":
                ring = z["poly"] if z["poly"][0] == z["poly"][-1] else z["poly"] + [z["poly"][0]]
                feats.append(dict(type="Feature", geometry=dict(type="Polygon", coordinates=[ring]),
                                  properties=dict(lie=z["lie"], src=z["src"], p=z.get("p", 0.5))))
    return dict(type="FeatureCollection", features=feats, properties=dict(schema="vision_any/2")), False


for slug in slugs:
    pslug = PK.get(slug, slug)
    pk0 = json.load(open(os.path.join(WT, "course_data/packages", pslug, "package.json")))
    fc0, have_v2 = base_fc(slug, pk0)
    feats = []
    if MODE != "none":
        D = VM.prepare(slug); S = D["S"]
        elS = D["elig"] & ~D["water0"] & D["course"]
        if have_v2:
            import rasterio
            with rasterio.open(os.path.join(WT, "course_data/vision_any", slug, "layers_v2.tif")) as r:
                cls = r.read(1)
            elS &= (cls != 2) & (cls != 3)
        g = S2.load_g10(slug)
        pg = P[slug + "_g"]
        rr, cc = np.mgrid[0:S.H, 0:S.W]
        p1 = pg[(rr + int(g["ro"])) // 10, (cc + int(g["co"])) // 10].astype(np.float32); del rr, cc
        if MODE == "pix":
            nat = VM.native_mask(p1, elS, THR, S.res)
        else:
            dyd = D["F"].get("d_fairway").reshape(S.H, S.W) / YD
            nat = np.zeros((S.H, S.W), bool)
            for ref, h in pk0["holes"].items():
                if not h.get("tee_ll") or not h.get("aim_ll") or (h.get("par") or 4) < 4: continue
                al, la = LB.corridor_coords(S, dict(tee_ll=h["tee_ll"], dot270_ll=h["aim_ll"]))
                for sgn in (-1, 1):
                    m = (al >= 150) & (al <= 340) & (np.abs(la) <= 50) & (np.sign(la) == sgn) & elS
                    j = np.flatnonzero(m.ravel())
                    if len(j) < 500: continue
                    dj = dyd.ravel()[j]; pj = p1.ravel()[j]
                    o = np.argsort(-dj); s = np.cumsum((pj - THR)[o]); k = int(np.argmax(s))
                    if s[k] <= 0: continue
                    nat.ravel()[j[o[:k + 1]]] = True
            nat = L.remove_small(nat, 150 * 0.8361)
        S.ll_to_rc([[0, 0]])
        for gm0 in L.mask_to_polys(S, nat, min_yd2=150, simplify_yd=2.0):
            gm = transform(lambda x, y: S._fwd.transform(x, y), gm0)
            feats.append(dict(type="Feature", geometry=mapping(gm0), properties=dict(
                lie="native", src="vision3:s2_experiment", p=0.5, area_yd2=round(gm.area / YD ** 2), model="experiment")))
        print(slug, MODE, THR, "native m2", int(nat.sum()), "polys", len(feats), flush=True)
    fc = copy.deepcopy(fc0); fc["features"] = feats + fc["features"]
    pk = C.rebuild_package(pslug, fc)
    od = os.path.join(OUT, NAME, pslug); os.makedirs(od, exist_ok=True)
    json.dump(pk, open(os.path.join(od, "package.json"), "w"))
