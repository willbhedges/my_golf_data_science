"""1 m course masks aggregated onto the Sentinel-2 10 m grid. python3 prep_grid10.py <wt> <outdir> slug..."""
import os, sys, json, numpy as np
os.environ.setdefault("OMP_NUM_THREADS", "1")
WT, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(WT, "course_data/vision_any"))
import v2_longgrass_cv as CV
CV.install_truth_labels()
import v2_model as VM


def g10(slug):
    m = json.load(open(os.path.join(WT, "course_data/vision_any", slug, "raw", "meta.json")))["grid"]
    x0, y0, x1, y1 = m["bounds"]
    X0 = np.floor(x0 / 10) * 10; Y1 = np.ceil(y1 / 10) * 10
    W = int((np.ceil(x1 / 10) * 10 - X0) / 10); H = int((Y1 - np.floor(y0 / 10) * 10) / 10)
    return m, int(x0 - X0), int(Y1 - y1), H, W


def agg(a, ro, co, H, W, how="mean"):
    h1, w1 = a.shape
    big = np.full((H * 10, W * 10), np.nan, np.float32)
    big[ro:ro + h1, co:co + w1] = a
    b = big.reshape(H, 10, W, 10)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return (np.nanmean(b, axis=(1, 3)) if how == "mean" else np.nanmin(b, axis=(1, 3))).astype(np.float32)


for slug in sys.argv[3:]:
    D = VM.prepare(slug); S = D["S"]; M = D["M"]
    m, co, ro, H, W = g10(slug)
    assert (S.H, S.W) == (m["height"], m["width"]), (S.H, S.W, m["height"], m["width"])
    dfw = D["F"].get("d_fairway").reshape(S.H, S.W).astype(np.float32)
    out = dict(fairway=agg(M["fairway"].astype(np.float32), ro, co, H, W),
               mown=agg(M["mown"].astype(np.float32), ro, co, H, W),
               canopy=agg(D["canopy"][2.5].astype(np.float32), ro, co, H, W),
               elig=agg((D["elig"] & ~D["water0"]).astype(np.float32), ro, co, H, W),
               water=agg(D["water0"].astype(np.float32), ro, co, H, W),
               course=agg(D["course"].astype(np.float32), ro, co, H, W),
               dfw_min=agg(dfw, ro, co, H, W, "min"), dfw_mean=agg(dfw, ro, co, H, W))
    np.savez_compressed(os.path.join(OUT, f"g10_{slug}.npz"), ro=ro, co=co, H=H, W=W, W1=S.W, H1=S.H, **out)
    print(slug, H, W, "fairway cells", int((out["fairway"] > 0.7).sum()), flush=True)
