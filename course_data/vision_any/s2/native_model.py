"""Sentinel-2 native (long grass) probability on a course's 10 m S2 grid, for the mapper (course_data/mapper/BRIEF.md).

The model is the 23-course S2 model of s2_longgrass.md ('Enlarged native set': LightGBM on s2lib.course_grid('s2')
features, P >= 0.5 LOCO precision / recall / IoU 0.72 / 0.55 / 0.45 in the landing corridors). It is NOT an
automatic layer: the mapper sees it as a suggestion and confirms or rejects it against the photos.

Leave-one-course-out safe:
  * a course in the training set gets the P of the fold model that was trained WITHOUT it
    (native_model/loco/<slug>.npz, the LOCO grids of the s2_longgrass.md run);
  * any other course gets the full model (native_model/full_model.txt, trained on all 23 courses), applied to its
    S2 stack (vision_any/s2/<slug>/s2_stack.npz) and its package masks aggregated to 10 m (no truth file is read).

  python3 course_data/vision_any/s2/native_model.py predict <slug>         # P grid summary (new course: full model)
  python3 course_data/vision_any/s2/native_model.py export <ds_dir> <pred_loco.npz>
        evaluator only: <ds_dir> holds build_ds_13.py / prep_grid10.py output (truth labels) and s2_loco.py's
        common.py / model_lib.py; trains the full model on the 23 courses and writes native_model/ from the LOCO pred.

API: p_grid(slug) -> dict(p=(H, W) float32 (nan = no data), transform=(a, b, c, d, e, f) affine of the grid,
     crs="EPSG:...", source="loco" | "full", note=str) or None when the course has no S2 stack.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
MODEL_DIR = os.path.join(HERE, "native_model")
THR = 0.5                      # the s2_longgrass.md operating point
SCALE = 200.0                  # P stored as uint8 round(P * 200); 255 = no data


def _stack_meta(slug):
    p = os.path.join(HERE, slug, "s2_stack.npz")
    if not os.path.exists(p):
        return None
    z = np.load(p, allow_pickle=False)
    return dict(transform=tuple(float(v) for v in z["transform"]), crs=str(z["crs"]),
                shape=tuple(int(v) for v in z["shape"]))


def meta():
    p = os.path.join(MODEL_DIR, "model.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def loco_path(slug):
    return os.path.join(MODEL_DIR, "loco", f"{slug}.npz")


def _decode(u8):
    p = u8.astype(np.float32) / SCALE
    p[u8 == 255] = np.nan
    return p


def _encode(p):
    q = np.where(np.isfinite(p), np.clip(np.round(p * SCALE), 0, 200), 255)
    return q.astype(np.uint8)


# ----------------------------------------------------------------------------- 10 m package masks (blind)
def g10_blind(slug):
    """prep_grid10.py's 1 m -> 10 m masks from the package (OSM, lidar canopy, eligibility); no truth label."""
    sys.path.insert(0, os.path.join(CD, "vision_any"))
    import v2_model as VM
    D = VM.prepare(slug)
    S, Mk = D["S"], D["M"]
    m = json.load(open(os.path.join(CD, "vision_any", slug, "raw", "meta.json")))["grid"]
    x0, y0, x1, y1 = m["bounds"]
    X0 = np.floor(x0 / 10) * 10
    Y1 = np.ceil(y1 / 10) * 10
    W = int((np.ceil(x1 / 10) * 10 - X0) / 10)
    H = int((Y1 - np.floor(y0 / 10) * 10) / 10)
    co, ro = int(x0 - X0), int(Y1 - y1)

    def agg(a, how="mean"):
        import warnings
        h1, w1 = a.shape
        big = np.full((H * 10, W * 10), np.nan, np.float32)
        big[ro:ro + h1, co:co + w1] = a
        b = big.reshape(H, 10, W, 10)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return (np.nanmean(b, axis=(1, 3)) if how == "mean" else np.nanmin(b, axis=(1, 3))).astype(np.float32)
    dfw = D["F"].get("d_fairway").reshape(S.H, S.W).astype(np.float32)
    return dict(fairway=agg(Mk["fairway"].astype(np.float32)), mown=agg(Mk["mown"].astype(np.float32)),
                canopy=agg(D["canopy"][2.5].astype(np.float32)),
                elig=agg((D["elig"] & ~D["water0"]).astype(np.float32)),
                water=agg(D["water0"].astype(np.float32)), course=agg(D["course"].astype(np.float32)),
                dfw_min=agg(dfw, "min"), dfw_mean=agg(dfw), ro=ro, co=co, H=H, W=W, W1=S.W, H1=S.H)


