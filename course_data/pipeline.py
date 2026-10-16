"""Auto-course orchestrator: "Spirit Hollow, white tees" -> holes.json + a course module + images.

  python3 course_data/pipeline.py --course "Spirit Hollow" --tees white
  python3 course_data/pipeline.py --course "Spirit Hollow" --tees white --lengths 1=413,2=609 --book

Thin on purpose: every stage lives in a team folder (see course_data/ARCHITECTURE.md) and is imported
defensively. A missing stage is reported and the pipeline falls back to the next-best source:

  S0/S1 course + OSM   course_data/<slug>/osm.geojson, summary.json   (fetch_course.py on Actions)
  S1 scorecard         <slug>/scorecard.json or course_data/tees/...   (tees/, on Actions)
  S2 tees              tee box by scorecard yardage                    (geometry.choose_tee; tees/place_tee.py)
  S3 holes             course_data/geometry/build_holes.build          (fallback: spike osm_to_model.convert)
  S4 gap-fill          <slug>/ vision zones GeoJSON                    (imagery/; optional)
  S5 images            imagery renderer, else a NAIP-preview fallback  (imagery/)
  S6 merge + QA        here: confidence per hole, holes.json, course_auto.py, qa.md

Nothing here touches the network. If the OSM extract is missing it prints the workflow to run.
"""
import argparse
import datetime as dt
import glob
import importlib.util
import json
import math
import os
import re
import sys
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, "mozingo")]

W, H = 920, 2000
LANDING = dict(a0=220, a1=340, lat=45, step=5)       # landing-zone grid (yds) for confidence + acceptance
PENAL = ("recovery", "native", "water", "sand", "ob")
MODEL_LIE = {"green": "fairway", "ob_boundary": "ob", "tee": "fairway", "trees": "recovery", "bunker": "sand"}


def model_zones(zones):
    """Map package lie names onto the model's (ARCHITECTURE 9.1-4): tee_strategy only knows
    fairway / first_cut / rough / sand / recovery / native / water / ob."""
    return [(MODEL_LIE.get(n, n), poly) for n, poly in zones]
LOG = []


def say(*a):
    msg = " ".join(str(x) for x in a)
    LOG.append(msg)
    print(msg, flush=True)


def slugify(name):
    s = re.sub(r"\b(golf|course|club|gc|country|cc|links|the)\b", " ", name.lower())
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_") or "course"


def load_module(path, name=None):
    """Import a file by path; None (with the reason printed) if it fails."""
    if not os.path.exists(path):
        return None
    name = name or "cd_" + os.path.splitext(os.path.relpath(path, HERE))[0].replace(os.sep, "_")
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:                                     # noqa: BLE001 - report and carry on
        say(f"  ! could not import {os.path.relpath(path, ROOT)}: {type(e).__name__}: {e}")
        return None


def find_fn(folder, names):
    """First function called one of `names` in any module of course_data/<folder>/."""
    for path in sorted(glob.glob(os.path.join(HERE, folder, "*.py"))):
        if os.path.basename(path).startswith(("test_", "fetch_")):
            continue
        mod = load_module(path)
        for n in names:
            if mod is not None and callable(getattr(mod, n, None)):
                return getattr(mod, n), f"{folder}/{os.path.basename(path)}:{n}"
    return None, None


# ----------------------------------------------------------------------------- S0 resolve
def resolve(course):
    """Course name -> (slug, dir, meta). Matches the course name recorded by fetch_course.py."""
    want = slugify(course)
    cands = []
    for s in sorted(glob.glob(os.path.join(HERE, "*", "summary.json"))) + \
            sorted(glob.glob(os.path.join(HERE, "*", "course.json"))):
        try:
            meta = json.load(open(s))
        except Exception:                                      # noqa: BLE001
            continue
        meta = meta.get("course", meta)
        name = meta.get("name", "")
        d = os.path.dirname(s)
        if slugify(name) == want or os.path.basename(d) == want or want in slugify(name):
            cands.append((d, meta))
    if cands:
        d, meta = cands[0]
        return os.path.basename(d), d, meta
    d = os.path.join(HERE, want)
    return want, d, None


