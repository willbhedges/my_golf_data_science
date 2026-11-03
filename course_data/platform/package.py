"""Any-course package builder (offline): request + fetched raw data -> course_data/packages/<slug>/.

  python course_data/platform/package.py build course_data/requests/package_mozingo_lake.json [--render]
  python course_data/platform/package.py run   course_data/requests/package_*.json    # fetch (Actions) + build

Pipeline (ARCHITECTURE.md stages; every stage is the existing team module, imported, not rewritten):
  S0/S1   raw/course.json, raw/osm.geojson         resolve.py, fetch_package.py (Actions)
  S1 card scorecard.py: request yardages > request["scorecard"] file (tees/ format) > the web cards by source
          reliability (club site > golfify > OpenGolfAPI; the first that passes scorecard.consistency, never the
          best fit to the map); the others are kept as a per-hole cross-check;
          > a golfer-typed card (request "typed_card": {"yards": "391 175 ...", "pars": "..."}, typed_card.py);
          no card -> the OSM tee nearest each hole-line start (usually the back tee) + a warning
          sanity.card_order: OSM refs 1..18 that walk as a round keep their order; a card far off them in that
          order is dropped ("card did not match the mapped holes", CHECK); else renumber_holes as before
          request "card": "none" (CARD-BLIND, cardless_card): every web / local / request / typed card and the
          card-based review overrides are ignored; the card is synthetic: tees/cardless.py if present, else the
          OSM hole lines (back = line length, 2nd set = back x CARDLESS_SET2_RATIO, par = OSM tag > length).
          That fallback card drives routing; after routing, tees/cardless.infer_card (cardless_infer) on every
          routed hole line + OSM tee boxes + lidar pads replaces it (request "cardless": "fallback" keeps it).
          Default behaviour (no "card" key) is unchanged. platform/CARDBLIND.md scores it (cardblind_eval.py)
          request "yardage_overrides" {ref: {set | "*": yds}} / "par_overrides" {ref: par} patch the chosen card
          (course reviews, library/review_fixes.py); "*" or a set not on the card = the chosen set
  S2a holes  stage selector (stage_select.py, PIPELINE.md) for holes OSM has no golf=hole way for: data tier
          (OSM greens / tees mapped?, card?) -> routing v2 + structure-solver prior (structure on OSM, or on the
          perception scene when OSM lacks greens / tees) > routing v2 > structure > geometry fallback, on any
          error; golfer-confirm payload -> confirm.json; package.pipeline records what ran
  S2 tees (default) tees/localize.py - OSM boxes + lidar pads + DEM/NAIP texture pads + segment-model /
          perception tee detections merged into one pad list, joint chain assignment, per-set uncertainty
          (holes[].tees[set].uncertainty); any failure falls back to v1 (stages.tee_localizer says which ran)
  S2 v1   (request "tee_localizer": "v1" or env TEE_LOCALIZER=v1, or the v2 fallback)
          tees/place_tee.place_course_sets: every set on a hole assigned together, back to front, distances
          to the OSM green centroid along the hole line; lidar flat-pad candidates (tees/lidar_pads.py, the
          3DEP DEM) where a set has no OSM box; walk-back if nothing fits. An OSM tee box tagged with the
          set's colour wins ("tagged")
  S2n     request "hole_renumber" {old: new | {to, near_ll}} renames hole ways / routed holes after S2a (a review
          found OSM or the router numbered them unlike the card); "green_overrides" {ref: [lat, lon]} ends the hole
          line on a review green (re-drawn from the review tee when it moves > GREEN_MOVE_YD; a missed hole is added)
  S2r     request "tee_overrides" {ref: {set: [lat, lon]}} (course reviews): that set's tee on that hole: kept
          when inside an OSM tee box, else moved onto the nearest box within OVERRIDE_SNAP_YD along its long axis
          (not to its centroid; else the point as given) unless the snapped point measures further from the set's
          card yardage (and > SNAP_CARD_TOL_YD off), or lands on a box another set holds and worsens the card
          match (review_tee_point: the reviewer put it off the box on purpose); wins over S2 (method "review")
  S3     geometry/build_holes.py: yard frame (package) + fitted pixel frame (images / the book)
  S4      course_data/vision_any/gapfill.py:gapfill(package, imagery_dir) if present (trees, long grass)
  S4f     course_data/vision_any/fairway_fill.py:fill_package(package, osm) for par-4/5 holes with no fairway in the
          landing corridor after OSM + segment: NAIP mown-turf LDA self-supervised on the hole lines (no OSM fairway
          used), course gate d' >= MIN_DPRIME, per-hole cover / width / share gates; src "fairway_fill:naip",
          stages.fairway_fill; request "fairway_fill": false turns it off
  S4c     course_data/ob/infer.py:apply_ob(package) when the course's OB evidence is fetched (call_ob)
  S4b     course_data/segment/gapfill.py:segment_gapfill(package, segment.geojson) when the segment workflow
          has run for the slug (requests/segment_<slug>.json): NAIP U-Net fairway / bunker / green + NIR water
          ONLY where OSM lacks them (never overrides OSM), src "segment:*", p, flags, stages.segment
  S5      request "agent_layers": "course_data/mapper/<slug>/" (course_data/mapper/BRIEF.md): the mapper agent's
          zone edits + tee checks (agent_zones.geojson, agent_tees.json) laid over the built package by
          course_data/mapper/apply.py after the vision / segment / OB layers; package.agent_layers, stages.agent_layers,
          holes[].provenance.agent record them. A missing folder or a failure is a warning, never a failed build
  S6      confidence per hole (pipeline.confidence), coverage stats, elevation (3DEP DEM + elevation/adjust.py)
Outputs in packages/<slug>/:
  package.json    the self-contained course package (schema course_package/1, below)
  course_auto.py  HOLES / PAR3 / ORDER / LABELS / NOTES / AIM_AT (spirit_hollow/course.py API, pixel frame)
  qa.md           per-hole confidence + flags, coverage, warnings
  screenshots/    holeNN.png in each hole's pixel frame (--render; needs the imagery)

package.json (course_package/1):
  course     {name, slug, osm{type,id}, center[lon,lat], bbox[w,s,e,n], boundary (GeoJSON MultiPolygon, every
              outer ring of the OSM course), town, state,
              website, holes_mapped, candidates}
  request    the request file as given
  tee_set    the chosen set's key; tee_set_info {requested, chosen, how, colour, substituted, warning}: a requested
              set that is not on the card is an error unless the request says "allow_substitute": true
              (CLI --allow-substitute); then the substitute is named in warning, warnings and qa.md
  tee_sets   {Name: {colour, aliases, yards[], par[], total, rating, slope, source}} (all sets on the card)
  scorecard  {source, url, kind, confidence, tried}
  frame      "yard": x = yds right of the tee line, y = -yds along it, tee (0,0), dot270 (0,-270)
  holes      {ref: {ref, par, length (card), measured_length, handicap, tee_ll, aim_ll, green_ll [lon,lat],
              bearing_deg (true, tee->aim), green_bearing_deg, tee, dot270, green, hole_line, green_polygon,
              zones [[lie, [[x,y],...]], ...] (later wins), zone_src [...], par3 {...} (par 3s),
              pixel {ppy, tee_px, size}, tee_choice, tee_options, elevation {...},
              provenance {tee|green|par|length|zones|bearing: {source, confidence}},
              confidence {score, band, osm, imagery, inferred, flags}, landing_lies {lie: share}, image}}
  imagery    {dir, source, year, acquired, resolution_m, crs, files} | null
  elevation  {file, source, resolution_m} | null
  coverage   osm_coverage.coverage(...)
  stages, warnings, built, attribution
  pipeline   {tier, profile (OSM greens / tees / hole ways, card, scene), card {kind}, holes {method, chosen, tried,
              fallbacks, lam, router_inputs, structure_input} | {method: "osm"}, tees {method, requested, status},
              confirm {file, questions}} - which method ran at each stage (PIPELINE.md)
"""
import argparse
import copy
import datetime as dt
import glob
import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [HERE, CD]
import osm_coverage  # noqa: E402
import platform_common as pc  # noqa: E402
import sanity  # noqa: E402
import scorecard as scm  # noqa: E402
import tee_line as tl  # noqa: E402

SCHEMA = "course_package/1"
W, H = 920, 2000
_MODS = {}


def load(path, name):
    """Import a team module by path (cached); None if it is absent or fails to import."""
    if name in _MODS:
        return _MODS[name]
    mod = None
    if os.path.exists(path):
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
        except Exception as e:                                   # noqa: BLE001
            pc.log(f"! could not import {path}: {type(e).__name__}: {e}")
            mod = None
    _MODS[name] = mod
    return mod


def geometry():
    return load(os.path.join(CD, "geometry", "build_holes.py"), "cdp_build_holes")


def naip_years_mod():
    return load(os.path.join(CD, "imagery", "naip_years.py"), "cdp_naip_years")


def check_green_visibility(holes, img_dir, imagery, stages, warnings):
    """Is every hole's green actually visible as turf on the imagery the package ships? (imagery/naip_years.
    green_visibility: per-green NDVI vs the course's other greens.) A green drawn from OSM on bare soil - a course
    flown mid-renovation (Wakonda NAIP 2023: greens 5, 9, 15, 17), a dead green, a green built after the flight -
    is the app's "green not drawn" report: the outline sits on dirt. Sets hole["green_visibility"]; reframe()
    turns visible=False into a confidence flag."""
    mod = naip_years_mod()
    if mod is None or not img_dir or not imagery:
        stages["green_visibility"] = "not run (no imagery)" if mod else "missing (imagery/naip_years.py)"
        return
    try:
        vis = mod.green_visibility(holes, img_dir)
    except Exception as e:                                       # noqa: BLE001
        stages["green_visibility"] = f"failed ({type(e).__name__}: {e})"[:300]
        return
    if not vis:
        stages["green_visibility"] = "not run (no NIR band)"
        return
    bad = [k for k, v in vis.items() if v.get("visible") is False]
    for k, v in vis.items():
        holes[k]["green_visibility"] = dict(v, year=imagery.get("year"))
    stages["green_visibility"] = (f"ok: {len(vis) - len(bad)}/{len(vis)} greens visible as turf on NAIP "
                                  f"{imagery.get('year')}" + (f"; NOT visible: holes {', '.join(bad)}" if bad else ""))
    if bad:
        warnings.append(f"greens of holes {', '.join(bad)} are not visible as turf on the NAIP {imagery.get('year')} "
                        "imagery (bare soil / construction / dead turf): pick another NAIP year (imagery/naip_years.py)")


def pipeline():
    return load(os.path.join(CD, "pipeline.py"), "cdp_pipeline")


def place_tee_mod():
    return load(os.path.join(CD, "tees", "place_tee.py"), "cdp_place_tee")


# ----------------------------------------------------------------------------- scorecard
def card_confidence(kind, consistent=True):
    c = scm.CARD_CONFIDENCE.get(kind, 0.0)
    return round(c if consistent else min(c, 0.6), 2)


def _cross(card, web_cards, own_kind):
    """Per-hole cross-check of the chosen card against every other web card (scorecard.cross_check)."""
    out = {}
    for c in web_cards:
        if c["source"] == own_kind or not c.get("card"):
            continue
        cc = scm.cross_check(card, scm.normalise(c["card"]))
        if cc:
            out[c["source"]] = cc
    return out


CONSENSUS_MIN_HOLES = 9     # OSM hole lines the consensus needs before it may overrule source reliability


def card_ground(fc, raw_dir):
    """card_consensus ground at build time: OSM hole lines + nearby tee boxes (fc), else raw/summary.json."""
    import card_consensus as cc
    g = cc.ground_from_fc(fc) if fc else {}
    if not g:
        g = cc.ground_from_summary(pc.read_json(os.path.join(raw_dir, "summary.json"), {}) or {})
    return g


def consensus_card(web_cards, ground, overrides=None):
    """-> (card, info) from card_consensus.consensus over the web cards (metres -> yards, swapped set names moved
    back, a stale / scrambled card never the base, per-hole fixes on the OSM ground), or None when the ground is
    too thin (fewer than CONSENSUS_MIN_HOLES hole lines) or no card is usable."""
    import card_consensus as cc
    if sum(1 for g in ground.values() if g.get("line")) < CONSENSUS_MIN_HOLES or not web_cards:
        return None
    try:
        res = cc.consensus([(c["source"], c["card"], c.get("url")) for c in web_cards], ground, overrides)
    except Exception:                                            # noqa: BLE001  (advisory: fall back to choose_card)
        return None
    if not res or not res.get("card"):
        return None
    info = dict(kind=res["base"], source=res["base"], url=res.get("base_url"),
                consensus=dict(changes=res["changes"], flags=res["flags"], method="card_consensus.py"))
    return scm.normalise(res["card"]), info


def pick_scorecard(req, raw_dir, fc=None):
    """-> (card | None, info dict). Order: request yardages > request scorecard file > web cards by
    scorecard.RELIABILITY (club site > golfify > OpenGolfAPI), the first that passes scorecard.consistency
    (else the most reliable, flagged). info carries consistency (flags) and the cross-check vs the other cards."""
    tried = []
    web = pc.read_json(os.path.join(raw_dir, "scorecard_web.json"), {}) or {}
    web_cards = [c for c in web.get("cards", []) if c.get("card")]
    card, info = None, None
    if req.get("yardages"):
        card = scm.card_from_yardages(req["yardages"], req.get("pars"),
                                      name=req.get("tee_set") or req.get("tees") or "request")
        info = dict(kind="request", source="request file yardages", url=None)
    if card is None and req.get("scorecard"):
        p = req["scorecard"] if os.path.isabs(req["scorecard"]) else os.path.join(pc.ROOT, req["scorecard"])
        c = pc.read_json(p)
        if c:
            card = scm.normalise(c)
            url = card.get("source") if isinstance(card.get("source"), str) else None
            info = dict(kind="file", source=os.path.relpath(p, pc.ROOT), url=url)
        else:
            tried.append(dict(source=req["scorecard"], ok=False, info="file missing or unreadable"))
    tried += web.get("tried", [])
    ground = card_ground(fc, raw_dir) if (fc or raw_dir) else {}
    if card is not None and ground:                     # an explicit card wins; only its units are checked
        others = [scm.normalise(c["card"]) for c in web_cards]
        try:
            import card_consensus as cc
            card2, unit_flag = cc.check_units(scm.normalise(card), ground, others)
        except Exception:                                        # noqa: BLE001
            card2, unit_flag = card, None
        if unit_flag:
            card = card2
            info["units"] = unit_flag
    if card is None:
        cons = consensus_card(web_cards, ground, req.get("yardage_overrides"))
        if cons:
            card, info = cons
    if card is None:
        pick = scm.choose_card([(c["source"], scm.normalise(c["card"]), c.get("url")) for c in web_cards])
        if pick:
            kind, card, url, _ = pick
            info = dict(kind=kind, source=kind, url=url)
    if card is None and req.get("typed_card"):
        # no card online: the golfer's typed yardages (+ pars), strictly validated (typed_card.py)
        import typed_card as tc
        t = req["typed_card"] if isinstance(req["typed_card"], dict) else dict(yards=req["typed_card"])
        c, issues = tc.parse_typed_card(t.get("yards"), t.get("pars"), tee=t.get("tee") or req.get("tees") or "Typed",
                                        unit=t.get("unit", "yd"), total=t.get("total"))
        if c:
            card = scm.normalise(c)
            info = dict(kind="typed", source="typed by golfer", url=None, typed_issues=issues)
        else:
            tried.append(dict(source="typed_card", ok=False, info="; ".join(i["msg"] for i in issues)[:300]))
    if card is None:
        return None, dict(kind=None, source=None, url=None, tried=tried, consistency=None, cross_check={})
    chk = scm.consistency(card)
    info.update(tried=tried, consistency=chk, cross_check=_cross(card, web_cards, info["kind"]),
                attribution=card.get("attribution"))
    return card, info


