"""Error budget: which map layer causes the wrong clubs / aims of the automatic build?

  python3 course_data/platform/error_budget.py [--courses blue_hills,ellis] [--n 4000] [--workers 4]
  -> course_data/platform/error_budget.json (+ error_budget_cache.json: decisions by hole fingerprint)
  python3 course_data/platform/error_budget.py --report        # rewrite the tables from the json only

For every course with a hand truth package the automatic build (course_data/packages/<slug>/package.json, the
build with the true card, as platform/picks_pipeline.py) and the all-truth package are compared hole by hole.
Then one layer at a time is swapped:

  forward   auto package + ONE truth layer          -> does this hole now match the all-truth plan?
  reverse   truth package + ONE auto layer          -> does this layer alone break the all-truth plan?
  groups    auto + truth frame (card, routing, tees, greens); auto + every truth hazard layer

Layers
  card       par + card yards of the scored set (hole par, yards{}, the tee entry's card_yards)
  routing    the hole line (hole_line_ll: where the product's tee line points, 250 yds along it)
  tees       the scored set's tee position (tee_ll)
  greens     green centre + outline
  fairway    lies fairway + first_cut      trees      recovery        water     water
  ob         ob (incl. course boundary)   long_grass native          bunkers   sand
  elevation  the per-club elevation table (carry / roll / kick): the truth's is the DEM sampled along the truth
             tee line (the hand truth has no elevation of its own: same 3DEP DEM), the auto's along the auto line

Hazard layers are swapped as lie REGIONS, not as polygon lists: the donor's stack (later wins) is flattened to
the region where each lie is the visible lie (shapely), the base keeps every zone of the other lies, and the
donor region is painted on top. So "auto + truth trees" = the auto map with its own tree zones removed and the
hand map's visible trees laid over it; everywhere else the auto lies are untouched. Swapping no layer reproduces
the auto lies exactly, swapping all of them the truth lies (test_error_budget.py).

Truth per course (the same truths gate_eval / scoreboard score against, put into one package framework):
  holes_truth courses   course_data/truth/<slug>/holes_truth.json (par, card, tees per set, green, hole line) +
                        hand_zones_ll.json (landing corridors: inside the traced footprint the hand map wins, a
                        'rough' footprint masks the auto zones; outside it the auto zones stay), as score_auto.py
  corridor-only         Veenker / Coldwater / Ellis: hand_zones_ll.json (tee, green, corridor zones)
  Spirit Hollow         course_data/spirit_hollow/hand_zones_ll.json, the Black boxes (tee moved up its line by
                        course.BLACK_TEE_FORWARD, as scoreboard.sh_geometry); 2B / 9B (Gold boxes) left out
  Colbert Hills         zero_tap/truth_sets/colbert_hills/holes_truth.json (tees, greens, lines, card, whole-hole
                        fairway / water / bunker polygons; no trees / OB / long grass: those stay auto)
  Mozingo Lake          not scored: its hand map (mozingo/tee_strategy.HOLES) is in screenshot pixels with no
                        WGS84 registration, so its layers cannot be put into the package

Decision: product/decide.quick_hole (n swings, default 4000; seed 31 for every config = common random numbers: every config
sees the same swings, so a changed pick is a changed map, not noise). A hole matches when the club is the same
and the aim points (club carry along the printed aim line, WGS84) are within AIM_TOL yds. Regret = EV on the
truth hole of the config's club at its aim point (re-expressed in the truth frame) - the truth plan's EV
(strokes). A reference tie = the truth plan's margin < 0.01 strokes.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
if HERE in sys.path:                       # platform/package.py and product/package.py share a module name
    sys.path.remove(HERE)
for _p in (os.path.join(CD, "product"), os.path.join(CD, "imagery"), os.path.join(ROOT, "mozingo")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

OUT_JSON = os.path.join(HERE, "error_budget.json")
CACHE_JSON = os.path.join(HERE, "error_budget_cache.json")
OUT_MD = os.path.join(HERE, "ERROR_BUDGET.md")

AIM_TOL = 10.0
TIE = 0.01
SEED = 31
CHUNK = 24
SAME_PLACE = 80.0       # yds: aim points further apart are on different holes (regret not defined)
ROUTE_TOL = 25.0        # yds: an auto green this close to a truth green is that hole (score_auto.py)

LAYERS = ["card", "routing", "tees", "greens", "fairway", "trees", "water", "ob", "long_grass", "bunkers",
          "elevation"]
ZONE_LAYERS = {"fairway": ("fairway", "first_cut"), "trees": ("recovery",), "water": ("water",), "ob": ("ob",),
               "long_grass": ("native",), "bunkers": ("sand",)}
FRAME_LAYERS = ["card", "routing", "tees", "greens"]
GROUPS = {"frame": FRAME_LAYERS, "hazards": list(ZONE_LAYERS)}

COURSES = [
    dict(slug="blue_hills", tees="Black", kind="holes_truth"),
    dict(slug="eagle_knoll", tees="Back", kind="holes_truth"),
    dict(slug="gateway_national", tees="Back", kind="holes_truth"),
    dict(slug="national_kc", tees="Black", kind="holes_truth"),
    dict(slug="hot_springs_arlington", tees="Gold", kind="holes_truth"),
    dict(slug="pine_dunes", tees="Gold", kind="holes_truth"),
    dict(slug="veenker", tees="Blue", kind="corridor"),
    dict(slug="coldwater", tees="Blue", kind="corridor"),
    dict(slug="ellis", tees="Blue", kind="corridor"),
    dict(slug="spirit_hollow", tees="Black", kind="spirit_hollow"),
    dict(slug="colbert_hills", tees="Black/Blue", kind="colbert",
         package="course_data/library/colbert_hills/package.json",
         truth="course_data/zero_tap/truth_sets/colbert_hills/holes_truth.json"),
]
NOT_SCORED = {"mozingo_lake": "hand map in screenshot pixels (mozingo/tee_strategy.HOLES), no WGS84 registration"}


def rj(p, d=None):
    try:
        return json.load(open(p))
    except (OSError, ValueError):
        return d


_PK = None


def PK():
    """course_data/product/package.py (loaded by path: the platform one has the same module name)."""
    global _PK
    if _PK is None:
        name = "eb_product_package"
        spec = importlib.util.spec_from_file_location(name, os.path.join(CD, "product", "package.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        _PK = mod
    return _PK


# ----------------------------------------------------------------------------- lie stacks (WGS84, later wins)
def _ring(poly):
    return [(float(p[0]), float(p[1])) for p in poly]


def auto_stack(pkg, h, ref_ll):
    """[(model lie, ring_ll)] exactly as product/package.load orders a hole's zones (precedence or given)."""
    P = PK()
    if P.FIRST_CUT_YDS:
        raise SystemExit("error_budget: PRODUCT_FIRST_CUT_YDS must be 0 (the band is drawn in pixels)")
    raw_z = h.get("zones_ll") if h.get("zones_ll") is not None else h.get("zones")
    zs = []
    for z, (lie, poly) in zip(P._zone_meta(raw_z), P._zones(raw_z)):
        if not poly or len(poly) < 3 or not P._is_ll(poly[0], ref_ll):
            continue
        boundary = lie == "ob" and str(z.get("src", "")).endswith("course_boundary")
        lie = P.LIE_MAP.get(lie, lie)
        if lie not in P.MODEL_LIES:
            continue
        zs.append(("ob_boundary" if boundary else lie, _ring(poly)))
    return [(lie, ring) for lie, ring in P.order_zones(zs, P.zone_order_mode(pkg, h))]


