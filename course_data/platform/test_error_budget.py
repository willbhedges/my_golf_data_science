"""Swap mechanics of error_budget.py: lie-region swaps, layer application, the no-swap / all-swap identities."""
import copy
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import error_budget as E  # noqa: E402

LON0, LAT0 = -94.6, 38.9
D = 1e-4                                    # ~10 yds per unit


def sq(x0, y0, x1, y1):
    return [(LON0 + x0 * D, LAT0 + y0 * D), (LON0 + x1 * D, LAT0 + y0 * D), (LON0 + x1 * D, LAT0 + y1 * D),
            (LON0 + x0 * D, LAT0 + y1 * D)]


def grid(n=81):
    xs = np.linspace(-1, 11, n)
    X, Y = np.meshgrid(xs, xs)
    return np.c_[LON0 + X.ravel() * D, LAT0 + Y.ravel() * D]


AUTO = [("recovery", sq(0, 0, 4, 10)), ("ob", sq(9, 0, 10, 10)), ("fairway", sq(3, 0, 7, 10)),
        ("sand", sq(5, 5, 6, 6))]
# truth: auto + footprint rough mask + hand zones (trees narrower, fairway wider, water, no OB)
TRUTH = AUTO + [("rough", sq(-1, -1, 11, 11)), ("recovery", sq(0, 0, 2, 10)), ("fairway", sq(2, 0, 8, 10)),
                ("water", sq(6, 2, 7, 3)), ("sand", sq(4, 4, 5, 5)), ("recovery", sq(4.5, 7, 5.5, 8))]


def test_no_swap_and_all_swap_identities():
    P = grid()
    a, t = E.lie_at_ll(AUTO, P), E.lie_at_ll(TRUTH, P)
    assert (E.lie_at_ll(E.mixed_stack(AUTO, TRUTH, set(), {}), P) == a).all()
    assert (E.lie_at_ll(E.mixed_stack(AUTO, TRUTH, set(E.LAYERS), {}), P) == t).all()
    # every hazard layer swapped via the region path (not the all-layers shortcut) == truth
    h = E.hybrid_stack(AUTO, TRUTH, E.lies_of(E.ZONE_LAYERS))
    assert ((E.lie_at_ll(h, P) == t) | _edge(P)).all()


@pytest.mark.parametrize("layer", list(E.ZONE_LAYERS))
def test_forward_swap_changes_only_that_layer(layer):
    P = grid()
    a, t = E.lie_at_ll(AUTO, P), E.lie_at_ll(TRUTH, P)
    lies = set(E.ZONE_LAYERS[layer])
    h = E.lie_at_ll(E.mixed_stack(AUTO, TRUTH, {layer}, {}), P)
    inside_t = np.isin(t, list(lies))
    on_edge = _edge(P)
    # where the truth shows the layer, the hybrid shows it
    assert ((h == t) | ~inside_t | on_edge).all()
    # where neither truth nor auto shows the layer, the hybrid is the auto lie
    neither = ~inside_t & ~np.isin(a, list(lies))
    assert ((h == a) | ~neither | on_edge).all()
    # the hybrid never shows the layer where the truth does not
    assert (~np.isin(h, list(lies)) | inside_t | on_edge).all()


@pytest.mark.parametrize("layer", list(E.ZONE_LAYERS))
def test_reverse_swap_keeps_auto_layer_on_truth(layer):
    P = grid()
    a, t = E.lie_at_ll(AUTO, P), E.lie_at_ll(TRUTH, P)
    lies = set(E.ZONE_LAYERS[layer])
    h = E.lie_at_ll(E.mixed_stack(AUTO, TRUTH, set(E.LAYERS) - {layer}, {}), P)
    in_a = np.isin(a, list(lies))
    on_edge = _edge(P)
    assert ((h == a) | ~in_a | on_edge).all()                 # auto layer painted on top
    neither = ~in_a & ~np.isin(t, list(lies))
    assert ((h == t) | ~neither | on_edge).all()              # elsewhere the truth


def _edge(P, tol=0.08):
    """grid points within tol units of a square edge (polygon boundary ambiguity)."""
    x, y = (P[:, 0] - LON0) / D, (P[:, 1] - LAT0) / D
    edges = {v for _, r in TRUTH for p in r for v in ((p[0] - LON0) / D, (p[1] - LAT0) / D)}
    near = np.zeros(len(P), bool)
    for e in edges:
        near |= (np.abs(x - e) < tol) | (np.abs(y - e) < tol)
    return near


def test_simple_rings_cut_holes():
    from shapely.geometry import Polygon
    g = Polygon(sq(0, 0, 10, 10), [sq(2, 2, 4, 4)[::-1], sq(6, 6, 8, 8)[::-1]])
    rings = E.simple_rings(g)
    assert len(rings) >= 2
    assert all(Polygon(r).is_valid for r in rings)
    P = grid()
    stack = [("water", r) for r in rings]
    want = np.array([g.contains(__import__("shapely").geometry.Point(*p)) for p in P])
    got = E.lie_at_ll(stack, P) == "water"
    assert (got == want).mean() > 0.99


def _pkg():
    hole = dict(par=4, yards={"Black": 400}, green_ll=[LON0 + 0.003, LAT0 + 0.003], hole_line_ll=[[LON0, LAT0], [LON0 + 0.003, LAT0 + 0.003]],
                tees={"Black": dict(tee_ll=[LON0, LAT0], aim_ll=[LON0 + 0.001, LAT0 + 0.001], card_yards=400)},
                zones_ll=[dict(lie="fairway", poly=sq(0, 0, 3, 3), src="osm")])
    return dict(tee_set="Black", tee_sets={"Black": {}}, holes={"1": hole})


