"""detector_pair.py OUT_DIR SLUG[,SLUG...]: paired detector comparison on TRAIN-BIG courses (.github/workflows/
routing_bench.yml stage detector_pair). Per course the inputs are rebuilt twice on the same machine with the same code
and the same NAIP years (benchdata/big/pinned_years.json: the package year + the 2 extra years the v2 bench's scenes
used), only the U-Net weights (+ their second-stage object models) differing:
    A: PAIR_UNET_A / PAIR_OBJ_A      B: PAIR_UNET_B / PAIR_OBJ_B      (paths relative to the repo root)
PAIR_REFETCH_B=1 fetches B's imagery again instead of sharing A's (the noise-floor run, A against A).
Both are routed with the same learned-score setup: route_learn state-fold models (ROUTE_BENCH_FOLD_RESCORE,
benchdata/folds: out-of-fold scores), the shipped re-ranker and tee step live (route_models/v2), production card pick.
FASTSCENE_VINTAGE=0 and FASTSCENE_UNET_MODEL=v2 for both (routing fits / thresholds of the v2 detector).
-> OUT_DIR/pair.jsonl: per course and variant holes right, hole_ok_fwd, card error (median |routed - card| yd), green /
tee recall of the scene against the truth, scene counts, timings."""
import gzip, json, math, os, shutil, subprocess, sys, tempfile, time, traceback
import numpy as np
FP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(FP)))
sys.path[:0] = [FP, os.path.dirname(FP)]
os.environ.setdefault("FASTPATH_TILE_CACHE", "off")
os.environ["FASTSCENE_UNET_MODEL"] = "v2"
os.environ["FASTSCENE_VINTAGE"] = "0"
BD = os.path.join(FP, "benchdata", "big")
PIN = json.load(open(os.path.join(BD, "pinned_years.json")))


def fetch(slug, pkg):
    """package with the pinned NAIP years (segv2/rebuild_big.py's pinning, years read from the v2 bench's status)"""
    import fast_imagery as fim
    import canopy
    raw = os.path.join(pkg, "raw")
    os.makedirs(raw, exist_ok=True)
    d = os.path.join(BD, "courses", slug)
    course = json.load(open(os.path.join(d, "course.json")))
    json.dump(course, open(os.path.join(raw, "course.json"), "w"))
    with gzip.open(os.path.join(d, "osm_golf.geojson.gz"), "rb") as fi, open(os.path.join(raw, "osm.geojson"), "wb") as fo:
        shutil.copyfileobj(fi, fo)
    shutil.copy(os.path.join(d, "scorecard.json"), os.path.join(raw, "scorecard_web.json"))
    pin = PIN[slug]
    img = os.path.join(pkg, "imagery")
    t = time.time()
    b = course["bbox"]                         # [W, S, E, N]
    have = sorted(y["year"] for y in fim.list_years((b[1], b[0], b[3], b[2])) if y["coverage"] > 0.9 and y["year"] >= 2012)
    want = pin["pkg"]
    if want not in have:                      # the recorded package year is not served (any more) for this box: the
        # gate-2 rule (segv2/rebuild_big.py): the first served year above the extra years, else the newest served
        want = next((y for y in have if y > max(pin["extra"])), have[-1] if have else want)
    fim.fetch(course["bbox"], img, None, str(want), label=course.get("name"))
    fim.to_06(img)
    g = json.load(open(os.path.join(img, "georef.json")))
    padded = tuple(g["padded_bbox_wgs84_snwe"])
    for y in pin["extra"]:
        o = os.path.join(img, "years", str(y))
        os.makedirs(o, exist_ok=True)
        im = fim.fetch_naip(padded, o, 0.6, year=str(y))
        if "nir" not in im.get("files", {}):
            raise RuntimeError("no NIR band in %s" % y)
        json.dump(dict(imagery=im), open(os.path.join(o, "georef.json"), "w"), indent=1)
        fim.to_06(o)
    canopy.fetch(course["bbox"], os.path.join(pkg, "canopy"))
    return dict(fetch_s=round(time.time() - t, 1), pkg_year=(g.get("imagery") or {}).get("year"), pinned_pkg=pin["pkg"],
                pkg_pin_kept=want == pin["pkg"], extra=pin["extra"])