# ----------------------------------------------------------------------------- card-blind ("card": "none")
CARD_INPUT_KEYS = ("yardages", "pars", "scorecard", "typed_card", "yardage_overrides", "par_overrides",
                   "tee_set", "tees", "local_scorecard")
CARDLESS_SET2_RATIO = 0.94       # 2nd set / back set, per hole (fallback only: no tees/cardless.py)
CARDLESS_FUNCS = ("synthetic_card", "cardless_card", "build_card", "make_card", "card")


def card_blind(req):
    return str(req.get("card") or "").strip().lower() in ("none", "blind", "cardless")


def strip_card_inputs(req):
    """The request without anything that encodes a card (card:none never sees a card)."""
    out = {k: v for k, v in req.items() if k not in CARD_INPUT_KEYS}
    out["local_scorecard"] = False
    return out


def par_from_length(yds):
    return 3 if yds < 250 else 4 if yds < 480 else 5


def cardless_fallback(fc):
    """Synthetic card from the OSM hole lines alone: back = line length, 2nd = back x CARDLESS_SET2_RATIO, par =
    OSM par tag (if 3-6) else from length. None when OSM has no numbered hole lines."""
    lines = osm_lines(fc)
    tags = {str(f["properties"]["ref"]): f["properties"] for f in fc["features"]
            if f["properties"].get("golf") == "hole" and f["properties"].get("ref")}
    refs = [r for r in lines if str(r).isdigit()]
    if not refs:
        return None
    n = max(int(r) for r in refs)
    n = 18 if 9 < n <= 18 else 9 if n <= 9 else n
    back, pars = [None] * n, [None] * n
    for r in refs:
        i = int(r) - 1
        if i >= n:
            continue
        L = lines[r]
        y = sum(_yd(L[j], L[j + 1]) for j in range(len(L) - 1))
        back[i] = int(round(y))
        tp = str(tags.get(r, {}).get("par", ""))
        pars[i] = int(tp) if tp.isdigit() and 3 <= int(tp) <= 6 else par_from_length(y)
    card = scm.card_from_yardages(back, pars, name="Back", source="cardless: OSM hole-line lengths")
    card["tee_sets"]["Second"] = dict(colour="second", aliases=["second"], source=card["source"],
                                      yards=[int(round(y * CARDLESS_SET2_RATIO)) if y else None for y in back])
    card["tee_sets"]["Second"]["total"] = sum(y for y in card["tee_sets"]["Second"]["yards"] if y)
    return card


def cardless_card(fc, course, raw_dir, req):
    """card:none -> (card | None, info). tees/cardless.py (first function of CARDLESS_FUNCS it defines, called
    with whichever of fc, course, raw_dir, req it accepts; returns a scorecard/1 card or (card, info)), else
    cardless_fallback. Never reads raw/scorecard_web.json."""
    import inspect
    mod = load(os.path.join(CD, "tees", "cardless.py"), "cdp_cardless")
    tried = []
    fn = next((getattr(mod, f) for f in CARDLESS_FUNCS if mod and callable(getattr(mod, f, None))), None)
    if fn is not None:
        try:
            have = dict(fc=fc, course=course, raw_dir=raw_dir, req=req)
            sig = inspect.signature(fn).parameters
            kw = {k: v for k, v in have.items() if k in sig}
            res = fn(**kw) if kw else fn(fc)
            card, extra = res if isinstance(res, tuple) else (res, {})
            if card and card.get("tee_sets"):
                info = dict(kind="cardless", source=f"tees/cardless.py:{fn.__name__}", url=None)
                info.update({k: v for k, v in (extra or {}).items() if k not in info})
                return scm.normalise(card), dict(info, tried=tried, consistency=None, cross_check={})
            tried.append(dict(source="tees/cardless.py", ok=False, info="no tee sets returned"))
        except Exception as e:                                   # noqa: BLE001  fall back to the OSM lines
            tried.append(dict(source="tees/cardless.py", ok=False, info=f"{type(e).__name__}: {e}"[:300]))
    else:
        tried.append(dict(source="tees/cardless.py", ok=False, info="absent" if mod is None else "no card function"))
    card = cardless_fallback(fc)
    if card is None:
        return None, dict(kind=None, source=None, url=None, tried=tried, consistency=None, cross_check={})
    return scm.normalise(card), dict(kind="cardless", source="osm hole lines (platform/package.cardless_fallback)",
                                     url=None, tried=tried, consistency=None, cross_check={})


def _ring_yd(ring, o):
    """[(lat, lon)] -> [(x, y)] yds about o (lat, lon)."""
    kx = math.cos(math.radians(o[0])) * 111320 / 0.9144
    return [((q[1] - o[1]) * kx, (q[0] - o[0]) * 111320 / 0.9144) for q in ring]


def _green_at(end, greens, max_yd=40.0):
    """(centre (lat, lon), equal-area radius yds) of the OSM green nearest a hole line's end, else (end, None)."""
    best = None
    for g in greens:
        xy = _ring_yd(g["coords"], end)
        a = cx = cy = 0.0
        for (x0, y0), (x1, y1) in zip(xy, xy[1:] + xy[:1]):
            c = x0 * y1 - x1 * y0
            a, cx, cy = a + c, cx + (x0 + x1) * c, cy + (y0 + y1) * c
        if abs(a) < 1e-6:
            continue
        cx, cy = cx / (3 * a), cy / (3 * a)
        d = math.hypot(cx, cy)
        if d <= max_yd and (best is None or d < best[0]):
            kx = math.cos(math.radians(end[0])) * 111320 / 0.9144
            best = (d, (end[0] + cy * 0.9144 / 111320, end[1] + cx / kx), math.sqrt(abs(a) / 2 / math.pi))
    return (best[1], best[2]) if best else (tuple(end), None)


def cardless_inputs(fc, pads=()):
    """tees/cardless.infer_card inputs from the (routed) package OSM, as tees/eval_cardless.course_inputs builds
    them: holes [{ref, line [(lat, lon)] tee -> green, green (lat, lon), green_r_yd}], OSM tee boxes [{id, coords}]
    (osm_tee_inputs), pads [{id, coords, source}]."""
    lines, tees, greens = osm_tee_inputs(fc)
    holes = []
    for r in sorted((r for r in lines if str(r).isdigit()), key=int):
        g, gr = _green_at(lines[r][-1], greens)
        holes.append(dict(ref=int(r), line=lines[r], green=g, green_r_yd=gr))
    boxes = [dict(id=f"osm/{t['id']}", coords=t["coords"]) for t in tees]
    pads = [dict(id=q.get("id"), coords=[tuple(c) for c in q["coords"]], source=q.get("source", "lidar"))
            for q in pads or () if q.get("coords")]
    return holes, boxes, pads


def cardless_infer(fc, req, pkg_dir, slug, routed=None):
    """card:none after routing: tees/cardless.infer_card on every routed hole line (+ OSM tee boxes, + lidar pads
    from the package DEM) -> (card on hole numbers 1..n with None for unrouted holes, info) or (None, reason).
    Hybrid: holes whose line is an OSM golf=hole way (not in `routed`, the refs the router placed) are anchored
    (infer_card anchored=: no Back on a box far behind the way's start); request "cardless": "unanchored" treats
    every line as a router line. Default: only when the router placed some holes (else the hole-line card stays;
    "cardless": "hybrid" forces infer_card)."""
    mode = str(req.get("cardless") or "").lower()
    if mode == "fallback":
        return None, "request cardless: fallback"
    if not routed and mode not in ("hybrid", "unanchored", "v2"):
        # default: where OSM maps every hole the hole-line card stays (CARDBLIND.md: the hybrid did not beat it on
        # the 13 mapped courses); request "cardless": "hybrid" runs infer_card there too
        return None, "OSM maps every hole: hole-line card kept (request cardless: hybrid to infer the card)"
    mod = load(os.path.join(CD, "tees", "cardless.py"), "cdp_cardless")
    if mod is None or not callable(getattr(mod, "infer_card", None)):
        return None, "tees/cardless.py infer_card not available"
    try:
        img_dir = find_imagery(req, pkg_dir, slug)
        _, elevation = imagery_ref(img_dir)
        pads, _ = lidar_pads(fc, os.path.join(pc.ROOT, elevation["file"]) if elevation else None) \
            if req.get("lidar_tees", True) else ([], "not run")
        holes, boxes, pads = cardless_inputs(fc, pads)
        if not holes:
            return None, "no numbered hole lines"
        routed = {str(r) for r in (routed or {})}
        anchored = None if mode == "unanchored" else [str(h["ref"]) not in routed for h in holes]
        import inspect
        if "anchored" in inspect.signature(mod.infer_card).parameters:
            c = mod.infer_card(holes, boxes, pads=pads, anchored=anchored)
        else:                                                # a cardless.py without the hybrid (v1)
            c = mod.infer_card(holes, boxes, pads=pads)
        n = max(h["ref"] for h in holes)
        n = 18 if 9 < n <= 18 else 9 if n <= 9 else n
        idx = [h["ref"] - 1 for h in holes]

        def spread(vals):
            out = [None] * n
            for i, v in zip(idx, vals):
                if i < n:
                    out[i] = v
            return out
        sets = {}
        for nm, ts in (c.get("tee_sets") or {}).items():
            ys = spread([int(round(y)) if y else None for y in ts["yards"]])
            sets[nm] = dict(colour=nm.lower(), aliases=[nm.lower()], yards=ys, total=sum(y for y in ys if y),
                            source=c.get("source"), ratio=ts.get("ratio"), inferred=True)
        if not sets:
            return None, "infer_card returned no tee sets"
        card = dict(schema="scorecard/1", source=c.get("source"), par=spread(c.get("par") or []), handicap=None,
                    tee_sets=sets, inferred=True)
        diag = c.get("diagnostics") or {}
        return scm.normalise(card), dict(kind="cardless", source=f"{c.get('source')} (tees/cardless.infer_card)",
                                         url=None, consistency=None, cross_check={},
                                         cardless=dict(S=diag.get("S"), n_pads=len(pads), n_boxes=len(boxes),
                                                       holes=len(holes),
                                                       anchored=sum(anchored) if anchored else 0))
    except Exception as e:                                       # noqa: BLE001  keep the pre-routing fallback card
        return None, f"infer_card failed: {type(e).__name__}: {e}"[:300]


# ----------------------------------------------------------------------------- review overrides
OVERRIDE_SNAP_YD = 15.0


def override_set(name, card_sets, chosen):
    """The card's set a review names: exact, case-insensitive, colour or alias ('osm_back (= Championship)' is
    looked up as 'osm_back' and 'Championship'); '*' and page-only names (Web, osm_back) -> the chosen set."""
    if name in (card_sets or {}):
        return name
    keys = {str(name).split("(")[0].strip().lower()}
    if "=" in str(name):
        keys.add(str(name).split("=", 1)[1].strip(" )").lower())
    for s, v in (card_sets or {}).items():
        if keys & ({s.lower(), str(v.get("colour") or "").lower()} | {str(a).lower() for a in v.get("aliases") or []}):
            return s
    return chosen


def apply_card_overrides(card, req, chosen):
    """Request yardage_overrides / par_overrides into the card (copy). -> (card, [notes])."""
    yo, po = req.get("yardage_overrides") or {}, req.get("par_overrides") or {}
    if not card or not (yo or po):
        return card, []
    card = copy.deepcopy(card)
    sets, notes = card.get("tee_sets") or {}, []
    for ref, by in yo.items():
        if not str(ref).isdigit():
            continue
        i = int(ref) - 1
        for name, y in (by if isinstance(by, dict) else {"*": by}).items():
            s = override_set(name, sets, chosen)
            if s not in sets or not y or i >= len(sets[s].get("yards") or []):
                continue
            if sets[s]["yards"][i] != int(y):
                notes.append(f"hole {ref} {s}: card {sets[s]['yards'][i]} -> {int(y)} yds (review)")
                sets[s]["yards"][i] = int(y)
                sets[s]["total"] = sum(v for v in sets[s]["yards"] if v)
    for ref, par in po.items():
        if not str(ref).isdigit() or not par:
            continue
        i = int(ref) - 1
        for lst in [card.get("par")] + [v.get("par") for v in sets.values()]:
            if isinstance(lst, list) and i < len(lst) and lst[i] != int(par):
                if lst is card.get("par"):
                    notes.append(f"hole {ref}: par {lst[i]} -> {int(par)} (review)")
                lst[i] = int(par)
    return card, notes


def apply_cardless_overrides(fc, req):
    """No card (osm_back page): request par_overrides into the OSM hole lines' par tags (copy), so geometry and the
    page take the review's par (apply_card_overrides has no card to patch: Sycamore Ridge 14 stayed par 3).
    Single-set yardage_overrides have no card number to replace (the length is measured) and are noted.
    -> (fc, [notes])."""
    po, yo = req.get("par_overrides") or {}, req.get("yardage_overrides") or {}
    notes = []
    if not (po or yo):
        return fc, notes
    fc = copy.deepcopy(fc)
    holes = {str(f["properties"].get("ref")): f for f in fc["features"]
             if f["properties"].get("golf") == "hole" and f["properties"].get("ref")}
    for ref, par in po.items():
        f = holes.get(str(ref))
        if f is None or not str(par).isdigit():
            notes.append(f"hole {ref}: par {par} not applied (no hole line, no card)")
            continue
        old = f["properties"].get("par")
        if str(old) != str(int(par)):
            f["properties"]["par"] = str(int(par))
            notes.append(f"hole {ref}: par {old or '?'} -> {int(par)} (review, no card)")
        f["properties"]["review_par"] = True
    if yo:
        notes.append(f"yardage_overrides on {len(yo)} hole(s) not applied: no card (lengths are measured)")
    return fc, notes


def _nearest_tee_box(lat, lon, tees, snap_yd):
    """(d, xy, poly, id) of the nearest OSM tee box within snap_yd of (lat, lon) (yds, the point at (0, 0)), or None."""
    kx, ky = math.cos(math.radians(lat)) * 111320 / 0.9144, 111320 / 0.9144
    best = None
    for t in tees:
        cs = np.array(t["coords"], float)
        if len(cs) > 2 and np.allclose(cs[0], cs[-1]):
            cs = cs[:-1]
        xy = np.c_[(cs[:, 1] - lon) * kx, (cs[:, 0] - lat) * ky]          # yds, the review point at (0, 0)
        if len(xy) >= 3:
            from shapely.geometry import Point as SPt
            from shapely.geometry import Polygon as SPoly
            poly = SPoly(xy).buffer(0)
            d = float(poly.distance(SPt(0.0, 0.0)))
        else:
            poly, d = None, float(np.hypot(*xy.mean(0)))
        if d <= snap_yd and (best is None or d < best[0]):
            best = (d, xy, poly, t["id"])
    return best


