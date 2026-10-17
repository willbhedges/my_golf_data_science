"""Course emulator: what a driver pattern does on the golfer's home holes, for summary-stat likelihoods.

The v2 simulator (spirit_hollow/v2/model.py: lie raster, roll-out, penalty rules) is run for a bank of
pattern parameters theta = (width, bias, nu, carry, roll, mishit rates, depth; plus nuisance rho, kappa,
lost-ball rates) on each driving hole of the home course. Per hole and theta it records

  fairway      share of tee shots finishing on the fairway (first cut counts as a miss, as apps do)
  left_share   share of misses finishing left of the fairway centre line
  penalty      expected tee-shot penalties per shot: water + OB + lost (lost-ball chance by depth into
               long grass, v2's ramp)
  mean_total   mean distance tee -> ball of good strikes (apps' "average drive" drops mishits)
  beyond40     share of shots > 40 yds offline (calibration only)

The golfer is assumed to aim at the fairway centre at his expected landing distance (the usual way
apps' fairway stats are produced; not our plan's aim). A polynomial response surface is then fitted on
the bank, per set of holes, and bayes.Model uses it as a smooth, cheap likelihood.

  python3 course_data/personal/emulator.py bank [--k 4096 --n 1500 --shard 0 --nshards 1 --out F.npz]
  python3 course_data/personal/emulator.py merge OUT.npz PART.npz ...
  python3 course_data/personal/emulator.py check BANK.npz    # held-out accuracy of the surface
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy import special, stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
V2 = os.path.join(ROOT, "spirit_hollow", "v2")

from bayes import HEAVY, SLIGHT, t_q                       # noqa: E402

# Black-tee driving holes (2F / 9F are the Black boxes; 3, 7, 12, 15 are par 3s)
COURSES = {"spirit_hollow": dict(holes=["1", "2F", "4", "5", "6", "8", "9F", "10", "11", "13", "14", "16", "17", "18"],
                                 geometry="scale,elev,green", club="Driver", carry0=275.0, roll0=25.0)}
FEATS = ["logW", "beta", "inv_nu", "carry", "roll", "ps", "ph", "log_dm"]
# proposal box for the bank (covers the generic prior's 99%)
BOX = dict(logW=(np.log(45), np.log(125)), beta=(-15, 15), inv_nu=(0.0, 0.4), carry=(200, 310), roll=(0, 45),
           ps=(0.0, 0.35), ph=(0.0, 0.10), log_dm=(np.log(0.7), np.log(2.2)))
OUTS = ["fairway", "left_share", "penalty", "mean_total", "beyond40"]


def _v2():
    if V2 not in sys.path:
        sys.path.insert(0, V2)
    import geom                                             # noqa: F401
    import model as M
    return geom, M


def draw_bank(k, seed=7):
    """Sobol draws in BOX + nuisance (rho, kappa, lost_edge, lost_deep) from v2's prior."""
    u = stats.qmc.Sobol(len(FEATS) + 4, scramble=True, seed=seed).random(k)
    th = {f: BOX[f][0] + (BOX[f][1] - BOX[f][0]) * u[:, i] for i, f in enumerate(FEATS)}
    j = len(FEATS)
    th.update(rho=-0.1 + 0.4 * u[:, j], kappa=0.16 * u[:, j + 1], lost_edge=0.1 + 0.3 * u[:, j + 2],
              lost_deep=0.5 + 0.3 * u[:, j + 3])
    return th