def fetch_hint(course, slug):
    return (f'gh workflow run course_fetch.yml -f name="{course}" -f near="<lat,lon>" '
            f'-f out="course_data/{slug}"   # then git pull; Overpass/NAIP need Actions, not this sandbox')


# ----------------------------------------------------------------------------- S1 scorecard
def load_scorecard(slug, cdir, tee_set):
    """{ref: {par, yards}} for the tee set, from the tees/ stage or a scorecard.json; {} if none."""
    fn, where = find_fn("tees", ["load_scorecard", "scorecard_for", "get_scorecard"])
    if fn:
        try:
            sc = fn(slug, tee_set)
            if sc:
                say(f"  scorecard: {where}")
                return _norm_card(sc, tee_set), where
        except Exception as e:                                 # noqa: BLE001
            say(f"  ! {where} failed: {type(e).__name__}: {e}")
    paths = [os.path.join(cdir, "scorecard.json"), os.path.join(HERE, "tees", slug, "scorecard.json"),
             os.path.join(HERE, "tees", f"{slug}_scorecard.json"), os.path.join(HERE, "tees", "scorecard.json"),
             os.path.join(HERE, "tees", f"{slug}.json")]
    for p in paths:
        if os.path.exists(p):
            try:
                card = _norm_card(json.load(open(p)), tee_set)
                if card:
                    say(f"  scorecard: {os.path.relpath(p, ROOT)} ({tee_set}: {len(card)} holes)")
                    return card, os.path.relpath(p, ROOT)
                say(f"  ! {os.path.relpath(p, ROOT)} has no '{tee_set}' tee set")
            except Exception as e:                             # noqa: BLE001
                say(f"  ! bad scorecard {p}: {e}")
    return {}, None


def _norm_card(sc, tee_set):
    """Accepts scorecard/1 (ARCHITECTURE 3.3) or a plain {ref: yards|{yards, par}} mapping."""
    if "tee_sets" in sc:
        sets = {k.lower(): v for k, v in sc["tee_sets"].items()}
        key = tee_set.lower()
        key = {k.lower(): v.lower() for k, v in (sc.get("aliases") or {}).items()}.get(key, key)
        for name, v in sets.items():                          # per-set alias lists (tees/scorecard.json)
            if isinstance(v, dict) and key in [str(x).lower() for x in v.get("aliases", [])]:
                key = name
                break
        if key not in sets:
            hit = [k for k in sets if key in k]
            if not hit:
                return {}
            key = hit[0]
        s = sets[key]
        if isinstance(s.get("yards"), list):                  # {yards: [18], par: [18] at the top level}
            pars = s.get("par") or sc.get("par") or [None] * len(s["yards"])
            return {str(i + 1): dict(yards=y, par=p) for i, (y, p) in enumerate(zip(s["yards"], pars))}
        sc = s.get("holes", s)
    out = {}
    for ref, v in sc.items():
        if isinstance(v, dict):
            out[str(ref)] = dict(yards=v.get("yards") or v.get("length"), par=v.get("par"))
        elif isinstance(v, (int, float)):
            out[str(ref)] = dict(yards=v, par=None)
    return out


# ----------------------------------------------------------------------------- S4 gap-fill layers
def vision_layers(cdir, files=None):
    """Extra (lie, [shapely geoms]) layers from the imagery stage, WGS84 GeoJSON with a `lie` property
    (or one file per lie: naip_trees.geojson -> recovery). Returns (layers, sources).
    `files` overrides the search (acceptance passes one leave-one-hole-out file per hole)."""
    from shapely.geometry import shape
    if files is not None:
        files = list(files)
    else:
        files = _vision_files(cdir)
    return _read_layers(files, shape)