def snap_to_tee_box(lat, lon, tees, snap_yd=None):
    """(lat, lon, how) for an approximate review tee point and the OSM tee boxes [{id, coords [(lat, lon)]}].

    Inside a box: the point stays (a long teeing ground holds several sets; hodge_park 3 had two review points
    11-12 yds apart on one box both jump to its centroid). Else, within snap_yd of a box's outline (nearest box):
    the point moves onto the box along its long axis (projected onto the axis through the centroid, clamped to the
    box's extent along it), not to the centroid. A point box (OSM node): its position. None: no box near.
    Whether the snapped point is used is review_tee_point's call (card yardage, boxes other sets hold)."""
    snap_yd = OVERRIDE_SNAP_YD if snap_yd is None else snap_yd
    kx, ky = math.cos(math.radians(lat)) * 111320 / 0.9144, 111320 / 0.9144
    best = _nearest_tee_box(lat, lon, tees, snap_yd)
    if best is None:
        return None
    d, xy, poly, tid = best
    if poly is not None and d == 0.0:
        return lat, lon, f"review (inside OSM tee {tid})"
    c = np.array(poly.centroid.coords[0]) if poly is not None else xy.mean(0)
    if poly is not None:
        _, vec = np.linalg.eigh(np.cov((xy - c).T))
        u = vec[:, -1]                                                   # long axis
        s = (xy - c) @ u
        q = c + float(np.clip(-c @ u, s.min(), s.max())) * u          # the point's projection, on the box
        how = f"review (snapped {d:.0f} yds along OSM tee {tid})"
    else:
        q, how = c, f"review (snapped {d:.0f} yds to OSM tee {tid})"
    return lat + q[1] / ky, lon + q[0] / kx, how


SNAP_CARD_TOL_YD = 3.0        # a snapped review tee within this of the set's card yardage is always fine
SNAP_WORSE_YD = 1.0           # ... onto a box another set holds: only if the card match is not worse than this
OCCUPIED_YD = 3.0             # another set's tee this close to a box's outline holds that box


def review_tee_point(lat, lon, tees, measure=None, card_yd=None, others=(), snap_yd=None):
    """(lat, lon, how) for one review tee point: snap_to_tee_box, then the card check. The reviewer may put a
    point off every box on purpose (la_nickell 5 Blue: 12 yds behind the White box, measuring the card's 325;
    snapped onto White's box it measured 313). With measure (lon, lat -> yds along the hole, or None) and the set's
    card yardage, the snapped point is used only when it measures closer to the card than the review point, or
    within SNAP_CARD_TOL_YD of it; and never onto a box another set's tee holds (others [(lat, lon)], within
    OCCUPIED_YD of its outline) when the card match gets worse by more than SNAP_WORSE_YD. Without a measure or a
    card number the snap stands (the 11-02 rule). Kept points say why in `how`."""
    snap_yd = OVERRIDE_SNAP_YD if snap_yd is None else snap_yd
    snap = snap_to_tee_box(lat, lon, tees, snap_yd)
    if snap is None:
        return lat, lon, "review"
    if "inside OSM tee" in snap[2] or measure is None or not card_yd:
        return snap
    l0, l1 = measure(lon, lat), measure(snap[1], snap[0])
    if l0 is None or l1 is None:
        return snap
    e0, e1 = abs(l0 - card_yd), abs(l1 - card_yd)
    held = False
    best = _nearest_tee_box(lat, lon, tees, snap_yd)
    if best is not None and best[2] is not None and others:
        from shapely.geometry import Point as SPt
        kx, ky = math.cos(math.radians(lat)) * 111320 / 0.9144, 111320 / 0.9144
        held = any(best[2].distance(SPt((o[1] - lon) * kx, (o[0] - lat) * ky)) <= OCCUPIED_YD for o in others)
    if e1 < e0 or (e1 <= SNAP_CARD_TOL_YD and not (held and e1 > e0 + SNAP_WORSE_YD)):
        return snap
    why = "another set's box, " if held else ""
    return lat, lon, (f"review (kept: snap {snap[2][len('review ('):-1]} would measure {l1:.0f}, "
                      f"{why}point {l0:.0f}, card {card_yd:.0f})")


def review_measure(bh, world):
    """(ref -> (lon, lat) -> playing yds from that tee point, as build_holes measures it; None when the hole has
    no line in the world)."""
    from shapely.geometry import Point as SPt
    holes = {str(h["props"].get("ref")): h for h in (world.holes or [])}

    def for_ref(ref):
        h = holes.get(str(ref))
        if h is None:
            return None
        g = bh.find_green(world, h["line"][-1])
        gp = np.array(g["pt"].coords[0]) if g else h["line"][-1]

        def m(lon, lat):
            pt = np.array(world.proj(SPt(float(lon), float(lat))).coords[0])
            return float(bh._tee_path(pt, h["line"], gp)[1])
        return m
    return for_ref


def tee_overrides_for(req, set_key, card_sets, chosen, fc, measure=None, card=None, others=None):
    """{ref: (lon, lat, how)} for one built set from request tee_overrides {ref: {set: [lat, lon]}}; each point is
    kept when it is inside an OSM tee box, else moved onto the nearest box within OVERRIDE_SNAP_YD along the box's
    long axis when that does not take it off the card (review_tee_point). measure: ref -> (lon, lat) -> yds (or
    None), card {ref: yds} for this set, others: ref -> [(lat, lon)] of the other sets' tees on that hole."""
    out = {}
    tees = None
    for ref, by in (req.get("tee_overrides") or {}).items():
        for name, ll in (by or {}).items():
            if override_set(name, card_sets, chosen) != set_key or not ll or len(ll) < 2:
                continue
            lat, lon = float(ll[0]), float(ll[1])
            if tees is None:
                tees = osm_tee_inputs(fc)[1]
            m = measure(str(ref)) if measure else None
            pt = review_tee_point(lat, lon, tees, m, (card or {}).get(str(ref)),
                                  (others(str(ref)) if others else ()) or ())
            out[str(ref)] = (float(pt[1]), float(pt[0]), pt[2])
    return out


def review_others(req, set_key, card_sets, chosen, joint):
    """ref -> [(lat, lon)]: the other sets' tees on a hole (their review point when the review names one, else the
    tee stage's point), for review_tee_point's occupied-box check."""
    def f(ref):
        pts, named = [], set()
        for name, ll in ((req.get("tee_overrides") or {}).get(ref) or {}).items():
            s = override_set(name, card_sets, chosen)
            if s != set_key and ll and len(ll) >= 2:
                pts.append((float(ll[0]), float(ll[1])))
                named.add(s)
        for s, r in ((((joint or {}).get("holes") or {}).get(ref) or {}).get("tees") or {}).items():
            if s != set_key and s not in named and r.get("lat") is not None:
                pts.append((float(r["lat"]), float(r["lon"])))
        return pts
    return f


def with_tee_overrides(tp, set_key, ov):
    """tee_positions-shaped dict with the review points for set_key (a copy; tp may be shared by every set)."""
    if not ov:
        return tp
    tp = copy.deepcopy(tp) if tp else dict(schema="tees/positions", method="review overrides", holes={})
    for ref, (lon, lat, how) in ov.items():
        e = tp["holes"].setdefault(ref, {})
        if set_key is None:                                   # no card: build_holes reads entry tee_ll
            e["tee_ll"], e["how"] = [lon, lat], how
        else:
            e.setdefault("tees", {})[set_key] = dict(lat=lat, lon=lon, method=how, source="review",
                                                     confidence="high", error_yd=0.0)
    return tp


RENUMBER_NEAR_YD = 120.0      # a renumber's near_ll must lie this close to the hole line it renames
GREEN_MOVE_YD = 60.0          # a green override this far from the line end re-draws the line tee -> green


def _yd(a, b):
    """Yards between two [lon, lat] points (local equirectangular)."""
    kx = math.cos(math.radians((a[1] + b[1]) / 2)) * 111320 / 0.9144
    return math.hypot((a[0] - b[0]) * kx, (a[1] - b[1]) * 111320 / 0.9144)


def _yd_to_line(p, line):
    """Yards from [lon, lat] p to a polyline of [lon, lat] (segment distance in a local frame around p)."""
    kx, ky = math.cos(math.radians(p[1])) * 111320 / 0.9144, 111320 / 0.9144
    pts = [((c[0] - p[0]) * kx, (c[1] - p[1]) * ky) for c in line]
    best = min(math.hypot(*q) for q in pts)
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy
        if L2 > 0:
            t = max(0.0, min(1.0, -(x1 * dx + y1 * dy) / L2))
            best = min(best, math.hypot(x1 + t * dx, y1 + t * dy))
    return best


def _hole_feats(fc):
    return {str(f["properties"]["ref"]): f for f in fc["features"]
            if f["properties"].get("golf") == "hole" and f["geometry"]["type"] == "LineString"
            and f["properties"].get("ref")}


def apply_hole_renumber(fc, routed, ren):
    """Request "hole_renumber" {old ref: new ref | {to, near_ll [lat, lon]}} (course reviews: OSM / the router
    numbered holes differently from the card) -> (fc copy, routed rekeyed, [notes]). Applied after routing, so
    it renames OSM ways, supplement ways and routed holes alike, all at once (1->18, 2->1, ... is fine). An entry
    whose near_ll (a review point on the hole, e.g. its tee) is more than RENUMBER_NEAR_YD from the line is
    skipped: the numbering it was written against changed. A hole that keeps its number but sits on a renamed
    hole's new number is dropped (the review says the renamed hole is that card hole)."""
    if not ren:
        return fc, routed, []
    fc = copy.deepcopy(fc)
    feats, notes, valid = _hole_feats(fc), [], {}
    for old, spec in ren.items():
        old = str(old)
        new = str(spec.get("to") if isinstance(spec, dict) else spec)
        near = spec.get("near_ll") if isinstance(spec, dict) else None
        if not new.isdigit() or old == new:
            continue
        if old not in feats:
            notes.append(f"hole {old} -> {new}: no hole {old} in this build (not renumbered)")
            continue
        if near and len(near) >= 2:
            d = _yd_to_line([float(near[1]), float(near[0])], feats[old]["geometry"]["coordinates"])
            if d > RENUMBER_NEAR_YD:
                notes.append(f"hole {old} -> {new}: review point {d:.0f} yds off hole {old}'s line (not renumbered)")
                continue
        valid[old] = new
    if len(set(valid.values())) < len(valid):
        return fc, routed, notes + [f"hole_renumber maps two holes to one number ({valid}); not applied"]
    targets, keep = set(valid.values()), []
    for f in fc["features"]:
        p = f["properties"]
        r = str(p.get("ref")) if p.get("golf") == "hole" and f["geometry"]["type"] == "LineString" else None
        if r in valid:
            p["ref"], p["renumbered_from"] = valid[r], r
        elif r in targets:
            notes.append(f"hole {r} dropped: its number goes to renumbered hole "
                         f"{next(o for o, n in valid.items() if n == r)}")
            continue
        keep.append(f)
    fc["features"] = keep
    notes += [f"hole {o} -> {n}" for o, n in sorted(valid.items(), key=lambda kv: kv[0].zfill(3))]
    routed = {valid.get(r, r): v for r, v in (routed or {}).items() if r in valid or r not in targets}
    return fc, routed, notes


def apply_green_overrides(fc, req):
    """Request "green_overrides" {ref: [lat, lon]} (course reviews: the green centre when OSM has no outline, or
    the build used another hole's green) -> (fc copy, [notes]). The hole line now ends on the point (build_holes
    then snaps to an OSM green within 40 m, else uses the point). A move of more than GREEN_MOVE_YD re-draws the
    line straight from the hole's review tee (tee_overrides, the farthest set) or its own start; a hole with no
    line gets one from its review tee (a hole the build missed), tagged src=review."""
    go = req.get("green_overrides") or {}
    if not go:
        return fc, []
    fc, notes = copy.deepcopy(fc), []
    feats = _hole_feats(fc)
    for ref, ll in go.items():
        ref = str(ref)
        if not ll or len(ll) < 2:
            continue
        g = [float(ll[1]), float(ll[0])]
        tees = [[float(t[1]), float(t[0])] for t in ((req.get("tee_overrides") or {}).get(ref) or {}).values()
                if isinstance(t, (list, tuple)) and len(t) >= 2]
        tee = max(tees, key=lambda t: _yd(t, g)) if tees else None
        f = feats.get(ref)
        if f is not None:
            line = f["geometry"]["coordinates"]
            d = _yd(line[-1], g)
            if d < 3:
                continue
            if d > GREEN_MOVE_YD:
                f["geometry"]["coordinates"] = [tee or list(line[0]), g]
                notes.append(f"hole {ref}: green moved {d:.0f} yds, line re-drawn {'review tee' if tee else 'start'} -> green")
            else:
                f["geometry"]["coordinates"] = [list(c) for c in line[:-1]] + [g]
                notes.append(f"hole {ref}: green moved {d:.0f} yds")
            f["properties"]["review_green"] = True
        elif tee:
            par = (req.get("par_overrides") or {}).get(ref)
            props = dict(golf="hole", ref=ref, src="review", review_green=True)
            if par:
                props["par"] = str(par)
            fc["features"].append(dict(type="Feature", properties=props,
                                       geometry=dict(type="LineString", coordinates=[tee, g])))
            notes.append(f"hole {ref}: added (review tee -> green, {_yd(tee, g):.0f} yds)")
        else:
            notes.append(f"hole {ref}: green override but no hole line and no review tee (not applied)")
    return fc, notes


# ----------------------------------------------------------------------------- tees (S2)
def _tee_tags(props):
    return " ".join(str(props.get(k, "")) for k in ("tee", "golf:tee", "colour", "color", "name")).lower().split()


def osm_tee_inputs(fc):
    """(hole lines {ref: [(lat, lon)]}, OSM tee boxes [{id, coords, tags}], greens [{id, coords}])."""
    lines, tees, greens = {}, [], []
    for f in fc["features"]:
        p, g = f["properties"], f["geometry"]
        if p.get("golf") == "hole" and g["type"] == "LineString" and p.get("ref"):
            lines[str(p["ref"])] = [(c[1], c[0]) for c in g["coordinates"]]
        elif p.get("golf") == "tee" and g["type"] in ("Polygon", "Point"):
            cs = g["coordinates"][0] if g["type"] == "Polygon" else [g["coordinates"]]
            tees.append(dict(id=p.get("osm_id"), coords=[(c[1], c[0]) for c in cs], tags=p))
        elif p.get("golf") == "green" and g["type"] == "Polygon":
            greens.append(dict(id=p.get("osm_id"), coords=[(c[1], c[0]) for c in g["coordinates"][0]]))
    return lines, tees, greens


