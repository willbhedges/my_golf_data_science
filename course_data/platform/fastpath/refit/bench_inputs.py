"""bench_inputs.py OUT_DIR SLUG[,SLUG...]: the routing bench's inputs rebuilt from free imagery for a refit on Actions
(.github/workflows/routing_bench.yml stage `inputs`), for TRAIN-BIG courses (tb_*) and the validation-set train courses.
Same NAIP years as the local bench: benchdata/big/pinned_years.json / benchdata/val/pinned_years.json (package year +
the extra years its scenes used). A pinned package year no longer served -> the first served year above the extra
years, else (no extra years, or none above them) the newest served; an extra year equal to the package year or not served is dropped, and fastscene's
fetch_years tops the extra years up to its k with the newest other served years (as a fresh build would).
Detector: the environment (FASTSCENE_UNET_MODEL, or FASTSCENE_UNET / FASTSCENE_OBJECTS2), FASTSCENE_VINTAGE=0.
Writes the cache layout route_bench / route_learn read (FASTPATH_CACHE=OUT_DIR):
    big/scenes/<slug>.json.gz, big/probs/<slug>/d0+yall.npz (P(green) / P(tee) only), big/maps/<slug>.npz
    val/scenes/v2seg_d0+yall/<slug>.json, heldout/probs/<slug>/d0.npz (6-class mean over the years), val/maps/d0+yall/<slug>.npz
and OUT_DIR/meta/<slug>.json: NAIP years and item ids per year, sha256 of every imagery / DEM / canopy file and of the
probabilities, scene counts, the CPU, the U-Net implementation used and the thread pins (to tell, between two runs,
whether the imagery or the arithmetic moved). The package is deleted after each course."""
import gzip, hashlib, json, os, shutil, sys, tempfile, time, traceback
import numpy as np
FP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CD = os.path.dirname(os.path.dirname(FP))
ROOT = os.path.dirname(CD)
sys.path[:0] = [FP, os.path.dirname(FP)]
os.environ.setdefault("FASTPATH_TILE_CACHE", "off")
os.environ.setdefault("FASTSCENE_UNET_MODEL", "v2")
os.environ["FASTSCENE_VINTAGE"] = "0"
BD = os.path.join(FP, "benchdata")
PIN = dict(json.load(open(os.path.join(BD, "big", "pinned_years.json"))),
           **json.load(open(os.path.join(BD, "val", "pinned_years.json"))))
VER = "v2seg_d0+yall"
PINS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_CORETYPE", "FASTPERC_IMPL", "GOLF_FASTC",
        "FASTSCENE_UNET_MODEL", "FASTSCENE_UNET", "FASTSCENE_OBJECTS2")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:16]


def cpu():
    m, fl = "?", ""
    try:
        for ln in open("/proc/cpuinfo"):
            if ln.startswith("model name") and m == "?":
                m = ln.split(":", 1)[1].strip()
            if ln.startswith("flags") and not fl:
                fl = ln
    except OSError:
        pass
    return dict(model=m, amx="amx_tile" in fl, avx512="avx512f" in fl, ncpu=os.cpu_count())


def course_files(slug):
    """-> (course dict, osm.geojson bytes path (gz), card path)"""
    if slug.startswith("tb_"):
        d = os.path.join(BD, "big", "courses", slug)
        return json.load(open(os.path.join(d, "course.json"))), os.path.join(d, "osm_golf.geojson.gz"), \
            os.path.join(d, "scorecard.json")
    d = os.path.join(BD, "val", "courses", slug)
    g = os.path.join(ROOT, PIN[slug]["dir"])
    cj = os.path.join(d, "course.json")
    return json.load(open(cj if os.path.exists(cj) else os.path.join(g, "course.json"))), \
        os.path.join(d, "osm.geojson.gz"), os.path.join(g, "scorecard.json")


