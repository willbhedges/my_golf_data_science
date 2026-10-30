"""Stage selector for platform/package.py: pick the best available hole-inference method from the data that exists.

    import stage_select as SS
    prof = SS.profile(fc, card, scene)                          # what data exists (OSM richness, card, scene)
    res, info = SS.infer_holes(fc, card, course, seg=..., pads=..., scene=...)   # holes 1..N + which method ran
    # res: routing.route-compatible {"holes": {ref: {tee_ll, green_ll, status, flags, p_hole, ...}}, ...}
    # info: {"tier", "method", "tried": [...], "fallbacks": [...], "profile": {...}}

Methods (each falls back to the next on any error or an empty result):
  v2+structure  routing v2 (platform/routing_v2.py) with the card-free structure solver's exact marginals
                P(green m is hole k) as a unary prior (routing_v2 `struct_prior`, strength lam per tier).
                Structure runs on the OSM scene when OSM has greens / tees, else on the perception scene
                (course_scene/1, course_data/perception/scenes/<slug>/) when one exists.
  v2            routing v2 alone (the previous default with a card)
  structure     the structure solver's MAP route alone (course_data/structure/structure.py)
  geometry      no routing: geometry/build_holes.infer_holes (the previous default without a card)
  sequence_v3   card tiers only: formation-v2 pair probabilities (zero_tap/formation/hole_pairs.py, hole_pairs/1)
                as the formation, then the zero-tap sequence solver v3 (zero_tap/sequence/solve.py: route CRF +
                card geometry, PAIRS_FORM_W 3, CARD_W 2, nesting on: zero_tap/sequence/results/v3/bench_d.md).
                OSM scene when mapped, else the perception scene. Its confirm session is the tier's v2+structure.

Tiers (from the data, `tier()`):
  mapped_card     OSM greens and tee boxes for >= 80 % of the holes, and a card (web, file, or typed)
  unmapped_card   OSM lacks greens / tees, card: router inputs = segment model + lidar pads; the perception
                  scene feeds the structure prior (as router candidates it hurt on train; option kept)
  mapped_nocard   OSM greens / tees, no card
  unmapped_nocard neither

SELECT below is the per-tier choice, made on the generalize TRAIN split only (pipeline_eval.py select); the test
split is reported once (pipeline_eval.py final -> PIPELINE.md).
"""
from __future__ import annotations

