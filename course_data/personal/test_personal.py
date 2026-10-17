"""Unit tests for the personalisation path (python3 -m pytest -q course_data/personal)."""
import json
import math
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bayes as B                                     # noqa: E402
import parsers as PZ                                  # noqa: E402
import player_profile as PR                                 # noqa: E402
import simulate as S                                  # noqa: E402

EX = os.path.join(HERE, "examples")
BAG2 = {k: v for k, v in B.BOOK_BAG.items() if k in ("Driver", "4-wood")}


# ----------------------------------------------------------------------------- parsers
@pytest.mark.parametrize("raw,want", [("Dr", "Driver"), ("1W", "Driver"), ("3 Wood", "3-wood"), ("3W", "3-wood"),
                                      ("4H", "4-hybrid"), ("Hybrid 4", "4-hybrid"), ("7i", "7-iron"),
                                      ("7 Iron", "7-iron"), ("Pitching Wedge", "PW"), ("sw", "SW")])
def test_canonical_club(raw, want):
    assert PZ.canonical_club(raw) == want


def test_garmin_r10_units_row_and_LR_side():
    aliases = json.load(open(os.path.join(EX, "bag.json")))
    d = PZ.parse_launch_monitor(os.path.join(EX, "garmin_r10_session.csv"),
                                {k: v["aliases"] for k, v in aliases.items()})
    assert len(d.lm) == 40
    assert {r["club"] for r in d.lm} == {"Driver", "4-wood"}
    drv = [r for r in d.lm if r["club"] == "Driver"]
    assert 230 < np.mean([r["carry"] for r in drv]) < 300
    assert any(r["side"] < 0 for r in drv) and any(r["side"] > 0 for r in drv)
    first = open(os.path.join(EX, "garmin_r10_session.csv")).read().splitlines()[2].split(",")
    assert drv[0]["side"] == pytest.approx(-float(first[17].split()[0]) if first[17].endswith("L")
                                           else float(first[17].split()[0]))


def test_trackman_metadata_and_metres():
    d = PZ.parse_launch_monitor(os.path.join(EX, "trackman_session.csv"))
    assert len(d.lm) == 15
    row = open(os.path.join(EX, "trackman_session.csv")).read().splitlines()[3].split(",")
    assert d.lm[0]["carry"] == pytest.approx(float(row[2]) * PZ.YD_PER_M)
    assert d.lm[0]["side"] == pytest.approx(float(row[4]) * PZ.YD_PER_M)


def test_tee_shot_geometry():
    lat0, lon0 = 40.8, -91.15
    R = 6371008.8 / 0.9144
    north = (lat0 + math.degrees(300 / R), lon0)
    end = (lat0 + math.degrees(260 / R), lon0 + math.degrees(20 / (R * math.cos(math.radians(lat0)))))
    tot, lat = PZ.tee_shot_geometry((lat0, lon0), end, north)
    assert tot == pytest.approx(math.hypot(260, 20), abs=0.5)
    assert lat == pytest.approx(20, abs=0.3)                 # east of a northward line = right


def test_shot_csv_and_arccos():
    d = PZ.parse_shot_csv(os.path.join(EX, "tee_shots.csv"))
    assert len(d.course) == 30
    ok = [r for r in d.course if r["censored"] is None]
    assert all(r["aim_sd"] == PZ.AIM_SD["plan"] for r in ok)
    assert 240 < np.median([r["total"] for r in ok]) < 330
    bm = json.load(open(os.path.join(EX, "arccos_bag_map.json")))
    a = PZ.parse_arccos_json(os.path.join(EX, "arccos_round.json"), bm)
    assert len(a.course) == 4 and all(r["club"] == "Driver" for r in a.course)
    assert all(r["aim_sd"] == PZ.AIM_SD["green_line"] for r in a.course if r["censored"] is None)