def features(slug, g):
    sys.path.insert(0, HERE)
    import s2lib as S2
    S2.S2DIR = HERE                              # the stacks live next to this file (s2lib defaults to ./s2)
    st = S2.load_stack(slug)
    H, W = int(g["H"]), int(g["W"])
    assert tuple(st["shape"]) == (H, W), (slug, st["shape"], H, W)
    F = S2.s2_features(st)
    cols = dict(S2.relative(F, g))
    cols.update(S2.context(g))
    names = sorted(cols)
    return names, np.stack([cols[n] for n in names], -1).reshape(H * W, len(names))


def predict_full(slug, g=None):
    import lightgbm as lgb
    md = meta()
    bst = lgb.Booster(model_file=os.path.join(MODEL_DIR, "full_model.txt"))
    g = g or g10_blind(slug)
    names, X = features(slug, g)
    if names != md.get("features"):
        raise SystemExit(f"{slug}: feature names differ from the trained model's ({len(names)} vs "
                         f"{len(md.get('features') or [])})")
    return bst.predict(X).astype(np.float32).reshape(int(g["H"]), int(g["W"]))


def p_grid(slug, allow_full=True):
    sm = _stack_meta(slug)
    if sm is None:
        return None
    md = meta()
    lp = loco_path(slug)
    if os.path.exists(lp):
        z = np.load(lp)
        p = _decode(z["p"])
        assert p.shape == sm["shape"], (slug, p.shape, sm["shape"])
        return dict(p=p, transform=sm["transform"], crs=sm["crs"], source="loco", thr=THR,
                    note=f"leave-one-course-out fold model (trained on the {len(md.get('courses', [])) - 1} other "
                         f"S2 training courses, not on this one)")
    if not allow_full:
        return None
    p = predict_full(slug)
    return dict(p=p, transform=sm["transform"], crs=sm["crs"], source="full", thr=THR,
                note=f"full model (trained on {len(md.get('courses', []))} courses; this course is not one of them)")


# ----------------------------------------------------------------------------- evaluator: export
def export(ds_dir, pred):
    """Train the full model on the 23 courses (s2_loco.py's train_10, same params) and write native_model/."""
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("S2DIR", HERE)
    sys.path.insert(0, HERE)
    import s2lib as S2
    S2.S2DIR = HERE
    courses = list(S2.COURSES)
    sys.path.insert(0, ds_dir)
    cwd = os.getcwd()
    os.chdir(ds_dir)
    try:
        src = open(os.path.join(HERE, "s2_loco.py")).read().split("out = {}")[0]
        S2.load_g10 = lambda slug: dict(np.load(os.path.join(ds_dir, f"g10_{slug}.npz")))
        sys.modules["s2lib"] = S2
        g = {"__name__": "s2_loco_export", "__file__": os.path.join(HERE, "s2_loco.py")}
        argv = sys.argv
        sys.argv = ["s2_loco.py", "s2", ",".join(courses)]
        exec(compile(src, "s2_loco.py", "exec"), g)
        sys.argv = argv
        clf = g["train_10"](courses)
        names = g["course"](courses[0])["names"]
    finally:
        os.chdir(cwd)
    os.makedirs(os.path.join(MODEL_DIR, "loco"), exist_ok=True)
    clf.booster_.save_model(os.path.join(MODEL_DIR, "full_model.txt"))
    P = np.load(pred)
    for c in courses:
        sm = _stack_meta(c)
        pg = P[c + "_g"]
        assert pg.shape == sm["shape"], (c, pg.shape, sm["shape"])
        np.savez_compressed(loco_path(c), p=_encode(pg))
    md = dict(schema="s2_native_model/1", thr=THR, scale=SCALE, courses=courses, features=list(names),
              params=g["P10"], model="LightGBM on s2lib.course_grid('s2') (fw_/rf_ relative S2 seasonal features + "
                                     "10 m package context), 10 m cell native when >= 50 % of its labelled 1 m cells",
              loco="loco/<slug>.npz: P of the fold model trained without <slug> (s2_loco.py s2 over the 23 courses)",
              doc="course_data/vision_any/s2_longgrass.md 'Enlarged native set'; used by course_data/mapper/s2_suggest.py")
    json.dump(md, open(os.path.join(MODEL_DIR, "model.json"), "w"), indent=1, default=float)
    print("exported", len(courses), "LOCO grids + full model ->", os.path.relpath(MODEL_DIR, CD))


def main():
    a = sys.argv[1:]
    if a and a[0] == "export":
        export(a[1], a[2])
    elif a and a[0] == "predict":
        r = p_grid(a[1])
        if r is None:
            raise SystemExit(f"{a[1]}: no S2 stack (course_data/vision_any/s2/{a[1]}/s2_stack.npz)")
        p = r["p"]
        print(a[1], r["source"], p.shape, f"cells P >= {THR}: {int((p >= THR).sum())} "
              f"({(p >= THR).sum() * 100 / 1e4:.1f} ha)")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