def fetch(slug, pkg):
    import fast_imagery as fim
    import canopy
    raw = os.path.join(pkg, "raw")
    os.makedirs(raw, exist_ok=True)
    course, osm, card = course_files(slug)
    json.dump(course, open(os.path.join(raw, "course.json"), "w"))
    with gzip.open(osm, "rb") as fi, open(os.path.join(raw, "osm.geojson"), "wb") as fo:
        shutil.copyfileobj(fi, fo)
    if os.path.exists(card):
        shutil.copy(card, os.path.join(raw, "scorecard_web.json"))
    pin = PIN[slug]
    img = os.path.join(pkg, "imagery")
    t = time.time()
    b = course["bbox"]                         # [W, S, E, N]
    have = sorted(y["year"] for y in fim.list_years((b[1], b[0], b[3], b[2])) if y["coverage"] > 0.9 and y["year"] >= 2012)
    extra = list(pin.get("extra") or [])
    want = pin["pkg"]
    if want not in have:
        want = next((y for y in have if y > max(extra)), have[-1]) if extra and have else (have[-1] if have else want)
    fim.fetch(course["bbox"], img, None, str(want), label=course.get("name"))
    fim.to_06(img)
    g = json.load(open(os.path.join(img, "georef.json")))
    own = (g.get("imagery") or {}).get("year")
    padded = tuple(g["padded_bbox_wgs84_snwe"])
    dropped = []
    for y in extra:
        if y == own or y not in have:
            dropped.append(y)
            continue
        o = os.path.join(img, "years", str(y))
        os.makedirs(o, exist_ok=True)
        im = fim.fetch_naip(padded, o, 0.6, year=str(y))
        if "nir" not in im.get("files", {}):
            shutil.rmtree(o, ignore_errors=True)
            dropped.append(y)
            continue
        json.dump(dict(imagery=im), open(os.path.join(o, "georef.json"), "w"), indent=1)
        fim.to_06(o)
    canopy.fetch(course["bbox"], os.path.join(pkg, "canopy"))
    return dict(fetch_s=round(time.time() - t, 1), pkg_year=own, pinned_pkg=pin["pkg"], pinned_extra=extra,
                pkg_pin_kept=own == pin["pkg"], extra_dropped=dropped, served=have)


def imagery_record(pkg):
    """years -> NAIP item ids + file hashes (after fastscene: the extra years it fetched itself included)"""
    img = os.path.join(pkg, "imagery")
    out = {}
    dirs = [(None, img)] + [(y, os.path.join(img, "years", y)) for y in sorted(os.listdir(os.path.join(img, "years")))
                            if os.path.isdir(os.path.join(img, "years", y))] if os.path.isdir(os.path.join(img, "years")) \
        else [(None, img)]
    for y, d in dirs:
        try:
            im = json.load(open(os.path.join(d, "georef.json"))).get("imagery") or {}
        except OSError:
            continue
        out[str(im.get("year") or y)] = dict(role="pkg" if y is None else "extra", items=im.get("items"),
                                             acquired=im.get("acquired"),
                                             sha={f: sha(os.path.join(d, f)) for f in ("naip_rgb.tif", "naip_nir.tif")
                                                  if os.path.exists(os.path.join(d, f))})
    files = {}
    for f in ("imagery/dem.tif", "canopy/chm_meta.tif"):
        if os.path.exists(os.path.join(pkg, f)):
            files[f] = sha(os.path.join(pkg, f))
    return out, files