def test_manual_percentages_to_counts():
    d = PZ.parse_manual(os.path.join(EX, "manual_stats.json"))
    s = d.summary[0]
    assert s["n_tee"] == 280 and s["fairways"] == round(280 * 0.52) and s["tee_penalties"] == 12
    assert s["miss_left"] + s["miss_right"] + s["fairways"] == 280


def test_garmin_scorecards_summary():
    obj = {"scorecards": [{"holes": [{"number": 1, "fairwayShotOutcome": "HIT", "penalties": 0},
                                      {"number": 2, "fairwayShotOutcome": "LEFT", "penalties": 1},
                                      {"number": 3}, {"number": 4, "fairwayShotOutcome": "RIGHT"}]}]}
    s = PZ.parse_garmin_scorecards(obj).summary[0]
    assert (s["n_tee"], s["fairways"], s["miss_left"], s["miss_right"], s["tee_penalties"]) == (3, 1, 1, 1, 1)


# ----------------------------------------------------------------------------- model
def test_t_quantile_matches_v2_convention():
    assert float(B.t_q(1e9)) == pytest.approx(2.0, abs=1e-3)       # width95 = 4 sigma for a normal
    assert float(B.t_q(4.0)) > 2.5


def test_prior_reproduces_final_decision_width():
    m = B.Model(BAG2)
    X = m.sample_prior(20000, np.random.default_rng(0))
    W = m.params(X)["W"]
    assert np.median(W) == pytest.approx(70, abs=0.5)
    assert np.quantile(W, 0.05) == pytest.approx(62.0, abs=1.0)
    assert np.quantile(W, 0.95) == pytest.approx(80.0, abs=1.0)
    r4 = m.params(X)["clubs"]["4-wood"]["width"] / W
    assert np.median(r4) == pytest.approx(54 / 70, abs=0.01)


def test_no_data_posterior_is_prior():
    post = B.Model(BAG2).fit(n_draws=1500, seed=1)
    s = post.summary(post.p["W"])
    assert s["median"] == pytest.approx(70, abs=1.5)
    assert s["ci90"][0] == pytest.approx(62, abs=2.0) and s["ci90"][1] == pytest.approx(80, abs=2.5)


def test_likelihood_peaks_near_truth():
    m0 = B.Model(BAG2)
    x = m0.prior_mean()
    x[m0.ix["logW"]] = math.log(82)
    T = S.truth_from(m0, x)
    rng = np.random.default_rng(3)
    d = B.Data(course=S.course_shots(T, "Driver", 400, rng, aim_sd=3))
    m = B.Model(BAG2, B.Prior.generic(), d)
    xs = np.repeat(x[None, :], 7, 0)
    ws = np.log([60, 70, 76, 82, 88, 95, 110])
    xs[:, m.ix["logW"]] = ws
    ll = m.loglik(xs)
    assert int(np.argmax(ll)) in (2, 3, 4)


def test_recovers_wide_driver_from_course_data():
    """A golfer at 82 yds (published 0-5 hcp) with 20 rounds of logged tee shots: the posterior moves off
    the 70-yd prior and covers the truth."""
    m0 = B.Model(BAG2)
    x = m0.prior_mean()
    x[m0.ix["logW"]] = math.log(82)
    x[m0.ix["beta"]] = 0.0
    T = S.truth_from(m0, x)
    rng = np.random.default_rng(11)
    d = B.Data(course=S.course_shots(T, "Driver", 200, rng, aim_sd=3) + S.course_shots(T, "4-wood", 60, rng, aim_sd=3))
    post = B.Model(BAG2, B.Prior.v2(), d).fit(n_draws=2000, seed=2)
    s = post.summary(post.p["W"])
    assert s["ci90"][0] <= 82 <= s["ci90"][1]
    assert s["median"] > 74