def _vision_files(cdir):
    files = sorted(set(glob.glob(os.path.join(cdir, "*vision*.geojson")) +
                       glob.glob(os.path.join(cdir, "naip_*.geojson")) +
                       glob.glob(os.path.join(cdir, "imagery", "*.geojson")) +
                       glob.glob(os.path.join(HERE, "imagery", os.path.basename(cdir), "*.geojson"))))
    if any(os.path.basename(f) == "gapfill.geojson" for f in files):    # it already holds the trees file's polygons
        files = [f for f in files if os.path.basename(f) != "naip_trees.geojson"]
    return files


def _read_layers(files, shape):
    by = {}
    for f in files:
        try:
            fc = json.load(open(f))
        except Exception:                                      # noqa: BLE001
            continue
        default = "recovery" if "tree" in f else ("native" if "native" in f or "grass" in f else
                                                  ("water" if "water" in f else None))
        for ft in fc.get("features", []):
            lie = ft.get("properties", {}).get("lie") or default
            if lie in ("recovery", "native", "water") and ft.get("geometry"):
                by.setdefault(lie, []).append(shape(ft["geometry"]))
    return [(k, v) for k, v in by.items()], [os.path.relpath(f, ROOT) for f in files]


# ----------------------------------------------------------------------------- S3 holes
def build_holes(fc, tee_set, lengths, extra, tees=None):
    """Hole dicts in a 920x2000 pixel frame (course.py format). Geometry stage, else the spike."""
    bh = load_module(os.path.join(HERE, "geometry", "build_holes.py"), "cd_geometry_build_holes")
    if bh is not None and hasattr(bh, "build"):
        try:
            holes, world = bh.build(fc, tee_set, lengths, extra, tees=tees)
        except TypeError:                                      # older geometry without the tees= argument
            holes, world = bh.build(fc, tee_set, lengths, extra)
        return {str(k): v for k, v in holes.items()}, "geometry/build_holes.py:build", (bh, world)
    om = load_module(os.path.join(HERE, "osm_to_model.py"), "cd_osm_to_model")
    if om is None:
        raise SystemExit("no hole builder: neither course_data/geometry/build_holes.py nor osm_to_model.py")
    say("  geometry stage missing -> spike osm_to_model.convert (yard frame, mapped to the virtual pixel frame)")
    raw = om.convert(fc, tee_set, lengths)
    ppy, tx, ty = 3.4, 460.0, 1900.0

    def px(p):
        return (round(tx + ppy * p[0], 1), round(ty + ppy * p[1], 1))
    out = {}
    for k, h in raw.items():
        out[str(k)] = dict(h, tee=(tx, ty), dot270=(tx, ty - 270 * ppy), green=px(h["green"]), px_per_yd=ppy,
                           hole_line=[px(p) for p in h["hole_line"]],
                           zones=[(n, [px(p) for p in poly]) for n, poly in h["zones"]])
    return out, "spike osm_to_model.convert", None


# ----------------------------------------------------------------------------- frames
def yard_frame(h):
    """(tee, fwd, right, ppy) of a course.py-style hole (tee_strategy.hole_frame)."""
    tee = np.array(h["tee"], float)
    v = np.array(h["dot270"], float) - tee
    ppy = np.linalg.norm(v) / 270.0
    fwd = v / np.linalg.norm(v)
    return tee, fwd, np.array([-fwd[1], fwd[0]]), ppy


def to_px(h, along, lat):
    tee, f, r, ppy = yard_frame(h)
    return tee + (np.asarray(along)[:, None] * f + np.asarray(lat)[:, None] * r) * ppy


def lie_with_index(h, pts):
    """lie_at, plus which zone index set it (-1 = default rough)."""
    from matplotlib.path import Path
    lie = np.array(["rough"] * len(pts), dtype=object)
    idx = np.full(len(pts), -1)
    for i, (name, poly) in enumerate(h["zones"]):
        m = Path(poly).contains_points(pts)
        lie[m], idx[m] = name, i
    return lie, idx


def landing_grid():
    a, l = np.meshgrid(np.arange(LANDING["a0"], LANDING["a1"] + 1, LANDING["step"]),
                       np.arange(-LANDING["lat"], LANDING["lat"] + 1, LANDING["step"]))
    return a.ravel().astype(float), l.ravel().astype(float)


