"""build_inputs.py OUT_DIR SLUG[,SLUG...]: rebuild the routing bench's TRAIN-BIG inputs for some courses from free
imagery, as route_big.fetch_stage + perceive_stage did (2026-11-17/19), without the card search: truth, course and
cards come from benchdata/big. Per course: NAIP latest + the 2 newest other years at 0.6 m, 3DEP DEM, Meta canopy into a
temporary package, fastscene.build (U-Net mean over the 3 years; FASTSCENE_VINTAGE=0 as the TRAIN-BIG build), then
OUT_DIR/big/{scenes/<slug>.json.gz, probs/<slug>/d0+yall.npz (P(green) / P(tee) only), maps/<slug>.npz} and
OUT_DIR/inputs_<slug>.json (NAIP years, scene counts, timings). The package is deleted after each course."""
import gzip, json, os, shutil, sys, tempfile, time, traceback
import numpy as np
FP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [FP, os.path.dirname(FP)]
os.environ.setdefault("FASTPATH_TILE_CACHE", "off")
os.environ.setdefault("FASTSCENE_UNET_MODEL", "v2")
os.environ["FASTSCENE_VINTAGE"] = "0"
BD = os.path.join(FP, "benchdata", "big", "courses")


def package(slug, root):
    import fast_imagery as fim
    import canopy
    pkg = os.path.join(root, slug)
    raw = os.path.join(pkg, "raw")
    os.makedirs(raw, exist_ok=True)
    d = os.path.join(BD, slug)
    course = json.load(open(os.path.join(d, "course.json")))
    json.dump(course, open(os.path.join(raw, "course.json"), "w"))
    with gzip.open(os.path.join(d, "osm_golf.geojson.gz"), "rb") as fi, open(os.path.join(raw, "osm.geojson"), "wb") as fo:
        shutil.copyfileobj(fi, fo)
    shutil.copy(os.path.join(d, "scorecard.json"), os.path.join(raw, "scorecard_web.json"))
    T = {}
    t = time.time()
    fim.fetch(course["bbox"], os.path.join(pkg, "imagery"), None, "latest", label=course.get("name"))
    fim.to_06(os.path.join(pkg, "imagery"))
    T["imagery"] = round(time.time() - t, 1)
    t = time.time()
    try:
        fim.fetch_years(os.path.join(pkg, "imagery"), 2)
    except Exception as e:                                           # noqa: BLE001
        T["years_err"] = repr(e)[:160]
    T["years"] = round(time.time() - t, 1)
    t = time.time()
    canopy.fetch(course["bbox"], os.path.join(pkg, "canopy"))
    T["canopy"] = round(time.time() - t, 1)
    return pkg, T


def perceive(slug, pkg, out, T):
    import fastscene as FS
    import route_learn as RL
    t = time.time()
    sc, info = FS.build(pkg, out=False)
    T["scene"] = round(time.time() - t, 1)
    P = info["P"]
    Pu = np.clip(np.round(P * 255), 0, 255).astype(np.uint8)
    yr = (json.load(open(os.path.join(pkg, "imagery", "georef.json"))).get("imagery") or {}).get("year")
    sc["route_bench"] = dict(version="big", probs="d0+yall", years=info["seconds"].get("unet_years"), naip_year=yr)
    for d in ("scenes", "maps", os.path.join("probs", slug)):
        os.makedirs(os.path.join(out, "big", d), exist_ok=True)
    with gzip.open(os.path.join(out, "big", "scenes", slug + ".json.gz"), "wt") as fh:
        json.dump(sc, fh, separators=(",", ":"))
    Pz = Pu.copy()
    Pz[[0, 3, 4, 5]] = 0
    np.savez_compressed(os.path.join(out, "big", "probs", slug, "d0+yall.npz"), p=Pz)
    cp = os.path.join(pkg, "canopy", "chm_meta.tif")
    chm = RL.warp_chm(cp, sc["grid"]) if os.path.exists(cp) else None
    m = RL.corridor_maps(Pu, sc["grid"], chm=chm)
    np.savez_compressed(os.path.join(out, "big", "maps", slug + ".npz"), fair=m.fair, turf=m.turf, water=m.water,
                        bunker=m.bunker, tree=m.tree)
    return dict(naip_year=yr, unet_years=sc["route_bench"]["years"], greens_hole=FS.hole_greens(sc),
                tee_complexes=len(sc.get("tee_complexes") or []), fastscene_s=info["seconds"].get("total"))


def main():
    out = os.path.abspath(sys.argv[1])
    slugs = [s for a in sys.argv[2:] for s in a.split(",") if s]
    os.makedirs(out, exist_ok=True)
    root = tempfile.mkdtemp(prefix="pkg_")
    fails = 0
    for slug in slugs:
        rec = dict(slug=slug)
        try:
            pkg, T = package(slug, root)
            rec.update(perceive(slug, pkg, out, T), T=T)
        except Exception as e:                                       # noqa: BLE001
            rec["error"] = repr(e)[:300]
            rec["trace"] = traceback.format_exc()[-1500:]
            fails += 1
        shutil.rmtree(os.path.join(root, slug), ignore_errors=True)
        json.dump(rec, open(os.path.join(out, "inputs_%s.json" % slug), "w"), indent=1)
        print(json.dumps({k: v for k, v in rec.items() if k != "trace"}), flush=True)
    sys.exit(1 if fails == len(slugs) else 0)


if __name__ == "__main__":
    main()
