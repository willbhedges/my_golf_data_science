"""Assemble detector outputs (grid metres) into course_scene/1 (SCENE_SCHEMA.md): scene.json + scene.geojson."""
from __future__ import annotations

import math
import time

import numpy as np

import geo

SCHEMA = "course_scene/1"


def _ring_ll(st, ring):
    if ring is None or len(ring) < 3:
        return None
    return geo.xy_to_ll_list(st, np.asarray(ring, float))


def _r(x, nd=2):
    if x is None:
        return None
    try:
        if not np.isfinite(x):
            return None
    except TypeError:
        return x
    return round(float(x), nd)


def node_near(G, greens, complexes, bld, parks):
    """For every graph node, the element within reach: green (<= 30 m of its edge), tee complex (25 m),
    building (25 m), parking (25 m)."""
    def nearest(p, objs, reach, radius=lambda o: 0.0):
        best, bd = None, 1e18
        for o in objs:
            d = math.hypot(o["xy"][0] - p[0], o["xy"][1] - p[1]) - radius(o)
            if d < bd:
                best, bd = o, d
        return best["id"] if best is not None and bd <= reach else None
    gr = lambda o: math.sqrt(o["area"] / math.pi)          # noqa: E731
    cr = lambda o: max(o.get("length", 0) / 2, math.sqrt(o["area"] / math.pi))  # noqa: E731
    br = lambda o: math.sqrt(o["area"] / math.pi)           # noqa: E731
    for n in G.nodes:
        p = (G.nodes[n]["x"], G.nodes[n]["y"])
        G.nodes[n]["near"] = dict(green=nearest(p, greens, 30, gr), tee=nearest(p, complexes, 25, cr),
                                  building=nearest(p, bld, 25, br), parking=nearest(p, parks, 25, br))


EDGE_FEATURES = ("dist_m", "path_m", "path_ratio", "path_direct", "aims_at_green", "tee_p", "rank_dist", "rank_path",
                 "n_cands", "axis_off", "tee_length", "green_p_hole", "tee_elev_drop")


def edge_features(rel, greens, complexes):
    """Feature rows for the learned green -> next-tee model, one per relation (same order)."""
    gi = {g["id"]: g for g in greens}
    ci = {c["id"]: c for c in complexes}
    by = {}
    for r in rel:
        by.setdefault(r["green"], []).append(r)
    rows = []
    for r in rel:
        g, c = gi[r["green"]], ci[r["tee"]]
        cs = by[r["green"]]
        dists = sorted(x["dist_m"] for x in cs)
        paths = sorted(x["path_m"] for x in cs if x["path_m"] is not None)
        off = None
        if c.get("axis") is not None and c.get("elong", 1) >= 1.3:
            off = geo.angle_diff(c["axis"], geo.bearing(g["xy"], c["xy"]) % 180)
        ge, te = g.get("elev"), c.get("elev")
        rows.append(dict(dist_m=r["dist_m"], path_m=r["path_m"],
                         path_ratio=(r["path_m"] / max(r["dist_m"], 1.0)) if r["path_m"] is not None else None,
                         path_direct=None if r["path_direct"] is None else float(r["path_direct"]),
                         aims_at_green=float(r.get("aims_at_green", False)), tee_p=c.get("p"),
                         rank_dist=float(dists.index(r["dist_m"])),
                         rank_path=float(paths.index(r["path_m"])) if r["path_m"] is not None else None,
                         n_cands=float(len(cs)), axis_off=off, tee_length=c.get("length"),
                         green_p_hole=g.get("p_hole"),
                         tee_elev_drop=(ge - te) if ge is not None and te is not None else None))
    return rows


def apply_edge_model(rel, greens, complexes, md):
    """Replace the rule p_next by the learned model, normalised over each green's candidates."""
    if not rel or not md:
        return rel
    import detect as DT
    rows = edge_features(rel, greens, complexes)
    pr, cl = DT._apply(md["clf"], rows, md["features"])
    p = pr[:, cl.index(1)]
    tot = {}
    for r, v in zip(rel, p):
        tot[r["green"]] = tot.get(r["green"], 0.0) + float(v)
    for r, v in zip(rel, p):
        r["p_edge"] = round(float(v), 3)
        r["p_next"] = round(float(v) / max(tot[r["green"]], 1e-9), 3)
    return rel


