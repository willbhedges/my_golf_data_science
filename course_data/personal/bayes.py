"""Bayesian update of a golfer's shot pattern (the personalisation model).

The golfer's pattern is the v2 shot model (spirit_hollow/v2/model.py) with its unknowns made explicit,
plus a Student-t lateral tail:

  per club k (stated carry C_k, stated total T_k):
    carry      ~ N(C_k + c_common + c_k, sd_k)                 good strike, sd_k = depth95_k * depth_mult / 4
    lateral    ~ b_k + s_k * t_nu                              s_k = width95_k / (2 * t_nu.ppf(0.97725))
               (width95 = the central 95.45 % interval of a good strike = 4 sigma when nu = inf, as in v2)
    width95_k  = W * r_k        W = the driver's on-course width, r_k = the club's width ratio
    bias b_k   = beta * C_k / C_driver + delta_k                (a common aim/shape bias, in angle, plus a club part)
    mishits    slight (rate p_s): carry = mean * U(0.92, 0.95), lateral scale x 1.15     (v2's numbers)
               heavy  (rate p_h): carry = mean * U(0.65, 0.85), lateral scale x 1.5
    roll       on the golfer's home fairways = (T_k - C_k) * roll_mult, +/-25 % per swing (v2)
  range -> course: a launch-monitor width is the on-course width / f  (f > 1 = the range is tighter)

Three kinds of data enter one posterior:
  (a) launch-monitor shots: carry + side at landing (yds, + = right of the target line), per session
  (b) on-course tee shots (GPS start/end): total distance + lateral offset of the resting ball from the
      intended line, with aim and GPS noise; penalty / lost balls enter as censored laterals
  (c) summary stats (fairways hit, misses left/right, tee penalties, average drive) through an emulator
      of the course simulator on the golfer's home holes (emulator.py)

Posterior: MAP + Laplace, then importance sampling from a multivariate-t around the MAP (vectorised,
draws x shots), with Pareto-smoothed-style weight truncation; if the effective sample size is low, an
adaptive random-walk Metropolis chain started from the IS draws takes over.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field

import numpy as np
from scipy import optimize, special, stats

Z95 = stats.norm.ppf(0.97725)                 # = 2.0: width95 = 4 sigma for a normal (v2 convention)
GH_X, GH_W = np.polynomial.hermite_e.hermegauss(9)    # E[f(e)], e ~ N(0,1) = sum w f(x) / sqrt(2 pi)
GH_W = GH_W / np.sqrt(2 * np.pi)
GH_X24, GH_W24 = np.polynomial.hermite_e.hermegauss(24)  # finer rule where the 'not a penalty' indicator cuts in
GH_W24 = GH_W24 / np.sqrt(2 * np.pi)

SLIGHT = dict(lo=0.92, hi=0.95, lat=1.15)     # v2 model.central
HEAVY = dict(lo=0.65, hi=0.85, lat=1.5)

# --------------------------------------------------------------------------------------- the bag
# v2's golfer (spirit_hollow/v2/model.py CLUBS): carry, total, width95, depth95 (yds)
BOOK_BAG = {
    "Driver": dict(carry=275, total=300, width=70.0, depth=28),
    "2-wood": dict(carry=265, total=280, width=65.0, depth=26),
    "4-wood": dict(carry=255, total=270, width=54.0, depth=24),
    "Long iron": dict(carry=210, total=220, width=40 * 54 / 50, depth=20),
    "Mid iron": dict(carry=185, total=192, width=34 * 54 / 50, depth=18),
}
# width ratio to the driver as a function of carry / driver carry (the golfer's 70:65:54, irons x 4-wood)
_RATIO_PTS = [(185 / 275, 34 * 54 / 50 / 70), (210 / 275, 40 * 54 / 50 / 70), (235 / 275, 45 * 54 / 50 / 70),
              (255 / 275, 54 / 70), (265 / 275, 65 / 70), (1.0, 1.0)]


def default_ratio(carry, driver_carry):
    """Prior centre of a club's width ratio to the driver, from its carry (the golfer's table;
    below a mid iron the width shrinks in proportion to carry, i.e. a constant angle)."""
    x = carry / driver_carry
    xs, ys = zip(*_RATIO_PTS)
    if x < xs[0]:
        return ys[0] * x / xs[0]
    return float(np.interp(x, xs, ys))


def make_bag(clubs: dict, driver: str | None = None) -> dict:
    """Complete a bag {name: {carry, total?, width?, depth?}} with prior centres for what is missing.
    The first club with the longest carry is the reference (driver) unless `driver` is given."""
    ref = driver or max(clubs, key=lambda k: clubs[k]["carry"])
    cd = float(clubs[ref]["carry"])
    out = {}
    for k, c in clubs.items():
        carry = float(c["carry"])
        total = float(c.get("total", carry * (1.09 if carry >= 0.9 * cd else 1.04)))
        ratio = float(c["width"]) / float(clubs[ref].get("width", 70.0)) if "width" in c and k != ref else \
            (1.0 if k == ref else default_ratio(carry, cd))
        out[k] = dict(carry=carry, total=total, ratio=ratio, depth=float(c.get("depth", 0.1 * carry)),
                      ref=(k == ref))
    return out


# --------------------------------------------------------------------------------------- priors
@dataclass
class Prior:
    """Prior on the pattern. `v2()` = the current golfer prior (final_decision.py / decide.prior_draws:
    driver width LN median 70, 90% 62-80; ratios 65/70 sd .04, 54/70 sd .06; carry N(0,5) common +
    N(0,3) per club; depth x LN(1.25, .2); mishits 8-16% slight, 1-4% heavy; roll x 0.8-1.2; aim bias
    N(0, 2)). `generic()` = a new app user we know nothing about (published 0-5 hcp centre 82)."""
    name: str = "v2"
    w_median: float = 70.0
    w_hi90: float = 80.0
    ratio_sd: dict = field(default_factory=lambda: {"2-wood": 0.04, "4-wood": 0.06})
    ratio_sd_default: float = 0.08
    c_common_sd: float = 5.0
    c_club_sd: float = 3.0
    depth_median: float = 1.25
    depth_sd: float = 0.2
    bias_sd: float = 2.0
    bias_club_sd: float = 1.5
    nu_median: float = 30.0          # Student-t tail: v2 is normal (nu = inf) + mishit scale mixture
    nu_logsd: float = 0.75           # 90% 8.7-103
    slight_ab: tuple = (23.8, 174.8)  # Beta, mean .12 sd .023 (v2: U(.08,.16))
    heavy_ab: tuple = (8.0, 313.0)    # Beta, mean .025 sd .0087 (v2: U(.01,.04))
    roll_mean: float = 1.0
    roll_sd: float = 0.115            # v2: U(0.8, 1.2)
    f_median: float = 1.05            # on-course width / range width (assumption; no published value found)
    f_logsd: float = 0.08
    session_sd: float = 3.0           # carry offset of one launch-monitor session (ball, air, mat)
    range_ball_shift: float = -0.05   # range balls: -5 % carry, sd 3 %
    range_ball_sd: float = 0.03

    @property
    def w_logsd(self):
        return math.log(self.w_hi90 / self.w_median) / 1.645

    @classmethod
    def v2(cls):
        return cls()

    @classmethod
    def generic(cls):
        return cls(name="generic", w_median=82.0, w_hi90=100.0, ratio_sd={}, ratio_sd_default=0.10,
                   c_common_sd=10.0, c_club_sd=5.0, depth_sd=0.3, bias_sd=6.0, bias_club_sd=3.0,
                   slight_ab=(3.0, 22.0), heavy_ab=(1.5, 48.5), roll_sd=0.2)

    def to_dict(self):
        d = dict(self.__dict__)
        d["slight_ab"], d["heavy_ab"] = list(self.slight_ab), list(self.heavy_ab)
        return d


# --------------------------------------------------------------------------------------- data
@dataclass
class Data:
    """Normalised observations (parsers.py builds these)."""
    lm: list = field(default_factory=list)        # {club, carry, side|None, session, ball}
    course: list = field(default_factory=list)    # {club, total|None, lateral|None, aim_sd, gps_sd, cond_sd,
    #                                                censored: None|'left'|'right'|'both', beyond}
    summary: list = field(default_factory=list)   # {n_tee, fairways, miss_left, miss_right, tee_penalties,
    #                                                avg_drive, n_drives, club, course, holes}

    def extend(self, other: "Data"):
        self.lm += other.lm
        self.course += other.course
        self.summary += other.summary
        return self

    def counts(self):
        out = {}
        for kind in ("lm", "course"):
            for r in getattr(self, kind):
                out.setdefault(r["club"], {"launch_monitor": 0, "on_course": 0})
                out[r["club"]]["launch_monitor" if kind == "lm" else "on_course"] += 1
        return out


# --------------------------------------------------------------------------------------- helpers
def t_logpdf(x, nu, scale):
    """Student-t log density, location 0 (broadcasting)."""
    z = x / scale
    return (special.gammaln((nu + 1) / 2) - special.gammaln(nu / 2) - 0.5 * np.log(nu * np.pi) - np.log(scale)
            - (nu + 1) / 2 * np.log1p(z * z / nu))


def t_sf(x, nu):
    return special.stdtr(nu, -x)


def t_q(nu):
    """t_nu quantile at 0.97725 (so width95 = 2 q s); vectorised, = 2.0 as nu -> inf."""
    return special.stdtrit(np.asarray(nu, float), 0.97725)


def unif_norm_logpdf(y, a, b, s):
    """log density of U(a, b) + N(0, s^2)."""
    w = np.maximum(b - a, 1e-6)
    p = special.ndtr((y - a) / s) - special.ndtr((y - b) / s)
    return np.log(np.maximum(p, 1e-300)) - np.log(w)


def norm_logpdf(y, m, s):
    return -0.5 * ((y - m) / s) ** 2 - np.log(s) - 0.5 * np.log(2 * np.pi)


def logsumexp3(a, b, c):
    m = np.maximum(np.maximum(a, b), c)
    return m + np.log(np.exp(a - m) + np.exp(b - m) + np.exp(c - m))


# --------------------------------------------------------------------------------------- the model
class Model:
    """Parameter vector layout, prior, likelihood and posterior for one golfer."""

    def __init__(self, bag: dict, prior: Prior | None = None, data: Data | None = None, emulators: dict | None = None,
                 fix: dict | None = None):
        self.bag = make_bag(bag) if not all("ratio" in v for v in bag.values()) else bag
        self.prior = prior or Prior.v2()
        self.data = data or Data()
        self.emulators = emulators or {}
        self.fix = fix or {}                 # e.g. {"log_f": 0.0}: treat the range as the course
        self.clubs = list(self.bag)
        self.ref = next(k for k, v in self.bag.items() if v.get("ref"))
        self.cref = self.bag[self.ref]["carry"]
        self.sessions = sorted({r.get("session", "s0") for r in self.data.lm})
        names = ["logW"] + [f"lr:{k}" for k in self.clubs if k != self.ref] + ["c_common"] + \
                [f"c:{k}" for k in self.clubs] + ["log_dm", "beta"] + [f"d:{k}" for k in self.clubs if k != self.ref] + \
                ["log_nu", "lg_ps", "lg_ph", "roll", "log_f"] + [f"so:{s}" for s in self.sessions]
        self.names = [n for n in names if n not in self.fix]
        self.ix = {n: i for i, n in enumerate(self.names)}
        self.d = len(self.names)
        self._prep()

    # ---------------------------------------------------------------- prior
    def _prior_spec(self):
        """name -> (kind, a, b): normal (mean, sd) or beta-logit (a, b)."""
        P = self.prior
        sp = {"logW": ("n", math.log(P.w_median), P.w_logsd), "c_common": ("n", 0.0, P.c_common_sd),
              "log_dm": ("n", math.log(P.depth_median), P.depth_sd), "beta": ("n", 0.0, P.bias_sd),
              "log_nu": ("n", math.log(P.nu_median), P.nu_logsd), "lg_ps": ("b",) + tuple(P.slight_ab),
              "lg_ph": ("b",) + tuple(P.heavy_ab), "roll": ("n", P.roll_mean, P.roll_sd),
              "log_f": ("n", math.log(P.f_median), P.f_logsd)}
        for k, v in self.bag.items():
            sp[f"c:{k}"] = ("n", 0.0, P.c_club_sd)
            if k != self.ref:
                sp[f"lr:{k}"] = ("n", math.log(v["ratio"]), P.ratio_sd.get(k, P.ratio_sd_default))
                sp[f"d:{k}"] = ("n", 0.0, P.bias_club_sd)
        for s in self.sessions:
            ball = next((r.get("ball", "premium") for r in self.data.lm if r.get("session", "s0") == s), "premium")
            if ball == "range":
                sp[f"so:{s}"] = ("rel", P.range_ball_shift, P.range_ball_sd)     # x driver carry
            else:
                sp[f"so:{s}"] = ("n", 0.0, P.session_sd)
        return sp

    def prior_mean(self):
        sp = self._prior_spec()
        x = np.zeros(self.d)
        for n, i in self.ix.items():
            s = sp[n]
            if s[0] == "n":
                x[i] = s[1]
            elif s[0] == "rel":
                x[i] = s[1] * self.cref
            else:
                m = s[1] / (s[1] + s[2])
                x[i] = math.log(m / (1 - m))
        return x

    def logprior(self, X):
        X = np.atleast_2d(X)
        sp = self._prior_spec()
        lp = np.zeros(len(X))
        for n, i in self.ix.items():
            s, x = sp[n], X[:, i]
            if s[0] == "n":
                lp += norm_logpdf(x, s[1], s[2])
            elif s[0] == "rel":
                lp += norm_logpdf(x, s[1] * self.cref, s[2] * self.cref)
            else:                                   # Beta(a, b) on p = sigmoid(x), with Jacobian
                a, b = s[1], s[2]
                lp += -a * np.logaddexp(0, -x) - b * np.logaddexp(0, x) - special.betaln(a, b)
        lp += np.where(self._get(X, "roll") > 0.2, 0.0, -1e6)
        return lp

    def sample_prior(self, n, rng):
        sp = self._prior_spec()
        X = np.zeros((n, self.d))
        for nme, i in self.ix.items():
            s = sp[nme]
            if s[0] == "n":
                X[:, i] = rng.normal(s[1], s[2], n)
            elif s[0] == "rel":
                X[:, i] = rng.normal(s[1], s[2], n) * self.cref
            else:
                p = rng.beta(s[1], s[2], n)
                X[:, i] = np.log(p / (1 - p))
        return X

    # ---------------------------------------------------------------- parameters
    def _get(self, X, name):
        if name in self.fix:
            return np.full(len(X), float(self.fix[name]))
        return X[:, self.ix[name]]

    def params(self, X):
        """Natural parameters per draw (arrays over draws)."""
        X = np.atleast_2d(X)
        g = lambda n: self._get(X, n)                    # noqa: E731
        W = np.exp(g("logW"))
        out = dict(W=W, c_common=g("c_common"), dm=np.exp(g("log_dm")), beta=g("beta"), nu=np.exp(g("log_nu")),
                   ps=special.expit(g("lg_ps")), ph=special.expit(g("lg_ph")), roll=g("roll"), f=np.exp(g("log_f")))
        clubs = {}
        for k, v in self.bag.items():
            r = np.ones(len(X)) if k == self.ref else np.exp(g(f"lr:{k}"))
            b = out["beta"] * v["carry"] / self.cref + (0.0 if k == self.ref else g(f"d:{k}"))
            clubs[k] = dict(width=W * r, ratio=r, carry=v["carry"] + out["c_common"] + g(f"c:{k}"),
                            sd_c=v["depth"] * out["dm"] / 4.0, bias=b, roll=(v["total"] - v["carry"]) * out["roll"])
        out["clubs"] = clubs
        out["sessions"] = {s: g(f"so:{s}") for s in self.sessions}
        return out

    # ---------------------------------------------------------------- likelihood
    def _prep(self):
        """Group the observations by club as arrays."""
        self.lm_by = {}
        for k in self.clubs:
            rows = [r for r in self.data.lm if r["club"] == k]
            if rows:
                self.lm_by[k] = dict(
                    carry=np.array([r["carry"] for r in rows], float),
                    side=np.array([np.nan if r.get("side") is None else r["side"] for r in rows], float),
                    sess=np.array([self.sessions.index(r.get("session", "s0")) for r in rows]))
        self.co_by = {}
        for k in self.clubs:
            rows = [r for r in self.data.course if r["club"] == k]
            if rows:
                f = lambda key, dflt: np.array([dflt if r.get(key) is None else r[key] for r in rows], float)  # noqa
                cens = np.array([{None: 0, "left": -1, "right": 1, "both": 2}[r.get("censored")] for r in rows])
                self.co_by[k] = dict(total=f("total", np.nan), lat=f("lateral", np.nan), aim_sd=f("aim_sd", 6.0),
                                     gps_sd=f("gps_sd", 5.0), cond_sd=f("cond_sd", 8.0), cens=cens,
                                     beyond=f("beyond", 35.0))

    def loglik(self, X):
        X = np.atleast_2d(X)
        p = self.params(X)
        S = len(X)
        ll = np.zeros(S)
        nu = p["nu"][:, None]
        q = t_q(p["nu"])[:, None]
        ps, ph = p["ps"][:, None], p["ph"][:, None]
        lw = np.log(np.maximum(1 - ps - ph, 1e-12)), np.log(ps), np.log(ph)
        f = p["f"][:, None]
        for k, D in self.lm_by.items():
            c = p["clubs"][k]
            mu = c["carry"][:, None] + (np.stack([p["sessions"][s] for s in self.sessions], 1)[:, D["sess"]]
                                        if self.sessions else 0.0)
            sdc = np.sqrt(c["sd_c"][:, None] ** 2 + 1.5 ** 2)          # + 1.5 yd measurement error
            y = D["carry"][None, :]
            lc = (norm_logpdf(y, mu, sdc), unif_norm_logpdf(y, mu * SLIGHT["lo"], mu * SLIGHT["hi"], 2.0),
                  unif_norm_logpdf(y, mu * HEAVY["lo"], mu * HEAVY["hi"], 2.0))
            s = (c["width"][:, None] / f) / (2 * q)
            side = D["side"][None, :]
            has = ~np.isnan(side)
            dv = np.where(has, side - c["bias"][:, None], 0.0)
            ll_lat = [np.where(has, t_logpdf(dv, nu, s * m), 0.0) for m in (1.0, SLIGHT["lat"], HEAVY["lat"])]
            ll += logsumexp3(lw[0] + lc[0] + ll_lat[0], lw[1] + lc[1] + ll_lat[1], lw[2] + lc[2] + ll_lat[2]).sum(1)
        for k, D in self.co_by.items():
            c = p["clubs"][k]
            mu = c["carry"][:, None]
            rl = c["roll"][:, None]
            ext2 = (rl * 0.25 / np.sqrt(3)) ** 2 + D["cond_sd"][None, :] ** 2 + D["gps_sd"][None, :] ** 2
            y = D["total"][None, :]
            hast = ~np.isnan(y) & (D["cens"][None, :] == 0)
            yy = np.where(hast, y, 0.0)
            ext = np.sqrt(ext2)
            lt = (norm_logpdf(yy, mu + rl, np.sqrt(c["sd_c"][:, None] ** 2 + ext2)),
                  unif_norm_logpdf(yy, mu * SLIGHT["lo"] + rl, mu * SLIGHT["hi"] + rl, ext),
                  unif_norm_logpdf(yy, mu * HEAVY["lo"] + rl, mu * HEAVY["hi"] + rl, ext))
            lt = [np.where(hast, v, 0.0) for v in lt]
            s = c["width"][:, None] / (2 * q)
            lat = D["lat"][None, :]
            hasl = ~np.isnan(lat) & (D["cens"][None, :] == 0)
            noise = np.sqrt(D["aim_sd"] ** 2 + D["gps_sd"] ** 2)[None, :, None]
            # true lateral (from the aim) = observed - aim/GPS noise; a found ball had |true| <= beyond
            # (beyond = penalty / lost), so the density is truncated there, matching the censored shots
            xt = np.where(hasl, lat, 0.0)[:, :, None] - noise * GH_X24[None, None, :]
            inside = np.abs(xt) <= D["beyond"][None, :, None]
            dv = xt - c["bias"][:, None, None]
            cen = D["cens"][None, :]
            beyond = D["beyond"][None, :]
            ll_lat = []
            for m in (1.0, SLIGHT["lat"], HEAVY["lat"]):
                sm = (s * m)[:, :, None]
                dens = np.log(np.maximum((np.exp(t_logpdf(dv, nu[:, :, None], sm)) * inside * GH_W24).sum(2), 1e-300))
                sc = (s * m)
                bR = (beyond - c["bias"][:, None]) / sc
                bL = (beyond + c["bias"][:, None]) / sc
                pr, pl = t_sf(bR, nu), t_sf(bL, nu)
                pc = np.where(cen == 1, pr, np.where(cen == -1, pl, pr + pl))
                v = np.where(hasl, dens, np.where(cen != 0, np.log(np.maximum(pc, 1e-300)), 0.0))
                ll_lat.append(v)
            ll += logsumexp3(lw[0] + lt[0] + ll_lat[0], lw[1] + lt[1] + ll_lat[1], lw[2] + lt[2] + ll_lat[2]).sum(1)
        for sm in self.data.summary:
            ll += self._summary_ll(p, sm)
        return ll

    def _summary_ll(self, p, sm):
        """Summary stats via the course emulator (emulator.py): fairways / misses L-R (multinomial),
        tee penalties (Poisson), average drive (normal, + 6 yd systematic: app definitions, firmness)."""
        em = self.emulators.get(sm.get("course", "spirit_hollow"))
        if em is None:
            raise ValueError("summary stats need an emulator for course %r" % sm.get("course"))
        k = sm.get("club", self.ref)
        c = p["clubs"][k]
        feat = dict(logW=np.log(c["width"]), beta=c["bias"], inv_nu=1.0 / p["nu"], carry=c["carry"],
                    roll=c["roll"], ps=p["ps"], ph=p["ph"], log_dm=np.log(p["dm"]))
        pr = em.predict(feat, holes=sm.get("holes"))
        ll = np.zeros(len(p["W"]))
        n = sm.get("n_tee")
        if n and sm.get("fairways") is not None:
            fw = sm["fairways"]
            pf = np.clip(pr["fairway"], 1e-4, 1 - 1e-4)
            ll += fw * np.log(pf) + (n - fw) * np.log1p(-pf)
            L, R = sm.get("miss_left"), sm.get("miss_right")
            if L is not None and R is not None:
                pl = np.clip(pr["left_share"], 1e-4, 1 - 1e-4)
                ll += L * np.log(pl) + R * np.log1p(-pl)
        if n and sm.get("tee_penalties") is not None:
            lam = np.maximum(pr["penalty"] * n, 1e-9)
            ll += sm["tee_penalties"] * np.log(lam) - lam
        if sm.get("avg_drive") is not None:
            nd = sm.get("n_drives") or n or 20
            se = np.sqrt(16.0 ** 2 / nd + 6.0 ** 2)
            ll += norm_logpdf(sm["avg_drive"], pr["mean_total"], se)
        return ll

    def logpost(self, X):
        return self.logprior(X) + self.loglik(X)

    # ---------------------------------------------------------------- inference
    def fit(self, n_draws=4000, seed=0, chunk=400, verbose=False, mcmc_if_ess_below=300):
        rng = np.random.default_rng(seed)
        def f(x):
            v = -float(self.logpost(x[None, :])[0])
            return v if np.isfinite(v) else 1e12
        x0 = self.prior_mean()
        best = None
        for start in (x0, x0 + 0.1 * rng.standard_normal(self.d)):
            r = optimize.minimize(f, start, method="L-BFGS-B")
            if best is None or r.fun < best.fun:
                best = r
        xm = best.x
        H = _hessian(f, xm)
        try:
            cov = np.linalg.inv(H)
            cov = 0.5 * (cov + cov.T)
            w_, V = np.linalg.eigh(cov)
            cov = (V * np.maximum(w_, 1e-8)) @ V.T
        except np.linalg.LinAlgError:
            cov = np.diag(1.0 / np.maximum(np.diag(H), 1e-6))
        df = 5.0
        L = np.linalg.cholesky(cov * 1.2)
        Z = rng.standard_normal((n_draws, self.d))
        g = rng.chisquare(df, n_draws) / df
        X = xm + (Z @ L.T) / np.sqrt(g)[:, None]
        lq = stats.multivariate_t(loc=xm, shape=cov * 1.2, df=df).logpdf(X)
        lp = np.concatenate([self.logpost(X[i:i + chunk]) for i in range(0, n_draws, chunk)])
        lp = np.where(np.isfinite(lp), lp, -np.inf)          # an extreme draw (nu -> 0, ...) gets no weight
        lw = lp - lq
        lw -= lw.max()
        w = np.exp(lw)
        # truncate the largest weights (Ionides 2008: at mean * sqrt(n))
        w = np.minimum(w, w.mean() * np.sqrt(n_draws))
        w /= w.sum()
        ess = 1.0 / np.sum(w ** 2)
        method = "laplace-is"
        if ess < mcmc_if_ess_below:
            X, w, acc = self._metropolis(xm, cov, rng, n=max(n_draws, 4000))
            ess, method = float(len(X)) / 10.0, f"metropolis (acc {acc:.2f})"
        if verbose:
            print(f"fit: d={self.d} map={-best.fun:.1f} ess={ess:.0f} {method}")
        return Posterior(self, X, w, dict(ess=float(ess), method=method, map=xm.tolist(), logpost_map=-best.fun))

    def _metropolis(self, x0, cov, rng, n=4000, burn=2000, thin=1):
        d = self.d
        scale = 2.38 ** 2 / d
        L = np.linalg.cholesky(cov * scale + 1e-10 * np.eye(d))
        x, lp = x0.copy(), float(self.logpost(x0[None])[0])
        out, acc = [], 0
        hist = []
        for it in range(burn + n * thin):
            y = x + L @ rng.standard_normal(d)
            ly = float(self.logpost(y[None])[0])
            ly = ly if np.isfinite(ly) else -np.inf
            if math.log(rng.random()) < ly - lp:
                x, lp = y, ly
                acc += 1
            hist.append(x.copy())
            if it == burn // 2:                            # adapt once
                C = np.cov(np.array(hist[burn // 4:]).T) + 1e-8 * np.eye(d)
                try:
                    L = np.linalg.cholesky(C * scale)
                except np.linalg.LinAlgError:
                    pass
            if it >= burn and (it - burn) % thin == 0:
                out.append(x.copy())
        X = np.array(out)
        return X, np.full(len(X), 1.0 / len(X)), acc / (burn + n * thin)


def _hessian(f, x, h=1e-3):
    d = len(x)
    H = np.zeros((d, d))
    fx = f(x)
    E = np.eye(d) * h
    fp = np.array([f(x + E[i]) for i in range(d)])
    fm = np.array([f(x - E[i]) for i in range(d)])
    for i in range(d):
        H[i, i] = (fp[i] - 2 * fx + fm[i]) / h ** 2
        for j in range(i + 1, d):
            v = (f(x + E[i] + E[j]) - fp[i] - fp[j] + fx) / h ** 2
            H[i, j] = H[j, i] = v
    return H


# --------------------------------------------------------------------------------------- posterior
def wquantile(x, w, qs):
    o = np.argsort(x)
    cw = np.cumsum(w[o])
    cw /= cw[-1]
    return np.interp(qs, cw, x[o])


class Posterior:
    def __init__(self, model: Model, X, w, info):
        self.model, self.X, self.w, self.info = model, X, w, info
        self.p = model.params(X)

    def summary(self, x, qs=(0.05, 0.5, 0.95)):
        x = np.asarray(x, float)
        q = wquantile(x, self.w, qs)
        m = float(np.sum(self.w * x))
        sd = float(np.sqrt(np.sum(self.w * (x - m) ** 2)))
        return dict(mean=m, sd=sd, median=float(q[1]), ci90=[float(q[0]), float(q[2])])

    def resample(self, n, seed=0):
        """n equally weighted draws (systematic resampling) as natural parameters."""
        rng = np.random.default_rng(seed)
        u = (rng.random() + np.arange(n)) / n
        idx = np.searchsorted(np.cumsum(self.w) / self.w.sum(), u)
        return self.model.params(self.X[np.minimum(idx, len(self.X) - 1)])


def json_default(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def dumps(obj):
    return json.dumps(obj, indent=1, default=json_default)