def lidar_pads(fc, dem_path):
    """tees/lidar_pads.detect_pads on the package DEM ([] when absent or failing) + a status string."""
    if not dem_path or not os.path.exists(dem_path):
        return [], "no DEM"
    mod = load(os.path.join(CD, "tees", "lidar_pads.py"), "cdp_lidar_pads")
    if mod is None:
        return [], "tees/lidar_pads.py not importable"
    lines, _, greens = osm_tee_inputs(fc)
    try:
        pads = mod.detect_pads(dem_path, greens=greens, lines=lines)
    except Exception as e:                                       # noqa: BLE001
        return [], f"failed: {type(e).__name__}: {e}"[:200]
    return pads, f"{len(pads)} candidate pads near hole starts"


def place_tees_joint(fc, per_hole_card, card_sets, pads=()):
    """tees/place_tee.place_course_sets for every hole and every set at once -> tee_positions-shaped dict
    {holes: {ref: {green, sets_without_box, tees: {set: {...}}}}}; a box tagged with a set's colour wins."""
    pt = place_tee_mod()
    if pt is None or not hasattr(pt, "place_course_sets"):
        return None
    lines, tees, greens = osm_tee_inputs(fc)
    if not lines:
        return None
    yards = {}
    for s, hc in per_hole_card.items():
        for ref, c in hc.items():
            if c.get("yards") and ref in lines:
                yards.setdefault(ref, {})[s] = float(c["yards"])
    res = pt.place_course_sets(lines, tees, yards, greens=greens, pads=list(pads))
    by_hole = pt.assign_tees_to_holes(lines, tees)
    for ref, hp in res.items():
        for s, r in hp["tees"].items():
            want = {str(s).lower(), str((card_sets.get(s) or {}).get("colour") or "").lower()} - {""}
            tagged = [t for t in by_hole.get(ref, []) if want & set(_tee_tags(t["tags"]))]
            if tagged:
                c = pt.centroid_ll(tagged[0]["coords"])
                hp["tees"][s] = dict(lat=c[0], lon=c[1], method="tagged", tee_id=tagged[0]["id"], confidence="high",
                                     error_yd=0.0, source="osm_tagged")
    return dict(schema="tees/positions", method="place_tee.place_course_sets (joint, ordered, green centroid)",
                holes=res)


def localizer_enabled(req):
    """S2 v2 (tees/localize.py) is the default (PIPELINE.md: held-out tees with OSM boxes hidden <= 10 yds 69 -> 86 %,
    neutral where OSM maps the boxes); request "tee_localizer": "v1" (or env TEE_LOCALIZER=v1) keeps the as-built
    place_tee.place_course_sets. Any v2 failure falls back to v1 (stages.tee_localizer says which ran)."""
    v = str(req.get("tee_localizer") or os.environ.get("TEE_LOCALIZER") or "v2").lower()
    return v not in ("v1", "place_tee", "off", "false", "0")


def place_tees_v2(fc, per_hole_card, card_sets, pads=(), img_dir=None, slug=None, req=None):
    """tees/localize.py: OSM boxes + lidar pads + DEM/NAIP texture pads + segment-model / perception tee
    detections, joint chain assignment with uncertainty (sigma_yd, p_assign per set). Same shape as
    place_tees_joint (an OSM box tagged with a set's colour still wins). Raises on failure (caller falls back)."""
    lz = load(os.path.join(CD, "tees", "localize.py"), "cdp_tee_localize")
    if lz is None:
        raise RuntimeError("tees/localize.py not importable")
    lines, tees, greens = osm_tee_inputs(fc)
    if not lines:
        raise RuntimeError("no hole lines")
    req = req or {}
    yards = {}
    for s, hc in per_hole_card.items():
        for ref, c in hc.items():
            if c.get("yards") and ref in lines:
                yards.setdefault(ref, {})[s] = float(c["yards"])
    texture, used = [], ["osm", "lidar"]
    if img_dir and os.path.exists(os.path.join(img_dir, "dem.tif")):
        try:
            texture = lz.texture_pads(os.path.join(img_dir, "dem.tif"), os.path.join(img_dir, "naip_nir.tif"),
                                      os.path.join(img_dir, "naip_rgb.tif"), greens=greens, lines=lines)
            used.append("texture")
        except Exception:                                          # noqa: BLE001  (optional source)
            texture = []
    seg = req.get("segment_geojson")
    seg = (seg if os.path.isabs(seg) else os.path.join(pc.ROOT, seg)) if seg else \
        os.path.join(CD, "segment", slug or "", "segment.geojson")
    seg = seg if os.path.exists(seg) else None
    scene = None
    for f in (os.path.join(CD, "perception", "scenes", slug or "", "scene.json"),
              os.path.join(CD, "perception", "scenes", slug or "", "scene.json.gz")):
        if slug and os.path.exists(f):
            import gzip
            scene = json.load(gzip.open(f, "rt") if f.endswith(".gz") else open(f))
            break
    used += ["segment"] * bool(seg) + ["scene"] * bool(scene)
    cands = lz.gather(osm_tees=tees, segment=seg, scene=scene, pads=list(pads), texture=texture)
    res = lz.localize_course(lines, greens, yards, cands)
    pt = place_tee_mod()
    by_hole = pt.assign_tees_to_holes(lines, tees)
    colours = {str(v).lower() for s in card_sets for v in (s, (card_sets.get(s) or {}).get("colour")) if v}
    for ref, hp in res.items():
        for s, r in hp["tees"].items():
            want = {str(s).lower(), str((card_sets.get(s) or {}).get("colour") or "").lower()} - {""}
            tagged = [t for t in by_hole.get(ref, []) if want & set(_tee_tags(t["tags"]))]
            if tagged:
                # the tagged box wins; the point is on its axis at the card yardage (as a localizer pad), not
                # its centroid (ERROR_BUDGET.md tees: tagged boxes are drawn short of the real back tee). A tagged
                # box > tag_off_card_yd off the card loses to an untagged box of the hole that fits the card
                # (localize.card_checked_point; sycamore_ridge 1 / 9)
                g = hp.get("green")
                y = (yards.get(ref) or {}).get(s)
                untagged = [t for t in by_hole.get(ref, []) if not (colours & set(_tee_tags(t["tags"])))]
                tp = lz.card_checked_point(lines[ref], (g["lat"], g["lon"]) if g else None, tagged, untagged, y)
                if tp is not None:
                    lat, lon, tid, dist, how = tp
                else:
                    (lat, lon), tid, dist, how = pt.centroid_ll(tagged[0]["coords"]), tagged[0]["id"], None, "tagged"
                if how == "card_box":
                    hp["tees"][s] = dict(lat=lat, lon=lon, method="card_box", tee_id=tid, confidence="high",
                                         error_yd=0.0, source="osm_untagged_card", sigma_yd=3.0, p_assign=1.0,
                                         dist_yd=dist, tagged_box_off_card=[t["id"] for t in tagged])
                else:
                    hp["tees"][s] = dict(lat=lat, lon=lon, method="tagged", tee_id=tid, confidence="high",
                                         error_yd=0.0, source="osm_tagged", sigma_yd=3.0, p_assign=1.0, dist_yd=dist)
    return dict(schema="tees/positions", method=f"{lz.VERSION} ({'+'.join(used)} pads, joint chain assignment)",
                sources=used, holes=res)


def place_tees(fc, card_holes, set_name, colour):
    """Pre-Q2 per-set placement (kept for comparison; build_package uses place_tees_joint).
    tees/place_tee.py for every hole -> tee_positions-shaped dict {holes: {ref: {tees: {set: {...}}}}}."""
    pt = place_tee_mod()
    lines, tees = {}, []
    for f in fc["features"]:
        p, g = f["properties"], f["geometry"]
        if p.get("golf") == "hole" and g["type"] == "LineString" and p.get("ref"):
            lines[str(p["ref"])] = [(c[1], c[0]) for c in g["coordinates"]]
        elif p.get("golf") == "tee" and g["type"] in ("Polygon", "Point"):
            cs = g["coordinates"][0] if g["type"] == "Polygon" else [g["coordinates"]]
            tees.append(dict(id=p.get("osm_id"), coords=[(c[1], c[0]) for c in cs], tags=p))
    if pt is None or not lines:
        return None
    by_hole = pt.assign_tees_to_holes(lines, tees)
    out = {}
    want = {str(set_name).lower(), str(colour or "").lower()} - {""}
    for ref, line in lines.items():
        yards = (card_holes.get(ref) or {}).get("yards")
        tagged = [t for t in by_hole.get(ref, []) if want & set(_tee_tags(t["tags"]))]
        if tagged:
            ring = tagged[0]["coords"]
            lat = sum(c[0] for c in ring) / len(ring)
            lon = sum(c[1] for c in ring) / len(ring)
            r = dict(lat=lat, lon=lon, method="tagged", tee_id=tagged[0]["id"], confidence="high", error_yd=0.0)
        elif yards:
            r = pt.place_tee(line, by_hole.get(ref, []), float(yards))
            if r["error_yd"] is None or r["error_yd"] > 10 or r["method"] == "walkback":
                alt = pt.place_tee(line, tees, float(yards))          # borrow a neighbour's box (place_course rule)
                if alt["method"] != "walkback" and alt["error_yd"] is not None and alt["error_yd"] <= 10:
                    alt["borrowed"] = True
                    r = alt
            r = {k: v for k, v in r.items() if k != "candidates"}
        else:
            continue
        out[ref] = dict(tees={set_name: r})
    return dict(schema="tees/positions", holes=out)


# ----------------------------------------------------------------------------- geo helpers
def bearing(a_ll, b_ll):
    from pyproj import Geod
    az, _, _ = Geod(ellps="WGS84").inv(a_ll[0], a_ll[1], b_ll[0], b_ll[1])
    return round(az % 360.0, 1)


def hole_frame(h):
    """imagery/render.Frame for a package hole (UTM, matching geometry's planar frame)."""
    rd = load(os.path.join(CD, "imagery", "render.py"), "cdp_render")
    return rd.Frame(h["tee_ll"], h["aim_ll"], ppy=h["pixel"]["ppy"], tee_px=h["pixel"]["tee_px"], proj="utm")


def dem_sampler(path):
    """lonlat (N,2) -> metres, bilinear on a DEM GeoTIFF (rasterio) ; None if unreadable."""
    try:
        import rasterio
        from pyproj import Transformer
        with rasterio.open(path) as src:
            z = src.read(1).astype(np.float64)
            tr = src.transform
            crs = src.crs.to_string()
            nd = src.nodata
        if nd is not None and not np.isnan(nd):
            z[z == nd] = np.nan
    except Exception as e:                                       # noqa: BLE001
        pc.log("dem unreadable", path, e)
        return None
    to = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    inv = ~tr

    def f(ll):
        ll = np.atleast_2d(np.asarray(ll, float))
        x, y = to.transform(ll[:, 0], ll[:, 1])
        x, y = np.asarray(x), np.asarray(y)
        c, r = inv.a * x + inv.b * y + inv.c, inv.d * x + inv.e * y + inv.f
        c, r = np.asarray(c) - 0.5, np.asarray(r) - 0.5
        c0, r0 = np.floor(c).astype(int), np.floor(r).astype(int)
        fc, fr = c - c0, r - r0
        hh, ww = z.shape
        ok = (c0 >= 0) & (r0 >= 0) & (c0 + 1 < ww) & (r0 + 1 < hh)
        c0, r0 = np.clip(c0, 0, ww - 2), np.clip(r0, 0, hh - 2)
        v = (z[r0, c0] * (1 - fc) * (1 - fr) + z[r0, c0 + 1] * fc * (1 - fr)
             + z[r0 + 1, c0] * (1 - fc) * fr + z[r0 + 1, c0 + 1] * fc * fr)
        return np.where(ok, v, np.nan)
    return f


def elevation_for_hole(h, sample, yds_to_ll):
    """Tee-line profile, landing plane and green drop from a DEM sampler (lonlat -> m), in the format
    elevation/adjust.py reads; + elevation/adjust.adjustments() per club when that module is present."""
    FT = 0.3048
    L = float(h.get("measured_length") or h["length"])
    tee_z = float(sample(yds_to_ll(np.array([[0.0, 0.0]])))[0])
    if not np.isfinite(tee_z):
        return None
    prof = []
    for a in np.arange(0, min(L + 20, 440) + 1, 10):
        pts = np.array([[x, -a] for x in (-10, -5, 0, 5, 10)])
        z = sample(yds_to_ll(pts))
        if np.isfinite(z).any():
            prof.append(dict(yd=float(a), band_ft_rel_tee=round(float(np.nanmean(z) - tee_z) / FT, 2)))
    gx, gy = h["green"]
    gz = float(sample(yds_to_ll(np.array([[gx, gy]])))[0])
    out = dict(par=h["par"], bearing_deg_true=h["bearing_deg"], tee_ft=round(tee_z / FT, 1), profile=prof,
               green=dict(delta_ft=round((gz - tee_z) / FT, 1) if np.isfinite(gz) else None, along_yd=round(-gy, 1)))
    if h["par"] >= 4:
        A, R = np.meshgrid(np.arange(240, 321, 8.0), np.arange(-20, 21, 8.0))
        A, R = A.ravel(), R.ravel()
        z = sample(yds_to_ll(np.c_[R, -A]))
        ok = np.isfinite(z)
        if ok.sum() >= 10:
            M = np.c_[np.ones(ok.sum()), A[ok], R[ok]]
            coef, *_ = np.linalg.lstsq(M, z[ok] / 0.9144, rcond=None)      # z in yards
            b, c = coef[1] * 100, coef[2] * 100
            out["landing_slope"] = dict(along_pct=round(float(b), 2), cross_pct=round(float(c), 2),
                                        magnitude_pct=round(float(math.hypot(b, c)), 2),
                                        fall_line_deg_cw_from_line=round(math.degrees(math.atan2(-c, -b)), 1))
        z270 = sample(yds_to_ll(np.array([[x, -270.0] for x in (-10, -5, 0, 5, 10)])))
        if np.isfinite(z270).any():
            out["landing"] = {"270": dict(delta_ft=round(float(np.nanmean(z270) - tee_z) / FT, 1))}
    adj = load(os.path.join(CD, "elevation", "adjust.py"), "cdp_elev_adjust")
    if adj is not None and out["green"]["delta_ft"] is not None and (h["par"] == 3 or "landing_slope" in out):
        try:
            out["adjustments"] = adj.adjustments(h["ref"], holes={h["ref"]: dict(out, green_slope=None)})
        except Exception as e:                                   # noqa: BLE001
            out["adjustments_error"] = f"{type(e).__name__}: {e}"[:200]
    return out


# ----------------------------------------------------------------------------- landing / par 3 helpers
def landing_lies(h):
    pl = pipeline()
    a, l = pl.landing_grid()
    lie, _ = pl.lie_with_index(h, pl.to_px(h, a, l))
    vals, counts = np.unique(lie.astype(str), return_counts=True)
    return {str(v): round(float(c) / len(lie), 3) for v, c in zip(vals, counts)}


