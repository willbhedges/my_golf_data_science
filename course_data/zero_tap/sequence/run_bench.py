"""Workstream C on workstream D's benchmark (course_data/zero_tap/BENCH.md): method `sequence`.

    python course_data/zero_tap/sequence/run_bench.py solve --tiers osm_card,nocard --shard 0/6 --out rows/zb_0.json
    python course_data/zero_tap/sequence/run_bench.py gate rows/zb_*.json --tag v1
  v2 (workstream A's hole_pairs/1 as the formation; out-of-fold pairs for dev courses):
    python course_data/zero_tap/sequence/run_bench.py solve --tiers nocard,osm_card,unmapped_nocard,unmapped_card \
        --pairs-root course_data/zero_tap/formation/hole_pairs --pairs-root-dev hp_oof --shard 0/6 --out rows/zb_0.json
    python course_data/zero_tap/sequence/run_bench.py gate2 rows/zb_*.json --tag v2 --method sequence_v2

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
FALLBACK = os.environ.get("ZT_STRUCT_FALLBACK", "0") == "1"      # v3: no hole_pairs/1 -> structure hypotheses


def _pairs_for(slug, tier, split, pairs_root, pairs_root_dev):
    """hole_pairs/1 for (course, tier): dev courses from pairs_root_dev when given (out-of-fold pairs: A's model was
    trained on the dev courses), else pairs_root (A's committed formation/hole_pairs/)."""
    for root in ([pairs_root_dev] if (split == "dev" and pairs_root_dev) else [pairs_root]):     # never in-sample
        p = os.path.join(root, tier, slug + ".json")
        if root and os.path.exists(p):
            return json.load(open(p)), p
    return None, None


def solve_rows(tiers, split, shard, of, slugs=None, pairs_root=None, pairs_root_dev=None):
    rows = DB.courses(None if split == "all" else split)
    if slugs:
        rows = [r for r in rows if r["slug"] in slugs]
    rows = [r for j, r in enumerate(rows) if j % of == shard]
    in_tier = {t: {c["slug"] for c in DB.courses(None, t)} for t in tiers}
    out = []
    for r in rows:
        for tier in tiers:
            if r["slug"] not in in_tier[tier]:                        # D scores unmapped tiers on a subset
                continue
            t0 = time.time()
            try:
                x = DB.inputs(r, tier)
                hp = None
                if pairs_root:
                    hp, src = _pairs_for(r["slug"], tier, r["split"], pairs_root, pairs_root_dev)
                    if hp is None and not (FALLBACK and not tier.startswith("unmapped")):
                        raise RuntimeError(f"no hole_pairs/1 for {r['slug']} {tier}")
                if hp is not None:
                    scene = None
                    if tier.startswith("unmapped"):
                        scene = x.get("scene") or SV._formation_data().perception_scene_obj(r["slug"])
                        if scene is None:
                            raise RuntimeError("no perception scene")
                    res, raw = SV.run(x["fc"], x["course"], x["card"], pairs=hp, gate_params={}, return_raw=True,
                                      scene=scene)
                    raw.setdefault("diag", {})
                    if raw["diag"]:
                        raw["diag"]["perception"] = bool(scene)
                    res["pairs_src"] = os.path.relpath(src, os.path.dirname(os.path.dirname(ZT)))
                else:
                    # v1 path; in v3 also the fallback for courses A never paired (benchmark v1's new courses):
                    # the structure solver's hypotheses (+ the card-geometry term when ZT_CARD_W > 0)
                    res, raw = SV.run(x["fc"], x["course"], x["card"], gate_params={}, n_holes=None, return_raw=True)
                    if pairs_root:
                        res["formation_fallback"] = "structure (no hole_pairs/1 for this course)"
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


def gate_and_write_v2(paths, tag, method="sequence_v2", results_root=None):
    """Gate v2: fit on DEV rows only (GT.fit_v2), dev confidences cross-fitted, the full-dev model applied ONCE to
    test; writes results/<method>/<tier>/<slug>.json and sequence/results/<tag>/bench_d.{json,md}."""
    rows = [r for p in paths for r in GT._read(p)]
    outdir = os.path.join(HERE, "results", tag)
    os.makedirs(outdir, exist_ok=True)
    gp, cv = GT.fit_v2([r for r in rows if r["split"] == "dev"])
    json.dump(gp, open(os.path.join(outdir, "gate_params.json"), "w"), indent=1, default=float)
    print(json.dumps(gp["calib"]), gp["feat_set"], gp["l2"], "threshold", round(gp["threshold_score"], 3), flush=True)
    root = results_root or os.path.join(ZT, "results")
    scored = []
    for r in rows:
        res = r["result"]
        dg = r.get("diag") or {}
        if dg:
            s = cv.get((r["slug"], r["tier"])) if r["split"] == "dev" else \
                float(GT.score(gp["model"], GT.features(dg, gp["feats"])[None])[0])
            ok = GT.hard_ok(dg)
            conf = float(GT.iso_apply(gp["iso"]["x"], gp["iso"]["v"], [s])[0])
            certain = bool(ok and s >= gp["threshold_score"])
        else:
            s, ok, conf, certain = None, False, 0.0, False
        res.update(method=method, version=tag, certain=certain, confidence=round(conf if ok else min(conf, 0.5), 4),
                   gate=dict(score=None if s is None else round(float(s), 4), threshold=gp["threshold_score"],
                             hard_ok=ok, version=gp["schema"],
                             dev_scores="cross-fitted" if r["split"] == "dev" else "full-dev model"))
        DB.write_result(res, os.path.join(root, method, r["tier"]))
        sc = DB.score_course(res, DB.truth(r["slug"]))
        sc.update(split=r["split"], tier=r["tier"], score=s, hard_ok=ok)
        scored.append(sc)
    board = {}
    md = ["| split | tier | courses | holes numbered right | fully right | certain | certain & right | precision | "
          "max coverage at precision >= 99 % | 95 % | 90 % |", "|" + "---|" * 11]
    for sp in ("dev", "test"):
        for tier in ("osm_card", "nocard", "unmapped_card", "unmapped_nocard"):
            xs = [s for s in scored if s["split"] == sp and s["tier"] == tier]
            if not xs:
                continue
            y = np.array([int(s["course_ok"]) for s in xs])
            c = np.array([int(s["certain"]) for s in xs])
            # the curve ranks by score among hard-rule-eligible courses (others are never certain)
            sc_ = np.array([s["score"] if (s["score"] is not None and s["hard_ok"]) else -1e9 for s in xs])
            cur = [p for p in GT.curve(sc_, y) if p["threshold"] > -1e8]
            cov = {t: max((p["coverage"] for p in cur if p["precision"] >= t), default=0.0) for t in (0.99, 0.95, 0.90)}
            H = sum(s["N"] for s in xs)
            d = dict(n=len(xs), holes_right=sum(s["number"] for s in xs) / H, formed=sum(s["formed"] for s in xs) / H,
                     fully=float(y.mean()), certain=int(c.sum()), certain_right=int((c * y).sum()),
                     coverage=float(c.mean()), precision=float(y[c == 1].mean()) if c.any() else None,
                     cov99=cov[0.99], cov95=cov[0.95], cov90=cov[0.90], hard_ok=int(sum(s["hard_ok"] for s in xs)),
                     certified=[s["slug"] for s in xs if s["certain"]] if sp == "dev" else None,
                     primary={str(k): sum(1 for s in xs if s["primary"] == k) for k in {s["primary"] for s in xs}})
            board[f"{sp}/{tier}"] = d
            prec = "-" if d["precision"] is None else f"{d['precision']:.1%}"
            md.append(f"| {sp} | {tier} | {d['n']} | {d['holes_right']:.1%} | {d['fully']:.1%} | {d['certain']} | "
                      f"{d['certain_right']} | {prec} | {d['cov99']:.1%} | {d['cov95']:.1%} | {d['cov90']:.1%} |")
    json.dump(dict(gate={k: gp[k] for k in ("schema", "feat_set", "feats", "l2", "threshold_score", "hard_rules",
                                             "calib", "trials")}, board=board),
              open(os.path.join(outdir, "bench_d.json"), "w"), indent=1, default=float)
    open(os.path.join(outdir, "bench_d_table.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))


def pick(paths, out):
    """Choose the pairs-mode formation weight on DEV rows only: files zrows_w<W>.json.gz -> the W with the most dev
    courses fully right (all tiers pooled; ties: more dev holes numbered right, then the smaller W). Test rows of the
    other weights are never read."""
    stats = []
    for p in paths:
        w = float(os.path.basename(p).split("_w")[1].split(".json")[0])
        rows = [r for r in GT._read(p) if r["split"] == "dev"]
        by = {}
        for r in rows:
            b = by.setdefault(r["tier"], [0, 0, 0, 0])
            b[0] += r["all_correct"]
            b[1] += r["number"]
            b[2] += r["N"]
            b[3] += 1
        stats.append(dict(w=w, path=p, fully=sum(r["all_correct"] for r in rows), numbered=sum(r["number"] for r in rows),
                          holes=sum(r["N"] for r in rows), by_tier=by))
        print(f"dev W={w}: fully right {stats[-1]['fully']} / {len(rows)}, numbered {stats[-1]['numbered']} / "
              f"{stats[-1]['holes']}  " + "  ".join(f"{t}: {b[0]}/{b[3]} {b[1] / max(b[2], 1):.1%}" for t, b in sorted(by.items())))
    best = sorted(stats, key=lambda s: (-s["fully"], -s["numbered"], s["w"]))[0]
    json.dump(dict(chosen=best["w"], path=best["path"], dev=stats), open(out, "w"), indent=1)
    print("chosen W", best["w"])
    return best


CARD_TIERS = ("osm_card", "unmapped_card")


def pick_card(paths, out, merged):
    """v3: choose the card-geometry variant on DEV card-tier rows only. Files zrows_<variant>.json.gz, variant
    c<CARD_W>[n] ('n' = no nesting); c0 is v2's card prior (and holds the no-card tiers). Most dev card-tier courses
    fully right, then most dev holes numbered right, then the simpler variant (smaller weight, nesting off last).
    Writes the merged rows: no-card tiers from c0, card tiers from the chosen variant. Test rows are not read for
    the choice."""
    stats, rows_by = [], {}
    for p in paths:
        v = os.path.basename(p).split("zrows_")[1].split(".json")[0]
        rows = GT._read(p)
        rows_by[v] = (p, rows)
        dev = [r for r in rows if r["split"] == "dev" and r["tier"] in CARD_TIERS]
        by = {}
        for r in dev:
            b = by.setdefault(r["tier"], [0, 0, 0, 0])
            b[0] += r["all_correct"]
            b[1] += r["number"]
            b[2] += r["N"]
            b[3] += 1
        w = float(v[1:].rstrip("n"))
        stats.append(dict(variant=v, w=w, nest=not v.endswith("n"), path=p, courses=len(dev),
                          fully=sum(r["all_correct"] for r in dev), numbered=sum(r["number"] for r in dev),
                          holes=sum(r["N"] for r in dev), by_tier=by))
        print(f"dev {v:6s}: card tiers fully right {stats[-1]['fully']} / {len(dev)}, numbered "
              f"{stats[-1]['numbered']} / {stats[-1]['holes']}  " +
              "  ".join(f"{t}: {b[0]}/{b[3]} {b[1] / max(b[2], 1):.1%}" for t, b in sorted(by.items())), flush=True)
    best = sorted(stats, key=lambda s: (-s["fully"], -s["numbered"], s["w"], s["nest"]))[0]
    base = rows_by["c0"][1]
    ch = rows_by[best["variant"]][1]
    out_rows = [r for r in base if r["tier"] not in CARD_TIERS] + [r for r in ch if r["tier"] in CARD_TIERS]
    import gzip
    with gzip.open(merged, "wt") as fh:
        json.dump(out_rows, fh)
    json.dump(dict(chosen=best["variant"], merged=merged, dev=stats), open(out, "w"), indent=1)
    print("chosen card variant", best["variant"], "->", merged, len(out_rows), "rows")
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["solve", "gate", "gate2", "pick", "pick_card"])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--tiers", default="osm_card,nocard")
    ap.add_argument("--split", default="all")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--slugs", default="")
    ap.add_argument("--out")
    ap.add_argument("--tag", default="default")
    ap.add_argument("--pairs-root", help="v2: hole_pairs/1 per <tier>/<slug>.json (workstream A)")
    ap.add_argument("--pairs-root-dev", help="v2: out-of-fold hole_pairs/1 for the dev courses (oof_pairs.py)")
    ap.add_argument("--method", default="sequence_v2")
    ap.add_argument("--merged", help="pick_card: merged rows file (.json.gz)")
    a = ap.parse_args()
    if a.what == "solve":
        k, of = (int(v) for v in a.shard.split("/"))
        rows = solve_rows(a.tiers.split(","), a.split, k, of, a.slugs.split(",") if a.slugs else None,
                          a.pairs_root, a.pairs_root_dev)
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(rows, open(a.out, "w"), default=float)
    elif a.what == "pick":
        pick(a.paths, a.out)
    elif a.what == "pick_card":
        pick_card(a.paths, a.out, a.merged)
    elif a.what == "gate2":
        gate_and_write_v2(a.paths, a.tag, a.method)
    else:
        gate_and_write(a.paths, a.tag)


if __name__ == "__main__":
    main()