def green_to_tee(G, greens, complexes, max_m=450.0, attach_m=45.0):
    """Ordering evidence: every (green, tee complex) pair within max_m, with the cart-path route between them."""
    import networkx as nx
    ids = list(G.nodes) if G is not None else []
    P = np.array([(G.nodes[n]["x"], G.nodes[n]["y"]) for n in ids]) if ids else np.zeros((0, 2))

    def attach(xy, radius):
        if not len(P):
            return []
        d = np.hypot(*(P - np.array(xy)).T) - radius
        order = np.argsort(d)[:4]
        return [(ids[i], max(float(d[i]), 0.0)) for i in order if d[i] <= attach_m]
    rel = []
    near_tee_nodes = {n for n in ids if G.nodes[n].get("near", {}).get("tee")}
    near_green_nodes = {n for n in ids if G.nodes[n].get("near", {}).get("green")}
    for g in greens:
        if g.get("p", 0) < 0.3:
            continue
        gr = math.sqrt(g["area"] / math.pi)
        src = attach(g["xy"], gr)
        dist_from = {}
        paths_from = {}
        for n0, d0 in src:
            dd, pp = nx.single_source_dijkstra(G, n0, cutoff=1500, weight="length")
            for k, v in dd.items():
                if v + d0 < dist_from.get(k, (1e18,))[0]:
                    dist_from[k] = (v + d0, n0)
                    paths_from[k] = pp[k]
        cands = []
        for c in complexes:
            if c.get("p", 0) < 0.3:
                continue
            d = math.hypot(c["xy"][0] - g["xy"][0], c["xy"][1] - g["xy"][1])
            if d > max_m:
                continue
            path_m, edges, direct = None, [], None
            best = None
            for n1, d1 in attach(c["xy"], max(c.get("length", 0) / 2, 5)):
                if n1 in dist_from:
                    v = dist_from[n1][0] + d1
                    if best is None or v < best[0]:
                        best = (v, n1)
            if best is not None:
                path_m = best[0]
                nodes = paths_from[best[1]]
                edges = [G.edges[a, b].get("eid") for a, b in zip(nodes[:-1], nodes[1:])]
                mid = nodes[1:-1]
                direct = not any((n in near_green_nodes and G.nodes[n]["near"]["green"] != g["id"]) or
                                 (n in near_tee_nodes and G.nodes[n]["near"]["tee"] != c["id"]) for n in mid)
            own = False                       # the tee whose line of play points at this green is its OWN hole's tee
            if c.get("axis") is not None and c.get("elong", 1) >= 1.3 and d > 90:
                own = geo.angle_diff(c["axis"], geo.bearing(c["xy"], g["xy"]) % 180) < 12
            cands.append(dict(green=g["id"], tee=c["id"], dist_m=round(d, 1),
                              path_m=_r(path_m, 1), path_edges=[e for e in edges if e], path_direct=direct,
                              aims_at_green=bool(own), _p=c.get("p", 0.5)))
        # p_next: a soft prior over this green's candidates (short walk, direct cart path)
        if cands:
            s = []
            for r in cands:
                walk = r["path_m"] if r["path_m"] is not None else 1.5 * r["dist_m"] + 60
                sc = -((max(walk - 40, 0)) / 110.0) ** 2 + (0.6 if r["path_direct"] else 0.0)
                sc -= 2.0 if r["dist_m"] < 25 else 0.0
                sc -= 1.5 if r["aims_at_green"] else 0.0
                sc += 1.0 * (r["_p"] - 0.5)
                s.append(sc)
            s = np.array(s)
            e = np.exp(s - s.max())
            for r, pv in zip(cands, e / e.sum()):
                r["p_next"] = round(float(pv), 3)
                r.pop("_p", None)
        rel += cands
    return rel


