"""Precompute what the app's in-browser golfer confirm (golf_confirm/1 ported to JS) needs: a pool of candidate
whole-round routings with their routing-v2 costs, so the page can re-solve after every answer without Python.

  python3 course_data/app/confirm_pool.py --package mozingo_lake [--no-card]     # course_data/packages/<slug>
  python3 course_data/app/confirm_pool.py --generalize falmouth_me               # course_data/generalize/courses/<slug>
  -> course_data/app/pools/<slug>.json            (golf_confirm_pool/1: embedded in the page)
     course_data/app/fixtures/confirm_truth/<slug>.json   (hidden truth: the OSM golf=hole ways, tests only)

Why a pool (and not routing_v2 in JS): routing_v2.solve is a 6000-state beam over per-course feature matrices
(walk, cart paths, facility points, coverage, line crossings) plus 18 leave-one-out re-solves; porting it would
put ~1-3 MB of matrices and seconds of CPU per answer on the phone. Instead the routing is solved here, many
times, and the page keeps the posterior exact over that pool:

  base      solve(keep_top=300, margins=True) - exactly what confirm.Session starts from (its posterior)
  pins      for every hole, its K_GREENS most likely greens (best hypothesis row per green, by hole cost, plus every
            green the base posterior gives it) are pinned one at a time: solve(fixed={hole: (tee, green)},
            beam PIN_BEAM, keep_top PIN_TOP). These are the routings a "yes" or a located hole leads to.
  costs     every routing keeps its exact routing_v2 cost (the beam's path cost, or local_search's exact cost):
            costs from different solves are comparable, so one Boltzmann posterior at tau covers the union.

In the page (confirm_engine.js), an answer is a constraint on the pool: "yes" / a locate pins hole n's key
(green + tee complex, routing_v2._hole_key), "no" removes routings with that green and a box within 45 yds of the
shown tee (routing_v2.reject). The re-solved routing is the cheapest routing that meets every constraint, and
p_hole is its key's Boltzmann share over the routings that meet them (as confirm.Session.marginals). When no pooled
routing meets them all, the routings with the fewest broken constraints are used (a pin on a green the pool has
under another tee complex counts half) and pinned holes are drawn where the golfer put them.

Typed cards (no card online): the pool is built without a card (`--no-card`); each pair keeps its straight
length and the lengths of the tee boxes on its line, so the page re-scores the routing_v2 length and fingerprint
terms with the typed yardages / pars (routing.length_cost / fingerprint), drops pairs outside the yardage window
(length cost >= 9.5) and re-ranks the pool.
"""
import argparse
import base64
import io
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
for p in (os.path.join(CD, "platform"), os.path.join(CD, "generalize")):
    if p not in sys.path:
        sys.path.insert(0, p)
import routing as R  # noqa: E402
import routing_v2 as R2  # noqa: E402
import confirm as CF  # noqa: E402

POOLS = os.path.join(HERE, "pools")
TRUTH = os.path.join(HERE, "fixtures", "confirm_truth")
K_GREENS = 10
PIN_BEAM = 500
PIN_TOP = 40
MAX_ROUTINGS = 6000


def log(*a):
    print(*a, flush=True)


def rd(p):
    try:
        return json.load(open(p))
    except (OSError, ValueError):
        return None


# ----------------------------------------------------------------------------- inputs
def hide(fc):
    return dict(fc, features=[dict(f, properties={k: v for k, v in f["properties"].items() if k != "ref"})
                              for f in fc["features"] if f["properties"].get("golf") != "hole"])


def package_inputs(slug, no_card=False):
    """A course package (course_data/packages/<slug>) as an unmapped course: its OSM golf=hole ways and refs are
    hidden (they become the truth), greens / tees from OSM + the segment model + lidar pads, the package card."""
    d = os.path.join(CD, "packages", slug)
    pkg = rd(os.path.join(d, "package.json"))
    fc = rd(os.path.join(d, "raw", "osm.geojson"))
    course = rd(os.path.join(d, "raw", "course.json")) or {}
    seg = rd(os.path.join(CD, "segment", slug, "segment.geojson"))
    dem = os.path.join(d, "imagery", "dem.tif")
    pads = []
    if os.path.exists(dem):
        sys.path.insert(0, os.path.join(CD, "tees"))
        import lidar_pads
        greens = [dict(id=f["properties"].get("osm_id"), coords=[(c[1], c[0]) for c in f["geometry"]["coordinates"][0]])
                  for f in fc["features"] if f["properties"].get("golf") == "green" and f["geometry"]["type"] == "Polygon"]
        try:
            pads = lidar_pads.detect_pads(dem, greens=greens, lines=None)
        except Exception as e:                                   # noqa: BLE001
            log(f"  lidar pads failed: {e}")
        pads = [dict(id=p["id"], centroid=p["centroid"], coords=[tuple(c) for c in p["coords"]]) for p in pads]
    truth = {k: v for k, v in R.truth_from_fc(fc).items() if int(k) <= 18}
    card = None
    if not no_card:
        par = None
        sets = {}
        for name, ts in pkg["tee_sets"].items():
            if ts.get("yards"):
                sets[name] = dict(yards=ts["yards"])
            par = par or ts.get("par")
        if not par:
            par = [pkg["holes"][str(i)].get("par") for i in range(1, len(pkg["holes"]) + 1)]
        card = dict(par=par, tee_sets=sets)
    inp = R.inputs_from_fc(fc, segment=seg, pads=pads, boundary=course.get("boundary"), hide_holes=True)
    return dict(slug=slug, name=pkg["course"]["name"], fc=hide(fc), inp=inp, card=card, truth=truth,
                boundary=course.get("boundary"), pkg=pkg, card_kind=("none" if no_card else pkg["scorecard"].get("kind")))


