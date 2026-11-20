"""Fast path: course name -> package + per-hole strategy, one command, one machine, raw fetches cached on disk.

  python3 course_data/platform/fastpath/fast.py "Crow Canyon Country Club, San Ramon, CA" [--slug S] [--n 2000]
          [--no-imagery] [--refetch]
  -> cache/packages/<slug>/{raw/, imagery/, package.json, decision.json, timing.json}

Stages (timed; timing.json): resolve (national index + OSM API) > OSM features (OSM API bbox) > scorecards ||
imagery (NAIP + 3DEP) > package build (platform/package.py build_package, unchanged) > solve (solve.py).
"""
import os as _os
_os.environ.setdefault("OMP_WAIT_POLICY", "PASSIVE")   # before any OpenMP runtime loads (lightgbm, sklearn,
# fastc): spinning OpenMP threads otherwise steal the cores OpenBLAS needs in the U-Net (31 s -> 62 s on Yorba Linda)
import argparse
import gzip
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(HERE)
CD = os.path.dirname(PLAT)
ROOT = os.path.dirname(CD)
CACHE = os.environ.get("FASTPATH_CACHE") or os.path.join(HERE, "cache")
sys.path[:0] = [HERE, PLAT]
import platform_common as pc  # noqa: E402

pc.PACKAGES = os.path.join(CACHE, "packages")
import osm_api  # noqa: E402

_ROWS = None
LATE = {}                # the card search thread of the last build (two-phase: wait_card() then build again)
CARD_BUDGET_S = 15.0     # the longest the build waits for the card search, from the start of the fetch
CARD_GRACE_S = 1.0       # ... and at most this long after the imagery / canopy fetches are done


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"['’]", "", s)
    return [w for w in re.sub(r"[^a-z0-9]+", " ", s).split() if w not in ("the", "golf", "course", "club", "country", "and", "at", "of", "cc", "gc")]


def index_rows():
    global _ROWS
    if _ROWS is None:
        d = json.load(gzip.open(os.path.join(CD, "library", "us_courses.json.gz")))
        _ROWS = [dict(zip(d["fields"], r)) for r in d["rows"]]
    return _ROWS


def lookup(query):
    """'Name, City, ST' (city optional) -> the best national-index row, or None. The app's pick screen does this
    on the phone (course_index.js); here: every name word must match, city breaks ties."""
    parts = [p.strip() for p in query.split(",")]
    st = parts[-1].upper() if len(parts) > 1 and len(parts[-1].strip()) == 2 else None
    if st is None and len(parts) > 1:
        st = pc.state_code(parts[-1])
    name = parts[0]
    city = parts[1] if len(parts) > 2 else ""
    want = set(norm(name))
    best = None
    for r in index_rows():
        if st and r["state"] != st:
            continue
        got = set(norm(r["name"]))
        if not want or not want <= got and not got <= want:
            continue
        sc = len(want & got) / max(len(want | got), 1) + (0.5 if city and norm(city) == norm(r["city"]) else 0) - (0.3 if r["closed"] else 0)
        if best is None or sc > best[0]:
            best = (sc, r)
    return best and best[1]


MAX_CONFIRMS = 3                # a course routed on imagery detections: at most this many flagged holes is shown
SOFT_GATE_PREFIXES = ("the card does not fit the map", "holes out of order", "built pars sum")   # auto policy: warnings
GATE_SHARED_GREEN_YD = 15.0     # two holes whose greens are this close are one hole built twice
GATE_MISFIT_YD, GATE_MISFIT_HOLES = 25.0, 3   # card vs measured yards off by more than this on this many holes