class HoleSim:
    """One hole: lie raster + fairway centre line + common random numbers."""

    def __init__(self, M, h, n, seed):
        self.M, self.h = M, h
        self.hd = M.HOLES[int(h) if str(h).isdigit() else h]
        self.R = M.Raster(self.hd)
        fw = self.R.lie == M.CODE["fairway"]
        cnt = fw.sum(1)
        cen = np.where(cnt > 0, (fw * self.R.LL).sum(1) / np.maximum(cnt, 1), np.nan)
        ok = ~np.isnan(cen)
        self.centre = np.interp(self.R.a, self.R.a[ok], cen[ok]) if ok.any() else np.zeros_like(self.R.a)
        r = np.random.default_rng(seed)
        self.z_t = r.standard_normal(n)          # replaced by a t draw per nu via the chi-square below
        self.chi_u = r.random(n)
        self.z_c = r.standard_normal(n)
        self.u_m = r.random(n)
        self.u_f = r.random(n)
        self.u_r = r.random(n)
        e = self.hd.get("elev", {}).get("Driver")
        self.dc, self.rf = (float(e[0]), float(e[1])) if e else (0.0, 1.0)

    def centre_at(self, a):
        return np.interp(a, self.R.a, self.centre)

    def reseed(self, n, seed):
        r = np.random.default_rng(seed)
        self.z_t, self.chi_u, self.z_c = r.standard_normal(n), r.random(n), r.standard_normal(n)
        self.u_m, self.u_f, self.u_r = r.random(n), r.random(n), r.random(n)
        self.u_lost = r.random(n)

    def outcomes(self, th):
        """Per swing: final (a, l, lie), on fairway, miss left, penalty probability, good strike, dev."""
        M = self.M
        nu = 1.0 / max(th["inv_nu"], 1e-6)
        # t draw with common random numbers: z / sqrt(chi2_nu / nu), chi2 by inverse CDF of a shared uniform
        if th["inv_nu"] < 1e-4:
            t = self.z_t
        else:
            t = self.z_t / np.sqrt(stats.chi2.ppf(np.clip(self.chi_u, 1e-9, 1 - 1e-9), nu) / nu)
        W = np.exp(th["logW"])
        s = W / (2 * float(t_q(nu)))
        sd_c = 28.0 * np.exp(th["log_dm"]) / 4.0
        carry = th["carry"] + self.dc
        roll = th["roll"] * self.rf
        kind = np.where(self.u_m < th["ps"], 1, np.where(self.u_m < th["ps"] + th["ph"], 2, 0))
        mult = np.choose(kind, [1.0, SLIGHT["lat"], HEAVY["lat"]])
        dev = th["beta"] + s * mult * t
        rho = th["rho"]
        zl = t / max(np.std(t), 1e-9)
        car = carry + sd_c * (np.sqrt(1 - rho ** 2) * self.z_c - rho * zl)
        car = car - th["kappa"] * s * (np.abs(t) - np.sqrt(2 / np.pi))
        car = np.where(kind == 1, carry * (SLIGHT["lo"] + (SLIGHT["hi"] - SLIGHT["lo"]) * self.u_f), car)
        car = np.where(kind == 2, carry * (HEAVY["lo"] + (HEAVY["hi"] - HEAVY["lo"]) * self.u_f), car)
        rl = np.maximum(roll * (1 + 0.25 * (2 * self.u_r - 1)), 0)
        aim = float(self.centre_at(carry + roll))
        a, l, lie = M.finish(self.R, car, dev + aim, rl, 0.3)
        C = M.CODE
        on_fw = lie == C["fairway"]
        left = ~on_fw & (l < self.centre_at(a))
        nat = lie == C["native"]
        dep = self.R.native_depth[self.R.idx(a, l)]
        pl = np.where(nat, th["lost_edge"] + (th["lost_deep"] - th["lost_edge"]) * np.clip(dep / 10.0, 0, 1), 0.0)
        hard = (lie == C["water"]) | (lie == C["ob"])
        return dict(a=a, l=l, on_fw=on_fw, left=left, p_pen=np.where(hard, 1.0, pl), hard=hard,
                    good=(kind == 0) & ~hard, dev=dev - th["beta"])

    def run(self, th):
        """Rates for one theta (dict of scalars)."""
        o = self.outcomes(th)
        miss = ~o["on_fw"]
        d = np.hypot(o["a"], o["l"])
        return dict(fairway=o["on_fw"].mean(), left_share=o["left"].sum() / max(miss.sum(), 1), left=o["left"].mean(),
                    miss=miss.mean(), penalty=o["p_pen"].mean(),
                    mean_total=float(d[o["good"]].mean()) if o["good"].any() else float(d.mean()),
                    beyond40=float(np.mean(np.abs(o["dev"]) > 40)))


def make_sims(course="spirit_hollow", n=1500, seed=11):
    geom, M = _v2()
    spec = COURSES[course]
    geom.set_geometry(spec["geometry"])
    return [HoleSim(M, h, n, seed + i) for i, h in enumerate(spec["holes"])]


def bank(course="spirit_hollow", k=4096, n=1500, shard=0, nshards=1, seed=7):
    th = draw_bank(k, seed)
    sims = make_sims(course, n)
    idx = np.arange(k)[shard::nshards]
    res = {o: np.zeros((len(idx), len(sims))) for o in OUTS + ["left", "miss"]}
    for j, i in enumerate(idx):
        one = {kk: float(v[i]) for kk, v in th.items()}
        for hi, sim in enumerate(sims):
            r = sim.run(one)
            for o in res:
                res[o][j, hi] = r[o]
        if j % 100 == 0:
            print(f"shard {shard}: {j}/{len(idx)}", flush=True)
    out = {f"th_{kk}": v[idx] for kk, v in th.items()}
    out.update({f"y_{o}": v for o, v in res.items()})
    out["idx"] = idx
    out["holes"] = np.array(COURSES[course]["holes"])
    out["n_swings"] = np.array(n)
    return out


