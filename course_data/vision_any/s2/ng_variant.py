"""Error-budget variant packages for the native layer, on top of the build-as-it-would-be base (committed package with
the 3f1a201d tee rule + vision_any/2 trees re-made from the lidar, platform/rebuild_tees_trees.py) .
python3 ng_variant.py <wt> <outdir> <name> <pred.npz | none> <thr> slug...
The native polygons: the held-out course's 10 m LOCO P upsampled to 1 m, v2_model.native_mask (strict eligibility:
elig & ~water & course, committed lidar trees excluded), put in with vision_any/gapfill like the trees."""
import os, sys, json, contextlib, io, numpy as np
os.environ.setdefault("OMP_NUM_THREADS", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
WT, OUT, NAME, PRED, THR = sys.argv[1:6]; THR = float(THR); slugs = sys.argv[6:]
sys.path.insert(0, HERE)
import s2lib as S2
CD = os.path.join(WT, "course_data")
sys.path[:0] = [os.path.join(CD, "platform"), os.path.join(CD, "vision_any")]
import rebuild_tees_trees as RT
import error_budget as E
VSL = {"mozingo_lake": "mozingo"}
P = np.load(PRED) if PRED != "none" else None
K = json.load(open(os.path.join(CD, "vision_any", "model_v2", "model.json")))["settings"]["trees"]["k_m"]
ELC = os.path.join(HERE, "elig_cache"); os.makedirs(ELC, exist_ok=True)


def elig(vslug):
    f = os.path.join(ELC, vslug + ".npz")
    if os.path.exists(f):
        z = np.load(f); return np.unpackbits(z["m"])[:int(z["n"])].reshape(z["shape"]).astype(bool)
    import v2_longgrass_cv as CV; CV.install_truth_labels()
    import v2_model as VM
    D = VM.prepare(vslug)
    m = D["elig"] & ~D["water0"] & D["course"] & ~D["canopy"][2.5]
    np.savez_compressed(f, m=np.packbits(m.ravel()), n=m.size, shape=np.array(m.shape))
    return m


def native_feats(vslug):
    import layers as L, v2_model as VM
    from shapely.geometry import mapping
    from shapely.ops import transform
    import run_any as RA
    S = L.Stack.load(vslug, RA.course_dir_for(vslug))
    el = elig(vslug)
    g = S2.load_g10(vslug); pg = P[vslug + "_g"]
    rr, cc = np.mgrid[0:S.H, 0:S.W]
    p1 = pg[(rr + int(g["ro"])) // 10, (cc + int(g["co"])) // 10].astype(np.float32); del rr, cc
    nat = VM.native_mask(p1, el, THR, S.res)
    S.ll_to_rc([[0, 0]]); feats = []
    for gm0 in L.mask_to_polys(S, nat, min_yd2=150, simplify_yd=2.0):
        gm = transform(lambda x, y: S._fwd.transform(x, y), gm0)
        feats.append(dict(type="Feature", geometry=mapping(gm0), properties=dict(
            lie="native", src="vision3:s2_experiment", p=0.5, area_yd2=round(gm.area / 0.9144 ** 2), model="experiment")))
    return feats, int(nat.sum())


cfgs = {c["slug"]: c for s in ("v1", "v2") for c in E.SETS[s]()}
for slug in slugs:
    vslug = VSL.get(slug, slug); cfg = cfgs.get(slug, {})
    pp = os.path.join(WT, cfg["package"]) if cfg.get("package") else os.path.join(CD, "packages", slug, "package.json")
    pkg = json.load(open(pp))
    with contextlib.redirect_stdout(io.StringIO()):
        pkg, n1 = RT.retee(pkg, os.path.dirname(pp), slug)
    fc = RT.tree_fc(vslug, K)
    fc["features"] = [f for f in fc["features"] if f["properties"].get("lie") != "native"]
    nm = 0
    if P is not None:
        nf, nm = native_feats(vslug); fc["features"] = nf + fc["features"]
    G = RT._load("ngv_gapfill", os.path.join(CD, "vision_any", "gapfill.py"))
    G.load_layers = lambda s, imagery_dir=None, course_dir=None: (fc, fc.get("properties", {}))
    with contextlib.redirect_stdout(io.StringIO()):
        pkg = G.gapfill(pkg, slug=vslug)
    nz = sum(1 for h in pkg["holes"].values() for z in h.get("zones_ll") or [] if z.get("lie") == "native")
    od = os.path.join(OUT, NAME, slug); os.makedirs(od, exist_ok=True)
    json.dump(pkg, open(os.path.join(od, "package.json"), "w"))
    print(slug, NAME, "native m2", nm, "native zones", nz, "|", n1, flush=True)