def par3_haz(h):
    """Worst lie 2-14 yds off each green edge (same rule as geometry.par3_entry) from the current zones."""
    from matplotlib.path import Path
    p3 = h["par3"]
    tee, flag = np.array(p3["tee"], float), np.array(p3["flag"], float)
    v = flag - tee
    fwd = v / np.linalg.norm(v)
    right = np.array([-fwd[1], fwd[0]])
    gl = np.array(p3["green"], float)
    sev = dict(water=4, ob=4, recovery=3, native=3, sand=2, fairway=0, first_cut=0, rough=0)
    nm = dict(water="water", ob="ob", recovery="trees", native="native", sand="bunker", fairway="rough", first_cut="rough",
              rough="rough")
    paths = [(n, Path(np.array(p, float))) for n, p in h["zones"]]
    haz = {}
    for side, (ax, sign) in dict(left=(0, -1), right=(0, 1), short=(1, -1), long=(1, 1)).items():
        edge = gl[:, ax].max() if sign > 0 else gl[:, ax].min()
        probes = []
        for dd in np.arange(2, 15, 2):
            for o in np.linspace(-6, 6, 5):
                q = np.zeros(2)
                q[ax], q[1 - ax] = edge + sign * dd, o
                probes.append(flag + q[0] * right + q[1] * fwd)
        lies = np.array(["rough"] * len(probes), dtype=object)
        for n, pth in paths:
            lies[pth.contains_points(np.array(probes))] = n
        lst = list(lies)
        haz[side] = nm[max(set(lst), key=lambda n: (sev[n], lst.count(n)))]
    return haz


# ----------------------------------------------------------------------------- build
LIE_ORDER = ["ob_boundary", "native", "recovery", "ob", "first_cut", "fairway", "green", "water", "sand"]
MODEL_LIE = {"green": "fairway", "ob_boundary": "ob"}


def apply_tee_line(h):
    """Every tee set's aim_ll / bearing_deg from the one tee-line rule (tee_line.py, ARCHITECTURE 9.1-8):
    tee -> the hole line 250 yds out (<= 62% of the hole), par 3s the green. Idempotent."""
    for t in (h.get("tees") or {}).values():
        if not t.get("tee_ll") or not h.get("green_ll"):
            continue
        aim, how = tl.aim_point(t["tee_ll"], h.get("hole_line_ll"), h["green_ll"],
                                t.get("card_yards") or t.get("measured_yards"), h.get("par"))
        t["aim_ll"] = [round(aim[0], 7), round(aim[1], 7)]
        t["aim_rule"] = how
        t["bearing_deg"] = bearing(t["tee_ll"], t["aim_ll"])
    return h
WINDOW_LAT, WINDOW_BEHIND, WINDOW_PAST, WINDOW_MIN = 150.0, 40.0, 40.0, 330.0


def find_imagery(req, pkg_dir, slug=None):
    """NAIP (+ DEM) directory with georef.json: request > packages/<slug>/imagery > imagery/<slug>."""
    for d in [req.get("imagery_dir"), os.path.join(pkg_dir, "imagery"),
              os.path.join(CD, "imagery", slug or os.path.basename(os.path.normpath(pkg_dir)))]:
        if not d:
            continue
        d = d if os.path.isabs(d) else os.path.join(pc.ROOT, d)
        if os.path.exists(os.path.join(d, "georef.json")):
            return d
    return None


def vision_raw_dirs(slug, course):
    """vision_any/<slug>/raw folders that look like this course (lidar HAG etc.), for gapfill."""
    out = []
    for d in sorted(glob.glob(os.path.join(CD, "vision_any", "*", "raw", "meta.json"))):
        name = os.path.basename(os.path.dirname(os.path.dirname(d)))
        if name == slug or slug.startswith(name + "_") or name.startswith(slug):
            out.append(os.path.relpath(os.path.dirname(d), pc.ROOT))
    return out


def imagery_ref(img_dir):
    if not img_dir:
        return None, None
    g = pc.read_json(os.path.join(img_dir, "georef.json"), {}) or {}
    im = g.get("imagery") or {}
    rel = os.path.relpath(img_dir, pc.ROOT)
    imagery = dict(dir=rel, source=im.get("source"), year=im.get("year"), acquired=im.get("acquired"),
                   naip_date=(im.get("acquired") or [None])[0], items=im.get("items"),
                   resolution_m=im.get("resolution_m"), crs=im.get("crs"), bands=im.get("bands"),
                   files=im.get("files"),
                   # which NAIP year and why (imagery/naip_years.py via fetch_imagery.py; None = fetched before
                   # year selection existed: the newest covering year)
                   selection=im.get("selection"),
                   present=all(os.path.exists(os.path.join(img_dir, f)) for f in (im.get("files") or {}).values())) \
        if im else None
    dem = g.get("dem")
    dem_path = os.path.join(img_dir, (dem or {}).get("file", "dem.tif"))
    elevation = dict(file=os.path.relpath(dem_path, pc.ROOT), source=(dem or {}).get("source"),
                     resolution_m=(dem or {}).get("resolution_m"), crs=(dem or {}).get("crs")) \
        if os.path.exists(dem_path) else None
    return imagery, elevation


def call_ob(package, warnings):
    """S4c OB inference (course_data/ob/infer.py, research plan B4): inferred OB polygons (property line, lots,
    roads) appended to zones_ll as lie 'ob' (src 'ob:<evidence>', p = confidence), within 60 yds of the line of
    play, never over fairway / green / water / sand. Runs only for a course whose OB evidence was fetched
    (course_data/ob/<slug>/raw/, .github/workflows/ob.yml via course_data/requests/ob_*.json) once
    course_data/ob/params.json is calibrated; otherwise the geometry stage's OSM OB stays as it is."""
    st = package["stages"]
    slug = package.get("slug") or (package.get("course") or {}).get("slug")
    if not (os.path.isdir(os.path.join(CD, "ob", str(slug), "raw")) and os.path.exists(os.path.join(CD, "ob", "params.json"))):
        st["ob"] = ("geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it "
                    "in course_data/requests/ob_*.json")
        return package
    mod = load(os.path.join(CD, "ob", "infer.py"), "cdp_ob_infer")
    if mod is None or not callable(getattr(mod, "apply_ob", None)):
        st["ob"] = "missing (course_data/ob/infer.py not importable)"
        return package
    try:
        out = mod.apply_ob(copy.deepcopy(package), use_reframe=False)
        return reframe(out)
    except Exception as e:                                       # noqa: BLE001
        warnings.append(f"OB inference failed: {type(e).__name__}: {str(e)[:200]}")
        st["ob"] = f"failed: {type(e).__name__}: {str(e)[:160]}"
        return package


def call_segment_fill(package, warnings):
    """S4b: imagery-model gap-fill where OSM lacks fairways / bunkers / greens / water (course_data/segment)."""
    mod = load(os.path.join(CD, "segment", "gapfill.py"), "cdp_segment_gapfill")
    st = package["stages"]
    seg = mod.segment_for(package) if mod is not None and hasattr(mod, "segment_for") else None
    if not seg:
        st["segment"] = "not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)"
        return package
    try:
        return mod.segment_gapfill(package, seg, reframe=False, log=lambda *a: None)
    except Exception as e:                                       # noqa: BLE001
        st["segment"] = f"failed: {type(e).__name__}: {e}"[:300]
        warnings.append("segment gap-fill failed; fairways / bunkers come from OSM only")
        return package


def call_fairway_fill(package, fc, req, warnings):
    """S4f: NAIP mown-fairway fill (course_data/vision_any/fairway_fill.py) for par-4/5 holes whose landing corridor
    has no fairway after OSM / segment (Creekmoor: OSM maps no golf=fairway). Course-level separation gate and
    per-hole gates; never over OSM. Request "fairway_fill": false turns it off. Never fatal."""
    st = package["stages"]
    if req.get("fairway_fill") is False:
        st["fairway_fill"] = "off (request fairway_fill: false)"
        return package
    mod = load(os.path.join(CD, "vision_any", "fairway_fill.py"), "cdp_fairway_fill")
    if mod is None:
        st["fairway_fill"] = "missing (course_data/vision_any/fairway_fill.py not importable)"
        return package
    out, rep = mod.fill_package(package, osm_fc=fc)
    # fill_package returns a deep copy: the stage text goes on the package that is kept (it was written on the
    # input, so no built package recorded stages.fairway_fill, e.g. creekmoor 2026-11-03)
    out.setdefault("stages", {})["fairway_fill"] = str(rep.get("status"))[:300]
    if str(rep.get("status", "")).startswith("ok"):
        out.setdefault("sources", {})["fairway_fill"] = dict(model=mod.VERSION, dprime=rep.get("dprime"),
                                                            holes=rep.get("holes"))
    elif str(rep.get("status", "")).startswith(("gated", "failed")):
        warnings.append(f"no fairway mapped on {len(rep.get('wanted') or [])} hole(s) and the NAIP fairway fill "
                        f"did not run: {rep['status']}"[:300])
    return out


VISION_PRODUCT = "vision_any/2"     # the product vision layer (course_data/vision_any/build_layers.py)


def call_gapfill(package, img_dir, warnings):
    mod = load(os.path.join(CD, "vision_any", "gapfill.py"), "cdp_vision_gapfill")
    st = package["stages"]
    if mod is None or not callable(getattr(mod, "gapfill", None)):
        st["vision"] = "missing (course_data/vision_any/gapfill.py not present)"
        return package
    if not img_dir and not package["sources"].get("vision_raw"):
        st["vision"] = "skipped: no imagery for this course"
        warnings.append("no imagery: trees / long grass come from OSM only")
        return package
    try:
        out = mod.gapfill(copy.deepcopy(package), img_dir)
        if not isinstance(out, dict):
            raise TypeError(f"gapfill returned {type(out).__name__}")
        for k, h in out.get("holes", {}).items():               # keep vision's exposure through reframe
            if h.get("exposure") != package["holes"].get(k, {}).get("exposure"):
                h["exposure_src"] = "vision"
        added = sum(str(z.get("src", "")).startswith("vision") for h in out.get("holes", {}).values()
                    for z in h.get("zones_ll") or [])
        v = str(out.get("stages", {}).get("vision", "") or "")
        if not v or v == str(st.get("vision", "") or ""):     # gapfill said nothing about this run
            v = (f"ok: vision_any/gapfill.py ({added} zones)" if added else
                 "missing: vision_any/gapfill.py added no zones (no layers for this course?)")
        elif v.startswith("ok") and not added:
            v = f"missing: {v[3:].strip()} ran but added no zones"
        slug = package.get("slug") or (package.get("course") or {}).get("slug")
        if v.startswith("ok") and not v.startswith("ok: " + VISION_PRODUCT):
            # an on-the-fly vision_any/1 build from raw/ (gapfill's fallback): keep its trees / water, drop its long
            # grass (the product keeps long grass off: model_v2/model.json native_thr null), and say so
            dropped = 0
            for h in out.get("holes", {}).values():
                zl = h.get("zones_ll") or []
                keep = [z for z in zl if not (str(z.get("src", "")).startswith("vision") and z.get("lie") == "native")]
                dropped += len(zl) - len(keep)
                h["zones_ll"] = keep
            v = (f"missing: product layer {VISION_PRODUCT} not built for '{slug}' (fell back to {v[3:].strip()[:60]} "
                 f"from raw/ on the fly: trees / water kept, {dropped} long-grass zones dropped)")
        if not v.startswith("ok"):
            v += f"; CHECK: build it with course_data/vision_any/build_layers.py {slug} (course_package.yml does on a fetch)"
        out.setdefault("stages", {})["vision"] = v
        if not v.startswith("ok"):
            w = out["warnings"] if isinstance(out.get("warnings"), list) else warnings
            w.append(f"CHECK vision: {v[:200]}; trees / water come from OSM (or the fallback) only")
        return out
    except Exception as e:                                       # noqa: BLE001
        st["vision"] = f"failed: {type(e).__name__}: {e}"[:300]
        warnings.append("vision gap-fill failed; trees / long grass come from OSM only")
        return package


def route_missing_holes(fc, card, course, req, pkg_dir, slug, warnings, stages, pipeline=None):
    """S2a hole inference through the stage selector (platform/stage_select.py, PIPELINE.md): the data tier
    (OSM greens / tees mapped or not, card or not) picks the method - routing v2 with the card-free structure
    solver's marginals as a prior (structure on the OSM scene, or on the perception scene when OSM lacks greens /
    tees), with routing v2 alone, the structure solver alone and the geometry fallback (build_holes.infer_holes)
    as fallbacks on any error. Only the refs OSM has no golf=hole way for are added. Request "routing": false
    keeps the geometry fallback; "hole_method": "v2" | "structure" | "v2+structure" | "sequence_v3" | "geometry"
    forces one (sequence_v3: formation-v2 pairs + zero-tap sequence solver v3, card tiers; falls back to
    v2+structure > v2 > structure > geometry on any error). package.json["pipeline"]["holes"]["method"] is what ran.
    The golfer-confirm payload (golf_confirm/1, confirm.py) for the routed holes goes to confirm.json.
    -> (fc, {ref: {status, flags, p_green, p_hole, ...}} for the routed holes). pipeline (dict) gets the record."""
    pipeline = pipeline if pipeline is not None else {}
    import routing as rt
    import stage_select as ss
    scene = ss.load_scene(slug)
    prof = ss.profile(fc, card, scene)
    pipeline.update(tier=ss.tier(prof), profile=prof)
    have = set(osm_lines(fc))
    missing = [str(i) for i in range(1, prof["n_holes"] + 1) if str(i) not in have]
    if not missing:
        pipeline["holes"] = dict(method="osm", note="OSM maps every hole")
        stages["routing"] = "not needed: OSM has a golf=hole way for every hole"
        return fc, {}
    if not req.get("routing", True) or req.get("hole_method") == "geometry":
        pipeline["holes"] = dict(method="geometry", note="request: routing off")
        stages["routing"] = "off (request): geometry fallback for holes OSM lacks"
        return fc, {}
    try:
        seg = next((pc.read_json(p) for p in (os.path.join(CD, "segment", slug, "segment.geojson"),
                                              os.path.join(pkg_dir, "segment.geojson")) if os.path.exists(p)), None)
        pads = []
        _, elev = imagery_ref(find_imagery(req, pkg_dir, slug))
        dem = os.path.join(pc.ROOT, elev["file"]) if elev else None
        if dem and os.path.exists(dem):
            lp = load(os.path.join(CD, "tees", "lidar_pads.py"), "cdp_lidar_pads")
            if lp is not None:
                pads = lp.detect_pads(dem, greens=osm_tee_inputs(fc)[2], lines=None)
        force = dict(method=req["hole_method"]) if req.get("hole_method") in ("v2", "structure", "v2+structure",
                                                                               "sequence_v3", "pathroute_v2") else None
        if force is None and card_blind(req) and req.get("pathroute", True):
            force = dict(method="pathroute_v2")      # card:none: the synthetic card carries no routing truth
        if force is None and req.get("pathroute", True) is False:
            force = dict(ss.SELECT_PRE_PATHROUTE.get(ss.tier(prof), {})) or None     # the routing before pathroute_v2
        res, info = ss.infer_holes(fc, card, course, seg=seg, pads=pads, scene=scene, force=force)
        info.pop("profile", None)
        pipeline["holes"] = info
        for fb in info.get("fallbacks", []):
            warnings.append(f"hole inference fallback: {fb}"[:200])
        if info.get("method") in (None, "geometry"):
            stages["routing"] = f"fallback: geometry/build_holes.infer_holes ({'; '.join(info.get('fallbacks', []))})"[:300]
            return fc, {}
        inp = res.pop("_inp", None)
        for n_ in sanity.guard_routed(res, fc, missing, (inp or {}).get("greens") or ()):
            warnings.append(n_[:240])
        fc2 = rt.to_hole_features(res, fc, inp)
        routed = {r: {k: res["holes"][r].get(k) for k in ("status", "flags", "p_green", "p_hole", "margin", "green_src", "tee_src",
                                                          "confidence")}
                  for r in missing if res["holes"].get(r, {}).get("green_ll") and res["holes"][r].get("tee_ll")}
        for r, h in routed.items():
            h["method"] = info["method"]
            if h["status"] != "ok":
                warnings.append(f"hole {r}: placed by {info['method']} inference, golfer check ({'; '.join(h['flags'] or [])})")
        out = {k: v for k, v in res.items() if k not in ("context", "top", "_inp")}
        out["pipeline"] = info
        pc.write_json(os.path.join(pkg_dir, "routing.json"), out)
        stages["routing"] = (f"ok: {info['method']} ({info['tier']}"
                             + (f", lam {info['lam']}" if info.get("lam") is not None else "")
                             + (f", structure on {info['structure_input']}" if info.get("structure_input") else "")
                             + f") placed {len(routed)}/{len(missing)} holes OSM has no way for "
                             f"({sum(h['status'] != 'ok' for h in routed.values())} to check; segment "
                             f"{'yes' if seg else 'no'}, lidar pads {len(pads)}, perception scene {'yes' if scene else 'no'})")
        if res.get("confirm") and res.get("method") == "pathroute_v2":     # its own confirm: ask order + facts
            pipeline["confirm"] = dict(file="routing.json#confirm", schema=res["confirm"].get("schema"),
                                       questions=len(res["confirm"].get("ask_order") or []))
        if inp is not None and req.get("confirm", True):
            try:                                 # golf_confirm/1 for the app (CONFIRM_UX.md)
                import confirm as cf
                s = cf.Session(inp, card, fc=fc, boundary=course.get("boundary"),
                               n_holes=None if card else prof["n_holes"])
                pc.write_json(os.path.join(pkg_dir, "confirm.json"),
                              s.payload(course=dict(name=course.get("name"), osm=course.get("osm"), state=course.get("state"))))
                pipeline["confirm"] = dict(file="confirm.json", questions=len(s.questions(3)) if not s.done() else 0)
            except Exception as e:                               # noqa: BLE001
                pipeline["confirm"] = dict(error=f"{type(e).__name__}: {e}"[:200])
        return fc2, routed
    except Exception as e:                                       # noqa: BLE001
        stages["routing"] = f"failed: {type(e).__name__}: {e}"[:300]
        pipeline["holes"] = dict(method="geometry", error=stages["routing"])
        warnings.append("hole inference failed: holes without OSM ways use the geometry fallback")
        return fc, {}


