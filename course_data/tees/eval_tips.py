"""Fit / evaluate tip_candidates.py (unmapped back tees) on the zero_tap benchmark, feeding accepted tips to cardless.

    python3 course_data/tees/eval_tips.py --fit     # fit tip_model.json on DEV (logistic + threshold), score dev
    python3 course_data/tees/eval_tips.py --test    # also score test once -> eval_tips.json

Only courses with lidar pads / segment / scene files have candidates (the 'imagery subset'); the other bench
courses are unchanged by construction and are reported in the full-split numbers as is.
Truth for the candidate label: the cleaned web card's back yardage lies inside the candidate (+-5 yds) and beyond
the farthest OSM box (+5 yds).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import cardless as CL  # noqa: E402
import eval_cardless as E  # noqa: E402
import tip_candidates as TC  # noqa: E402


def prepare(courses):
    for c in courses:
        cands = TC.load_candidates(c["files"], resolve=lambda p: E._p(p) or p)
        c["cands"] = cands
        c["rows"] = TC.candidate_rows(c["holes"], c["tees"], cands) if cands else [(None, [])] * c["n"]
        yb = c["sets"][0][1]
        for i, (top, rows) in enumerate(c["rows"]):
            for r in rows:
                r["y"] = float(r["d_front"] - TC.HIT_YD <= yb[i] <= r["d_back"] + TC.HIT_YD and yb[i] > top + TC.HIT_YD)
    return courses


def auc(ps, ys):
    pos = [p for p, y in zip(ps, ys) if y]
    neg = [p for p, y in zip(ps, ys) if not y]
    if not pos or not neg:
        return None
    s = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return round(s / (len(pos) * len(neg)), 3)


def apply(courses, model, thr):
    st = dict(accepted=0, true=0, too_long=0, holes_uncovered=0, uncovered_fixed=0)
    for c in courses:
        if not c["cands"]:
            c["extra"] = None
            continue
        c["extra"], _ = TC.select_tips(c["holes"], c["tees"], c["cands"], model, thr)
        yb = c["sets"][0][1]
        for i, (ex, (top, rows)) in enumerate(zip(c["extra"], c["rows"])):
            unc = top is not None and yb[i] > top + TC.HIT_YD
            st["holes_uncovered"] += unc
            if ex:
                st["accepted"] += 1
                m = CL.measure_boxes(c["holes"][i], ex)[0]
                hit = m["d_front"] - TC.HIT_YD <= yb[i] <= m["d_back"] + TC.HIT_YD
                st["true"] += hit and unc
                st["uncovered_fixed"] += hit and unc
                st["too_long"] += m["d_front"] > yb[i] + 10
    st["precision"] = round(st["true"] / max(1, st["accepted"]), 3)
    st["false_positive_rate"] = round(1 - st["precision"], 3) if st["accepted"] else None
    st["recall_of_unmapped"] = round(st["uncovered_fixed"] / max(1, st["holes_uncovered"]), 3)
    return st


def summary(o):
    he, te = o["hole_yd_err"], o["total_yd_err"]
    return dict(courses=o["courses"], holes=o["holes"], back=he.get("back"), second=he.get("2nd"),
                back_total=te.get("back"), second_total=te.get("2nd"), S_exact=o["S_exact"], S_within1=o["S_within1"],
                par_hole_acc=o["par_hole_acc"])


def score(courses, model, use):
    for c in courses:
        if not use:
            c["extra"] = None
    o, pc = E.evaluate(courses, CL.load_model())
    return summary(o), pc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fit", action="store_true")
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "eval_tips.json"))
    a = ap.parse_args()
    dev = prepare(E.load("dev"))
    dsub = [c for c in dev if c["cands"]]
    X = [r["x"] for c in dsub for _, rows in c["rows"] for r in rows]
    Y = [r["y"] for c in dsub for _, rows in c["rows"] for r in rows]
    print("dev candidates", len(X), "positives", int(sum(Y)), "courses", len(dsub))
    if a.fit:
        w = TC.fit_logistic(X, Y)
        model = dict(w=w, features=list(TC.FEATURES), thr=0.5, fitted_on="zero_tap dev imagery subset",
                     n_candidates=len(X), n_pos=int(sum(Y)))
        sweep = {}
        for thr in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
            st = apply(dsub, model, thr)
            s, _ = score(dsub, model, True)
            sweep[thr] = dict(back=s["back"], back_total=s["back_total"], second=s["second"], S_exact=s["S_exact"], tips=st)
            print(thr, json.dumps(sweep[thr]))
        # objective: back within-10 share, minus a penalty on accepted false tips (a fake tip makes a hole too long)
        best = max(sweep, key=lambda t: (sweep[t]["back"]["within10"] - 0.5 * sweep[t]["tips"]["accepted"]
                                         * (1 - sweep[t]["tips"]["precision"]) / max(1, sum(c["n"] for c in dsub)),
                                         -sweep[t]["back"]["p90"]))
        model["thr"] = best
        model["sweep_dev"] = {str(k): v for k, v in sweep.items()}
        json.dump(model, open(TC.MODEL_PATH, "w"), indent=1)
        print("thr", best, "wrote", TC.MODEL_PATH)
    model = TC.load_model()
    res = dict(model_thr=model["thr"], weights=dict(zip(TC.FEATURES, model["w"])))
    ps = [TC.prob(x, model["w"]) for x in X]
    res["dev_candidate_auc"] = auc(ps, Y)
    splits = [("dev", dev)] + ([("test", prepare(E.load("test")))] if a.test else [])
    for name, cs in splits:
        sub = [c for c in cs if c["cands"]]
        if name == "test":
            Xt = [r["x"] for c in sub for _, rows in c["rows"] for r in rows]
            Yt = [r["y"] for c in sub for _, rows in c["rows"] for r in rows]
            res["test_candidate_auc"] = auc([TC.prob(x, model["w"]) for x in Xt], Yt)
        r = {}
        r["subset_before"], pcb = score(sub, model, False)
        r["tips"] = apply(sub, model, model["thr"])
        r["subset_after"], pca = score(sub, model, True)
        r["full_before"], _ = score(cs, model, False)
        apply(sub, model, model["thr"])
        r["full_after"], _ = score(cs, model, True)
        r["per_course"] = [dict(slug=b["slug"], true_back_tot=b["true_back_tot"], before=b["back_tot"],
                                after=x["back_tot"], before_med=b["back_med"], after_med=x["back_med"],
                                S_true=b["S_true"], S_before=b["S"], S_after=x["S"]) for b, x in zip(pcb, pca)]
        res[name] = r
        print(name, json.dumps({k: v for k, v in r.items() if k != "per_course"}, indent=1))
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
