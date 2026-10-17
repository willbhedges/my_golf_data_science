"""Recovery study: simulated golfers with known patterns -> data -> posterior. How much data is enough?

  python3 course_data/personal/validate.py run --shard 0 --nshards 12 [--quick] --out parts/rec_0.jsonl
  python3 course_data/personal/validate.py merge parts/rec_*.jsonl       -> output/recovery.json, recovery.md

Experiments (bag = Driver + 4-wood, the book's numbers):
  lm       launch-monitor shots per club n in {10, 25, 50, 100, 200}; range factor f uncertain ("lm") or the
           range treated as the course ("lm_f1": data made with f = 1, f fixed at 1)
  course   on-course tee shots, R rounds x (10 Driver + 3 4-wood), R in {1, 3, 5, 10, 20, 40}; aim known to
           3 yds (the app logged the plan's aim) or 10 yds (tee -> pin line); balls > 35 yds offline censored
  both     50 launch-monitor shots per club + R rounds on course (aim sd 3)
  summary  R rounds of summary stats on Spirit Hollow (14 driving holes, Black tees), R in {5, 10, 20, 40, 80};
           truth simulated with the v2 course simulator (lie raster, roll-out, penalties), fitted through the
           emulator (emulator.py bank, built first)
Golfers: 24 drawn from the prior + 5 scenarios x 4 replicates (book 70; published 82; wide 95 with nu = 4 tails;
a fader, bias +8; mishits 25 %), each under the v2 prior and the generic prior.
"""
import argparse
import glob
import json
import os
import sys
import time
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bayes as B                                      # noqa: E402
import simulate as S                                   # noqa: E402

BAG = {k: v for k, v in B.BOOK_BAG.items() if k in ("Driver", "4-wood")}
BREAK_EVENS = [62.9, 67.4, 77.7, 79.1, 81.7, 86.0]    # v2 width break-evens (holes 1, 8, 13, 5, 4, 16)
SCEN = {"book70": dict(W=70.0), "published82": dict(W=82.0), "wide95_t4": dict(W=95.0, nu=4.0),
        "fader+8": dict(beta=8.0), "mishit25": dict(ps=0.25)}
N_PRIOR, N_REP = 24, 4
GRID = dict(lm=[10, 25, 50, 100, 200], lm_f1=[10, 25, 50, 100, 200], course3=[1, 3, 5, 10, 20, 40],
            course10=[1, 3, 5, 10, 20, 40], both=[1, 3, 5, 10], summary=[5, 10, 20, 40, 80])


def tasks(quick=False):
    out = []
    for exp, ns in GRID.items():
        for prior in ("v2", "generic"):
            gol = [("prior", i) for i in range(N_PRIOR if not quick else 2)] + \
                  [(s, r) for s in SCEN for r in range(N_REP if not quick else 1)]
            for n in (ns if not quick else ns[:2]):
                for g in gol:
                    out.append(dict(exp=exp, prior=prior, n=n, golfer=g[0], rep=g[1]))
    return out


def _h(obj):
    """Stable seed (Python's hash() of a str changes per process)."""
    return zlib.crc32(json.dumps(obj).encode())


def make_truth(task):
    prior = B.Prior.v2() if task["prior"] == "v2" else B.Prior.generic()
    m = B.Model(BAG, prior)
    seed = _h((task["prior"], task["golfer"], task["rep"]))
    rng = np.random.default_rng(seed)
    if task["golfer"] == "prior":
        x = m.sample_prior(1, rng)[0]
    else:
        x = m.prior_mean()
        x[m.ix["c_common"]] += rng.normal(0, 3)
        sc = SCEN[task["golfer"]]
        if "W" in sc:
            x[m.ix["logW"]] = np.log(sc["W"])
        if "nu" in sc:
            x[m.ix["log_nu"]] = np.log(sc["nu"])
        if "beta" in sc:
            x[m.ix["beta"]] = sc["beta"]
        if "ps" in sc:
            x[m.ix["lg_ps"]] = np.log(sc["ps"] / (1 - sc["ps"]))
    if task["exp"] == "lm_f1":
        x[m.ix["log_f"]] = 0.0
    return prior, x, S.truth_from(m, x)