def perceive(slug, pkg, out):
    import fastscene as FS
    import route_learn as RL
    t = time.time()
    sc, info = FS.build(pkg, out=False)
    P = info["P"]
    Pu = np.clip(np.round(P * 255), 0, 255).astype(np.uint8)
    yrs = info["seconds"].get("unet_years")
    impl = sorted({type(v).__name__ for v in FS._NET.values()})
    sc["route_bench"] = dict(version=VER if not slug.startswith("tb_") else "big", probs="d0+yall", years=yrs,
                             unet=os.environ.get("FASTSCENE_UNET") or os.environ.get("FASTSCENE_UNET_MODEL"))
    cp = os.path.join(pkg, "canopy", "chm_meta.tif")
    chm = RL.warp_chm(cp, sc["grid"]) if os.path.exists(cp) else None
    m = RL.corridor_maps(Pu, sc["grid"], chm=chm)
    if slug.startswith("tb_"):
        for d in ("scenes", "maps", os.path.join("probs", slug)):
            os.makedirs(os.path.join(out, "big", d), exist_ok=True)
        with gzip.open(os.path.join(out, "big", "scenes", slug + ".json.gz"), "wt") as fh:
            json.dump(sc, fh, separators=(",", ":"))
        Pz = Pu.copy()
        Pz[[0, 3, 4, 5]] = 0
        np.savez_compressed(os.path.join(out, "big", "probs", slug, "d0+yall.npz"), p=Pz)
        mp = os.path.join(out, "big", "maps", slug + ".npz")
    else:
        for d in (os.path.join("val", "scenes", VER), os.path.join("val", "maps", "d0+yall"), os.path.join("heldout", "probs", slug)):
            os.makedirs(os.path.join(out, d), exist_ok=True)
        json.dump(sc, open(os.path.join(out, "val", "scenes", VER, slug + ".json"), "w"), separators=(",", ":"))
        np.savez_compressed(os.path.join(out, "heldout", "probs", slug, "d0.npz"), p=Pu)
        mp = os.path.join(out, "val", "maps", "d0+yall", slug + ".npz")
    np.savez_compressed(mp, fair=m.fair, turf=m.turf, water=m.water, bunker=m.bunker, tree=m.tree)
    return dict(scene_s=round(time.time() - t, 1), unet_years=yrs, unet_impl=impl, probs_sha=hashlib.sha256(Pu.tobytes()).hexdigest()[:16],
                greens_hole=FS.hole_greens(sc), tee_complexes=len(sc.get("tee_complexes") or []),
                greens=len(sc.get("greens") or []))


def main():
    out = os.path.abspath(sys.argv[1])
    slugs = [s for a in sys.argv[2:] for s in a.split(",") if s]
    os.makedirs(os.path.join(out, "meta"), exist_ok=True)
    root = tempfile.mkdtemp(prefix="bin_")
    env = {k: os.environ.get(k) for k in PINS}
    c = cpu()
    fails = 0
    for slug in slugs:
        rec = dict(slug=slug, cpu=c, env=env)
        pkg = os.path.join(root, slug)
        try:
            for k in range(4):                 # Planetary Computer's token endpoint answers 429 under load
                try:
                    rec["fetch"] = fetch(slug, pkg)
                    break
                except Exception as e:                               # noqa: BLE001
                    if "429" not in repr(e) or k == 3:
                        raise
                    shutil.rmtree(pkg, ignore_errors=True)
                    time.sleep(60 * (k + 1))
            rec.update(perceive(slug, pkg, out))
            rec["imagery"], rec["files"] = imagery_record(pkg)
        except Exception as e:                                       # noqa: BLE001
            rec["error"] = repr(e)[:300]
            rec["trace"] = traceback.format_exc()[-1500:]
            fails += 1
        shutil.rmtree(pkg, ignore_errors=True)
        json.dump(rec, open(os.path.join(out, "meta", slug + ".json"), "w"), indent=1)
        print(json.dumps({k: v for k, v in rec.items() if k not in ("trace", "imagery", "env", "cpu")})[:400], flush=True)
    print("cpu", json.dumps(c), "env", json.dumps(env), "failed", fails, "of", len(slugs), flush=True)
    shutil.rmtree(root, ignore_errors=True)
    sys.exit(1 if slugs and fails == len(slugs) else 0)


if __name__ == "__main__":
    main()