# ----------------------------------------------------------------------------- S6 confidence
TEE_TRUST = [("tagged", 1.0), ("lidar", 0.6), ("closest to", 0.9), ("length", 0.9), ("centroid", 0.9), ("axis", 0.8),
             ("interpol", 0.6), ("walkback", 0.5), ("nearest the hole-line start", 0.4),
             ("hole-line start", 0.3), ("hole line start", 0.3)]


def confidence(h, h_osm, osm_hole_props, card, ref):
    """ARCHITECTURE section 6. h = final hole, h_osm = the same hole built without imagery layers."""
    flags = []
    how = str(h.get("tee_choice", ""))
    tee_c = next((v for k, v in TEE_TRUST if k in how), 0.4)
    if h.get("inferred"):
        tee_c = min(tee_c, 0.4)
        flags.append("hole line inferred (no golf=hole way)")
    if tee_c < 0.9:
        flags.append(f"tee: {how or 'unknown'}")
    green_c = 1.0
    hl = h.get("hole_line") or []
    if hl and np.allclose(hl[-1], h["green"], atol=0.5) and not h.get("green_osm", True):
        green_c = 0.6
    if h.get("green_from") == "hole_line_end":
        green_c = 0.6
        flags.append("green from the hole-line end (no golf=green polygon)")
    par_c = 1.0 if (card or {}).get("par") else (0.8 if str(osm_hole_props.get("par", "")).isdigit() else 0.5)
    len_c = 1.0 if (card or {}).get("yards") else 0.8
    if card and card.get("yards") and abs(h["length"] - float(card["yards"])) > 15:
        flags.append(f"measured {h['length']} vs card {card['yards']} yds: wrong box or re-routed hole")
        len_c = 0.6
    if card and card.get("par") and h.get("par") and int(card["par"]) != int(h["par"]):
        flags.append(f"par: OSM {h['par']} vs card {card['par']}")

    osm = img = inf = 0.0
    if h["par"] >= 4:
        a, l = landing_grid()
        pts = to_px(h, a, l)
        lie, idx = lie_with_index(h, pts)
        lie0, _ = lie_with_index(h_osm, to_px(h_osm, a, l)) if h_osm is not None else (lie, None)
        boundary_ob = np.zeros(len(lie), bool)
        if h["zones"] and h["zones"][0][0] == "ob":             # geometry puts the course-boundary OB first
            from matplotlib.path import Path
            boundary_ob = Path(h["zones"][0][1]).contains_points(pts) & (idx == 0)
        from_img = lie != lie0
        from_osm = (lie != "rough") & ~from_img & ~boundary_ob
        img = float(from_img.mean())
        osm = float(from_osm.mean())
        inf = 1.0 - osm - img
        pen = {k: float(np.mean(lie == k)) for k in PENAL}
        if pen["recovery"] + pen["native"] == 0:
            flags.append("no trees or long grass mapped in the landing zone (unmapped hazards play as rough)")
        if boundary_ob.any():
            flags.append(f"OB from the course boundary on {boundary_ob.mean():.0%} of the landing zone")
        if np.mean(lie == "fairway") == 0:
            flags.append("no fairway in the landing zone")
    else:
        osm, inf = (1.0, 0.0) if h.get("has_green_polygon", True) else (0.0, 1.0)
    cover = osm + 0.8 * img + 0.3 * inf
    score = 0.35 * tee_c + 0.15 * green_c + 0.10 * (par_c + len_c) / 2 + 0.40 * cover
    band = "auto" if score >= 0.8 else ("check the flags" if score >= 0.6 else "needs review")
    return dict(score=round(score, 3), band=band, tee=tee_c, green=green_c, par=par_c, length=len_c,
                osm=round(osm, 3), imagery=round(img, 3), inferred=round(inf, 3), flags=flags)