def perceive(slug, pkg, root, unet, obj):
    import fastscene as FS
    import route_learn as RL
    os.environ["FASTSCENE_UNET"] = os.path.join(ROOT, unet)
    os.environ["FASTSCENE_OBJECTS2"] = os.path.join(ROOT, obj)
    t = time.time()
    sc, info = FS.build(pkg, out=False)
    yrs = info["seconds"].get("unet_years")
    P = info["P"]
    Pu = np.clip(np.round(P * 255), 0, 255).astype(np.uint8)
    sc["route_bench"] = dict(version="big", probs="d0+yall", years=yrs, unet=unet, objects=obj)
    for d in ("scenes", "maps", os.path.join("probs", slug)):
        os.makedirs(os.path.join(root, "big", d), exist_ok=True)
    with gzip.open(os.path.join(root, "big", "scenes", slug + ".json.gz"), "wt") as fh:
        json.dump(sc, fh, separators=(",", ":"))
    Pz = Pu.copy()
    Pz[[0, 3, 4, 5]] = 0
    np.savez_compressed(os.path.join(root, "big", "probs", slug, "d0+yall.npz"), p=Pz)
    cp = os.path.join(pkg, "canopy", "chm_meta.tif")
    chm = RL.warp_chm(cp, sc["grid"]) if os.path.exists(cp) else None
    m = RL.corridor_maps(Pu, sc["grid"], chm=chm)
    np.savez_compressed(os.path.join(root, "big", "maps", slug + ".npz"), fair=m.fair, turf=m.turf, water=m.water,
                        bunker=m.bunker, tree=m.tree)
    return sc, dict(scene_s=round(time.time() - t, 1), unet_years=yrs, greens_hole=FS.hole_greens(sc),
                    tee_complexes=len(sc.get("tee_complexes") or []))


def recall(slug, sc):
    """truth greens with a scene green (not practice) within 20 yd; truth tees (hole-way start) with a scene tee box /
    complex centroid within 40 yd (the scorer's tolerances)"""
    import routing as R
    fc = json.load(gzip.open(os.path.join(BD, "courses", slug, "osm_golf.geojson.gz"), "rt"))
    T = {k: v for k, v in R.truth_from_fc(fc).items() if int(k) <= 18}

    def yd(a, b):
        k = math.cos(math.radians(a[1]))
        return math.hypot((a[0] - b[0]) * k, a[1] - b[1]) * 111320.0 / 0.9144
    gs = [g["centroid"] for g in sc.get("greens") or [] if g.get("kind") != "practice" and g.get("centroid")]
    ts = [c["centroid"] for c in sc.get("tee_complexes") or [] if c.get("centroid")]
    ts += [b["centroid"] for c in sc.get("tee_complexes") or [] for b in c.get("boxes") or [] if b.get("centroid")]
    gr = sum(any(yd(v["green_ll"], q) <= 20 for q in gs) for v in T.values())
    tr = sum(any(yd(v["tee_ll"], q) <= 40 for q in ts) for v in T.values())
    return dict(n_true=len(T), green_recall=gr, tee_recall=tr)


def setup_root(root):
    os.makedirs(os.path.join(root, "big"), exist_ok=True)
    for x in ("courses", "manifest.json", "status"):
        p = os.path.join(root, "big", x)
        if not os.path.lexists(p):
            os.symlink(os.path.join(BD, x), p)