def extra_gate(package):
    """Blocks the course-page gate does not have (blind loop 2026-11-09, Down River: hole 12 routed onto hole 1's
    green; the card 50-125 yds longer than the map on 3 holes). -> reasons (empty: publishable)."""
    import math
    out = []
    S = package.get("tee_set")
    hs = sorted(package["holes"].items(), key=lambda kv: (len(kv[0]), kv[0]))
    g = [(r, h.get("green_ll")) for r, h in hs if h.get("green_ll")]
    for i, (ra, a) in enumerate(g):
        for rb, b in g[i + 1:]:
            k = math.cos(math.radians(a[1]))
            if math.hypot((a[0] - b[0]) * k, a[1] - b[1]) * 111320.0 / 0.9144 <= GATE_SHARED_GREEN_YD:
                out.append(f"holes {ra} and {rb} share a green: one of them is not routed")
    bad = []
    for r, h in hs:
        t = (h.get("tees") or {}).get(S) or {}
        card = (h.get("yards") or {}).get(S) if isinstance(h.get("yards"), dict) else None
        if card and t.get("measured_yards") and abs(card - t["measured_yards"]) > GATE_MISFIT_YD:
            bad.append(f"{r} ({card} vs {t['measured_yards']})")
    if len(bad) >= GATE_MISFIT_HOLES:
        out.append(f"the card does not fit the map on {len(bad)} holes (card vs measured yards: {', '.join(bad)}): "
                   "wrong card, or holes numbered differently")
    return out


def _mark_confidence(package, p_holes, warnings, source, pkg_dir, p_all=None):
    """auto policy: per-hole calibrated P(hole right) into package.json (holes[ref].p_right / approximate, and
    routing_confidence), rewritten in place"""
    import package as pk
    import route_gate
    for ref, pr in p_holes.items():
        h = (package.get("holes") or {}).get(str(ref))
        if isinstance(h, dict):
            h["p_right"] = pr
            h["approximate"] = bool(pr < route_gate.APPROX_P)
    if p_all is None and p_holes:
        import math
        p_all = float(math.prod(p_holes.values()))
    package["routing_confidence"] = dict(policy="auto", source=source, p_all=p_all, p_holes=dict(p_holes),
                                         approximate=[str(r) for r, p in p_holes.items() if p < route_gate.APPROX_P],
                                         approx_below=route_gate.APPROX_P, warnings=list(warnings))
    pk.write(package, pkg_dir)


def wait_card(seconds=60.0):
    """True when the card search of the last build was still running at its budget and has now finished
    (seconds=None: wait until it finishes)."""
    t = LATE.get("card")
    if t is None or not t.is_alive():
        return False
    t.join(seconds)
    return not t.is_alive()