_EMU, _SIMS = {}, {}


def summary_data(truth, rounds, rng, nuis):
    """Simulate R rounds of app summary stats on Spirit Hollow (one Driver tee shot per driving hole)."""
    import emulator as E
    if "sims" not in _SIMS:
        _SIMS["sims"] = E.make_sims(n=10)
    c = truth["clubs"]["Driver"]
    th = dict(logW=np.log(c["width"]), beta=c["bias"], inv_nu=1 / truth["nu"], carry=c["carry"], roll=c["roll"],
              ps=truth["ps"], ph=truth["ph"], log_dm=np.log(truth["dm"]), **nuis)
    n = fw = L = R = pen = 0
    drives = []
    for hs in _SIMS["sims"]:
        hs.reseed(rounds, int(rng.integers(2 ** 31)))
        o = hs.outcomes(th)
        n += rounds
        fw += int(o["on_fw"].sum())
        L += int(o["left"].sum())
        R += int((~o["on_fw"] & ~o["left"]).sum())
        pen += int((rng.random(rounds) < o["p_pen"]).sum())
        drives += list(np.hypot(o["a"], o["l"])[o["good"]])
    return [dict(n_tee=n, fairways=fw, miss_left=L, miss_right=R, tee_penalties=pen,
                 avg_drive=float(np.mean(drives)) if drives else None, n_drives=len(drives), club="Driver",
                 course="spirit_hollow", holes=None)]


def run_task(task, emu_path=None):
    prior, x, T = make_truth(task)
    rng = np.random.default_rng(_h(tuple(task.values())))
    exp, n = task["exp"], task["n"]
    data = B.Data()
    fix = {}
    emus = {}
    if exp in ("lm", "lm_f1"):
        for k in BAG:
            data.lm += S.lm_shots(T, k, n, rng, session="s0", session_offset=float(rng.normal(0, 3)))
        if exp == "lm_f1":
            fix = {"log_f": 0.0}
    elif exp.startswith("course") or exp == "both":
        aim = 3.0 if exp in ("course3", "both") else 10.0
        data.course += S.course_shots(T, "Driver", 10 * n, rng, aim_sd=aim)
        data.course += S.course_shots(T, "4-wood", 3 * n, rng, aim_sd=aim)
        if exp == "both":
            for k in BAG:
                data.lm += S.lm_shots(T, k, 50, rng, session="s0", session_offset=float(rng.normal(0, 3)))
    elif exp == "summary":
        import emulator as E
        if "spirit_hollow" not in _EMU:
            _EMU["spirit_hollow"] = E.Emulator(emu_path)
        emus = _EMU
        nuis = dict(rho=float(rng.uniform(-0.1, 0.3)), kappa=float(rng.uniform(0, 0.16)),
                    lost_edge=float(rng.uniform(0.1, 0.4)), lost_deep=float(rng.uniform(0.5, 0.8)))
        data.summary = summary_data(T, n, rng, nuis)
    m = B.Model(BAG, prior, data, emus, fix=fix)
    t0 = time.time()
    post = m.fit(n_draws=2000, seed=int(rng.integers(1e9)))
    p = post.p
    res = dict(task, secs=round(time.time() - t0, 1), ess=post.info["ess"], method=post.info["method"])
    tv = dict(W=T["clubs"]["Driver"]["width"], ratio4=T["clubs"]["4-wood"]["ratio"],
              carry=T["clubs"]["Driver"]["carry"], bias=T["clubs"]["Driver"]["bias"], ps=T["ps"],
              nu=T["nu"], roll=T["clubs"]["Driver"]["roll"], f=T["f"])
    pv = dict(W=p["clubs"]["Driver"]["width"], ratio4=p["clubs"]["4-wood"]["ratio"],
              carry=p["clubs"]["Driver"]["carry"], bias=p["clubs"]["Driver"]["bias"], ps=p["ps"], nu=p["nu"],
              roll=p["clubs"]["Driver"]["roll"], f=p["f"])
    for k in tv:
        s = post.summary(pv[k])
        res[k] = dict(truth=float(tv[k]), median=s["median"], sd=s["sd"], lo=s["ci90"][0], hi=s["ci90"][1],
                      cover=bool(s["ci90"][0] <= tv[k] <= s["ci90"][1]))
    W = pv["W"]
    res["breakeven"] = [dict(b=b, truth_above=bool(tv["W"] > b), p_above=float(np.sum(post.w * (W > b))))
                        for b in BREAK_EVENS]
    if exp == "summary":
        res["obs"] = data.summary[0]
    return res