def route(root, slugs, out):
    env = dict(os.environ, FASTPATH_CACHE=root, ROUTE_BENCH_PREP=os.path.join(root, "prep"), ROUTE_BENCH_CARD="pick",
               ROUTE_BENCH_PROBS="d0+yall", ROUTE_LEARN_VER="v2seg_d0+yall", ROUTE_P_TEE="0.0", ROUTE_TEE_PEAKS="0.1",
               ROUTE_TEE_PEAK_FILL="2", ROUTE_BENCH_FOLD_RESCORE="1",
               ROUTE_BENCH_FOLDS=os.path.join(FP, "benchdata", "folds"), ROUTE_RERANK="1", ROUTE_TEE="1")
    for k in ("ROUTE_BENCH_SC", "ROUTE_RERANK_PICKS", "ROUTE_TEE_PICKS", "FASTSCENE_UNET", "FASTSCENE_OBJECTS2"):
        env.pop(k, None)
    r = subprocess.run([sys.executable, os.path.join(FP, "route_bench.py"), "eval", "--scene", "fast", "--router", "v2",
                        "--card-only", "--prep", "--ver", "v2seg_d0+yall", "--split", "train+big", "--slugs",
                        ",".join(slugs), "--procs", str(os.cpu_count() or 2), "--out", out], cwd=FP, env=env,
                       capture_output=True, text=True)
    print(r.stdout[-600:], r.stderr[-1500:], flush=True)
    return {c["slug"]: c for c in json.load(open(out))["courses"]} if os.path.exists(out) else {}


def main():
    out = os.path.abspath(sys.argv[1])
    slugs = [s for a in sys.argv[2:] for s in a.split(",") if s]
    os.makedirs(out, exist_ok=True)
    V = {"A": (os.environ["PAIR_UNET_A"], os.environ["PAIR_OBJ_A"]),
         "B": (os.environ["PAIR_UNET_B"], os.environ["PAIR_OBJ_B"])}
    refetch = os.environ.get("PAIR_REFETCH_B") == "1"
    roots = {k: os.path.join(out, "root_" + k) for k in V}
    for r in roots.values():
        setup_root(r)
    tmp = tempfile.mkdtemp(prefix="pair_")
    recs = {}
    for slug in slugs:
        rec = dict(slug=slug, refetch_b=refetch, unet={k: v[0] for k, v in V.items()}, objects={k: v[1] for k, v in V.items()})
        try:
            pkg = os.path.join(tmp, slug)
            rec["fetch"] = fetch(slug, pkg)
            for k in ("A", "B"):
                if k == "B" and refetch:
                    shutil.rmtree(pkg, ignore_errors=True)
                    rec["fetch_b"] = fetch(slug, pkg)
                sc, info = perceive(slug, pkg, roots[k], *V[k])
                rec[k] = dict(info, **recall(slug, sc))
        except Exception as e:                                       # noqa: BLE001
            rec["error"] = repr(e)[:300]
            rec["trace"] = traceback.format_exc()[-1200:]
        shutil.rmtree(os.path.join(tmp, slug), ignore_errors=True)
        recs[slug] = rec
        print(json.dumps({k: v for k, v in rec.items() if k != "trace"})[:600], flush=True)
    ok = [s for s, r in recs.items() if "error" not in r]
    for k in ("A", "B"):
        t = time.time()
        res = route(roots[k], ok, os.path.join(out, "bench_%s.json" % k)) if ok else {}
        for s in ok:
            c = res.get(s) or {}
            res_ = [abs(v) for v in (c.get("card_resid") or {}).values()]
            recs[s][k].update(right=sum((c.get("hole_ok") or {}).values()), right_fwd=sum((c.get("hole_ok_fwd") or {}).values()),
                              card_err_med=round(float(np.median(res_)), 1) if res_ else None, route_error=c.get("error"))
        print("routed", k, len(res), "in", round(time.time() - t, 1), "s", flush=True)
    with open(os.path.join(out, "pair.jsonl"), "w") as fh:
        for s in slugs:
            fh.write(json.dumps(recs[s]) + "\n")
    shutil.rmtree(tmp, ignore_errors=True)
    for r in roots.values():                                         # keep the scenes (artifact), drop the prep pickles
        shutil.rmtree(os.path.join(r, "prep"), ignore_errors=True)


if __name__ == "__main__":
    main()