def generalize_inputs(slug):
    import route_eval as RE
    c = RE.load(slug)
    meta = rd(os.path.join(CD, "generalize", "courses", slug, "course.json")) or {}
    c["name"] = meta.get("name") or slug
    return c


# ----------------------------------------------------------------------------- pool
def pin_candidates(ctx, w, base_keys, h):
    """(t, g) pins worth precomputing for hole h: the best hypothesis row of each of its K_GREENS cheapest greens
    plus every (t, g) the base posterior gives it."""
    ht, hg, F = R2.hole_rows(ctx, h, w)
    c = F @ w
    best = {}
    for t, g, cc in zip(ht, hg, c):
        t, g = int(t), int(g)
        if g < 0 or t < 0:
            continue
        if g not in best or cc < best[g][0]:
            best[g] = (cc, t)
    order = sorted(best, key=lambda g: best[g][0])[:K_GREENS]
    out = {(best[g][1], g) for g in order}
    for a in base_keys:
        if a[h][0] >= 0 and a[h][1] >= 0:
            out.add(tuple(a[h]))
    return sorted(out)


def build_pool(c, name=None):
    t0 = time.time()
    w, tau, p_check = R2.load_weights()
    ctx = R2.context(c["inp"], c["card"], fc=c["fc"], boundary=c["boundary"])
    n = ctx["n"]
    base = R2.solve(ctx, w=w, tau=tau, p_check=p_check, keep_top=300, margins=True)
    if base.get("cost") is None:
        raise SystemExit(f"{c['slug']}: routing failed ({base.get('status')})")
    routs = {}

    def add(cost, a):
        a = tuple((int(t), int(g)) for t, g in a)
        k = tuple(R2._hole_key(ctx, t, g) for t, g in a)
        if k not in routs or cost < routs[k][0]:
            routs[k] = (float(cost), a)
    for cost, a in base["top"]:
        add(cost, a)
    base_assigns = [a for _, a in base["top"][:60]]
    log(f"  base solve: {len(routs)} routings, {time.time() - t0:.0f}s")
    n_pins = 0
    for h in range(n):
        for t, g in pin_candidates(ctx, w, base_assigns, h):
            r = R2.solve(ctx, w=w, tau=tau, p_check=p_check, fixed={str(h + 1): (t, g)}, beam=PIN_BEAM,
                         keep_top=PIN_TOP, polish=1, margins=False)
            for cost, a in r.get("top", []):
                add(cost, a)
            n_pins += 1
        log(f"  hole {h + 1}: {n_pins} pins, {len(routs)} routings, {time.time() - t0:.0f}s")
    items = sorted(routs.values(), key=lambda x: x[0])[:MAX_ROUTINGS]
    # per-hole pair tables
    pairs = [dict() for _ in range(n)]
    for _, a in items:
        for h, tg in enumerate(a):
            pairs[h].setdefault(tg, len(pairs[h]))
    G, T, D = ctx["G"], ctx["T"], ctx["D"]
    txy, gxy = ctx["txy"], ctx["gxy"]
    tee_axes = ctx["tee_axes"]

    def pair_info(t, g):
        """[t, g, back tee, straight yds, on-hole box lengths] (back tee: the farthest box on the line, as
        routing_v2._result's back_tee_ll; box lengths feed the typed-card fingerprint)."""
        if t < 0 or g < 0:
            return [t, g, t, None, []]
        onh = np.nonzero(R._on_hole(txy, txy[t], gxy[g], tee_axes))[0]
        bk = int(onh[np.argmax(D[onh, g])]) if len(onh) else t
        d = gxy[g] - txy[t]
        L = max(float(np.hypot(*d)), 1e-6)
        rel = txy - txy[t]
        u = (rel @ d) / L
        v = np.abs(rel[:, 0] * d[1] - rel[:, 1] * d[0]) / L
        on = np.nonzero((u >= -R.COV_BACK) & (u <= R.COV_FWD * L) & (v <= R.COV_PERP))[0]
        return [t, g, bk, round(float(D[t, g]), 1), sorted(round(float(D[b, g]), 1) for b in on)]
    pair_tab = [[pair_info(t, g) for (t, g), _ in sorted(p.items(), key=lambda kv: kv[1])] for p in pairs]
    rows = [[pairs[h][tg] for h, tg in enumerate(a)] for _, a in items]
    costs = [round(cst, 4) for cst, _ in items]
    cx = [f"{int(round(x / 40.0))},{int(round(y / 40.0))}" for x, y in txy]
    holes_card = [dict(par=ctx["pars"][h] if ctx["pars"] else None, yards=list(ctx["yards"][h]) if ctx["yards"] else [])
                  for h in range(n)]
    pool = dict(
        schema="golf_confirm_pool/1", slug=c["slug"], name=name or c.get("name"), n=n, card=bool(c["card"]),
        card_kind=c.get("card_kind"),
        built=time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()),
        params=dict(tau=tau, p_check=p_check, p_stop=p_check, doubt=CF.DOUBT, snap_green=CF.SNAP_GREEN,
                    snap_tee=CF.SNAP_TEE, reject_r=45.0, w_length=float(w[R2.FI["length"]]),
                    w_fingerprint=float(w[R2.FI["fingerprint"]]), fp_cap=R.FP_CAP, lc_max=9.5,
                    par_ranges={str(k): v for k, v in R.PAR_RANGES.items()}),
        holes=holes_card,
        greens=[dict(ll=[round(g["ll"][0], 7), round(g["ll"][1], 7)], src=g["src"]) for g in G],
        tees=[dict(ll=[round(t["ll"][0], 7), round(t["ll"][1], 7)], src=t["src"], cx=cx[i]) for i, t in enumerate(T)],
        pairs=pair_tab, routings=rows, costs=costs,
        stats=dict(base_routings=len(base["top"]), pins=n_pins, routings=len(rows), seconds=round(time.time() - t0, 1),
                   pin_beam=PIN_BEAM, pin_top=PIN_TOP, k_greens=K_GREENS))
    return pool, base, ctx