import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
STRUCT = os.path.join(CD, "structure")
PERC = os.path.join(CD, "perception")
for _p in (HERE, STRUCT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import routing as R  # noqa: E402
import routing_v2 as R2  # noqa: E402

RICH = 0.8                        # OSM greens AND tee features for >= 80 % of the holes -> "mapped"
SCENE_MIN_GREEN, SCENE_MIN_COMPLEX = 0.5, 0.4

# per tier: (method, structure-prior strength lam, use perception candidates). Chosen on the train split
# (pipeline_eval.py select, PIPELINE.md "Selection"); the first entry is tried first, then the fallbacks.
# Train split (51 courses, pipeline_select.json), hole-number accuracy of the pick vs the previous default:
#   mapped_card      v2 + structure prior lam 0.5     0.836 vs 0.825 (all 18 right 15.7 vs 9.8 %)
#   unmapped_card    v2 + structure(perception) 0.25  0.733 vs 0.689 (perception greens/tees as extra router
#                    candidates hurt: 0.46-0.62, so they only feed the structure prior)
#   mapped_nocard    structure alone                  0.219 vs 0.099 (geometry); best v2 session: lam 1.0 (0.200)
#   unmapped_nocard  structure on the perception scene 0.140 vs 0.0; best v2 session: v2 alone (0.081)
# "confirm": the routing v2 session behind golf_confirm/1 when the method itself has none (structure alone).
SELECT = {
    "mapped_card": dict(method="v2+structure", lam=0.5, perception=False),
    "unmapped_card": dict(method="v2+structure", lam=0.25, perception=False),
    "mapped_nocard": dict(method="structure", confirm=dict(method="v2+structure", lam=1.0)),
    "unmapped_nocard": dict(method="structure", confirm=dict(method="v2")),
}
# sequence_v3 (formation-v2 pairs + sequence solver v3) for the card tiers: PIPELINE.md section 8. It becomes the
# default only if the held-out test (pipeline_eval.py v3) and the gate courses improve or tie; otherwise SELECT
# stays as above and SELECT_V3 is opt-in (request "hole_method": "sequence_v3").
SELECT_V3 = {
    "mapped_card": dict(method="sequence_v3", confirm=dict(method="v2+structure", lam=0.5)),
    "unmapped_card": dict(method="sequence_v3", confirm=dict(method="v2+structure", lam=0.25)),
}
V3 = dict(form_w=3.0, card_w=2.0, nest=True)       # zero_tap_seqv3.yml variant c2 (chosen on dev)
USE_V3 = False                                      # True: SELECT_V3 overrides SELECT for the card tiers
FALLBACK = {"sequence_v3": ["v2+structure", "v2", "structure", "geometry"],
            "v2+structure": ["v2", "structure", "geometry"], "v2": ["structure", "geometry"],
            "structure": ["v2", "geometry"], "geometry": []}


# ----------------------------------------------------------------------------- data profile
def osm_counts(fc):
    n = dict(greens=0, tees=0, fairways=0, hole_refs=set())
    for f in (fc or {}).get("features", []):
        p = f.get("properties", {})
        if p.get("inside_course") is False:
            continue
        g = p.get("golf")
        if g == "green":
            n["greens"] += 1
        elif g == "tee":
            n["tees"] += 1
        elif g == "fairway":
            n["fairways"] += 1
        elif g == "hole" and (f.get("geometry") or {}).get("type") == "LineString" and str(p.get("ref", "")).isdigit():
            n["hole_refs"].add(str(int(p["ref"])))
    return n


def profile(fc, card=None, scene=None):
    """What data exists: OSM greens / tees / fairways / hole ways vs the hole count, card, perception scene."""
    c = osm_counts(fc)
    n_card = R.card_holes(card)[0] if card else None
    n = n_card or (18 if c["greens"] >= 13 or len(c["hole_refs"]) > 9 else 9)
    mapped = c["greens"] >= RICH * n and c["tees"] >= RICH * n
    return dict(n_holes=n, n_from="card" if n_card else "guess", card=bool(card), osm_greens=c["greens"],
                osm_tees=c["tees"], osm_fairways=c["fairways"], osm_hole_ways=len(c["hole_refs"]),
                osm_holes_complete=all(str(i) in c["hole_refs"] for i in range(1, n + 1)),
                osm_mapped=bool(mapped), scene=bool(scene))


def tier(prof):
    return ("mapped" if prof["osm_mapped"] else "unmapped") + ("_card" if prof["card"] else "_nocard")


def load_scene(slug):
    """The perception agent's blind course_scene/1 for this slug, or None (read-only)."""
    for name in ("scene.json.gz", "scene.json"):
        p = os.path.join(PERC, "scenes", slug or "", name)
        if slug and os.path.exists(p):
            try:
                with (gzip.open(p, "rt") if p.endswith(".gz") else open(p)) as fh:
                    return json.load(fh)
            except (OSError, ValueError):
                return None
    return None


# ----------------------------------------------------------------------------- structure solver
def struct_card(card):
    """Any card shape routing accepts -> the structure solver's {par, yards} (longest set per hole)."""
    if not card:
        return None
    n, pars, yards = R.card_holes(card)
    if not n:
        return None
    ys = [max(r) if r else None for r in yards]
    out = dict(par=pars if any(p for p in pars) else None)
    if all(ys):
        out["yards"] = ys
    return out if (out.get("par") or out.get("yards")) else None


_CACHE = {}


def clear_cache():
    _CACHE.clear()


def structure_solve(fc=None, course=None, card=None, scene=None, n_holes=None):
    """-> (course_structure/1 contract, prior {greens_ll, P (M, N)} for routing_v2 struct_prior, or None).
    scene (course_scene/1) wins over fc when given. Memoised per input objects (clear_cache() between courses)."""
    key = (id(fc), id(course), id(card), id(scene), n_holes)
    if key not in _CACHE:
        _CACHE[key] = _structure_solve(fc, course, card, scene, n_holes)
    return _CACHE[key]


def _structure_solve(fc=None, course=None, card=None, scene=None, n_holes=None):
    import scene as S
    import solver as V
    import structure as ST
    if scene is not None:
        sc = S.scene_from_perception(scene)
        src = "perception"
    else:
        sc = S.scene_from_osm(fc, (course or {}).get("boundary"))
        src = "osm"
    res = V.solve(sc, card=struct_card(card), n_holes=n_holes, return_debug=True)
    dbg = res.pop("debug", None)
    con = ST.contract(res, sc, src)
    prior = None
    if dbg is not None and res.get("status") == "ok":
        gid = [sc.greens[g] for g in dbg["keep"]]
        prior = dict(greens_ll=[list(sc.proj.ll(g["c"])) for g in gid], P=np.asarray(dbg["marg_oriented"], float).tolist(),
                     n=int(res["n_holes"]), src=src)
    return con, prior


def structure_as_routing(con):
    """course_structure/1 -> routing-compatible result (holes[ref]: tee_ll, green_ll, status, flags, p_hole)."""
    holes = {}
    for ref, h in (con.get("holes") or {}).items():
        holes[ref] = dict(ref=ref, par=h.get("par"), tee_ll=list(h["tee_ll"]), green_ll=list(h["green_ll"]),
                          straight_yd=h.get("length_yd"), p_hole=h.get("confidence"), p_green=h.get("p_number"),
                          status=h.get("status"), flags=list(h.get("flags") or []), tee_src=con.get("input"),
                          green_src=con.get("input"))
    return dict(method="structure/1", status=con.get("status"), n_holes=con.get("n_holes"), holes=holes,
                n_check=sum(h["status"] != "ok" for h in holes.values()))


# ----------------------------------------------------------------------------- router inputs
def _perception_scene_mod():
    """perception/scene.py under its own module name (structure/ also has a scene.py)."""
    if "perception_scene" in sys.modules:
        return sys.modules["perception_scene"]
    import importlib.util
    if PERC not in sys.path:
        sys.path.append(PERC)                   # for its `import geo`; appended so structure's scene.py wins
    spec = importlib.util.spec_from_file_location("perception_scene", os.path.join(PERC, "scene.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["perception_scene"] = mod
    spec.loader.exec_module(mod)
    return mod


def perception_candidates(scene, min_box=0.3):
    """Scene -> (facility fc: clubhouse / buildings / parking, segment-style fc of greens / tee boxes / fairways):
    perceived elements enter the router as model detections, like the segment model's (as
    perception/route_check.segment_style)."""
    feats = []

    def geom(o):
        return dict(type="Polygon", coordinates=[o["polygon"]]) if o.get("polygon") else \
            dict(type="Point", coordinates=o["centroid"])
    for g in scene.get("greens", []):
        if g.get("kind") != "practice":
            feats.append(dict(type="Feature", geometry=geom(g), properties={
                "class": "green", "area_m2": g.get("area_m2") or 400,
                "p": (g.get("p_hole") or 0) + 0.1 * (g.get("kind") == "hole")}))
    for t in scene.get("tee_complexes", []):
        for b in t.get("boxes", []):
            p = max(b.get("p") or 0, t.get("p") or 0)
            if p >= min_box:
                feats.append(dict(type="Feature", geometry=geom(b), properties={
                    "class": "tee", "p": max(p, 0.5), "area_m2": max(b.get("area_m2") or 0, 60)}))
    for f in scene.get("fairways", []):
        if f.get("polygon"):
            feats.append(dict(type="Feature", geometry=geom(f), properties={"class": "fairway", "p": 1.0}))
    fc = _perception_scene_mod().to_geojson(scene)
    fac = dict(fc, features=[f for f in fc["features"] if f["properties"].get("class") in ("clubhouse", "building", "parking")])
    return fac, dict(type="FeatureCollection", features=feats)


def merge_fc(*fcs):
    return dict(type="FeatureCollection", features=[f for fc in fcs if fc for f in fc.get("features", [])])


def router_inputs(fc, course, seg=None, pads=None, scene=None, mapped=True, use_perception=False, hide_holes=False):
    """routing.inputs_from_fc for the tier: OSM features when mapped; segment model + lidar pads always; the
    perception scene's greens / tees / fairways as model-style candidates when asked (unmapped tiers)."""
    boundary = (course or {}).get("boundary")
    fac = None
    if use_perception and scene is not None:
        fac, pseg = perception_candidates(scene)
        seg = merge_fc(seg, pseg)
    fc_in = fc if (fac is None or mapped) else merge_fc(fc, fac)
    return R.inputs_from_fc(fc_in, segment=seg, pads=pads or [], boundary=boundary, hide_holes=hide_holes,
                            osm_features=mapped)


def geometry_holes(fc):
    """The previous no-card default: geometry/build_holes.infer_holes (green -> best tee group by fairway cover),
    numbered in OSM green order. -> routing-compatible result."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("cdp_build_holes_ss", os.path.join(CD, "geometry", "build_holes.py"))
    bh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bh)
    fc2 = dict(fc, features=[f for f in fc.get("features", []) if f["properties"].get("golf") != "hole"])
    world = bh.World(fc2)
    holes = {}
    for h in bh.infer_holes(world):
        line = np.asarray(h["line"], float) * bh.YD
        lon, lat = world.inv.transform(line[:, 0], line[:, 1])
        ref = h["props"]["ref"]
        holes[ref] = dict(ref=ref, par=int(h["props"]["par"]), tee_ll=[float(lon[0]), float(lat[0])],
                          green_ll=[float(lon[-1]), float(lat[-1])], status="check", flags=["inferred geometry"],
                          p_hole=None, straight_yd=round(float(np.hypot(*(line[-1] - line[0]))) / bh.YD, 1))
    return dict(method="geometry/infer_holes", status="ok" if holes else "empty", n_holes=len(holes), holes=holes)


# ----------------------------------------------------------------------------- sequence v3 (zero-tap)
ZT = os.path.join(CD, "zero_tap")


def scorecard1(card):
    """Any card shape routing accepts -> scorecard/1 {par, tee_sets {name: {yards}}, handicap} (what the zero-tap
    formation and sequence code read), including {"par", "yards": {set: [...]}} and {"par", "yards": [...]}."""
    if not card:
        return None
    ts = card.get("tee_sets")
    if not ts:
        y = card.get("yards")
        ts = {k: dict(yards=v) for k, v in y.items()} if isinstance(y, dict) else ({"card": dict(yards=y)} if y else {})
    ts = {k: (v if isinstance(v, dict) else dict(yards=v)) for k, v in ts.items() if v}

    def num(x):
        try:
            return int(round(float(x))) if x not in (None, "") else None
        except (TypeError, ValueError):
            return None
    ts = {k: dict(v, yards=[num(x) for x in v["yards"]]) for k, v in ts.items() if v.get("yards")}
    pars = card.get("par") or card.get("pars") or next((v.get("par") for v in ts.values() if v.get("par")), None)
    out = dict(par=[num(p) for p in pars] if pars else None, tee_sets=ts)
    if card.get("handicap"):
        out["handicap"] = card["handicap"]
    return out if (out["tee_sets"] or out["par"]) else None


def _zero_tap_mods():
    for d in (os.path.join(ZT, "sequence"), os.path.join(ZT, "formation")):
        if d not in sys.path:
            sys.path.append(d)
    import solve as SQ                                   # zero_tap/sequence/solve.py
    import hole_pairs as HP                              # zero_tap/formation/hole_pairs.py
    SQ.PAIRS_FORM_W, SQ.CARD_W, SQ.NEST = V3["form_w"], V3["card_w"], V3["nest"]
    return SQ, HP


def sequence_v3(fc, course, card, scene=None, mapped=True, slug=None):
    """formation-v2 hole_pairs/1 + sequence solver v3 -> (routing-compatible result, details). Raises on failure."""
    import scene as S
    SQ, HP = _zero_tap_mods()
    c1 = scorecard1(card)
    if not c1:
        raise RuntimeError("sequence_v3 needs a scorecard")
    if not mapped and scene is None:
        raise RuntimeError("unmapped and no perception scene")
    sc = S.scene_from_osm(fc, (course or {}).get("boundary")) if mapped else S.scene_from_perception(scene)
    hp = HP.hole_pairs(sc, card=c1, slug=slug)
    if not hp.get("pairs"):
        raise RuntimeError("hole_pairs: no pairs")
    n_card = R.card_holes(card)[0]
    out = SQ.run(fc, course or {}, c1, pairs=hp, n_holes=n_card if n_card and n_card <= 18 else None,
                 scene=None if mapped else scene)
    if not out.get("holes"):
        raise RuntimeError(f"sequence_v3: {out.get('status')}")
    holes = {}
    for h in out["holes"]:
        ref = str(int(h["number"]))
        conf = h.get("confidence")
        ok = bool(out.get("certain")) or (conf is not None and conf >= 0.9)
        holes[ref] = dict(ref=ref, par=h.get("par"), tee_ll=list(h["tee_ll"]), green_ll=list(h["green_ll"]),
                          straight_yd=h.get("length_yd"), p_hole=conf, p_green=h.get("p_number"),
                          status="ok" if ok else "check",
                          flags=[] if ok else [f"sequence_v3 confidence {0 if conf is None else conf:.2f}"],
                          tee_src="osm" if mapped else "perception", green_src="osm" if mapped else "perception")
    res = dict(method="sequence_v3", status=out.get("status") or "ok", n_holes=out.get("n_holes"), holes=holes,
               n_check=sum(h["status"] != "ok" for h in holes.values()), certain=bool(out.get("certain")),
               confidence=out.get("confidence"))
    inputs = out.get("inputs") or {}
    det = dict(formation="hole_pairs/1 (" + str(hp.get("model", "?")) + ")", sequence="sequence_v3",
               certain=bool(out.get("certain")), course_confidence=out.get("confidence"),
               pairs_join=inputs.get("join"), card_geo=inputs.get("card_geo"),
               structure_input="osm" if mapped else "perception")
    return res, det


# ----------------------------------------------------------------------------- the selector
def run_method(method, fc, card, course, seg=None, pads=None, scene=None, prof=None, lam=1.0, use_perception=False,
               margins=True, hide_holes=False, w=None):
    """One method -> (routing-compatible result, details). Raises on failure."""
    prof = prof or profile(fc, card, scene)
    mapped = prof["osm_mapped"]
    if method == "geometry":
        return geometry_holes(fc), {}
    if method == "sequence_v3":
        return sequence_v3(fc, course, card, scene=scene, mapped=mapped, slug=(course or {}).get("slug"))
    if method == "structure":
        sc = scene if (not mapped and scene is not None) else None
        if not mapped and sc is None and prof["osm_greens"] < 3:
            raise RuntimeError("no OSM greens and no perception scene")
        con, _ = structure_solve(fc, course, card, scene=sc)
        if not con.get("holes"):
            raise RuntimeError(f"structure: {con.get('status')}")
        return structure_as_routing(con), dict(structure_input=con.get("input"))
    if method in ("v2", "v2+structure"):
        inp = router_inputs(fc, course, seg, pads, scene, mapped=mapped, use_perception=use_perception,
                            hide_holes=hide_holes)
        det = dict(router_inputs=("osm" if mapped else "model") + ("+perception" if (use_perception and scene) else ""),
                   greens=len(inp.get("greens", [])), tees=len(inp.get("tees", [])))
        n_holes = None if card else prof["n_holes"]
        if method == "v2+structure":
            sc = scene if (not mapped and scene is not None) else None
            if not mapped and sc is None:
                raise RuntimeError("unmapped and no perception scene: no structure prior")
            con, prior = structure_solve(fc, course, card, scene=sc, n_holes=prof["n_holes"])
            if prior is None:
                raise RuntimeError(f"structure gave no marginals ({con.get('status')})")
            inp = dict(inp, struct_prior=dict(prior, lam=lam))
            det.update(structure_input=prior["src"], lam=lam)
        res = R2.route(inp, card, fc=fc, boundary=(course or {}).get("boundary"), n_holes=n_holes, w=w,
                       margins=margins)
        if not res.get("holes"):
            raise RuntimeError(f"routing v2: {res.get('status')}")
        res["_inp"] = inp
        return res, det
    raise ValueError(method)


def infer_holes(fc, card, course, seg=None, pads=None, scene=None, select=None, margins=True, hide_holes=False,
                force=None):
    """The selector: tier from the data -> SELECT[tier] -> fallbacks on error. -> (result, info)."""
    prof = profile(fc, card, scene)
    t = tier(prof)
    base = select or (dict(SELECT, **SELECT_V3) if USE_V3 else SELECT)
    cfg = dict(base[t])
    if force and force.get("method") == "sequence_v3" and t in SELECT_V3:
        cfg = dict(SELECT_V3[t])
    if force:
        cfg.update(force)
    order = [cfg["method"]] + FALLBACK.get(cfg["method"], [])
    tried, fallbacks = [], []
    for m in order:
        try:
            res, det = run_method(m, fc, card, course, seg, pads, scene, prof, lam=cfg.get("lam", 1.0),
                                  use_perception=cfg.get("perception", False), margins=margins, hide_holes=hide_holes)
            tried.append(m)
            info = dict(tier=t, method=m, chosen=cfg["method"], tried=tried, fallbacks=fallbacks, profile=prof, **det)
            if res.get("_inp") is None and cfg.get("confirm"):
                # a routing v2 session for the golfer confirm (the structure solver has no constraint re-solve)
                cc = cfg["confirm"]
                try:
                    inp = router_inputs(fc, course, seg, pads, scene, mapped=prof["osm_mapped"],
                                        use_perception=cc.get("perception", False), hide_holes=hide_holes)
                    if cc["method"] == "v2+structure":
                        sc = scene if (not prof["osm_mapped"] and scene is not None) else None
                        _, prior = structure_solve(fc, course, card, scene=sc, n_holes=prof["n_holes"])
                        if prior is not None:
                            inp = dict(inp, struct_prior=dict(prior, lam=cc.get("lam", 1.0)))
                    res["_inp"] = inp
                    info["confirm_session"] = dict(cc)
                except Exception as e:                           # noqa: BLE001
                    info["confirm_session"] = dict(error=f"{type(e).__name__}: {e}"[:200])
            return res, info
        except Exception as e:                                   # noqa: BLE001
            tried.append(m)
            fallbacks.append(f"{m}: {type(e).__name__}: {e}"[:200])
    return dict(method="none", status="failed", holes={}), dict(tier=t, method=None, chosen=cfg["method"],
                                                                 tried=tried, fallbacks=fallbacks, profile=prof)