def build_scene(st, L, D, mode="blind", models_id=None, models=None):
    """D: dict of detector outputs (perceive.run)."""
    G = D["graph"]
    greens, complexes = D["greens"], D["complexes"]
    # ids on graph
    nid = {}
    for k, n in enumerate(sorted(G.nodes)):
        nid[n] = f"n{k + 1}"
    for k, (u, v) in enumerate(G.edges):
        G.edges[u, v]["eid"] = f"e{k + 1}"
    node_near(G, greens, complexes, D["buildings"], D["parking"])
    rel = green_to_tee(G, greens, complexes)
    rel = apply_edge_model(rel, greens, complexes, (models or {}).get("edge"))

    def poly_obj(o, extra=None):
        d = dict(id=o["id"], p=_r(o.get("p", 0.5), 3), centroid=geo.pt_ll(st, *o["xy"]), area_m2=_r(o["area"], 1),
                 polygon=_ring_ll(st, o.get("ring")))
        if extra:
            d.update(extra)
        return d

    gl = []
    for g in greens:
        ring = g.get("ring")
        collar = None
        if ring is not None and len(ring) >= 3:
            from shapely.geometry import Polygon
            try:
                cp = Polygon(ring).buffer(2.0).simplify(0.5)
                collar = _ring_ll(st, list(cp.exterior.coords))
            except Exception:                                    # noqa: BLE001
                collar = None
        gl.append(poly_obj(g, dict(kind=g["kind"], p_hole=_r(g["p_hole"], 3), p_practice=_r(g["p_practice"], 3),
                                   collar_polygon=collar, elev_m=_r(g.get("elev")), raised_m=_r(g.get("raised")),
                                   slope_pct=_r(g["feat"].get("slope")), tees_in_range=g.get("tees_in_range"),
                                   dist_clubhouse_m=_r(g.get("d_clubhouse"), 1),
                                   src=["segment"] + (["lidar_dtm"] if g.get("raised") is not None else []))))
    tl = []
    for c in complexes:
        hull = None
        pts = np.vstack([np.asarray(b["ring"], float) for b in c["boxes"] if b.get("ring") is not None] or [np.array([c["xy"]])])
        if len(pts) >= 3:
            from shapely.geometry import MultiPoint
            h = MultiPoint([tuple(p) for p in pts]).convex_hull
            if h.geom_type == "Polygon":
                hull = _ring_ll(st, list(h.exterior.coords))
        tl.append(dict(id=c["id"], p=_r(c["p"], 3), p_range_tee=_r(c.get("p_range_tee", 0.0), 3),
                       centroid=geo.pt_ll(st, *c["xy"]), polygon=hull, axis_deg=_r(c["axis"], 1) if c["elong"] >= 1.3 else None,
                       length_m=_r(c["length"], 1), elev_m=_r(c.get("elev")), src=c["src"],
                       boxes=[dict(id=b["cid"], p=_r(b["p"], 3), centroid=geo.pt_ll(st, *b["xy"]), area_m2=_r(b["area"], 1),
                                   polygon=_ring_ll(st, b.get("ring")), src=b["src"]) for b in c["boxes"]]))
    fl = []
    for f in D["fairways"]:
        cl = f["centerline"]
        fl.append(poly_obj(f, dict(centerline=geo.xy_to_ll_list(st, cl) if len(cl) else [], length_m=_r(f["length"], 1),
                                   width_m=_r(f["width"], 1), axis_deg=_r(f["axis"], 1),
                                   ends=[geo.pt_ll(st, *cl[0]), geo.pt_ll(st, *cl[-1])] if len(cl) else [],
                                   stripe_deg=_r(f["stripe"], 1) if f["stripe_strength"] >= 0.05 else None,
                                   stripe_strength=_r(f["stripe_strength"], 3), src=["segment"])))
    bl = [poly_obj(b, dict(src=["segment"])) for b in D["bunkers"]]
    wl = [poly_obj(w, dict(kind=w["kind"], src=["naip_nir_water"])) for w in D["water"]]
    trl = []
    for t in D["trees"]:
        d = dict(id=t["id"], p=_r(t["p"], 2), centroid=geo.pt_ll(st, *t["xy"]), area_m2=_r(t["area"], 1),
                 height_m=_r(t.get("height"), 1), kind=t["kind"])
        if t["kind"] == "stand":
            d["polygon"] = _ring_ll(st, t.get("ring"))
        trl.append(d)
    nodes = []
    for n in sorted(G.nodes):
        deg = G.degree(n)
        nodes.append(dict(id=nid[n], ll=geo.pt_ll(st, G.nodes[n]["x"], G.nodes[n]["y"]), degree=deg,
                          kind="end" if deg == 1 else ("junction" if deg >= 3 else "bend"), near=G.nodes[n]["near"]))
    import paths as PT
    edges = []
    for u, v, d in G.edges(data=True):
        pts = PT.simplify(d["pts"], 1.0)
        edges.append(dict(id=d["eid"], u=nid[u], v=nid[v], length_m=_r(d["length"], 1), line=geo.xy_to_ll_list(st, pts),
                          p=_r(d["p"], 3), width_m=_r(d.get("width"), 1), surface="unknown", bridge=bool(d.get("bridge"))))
    import networkx as nx
    cart = dict(nodes=nodes, edges=edges, total_km=round(PT.graph_length(G) / 1000, 3),
                components=nx.number_connected_components(G) if G.number_of_nodes() else 0)
    bld = [poly_obj(b, dict(height_m=_r(b.get("height"), 1), src=["lidar_class", "lidar_hag"])) for b in D["buildings"]]
    pk = [poly_obj(p, dict(n_stall_lines=0, src=["naip_ndvi", "lidar_hag"])) for p in D["parking"] if p["p"] >= 0.3]
    ch = D.get("clubhouse")
    chd = None
    if ch:
        chd = dict(ll=geo.pt_ll(st, *ch["xy"]), building=ch.get("building"), p=_r(ch["p"], 3), radius_m=D.get("ch_radius", 120),
                   evidence=dict(ch.get("evidence") or {}, how=ch.get("how")))
    rng = D.get("range")
    rngd = None
    if rng:
        rngd = dict(polygon=_ring_ll(st, rng["ring"]), centroid=geo.pt_ll(st, *rng["xy"]), axis_deg=_r(rng["axis"], 1),
                    hitting_end=geo.pt_ll(st, *rng["hitting_end"]), length_m=_r(rng["length"], 1),
                    width_m=_r(rng["width"], 1), p=_r(rng["p"], 3), tee_complex=rng.get("complex"),
                    fairway=rng.get("fairway"))
    g = st.meta["grid"]
    naip_years = ((st.meta.get("naip") or {}).get("years") or [{}])
    scene = dict(
        schema=SCHEMA, slug=st.meta.get("slug"), name=(st.meta.get("course") or {}).get("name") or st.meta.get("name"),
        built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), mode=mode,
        bbox_wsen=[round(v, 6) for v in g.get("ll_bbox_wsen", [])],
        grid=dict(crs=g["crs"], res_m=g["res_m"], width=st.W, height=st.H, transform=g["transform"][:6]),
        sources=dict(naip=dict(year=naip_years[0].get("year"), acquired=naip_years[0].get("acquired"), res_m=0.6),
                     lidar=dict(hag=bool(L["lidar"]), classification=bool((st.cls() > 0).mean() > 0.5),
                                intensity=bool((st.a["inten"] > 0).mean() > 0.5), dtm=bool(np.isfinite(L["dtm"]).mean() > 0.5)),
                     models=dict(segment=(st.meta.get("segment") or {}).get("sha"), perception=models_id)),
        coverage={k: round(float(v), 3) for k, v in (st.meta.get("coverage") or {}).items()},
        greens=gl, tee_complexes=tl, fairways=fl, bunkers=bl, water=wl, trees=trl, cart_paths=cart,
        buildings=bld, parking=pk, clubhouse=chd,
        practice=dict(putting_greens=[x["id"] for x in gl if x["kind"] == "practice"], driving_range=rngd),
        relations=dict(green_to_tee=rel),
        summary=dict(greens_hole=sum(x["kind"] == "hole" for x in gl), greens_practice=sum(x["kind"] == "practice" for x in gl),
                     greens_uncertain=sum(x["kind"] == "uncertain" for x in gl),
                     tee_complexes=sum((x["p"] or 0) >= 0.5 for x in tl), fairways=len(fl), bunkers=len(bl), water=len(wl),
                     tree_stands=sum(t["kind"] == "stand" for t in trl), trees=sum(t["kind"] == "tree" for t in trl),
                     cart_path_km=cart["total_km"], cart_path_components=cart["components"], buildings=len(bld),
                     parking=len(pk), clubhouse=bool(chd), driving_range=bool(rngd)),
        warnings=D.get("warnings", []))
    return scene