def merge(paths, out_dir):
    rows = [json.loads(l) for p in paths for l in open(p) if l.strip()]
    errors = [r for r in rows if "error" in r]
    rows = [r for r in rows if "error" not in r]
    tab = {}
    for r in rows:
        key = (r["exp"], r["prior"], r["n"])
        tab.setdefault(key, []).append(r)
    summ = []
    for (exp, prior, n), rs in sorted(tab.items(), key=lambda kv: (list(GRID).index(kv[0][0]), kv[0][1], kv[0][2])):
        def agg(rows, par):
            e = np.array([r[par]["median"] - r[par]["truth"] for r in rows])
            rel = par in ("W", "nu", "roll", "f", "ratio4")
            if rel:
                e = np.array([np.log(r[par]["median"] / r[par]["truth"]) for r in rows])
            return dict(err_med_abs=float(np.median(np.abs(e))), rmse=float(np.sqrt(np.mean(e ** 2))),
                        sd=float(np.median([r[par]["sd"] for r in rows])),
                        ci_width=float(np.median([r[par]["hi"] - r[par]["lo"] for r in rows])),
                        cover=float(np.mean([r[par]["cover"] for r in rows])), rel=rel)
        pri = [r for r in rs if r["golfer"] == "prior"]
        row = dict(exp=exp, prior=prior, n=n, n_fits=len(rs), secs=float(np.median([r["secs"] for r in rs])),
                   all={p: agg(rs, p) for p in ("W", "ratio4", "carry", "bias", "ps", "nu", "roll", "f")},
                   from_prior={p: agg(pri, p) for p in ("W", "bias", "carry")} if pri else None,
                   scenarios={s: dict(W_median=float(np.median([r["W"]["median"] for r in rs if r["golfer"] == s])),
                                      W_truth=float(np.median([r["W"]["truth"] for r in rs if r["golfer"] == s])),
                                      W_ci=[float(np.median([r["W"]["lo"] for r in rs if r["golfer"] == s])),
                                            float(np.median([r["W"]["hi"] for r in rs if r["golfer"] == s]))],
                                      bias_median=float(np.median([r["bias"]["median"] for r in rs if r["golfer"] == s])))
                              for s in SCEN if any(r["golfer"] == s for r in rs)})
        be = [(b["truth_above"], b["p_above"], abs(r["W"]["truth"] - b["b"])) for r in rs for b in r["breakeven"]]
        far = [(t, pa) for t, pa, d in be if d >= 5]
        row["breakeven_correct_5yd"] = float(np.mean([(pa > 0.5) == t for t, pa in far])) if far else None
        row["breakeven_confident_5yd"] = float(np.mean([(pa > 0.9) if t else (pa < 0.1) for t, pa in far])) if far else None
        summ.append(row)
    os.makedirs(out_dir, exist_ok=True)
    json.dump(dict(rows=len(rows), errors=len(errors), table=summ), open(os.path.join(out_dir, "recovery.json"), "w"), indent=1)
    with open(os.path.join(out_dir, "recovery_fits.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    md = write_md(summ)
    open(os.path.join(out_dir, "recovery.md"), "w").write(md)
    print(md)


UNIT = {"lm": "shots/club", "lm_f1": "shots/club", "course3": "rounds", "course10": "rounds", "both": "rounds + 50 LM",
        "summary": "rounds"}
LABEL = {"lm": "Launch monitor (range factor f uncertain)", "lm_f1": "Launch monitor (range = course, f = 1)",
         "course3": "On-course GPS tee shots, aim logged (sd 3)", "course10": "On-course GPS tee shots, tee->pin line (aim sd 10)",
         "both": "50 LM shots/club + on-course rounds", "summary": "Summary stats only (Spirit Hollow emulator)"}


def write_md(summ):
    out = ["# Recovery study: how much of the golfer's own data pins the pattern down", "",
           "Each row: median over simulated golfers (24 from the prior + 5 scenarios x 4). Driver width W: "
           "posterior sd and 90% CI width in yds at W ~ 70-82 (from the log-scale sd), median |error| of the posterior "
           "median (%), 90% CI coverage (all golfers). Break-even: share of (golfer, break-even) pairs at least 5 yds "
           "apart where the posterior median is on the right side / where P(right side) > 90%.", ""]
    for exp in GRID:
        for prior in ("v2", "generic"):
            rs = [r for r in summ if r["exp"] == exp and r["prior"] == prior]
            if not rs:
                continue
            out += [f"## {LABEL[exp]}, {prior} prior", "",
                    f"| {UNIT[exp]} | W sd (log) | W 90% CI (yds at 76) | |err| W | cover W | bias sd | carry sd | "
                    f"mishit sd | nu |err| (log) | right side of break-even | confident (>90%) | fits |",
                    "|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for r in rs:
                a = r["all"]
                out.append(f"| {r['n']} | {a['W']['sd']:.3f} | {76 * (np.exp(1.645 * a['W']['sd']) - np.exp(-1.645 * a['W']['sd'])):.1f} | "
                           f"{100 * a['W']['err_med_abs']:.1f}% | {a['W']['cover']:.0%} | {a['bias']['sd']:.1f} | "
                           f"{a['carry']['sd']:.1f} | {a['ps']['sd']:.3f} | {a['nu']['err_med_abs']:.2f} | "
                           f"{r['breakeven_correct_5yd'] or 0:.0%} | {r['breakeven_confident_5yd'] or 0:.0%} | {r['n_fits']} |")
            out.append("")
            sc = rs[-1]["scenarios"]
            if sc:
                out.append(f"Scenarios at the largest n ({rs[-1]['n']}): " + "; ".join(
                    f"{s}: W {v['W_median']:.0f} (truth {v['W_truth']:.0f}, 90% {v['W_ci'][0]:.0f}-{v['W_ci'][1]:.0f}), "
                    f"bias {v['bias_median']:+.1f}" for s, v in sc.items()))
                out.append("")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "merge", "count"])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--exps", default="")
    ap.add_argument("--emulator", default=os.path.join(HERE, "output", "emulator_spirit_hollow.npz"))
    ap.add_argument("--out", default="recovery.jsonl")
    a = ap.parse_args()
    T = tasks(a.quick)
    if a.exps:
        T = [t for t in T if t["exp"] in a.exps.split(",")]
    if a.cmd == "count":
        print(len(T), "tasks")
        return
    if a.cmd == "merge":
        merge(sorted(sum([glob.glob(p) for p in a.paths], [])), os.path.join(HERE, "output"))
        return
    mine = T[a.shard::a.nshards]
    with open(a.out, "w") as f:
        for i, t in enumerate(mine):
            try:
                r = run_task(t, a.emulator)
            except Exception as e:                       # keep the shard going; report the failure
                r = dict(t, error=repr(e))
                print("ERROR", t, e, flush=True)
            f.write(json.dumps(r, default=B.json_default) + "\n")
            f.flush()
            print(f"[{a.shard}] {i + 1}/{len(mine)} {t['exp']} {t['prior']} n={t['n']} {t['golfer']}#{t['rep']} "
                  f"{r.get('secs', '-')}s W {r.get('W', {}).get('truth', 0):.0f}->{r.get('W', {}).get('median', 0):.0f}",
                  flush=True)


if __name__ == "__main__":
    main()