def ss_scene(slug):
    try:
        import stage_select as ss
        return ss.load_scene(slug) is not None
    except Exception:                                            # noqa: BLE001
        return False


def find_local_card(course):
    """A card already in the repo for this OSM course (tees/scorecard.json for Spirit Hollow)."""
    for p in glob.glob(os.path.join(CD, "tees", "*scorecard*.json")) + glob.glob(os.path.join(CD, "tees", "*", "scorecard.json")):
        c = pc.read_json(p, {}) or {}
        meta = c.get("course") if isinstance(c.get("course"), dict) else {}
        oid = meta.get("osm_relation") or meta.get("osm_id") or (meta.get("osm") or {}).get("id")
        if oid and course.get("osm") and int(oid) == int(course["osm"]["id"]) and c.get("tee_sets"):
            return os.path.relpath(p, pc.ROOT)
    return None


def osm_lines(fc):
    return {str(f["properties"]["ref"]): f["geometry"]["coordinates"] for f in fc["features"]
            if f["properties"].get("golf") == "hole" and f["geometry"]["type"] == "LineString"
            and f["properties"].get("ref")}


def _frame(tee_ll, aim_ll):
    rd = load(os.path.join(CD, "imagery", "render.py"), "cdp_render")
    return rd.Frame(tee_ll, aim_ll, proj="utm")


def _ring_ll(fr, poly):
    return [[round(float(a), 7), round(float(b), 7)] for a, b in fr.yds_to_ll(np.asarray(poly, float))]