# ----------------------------------------------------------------------------- S5 images
def render_images(cdir, holes, ctx, fc, out_dir):
    """Imagery stage renderer if present, else a fallback from naip_preview.png (+.pgw world file)."""
    fn, where = find_fn("imagery", ["render_hole", "render_holes"])
    os.makedirs(out_dir, exist_ok=True)
    done = {}
    if fn:
        say(f"  images: {where}")
        for k, h in holes.items():
            name = f"hole{int(k):02d}.png" if str(k).isdigit() else f"hole{k}.png"
            try:
                fn(cdir, h, os.path.join(out_dir, name))
                done[k] = name
            except Exception as e:                             # noqa: BLE001
                say(f"  ! {where} failed on {k}: {type(e).__name__}: {e}")
                break
        if len(done) == len(holes):
            return done, where
    pre = os.path.join(cdir, "naip_preview.png")
    if ctx is None or not os.path.exists(pre):
        say("  images: none (no imagery renderer, no naip_preview.png or no geometry world)")
        return done, None
    try:
        return _fallback_render(cdir, holes, ctx, out_dir, done), "fallback: naip_preview.png (0.9 m)"
    except Exception as e:                                     # noqa: BLE001
        say(f"  ! fallback render failed: {type(e).__name__}: {e}")
        traceback.print_exc()
        return done, None


def _px_to_world(h, bh, world):
    """Complex similarity (with the y flip) from the hole's px frame to the geometry world (UTM yds),
    from two correspondences: tee (lonlat_tee) and the green (find_green on the OSM hole line)."""
    from shapely.geometry import Point
    tw = np.array(world.proj(Point(h["lonlat_tee"])).coords[0])
    ref = None
    for hole in world.holes:
        if str(hole["props"].get("ref")) == str(h.get("_ref")):
            ref = hole
    if ref is None:
        return None
    g = bh.find_green(world, ref["line"][-1])
    gw = np.array(g["pt"].coords[0]) if g else ref["line"][-1]
    P1, P2 = complex(h["tee"][0], -h["tee"][1]), complex(h["green"][0], -h["green"][1])
    W1, W2 = complex(*tw), complex(*gw)
    a = (P2 - P1) / (W2 - W1)
    b = P1 - a * W1
    return a, b


def _fallback_render(cdir, holes, ctx, out_dir, done):
    from PIL import Image
    from pyproj import Transformer
    Image.MAX_IMAGE_PIXELS = None
    bh, world = ctx
    summ = json.load(open(os.path.join(cdir, "summary.json")))
    crs = (summ.get("naip") or {}).get("crs")
    pgw = [float(x) for x in open(os.path.join(cdir, "naip_preview.pgw")).read().split()]
    img = np.asarray(Image.open(os.path.join(cdir, "naip_preview.png")).convert("RGB"))
    to_img = Transformer.from_crs(world.crs, crs, always_xy=True)
    YD = 0.9144
    ys, xs = np.mgrid[0:H:2, 0:W:2]                            # half-res grid, upsampled below
    for k, h in holes.items():
        if k in done:
            continue
        ab = _px_to_world(h, bh, world)
        if ab is None:
            continue
        a, b = ab
        Wc = ((xs - 1j * ys).ravel() - b) / a                 # px -> world yds (complex)
        E, N = to_img.transform(Wc.real * YD, Wc.imag * YD)
        col = ((np.asarray(E) - pgw[4]) / pgw[0]).round().astype(int)
        row = ((np.asarray(N) - pgw[5]) / pgw[3]).round().astype(int)
        ok = (col >= 0) & (col < img.shape[1]) & (row >= 0) & (row < img.shape[0])
        out = np.full((xs.size, 3), 40, np.uint8)
        out[ok] = img[row[ok], col[ok]]
        im = Image.fromarray(out.reshape(xs.shape + (3,))).resize((W, H), Image.BILINEAR)
        name = f"hole{int(k):02d}.png" if str(k).isdigit() else f"hole{k}.png"
        im.save(os.path.join(out_dir, name), optimize=True)
        done[k] = name
    return done