def model_lie(lie):
    P = PK()
    lie = P.LIE_MAP.get(lie, lie)
    return lie if lie in P.MODEL_LIES else None


def _geom(ring):
    from shapely.geometry import Polygon
    try:
        g = Polygon(ring)
        if not g.is_valid:
            g = g.buffer(0)
        return g
    except Exception:                                    # noqa: BLE001
        return None


def effective(stack):
    """{lie: shapely geometry where that lie is the visible one} for a later-wins stack."""
    reg = {}
    for lie, ring in stack:
        g = _geom(ring)
        if g is None or g.is_empty:
            continue
        for o in list(reg):
            if reg[o].intersects(g):
                reg[o] = reg[o].difference(g)
        reg[lie] = reg[lie].union(g) if lie in reg else g
    return reg


MIN_AREA = 1e-11          # deg^2, ~0.1 m^2: drop slivers


def simple_rings(g):
    """Hole-free exterior rings covering exactly geometry g (polygons with holes are cut through each hole)."""
    from shapely.geometry import LineString, MultiPolygon, Polygon, GeometryCollection
    from shapely.ops import split
    if g is None or g.is_empty:
        return []
    if isinstance(g, (MultiPolygon, GeometryCollection)):
        return [r for p in g.geoms for r in simple_rings(p)]
    if not isinstance(g, Polygon):
        return []
    if g.area < MIN_AREA:
        return []
    if not g.interiors:
        return [list(g.exterior.coords)[:-1]]
    c = Polygon(g.interiors[0]).representative_point()        # strictly inside the hole
    x0, y0, x1, y1 = g.bounds
    nh = len(g.interiors)
    for cut in (LineString([(c.x, y0 - 1e-3), (c.x, y1 + 1e-3)]), LineString([(x0 - 1e-3, c.y), (x1 + 1e-3, c.y)])):
        parts = [p for p in split(g, cut).geoms if isinstance(p, Polygon)]
        if len(parts) >= 2 and all(len(p.interiors) < nh for p in parts):
            return [r for p in parts for r in simple_rings(p)]
    # could not cut (degenerate hole): keep the outline, paint nothing for the hole
    return [list(g.exterior.coords)[:-1]]


def hybrid_stack(base, donor, lies, donor_eff=None):
    """base stack with every zone of `lies` removed and the donor's visible regions of `lies` painted on top."""
    lies = set(lies)
    if not lies:
        return list(base)
    eff = donor_eff if donor_eff is not None else effective(donor)
    out = [z for z in base if z[0] not in lies]
    for lie in sorted(lies):
        out += [(lie, r) for r in simple_rings(eff.get(lie))]
    return out


def lies_of(layers):
    return {lie for L in layers if L in ZONE_LAYERS for lie in ZONE_LAYERS[L]}


def mixed_stack(auto_st, truth_st, truth_layers, eff_cache):
    """The hole's stack when the zone layers in truth_layers come from the truth and the rest from the auto map:
    the base is whichever side holds the majority of the hazard layers, the other side is painted over it."""
    differ = differing_layers(auto_st, truth_st, eff_cache)
    zl = [L for L in differ if L in truth_layers]
    if not zl:                         # every layer that differs on this hole is auto (a no-op swap is no swap)
        return list(auto_st)
    if len(zl) == len(differ):
        return list(truth_st)
    if len(zl) * 2 <= len(differ):
        return hybrid_stack(auto_st, truth_st, lies_of(zl), eff_cache["truth"])
    return hybrid_stack(truth_st, auto_st, lies_of([L for L in differ if L not in zl]), eff_cache["auto"])


DIFF_AREA = 1e-10        # deg^2 (~1 m^2): a layer whose visible regions differ by less is the same layer


def differing_layers(auto_st, truth_st, eff_cache):
    """Hazard layers whose visible regions differ between the auto and the truth stack of a hole."""
    if "differ" not in eff_cache:
        from shapely.geometry import Polygon
        from shapely.ops import unary_union
        ea = eff_cache.setdefault("auto", effective(auto_st))
        et = eff_cache.setdefault("truth", effective(truth_st))
        out = []
        for L, lies in ZONE_LAYERS.items():
            a = unary_union([ea[l] for l in lies if l in ea]) if any(l in ea for l in lies) else Polygon()
            t = unary_union([et[l] for l in lies if l in et]) if any(l in et for l in lies) else Polygon()
            if a.symmetric_difference(t).area > DIFF_AREA:
                out.append(L)
        eff_cache["differ"] = out
    return eff_cache["differ"]