def reference_sim(c, max_taps=30):
    """The same oracle golfer against the real thing (confirm.Session: a full routing_v2 re-solve per answer,
    route_eval.simulate_confirm) -> {taps, questions, stop_rule_taps, stop_rule_wrong, seconds}: the yardstick the
    page's pool re-solve is compared with (test_confirm.js)."""
    import route_eval as RE
    t0 = time.time()
    r = RE.simulate_confirm(dict(c, truth=c["truth"]), policy="eig", max_taps=max_taps)
    return dict(taps=r["taps"], questions=r["questions"], stop_rule_taps=r["stop_rule_taps"],
                stop_rule_wrong=r["stop_rule_wrong"], wrong_left=r["wrong_left"], seconds=round(time.time() - t0, 1),
                log=r["log"])


def truth_doc(c):
    """Hidden truth for the simulated golfer: per hole the OSM way (tee_ll, green_ll, the line)."""
    return dict(schema="golf_confirm_truth/1", slug=c["slug"],
                note="OSM golf=hole ways hidden from routing; the simulated golfer answers from these (tests only, "
                     "never embedded in the page). Scored as routing.score: green within 20 yds, tee within 40 yds "
                     "of the first 60 % of the line.",
                holes={r: dict(tee_ll=list(t["tee_ll"]), green_ll=list(t["green_ll"]), line=t["line"], par=t.get("par"))
                       for r, t in sorted(c["truth"].items(), key=lambda kv: int(kv[0]))},
                card=c["card"])