# --------------------------------------------------------------------------------------- surface
def design(F):
    """Polynomial features: full quadratic in the 8 inputs (scaled to [-1, 1]) + cubic/quartic in width
    and bias, and width x bias^2."""
    Z = []
    for f in FEATS:
        lo, hi = BOX[f]
        Z.append(2 * (np.asarray(F[f], float) - lo) / (hi - lo) - 1)
    Z = np.array(np.broadcast_arrays(*Z))
    cols = [np.ones(Z.shape[1:])] + list(Z)
    d = len(FEATS)
    for i in range(d):
        for j in range(i, d):
            cols.append(Z[i] * Z[j])
    w, b, nu, c, r = Z[0], Z[1], Z[2], Z[3], Z[4]
    cols += [w ** 3, b ** 4, w * b * b, w ** 2 * b * b, b ** 3, w * w * b, w ** 4, c ** 3, w * w * c, w * c * c,
             b * b * c, b * b * nu, w * w * nu, b * b * r, c * c * r]
    return np.stack(cols, -1)


class Emulator:
    def __init__(self, bank_npz, course="spirit_hollow"):
        D = np.load(bank_npz) if isinstance(bank_npz, str) else bank_npz
        self.th = {f: D[f"th_{f}"] for f in FEATS}
        self.y = {o: D[f"y_{o}"] for o in OUTS + ["left", "miss"]}
        self.holes = [str(h) for h in D["holes"]]
        spec = COURSES[course]
        self.carry0, self.roll0 = spec["carry0"], spec["roll0"]
        self.X = design(self.th)
        self._cache = {}

    @staticmethod
    def _tf(o, v):
        if o in ("fairway", "left_share"):
            return special.logit(np.clip(v, 1e-3, 1 - 1e-3))
        if o == "penalty":
            return np.log(v + 2e-3)
        return v

    @staticmethod
    def _itf(o, v):
        if o in ("fairway", "left_share"):
            return special.expit(v)
        if o == "penalty":
            return np.maximum(np.exp(v) - 2e-3, 0.0)
        return v

    def _agg(self, holes):
        hi = [self.holes.index(str(h)) for h in holes] if holes else list(range(len(self.holes)))
        y = {o: self.y[o][:, hi].mean(1) for o in ("fairway", "penalty", "mean_total", "beyond40", "left", "miss")}
        y["left_share"] = y["left"] / np.maximum(y["miss"], 1e-6)
        return y

    def coefs(self, holes=None, rows=None):
        key = (tuple(holes) if holes else None, None if rows is None else (rows[0], len(rows)))
        if key not in self._cache:
            y = self._agg(holes)
            X = self.X if rows is None else self.X[rows]
            self._cache[key] = {o: np.linalg.lstsq(X, self._tf(o, y[o] if rows is None else y[o][rows]), rcond=None)[0]
                                for o in ("fairway", "left_share", "penalty", "mean_total", "beyond40")}
        return self._cache[key]

    def predict(self, feat, holes=None):
        F = {f: np.clip(np.asarray(feat[f], float), *BOX[f]) for f in FEATS}
        X = design(F)
        cf = self.coefs(holes)
        return {o: self._itf(o, X @ b) for o, b in cf.items()}

    def check(self, holes=None, frac=0.2, seed=0):
        """Held-out error of the surface vs the bank's own Monte Carlo noise."""
        n = len(self.X)
        rng = np.random.default_rng(seed)
        perm = rng.permutation(n)
        te, tr = perm[:int(frac * n)], np.sort(perm[int(frac * n):])
        y = self._agg(holes)
        out = {}
        for o in ("fairway", "left_share", "penalty", "mean_total"):
            b = np.linalg.lstsq(self.X[tr], self._tf(o, y[o][tr]), rcond=None)[0]
            pred = self._itf(o, self.X[te] @ b)
            out[o] = dict(rmse=float(np.sqrt(np.mean((pred - y[o][te]) ** 2))), sd=float(np.std(y[o][te])))
        return out


def merge(out, parts):
    Ds = [dict(np.load(p)) for p in parts]
    idx = np.concatenate([d["idx"] for d in Ds])
    o = np.argsort(idx)
    res = {}
    for k in Ds[0]:
        if k in ("holes", "n_swings"):
            res[k] = Ds[0][k]
        else:
            res[k] = np.concatenate([d[k] for d in Ds])[o]
    np.savez_compressed(out, **{k: (v.astype(np.float32) if v.dtype == np.float64 and k.startswith("y_") else v)
                                for k, v in res.items()})
    print("merged", len(idx), "->", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["bank", "merge", "check"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--k", type=int, default=4096)
    ap.add_argument("--n", type=int, default=1500)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--out", default=os.path.join(HERE, "output", "emulator_spirit_hollow.npz"))
    a = ap.parse_args()
    if a.cmd == "bank":
        r = bank(k=a.k, n=a.n, shard=a.shard, nshards=a.nshards)
        np.savez_compressed(a.out, **r)
        print("wrote", a.out)
    elif a.cmd == "merge":
        merge(a.args[0], sorted(sum([glob.glob(p) for p in a.args[1:]], [])))
    else:
        em = Emulator(a.args[0])
        print(json.dumps(em.check(), indent=1))


if __name__ == "__main__":
    main()