def lie_at_ll(stack, pts):
    from matplotlib.path import Path
    lie = np.array(["rough"] * len(pts), dtype=object)
    for name, ring in stack:
        if len(ring) >= 3:
            lie[Path(np.asarray(ring, float)).contains_points(pts)] = name
    return np.array([("ob" if x == "ob_boundary" else x) for x in lie], dtype=object)


# ----------------------------------------------------------------------------- truth per course
def _move_up(tee_ll, dot_ll, yds):
    import render as R
    fr = R.Frame(tee_ll, dot_ll, ppy=1.0, tee_px=(0.0, 0.0), proj="enu")
    return [float(v) for v in fr.yds_to_ll([[0.0, -float(yds)]])[0]]


def sh_forward():
    import re
    src = open(os.path.join(ROOT, "spirit_hollow", "course.py")).read()
    m = re.search(r"^BLACK_TEE_FORWARD\s*=\s*(\{[^}]*\})", src, re.M)
    import ast
    return {str(k): float(v) for k, v in ast.literal_eval(m.group(1)).items()} if m else {}


def truth_holes(cfg):
    """{ref: truth record} with keys par, yards {set: yd}, line, green_ll, green_poly, tee_ll (scored set),
    hand (corridor map: footprint + zones in traced order), extra (zones on top), known_full ({lie: [rings]})."""
    S = cfg["tees"]
    out = {}
    if cfg["kind"] == "holes_truth":
        T = rj(os.path.join(CD, "truth", cfg["slug"], "holes_truth.json"))
        HZ = (rj(os.path.join(CD, "truth", cfg["slug"], "hand_zones_ll.json")) or {}).get("holes", {})
        for ref, th in T["holes"].items():
            m = HZ.get(ref)
            out[ref] = dict(par=int(th["par"]), yards={k: v for k, v in (th.get("card") or {}).items()},
                            line=th.get("hole_line_ll"), green_ll=th["green_ll"], green_poly=th.get("green_poly_ll"),
                            tee_ll=(th.get("tees") or {}).get(S),
                            hand=dict(footprint=m["footprint_ll"], zones=m["zones"]) if m else None,
                            extra=th.get("extra_zones") or [])
    elif cfg["kind"] == "corridor":
        HZ = rj(os.path.join(CD, "truth", cfg["slug"], "hand_zones_ll.json"))["holes"]
        for ref, m in HZ.items():
            if (m.get("tee_set") or S) != S:
                continue
            out[ref] = dict(par=int(m["par"]) if m.get("par") else None, tee_ll=m["tee_ll"],
                            green_ll=m.get("green_ll"), hand=dict(footprint=m["footprint_ll"], zones=m["zones"]))
    elif cfg["kind"] == "spirit_hollow":
        HZ = rj(os.path.join(CD, "spirit_hollow", "hand_zones_ll.json"))["holes"]
        shots = {k: v["set"] for k, v in rj(os.path.join(CD, "spirit_hollow", "screenshot_tee_sets.json"))["holes"].items()}
        fwd = sh_forward()
        for key, m in HZ.items():
            st = "Black" if key in fwd else shots.get(key, "Black")
            if st != S:
                continue
            ref = key.rstrip("BF")
            out[ref] = dict(par=int(m["par"]) if m.get("par") else None, key=key,
                            tee_ll=_move_up(m["tee_ll"], m["dot270_ll"], fwd.get(key, 0.0)),
                            green_ll=m.get("green_ll"), hand=dict(footprint=m["footprint_ll"], zones=m["zones"]))
    elif cfg["kind"] == "colbert":
        T = rj(os.path.join(ROOT, cfg["truth"]))
        for ref, th in T["holes"].items():
            full = {}
            for f, lie in (("fairway_ll", "fairway"), ("water_ll", "water"), ("bunker_ll", "sand")):
                if th.get(f) is not None:
                    full[lie] = [p for p in th[f] if len(p) >= 3]
            out[ref] = dict(par=int(th["par"]), yards=dict(th.get("card") or {}), line=th.get("hole_line_ll"),
                            green_ll=th["green_ll"], green_poly=th.get("green_poly_ll"),
                            tee_ll=(th.get("tees") or {}).get(S), known_full=full)
    return out


def truth_stack(auto_st, td):
    """The truth hole's lie stack: the auto stack, then (corridor maps) a rough footprint masking it and the hand
    zones in traced order, or (whole-hole layers) the known lies replaced outright."""
    st = list(auto_st)
    if td.get("known_full"):
        known = set(td["known_full"])
        st = [z for z in st if z[0] not in known]
        for lie in ("fairway", "water", "sand"):
            st += [(lie, _ring(r)) for r in td["known_full"].get(lie, [])]
    if td.get("hand"):
        st.append(("rough", _ring(td["hand"]["footprint"])))
        for z in td["hand"]["zones"]:
            lie = model_lie(z["lie"])
            if lie and len(z["poly_ll"]) >= 3:
                st.append((lie, _ring(z["poly_ll"])))
    for z in td.get("extra") or []:
        lie = model_lie(z["lie"])
        if lie and len(z["poly_ll"]) >= 3:
            st.append((lie, _ring(z["poly_ll"])))
    return st


# ----------------------------------------------------------------------------- hybrid packages
def tee_entry(h, S, default_set):
    """The scored set's tee entry (created from the package's own set when the build has no such set)."""
    tees = h.setdefault("tees", {})
    k = next((k for k in tees if k.lower() == S.lower()), None)
    if k is None:
        src = tees.get(default_set) or (next(iter(tees.values())) if tees else {})
        tees[S] = copy.deepcopy(src)
        if not tees[S].get("tee_ll") and h.get("tee_ll"):
            tees[S]["tee_ll"] = h["tee_ll"]
        tees[S].pop("card_yards", None)
        k = S
    return tees[k]


def prepare(auto_pkg, S):
    """auto package normalised for the scored set S (S in tee_sets, a tee entry for S on every hole)."""
    pkg = copy.deepcopy(auto_pkg)
    default = pkg.get("tee_set")
    sets = pkg.setdefault("tee_sets", {})
    if not any(k.lower() == S.lower() for k in sets):
        sets[S] = {}
    for h in pkg["holes"].values():
        tee_entry(h, S, default)
    pkg["tee_set"] = S
    return pkg