def test_launch_monitor_learns_carry_and_bias():
    m0 = B.Model(BAG2, B.Prior.generic())
    x = m0.prior_mean()
    x[m0.ix["beta"]] = 7.0
    x[m0.ix["c_common"]] = -12.0
    x[m0.ix["log_f"]] = 0.0
    T = S.truth_from(m0, x)
    rng = np.random.default_rng(5)
    d = B.Data(lm=S.lm_shots(T, "Driver", 80, rng) + S.lm_shots(T, "4-wood", 80, rng))
    post = B.Model(BAG2, B.Prior.generic(), d, fix={"log_f": 0.0}).fit(n_draws=2000, seed=3)
    c = post.summary(post.p["clubs"]["Driver"]["carry"])
    b = post.summary(post.p["clubs"]["Driver"]["bias"])
    assert c["ci90"][0] <= 263 <= c["ci90"][1]
    assert b["ci90"][0] <= 7 <= b["ci90"][1] and b["median"] > 3


# ----------------------------------------------------------------------------- profile
@pytest.fixture(scope="module")
def profile():
    d = PZ.parse_shot_csv(os.path.join(EX, "tee_shots.csv"))
    post = B.Model(B.BOOK_BAG, B.Prior.v2(), d).fit(n_draws=1500, seed=4)
    return PR.build_profile(post, "example", [dict(kind="on_course", file="tee_shots.csv", n=30)])


def test_profile_contract(profile):
    assert profile["schema"] == "golf_player/1"
    for k in B.BOOK_BAG:
        c = profile["clubs"][k]
        for f in ("carry", "total", "roll", "width95", "depth95", "bias"):
            assert set(c[f]) >= {"median", "sd", "ci90"}
        assert c["carry"]["ci90"][0] <= c["carry"]["median"] <= c["carry"]["ci90"][1]
    assert profile["clubs"]["Driver"]["source"] == "data" and profile["clubs"]["Mid iron"]["source"] == "prior"
    assert len(profile["draws"]["clubs"]["Driver"]["width95"]) == PR.N_DRAWS
    assert set(profile["app_player"]["clubs"]["Driver"]) == {"carry", "total", "width95"}
    json.dumps(profile)


def test_profile_to_v2_and_picks(profile):
    P = PR.to_v2_params(profile)
    assert P["width"]["Driver"] == pytest.approx(profile["clubs"]["Driver"]["width95"]["median"])
    assert set(P["width"]) >= {"Driver", "2-wood", "4-wood", "Long iron", "Mid iron"}
    P0 = PR.to_v2_params(profile, 0)
    assert P0["width"]["Driver"] == profile["draws"]["clubs"]["Driver"]["width95"][0]
    pk = PR.picks_at_interval(profile)
    h5 = next(r for r in pk["holes"] if r["hole"] == "5")
    assert h5["break_evens"] and 0 <= h5["p_other_club"] <= 1
    # a profile pinned at 90 yds puts hole 5 on the 4-wood side of its 79-yd break-even
    pk90 = PR.picks_at_interval(dict(profile, clubs=dict(profile["clubs"], Driver=dict(
        profile["clubs"]["Driver"], width95=dict(median=90, ci90=[88, 92])))), width_draws=[89, 90, 91])
    assert next(r for r in pk90["holes"] if r["hole"] == "5")["pick_median"] == "4-wood"


# ----------------------------------------------------------------------------- emulator
@pytest.mark.skipif(not os.path.exists(os.path.join(os.path.dirname(os.path.dirname(HERE)), "spirit_hollow", "v2",
                                                    "model.py")), reason="v2 model missing")
def test_emulator_small_bank_monotone():
    import emulator as E
    r = E.bank(k=128, n=300)
    em = E.Emulator(r)
    f = dict(logW=np.log([55, 70, 90, 110]), beta=np.zeros(4), inv_nu=np.full(4, 0.03), carry=np.full(4, 275.0),
             roll=np.full(4, 25.0), ps=np.full(4, 0.12), ph=np.full(4, 0.025), log_dm=np.full(4, np.log(1.25)))
    p = em.predict(f)
    assert np.all(np.diff(p["fairway"]) < 0.02)           # wider -> fewer fairways (noisy small bank)
    assert p["fairway"][0] > p["fairway"][-1] + 0.05
    assert p["penalty"][-1] > p["penalty"][0]