def build(query, slug=None, n=2000, imagery=True, row=None, log=print, extra=None, year="auto", canopy_trees=True):
    T = {}
    t_all = time.time()

    def lap(name, t0):
        T[name] = round(time.time() - t0, 2)
        log(f"  {name}: {T[name]} s")
    t0 = time.time()
    row = row or lookup(query)
    if row is None:
        return dict(status="not_found", query=query)
    slug = slug or pc.slugify(row["name"]) + "_" + row["state"].lower()
    pkg_dir = os.path.join(pc.PACKAGES, slug)
    raw = os.path.join(pkg_dir, "raw")
    os.makedirs(raw, exist_ok=True)
    prefetch = None                # the NAIP search round the index point runs while the outline is resolved
    if imagery and not os.path.exists(os.path.join(pkg_dir, "imagery", "georef.json")):
        import fast_imagery as fim
        prefetch = ThreadPoolExecutor(1).submit(fim.stac_prefetch, row["lat"], row["lon"])
    course = osm_api.course_from_row(row, CACHE)
    pc.write_json(os.path.join(raw, "course.json"), course)
    lap("resolve", t0)
    if course["status"] != "ok":
        return dict(status=course["status"], slug=slug, why=course.get("closed"))
    req = dict(schema="request/1", kind="package", course=row["name"], state=row["state"], slug=slug, tees="Black",
               allow_substitute=True, builder="fastpath", town=row.get("city"), osm=row["osm"],
               near=f"{row['lat']:.5f},{row['lon']:.5f}", **(extra or {}))
    pc.write_json(os.path.join(pkg_dir, "package_request.json"), req)
    import fetch_package as fp
    from concurrent.futures import Future
    osm_future = Future()          # the year scoring needs the OSM turf; the NAIP listing, DEM and canopy only the bbox
    summ_future = Future()         # the card checks need the OSM hole lengths; three of its four sources do not

    def cards():
        t = time.time()
        if not os.path.exists(os.path.join(raw, "scorecard_web.json")):
            fp.fetch_scorecards(req, course, summ_future, raw, parallel=True)
        T["card"] = round(time.time() - t, 2)

    def img():
        t = time.time()
        if imagery and not os.path.exists(os.path.join(pkg_dir, "imagery", "georef.json")):
            import fast_imagery as fim
            _, ti = fim.fetch(course["bbox"], os.path.join(pkg_dir, "imagery"), osm_future, year, label=course["name"],
                              prefetch=prefetch)
            T.update(ti)
        T["imagery"] = round(time.time() - t, 2)
    def route_no_lines():
        """OSM maps greens + tees but not the hole lines: joint routing (route_joint.py) -> golf=hole ways"""
        nonlocal fc, summ
        n_lines = sum(1 for f in fc["features"] if (f.get("properties") or {}).get("golf") == "hole"
                      and f["properties"].get("inside_course") is not False)
        n_green = sum(1 for f in fc["features"] if (f.get("properties") or {}).get("golf") == "green")
        n_tee = sum(1 for f in fc["features"] if (f.get("properties") or {}).get("golf") == "tee")
        import package as pk
        import route_joint
        t = time.time()
        card, _ = pk.pick_scorecard(req, raw, fc)
        n = len(next(iter(card["tee_sets"].values()))["yards"]) if card and card.get("tee_sets") else (row.get("holes") or 18)
        lines = route_joint.unnumbered_lines(fc, n)
        if lines is None and (n_lines >= 3 or n_green < 7 or n_tee < 5):
            return None
        try:
            r = route_joint.route_lines(fc, lines, card, n) if lines is not None else route_joint.route(fc, card, n)
        except Exception as e:                                       # noqa: BLE001
            T["route_joint"] = f"failed: {type(e).__name__}: {e}"[:200]
            return None
        if r.get("features"):
            if lines is not None:
                req["ignore_osm_holes"] = True          # the unnumbered OSM ways are replaced by their numbered copies
            sup = os.path.join(raw, "joint_holes.geojson")
            pc.write_json(sup, {"type": "FeatureCollection", "features": r["features"]})
            req["osm_supplement"] = sup
            pc.write_json(os.path.join(pkg_dir, "package_request.json"), req)
            fc, summ = osm_api.features(course, raw, CACHE, req)
        T["route_joint"] = round(time.time() - t, 2)
        try:                                     # per-hole card fit: the tier C confidence model's input
            import route_gate
            r["card_rel"] = route_gate.joint_card_rel(r.get("features"), card, n)
        except Exception:                                            # noqa: BLE001
            r["card_rel"] = None
        return {k: v for k, v in r.items() if k != "features"}

    def route_perception():
        """OSM has too little to route (tiers C / D): the fast-path perception scene (fastscene.py: NAIP + DEM +
        canopy pixel classifier -> perception detectors) adds greens / tee boxes / fairways, the joint solver routes
        OSM + detections (route_scene.py) -> golf=hole ways + the detected objects as an osm_supplement"""
        nonlocal fc, summ
        import package as pk
        import route_scene
        card, cinfo = pk.pick_scorecard(req, raw, fc)
        n = len(next(iter(card["tee_sets"].values()))["yards"]) if card and card.get("tee_sets") else (row.get("holes") or 18)
        if not imagery or os.environ.get("FASTPATH_PERCEPTION", "1") == "0" or not route_scene.needs_perception(fc, n):
            return None
        t = time.time()
        try:                                     # web cards only: a request / file / typed card is never replaced
            r, sup, ts = route_scene.run(pkg_dir, fc, card, n,
                                         card_select=(cinfo or {}).get("kind") not in ("request", "file", "typed"))
        except Exception as e:                                       # noqa: BLE001
            T["perception"] = f"failed: {type(e).__name__}: {e}"[:200]
            return None
        T["perception"] = ts
        cs = r.get("card_select") or {}
        if cs.get("switched") and cs.get("card"):   # the routed holes fit another web card better: the package uses it
            p = os.path.join(raw, "scene_card.json")
            pc.write_json(p, cs.pop("card"))
            req["scorecard"] = p
            pc.write_json(os.path.join(pkg_dir, "package_request.json"), req)
        cs.pop("card", None)
        if r.get("n_holes") and any((f.get("properties") or {}).get("golf") == "hole" for f in sup):
            p = os.path.join(raw, "scene_holes.geojson")
            pc.write_json(p, {"type": "FeatureCollection", "features": sup})
            req["osm_supplement"] = p
            pc.write_json(os.path.join(pkg_dir, "package_request.json"), req)
            fc, summ = osm_api.features(course, raw, CACHE, req)
        T["route_scene"] = round(time.time() - t, 2)
        return r

    def trees():
        t = time.time()
        if canopy_trees:
            import canopy
            canopy.fetch(course["bbox"], os.path.join(pkg_dir, "canopy"))
        T["canopy"] = round(time.time() - t, 2)
    # the fetch DAG: imagery (NAIP listing || DEM, then year scoring once OSM is in) || canopy || card search (its
    # checks once OSM is in) || OSM features. The build waits for the card only while the other fetches run, plus
    # CARD_GRACE_S, and never past CARD_BUDGET_S from the start of the fetch; a late card is picked up by wait_card()
    t0 = time.time()
    import threading
    with ThreadPoolExecutor(2) as ex:
        fs = [ex.submit(img), ex.submit(trees)]
        tc = threading.Thread(target=cards, daemon=True)
        tc.start()
        LATE["card"] = tc
        t = time.time()
        try:
            fc, summ = osm_api.features(course, raw, CACHE, req)
        except BaseException as e:
            osm_future.set_exception(e)
            summ_future.set_exception(e)
            raise
        osm_future.set_result(fc)
        summ_future.set_result(summ)
        lap("osm", t)
        for f in fs:
            f.result()
    tc.join(max(0.0, min(CARD_GRACE_S, CARD_BUDGET_S - (time.time() - t0))))
    if tc.is_alive():
        T["card_late"] = (f"still searching {round(time.time() - t0, 1)} s into the fetch: built without it "
                          "(wait_card() then build again, or a later run, reads the cached answer)")
    lap("fetch (card || imagery)", t0)
    routed = None
    scene_routed = None
    if not tc.is_alive():
        routed = route_no_lines()
        if routed is None:
            scene_routed = route_perception()
    t0 = time.time()
    import package as pk
    try:
        package = pk.build_package(req, pkg_dir)
    except SystemExit as e:
        T["total"] = round(time.time() - t_all, 2)
        pc.write_json(os.path.join(pkg_dir, "timing.json"), T)
        return dict(status="failed", stage="package", why=str(e)[:400], slug=slug, timing=T)
    lap("package build", t0)
    if canopy_trees and not str((package.get("stages") or {}).get("vision", "")).startswith("ok"):
        t0 = time.time()
        import canopy
        if canopy.add_trees(package, CACHE):
            st = package.get("stages")
            package = pk.reframe(package)
            package["stages"] = st
        lap("trees (Meta canopy)", t0)
    pk.write(package, pkg_dir)
    t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(HERE, "solve.py"), os.path.join(pkg_dir, "package.json"), "--n", str(n),
                        "--out", os.path.join(pkg_dir, "decision.json")], capture_output=True, text=True)
    lap("solve", t0)
    if r.returncode:
        log(r.stderr[-1500:])
    # the publish gate of the course-page pipeline (library/course_page.py): a map that is too wrong is never shown
    blocked = []
    try:
        sys.path.insert(0, os.path.join(CD, "library"))
        import course_page as cp
        blocked = cp.publish_gate(package, {"tees": package.get("tee_set")}, req.get("near"))
    except Exception as e:                                           # noqa: BLE001
        blocked = [f"gate could not run: {type(e).__name__}: {e}"]
    blocked += extra_gate(package)
    auto_warn = None
    if routed is not None:
        import route_joint
        import route_gate
        pc.write_json(os.path.join(pkg_dir, "route_joint.json"), routed)
        pj_ = None
        if route_gate.policy() == "auto" and routed.get("card_rel"):
            rows_ = route_gate.joint_rows(routed, routed["card_rel"], "lines" if routed.get("mode") else "osm")
            pj_ = route_gate.p_joint(rows_)
        if pj_:
            # ROUTE_SHOW_POLICY=auto: tier C delivered with per-hole confidence (route_gate_joint.json, calibrated on
            # mapped courses with their hole ways hidden); the margin rule and the soft gates become warnings
            soft = [b for b in blocked if b.startswith(SOFT_GATE_PREFIXES)]
            if routed.get("min_margin", 0.0) < route_joint.MIN_MARGIN or routed.get("n_virtual"):
                soft.append(f"joint routing min margin {routed.get('min_margin', 0):.1f} (< {route_joint.MIN_MARGIN}), "
                            f"{routed.get('n_virtual', 0)} holes without a tee or green")
            blocked = [b for b in blocked if not b.startswith(SOFT_GATE_PREFIXES)]
            auto_warn = soft
            _mark_confidence(package, pj_, soft, "route_joint", pkg_dir)
            routed["gate"] = dict(policy="auto", p_holes=pj_)
            pc.write_json(os.path.join(pkg_dir, "route_joint.json"), routed)
        elif routed.get("min_margin", 0.0) < route_joint.MIN_MARGIN or routed.get("n_virtual"):
            blocked.append(f"hole lines routed by the joint solver with min margin {routed.get('min_margin', 0):.1f} "
                           f"(< {route_joint.MIN_MARGIN}; {routed.get('n_virtual', 0)} holes without a tee or green): "
                           "the numbering is not certain")
    confirm = []
    draft = []
    if scene_routed is not None:
        import route_scene
        pc.write_json(os.path.join(pkg_dir, "route_scene.json"), scene_routed)
        if scene_routed.get("version") in ("v1", "v2"):
            # calibrated show / block (route_gate.py): shown only when P(every hole numbered right) clears the
            # threshold fitted on the routing bench; otherwise a draft, not shown, with the reason. No golfer questions.
            import route_gate
            g = route_gate.decide(scene_routed)
            scene_routed["gate"] = g
            pc.write_json(os.path.join(pkg_dir, "route_scene.json"), scene_routed)
            draft = [f"holes routed on imagery detections: {r}" for r in g["reasons"]]
            if g.get("policy") == "auto":
                # ROUTE_SHOW_POLICY=auto (default): delivered without golfer confirms. The quality gates that only say
                # the routing may be wrong (card misfit, long walks, par sum) become warnings; the per-hole P(right)
                # says where. Broken builds stay drafts: missing holes / no card / shared green / wrong course.
                soft = [b for b in blocked if b.startswith(SOFT_GATE_PREFIXES)]
                blocked = [b for b in blocked if not b.startswith(SOFT_GATE_PREFIXES)]
                auto_warn = soft
                refs = [str(h.get("ref")) for h in scene_routed.get("hole_features") or []]
                _mark_confidence(package, dict(zip(refs, g.get("p_holes") or [])), soft, "route_scene", pkg_dir,
                                 p_all=g.get("p_all"))
        else:
            import route_joint
            if scene_routed.get("min_margin", 0.0) < route_joint.MIN_MARGIN or scene_routed.get("n_virtual") \
                    or len(scene_routed.get("margins") or []) < scene_routed.get("n_holes", 0):
                blocked.append(f"hole lines routed on imagery detections with min margin {scene_routed.get('min_margin', 0):.1f} "
                               f"(< {route_joint.MIN_MARGIN}; {scene_routed.get('n_virtual', 0)} holes without a tee or green): "
                               "the routing is not certain")
            confirm = [f"hole {r}: green or tee from the imagery detector, confirm it" for r in scene_routed.get("detected_holes") or []]
            if len(confirm) > MAX_CONFIRMS:     # the blind-loop rule: more than 3 holes to check is not a usable page
                blocked.append(f"{len(confirm)} holes rest on imagery detections (more than {MAX_CONFIRMS}): shown only after "
                               "the golfer confirms them (confirm_scene.json)")
            pc.write_json(os.path.join(pkg_dir, "confirm_scene.json"), route_scene.confirm_questions(package, scene_routed))
    gate_out = dict(blocked=blocked, confirm=confirm, draft=draft)
    if auto_warn is not None:
        gate_out["policy"] = "auto"
        gate_out["warnings"] = auto_warn
    if routed is not None and routed.get("gate"):
        ph = routed["gate"]["p_holes"]
        gate_out["routing"] = dict(source="route_joint", p_holes=ph, unsure=[r for r, p in ph.items() if p < 0.5],
                                   policy="auto")
    if scene_routed is not None and scene_routed.get("gate"):
        # per-hole calibrated P(hole numbered right) next to the course-level P(all): a draft view can mark the unsure
        # holes; what is shown is decided by p_all and the hard blocks only
        gg = scene_routed["gate"]
        ph = gg.get("p_holes") or []
        refs = [h.get("ref") for h in scene_routed.get("hole_features") or []]
        gate_out["routing"] = dict(p_all=gg.get("p_all"), threshold=gg.get("threshold"),
                                   p_holes={str(r): p for r, p in zip(refs, ph)},
                                   unsure=[str(r) for r, p in zip(refs, ph) if p < 0.5],
                                   policy=gg.get("policy"))
    pc.write_json(os.path.join(pkg_dir, "gate.json"), gate_out)
    T["total"] = round(time.time() - t_all, 2)
    T["stages"] = package.get("stages")
    pc.write_json(os.path.join(pkg_dir, "timing.json"), T)
    if draft and not blocked and r.returncode == 0:
        return dict(status="draft", stage="gate", why="draft (not shown): " + "; ".join(draft)[:400], slug=slug,
                    holes=len(package["holes"]), timing={k: v for k, v in T.items() if k != "stages"}, dir=pkg_dir)
    if blocked and r.returncode == 0:
        if draft:
            blocked = draft + blocked
        return dict(status="blocked", stage="gate", why="; ".join(blocked)[:400], slug=slug, holes=len(package["holes"]),
                    timing={k: v for k, v in T.items() if k != "stages"}, dir=pkg_dir)
    if auto_warn is not None and r.returncode == 0:
        rc = package.get("routing_confidence") or {}
        how = "routed by the joint solver on OSM greens / tees" if rc.get("source") == "route_joint" else "routed on imagery detections"
        return dict(status="shown", stage=None, why=f"{how}, shown (policy auto): P(all) "
                    f"{(rc.get('p_all') or 0):.3f}, approximate holes {', '.join(rc.get('approximate') or []) or 'none'}"
                    + (f"; warnings: {'; '.join(auto_warn)}"[:300] if auto_warn else ""), slug=slug,
                    holes=len(package["holes"]), p_holes=rc.get("p_holes"), approximate=rc.get("approximate"),
                    timing={k: v for k, v in T.items() if k != "stages"}, dir=pkg_dir)
    if confirm and r.returncode == 0:
        return dict(status="confirm", stage="gate", why=f"usable with {len(confirm)} flagged confirms", slug=slug,
                    holes=len(package["holes"]), confirm=len(confirm), timing={k: v for k, v in T.items() if k != "stages"},
                    dir=pkg_dir)
    return dict(status="ok" if r.returncode == 0 else "failed", stage=None if r.returncode == 0 else "solve", slug=slug,
                holes=len(package["holes"]), confirm=len(confirm), timing={k: v for k, v in T.items() if k != "stages"}, dir=pkg_dir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--slug")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--no-imagery", action="store_true", help="the ~10 s point: OSM + card + solve (no NAIP / DEM)")
    ap.add_argument("--no-trees", action="store_true")
    ap.add_argument("--year", default="auto")
    a = ap.parse_args()
    print(json.dumps(build(a.query, a.slug, a.n, not a.no_imagery, year=a.year, canopy_trees=not a.no_trees), indent=1),
          flush=True)
    if LATE.get("card") is not None and LATE["card"].is_alive():
        t = time.time()
        done = wait_card(90)            # let the late card land in the cache, so the next run is built with it
        print(f"late card search {'finished' if done else 'still running'} {time.time() - t:.1f} s after the answer"
              + (" (cached: run again to build with it)" if done else ""), file=sys.stderr)
