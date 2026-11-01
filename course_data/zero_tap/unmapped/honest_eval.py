"""Honest unmapped-tier table: pairing + taps per method, split by perception provenance (detect_eval.perc_split).

    python course_data/zero_tap/unmapped/honest_eval.py --results results/<method>/<tier> ... [--json OUT]

Per method dir and split: courses, paired (bench 'formed'), all pairs right, numbered, holes right, and taps to 98 %
pair precision. The taps threshold is chosen on DEV (all dev courses of that method dir, CF.taps_to_precision) and
applied unchanged to test (`taps_dev_thr`); `taps_oracle` is the test-optimal threshold, shown only to expose the
gap. 'held_out' = courses whose scene came from perception models that never trained on their state.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ZT, "pathroute_v2"), ZT]
import bench as B  # noqa: E402
import detect_eval as DE  # noqa: E402
import confidence as CF  # noqa: E402
import run2 as R2  # noqa: E402


def taps_at(cs, thr):
    right = taps = n = zero = 0
    for c, y in cs:
        ask = c < thr
        right += int(np.sum(y[~ask])) + int(ask.sum())
        taps += int(ask.sum())
        n += len(c)
        zero += int(ask.sum() == 0)
    return dict(threshold=round(float(thr), 4), taps_per_course=round(taps / max(len(cs), 1), 2),
                precision=round(right / max(n, 1), 4), courses_no_tap=round(zero / max(len(cs), 1), 4))


def method_rows(rd, split):
    res = {x["slug"]: x for x in (B.load_results(rd) if os.path.exists(rd) else [])}
    tier = os.path.basename(rd.rstrip("/"))
    out = []
    for r in B.courses(split, tier=tier):
        t = B.truth(r["slug"])
        x = res.get(r["slug"]) or dict(slug=r["slug"], holes=[], error="no result")
        x.setdefault("slug", r["slug"])
        sc = DE.load_scene(r)
        r["_perc_models"] = (sc.get("sources") or {}).get("models", {}).get("perception")
        G, T = DE.green_cands(sc), DE.tee_cands(sc)
        det = DE.detect_course(t, G, T, lambda g: True, lambda q: True)
        pc = DE.pairing_course(x, t, det)
        cr = R2.course_rows([x])[0]
        out.append(dict(row=r, pc=pc, cs=(np.r_[cr["c"], np.zeros(cr["miss"])], np.r_[cr["y"], np.zeros(cr["miss"], int)])))
    return out


def summarize(rows, thr=None):
    N = sum(p["pc"]["N"] for p in rows)
    d = dict(courses=len(rows), holes=N,
             paired=round(sum(p["pc"]["formed"] for p in rows) / max(1, N), 4),
             all_pairs_right=round(sum(p["pc"]["all_right"] for p in rows) / max(1, len(rows)), 4),
             numbered=round(sum(p["pc"]["number"] for p in rows) / max(1, N), 4),
             holes_right=round(sum(p["pc"]["holes_ok"] for p in rows) / max(1, len(rows)), 4))
    cs = [p["cs"] for p in rows]
    has_conf = any(len(c) and np.any(c > 0) for c, _ in cs)
    if has_conf and rows:
        tp = CF.taps_to_precision(cs, 0.98)
        d["taps_oracle"] = dict(threshold=round(tp[0], 4), taps_per_course=round(tp[1], 2), precision=round(tp[2], 4)) if tp else None
        if thr is not None:
            d["taps_dev_thr"] = taps_at(cs, thr)
    return d


def run(result_dirs):
    out = {}
    for rd in result_dirs:
        key = os.path.relpath(os.path.abspath(rd), os.path.join(ZT, "results"))
        dev = method_rows(rd, "dev")
        test = method_rows(rd, "test")
        tp = CF.taps_to_precision([p["cs"] for p in dev], 0.98) if dev else None
        thr = tp[0] if tp else None
        o = dict(dev_threshold=None if thr is None else round(thr, 4))
        for sp, rows in (("dev", dev), ("test", test)):
            for sub in ("all", "held_out", "in_sample"):
                sel = [p for p in rows if sub == "all" or DE.perc_split(p["row"]) == sub]
                o[f"{sp}/{sub}"] = summarize(sel, thr)
        out[key] = o
    return out


def show(o):
    for m, d in o.items():
        print(f"== {m} (dev taps threshold {d['dev_threshold']})")
        for k, v in d.items():
            if k == "dev_threshold":
                continue
            t = v.get("taps_dev_thr") or {}
            print(f"  {k:16s} n={v['courses']:3d} paired {100 * v['paired']:5.1f} all-pairs {100 * v['all_pairs_right']:5.1f} "
                  f"numbered {100 * v['numbered']:5.1f} holes-right {100 * v['holes_right']:5.1f} "
                  f"taps@dev {t.get('taps_per_course', '-')} ({100 * t['precision']:.1f} %)" if t else
                  f"  {k:16s} n={v['courses']:3d} paired {100 * v['paired']:5.1f} all-pairs {100 * v['all_pairs_right']:5.1f} "
                  f"numbered {100 * v['numbered']:5.1f} holes-right {100 * v['holes_right']:5.1f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", nargs="+")
    ap.add_argument("--json")
    a = ap.parse_args()
    o = run(a.results)
    show(o)
    if a.json:
        json.dump(o, open(a.json, "w"), indent=1)