def renumber(pkg, truth, S):
    """(package with every hole number given the auto hole whose green is the truth green of that number, within
    ROUTE_TOL; the card fields stay with the number) and {ref: auto ref moved there}. The auto geometry (tees,
    green, zones, elevation) of the physical hole is kept: only the numbering is the truth's."""
    out = copy.deepcopy(pkg)
    P = PK()
    greens = {r: P._ll(h.get("green_ll")) for r, h in pkg["holes"].items() if P._ll(h.get("green_ll"))}
    moved = {}
    for ref, td in truth.items():
        if not td.get("green_ll") or not greens:
            continue
        j = min(greens, key=lambda r: yd_between(greens[r], td["green_ll"]))
        if j == ref or yd_between(greens[j], td["green_ll"]) > ROUTE_TOL:
            continue
        own = pkg["holes"].get(ref) or {}
        h = copy.deepcopy(pkg["holes"][j])
        for f in ("par", "yards"):
            if f in own:
                h[f] = copy.deepcopy(own[f])
            else:
                h.pop(f, None)
        e_own = tee_entry(copy.deepcopy(own), S, pkg.get("tee_set")) if own else {}
        ent = tee_entry(h, S, pkg.get("tee_set"))
        if e_own.get("card_yards"):
            ent["card_yards"] = e_own["card_yards"]
        else:
            ent.pop("card_yards", None)
        h["ref"] = ref
        out["holes"][ref] = h
        moved[ref] = j
    return out, moved


def apply_layers(pkg, truth, S, layers, stacks):
    """Package with `layers` (a set of LAYERS names) from the truth; stacks: {ref: mixed stack} for the zones."""
    out = copy.deepcopy(pkg)
    for ref, h in out["holes"].items():
        td = truth.get(ref) or {}
        ent = tee_entry(h, S, pkg.get("tee_set"))
        if "card" in layers and td.get("par"):
            h["par"] = td["par"]
            if td.get("yards"):
                h["yards"] = dict(td["yards"])
                y = next((v for k, v in td["yards"].items() if k.lower() == S.lower()), None)
                if y:
                    ent["card_yards"] = y
        if "routing" in layers and td.get("line"):
            h["hole_line_ll"] = td["line"]
        if "greens" in layers and td.get("green_ll"):
            h["green_ll"] = td["green_ll"]
            if td.get("green_poly"):
                h["green_polygon_ll"] = td["green_poly"]
        if "tees" in layers and td.get("tee_ll"):
            ent["tee_ll"] = td["tee_ll"]
            ent.pop("aim_ll", None)
        if ref in stacks:
            h["zones_ll"] = [dict(lie=("ob" if l == "ob_boundary" else l), poly=[list(p) for p in r], src="error_budget")
                             for l, r in stacks[ref]]
            h["zone_order"] = "given"
            h.pop("zones", None)
    return out


def load_models(pkg, S, name):
    """(Course, {key: model hole}) of a package dict."""
    P = PK()
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "package.json")
        json.dump(pkg, open(p, "w"))
        C = P.load(p, S)
    return C, C.holes


def fp(h):
    return hashlib.sha1(json.dumps(h, sort_keys=True, default=str).encode()).hexdigest()[:16]


def configs():
    """[(name, kind, set of truth layers)]"""
    cf = [("auto", "ref", set()), ("truth", "ref", set(LAYERS))]
    cf += [(f"+{L}", "forward", {L}) for L in LAYERS]
    cf += [(f"-{L}", "reverse", set(LAYERS) - {L}) for L in LAYERS]
    cf += [(f"+{g}", "group", set(ls)) for g, ls in GROUPS.items()]
    return cf


# ----------------------------------------------------------------------------- decisions
_BBOX = {}


def fast_lie_at(h, pts):
    """tee_strategy.lie_at with a bounding-box prefilter per zone: the same lies (a point outside a zone's box is
    never inside it), several times faster on maps with many small zones."""
    from matplotlib.path import Path
    pts = np.asarray(pts, float)
    lie = np.array(["rough"] * len(pts), dtype=object)
    for name, poly in h["zones"]:
        key = id(poly)
        b = _BBOX.get(key)
        if b is None or b[0] is not poly:
            P = np.asarray(poly, float)
            b = _BBOX[key] = (poly, P.min(0), P.max(0), Path(P))
        _, lo, hi, path = b
        m = (pts[:, 0] >= lo[0]) & (pts[:, 0] <= hi[0]) & (pts[:, 1] >= lo[1]) & (pts[:, 1] <= hi[1])
        if m.any():
            idx = np.flatnonzero(m)
            lie[idx[path.contains_points(pts[idx])]] = name
    return lie


def use_fast_lie_at():
    import tee_strategy as t
    t.lie_at = fast_lie_at


def run_decisions(jobs, n, workers, cache):
    """jobs {fp: model hole} -> cache[fp] = compact quick result (common random numbers: seed SEED)."""
    import decide
    use_fast_lie_at()
    todo = {k: v for k, v in jobs.items() if f"{k}|{n}" not in cache}
    if todo:
        t0 = time.time()
        print(f"  deciding {len(todo)} unique holes ({len(jobs) - len(todo)} cached) ...", flush=True)
        ks = list(todo)
        for i in range(0, len(ks), CHUNK):           # in chunks, the cache saved after each (resumable)
            res = decide.run(copy.deepcopy({k: todo[k] for k in ks[i:i + CHUNK]}), "quick", workers=workers,
                             log=lambda *a: None, n=n)
            for k, v in res.items():
                cache[f"{k}|{n}"] = dict(pick=v["pick"], aim=v["aim"], ev=v["ev"], runner=v["runner"],
                                         margin=v["margin"], tie=v["tie"], evs={c: r["ev"] for c, r in v["clubs"].items()},
                                         aims={c: r["aim"] for c, r in v["clubs"].items()})
            json.dump(cache, open(CACHE_JSON, "w"))
            print(f"    {min(i + CHUNK, len(ks))}/{len(ks)} ({time.time() - t0:.0f} s)", flush=True)
        print(f"  ... {time.time() - t0:.0f} s", flush=True)
    return {k: cache[f"{k}|{n}"] for k in jobs}