TD = {"1": dict(par=5, yards={"Black": 510}, line=[[LON0, LAT0], [LON0 + 0.004, LAT0]], green_ll=[LON0 + 0.004, LAT0],
                green_poly=sq(39, -1, 41, 1), tee_ll=[LON0 - 0.0001, LAT0])}


@pytest.mark.parametrize("layer,field", [("card", "par"), ("routing", "hole_line_ll"), ("greens", "green_ll"),
                                         ("tees", "tee")])
def test_apply_single_frame_layer(layer, field):
    base = E.prepare(_pkg(), "Black")
    out = E.apply_layers(base, TD, "Black", {layer}, {})
    h0, h = base["holes"]["1"], out["holes"]["1"]
    changed = {k for k in set(h) | set(h0) if h.get(k) != h0.get(k)}
    tee_changed = h["tees"]["Black"] != h0["tees"]["Black"]
    if layer == "card":
        assert h["par"] == 5 and h["yards"] == {"Black": 510} and h["tees"]["Black"]["card_yards"] == 510
        assert changed == {"par", "yards", "tees"}
    elif layer == "routing":
        assert changed == {"hole_line_ll"} and not tee_changed
    elif layer == "greens":
        assert changed == {"green_ll", "green_polygon_ll"} and not tee_changed
    else:
        assert changed == {"tees"} and h["tees"]["Black"]["tee_ll"] == TD["1"]["tee_ll"]
        assert "aim_ll" not in h["tees"]["Black"] and h["tees"]["Black"]["card_yards"] == 400
    assert base["holes"]["1"] == E.prepare(_pkg(), "Black")["holes"]["1"]      # the base is not mutated


def test_prepare_adds_missing_set():
    pkg = _pkg()
    pkg["tee_set"] = "osm_back"
    pkg["tee_sets"] = {"osm_back": {}}
    pkg["holes"]["1"]["tees"] = {"osm_back": dict(tee_ll=[LON0, LAT0])}
    b = E.prepare(pkg, "Black")
    assert "Black" in b["tee_sets"] and b["holes"]["1"]["tees"]["Black"]["tee_ll"] == [LON0, LAT0]


def test_configs_cover_every_layer_both_ways():
    names = {n for n, _, _ in E.configs()}
    for L in E.LAYERS:
        assert f"+{L}" in names and f"-{L}" in names
    assert {"auto", "truth"} <= names


PKG = os.path.join(E.CD, "packages", "blue_hills", "package.json")


@pytest.mark.skipif(not os.path.exists(PKG), reason="needs course_data/packages/blue_hills")
def test_real_package_auto_config_reproduces_loader():
    """The auto configuration (zones re-emitted in model order, zone_order given) gives the loader's own lies."""
    import tee_strategy as t
    raw = json.load(open(PKG))
    _, H0 = E.load_models(raw, "Black", "t0")
    base = E.prepare(raw, "Black")
    P = E.PK()
    stacks = {}
    for ref, h in base["holes"].items():
        ent = E.tee_entry(h, "Black", "Black")
        stacks[ref] = E.auto_stack(base, h, P._ll(ent["tee_ll"]))
    _, H = E.load_models(E.apply_layers(base, {}, "Black", set(), stacks), "Black", "t1")
    g = np.mgrid[0:920:9, 0:2000:9].reshape(2, -1).T.astype(float)
    for k in H0:
        assert (t.lie_at(H0[k], g) == t.lie_at(H[k], g)).all()
        assert H0[k]["tee"] == H[k]["tee"] and H0[k]["green"] == H[k]["green"]


def test_renumber_moves_geometry_keeps_card():
    pkg = _pkg()
    h2 = copy.deepcopy(pkg["holes"]["1"])
    h2.update(par=3, yards={"Black": 180}, green_ll=[LON0 + 0.01, LAT0])
    h2["tees"]["Black"].update(tee_ll=[LON0 + 0.009, LAT0], card_yards=180)
    pkg["holes"]["2"] = h2
    base = E.prepare(pkg, "Black")
    # truth: number 1 is the physical hole the build called 2, and the other way round
    truth = {"1": dict(green_ll=[LON0 + 0.01, LAT0]), "2": dict(green_ll=[LON0 + 0.003, LAT0 + 0.003])}
    out, moved = E.renumber(base, truth, "Black")
    assert moved == {"1": "2", "2": "1"}
    assert out["holes"]["1"]["green_ll"] == [LON0 + 0.01, LAT0] and out["holes"]["1"]["par"] == 4
    assert out["holes"]["1"]["tees"]["Black"]["tee_ll"] == [LON0 + 0.009, LAT0]
    assert out["holes"]["1"]["tees"]["Black"]["card_yards"] == 400
    same, moved2 = E.renumber(base, {"1": dict(green_ll=[LON0 + 0.003, LAT0 + 0.003])}, "Black")
    assert moved2 == {} and same["holes"] == base["holes"]


def test_configs_subset_keeps_the_references(monkeypatch):
    """--configs: only the named configurations, plus auto / truth / +routing (the elevation donors)."""
    monkeypatch.setattr(E, "ONLY", {"+tees", "-trees"})
    names = [n for n, _, _ in E.configs()]
    assert sorted(names) == sorted(["auto", "truth", "+routing", "+tees", "-trees"])
    monkeypatch.setattr(E, "ONLY", None)
    assert len(E.configs()) == 2 + 2 * len(E.LAYERS) + len(E.GROUPS)