# ----------------------------------------------------------------------------- S6 outputs
COURSE_MODULE = '''"""Auto-built course module for {name} ({tee_set} tees). Generated by course_data/pipeline.py
on {built}; do not edit by hand, re-run:

  python3 course_data/pipeline.py --course "{course_arg}" --tees {tee_set}

Same API as spirit_hollow/course.py (HOLES, PAR3, NOTES, AIM_AT, ORDER, LABELS), in the 920 x 2000
pixel frame of each hole's image, so mozingo/yardage_book.use_course() takes it unchanged:

  import course_auto as course
  yb.use_course("{name}", "<this dir>", "{prefix}", course.HOLES, course.PAR3, course.NOTES,
                course.AIM_AT, course.ORDER, course.LABELS)

Per-hole provenance and confidence: HOLES[k]["auto"] / holes.json.
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "holes.json")) as _fh:
    MODEL = json.load(_fh)


def _key(k):
    return int(k) if str(k).isdigit() else k


HOLES, PAR3, NOTES, AIM_AT = {{}}, {{}}, {{}}, {{}}
for _k, _h in MODEL["holes"].items():
    _h = dict(_h)
    _h["tee"], _h["dot270"], _h["green"] = tuple(_h["tee"]), tuple(_h["dot270"]), tuple(_h["green"])
    _h["zones"] = [(n, [tuple(p) for p in poly]) for n, poly in _h["zones"]]
    _h.setdefault("aim_min", -60)          # wider than course.py's +/-40: the auto tee line points at the
    _h.setdefault("aim_max", 60)           # first hole-line node, which on dog-legs is off the landing area
    _p3 = _h.pop("par3", None)
    _c = _h.get("auto", {{}})
    NOTES[_key(_k)] = _h.pop("note", "Auto-built.")
    if _p3:
        _p3 = dict(_p3, image=_h.get("image"), tee=tuple(_p3["tee"]), flag=tuple(_p3["flag"]),
                   green=[tuple(p) for p in _p3["green"]])
        PAR3[_key(_k)] = _p3
    else:
        HOLES[_key(_k)] = _h
        AIM_AT[_key(_k)] = "Centre of the fairway"

ORDER = sorted(set(HOLES) | set(PAR3), key=lambda k: (str(k).rstrip("BF").zfill(3), str(k)))
LABELS = {{}}
APP, GREEN_SIDE = {{}}, {{}}
'''


def note_for(h, conf, card):
    src = ["OSM"]
    if conf["imagery"] > 0:
        src.append(f"imagery {conf['imagery']:.0%} of the landing zone")
    s = f"Auto-built ({', '.join(src)}; confidence {conf['score']:.2f}, {conf['band']}). Tee: {h.get('tee_choice', '?')}."
    if conf["flags"]:
        s += " Check: " + "; ".join(conf["flags"][:3]) + "."
    return s


def load_tee_positions(slug, cdir):
    """S2 output: tees.json (ARCHITECTURE 3.4) or the tee scientist's tee_positions.json; None if absent."""
    for p in (os.path.join(cdir, "tees.json"), os.path.join(HERE, "tees", slug, "tee_positions.json"),
              os.path.join(HERE, "tees", "tee_positions.json")):
        if os.path.exists(p):
            try:
                return json.load(open(p)), os.path.relpath(p, ROOT)
            except Exception as e:                             # noqa: BLE001
                say(f"  ! bad tee file {p}: {e}")
    return None, None


