"""Routing v1 vs v2 on the shared validation set (validation_set.json), weight training, and the golfer-confirm
simulation (offline, one process; inputs are the committed caches).

  python course_data/generalize/route_eval.py eval --split train [--methods v1,v2] [--inputs osm|model]
  python course_data/generalize/route_eval.py train [--epochs 12]       # fits routing_v2_weights.json on train
  python course_data/generalize/route_eval.py confirm --split test       # taps-to-correct simulation
  python course_data/generalize/route_eval.py final                     # test split: v1 vs v2 + confirm -> eval_v2.json

Inputs per course (`load`): the hidden-holes inputs of report.py's V-osm (OSM greens / tees / fairways + segment
model + lidar pads) or V-model (model + lidar only); the card is the web scorecard when found, else pars +
lengths of the hidden OSM ways (`card_kind` osm-derived). Truth = OSM golf=hole ways 1..18 (routing.score).
The test split is only read by `final` (and `eval --split test`): nothing in `train` touches it.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(CD, "platform"), HERE]
import report as RP  # noqa: E402
import routing as R  # noqa: E402
import routing_v2 as R2  # noqa: E402
import validation_set as VS  # noqa: E402

OUT = os.path.join(HERE, "eval_v2.json")


def log(*a):
    print(*a, flush=True)


# ----------------------------------------------------------------------------- data
def load(slug, inputs="osm", card_mode="web"):
    d = os.path.join(HERE, "courses", slug)

    def rd(p):
        return RP.rd(os.path.join(d, p))
    fc, course = rd("osm_golf.geojson"), rd("course.json") or {}
    seg, pads = rd("segment.geojson"), RP.pads_in(rd("pads.json"))
    truth = {k: v for k, v in R.truth_from_fc(fc).items() if int(k) <= 18}
    card = RP.card_of(rd("scorecard.json")) if card_mode == "web" else None
    kind = "web" if card else "osm-derived"
    if not card and card_mode != "none":
        card = RP.synthetic_card(truth)
    if card_mode == "none":
        card, kind = None, "none"
    if inputs == "model" and not seg:
        return None
    inp = R.inputs_from_fc(fc, segment=seg, pads=pads, boundary=course.get("boundary"), hide_holes=True,
                           osm_features=inputs != "model")
    # the OSM file given to v2 (facility points, cart paths): golf=hole ways and refs removed
    fc_h = dict(fc, features=[dict(f, properties={k: v for k, v in f["properties"].items() if k != "ref"})
                              for f in fc["features"] if f["properties"].get("golf") != "hole"])
    return dict(slug=slug, fc=fc_h, inp=inp, card=card, card_kind=kind, truth=truth, boundary=course.get("boundary"))


def truth_allowed(ctx, truth):
    """{ref: bool (nT + 1, nG + 1)} - the (tee, green) pairs routing.score counts as hole `ref` (+ "no tee" on the
    right green). Holes whose green no candidate matches are left free."""
    pr = ctx["proj"]
    out = {}
    for ref, t in truth.items():
        if int(ref) > ctx["n"]:
            continue
        p = R.Proj(*t["green_ll"])
        gx = np.array([math.hypot(*p.fwd(*g["ll"])) for g in ctx["G"]])
        gok = gx <= 20.0
        if not gok.any():
            continue
        line = p.ring(t["line"])
        cum = np.r_[0, np.cumsum(np.hypot(*np.diff(line, axis=0).T))]
        first = line[: max(2, int(np.searchsorted(cum, 0.6 * cum[-1])) + 1)]
        tok = np.array([R._seg_dist(np.asarray(p.fwd(*tt["ll"])), first) <= 40.0 for tt in ctx["T"]], bool)
        m = np.zeros((ctx["nT"] + 1, ctx["nG"] + 1), bool)
        m[np.ix_(np.r_[np.nonzero(tok)[0], ctx["nT"]], np.nonzero(gok)[0])] = True
        out[ref] = m
    return out


def per_hole_ok(res, truth):
    sc = R.score(res, truth)
    return sc, {r: e["hole_ok"] for r, e in sc["per_hole"].items()}


def flags_from_top(res, tau, p_check, fixed=()):
    """Re-derive v2 flags for another (tau, p_check) from the stored top routings (no re-solve)."""
    top = res.get("_top_keys")
    if not top:
        return {r for r, h in res["holes"].items() if h["status"] != "ok"}
    c = np.array([t[0] for t in top])
    p = np.exp(-(c - c.min()) / tau)
    p /= p.sum()
    best = top[0][1]
    out = set()
    for h in range(len(best)):
        ph = sum(pi for pi, t in zip(p, top) if t[1][h] == best[h])
        if ph < p_check and str(h + 1) not in fixed:
            out.add(str(h + 1))
    return out


def run_v2(c, w=None, tau=None, p_check=None, ctx=None):
    ctx = ctx or R2.context(c["inp"], c["card"], fc=c["fc"], boundary=c["boundary"])
    res = R2.solve(ctx, w=w, tau=tau, p_check=p_check, keep_top=300)
    if res.get("cost") is None:
        return res, ctx
    # keep the top routings' (cost, hole keys) for re-flagging at other temperatures
    res["_top_keys"] = [(cst, [R2._hole_key(ctx, t, g) for t, g in a]) for cst, a in res.get("top", [])]
    return res, ctx


def summarise(scores):
    if not scores:
        return {}
    f = lambda k: float(np.mean([s[k] for s in scores]))      # noqa: E731
    return dict(n=len(scores), hole_number_acc=round(f("hole_number_acc"), 3), green_assign_acc=round(f("green_assign_acc"), 3),
                all_correct=round(float(np.mean([s["all_correct"] for s in scores])), 3),
                correct_after_check=round(float(np.mean([s["wrong_unflagged"] == 0 for s in scores])), 3),
                flags_per_course=round(f("flagged"), 2), wrong_per_course=round(f("wrong"), 2),
                wrong_unflagged_per_course=round(f("wrong_unflagged"), 2))


def courses_of(split):
    return [r["slug"] for r in VS.load(split)]


# ----------------------------------------------------------------------------- eval
def evaluate(split, methods=("v1", "v2"), inputs="osm", card_mode="web", w=None, quiet=False):
    rows = []
    for slug in courses_of(split):
        c = load(slug, inputs, card_mode)
        if c is None or len(c["truth"]) < 9:
            continue
        row = dict(slug=slug, card_kind=c["card_kind"])
        for m in methods:
            t0 = time.time()
            if m == "v1":
                res = R.route(c["inp"], c["card"], margins=c["card"] is not None)
            else:
                res, _ = run_v2(c, w=w)
            sc = R.score(res, c["truth"]) if res.get("holes") else dict(hole_number_acc=0, green_assign_acc=0,
                                                                          all_correct=False, flagged=0, wrong=len(c["truth"]),
                                                                          wrong_unflagged=len(c["truth"]), per_hole={})
            sc.pop("per_hole", None)
            sc["seconds"] = round(time.time() - t0, 1)
            row[m] = sc
        rows.append(row)
        if not quiet:
            log(slug, c["card_kind"], *[(m, row[m]["hole_number_acc"], row[m]["flagged"], row[m]["wrong"],
                                         row[m]["wrong_unflagged"]) for m in methods])
    agg = {m: summarise([r[m] for r in rows]) for m in methods}
    return rows, agg


# ----------------------------------------------------------------------------- training
def train(epochs=12, C=0.3, margin=0.5, inputs=("osm", "model"), seed=0, out=R2.WEIGHTS_FILE):
    """Averaged passive-aggressive structured learning: on each train course, the router's best routing vs the
    cheapest routing that agrees with the hidden holes (truth_allowed); when the router is wrong,
    w -= step (f_truth - f_pred) with step = min(C, (w . d + margin x wrong holes) / |d|^2). The averaged weights of
    the epoch with the fewest wrong train holes are kept.
    Then tau / p_check are calibrated on the same courses (min flags with every wrong hole flagged)."""
    data = []
    for slug in courses_of("train"):
        for mode in inputs:
            c = load(slug, mode)
            if c is None or len(c["truth"]) < 9:
                continue
            ctx = R2.context(c["inp"], c["card"], fc=c["fc"], boundary=c["boundary"])
            if not ctx.get("ok"):
                continue
            data.append((c, ctx, truth_allowed(ctx, c["truth"])))
    log("train courses x inputs:", len(data))
    w0, _, _ = R2.load_weights(None)
    w = w0.copy()
    signed = np.array([k in R2.SIGNED for k in R2.FEATURES])
    rnd = np.random.default_rng(seed)
    hist = []

    def wrong_total(wv):
        tot, allc = 0, 0
        for c, ctx, _ in data:
            res = R2.solve(ctx, w=wv, tau=1.0, p_check=0.0, keep_top=1)
            sc = R.score(res, c["truth"])
            tot += sc["wrong"]
            allc += sc["all_correct"]
        return tot, allc
    best = (*wrong_total(w), w.copy(), -1)
    log("start: wrong holes %d, all correct %d" % best[:2])
    wsum, cnt = w.copy(), 1
    for ep in range(epochs):
        n_upd = 0
        for i in rnd.permutation(len(data)):
            c, ctx, allowed = data[i]
            res = R2.solve(ctx, w=w, tau=1.0, p_check=0.0, keep_top=1)
            sc = R.score(res, c["truth"])
            if sc["wrong"] > 0:
                rt = R2.solve(ctx, w=w, allowed=allowed, tau=1.0, p_check=0.0, keep_top=1)
                if rt.get("cost") is not None:
                    d = np.array(rt["features"]) - np.array(res["features"])      # f_truth - f_pred
                    loss = float(w @ d) + margin * sc["wrong"]
                    nn = float(d @ d)
                    if loss > 0 and nn > 1e-9:
                        step = min(C, loss / nn)                                   # passive-aggressive (PA-I)
                        w = w - step * d
                        w = np.where(signed, w, np.maximum(w, 0.0))
                        n_upd += 1
            wsum += w
            cnt += 1
        wa = wsum / cnt
        wr, ac = wrong_total(wa)
        hist.append(dict(epoch=ep, wrong_holes=wr, all_correct=ac, updates=n_upd))
        log(f"epoch {ep}: averaged w -> wrong holes {wr}, all correct {ac}; updates {n_upd}", np.round(wa, 2).tolist())
        if wr < best[0] or (wr == best[0] and ac > best[1]):
            best = (wr, ac, wa.copy(), ep)
    wa, best_ep = best[2], best[3]
    log("best epoch", best_ep, "wrong holes", best[0], "all correct", best[1])
    # calibration of the posterior temperature and the flag threshold
    stats = []
    for c, ctx, _ in data:
        res, _ = run_v2(c, w=wa, tau=1.0, p_check=0.0, ctx=ctx)
        _, ok = per_hole_ok(res, c["truth"])
        stats.append((res, ok))
    best = None
    for tau in (0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0):
        for pc in (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98):
            caught, flags = 0, 0
            for res, ok in stats:
                fl = flags_from_top(res, tau, pc)
                wrong = {r for r, v in ok.items() if not v}
                caught += wrong <= fl
                flags += len(fl)
            obj = caught / len(stats) - 0.01 * flags / len(stats)
            if best is None or obj > best[0]:
                best = (obj, tau, pc, caught / len(stats), flags / len(stats))
    log("calibration: tau %.2f p_check %.2f -> correct after check %.2f, flags/course %.2f" % best[1:])
    js = dict(schema="routing_v2_weights/1", trained_on="validation_set.json split train (inputs %s)" % "+".join(inputs),
              n=len(data), epochs=epochs, C=C, margin=margin, best_epoch=best_ep, w={k: round(float(v), 4) for k, v in zip(R2.FEATURES, wa)},
              tau=best[1], p_check=best[2], calibration=dict(correct_after_check=round(best[3], 3),
                                                             flags_per_course=round(best[4], 2)),
              history=hist, built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    json.dump(js, open(out, "w"), indent=1)
    return js


# ----------------------------------------------------------------------------- golfer confirm simulation
def simulate_confirm(c, policy="eig", max_taps=40, w=None, tau=None, p_check=None, p_stop=None):
    """An oracle golfer (the hidden OSM holes) answers platform/confirm.py's questions until the routing is 100 %
    right; every answer re-solves the round. policy: eig (best bits per tap), eig_confirm (yes / no questions
    only), flagged (confirm the flagged holes in card order, then the least sure). -> dict(taps (None = not
    reached within max_taps), questions, log, stop_rule_taps, stop_rule_wrong): stop_rule_* = when the app
    itself stops asking (every unconfirmed hole p_hole >= p_stop) and how many holes are still wrong then."""
    import confirm as CF
    s = CF.Session(c["inp"], c["card"], fc=c["fc"], boundary=c["boundary"], w=w, tau=tau, p_check=p_check,
                   p_stop=p_stop)
    truth = c["truth"]
    stop = None
    while True:
        if s.res.get("cost") is None:
            return dict(taps=None, questions=len(s.history), log=s.history, stop_rule_taps=None, stop_rule_wrong=None,
                        wrong_left=None)
        _, ok = per_hole_ok(s.res, truth)
        wrong = [r for r, v in ok.items() if not v]
        if stop is None and s.done():
            stop = (s.taps, len(wrong))
        if not wrong or s.taps >= max_taps:
            st = stop or (s.taps, len(wrong))
            return dict(taps=s.taps if not wrong else None, questions=len(s.history), log=s.history,
                        stop_rule_taps=st[0], stop_rule_wrong=st[1], wrong_left=len(wrong))
        qs = s.questions(k=200)
        if policy == "eig_confirm":
            qs = [q for q in qs if q["kind"] == "confirm"]
        elif policy == "flagged":            # v1's check list: each flagged hole in card order, a locate after a "no"
            pick = [q for q in qs if (q["kind"] == "confirm") != (q["ref"] in s.rejected)]
            fl = sorted([q for q in pick if s.res["holes"][q["ref"]]["status"] != "ok"], key=lambda q: int(q["ref"]))
            qs = fl or sorted(pick, key=lambda q: q["p_hole"])
        if not qs:
            st = stop or (s.taps, len(wrong))
            return dict(taps=None, questions=len(s.history), log=s.history, stop_rule_taps=st[0],
                        stop_rule_wrong=st[1], wrong_left=len(wrong))
        q = qs[0]
        r = q["ref"]
        if q["kind"] == "confirm":
            s.answer(dict(question=q["id"], answer="yes" if ok.get(r, True) else "no"))
        else:
            t = truth.get(r)
            if t is None:
                h = s.res["holes"][r]
                s.answer(dict(question=q["id"], answer=dict(tee_ll=h.get("tee_ll"), green_ll=h.get("green_ll"))))
            else:
                s.answer(dict(question=q["id"], answer=dict(tee_ll=list(t["tee_ll"]), green_ll=list(t["green_ll"]))))


def confirm_study(split, policies=("eig", "eig_confirm", "flagged", "locate_all"), inputs="osm", w=None, max_taps=40):
    rows = []
    for slug in courses_of(split):
        c = load(slug, inputs)
        if c is None or len(c["truth"]) < 9:
            continue
        row = dict(slug=slug)
        for pol in policies:
            if pol == "locate_all":            # no inference at all: tap every hole's tee + green
                row[pol] = dict(taps=2 * len(c["truth"]))
                continue
            row[pol] = simulate_confirm(c, policy=pol, max_taps=max_taps, w=w)
            row[pol]["log"] = row[pol]["log"][:40]
        rows.append(row)
        log(slug, {p: (row[p].get("taps"), row[p].get("stop_rule_taps"), row[p].get("stop_rule_wrong")) for p in policies})
    agg = {}
    for pol in policies:
        t = [r[pol].get("taps") for r in rows]
        ok = [x for x in t if x is not None]
        agg[pol] = dict(n=len(rows), reached_100=round(len(ok) / max(len(rows), 1), 3),
                        median_taps=float(np.median(ok)) if ok else None, mean_taps=round(float(np.mean(ok)), 2) if ok else None,
                        p90_taps=float(np.percentile(ok, 90)) if ok else None,
                        zero_taps=round(sum(x == 0 for x in ok) / max(len(rows), 1), 3),
                        within_3=round(sum(x <= 3 for x in ok) / max(len(rows), 1), 3),
                        within_6=round(sum(x <= 6 for x in ok) / max(len(rows), 1), 3))
        if pol != "locate_all":
            st = [r[pol] for r in rows]
            agg[pol].update(stop_rule_mean_taps=round(float(np.mean([s["stop_rule_taps"] for s in st])), 2),
                            stop_rule_all_correct=round(float(np.mean([s["stop_rule_wrong"] == 0 for s in st])), 3),
                            stop_rule_wrong_holes=round(float(np.mean([s["stop_rule_wrong"] or 0 for s in st])), 2))
    return rows, agg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["eval", "train", "confirm", "final"])
    ap.add_argument("--split", default="train")
    ap.add_argument("--methods", default="v1,v2")
    ap.add_argument("--inputs", default="osm")
    ap.add_argument("--card", default="web", choices=["web", "none"])
    ap.add_argument("--epochs", type=int, default=12)
    ap.add_argument("--policies", default="eig,eig_confirm,flagged,locate_all")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "eval":
        rows, agg = evaluate(a.split, a.methods.split(","), a.inputs, a.card)
        log(json.dumps(agg, indent=1))
        if a.out:
            json.dump(dict(rows=rows, agg=agg), open(a.out, "w"), indent=1)
    elif a.cmd == "train":
        if a.split != "train":
            sys.exit("training reads the train split only")
        train(a.epochs)
    elif a.cmd == "confirm":
        rows, agg = confirm_study(a.split, a.policies.split(","), a.inputs)
        log(json.dumps(agg, indent=1))
        if a.out:
            json.dump(dict(rows=rows, agg=agg), open(a.out, "w"), indent=1, default=str)
    else:
        out = dict(built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   weights=json.load(open(R2.WEIGHTS_FILE)) if os.path.exists(R2.WEIGHTS_FILE) else None)
        for split in ("train", "test"):
            for inputs in ("osm", "model"):
                rows, agg = evaluate(split, ("v1", "v2"), inputs)
                out[f"{split}_{inputs}"] = dict(agg=agg, rows=rows)
                log(split, inputs, json.dumps(agg))
            rows, agg = evaluate(split, ("v1", "v2"), "osm", "none")
            out[f"{split}_osm_nocard"] = dict(agg=agg, rows=rows)
        rows, agg = confirm_study("test", a.policies.split(","), "osm")
        out["confirm_test_osm"] = dict(agg=agg, rows=rows)
        rows, agg = confirm_study("test", ("eig",), "model")
        out["confirm_test_model"] = dict(agg=agg, rows=rows)
        json.dump(out, open(a.out or OUT, "w"), indent=1, default=str)
        log("wrote", a.out or OUT)


if __name__ == "__main__":
    main()
