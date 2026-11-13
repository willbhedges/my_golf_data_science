"""Shot-pattern experiments, central world, every Back tee shot.  python3 exp2_disp.py out.json [holes] [names]
Pattern statistics of the central world (python3 exp2_disp.py stats)."""
import json, sys, time
from harness import *
from scipy.stats import norm, t as tdist

base_shots = M.shots
MODE = dict(kind=None)


def shots(hd, club, P, z, wind=None):
    k = MODE["kind"]
    if k is None:
        return base_shots(hd, club, P, z, wind)
    z = np.array(z, copy=True)
    n = z.shape[1]
    u = np.random.default_rng(n * 31 + 5).random(n)            # one extra uniform per swing, common to all
    if k[0] == "mix":                                           # (p_big, mult, core scale)
        _, p, mult, core = k
        z[0] = np.where(u < p, z[0] * mult, z[0] * core)
    elif k[0] == "t":                                           # Student-t lateral, same 95 % width
        _, nu = k
        z[0] = tdist.ppf(norm.cdf(z[0]), nu) * (1.96 / tdist.ppf(0.975, nu))
    elif k[0] == "oneway":                                      # big misses on one side only (p, mult, sign)
        _, p, mult, sg = k
        z[0] = np.where(u < p, sg * np.abs(z[0]) * mult, z[0])
    return base_shots(hd, club, P, z, wind)


M.shots = shots
# v2_course.install_engine may have wrapped ev_curve around the original shots; Gateway has no flight trees, so
# M.ev_curve is model.ev_curve and reads M.shots at call time (module global) -> the patch is live.


def core_for(p, mult, width_ratio=1.0):
    """Core sigma scale so that the mixture's central 95 % width = width_ratio x the Gaussian's."""
    from scipy.optimize import brentq
    f = lambda c: (1 - p) * (2 * norm.cdf(1.96 * width_ratio / c) - 1) + p * (2 * norm.cdf(1.96 * width_ratio / mult) - 1) - 0.95  # noqa
    return brentq(f, 0.3, 1.5)


C = lambda h, **kw: D.central(h, **kw)                     # noqa: E731
W = lambda h, f: {c: v * f for c, v in C(h)["width"].items()}   # noqa: E731


def wratio(h, r2, r4):
    w = dict(C(h)["width"])
    d = w["Driver"]
    k = (d * r4) / w["4-wood"]
    w["2-wood"] = d * r2
    for c in w:
        if c not in ("Driver", "2-wood"):
            w[c] = w[c] * k if c == "4-wood" else w[c]
    return w


VARS = {
    "central": (None, lambda h: C(h)),
    "width 60": (None, lambda h: C(h, width=W(h, 60 / 70))),
    "width 65 (stated)": (None, lambda h: C(h, width=W(h, 65 / 70))),
    "width 76": (None, lambda h: C(h, width=W(h, 76 / 70))),
    "width 82 (Arccos 0-5)": (None, lambda h: C(h, width=W(h, 82 / 70))),
    "width 90": (None, lambda h: C(h, width=W(h, 90 / 70))),
    "big miss 6% x2.2 added": (("mix", 0.06, 2.2, 1.0), lambda h: C(h)),
    "big miss 6% x2.2, same 95% width": (("mix", 0.06, 2.2, core_for(0.06, 2.2)), lambda h: C(h)),
    "big miss 10% x2.5 added": (("mix", 0.10, 2.5, 1.0), lambda h: C(h)),
    "t5 same 95% width": (("t", 5), lambda h: C(h)),
    "t3 same 95% width": (("t", 3), lambda h: C(h)),
    "one-way right 6% x2.5": (("oneway", 0.06, 2.5, 1.0), lambda h: C(h)),
    "one-way left 6% x2.5": (("oneway", 0.06, 2.5, -1.0), lambda h: C(h)),
    "no mishits": (None, lambda h: C(h, mis_slight=0.0, mis_heavy=0.0)),
    "heavy mishits 6%": (None, lambda h: C(h, mis_heavy=0.06)),
    "rho 0.4 (push short)": (None, lambda h: C(h, rho=0.4)),
    "rho -0.2": (None, lambda h: C(h, rho=-0.2)),
    "kappa 0": (None, lambda h: C(h, kappa=0.0)),
    "kappa 0.25": (None, lambda h: C(h, kappa=0.25)),
    "depth x0.8": (None, lambda h: C(h, depth_mult=1.0)),
    "depth x1.3": (None, lambda h: C(h, depth_mult=1.6)),
    "fade skew +0.3": (None, lambda h: C(h, skew=0.3)),
    "draw skew -0.3": (None, lambda h: C(h, skew=-0.3)),
    "equal-angle woods (4w 63)": (None, lambda h: C(h, width=wratio(h, 280 / 300, 270 / 300))),
    "DECADE woods 70/65/60": (None, lambda h: C(h, width=wratio(h, 65 / 70, 60 / 70))),
    "roll x0.7 (soft Nov)": (None, lambda h: C(h, roll_mult=0.7)),
    "roll x1.3 (firm dormant)": (None, lambda h: C(h, roll_mult=1.3)),
}


def stats():
    h = 5
    P = C(h, temp_f=70.0)
    hd = dict(M.HOLES[h], elev={})
    z = M.draws_z(200000, 3)
    for kind in (None, ("mix", 0.06, 2.2, 1.0), ("t", 5)):
        MODE["kind"] = kind
        print("pattern", kind)
        for c in M.REAL_CLUBS:
            car, dev, roll = shots(hd, c, P, z)
            tot = car + roll
            good = z[2] >= P["mis_slight"] + P["mis_heavy"]
            lo, hi = np.percentile(dev, [2.5, 97.5])
            dlo, dhi = np.percentile(car, [2.5, 97.5])
            print("  %-10s carry mean %.1f median %.1f sd %.1f (good swings sd %.1f) 95%% depth %.0f | total %.1f | lat sd %.1f yds = %.2f deg, 95%% width %.1f, P(|lat|>30) %.3f >40 %.3f >60 %.4f, kurt %.2f, corr(lat,carry) %.2f" % (
                c, car.mean(), np.median(car), car.std(), car[good].std(), dhi - dlo, tot.mean(), dev.std(),
                np.degrees(np.arctan(dev.std() / np.median(tot))), hi - lo, np.mean(np.abs(dev) > 30),
                np.mean(np.abs(dev) > 40), np.mean(np.abs(dev) > 60), ((dev - dev.mean()) ** 4).mean() / dev.var() ** 2,
                np.corrcoef(dev, car)[0, 1]))


if __name__ == "__main__":
    if sys.argv[1] == "stats":
        stats()
        sys.exit()
    out = sys.argv[1]
    holes = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 and sys.argv[2] else HOLES
    names = sys.argv[3].split("|") if len(sys.argv) > 3 else None
    res = {}
    for h in holes:
        res[h] = {}
        for k, (mode, f) in VARS.items():
            if names and k not in names and k != "central":
                continue
            t0 = time.time()
            MODE["kind"] = mode
            r = solve(h, f(h), keep=True)
            raw = r.pop("raw")
            p = raw[r["pick"]]
            r["shares"] = {n: round(float(np.mean(p["lie"] == M.CODE[n])), 4) for n in M.LIES}
            res[h][k] = r
            print(h, "%-34s" % k, short(r), "| " + (compare(res[h]["central"], r) if k != "central" else ""),
                  "%.0fs" % (time.time() - t0), flush=True)
        json.dump({str(a): b for a, b in res.items()}, open(out, "w"), indent=0, default=float)