def build_package(req, pkg_dir, render=False, gapfill=True):
    """Offline: raw/ (+ imagery/) -> package dict. Raises SystemExit when raw data is missing."""
    raw = os.path.join(pkg_dir, "raw")
    slug = os.path.basename(os.path.normpath(pkg_dir))
    course = pc.read_json(os.path.join(raw, "course.json"))
    if not course:
        raise SystemExit(f"{raw}/course.json missing: run fetch_package.py (GitHub Actions)")
    if course.get("status") != "ok":
        raise SystemExit(f"course not resolved ({course.get('status')}): candidates "
                         + json.dumps(course.get("candidates", [])[:8]))
    fc = pc.read_json(os.path.join(raw, "osm.geojson"))
    if not fc:
        raise SystemExit(f"{raw}/osm.geojson missing")
    summ = pc.read_json(os.path.join(raw, "summary.json"), {}) or {}
    stages, warnings = {}, []
    stages["resolve"] = (f"ok: {course['osm']['type']}/{course['osm']['id']} {course['name']} "
                         f"({course.get('town')}, {course.get('state')})")
    stages["osm"] = f"ok: {len(fc['features'])} features"

    # S1 scorecard + tee set
    req = dict(req)
    blind = card_blind(req)
    if blind:                                            # card:none: no card of any kind reaches the build
        req = strip_card_inputs(req)
    if not req.get("scorecard") and not req.get("yardages") and req.get("local_scorecard", True):
        local = find_local_card(course)
        if local:
            req["scorecard"] = local
    fc, osm_notes = sanity.clean_osm(fc, names=[n for n in (req.get("course"), course.get("name")) if n],
                                     near=req.get("near"))
    warnings += osm_notes
    card, cinfo = cardless_card(fc, course, raw, req) if blind else pick_scorecard(req, raw, fc)
    if cinfo.get("units"):
        warnings.append(f"scorecard units: {cinfo['units']}")
    for f_ in ((cinfo.get("consensus") or {}).get("flags") or [])[:6]:
        warnings.append(f"card consensus: {f_}"[:240])
    order = None
    if card and not blind and req.get("auto_renumber", True) and not req.get("hole_renumber"):
        # sanity.card_order: OSM refs 1..18 that walk as a round are never renumbered to fit a card (TPC Sawgrass:
        # Dye's Valley's card renumbered the Stadium); a card far off them in that order is not this course's card
        order = sanity.card_order(fc, card)
        if order["note"]:
            stages["card_order"] = f"{order['action']}: {order['note']}"[:600]
        if order["action"] == "reject":
            warnings.append(f"{order['note']} ({cinfo.get('kind')}: {cinfo.get('source')}) (CHECK)"[:400])
            rejected = dict(source=cinfo.get("source"), ok=False, info=order["note"][:300])
            card, cinfo = None, dict(kind=None, source=None, url=None, tried=(cinfo.get("tried") or []) + [rejected],
                                     consistency=None, cross_check={})
        elif order["action"] == "keep":
            warnings.append(order["note"] + " (CHECK)")
    wanted = req.get("tee_set") or req.get("tees")
    chosen, how = scm.choose_tee_set(card, wanted) if card else (None, "no scorecard")
    substituted = None
    if card and chosen is None:
        chosen, _ = scm.choose_tee_set(card, "back")
        if not req.get("allow_substitute"):
            raise SystemExit(f"{how}: refusing to build another set. Ask the golfer, or set \"allow_substitute\": "
                             f"true in the request (CLI --allow-substitute) to use the longest set '{chosen}'")
        substituted = (f"requested tee set '{wanted}' is not on the card; using '{chosen}' instead "
                       f"(allow_substitute). Sets on the card: {', '.join((card.get('tee_sets') or {}))}")
        warnings.append(substituted)
        how = f"substitute: longest set ({how})"
    card, card_fixes = apply_card_overrides(card, req, chosen)
    if card and order and order["action"] == "renumber":   # OSM hole order != card order (and OSM's does not walk)
        fc, renum = (order["fc"], order["mapping"]) if order.get("swap") else sanity.renumber_holes(fc, card)
        if renum:
            stages["renumber"] = "ok: OSM hole refs -> card holes " + ", ".join(f"{a}->{b}" for a, b in sorted(
                renum.items(), key=lambda kv: kv[0].zfill(3)))
            warnings.append("OSM hole numbering differs from the card: " + stages["renumber"][4:] + " (CHECK)")
    if card_fixes:
        stages["card_overrides"] = f"ok: {len(card_fixes)} review fix(es): " + "; ".join(card_fixes)[:400]
    pipe = dict(schema="pipeline/1", doc="platform/PIPELINE.md: which method ran at each stage, and why",
                card=dict(kind=cinfo["kind"], source=cinfo["source"]) if card else dict(kind=None))
    fc, routed = route_missing_holes(fc, card, course, req, pkg_dir, slug, warnings, stages, pipeline=pipe)
    fc, routed, ren_notes = apply_hole_renumber(fc, routed, req.get("hole_renumber"))
    if ren_notes:
        stages["hole_renumber"] = "ok: " + "; ".join(ren_notes)[:400]
        warnings += [f"review renumber: {n}" for n in ren_notes if "not " in n or "dropped" in n]
    fc, green_notes = apply_green_overrides(fc, req)
    if green_notes:
        stages["green_overrides"] = "ok: " + "; ".join(green_notes)[:400]
    if not card:
        fc, cl_notes = apply_cardless_overrides(fc, req)
        if cl_notes:
            stages["card_overrides"] = "ok: " + "; ".join(cl_notes)[:400]
            warnings += [f"review override: {n}" for n in cl_notes if "not applied" in n]
    if blind:          # card:none: the synthetic card from tees/cardless.py on the routed holes (else keep the fallback)
        c2, i2 = cardless_infer(fc, req, pkg_dir, slug, routed)
        if c2 is not None:
            i2["tried"] = (cinfo.get("tried") or []) + [dict(source="pre-routing", ok=True, info=cinfo.get("source"))]
            card, cinfo = c2, i2
            chosen, how = scm.choose_tee_set(card, None)
            pipe["card"] = dict(kind=cinfo["kind"], source=cinfo["source"])
        else:
            cinfo.setdefault("tried", []).append(dict(source="tees/cardless.infer_card", ok=False, info=i2))
            if not str(i2).startswith("OSM maps every hole"):
                warnings.append(f"cardless: {i2}; using the OSM hole-line card"[:240])
    refs =sorted(osm_lines(fc), key=lambda r: r.zfill(3))
    stages["scorecard"] = f"ok: {cinfo['kind']} ({cinfo['source']})" if card else "missing"
    if not card:
        warnings.append("no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM "
                        "tee box nearest each hole-line start (usually the back tee); lengths are measured")
    card_sets = (card or {}).get("tee_sets") or {}
    per_hole_card = {s: scm.per_hole(card, s, refs) for s in card_sets}
    main_card = per_hole_card.get(chosen, {})

    # card pars into the OSM hole tags so geometry builds par-3 entries for card par 3s
    fc = copy.deepcopy(fc)
    par_src = {}
    for f in fc["features"]:
        p = f["properties"]
        if p.get("golf") == "hole" and p.get("ref"):
            r = str(p["ref"])
            ch = main_card.get(r) or next((v.get(r) for v in per_hole_card.values() if v.get(r, {}).get("par")), {}) or {}
            if ch.get("par"):
                par_src[r] = "card" if str(p.get("par", "")) in ("", str(ch["par"])) else f"card (OSM says {p['par']})"
                p["par"] = str(ch["par"])
            elif str(p.get("par", "")).isdigit():
                par_src[r] = "review" if p.get("review_par") else "osm"

    # S2 (all sets jointly) + S3 for every tee set on the card (zones come from the longest set's window)
    img_dir = find_imagery(req, pkg_dir, slug)
    imagery, elevation = imagery_ref(img_dir)
    pads, pad_status = lidar_pads(fc, os.path.join(pc.ROOT, elevation["file"]) if elevation else None) \
        if card_sets and req.get("lidar_tees", True) else ([], "not run")
    joint, v2_status = None, None
    if card_sets and localizer_enabled(req):
        try:
            joint = place_tees_v2(fc, per_hole_card, card_sets, pads, img_dir=img_dir, slug=slug, req=req)
            v2_status = f"ok: {joint['method']}"
        except Exception as e:                                    # noqa: BLE001  fall back to the joint S2
            joint = None
            v2_status = f"failed ({type(e).__name__}: {e}); fell back to place_tee.place_course_sets"[:300]
            warnings.append(f"tee localizer v2 {v2_status}")
    if joint is None:
        joint = place_tees_joint(fc, per_hole_card, card_sets, pads) if card_sets else None
    if joint is not None and req.get("tee_guard", True):     # sanity.guard_tees: forward walk-backs, tees on greens / buildings
        for n_ in sanity.guard_tees(joint, fc):
            warnings.append(n_[:240])
    if v2_status:
        stages["tee_localizer"] = v2_status
    pipe["tees"] = dict(method=("tees/localize.py (v2)" if joint is not None and str(joint.get("method", "")).startswith("tees/localize")
                                else "tees/place_tee.place_course_sets (v1)" if joint is not None
                                else "place_tee.py per set" if card_sets else "OSM tee nearest the hole-line start"),
                        requested=str(req.get("tee_localizer") or os.environ.get("TEE_LOCALIZER") or "default (v2)"),
                        status=v2_status)
    bh = geometry()
    world = bh.World(fc)
    built, tee_pos = {}, {}
    for s in (card_sets or {None: None}):
        hc = per_hole_card.get(s, {})
        tp = joint if (s and hc and joint) else (place_tees(fc, hc, s, card_sets[s].get("colour")) if (s and hc) else None)
        ov = tee_overrides_for(req, s, card_sets, chosen, fc, measure=review_measure(bh, world),
                               card={r: float(c["yards"]) for r, c in hc.items() if c.get("yards")},
                               others=review_others(req, s, card_sets, chosen, joint)) \
            if req.get("tee_overrides") else {}
        if ov:
            tp = with_tee_overrides(tp, s, ov)
            stages["tee_overrides"] = (stages.get("tee_overrides") or "ok:") + f" {s or 'osm_back'} " + ", ".join(
                f"{r} {v[2]}" for r, v in sorted(ov.items(), key=lambda kv: kv[0].zfill(3))) + ";"
        lengths = {r: float(c["yards"]) for r, c in hc.items() if c.get("yards")}
        built[s], _ = bh.build(fc, s, lengths or None, world=world, tees=tp, frame="yard")
        tee_pos[s] = tp
    n_lidar = sum(r.get("source") == "lidar" for hp in ((joint or {}).get("holes") or {}).values()
                  for r in hp["tees"].values())
    stages["tees"] = (f"ok: tees/place_tee.place_course_sets (joint, ordered back to front, green centroid) for "
                      f"{len(card_sets)} sets; lidar pads: {pad_status}, {n_lidar} placement(s) on one" if joint else
                      f"ok: tees/place_tee.py for {len(card_sets)} sets on the card yardages" if card_sets else
                      "fallback: OSM tee nearest the hole-line start (no yardages)")
    if joint is not None and str(joint.get("method", "")).startswith("tees/localize"):
        stages["tees"] = f"ok: {joint['method']} for {len(card_sets)} sets; lidar pads: {pad_status}"
    if not built or not any(built.values()):
        n = {k: sum((f.get("properties") or {}).get("golf") == k for f in fc["features"]) for k in ("hole", "green", "tee")}
        raise SystemExit(f"no holes built (no golf=hole ways and no tee/green pairs: OSM maps {n['hole']} holes, "
                         f"{n['green']} greens, {n['tee']} tees; perception scene {'yes' if ss_scene(slug) else 'no'}). "
                         "Fix the data: map the course in OSM, add an osm_supplement, or build a perception scene")
    back = max(built, key=lambda s: sum(h["length"] for h in built[s].values()))
    chosen_key = chosen if chosen in built else back
    base = built[back]
    stages["geometry"] = f"ok: geometry/build_holes.py ({len(base)} holes, {len(built)} tee set(s))"

    lines = osm_lines(fc)
    feats_now = _hole_feats(fc)
    holes = {}
    for k in sorted(base, key=lambda r: str(r).zfill(3)):
        b = base[k]
        frb = _frame(b["tee_ll"], b["aim_ll"])
        zones_ll = []
        for lie, poly in b["zones"]:
            ring = _ring_ll(frb, poly)
            src = "osm"
            if lie == "ob" and world.course is not None:
                from shapely.geometry import Polygon as SPoly
                rp = world.proj(SPoly(ring)).representative_point()
                if not world.course.contains(rp):
                    src = "osm:course_boundary"
            zones_ll.append(dict(lie=lie, poly=ring, src=src, p=1.0))
        tees = {}
        for s, hs in built.items():
            y = hs.get(k)
            if not y:
                continue
            ch = per_hole_card.get(s, {}).get(k, {})
            meth = y["tee_choice"]
            tp_r = ((tee_pos.get(s) or {}).get("holes", {}).get(k, {}).get("tees", {}).get(s, {}) or {})
            tees[s or "osm_back"] = dict(
                tee_ll=y["tee_ll"], aim_ll=y["aim_ll"], bearing_deg=bearing(y["tee_ll"], y["aim_ll"]),
                method=meth.replace("tee stage: ", "").replace(f"{s} ", "") if s else meth,
                tee_choice=meth, confidence=next((v for kk, v in pipeline().TEE_TRUST if kk in meth), 0.4),
                measured_yards=y["length"], card_yards=ch.get("yards"),
                tee_id=tp_r.get("tee_id"), tee_source=tp_r.get("source"), order_ok=tp_r.get("order_ok"),
                shared_with=tp_r.get("shared_with"), box_error_yd=tp_r.get("error_yd"))
            if tp_r.get("sigma_yd") is not None:                 # S2 v2 (tees/localize.py): uncertainty
                tees[s or "osm_back"]["uncertainty"] = {kk: tp_r.get(kk) for kk in (
                    "sigma_yd", "sigma_along_yd", "sigma_lat_yd", "p_assign", "alternatives", "sources", "localizer")}
            if ch.get("yards") and abs(y["length"] - ch["yards"]) > 15 and s == chosen_key:
                warnings.append(f"hole {k}: measured {y['length']} vs card {ch['yards']} yds for {s} "
                                "(no OSM tee box at that yardage?)")
        hcp = main_card.get(k, {}).get("hcp") or b.get("handicap")
        h = dict(ref=k, par=int(b["par"]), hcp=int(hcp) if str(hcp or "").isdigit() else hcp,
                 yards={s: per_hole_card[s].get(k, {}).get("yards") for s in per_hole_card},
                 hole_line_ll=[[round(x, 7), round(y_, 7)] for x, y_ in lines[k]] if k in lines else
                 _ring_ll(frb, b["hole_line"]),
                 green_ll=b["green_ll"],
                 green_polygon_ll=_ring_ll(frb, b["green_polygon"]) if b.get("green_polygon") else None,
                 tees=tees, zones_ll=zones_ll, inferred=b.get("inferred", False), tee_options=b["tee_options"],
                 provenance=dict(green="osm_green" if b["provenance"]["green"] == "osm_green" else "hole_line_end",
                                 par=par_src.get(k, "length rule")))
        h["green_polygon"] = h["green_polygon_ll"]
        hp = (feats_now.get(k) or {}).get("properties", {})
        if hp.get("review_green"):
            h["provenance"]["green"] = "review (snapped to OSM green)" if b["provenance"]["green"] == "osm_green" else "review"
        if hp.get("renumbered_from"):
            h["provenance"]["number"] = f"review: was hole {hp['renumbered_from']}"
        if k in routed:
            h["provenance"]["hole"] = f"routing:{routed[k]['status']}"
            h["routing"] = routed[k]
        holes[k] = apply_tee_line(h)

    stages["imagery"] = f"ok: {imagery['dir']} ({imagery['source']}, {imagery['year']})" if imagery else "missing"
    check_green_visibility(holes, img_dir, imagery, stages, warnings)
    tee_sets = {}
    for name, s in card_sets.items():
        r = s.get("ratings") or []
        tee_sets[name] = dict(colour=s.get("colour"), aliases=s.get("aliases", []), yards=s.get("yards"),
                              par=s.get("par") or card.get("par"), total=s.get("total"),
                              rating=s.get("rating") or (r[0].get("rating") if r else None),
                              slope=s.get("slope") or (r[0].get("slope") if r else None),
                              source=s.get("source") or cinfo["source"])
    if not tee_sets:
        tee_sets["osm_back"] = dict(colour=None, aliases=["back"], yards=None, par=None, total=None, rating=None,
                                    slope=None, source="OSM tee nearest each hole-line start (no scorecard)")
    town = course.get("town")
    card_city = ((card or {}).get("course") or {}).get("city") if isinstance((card or {}).get("course"), dict) else None
    card_city = card_city or ((card or {}).get("facility") or {}).get("city")
    if card_city and (not town or "county" in str(town).lower()):
        town = card_city
    course = dict(course, town=town)
    bnd = course.get("boundary")
    ring = None
    if bnd:                                       # every outer ring (QA P1: SH holes 5-9 are a 2nd/3rd ring)
        polys = [bnd["coordinates"]] if bnd["type"] == "Polygon" else list(bnd["coordinates"])
        ring = dict(type="MultiPolygon", coordinates=polys)
    package = dict(
        schema=SCHEMA, slug=slug, built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        request=req,
        course=dict({k: course.get(k) for k in ("name", "osm", "center", "bbox", "town", "state", "address",
                                                "website", "holes_mapped", "candidates")},
                    slug=slug, city=course.get("town"), boundary=ring, boundary_geojson=bnd),
        sources=dict(osm=dict(fetched=summ.get("fetched_utc"), file=os.path.relpath(os.path.join(raw, "osm.geojson"), pc.ROOT),
                              attribution="(c) OpenStreetMap contributors, ODbL 1.0"),
                     scorecard=dict(kind=cinfo["kind"], source=cinfo["source"], url=cinfo.get("url"),
                                    confidence=card_confidence(cinfo["kind"], (cinfo.get("consistency") or {}).get("ok", True)),
                                    tried=cinfo["tried"], consistency=cinfo.get("consistency"),
                                    cross_check=cinfo.get("cross_check"), attribution=cinfo.get("attribution")),
                     imagery=imagery, dem=elevation, vision_raw=vision_raw_dirs(slug, course)),
        tee_set=chosen_key if chosen_key else "osm_back",
        tee_set_info=dict(requested=wanted, chosen=chosen, how=how,
                          colour=card_sets.get(chosen, {}).get("colour") if chosen else None,
                          substituted=bool(substituted),
                          warning=substituted or (None if card else "no scorecard: back tee (OSM tee nearest each "
                                                                    "hole-line start)")),
        tee_sets=tee_sets, scorecard=dict(kind=cinfo["kind"], source=cinfo["source"], url=cinfo.get("url"),
                                          confidence=card_confidence(cinfo["kind"], (cinfo.get("consistency") or {}).get("ok", True)),
                                          flags=(cinfo.get("consistency") or {}).get("flags", [])),
        imagery=imagery, elevation=elevation,
        frame="yard",
        frame_doc="zones_ll / *_ll are WGS84 [lon, lat] and frame-free. zones, tee, dot270, green, hole_line are "
                  "the yard frame of tee_set (x = yds right of the tee line, y = -yds along it; tee (0,0), "
                  "dot270 (0,-270)), derived by platform/package.py reframe(). Pixel frame per hole: "
                  "px = pixel.tee_px + pixel.ppy * (x, y) (920 x 2000, the image / book frame).",
        holes=holes, stages=stages, warnings=warnings, pipeline=pipe,
        attribution=["(c) OpenStreetMap contributors, ODbL 1.0", "USDA NAIP (public domain)", "USGS 3DEP (public domain)"]
        + ([scm.OPENGOLFAPI_ATTRIBUTION] if cinfo.get("kind") == "opengolfapi" or "opengolfapi" in (cinfo.get("cross_check") or {})
           else []))
    for f in (cinfo.get("consistency") or {}).get("flags", []):
        warnings.append(f"scorecard ({cinfo['kind']}): {f}")
    if package["tee_set"] == "osm_back":
        for h in holes.values():
            if None in h["tees"]:
                h["tees"]["osm_back"] = h["tees"].pop(None)

    # elevation for every tee set
    sample = dem_sampler(os.path.join(pc.ROOT, elevation["file"])) if elevation else None
    if sample is not None:
        n_ok = 0
        for k, h in holes.items():
            for s, t in h["tees"].items():
                fr = _frame(t["tee_ll"], t["aim_ll"])
                g = fr.ll_to_yds(np.array([h["green_ll"]]))[0]
                hh = dict(ref=k, par=h["par"], length=t["card_yards"] or t["measured_yards"],
                          measured_length=t["measured_yards"], green=[float(g[0]), float(g[1])],
                          bearing_deg=t["bearing_deg"])
                try:
                    t["elevation"] = elevation_for_hole(hh, sample, fr.yds_to_ll)
                    n_ok += t["elevation"] is not None and s == package["tee_set"]
                except Exception as e:                           # noqa: BLE001
                    t["elevation"] = None
                    warnings.append(f"hole {k} {s}: elevation failed ({type(e).__name__}: {e})")
        stages["elevation"] = f"ok: {elevation['file']} ({n_ok}/{len(holes)} holes)"
    else:
        stages["elevation"] = "missing (no DEM)"

    package = reframe(package)
    if gapfill:
        package = call_gapfill(package, img_dir, warnings)
        package["warnings"] = warnings if package.get("warnings") is None else package["warnings"]
        package = call_segment_fill(package, warnings)
        package = call_fairway_fill(package, fc, req, warnings)
        package = reframe(package)
    else:
        stages["vision"] = "not run (gapfill=False)"
    package = call_ob(package, warnings)
    package = apply_agent_layers(req, package, warnings)
    package["coverage"] = osm_coverage.coverage(fc, package["holes"])
    if render:
        package["stages"]["images"] = render_images(package, pkg_dir, img_dir)
    return package


def _yard_poly(fr, ring):
    from shapely.geometry import Polygon as SPoly
    p = SPoly(fr.ll_to_yds(np.asarray(ring, float)))
    return p if p.is_valid else p.buffer(0)


def reframe(package, tee_set=None):
    """Yard-frame view of every hole for `tee_set` (default package["tee_set"]) from the WGS84 data
    (tees[set].tee_ll / aim_ll, green_ll, green_polygon_ll, hole_line_ll, zones_ll): zones clipped to the
    hole window, sorted by the lie order (later wins), par-3 entries, pixel frame (geometry.frame_for 'fit'),
    then confidence, landing lies, exposure and notes. Returns a new dict; the input is not modified."""
    from shapely.geometry import LineString, Point, box
    from shapely.geometry import Polygon as SPoly
    bh = geometry()
    p = copy.deepcopy(package)
    s = tee_set or p.get("tee_set")
    p["tee_set"] = s
    for k, h in p["holes"].items():
        apply_tee_line(h)
        t = h["tees"].get(s)
        if t is None:                                            # set not on this hole: nearest by length
            t = next(iter(h["tees"].values()))
            h.setdefault("flags", []).append(f"tee set {s} missing on this hole")
        elif t.get("tee_source") == "lidar":
            h.setdefault("flags", []).append(f"{s} tee on a lidar pad (no OSM box at {t.get('card_yards')} yds)")
        elif t.get("tee_source") in ("segment", "scene", "texture"):
            h.setdefault("flags", []).append(f"{s} tee on an imagery-detected pad ({t['tee_source']}; no OSM box at "
                                             f"{t.get('card_yards')} yds)")
        elif str(t.get("method", "")).startswith("walkback"):
            h.setdefault("flags", []).append(f"{s} tee walked back along the hole line (no box at {t.get('card_yards')} yds)")
        if t.get("order_ok") is False:
            h.setdefault("flags", []).append(f"{s} tee out of order with the other sets")
        gv = h.get("green_visibility") or {}
        if gv.get("visible") is False:
            h.setdefault("flags", []).append(
                f"green not visible on the NAIP {gv.get('year')} imagery (NDVI {gv.get('ndvi')} vs "
                f"{gv.get('course_median')} on the course's other greens: bare soil / construction); "
                "the outline is OSM's")
        fr = _frame(t["tee_ll"], t["aim_ll"])
        Y = lambda ll: fr.ll_to_yds(np.asarray(ll, float))      # noqa: E731
        green = Y([h["green_ll"]])[0]
        gpoly = _yard_poly(fr, h["green_polygon_ll"]) if h.get("green_polygon_ll") else None
        line = Y(h["hole_line_ll"])
        W_ = lambda xy: np.c_[np.asarray(xy)[:, 0], -np.asarray(xy)[:, 1]]   # noqa: E731  yard -> (right, along)
        path, L, _, _, _ = bh._tee_path(np.zeros(2), W_(line), W_([green])[0])
        far = max([-green[1]] + ([-y for _, y in gpoly.exterior.coords] if gpoly is not None else []))
        reach = max(WINDOW_MIN, far + WINDOW_PAST)
        win = box(-WINDOW_LAT, -reach, WINDOW_LAT, WINDOW_BEHIND)
        order = []
        for i, z in enumerate(h.get("zones_ll") or []):
            lie = z.get("lie")
            key = "ob_boundary" if (lie == "ob" and str(z.get("src", "")).endswith("course_boundary")) else lie
            order.append((LIE_ORDER.index(key) if key in LIE_ORDER else 0, i, z))
        order.sort(key=lambda o: (o[0], o[1]))
        zones, zsrc = [], []
        for _, _, z in order:
            try:
                g = _yard_poly(fr, z["poly"]).intersection(win)
            except Exception:                                    # noqa: BLE001
                continue
            if g.is_empty:
                continue
            for piece in bh._holefree(g):
                if piece.area < 1.5:
                    continue
                zones.append([MODEL_LIE.get(z["lie"], z["lie"]),
                              [[round(x, 1), round(y, 1)] for x, y in piece.exterior.coords[:-1]]])
                zsrc.append(z.get("src", "osm"))
        card_y = t.get("card_yards")
        h.update(tee_ll=t["tee_ll"], aim_ll=t["aim_ll"], bearing_deg=t["bearing_deg"],
                 green_bearing_deg=bearing(t["tee_ll"], h["green_ll"]),
                 length=int(card_y) if card_y else int(round(t["measured_yards"])),
                 measured_length=t["measured_yards"], tee_choice=t["tee_choice"],
                 tee=[0.0, 0.0], dot270=[0.0, -270.0], green=[round(float(green[0]), 1), round(float(green[1]), 1)],
                 hole_line=[[round(float(x), 1), round(float(-a), 1)] for x, a in path],
                 green_polygon_yd=[[round(x, 1), round(y, 1)] for x, y in gpoly.exterior.coords[:-1]] if gpoly is not None else None,
                 zones=zones, zone_src=zsrc, elevation=t.get("elevation"))
        h["provenance"].update(tee=f"tees:{t['method']}", length=f"card:{s}" if card_y else "measured",
                               bearing="geodesic tee -> aim_ll, degrees true", aim=tl.RULE)
        # pixel frame: geometry.frame_for 'fit' in (right, along) coordinates
        gW = SPoly(W_(np.array(gpoly.exterior.coords))) if gpoly is not None else None
        _, ppy, tee_px, _, _, _ = bh.frame_for(np.zeros(2), np.array([0.0, 1.0]), gW, W_([green])[0],
                                               h["par"], h["length"], "fit")
        h["pixel"] = dict(ppy=round(float(ppy), 4), tee_px=[round(float(tee_px[0]), 1), round(float(tee_px[1]), 1)],
                          size=[W, H], proj="utm")
        h.pop("par3", None)
        if h["par"] == 3 and gpoly is not None:
            h["par3"] = par3_entry(h, gpoly)
    finish(p)
    return p


