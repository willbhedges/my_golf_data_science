"""Player profile (`golf_player/1`): the posterior as a JSON document the app and the planner consume.

  python3 course_data/personal/player_profile.py --bag bag.json [--lm FILE ...] [--shots FILE ...] [--arccos FILE
          --arccos-bag MAP.json] [--manual FILE] [--prior v2|generic] [--out profile.json]

Contract: see PROFILE.md. Also here:
  to_v2_params(profile, i)  -> keyword overrides for spirit_hollow/v2/model.central (posterior draw i), so
                               decide.py can run its Bayesian plan over the golfer's posterior draws
                               instead of the generic prior.
  picks_at_interval(profile) -> how the Spirit Hollow picks change across the profile's credible interval
                               for the driver width (v2 width sweep / break-evens, final_decision.py logic).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import bayes as B                                        # noqa: E402
import parsers as PZ                                     # noqa: E402

SCHEMA = "golf_player/1"
N_DRAWS = 64            # posterior draws carried in the profile (the planner's 64 Sobol prior draws -> these)


def _r(x, n=1):
    return None if x is None else round(float(x), n)


def _summ(post, x, nd=1):
    s = post.summary(x)
    return dict(median=_r(s["median"], nd), mean=_r(s["mean"], nd), sd=_r(s["sd"], nd + 1),
                ci90=[_r(s["ci90"][0], nd), _r(s["ci90"][1], nd)])


def build_profile(post: B.Posterior, name="player", sources=None, home_course=None, seed=0):
    m = post.model
    p = post.p
    counts = m.data.counts()
    clubs = {}
    for k, v in m.bag.items():
        c = p["clubs"][k]
        n = counts.get(k, {"launch_monitor": 0, "on_course": 0})
        lw = np.log(c["width"])
        clubs[k] = dict(
            stated=dict(carry=v["carry"], total=v["total"]),
            carry=_summ(post, c["carry"]),
            total=_summ(post, c["carry"] + c["roll"]),
            roll=_summ(post, c["roll"]),
            width95=dict(_summ(post, c["width"]), sd_log=_r(post.summary(lw)["sd"], 4)),
            depth95=_summ(post, c["sd_c"] * 4),
            bias=_summ(post, c["bias"]),
            ratio_to_ref=_summ(post, c["ratio"], 3),
            n_shots=n,
            source="data" if (n["launch_monitor"] + n["on_course"]) else ("summary" if m.data.summary and k == m.ref
                                                                          else "prior"))
    shared = dict(
        nu=_summ(post, p["nu"]), mishit_slight=_summ(post, p["ps"], 3), mishit_heavy=_summ(post, p["ph"], 4),
        roll_mult=_summ(post, p["roll"], 3), depth_mult=_summ(post, p["dm"], 3),
        range_to_course=_summ(post, p["f"], 3),
        mishit_model=dict(slight=dict(carry_frac=[B.SLIGHT["lo"], B.SLIGHT["hi"]], lateral_x=B.SLIGHT["lat"]),
                          heavy=dict(carry_frac=[B.HEAVY["lo"], B.HEAVY["hi"]], lateral_x=B.HEAVY["lat"])),
        not_learned=dict(rho="U(-0.1, 0.3) (v2 prior)", kappa="U(0, 0.16) (v2 prior)"))
    R = post.resample(N_DRAWS, seed)
    draws = dict(n=N_DRAWS, nu=[_r(x, 2) for x in R["nu"]], mishit_slight=[_r(x, 4) for x in R["ps"]],
                 mishit_heavy=[_r(x, 4) for x in R["ph"]], roll_mult=[_r(x, 3) for x in R["roll"]],
                 depth_mult=[_r(x, 3) for x in R["dm"]],
                 clubs={k: dict(carry=[_r(x) for x in c["carry"]], width95=[_r(x) for x in c["width"]],
                                bias=[_r(x, 2) for x in c["bias"]], roll=[_r(x) for x in c["roll"]],
                                depth95=[_r(x) for x in c["sd_c"] * 4]) for k, c in R["clubs"].items()})
    app = dict(clubs={k: dict(carry=clubs[k]["carry"]["median"], total=clubs[k]["total"]["median"],
                              width95=clubs[k]["width95"]["median"]) for k in m.bag},
               temp_carry_pct_per_f=0.10, temp_ref_f=70)
    prof = dict(
        schema=SCHEMA, player=name, updated=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        home_course=home_course, reference_club=m.ref, prior=m.prior.name,
        conventions=dict(units="yards", lateral="+ = right of the intended line", temp_ref_f=70,
                         width95="central 95.45 % lateral interval of a good strike (= 4 sigma when normal), on course",
                         depth95="carry window of a good strike (= 4 sd)", total="carry + roll on the home course's fairways"),
        sources=sources or [],
        data=dict(launch_monitor=len(m.data.lm), on_course=len(m.data.course), summary=len(m.data.summary)),
        fit=dict(post.info, map=None),
        clubs=clubs, shared=shared, draws=draws, app_player=app)
    return prof


def to_v2_params(profile, i=None):
    """model.central(**overrides) for posterior draw i (None = medians). Clubs map by name to v2's
    (Driver, 2-wood, 4-wood, Long iron, Mid iron); others are ignored by v2. c_common = 0 and all carry
    shifts go to c_club, so the stated v2 carries + c_club = the posterior carry."""
    sys.path.insert(0, os.path.join(ROOT, "spirit_hollow", "v2"))
    import model as M

    def val(club, field):
        return profile["clubs"][club][field]["median"] if i is None else profile["draws"]["clubs"][club][field][i]

    def g(key):
        return profile["shared"][key]["median"] if i is None else profile["draws"][key][i]
    width, cclub = {}, {}
    for c in profile["clubs"]:
        if c in M.CLUBS:
            width[c] = float(val(c, "width95"))
            cclub[c] = float(val(c, "carry")) - M.CLUBS[c][0]
    ref = profile["reference_club"]
    bias = val(ref, "bias")
    base = M.central()
    for c in M.CLUBS:
        width.setdefault(c, base["width"][c] * (width.get("Driver", 70.0) / base["width"]["Driver"]))
    rm = g("roll_mult")
    if ref in M.CLUBS and M.CLUBS[ref][1] > M.CLUBS[ref][0]:      # v2 rolls x (its total - carry)
        rm = float(val(ref, "roll")) / (M.CLUBS[ref][1] - M.CLUBS[ref][0])
    return dict(width=width, c_common=0.0, c_club=cclub, bias=float(bias), mis_slight=float(g("mishit_slight")),
                mis_heavy=float(g("mishit_heavy")), roll_mult=float(rm), depth_mult=float(g("depth_mult")))


# --------------------------------------------------------------------------------------- picks
def _pick_at(sweep, flips, w):
    pick = sweep[0]["pick"]
    for f in sorted(flips, key=lambda f: f["width"]):
        if w >= f["width"]:
            pick = f["to"]
    return pick


def picks_at_interval(profile, decisions=None, width_draws=None):
    """Per hole: the pick at the driver width's median and 90% interval ends, the break-even widths and
    the posterior probability that the other club is right (mass beyond a break-even).
    decisions: spirit_hollow/v2/output/v2_decisions.json (default) or output/final_decision.json (v1)."""
    path = decisions or os.path.join(ROOT, "spirit_hollow", "v2", "output", "v2_decisions.json")
    D = json.load(open(path))
    ref = profile["reference_club"]
    W = profile["clubs"][ref]["width95"]
    lo, med, hi = W["ci90"][0], W["median"], W["ci90"][1]
    wd = np.asarray(width_draws if width_draws is not None else profile["draws"]["clubs"][ref]["width95"], float)
    rows = []
    for h, r in D.items():
        sweep, flips = r.get("width_sweep"), r.get("width_flips") or []
        if not sweep:
            continue
        pm = _pick_at(sweep, flips, med)
        p_other = float(np.mean([_pick_at(sweep, flips, x) != pm for x in wd]))
        near = [f for f in flips if lo - 5 <= f["width"] <= hi + 5]
        rows.append(dict(hole=h, pick_median=pm, pick_lo=_pick_at(sweep, flips, lo), pick_hi=_pick_at(sweep, flips, hi),
                         break_evens=[dict(width=f["width"], frm=f["frm"], to=f["to"]) for f in flips],
                         inside_ci=[f["width"] for f in flips if lo <= f["width"] <= hi], near=bool(near),
                         p_other_club=round(p_other, 3), plan_pick=r.get("pick")))
    return dict(width=dict(median=med, ci90=[lo, hi]), source=os.path.relpath(path, ROOT), holes=rows,
                note="Break-evens scale every club's width with the driver's (common mode, as in "
                     "final_decision.py / decide.width_sweep); aims also move with width (re-solve per profile).")


def picks_markdown(pk):
    out = [f"Driver width {pk['width']['median']:.0f} yds (90% {pk['width']['ci90'][0]:.0f}-{pk['width']['ci90'][1]:.0f}); "
           f"picks from `{pk['source']}`.", "",
           "| Hole | Pick at median | at 5% | at 95% | Break-evens | P(other club right) |", "|---|---|---|---|---|---|"]
    for r in pk["holes"]:
        be = "; ".join(f"{b['frm']}→{b['to']} at {b['width']:.0f}" for b in r["break_evens"]) or "none 55-90"
        out.append(f"| {r['hole']} | {r['pick_median']} | {r['pick_lo']} | {r['pick_hi']} | {be} | {r['p_other_club']:.0%} |")
    return "\n".join(out)


# --------------------------------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bag", help="JSON {club: {carry, total?, width?, depth?, aliases?}}; default = the book's bag")
    ap.add_argument("--lm", nargs="*", default=[])
    ap.add_argument("--range-balls", action="store_true")
    ap.add_argument("--shots", nargs="*", default=[])
    ap.add_argument("--arccos", nargs="*", default=[])
    ap.add_argument("--arccos-bag", help="JSON {clubId: bag name}")
    ap.add_argument("--manual", nargs="*", default=[])
    ap.add_argument("--prior", default="v2", choices=["v2", "generic"])
    ap.add_argument("--emulator", default=os.path.join(HERE, "output", "emulator_spirit_hollow.npz"))
    ap.add_argument("--name", default="player")
    ap.add_argument("--out", default="profile.json")
    a = ap.parse_args()
    bagj = json.load(open(a.bag)) if a.bag else B.BOOK_BAG
    aliases = {k: v.get("aliases", [k]) for k, v in bagj.items()}
    bag = {k: {kk: vv for kk, vv in v.items() if kk != "aliases"} for k, v in bagj.items()}
    data, sources = B.Data(), []
    for f in a.lm:
        d = PZ.parse_launch_monitor(f, aliases, ball="range" if a.range_balls else "premium", clubs=list(bag))
        for r in d.lm:
            r["session"] = os.path.basename(f) + ":" + r["session"]
        data.extend(d)
        sources.append(dict(kind="launch_monitor", file=os.path.basename(f), n=len(d.lm)))
    for f in a.shots:
        d = PZ.parse_shot_csv(f, aliases)
        d.course = [r for r in d.course if r["club"] in bag]
        data.extend(d)
        sources.append(dict(kind="on_course", file=os.path.basename(f), n=len(d.course)))
    if a.arccos:
        bm = json.load(open(a.arccos_bag))
        for f in a.arccos:
            d = PZ.parse_arccos_json(f, bm)
            data.extend(d)
            sources.append(dict(kind="arccos", file=os.path.basename(f), n=len(d.course)))
    emus = {}
    for f in a.manual:
        d = PZ.parse_manual(f)
        data.extend(d)
        sources.append(dict(kind="summary", file=os.path.basename(f), rounds=d.summary[0].get("rounds")))
    if data.summary:
        from emulator import Emulator
        emus["spirit_hollow"] = Emulator(a.emulator)
    prior = B.Prior.v2() if a.prior == "v2" else B.Prior.generic()
    model = B.Model(bag, prior, data, emus)
    post = model.fit(verbose=True)
    prof = build_profile(post, a.name, sources, home_course=(data.summary[0]["course"] if data.summary else None))
    try:
        prof["spirit_hollow_picks"] = picks_at_interval(prof)
    except (OSError, KeyError):
        pass
    with open(a.out, "w") as f:
        f.write(B.dumps(prof))
    print("wrote", a.out)
    if "spirit_hollow_picks" in prof:
        print(picks_markdown(prof["spirit_hollow_picks"]))


if __name__ == "__main__":
    main()