def aim_point_ll(C, k, hole, club, aim):
    import decide
    import render as R
    import tee_strategy as t
    pt, _ = decide._aim_point(hole, club, aim)
    return R.Frame.from_json(C.frames[k]).px_to_ll([pt])[0]


def truth_ev(truth_hole, club, aim, n):
    import decide
    import tee_strategy as t
    decide.bind({"T": truth_hole})
    decide.set_prior_means()
    z = decide._z(n, SEED)
    return float(t.simulate("T", club, aim, z=z)[3].mean())


def aim_in_frame(C, k, hole, ll, club):
    """lateral aim (yds) in hole k's frame that points at ll (angle kept: lateral at the club's carry)."""
    import decide
    import render as R
    import tee_strategy as t
    px = R.Frame.from_json(C.frames[k]).ll_to_px([ll])[0]
    tee, fwd, right, ppy = t.hole_frame(hole)
    rel = (np.asarray(px, float) - tee) / ppy
    along, lat = float(rel @ fwd), float(rel @ right)
    return lat * decide._carry(club) / max(along, 1.0)


def yd_between(a, b):
    import render as R
    fr = R.Frame(list(a), [a[0], a[1] + 0.001], ppy=1.0, proj="utm")
    return float(np.linalg.norm(fr.ll_to_yds([a])[0] - fr.ll_to_yds([b])[0]))


# ----------------------------------------------------------------------------- diagnostics
def _to_yd_fn(lat0, lon0):
    kx = np.cos(np.radians(lat0)) * 111320.0 / 0.9144
    ky = 110574.0 / 0.9144
    return lambda x, y, z=None: ((np.asarray(x) - lon0) * kx, (np.asarray(y) - lat0) * ky)


def layer_diagnostics(auto_st, truth_st, tee_ll, aim_ll):
    """Per hazard layer, in the truth tee shot's landing corridor (180-320 yds along the truth tee line, +/-50):
    truth area, auto area, missing (truth not auto), extra (auto not truth) in sq yds and their mean side (yds,
    + = right), and the lateral offset of the region's inner edge on each side."""
    from shapely import transform as _tr
    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    def transform(fn, g):
        return _tr(g, lambda xy: np.c_[fn(xy[:, 0], xy[:, 1])])
    f = _to_yd_fn(tee_ll[1], tee_ll[0])
    T0 = np.array(f(tee_ll[0], tee_ll[1]), float)
    A1 = np.array(f(aim_ll[0], aim_ll[1]), float) - T0
    fwd = A1 / np.linalg.norm(A1)
    right = np.array([fwd[1], -fwd[0]])            # east-north: golfer's right of north is east
    corners = [T0 + fwd * a + right * l for a, l in ((180, -50), (320, -50), (320, 50), (180, 50))]
    corr = Polygon(corners)
    ea, et = effective(auto_st), effective(truth_st)
    out = {}
    for L, lies in ZONE_LAYERS.items():
        ga = [transform(f, ea[l]) for l in lies if l in ea]
        gt = [transform(f, et[l]) for l in lies if l in et]
        a = unary_union(ga).intersection(corr) if ga else Polygon()
        tt = unary_union(gt).intersection(corr) if gt else Polygon()
        miss, extra = tt.difference(a), a.difference(tt)

        def side(g):
            if g.is_empty or g.area < 1:
                return None
            c = np.array([g.centroid.x, g.centroid.y]) - T0
            return round(float(c @ right), 1)
        out[L] = dict(truth=round(tt.area), auto=round(a.area), missing=round(miss.area), extra=round(extra.area),
                      missing_side=side(miss), extra_side=side(extra))
    return out