# ----------------------------------------------------------------------------- overview image
def overview_image(slug, pool, max_px=900, quality=68):
    """The package's NAIP mosaic cropped to every candidate (+60 m), as a JPEG data URI, with the affine
    lon/lat -> px fit (UTM is affine to lon/lat within ~0.2 m over a course)."""
    from PIL import Image
    from pyproj import Transformer
    d = os.path.join(CD, "packages", slug, "imagery")
    geo = rd(os.path.join(d, "georef.json"))
    if not geo:
        return None
    lo = geo["imagery"]["lo"]
    a, _, c0, _, e, f0 = lo["transform"]
    tr = Transformer.from_crs("EPSG:4326", f"EPSG:{geo['imagery']['epsg']}", always_xy=True)
    pts = [g["ll"] for g in pool["greens"]] + [t["ll"] for t in pool["tees"]]
    pkg = rd(os.path.join(CD, "packages", slug, "package.json")) or {}
    bb = (pkg.get("course") or {}).get("bbox")         # the whole course: a hole whose tee nobody detected is on it too
    if bb:
        pts += [[bb[0], bb[1]], [bb[2], bb[3]]]
    X, Y = tr.transform([p[0] for p in pts], [p[1] for p in pts])
    col = (np.asarray(X) - c0) / a
    row = (np.asarray(Y) - f0) / e
    pad = 60 / abs(a)
    im = Image.open(os.path.join(d, lo["files"]["rgb"])).convert("RGB")
    x0, y0 = max(0, int(col.min() - pad)), max(0, int(row.min() - pad))
    x1, y1 = min(im.width, int(col.max() + pad)), min(im.height, int(row.max() + pad))
    crop = im.crop((x0, y0, x1, y1))
    s = min(1.0, max_px / max(crop.size))
    crop = crop.resize((round(crop.width * s), round(crop.height * s)), Image.LANCZOS)
    buf = io.BytesIO()
    crop.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    # affine fit lon/lat -> px on a grid over the crop
    lon0, lat0 = np.mean([p[0] for p in pts]), np.mean([p[1] for p in pts])
    inv = Transformer.from_crs(f"EPSG:{geo['imagery']['epsg']}", "EPSG:4326", always_xy=True)
    gx, gy = np.meshgrid(np.linspace(x0, x1, 6), np.linspace(y0, y1, 6))
    E, N = c0 + gx.ravel() * a, f0 + gy.ravel() * e
    lon, lat = inv.transform(E, N)
    A = np.c_[np.asarray(lon) - lon0, np.asarray(lat) - lat0, np.ones(len(E))]
    px = (gx.ravel() - x0) * s
    py = (gy.ravel() - y0) * s
    cx, *_ = np.linalg.lstsq(A, px, rcond=None)
    cy, *_ = np.linalg.lstsq(A, py, rcond=None)
    err = float(np.max(np.hypot(A @ cx - px, A @ cy - py)))
    return dict(img="data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), w=crop.width, h=crop.height,
                ll0=[round(lon0, 7), round(lat0, 7)], ax=[float(x) for x in cx], ay=[float(y) for y in cy],
                m_per_px=round(abs(a) / s, 2), fit_err_px=round(err, 3), source=geo["imagery"].get("source"),
                year=geo["imagery"].get("year"))


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--package")
    src.add_argument("--generalize")
    ap.add_argument("--no-card", action="store_true", help="build without the card (the page asks for a typed one)")
    ap.add_argument("--out", default=POOLS)
    ap.add_argument("--reference", action="store_true", help="also run confirm.Session's oracle simulation (minutes)")
    ap.add_argument("--reference-only", action="store_true", help="only add the reference run to the truth fixture")
    ap.add_argument("--overview-only", action="store_true", help="only redo the overview image of an existing pool")
    a = ap.parse_args()
    if a.overview_only:
        path = os.path.join(a.out, f"{a.package}.json")
        pool = rd(path)
        pool["overview"] = overview_image(a.package, pool)
        with open(path, "w") as fh:
            json.dump(pool, fh, separators=(",", ":"))
        log(f"{path}: overview {pool['overview']['w']} x {pool['overview']['h']}")
        return
    if a.package:
        c = package_inputs(a.package, no_card=a.no_card)
    else:
        c = generalize_inputs(a.generalize)
    log(f"{c['slug']}: {len(c['inp']['greens'])} greens, {len(c['inp']['tees'])} tees, card {bool(c['card'])}")
    tpath = os.path.join(TRUTH, f"{c['slug']}.json")
    if a.reference_only:
        doc = rd(tpath) or truth_doc(c)
        doc.setdefault("reference", {})["card" if c["card"] else "nocard"] = reference_sim(c)
        with open(tpath, "w") as fh:
            json.dump(doc, fh, separators=(",", ":"))
        log(f"reference: {doc['reference']}")
        return
    pool, base, ctx = build_pool(c, name=c.get("name"))
    # how right is the routing before any answer (routing.score vs the hidden ways)
    sc = R.score(base, c["truth"])
    pool["stats"]["base_correct_holes"] = int(sum(e["hole_ok"] for e in sc["per_hole"].values()))
    if a.package:
        ov = overview_image(a.package, pool)
        if ov:
            pool["overview"] = ov
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(TRUTH, exist_ok=True)
    path = os.path.join(a.out, f"{c['slug']}.json")
    with open(path, "w") as fh:
        json.dump(pool, fh, separators=(",", ":"))
    doc = truth_doc(c)
    old = rd(tpath) or {}
    if old.get("reference"):
        doc["reference"] = old["reference"]
    if a.reference:
        doc.setdefault("reference", {})["card" if c["card"] else "nocard"] = reference_sim(c)
    with open(tpath, "w") as fh:
        json.dump(doc, fh, separators=(",", ":"))
    log(f"wrote {path} {os.path.getsize(path) / 1e6:.2f} MB: {pool['stats']}")


if __name__ == "__main__":
    main()
