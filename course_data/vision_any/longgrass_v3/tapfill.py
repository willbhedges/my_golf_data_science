"""Simulated golfer tap 'native grass along this hole?' (answer = hand map has > 250 m2 native in the corridor),
then native = eligible (strict) cells >= D m from OSM fairway inside that hole's landing corridor (150-340 yds,
|lat| <= 50 yds), optionally also P(native) >= pmin. python3 tapfill.py <wt> <outdir> <D> <pmin> slug..."""
import os, sys, json, copy, numpy as np
os.environ.setdefault("OMP_NUM_THREADS", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
WT, OUT, DM, PMIN = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]); slugs = sys.argv[5:]
sys.path.insert(0, HERE)
from common import *
sys.path.insert(0, os.path.join(WT, "course_data/vision_any"))
import v2_longgrass_cv as CV
LB = CV.install_truth_labels()
import v2_model as VM, v2_calibrate as C, layers as L, rasterio
from shapely.geometry import mapping
from shapely.ops import transform
for slug in slugs:
    d = load(slug)
    cor = (d["along"] >= 180) & (d["along"] <= 320) & (np.abs(d["lat"]) <= 50)
    yes = {r for r in np.unique(d["ref"]) if ((d["ref"] == r) & cor & (d["cls"] == NATIVE)).sum() > 250}
    D = VM.prepare(slug); S = D["S"]
    vd = os.path.join(WT, "course_data/vision_any", slug)
    with rasterio.open(os.path.join(vd, "layers_v2.tif")) as r:
        cls = r.read(1)
    elS = D["elig"] & ~D["water0"] & D["course"] & (cls != 2) & (cls != 3)
    dfw = D["F"].get("d_fairway").reshape(S.H, S.W)
    pp = os.path.join(HERE, "var", f"p_norm_{slug}.npy")
    P = np.load(pp).astype(np.float32) / 255 if (PMIN > 0 and os.path.exists(pp)) else None
    pk0 = json.load(open(os.path.join(WT, "course_data/packages", slug, "package.json")))
    nat = np.zeros((S.H, S.W), bool)
    for ref in yes:
        h = pk0["holes"].get(str(ref))
        if not h or not h.get("tee_ll") or not h.get("aim_ll"): continue
        al, la = LB.corridor_coords(S, dict(tee_ll=h["tee_ll"], dot270_ll=h["aim_ll"]))
        m = (al >= 150) & (al <= 340) & (np.abs(la) <= 50) & elS & (dfw >= DM)
        if P is not None: m &= P >= PMIN
        nat |= m
    nat = L.remove_small(nat, 150 * 0.8361)
    fc0 = json.load(open(os.path.join(vd, "vision_any.geojson")))
    fc0["features"] = [f for f in fc0["features"] if f["properties"]["lie"] != "native"]
    feats = []
    S.ll_to_rc([[0, 0]])
    for g in L.mask_to_polys(S, nat, min_yd2=150, simplify_yd=2.0):
        gm = transform(lambda x, y: S._fwd.transform(x, y), g)
        feats.append(dict(type="Feature", geometry=mapping(g), properties=dict(lie="native", src="experiment:tapfill", p=0.5,
                                                                              area_yd2=round(gm.area / 0.9144 ** 2), model="experiment")))
    fc = copy.deepcopy(fc0); fc["features"] = feats + fc["features"]
    pk = C.rebuild_package(slug, fc)
    od = os.path.join(OUT, f"tap_d{int(DM)}_p{PMIN}", slug); os.makedirs(od, exist_ok=True)
    json.dump(pk, open(os.path.join(od, "package.json"), "w"))
    print(slug, "tap yes holes", sorted(yes, key=lambda x: int(x) if x.isdigit() else 99), "native m2", int(nat.sum()), "polys", len(feats), flush=True)