def to_geojson(scene):
    """scene -> FeatureCollection with OSM-style tags (routing.inputs_from_fc reads it)."""
    src = f"perception:{(scene.get('sources') or {}).get('models', {}).get('perception')}"
    feats = []

    def poly(o, cls, tags):
        if o.get("polygon"):
            geom = dict(type="Polygon", coordinates=[o["polygon"]])
        else:
            geom = dict(type="Point", coordinates=o["centroid"])
        props = dict({"class": cls, "id": o["id"], "p": o.get("p"), "src": src}, **tags)
        feats.append(dict(type="Feature", geometry=geom, properties=props))
    for g in scene["greens"]:
        poly(g, "green", {"golf": "green", "kind": g["kind"], "p_hole": g["p_hole"], "p_practice": g["p_practice"]})
    for t in scene["tee_complexes"]:
        for b in t["boxes"]:
            poly(b, "tee_box", {"golf": "tee", "complex": t["id"]})
        poly(t, "tee_complex", {"axis_deg": t["axis_deg"], "length_m": t["length_m"]})
    for f in scene["fairways"]:
        poly(f, "fairway", {"golf": "fairway"})
        if f["centerline"]:
            feats.append(dict(type="Feature", geometry=dict(type="LineString", coordinates=f["centerline"]),
                              properties={"class": "fairway_centerline", "id": f["id"], "p": f["p"], "src": src,
                                          "stripe_deg": f["stripe_deg"]}))
    for b in scene["bunkers"]:
        poly(b, "bunker", {"golf": "bunker"})
    for w in scene["water"]:
        poly(w, "water", {"golf": "water_hazard", "natural": "water"})
    for t in scene["trees"]:
        poly(t, "trees", {"natural": "wood" if t["kind"] == "stand" else "tree", "height_m": t.get("height_m")})
    for e in scene["cart_paths"]["edges"]:
        feats.append(dict(type="Feature", geometry=dict(type="LineString", coordinates=e["line"]),
                          properties={"class": "cart_path", "id": e["id"], "p": e["p"], "src": src, "golf": "cartpath",
                                      "highway": "path", "u": e["u"], "v": e["v"], "length_m": e["length_m"]}))
    for n in scene["cart_paths"]["nodes"]:
        if n["kind"] != "bend":
            feats.append(dict(type="Feature", geometry=dict(type="Point", coordinates=n["ll"]),
                              properties={"class": "cart_path_node", "id": n["id"], "kind": n["kind"], "degree": n["degree"],
                                          "src": src}))
    for b in scene["buildings"]:
        poly(b, "building", {"building": "yes"})
    for p in scene["parking"]:
        poly(p, "parking", {"amenity": "parking"})
    ch = scene.get("clubhouse")
    if ch:
        feats.append(dict(type="Feature", geometry=dict(type="Point", coordinates=ch["ll"]),
                          properties={"class": "clubhouse", "id": "clubhouse", "p": ch["p"], "src": src, "golf": "clubhouse",
                                      "building": "clubhouse", "name": "clubhouse (perceived)"}))
    r = scene["practice"].get("driving_range")
    if r:
        feats.append(dict(type="Feature", geometry=dict(type="Polygon", coordinates=[r["polygon"]]),
                          properties={"class": "driving_range", "id": "range", "p": r["p"], "src": src, "golf": "driving_range"}))
    return dict(type="FeatureCollection", features=feats, properties=dict(schema=scene["schema"], slug=scene["slug"],
                                                                          mode=scene["mode"]))
