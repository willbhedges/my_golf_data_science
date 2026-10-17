"""Stage selector (stage_select.py) and the routing_v2 structure prior: data tiers, fallbacks, prior plane."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import routing as R  # noqa: E402
import routing_v2 as R2  # noqa: E402
import stage_select as SS  # noqa: E402


def _poly(lon, lat, d=0.0001, **props):
    ring = [[lon - d, lat - d], [lon + d, lat - d], [lon + d, lat + d], [lon - d, lat + d], [lon - d, lat - d]]
    return dict(type="Feature", geometry=dict(type="Polygon", coordinates=[ring]), properties=props)


def _fc(n_greens, n_tees, holes=()):
    feats = [_poly(-93.6 + 0.004 * i, 41.6, golf="green", osm_id=i) for i in range(n_greens)]
    feats += [_poly(-93.6 + 0.004 * i, 41.603, golf="tee", osm_id=100 + i) for i in range(n_tees)]
    for r in holes:
        feats.append(dict(type="Feature", properties=dict(golf="hole", ref=str(r)),
                          geometry=dict(type="LineString", coordinates=[[-93.6, 41.603], [-93.6, 41.6]])))
    return dict(type="FeatureCollection", features=feats)


CARD = dict(par=[4] * 18, tee_sets={"White": dict(yards=[380] * 18)})


def test_tiers_from_data():
    assert SS.tier(SS.profile(_fc(18, 20), CARD)) == "mapped_card"
    assert SS.tier(SS.profile(_fc(3, 2), CARD)) == "unmapped_card"
    assert SS.tier(SS.profile(_fc(18, 20), None)) == "mapped_nocard"
    assert SS.tier(SS.profile(_fc(0, 0), None)) == "unmapped_nocard"
    p = SS.profile(_fc(18, 20, holes=range(1, 19)), CARD)
    assert p["osm_holes_complete"] and p["n_holes"] == 18 and p["n_from"] == "card"
    assert SS.profile(_fc(9, 9), None)["n_holes"] == 9


def test_fallbacks_recorded():
    """Unmapped, no card, no scene: the structure solver has nothing to run on -> the chain falls through and says so."""
    res, info = SS.infer_holes(_fc(0, 0), None, {}, scene=None)
    assert info["tier"] == "unmapped_nocard"
    assert info["tried"][0] == SS.SELECT["unmapped_nocard"]["method"] and info["fallbacks"]
    assert info["method"] in (None, "v2", "structure", "geometry")


def test_struct_card_shapes():
    assert SS.struct_card(CARD) == dict(par=[4] * 18, yards=[380] * 18)
    syn = dict(par=[4] * 9, yards={"osm": [300 + i for i in range(9)]})
    assert SS.struct_card(syn)["yards"] == [300 + i for i in range(9)]
    assert SS.struct_card(None) is None


def test_prior_plane():
    pr = R.Proj(-93.6, 41.6)
    gxy = np.array([pr.fwd(-93.6, 41.6), pr.fwd(-93.59, 41.6), pr.fwd(-93.58, 41.6)])
    P = np.array([[0.9, 0.1], [0.1, 0.9]])
    sp = dict(greens_ll=[[-93.6, 41.6], [-93.59, 41.6001]], P=P.tolist(), lam=2.0)
    pl = R2.prior_plane(sp, pr, gxy, 2)
    assert pl.shape == (2, 3)
    assert pl[0, 0] < 0 < pl[1, 0] and pl[1, 1] < 0 < pl[0, 1]     # confident -> reward, unlikely -> cost
    assert pl[0, 2] == 0 and pl[1, 2] == 0                          # no structure green within 25 yds
    assert R2.prior_plane(sp, pr, gxy, 3) is None                   # hole counts differ: no prior
    assert R2.prior_plane(dict(sp, lam=0), pr, gxy, 2) is None


def test_localizer_v2_is_default():
    import package as pkg
    assert pkg.localizer_enabled({})
    assert pkg.localizer_enabled({"tee_localizer": "v2"})
    assert not pkg.localizer_enabled({"tee_localizer": "v1"})