# ----------------------------------------------------------------------------- one course
def score_course(cfg, n, workers, cache):
    S = cfg["tees"]
    pkg_path = os.path.join(ROOT, cfg.get("package") or f"course_data/packages/{cfg['slug']}/package.json")
    auto_raw = rj(pkg_path)
    if auto_raw is None:
        return dict(slug=cfg["slug"], error=f"no package {os.path.relpath(pkg_path, ROOT)}")
    base = prepare(auto_raw, S)
    truth = truth_holes(cfg)
    base_r, moved = renumber(base, truth, S)
    P = PK()
    # stacks: auto as numbered by the build (A) and renumbered to the truth routing (R); the truth over R
    auto_st, truth_st, eff_cache = {"A": {}, "R": {}}, {}, {"A": {}, "R": {}}
    for v, b in (("R", base_r), ("A", base)):
        for ref, td in truth.items():
            h = b["holes"].get(ref)
            if h is None:
                continue
            ent = tee_entry(h, S, b.get("tee_set"))
            ref_ll = P._ll(ent.get("tee_ll")) or P._ll(h.get("tee_ll")) or td.get("tee_ll")
            if ref_ll is None:
                continue
            auto_st[v][ref] = auto_stack(b, h, ref_ll)
            if v == "R":
                truth_st[ref] = truth_stack(auto_st[v][ref], td)
            eff_cache[v][ref] = {}
    built = {}
    for name, kind, layers in configs():
        v = "R" if "routing" in layers else "A"
        b = base_r if v == "R" else base
        stacks = {ref: mixed_stack(auto_st[v][ref], truth_st[ref], layers, eff_cache[v][ref])
                  for ref in auto_st[v] if ref in truth_st}
        pk = apply_layers(b, truth, S, layers, stacks)
        C, holes = load_models(pk, S, f"eb_{cfg['slug']}_{name}")
        built[name] = (C, holes, layers)
    # elevation: the donor's table (decoupled from the tee line)
    elev = {"auto": {k: h.get("elev") for k, h in built["auto"][1].items()},
            "auto_R": {k: h.get("elev") for k, h in built["+routing"][1].items()},
            "truth": {k: h.get("elev") for k, h in built["truth"][1].items()}}
    for name, (C, holes, layers) in built.items():
        src = elev["truth" if "elevation" in layers else "auto_R" if "routing" in layers else "auto"]
        for k, h in holes.items():
            if src.get(k):
                h["elev"] = src[k]
            else:
                h.pop("elev", None)
    keys = [k for k in built["truth"][1] if str(k) in truth]
    jobs = {}
    for name, (C, holes, _) in built.items():
        for k in keys:
            if k in holes:
                jobs[fp(holes[k])] = holes[k]
    res = run_decisions(jobs, n, workers, cache)
    Ct, Ht, _ = built["truth"]
    rows = []
    for k in keys:
        ref = str(k)
        tr = res[fp(Ht[k])]
        t_aim_ll = aim_point_ll(Ct, k, Ht[k], tr["pick"], tr["aim"])
        row = dict(hole=ref, truth=dict(pick=tr["pick"], aim=round(tr["aim"], 1), ev=round(tr["ev"], 4),
                                        runner=tr["runner"], margin=round(tr["margin"], 4), tie=tr["margin"] < TIE),
                   configs={})
        for name, (C, holes, layers) in built.items():
            if k not in holes:
                row["configs"][name] = dict(pick=None, aim=0.0, match=False, club=False, same_or_tie=False,
                                            regret=None, note="not a tee-shot hole here (planned as a par 3)")
                continue
            r = res[fp(holes[k])]
            ll = aim_point_ll(C, k, holes[k], r["pick"], r["aim"])
            d = yd_between(ll, t_aim_ll)
            club = r["pick"] == tr["pick"]
            tie = club or (tr["margin"] < TIE and r["pick"] == tr["runner"]) or (r["margin"] < TIE and r["runner"] == tr["pick"])
            reg = None                           # aim point on another hole (wrong routing): no regret on this one
            if d <= SAME_PLACE:
                a_t = round(float(aim_in_frame(Ct, k, Ht[k], ll, r["pick"])), 2)
                ck = f"rg|{fp(Ht[k])}|{r['pick']}|{a_t}|{n}"
                if ck not in cache:
                    cache[ck] = truth_ev(Ht[k], r["pick"], a_t, n)
                reg = cache[ck] - tr["ev"]
            row["configs"][name] = dict(pick=r["pick"], aim=round(r["aim"], 1), margin=round(r["margin"], 4),
                                        aim_dist=round(d, 1), club=club, same_or_tie=bool(tie),
                                        match=bool(club and d <= AIM_TOL),
                                        regret=None if reg is None else round(float(reg), 4))
        # geometry diagnostics (auto vs truth)
        Ca, Ha, _ = built["auto"]
        td = truth[ref]
        g = dict()
        if k in Ha:
            fa, ft = Ca.frames[k], Ct.frames[k]
            g["tee_err"] = round(yd_between(fa["tee_ll"], ft["tee_ll"]), 1)
            ha = base["holes"][ref]
            ga = P._ll(ha.get("green_ll"))
            if ga and td.get("green_ll"):
                g["green_err"] = round(yd_between(ga, td["green_ll"]), 1)
            g["line_turn_deg"] = round(float(abs(((Ca.bearings[k] - Ct.bearings[k]) + 180) % 360 - 180)), 1)
            g["len_auto"], g["len_truth"] = Ha[k]["length"], Ht[k]["length"]
            ead = elev["auto"].get(k) or {}
            etd = elev["truth"].get(k) or {}
            if ead.get("Driver") and etd.get("Driver"):
                g["elev_driver_carry"] = [round(ead["Driver"][0], 1), round(etd["Driver"][0], 1)]
                g["elev_driver_kick"] = [round(ead["Driver"][2], 1), round(etd["Driver"][2], 1)]
            try:
                g["layers"] = layer_diagnostics(auto_st["R"][ref], truth_st[ref], ft["tee_ll"], ft["aim_ll"])  # the physical hole
            except Exception as e:                       # noqa: BLE001
                g["layers_error"] = f"{type(e).__name__}: {e}"
            g["auto_src"] = sorted({str(z.get("src", ""))[:30] for z in (ha.get("zones_ll") or []) if isinstance(z, dict)})
        row["geo"] = g
        rows.append(row)
    return dict(slug=cfg["slug"], tees=S, kind=cfg["kind"], package=os.path.relpath(pkg_path, ROOT), renumbered=moved,
                truth_holes=len(truth), scored=len(rows), rows=rows)


# ----------------------------------------------------------------------------- summary / report
NO_CARD = ("national_kc",)       # the build found no web card (tee set osm_back): hole numbering wrong


def summarise(courses, skip=()):
    rows = [(c["slug"], r) for c in courses if "rows" in c and c["slug"] not in skip for r in c["rows"]]
    miss = [(s, r) for s, r in rows if not r["configs"]["auto"]["match"]]
    out = dict(holes=len(rows), auto_match=len(rows) - len(miss), auto_club=sum(r["configs"]["auto"]["club"] for _, r in rows),
               auto_same_or_tie=sum(r["configs"]["auto"]["same_or_tie"] for _, r in rows),
               ref_ties=sum(r["truth"]["tie"] for _, r in rows), misses=len(miss),
               misses_tie=sum(r["truth"]["tie"] for _, r in miss),
               auto_regret=round(sum(r["configs"]["auto"]["regret"] or 0 for _, r in rows), 3), layers={})
    names = [n for n, _, _ in configs() if n not in ("auto", "truth")]
    for name in names:
        fixed = [(s, r) for s, r in miss if r["configs"][name]["match"]]
        broke = [(s, r) for s, r in rows if r["configs"]["auto"]["match"] and not r["configs"][name]["match"]]
        cl_fixed = sum(1 for s, r in rows if not r["configs"]["auto"]["club"] and r["configs"][name]["club"])
        rg = sum(r["configs"][name]["regret"] for _, r in rows if r["configs"][name].get("regret") is not None)
        nontie = [(s, r) for s, r in fixed if not r["truth"]["tie"]]
        out["layers"][name] = dict(fixed=len(fixed), fixed_nontie=len(nontie), broke=len(broke),
                                   club_fixed=cl_fixed, match=sum(r["configs"][name]["match"] for _, r in rows),
                                   regret=round(rg, 3), fixed_holes=[f"{s}:{r['hole']}" for s, r in fixed],
                                   wrong_holes=[f"{s}:{r['hole']}" for s, r in rows if not r["configs"][name]["match"]])
    fwd = [f"+{L}" for L in LAYERS]
    resid = [(s, r) for s, r in miss if not any(r["configs"][n]["match"] for n in fwd)]
    out["residual"] = dict(n=len(resid), holes=[f"{s}:{r['hole']}" for s, r in resid],
                           fixed_by_groups=[f"{s}:{r['hole']}" for s, r in resid
                                            if any(r["configs"][f"+{g}"]["match"] for g in GROUPS)])
    out["auto_regret_note"] = "regret summed where the aim point is on the same hole (<= SAME_PLACE yds)"
    return out


