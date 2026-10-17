"""Workstream C on workstream D's benchmark (course_data/zero_tap/BENCH.md): method `sequence`.

    python course_data/zero_tap/sequence/run_bench.py solve --tiers osm_card,nocard --shard 0/6 --out rows/zb_0.json
    python course_data/zero_tap/sequence/run_bench.py gate rows/zb_*.json --tag v1

solve: per benchmark course and tier, bench.inputs(row, tier) -> solve.run (joint solver + anchors v2) -> the
       uncalibrated zero_tap_result/1 + the gate diagnostics + D's per-course score (labels).
gate:  fit the certainty gate on the DEV split only (labels: D's course_ok = every number and known par right),
       apply it to every course, write course_data/zero_tap/results/sequence/<tier>/<slug>.json (certain, confidence),
       and the scoreboard rows of D's scorer to results/<tag>/bench_d.{json,md}. Test is scored once, never fitted.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ZT)
import solve as SV                                                   # noqa: E402
import gate as GT                                                    # noqa: E402
import importlib.util                                                # noqa: E402

_spec = importlib.util.spec_from_file_location("zt_bench_d", os.path.join(ZT, "bench.py"))
DB = importlib.util.module_from_spec(_spec)                          # course_data/zero_tap/bench.py (workstream D)
sys.modules["zt_bench_d"] = DB
_spec.loader.exec_module(DB)

assert hasattr(DB, "inputs"), "expected workstream D's course_data/zero_tap/bench.py"
METHOD = "sequence"


def solve_rows(tiers, split, shard, of, slugs=None):
    rows = DB.courses(None if split == "all" else split)
    if slugs:
        rows = [r for r in rows if r["slug"] in slugs]
    rows = [r for j, r in enumerate(rows) if j % of == shard]
    out = []
    for r in rows:
        for tier in tiers:
            t0 = time.time()
            try:
                x = DB.inputs(r, tier)
                n = r.get("n_holes") if tier.endswith("_card") else None
                res, raw = SV.run(x["fc"], x["course"], x["card"], gate_params={}, n_holes=None, return_raw=True)
                diag = raw.get("diag") or {}
            except Exception as e:                                    # noqa: BLE001
                traceback.print_exc()
                res, diag = dict(holes=[], error=repr(e)[:300]), {}
                x = dict(card_kind=None)
            res.update(schema="zero_tap_result/1", method=METHOD, tier=tier, slug=r["slug"],
                       card_kind=x.get("card_kind"), seconds=round(time.time() - t0, 1))
            sc = DB.score_course(res, DB.truth(r["slug"]))
            out.append(dict(slug=r["slug"], split=r["split"], tier=tier, mode=f"bench_{tier}", kind=r["kind"],
                            result=res, diag=diag, all_correct=int(sc["course_ok"]), holes_ok=int(sc["holes_ok"]),
                            primary=sc["primary"], formed=sc["formed"], number=sc["number"], N=sc["N"]))
            print(f"{r['split']:5s} {r['slug'][:28]:28s} {tier:9s} N={sc['N']:2d} formed {sc['formed']:2d} "
                  f"num {sc['number']:2d} ok={int(sc['course_ok'])} {sc['primary']} {res['seconds']}s", flush=True)
    return out


def gate_and_write(paths, tag, results_root=None):
    rows = [r for p in paths for r in GT._read(p)]
    modes = tuple(sorted({r["mode"] for r in rows}))
    outdir = os.path.join(HERE, "results", tag)
    os.makedirs(outdir, exist_ok=True)
    gp_path = os.path.join(HERE, "gate_params_bench.json")
    gp = GT.fit(paths, out=gp_path, modes=modes, splits=("dev",))
    # cross-fitted dev confidences (honest on dev); full-dev model for test
    dev = [r for r in rows if r["split"] == "dev" and r.get("diag")]
    _, Xd, yd = GT.dataset(dev, modes)
    s_cv = GT.crossfit(dev, Xd, yd)
    cv = {(r["slug"], r["tier"]): s for r, s in zip(dev, s_cv)}
    root = results_root or os.path.join(ZT, "results")
    scored = []
    for r in rows:
        res = r["result"]
        if r.get("diag"):
            s = cv.get((r["slug"], r["tier"])) if r["split"] == "dev" else float(GT.score(gp["model"], GT.features(r["diag"])[None])[0])
            conf = float(GT.iso_apply(gp["iso"]["x"], gp["iso"]["v"], [s])[0])
            certain = bool(s >= gp["threshold_score"])
        else:
            s, conf, certain = None, 0.0, False
        res.update(certain=certain, confidence=round(conf, 4), gate=dict(score=None if s is None else round(float(s), 4),
                                                                         threshold=gp["threshold_score"],
                                                                         dev_scores="cross-fitted" if r["split"] == "dev" else "full-dev model"))
        DB.write_result(res, os.path.join(root, METHOD, r["tier"]))
        sc = DB.score_course(res, DB.truth(r["slug"]))
        sc.update(split=r["split"], tier=r["tier"], score=s)
        scored.append(sc)
    md = ["| split | tier | courses | holes numbered right | fully right | certain | coverage | precision | "
          "max coverage at precision >= 99 % | 95 % | 90 % |", "|" + "---|" * 11]
    board = {}
    for sp in ("dev", "test"):
        for tier in sorted({s["tier"] for s in scored}):
            xs = [s for s in scored if s["split"] == sp and s["tier"] == tier]
            if not xs:
                continue
            y = np.array([int(s["course_ok"]) for s in xs])
            c = np.array([int(s["certain"]) for s in xs])
            sc_ = np.array([s["score"] if s["score"] is not None else -1e9 for s in xs])
            cur = GT.curve(sc_, y)
            cov = {t: max((p["coverage"] for p in cur if p["precision"] >= t), default=0.0) for t in (0.99, 0.95, 0.90)}
            H = sum(s["N"] for s in xs)
            d = dict(n=len(xs), holes_right=sum(s["number"] for s in xs) / H, fully=float(y.mean()), certain=int(c.sum()),
                     coverage=float(c.mean()), precision=float(y[c == 1].mean()) if c.any() else None,
                     cov99=cov[0.99], cov95=cov[0.95], cov90=cov[0.90], curve=cur,
                     certified=[s["slug"] for s in xs if s["certain"]],
                     certified_wrong=[s["slug"] for s in xs if s["certain"] and not s["course_ok"]],
                     primary={k: sum(1 for s in xs if s["primary"] == k) for k in {s["primary"] for s in xs}})
            board[f"{sp}/{tier}"] = d
            prec = "-" if d["precision"] is None else f"{d['precision']:.1%}"
            md.append(f"| {sp} | {tier} | {d['n']} | {d['holes_right']:.1%} | {d['fully']:.1%} | {d['certain']} | "
                      f"{d['coverage']:.1%} | {prec} | {d['cov99']:.1%} | {d['cov95']:.1%} | {d['cov90']:.1%} |")
    json.dump(dict(gate=dict(calib=gp["calib"], threshold_score=gp["threshold_score"], ltt=gp["ltt_threshold"]),
                   board=board), open(os.path.join(outdir, "bench_d.json"), "w"), indent=1, default=float)
    open(os.path.join(outdir, "bench_d.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["solve", "gate"])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--tiers", default="osm_card,nocard")
    ap.add_argument("--split", default="all")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--slugs", default="")
    ap.add_argument("--out")
    ap.add_argument("--tag", default="default")
    a = ap.parse_args()
    if a.what == "solve":
        k, of = (int(v) for v in a.shard.split("/"))
        rows = solve_rows(a.tiers.split(","), a.split, k, of, a.slugs.split(",") if a.slugs else None)
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(rows, open(a.out, "w"), default=float)
    else:
        gate_and_write(a.paths, a.tag)


if __name__ == "__main__":
    main()