def par3_entry(h, gpoly):
    """course.PAR3 fields in the yard frame: flag = green centre; green outline as (yds right, yds past the flag)."""
    tee = np.zeros(2)
    flag = np.array(h["green"], float)
    v = flag - tee
    center = float(np.linalg.norm(v))
    fwd = v / center
    right = np.array([-fwd[1], fwd[0]])
    rel = np.array(gpoly.simplify(0.3).exterior.coords[:-1]) - flag
    green = [[round(float(q @ right), 1), round(float(q @ fwd), 1)] for q in rel]
    past = [g[1] for g in green]
    return dict(tee=[0.0, 0.0], flag=[round(float(flag[0]), 1), round(float(flag[1]), 1)], center=round(center),
                front=round(center + min(past)), back=round(center + max(past)), green=green, source="package")


def exposure(h):
    """Share of the landing zone's lateral edges (40-60 yds off the line, 220-340 along) that is trees."""
    from matplotlib.path import Path
    a = np.arange(220, 341, 10.0)
    pts = np.array([[sgn * d, -al] for al in a for d in (40.0, 50.0, 60.0) for sgn in (-1, 1)])
    hit = np.zeros(len(pts), bool)
    for n, poly in h["zones"]:
        if n == "recovery":
            hit |= Path(np.array(poly, float)).contains_points(pts)
    return round(float(hit.mean()), 3)


def finish(package):
    """Confidence, landing lies, par-3 hazards, exposure and notes from the current yard-frame zones."""
    pl = pipeline()
    for k, h in package["holes"].items():
        src = h.get("zone_src") or ["osm"] * len(h["zones"])
        h_osm = dict(h, zones=[z for z, s_ in zip(h["zones"], src) if str(s_).startswith("osm")])
        hh = dict(h, has_green_polygon=h["provenance"]["green"] == "osm_green")
        if not hh["has_green_polygon"]:
            hh["green_from"] = "hole_line_end"
        card = dict(par=h["par"] if str(h["provenance"]["par"]).startswith("card") else None,
                    yards=h["length"] if str(h["provenance"]["length"]).startswith("card") else None)
        c = pl.confidence(hh, h_osm, {"par": h["par"]} if h["provenance"]["par"] == "osm" else {}, card, k)
        c["flags"] = c["flags"] + h.pop("flags", [])
        h["confidence"] = c
        lies = {}
        for z, s_ in zip(h["zones"], src):
            lies.setdefault(z[0], set()).add(str(s_).split(":")[0])
        h["provenance"]["zones"] = {lie: "+".join(sorted(v)) for lie, v in sorted(lies.items())}
        h["landing_lies"] = landing_lies(h) if h["par"] >= 4 else {}
        if not h.get("exposure_src", "").startswith("vision"):
            h["exposure"] = exposure(h) if h["par"] >= 4 else 0.0
            h["exposure_src"] = "zones"
        if h.get("par3"):
            h["par3"]["haz"] = par3_haz(h)
            bad = [f"{v} {s_}" for s_, v in h["par3"]["haz"].items() if v != "rough"]
            h["par3"]["short"] = ", ".join(bad) + "." if bad else "No mapped trouble near the green."
            h["par3"]["note"] = f"Auto-built ({'+'.join(sorted({str(x).split(':')[0] for x in src})) or 'osm'}). {h['par3']['short']}"
        src_txt = "OSM" + (" + imagery" if c["imagery"] > 0 else "")
        h["note"] = (f"Auto-built ({src_txt}; confidence {c['score']:.2f}, {c['band']}). Tee: {h['tee_choice']}."
                     + (" Check: " + "; ".join(c["flags"][:3]) + "." if c["flags"] else ""))


# ----------------------------------------------------------------------------- outputs
COURSE_MODULE = '''"""Course module for {name} ({tee_set} tees), generated from package.json by
course_data/platform/package.py on {built}. Do not edit; rebuild with

  python course_data/platform/package.py build course_data/requests/package_{slug}.json

Same API as spirit_hollow/course.py (HOLES, PAR3, NOTES, AIM_AT, ORDER, LABELS, APP, GREEN_SIDE) in each
hole's 920 x 2000 pixel frame (px = tee_px + ppy * yard-frame point), so mozingo/tee_strategy.py and
mozingo/yardage_book.use_course() take it unchanged:

  yb.use_course(NAME, DIR, PREFIX, HOLES, PAR3, NOTES, AIM_AT, ORDER, LABELS)
"""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(DIR, "package.json")) as _fh:
    PACKAGE = json.load(_fh)
NAME = PACKAGE["course"]["name"]
PREFIX = "{prefix}"
TEE_SET = PACKAGE["tee_set"]


def _key(k):
    return int(k) if str(k).isdigit() else k


def _px(h, p):
    ppy, (tx, ty) = h["pixel"]["ppy"], h["pixel"]["tee_px"]
    return (round(tx + ppy * p[0], 1), round(ty + ppy * p[1], 1))


HOLES, PAR3, NOTES, AIM_AT = {{}}, {{}}, {{}}, {{}}
for _k, _h in PACKAGE["holes"].items():
    _z = [(n, [_px(_h, p) for p in poly]) for n, poly in _h["zones"]]
    _hole = dict(par=_h["par"], image=_h.get("image"), length=_h["length"], tee=_px(_h, (0, 0)),
                 dot270=_px(_h, (0, -270)), green=_px(_h, _h["green"]), zones=_z, aim_min=-60, aim_max=60,
                 px_per_yd=_h["pixel"]["ppy"], hole_line=[_px(_h, p) for p in _h["hole_line"]],
                 tee_ll=_h["tee_ll"], aim_ll=_h["aim_ll"], green_ll=_h["green_ll"], bearing_deg=_h["bearing_deg"],
                 auto=_h["confidence"], elevation=_h.get("elevation"))
    NOTES[_key(_k)] = _h.get("note", "Auto-built.")
    _p3 = _h.get("par3")
    if _p3:
        PAR3[_key(_k)] = dict(_p3, image=_h.get("image"), tee=_px(_h, _p3["tee"]), flag=_px(_h, _p3["flag"]),
                              green=[tuple(q) for q in _p3["green"]], zones=_z, auto=_h["confidence"])
    else:
        HOLES[_key(_k)] = _hole
        AIM_AT[_key(_k)] = "Centre of the fairway"

ORDER = sorted(set(HOLES) | set(PAR3), key=lambda k: (str(k).rstrip("BF").zfill(3), str(k)))
LABELS = {{}}
APP, GREEN_SIDE = {{}}, {{}}
'''


def qa_md(p):
    c = p["course"]
    s = p["coverage"]["summary"]
    lines = [f"# {c['name']} ({c.get('town')}, {c.get('state')}) - {p['tee_set']} tees",
             "", f"Built {p['built']}. OSM {c['osm']['type']}/{c['osm']['id']}. Scorecard: {p['scorecard']['kind']} "
             f"({p['scorecard']['source']}). Tee set: {p['tee_set_info']['how']}.", ""]
    if (p.get("tee_set_info") or {}).get("substituted"):
        lines += [f"**WARNING: {p['tee_set_info']['warning']}**", ""]
    lines += ["## Coverage", "", "| | |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in s.items()]
    lines += ["", "OSM features inside the course: " + ", ".join(f"{k} {v}" for k, v in p["coverage"]["features"].items()), "",
              "## Holes", "", "| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, h in p["holes"].items():
        cf = h["confidence"]
        lines.append(f"| {k} | {h['par']} | {h['length']} / {h['measured_length']} | {h['bearing_deg']:.0f} | {cf['score']:.2f} | "
                     f"{cf['band']} | {cf['osm']:.0%} | {cf['imagery']:.0%} | {cf['inferred']:.0%} | {h['tee_choice']} | "
                     f"{'; '.join(cf['flags'])} |")
    lines += ["", "## Stages", ""] + [f"- **{k}**: {v}" for k, v in p["stages"].items()]
    if p["warnings"]:
        lines += ["", "## Warnings", ""] + [f"- {w}" for w in p["warnings"]]
    return "\n".join(lines) + "\n"


def render_images(package, pkg_dir, img_dir):
    if not img_dir:
        return "missing (no imagery)"
    rd = load(os.path.join(CD, "imagery", "render.py"), "cdp_render")
    try:
        img = rd.Imagery(img_dir)
    except Exception as e:                                       # noqa: BLE001
        return f"failed: {type(e).__name__}: {e}"[:200]
    n = 0
    for k, h in package["holes"].items():
        name = f"hole{int(k):02d}.png" if str(k).isdigit() else f"hole{k}.png"
        try:
            rd.render_hole(pkg_dir, h, os.path.join(pkg_dir, "screenshots", name),
                           frame=dict(tee_ll=h["tee_ll"], aim_ll=h["aim_ll"], ppy=h["pixel"]["ppy"],
                                      tee_px=h["pixel"]["tee_px"], proj="utm"), imagery=img)
            h["image"] = name
            n += 1
        except Exception as e:                                   # noqa: BLE001
            pc.log("render", k, e)
    return f"ok: {n}/{len(package['holes'])} rendered from {os.path.relpath(img_dir, pc.ROOT)}"


def apply_agent_layers(req, package, warnings=None):
    """S5: request "agent_layers" (a folder with agent_zones.geojson / agent_tees.json, course_data/mapper/apply.py)
    -> the package with the mapper agent's layers. Never fails the build: problems go to stages + warnings."""
    d = (req or {}).get("agent_layers")
    if not d:
        return package
    warnings = package.setdefault("warnings", []) if warnings is None else warnings
    stages = package.setdefault("stages", {})
    path = d if os.path.isabs(d) else os.path.join(pc.ROOT, d)
    mod = load(os.path.join(CD, "mapper", "apply.py"), "cdp_mapper_apply")
    if not os.path.isdir(path) or mod is None:
        stages["agent_layers"] = f"missing: {d}" + (" (no such folder)" if not os.path.isdir(path) else
                                                    " (course_data/mapper/apply.py not importable)")
        warnings.append(f"agent_layers not applied: {stages['agent_layers']}")
        return package
    try:
        out, _ = mod.apply(package, path, pk=sys.modules[__name__])
    except Exception as e:                                       # noqa: BLE001
        stages["agent_layers"] = f"failed: {type(e).__name__}: {e}"[:300]
        warnings.append(f"agent_layers not applied: {stages['agent_layers']}")
        return package
    if out.get("warnings") is not warnings:
        out["warnings"] = warnings
    return out


def reapply_corrections(package, pkg_dir):
    """Golfer corrections from the review page (packages/<slug>/corrections.json, product/apply_answers.py)
    survive a rebuild: matched to the new zones by lie + overlap and redone. Never fails the build."""
    path = os.path.join(pkg_dir, "corrections.json")
    if not os.path.exists(path):
        return None
    try:
        aa = load(os.path.join(CD, "product", "apply_answers.py"), "cdp_apply_answers")
        if aa is None:
            return None
        res = aa.reapply(package, pc.read_json(path), reframe=reframe, log=pc.log)
        package.setdefault("warnings", []).append(
            f"golfer corrections re-applied: {res['applied']} (skipped {len(res['skipped'])})")
        return res
    except Exception as e:                                       # noqa: BLE001
        pc.log(f"! corrections not re-applied: {type(e).__name__}: {e}")
        return None


def write(package, pkg_dir):
    reapply_corrections(package, pkg_dir)
    pc.write_json(os.path.join(pkg_dir, "package.json"), package, indent=None)
    slug = package["slug"]
    with open(os.path.join(pkg_dir, "course_auto.py"), "w") as fh:
        fh.write(COURSE_MODULE.format(name=package["course"]["name"], tee_set=package["tee_set"],
                                      built=package["built"], slug=slug,
                                      prefix="".join(w.title() for w in slug.split("_")) + "_Auto"))
    with open(os.path.join(pkg_dir, "qa.md"), "w") as fh:
        fh.write(qa_md(package))
    pc.write_json(os.path.join(pkg_dir, "coverage.json"), package["coverage"])


def build_request(req_path, render=False, allow_substitute=False):
    import fetch_package as fp
    req = pc.read_json(req_path)
    if allow_substitute:
        req = dict(req, allow_substitute=True)
    slug = fp.request_slug(req, req_path)
    pkg_dir = os.path.join(pc.PACKAGES, slug)
    package = build_package(req, pkg_dir, render=render)
    write(package, pkg_dir)
    s = package["coverage"]["summary"]
    print(f"{slug}: {package['course']['name']} | tee set {package['tee_set']} ({package['tee_set_info']['how']}) | "
          f"{len(package['holes'])} holes | {json.dumps(s)}")
    return package


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["build", "run"])
    ap.add_argument("requests", nargs="+")
    ap.add_argument("--render", action="store_true", help="render holeNN.png from the imagery")
    ap.add_argument("--allow-substitute", action="store_true",
                    help="build the longest set when the requested tee set is not on the card (else an error)")
    a = ap.parse_args()
    paths = [p for r in a.requests for p in sorted(glob.glob(r))]
    failed = []
    for p in paths:
        try:
            if a.cmd == "run":
                import fetch_package as fp
                slug, status = fp.fetch(p)
                if status != "ok":
                    print(f"{slug}: {status}; see packages/{slug}/raw/course.json for the candidates")
                    failed.append(p)
                    continue
            req = pc.read_json(p)
            build_request(p, render=a.render or bool(req.get("render")), allow_substitute=a.allow_substitute)
        except SystemExit as e:
            print(f"{p}: {e}")
            failed.append(p)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