def table(S, title):
    L = [title, "",
         "| layer | misses fixed (+layer) | of them not a reference tie | share of misses | new misses it causes | "
         "regret with +layer | holes wrong with -layer (truth + this auto layer) | regret with -layer |",
         "|---|---|---|---|---|---|---|---|",
         f"| *none (auto)* | | | | | {S['auto_regret']} | {S['misses']} | |"]
    for Ly in LAYERS:
        f, r = S["layers"][f"+{Ly}"], S["layers"][f"-{Ly}"]
        L.append(f"| {Ly} | {f['fixed']} | {f['fixed_nontie']} | {100 * f['fixed'] / max(S['misses'], 1):.0f}% | {f['broke']} | "
                 f"{f['regret']} | {S['holes'] - r['match']} | {r['regret']} |")
    for g, ls in GROUPS.items():
        f = S["layers"][f"+{g}"]
        L.append(f"| *group {g}* ({', '.join(ls)}) | {f['fixed']} | {f['fixed_nontie']} | "
                 f"{100 * f['fixed'] / max(S['misses'], 1):.0f}% | {f['broke']} | {f['regret']} | | |")
    R = S["residual"]
    L += ["", f"**Residual**: {R['n']} of {S['misses']} misses are fixed by no single layer "
          f"({', '.join(R['holes']) or '-'}); of these the two groups fix {len(R['fixed_by_groups'])} "
          f"({', '.join(R['fixed_by_groups']) or '-'}).", ""]
    return L