def build_course(course, tee_set="white", lengths=None, cdir=None, render=True, quiet=False, tee_stage=True,
                 vision=True, layers=True):
    """Run S1-S6 offline. Returns the course model dict (holes.json) without writing it."""
    del LOG[:]
    slug, d, meta = resolve(course)
    cdir = cdir or d
    say(f"[S0] course '{course}' -> {slug} ({os.path.relpath(cdir, ROOT)})"
        + ("" if meta else "  (not fetched yet)"))
    stages = {}
    geo = os.path.join(cdir, "osm.geojson")
    if not os.path.exists(geo):
        say("[S1] MISSING osm.geojson. Run on GitHub Actions:\n  " + fetch_hint(course, slug))
        raise SystemExit(2)
    fc = json.load(open(geo))
    stages["osm"] = "ok: " + os.path.relpath(geo, ROOT)
    say(f"[S1] OSM: {len(fc['features'])} features")

    card, where = load_scorecard(slug, cdir, tee_set)
    stages["scorecard"] = f"ok: {where}" if card else "missing"
    if not card:
        say(f"[S1] scorecard: none for '{tee_set}' -> tee boxes can't be matched to the set "
            "(pass --lengths, or run the tees fetch workflow)")
    lens = {r: float(c["yards"]) for r, c in card.items() if c.get("yards")}
    lens.update({str(k): float(v) for k, v in (lengths or {}).items()})
    tees, tsrc = load_tee_positions(slug, cdir) if tee_stage else (None, None)
    if tees is not None:
        stages["tees"] = f"ok: {tsrc} (set '{tee_set}'; card yardage -> box where the file has no point)"
    else:
        stages["tees"] = ("card yardage -> tee box (geometry.choose_tee)" if lens else
                          "no yardages: OSM tee nearest the hole-line start")
    say(f"[S2] tees: {stages['tees']}")

    extra, vsrc = vision_layers(cdir) if layers else ([], [])
    stages["vision"] = ("ok: " + ", ".join(vsrc)) if extra else "missing (no gap-fill layers)"
    say(f"[S4] vision layers: {[(k, len(v)) for k, v in extra] or 'none'}")

    holes, how, ctx = build_holes(fc, tee_set, lens or None, extra, tees)
    stages["geometry"] = how
    holes_osm = build_holes(fc, tee_set, lens or None, [], tees)[0] if extra else None
    say(f"[S3] holes: {len(holes)} via {how}")

    # S4 any-course gap-fill (vision_any: lidar trees, NAIP long grass, creek corridors), when present
    layers = os.path.join(HERE, "vision_any", slug, "vision_any.geojson")
    ga = None
    if vision and not os.path.exists(layers):
        # gapfill() would build the layers on the fly from the raw rasters: >13 min and >3.4 GB here (killed)
        say(f"[S4] vision_any: no precomputed {os.path.relpath(layers, ROOT)} (built by vision_any.yml); skipped")
    elif vision:
        ga = load_module(os.path.join(HERE, "vision_any", "gapfill.py"), "cd_vision_any_gapfill")
    if ga is not None and hasattr(ga, "gapfill_holes"):
        try:
            import copy
            before = copy.deepcopy(holes)
            g = ga.gapfill_holes(dict(holes=holes, slug=slug, course=meta or {}), slug=slug)
            holes = {str(k): v for k, v in g["holes"].items()}
            holes_osm = holes_osm or before
            stages["vision"] = "ok: vision_any/gapfill.py:gapfill_holes" + (
                "; " + stages["vision"] if extra else "")
            say(f"[S4] vision_any gap-fill: {stages['vision']}")
        except Exception as e:                                 # noqa: BLE001
            say(f"  ! vision_any gapfill failed: {type(e).__name__}: {str(e)[:200]}")

    props = {}
    for f in fc["features"]:
        p = f["properties"]
        if p.get("golf") == "hole":
            props[str(p.get("ref"))] = p
    for k, h in holes.items():
        h["zones"] = model_zones(h["zones"])
        h["_ref"] = k
        h["has_green_polygon"] = True
        if ctx is not None:
            bh, world = ctx
            line = next((x["line"] for x in world.holes if str(x["props"].get("ref")) == k), None)
            if line is not None and bh.find_green(world, line[-1]) is None:
                h["green_from"] = "hole_line_end"
                h["has_green_polygon"] = False
        if card.get(k, {}).get("par"):
            h["par"] = int(card[k]["par"])
        h["par"] = int(h["par"])

    if render:
        images, isrc = render_images(cdir, holes, ctx, fc, os.path.join(cdir, "screenshots"))
    else:                                                      # keep earlier renders (frames are deterministic)
        images = {k: n for k in holes for n in [f"hole{int(k):02d}.png" if k.isdigit() else f"hole{k}.png"]
                  if os.path.exists(os.path.join(cdir, "screenshots", n))}
        isrc = "previous render (--no-images)" if images else None
    stages["images"] = f"ok: {isrc} ({len(images)}/{len(holes)})" if images else "missing"

    out = {}
    for k, h in holes.items():
        c = confidence(h, (holes_osm or {}).get(k), props.get(k, {}), card.get(k), k)
        h["auto"] = c
        h["image"] = images.get(k)
        h["note"] = note_for(h, c, card.get(k))
        if h.get("par3"):
            h["par3"]["note"] = h["par3"].get("note", "") + f" (confidence {c['score']:.2f})"
        h.pop("_ref", None)
        out[k] = h
    model = dict(schema="course_model/1", course=meta or dict(name=course, slug=slug), slug=slug,
                 tee_set=tee_set, built=dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ"), frame="pixel",
                 pixel_frame=dict(size=[W, H], note="per-hole: tee, dot270 (270 yds up the tee line), px_per_yd"),
                 lengths=lens, stages=stages,
                 holes=dict(sorted(out.items(), key=lambda kv: (len(kv[0]), kv[0]))))
    say("[S6] stages: " + json.dumps(stages, indent=1))
    return model


