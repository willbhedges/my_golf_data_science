"""Unit / smoke tests on a synthetic course (no network): python -m pytest -q course_data/perception"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stack as S  # noqa: E402


def synthetic_course():
    H = W = 600
    st = S.synthetic(H, W)
    a = st.a
    rr, cc = np.indices((H, W))
    # grass everywhere: R 60, G 110, B 50, NIR 170
    a["naip"][:] = np.array([60, 110, 50, 170], np.uint8)[:, None, None]
    a["naip"][1] += ((cc // 2) % 2 * 6).astype(np.uint8)            # faint N-S mowing stripes (vary along x)
    a["hag"][:] = 0
    a["cls"][:] = 2
    z = 1000 + 0 * rr

    def disk(r0, c0, rad):
        return (rr - r0) ** 2 + (cc - c0) ** 2 <= rad * rad
    # hole: tee (row 520) -> fairway (rows 200-480, cols 280-320) -> green (row 150)
    gm = disk(150, 300, 15)
    a["seg"][0][gm] = 230
    z = np.where(gm, z + 60, z)
    fm = (rr > 200) & (rr < 480) & (cc > 275) & (cc < 325)
    a["seg"][2][fm] = 220
    tm = (rr > 515) & (rr < 530) & (cc > 292) & (cc < 308)
    tm2 = (rr > 540) & (rr < 552) & (cc > 294) & (cc < 306)
    a["seg"][1][tm | tm2] = 220
    z = np.where(tm | tm2, z + 50, z)
    bm = disk(170, 330, 6)
    a["seg"][3][bm] = 230
    a["naip"][:, bm] = np.array([200, 190, 160, 190], np.uint8)[:, None]
    # practice green near the clubhouse
    pg = disk(80, 520, 18)
    a["seg"][0][pg] = 230
    # pond (dark NIR)
    wm = disk(330, 120, 30)
    a["naip"][:, wm] = np.array([40, 50, 45, 20], np.uint8)[:, None]
    # clubhouse + parking
    bl = (rr > 40) & (rr < 70) & (cc > 440) & (cc < 490)
    a["hag"][bl] = 24
    a["cls"][bl] = 6
    a["naip"][:, bl] = np.array([120, 120, 120, 110], np.uint8)[:, None]
    pk = (rr > 75) & (rr < 115) & (cc > 430) & (cc < 495)
    a["naip"][:, pk] = np.array([100, 100, 100, 95], np.uint8)[:, None]
    # cart path: from the green (row 150) east then south to the tee of the "next hole" (row 300, col 560)
    path = ((rr >= 149) & (rr <= 151) & (cc > 318) & (cc < 560)) | ((cc >= 559) & (cc <= 561) & (rr > 150) & (rr < 300))
    a["naip"][:, path] = np.array([150, 150, 145, 140], np.uint8)[:, None]
    t2 = (rr > 300) & (rr < 314) & (cc > 553) & (cc < 567)
    a["seg"][1][t2] = 220
    a["dtm"] = np.clip(z, 0, 65534).astype(np.uint16)
    a["inten"][:] = 100

    # labels
    def ring(mask):
        r, c = np.nonzero(mask)
        r0, r1, c0, c1 = r.min(), r.max() + 1, c.min(), c.max() + 1
        xs, ys = st.rc_to_xy(np.array([r0, r0, r1, r1, r0]) - 0.5, np.array([c0, c1, c1, c0, c0]) - 0.5)
        lon, lat = st.xy_to_ll(xs, ys)
        return [[float(x), float(y)] for x, y in zip(lon, lat)]

    def line(rcs):
        r = np.array([p[0] for p in rcs], float)
        c = np.array([p[1] for p in rcs], float)
        lon, lat = st.rc_to_ll(r, c)
        return [[float(x), float(y)] for x, y in zip(lon, lat)]
    F = []

    def poly(tags, mask):
        F.append(dict(type="Feature", properties=tags, geometry=dict(type="Polygon", coordinates=[ring(mask)])))
    poly({"golf": "green"}, gm)
    poly({"golf": "green"}, pg)
    poly({"golf": "tee"}, tm)
    poly({"golf": "tee"}, tm2)
    poly({"golf": "tee"}, t2)
    poly({"golf": "fairway"}, fm)
    poly({"golf": "bunker"}, bm)
    poly({"natural": "water"}, wm)
    poly({"building": "yes", "golf": "clubhouse"}, bl)
    poly({"amenity": "parking"}, pk)
    F.append(dict(type="Feature", properties={"golf": "hole", "ref": "1"}, geometry=dict(type="LineString", coordinates=line([(535, 300), (150, 300)]))))
    F.append(dict(type="Feature", properties={"golf": "hole", "ref": "2"}, geometry=dict(type="LineString", coordinates=line([(307, 560), (580, 560)]))))
    F.append(dict(type="Feature", properties={"golf": "cartpath", "highway": "path"},
                  geometry=dict(type="LineString", coordinates=line([(150, 318), (150, 560), (300, 560)]))))
    st.labels = dict(type="FeatureCollection", features=F)
    st.meta["boundary"] = dict(type="Polygon", coordinates=[ring(np.ones((H, W), bool))])
    st.meta["slug"] = "synthetic"
    return st


def test_stack_roundtrip(tmp_path):
    st = synthetic_course()
    st.save(str(tmp_path))
    st2 = S.load(str(tmp_path))
    assert st2.H == st.H and st2.labels["features"]
    lon, lat = st.rc_to_ll(10, 20)
    r, c = st.ll_to_rc(lon, lat)
    assert abs(float(r) - 10) < 1e-6 and abs(float(c) - 20) < 1e-6


def test_perceive_synthetic(tmp_path):
    import perceive as P
    import scene as SC
    import evaluate as EV
    import truth as TR
    st = synthetic_course()
    L, D = P.run(st, {})
    assert len(D["greens"]) == 2
    assert any(len(c["boxes"]) == 2 for c in D["complexes"]), [len(c["boxes"]) for c in D["complexes"]]
    assert len(D["fairways"]) == 1
    f = D["fairways"][0]
    assert f["length"] > 200 and min(f["axis"], 180 - f["axis"]) < 10          # runs N-S
    assert D["water"], "pond not found"
    assert D["buildings"] and D["clubhouse"] is not None
    sc = SC.build_scene(st, L, D, models_id="test")
    D["relations"] = sc["relations"]["green_to_tee"]
    js = json.dumps(sc)
    assert sc["schema"] == "course_scene/1"
    gj = SC.to_geojson(sc)
    assert any(ft["properties"].get("golf") == "green" for ft in gj["features"])
    TR.Truth.MIN_HOLES = 2
    T = TR.Truth(st)
    assert T.mapped_holes == 2 and T.clubhouse is not None
    kinds = sorted(g["kind"] for g in T.greens)
    assert kinds == ["hole", "practice"], kinds
    ev = EV.evaluate(st, L, D, T)
    assert ev["greens_any"]["recall"] == 1.0
    assert ev["clubhouse"]["error_m"] is not None and ev["clubhouse"]["error_m"] < 30
    assert ev["cart_paths"]["length_recall"] is not None
    P.tables(st, L, D, T, str(tmp_path / "tables"))
    assert os.path.exists(tmp_path / "tables" / "objects.json")
    assert len(js) > 1000


def test_stripes():
    import detect as DT
    g = np.zeros((80, 80), np.float32)
    g[:, ::4] = 10
    g[:, 1::4] = 10                       # stripes running N-S (constant along rows)
    m = np.ones((80, 80), bool)
    s, coh = DT.stripe_orientation(g, m)
    assert s is not None and min(s, 180 - s) < 5 and coh > 0.5


def test_graph_bridge():
    import paths as PT
    st = S.synthetic(120, 120)
    m = np.zeros((120, 120), bool)
    m[60:62, 5:50] = True
    m[60:62, 58:115] = True
    prob = np.where(m, 0.9, 0.3).astype(np.float32)
    G = PT.skeleton_graph(m, prob, st)
    G = PT.bridge_gaps(G, prob, st)
    G = PT.prune(G)
    import networkx as nx
    assert nx.number_connected_components(G) == 1
    assert 100 < PT.graph_length(G) < 120


def test_linear_components_drop_blobs():
    import paths as PT
    m = np.zeros((200, 200), bool)
    m[50:53, 10:150] = True          # a 140 m path
    m[120:160, 120:160] = True       # a 40 x 40 m blob (roof / lot)
    k = PT.linear_components(m)
    assert k[51, 80] and not k[140, 140]


def test_threshold_shift():
    import detect as DT

    class C:
        classes_ = np.array([0, 1])

        def predict_proba(self, X):
            return np.c_[1 - X[:, 0], X[:, 0]]
    pr, cl = DT._apply(C(), [{"a": 0.2}, {"a": 0.1}], ["a"], thr=0.2)
    assert abs(pr[0, 1] - 0.5) < 1e-6 and pr[1, 1] < 0.5
