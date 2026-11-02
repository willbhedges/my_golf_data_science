"""Corridor-cell dataset for long-grass LOCO experiments. usage: build_ds.py <wt> <out_dir> slug..."""
import os, sys, json, numpy as np
os.environ.setdefault("OMP_NUM_THREADS", "1")
WT, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(WT, "course_data/vision_any"))
import v2_longgrass_cv as CV
LB = CV.install_truth_labels()
import v2_model as VM
from scipy import ndimage
C = dict(a0=145.0, a1=440.0, lat=60.0)
for slug in sys.argv[3:]:
    D = VM.prepare(slug)
    S, F = D["S"], D["F"]
    H = VM.hole_data(D)
    el = (D["elig_rel"] & ~D["water0"]).ravel()
    elS = (D["elig"] & ~D["water0"]).ravel()
    idx, y, ref, al, la, cl = [], [], [], [], [], []
    for x in H:
        cls = x["cls"]; sl = x["sl"]
        m = (cls >= 0) & (x["along"] >= C["a0"]) & (x["along"] <= C["a1"]) & (np.abs(x["lat"]) <= C["lat"])
        rr, cc = np.nonzero(m)
        g = (rr + sl[0].start) * S.W + (cc + sl[1].start)
        k = el[g]
        idx.append(g[k]); cl.append(cls[rr, cc][k]); ref.append(np.full(k.sum(), x["ref"], object))
        al.append(x["along"][rr, cc][k]); la.append(x["lat"][rr, cc][k])
    idx = np.concatenate(idx); cl = np.concatenate(cl); ref = np.concatenate(ref); al = np.concatenate(al); la = np.concatenate(la)
    names = list(F.names)
    X = F.matrix(idx, names).astype(np.float32)
    # whole-course eligible sample (for course-level priors and full-course false-positive area)
    R = np.random.default_rng(0)
    ce = np.flatnonzero(el & D["course"].ravel())
    cs = R.choice(ce, min(60000, len(ce)), replace=False)
    Xc = F.matrix(cs, names).astype(np.float32)
    np.savez_compressed(os.path.join(OUT, f"ds_{slug}.npz"), X=X, cls=cl, idx=idx, ref=ref.astype(str), along=al, lat=la,
                        strict=elS[idx], Xc=Xc, cidx=cs, names=np.array(names), shape=np.array([S.H, S.W]),
                        n_course_elig=len(ce))
    print(slug, "cells", len(idx), "native", int((cl == LB.CI["native"]).sum()), flush=True)