def report(res):
    S = res["summary"]
    A = res.get("summary_all") or S
    L = ["# Error budget: which map layer causes the wrong clubs and aims", "",
         f"Built {res['made_utc']} by `course_data/platform/error_budget.py` (quick decision n={res['n']}, seed {SEED} "
         "for every configuration: common random numbers). Re-run: `python3 course_data/platform/error_budget.py --n "
         f"{res['n']}` (decisions are cached by hole fingerprint in `error_budget_cache.json`); `--report` rewrites "
         "this file from `error_budget.json`.", "",
         "## Set-up", "",
         "* **Auto** = the automatic build with the true card (`course_data/packages/<slug>/package.json`, the builds "
         "`picks_pipeline.py` scores; Colbert Hills: `library/colbert_hills/package.json`). **Truth** = the same package "
         "with every hand-checked layer put in (truth tees, greens, hole line, card, hole numbering; the hand corridor "
         "zones over the auto zones inside the traced footprint; the elevation table sampled along the truth tee line).",
         "* **Match** = same club and the two aim points (club carry along the printed aim line) within "
         f"{AIM_TOL:.0f} yds, against the all-truth plan through the same decision. **Regret** = truth-map EV of the "
         "configuration's club at its aim point minus the truth plan's EV (strokes, summed over holes; only where the "
         f"aim point is within {SAME_PLACE:.0f} yds of the truth's, i.e. on the same hole).",
         "* **+layer** = auto with that one truth layer. **-layer** = truth with that one auto layer (does the auto layer "
         "alone break the plan?). Hazard layers are swapped as visible-lie regions (see the module docstring). "
         "**routing** = hole numbering (each number gets the auto hole whose green is that truth green, within "
         f"{ROUTE_TOL:.0f} yds, keeping the auto geometry) + the truth hole line.",
         f"* **Headline: {S['holes']} par-4/5 tee shots on the {len(res['courses']) - len(NO_CARD)} courses whose build "
         f"has the card.** Auto vs all-truth: **{S['auto_match']}/{S['holes']} match** "
         f"({100 * S['auto_match'] / max(S['holes'], 1):.0f}%), same club {S['auto_club']} "
         f"({100 * S['auto_club'] / max(S['holes'], 1):.0f}%), same club or tie {S['auto_same_or_tie']}; total regret "
         f"{S['auto_regret']} strokes. {S['misses']} misses, of which {S['misses_tie']} are reference ties (truth margin < "
         f"{TIE} strokes). National KC (no web card found, so the build numbered the holes itself: 1/14 match) is "
         "reported apart.", ""]
    L += table(S, "## The table (card courses)")
    L += ["Shares can add to more than 100%: one miss can be fixed by either of two layers.", ""]
    L += table(A, f"### All {len(res['courses'])} courses, National KC included")
    L += ["## Per course", "",
          "| course | set | tee shots | auto match | same club | regret | misses fixed by (layer: n) |",
          "|---|---|---|---|---|---|---|"]
    for c in res["courses"]:
        if "rows" not in c:
            L.append(f"| {c['slug']} | | | | | | {c.get('error')} |")
            continue
        rows = c["rows"]
        m = sum(r["configs"]["auto"]["match"] for r in rows)
        cl = sum(r["configs"]["auto"]["club"] for r in rows)
        rg = round(sum(r["configs"]["auto"]["regret"] or 0 for r in rows), 3)
        fx = {}
        for r in rows:
            if r["configs"]["auto"]["match"]:
                continue
            for Ly in LAYERS:
                if r["configs"][f"+{Ly}"]["match"]:
                    fx[Ly] = fx.get(Ly, 0) + 1
        L.append(f"| {c['slug']} | {c['tees']} | {len(rows)} | {m} | {cl} | {rg} | "
                 f"{', '.join(f'{k}: {v}' for k, v in sorted(fx.items(), key=lambda kv: -kv[1])) or '-'} |")
    L += ["", f"Not scored: " + "; ".join(f"{k} ({v})" for k, v in NOT_SCORED.items()), "",
          "## Every miss", "",
          "| hole | truth plan | auto plan | aim apart | regret | fixed by | tee / green err | layer evidence (corridor, sq yds missing / extra) |",
          "|---|---|---|---|---|---|---|---|"]
    for c in res["courses"]:
        for r in c.get("rows") or []:
            a = r["configs"]["auto"]
            if a["match"]:
                continue
            fixed = [Ly for Ly in LAYERS if r["configs"][f"+{Ly}"]["match"]]
            grp = [g for g in GROUPS if r["configs"][f"+{g}"]["match"]]
            g = r["geo"]
            ev = []
            for Ly, d in (g.get("layers") or {}).items():
                if d["missing"] + d["extra"] >= 150:
                    s = f"{Ly} -{d['missing']}"
                    if d["missing_side"] is not None and d["missing"] >= 150:
                        s += f" ({'R' if d['missing_side'] > 0 else 'L'}{abs(d['missing_side']):.0f})"
                    s += f"/+{d['extra']}"
                    if d["extra_side"] is not None and d["extra"] >= 150:
                        s += f" ({'R' if d['extra_side'] > 0 else 'L'}{abs(d['extra_side']):.0f})"
                    ev.append(s)
            t = r["truth"]
            L.append(f"| {c['slug']} {r['hole']} | {t['pick']} {t['aim']:+.0f}{' (tie)' if t['tie'] else ''} | "
                     f"{a.get('pick')} {a.get('aim', 0):+.0f} | {a.get('aim_dist')} | {a.get('regret')} | "
                     f"{', '.join(fixed) or ('groups: ' + ', '.join(grp) if grp else 'none')} | "
                     f"{g.get('tee_err')} / {g.get('green_err')} | {'; '.join(ev)} |")
    L += ["", "Layer evidence: area of that layer in the truth tee shot's landing corridor (180-320 yds along the truth "
          "tee line, +/-50 yds) that the truth has and the auto map lacks (-) / the auto map has and the truth lacks (+); "
          "L/R n = the mean side of that area, yds left / right of the line.", ""]
    L += ["## Honesty notes", "",
          f"* n = {res['n']} swings per club and aim, not the scoreboard's 8000: 26 configurations x 152 holes on a shared "
          "4-core box. Every configuration uses the same seed, so a changed pick is a changed map; picks with a margin "
          "under 0.01 strokes are marked as reference ties.",
          "* The all-truth plan here is the hand map in the package through the quick decision, for every course. It is not "
          "the scoreboard's truth (Spirit Hollow's Bayesian final_decision.json; Veenker / Coldwater / Ellis rough "
          "outside the corridor). So the 89% same club here does not compare one to one with PIPELINE.md section 5's 77.5%.",
          "* Elevation has no hand truth: both sides sample the same 3DEP DEM, so the elevation layer only tests the "
          "table along the wrong tee line. Colbert Hills' truth has no trees, OB or long grass, so those stay auto there.",
          "* The hand corridor maps cover 150-340 yds of each tee shot. Lies outside the footprint are the auto map's in "
          "the truth too, so a layer error outside the corridor is not counted.",
          "* Mozingo Lake is not scored: its hand map is in screenshot pixels. `vision_any/register_mozingo.py` may give "
          "the WGS84 registration needed to add it.", ""]
    if res.get("recommendation"):
        L += ["## Recommendation", "", res["recommendation"], ""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--courses")
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.report:
        res = rj(OUT_JSON)
        res["summary"] = summarise(res["courses"], NO_CARD)
        res["summary_all"] = summarise(res["courses"])
        json.dump(res, open(OUT_JSON, "w"), indent=1, default=float)
        open(OUT_MD, "w").write(report(res))
        return
    want = set(a.courses.split(",")) if a.courses else None
    cache = rj(CACHE_JSON, {}) or {}
    old = rj(OUT_JSON) or {}
    prev = {c["slug"]: c for c in old.get("courses", []) if old.get("n") == a.n}
    for cfg in COURSES:
        if want and cfg["slug"] not in want:
            continue
        t0 = time.time()
        print(f"== {cfg['slug']} ({cfg['tees']})", flush=True)
        try:
            prev[cfg["slug"]] = score_course(cfg, a.n, a.workers, cache)
        except Exception as e:                           # noqa: BLE001
            import traceback
            prev[cfg["slug"]] = dict(slug=cfg["slug"], error=f"{type(e).__name__}: {e}", trace=traceback.format_exc()[-2000:])
            print(prev[cfg["slug"]]["trace"])
        json.dump(cache, open(CACHE_JSON, "w"))
        c = prev[cfg["slug"]]
        if "rows" in c:
            print(f"  {cfg['slug']}: auto match {sum(r['configs']['auto']['match'] for r in c['rows'])}/{len(c['rows'])} "
                  f"({time.time() - t0:.0f} s)", flush=True)
    order = [c["slug"] for c in COURSES]
    courses = [prev[s] for s in order if s in prev]
    res = dict(schema="error_budget/1", made_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ"), n=a.n,
               aim_tol=AIM_TOL, tie=TIE, layers=LAYERS, groups=GROUPS, not_scored=NOT_SCORED, courses=courses)
    res["summary"] = summarise(courses, NO_CARD)
    res["summary_all"] = summarise(courses)
    res["recommendation"] = old.get("recommendation")       # hand-written from the numbers (kept across runs)
    json.dump(res, open(OUT_JSON, "w"), indent=1, default=float)
    open(OUT_MD, "w").write(report(res))
    print(json.dumps({k: v for k, v in res["summary"].items() if k != "layers"}, default=str))


if __name__ == "__main__":
    main()
