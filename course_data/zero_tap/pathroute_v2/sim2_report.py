"""Summarise a sim2.py run: taps per course to reach a pair precision with confirm-and-resolve, vs no resolve.

    python course_data/zero_tap/pathroute_v2/sim2_report.py SIM.json [--out summary_resolve.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ZT, "pathroute"), ZT]
import bench as B  # noqa: E402
import confidence as CF  # noqa: E402


def stop(traj, thr):
    for k, st in enumerate(traj):
        if st["min_un"] >= thr:
            return k
    return len(traj) - 1


def at(sim, thr):
    """Per course at threshold thr: (taps, right, total, all_pairs_right, k)."""
    out = []
    for r in sim:
        if r.get("error") or not r.get("traj"):
            N = r.get("N") or B.truth(r["slug"])["n_holes"]
            out.append(dict(slug=r["slug"], taps=N, right=N, total=N, allright=False, k=None, N=N))
            continue
        k = stop(r["traj"], thr)
        st = r["traj"][k]
        y = np.array(st["y"])
        out.append(dict(slug=r["slug"], taps=st["taps"] + st["miss"], right=int(y.sum()) + st["miss"],
                        total=len(y) + st["miss"], allright=int(y.sum()) == st["N"] and st["miss"] == 0, k=k,
                        N=st["N"], kind=r["kind"]))
    return out


def dist(v):
    v = np.asarray(v, float)
    return dict(mean=round(float(v.mean()), 2), median=float(np.median(v)), p75=float(np.percentile(v, 75)),
                p90=float(np.percentile(v, 90)), max=float(v.max()), zero=round(float(np.mean(v == 0)), 3),
                hist={str(a): int(np.sum(v == a)) for a in range(0, 8)} | {"8+": int(np.sum(v >= 8))})


def summarise(sim, target=0.98, extra_thr=(0.9, 0.95, 0.98), add_missing=True, split="test"):
    have = {r["slug"] for r in sim}
    if add_missing:            # test courses without a result (no OSM tees): each true hole = one tap
        sim = list(sim) + [dict(slug=r["slug"], error="no result (no OSM tees / not simulated)", kind=r["kind"])
                           for r in B.courses(split) if r["slug"] not in have]
    grid = sorted({0.0} | {c for r in sim for st in r.get("traj") or [] for c in [st["min_un"]]} | {0.999})
    best = None
    for thr in grid:
        rows = at(sim, thr)
        prec = sum(x["right"] for x in rows) / sum(x["total"] for x in rows)
        if prec >= target:
            best = (thr, rows, prec)
            break
    out = dict(n_courses=len(sim))
    if best:
        thr, rows, prec = best
        out["resolve_98"] = dict(threshold=round(thr, 4), precision=round(prec, 4),
                                 taps=dist([x["taps"] for x in rows]),
                                 all_pairs_right=round(float(np.mean([x["allright"] for x in rows])), 3))
    for thr in extra_thr:
        rows = at(sim, thr)
        out[f"resolve_thr_{thr}"] = dict(precision=round(sum(x["right"] for x in rows) / sum(x["total"] for x in rows), 4),
                                         taps=dist([x["taps"] for x in rows]),
                                         all_pairs_right=round(float(np.mean([x["allright"] for x in rows])), 3))
    # no resolve: confirm every hole below a threshold, no re-decode (run2.pair_summary's estimate)
    cs = []
    for r in sim:
        if r.get("error") or not r.get("traj"):
            N = B.truth(r["slug"])["n_holes"]
            cs.append((np.zeros(N), np.zeros(N, int)))
            continue
        st = r["traj"][0]
        cs.append((np.r_[st["conf"], np.zeros(st["miss"])], np.r_[st["y"], np.zeros(st["miss"], int)]))
    tp = CF.taps_to_precision(cs, target)
    thr0 = tp[0]
    taps0 = [int(np.sum(c < thr0)) for c, _ in cs]
    out["no_resolve_98"] = dict(threshold=round(thr0, 4), precision=round(tp[2], 4), taps=dist(taps0))
    # all 18 pairs right: oracle taps = first step where every true hole is paired right (golfer adds misses)
    orc = []
    for r in sim:
        if r.get("error") or not r.get("traj"):
            orc.append(B.truth(r["slug"])["n_holes"])
            continue
        k = next((k for k, st in enumerate(r["traj"]) if sum(st["y"]) == st["N"] and st["miss"] == 0), None)
        orc.append(r["traj"][k]["taps"] if k is not None else r["traj"][-1]["taps"] + r["traj"][-1]["miss"])
    out["all_pairs_right_taps_oracle"] = dist(orc)
    noresolve_all = []
    for c, y in cs:                    # no resolve: asking every wrong hole needs all holes below the wrong one's conf
        wrong = c[y == 0]
        noresolve_all.append(int(np.sum(c <= wrong.max())) if len(wrong) else 0)
    out["all_pairs_right_taps_no_resolve_oracle"] = dist(noresolve_all)
    # numbering (9 / 18-hole courses): no tap / + hole-1 tap, at step 0 and at the 98 % stop
    num = dict(n=0, N=0, s0=0, s0_h1=0, stop=0, stop_h1=0, all_s0_h1=0, all_stop_h1=0)
    stops = {x["slug"]: x["k"] for x in best[1]} if best else {}
    for r in sim:
        if r.get("error") or not r.get("traj") or r["kind"] not in (9, 18):
            continue
        N = r["traj"][0]["N"]
        num["n"] += 1
        num["N"] += N
        h1 = r.get("hole1") or {}
        k = stops.get(r["slug"], 0) or 0
        num["s0"] += r["traj"][0]["num"]
        num["stop"] += r["traj"][k]["num"]
        a = h1.get(str(0), h1.get(0))
        b = h1.get(str(k), h1.get(k))
        num["s0_h1"] += a["num"] if a else r["traj"][0]["num"]
        num["stop_h1"] += b["num"] if b else r["traj"][k]["num"]
        num["all_s0_h1"] += int(bool(a) and a["num"] == N)
        num["all_stop_h1"] += int(bool(b) and b["num"] == N)
    out["numbering_9_18"] = dict(courses=num["n"], holes=num["N"],
                                 no_tap=round(num["s0"] / num["N"], 4),
                                 hole1_tap_only=round(num["s0_h1"] / num["N"], 4),
                                 at_98_stop=round(num["stop"] / num["N"], 4),
                                 at_98_stop_plus_hole1=round(num["stop_h1"] / num["N"], 4),
                                 courses_all_numbered_hole1_only=round(num["all_s0_h1"] / max(num["n"], 1), 3),
                                 courses_all_numbered_98_plus_hole1=round(num["all_stop_h1"] / max(num["n"], 1), 3))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sim")
    ap.add_argument("--out")
    ap.add_argument("--errors", help="partial run: add only these slugs (comma list) as no-result courses")
    a = ap.parse_args()
    sim = json.load(open(a.sim))
    if a.errors is not None:
        ks = {r["slug"]: r["kind"] for r in B.courses("test")}
        sim += [dict(slug=x, error="no result", kind=ks[x]) for x in a.errors.split(",") if x in ks]
    s = summarise(sim, add_missing=a.errors is None)
    print(json.dumps(s, indent=1))
    if a.out:
        json.dump(s, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