def write_outputs(model, cdir, course_arg):
    os.makedirs(cdir, exist_ok=True)
    with open(os.path.join(cdir, "holes.json"), "w") as fh:
        json.dump(model, fh, separators=(",", ":"), default=float)
    name = model["course"].get("name", course_arg)
    with open(os.path.join(cdir, "course_auto.py"), "w") as fh:
        fh.write(COURSE_MODULE.format(name=name, tee_set=model["tee_set"], built=model["built"],
                                      course_arg=course_arg, prefix=model["slug"].title().replace("_", "_")))
    lines = [f"# QA: {name}, {model['tee_set']} tees ({model['built']})", "",
             "| hole | par | yds | score | band | OSM | imagery | inferred | flags |",
             "|---|---|---|---|---|---|---|---|---|"]
    for k, h in model["holes"].items():
        c = h["auto"]
        lines.append(f"| {k} | {h['par']} | {h['length']} | {c['score']:.2f} | {c['band']} | {c['osm']:.0%} | "
                     f"{c['imagery']:.0%} | {c['inferred']:.0%} | {'; '.join(c['flags'])} |")
    lines += ["", "Stages:", ""] + [f"- **{k}**: {v}" for k, v in model["stages"].items()]
    with open(os.path.join(cdir, "qa.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"wrote {os.path.relpath(cdir, ROOT)}/holes.json, course_auto.py, qa.md")


def build_book(model, cdir):
    import yardage_book as yb
    mod = load_module(os.path.join(cdir, "course_auto.py"), "course_auto_" + model["slug"])
    missing = [k for k, h in mod.HOLES.items() if not h.get("image")]
    if missing:
        print("book: holes without images", missing, "- the book needs the imagery stage")
        return
    yb.use_course(model["course"].get("name", model["slug"]), cdir, model["slug"].title() + "_Auto",
                  mod.HOLES, mod.PAR3, mod.NOTES, mod.AIM_AT, mod.ORDER, mod.LABELS)
    yb.build()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--course", required=True, help='course name, e.g. "Spirit Hollow"')
    ap.add_argument("--tees", default="white", help="tee set name on the scorecard (white, blue, ...)")
    ap.add_argument("--lengths", help="override yardages, e.g. 1=413,2=609 (picks the tee boxes)")
    ap.add_argument("--no-images", action="store_true")
    ap.add_argument("--no-vision", action="store_true", help="skip the vision_any gap-fill (OSM zones only)")
    ap.add_argument("--book", action="store_true", help="also build the strategy PDF (needs images)")
    a = ap.parse_args()
    lengths = {k: float(v) for k, v in (kv.split("=") for kv in a.lengths.split(","))} if a.lengths else None
    model = build_course(a.course, a.tees, lengths, render=not a.no_images, vision=not a.no_vision)
    slug, cdir, _ = resolve(a.course)
    write_outputs(model, cdir, a.course)
    if a.book:
        build_book(model, cdir)


if __name__ == "__main__":
    main()
