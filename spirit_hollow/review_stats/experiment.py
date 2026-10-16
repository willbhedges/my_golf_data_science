"""Review experiments for spirit_hollow/decision.py.  python3 spirit_hollow/review_stats/experiment.py [holes...]

  A. R independent randomised-QMC batches (fresh Sobol scramble + fresh swings), S draws each.
     -> winner's curse: pick chosen on one batch, scored on the other R-1 batches pooled.
     -> RQMC replicate SE of the margin vs decision.py's iid SE.
     -> error budget (prior vs swing variance) and the S needed for SE < 0.005.
     -> P(best) and EVPI: naive vs cross-fitted vs deconvolved.
  B. "Truth" for the first T draws of batch 0 at N_TRUE swings: per-draw winners and EVPI with
     5x less swing noise, to check the corrections.
  C. Width break-even: driver-only (decision.py) vs common scaling of every club.
  D. Calibration: fairway / penalty share for the driver at the prior-mean world vs research.md.
Writes review_stats/experiment_results.json.
"""
import copy
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(SH, "..", "mozingo"), SH, HERE]

import decision as D            # noqa: E402
import decision_stats as DS     # noqa: E402
import tee_strategy as t        # noqa: E402

HOLES = [int(a) if a.isdigit() else a for a in sys.argv[1:]] or [1, 16, 5]
R, S, N = 4, 32, 3000
T, N_TRUE = 24, 15000


def zgen(seed, n):
    r = np.random.default_rng(seed)
    return np.vstack([r.standard_normal((2, n)), r.random((2, n))])


def run_batch(b):
    E = {h: {} for h in HOLES}
    draws = D.prior_draws(S, seed=1000 + b)
    for si, th in enumerate(draws):
        D.apply(th)
        z = zgen(50_000 + 100 * b + si, N)
        for h in HOLES:
            DS.accumulate(E[h], DS.ev_grid_halves(h, z))
    D.reset()
    return E, draws


