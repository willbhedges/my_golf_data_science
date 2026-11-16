"""route_scene: when perception runs, the candidate merge (OSM wins), confirm questions."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import route_scene as RS  # noqa: E402


def _f(golf, coords, typ="Polygon", **p):
    return {"type": "Feature", "geometry": {"type": typ, "coordinates": coords}, "properties": dict(golf=golf, **p)}


def _sq(lon, lat, d=0.0002):
    return [[[lon, lat], [lon + d, lat], [lon + d, lat + d], [lon, lat + d], [lon, lat]]]


def test_needs_perception():
    full = {"features": [_f("hole", [[0, 0], [0, 0.003]], "LineString", ref=str(i)) for i in range(1, 10)]}
    assert not RS.needs_perception(full, 9)
    mapped = {"features": [_f("green", _sq(-90 + i * 0.003, 40)) for i in range(9)]
              + [_f("tee", _sq(-90 + i * 0.003, 40.002)) for i in range(9)]}
    assert not RS.needs_perception(mapped, 9)
    assert RS.needs_perception({"features": []}, 18)
    assert RS.needs_perception({"features": mapped["features"][:7]}, 9)


def test_candidates_osm_wins():
    fc = {"features": [_f("green", _sq(-90.0, 40.0)), _f("tee", _sq(-90.0, 40.003))]}
    scene = dict(greens=[dict(id="g1", centroid=[-90.0001, 40.0001], area_m2=400, p=0.9, p_hole=0.9, kind="hole",
                              polygon=_sq(-90.0, 40.0)[0]),
                         dict(id="g2", centroid=[-90.004, 40.0], area_m2=400, p=0.9, p_hole=0.9, kind="hole",
                              polygon=_sq(-90.004, 40.0)[0])],
                 tee_complexes=[dict(id="t1", centroid=[-90.004, 40.003], p=0.8, boxes=[dict(centroid=[-90.004, 40.003])])])
    co, info = RS.candidates(fc, scene, n_holes=2)
    assert info["greens_osm"] == 1 and info["greens_scene"] == 1        # g1 sits on the OSM green: dropped
    assert info["tees_osm"] == 1 and info["tees_scene"] == 1


def test_confirm_questions_order():
    pkg = {"holes": {"1": dict(tee_ll=[0, 0], green_ll=[0, 1], par=4, length=380),
                     "2": dict(tee_ll=[1, 0], green_ll=[1, 1], par=3, length=160),
                     "3": dict(tee_ll=[2, 0], green_ll=[2, 1], par=5, length=520)}}
    q = RS.confirm_questions(pkg, dict(margins=[5.0, 1.0, 9.0], detected_holes=["1", "2"], min_margin=1.0))
    assert [x["hole"] for x in q["questions"]] == ["2", "1"]


def _chain(n=9, drop_tee=None):
    """a synthetic loop of n holes going east then back west: hole i tee -> green 330-420 yd north / south; the next
    tee 30 yd beyond the green. -> (scene, card yards, true (tee, green) lon / lat per hole)"""
    import math
    lat0, lon0 = 40.0, -90.0
    ky, kx = 1 / 111320.0, 1 / (111320.0 * math.cos(math.radians(lat0)))
    yards = [380, 410, 170, 520, 350, 395, 160, 450, 400][:n]
    x, y, holes = 0.0, 0.0, []
    for i, L in enumerate(yards):
        m = L * 0.9144
        d = 1 if i % 2 == 0 else -1
        tee = (x, y)
        green = (x + 40.0, y + d * m)
        holes.append((tee, green))
        x, y = green[0] + 60.0, green[1] + d * 25.0
    ll = lambda p: [lon0 + p[0] * kx, lat0 + p[1] * ky]           # noqa: E731
    sq = lambda p, r: [ll((p[0] + a, p[1] + b)) for a, b in ((-r, -r), (r, -r), (r, r), (-r, r), (-r, -r))]  # noqa: E731
    greens = [dict(id="g%d" % i, centroid=ll(g), area_m2=500, p=0.95, p_hole=0.9, kind="hole", polygon=sq(g, 12))
              for i, (t, g) in enumerate(holes)]
    tees = [dict(id="t%d" % i, centroid=ll(t), p=0.9, boxes=[dict(centroid=ll(t), polygon=sq(t, 5))])
            for i, (t, g) in enumerate(holes) if i != drop_tee]
    fair = [dict(id="f%d" % i, p=0.9, polygon=[ll((t[0] - 15 + 40 * s, t[1] + (g[1] - t[1]) * s)) for s in (0.25, 0.85)]
                 + [ll((t[0] + 15 + 40 * s, t[1] + (g[1] - t[1]) * s)) for s in (0.85, 0.25)])
            for i, (t, g) in enumerate(holes)]
    for f in fair:
        f["polygon"].append(f["polygon"][0])
    sc = dict(greens=greens, tee_complexes=tees, fairways=fair, parking=[], clubhouse={})
    return sc, yards, [(ll(t), ll(g)) for t, g in holes]


def _right(r, truth, tol_m=25.0):
    import math
    ok = 0
    for f in r["features"]:
        i = int(f["properties"]["ref"]) - 1
        t, g = f["geometry"]["coordinates"][0], f["geometry"]["coordinates"][-1]
        dt = math.hypot((t[0] - truth[i][0][0]) * 85000, (t[1] - truth[i][0][1]) * 111320)
        dg = math.hypot((g[0] - truth[i][1][0]) * 85000, (g[1] - truth[i][1][1]) * 111320)
        ok += dt < 45 and dg < tol_m
    return ok


def test_v1_routes_chain_and_places_a_missing_tee():
    sc, yards, truth = _chain(9)
    card = dict(par=[4, 4, 3, 5, 4, 4, 3, 4, 4], tee_sets=dict(Blue=dict(yards=yards)))
    r = RS.route({"features": []}, sc, card, 9, version="v1", params=dict(beam=500))
    assert _right(r, truth) == 9
    sc, yards, truth = _chain(9, drop_tee=4)
    r = RS.route({"features": []}, sc, card, 9, version="v1", params=dict(beam=500))
    assert r["n_vt"] == 1 and _right(r, truth) >= 8
    f5 = [f for f in r["features"] if f["properties"]["ref"] == "5"][0]
    assert f5["properties"]["tee_src"] == "virtual"


def test_gate_hard_blocks():
    import route_gate as RG
    p = dict(w=[5.0] + [0.0] * len(RG.FEATS), threshold=0.5)
    hf = [dict(ref=str(i + 1), margin=9.0, kind=0, card_rel=0.02, ob=0.0, ph=0.8, cross=0) for i in range(9)]
    assert RG.decide(dict(n_holes=9, hole_features=hf, n_miss=0), p)["show"]
    assert not RG.decide(dict(n_holes=9, hole_features=hf[:8], n_miss=1), p)["show"]
    assert not RG.decide(dict(n_holes=9, hole_features=hf, n_miss=0), dict(p, threshold=1.1))["show"]


def test_gate_card_order_conflict():
    import route_gate as RG
    a = dict(tee_sets=dict(B=dict(yards=[400, 175, 340, 260, 515, 335, 460, 165, 455])))
    rot = dict(tee_sets=dict(B=dict(yards=[460, 165, 455, 400, 175, 340, 260, 515, 335])))
    near = dict(tee_sets=dict(W=dict(yards=[390, 170, 330, 250, 505, 330, 450, 160, 445])))
    assert RG.card_order_conflict(a, [a, rot], 9)
    assert not RG.card_order_conflict(a, [a, near], 9)
    hf = [dict(ref=str(i + 1), margin=9.0, kind=0, card_rel=0.02, ob=0.0, ph=0.8, cross=0) for i in range(9)]
    p = dict(w=[5.0] + [0.0] * len(RG.FEATS), threshold=0.5)
    assert not RG.decide(dict(n_holes=9, hole_features=hf, n_miss=0, card_conflict=True), p)["show"]


def _grid_scene():
    return dict(grid=dict(crs="EPSG:32616", transform=[1.0, 0, 332000.0, 0, -1.0, 4483000.0], width=400, height=300),
                greens=[])


def test_augment_scene_adds_map_greens():
    import numpy as np
    import route_learn as RL
    sc = _grid_scene()
    P = np.zeros((6, 300, 400), np.uint8)
    P[1, 100:120, 100:125] = 230                   # a 500 m2 green blob
    P[1, 10:13, 10:13] = 255                       # too small
    s2, n = RL.augment_scene(sc, P)
    assert n == 1 and s2["greens"][0]["kind"] == "map" and 450 <= s2["greens"][0]["area_m2"] <= 520
    s3, n3 = RL.augment_scene(s2 | dict(greens=[dict(s2["greens"][0], kind="hole", p_hole=0.9)]), P)
    assert n3 == 0                                 # already a candidate there


def test_maps_sampling_follows_the_grid():
    import numpy as np
    import route_learn as RL
    from routing import Proj
    from pyproj import Transformer
    sc = _grid_scene()
    P = np.zeros((6, 300, 400), np.uint8)
    P[3, :, 200:] = 255                            # fairway on the east half
    M = RL.corridor_maps(P, sc["grid"])
    lon, lat = Transformer.from_crs("EPSG:32616", "EPSG:4326", always_xy=True).transform(332200.0, 4482850.0)
    M.bind(Proj(lon, lat))
    v = M.sample(np.array([[-40.0, 0.0], [40.0, 0.0]]), "fair")
    assert v[0] < 0.1 and v[1] > 0.9


def test_route_v2_smoke():
    """v2 on the synthetic chain with flat maps: routes every hole (learned scores when the model file exists)"""
    import numpy as np
    from pyproj import Transformer
    sc, yards, truth = _chain(9)
    tr = Transformer.from_crs("EPSG:4326", "EPSG:32616", always_xy=True)
    xs, ys = tr.transform([p[0] for t in truth for p in t], [p[1] for t in truth for p in t])
    x0, y1 = int(min(xs)) - 300, int(max(ys)) + 300
    W, H = int(max(xs)) + 300 - x0, y1 - (int(min(ys)) - 300)
    sc["grid"] = dict(crs="EPSG:32616", transform=[1.0, 0, float(x0), 0, -1.0, float(y1)], width=W, height=H)
    P = np.zeros((6, H, W), np.uint8)
    card = dict(par=[4, 4, 3, 5, 4, 4, 3, 4, 4], tee_sets=dict(Blue=dict(yards=yards)))
    r, ci, s2 = RS.route_v2({"features": []}, sc, card, 9, P, params=dict(beam=500))
    assert len(r["features"]) == 9 and ci["greens_map"] == 0
    assert all(h.get("pw") is None or 0 <= h["pw"] <= 1 for h in r["hole_features"])