def main():
    t0 = time.time()
    out = {"config": dict(R=R, S=S, N=N, T=T, N_TRUE=N_TRUE, holes=[str(h) for h in HOLES])}
    batches = []
    for b in range(R):
        batches.append(run_batch(b))
        print(f"batch {b} done {time.time() - t0:.0f}s", flush=True)

    for h in HOLES:
        st = [DS.stack(E[h]) for E, _ in batches]
        clubs, aims = st[0][0], st[0][1]
        Mb = [{c: (MA[c] + MB[c]) / 2 for c in clubs} for _, _, MA, MB in st]
        # pooled (all R*S draws) = best available estimate of the posterior
        Mall = {c: np.vstack([m[c] for m in Mb]) for c in clubs}
        p_all, r_all, col_all, ev_all = DS.posterior_pick(Mall, clubs)
        per = []
        for i in range(R):
            p, r, col, ev = DS.posterior_pick(Mb[i], clubs)
            Moth = {c: np.vstack([Mb[j][c] for j in range(R) if j != i]) for c in clubs}
            e_p_oos = float(Moth[p].mean(0)[col[p]])
            e_r_oos = float(Moth[r].mean(0)[col[r]])
            best_oos = min(float(Moth[c].mean(0).min()) for c in clubs)
            Eh = batches[i][0][h]
            s = DS.summarize(Eh)
            per.append(dict(pick=p, aim=float(aims[p][col[p]]), runner=r, ev_in=ev[p], ev_oos=e_p_oos,
                            margin_in=ev[r] - ev[p], margin_oos=e_r_oos - e_p_oos,
                            regret_oos=e_p_oos - best_oos, summary=s))
        # replicate SE of the pooled-pick margin (fixed pooled aims => no selection inside)
        mar_b = [float((Mb[i][r_all][:, col_all[r_all]] - Mb[i][p_all][:, col_all[p_all]]).mean()) for i in range(R)]
        iid_se = [x["summary"]["margin_se"] for x in per]
        out[str(h)] = dict(
            pooled=dict(pick=p_all, runner=r_all, aim=float(aims[p_all][col_all[p_all]]),
                        margin=ev_all[r_all] - ev_all[p_all],
                        clubs={c: dict(aim=float(aims[c][col_all[c]]), ev=ev_all[c]) for c in clubs}),
            batches=per,
            rqmc_replicate_sd_of_margin=float(np.std(mar_b, ddof=1)),
            mean_iid_se=float(np.mean(iid_se)),
            optimism_ev_mean=float(np.mean([x["ev_oos"] - x["ev_in"] for x in per])),
            margin_shrink_mean=float(np.mean([x["margin_in"] - x["margin_oos"] for x in per])),
            pick_agreement=[x["pick"] for x in per])
        print(h, json.dumps({k: v for k, v in out[str(h)].items() if k != "batches"}, default=float), flush=True)

    # ---- B. truth at N_TRUE for the first T draws of batch 0
    E0, draws0 = batches[0]
    truth = {h: {} for h in HOLES}
    for si, th in enumerate(draws0[:T]):
        D.apply(th)
        z = zgen(90_000 + si, N_TRUE)
        for h in HOLES:
            DS.accumulate(truth[h], DS.ev_grid_halves(h, z))
    D.reset()
    print(f"truth done {time.time() - t0:.0f}s", flush=True)
    for h in HOLES:
        clubs, aims, MA, MB = DS.stack(E0[h])
        sub = {c: (MA[c][:T], MB[c][:T]) for c in clubs}
        MA_, MB_ = {c: sub[c][0] for c in clubs}, {c: sub[c][1] for c in clubs}
        M_ = {c: (MA_[c] + MB_[c]) / 2 for c in clubs}
        p, r, col, _ = DS.posterior_pick(M_, clubs)
        _, _, TA, TB = DS.stack(truth[h])
        TM = {c: (TA[c] + TB[c]) / 2 for c in clubs}
        en, ecf = DS.evpi_bracket(MA_, MB_, clubs, p, col[p])
        tn, tcf = DS.evpi_bracket(TA, TB, clubs, p, col[p])
        dec, pair = DS.p_best_deconvolved(MA_, MB_, clubs, col)
        out[str(h)]["truth_check"] = dict(
            pick_on_T=p,
            p_best_naive_N3000=DS.p_best_naive(M_, clubs),
            p_best_crossfit_N3000=DS.p_best_crossfit(MA_, MB_, clubs),
            p_best_naive_Ntrue=DS.p_best_naive(TM, clubs),
            p_best_fixed_aims_naive_N3000=DS.p_best_fixed_aims_naive(MA_, MB_, clubs, col),
            p_best_fixed_aims_deconv_N3000=dec,
            p_best_fixed_aims_naive_Ntrue=DS.p_best_fixed_aims_naive(TA, TB, clubs, col),
            p_best_fixed_aims_deconv_Ntrue=DS.p_best_deconvolved(TA, TB, clubs, col)[0],
            evpi_naive_N3000=en, evpi_crossfit_N3000=ecf, evpi_naive_Ntrue=tn, evpi_crossfit_Ntrue=tcf,
            winner_flips_vs_truth=float(np.mean(
                np.argmin(np.stack([M_[c].min(1) for c in clubs]), 0)
                != np.argmin(np.stack([TM[c].min(1) for c in clubs]), 0))))
        print(h, "truth", json.dumps(out[str(h)]["truth_check"]), flush=True)

    # ---- C. width break-evens
    for h in HOLES:
        res = {}
        for mode in ("driver_only", "common"):
            picks, flips, _ = DS.width_sweep(h, mode)
            res[mode] = dict(picks=picks, flips=[(float(w), a, b) for w, a, b in flips])
        out[str(h)]["width_sweep"] = res
        print(h, "sweep", res, flush=True)

    # ---- D. calibration at the prior-mean world, all holes, driver at aim 0 and posterior aim
    mean_th = dict(width=D.CENTER_WIDTH / 65.0, c_drv=0.0, c_2w=0.0, c_4w=0.0, roll=1.0, trees=0.8,
                   lost=0.5, mishit=0.15, map_seed=0)
    cal = {}
    z = zgen(7, 6000)
    for W in (70, 84):
        D.apply(dict(mean_th, width=W / 65.0))
        t.HOLES = copy.deepcopy(D.BASE["holes"])
        rows = {}
        for h in D.BASE["holes"]:
            _, lie, _, _ = t.simulate(h, "Driver", 0.0, z=z)
            rows[str(h)] = dict(fw=float(np.mean(lie == "fairway")),
                                pen=float(np.mean(np.isin(lie, ("water", "ob"))) + 0.5 * np.mean(lie == "native")),
                                dead=float(np.mean(np.isin(lie, ("water", "ob", "native", "recovery")))))
        cal[W] = dict(mean_fw=float(np.mean([r["fw"] for r in rows.values()])),
                      mean_pen=float(np.mean([r["pen"] for r in rows.values()])),
                      mean_dead=float(np.mean([r["dead"] for r in rows.values()])), holes=rows)
        print("calibration", W, {k: v for k, v in cal[W].items() if k != "holes"}, flush=True)
    D.reset()
    out["calibration"] = cal
    out["elapsed_s"] = time.time() - t0
    with open(os.path.join(HERE, "experiment_results.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
